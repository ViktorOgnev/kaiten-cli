"""Best-effort update checks for interactive CLI runs.

The update path is deliberately isolated from normal command execution: it only
runs after a successful human-facing command, never changes JSON output, and
fails open when install metadata, Git, the network, or the installer is absent.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlsplit, urlunsplit

import click
from platformdirs import user_cache_path

from kaiten_cli.runtime.fs_security import (
    PRIVATE_FILE_MODE,
    secure_directory,
    secure_existing_file,
)


PACKAGE_NAME = "kaiten-cli"
UPDATE_CHECK_ENV = "KAITEN_CLI_UPDATE_CHECK"
UPDATE_CACHE_SCHEMA_VERSION = 1
UPDATE_CHECK_INTERVAL_SECONDS = 24 * 60 * 60
GIT_CHECK_TIMEOUT_SECONDS = 8
UV_DETECTION_TIMEOUT_SECONDS = 2

_RELEASE_TAG_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_VERSION_RE = re.compile(r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_COMMIT_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
_REMOTE_GIT_SCHEMES = frozenset({"git", "http", "https", "ssh"})
_FALSE_VALUES = frozenset({"0", "false", "no", "off"})


@dataclass(frozen=True, slots=True)
class InstallSource:
    """A supported remote Git installation and its owning installer."""

    manager: str
    manager_executable: str | None
    git_url: str
    installed_version: str
    requested_revision: str | None = None
    subdirectory: str | None = None

    @property
    def pinned_release(self) -> bool:
        return _parse_release_tag(self.requested_revision) is not None

    @property
    def immutable_commit(self) -> bool:
        return bool(self.requested_revision and _COMMIT_RE.fullmatch(self.requested_revision))


@dataclass(frozen=True, slots=True)
class UpdateCandidate:
    source: InstallSource
    latest_tag: str
    source_key: str


def update_cache_path() -> Path:
    return user_cache_path("kaiten-cli") / "update-check.json"


def _normalize_package_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def _read_json_text(value: str | None) -> dict[str, Any] | None:
    if not value:
        return None
    try:
        payload = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _read_json_file(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _pipx_metadata(prefix: Path) -> dict[str, Any] | None:
    payload = _read_json_file(prefix / "pipx_metadata.json")
    if payload is None:
        return None
    main_package = payload.get("main_package")
    if not isinstance(main_package, dict):
        return None
    package = main_package.get("package")
    if not isinstance(package, str) or _normalize_package_name(package) != PACKAGE_NAME:
        return None
    suffix = main_package.get("suffix")
    if suffix not in (None, ""):
        return None
    return payload


def _path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except (OSError, ValueError):
        return False
    return True


def _uv_tool_executable(prefix: Path) -> str | None:
    executable = shutil.which("uv")
    if executable is None:
        return None
    try:
        result = subprocess.run(
            [executable, "tool", "dir"],
            capture_output=True,
            text=True,
            timeout=UV_DETECTION_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return executable if _path_is_within(prefix, Path(result.stdout.strip())) else None


def _git_transport_url(value: str) -> str:
    return value[4:] if value.startswith("git+") else value


def _is_remote_git_url(value: str) -> bool:
    parsed = urlsplit(_git_transport_url(value))
    return bool(parsed.hostname and parsed.scheme.lower() in _REMOTE_GIT_SCHEMES)


def detect_install_source() -> InstallSource | None:
    """Return a supported install source, or ``None`` for local/unknown installs."""

    try:
        distribution = metadata.distribution(PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return None

    direct_url = _read_json_text(distribution.read_text("direct_url.json"))
    if direct_url is None or isinstance(direct_url.get("dir_info"), dict):
        return None

    vcs_info = direct_url.get("vcs_info")
    git_url = direct_url.get("url")
    if (
        not isinstance(vcs_info, dict)
        or vcs_info.get("vcs") != "git"
        or not isinstance(git_url, str)
        or not _is_remote_git_url(git_url)
    ):
        return None

    requested_revision = vcs_info.get("requested_revision")
    if not isinstance(requested_revision, str) or not requested_revision.strip():
        requested_revision = None
    subdirectory = direct_url.get("subdirectory")
    if not isinstance(subdirectory, str) or not subdirectory.strip():
        subdirectory = None

    prefix = Path(sys.prefix)
    pipx = _pipx_metadata(prefix)
    if pipx is not None:
        manager = "pipx"
        manager_executable = shutil.which("pipx")
    else:
        uv_executable = _uv_tool_executable(prefix)
        if uv_executable is not None:
            manager = "uv"
            manager_executable = uv_executable
        else:
            manager = "pip"
            manager_executable = sys.executable

    return InstallSource(
        manager=manager,
        manager_executable=manager_executable,
        git_url=_git_transport_url(git_url),
        installed_version=distribution.version,
        requested_revision=requested_revision,
        subdirectory=subdirectory,
    )


def _parse_release_tag(value: str | None) -> tuple[int, int, int] | None:
    if value is None:
        return None
    match = _RELEASE_TAG_RE.fullmatch(value.strip())
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())


def _parse_installed_version(value: str) -> tuple[int, int, int] | None:
    match = _VERSION_RE.fullmatch(value.strip())
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())


def _latest_remote_release(git_url: str) -> tuple[bool, str | None]:
    git = shutil.which("git")
    if git is None:
        return False, None
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["SSH_ASKPASS_REQUIRE"] = "never"
    try:
        result = subprocess.run(
            [git, "ls-remote", "--tags", "--refs", git_url, "refs/tags/v*"],
            capture_output=True,
            text=True,
            timeout=GIT_CHECK_TIMEOUT_SECONDS,
            check=False,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, None
    if result.returncode != 0:
        return False, None

    releases: list[tuple[tuple[int, int, int], str]] = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) != 2 or not parts[1].startswith("refs/tags/"):
            continue
        tag = parts[1].removeprefix("refs/tags/")
        version = _parse_release_tag(tag)
        if version is not None:
            releases.append((version, tag))
    if not releases:
        return True, None
    return True, max(releases)[1]


def _display_git_source(git_url: str) -> str:
    parsed = urlsplit(git_url)
    if not parsed.hostname:
        return "remote Git source"
    host = parsed.hostname
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    return f"{host}{parsed.path}"


def _source_key(source: InstallSource) -> str:
    display = _display_git_source(source.git_url).lower()
    material = f"{display}\0{source.subdirectory or ''}".encode()
    return hashlib.sha256(material).hexdigest()


def _empty_cache() -> dict[str, Any]:
    return {"schema_version": UPDATE_CACHE_SCHEMA_VERSION, "sources": {}}


def _load_cache() -> dict[str, Any]:
    path = update_cache_path()
    try:
        secure_existing_file(path)
    except OSError:
        return _empty_cache()
    payload = _read_json_file(path)
    if (
        payload is None
        or payload.get("schema_version") != UPDATE_CACHE_SCHEMA_VERSION
        or not isinstance(payload.get("sources"), dict)
    ):
        return _empty_cache()
    return payload


def _save_cache(payload: dict[str, Any]) -> None:
    path = update_cache_path()
    temporary_path: Path | None = None
    descriptor: int | None = None
    try:
        secure_directory(path.parent)
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        temporary_path = Path(temporary_name)
        fchmod = getattr(os, "fchmod", None)
        if fchmod is not None:
            fchmod(descriptor, PRIVATE_FILE_MODE)
        else:  # pragma: no cover - Windows fallback
            temporary_path.chmod(PRIVATE_FILE_MODE)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = None
            json.dump(payload, stream, ensure_ascii=False, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary_path.replace(path)
        secure_existing_file(path)
    except OSError:
        return
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            with contextlib.suppress(OSError):
                temporary_path.unlink(missing_ok=True)


def _record_for(cache: dict[str, Any], source_key: str) -> dict[str, Any]:
    sources = cache.setdefault("sources", {})
    existing = sources.get(source_key)
    if isinstance(existing, dict):
        return existing
    record: dict[str, Any] = {}
    sources[source_key] = record
    return record


def check_for_update(source: InstallSource, *, now: float | None = None) -> UpdateCandidate | None:
    """Return a newer stable release while respecting check and prompt TTLs."""

    installed_version = _parse_installed_version(source.installed_version)
    if installed_version is None or source.immutable_commit:
        return None

    current_time = time.time() if now is None else now
    key = _source_key(source)
    cache = _load_cache()
    record = _record_for(cache, key)
    checked_at = record.get("checked_at")
    latest_tag = record.get("latest_tag")
    cache_is_fresh = isinstance(checked_at, (int, float)) and (
        current_time - float(checked_at) < UPDATE_CHECK_INTERVAL_SECONDS
    )

    if not cache_is_fresh:
        succeeded, fetched_tag = _latest_remote_release(source.git_url)
        record["checked_at"] = current_time
        if succeeded:
            latest_tag = fetched_tag
            record["latest_tag"] = fetched_tag
        _save_cache(cache)

    if not isinstance(latest_tag, str):
        return None
    latest_version = _parse_release_tag(latest_tag)
    if latest_version is None or latest_version <= installed_version:
        return None

    prompted_tag = record.get("prompted_tag")
    prompted_at = record.get("prompted_at")
    if (
        prompted_tag == latest_tag
        and isinstance(prompted_at, (int, float))
        and current_time - float(prompted_at) < UPDATE_CHECK_INTERVAL_SECONDS
    ):
        return None
    return UpdateCandidate(source=source, latest_tag=latest_tag, source_key=key)


def _record_prompted(candidate: UpdateCandidate, *, now: float | None = None) -> None:
    cache = _load_cache()
    record = _record_for(cache, candidate.source_key)
    record["prompted_tag"] = candidate.latest_tag
    record["prompted_at"] = time.time() if now is None else now
    _save_cache(cache)


def _git_install_spec(source: InstallSource, revision: str | None) -> str:
    url = urlunsplit(urlsplit(source.git_url))
    spec = f"git+{url}"
    if revision:
        spec = f"{spec}@{revision}"
    if source.subdirectory:
        spec = f"{spec}#{urlencode({'subdirectory': source.subdirectory})}"
    return spec


def build_update_command(source: InstallSource, latest_tag: str) -> list[str] | None:
    """Build a shell-free installer command for the detected install mode."""

    executable = source.manager_executable
    if executable is None:
        return None
    if source.pinned_release:
        specification = _git_install_spec(source, latest_tag)
        if source.manager == "pipx":
            return [executable, "install", "--force", specification]
        if source.manager == "uv":
            return [executable, "tool", "install", "--force", specification]
        return [executable, "-m", "pip", "install", "--upgrade", specification]

    if source.manager == "pipx":
        return [executable, "upgrade", PACKAGE_NAME]
    if source.manager == "uv":
        return [executable, "tool", "upgrade", PACKAGE_NAME]
    return [
        executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        _git_install_spec(source, source.requested_revision),
    ]


def _perform_update(candidate: UpdateCandidate) -> int:
    command = build_update_command(candidate.source, candidate.latest_tag)
    if command is None:
        click.echo(
            f"Unable to update automatically: {candidate.source.manager} is not available on PATH.",
            err=True,
        )
        return 1
    try:
        result = subprocess.run(command, check=False)
    except OSError as exc:
        click.echo(
            f"Automatic update failed: {candidate.source.manager} could not be started "
            f"({type(exc).__name__}).",
            err=True,
        )
        return 1
    if result.returncode != 0:
        click.echo(
            f"Automatic update failed in {candidate.source.manager} "
            f"(exit code {result.returncode}).",
            err=True,
        )
        return result.returncode if result.returncode > 0 else 1
    click.echo(
        f"kaiten-cli {candidate.latest_tag.removeprefix('v')} installed. "
        "The new version will be used on the next run.",
        err=True,
    )
    return 0


def should_check_for_updates(
    args: list[str], *, stdin: Any | None = None, stderr: Any | None = None
) -> bool:
    """Keep update traffic and prompts out of automation and exact-output modes."""

    if not args or "--json" in args or "--no-update-check" in args:
        return False
    if any(argument in {"-h", "--help", "--version"} for argument in args):
        return False
    setting = os.environ.get(UPDATE_CHECK_ENV)
    if setting is not None and setting.strip().lower() in _FALSE_VALUES:
        return False
    if os.environ.get("_KAITEN_COMPLETE"):
        return False
    input_stream = sys.stdin if stdin is None else stdin
    error_stream = sys.stderr if stderr is None else stderr
    return bool(input_stream.isatty() and error_stream.isatty())


def maybe_offer_update(args: list[str]) -> int:
    """Check and optionally install an update after a successful CLI command."""

    if not should_check_for_updates(args):
        return 0
    source = detect_install_source()
    if source is None:
        return 0
    candidate = check_for_update(source)
    if candidate is None:
        return 0

    source_display = _display_git_source(source.git_url)
    prompt = (
        f"kaiten-cli {candidate.latest_tag.removeprefix('v')} is available "
        f"(installed {source.installed_version}, source {source_display}). "
        f"Update now with {source.manager}?"
    )
    try:
        confirmed = click.confirm(prompt, default=False, err=True)
    except click.Abort:
        confirmed = False
    if not confirmed:
        _record_prompted(candidate)
        click.echo("Update skipped; this release can be offered again after 24 hours.", err=True)
        return 0
    result = _perform_update(candidate)
    if result == 0:
        _record_prompted(candidate)
    return result
