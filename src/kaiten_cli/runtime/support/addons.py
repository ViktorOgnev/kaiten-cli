"""Addon data helpers: deterministic addon UIDs and GitHub-addon attachment stores.

Kaiten addons keep their per-card state in `card_addon_data` rows addressed by
`(card, addon_uid)` and read/written through `/cards/{card_id}/addons-data/{addon_uid}`.
The server shallow-merges the PATCHed `data` object over the stored one, so every
write here sends the FULL replacement value for the key it touches and leaves
sibling keys of other addon features untouched.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from kaiten_cli.errors import ValidationError

# Fixed namespace from kaiten-lib/src/shared/addons/generateAddonUid.js. On
# self-hosted Kaiten an addon UID is the UUID v5 of its normalized URL path, so
# the addons-data endpoint is addressable without registering or looking it up.
# The namespace and the normalization must stay byte-identical to the platform
# helper or derived UIDs stop matching.
KAITEN_ADDONS_NAMESPACE = uuid.UUID("d202834b-4740-4d9b-9ee0-cb1eb833124d")

GITHUB_ADDON_URL_PATH = "/github"

SHARED_SCOPE = "shared"
PRIVATE_SCOPE = "private"

# Addon SDK keys the GitHub addon stores its attachments under (shared scope).
# Must match `setData('card', 'shared', <key>, ...)` in kaiten-addons/addons/github.
ATTACHED_PULLS_KEY = "attachedPulls"
ATTACHED_BRANCHES_KEY = "attachedBranches"
ATTACHED_COMMITS_KEY = "attachedCommits"
ATTACHED_ISSUES_KEY = "attachedIssues"

# Placeholder values the addon itself writes when GitHub omits a field; kept
# identical so a CLI-written entry is indistinguishable from a UI-written one.
UNKNOWN_AUTHOR = "Неизвестный автор"
FALLBACK_AUTHOR_URL = "https://github.com"
FALLBACK_AVATAR_URL = "https://avatars.githubusercontent.com/u/583231?v=4"
NO_DATA = "no data"


def generate_addon_uid(url_path: str) -> str:
    """Deterministic addon UID for a mount path, mirroring `generateAddonUid`."""

    return str(uuid.uuid5(KAITEN_ADDONS_NAMESPACE, normalize_addon_url_path(url_path)))


def normalize_addon_url_path(url_path: str) -> str:
    """Strip surrounding slashes and lowercase, exactly as the platform helper does."""

    return url_path.strip("/").lower()


def resolve_github_addon_uid(payload: dict[str, Any]) -> str:
    """Explicit `--addon-uid` wins; otherwise derive it from the addon mount path."""

    explicit = payload.get("addon_uid")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    return generate_addon_uid(payload.get("addon_url_path") or GITHUB_ADDON_URL_PATH)


def shared_row(rows: Any) -> dict[str, Any] | None:
    """The shared row (`user_uid: null`) out of an addons-data row list."""

    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get("user_uid") is None:
            return row
    return None


def attached_items(rows: Any, key: str) -> list[dict[str, Any]]:
    """Items stored under `key` in the shared row; [] for a missing/malformed blob."""

    row = shared_row(rows)
    data = row.get("data") if isinstance(row, dict) else None
    value = data.get(key) if isinstance(data, dict) else None
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"Field {field} must be a JSON object with the GitHub REST payload.")
    return value


def _require_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"Field {field} must be an integer.")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"Field {field} must be a non-empty string.")
    return value


def _author(user: Any) -> dict[str, Any]:
    user = user if isinstance(user, dict) else {}
    return {
        "login": user.get("login") or UNKNOWN_AUTHOR,
        "htmlUrl": user.get("html_url") or FALLBACK_AUTHOR_URL,
        "avatar": user.get("avatar_url") or FALLBACK_AVATAR_URL,
    }


def _nested(source: Any, *path: str) -> Any:
    current = source
    for segment in path:
        if not isinstance(current, dict):
            return None
        current = current.get(segment)
    return current


def map_rest_pull(rest: Any, payload: dict[str, Any]) -> dict[str, Any]:
    """Map a GitHub REST pull object to the addon's `attachedPulls` entry shape."""

    pull = _require_object(rest, "pull_json")
    return {
        "id": _require_int(pull.get("id"), "pull_json.id"),
        "number": _require_int(pull.get("number"), "pull_json.number"),
        "htmlUrl": pull.get("html_url"),
        "state": pull.get("state"),
        "title": pull.get("title"),
        "body": pull.get("body"),
        "createdAt": pull.get("created_at"),
        "author": _author(pull.get("user")),
        "baseBranch": _nested(pull, "base", "ref") or NO_DATA,
        "headBranch": _nested(pull, "head", "ref") or NO_DATA,
        "repoName": _nested(pull, "base", "repo", "name") or NO_DATA,
        "repoOwner": _nested(pull, "base", "repo", "owner", "login") or NO_DATA,
    }


