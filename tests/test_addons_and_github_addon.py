from __future__ import annotations

import json

import pytest
import respx
from httpx import Response

from kaiten_cli.app import cli
from kaiten_cli.errors import MutationBlockedError, ValidationError
from kaiten_cli.registry import resolve_tool
from kaiten_cli.runtime.executor import (
    build_request,
    execute_tool,
    execute_tool_with_diagnostics,
)
from kaiten_cli.runtime.input import merge_inputs
from kaiten_cli.runtime.support.addons import (
    attached_items,
    explicit_addon_uid,
    generate_addon_uid,
    map_rest_branch,
    map_rest_commit,
    map_rest_issue,
    map_rest_pull,
    validate_addon_uid_value,
)

API = "https://sandbox.kaiten.ru/api/latest"
CARD_URL = f"{API}/cards/10"
SPACE_ADDONS_URL = f"{API}/spaces/5/addons"
# Same UID the platform derives for an addon mounted at /github.
GITHUB_ADDON_UID = "0ce23a01-560f-51e0-9982-1e3445dc5990"
CARD_ADDON_DATA_URL = f"{API}/cards/10/addons-data/{GITHUB_ADDON_UID}"
ENV = {"KAITEN_DOMAIN": "sandbox", "KAITEN_TOKEN": "test-token"}


def _rest_pull(pull_id: int = 111, number: int = 42) -> dict:
    return {
        "id": pull_id,
        "number": number,
        "html_url": f"https://github.com/acme/web/pull/{number}",
        "state": "open",
        "title": "Add login",
        "body": "Body",
        "created_at": "2026-01-01T00:00:00Z",
        "user": {
            "login": "octocat",
            "html_url": "https://github.com/octocat",
            "avatar_url": "https://github.com/octocat.png",
        },
        "base": {"ref": "master", "repo": {"name": "web", "owner": {"login": "acme"}}},
        "head": {"ref": "feature/login"},
    }


def _addon_pull(pull_id: int = 111, number: int = 42) -> dict:
    return {
        "id": pull_id,
        "number": number,
        "htmlUrl": f"https://github.com/acme/web/pull/{number}",
        "state": "open",
        "title": "Add login",
        "body": "Body",
        "createdAt": "2026-01-01T00:00:00Z",
        "author": {
            "login": "octocat",
            "htmlUrl": "https://github.com/octocat",
            "avatar": "https://github.com/octocat.png",
        },
        "baseBranch": "master",
        "headBranch": "feature/login",
        "repoName": "web",
        "repoOwner": "acme",
    }


def _github_addon(uid: str = GITHUB_ADDON_UID, path: str = "/github") -> dict:
    return {"id": uid, "name": "Github", "iframe_initial_url": f"https://addons.example{path}"}


def _mock_addon_lookup(
    addons: list[dict] | None = None,
    *,
    board_spaces: list[int] | None = None,
    other_space_addons: dict[int, list[dict]] | None = None,
) -> None:
    """Mock the card read the UID resolution actually uses.

    A real card response embeds `board.spaces[].addons`, filtered to the addons
    available for that card, so one read answers the question.
    """

    spaces = [{"id": 5, "addons": addons or []}]
    for space_id in board_spaces or []:
        if space_id == 5:
            continue
        spaces.append({"id": space_id, "addons": (other_space_addons or {}).get(space_id, [])})
    respx.get(CARD_URL).mock(
        return_value=Response(
            200, json={"id": 10, "board_id": 7, "board": {"id": 7, "spaces": spaces}}
        )
    )


def _mock_legacy_card() -> None:
    """A card response without the embedded board spaces, as an older server sends."""

    respx.get(CARD_URL).mock(return_value=Response(200, json={"id": 10, "board_id": 7}))


def _rows(data: dict | None, *, private: dict | None = None) -> list[dict]:
    rows = [
        {
            "id": "row-shared",
            "card_uid": "card-uid",
            "addon_uid": GITHUB_ADDON_UID,
            "user_uid": None,
            "data": data,
        }
    ]
    if private is not None:
        rows.append(
            {
                "id": "row-private",
                "card_uid": "card-uid",
                "addon_uid": GITHUB_ADDON_UID,
                "user_uid": "user-uid",
                "data": private,
            }
        )
    return rows


def test_help_shows_addon_namespaces(runner):
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "addons" in result.output
    assert "space-addons" in result.output
    assert "card-addon-data" in result.output
    assert "github-addon" in result.output


def test_resolve_addon_aliases():
    assert resolve_tool("kaiten_get_card_addon_data").canonical_name == "card-addon-data.get"
    assert resolve_tool("kaiten_derive_addon_uid").canonical_name == "addons.uid"
    assert resolve_tool("kaiten_attach_github_pull").canonical_name == "github-addon.pulls.attach"


def test_derived_addon_uid_matches_the_platform_derivation():
    # kaiten-lib/src/shared/addons/generateAddonUid.js produces exactly this UID
    # for the addon mounted at /github; the CLI must stay byte-compatible.
    assert generate_addon_uid("/github") == GITHUB_ADDON_UID
    assert generate_addon_uid("github") == GITHUB_ADDON_UID
    assert generate_addon_uid("/GitHub/") == GITHUB_ADDON_UID
    assert generate_addon_uid("/sipuni") != GITHUB_ADDON_UID


