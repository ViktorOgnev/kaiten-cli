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
    assert "cards batch-get" in heavy_text
    assert "time-logs batch-list" in heavy_text
    assert "card-children batch-list" in heavy_text
    assert "comments batch-list" in heavy_text
    assert "snapshot build" in heavy_text
    assert "query cards" in heavy_text
    assert "--view summary" in heavy_text
    assert "--trace-file" in heavy_text
    assert "--cache-mode readwrite" in heavy_text

    assert "name: kaiten-cli-metrics" in metrics_text
    assert "cards list-all" in metrics_text
    assert "time-logs batch-list" in metrics_text
    assert "space-topology get" in metrics_text
    assert "snapshot build" in metrics_text
    assert "query metrics" in metrics_text
    assert "compute-jobs get" in metrics_text
    assert "--trace-file" in metrics_text

    assert "skills/kaiten-cli-heavy-data/SKILL.md" in readme
    assert "skills/kaiten-cli-metrics/SKILL.md" in readme
    assert "COMMAND_REFERENCE.md" in readme
    assert "## Как работает кэш" in readme
    assert "## Investigation and report workflows" in readme
    assert "## Local-first analytics and headless workflows" in readme
    assert "card-children.batch-list" in readme
    assert "comments.batch-list" in readme
    assert "space-topology.get" in readme
    assert "snapshot build" in readme
    assert "query metrics" in readme
    assert "cards.batch-get" in readme
    assert "time-logs.batch-list" in readme
    assert "query cards --snapshot team-basic --view summary" in readme
    assert "--trace-file" in readme
    assert "--cache-mode" in readme
    assert "--cache-ttl-seconds" in readme
    assert "request-scoped" in readme
    assert "persistent" in readme
    assert "Local-first path остаётся explicit" in readme
    assert "benchmark_reference_workflows.py" in readme
    assert "Полный generated справочник" in readme
    assert "skills/kaiten-cli-heavy-data/SKILL.md" in agents
    assert "COMMAND_REFERENCE.md" in agents
    assert "--trace-file" in agents
    assert "snapshot build" in agents
    assert "cards.batch-get" in agents
    assert "generic local metrics layer" in agents
