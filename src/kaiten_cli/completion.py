"""Safe installation and inspection of Click shell completion scripts."""

from __future__ import annotations

import contextlib
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import click
from click.shell_completion import get_completion_class
from platformdirs import user_data_path

from kaiten_cli.errors import ConfigError, ValidationError
from kaiten_cli.runtime.fs_security import (
    PRIVATE_DIRECTORY_MODE,
    PRIVATE_FILE_MODE,
    secure_directory,
)


SUPPORTED_SHELLS = ("bash", "zsh")
COMPLETION_VARIABLE = "_KAITEN_COMPLETE"
PROGRAM_NAME = "kaiten"
MANAGED_BLOCK_BEGIN = "# >>> kaiten-cli completion >>>"
MANAGED_BLOCK_END = "# <<< kaiten-cli completion <<<"
LEGACY_ZSH_BLOCK = """# Kaiten CLI completion
if (( $+commands[kaiten] )); then
  eval \"$(_KAITEN_COMPLETE=zsh_source kaiten)\"
fi
"""
_BASH_VERSION_RE = re.compile(r"version\s+(\d+)\.(\d+)", re.IGNORECASE)
FileSignature = tuple[int, int, int, int]


def completion_data_dir() -> Path:
    """Return the private directory used for generated completion scripts."""

    return user_data_path("kaiten-cli") / "completions"


def completion_script_path(shell: str) -> Path:
    suffix = "bash" if shell == "bash" else "zsh"
    return completion_data_dir() / f"kaiten-complete.{suffix}"


def detect_shell(shell: str | None = None) -> str:
    """Normalize an explicit shell or detect it from the conventional SHELL variable."""

    candidate = shell
    if candidate is None:
        candidate = os.environ.get("SHELL")
    normalized = Path(candidate).name.lower() if candidate else ""
    if normalized not in SUPPORTED_SHELLS:
        supported = ", ".join(SUPPORTED_SHELLS)
        if candidate:
            raise ValidationError(
                f"Unsupported shell: {candidate}. Expected one of: {supported}. "
                "Use --shell to select explicitly."
            )
        raise ValidationError(
            f"Unable to detect shell from SHELL. Use --shell with one of: {supported}."
        )
    return normalized


def default_config_path(shell: str) -> Path:
    return Path.home() / (".bashrc" if shell == "bash" else ".zshrc")


def generate_completion_source(command: click.Command, shell: str) -> str:
    """Generate a static completion registration script using Click's public API."""

    normalized = detect_shell(shell)
    completion_class = get_completion_class(normalized)
    if completion_class is None:  # pragma: no cover - guarded by SUPPORTED_SHELLS
        raise ValidationError(f"Click does not provide completion support for {normalized}.")
    source = completion_class(command, {}, PROGRAM_NAME, COMPLETION_VARIABLE).source()
    return source if source.endswith("\n") else source + "\n"


def _shell_executable(shell: str) -> str | None:
    configured = os.environ.get("SHELL")
    if configured and Path(configured).name.lower() == shell and Path(configured).is_file():
        return configured
    return shutil.which(shell)


def _bash_version(executable: str) -> tuple[int, int] | None:
    try:
        result = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    match = _BASH_VERSION_RE.search(result.stdout)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))


def _shell_support(shell: str) -> tuple[bool, str | None, str | None]:
    executable = _shell_executable(shell)
    if executable is None:
        return False, None, f"Shell executable is not available on PATH: {shell}."
    if shell == "bash":
        version = _bash_version(executable)
        if version is None:
            return False, executable, "Unable to determine Bash version; Click requires Bash 4.4+."
        if version < (4, 4):
            return (
                False,
                executable,
                f"Bash {version[0]}.{version[1]} is unsupported; Click requires Bash 4.4+.",
            )
    return True, executable, None


def _command_path() -> str | None:
    return shutil.which(PROGRAM_NAME)