def test_explicit_addon_uid_is_validated_and_lowercased():
    assert explicit_addon_uid({}) is None
    assert explicit_addon_uid({"addon_url_path": "/gh-mirror"}) is None
    # Kaiten compares the path segment to a lowercase Postgres uuid with ===,
    # so an uppercase UUID reads fine and then fails every write with 403.
    assert explicit_addon_uid({"addon_uid": GITHUB_ADDON_UID.upper()}) == GITHUB_ADDON_UID


def test_addon_uid_validation_matches_the_server_route_rule():
    assert validate_addon_uid_value("0CE23A01-560F-51E0-9982-1E3445DC5990") == GITHUB_ADDON_UID

    # uuidIdRule requires version 4 or 5 and the RFC-4122 variant; anything the
    # route rejects can never address an addon.
    for rejected in (
        "00000000-0000-0000-0000-000000000000",
        "0ce23a01-560f-11e0-9982-1e3445dc5990",
        "0ce23a01-560f-51e0-0982-1e3445dc5990",
        "not-a-uuid",
    ):
        with pytest.raises(ValidationError):
            validate_addon_uid_value(rejected)


def test_attached_items_only_reads_the_shared_row():
    rows = _rows({"attachedPulls": [_addon_pull()]}, private={"attachedPulls": [_addon_pull(9, 9)]})

    items = attached_items(rows, "attachedPulls")

    assert [item["id"] for item in items] == [111]


@pytest.mark.parametrize(
    "rows",
    [
        [],
        _rows(None),
        _rows({}),
        _rows({"attachedPulls": "not-a-list"}),
        "not-a-list",
    ],
)
def test_attached_items_tolerates_missing_or_malformed_data(rows):
    assert attached_items(rows, "attachedPulls") == []


def test_map_rest_pull_matches_the_addon_dto():
    assert map_rest_pull(_rest_pull(), {}) == _addon_pull()


def test_map_rest_pull_uses_addon_placeholders_for_cosmetic_fields():
    minimal = {
        "id": 1,
        "number": 2,
        "html_url": "https://github.com/acme/web/pull/2",
        "base": {"repo": {"name": "web", "owner": {"login": "acme"}}},
    }

    mapped = map_rest_pull(minimal, {})

    assert mapped["author"] == {
        "login": "Неизвестный автор",
        "htmlUrl": "https://github.com",
        "avatar": "https://avatars.githubusercontent.com/u/583231?v=4",
    }
    assert mapped["baseBranch"] == "no data"


def test_map_rest_pull_rejects_a_payload_without_github_ids():
    with pytest.raises(ValidationError):
        map_rest_pull({"number": 2}, {})


def test_map_rest_pull_rejects_a_payload_without_a_repository():
    # The widget refreshes an attachment by (repoOwner, repoName, number), so a
    # placeholder repository would store an entry that can never resolve again.
    trimmed = {"id": 1, "number": 2, "html_url": "https://github.com/acme/web/pull/2"}

    with pytest.raises(ValidationError):
        map_rest_pull(trimmed, {})


def test_map_rest_pull_accepts_an_explicit_repository_fallback():
    trimmed = {"id": 1, "number": 2, "html_url": "https://github.com/acme/web/pull/2"}

    mapped = map_rest_pull(trimmed, {"owner": "acme", "repo": "web"})

    assert (mapped["repoOwner"], mapped["repoName"]) == ("acme", "web")


def test_build_request_for_card_addon_data_set():
    tool = resolve_tool("card-addon-data.set")
    payload = merge_inputs(
        tool,
        {
            "card_id": 10,
            "addon_uid": GITHUB_ADDON_UID,
            "type": "shared",
            "data": '{"attachedPulls": []}',
        },
    )

    path, query, body = build_request(tool, payload)

    assert path == f"/cards/10/addons-data/{GITHUB_ADDON_UID}"
    assert query is None
    assert body == {"type": "shared", "data": {"attachedPulls": []}}


def test_card_addon_data_set_rejects_an_unknown_scope():
    tool = resolve_tool("card-addon-data.set")

    with pytest.raises(ValidationError):
        merge_inputs(
            tool,
            {"card_id": 10, "addon_uid": GITHUB_ADDON_UID, "type": "team", "data": {}},
        )


def test_build_request_for_space_addon_install():
    tool = resolve_tool("space-addons.install")
    payload = merge_inputs(
        tool, {"space_id": 1, "addon_uid": GITHUB_ADDON_UID, "settings": {"repo": "acme/web"}}
    )

    path, query, body = build_request(tool, payload)

    assert path == f"/spaces/1/addons/{GITHUB_ADDON_UID}"
    assert query is None
    assert body == {"settings": {"repo": "acme/web"}}


async def test_addons_uid_needs_no_profile_and_no_request():
    tool = resolve_tool("addons.uid")

    result = await execute_tool(tool, merge_inputs(tool, {"url_path": "/github"}))

    assert result == {
        "url_path": "/github",
        "normalized_url_path": "github",
        "addon_uid": GITHUB_ADDON_UID,
    }


