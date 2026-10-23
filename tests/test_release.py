from __future__ import annotations

import importlib.util
import io
import subprocess
import tarfile
import urllib.error
import zipfile
from contextlib import nullcontext
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_release", ROOT / "scripts/check_release.py")
assert SPEC and SPEC.loader
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


@pytest.mark.parametrize("tag", ["v0.3.3", "v1.0.0", "v10.20.30"])
def test_stable_tags(tag):
    assert release.tag_version(tag) == tag[1:]


@pytest.mark.parametrize(
    "tag", ["0.3.3", "v01.3.3", "v0.3.3rc1", "v0.3.3.dev1", "v0.3.3+build", "v0.3", "v١.٢.٣"]
)
def test_nonrelease_tags_are_rejected(tag):
    with pytest.raises(release.ReleaseError, match="stable"):
        release.tag_version(tag)


def run_git(root, *args):
    return subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=True
    ).stdout.strip()


@pytest.fixture
def repository(tmp_path):
    run_git(tmp_path, "init", "--initial-branch=master")
    run_git(tmp_path, "config", "user.email", "release-test@example.invalid")
    run_git(tmp_path, "config", "user.name", "Release Test")
    package = tmp_path / "src/kaiten_cli"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('__version__ = "0.3.3"\n', encoding="utf-8")
    run_git(tmp_path, "add", "src")
    run_git(tmp_path, "commit", "-m", "Base")
    commit = run_git(tmp_path, "rev-parse", "HEAD")
    run_git(tmp_path, "update-ref", "refs/remotes/origin/master", commit)
    run_git(tmp_path, "tag", "-a", "v0.3.3", "-m", "Release")
    return tmp_path, commit


def test_preflight_accepts_annotated_tag_on_master(repository):
    root, commit = repository
    release.check_commit(root, "v0.3.3", commit, "origin/master")


def test_preflight_accepts_ancestor_of_master(repository):
    root, commit = repository
    run_git(root, "commit", "--allow-empty", "-m", "Later master commit")
    run_git(root, "update-ref", "refs/remotes/origin/master", "HEAD")
    run_git(root, "checkout", "--detach", "v0.3.3")
    release.check_commit(root, "v0.3.3", commit, "origin/master")


def test_preflight_rejects_version_mismatch(repository):
    root, commit = repository
    with pytest.raises(release.ReleaseError, match="version"):
        release.check_commit(root, "v0.3.4", commit, "origin/master")


def test_preflight_rejects_wrong_trigger_commit(repository):
    root, _ = repository
    with pytest.raises(release.ReleaseError, match="identical"):
        release.check_commit(root, "v0.3.3", "0" * 40, "origin/master")


def test_preflight_rejects_tag_on_another_commit(repository):
    root, _ = repository
    run_git(root, "commit", "--allow-empty", "-m", "Another commit")
    commit = run_git(root, "rev-parse", "HEAD")
    with pytest.raises(release.ReleaseError, match="identical"):
        release.check_commit(root, "v0.3.3", commit, "origin/master")


def test_preflight_rejects_unmerged_commit(repository):
    root, _ = repository
    run_git(root, "checkout", "-b", "unmerged")
    run_git(root, "commit", "--allow-empty", "-m", "Unmerged")
    run_git(root, "tag", "-f", "v0.3.3")
    commit = run_git(root, "rev-parse", "HEAD")
    with pytest.raises(release.ReleaseError, match="merge-base"):
        release.check_commit(root, "v0.3.3", commit, "origin/master")


@pytest.mark.parametrize("status", [404, 403, 429, 500])
def test_only_pypi_404_allows_publishing(monkeypatch, status):
    def lookup(request, *, timeout):
        assert request.full_url == "https://pypi.org/pypi/kaiten-cli/0.3.3/json"
        assert timeout == 15
        raise urllib.error.HTTPError(request.full_url, status, "test", {}, None)

    monkeypatch.setattr(release.urllib.request, "urlopen", lookup)
    if status == 404:
        release.check_unpublished("0.3.3")
    else:
        with pytest.raises(release.ReleaseError, match=f"HTTP {status}"):
            release.check_unpublished("0.3.3")


def test_existing_pypi_release_is_rejected(monkeypatch):
    monkeypatch.setattr(release.urllib.request, "urlopen", lambda *_a, **_kw: nullcontext())
    with pytest.raises(release.ReleaseError, match="already exists"):
        release.check_unpublished("0.3.3")


