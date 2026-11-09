"""Private run storage and immutable import-package staging."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from uuid import UUID
from zipfile import BadZipFile, ZipFile

from platformdirs import user_data_path

from kaiten_cli.errors import ConfigError, ValidationError
from kaiten_cli.i18n import tr
from kaiten_cli.runtime.fs_security import secure_existing_file

MANIFEST = "meta-data.json"
STORAGE_READ_ONLY = "KAITEN_CLI_STORAGE_READ_ONLY"
DISK_RESERVE = 64 * 1024**2
MAX_MANIFEST = 32 * 1024**2
MAX_FILES = 200_000
RESOURCES = frozenset(
    "activities attachments boards card_blockers card_children card_history card_links "
    "card_members card_planned_relations card_time_logs card_types cards checklist_items "
    "checklists columns comments custom_directories custom_directory_records custom_properties "
    "document_comments documents folders iteration_cards iterations lanes roles space_boards "
    "spaces tags tree_entity_roles user_groups users".split()
)


def root_dir(work_dir: str | None = None) -> Path:
    return (
        Path(work_dir).expanduser().resolve()
        if work_dir
        else user_data_path("kaiten-cli") / "imports"
    )


def run_dir(run: str, work_dir: str | None = None) -> Path:
    try:
        if str(UUID(run)) != run:
            raise ValueError
    except (TypeError, ValueError):
        raise ValidationError(tr("Invalid import run ID.")) from None
    return root_dir(work_dir) / run


def writable() -> bool:
    return os.environ.get(STORAGE_READ_ONLY, "").strip().lower() not in {"1", "true", "yes", "on"}


def require_writable() -> None:
    if not writable():
        raise ConfigError(tr("Import storage is read-only. Continue in a local CLI session."))


def atomic_json(path: Path, data: object) -> None:
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, allow_nan=False)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def read_json(path: Path, max_bytes: int = MAX_MANIFEST):
    try:
        with path.open("rb") as handle:
            raw = handle.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise ValueError
        return json.loads(raw)
    except (OSError, ValueError, RecursionError):
        raise ValidationError(
            tr("Invalid or oversized import JSON: {value_0}", value_0=path.name)
        ) from None


@contextmanager
def lock_run(path: Path) -> Iterator[None]:
    """The OS releases the run lock when a CLI process exits or crashes."""
    require_writable()
    lock = path / ".lock"
    if path.is_symlink() or lock.is_symlink() or not path.is_dir():
        raise ValidationError(tr("Import run was not found."))
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        try:
            if os.name == "nt":  # pragma: no cover - Windows
                import msvcrt

                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise ValidationError(tr("Another command is using this import run.")) from None
        yield
    finally:
        os.close(fd)


def load_run(path: Path) -> dict:
    file = path / "run.json"
    if path.is_symlink() or file.is_symlink() or not file.is_file():
        raise ValidationError(tr("Import run was not found."))
    data = read_json(file)
    if not isinstance(data, dict) or data.get("version") != 1 or data.get("run_id") != path.name:
        raise ValidationError(tr("Invalid import run manifest."))
    return data


def read_secrets(path: Path) -> dict:
    file = path / "credentials.json"
    if not file.exists():
        return {}
    secure_existing_file(file)
    data = read_json(file, 16384)
    return data if isinstance(data, dict) else {}


def free_bytes(path: Path) -> int:
    while not path.exists():
        path = path.parent
    return shutil.disk_usage(path).free


def require_disk(path: Path, data_bytes: int) -> None:
    if free_bytes(path) < data_bytes + DISK_RESERVE:
        raise ValidationError(
            tr("Insufficient disk space for import staging. Choose another work directory.")
        )


def safe_path(value: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) > 2048
        or any(c in value for c in "\\:\x00")
        or any(
            part in {"", ".", "..", "~"} or part.endswith((".", " ")) for part in value.split("/")
        )
        or re.search(r"%[0-9a-fA-F]{2}", value)
        or any(
            part.split(".")[0].upper()
            in {
                "CON",
                "PRN",
                "AUX",
                "NUL",
                *(f"COM{i}" for i in range(1, 10)),
                *(f"LPT{i}" for i in range(1, 10)),
            }
            for part in value.split("/")
        )
    ):
        raise ValidationError(tr("The import archive contains an unsafe path."))
    return value


def directory_files(path: Path) -> dict[str, int]:
    result = {}
    for child in path.rglob("*"):
        if child.is_symlink() or not (child.is_file() or child.is_dir()):
            raise ValidationError(
                tr("Import packages must contain only regular files and directories.")
            )
        if child.is_file():
            result[safe_path(child.relative_to(path).as_posix())] = child.stat().st_size
            if len(result) > MAX_FILES:
                raise ValidationError(tr("The import package has too many files."))
    return result


def zip_files(archive: ZipFile) -> dict[str, int]:
    result = {}
    seen = set()
    for item in archive.infolist():
        name = safe_path(item.filename.rstrip("/") if item.is_dir() else item.filename)
        kind = stat.S_IFMT(item.external_attr >> 16)
        if (
            name.casefold() in seen
            or kind not in {0, stat.S_IFREG, stat.S_IFDIR}
            or item.flag_bits & 1
        ):
            raise ValidationError(
                tr("The import archive contains duplicate, encrypted or special entries.")
            )
        seen.add(name.casefold())
        if not item.is_dir():
            result[name] = item.file_size
        if len(seen) > MAX_FILES:
            raise ValidationError(tr("The import package has too many files."))
    paths = {PurePosixPath(name.casefold()) for name in result}
    if any(parent in paths for name in paths for parent in name.parents):
        raise ValidationError(tr("The import archive contains conflicting file paths."))
    return result


def validate_manifest(manifest: object, files: dict[str, int]) -> dict:
    try:
        if (
            not isinstance(manifest, dict)
            or manifest["profile"] != {"name": "external"}
            or manifest["binary_files"] != {"base_path": "files/"}
            or manifest["timeline_mode"] not in {"current_state_only", "explicit"}
        ):
            raise ValueError
        UUID(manifest["package_id"])
        source = manifest["source"]
        if not all(
            isinstance(source[key], str) and source[key]
            for key in ("system", "namespace", "exported_at")
        ):
            raise ValueError
        resources = manifest["resource_files"]
        if not isinstance(resources, list) or not 1 <= len(resources) <= 100_000:
            raise ValueError
        listed = set()
        for entry in resources:
            path = safe_path(entry["path"])
            if (
                entry["resource"] not in RESOURCES
                or path in listed
                or path not in files
                or path == MANIFEST
                or path.startswith("files/")
            ):
                raise ValueError
            listed.add(path)
        if any(
            p.endswith(".json") and not p.startswith("files/") and p not in listed | {MANIFEST}
            for p in files
        ):
            raise ValueError
    except (KeyError, TypeError, ValueError, AttributeError):
        raise ValidationError(
            tr("Invalid Universal Format 2.0 external package manifest.")
        ) from None
    return manifest


def _zip_manifest(archive: ZipFile, files: dict[str, int]) -> dict:
    if MANIFEST not in files or files[MANIFEST] > MAX_MANIFEST:
        raise ValidationError(tr("Invalid Universal Format 2.0 external package manifest."))
    return validate_manifest(json.loads(archive.read(MANIFEST)), files)


def inspect_package(source: Path, destination: Path | None = None) -> dict:
    """Inspect headers or copy into an empty, CLI-owned directory without archive extraction APIs."""
    try:
        if source.is_symlink():
            raise ValidationError(
                tr("Import packages must contain only regular files and directories.")
            )
        if source.is_dir():
            files = directory_files(source)
            manifest = validate_manifest(read_json(source / MANIFEST), files)
            if destination is not None:
                require_disk(destination, sum(files.values()))
                for name in files:
                    with (source / name).open("rb") as incoming:
                        _copy(incoming, destination / name, files[name])
        else:
            with ZipFile(source) as archive:
                files = zip_files(archive)
                manifest = _zip_manifest(archive, files)
                if destination is not None:
                    require_disk(destination, sum(files.values()))
                    for name in files:
                        with archive.open(name) as incoming:
                            _copy(incoming, destination / name, files[name])
        if len({name.casefold() for name in files}) != len(files):
            raise ValidationError(tr("The import archive contains conflicting file paths."))
    except (BadZipFile, OSError, ValueError, RuntimeError, NotImplementedError, RecursionError):
        raise ValidationError(tr("Unable to read or stage the import package.")) from None
    return {
        "package_id": manifest["package_id"],
        "files": len(files),
        "bytes": sum(files.values()),
        "resources": sorted({entry["resource"] for entry in manifest["resource_files"]}),
    }


def _copy(incoming, target: Path, expected: int) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    copied = 0
    with os.fdopen(fd, "wb") as out:
        while block := incoming.read(1024 * 1024):
            copied += len(block)
            if copied > expected:
                raise ValueError
            out.write(block)
    if copied != expected:
        raise ValueError


def fingerprint(package: Path) -> str:
    digest = hashlib.sha256()
    for name, size in sorted(directory_files(package).items()):
        digest.update(json.dumps([name, size], ensure_ascii=True).encode("ascii"))
        with (package / name).open("rb") as file:
            digest.update(hashlib.file_digest(file, "sha256").digest())
    return digest.hexdigest()