@respx.mock
async def test_pulls_list_returns_the_shared_attachments(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )

    tool = resolve_tool("github-addon.pulls.list")
    result = await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))

    assert [item["htmlUrl"] for item in result] == ["https://github.com/acme/web/pull/42"]


@respx.mock
async def test_pulls_attach_appends_the_mapped_entry(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    existing = _addon_pull(222, 7)
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": [existing]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={"id": 1}))

    tool = resolve_tool("github-addon.pulls.attach")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "pull_json": _rest_pull()})
    )

    assert result["status"] == "attached"
    assert result["attached_count"] == 2
    assert result["addon_uid"] == GITHUB_ADDON_UID
    sent = json.loads(patch_route.calls.last.request.content)
    assert sent == {"type": "shared", "data": {"attachedPulls": [existing, _addon_pull()]}}


@respx.mock
async def test_pulls_attach_is_idempotent_by_github_id(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.attach")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "pull_json": _rest_pull()})
    )

    assert result["status"] == "already_attached"
    assert not patch_route.called


@respx.mock
async def test_pulls_attach_dry_run_does_not_write(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup([_github_addon()])
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.attach")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "pull_json": _rest_pull(), "dry_run": True})
    )

    assert result["status"] == "would_attach"
    assert result["item"] == _addon_pull()
    assert not patch_route.called


@respx.mock
async def test_pulls_attach_preserves_sibling_addon_keys(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(
            200, json=_rows({"attachedBranches": [{"pseudoId": "acme/web/master"}]})
        )
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.attach")
    await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "pull_json": _rest_pull()}))

    # The server shallow-merges by top-level key, so only attachedPulls is sent.
    sent = json.loads(patch_route.calls.last.request.content)
    assert set(sent["data"]) == {"attachedPulls"}


@respx.mock
async def test_pulls_detach_removes_only_the_selected_entry(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    kept = _addon_pull(222, 7)
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull(), kept]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.detach")
    result = await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "number": 42}))

    assert result["status"] == "detached"
    assert [item["id"] for item in result["removed"]] == [111]
    sent = json.loads(patch_route.calls.last.request.content)
    assert sent == {"type": "shared", "data": {"attachedPulls": [kept]}}


@respx.mock
async def test_pulls_detach_of_the_last_entry_writes_null(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.detach")
    result = await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "pull_id": 111}))

    assert result["attached_count"] == 0
    sent = json.loads(patch_route.calls.last.request.content)
    assert sent == {"type": "shared", "data": {"attachedPulls": None}}


@respx.mock
async def test_pulls_detach_without_a_match_does_not_write(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.detach")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "number": 42, "repo": "other"})
    )

    assert result["status"] == "not_found"
    assert result["attached_count"] == 1
    assert not patch_route.called


async def test_detach_requires_a_selector(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    tool = resolve_tool("github-addon.pulls.detach")

    with pytest.raises(ValidationError):
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))


@respx.mock
async def test_branch_attach_builds_the_addon_identity(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup([_github_addon()])
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.branches.attach")
    result = await execute_tool(
        tool,
        merge_inputs(
            tool,
            {
                "card_id": 10,
                "owner": "acme",
                "repo": "web",
                "branch_json": {
                    "name": "feature/login",
                    "commit": {"url": "https://api.github.com/repos/acme/web/commits/abc"},
                },
            },
        ),
    )

    assert result["item"] == {
        "branchName": "feature/login",
        "htmlUrl": "https://github.com/acme/web/tree/feature/login",
        "commitUrl": "https://api.github.com/repos/acme/web/commits/abc",
        "repo": "web",
        "owner": "acme",
        "pseudoId": "acme/web/feature/login",
    }
    sent = json.loads(patch_route.calls.last.request.content)
    assert set(sent["data"]) == {"attachedBranches"}


@respx.mock
async def test_commit_attach_falls_back_to_the_git_author(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup([_github_addon()])
    respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.commits.attach")
    result = await execute_tool(
        tool,
        merge_inputs(
            tool,
            {
                "card_id": 10,
                "owner": "acme",
                "repo": "web",
                "commit_json": {
                    "sha": "abc123",
                    "html_url": "https://github.com/acme/web/commit/abc123",
                    "commit": {
                        "message": "Fix login",
                        "author": {"name": "Unlinked Author", "date": "2026-01-01T00:00:00Z"},
                    },
                },
            },
        ),
    )

    assert result["item"]["author"]["login"] == "Unlinked Author"
    assert result["item"]["date"] == "2026-01-01T00:00:00Z"


async def test_issue_attach_rejects_a_pull_request_payload(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    tool = resolve_tool("github-addon.issues.attach")
    payload = merge_inputs(
        tool,
        {
            "card_id": 10,
            "owner": "acme",
            "repo": "web",
            "issue_json": {"id": 1, "number": 2, "pull_request": {"url": "https://example"}},
        },
    )

    with pytest.raises(ValidationError):
        await execute_tool(tool, payload)


async def test_read_only_mode_blocks_addon_writes():
    tool = resolve_tool("github-addon.pulls.attach")
    payload = merge_inputs(tool, {"card_id": 10, "pull_json": _rest_pull()})

    with pytest.raises(MutationBlockedError):
        await execute_tool(tool, payload, read_only=True)


@respx.mock
def test_cli_pulls_list_supports_field_selection(runner):
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )

    result = runner.invoke(
        cli,
        ["--json", "github-addon", "pulls", "list", "--card-id", "10", "--fields", "number,state"],
        env=ENV,
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["success"] is True
    assert payload["data"] == [{"number": 42, "state": "open"}]


@respx.mock
def test_cli_pulls_attach_accepts_a_custom_addon_mount_path(runner):
    mirror_uid = generate_addon_uid("/gh-mirror")
    url = f"{API}/cards/10/addons-data/{mirror_uid}"
    respx.get(url).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup([_github_addon(mirror_uid, "/gh-mirror")])
    respx.patch(url).mock(return_value=Response(200, json={}))

    result = runner.invoke(
        cli,
        [
            "--json",
            "github-addon",
            "pulls",
            "attach",
            "--card-id",
            "10",
            "--addon-url-path",
            "/gh-mirror",
            "--pull-json",
            json.dumps(_rest_pull()),
        ],
        env=ENV,
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["data"]["addon_uid"] == mirror_uid
    assert payload["data"]["status"] == "attached"


@respx.mock
async def test_pulls_detach_rejects_an_ambiguous_selector(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    other_repo = {**_addon_pull(222, 42), "repoOwner": "other", "repoName": "api"}
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull(), other_repo]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.detach")

    with pytest.raises(ValidationError) as error:
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "number": 42}))

    assert "acme/web#42" in str(error.value)
    assert "other/api#42" in str(error.value)
    assert not patch_route.called


@respx.mock
async def test_pulls_detach_removes_every_match_with_all(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    other_repo = {**_addon_pull(222, 42), "repoOwner": "other", "repoName": "api"}
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull(), other_repo]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.detach")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "number": 42, "all": True})
    )

    assert result["status"] == "detached"
    assert len(result["removed"]) == 2
    sent = json.loads(patch_route.calls.last.request.content)
    assert sent == {"type": "shared", "data": {"attachedPulls": None}}


