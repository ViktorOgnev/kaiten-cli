"""Addon data helpers: deterministic addon UIDs and GitHub-addon attachment stores.

Kaiten addons keep their per-card state in `card_addon_data` rows addressed by
`(card, addon_uid)` and read/written through `/cards/{card_id}/addons-data/{addon_uid}`.
The server shallow-merges the PATCHed `data` object over the stored one, so every
write here sends the FULL replacement value for the key it touches and leaves
sibling keys of other addon features untouched.
"""

from __future__ import annotations

import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from kaiten_cli.errors import ApiError, TransportError, ValidationError
from kaiten_cli.runtime.support.pagination import fetch_all_offset_pages

# Fixed namespace from kaiten-lib/src/shared/addons/generateAddonUid.js. On
# self-hosted Kaiten an addon UID is the UUID v5 of its normalized URL path, so
# the addons-data endpoint is addressable without registering or looking it up.
# The namespace and the normalization must stay byte-identical to the platform
# helper or derived UIDs stop matching.
KAITEN_ADDONS_NAMESPACE = uuid.UUID("d202834b-4740-4d9b-9ee0-cb1eb833124d")

GITHUB_ADDON_URL_PATH = "/github"

SHARED_SCOPE = "shared"

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

# Mirrors uuidIdRule from kaiten/shared/idRules.js: version 4 or 5, RFC-4122
# variant. A value the route regex rejects can never address anything, and a
# stray string in the path would silently redirect the call to another endpoint.
_UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[45][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)


def validate_addon_uid_value(value: Any, field: str = "addon_uid") -> str:
    """Validate an addon UUID and normalize its case.

    Kaiten stores addon ids in a Postgres uuid column and returns them
    lowercase, while `checkAccessForUpdate` compares them to the path segment
    with `===`. An uppercase UUID therefore reads fine and then fails every
    write with 403, so the case is normalized here rather than passed through.
    """

    text = value.strip().lower() if isinstance(value, str) else ""
    if not _UUID_PATTERN.match(text):
        raise ValidationError(
            f"Field {field} must be an addon UUID such as "
            "0ce23a01-560f-51e0-9982-1e3445dc5990; take it from space-addons.list, "
            "company-addons.list or addons.uid."
        )
    return text


def validate_addon_uid_payload(tool, payload: dict[str, Any]) -> None:
    """Payload validator for the tools that take addon_uid as a path segment."""

    validate_addon_uid_value(payload.get("addon_uid"))


def generate_addon_uid(url_path: str) -> str:
    """Deterministic addon UID for a mount path, mirroring `generateAddonUid`."""

    return str(uuid.uuid5(KAITEN_ADDONS_NAMESPACE, normalize_addon_url_path(url_path)))


def normalize_addon_url_path(url_path: str) -> str:
    """Strip surrounding slashes and lowercase, exactly as the platform helper does."""

    return url_path.strip("/").lower()


def explicit_addon_uid(payload: dict[str, Any]) -> str | None:
    """The validated `--addon-uid` when the caller gave one."""

    explicit = payload.get("addon_uid")
    if isinstance(explicit, str) and explicit.strip():
        return validate_addon_uid_value(explicit)
    return None


def addon_url_path(payload: dict[str, Any]) -> str:
    return payload.get("addon_url_path") or GITHUB_ADDON_URL_PATH


def _iframe_url_path(url: Any) -> str | None:
    """Normalized path of an addon's iframe URL, the input of the UID derivation."""

    if not isinstance(url, str) or not url:
        return None
    try:
        return normalize_addon_url_path(urlparse(url).path)
    except ValueError:  # pragma: no cover - urlparse only raises on malformed IPv6
        return None


