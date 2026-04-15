from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(autouse=True)
def isolated_config_env(request: pytest.FixtureRequest, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path | None:
    if request.node.get_closest_marker("live"):
        return None
    path = tmp_path / "config.json"
    monkeypatch.setenv("KAITEN_CLI_CONFIG_PATH", str(path))
    return path


@pytest.fixture
def config_env(isolated_config_env: Path) -> Path:
    return isolated_config_env
