"""HTTP gateway that exposes kaiten-cli as a chat agent endpoint."""

from __future__ import annotations

import argparse
import contextlib
import hmac
import ipaddress
import json
import logging
import os
import signal
import subprocess
import tempfile
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

from kaiten_cli import __version__
from kaiten_cli.app import _agent_help_payload


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787
DEFAULT_TIMEOUT_SECONDS = 180
DEFAULT_REASONING_EFFORT = "low"
DEFAULT_CODEX_BIN = "codex"
MAX_REQUEST_BODY_BYTES = 1024 * 1024
MAX_CONCURRENT_CODEX_EXECUTIONS = 2
REQUEST_READ_TIMEOUT_SECONDS = 10.0
SKILL_NAMES = ("kaiten-cli-heavy-data", "kaiten-cli-metrics")

LOGGER = logging.getLogger(__name__)

# Keep child credentials and process settings deliberately narrow. In particular,
# KAITEN_LIVE and arbitrary secrets from the gateway environment must not reach Codex.
CODEX_ENV_ALLOWLIST = frozenset(
    {
        "ALL_PROXY",
        "APPDATA",
        "CODEX_HOME",
        "COMSPEC",
        "HOME",
        "HTTPS_PROXY",
        "HTTP_PROXY",
        "KAITEN_CLI_CONFIG_PATH",
        "KAITEN_DOMAIN",
        "KAITEN_TOKEN",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "LOCALAPPDATA",
        "LOGNAME",
        "NO_PROXY",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_ORG_ID",
        "OPENAI_PROJECT_ID",
        "PATH",
        "PATHEXT",
        "REQUESTS_CA_BUNDLE",
        "SHELL",
        "SSL_CERT_DIR",
        "SSL_CERT_FILE",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "TMPDIR",
        "USER",
        "USERPROFILE",
        "XDG_CACHE_HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "all_proxy",
        "http_proxy",
        "https_proxy",
        "no_proxy",
    }
)
SENSITIVE_CHILD_ENV_KEYS = frozenset(
    {
        "ALL_PROXY",
        "HTTPS_PROXY",
        "HTTP_PROXY",
        "KAITEN_TOKEN",
        "OPENAI_API_KEY",
        "OPENAI_ORG_ID",
        "OPENAI_PROJECT_ID",
        "all_proxy",
        "http_proxy",
        "https_proxy",
    }
)

SYSTEM_PROMPT = """You are Kaiten Agent, an assistant embedded into Kaiten.
Use kaiten-cli as the primary tool surface for Kaiten data.
Start with discovery commands before heavy reads:
- kaiten agent-help
- kaiten search-tools "<query>"
- kaiten describe <tool>
- kaiten examples <tool>

Prefer machine-readable, narrow, and bulk workflows:
- use --json for tool output
- use --compact and --fields to reduce payload
- prefer cards list-all, batch commands, snapshots, and query commands over per-card loops
- inspect cache/runtime stats before widening expensive reads
- reuse local scripts that are available in the configured workdir or extra directories

This gateway is always read-only. Never mutate Kaiten; explain that writes must be run
outside this gateway when a user asks for a write operation.
Answer in the user's language unless they request otherwise.
"""

SKILL_FALLBACKS = {
    "kaiten-cli-heavy-data": (
        "Use bulk commands, snapshots, compact fields, and cache-aware workflows. "
        "Avoid one CLI process or API request per card when a batch command exists."
    ),
    "kaiten-cli-metrics": (
        "For metrics, start from topology, bulk card fields, snapshots/query metrics, "
        "space activity, chart tools, and card-location-history batch-get only when needed."
    ),
}


@dataclass(frozen=True)
class AgentGatewayConfig:
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    codex_bin: str = DEFAULT_CODEX_BIN
    codex_model: str | None = None
    reasoning_effort: str = DEFAULT_REASONING_EFFORT
    workdir: Path = Path.cwd()
    extra_dirs: tuple[Path, ...] = ()
    skip_git_repo_check: bool = False
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    bearer_token: str | None = None
    repo_root: Path = Path.cwd()


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _safe_read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def load_skill_texts(repo_root: Path) -> dict[str, str]:
    skills: dict[str, str] = {}
    for skill_name in SKILL_NAMES:
        skill_path = repo_root / "skills" / skill_name / "SKILL.md"
        skills[skill_name] = _safe_read_text(skill_path) or SKILL_FALLBACKS[skill_name]
    return skills