@respx.mock
async def test_pulls_detach_narrowed_by_repository_removes_one(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    other_repo = {**_addon_pull(222, 42), "repoOwner": "other", "repoName": "api"}
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull(), other_repo]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.detach")
    result = await execute_tool(
        tool,
        merge_inputs(tool, {"card_id": 10, "number": 42, "owner": "acme", "repo": "web"}),
    )

    assert [item["id"] for item in result["removed"]] == [111]
    sent = json.loads(patch_route.calls.last.request.content)
    assert sent["data"]["attachedPulls"] == [other_repo]


async def test_detach_rejects_a_blank_selector(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    tool = resolve_tool("github-addon.branches.detach")

    with pytest.raises(ValidationError):
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "branch_name": "  "}))


@respx.mock
async def test_branch_attach_prepends_like_the_addon_ui(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    existing = {"branchName": "master", "pseudoId": "acme/web/master"}
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedBranches": [existing]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.branches.attach")
    await execute_tool(
        tool,
        merge_inputs(
            tool,
            {
                "card_id": 10,
                "owner": "acme",
                "repo": "web",
                "branch_json": {"name": "feature/login"},
            },
        ),
    )

    # branch-select.jsx prepends a new branch; pulls, commits and issues append.
    sent = json.loads(patch_route.calls.last.request.content)
    assert [item["pseudoId"] for item in sent["data"]["attachedBranches"]] == [
        "acme/web/feature/login",
        "acme/web/master",
    ]


def test_addon_uid_must_be_a_uuid():
    tool = resolve_tool("card-addon-data.get")

    with pytest.raises(ValidationError):
        merge_inputs(tool, {"card_id": 10, "addon_uid": "../../cards/999"})


async def test_github_addon_uid_override_must_be_a_uuid(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    tool = resolve_tool("github-addon.pulls.list")

    with pytest.raises(ValidationError):
        await execute_tool(
            tool, merge_inputs(tool, {"card_id": 10, "addon_uid": "../../cards/999"})
        )


@respx.mock
async def test_pulls_list_retries_with_the_registered_addon_uid(monkeypatch):
    """A derived UID is a guess outside on-prem; an empty read must not end the story."""

    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    registered_uid = "9f8e7d6c-5b4a-4392-8817-665544332211"
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup([_github_addon(registered_uid)])
    registered_route = respx.get(f"{API}/cards/10/addons-data/{registered_uid}").mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )

    tool = resolve_tool("github-addon.pulls.list")
    result = await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))

    assert [item["number"] for item in result] == [42]
    assert registered_route.called


@respx.mock
async def test_explicit_addon_uid_skips_the_space_lookup(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    card_route = respx.get(CARD_URL).mock(return_value=Response(200, json={"space_id": 5}))

    tool = resolve_tool("github-addon.pulls.list")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "addon_uid": GITHUB_ADDON_UID})
    )

    assert result == []
    assert not card_route.called


@respx.mock
async def test_unverifiable_empty_read_fails_instead_of_answering_nothing(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    respx.get(CARD_URL).mock(return_value=Response(403, json={"message": "no access"}))

    tool = resolve_tool("github-addon.pulls.list")

    # [] here could equally mean "nothing attached" or "wrong addon entirely".
    with pytest.raises(ValidationError) as error:
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))

    assert "--addon-uid" in str(error.value)