def _resolve_edit_path(path: Path, *, require_owned: bool = False) -> Path:
    path = path.expanduser()
    if path.is_symlink():
        try:
            target = path.resolve(strict=True)
        except OSError as exc:
            raise ConfigError(f"Unable to resolve shell config symlink {path}: {exc}") from exc
        if not target.is_file():
            raise ConfigError(f"Shell config symlink target is not a regular file: {target}")
        path = target
    if path.exists() and not path.is_file():
        raise ConfigError(f"Shell config is not a regular file: {path}")
    getuid = getattr(os, "getuid", None)
    if require_owned and path.exists() and getuid is not None and path.stat().st_uid != getuid():
        raise ConfigError(f"Refusing to replace shell config not owned by the current user: {path}")
    return path


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ConfigError(f"Unable to read shell config at {path}: {exc}") from exc


def _existing_mode(path: Path, default: int) -> int:
    try:
        return stat.S_IMODE(path.stat().st_mode) if path.exists() else default
    except OSError as exc:
        raise ConfigError(f"Unable to inspect file mode at {path}: {exc}") from exc


def _file_signature(path: Path) -> FileSignature | None:
    try:
        if not path.exists():
            return None
        file_stat = path.stat()
    except OSError as exc:
        raise ConfigError(f"Unable to inspect file at {path}: {exc}") from exc
    return (file_stat.st_dev, file_stat.st_ino, file_stat.st_mtime_ns, file_stat.st_size)


def _read_edit_state(path: Path) -> tuple[str, FileSignature | None, int]:
    before = _file_signature(path)
    text = _read_text(path)
    after = _file_signature(path)
    if before != after:
        raise ConfigError(f"Shell config changed while it was being read: {path}")
    return text, after, _existing_mode(path, PRIVATE_FILE_MODE)