def build_prompt(payload: dict[str, Any], *, repo_root: Path | None = None) -> str:
    repo = repo_root or default_repo_root()
    messages = payload.get("messages") if isinstance(payload.get("messages"), list) else []
    context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
    endpoint_instructions = str(payload.get("instructions") or "").strip()

    parts = [
        SYSTEM_PROMPT.strip(),
        "",
        "Endpoint instructions from Kaiten:",
        endpoint_instructions or "(none)",
        "",
        "kaiten agent-help JSON:",
        _json_dumps(_agent_help_payload()),
        "",
        "Bundled skills:",
        _json_dumps(load_skill_texts(repo)),
        "",
        "Kaiten runtime context:",
        _json_dumps(context),
        "",
        "Conversation messages:",
        _json_dumps(messages),
        "",
        "Return a concise final answer only. Mention exact commands when they materially help.",
    ]
    return "\n".join(parts)


def build_codex_command(config: AgentGatewayConfig, last_message_path: Path) -> list[str]:
    command = [
        config.codex_bin,
        "exec",
        "--sandbox",
        "read-only",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--cd",
        str(config.workdir),
        "--output-last-message",
        str(last_message_path),
    ]

    for extra_dir in config.extra_dirs:
        command.extend(["--add-dir", str(extra_dir)])

    if config.skip_git_repo_check:
        command.append("--skip-git-repo-check")

    if config.codex_model:
        command.extend(["--model", config.codex_model])

    if config.reasoning_effort:
        command.extend(["-c", f'model_reasoning_effort="{config.reasoning_effort}"'])

    command.append("-")
    return command


