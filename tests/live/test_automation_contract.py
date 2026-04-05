from __future__ import annotations

from datetime import UTC, datetime

import pytest


def _iso_datetime() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _automation_actions(current_user_id: int) -> list[dict]:
    return [
        {
            "type": "add_assignee",
            "created": _iso_datetime(),
            "data": {"variant": "specific", "userId": current_user_id},
        }
    ]


@pytest.mark.live
@pytest.mark.timeout(180)
def test_automation_contract_known_good_payload(live_harness):
    h = live_harness

    current_user = h.run_tool("users.current")
    h.state["current_user_id"] = current_user["id"]

    primary_space = h.run_tool(
        "spaces.create",
        title=h.name("automation-space"),
        description="Automation contract validation space",
        access="for_everyone",
    )
    h.state["space_id"] = primary_space["id"]
    h.push_cleanup("delete automation validation space", "spaces.delete", space_id=h.state["space_id"])

    secondary_space = h.run_tool(
        "spaces.create",
        title=h.name("automation-space-secondary"),
        description="Secondary automation contract validation space",
        access="for_everyone",
    )
    h.state["secondary_space_id"] = secondary_space["id"]
    h.push_cleanup("delete secondary automation validation space", "spaces.delete", space_id=h.state["secondary_space_id"])

    created, payload = h.run_tool_maybe(
        "automations.create",
        expected_error_statuses={400, 403, 405},
        space_id=h.state["space_id"],
        name=h.name("automation"),
        type="on_action",
        trigger={"type": "card_created"},
        actions=_automation_actions(h.state["current_user_id"]),
    )
    h.run_tool("automations.list", space_id=h.state["space_id"])

    if not created:
        pytest.fail(f"Known-good automation payload is still rejected on sandbox: {payload}")

    automation_id = payload["id"]
    h.push_cleanup("delete automation", "automations.delete", space_id=h.state["space_id"], automation_id=automation_id)

    h.run_tool_maybe(
        "automations.get",
        expected_error_statuses={405},
        space_id=h.state["space_id"],
        automation_id=automation_id,
    )
    h.run_tool(
        "automations.update",
        space_id=h.state["space_id"],
        automation_id=automation_id,
        name=h.name("automation-updated"),
    )

    copied, copied_payload = h.run_tool_maybe(
        "automations.copy",
        expected_error_statuses={400, 403, 404, 405},
        space_id=h.state["space_id"],
        automation_id=automation_id,
        target_space_id=h.state["secondary_space_id"],
    )
    if copied and isinstance(copied_payload, dict) and "id" in copied_payload:
        h.push_cleanup(
            "delete copied automation",
            "automations.delete",
            space_id=h.state["secondary_space_id"],
            automation_id=copied_payload["id"],
        )