def map_rest_branch(rest: Any, payload: dict[str, Any]) -> dict[str, Any]:
    """Map a GitHub REST branch object to the addon's `attachedBranches` entry shape."""

    branch = _require_object(rest, "branch_json")
    owner = _require_text(payload.get("owner"), "owner")
    repo = _require_text(payload.get("repo"), "repo")
    name = _require_text(branch.get("name"), "branch_json.name")
    return {
        "branchName": name,
        "htmlUrl": f"https://github.com/{owner}/{repo}/tree/{name}",
        "commitUrl": _nested(branch, "commit", "url"),
        "repo": repo,
        "owner": owner,
        "pseudoId": f"{owner}/{repo}/{name}",
    }


def map_rest_commit(rest: Any, payload: dict[str, Any]) -> dict[str, Any]:
    """Map a GitHub REST commit object to the addon's `attachedCommits` entry shape."""

    commit = _require_object(rest, "commit_json")
    owner = _require_text(payload.get("owner"), "owner")
    repo = _require_text(payload.get("repo"), "repo")
    # The commit author can come from the linked GitHub account or, for an
    # unlinked email, only from the raw git metadata; the addon prefers the
    # account and falls back to the git name.
    account = commit.get("author") if isinstance(commit.get("author"), dict) else {}
    git_author = _nested(commit, "commit", "author") or {}
    return {
        "sha": _require_text(commit.get("sha"), "commit_json.sha"),
        "htmlUrl": commit.get("html_url"),
        "message": _nested(commit, "commit", "message"),
        "date": git_author.get("date") if isinstance(git_author, dict) else None,
        "author": {
            "login": account.get("login")
            or (git_author.get("name") if isinstance(git_author, dict) else None)
            or UNKNOWN_AUTHOR,
            "htmlUrl": account.get("html_url") or FALLBACK_AUTHOR_URL,
            "avatar": account.get("avatar_url") or FALLBACK_AVATAR_URL,
        },
        "repo": repo,
        "owner": owner,
    }


def map_rest_issue(rest: Any, payload: dict[str, Any]) -> dict[str, Any]:
    """Map a GitHub REST issue object to the addon's `attachedIssues` entry shape."""

    issue = _require_object(rest, "issue_json")
    if issue.get("pull_request") is not None:
        raise ValidationError(
            "Field issue_json describes a pull request; attach it with github-addon pulls attach."
        )
    owner = _require_text(payload.get("owner"), "owner")
    repo = _require_text(payload.get("repo"), "repo")
    return {
        "id": _require_int(issue.get("id"), "issue_json.id"),
        "number": _require_int(issue.get("number"), "issue_json.number"),
        "title": issue.get("title"),
        "state": issue.get("state"),
        "createdAt": issue.get("created_at"),
        "htmlUrl": issue.get("html_url"),
        # Issues store the author under `user`, pulls under `author`; both shapes
        # come straight from the addon's own DTO creators.
        "user": _author(issue.get("user")),
        "repoName": repo,
        "repoOwner": owner,
    }


# Attach dedup keys, one per store, matching what the addon UI compares on.
def _pull_identity(item: dict[str, Any]) -> Any:
    return item.get("id")


def _branch_identity(item: dict[str, Any]) -> Any:
    return item.get("pseudoId")


def _commit_identity(item: dict[str, Any]) -> Any:
    return item.get("sha")


def _issue_identity(item: dict[str, Any]) -> Any:
    return item.get("id")