@respx.mock
async def test_confirmed_empty_read_is_an_answer(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup([_github_addon()])

    tool = resolve_tool("github-addon.pulls.list")

    # The addon was found and it is the UID we read, so [] is a real answer.
    assert await execute_tool(tool, merge_inputs(tool, {"card_id": 10})) == []


@respx.mock
async def test_writes_keep_going_when_the_space_lookup_fails(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    respx.get(CARD_URL).mock(return_value=Response(403, json={"message": "no access"}))
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.attach")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "pull_json": _rest_pull()})
    )

    # A write is verified by the server: a wrong UUID is rejected with 403, so
    # there is no silently wrong outcome to protect against.
    assert result["status"] == "attached"
    assert result["addon_uid_confirmed"] is False
    assert patch_route.called


@respx.mock
async def test_attach_envelope_reports_a_missing_addon_row(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup([_github_addon()])
    respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.attach")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "pull_json": _rest_pull()})
    )

    assert result["addon_data_row_found"] is False
    assert result["addon_uid"] == GITHUB_ADDON_UID


@respx.mock
async def test_raw_card_addon_data_read_is_not_transformed(monkeypatch):
    """The blob is opaque third-party JSON and feeds a read-modify-write cycle."""

    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    blob = {
        "description": "addon description",
        "icon": "data:image/png;base64,AAAA",
        "attachedPulls": [_addon_pull()],
    }
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=_rows(blob)))

    tool = resolve_tool("card-addon-data.get")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "addon_uid": GITHUB_ADDON_UID})
    )

    assert result[0]["data"] == blob


@respx.mock
async def test_branches_detach_matches_owner_repo_and_name(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    target = {
        "branchName": "feature/login",
        "owner": "acme",
        "repo": "web",
        "pseudoId": "acme/web/feature/login",
    }
    other = {
        "branchName": "feature/login",
        "owner": "other",
        "repo": "api",
        "pseudoId": "other/api/feature/login",
    }
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedBranches": [target, other]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.branches.detach")
    result = await execute_tool(
        tool,
        merge_inputs(
            tool,
            {"card_id": 10, "branch_name": "feature/login", "owner": "acme", "repo": "web"},
        ),
    )

    assert result["removed"] == [target]
    sent = json.loads(patch_route.calls.last.request.content)
    assert sent["data"]["attachedBranches"] == [other]


@respx.mock
async def test_branches_detach_by_pseudo_id_is_unambiguous(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    target = {
        "branchName": "feature/login",
        "owner": "acme",
        "repo": "web",
        "pseudoId": "acme/web/feature/login",
    }
    other = {
        "branchName": "feature/login",
        "owner": "other",
        "repo": "api",
        "pseudoId": "other/api/feature/login",
    }
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedBranches": [target, other]}))
    )
    respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.branches.detach")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "pseudo_id": "other/api/feature/login"})
    )

    assert result["removed"] == [other]


@respx.mock
async def test_branches_detach_rejects_an_ambiguous_branch_name(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    target = {"branchName": "main", "owner": "acme", "repo": "web", "pseudoId": "acme/web/main"}
    other = {"branchName": "main", "owner": "other", "repo": "api", "pseudoId": "other/api/main"}
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedBranches": [target, other]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.branches.detach")

    with pytest.raises(ValidationError) as error:
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "branch_name": "main"}))

    assert "acme/web/main" in str(error.value)
    assert not patch_route.called


@respx.mock
async def test_commits_detach_matches_sha_and_repository(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    sha = "0" * 40
    target = {"sha": sha, "owner": "acme", "repo": "web"}
    other = {"sha": sha, "owner": "other", "repo": "api"}
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedCommits": [target, other]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.commits.detach")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "sha": sha, "owner": "acme", "repo": "web"})
    )

    assert result["removed"] == [target]
    sent = json.loads(patch_route.calls.last.request.content)
    assert sent["data"]["attachedCommits"] == [other]


@respx.mock
async def test_commits_detach_ignores_a_short_sha(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    stored = {"sha": "0" * 40, "owner": "acme", "repo": "web"}
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedCommits": [stored]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.commits.detach")
    result = await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "sha": "0000000"}))

    assert result["status"] == "not_found"
    assert not patch_route.called


@respx.mock
async def test_issues_detach_by_number_and_repository(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    target = {"id": 7, "number": 3, "repoOwner": "acme", "repoName": "web"}
    other = {"id": 8, "number": 3, "repoOwner": "other", "repoName": "api"}
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedIssues": [target, other]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.issues.detach")
    result = await execute_tool(
        tool,
        merge_inputs(tool, {"card_id": 10, "number": 3, "owner": "acme", "repo": "web"}),
    )

    assert result["removed"] == [target]
    sent = json.loads(patch_route.calls.last.request.content)
    assert sent["data"]["attachedIssues"] == [other]


@respx.mock
async def test_issues_detach_by_id_is_unambiguous(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    target = {"id": 7, "number": 3, "repoOwner": "acme", "repoName": "web"}
    other = {"id": 8, "number": 3, "repoOwner": "other", "repoName": "api"}
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedIssues": [target, other]}))
    )
    respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.issues.detach")
    result = await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "issue_id": 8}))

    assert result["removed"] == [other]


