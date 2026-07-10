"""File download helpers."""

from __future__ import annotations

import os
import mimetypes
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import httpx

from kaiten_cli.errors import ConfigError, TransportError, ValidationError
from kaiten_cli.models import DebugReporter, ToolSpec

CHUNK_SIZE = 1024 * 1024
SIGNED_URL_REFRESH_STATUSES = {401, 403}
RESOLVE_QUERY = {"prevent_redirect": True, "response_type": "json"}

UUID_RE = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
INTERNAL_FILE_RE = re.compile(
    rf"/(?:files/)?companies/{UUID_RE}/(?P<kind>documents|cards)/(?P<owner>{UUID_RE})/"
    rf"(?P<file>{UUID_RE})(?:\.[^/?#]+)?$"
)
API_PREFIX_RE = re.compile(r"^/api(?:/latest)?(?P<path>/.*)$")


@dataclass(frozen=True)
class DownloadSource:
    kind: str
    endpoint_path: str | None
    direct_url: str | None
    entity_type: str | None = None
    file_id: str | None = None


@dataclass(frozen=True)
class ResolvedDownload:
    url: str
    source: DownloadSource


@dataclass(frozen=True)
class DownloadResult:
    path: Path
    bytes_written: int
    resumed: bool
    content_type: str | None
    status_code: int


def _emit_debug(reporter: DebugReporter | None, message: str) -> None:
    if reporter is not None:
        reporter(message)