def _write_text_atomic(
    path: Path,
    text: str,
    *,
    mode: int,
    expected_signature: FileSignature | None = None,
    verify_signature: bool = False,
) -> None:
    """Atomically replace one regular file while preserving the requested POSIX mode."""

    temporary_path: Path | None = None
    descriptor: int | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIRECTORY_MODE)
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        temporary_path = Path(temporary_name)
        fchmod = getattr(os, "fchmod", None)
        if fchmod is not None:
            fchmod(descriptor, mode)
        else:  # pragma: no cover - Windows is outside the supported shell scope
            temporary_path.chmod(mode)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = None
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        if verify_signature and _file_signature(path) != expected_signature:
            raise ConfigError(f"File changed before atomic replacement; no changes applied: {path}")
        temporary_path.replace(path)
    except OSError as exc:
        raise ConfigError(f"Unable to write file at {path}: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            with contextlib.suppress(OSError):
                temporary_path.unlink(missing_ok=True)


def _managed_block(script_path: Path) -> str:
    quoted_path = shlex.quote(str(script_path))
    return "\n".join(
        [
            MANAGED_BLOCK_BEGIN,
            f"if [ -r {quoted_path} ]; then",
            f"  . {quoted_path}",
            "fi",
            MANAGED_BLOCK_END,
        ]
    )


def _remove_managed_blocks(text: str) -> tuple[str, int]:
    removed = 0
    while True:
        start = text.find(MANAGED_BLOCK_BEGIN)
        if start < 0:
            break
        end = text.find(MANAGED_BLOCK_END, start + len(MANAGED_BLOCK_BEGIN))
        if end < 0:
            raise ConfigError(
                f"Managed completion block is incomplete: missing {MANAGED_BLOCK_END!r}."
            )
        end += len(MANAGED_BLOCK_END)
        if end < len(text) and text[end] == "\n":
            end += 1
        if start >= 2 and text[start - 2 : start] == "\n\n":
            start -= 1
        text = text[:start] + text[end:]
        removed += 1
    return text, removed


def _desired_config(text: str, script_path: Path, shell: str) -> tuple[str, bool]:
    without_managed, _ = _remove_managed_blocks(text)
    legacy_migrated = False
    if shell == "zsh" and LEGACY_ZSH_BLOCK in without_managed:
        without_managed = without_managed.replace(LEGACY_ZSH_BLOCK, "", 1)
        legacy_migrated = True
    base = without_managed.rstrip("\n")
    block = _managed_block(script_path)
    desired = f"{base}\n\n{block}\n" if base else f"{block}\n"
    return desired, legacy_migrated


def _unmanaged_registration(text: str, shell: str) -> bool:
    needle = f"{COMPLETION_VARIABLE}={shell}_source {PROGRAM_NAME}"
    managed_text, _ = _remove_managed_blocks(text)
    if shell == "zsh":
        managed_text = managed_text.replace(LEGACY_ZSH_BLOCK, "")
    return needle in managed_text


def _bash_startup_warning(config_path: Path) -> str | None:
    if sys.platform != "darwin" or config_path != default_config_path("bash"):
        return None
    home = Path.home()
    profiles = [home / ".bash_profile", home / ".bash_login", home / ".profile"]
    active_profile = next((path for path in profiles if path.exists()), None)
    if active_profile is None:
        return (
            "macOS login Bash may not load ~/.bashrc. Use --config ~/.bash_profile "
            "or make ~/.bash_profile source ~/.bashrc."
        )
    try:
        profile_text = active_profile.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return f"Unable to confirm that {active_profile} loads ~/.bashrc."
    if ".bashrc" not in profile_text:
        return (
            f"{active_profile} does not appear to load ~/.bashrc; login Bash may not enable "
            "completion. Use --config with the active profile or source ~/.bashrc from it."
        )
    return None


def completion_status(
    command: click.Command,
    *,
    shell: str | None = None,
    config_path: Path | None = None,
) -> dict[str, Any]:
    normalized = detect_shell(shell)
    requested_config = (config_path or default_config_path(normalized)).expanduser()
    edit_path = _resolve_edit_path(requested_config)
    script_path = completion_script_path(normalized)
    source = generate_completion_source(command, normalized)
    config_text = _read_text(edit_path)
    script_is_symlink = script_path.is_symlink()
    script_is_regular = script_path.is_file() and not script_is_symlink
    script_parent_is_symlink = script_path.parent.is_symlink()
    script_parent_is_directory = script_path.parent.is_dir() and not script_parent_is_symlink
    script_parent_mode = (
        _existing_mode(script_path.parent, PRIVATE_DIRECTORY_MODE)
        if script_parent_is_directory
        else None
    )
    script_parent_secure = (
        script_parent_is_directory and script_parent_mode == PRIVATE_DIRECTORY_MODE
    )
    script_text = _read_text(script_path) if script_is_regular else ""
    script_mode = _existing_mode(script_path, PRIVATE_FILE_MODE) if script_is_regular else None
    script_secure = script_is_regular and script_mode == PRIVATE_FILE_MODE
    supported, shell_path, support_warning = _shell_support(normalized)
    command_path = _command_path()
    block = _managed_block(script_path)
    warnings = [warning for warning in (support_warning,) if warning]
    bash_warning = _bash_startup_warning(requested_config)
    if bash_warning:
        warnings.append(bash_warning)
    legacy_registration = normalized == "zsh" and LEGACY_ZSH_BLOCK in config_text
    if legacy_registration:
        warnings.append(
            "A legacy dynamic Kaiten completion block was found; run completion install "
            "to migrate it."
        )
    unmanaged = _unmanaged_registration(config_text, normalized)
    if unmanaged:
        warnings.append(
            "An unmanaged Kaiten completion registration was found and was left unchanged."
        )
    if script_is_symlink:
        warnings.append("The completion script path is a symlink and will not be trusted.")
    if script_path.parent.exists() and not script_parent_secure:
        warnings.append("The completion script directory is not a private 0700 directory.")
    managed = block in config_text
    script_current = script_text == source
    configured = bool(
        command_path
        and supported
        and managed
        and script_current
        and script_secure
        and script_parent_secure
    )
    return {
        "shell": normalized,
        "supported": supported,
        "shell_executable": shell_path,
        "command_available": command_path is not None,
        "command_path": command_path,
        "config_path": str(requested_config),
        "config_target_path": str(edit_path),
        "script_path": str(script_path),
        "script_exists": script_is_regular,
        "script_parent_mode": script_parent_mode,
        "script_parent_secure": script_parent_secure,
        "script_mode": script_mode,
        "script_secure": script_secure,
        "script_current": script_current,
        "managed_block": managed,
        "legacy_registration": legacy_registration,
        "unmanaged_registration": unmanaged,
        "configured": configured,
        "warnings": warnings,
        "restart_command": f"exec {shlex.quote(normalized)}",
    }


def install_completion(
    command: click.Command,
    *,
    shell: str | None = None,
    config_path: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    normalized = detect_shell(shell)
    supported, _, warning = _shell_support(normalized)
    if not supported:
        raise ValidationError(warning or f"Shell is not supported: {normalized}.")
    if _command_path() is None:
        raise ConfigError(
            "The installed 'kaiten' entry point is not available on PATH. "
            "Finish uv/pipx PATH setup before installing completion."
        )

    requested_config = (config_path or default_config_path(normalized)).expanduser()
    edit_path = _resolve_edit_path(requested_config, require_owned=True)
    script_path = completion_script_path(normalized)
    source = generate_completion_source(command, normalized)
    current_config, config_signature, config_mode = _read_edit_state(edit_path)
    desired_config, legacy_migrated = _desired_config(current_config, script_path, normalized)
    script_parent_secure = (
        script_path.parent.is_dir()
        and not script_path.parent.is_symlink()
        and _existing_mode(script_path.parent, PRIVATE_DIRECTORY_MODE) == PRIVATE_DIRECTORY_MODE
    )
    directory_changed = not script_parent_secure
    if not dry_run:
        secure_directory(script_path.parent)
    if script_path.is_symlink():
        raise ConfigError(f"Refusing to replace symlinked completion script: {script_path}")
    if script_path.exists() and not script_path.is_file():
        raise ConfigError(f"Completion script is not a regular file: {script_path}")
    current_script = _read_text(script_path)
    current_script_mode = _existing_mode(script_path, PRIVATE_FILE_MODE)
    script_changed = current_script != source or current_script_mode != PRIVATE_FILE_MODE
    config_changed = current_config != desired_config

    if not dry_run:
        if script_changed:
            _write_text_atomic(script_path, source, mode=PRIVATE_FILE_MODE)
        if config_changed:
            _write_text_atomic(
                edit_path,
                desired_config,
                mode=config_mode,
                expected_signature=config_signature,
                verify_signature=True,
            )

    status = completion_status(
        command,
        shell=normalized,
        config_path=requested_config,
    )
    status.update(
        {
            "dry_run": dry_run,
            "script_changed": script_changed,
            "directory_changed": directory_changed,
            "config_changed": config_changed,
            "legacy_migrated": legacy_migrated,
            "would_configure": True,
        }
    )
    if not dry_run and not status["configured"]:
        raise ConfigError(
            "Completion files were written but the resulting configuration did not pass "
            "the static verification check."
        )
    return status


def uninstall_completion(
    command: click.Command,
    *,
    shell: str | None = None,
    config_path: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    normalized = detect_shell(shell)
    requested_config = (config_path or default_config_path(normalized)).expanduser()
    edit_path = _resolve_edit_path(requested_config, require_owned=True)
    script_path = completion_script_path(normalized)
    current_config, config_signature, config_mode = _read_edit_state(edit_path)
    desired_config, removed_blocks = _remove_managed_blocks(current_config)
    config_changed = desired_config != current_config
    script_exists = script_path.exists()
    if script_path.is_symlink():
        raise ConfigError(f"Refusing to remove symlinked completion script: {script_path}")
    if script_path.exists() and not script_path.is_file():
        raise ConfigError(f"Completion script is not a regular file: {script_path}")

    if not dry_run:
        if config_changed:
            _write_text_atomic(
                edit_path,
                desired_config,
                mode=config_mode,
                expected_signature=config_signature,
                verify_signature=True,
            )
        with contextlib.suppress(FileNotFoundError):
            script_path.unlink()
        with contextlib.suppress(OSError):
            script_path.parent.rmdir()

    status = completion_status(
        command,
        shell=normalized,
        config_path=requested_config,
    )
    status.update(
        {
            "dry_run": dry_run,
            "config_changed": config_changed,
            "script_changed": script_exists,
            "removed_blocks": removed_blocks,
            "would_remove": config_changed or script_exists,
        }
    )
    return status