@respx.mock
async def test_detach_dry_run_reports_without_writing(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.detach")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "number": 42, "dry_run": True})
    )

    assert result["status"] == "would_detach"
    assert result["attached_count"] == 0
    assert [item["id"] for item in result["removed"]] == [111]
    assert not patch_route.called


def test_issue_mapping_requires_a_repository():
    issue = {"id": 1, "number": 2, "html_url": "https://github.com/acme/web/issues/2"}

    with pytest.raises(ValidationError):
        map_rest_issue(issue, {})

    assert map_rest_issue(issue, {"owner": "acme", "repo": "web"})["repoOwner"] == "acme"


def test_attach_mapping_requires_the_link_the_addon_always_stores():
    with pytest.raises(ValidationError):
        map_rest_pull(
            {"id": 1, "number": 2, "base": {"repo": {"name": "web", "owner": {"login": "acme"}}}},
            {},
        )

    with pytest.raises(ValidationError):
        map_rest_commit({"sha": "abc"}, {"owner": "acme", "repo": "web"})


def test_blank_repository_options_are_rejected_on_attach():
    pull = {"id": 1, "number": 2, "html_url": "https://github.com/acme/web/pull/2"}

    with pytest.raises(ValidationError):
        map_rest_pull(pull, {"owner": "  ", "repo": "  "})

    branch = map_rest_branch({"name": "feat"}, {"owner": " acme ", "repo": " web "})
    assert branch["pseudoId"] == "acme/web/feat"


@respx.mock
async def test_issues_attach_is_idempotent_by_github_id(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    stored = {"id": 5, "number": 3, "repoOwner": "acme", "repoName": "web"}
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedIssues": [stored]}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.issues.attach")
    result = await execute_tool(
        tool,
        merge_inputs(
            tool,
            {
                "card_id": 10,
                "owner": "acme",
                "repo": "web",
                "issue_json": {
                    "id": 5,
                    "number": 3,
                    "html_url": "https://github.com/acme/web/issues/3",
                },
            },
        ),
    )

    assert result["status"] == "already_attached"
    assert not patch_route.called


@respx.mock
async def test_commits_detach_ambiguity_names_the_repositories(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    sha = "0" * 40
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(
            200,
            json=_rows(
                {
                    "attachedCommits": [
                        {"sha": sha, "owner": "acme", "repo": "web"},
                        {"sha": sha, "owner": "other", "repo": "api"},
                    ]
                }
            ),
        )
    )

    tool = resolve_tool("github-addon.commits.detach")

    with pytest.raises(ValidationError) as error:
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "sha": sha}))

    assert f"acme/web@{sha}" in str(error.value)


@respx.mock
def test_verbose_reports_a_missing_addon_data_row(runner):
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup([_github_addon()])

    result = runner.invoke(
        cli,
        ["--json", "--verbose", "github-addon", "pulls", "list", "--card-id", "10"],
        env=ENV,
    )

    assert result.exit_code == 0
    assert "no shared row" in result.stderr


@respx.mock
async def test_addon_is_found_in_another_space_of_the_same_board(monkeypatch):
    """A board can sit in several spaces, and the server checks all of them."""

    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    registered_uid = "9f8e7d6c-5b4a-4392-8817-665544332211"
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    # The card's own space has no GitHub addon; the board is also in space 9.
    _mock_addon_lookup(
        [],
        board_spaces=[5, 9],
        other_space_addons={9: [_github_addon(registered_uid)]},
    )
    respx.get(f"{API}/cards/10/addons-data/{registered_uid}").mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )

    tool = resolve_tool("github-addon.pulls.list")
    result = await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))

    assert [item["number"] for item in result] == [42]


@respx.mock
async def test_card_reporting_no_addon_is_a_real_empty_answer(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup([])

    tool = resolve_tool("github-addon.pulls.list")

    # The card itself lists the addons it may use, so "none of them" is an answer.
    assert await execute_tool(tool, merge_inputs(tool, {"card_id": 10})) == []


@respx.mock
async def test_attach_says_why_when_the_card_has_no_such_addon(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup([])
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.attach")

    with pytest.raises(ValidationError) as error:
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "pull_json": _rest_pull()}))

    assert "nothing to write to" in str(error.value)
    assert not patch_route.called


@respx.mock
async def test_attach_refuses_to_rewrite_a_list_with_non_object_entries(monkeypatch):
    """A rewrite replaces the whole key, so unknown entries would be destroyed."""

    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(
            200, json=_rows({"attachedPulls": [_addon_pull(), None, "legacy-marker"]})
        )
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.attach")

    with pytest.raises(ValidationError) as error:
        await execute_tool(
            tool, merge_inputs(tool, {"card_id": 10, "pull_json": _rest_pull(222, 7)})
        )

    assert "position(s) 1, 2" in str(error.value)
    assert not patch_route.called


@respx.mock
async def test_detach_refuses_to_rewrite_a_non_list_value(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": {"legacy": "object"}}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.detach")

    with pytest.raises(ValidationError) as error:
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "number": 42}))

    assert "not a list" in str(error.value)
    assert not patch_route.called