def _payload_str(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _strip_file_extension(value: str) -> str:
    if re.fullmatch(rf"{UUID_RE}\.[^./\\]+", value):
        return value.rsplit(".", 1)[0]
    return value


def _file_id(payload: dict[str, Any]) -> str:
    value = _payload_str(payload, "file_id")
    if value is None:
        raise ValidationError("Missing required field: file_id.")
    return _strip_file_extension(value)


def _first_payload_str(payload: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = _payload_str(payload, key)
        if value is not None:
            return value
    return None


def _source_from_entity(payload: dict[str, Any]) -> DownloadSource:
    entity_type = _payload_str(payload, "entity_type")
    file_id = _file_id(payload)

    if entity_type == "document":
        document_uid = _payload_str(payload, "document_uid")
        if document_uid is None:
            raise ValidationError("document files require --document-uid.")
        return DownloadSource(
            kind="kaiten_api",
            endpoint_path=f"/documents/{document_uid}/files/{file_id}",
            direct_url=None,
            entity_type=entity_type,
            file_id=file_id,
        )

    if entity_type == "card":
        card_ref = _first_payload_str(payload, "card_id_or_uid", "card_uid", "card_id")
        if card_ref is None:
            raise ValidationError("card files require --card-id, --card-uid, or --card-id-or-uid.")
        return DownloadSource(
            kind="kaiten_api",
            endpoint_path=f"/cards/{card_ref}/files/{file_id}",
            direct_url=None,
            entity_type=entity_type,
            file_id=file_id,
        )

    if entity_type == "comment":
        card_ref = _first_payload_str(payload, "card_id_or_uid", "card_uid", "card_id")
        comment_uid = _payload_str(payload, "comment_uid")
        if card_ref is None or comment_uid is None:
            raise ValidationError("comment files require --card-id/--card-uid and --comment-uid.")
        return DownloadSource(
            kind="kaiten_api",
            endpoint_path=f"/cards/{card_ref}/comments/{comment_uid}/files/{file_id}",
            direct_url=None,
            entity_type=entity_type,
            file_id=file_id,
        )

    if entity_type == "custom_property":
        card_ref = _first_payload_str(payload, "card_id_or_uid", "card_uid", "card_id")
        custom_property_uid = _payload_str(payload, "custom_property_uid")
        if card_ref is None or custom_property_uid is None:
            raise ValidationError(
                "custom property files require --card-id/--card-uid and --custom-property-uid."
            )
        return DownloadSource(
            kind="kaiten_api",
            endpoint_path=f"/cards/{card_ref}/custom-properties/{custom_property_uid}/files/{file_id}",
            direct_url=None,
            entity_type=entity_type,
            file_id=file_id,
        )

    if entity_type == "conversation_message":
        conversation_uid = _payload_str(payload, "conversation_uid")
        conversation_message_uid = _payload_str(payload, "conversation_message_uid")
        if conversation_uid is None or conversation_message_uid is None:
            raise ValidationError(
                "conversation message files require --conversation-uid and --conversation-message-uid."
            )
        return DownloadSource(
            kind="kaiten_api",
            endpoint_path=(
                f"/conversations/{conversation_uid}/messages/{conversation_message_uid}/files/{file_id}"
            ),
            direct_url=None,
            entity_type=entity_type,
            file_id=file_id,
        )

    raise ValidationError(
        "Provide --url or --entity-type with one of: card, document, comment, "
        "custom_property, conversation_message."
    )


def _source_from_url(url: str) -> DownloadSource:
    parsed = urlparse(url)
    path = parsed.path or url

    api_match = API_PREFIX_RE.match(path)
    if api_match is not None:
        endpoint_path = api_match.group("path")
        return DownloadSource(
            kind="kaiten_api",
            endpoint_path=endpoint_path,
            direct_url=None,
            file_id=_file_id_from_endpoint(endpoint_path),
        )

    internal_match = INTERNAL_FILE_RE.search(path)
    if internal_match is not None:
        kind = internal_match.group("kind")
        entity_type = "document" if kind == "documents" else "card"
        endpoint_prefix = "/documents" if kind == "documents" else "/cards"
        file_id = internal_match.group("file")
        return DownloadSource(
            kind="kaiten_internal_file_url",
            endpoint_path=f"{endpoint_prefix}/{internal_match.group('owner')}/files/{file_id}",
            direct_url=None,
            entity_type=entity_type,
            file_id=file_id,
        )

    if parsed.scheme in {"http", "https"}:
        return DownloadSource(kind="direct_url", endpoint_path=None, direct_url=url)

    raise ValidationError(
        "Unsupported file URL. Use a Kaiten /api/... URL or an absolute http(s) URL."
    )


def _file_id_from_endpoint(endpoint_path: str) -> str | None:
    parts = [part for part in endpoint_path.split("/") if part]
    if "files" not in parts:
        return None
    index = parts.index("files")
    if index + 1 >= len(parts):
        return None
    return _strip_file_extension(parts[index + 1])


def resolve_download_source(payload: dict[str, Any]) -> DownloadSource:
    url = _payload_str(payload, "url")
    if url is not None:
        return _source_from_url(url)
    return _source_from_entity(payload)


def _suggested_name(payload: dict[str, Any], source: DownloadSource, resolved_url: str) -> str:
    explicit = _payload_str(payload, "name")
    if explicit is not None:
        return _safe_filename(explicit)
    parsed = urlparse(resolved_url)
    basename = unquote(Path(parsed.path).name)
    if basename:
        return _safe_filename(basename)
    if source.file_id:
        return _safe_filename(source.file_id)
    return "kaiten-file"


def _safe_filename(name: str) -> str:
    sanitized = name.replace("/", "_").replace("\\", "_").strip()
    return sanitized or "kaiten-file"


def _part_path(target_path: Path) -> Path:
    return target_path.with_name(f"{target_path.name}.part")


def _upload_file_path(payload: dict[str, Any]) -> Path:
    value = _payload_str(payload, "file")
    if value is None:
        raise ValidationError("Missing required field: file.")
    path = Path(value).expanduser()
    if not path.exists():
        raise ValidationError(f"Upload file does not exist: {path}.")
    if not path.is_file():
        raise ValidationError(f"Upload path is not a file: {path}.")
    return path


def _upload_content_type(path: Path) -> str:
    content_type, _ = mimetypes.guess_type(str(path))
    return content_type or "application/octet-stream"


def _output_allows_remote_filename(output: str | None) -> bool:
    if output is None:
        return True
    return output.endswith(("/", os.sep)) or Path(output).is_dir()


def _target_path(output: str | None, filename: str) -> Path:
    if output is None:
        return Path.cwd() / filename
    output_path = Path(output).expanduser()
    if output.endswith(("/", os.sep)) or output_path.is_dir():
        return output_path / filename
    return output_path


def _content_disposition_filename(header: str | None) -> str | None:
    if not header:
        return None
    star_match = re.search(r"filename\*\s*=\s*UTF-8''([^;]+)", header, flags=re.IGNORECASE)
    if star_match:
        return _safe_filename(unquote(star_match.group(1).strip().strip('"')))
    match = re.search(r'filename\s*=\s*"([^"]+)"', header, flags=re.IGNORECASE)
    if match:
        return _safe_filename(match.group(1))
    match = re.search(r"filename\s*=\s*([^;]+)", header, flags=re.IGNORECASE)
    if match:
        return _safe_filename(match.group(1).strip().strip('"'))
    return None


async def _resolve_signed_url(
    client: Any,
    source: DownloadSource,
    *,
    timeout: float,
    reporter: DebugReporter | None,
) -> ResolvedDownload:
    if source.direct_url is not None:
        return ResolvedDownload(url=source.direct_url, source=source)
    if client is None:
        raise ConfigError("This file source requires a Kaiten profile.")
    if source.endpoint_path is None:
        raise ValidationError("Cannot resolve file source without endpoint path.")
    _emit_debug(reporter, f"download: resolving file endpoint {source.endpoint_path}")
    response = await client.get(source.endpoint_path, params=RESOLVE_QUERY, timeout=timeout)
    if not isinstance(response, dict) or not isinstance(response.get("url"), str):
        raise TransportError("Kaiten did not return a downloadable URL for this file.")
    return ResolvedDownload(url=response["url"], source=source)


async def _download_once(
    url: str,
    *,
    target_path: Path,
    output: str | None,
    continue_enabled: bool,
    overwrite: bool,
    timeout: float,
    reporter: DebugReporter | None,
    client: Any,
) -> DownloadResult | int:
    part_path = _part_path(target_path)
    if part_path.exists() and not continue_enabled:
        if overwrite:
            part_path.unlink()
        else:
            raise ValidationError(
                f"Partial file already exists: {part_path}. Use --continue or --overwrite."
            )

    resume_from = part_path.stat().st_size if continue_enabled and part_path.exists() else 0
    headers = {"Range": f"bytes={resume_from}-"} if resume_from > 0 else None
    if resume_from > 0:
        _emit_debug(reporter, f"download: resuming from byte {resume_from}")

    async with httpx.AsyncClient(follow_redirects=True) as http:
        started = time.perf_counter()
        status_code: int | None = None
        try:
            async with http.stream("GET", url, headers=headers, timeout=timeout) as response:
                status_code = response.status_code
                if response.status_code in SIGNED_URL_REFRESH_STATUSES:
                    return response.status_code
                if resume_from > 0 and response.status_code != 206:
                    raise TransportError(
                        "Server did not honor the Range request for the existing .part file. "
                        "Use --overwrite to restart the download."
                    )
                if resume_from == 0 and response.status_code != 200:
                    raise TransportError(f"File download failed with HTTP {response.status_code}.")

                remote_filename = _content_disposition_filename(
                    response.headers.get("content-disposition")
                )
                if remote_filename and _output_allows_remote_filename(output) and resume_from == 0:
                    remote_target = _target_path(output, remote_filename)
                    if remote_target != target_path and not _part_path(remote_target).exists():
                        target_path = remote_target
                        part_path = _part_path(target_path)

                if target_path.exists() and not overwrite:
                    raise ValidationError(
                        f"Output file already exists: {target_path}. Use --overwrite to replace it."
                    )
                if part_path.exists() and not continue_enabled:
                    raise ValidationError(
                        f"Partial file already exists: {part_path}. Use --continue or --overwrite."
                    )

                target_path.parent.mkdir(parents=True, exist_ok=True)
                mode = "ab" if resume_from > 0 else "wb"
                with part_path.open(mode) as file_obj:
                    async for chunk in response.aiter_bytes(CHUNK_SIZE):
                        if chunk:
                            file_obj.write(chunk)

                part_path.replace(target_path)
                return DownloadResult(
                    path=target_path,
                    bytes_written=target_path.stat().st_size,
                    resumed=resume_from > 0,
                    content_type=response.headers.get("content-type"),
                    status_code=response.status_code,
                )
        except httpx.TimeoutException as exc:
            raise TransportError(f"Timeout downloading file: {exc}") from exc
        except httpx.HTTPError as exc:
            raise TransportError(f"Connection error downloading file: {exc}") from exc
        finally:
            if getattr(client, "execution_context", None) is not None:
                path = urlparse(url).path or "/"
                client.execution_context.stats.record_http_attempt(
                    source="download",
                    method="GET",
                    path=path,
                    wait_ms=(time.perf_counter() - started) * 1000.0,
                    status_code=status_code,
                    error=status_code is None,
                )


async def _download_with_refresh(
    client: Any,
    resolved: ResolvedDownload,
    payload: dict[str, Any],
    *,
    timeout: float,
    reporter: DebugReporter | None,
) -> DownloadResult:
    continue_enabled = bool(payload.get("continue", True))
    overwrite = bool(payload.get("overwrite", False))
    output = _payload_str(payload, "output")
    suggested_name = _suggested_name(payload, resolved.source, resolved.url)
    target_path = _target_path(output, suggested_name)

    for attempt in range(2):
        result = await _download_once(
            resolved.url,
            target_path=target_path,
            output=output,
            continue_enabled=continue_enabled,
            overwrite=overwrite,
            timeout=timeout,
            reporter=reporter,
            client=client,
        )
        if isinstance(result, DownloadResult):
            return result
        if resolved.source.direct_url is not None:
            raise TransportError(f"File download failed with HTTP {result}.")
        if attempt == 1:
            raise TransportError(
                f"File download failed with HTTP {result} after refreshing signed URL."
            )
        _emit_debug(reporter, "download: signed URL expired, resolving it again")
        resolved = await _resolve_signed_url(
            client, resolved.source, timeout=timeout, reporter=reporter
        )

    raise TransportError("File download failed.")


async def execute_file_download(
    client: Any,
    tool: ToolSpec,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter: DebugReporter | None,
) -> dict[str, Any]:
    del tool, path, query, body
    source = resolve_download_source(payload)
    resolved = await _resolve_signed_url(client, source, timeout=timeout, reporter=reporter)
    result = await _download_with_refresh(
        client, resolved, payload, timeout=timeout, reporter=reporter
    )
    return {
        "path": str(result.path),
        "bytes": result.bytes_written,
        "resumed": result.resumed,
        "source_kind": source.kind,
        "entity_type": source.entity_type,
        "file_id": source.file_id,
        "content_type": result.content_type,
        "status_code": result.status_code,
    }


async def execute_file_upload(
    client: Any,
    tool: ToolSpec,
    payload: dict[str, Any],
    path: str,
    query: dict[str, Any] | None,
    body: dict[str, Any] | None,
    timeout: float,
    reporter: DebugReporter | None,
) -> dict[str, Any]:
    del tool, query, body
    if client is None:
        raise ConfigError("This command requires a Kaiten profile.")

    file_path = _upload_file_path(payload)
    content_type = _upload_content_type(file_path)
    _emit_debug(reporter, f"upload: sending {file_path} as multipart field file")
    try:
        with file_path.open("rb") as file_obj:
            return await client.put(
                path,
                files={"file": (file_path.name, file_obj, content_type)},
                timeout=timeout,
            )
    except OSError as exc:
        raise ValidationError(f"Cannot read upload file {file_path}: {exc}") from exc
