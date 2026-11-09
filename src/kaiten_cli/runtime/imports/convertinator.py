"""Open the installed Convertinator or direct the operator to the Kaiten interface."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

from kaiten_cli.errors import ValidationError
from kaiten_cli.i18n import tr

INSTALL_GUIDE = "https://faq-ru.kaiten.site/import-iz-jira-cherez-convertinator"


def has_desktop() -> bool:
    if sys.platform == "linux":
        return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    if sys.platform == "darwin":
        return (
            not os.environ.get("SSH_CONNECTION")
            or Path("/dev/console").stat().st_uid == os.getuid()
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


def _is_signed_app(path: Path) -> bool:
    if path.name.casefold() != "convertinator.app" or not path.is_dir():
        return False
    try:
        result = subprocess.run(
            [
                "/usr/bin/codesign",
                "--verify",
                "--deep",
                "--strict",
                '-R=anchor apple generic and certificate leaf[subject.OU] = "SEPSUB9HE8"',
                str(path),
            ],
            capture_output=True,
            check=False,
            timeout=15,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def desktop_app(app_path: str | None = None) -> Path | None:
    if sys.platform == "darwin":
        roots = (Path.home() / "Applications", Path("/Applications"))
        candidates = (
            (Path(app_path).expanduser(),)
            if app_path
            else (
                root / name for root in roots for name in ("Convertinator.app", "convertinator.app")
            )
        )
        for path in candidates:
            if _is_signed_app(path.absolute()):
                return path.absolute()
    elif sys.platform in {"linux", "win32"}:
        name = "convertinator.exe" if sys.platform == "win32" else "convertinator"
        if app_path:
            path = Path(app_path).expanduser().absolute()
            executable = shutil.which(str(path)) if path.name.casefold() == name else None
        else:
            executable = shutil.which(name)
        if executable:
            return Path(executable).absolute()
    if app_path:
        raise ValidationError(tr("Select the installed official Convertinator application."))
    return None


def _launch(args: list[str]) -> bool:
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("KAITEN_")}
    try:
        subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
    except OSError:
        return False
    return True


def launch_desktop(app: Path | None) -> bool:
    if app is None or not has_desktop():
        return False
    args = ["/usr/bin/open", "-a", str(app)] if sys.platform == "darwin" else [str(app)]
    return _launch(args)


def launch_browser(url: str) -> bool:
    try:
        if not has_desktop():
            return False
        if sys.platform == "darwin":
            return _launch(["/usr/bin/open", url])
        if sys.platform == "linux" and (opener := shutil.which("xdg-open")):
            return _launch([opener, url])
        return webbrowser.open(url)
    except (OSError, webbrowser.Error):
        return False
