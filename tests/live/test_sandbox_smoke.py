from __future__ import annotations

import json
import os
import time

import pytest

from kaiten_cli.app import cli

pytestmark = pytest.mark.live


def _env() -> dict[str, str]:
    domain = os.environ.get("KAITEN_DOMAIN")
    token = os.environ.get("KAITEN_TOKEN")
    if os.environ.get("KAITEN_LIVE") != "1" or not domain or not token:
        pytest.skip("Live sandbox smoke test is opt-in. Set KAITEN_LIVE=1 with sandbox credentials.")
    return {"KAITEN_DOMAIN": domain, "KAITEN_TOKEN": token}


def _pause() -> None:
    time.sleep(0.5)


@pytest.mark.timeout(120)
def test_sandbox_smoke_sequential(runner, socket_enabled):
    env = _env()
    card_id: int | None = None
    time_log_id: int | None = None

    try:
        company = runner.invoke(
            cli,
            ["--json", "company", "current"],
            env=env,
        )
        assert company.exit_code == 0, company.output
        company_payload = json.loads(company.output)
        assert company_payload["success"] is True
        assert company_payload["data"]["id"]
        _pause()

        current_user = runner.invoke(
            cli,
            ["--json", "users", "current"],
            env=env,
        )
        assert current_user.exit_code == 0, current_user.output
        current_user_payload = json.loads(current_user.output)
        assert current_user_payload["success"] is True
        assert current_user_payload["data"]["id"]
        _pause()

        users = runner.invoke(
            cli,
            ["--json", "users", "list", "--limit", "5", "--compact"],
            env=env,
        )
        assert users.exit_code == 0, users.output
        users_payload = json.loads(users.output)
        assert users_payload["success"] is True
        assert isinstance(users_payload["data"], list)
        _pause()

        calendars = runner.invoke(
            cli,
            ["--json", "calendars", "list", "--limit", "5"],
            env=env,
        )
        assert calendars.exit_code == 0, calendars.output
        calendars_payload = json.loads(calendars.output)
        assert calendars_payload["success"] is True
        assert calendars_payload["data"]
        calendar_id = calendars_payload["data"][0]["id"]
        _pause()

        calendar = runner.invoke(
            cli,
            ["--json", "calendars", "get", "--calendar-id", str(calendar_id)],
            env=env,
        )
        assert calendar.exit_code == 0, calendar.output
        calendar_payload = json.loads(calendar.output)
        assert calendar_payload["success"] is True
        assert str(calendar_payload["data"]["id"]) == str(calendar_id)
        _pause()

        spaces = runner.invoke(
            cli,
            ["--json", "spaces", "list", "--compact", "--fields", "id,title"],
            env=env,
        )
        assert spaces.exit_code == 0, spaces.output
        spaces_payload = json.loads(spaces.output)
        assert spaces_payload["success"] is True
        assert spaces_payload["data"]
        space_id = spaces_payload["data"][0]["id"]
        _pause()

        boards = runner.invoke(
            cli,
            ["--json", "boards", "list", "--space-id", str(space_id), "--compact", "--fields", "id,title"],
            env=env,
        )
        assert boards.exit_code == 0, boards.output
        boards_payload = json.loads(boards.output)
        assert boards_payload["success"] is True
        assert boards_payload["data"]
        board_id = boards_payload["data"][0]["id"]
        _pause()

        columns = runner.invoke(
            cli,
            ["--json", "columns", "list", "--board-id", str(board_id)],
            env=env,
        )
        assert columns.exit_code == 0, columns.output
        columns_payload = json.loads(columns.output)
        assert columns_payload["success"] is True
        assert columns_payload["data"]
        _pause()

        lanes = runner.invoke(
            cli,
            ["--json", "lanes", "list", "--board-id", str(board_id)],
            env=env,
        )
        assert lanes.exit_code == 0, lanes.output
        lanes_payload = json.loads(lanes.output)
        assert lanes_payload["success"] is True
        assert isinstance(lanes_payload["data"], list)
        _pause()

        cards = runner.invoke(
            cli,
            ["--json", "cards", "list", "--board-id", str(board_id), "--limit", "5", "--compact", "--fields", "id,title,state"],
            env=env,
        )
        assert cards.exit_code == 0, cards.output
        cards_payload = json.loads(cards.output)
        assert cards_payload["success"] is True
        _pause()

        title = f"codex-cli-live-{int(time.time())}"
        created = runner.invoke(
            cli,
            ["--json", "cards", "create", "--title", title, "--board-id", str(board_id), "--compact", "--fields", "id,title,state,board_id"],
            env=env,
        )
        assert created.exit_code == 0, created.output
        created_payload = json.loads(created.output)
        assert created_payload["success"] is True
        card_id = created_payload["data"]["id"]
        _pause()

        fetched = runner.invoke(
            cli,
            ["--json", "cards", "get", "--card-id", str(card_id), "--compact", "--fields", "id,title,state,board_id"],
            env=env,
        )
        assert fetched.exit_code == 0, fetched.output
        fetched_payload = json.loads(fetched.output)
        assert fetched_payload["data"]["id"] == card_id
        _pause()

        updated_title = f"{title}-updated"
        updated = runner.invoke(
            cli,
            ["--json", "cards", "update", "--card-id", str(card_id), "--title", updated_title, "--compact", "--fields", "id,title,state"],
            env=env,
        )
        assert updated.exit_code == 0, updated.output
        updated_payload = json.loads(updated.output)
        assert updated_payload["data"]["title"] == updated_title
        _pause()

        time_log_created = runner.invoke(
            cli,
            ["--json", "time-logs", "create", "--card-id", str(card_id), "--time-spent", "15", "--comment", "Smoke log"],
            env=env,
        )
        assert time_log_created.exit_code == 0, time_log_created.output
        time_log_created_payload = json.loads(time_log_created.output)
        assert time_log_created_payload["success"] is True
        time_log_id = time_log_created_payload["data"]["id"]
        _pause()

        time_logs = runner.invoke(
            cli,
            ["--json", "time-logs", "list", "--card-id", str(card_id)],
            env=env,
        )
        assert time_logs.exit_code == 0, time_logs.output
        time_logs_payload = json.loads(time_logs.output)
        assert time_logs_payload["success"] is True
        assert any(item["id"] == time_log_id for item in time_logs_payload["data"])
        _pause()

        time_log_updated = runner.invoke(
            cli,
            ["--json", "time-logs", "update", "--card-id", str(card_id), "--time-log-id", str(time_log_id), "--time-spent", "20", "--comment", "Smoke log updated"],
            env=env,
        )
        assert time_log_updated.exit_code == 0, time_log_updated.output
        time_log_updated_payload = json.loads(time_log_updated.output)
        assert time_log_updated_payload["success"] is True
        _pause()
    finally:
        if time_log_id is not None and card_id is not None:
            runner.invoke(
                cli,
                ["--json", "time-logs", "delete", "--card-id", str(card_id), "--time-log-id", str(time_log_id)],
                env=env,
            )
            _pause()
        if card_id is not None:
            runner.invoke(
                cli,
                ["--json", "cards", "delete", "--card-id", str(card_id), "--compact", "--fields", "id,title,condition"],
                env=env,
            )
