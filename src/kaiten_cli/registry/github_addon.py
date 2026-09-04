"""GitHub addon tool specs: the PR/branch/commit/issue attachments shown on a card.

The Kaiten GitHub addon does not store attachments as external links. It keeps
them in the card's shared addon data under `attachedPulls`, `attachedBranches`,
`attachedCommits` and `attachedIssues`, and the card widget re-reads each entry
from GitHub by (owner, repo, number/name/sha). These commands read and write that
store in the addon's own payload shape: the same keys, the same identity fields and
the same placeholders the addon writes. Optional presentation fields (title, state,
author) are only as complete as the payload handed to the CLI, so pass the full REST
object rather than a trimmed one.
"""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import PLAIN_ENTITY_POLICY, make_tool, shaping_properties
from kaiten_cli.runtime.support.addons import (
    execute_github_branches_attach,
    execute_github_branches_detach,
    execute_github_branches_list,
    execute_github_commits_attach,
    execute_github_commits_detach,
    execute_github_commits_list,
    execute_github_issues_attach,
    execute_github_issues_detach,
    execute_github_issues_list,
    execute_github_pulls_attach,
    execute_github_pulls_detach,
    execute_github_pulls_list,
)

CARD_DATA_PATH = "/cards/{card_id}/addons-data"

ADDON_UID_PATH_NOTE = (
    "The addon UUID is appended to the path at runtime, so the path template above stops at "
    "addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path "
    "(default /github)."
)
UID_FALLBACK_NOTE = (
    "Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten "
    "stores a random one. When a derived UUID finds no data row the command reads the card, "
    "whose response lists the addons available to it across every space of its board - the "
    "same set the server checks when authorizing a write - and retries with the registered "
    "UUID. A card that reports no such addon is a real answer: it can have no attachments."
)
UID_FALLBACK_COST_NOTE = (
    "The lookup costs one extra read per card - the card itself - and falls back to the space "
    "listing only for responses that do not carry the addon data. Nothing is amortized across "
    "cards, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid."
)
STRICT_WRITE_NOTE = (
    "A write replaces the whole key, so the command refuses to proceed when the stored addon "
    "data is not an object or the key is not a plain list of objects: rewriting it would "
    "silently drop what the CLI does not understand. Inspect it with card-addon-data get."
)
AMBIGUOUS_ADDON_NOTE = (
    "A mount path is not an identity - two addons can be served from different hosts under the "
    "same path. When more than one addon of the card's board matches, the command refuses to "
    "choose and asks for --addon-uid, because writing to the wrong one would put GitHub "
    "attachments into unrelated addon data."
)
RACE_NOTE = (
    "The shared row has no version or ETag: a simultaneous change from the addon UI or another "
    "CLI run can be lost. Re-read before retrying."
)
REST_JSON_NOTE = (
    "Pass the raw GitHub REST object from gh api repos/OWNER/REPO/..., not gh pr view --json: "
    "the latter returns GraphQL fields (a string node id, camelCase names) that this mapping "
    "rejects. The CLI never calls GitHub itself, so the payload is the only source of the "
    "title, state and author the widget shows when it cannot reach GitHub."
)
REPO_IDENTITY_NOTE = (
    "The card widget re-reads every attachment from GitHub by owner, repository and "
    "number/name/sha, so the repository is part of the stored identity: a wrong or missing "
    "value leaves an entry that can never resolve again."
)
AMBIGUOUS_SELECTOR_NOTE = (
    "A selector that matches several attachments is rejected as ambiguous; narrow it with "
    "--owner and --repo, or pass --all when removing every match is what you want."
)
SHARED_WRITE_NOTE = (
    "The write needs card.update in the card's space and the GitHub addon installed there; "
    "otherwise Kaiten rejects the shared row update."
)
DEDUP_NOTE_BY_ID = "Already attached entries are detected by GitHub numeric id and left untouched."
DEDUP_NOTE_BY_PSEUDO_ID = (
    "Already attached entries are detected by owner/repo/branch, matching the addon UI."
)
DEDUP_NOTE_BY_SHA = "Already attached entries are detected by commit sha."
EMPTY_KEY_NOTE = (
    "Detaching the last entry stores null for the key rather than an empty array, which is what "
    "the addon UI writes and what hides the widget section on the card."
)
DRY_RUN_NOTE = (
    "--dry-run reads the current attachments and reports the outcome without writing; it is "
    "still classified as a mutation, so it is blocked by --read-only."
)