@respx.mock
async def test_list_still_tolerates_what_a_write_refuses(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(
            200, json=_rows({"attachedPulls": [_addon_pull(), None, "legacy-marker"]})
        )
    )

    tool = resolve_tool("github-addon.pulls.list")
    result = await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))

    assert [item["number"] for item in result] == [42]


@respx.mock
async def test_attach_starts_from_empty_when_the_addon_cleared_the_key(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    # The addon UI writes null instead of [] when the last entry is removed.
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(200, json=_rows({"attachedPulls": None}))
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.attach")
    result = await execute_tool(
        tool, merge_inputs(tool, {"card_id": 10, "pull_json": _rest_pull()})
    )

    assert result["status"] == "attached"
    sent = json.loads(patch_route.calls.last.request.content)
    assert sent["data"]["attachedPulls"] == [_addon_pull()]


@respx.mock
async def test_card_read_alone_resolves_the_addon(monkeypatch):
    """The space listing is megabytes on a real tenant; the card already knows."""

    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    registered_uid = "9f8e7d6c-5b4a-4392-8817-665544332211"
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup([_github_addon(registered_uid)])
    spaces_route = respx.get(f"{API}/spaces")
    space_addons_route = respx.get(SPACE_ADDONS_URL)
    respx.get(f"{API}/cards/10/addons-data/{registered_uid}").mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )

    tool = resolve_tool("github-addon.pulls.list")
    _, stats = await execute_tool_with_diagnostics(tool, merge_inputs(tool, {"card_id": 10}))

    # derived addons-data, the card, addons-data under the registered UID.
    assert stats.http_request_count == 3
    assert not spaces_route.called
    assert not space_addons_route.called


@respx.mock
async def test_unreadable_own_space_does_not_end_the_search(monkeypatch):
    """The space the caller cannot read is exactly why the other spaces matter."""

    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    registered_uid = "9f8e7d6c-5b4a-4392-8817-665544332211"
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_legacy_card()
    respx.get(SPACE_ADDONS_URL).mock(return_value=Response(403, json={"message": "no access"}))
    respx.get(f"{API}/spaces").mock(
        return_value=Response(
            200, json=[{"id": 5, "boards": [{"id": 7}]}, {"id": 9, "boards": [{"id": 7}]}]
        )
    )
    space_9 = respx.get(f"{API}/spaces/9/addons").mock(
        return_value=Response(200, json=[_github_addon(registered_uid)])
    )
    respx.get(f"{API}/cards/10/addons-data/{registered_uid}").mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )

    tool = resolve_tool("github-addon.pulls.list")
    result = await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))

    assert space_9.called
    assert [item["number"] for item in result] == [42]


@respx.mock
async def test_legacy_card_falls_back_to_the_space_listing(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    registered_uid = "9f8e7d6c-5b4a-4392-8817-665544332211"
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_legacy_card()
    respx.get(f"{API}/spaces").mock(
        return_value=Response(200, json=[{"id": 5, "boards": [{"id": 7}]}])
    )
    respx.get(SPACE_ADDONS_URL).mock(
        return_value=Response(200, json=[_github_addon(registered_uid)])
    )
    respx.get(f"{API}/cards/10/addons-data/{registered_uid}").mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )

    tool = resolve_tool("github-addon.pulls.list")

    assert [i["number"] for i in await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))] == [
        42
    ]


@respx.mock
async def test_malformed_space_listing_does_not_crash_the_command(monkeypatch):
    """The pagination guard raises ConfigError; this read is best effort."""

    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_legacy_card()
    respx.get(f"{API}/spaces").mock(return_value=Response(200, json={"message": "not a list"}))

    tool = resolve_tool("github-addon.pulls.list")

    with pytest.raises(ValidationError) as error:
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))

    assert "--addon-uid" in str(error.value)


@respx.mock
async def test_missing_board_id_skips_the_space_listing(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    respx.get(CARD_URL).mock(return_value=Response(200, json={"id": 10, "space_id": 5}))
    respx.get(SPACE_ADDONS_URL).mock(return_value=Response(200, json=[]))
    spaces_route = respx.get(f"{API}/spaces")

    tool = resolve_tool("github-addon.pulls.list")

    with pytest.raises(ValidationError):
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))

    assert not spaces_route.called


@respx.mock
async def test_space_listing_is_read_with_pagination_and_archived_spaces(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    registered_uid = "9f8e7d6c-5b4a-4392-8817-665544332211"
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    respx.get(CARD_URL).mock(
        return_value=Response(200, json={"id": 10, "space_id": 5, "board_id": 7})
    )
    respx.get(SPACE_ADDONS_URL).mock(return_value=Response(200, json=[]))
    # The board is only reachable through an archived space on the second page.
    first_page = [{"id": 100 + i, "boards": []} for i in range(100)]
    spaces_route = respx.get(f"{API}/spaces").mock(
        side_effect=[
            Response(200, json=first_page),
            Response(200, json=[{"id": 9, "archived": True, "boards": [{"id": 7}]}]),
            Response(200, json=[]),
        ]
    )
    respx.get(f"{API}/spaces/9/addons").mock(
        return_value=Response(200, json=[_github_addon(registered_uid)])
    )
    respx.get(f"{API}/cards/10/addons-data/{registered_uid}").mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )

    tool = resolve_tool("github-addon.pulls.list")
    result = await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))

    assert [item["number"] for item in result] == [42]
    assert spaces_route.calls[0].request.url.params["archived"] == "true"
    assert spaces_route.calls[0].request.url.params["limit"] == "100"


