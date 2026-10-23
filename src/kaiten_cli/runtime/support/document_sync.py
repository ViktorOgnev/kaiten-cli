"""Explicit Yjs content transport. Failures never trigger automatic API replacement."""

from __future__ import annotations

import asyncio
import contextlib
import json
import re
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import click

from kaiten_cli.errors import CliError, ConfigError, TransportError, ValidationError
from kaiten_cli.i18n import tr
from kaiten_cli.runtime.support.documents import markdown_to_prosemirror

HELPER_PATH = Path(__file__).resolve().parents[2] / "assets" / "document_yjs.cjs"
MAX_IPC_BYTES = 16 * 1024 * 1024


def _node_error() -> ConfigError:
    return ConfigError(
        tr(
            "Could not update the document through Yjs: Node.js 20+ is required. No write was performed. Automatic API fallback is disabled because it may duplicate the document content."
        )
    )


async def find_node() -> str:
    """Check an existing runtime; never download or install anything."""
    node = shutil.which("node")
    if node is None:
        raise _node_error()
    try:
        process = await asyncio.create_subprocess_exec(
            node, "--version", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
        )
    except OSError as exc:
        raise _node_error() from exc
    try:
        output, _ = await asyncio.wait_for(process.communicate(), timeout=5)
    except (TimeoutError, asyncio.CancelledError) as exc:
        with contextlib.suppress(ProcessLookupError):
            process.kill()
        await process.wait()
        if isinstance(exc, asyncio.CancelledError):
            raise
        raise _node_error() from None
    version = re.fullmatch(rb"v(\d+)\.\d+\.\d+\s*", output)
    if process.returncode or version is None or int(version[1]) < 20:
        raise _node_error()
    if not HELPER_PATH.is_file():
        raise ConfigError(
            tr("The bundled Yjs helper is missing. Reinstall kaiten-cli. No write was performed.")
        )
    return node


def socket_origin(value: str) -> str:
    parsed = urlsplit(value)
    try:
        port = parsed.port
    except ValueError:
        port = -1
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
        or port == -1
    ):
        raise ValidationError(
            tr(
                "--socket-url must be an http(s) origin without credentials, path, query or fragment."
            )
        )
    return value.rstrip("/")


def sync_error(code: str, *, attempted: bool, acknowledged: bool) -> CliError:
    if acknowledged:
        message = tr(
            "The Yjs update was acknowledged, but its saved content could not be verified. Concurrent edits may have changed it. No automatic retry or API fallback was performed."
        )
    elif attempted:
        message = tr(
            "No confirmation was received. The update may have been saved; the write result is unknown. No automatic retry or API fallback was performed."
        )
    else:
        message = tr(
            "Yjs update failed before sending content ({value_0}). No content update was sent. No API fallback was performed.",
            value_0=code,
        )
    return CliError(
        message,
        5,
        "document_sync_error",
        {"reason": code, "write_attempted": attempted, "acknowledged": acknowledged},
    )


