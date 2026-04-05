from __future__ import annotations

from kaiten_cli.live_contracts import (
    LIVE_POLICY_EXCLUSIONS,
    VALID_LIVE_STATUSES,
    get_live_contract,
    iter_special_live_contracts,
)
from kaiten_cli.registry import iter_tools, resolve_tool


def test_all_tools_have_a_live_contract_status():
    statuses = {tool.canonical_name: get_live_contract(tool.canonical_name).status for tool in iter_tools()}

    assert statuses
    assert set(statuses.values()) <= VALID_LIVE_STATUSES


def test_special_live_contracts_point_to_real_tools():
    missing: list[str] = []
    for name, _ in iter_special_live_contracts():
        try:
            resolve_tool(name)
        except KeyError:
            missing.append(name)

    assert missing == []


def test_policy_exclusions_match_live_contracts():
    assert LIVE_POLICY_EXCLUSIONS == {
        "api-keys.create": "Creating API keys is excluded from live validation because teardown would require testing key deletion.",
        "api-keys.delete": "Deleting API keys is explicitly excluded from live validation by user instruction.",
    }


def test_projects_cards_list_is_classified_as_synthetic_read():
    contract = get_live_contract("projects.cards.list")

    assert contract.status == "synthetic_read"
    assert contract.expected_statuses == (405,)