@respx.mock
async def test_two_addons_on_the_same_path_are_a_refusal_not_a_choice(monkeypatch):
    """A path is not an identity: on cloud the two UIDs are unrelated."""

    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    first = "9f8e7d6c-5b4a-4392-8817-665544332211"
    second = "11112222-3333-4444-8555-666677778888"
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup(
        [
            {"id": first, "iframe_initial_url": "https://custom.example/github"},
            {"id": second, "iframe_initial_url": "https://official.example/github"},
        ]
    )

    tool = resolve_tool("github-addon.pulls.list")

    with pytest.raises(ValidationError) as error:
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))

    assert first in str(error.value) and second in str(error.value)
    assert "--addon-uid" in str(error.value)


@respx.mock
async def test_attach_refuses_before_writing_to_an_ambiguous_addon(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    _mock_addon_lookup(
        [
            {
                "id": "9f8e7d6c-5b4a-4392-8817-665544332211",
                "iframe_initial_url": "https://a.example/github",
            },
            {
                "id": "11112222-3333-4444-8555-666677778888",
                "iframe_initial_url": "https://b.example/github",
            },
        ]
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.attach")

    with pytest.raises(ValidationError):
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "pull_json": _rest_pull()}))

    # The whole point: never PATCH GitHub data into some other addon's row.
    assert not patch_route.called


@respx.mock
async def test_ambiguity_across_board_spaces_is_refused(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    respx.get(CARD_URL).mock(
        return_value=Response(200, json={"id": 10, "space_id": 5, "board_id": 7})
    )
    respx.get(SPACE_ADDONS_URL).mock(return_value=Response(200, json=[]))
    respx.get(f"{API}/spaces").mock(
        return_value=Response(
            200,
            json=[
                {"id": 5, "boards": [{"id": 7}]},
                {"id": 8, "boards": [{"id": 7}]},
                {"id": 9, "boards": [{"id": 7}]},
            ],
        )
    )
    respx.get(f"{API}/spaces/8/addons").mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "9f8e7d6c-5b4a-4392-8817-665544332211",
                    "iframe_initial_url": "https://a.example/github",
                }
            ],
        )
    )
    respx.get(f"{API}/spaces/9/addons").mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "11112222-3333-4444-8555-666677778888",
                    "iframe_initial_url": "https://b.example/github",
                }
            ],
        )
    )

    tool = resolve_tool("github-addon.pulls.list")

    with pytest.raises(ValidationError) as error:
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))

    assert "board 7" in str(error.value)


@respx.mock
async def test_the_same_addon_in_several_board_spaces_is_one_candidate(monkeypatch):
    """A board shared across spaces normally reports the same addon in each."""

    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    registered_uid = "9f8e7d6c-5b4a-4392-8817-665544332211"
    respx.get(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json=[]))
    respx.get(CARD_URL).mock(
        return_value=Response(200, json={"id": 10, "space_id": 5, "board_id": 7})
    )
    respx.get(SPACE_ADDONS_URL).mock(return_value=Response(200, json=[]))
    respx.get(f"{API}/spaces").mock(
        return_value=Response(
            200, json=[{"id": 8, "boards": [{"id": 7}]}, {"id": 9, "boards": [{"id": 7}]}]
        )
    )
    for space in (8, 9):
        respx.get(f"{API}/spaces/{space}/addons").mock(
            return_value=Response(200, json=[_github_addon(registered_uid)])
        )
    respx.get(f"{API}/cards/10/addons-data/{registered_uid}").mock(
        return_value=Response(200, json=_rows({"attachedPulls": [_addon_pull()]}))
    )

    tool = resolve_tool("github-addon.pulls.list")
    result = await execute_tool(tool, merge_inputs(tool, {"card_id": 10}))

    assert [item["number"] for item in result] == [42]


@respx.mock
async def test_attach_refuses_a_malformed_addon_data_container(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "row",
                    "card_uid": "c",
                    "addon_uid": GITHUB_ADDON_UID,
                    "user_uid": None,
                    "data": "legacy",
                }
            ],
        )
    )
    patch_route = respx.patch(CARD_ADDON_DATA_URL).mock(return_value=Response(200, json={}))

    tool = resolve_tool("github-addon.pulls.attach")

    with pytest.raises(ValidationError) as error:
        await execute_tool(tool, merge_inputs(tool, {"card_id": 10, "pull_json": _rest_pull()}))

    assert "not an object" in str(error.value)
    assert not patch_route.called


@respx.mock
async def test_list_still_reads_through_a_malformed_container(monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "test-token")
    respx.get(CARD_ADDON_DATA_URL).mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "row",
                    "card_uid": "c",
                    "addon_uid": GITHUB_ADDON_UID,
                    "user_uid": None,
                    "data": 7,
                }
            ],
        )
    )

    tool = resolve_tool("github-addon.pulls.list")

    # The row exists, so the UID is confirmed; the container simply holds nothing
    # this command can read.
    assert await execute_tool(tool, merge_inputs(tool, {"card_id": 10})) == []