def _addon_uids_in(addons: Any, normalized_path: str) -> list[str]:
    """Every distinct addon UID mounted at `normalized_path` in one space listing.

    A path is not an identity: two addons can be served from different hosts under
    the same path, and on a cloud tenant their UIDs are unrelated random values.
    Returning all of them lets the caller refuse to guess.
    """

    found: list[str] = []
    if not isinstance(addons, list):
        return found
    for addon in addons:
        if not isinstance(addon, dict):
            continue
        if _iframe_url_path(addon.get("iframe_initial_url")) != normalized_path:
            continue
        uid = addon.get("id")
        if isinstance(uid, str) and _UUID_PATTERN.match(uid.lower()):
            lowered = uid.lower()
            if lowered not in found:
                found.append(lowered)
    return found


def _single_addon_uid(uids: list[str], url_path: str, where: str) -> str | None:
    """Exactly one candidate can be trusted; several are a refusal, not a choice."""

    if not uids:
        return None
    if len(uids) == 1:
        return uids[0]
    raise ValidationError(
        f"{where} has {len(uids)} addons mounted at {url_path} ({', '.join(uids)}), so the "
        "right one cannot be chosen automatically. Pass --addon-uid; writing to the wrong "
        "addon would put GitHub attachments into unrelated addon data."
    )


async def _board_space_ids(client, board_id: Any, timeout: float, reporter) -> list[int]:
    """Every space the board belongs to, in listing order.

    Kaiten decides addon availability for a card over all spaces of the card's
    board (`space_boards` in `getAvailableAddonsForCard`), and a board can sit in
    several spaces. There is no board->spaces endpoint, but the space listing
    embeds each space's boards. Archived spaces are included because the server
    does not filter them out either.

    Only consulted after the card's own space came up empty: the listing is large
    on a big tenant, and the card's own space answers almost every case.
    """

    try:
        spaces = await fetch_all_offset_pages(
            client,
            "/spaces",
            params={"archived": True},
            timeout=timeout,
            reporter=reporter,
        )
    except (ApiError, TransportError) as error:
        if reporter:
            reporter(f"addon lookup: /spaces unavailable ({error})")
        return []

    matching: list[int] = []
    for space in spaces:
        if not isinstance(space, dict):
            continue
        boards = space.get("boards")
        if not isinstance(boards, list):
            continue
        if any(isinstance(b, dict) and b.get("id") == board_id for b in boards):
            space_id = space.get("id")
            if isinstance(space_id, int):
                matching.append(space_id)
    return matching


async def _space_addon_uids(
    client, space_id: Any, normalized_path: str, timeout: float, reporter
) -> list[str]:
    """One space's candidates, or [] when that space cannot be read.

    A space the caller may not read must not end the search: the addon can be
    registered in another space of the same board, and that is exactly the case
    this lookup exists for.
    """

    try:
        addons = await client.get(f"/spaces/{space_id}/addons", timeout=timeout)
    except (ApiError, TransportError) as error:
        if reporter:
            reporter(f"addon lookup: /spaces/{space_id}/addons unavailable ({error})")
        return []
    return _addon_uids_in(addons, normalized_path)


async def registered_addon_uid(
    client, card_id: Any, url_path: str, timeout: float, reporter
) -> str | None:
    """The UID Kaiten registered for `url_path` on the card's board, or None.

    None means "not established": the lookup could not be performed, or no space
    of the card's board reports that addon. Neither confirms the derived UID, so
    None must never be read as "the addon exists and has nothing attached".

    Each read is fault-isolated: one unreadable space narrows the search instead
    of ending it.
    """

    normalized = normalize_addon_url_path(url_path)
    try:
        card = await client.get(f"/cards/{card_id}", timeout=timeout)
    except (ApiError, TransportError) as error:
        if reporter:
            reporter(f"addon lookup: /cards/{card_id} unavailable ({error})")
        return None
    if not isinstance(card, dict):
        return None

    space_id, board_id = card.get("space_id"), card.get("board_id")
    if space_id is not None:
        own = await _space_addon_uids(client, space_id, normalized, timeout, reporter)
        uid = _single_addon_uid(own, url_path, f"Space {space_id}")
        if uid is not None:
            return uid

    if board_id is None:
        return None
    # Only now is the space listing worth its size: the board may be shared into
    # spaces other than the card's own. Candidates are pooled across those spaces
    # before choosing, so two different addons on the same path are a refusal
    # rather than a race between spaces. The same UID seen in several spaces is
    # one candidate, which is the normal shape of a shared board.
    pooled: list[str] = []
    for candidate in await _board_space_ids(client, board_id, timeout, reporter):
        if candidate == space_id:
            continue
        for uid in await _space_addon_uids(client, candidate, normalized, timeout, reporter):
            if uid not in pooled:
                pooled.append(uid)
    resolved = _single_addon_uid(pooled, url_path, f"The spaces of board {board_id}")
    if resolved is not None and reporter:
        reporter("addon lookup: found in another space of the board, not the card's own space")
    return resolved