def _codex_environment(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    source = os.environ if environ is None else environ
    child_env = {key: source[key] for key in CODEX_ENV_ALLOWLIST if key in source}
    child_env["KAITEN_CLI_READ_ONLY"] = "1"
    child_env["KAITEN_CLI_STORAGE_READ_ONLY"] = "1"
    return child_env


def _redact_child_secrets(text: str, child_env: Mapping[str, str]) -> str:
    redacted = text
    for key in SENSITIVE_CHILD_ENV_KEYS:
        value = child_env.get(key)
        if value:
            redacted = redacted.replace(value, "[REDACTED]")
    return redacted


def _run_process_group(
    command: list[str],
    *,
    input: str,
    text: bool,
    capture_output: bool,
    env: Mapping[str, str],
    timeout: int,
    check: bool,
) -> subprocess.CompletedProcess[str]:
    """Run Codex in its own process group so timeouts terminate normal descendants."""

    popen_kwargs: dict[str, Any] = {
        "stdin": subprocess.PIPE,
        "stdout": subprocess.PIPE if capture_output else None,
        "stderr": subprocess.PIPE if capture_output else None,
        "text": text,
        "env": dict(env),
    }
    if os.name == "posix":
        popen_kwargs["start_new_session"] = True
    elif os.name == "nt":  # pragma: no cover - Windows-specific containment
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    process = subprocess.Popen(command, **popen_kwargs)
    try:
        stdout, stderr = process.communicate(input=input, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        if os.name == "posix":
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
        elif os.name == "nt":  # pragma: no cover - Windows-specific containment
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                capture_output=True,
                check=False,
            )
        else:  # pragma: no cover - defensive platform fallback
            process.kill()
        process.communicate()
        raise subprocess.TimeoutExpired(
            command,
            timeout,
            output=error.output,
            stderr=error.stderr,
        ) from error

    completed = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    if check and completed.returncode:
        raise subprocess.CalledProcessError(
            completed.returncode,
            command,
            output=stdout,
            stderr=stderr,
        )
    return completed


def run_codex(
    prompt: str,
    config: AgentGatewayConfig,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> str:
    child_env = _codex_environment()
    effective_runner = runner or _run_process_group
    with tempfile.TemporaryDirectory(prefix="kaiten-agent-") as tmpdir:
        last_message_path = Path(tmpdir) / "last-message.txt"
        result = effective_runner(
            build_codex_command(config, last_message_path),
            input=prompt,
            text=True,
            capture_output=True,
            env=child_env,
            timeout=config.timeout_seconds,
            check=False,
        )

        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            safe_detail = _redact_child_secrets(detail[-4000:], child_env)
            raise RuntimeError(safe_detail or f"codex exited with {result.returncode}")

        output = _safe_read_text(last_message_path)
        if output and output.strip():
            return _redact_child_secrets(output.strip(), child_env)

        return _redact_child_secrets((result.stdout or "").strip(), child_env)


def chat_response(content: str) -> dict[str, Any]:
    return {
        "message": {
            "role": "assistant",
            "content": content,
        },
        "tool_runs": [
            {
                "type": "codex_exec",
                "sandbox": "read-only",
            }
        ],
        "artifacts": [],
        "usage": {
            "provider": "codex_exec",
        },
    }


class RequestBodyTooLarge(ValueError):
    """Raised when an HTTP request exceeds the gateway's fixed body limit."""


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    if handler.headers.get("Transfer-Encoding"):
        raise ValueError("Transfer-Encoding request bodies are not supported")

    try:
        content_length = int(handler.headers.get("Content-Length") or 0)
    except ValueError as error:
        raise ValueError("Content-Length must be an integer") from error

    if content_length < 0:
        raise ValueError("Content-Length must not be negative")
    if content_length > MAX_REQUEST_BODY_BYTES:
        raise RequestBodyTooLarge(f"Request body exceeds the {MAX_REQUEST_BODY_BYTES}-byte limit")
    if handler.headers.get_content_type() != "application/json":
        raise ValueError("Content-Type must be application/json")
    if content_length <= 0:
        raise ValueError("JSON request body is required")

    raw = handler.rfile.read(content_length)
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON body must be an object")
    return data


def _send_json(
    handler: BaseHTTPRequestHandler, status: HTTPStatus, payload: dict[str, Any]
) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status.value)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _authorized(handler: BaseHTTPRequestHandler, config: AgentGatewayConfig) -> bool:
    if not config.bearer_token:
        return True
    supplied = handler.headers.get("Authorization") or ""
    expected = f"Bearer {config.bearer_token}"
    return hmac.compare_digest(supplied.encode("utf-8"), expected.encode("utf-8"))


def _is_loopback_host(host: str) -> bool:
    normalized = host.strip().lower()
    if normalized == "localhost":
        return True
    if normalized.startswith("[") and normalized.endswith("]"):
        normalized = normalized[1:-1]
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


def validate_gateway_config(config: AgentGatewayConfig) -> None:
    if not _is_loopback_host(config.host) and not config.bearer_token:
        raise ValueError("A bearer token is required when binding to a non-loopback host")


def make_handler(config: AgentGatewayConfig) -> type[BaseHTTPRequestHandler]:
    validate_gateway_config(config)
    codex_slots = threading.BoundedSemaphore(MAX_CONCURRENT_CODEX_EXECUTIONS)

    class AgentGatewayHandler(BaseHTTPRequestHandler):
        server_version = "kaiten-agent-gateway"

        def setup(self) -> None:
            super().setup()
            self.connection.settimeout(REQUEST_READ_TIMEOUT_SECONDS)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

        def _guard_auth(self) -> bool:
            if _authorized(self, config):
                return True
            _send_json(self, HTTPStatus.UNAUTHORIZED, {"message": "Unauthorized"})
            return False

        def do_GET(self) -> None:  # noqa: N802
            if not self._guard_auth():
                return
            if self.path != "/health":
                _send_json(self, HTTPStatus.NOT_FOUND, {"message": "Not found"})
                return
            _send_json(
                self,
                HTTPStatus.OK,
                {
                    "ok": True,
                    "name": "kaiten-agent-gateway",
                    "version": __version__,
                    "capabilities": ["health", "chat", "kaiten-cli", "codex-exec"],
                },
            )

        def do_POST(self) -> None:  # noqa: N802
            if not self._guard_auth():
                return
            if self.path != "/v1/chat":
                _send_json(self, HTTPStatus.NOT_FOUND, {"message": "Not found"})
                return

            try:
                payload = _read_json(self)
                prompt = build_prompt(payload, repo_root=config.repo_root)
            except RequestBodyTooLarge as error:
                self.close_connection = True
                _send_json(self, HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"message": str(error)})
                return
            except TimeoutError:
                self.close_connection = True
                _send_json(self, HTTPStatus.REQUEST_TIMEOUT, {"message": "Request body timed out"})
                return
            except json.JSONDecodeError as error:
                _send_json(self, HTTPStatus.BAD_REQUEST, {"message": f"Invalid JSON: {error}"})
                return
            except ValueError as error:
                _send_json(self, HTTPStatus.BAD_REQUEST, {"message": str(error)})
                return

            if not codex_slots.acquire(blocking=False):
                _send_json(
                    self,
                    HTTPStatus.TOO_MANY_REQUESTS,
                    {"message": "Too many concurrent agent requests"},
                )
                return

            try:
                content = run_codex(prompt, config)
            except subprocess.TimeoutExpired:
                LOGGER.warning("Codex execution timed out after %s seconds", config.timeout_seconds)
                _send_json(self, HTTPStatus.GATEWAY_TIMEOUT, {"message": "Agent request timed out"})
                return
            except Exception as error:  # pragma: no cover - behavior is tested via the handler
                LOGGER.error("Codex execution failed (%s)", type(error).__name__)
                _send_json(self, HTTPStatus.BAD_GATEWAY, {"message": "Agent execution failed"})
                return
            finally:
                codex_slots.release()

            if not content:
                _send_json(
                    self, HTTPStatus.BAD_GATEWAY, {"message": "Codex returned an empty response"}
                )
                return

            _send_json(self, HTTPStatus.OK, chat_response(content))

    return AgentGatewayHandler