async def run_helper(
    node: str, request: dict[str, Any], client: Any, timeout: float
) -> dict[str, Any]:
    context = client.execution_context
    stats: dict[str, Any] = {
        "transport": "socket.io",
        "connection_attempt_count": 0,
        "update_attempt_count": 0,
        "ack_count": 0,
        "verification_count": 0,
    }
    if context is not None:
        context.stats.document_sync = stats
    attempted = False
    acknowledged = False
    try:
        process = await asyncio.create_subprocess_exec(
            node,
            str(HELPER_PATH),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            limit=MAX_IPC_BYTES,
        )
    except OSError as exc:
        raise _node_error() from exc

    async def exchange() -> dict[str, Any]:
        nonlocal attempted, acknowledged
        assert process.stdin is not None and process.stdout is not None
        process.stdin.write((json.dumps(request, ensure_ascii=False) + "\n").encode())
        await process.stdin.drain()
        while line := await process.stdout.readline():
            message = json.loads(line)
            event = message.get("event")
            if event == "connecting":
                stats["connection_attempt_count"] += 1
            elif event == "write_ready":
                if attempted:
                    raise ValueError("duplicate write request")
                # Invalidate before releasing the helper to send a mutation, including
                # ambiguous failures. Do not count sockets as HTTP requests.
                if context is not None:
                    await context.invalidate_after_mutation()
                attempted = True
                stats["update_attempt_count"] = 1
                process.stdin.write(b'{"action":"write"}\n')
                await process.stdin.drain()
            elif event == "acknowledged":
                acknowledged = True
                stats["ack_count"] = 1
            elif event == "result":
                result = message.get("result")
                if not isinstance(result, dict) or result.get("status") not in {
                    "verified",
                    "unchanged",
                }:
                    raise ValueError("invalid helper result")
                if result["status"] == "verified" and not acknowledged:
                    raise ValueError("missing acknowledgement")
                stats["verification_count"] = 1
                stats["outcome"] = result["status"]
                return result
            elif event == "error":
                code = message.get("code", "helper_error")
                # Only expose protocol codes, never arbitrary child output or secrets.
                if not isinstance(code, str) or not re.fullmatch(r"[a-z_]{1,64}", code):
                    code = "helper_error"
                raise sync_error(code, attempted=attempted, acknowledged=acknowledged)
            else:
                raise ValueError("unexpected helper event")
        raise sync_error("helper_exit", attempted=attempted, acknowledged=acknowledged)

    try:
        return await asyncio.wait_for(exchange(), timeout=timeout + 5)
    except (TimeoutError, ValueError, BrokenPipeError, ConnectionError) as exc:
        reason = "timeout" if isinstance(exc, TimeoutError) else "helper_protocol_error"
        raise sync_error(reason, attempted=attempted, acknowledged=acknowledged) from None
    finally:
        if process.returncode is None:
            with contextlib.suppress(ProcessLookupError):
                process.kill()
        await process.wait()
        if process.stdin is not None:
            process.stdin.close()
        # A failed attempt must not leave a subsequently filled read cache behind.
        if attempted and context is not None:
            await context.invalidate_after_mutation()
        stats.setdefault("outcome", "unverified" if attempted else "not_sent")


async def execute_document_update(client, tool, payload, path, query, body, timeout, reporter):
    del tool, reporter
    if client is None:
        raise ConfigError(tr("This command requires a Kaiten profile."))
    if payload.get("content_mode", "api") != "yjs":
        if "data" in payload or "text" in payload:
            click.echo(
                tr(
                    "Warning: updating content through the API may duplicate the entire document when syncing with an open editor."
                ),
                err=True,
            )
        return await client.patch(path, params=query, json=body, timeout=timeout)

    node = await find_node()
    origin = socket_origin(payload.get("socket_url") or client.root_url)
    document = await client.get(path, timeout=timeout)
    if not isinstance(document, dict):
        raise ValidationError(tr("Kaiten returned an unexpected document payload."))
    schema_version = document.get("schema_version")
    if not schema_version:
        # Public API serialization may omit this field. The UI likewise uses
        # the installation's latest schema; never guess v1 for modern content.
        schema = await client.get("/document-schemas/latest", timeout=timeout)
        schema_version = schema.get("version") if isinstance(schema, dict) else None
    if not isinstance(schema_version, str) or not schema_version:
        raise ValidationError(
            tr("Kaiten did not report a document schema version. No content update was sent.")
        )
    token = await client.get("/token-please", timeout=timeout)
    if not isinstance(token, dict) or not isinstance(token.get("token"), str) or not token["token"]:
        raise TransportError(tr("Could not obtain a websocket JWT. No content update was sent."))
    data = payload["data"] if "data" in payload else markdown_to_prosemirror(payload["text"])
    return await run_helper(
        node,
        {
            "documentId": payload["document_uid"],
            "schemaVersion": schema_version,
            "socketUrl": origin,
            "token": token["token"],
            "data": data,
            "timeoutMs": int(timeout * 1000),
        },
        client,
        timeout,
    )