def _repo_matches(
    item: dict[str, Any], payload: dict[str, Any], owner_key: str, repo_key: str
) -> bool:
    """Optional owner/repo narrowing shared by every detach selector."""

    for expected, field in ((payload.get("owner"), owner_key), (payload.get("repo"), repo_key)):
        if expected is not None and item.get(field) != expected:
            return False
    return True


def _require_any_selector(payload: dict[str, Any], fields: tuple[str, ...]) -> None:
    if not any(payload.get(field) is not None for field in fields):
        options = ", ".join(f"--{field.replace('_', '-')}" for field in fields)
        raise ValidationError(f"Provide at least one selector: {options}.")


def _pull_matches(item: dict[str, Any], payload: dict[str, Any]) -> bool:
    if payload.get("pull_id") is not None and item.get("id") != payload["pull_id"]:
        return False
    if payload.get("number") is not None and item.get("number") != payload["number"]:
        return False
    return _repo_matches(item, payload, "repoOwner", "repoName")


def _branch_matches(item: dict[str, Any], payload: dict[str, Any]) -> bool:
    if payload.get("pseudo_id") is not None and item.get("pseudoId") != payload["pseudo_id"]:
        return False
    if payload.get("branch_name") is not None and item.get("branchName") != payload["branch_name"]:
        return False
    return _repo_matches(item, payload, "owner", "repo")


def _commit_matches(item: dict[str, Any], payload: dict[str, Any]) -> bool:
    if item.get("sha") != payload["sha"]:
        return False
    return _repo_matches(item, payload, "owner", "repo")


def _issue_matches(item: dict[str, Any], payload: dict[str, Any]) -> bool:
    if payload.get("issue_id") is not None and item.get("id") != payload["issue_id"]:
        return False
    if payload.get("number") is not None and item.get("number") != payload["number"]:
        return False
    return _repo_matches(item, payload, "repoOwner", "repoName")


@dataclass(frozen=True, slots=True)
class GithubEntity:
    """Everything that differs between the four GitHub-addon attachment stores."""

    name: str
    key: str
    payload_field: str
    mapper: Callable[[Any, dict[str, Any]], dict[str, Any]]
    identity: Callable[[dict[str, Any]], Any]
    matches: Callable[[dict[str, Any], dict[str, Any]], bool]
    selectors: tuple[str, ...]


PULLS = GithubEntity(
    name="pulls",
    key=ATTACHED_PULLS_KEY,
    payload_field="pull_json",
    mapper=map_rest_pull,
    identity=_pull_identity,
    matches=_pull_matches,
    selectors=("pull_id", "number"),
)
BRANCHES = GithubEntity(
    name="branches",
    key=ATTACHED_BRANCHES_KEY,
    payload_field="branch_json",
    mapper=map_rest_branch,
    identity=_branch_identity,
    matches=_branch_matches,
    selectors=("pseudo_id", "branch_name"),
)
COMMITS = GithubEntity(
    name="commits",
    key=ATTACHED_COMMITS_KEY,
    payload_field="commit_json",
    mapper=map_rest_commit,
    identity=_commit_identity,
    matches=_commit_matches,
    selectors=("sha",),
)
ISSUES = GithubEntity(
    name="issues",
    key=ATTACHED_ISSUES_KEY,
    payload_field="issue_json",
    mapper=map_rest_issue,
    identity=_issue_identity,
    matches=_issue_matches,
    selectors=("issue_id", "number"),
)


def _addon_data_path(path: str, addon_uid: str) -> str:
    return f"{path.rstrip('/')}/{addon_uid}"


async def _read_attached(client, path: str, addon_uid: str, key: str, timeout: float) -> list:
    rows = await client.get(_addon_data_path(path, addon_uid), timeout=timeout)
    return attached_items(rows, key)


async def _write_attached(
    client, path: str, addon_uid: str, key: str, items: list, timeout: float
) -> Any:
    # The addon UI clears a key by writing null rather than an empty array; keep
    # the stored shape identical so the card widget renders the same way.
    value: Any = items if items else None
    return await client.patch(
        _addon_data_path(path, addon_uid),
        json={"type": SHARED_SCOPE, "data": {key: value}},
        timeout=timeout,
    )


def _envelope(payload: dict[str, Any], addon_uid: str, entity: GithubEntity) -> dict[str, Any]:
    return {
        "card_id": payload["card_id"],
        "addon_uid": addon_uid,
        "key": entity.key,
        "entity": entity.name,
    }