def shared_row(rows: Any) -> dict[str, Any] | None:
    """The shared row (`user_uid: null`) out of an addons-data row list."""

    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get("user_uid") is None:
            return row
    return None


UNSET = object()


def shared_data(rows: Any) -> Any:
    """The whole `data` container of the shared row, or UNSET when there is no row.

    Kept separate from `stored_value` because "there is no container" and "the
    container is something we do not recognise" are different facts: only the
    first one is a safe empty start for a write.
    """

    row = shared_row(rows)
    if not isinstance(row, dict):
        return UNSET
    return row.get("data", UNSET)


def stored_value(rows: Any, key: str) -> Any:
    """Raw value stored under `key` in the shared row, or UNSET when absent.

    Callers that are about to write must look at the raw value: a read-modify-write
    that silently normalizes it would persist the normalization and drop whatever
    it did not understand.
    """

    data = shared_data(rows)
    if not isinstance(data, dict) or key not in data:
        return UNSET
    return data[key]


def attached_items(rows: Any, key: str) -> list[dict[str, Any]]:
    """Items stored under `key` in the shared row; [] for a missing/malformed blob.

    Tolerant on purpose - this is the read path. The write path uses
    `mutable_attached_items`, which refuses to normalize anything.
    """

    value = stored_value(rows, key)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def mutable_attached_items(rows: Any, key: str) -> list[dict[str, Any]]:
    """The stored list, or a hard failure when its shape is not what we can rewrite.

    A write replaces the whole key, so anything the tolerant reader would have
    dropped - a null, a legacy string marker, a value that is not a list at all -
    would be destroyed by the rewrite. Refuse instead, and let the caller decide.
    """

    data = shared_data(rows)
    if data is not UNSET and data is not None and not isinstance(data, dict):
        # The row exists but its container is not an object. A write would replace
        # it with one, so whatever is stored there would be gone.
        raise ValidationError(
            f"Addon data for this card holds {type(data).__name__}, not an object, so this "
            "command cannot rewrite it without losing data. Inspect it with card-addon-data "
            "get and fix it with card-addon-data set."
        )

    value = stored_value(rows, key)
    if value is UNSET or value is None:
        # No key yet, or the addon cleared it: both mean "start from empty", which
        # is exactly what the addon UI writes when the last entry is removed.
        return []
    if not isinstance(value, list):
        raise ValidationError(
            f"Addon key {key} holds {type(value).__name__}, not a list, so this command cannot "
            "rewrite it without losing data. Inspect it with card-addon-data get and fix it "
            "with card-addon-data set."
        )
    unexpected = [index for index, item in enumerate(value) if not isinstance(item, dict)]
    if unexpected:
        positions = ", ".join(str(index) for index in unexpected[:5])
        raise ValidationError(
            f"Addon key {key} has non-object entries at position(s) {positions}; rewriting the "
            "list would drop them. Inspect it with card-addon-data get and fix it with "
            "card-addon-data set."
        )
    return list(value)


def _require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"Field {field} must be a JSON object with the GitHub REST payload.")
    return value


def _require_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"Field {field} must be an integer.")
    return value


def _require_text(value: Any, field: str) -> str:
    text = value.strip() if isinstance(value, str) else ""
    if not text:
        raise ValidationError(f"Field {field} must be a non-empty string.")
    return text