def config_from_args(args: argparse.Namespace) -> AgentGatewayConfig:
    repo_root = Path(
        args.repo_root or os.environ.get("KAITEN_AGENT_REPO_ROOT") or default_repo_root()
    )
    workdir = Path(args.workdir or os.environ.get("KAITEN_AGENT_WORKDIR") or repo_root)
    extra_dir_values = list(args.add_dir or [])
    env_extra_dirs = os.environ.get("KAITEN_AGENT_EXTRA_DIRS")
    if env_extra_dirs:
        extra_dir_values.extend(env_extra_dirs.split(os.pathsep))

    return AgentGatewayConfig(
        host=args.host,
        port=args.port,
        codex_bin=args.codex_bin or os.environ.get("KAITEN_AGENT_CODEX_BIN") or DEFAULT_CODEX_BIN,
        codex_model=args.codex_model or os.environ.get("KAITEN_AGENT_CODEX_MODEL") or None,
        reasoning_effort=(
            args.reasoning_effort
            or os.environ.get("KAITEN_AGENT_CODEX_REASONING_EFFORT")
            or DEFAULT_REASONING_EFFORT
        ),
        workdir=workdir.resolve(),
        extra_dirs=tuple(Path(value).expanduser().resolve() for value in extra_dir_values if value),
        skip_git_repo_check=args.skip_git_repo_check,
        timeout_seconds=int(
            args.timeout_seconds
            or os.environ.get("KAITEN_AGENT_TIMEOUT_SECONDS")
            or DEFAULT_TIMEOUT_SECONDS
        ),
        bearer_token=args.bearer_token or os.environ.get("KAITEN_AGENT_BEARER_TOKEN") or None,
        repo_root=repo_root.resolve(),
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local Kaiten Agent HTTP gateway.")
    parser.add_argument("--host", default=os.environ.get("KAITEN_AGENT_HOST", DEFAULT_HOST))
    parser.add_argument(
        "--port", type=int, default=int(os.environ.get("KAITEN_AGENT_PORT", DEFAULT_PORT))
    )
    parser.add_argument("--codex-bin", default=None)
    parser.add_argument("--codex-model", default=None)
    parser.add_argument("--reasoning-effort", default=None)
    parser.add_argument("--workdir", default=None)
    parser.add_argument("--add-dir", action="append", default=None)
    parser.add_argument("--skip-git-repo-check", action="store_true")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=None)
    parser.add_argument("--bearer-token", default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    config = config_from_args(parse_args(argv))
    server = ThreadingHTTPServer((config.host, config.port), make_handler(config))
    print(f"kaiten-agent-gateway listening on http://{config.host}:{config.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
