from __future__ import annotations

from pathlib import Path


def test_executor_has_no_tool_specific_canonical_name_branching():
    executor_path = Path(__file__).resolve().parents[1] / "src" / "kaiten_cli" / "runtime" / "executor.py"
    source = executor_path.read_text(encoding="utf-8")

    assert "tool.canonical_name" not in source
