"""Markdown export helpers for Kaiten cards and documents."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from kaiten_cli.errors import ConfigError, ValidationError
from kaiten_cli.models import DebugReporter, ToolSpec

UUID_RE = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
INTERNAL_FILE_RE = re.compile(
    rf"/(?:files/)?companies/{UUID_RE}/(?P<kind>documents|cards)/(?P<owner>{UUID_RE})/"
    rf"(?P<file>{UUID_RE})(?:\.[^/?#\])]+)?$"
)
API_FILE_RE = re.compile(
    rf"^/api(?:/latest)?/(?P<kind>documents|cards)/(?P<owner>[^/]+)/files/(?P<file>{UUID_RE})(?:\.[^/?#\])]+)?$"
)
INTERNAL_FILE_TEXT_RE = re.compile(
    rf"(?P<url>(?:https?://[^)\]\s]+)?/(?:files/)?companies/{UUID_RE}/"
    rf"(?P<kind>documents|cards)/(?P<owner>{UUID_RE})/(?P<file>{UUID_RE})(?:\.[^)\]\s]+)?)"
)
API_FILE_TEXT_RE = re.compile(
    rf"(?P<url>/api(?:/latest)?/(?P<kind>documents|cards)/(?P<owner>[^/)\]\s]+)/files/"
    rf"(?P<file>{UUID_RE})(?:\.[^)\]\s]+)?)"
)


def _payload_str(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_filename(value: str, fallback: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w\s.-]+", "", value, flags=re.UNICODE)
    value = re.sub(r"[\s/]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-._")
    return value[:90] or fallback


def _output_path(output: str | None, filename: str) -> Path:
    if output is None:
        return Path.cwd() / filename
    output_path = Path(output).expanduser()
    if output.endswith(("/", os.sep)) or output_path.is_dir():
        return output_path / filename
    return output_path


def _write_text_atomic(path: Path, text: str, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise ValidationError(f"Output file already exists: {path}. Use --overwrite to replace it.")
    path.parent.mkdir(parents=True, exist_ok=True)
    part_path = path.with_name(f"{path.name}.part")
    if part_path.exists() and not overwrite:
        raise ValidationError(f"Partial file already exists: {part_path}. Use --overwrite to replace it.")
    part_path.write_text(text, encoding="utf-8")
    part_path.replace(path)


def _yaml_scalar(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _frontmatter(entity_type: str, fields: dict[str, Any]) -> str:
    lines = ["---", f"type: {_yaml_scalar(entity_type)}"]
    for key, value in fields.items():
        if value is not None:
            lines.append(f"{key}: {_yaml_scalar(value)}")
    lines.extend(["---", ""])
    return "\n".join(lines)


def _parse_document_data(data: Any) -> dict[str, Any]:
    if isinstance(data, dict):
        return data
    if isinstance(data, str) and data.strip():
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            return {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": data}]}]}
        if isinstance(parsed, dict):
            return parsed
    return {"type": "doc", "content": []}


def _children(node: dict[str, Any]) -> list[dict[str, Any]]:
    content = node.get("content")
    return [child for child in content if isinstance(child, dict)] if isinstance(content, list) else []


def _attrs(node: dict[str, Any]) -> dict[str, Any]:
    attrs = node.get("attrs")
    return attrs if isinstance(attrs, dict) else {}


def _text_content(node: dict[str, Any], *, document_uid: str | None = None) -> str:
    if node.get("type") == "text":
        return str(node.get("text") or "")
    return "".join(_inline(child, document_uid=document_uid) for child in _children(node))


def _escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _escape_link_text(value: str) -> str:
    return value.replace("[", "\\[").replace("]", "\\]")


def _strip_file_extension(value: Any) -> str:
    text = str(value)
    if re.fullmatch(rf"{UUID_RE}\.[^./\\]+", text):
        return text.rsplit(".", 1)[0]
    return text


def _api_file_link(kind: str, owner: Any, file_id: Any) -> str:
    return f"/api/{kind}/{owner}/files/{_strip_file_extension(file_id)}"


def _normalize_kaiten_file_url(url: str) -> str:
    if not url:
        return url
    parsed = urlparse(url)
    path = parsed.path or url
    if not path.startswith("/"):
        path = f"/{path}"

    api_match = API_FILE_RE.match(path)
    if api_match is not None:
        return _api_file_link(api_match.group("kind"), api_match.group("owner"), api_match.group("file"))

    internal_match = INTERNAL_FILE_RE.search(path)
    if internal_match is not None:
        return _api_file_link(
            internal_match.group("kind"),
            internal_match.group("owner"),
            internal_match.group("file"),
        )

    return url


def _normalize_file_links_in_markdown(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return _api_file_link(match.group("kind"), match.group("owner"), match.group("file"))

    text = API_FILE_TEXT_RE.sub(repl, text)
    return INTERNAL_FILE_TEXT_RE.sub(repl, text)


def _link_for_file(attrs: dict[str, Any], *, document_uid: str | None) -> str:
    file_id = attrs.get("fileId") or attrs.get("file_id")
    if file_id and document_uid:
        return _api_file_link("documents", document_uid, file_id)
    return _normalize_kaiten_file_url(str(attrs.get("url") or attrs.get("src") or ""))


def _apply_marks(text: str, marks: Any, *, document_uid: str | None) -> str:
    if not isinstance(marks, list):
        return text
    result = text
    link: dict[str, Any] | None = None
    for mark in marks:
        if not isinstance(mark, dict):
            continue
        mark_type = str(mark.get("type") or "")
        attrs = mark.get("attrs") if isinstance(mark.get("attrs"), dict) else {}
        if mark_type in {"bold", "strong"}:
            result = f"**{result}**"
        elif mark_type in {"italic", "em"}:
            result = f"*{result}*"
        elif mark_type in {"strikethrough", "strike"}:
            result = f"~~{result}~~"
        elif mark_type == "code":
            result = f"`{result}`"
        elif mark_type == "underline":
            result = f"++{result}++"
        elif mark_type == "sup":
            result = f"^{result}^"
        elif mark_type == "sub":
            result = f"~{result}~"
        elif mark_type == "link":
            link = attrs
    if link is not None:
        href = link.get("href") or ""
        if link.get("fileId") and link.get("fileEntityType"):
            kind = {"document": "documents", "card": "cards"}.get(str(link["fileEntityType"]))
            if kind == "documents" and document_uid:
                href = _api_file_link(kind, document_uid, link["fileId"])
            elif kind and (link.get("entityId") or link.get("entityUid")):
                href = _api_file_link(kind, link.get("entityId") or link.get("entityUid") or "", link["fileId"])
            else:
                href = _normalize_kaiten_file_url(str(href))
        else:
            href = _normalize_kaiten_file_url(str(href))
        title = str(link.get("title") or "")
        escaped_title = title.replace('"', '\\"')
        quoted_title = f' "{escaped_title}"' if title else ""
        result = f"[{_escape_link_text(result)}]({href}{quoted_title})"
    return result


def _inline(node: dict[str, Any], *, document_uid: str | None) -> str:
    node_type = node.get("type")
    if node_type == "text":
        return _apply_marks(str(node.get("text") or ""), node.get("marks"), document_uid=document_uid)
    if node_type == "hard_break":
        return "\n"
    if node_type == "mention":
        return str(_attrs(node).get("label") or "")
    if node_type == "inline_card_link":
        return str(_attrs(node).get("url") or "")
    if node_type == "image":
        attrs = _attrs(node)
        url = _link_for_file(attrs, document_uid=document_uid)
        alt = str(attrs.get("alt") or attrs.get("title") or attrs.get("name") or "image")
        return f"![{_escape_link_text(alt)}]({url})" if url else alt
    return "".join(_inline(child, document_uid=document_uid) for child in _children(node))


def _render_list(
    node: dict[str, Any],
    *,
    document_uid: str | None,
    ordered: bool = False,
    check_list: bool = False,
) -> str:
    lines: list[str] = []
    start = int(_attrs(node).get("order") or 1)
    for index, item in enumerate(_children(node), start=start):
        attrs = _attrs(item)
        if check_list:
            prefix = "- [x] " if attrs.get("checked") else "- [ ] "
        elif ordered:
            prefix = f"{index}. "
        else:
            prefix = "* "
        item_text = _block(item, document_uid=document_uid).strip()
        item_lines = item_text.splitlines() or [""]
        lines.append(f"{prefix}{item_lines[0]}")
        continuation = " " * len(prefix)
        lines.extend(f"{continuation}{line}" for line in item_lines[1:])
    return "\n".join(lines)


def _render_table(node: dict[str, Any], *, document_uid: str | None) -> str:
    rows: list[list[str]] = []
    for row in _children(node):
        if row.get("type") not in {"table_row", "tableRow"}:
            continue
        cells = [_escape_table_cell(_text_content(cell, document_uid=document_uid)) for cell in _children(row)]
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join("---" for _ in range(width)) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows[1:])
    return "\n".join(lines)


def _prefix_lines(text: str, prefix: str) -> str:
    return "\n".join(f"{prefix}{line}" if line else prefix.rstrip() for line in text.splitlines())


def _block(node: dict[str, Any], *, document_uid: str | None) -> str:
    node_type = node.get("type")
    attrs = _attrs(node)

    if node_type == "doc":
        return _blocks(_children(node), document_uid=document_uid)
    if node_type == "paragraph":
        return "".join(_inline(child, document_uid=document_uid) for child in _children(node)).strip()
    if node_type in {"heading", "heading1", "heading2", "heading3"}:
        level = int(attrs.get("level") or str(node_type).removeprefix("heading") or 1)
        return f"{'#' * min(max(level, 1), 6)} {_text_content(node, document_uid=document_uid).strip()}".rstrip()
    if node_type == "toggle_heading":
        return f"**{_text_content(node, document_uid=document_uid).strip()}**"
    if node_type in {"bullet_list", "list"}:
        return _render_list(node, document_uid=document_uid)
    if node_type == "ordered_list":
        return _render_list(node, document_uid=document_uid, ordered=True)
    if node_type == "check_list":
        return _render_list(node, document_uid=document_uid, check_list=True)
    if node_type in {"list_item", "check_list_item", "toggle_content", "columns", "column", "toggle"}:
        return _blocks(_children(node), document_uid=document_uid)
    if node_type in {"blockquote", "alert"}:
        return _prefix_lines(_blocks(_children(node), document_uid=document_uid), "> ")
    if node_type == "code_block":
        language = attrs.get("language") or attrs.get("params") or ""
        return f"```{language}\n{node.get('text') or _text_content(node, document_uid=document_uid).strip()}\n```"
    if node_type == "horizontal_rule":
        return "---"
    if node_type == "table":
        return _render_table(node, document_uid=document_uid)
    if node_type in {"image", "imageBlock"}:
        rendered = _inline(node, document_uid=document_uid)
        return rendered or _blocks(_children(node), document_uid=document_uid)
    if node_type == "file":
        url = _link_for_file(attrs, document_uid=document_uid)
        label = str(attrs.get("name") or attrs.get("title") or attrs.get("fileName") or attrs.get("fileId") or "file")
        return f"[{_escape_link_text(label)}]({url})" if url else label
    if node_type in {"inline_card_link", "block_card_link"}:
        return str(attrs.get("url") or "")

    if _children(node):
        return _blocks(_children(node), document_uid=document_uid)
    return ""


def _blocks(nodes: list[dict[str, Any]], *, document_uid: str | None) -> str:
    rendered = [_block(node, document_uid=document_uid).strip() for node in nodes]
    return "\n\n".join(block for block in rendered if block)


def document_to_markdown(document: dict[str, Any]) -> str:
    document_uid = str(document.get("uid") or document.get("id") or "")
    title = str(document.get("title") or document_uid or "Document")
    frontmatter = _frontmatter(
        "document",
        {
            "uid": document.get("uid"),
            "id": document.get("id"),
            "title": title,
            "created": document.get("created"),
            "updated": document.get("updated"),
            "parent_entity_uid": document.get("parent_entity_uid"),
        },
    )
    body = _block(_parse_document_data(document.get("data")), document_uid=document_uid).strip()
    return f"{frontmatter}\n# {title}\n\n{body}\n".rstrip() + "\n"


def _card_file_link(card: dict[str, Any], file_item: dict[str, Any]) -> str | None:
    file_id = file_item.get("id") or file_item.get("uid")
    if file_id is None:
        return None
    card_ref = card.get("uid") or card.get("id")
    if card_ref is None:
        return None
    return _api_file_link("cards", card_ref, file_id)


def card_to_markdown(card: dict[str, Any], files: list[dict[str, Any]]) -> str:
    card_id = card.get("id")
    title = str(card.get("title") or card.get("name") or card_id or "Card")
    frontmatter = _frontmatter(
        "card",
        {
            "id": card_id,
            "uid": card.get("uid"),
            "title": title,
            "created": card.get("created"),
            "updated": card.get("updated"),
            "state": card.get("state"),
            "board_id": card.get("board_id"),
        },
    )
    description = _normalize_file_links_in_markdown(str(card.get("description") or "").strip())
    body_parts = [frontmatter, f"# {title}", description]
    attachment_lines = []
    for item in files:
        url = _card_file_link(card, item)
        if url is None:
            continue
        label = str(item.get("name") or item.get("filename") or item.get("id") or "file")
        attachment_lines.append(f"- [{_escape_link_text(label)}]({url})")
    if attachment_lines:
        body_parts.extend(["## Attachments", "\n".join(attachment_lines)])
    return "\n\n".join(part for part in body_parts if part).rstrip() + "\n"


def validate_card_get_markdown_options(tool: ToolSpec, payload: dict[str, Any]) -> None:
    del tool
    if payload.get("markdown") and payload.get("fields"):
        raise ValidationError("--fields cannot be combined with --markdown.")


def _entity_filename(title: str, identifier: Any, fallback: str) -> str:
    slug = _safe_filename(title, fallback)
    suffix = _safe_filename(str(identifier), fallback)
    return f"{slug}--{suffix}.md"


def _write_markdown_result(
    *,
    text: str,
    output: str | None,
    filename: str,
    overwrite: bool,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    path = _output_path(output, filename)
    _write_text_atomic(path, text, overwrite=overwrite)
    return {"path": str(path), "bytes": path.stat().st_size, **metadata}


async def execute_document_get(
    client: Any,
    tool: ToolSpec,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter: DebugReporter | None,
) -> dict[str, Any]:
    del tool, body, reporter
    if client is None:
        raise ConfigError("This command requires a Kaiten profile.")
    document = await client.get(path, params=query, timeout=timeout)
    if not isinstance(document, dict):
        raise ValidationError("Kaiten returned an unexpected document payload.")
    if not payload.get("markdown"):
        return document
    document_uid = _payload_str(payload, "document_uid")
    if document_uid is None:
        raise ValidationError("Missing required field: document_uid.")
    text = document_to_markdown(document)
    filename = _entity_filename(str(document.get("title") or "document"), document_uid, "document")
    return _write_markdown_result(
        text=text,
        output=_payload_str(payload, "output"),
        filename=filename,
        overwrite=bool(payload.get("overwrite", False)),
        metadata={
            "entity_type": "document",
            "document_uid": document_uid,
            "title": document.get("title"),
        },
    )


async def execute_card_get(
    client: Any,
    tool: ToolSpec,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter: DebugReporter | None,
) -> dict[str, Any]:
    del tool, body, reporter
    if client is None:
        raise ConfigError("This command requires a Kaiten profile.")
    card_id = _payload_str(payload, "card_id")
    if card_id is None:
        raise ValidationError("Missing required field: card_id.")
    card = await client.get(path, params=query, timeout=timeout)
    if not isinstance(card, dict):
        raise ValidationError("Kaiten returned an unexpected card payload.")
    if not payload.get("markdown"):
        return card
    card_ref = card.get("uid") or card.get("id") or card_id
    files_payload = await client.get(f"/cards/{card_ref}/files", timeout=timeout)
    files = files_payload if isinstance(files_payload, list) else []
    text = card_to_markdown(card, files)
    filename = _entity_filename(str(card.get("title") or "card"), card.get("id") or card_id, "card")
    return _write_markdown_result(
        text=text,
        output=_payload_str(payload, "output"),
        filename=filename,
        overwrite=bool(payload.get("overwrite", False)),
        metadata={
            "entity_type": "card",
            "card_id": card_id,
            "title": card.get("title"),
            "attachment_count": len(files),
        },
    )
