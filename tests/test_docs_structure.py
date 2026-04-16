from __future__ import annotations

from pathlib import Path


def test_primary_docs_and_archive_layout_are_explicit():
    root = Path(__file__).resolve().parents[1]

    primary_docs = {
        "README.md",
        "AGENTS.md",
        "ARCHITECTURE.md",
        "LIVE_VALIDATION.md",
        "API_BEHAVIOR_MATRIX.md",
    }
    archived_docs = {
        "PLAN.md",
        "PLAN_EXTERNAL_REVIEW.md",
        "PLAN_TRIZ_VERIFICATION.md",
        "PARITY_CHECKLIST.md",
    }

    for name in primary_docs:
        assert (root / name).is_file(), name

    for name in archived_docs:
        assert not (root / name).exists(), name
        assert (root / "docs" / "archive" / name).is_file(), name

    assert (root / "docs" / "archive" / "README.md").is_file()
    assert (root / "scripts" / "benchmark_reference_workflows.py").is_file()
