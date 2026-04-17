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
    }

    for name in primary_docs:
        assert (root / name).is_file(), name

    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    assert "/docs/archive/" in gitignore
    assert "/PLAN*.md" in gitignore
    assert "/PARITY_CHECKLIST.md" in gitignore

    assert not (root / "docs" / "archive" / "README.md").exists()
    assert not (root / "docs" / "archive" / "PLAN.md").exists()
    assert not (root / "docs" / "archive" / "PLAN_EXTERNAL_REVIEW.md").exists()
    assert not (root / "docs" / "archive" / "PLAN_TRIZ_VERIFICATION.md").exists()
    assert not (root / "docs" / "archive" / "PARITY_CHECKLIST.md").exists()
    assert (root / "scripts" / "benchmark_reference_workflows.py").is_file()
