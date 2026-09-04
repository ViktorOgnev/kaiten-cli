from __future__ import annotations

from pathlib import Path


def test_primary_docs_and_archive_layout_are_explicit():
    root = Path(__file__).resolve().parents[1]

    primary_docs = {
        "README.md",
        "COMMAND_REFERENCE.md",
        "AGENTS.md",
        "ARCHITECTURE.md",
        "LIVE_VALIDATION.md",
        "API_BEHAVIOR_MATRIX.md",
        "SECURITY.md",
    }

    for name in primary_docs:
        assert (root / name).is_file(), name

    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    assert "/docs/archive/" in gitignore
    assert "/PLAN*.md" in gitignore
    assert "/PARITY_CHECKLIST.md" in gitignore
    assert ".env_private" in gitignore
    assert ".DS_Store" in gitignore

    assert not (root / "docs" / "archive" / "README.md").exists()
    assert not (root / "docs" / "archive" / "PLAN.md").exists()
    assert not (root / "docs" / "archive" / "PLAN_EXTERNAL_REVIEW.md").exists()
    assert not (root / "docs" / "archive" / "PLAN_TRIZ_VERIFICATION.md").exists()
    assert not (root / "docs" / "archive" / "PARITY_CHECKLIST.md").exists()
    assert (root / "scripts" / "benchmark_reference_workflows.py").is_file()


def test_primary_docs_expose_current_install_safety_and_live_metadata():
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    live_validation = (root / "LIVE_VALIDATION.md").read_text(encoding="utf-8")
    behavior_matrix = (root / "API_BEHAVIOR_MATRIX.md").read_text(encoding="utf-8")

    assert "@v0.2.0" in readme
    assert "@v0.1.29" not in readme
    assert "@v0.1.23" not in readme
    assert "`v0.2.0` — граница совместимости" in readme
    assert "stats.pagination_compatibility" in readme
    assert "KAITEN_CLI_READ_ONLY" in readme
    assert "KAITEN_CLI_UPDATE_CHECK" in readme
    assert "--no-update-check" in readme
    assert "kaiten completion install" in readme
    assert "kaiten completion status" in readme
    assert "kaiten completion uninstall" in readme
    assert "Bash версии 4.4" in readme
    assert "update-check.json" in readme
    assert "http-cache.sqlite3" in readme
    assert "snapshots.sqlite3" in readme
    assert "live suite **не запускался**" in live_validation
    assert "Последняя полная live campaign" in behavior_matrix