def _optional_text(value: Any) -> str | None:
    """A blank option (an unset shell variable) is absence, not a value."""

    text = value.strip() if isinstance(value, str) else ""
    return text or None


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
    # The card widget re-reads every attached PR by (repoOwner, repoName, number),
    # so the repository is identity, not decoration: a placeholder here would
    # store an entry that can never resolve on GitHub again. A trimmed payload
    # (gh pr view --json ...) may omit base.repo, hence the explicit fallback.
    owner = _nested(pull, "base", "repo", "owner", "login") or _optional_text(payload.get("owner"))
    repo = _nested(pull, "base", "repo", "name") or _optional_text(payload.get("repo"))
    if not owner or not repo:
        raise ValidationError(
            "Field pull_json has no base.repo.owner.login / base.repo.name; pass the full "
            "GitHub REST pull object (gh api repos/OWNER/REPO/pulls/NUMBER) or give "
            "--owner and --repo explicitly."
        )
    return {
        "id": _require_int(pull.get("id"), "pull_json.id"),
        "number": _require_int(pull.get("number"), "pull_json.number"),
        # The addon always stores a real link: its own DTO reads html_url from a
        # full REST response, and the widget falls back to the stored link when
        # GitHub is unreachable.
        "htmlUrl": _require_text(pull.get("html_url"), "pull_json.html_url"),
        "state": pull.get("state"),
        "title": pull.get("title"),
        "body": pull.get("body"),
        "createdAt": pull.get("created_at"),
        "author": _author(pull.get("user")),
        "baseBranch": _nested(pull, "base", "ref") or NO_DATA,
        "headBranch": _nested(pull, "head", "ref") or NO_DATA,
        "repoName": repo,
        "repoOwner": owner,
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
    # The addon's own DTO reads commit.commit.message and commit.commit.author.date
    # without guards, so an entry without them is one the addon could not produce.
    return {
        "sha": _require_text(commit.get("sha"), "commit_json.sha"),
        "htmlUrl": _require_text(commit.get("html_url"), "commit_json.html_url"),
        "message": _require_text(
            _nested(commit, "commit", "message"), "commit_json.commit.message"
        ),
        "date": _require_text(
            git_author.get("date") if isinstance(git_author, dict) else None,
            "commit_json.commit.author.date",
        ),
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
        "htmlUrl": _require_text(issue.get("html_url"), "issue_json.html_url"),
        # Issues store the author under `user`, pulls under `author`; both shapes
        # come straight from the addon's own DTO creators.
        "user": _author(issue.get("user")),
        "repoName": repo,
        "repoOwner": owner,
    }


def _fold(value: Any) -> Any:
    """Case-fold a GitHub identifier. Owners, repositories and shas are
    case-insensitive on GitHub; branch names are not and stay untouched."""

    return value.casefold() if isinstance(value, str) else value


# Attach dedup keys, one per store, matching what the addon UI compares on.
def _pull_identity(item: dict[str, Any]) -> Any:
    return item.get("id")


def _branch_identity(item: dict[str, Any]) -> Any:
    owner, repo = item.get("owner"), item.get("repo")
    if isinstance(owner, str) and isinstance(repo, str):
        return (_fold(owner), _fold(repo), item.get("branchName"))
    return item.get("pseudoId")


def _commit_identity(item: dict[str, Any]) -> Any:
    return _fold(item.get("sha"))


def _issue_identity(item: dict[str, Any]) -> Any:
    return item.get("id")


def _repo_matches(
    item: dict[str, Any], payload: dict[str, Any], owner_key: str, repo_key: str
) -> bool:
    """Optional owner/repo narrowing shared by every detach selector."""

    for expected, field in ((payload.get("owner"), owner_key), (payload.get("repo"), repo_key)):
        if expected is not None and _fold(item.get(field)) != _fold(expected):
            return False
    return True


def _option(field: str) -> str:
    return f"--{field.replace('_', '-')}"


def _require_any_selector(payload: dict[str, Any], fields: tuple[str, ...]) -> None:
    if not any(payload.get(field) is not None for field in fields):
        options = ", ".join(_option(field) for field in fields)
        raise ValidationError(f"Provide at least one selector: {options}.")
    # An empty string reaches here from an unset shell variable. Treated as a
    # filter it would silently match nothing, so reject it instead.
    for field in (*fields, "owner", "repo"):
        value = payload.get(field)
        if isinstance(value, str) and not value.strip():
            raise ValidationError(f"Field {_option(field)} must not be empty.")


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
    if payload.get("sha") is not None and _fold(item.get("sha")) != _fold(payload["sha"]):
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
    # The addon UI prepends new branches and appends everything else; the stored
    # order is what the card widget renders, so it is mirrored here.
    prepend: bool = False


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
    prepend=True,
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


def _describe_item(entity: GithubEntity, item: dict[str, Any]) -> str:
    """Short human-readable identity of one attachment, for error messages."""

    if entity is BRANCHES:
        return str(item.get("pseudoId") or item.get("branchName"))
    if entity is COMMITS:
        return f"{item.get('owner')}/{item.get('repo')}@{item.get('sha')}"
    owner = item.get("repoOwner")
    repo = item.get("repoName")
    return f"{owner}/{repo}#{item.get('number')}"


def _addon_data_path(path: str, addon_uid: str) -> str:
    return f"{path.rstrip('/')}/{addon_uid}"


@dataclass(frozen=True, slots=True)
class AttachedState:
    """What one addons-data read found, and under which UID."""

    addon_uid: str
    row_found: bool
    # True only when the UID is known to be the right one: it was given
    # explicitly, or an addon registration was actually found for the card's
    # board. "The space I could see has no such addon" is NOT a confirmation -
    # the board may live in a space this user cannot read.
    uid_confirmed: bool
    items: list[dict[str, Any]]


async def _read_attached(
    client,
    payload: dict[str, Any],
    path: str,
    entity: GithubEntity,
    timeout: float,
    reporter,
    *,
    for_write: bool = False,
) -> AttachedState:
    """Read the shared attachments, re-resolving the addon UID if a guess missed.

    Without an explicit `--addon-uid` the UID is derived from the mount path,
    which only matches on-premises installations. An empty read is therefore
    ambiguous: no attachments, or the wrong addon entirely. Ask which addon the
    card's board actually has before believing the empty answer.

    `for_write` switches the item parsing from tolerant to strict, because the
    caller is about to rewrite the whole key.
    """

    explicit = explicit_addon_uid(payload)
    url_path = addon_url_path(payload)
    addon_uid = explicit or generate_addon_uid(url_path)
    rows = await client.get(_addon_data_path(path, addon_uid), timeout=timeout)
    confirmed = explicit is not None

    if shared_row(rows) is None and explicit is None:
        registered = await registered_addon_uid(
            client, payload["card_id"], url_path, timeout, reporter
        )
        confirmed = registered is not None
        if registered is not None and registered != addon_uid:
            if reporter:
                reporter(
                    f"addon uid: derived {addon_uid} has no data, using registered {registered}"
                )
            addon_uid = registered
            rows = await client.get(_addon_data_path(path, addon_uid), timeout=timeout)

    read_items = mutable_attached_items if for_write else attached_items
    return AttachedState(
        addon_uid=addon_uid,
        row_found=shared_row(rows) is not None,
        uid_confirmed=confirmed,
        items=read_items(rows, entity.key),
    )


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


def _envelope(
    payload: dict[str, Any], state: AttachedState, entity: GithubEntity
) -> dict[str, Any]:
    return {
        "card_id": payload["card_id"],
        "addon_uid": state.addon_uid,
        # False means the card has no data row for this addon at all, which also
        # covers "the addon is not installed here" - useful when an empty list
        # would otherwise read as "nothing is attached".
        "addon_data_row_found": state.row_found,
        "addon_uid_confirmed": state.uid_confirmed,
        "key": entity.key,
        "entity": entity.name,
    }


def _make_list_executor(entity: GithubEntity):
    async def execute(client, tool, payload, path, query, body, timeout, reporter):
        if reporter:
            reporter(f"execution: read shared addon key {entity.key}")
        state = await _read_attached(client, payload, path, entity, timeout, reporter)
        if not state.row_found and not state.uid_confirmed:
            # An empty list here would be indistinguishable from "we read the
            # wrong addon", and a read cannot be verified by the server the way
            # a write is. Refuse to answer instead of answering "nothing".
            raise ValidationError(
                f"Cannot confirm that {state.addon_uid} is this card's GitHub addon: the UUID "
                "was derived from --addon-url-path, it holds no data, and no space of the "
                "card's board reported that addon - it may be installed in a space you cannot "
                "read, or not installed at all. Pass --addon-uid (see space-addons.list or "
                "company-addons.list) and retry."
            )
        if reporter and not state.row_found:
            reporter(
                f"addon data: no shared row under {state.addon_uid}; "
                "the card has no attachments or the addon is not installed here"
            )
        return state.items

    execute.__name__ = f"execute_github_addon_{entity.name}_list"
    return execute


def _make_attach_executor(entity: GithubEntity):
    async def execute(client, tool, payload, path, query, body, timeout, reporter):
        item = entity.mapper(payload.get(entity.payload_field), payload)
        if reporter:
            reporter(f"execution: read-modify-write of shared addon key {entity.key}")
        state = await _read_attached(
            client, payload, path, entity, timeout, reporter, for_write=True
        )
        addon_uid, existing = state.addon_uid, state.items
        result = _envelope(payload, state, entity)
        result["action"] = "attach"
        result["item"] = item

        identity = entity.identity(item)
        if any(entity.identity(current) == identity for current in existing):
            result["status"] = "already_attached"
            result["dry_run"] = bool(payload.get("dry_run", False))
            result["attached_count"] = len(existing)
            return result

        updated = [item, *existing] if entity.prepend else [*existing, item]
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
        if reporter:
            reporter(f"execution: read-modify-write of shared addon key {entity.key}")
        state = await _read_attached(
            client, payload, path, entity, timeout, reporter, for_write=True
        )
        addon_uid, existing = state.addon_uid, state.items
        selected = [entity.matches(item, payload) for item in existing]
        removed = [item for item, hit in zip(existing, selected) if hit]
        kept = [item for item, hit in zip(existing, selected) if not hit]

        result = _envelope(payload, state, entity)
        result["action"] = "detach"
        result["removed"] = removed

        if not removed:
            # Nothing selected: skip the write entirely instead of rewriting the
            # same list, so a mistyped selector cannot touch the shared row.
            result["status"] = "not_found"
            result["attached_count"] = len(existing)
            result["dry_run"] = bool(payload.get("dry_run", False))
            return result

        # A number or a branch name is only unique inside one repository, so a
        # selector that hits several attachments is ambiguous rather than a
        # request to remove them all. Removing the extra ones has to be asked for.
        if len(removed) > 1 and not payload.get("all", False):
            raise ValidationError(
                f"Selector matches {len(removed)} attachments: "
                + ", ".join(_describe_item(entity, item) for item in removed)
                + ". Narrow it with --owner and --repo, or pass --all to remove every match."
            )

        result["attached_count"] = len(kept)

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
    if not normalize_addon_url_path(url_path):
        # companyAddonsController derives a UID only for a non-empty path and
        # leaves a random one otherwise, so a UUID for "/" would be a value the
        # platform never assigns.
        raise ValidationError(
            "Field url_path must contain a path segment: Kaiten does not derive a UUID for an "
            "addon mounted at the root, it keeps the random one. Read the real value from "
            "space-addons.list or company-addons.list."
        )
    if reporter:
        reporter("execution: local UUID v5 derivation, no API call")
    return {
        "url_path": url_path,
        "normalized_url_path": normalize_addon_url_path(url_path),
        "addon_uid": generate_addon_uid(url_path),
    }