def _make_list_executor(entity: GithubEntity):
    async def execute(client, tool, payload, path, query, body, timeout, reporter):
        addon_uid = resolve_github_addon_uid(payload)
        if reporter:
            reporter(f"execution: read shared addon key {entity.key} for addon {addon_uid}")
        return await _read_attached(client, path, addon_uid, entity.key, timeout)

    execute.__name__ = f"execute_github_addon_{entity.name}_list"
    return execute


def _make_attach_executor(entity: GithubEntity):
    async def execute(client, tool, payload, path, query, body, timeout, reporter):
        addon_uid = resolve_github_addon_uid(payload)
        item = entity.mapper(payload.get(entity.payload_field), payload)
        if reporter:
            reporter(f"execution: read-modify-write of shared addon key {entity.key}")
        existing = await _read_attached(client, path, addon_uid, entity.key, timeout)
        result = _envelope(payload, addon_uid, entity)
        result["action"] = "attach"
        result["item"] = item

        identity = entity.identity(item)
        if any(entity.identity(current) == identity for current in existing):
            result["status"] = "already_attached"
            result["dry_run"] = bool(payload.get("dry_run", False))
            result["attached_count"] = len(existing)
            return result

        updated = [*existing, item]
        result["attached_count"] = len(updated)
        if payload.get("dry_run", False):
            result["status"] = "would_attach"
            result["dry_run"] = True
            return result

        await _write_attached(client, path, addon_uid, entity.key, updated, timeout)
        result["status"] = "attached"
        result["dry_run"] = False
        return result

    execute.__name__ = f"execute_github_addon_{entity.name}_attach"
    return execute


def _make_detach_executor(entity: GithubEntity):
    async def execute(client, tool, payload, path, query, body, timeout, reporter):
        _require_any_selector(payload, entity.selectors)
        addon_uid = resolve_github_addon_uid(payload)
        if reporter:
            reporter(f"execution: read-modify-write of shared addon key {entity.key}")
        existing = await _read_attached(client, path, addon_uid, entity.key, timeout)
        selected = [entity.matches(item, payload) for item in existing]
        removed = [item for item, hit in zip(existing, selected) if hit]
        kept = [item for item, hit in zip(existing, selected) if not hit]

        result = _envelope(payload, addon_uid, entity)
        result["action"] = "detach"
        result["removed"] = removed
        result["attached_count"] = len(kept)

        if not removed:
            # Nothing selected: skip the write entirely instead of rewriting the
            # same list, so a mistyped selector cannot touch the shared row.
            result["status"] = "not_found"
            result["attached_count"] = len(existing)
            result["dry_run"] = bool(payload.get("dry_run", False))
            return result

        if payload.get("dry_run", False):
            result["status"] = "would_detach"
            result["dry_run"] = True
            return result

        await _write_attached(client, path, addon_uid, entity.key, kept, timeout)
        result["status"] = "detached"
        result["dry_run"] = False
        return result

    execute.__name__ = f"execute_github_addon_{entity.name}_detach"
    return execute


execute_github_pulls_list = _make_list_executor(PULLS)
execute_github_pulls_attach = _make_attach_executor(PULLS)
execute_github_pulls_detach = _make_detach_executor(PULLS)

execute_github_branches_list = _make_list_executor(BRANCHES)
execute_github_branches_attach = _make_attach_executor(BRANCHES)
execute_github_branches_detach = _make_detach_executor(BRANCHES)

execute_github_commits_list = _make_list_executor(COMMITS)
execute_github_commits_attach = _make_attach_executor(COMMITS)
execute_github_commits_detach = _make_detach_executor(COMMITS)

execute_github_issues_list = _make_list_executor(ISSUES)
execute_github_issues_attach = _make_attach_executor(ISSUES)
execute_github_issues_detach = _make_detach_executor(ISSUES)


async def execute_addon_uid(client, tool, payload, path, query, body, timeout, reporter):
    """Local-only: derive an addon UID without calling Kaiten."""

    url_path = payload["url_path"]
    if reporter:
        reporter("execution: local UUID v5 derivation, no API call")
    return {
        "url_path": url_path,
        "normalized_url_path": normalize_addon_url_path(url_path),
        "addon_uid": generate_addon_uid(url_path),
    }
