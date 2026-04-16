from __future__ import annotations

import json

from kaiten_cli.errors import BatchExecutionError, ConfigError
from kaiten_cli.runtime.output import render_error, render_success


def test_render_success_json():
    payload = json.loads(render_success("cards.list", [{"id": 1}], True))
    assert payload["success"] is True
    assert payload["command"] == "cards.list"
    assert payload["data"] == [{"id": 1}]


def test_render_error_json():
    payload = json.loads(render_error("cards.list", ConfigError("missing config"), True))
    assert payload["success"] is False
    assert payload["command"] == "cards.list"
    assert payload["error"]["type"] == "config_error"


def test_render_batch_execution_error_json_includes_data():
    payload = json.loads(
        render_error(
            "card-location-history.batch-get",
            BatchExecutionError("all failed", {"items": [], "errors": [{"card_id": 1}], "meta": {"failed": 1}}),
            True,
        )
    )

    assert payload["error"]["type"] == "batch_execution_error"
    assert payload["error"]["data"]["meta"]["failed"] == 1