# Attachments are GitHub-shaped JSON, so the generic --compact rules have nothing
# to strip here; only field selection is offered. Unlike card-addon-data.get this
# read keeps the common transforms: it is not the input of a write, because attach
# takes a GitHub REST object and re-reads the stored list itself.
LIST_POLICY = ResponsePolicy(fields_supported=True, result_kind="list")


def _card_addon_properties() -> dict[str, dict]:
    return {
        "card_id": {"type": "integer", "description": "Card ID"},
        "addon_uid": {
            "type": "string",
            "description": "GitHub addon UUID; derived from the mount path when omitted.",
        },
        "addon_url_path": {
            "type": "string",
            "description": "GitHub addon mount path used to derive the UUID (default /github).",
        },
    }


def _fields_property() -> dict[str, dict]:
    return {"fields": shaping_properties()["fields"]}


# The same two options play three different roles: stored identity (branches,
# commits, issues), fallback identity (a pull payload without base.repo) and an
# optional narrowing filter (detach).
_REPO_ROLE_SUFFIX = {
    "identity": "",
    "fallback": " Required when the payload carries no repository.",
    "filter": " Optional filter.",
}


def _repo_properties(role: str) -> dict[str, dict]:
    suffix = _REPO_ROLE_SUFFIX[role]
    return {
        "owner": {"type": "string", "description": f"GitHub repository owner login.{suffix}"},
        "repo": {"type": "string", "description": f"GitHub repository name.{suffix}"},
    }


def _dry_run_property() -> dict[str, dict]:
    return {
        "dry_run": {
            "type": "boolean",
            "description": "Report the resulting change without writing it.",
        },
    }


def _all_property() -> dict[str, dict]:
    return {
        "all": {
            "type": "boolean",
            "description": "Allow removing every attachment the selectors match, not just one.",
        },
    }


def _list_operation() -> OperationSpec:
    return OperationSpec(method="GET", path_template=CARD_DATA_PATH, path_fields=("card_id",))


def _write_operation() -> OperationSpec:
    return OperationSpec(method="PATCH", path_template=CARD_DATA_PATH, path_fields=("card_id",))


def _behavior(executor) -> RuntimeBehavior:
    return RuntimeBehavior(execution_mode="custom", custom_executor=executor)


