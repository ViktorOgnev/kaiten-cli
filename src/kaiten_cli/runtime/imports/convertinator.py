"""Verified desktop setup and the opt-in Convertinator machine transport."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import platform
import plistlib
import subprocess
import sys
import tempfile
import webbrowser
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import httpx
from platformdirs import user_data_path

from kaiten_cli.errors import TransportError, ValidationError
from kaiten_cli.i18n import tr
from kaiten_cli.runtime.fs_security import secure_directory
from kaiten_cli.runtime.imports.storage import require_disk

VERSION = "1.36.0"
RELEASE_ORIGIN = "https://convertinator.kaiten-dev.ru/convertinator"
INSTALL_GUIDE = "https://faq-ru.kaiten.site/universalnyy-import-v-kaiten-iz-lyubyh-sistem"
RUNNER_ENV = "KAITEN_IMPORT_CONVERTINATOR_RUNNER"
DIGESTS = {
    ("darwin", "arm64"): "fc7570b5a43c63900913bbd73476458869a14207c5a6ce8b96e559fa36f57cca",
    ("darwin", "x64"): "9a73de5278193a3e21f0213da60eec0afa5e6327c1ec93861eb8c3edbb06b7bf",
    ("linux", "x64"): "07ad769f4bcaffe8d8df08413666f93ff0dd21dbcce108a5afe2427488ae290f",
    ("win32", "x64"): "8e06cc2a8a1e0f78284ea05c71cc22b3b29ac28a59d45d822a6927c0be39469a",
}
MAX_DOWNLOAD = 512 * 1024**2
MAX_UNPACKED = 2 * 1024**3
MAX_MACHINE_RESPONSE = 2 * 1024**2


def host_platform() -> tuple[str, str]:
    machine = platform.machine().lower()
    return sys.platform, {"amd64": "x64", "x86_64": "x64", "aarch64": "arm64"}.get(machine, machine)


def has_desktop() -> bool:
    if sys.platform == "linux":
        return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    if sys.platform == "darwin":
        import stat

        return (
            not os.environ.get("SSH_CONNECTION")
            or Path("/dev/console").stat().st_uid == os.getuid()
            and stat.S_ISCHR(Path("/dev/console").stat().st_mode)
        )
    return sys.platform == "win32" and os.environ.get("SESSIONNAME", "").lower() != "services"


def access_notice() -> dict:
    notice = {
        "kaiten": tr(
            "Kaiten authorization uses the signed-in account's permissions. Choose the target space in Convertinator."
        ),
    }
    if sys.platform == "darwin":
        notice["macos_keychain"] = tr(
            "In the official Convertinator, macOS may ask for the convertinator Safe Storage item to encrypt cookies. Permission applies only to the item named in the dialog. Use Allow for one-time access if the app and item match, or Deny if they differ."
        )
    return notice


def _install_dir() -> Path:
    system, arch = host_platform()
    return user_data_path("kaiten-cli") / "convertinator" / f"{VERSION}-{system}-{arch}"


def _entry(root: Path) -> Path | None:
    if sys.platform == "darwin":
        candidates = sorted(root.glob("*.app")) + sorted(root.glob("*/*.app"))
        return next(
            (
                app
                for app in candidates
                if app.name.casefold() == "convertinator.app" and app.is_dir()
            ),
            None,
        )
    basename = "convertinator.exe" if sys.platform == "win32" else "convertinator"
    return next(
        (file for file in root.rglob("*") if file.name.casefold() == basename and file.is_file()),
        None,
    )


def desktop_app() -> Path | None:
    root = _install_dir()
    if root.is_dir() and not root.is_symlink():
        verified = root / ".verified-sha256"
        if verified.is_file() and verified.read_text().strip() == DIGESTS.get(host_platform()):
            return _entry(root)
    if sys.platform == "darwin":
        for location in (Path.home() / "Applications", Path("/Applications")):
            entry = _entry(location)
            if entry is None:
                continue
            try:
                with (entry / "Contents/Info.plist").open("rb") as file:
                    info = plistlib.load(file)
                installed = tuple(map(int, info["CFBundleShortVersionString"].split(".")))
                if installed < (1, 36, 0):
                    continue
                result = subprocess.run(
                    [
                        "/usr/bin/codesign",
                        "--verify",
                        "--deep",
                        "--strict",
                        '-R=anchor apple generic and certificate leaf[subject.OU] = "SEPSUB9HE8"',
                        str(entry),
                    ],
                    capture_output=True,
                    check=False,
                    timeout=15,
                )
                if result.returncode == 0:
                    return entry
            except (
                OSError,
                KeyError,
                ValueError,
                subprocess.TimeoutExpired,
                plistlib.InvalidFileException,
            ):
                continue
    return None


async def ensure_desktop() -> Path | None:
    found = desktop_app()
    if found is not None:
        return found
    system, arch = host_platform()
    digest = DIGESTS.get((system, arch))
    if digest is None or not has_desktop():
        return None
    root = _install_dir()
    secure_directory(root.parent)
    with tempfile.TemporaryDirectory(prefix=".install-", dir=root.parent) as temp:
        archive_path = Path(temp) / "convertinator.zip"
        unpacked = Path(temp) / "app"
        unpacked.mkdir(mode=0o700)
        release = f"{RELEASE_ORIGIN}/{system}/{arch}/convertinator-{system}-{arch}-{VERSION}.zip"
        try:
            async with httpx.AsyncClient(follow_redirects=False, timeout=45) as http:
                async with http.stream(
                    "GET", release, headers={"Accept-Encoding": "identity"}
                ) as response:
                    response.raise_for_status()
                    maximum = int(response.headers.get("Content-Length", MAX_DOWNLOAD))
                    if not 0 < maximum <= MAX_DOWNLOAD:
                        raise ValueError
                    require_disk(root.parent, maximum)
                    checksum = hashlib.sha256()
                    total = 0
                    with archive_path.open("wb") as file:
                        async for block in response.aiter_raw():
                            total += len(block)
                            if total > maximum:
                                raise ValueError
                            checksum.update(block)
                            file.write(block)
            if checksum.hexdigest() != digest:
                raise ValidationError(tr("The Convertinator download failed its SHA-256 check."))
            with ZipFile(archive_path) as archive:
                require_disk(root.parent, sum(info.file_size for info in archive.infolist()))
                if sum(info.file_size for info in archive.infolist()) > MAX_UNPACKED:
                    raise ValueError
                if system != "darwin":
                    # The pinned release is trusted. Preserve executable permissions on Linux.
                    for info in archive.infolist():
                        output = Path(archive.extract(info, unpacked))
                        if (
                            not info.is_dir()
                            and system == "linux"
                            and (info.external_attr >> 16) & 0o111
                        ):
                            output.chmod(0o700)
            if system == "darwin":
                # ditto preserves the framework symlinks and signed app bundle layout.
                await asyncio.to_thread(
                    subprocess.run,
                    ["/usr/bin/ditto", "-x", "-k", str(archive_path), str(unpacked)],
                    check=True,
                    timeout=120,
                    capture_output=True,
                )
            if _entry(unpacked) is None:
                raise ValueError
            (unpacked / ".verified-sha256").write_text(digest + "\n")
            try:
                unpacked.rename(root)
            except OSError:
                if desktop_app() is None:
                    raise
        except (httpx.HTTPError, OSError, ValueError, BadZipFile, subprocess.SubprocessError):
            raise TransportError(
                tr("Unable to install Convertinator. Use the official installer on a desktop.")
            ) from None
    return desktop_app()


def launch_desktop(app: Path | None) -> bool:
    if app is None or not has_desktop():
        return False
    args = ["/usr/bin/open", "-a", str(app)] if sys.platform == "darwin" else [str(app)]
    try:
        subprocess.Popen(
            args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except OSError:
        return False
    return True


def launch_browser(url: str) -> bool:
    try:
        return has_desktop() and webbrowser.open(url)
    except (OSError, webbrowser.Error):
        return False


async def machine(action: str, payload: dict, *, token: str | None = None) -> dict | None:
    """The opt-in executable receives only protocol JSON over a private pipe."""
    executable = os.environ.get(RUNNER_ENV)
    if not executable:
        return None
    path = Path(executable).expanduser()
    if not path.is_absolute() or not path.is_file():
        raise ValidationError(tr("The Convertinator runner must be an absolute executable path."))
    request = {"protocol": 1, "action": action, **payload}
    if token is not None:
        request["kaiten_token"] = token
    allowed_env = {
        "PATH",
        "SYSTEMROOT",
        "WINDIR",
        "TEMP",
        "TMP",
        "TMPDIR",
        "HOME",
        "USERPROFILE",
        "APPDATA",
        "LOCALAPPDATA",
        "XDG_RUNTIME_DIR",
        "DISPLAY",
        "WAYLAND_DISPLAY",
        "LANG",
        "LC_ALL",
        "NODE_EXTRA_CA_CERTS",
    }
    env = {key: value for key, value in os.environ.items() if key.upper() in allowed_env}
    try:
        with (
            tempfile.TemporaryFile() as output,
            tempfile.TemporaryDirectory(prefix="kaiten-import-session-") as session,
        ):
            isolated = [f"--user-data-dir={Path(session).resolve()}"]
            if sys.platform == "darwin":
                isolated.append("--use-mock-keychain")
            elif sys.platform == "linux":
                isolated.append("--password-store=basic")
            process = await asyncio.create_subprocess_exec(
                str(path),
                "--kaiten-import-machine",
                *isolated,
                stdin=asyncio.subprocess.PIPE,
                stdout=output,
                stderr=asyncio.subprocess.DEVNULL,
                env=env,
            )
            try:
                await asyncio.wait_for(
                    process.communicate(json.dumps(request).encode()),
                    timeout=30 if action in {"capabilities", "status"} else 86400,
                )
            except (asyncio.TimeoutError, asyncio.CancelledError):
                if process.returncode is None:
                    process.kill()
                    await process.wait()
                raise
            output.seek(0)
            raw = output.read(MAX_MACHINE_RESPONSE + 1)
        if process.returncode != 0 or len(raw) > MAX_MACHINE_RESPONSE:
            raise ValueError
        response = json.loads(raw)
        if not isinstance(response, dict) or response.get("protocol") != 1:
            raise ValueError
        return response
    except (OSError, ValueError, RecursionError, asyncio.TimeoutError):
        raise TransportError(
            tr(
                "Convertinator did not return a valid result. Check the existing operation before retrying."
            )
        ) from None
