"""Fail-closed checks for stable PyPI releases; no upload or credential handling."""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import subprocess
import tarfile
import urllib.error
import urllib.request
import zipfile
from email.parser import BytesParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "kaiten-cli"
STABLE_TAG = re.compile(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", re.ASCII)


class ReleaseError(ValueError):
    """A release invariant failed; publishing must stop."""


def source_version(root: Path) -> str:
    tree = ast.parse((root / "src/kaiten_cli/__init__.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets
        ):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return node.value.value
    raise ReleaseError("Cannot read a literal __version__ from the package")


def tag_version(tag: str) -> str:
    if not STABLE_TAG.fullmatch(tag):
        raise ReleaseError(f"Expected a stable vX.Y.Z tag, got {tag!r}")
    return tag[1:]


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False, timeout=30
    )
    if result.returncode:
        raise ReleaseError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def check_commit(root: Path, tag: str, commit: str, master_ref: str) -> None:
    version = tag_version(tag)
    if source_version(root) != version:
        raise ReleaseError(f"Tag {tag} does not match the checked-out package version")
    head = git(root, "rev-parse", "HEAD")
    if head != commit or git(root, "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}") != head:
        raise ReleaseError("HEAD, the release tag and the triggering commit must be identical")
    git(root, "merge-base", "--is-ancestor", head, master_ref)


def check_unpublished(version: str) -> None:
    # Only an explicit 404 means absent. Timeouts, rate limits and server errors
    # must never be mistaken for permission to upload.
    url = f"https://pypi.org/pypi/{PACKAGE}/{version}/json"
    request = urllib.request.Request(url, headers={"User-Agent": "kaiten-cli-release-check"})
    try:
        with urllib.request.urlopen(request, timeout=15):
            pass
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return
        raise ReleaseError(f"PyPI version lookup failed: HTTP {exc.code}") from exc
    except (OSError, urllib.error.URLError) as exc:
        raise ReleaseError(f"PyPI version lookup failed: {exc}") from exc
    raise ReleaseError(f"{PACKAGE} {version} already exists on PyPI; inspect it before retrying")


def check_metadata(data: bytes, version: str, archive: Path) -> None:
    metadata = BytesParser().parsebytes(data)
    name = re.sub(r"[-_.]+", "-", metadata.get("Name", "")).lower()
    if name != PACKAGE or metadata.get("Version") != version:
        raise ReleaseError(
            f"Unexpected Name/Version in {archive.name}: expected {PACKAGE} {version}"
        )


def check_artifacts(dist: Path, version: str) -> list[Path]:
    files = sorted(dist.iterdir())
    wheels = [path for path in files if path.suffix == ".whl"]
    sdists = [path for path in files if path.name.endswith(".tar.gz")]
    if len(files) != 2 or len(wheels) != 1 or len(sdists) != 1:
        raise ReleaseError("Expected exactly one wheel and one .tar.gz sdist, with no extra files")
    with zipfile.ZipFile(wheels[0]) as wheel:
        names = [name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")]
        if len(names) != 1:
            raise ReleaseError("Expected exactly one wheel METADATA file")
        check_metadata(wheel.read(names[0]), version, wheels[0])
    with tarfile.open(sdists[0], "r:gz") as sdist:
        members = [
            member
            for member in sdist.getmembers()
            if member.name.count("/") == 1 and member.name.endswith("/PKG-INFO")
        ]
        if len(members) != 1 or not members[0].isfile():
            raise ReleaseError("Expected exactly one top-level sdist PKG-INFO file")
        stream = sdist.extractfile(members[0])
        assert stream is not None
        with stream:
            check_metadata(stream.read(), version, sdists[0])
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preflight = commands.add_parser("preflight", help="Check tag, master ancestry and PyPI version")
    preflight.add_argument("--tag", required=True)
    preflight.add_argument("--commit", required=True)
    preflight.add_argument("--master-ref", default="origin/master")
    artifacts = commands.add_parser(
        "artifacts", help="Check built archive metadata and print SHA256"
    )
    artifacts.add_argument("--dist", type=Path, default=Path("dist"))
    artifacts.add_argument("--tag", help="Require this stable release tag to match the archives")
    args = parser.parse_args(argv)
    try:
        if args.command == "preflight":
            check_commit(ROOT, args.tag, args.commit, args.master_ref)
            check_unpublished(tag_version(args.tag))
            print(f"Release preflight passed for {args.tag} at {args.commit}")
        else:
            version = tag_version(args.tag) if args.tag else source_version(ROOT)
            for path in check_artifacts(args.dist, version):
                print(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    except (
        ReleaseError,
        OSError,
        SyntaxError,
        subprocess.TimeoutExpired,
        tarfile.TarError,
        zipfile.BadZipFile,
    ) as exc:
        parser.exit(1, f"Release check failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
