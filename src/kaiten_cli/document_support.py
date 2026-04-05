"""Helpers for document payload shaping."""

from __future__ import annotations

import re
import time
from typing import Any

_MARK_ALIASES = {
    "bold": "strong",
    "italic": "em",
    "strikethrough": "strike",
}

_INLINE_PATTERNS = [
    (re.compile(r"\*\*(.+?)\*\*"), "strong"),
    (re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)"), "em"),
    (re.compile(r"~~(.+?)~~"), "strike"),
    (re.compile(r"`(.+?)`"), "code"),
]


def extract_text_from_node(node: dict[str, Any]) -> str:
    if not isinstance(node, dict):
        return ""
    if node.get("type") == "text":
        return str(node.get("text", ""))
    return "".join(extract_text_from_node(child) for child in node.get("content", []))


def parse_inline(text: str) -> list[dict[str, Any]]:
    if not text:
        return []

    nodes: list[dict[str, Any]] = []
    pos = 0
    while pos < len(text):
        best_match = None
        best_mark = None
        for pattern, mark in _INLINE_PATTERNS:
            match = pattern.search(text, pos)
            if match and (best_match is None or match.start() < best_match.start()):
                best_match = match
                best_mark = mark

        if best_match is None:
            nodes.append({"type": "text", "text": text[pos:]})
            break

        if best_match.start() > pos:
            nodes.append({"type": "text", "text": text[pos : best_match.start()]})
        nodes.append(
            {
                "type": "text",
                "text": best_match.group(1),
                "marks": [{"type": best_mark}],
            }
        )
        pos = best_match.end()
    return nodes


def markdown_to_prosemirror(text: str) -> dict[str, Any]:
    content: list[dict[str, Any]] = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph_lines:
            joined = " ".join(paragraph_lines)
            content.append({"type": "paragraph", "content": parse_inline(joined)})
            paragraph_lines.clear()

    for line in text.strip().split("\n"):
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)", stripped)
        if heading:
            flush_paragraph()
            content.append(
                {
                    "type": "heading",
                    "attrs": {"level": len(heading.group(1))},
                    "content": parse_inline(heading.group(2)),
                }
            )
            continue

        if re.match(r"^---+$", stripped):
            flush_paragraph()
            content.append({"type": "horizontal_rule"})
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            content.append(
                {
                    "type": "blockquote",
                    "content": [{"type": "paragraph", "content": parse_inline(stripped[2:])}],
                }
            )
            continue

        paragraph_lines.append(stripped)

    flush_paragraph()

    if not content:
        content = [{"type": "paragraph", "content": []}]

    return {"type": "doc", "content": content}


def sanitize_prosemirror(node: Any) -> Any:
    if not isinstance(node, dict):
        return node

    node_type = node.get("type")
    if node_type in {"bullet_list", "ordered_list"}:
        paragraphs = []
        for index, item in enumerate(node.get("content", []), 1):
            prefix = "• " if node_type == "bullet_list" else f"{index}. "
            text = extract_text_from_node(item)
            if text:
                paragraphs.append(
                    {"type": "paragraph", "content": [{"type": "text", "text": f"{prefix}{text}"}]}
                )
        return paragraphs if paragraphs else [{"type": "paragraph", "content": []}]

    if "marks" in node:
        node = {
            **node,
            "marks": [
                ({**mark, "type": _MARK_ALIASES[mark["type"]]} if isinstance(mark, dict) and mark.get("type") in _MARK_ALIASES else mark)
                for mark in node["marks"]
            ],
        }

    if "content" in node:
        new_content = []
        for child in node["content"]:
            result = sanitize_prosemirror(child)
            if isinstance(result, list):
                new_content.extend(result)
            else:
                new_content.append(result)
        node = {**node, "content": new_content}

    return node


def prepare_document_body(canonical_name: str, body: dict[str, Any]) -> dict[str, Any]:
    prepared = dict(body)

    if canonical_name == "documents.create":
        prepared.setdefault("sort_order", int(time.time()))
    if canonical_name == "document-groups.create":
        prepared.setdefault("sort_order", int(time.time()))

    if canonical_name in {"documents.create", "documents.update"}:
        text = prepared.pop("text", None)
        raw_data = prepared.pop("data", None)
        if text:
            prepared["data"] = markdown_to_prosemirror(text)
        elif raw_data is not None:
            sanitized = sanitize_prosemirror(raw_data)
            prepared["data"] = sanitized if isinstance(sanitized, dict) else raw_data

    return prepared
