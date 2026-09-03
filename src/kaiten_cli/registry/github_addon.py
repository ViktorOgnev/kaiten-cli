"""GitHub addon tool specs: the PR/branch/commit/issue attachments shown on a card.

The Kaiten GitHub addon does not store attachments as external links. It keeps
them in the card's shared addon data under `attachedPulls`, `attachedBranches`,
`attachedCommits` and `attachedIssues`, and the card widget re-reads each entry
from GitHub by (owner, repo, number/name/sha). These commands read and write that
store in the addon's own payload shape, so an entry written from the CLI is
indistinguishable from one added through the addon UI.
"""

from __future__ import annotations

from kaiten_cli.models import ExampleSpec, OperationSpec, ResponsePolicy, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
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

ADDON_UID_NOTE = (
    "The addon UUID is appended to the path at runtime: --addon-uid when given, otherwise "
    "derived from --addon-url-path (default /github), which matches how self-hosted Kaiten "
    "derives addon UUIDs from mount paths."
)
REST_JSON_NOTE = (
    "Pass the raw GitHub REST object, for example from gh api. The CLI never calls GitHub "
    "itself, so the payload is the only source of title, state and author shown as a fallback "
    "when the widget cannot reach GitHub."
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

LIST_POLICY = ResponsePolicy(compact_supported=True, fields_supported=True, result_kind="list")
# Write results are small envelopes, so they expose no --compact / --fields options.
ENTITY_POLICY = ResponsePolicy(result_kind="entity")


def _addon_properties() -> dict[str, dict]:
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


def _shaping_properties() -> dict[str, dict]:
    return {
        "compact": {
            "type": "boolean",
            "description": "Return compact output without heavy nested fields.",
        },
        "fields": {
            "type": "string",
            "description": "Comma-separated field names to return.",
        },
    }


def _repo_properties(required: bool) -> dict[str, dict]:
    suffix = "" if required else " Optional filter."
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


def _list_operation() -> OperationSpec:
    return OperationSpec(method="GET", path_template=CARD_DATA_PATH, path_fields=("card_id",))


def _write_operation() -> OperationSpec:
    return OperationSpec(method="PATCH", path_template=CARD_DATA_PATH, path_fields=("card_id",))


def _list_behavior(executor) -> RuntimeBehavior:
    return RuntimeBehavior(execution_mode="custom", custom_executor=executor)


def _write_behavior(executor) -> RuntimeBehavior:
    return RuntimeBehavior(execution_mode="custom", custom_executor=executor)


TOOLS = (
    make_tool(
        canonical_name="github-addon.pulls.list",
        mcp_alias="kaiten_list_card_github_pulls",
        description="List pull requests attached to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {**_addon_properties(), **_shaping_properties()},
            "required": ["card_id"],
        },
        operation=_list_operation(),
        response_policy=LIST_POLICY,
        runtime_behavior=_list_behavior(execute_github_pulls_list),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon pulls list --card-id 10 --fields number,htmlUrl,state",
                description="Read the PR links attached to a card.",
            ),
        ),
        usage_notes=(
            ADDON_UID_NOTE,
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
                **_addon_properties(),
                "pull_json": {
                    "type": "object",
                    "description": "Raw GitHub REST pull request object.",
                },
                **_dry_run_property(),
            },
            "required": ["card_id", "pull_json"],
        },
        operation=_write_operation(),
        response_policy=ENTITY_POLICY,
        runtime_behavior=_write_behavior(execute_github_pulls_attach),
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
        usage_notes=(REST_JSON_NOTE, DEDUP_NOTE_BY_ID, SHARED_WRITE_NOTE, DRY_RUN_NOTE),
    ),
    make_tool(
        canonical_name="github-addon.pulls.detach",
        mcp_alias="kaiten_detach_github_pull",
        description="Detach a pull request from a card in the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {
                **_addon_properties(),
                "pull_id": {"type": "integer", "description": "GitHub numeric pull request id."},
                "number": {"type": "integer", "description": "Pull request number."},
                **_repo_properties(required=False),
                **_dry_run_property(),
            },
            "required": ["card_id"],
        },
        operation=_write_operation(),
        response_policy=ENTITY_POLICY,
        runtime_behavior=_write_behavior(execute_github_pulls_detach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon pulls detach --card-id 10 --number 42 --owner acme --repo web",
                description="Detach one PR from a card.",
            ),
        ),
        usage_notes=(
            (
                "Provide --pull-id or --number; --owner and --repo narrow the match when the same "
                "number exists in several repositories."
            ),
            (
                "Every attachment matching the given selectors is removed; a selector that matches "
                "nothing leaves the stored data untouched."
            ),
            EMPTY_KEY_NOTE,
            DRY_RUN_NOTE,
        ),
    ),
    make_tool(
        canonical_name="github-addon.branches.list",
        mcp_alias="kaiten_list_card_github_branches",
        description="List branches attached to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {**_addon_properties(), **_shaping_properties()},
            "required": ["card_id"],
        },
        operation=_list_operation(),
        response_policy=LIST_POLICY,
        runtime_behavior=_list_behavior(execute_github_branches_list),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon branches list --card-id 10 --fields branchName,htmlUrl",
                description="Read the branches attached to a card.",
            ),
        ),
        usage_notes=(ADDON_UID_NOTE,),
    ),
    make_tool(
        canonical_name="github-addon.branches.attach",
        mcp_alias="kaiten_attach_github_branch",
        description="Attach a branch to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {
                **_addon_properties(),
                "branch_json": {"type": "object", "description": "Raw GitHub REST branch object."},
                **_repo_properties(required=True),
                **_dry_run_property(),
            },
            "required": ["card_id", "branch_json", "owner", "repo"],
        },
        operation=_write_operation(),
        response_policy=ENTITY_POLICY,
        runtime_behavior=_write_behavior(execute_github_branches_attach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon branches attach --card-id 10 --owner acme --repo web --branch-json @branch.json",
                description="Attach a branch fetched with gh api repos/OWNER/REPO/branches/NAME.",
            ),
        ),
        usage_notes=(
            REST_JSON_NOTE,
            (
                "A REST branch object carries no repository, so --owner and --repo are required and "
                "form the stored branch identity."
            ),
            DEDUP_NOTE_BY_PSEUDO_ID,
            SHARED_WRITE_NOTE,
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
                **_addon_properties(),
                "branch_name": {"type": "string", "description": "Branch name."},
                "pseudo_id": {
                    "type": "string",
                    "description": "Stored branch identity in owner/repo/branch form.",
                },
                **_repo_properties(required=False),
                **_dry_run_property(),
            },
            "required": ["card_id"],
        },
        operation=_write_operation(),
        response_policy=ENTITY_POLICY,
        runtime_behavior=_write_behavior(execute_github_branches_detach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon branches detach --card-id 10 --branch-name feature/login --owner acme --repo web",
                description="Detach one branch from a card.",
            ),
        ),
        usage_notes=(
            (
                "Provide --pseudo-id or --branch-name; --owner and --repo narrow the match when the "
                "same branch name exists in several repositories."
            ),
            EMPTY_KEY_NOTE,
            DRY_RUN_NOTE,
        ),
    ),
    make_tool(
        canonical_name="github-addon.commits.list",
        mcp_alias="kaiten_list_card_github_commits",
        description="List commits attached to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {**_addon_properties(), **_shaping_properties()},
            "required": ["card_id"],
        },
        operation=_list_operation(),
        response_policy=LIST_POLICY,
        runtime_behavior=_list_behavior(execute_github_commits_list),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon commits list --card-id 10 --fields sha,htmlUrl,message",
                description="Read the commits attached to a card.",
            ),
        ),
        usage_notes=(ADDON_UID_NOTE,),
    ),
    make_tool(
        canonical_name="github-addon.commits.attach",
        mcp_alias="kaiten_attach_github_commit",
        description="Attach a commit to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {
                **_addon_properties(),
                "commit_json": {"type": "object", "description": "Raw GitHub REST commit object."},
                **_repo_properties(required=True),
                **_dry_run_property(),
            },
            "required": ["card_id", "commit_json", "owner", "repo"],
        },
        operation=_write_operation(),
        response_policy=ENTITY_POLICY,
        runtime_behavior=_write_behavior(execute_github_commits_attach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon commits attach --card-id 10 --owner acme --repo web --commit-json @commit.json",
                description="Attach a commit fetched with gh api repos/OWNER/REPO/commits/SHA.",
            ),
        ),
        usage_notes=(
            REST_JSON_NOTE,
            (
                "The stored author prefers the linked GitHub account and falls back to the git "
                "author name, exactly as the addon does."
            ),
            DEDUP_NOTE_BY_SHA,
            SHARED_WRITE_NOTE,
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
                **_addon_properties(),
                "sha": {"type": "string", "description": "Full commit sha as stored."},
                **_repo_properties(required=False),
                **_dry_run_property(),
            },
            "required": ["card_id"],
        },
        operation=_write_operation(),
        response_policy=ENTITY_POLICY,
        runtime_behavior=_write_behavior(execute_github_commits_detach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon commits detach --card-id 10 --sha 3f1a2bc4d5e6f708192a3b4c5d6e7f8091a2b3c4",
                description="Detach one commit from a card.",
            ),
        ),
        usage_notes=(
            "--sha is required and matched in full; short shas do not match stored entries.",
            EMPTY_KEY_NOTE,
            DRY_RUN_NOTE,
        ),
    ),
    make_tool(
        canonical_name="github-addon.issues.list",
        mcp_alias="kaiten_list_card_github_issues",
        description="List issues attached to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {**_addon_properties(), **_shaping_properties()},
            "required": ["card_id"],
        },
        operation=_list_operation(),
        response_policy=LIST_POLICY,
        runtime_behavior=_list_behavior(execute_github_issues_list),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon issues list --card-id 10 --fields number,htmlUrl,state",
                description="Read the issues attached to a card.",
            ),
        ),
        usage_notes=(ADDON_UID_NOTE,),
    ),
    make_tool(
        canonical_name="github-addon.issues.attach",
        mcp_alias="kaiten_attach_github_issue",
        description="Attach an issue to a card through the GitHub addon.",
        input_schema={
            "type": "object",
            "properties": {
                **_addon_properties(),
                "issue_json": {"type": "object", "description": "Raw GitHub REST issue object."},
                **_repo_properties(required=True),
                **_dry_run_property(),
            },
            "required": ["card_id", "issue_json", "owner", "repo"],
        },
        operation=_write_operation(),
        response_policy=ENTITY_POLICY,
        runtime_behavior=_write_behavior(execute_github_issues_attach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon issues attach --card-id 10 --owner acme --repo web --issue-json @issue.json",
                description="Attach an issue fetched with gh api repos/OWNER/REPO/issues/NUMBER.",
            ),
        ),
        usage_notes=(
            REST_JSON_NOTE,
            (
                "GitHub returns pull requests from the issues endpoint too; a payload with a "
                "pull_request field is rejected, attach it as a pull request instead."
            ),
            DEDUP_NOTE_BY_ID,
            SHARED_WRITE_NOTE,
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
                **_addon_properties(),
                "issue_id": {"type": "integer", "description": "GitHub numeric issue id."},
                "number": {"type": "integer", "description": "Issue number."},
                **_repo_properties(required=False),
                **_dry_run_property(),
            },
            "required": ["card_id"],
        },
        operation=_write_operation(),
        response_policy=ENTITY_POLICY,
        runtime_behavior=_write_behavior(execute_github_issues_detach),
        examples=(
            ExampleSpec(
                command="kaiten --json github-addon issues detach --card-id 10 --number 7 --owner acme --repo web",
                description="Detach one issue from a card.",
            ),
        ),
        usage_notes=(
            (
                "Provide --issue-id or --number; --owner and --repo narrow the match when the same "
                "number exists in several repositories."
            ),
            EMPTY_KEY_NOTE,
            DRY_RUN_NOTE,
        ),
    ),
)
