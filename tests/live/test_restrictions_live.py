"""Focused opt-in restriction lifecycle; never uses existing user rules."""

from __future__ import annotations

import pytest

from test_sandbox_live_full import _exercise_restrictions


@pytest.mark.live
@pytest.mark.timeout(300)
def test_restrictions_live_lifecycle(live_harness, tmp_path):
    h = live_harness
    h.env["KAITEN_TRACE_FILE"] = str(tmp_path / "restrictions-live.jsonl")
    result, probe = h._invoke(["--read-only", "profile", "probe"], "restriction profile probe")
    assert result.exit_code == 0 and probe["success"], result.output
    for key in ("space_id", "secondary_space_id"):
        space = h.run_tool("spaces.create", title=h.name(key), access="for_everyone")
        h.state[key] = space["id"]
        h.push_cleanup("delete temporary restriction space", "spaces.delete", space_id=space["id"])
    _exercise_restrictions(h)
