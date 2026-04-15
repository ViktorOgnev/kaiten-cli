from __future__ import annotations

from kaiten_cli.runtime.client import DEFAULT_TIMEOUT, HEAVY_TIMEOUT
from kaiten_cli.runtime.executor import timeout_for_tool
from kaiten_cli.models import OperationSpec, ResponsePolicy
from kaiten_cli.registry import resolve_tool
from kaiten_cli.registry.base import make_tool


def test_timeout_default_for_regular_tool():
    tool = resolve_tool("cards.list")
    assert timeout_for_tool(tool) == DEFAULT_TIMEOUT


def test_timeout_heavy_for_heavy_tool():
    tool = make_tool(
        canonical_name="cards.heavy",
        mcp_alias="kaiten_cards_heavy",
        description="Heavy test tool",
        input_schema={"type": "object", "properties": {}},
        operation=OperationSpec(method="GET", path_template="/cards"),
        response_policy=ResponsePolicy(heavy=True),
    )
    assert timeout_for_tool(tool) == HEAVY_TIMEOUT
