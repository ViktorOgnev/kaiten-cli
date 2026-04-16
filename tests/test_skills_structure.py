from __future__ import annotations

from pathlib import Path


def test_repo_contains_expected_skill_files():
    root = Path(__file__).resolve().parents[1]
    heavy = root / "skills" / "kaiten-cli-heavy-data" / "SKILL.md"
    metrics = root / "skills" / "kaiten-cli-metrics" / "SKILL.md"
    readme = (root / "README.md").read_text(encoding="utf-8")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")

    assert heavy.is_file()
    assert metrics.is_file()

    heavy_text = heavy.read_text(encoding="utf-8")
    metrics_text = metrics.read_text(encoding="utf-8")

    assert "name: kaiten-cli-heavy-data" in heavy_text
    assert "card-location-history batch-get" in heavy_text
    assert "--cache-mode readwrite" in heavy_text

    assert "name: kaiten-cli-metrics" in metrics_text
    assert "cards list-all" in metrics_text
    assert "compute-jobs get" in metrics_text

    assert "skills/kaiten-cli-heavy-data/SKILL.md" in readme
    assert "skills/kaiten-cli-metrics/SKILL.md" in readme
    assert "## Как работает кэш" in readme
    assert "--cache-mode" in readme
    assert "--cache-ttl-seconds" in readme
    assert "request-scoped" in readme
    assert "persistent" in readme
    assert "skills/kaiten-cli-heavy-data/SKILL.md" in agents