@pytest.mark.parametrize("error", [urllib.error.URLError("offline"), TimeoutError("timeout")])
def test_network_failure_never_allows_publishing(monkeypatch, error):
    def lookup(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(release.urllib.request, "urlopen", lookup)
    with pytest.raises(release.ReleaseError, match="lookup failed"):
        release.check_unpublished("0.3.3")


def make_archives(root, *, wheel_version="0.3.3", sdist_version="0.3.3", name="kaiten-cli"):
    root.mkdir(exist_ok=True)
    with zipfile.ZipFile(root / "kaiten_cli-0.3.3-py3-none-any.whl", "w") as wheel:
        wheel.writestr(
            "kaiten_cli-0.3.3.dist-info/METADATA", f"Name: {name}\nVersion: {wheel_version}\n"
        )
    with tarfile.open(root / "kaiten_cli-0.3.3.tar.gz", "w:gz") as sdist:
        data = f"Name: {name}\nVersion: {sdist_version}\n".encode()
        member = tarfile.TarInfo("kaiten_cli-0.3.3/PKG-INFO")
        member.size = len(data)
        sdist.addfile(member, io.BytesIO(data))


def test_matching_archives(tmp_path):
    make_archives(tmp_path)
    assert len(release.check_artifacts(tmp_path, "0.3.3")) == 2


@pytest.mark.parametrize(
    "changes",
    [{"wheel_version": "0.3.2"}, {"sdist_version": "0.3.2"}, {"name": "another-package"}],
)
def test_mismatching_archive_metadata(tmp_path, changes):
    make_archives(tmp_path, **changes)
    with pytest.raises(release.ReleaseError, match="Name/Version"):
        release.check_artifacts(tmp_path, "0.3.3")


@pytest.mark.parametrize("change", ["extra", "missing", "duplicate"])
def test_ambiguous_or_incomplete_archive_set(tmp_path, change):
    make_archives(tmp_path)
    if change == "extra":
        (tmp_path / "old-build.txt").touch()
    elif change == "missing":
        next(tmp_path.glob("*.whl")).unlink()
    else:
        next(tmp_path.glob("*.whl")).rename(tmp_path / "duplicate.whl")
        (tmp_path / "another.whl").touch()
    with pytest.raises(release.ReleaseError, match="exactly one wheel"):
        release.check_artifacts(tmp_path, "0.3.3")


def test_artifacts_command_checks_tag_and_reports_hashes(tmp_path, capsys):
    make_archives(tmp_path)
    assert release.main(["artifacts", "--dist", str(tmp_path), "--tag", "v0.3.3"]) == 0
    assert len(capsys.readouterr().out.splitlines()) == 2
    with pytest.raises(SystemExit) as exc:
        release.main(["artifacts", "--dist", str(tmp_path), "--tag", "v0.3.2"])
    assert exc.value.code == 1
    assert "Release check failed" in capsys.readouterr().err


def test_preflight_command_stops_before_lookup_when_git_check_fails(monkeypatch, repository):
    root, _ = repository
    monkeypatch.setattr(release, "ROOT", root)
    monkeypatch.setattr(
        release,
        "check_unpublished",
        lambda _v: pytest.fail("Must not query PyPI after failed gate"),
    )
    with pytest.raises(SystemExit) as exc:
        release.main(["preflight", "--tag", "v0.3.3", "--commit", "0" * 40])
    assert exc.value.code == 1


def test_publish_workflow_gates_upload_on_all_checks():
    publish = yaml.load(
        (ROOT / ".github/workflows/publish.yml").read_text(), Loader=yaml.BaseLoader
    )
    ci = yaml.load((ROOT / ".github/workflows/ci.yml").read_text(), Loader=yaml.BaseLoader)
    # A branch push or a PR must never upload. Both normal CI entrypoints remain.
    assert set(publish["on"]) == {"push"}
    assert set(publish["on"]["push"]) == {"tags"}
    assert set(ci["on"]) == {"push", "pull_request", "workflow_call"}
    jobs = publish["jobs"]
    preflight_steps = jobs["preflight"]["steps"]
    assert preflight_steps[0]["with"]["fetch-depth"] == "0"
    assert "check_release.py preflight" in preflight_steps[-1]["run"]
    assert preflight_steps[-1]["env"]["RELEASE_COMMIT"] == "${{ github.sha }}"
    assert jobs["checks"]["needs"] == "preflight"
    assert jobs["checks"]["uses"] == "./.github/workflows/ci.yml"
    assert jobs["publish"]["needs"] == "checks"
    assert "if" not in jobs["publish"]  # Keep the default success() dependency gate.
    assert "continue-on-error" not in str(jobs) + str(ci)
    assert jobs["publish"]["environment"]["name"] == "pypi"
    assert jobs["publish"]["permissions"] == {"id-token": "write"}
    assert "id-token" not in str(publish["permissions"]) + str(ci)
    assert all("id-token" not in str(jobs[job]) for job in ("preflight", "checks"))
    upload_steps = jobs["publish"]["steps"]
    assert len(upload_steps) == 2
    assert upload_steps[0]["uses"].startswith("actions/download-artifact@")
    assert upload_steps[0]["with"]["name"] == "distribution"
    assert upload_steps[1]["uses"].startswith("pypa/gh-action-pypi-publish@")
    assert upload_steps[1]["with"]["skip-existing"] == "false"
    assert publish["concurrency"]["cancel-in-progress"] == "false"
    assert "github.ref" in publish["concurrency"]["group"]
    assert {"quality", "test", "coverage", "dependency-audit", "build", "install-smoke"} <= set(
        ci["jobs"]
    )
    build_steps = ci["jobs"]["build"]["steps"]
    assert build_steps[-1]["with"]["name"] == upload_steps[0]["with"]["name"]
    assert ci["jobs"]["install-smoke"]["needs"] == "build"