TOOLS = (
    make_tool(
        canonical_name="github-addon.pulls.list",
        mcp_alias="kaiten_list_card_github_pulls",
        description="List pull requests attached to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {**_card_addon_properties(), **_fields_property()},
            "required": ["card_id"],
        },
        operation=_list_operation(),
        response_policy=LIST_POLICY,
        runtime_behavior=_behavior(execute_github_pulls_list),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon pulls list --card-id 10 --fields number,htmlUrl,state",
                description="Read the PR links attached to a card.",
            ),
        ),
        usage_notes=(
            ADDON_UID_PATH_NOTE,
            UID_FALLBACK_NOTE,
            AMBIGUOUS_ADDON_NOTE,
            UID_FALLBACK_COST_NOTE,
            (
                "When the UUID was derived, holds no data and no readable space of the card's "
                "board reports that addon, the command fails instead of returning an empty list "
                'that could mean either "nothing attached" or "wrong addon". If the addon is '
                "simply not installed for this board, that failure is expected and the card "
                "genuinely has no attachments."
            ),
            (
                "Returns the stored attachedPulls entries; an uninstalled addon or a card without "
                "attachments both yield an empty list."
            ),
            (
                "Card PR references can also live in external links; check external-links.list too "
                "when you need every PR referenced by a card."
            ),
        ),
    ),
    make_tool(
        canonical_name="github-addon.pulls.attach",
        mcp_alias="kaiten_attach_github_pull",
        description="Attach a pull request to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {
                **_card_addon_properties(),
                "pull_json": {
                    "type": "object",
                    "description": "Raw GitHub REST pull request object.",
                },
                **_repo_properties("fallback"),
                **_dry_run_property(),
            },
            "required": ["card_id", "pull_json"],
        },
        operation=_write_operation(),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=_behavior(execute_github_pulls_attach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon pulls attach --card-id 10 --pull-json @pull.json",
                description="Attach a PR fetched with gh api repos/OWNER/REPO/pulls/NUMBER.",
            ),
            ExampleSpec(
                command="kaiten --json github-addon pulls attach --card-id 10 --pull-json @pull.json --dry-run",
                description="Preview the attachment without writing it.",
            ),
        ),
        usage_notes=(
            ADDON_UID_PATH_NOTE,
            UID_FALLBACK_NOTE,
            AMBIGUOUS_ADDON_NOTE,
            UID_FALLBACK_COST_NOTE,
            REST_JSON_NOTE,
            REPO_IDENTITY_NOTE,
            (
                "The repository is read from base.repo. A REST payload trimmed with --jq can lose "
                "it; then pass --owner and --repo. Output of gh pr view --json is a different "
                "schema entirely and is not accepted with or without them."
            ),
            DEDUP_NOTE_BY_ID,
            SHARED_WRITE_NOTE,
            STRICT_WRITE_NOTE,
            RACE_NOTE,
            DRY_RUN_NOTE,
        ),
    ),
    make_tool(
        canonical_name="github-addon.pulls.detach",
        mcp_alias="kaiten_detach_github_pull",
        description="Detach a pull request from a card in the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {
                **_card_addon_properties(),
                "pull_id": {"type": "integer", "description": "GitHub numeric pull request id."},
                "number": {"type": "integer", "description": "Pull request number."},
                **_repo_properties("filter"),
                **_all_property(),
                **_dry_run_property(),
            },
            "required": ["card_id"],
        },
        operation=_write_operation(),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=_behavior(execute_github_pulls_detach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon pulls detach --card-id 10 --number 42 --owner acme --repo web",
                description="Detach one PR from a card.",
            ),
        ),
        usage_notes=(
            ADDON_UID_PATH_NOTE,
            UID_FALLBACK_NOTE,
            AMBIGUOUS_ADDON_NOTE,
            UID_FALLBACK_COST_NOTE,
            (
                "Provide --pull-id or --number; --owner and --repo narrow the match when the same "
                "number exists in several repositories."
            ),
            AMBIGUOUS_SELECTOR_NOTE,
            "A selector that matches nothing leaves the stored data untouched.",
            EMPTY_KEY_NOTE,
            STRICT_WRITE_NOTE,
            RACE_NOTE,
            DRY_RUN_NOTE,
        ),
    ),
    make_tool(
        canonical_name="github-addon.branches.list",
        mcp_alias="kaiten_list_card_github_branches",
        description="List branches attached to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {**_card_addon_properties(), **_fields_property()},
            "required": ["card_id"],
        },
        operation=_list_operation(),
        response_policy=LIST_POLICY,
        runtime_behavior=_behavior(execute_github_branches_list),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon branches list --card-id 10 --fields branchName,htmlUrl",
                description="Read the branches attached to a card.",
            ),
        ),
        usage_notes=(ADDON_UID_PATH_NOTE, UID_FALLBACK_NOTE, UID_FALLBACK_COST_NOTE),
    ),
    make_tool(
        canonical_name="github-addon.branches.attach",
        mcp_alias="kaiten_attach_github_branch",
        description="Attach a branch to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {
                **_card_addon_properties(),
                "branch_json": {"type": "object", "description": "Raw GitHub REST branch object."},
                **_repo_properties("identity"),
                **_dry_run_property(),
            },
            "required": ["card_id", "branch_json", "owner", "repo"],
        },
        operation=_write_operation(),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=_behavior(execute_github_branches_attach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon branches attach --card-id 10 --owner acme --repo web --branch-json @branch.json",
                description="Attach a branch fetched with gh api repos/OWNER/REPO/branches/NAME.",
            ),
        ),
        usage_notes=(
            ADDON_UID_PATH_NOTE,
            UID_FALLBACK_NOTE,
            AMBIGUOUS_ADDON_NOTE,
            UID_FALLBACK_COST_NOTE,
            REST_JSON_NOTE,
            (
                "A REST branch object carries no repository, so --owner and --repo are required and "
                "form the stored branch identity."
            ),
            REPO_IDENTITY_NOTE,
            DEDUP_NOTE_BY_PSEUDO_ID,
            SHARED_WRITE_NOTE,
            STRICT_WRITE_NOTE,
            RACE_NOTE,
            DRY_RUN_NOTE,
        ),
    ),
    make_tool(
        canonical_name="github-addon.branches.detach",
        mcp_alias="kaiten_detach_github_branch",
        description="Detach a branch from a card in the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {
                **_card_addon_properties(),
                "branch_name": {"type": "string", "description": "Branch name."},
                "pseudo_id": {
                    "type": "string",
                    "description": "Stored branch identity in owner/repo/branch form.",
                },
                **_repo_properties("filter"),
                **_all_property(),
                **_dry_run_property(),
            },
            "required": ["card_id"],
        },
        operation=_write_operation(),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=_behavior(execute_github_branches_detach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon branches detach --card-id 10 --branch-name feature/login --owner acme --repo web",
                description="Detach one branch from a card.",
            ),
        ),
        usage_notes=(
            ADDON_UID_PATH_NOTE,
            UID_FALLBACK_NOTE,
            AMBIGUOUS_ADDON_NOTE,
            UID_FALLBACK_COST_NOTE,
            (
                "Provide --pseudo-id or --branch-name; --owner and --repo narrow the match when the "
                "same branch name exists in several repositories."
            ),
            AMBIGUOUS_SELECTOR_NOTE,
            EMPTY_KEY_NOTE,
            STRICT_WRITE_NOTE,
            RACE_NOTE,
            DRY_RUN_NOTE,
        ),
    ),
    make_tool(
        canonical_name="github-addon.commits.list",
        mcp_alias="kaiten_list_card_github_commits",
        description="List commits attached to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {**_card_addon_properties(), **_fields_property()},
            "required": ["card_id"],
        },
        operation=_list_operation(),
        response_policy=LIST_POLICY,
        runtime_behavior=_behavior(execute_github_commits_list),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon commits list --card-id 10 --fields sha,htmlUrl,message",
                description="Read the commits attached to a card.",
            ),
        ),
        usage_notes=(ADDON_UID_PATH_NOTE, UID_FALLBACK_NOTE, UID_FALLBACK_COST_NOTE),
    ),
    make_tool(
        canonical_name="github-addon.commits.attach",
        mcp_alias="kaiten_attach_github_commit",
        description="Attach a commit to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {
                **_card_addon_properties(),
                "commit_json": {"type": "object", "description": "Raw GitHub REST commit object."},
                **_repo_properties("identity"),
                **_dry_run_property(),
            },
            "required": ["card_id", "commit_json", "owner", "repo"],
        },
        operation=_write_operation(),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=_behavior(execute_github_commits_attach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon commits attach --card-id 10 --owner acme --repo web --commit-json @commit.json",
                description="Attach a commit fetched with gh api repos/OWNER/REPO/commits/SHA.",
            ),
        ),
        usage_notes=(
            ADDON_UID_PATH_NOTE,
            UID_FALLBACK_NOTE,
            AMBIGUOUS_ADDON_NOTE,
            UID_FALLBACK_COST_NOTE,
            REST_JSON_NOTE,
            (
                "The stored author prefers the linked GitHub account and falls back to the git "
                "author name, exactly as the addon does."
            ),
            DEDUP_NOTE_BY_SHA,
            SHARED_WRITE_NOTE,
            STRICT_WRITE_NOTE,
            RACE_NOTE,
            DRY_RUN_NOTE,
        ),
    ),
    make_tool(
        canonical_name="github-addon.commits.detach",
        mcp_alias="kaiten_detach_github_commit",
        description="Detach a commit from a card in the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {
                **_card_addon_properties(),
                "sha": {"type": "string", "description": "Full commit sha as stored."},
                **_repo_properties("filter"),
                **_all_property(),
                **_dry_run_property(),
            },
            "required": ["card_id"],
        },
        operation=_write_operation(),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=_behavior(execute_github_commits_detach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon commits detach --card-id 10 --sha 3f1a2bc4d5e6f708192a3b4c5d6e7f8091a2b3c4",
                description="Detach one commit from a card.",
            ),
        ),
        usage_notes=(
            ADDON_UID_PATH_NOTE,
            UID_FALLBACK_NOTE,
            AMBIGUOUS_ADDON_NOTE,
            UID_FALLBACK_COST_NOTE,
            "--sha is required and matched in full; short shas do not match stored entries.",
            AMBIGUOUS_SELECTOR_NOTE,
            EMPTY_KEY_NOTE,
            STRICT_WRITE_NOTE,
            RACE_NOTE,
            DRY_RUN_NOTE,
        ),
    ),
    make_tool(
        canonical_name="github-addon.issues.list",
        mcp_alias="kaiten_list_card_github_issues",
        description="List issues attached to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {**_card_addon_properties(), **_fields_property()},
            "required": ["card_id"],
        },
        operation=_list_operation(),
        response_policy=LIST_POLICY,
        runtime_behavior=_behavior(execute_github_issues_list),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon issues list --card-id 10 --fields number,htmlUrl,state",
                description="Read the issues attached to a card.",
            ),
        ),
        usage_notes=(ADDON_UID_PATH_NOTE, UID_FALLBACK_NOTE, UID_FALLBACK_COST_NOTE),
    ),
    make_tool(
        canonical_name="github-addon.issues.attach",
        mcp_alias="kaiten_attach_github_issue",
        description="Attach an issue to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {
                **_card_addon_properties(),
                "issue_json": {"type": "object", "description": "Raw GitHub REST issue object."},
                **_repo_properties("identity"),
                **_dry_run_property(),
            },
            "required": ["card_id", "issue_json", "owner", "repo"],
        },
        operation=_write_operation(),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=_behavior(execute_github_issues_attach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon issues attach --card-id 10 --owner acme --repo web --issue-json @issue.json",
                description="Attach an issue fetched with gh api repos/OWNER/REPO/issues/NUMBER.",
            ),
        ),
        usage_notes=(
            ADDON_UID_PATH_NOTE,
            UID_FALLBACK_NOTE,
            AMBIGUOUS_ADDON_NOTE,
            UID_FALLBACK_COST_NOTE,
            REST_JSON_NOTE,
            (
                "GitHub returns pull requests from the issues endpoint too; a payload with a "
                "pull_request field is rejected, attach it as a pull request instead."
            ),
            DEDUP_NOTE_BY_ID,
            SHARED_WRITE_NOTE,
            STRICT_WRITE_NOTE,
            RACE_NOTE,
            DRY_RUN_NOTE,
        ),
    ),
    make_tool(
        canonical_name="github-addon.issues.detach",
        mcp_alias="kaiten_detach_github_issue",
        description="Detach an issue from a card in the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {
                **_card_addon_properties(),
                "issue_id": {"type": "integer", "description": "GitHub numeric issue id."},
                "number": {"type": "integer", "description": "Issue number."},
                **_repo_properties("filter"),
                **_all_property(),
                **_dry_run_property(),
            },
            "required": ["card_id"],
        },
        operation=_write_operation(),
        response_policy=PLAIN_ENTITY_POLICY,
        runtime_behavior=_behavior(execute_github_issues_detach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon issues detach --card-id 10 --number 7 --owner acme --repo web",
                description="Detach one issue from a card.",
            ),
        ),
        usage_notes=(
            ADDON_UID_PATH_NOTE,
            UID_FALLBACK_NOTE,
            AMBIGUOUS_ADDON_NOTE,
            UID_FALLBACK_COST_NOTE,
            (
                "Provide --issue-id or --number; --owner and --repo narrow the match when the same "
                "number exists in several repositories."
            ),
            AMBIGUOUS_SELECTOR_NOTE,
            EMPTY_KEY_NOTE,
            STRICT_WRITE_NOTE,
            RACE_NOTE,
            DRY_RUN_NOTE,
        ),
    ),
)
