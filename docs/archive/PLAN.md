# kaiten-cli v1: archived execution baseline

## Summary

This file is an archived execution snapshot.
It is preserved for historical context and implementation archaeology, not as the current source of truth.

Current maintained docs live in the repo root:

- [README.md](../../README.md)
- [ARCHITECTURE.md](../../ARCHITECTURE.md)
- [LIVE_VALIDATION.md](../../LIVE_VALIDATION.md)
- [API_BEHAVIOR_MATRIX.md](../../API_BEHAVIOR_MATRIX.md)

The CLI is already established as a separate native project: no runtime dependency on `kaiten-mcp`, manual registry as the source of truth, test-first delivery, and live validation only after green local tests.

As of `2026-04-15`, the CLI has reached full tool-set registry parity with the current sibling `kaiten-mcp` tool surface. The plan below freezes the completed baseline, the active guardrails, and the remaining maintenance/live-expansion decisions so that further work does not drift from the original direction.

Supporting documents:

- [PLAN_TRIZ_VERIFICATION.md](PLAN_TRIZ_VERIFICATION.md) records verification status for this plan.
- [PLAN_EXTERNAL_REVIEW.md](PLAN_EXTERNAL_REVIEW.md) records the independent external review.
- [PARITY_CHECKLIST.md](PARITY_CHECKLIST.md) is the representative subset used for MCP parity checks.
- [LIVE_VALIDATION.md](../../LIVE_VALIDATION.md) records the live-validation process and contract classes.
- [API_BEHAVIOR_MATRIX.md](../../API_BEHAVIOR_MATRIX.md) records special sandbox API contracts and synthetic fallbacks.

These documents do not define extra scope beyond this file.

## Execution Status

- `Phase 1: foundation and representative subset` — `completed`
  - Native CLI architecture is in place.
  - Canonical commands, MCP aliases, discovery, profiles, JSON envelopes, local transforms, and sandbox mutation guard are implemented.
  - Representative subset for `spaces`, `boards`, and `cards` is implemented and verified.
- `Phase 2: low-risk domain expansion` — `completed`
  - Added bounded registry coverage for `columns`, `subcolumns`, `lanes`, `checklists`, `checklist-items`, and `comments`.
  - Added offline tests for namespace visibility, alias parity, and request shaping for the new slice.
  - Extended the opt-in live smoke path with safe read-only checks for `columns list`, `lanes list`, `users current`, and `users list`.
- `Phase 3: card-adjacent bounded expansion` — `completed`
  - Added bounded registry coverage for `external-links`, `tags`, `card-tags`, `card-members`, `users`, `blockers`, `files`, `card-children`, `card-parents`, and `planned-relations`.
  - Added offline tests for request remapping, default-limit injection, alias parity, and special execution behavior for `blockers.get`.
  - Kept live smoke narrow: only safe read-only coverage was added, with no new live mutations beyond the original `cards` smoke path.
- `Phase 4: project and time-log expansion` — `completed`
  - Added bounded registry coverage for `projects`, `projects.cards`, and `time-logs`.
  - Added offline tests for `projects.title -> name` remapping, default `role_id = -1` for `time-logs.create`, and compact project-card listing.
  - Extended live smoke with safe `time-logs create/list/update/delete` checks on the temporary smoke card.
- `Phase 5: utilities bounded subset` — `completed`
  - Added registry coverage for `company.current`, `calendars.list/get`, and `user-timers.list/create/get/update/delete`.
  - Added offline tests for `calendars.list` default-limit parity and `user-timers` request shaping.
  - Extended live smoke with `company.current` and `calendars.list/get`.
  - Explicitly kept `user-timers` out of the live allowlist after sandbox showed `405`/singleton-timer instability.
- `Phase 6: higher-complexity remaining domains` — `completed`
  - Nested command-tree hardening is completed: canonical nested resources now resolve as real nested commands instead of dotted pseudo-actions.
  - Registry examples are validated against the actual CLI command tree to prevent future drift.
  - Added offline-only bounded coverage for `documents`, `document-groups`, `tree.children.list`, and `tree.get`.
  - Added offline parity tests for document payload shaping, default limits, tree aggregation, and nested alias parity.
  - Live allowlist remains unchanged for this slice because `tree` is heavy and `documents` introduce new mutation/cleanup flows.
  - Added offline-only bounded coverage for `card-types`, `custom-properties`, and nested `custom-properties.select-values`.
  - Added offline parity tests for default limits, nested alias parity, delete-body shaping, and soft-delete PATCH semantics for select values.
  - Live allowlist remains unchanged for this slice because these domains add company-level mutations that are not yet part of the sandbox smoke contract.
  - Added offline-only bounded coverage for `space-users`, `company-groups`, `group-users`, `roles`, `card-subscribers`, and `column-subscribers`.
  - Added offline parity tests for list defaults, compact response shaping, nested alias parity, and `column-subscribers.add` default `type = 1`.
  - Live allowlist remains unchanged for this slice because subscriber and company-group mutations are outside the current sandbox smoke contract.
  - Added offline-only bounded coverage for `webhooks`, `incoming-webhooks`, `automations`, and `workflows`.
  - Added offline parity tests for workflow default limits, automation alias parity, `automations.copy` body remapping, and incoming-webhook request shaping.
  - Live allowlist remains unchanged for this slice because these domains introduce integration/webhook side effects outside the current sandbox smoke contract.
  - Added bounded coverage for the remaining lightweight `utilities` endpoints: `api-keys`, `removed-cards`, and `removed-boards`.
  - Added offline parity tests for recycle-bin default limits, utility alias parity, and API-key request shaping.
  - Added full offline coverage for the remaining heavy/high-variance domains: `service-desk`, `charts`, and `audit_and_analytics`.
  - Added final completion coverage for the previously hidden parity tail: `cards.move`, `cards.list-all`, `sprints.*`, and `company.update`.
  - Added parity-specific executor support for `saved-filters name -> title`, synthetic `space-activity-all` pagination, and synthetic `cards.list-all` pagination.
  - Added a local parity regression test that compares the implemented alias set against the current `kaiten-mcp` tool registry snapshot in the sibling repo.
  - Local baseline after completion: `120 passed, 1 deselected`.
  - Functional command parity against `kaiten-mcp` is now complete; the remaining decisions are about maintenance and optional live-surface growth, not missing domains.
- `Phase 7: full sandbox live validation campaign` — `in progress`
  - The narrow smoke suite has been replaced by a phased full live harness under `tests/live/`.
  - Live execution now uses a strict cleanup stack, reverse-order teardown, canonical-command coverage accounting, and policy exclusions for irreversible commands.
  - Current live safety exclusions:
    - `api-keys.create`
    - `api-keys.delete`
  - Live-contract documentation is now explicit instead of being hidden only inside `tests/live/`:
    - added `README.md`
    - added `LIVE_VALIDATION.md`
    - added `API_BEHAVIOR_MATRIX.md`
    - added shared live-contract metadata in `src/kaiten_cli/registry/live_contracts.py`
  - `projects.cards.list` no longer relies on MCP parity alone:
    - primary path stays `GET /projects/{project_id}/cards`
    - on sandbox `405`, CLI now falls back to `GET /projects/{project_id}?with_cards_data=true`
    - embedded project cards are extracted as a documented synthetic read contract
  - Live-suite assumptions were corrected to match real sandbox behavior:
    - `sprints.list` may return `403/405`
    - `sprints.create` may succeed without returning an `id`
    - `sprints.update` on a sentinel id may return `500`
    - `space-users.add` / `space-users.update` require UUID `role_id`, not integer
    - `custom-properties.create` for `type=vote` requires non-empty typed `data`
  - Local baseline after the live-harness refactor: `121 passed, 1 deselected`.
  - Real sandbox contracts already confirmed during this phase:
    - `boards.delete` requires `force`
    - `removed-boards.list` returns `405`
    - `removed-cards.list` returns `405`
    - `checklists.list` returns `405`
    - `checklist-items.list` returns `405`
    - `card-subscribers.list` returns `405`
    - `column-subscribers.list` returns `405`
    - `card-members.remove` may return a successful no-op on a missing user instead of `404`
    - `space-users.remove` may return a successful no-op on a missing user instead of `404`
    - `automations.get` may return `405` even after successful creation
    - `automations.create` succeeds on sandbox when the payload matches the e2e-derived `add_assignee + created + data.variant + data.userId` shape
    - `automations.copy` remains sandbox-dependent even with a live-valid source automation
    - `service-desk.users.update` may return `400 Should be service desk user` for the current sandbox account
    - `service-desk.users.set-temp-password` may either succeed or return `403/404/405` on the same sandbox account
    - `service-desk.organization-users.update` may either succeed or return `400/403/404/405` even after a successful `organization-users.add`
    - `service-desk.services.create` requires `lng`; the CLI contract was tightened to make `lng` mandatory
    - `webhooks.get` / `webhooks.delete` may return `404/405` even after successful creation
  - The phase is not complete yet: the full live suite is running iteratively against sandbox until all remaining blockers are either fixed in CLI/runtime or codified as verified sandbox error contracts.
  - Current local baseline after restoring strict tool-set parity and extending coverage: `136 passed, 2 deselected`.
  - Current live blocker after the latest full pass: `service-desk.sla.create` returns `400 Sla.rules[0] should have required property 'type'` for the current minimal rules payload.

## Current Baseline

### 1. Architecture in force

- `kaiten-cli` remains a standalone native CLI project.
- Runtime integration with `kaiten-mcp` is intentionally absent.
- The source of truth is the manual registry under `src/kaiten_cli/registry/`.
- Command surface supports both canonical commands and MCP-style aliases.
- Delivery remains strictly test-first for every new domain or behavior.

### 2. Implemented CLI surface

Global interface already present:

- `kaiten <namespace...> <action>`
- `kaiten <mcp_alias>`
- `kaiten search-tools <query>`
- `kaiten describe <command-or-alias>`
- `kaiten examples <command-or-alias>`
- `kaiten profile add|use|list|show|remove`

Global flags already present:

- `--json`
- `--profile`
- `--from-file`
- `--stdin-json`
- `--verbose`
- `--no-color`

Representative domain subset already present:

- `spaces.list`
- `spaces.get`
- `spaces.create`
- `spaces.update`
- `spaces.delete`
- `boards.list`
- `boards.get`
- `boards.create`
- `boards.update`
- `boards.delete`
- `cards.list`
- `cards.get`
- `cards.create`
- `cards.update`
- `cards.delete`
- `cards.archive`
- `columns.list`
- `columns.create`
- `columns.update`
- `columns.delete`
- `subcolumns.list`
- `subcolumns.create`
- `subcolumns.update`
- `subcolumns.delete`
- `lanes.list`
- `lanes.create`
- `lanes.update`
- `lanes.delete`
- `checklists.list`
- `checklists.create`
- `checklists.update`
- `checklists.delete`
- `checklist-items.list`
- `checklist-items.create`
- `checklist-items.update`
- `checklist-items.delete`
- `comments.list`
- `comments.create`
- `comments.update`
- `comments.delete`
- `external-links.list`
- `external-links.create`
- `external-links.update`
- `external-links.delete`
- `tags.list`
- `tags.create`
- `tags.update`
- `tags.delete`
- `card-tags.add`
- `card-tags.remove`
- `card-members.list`
- `card-members.add`
- `card-members.remove`
- `users.list`
- `users.current`
- `blockers.list`
- `blockers.get`
- `blockers.create`
- `blockers.update`
- `blockers.delete`
- `files.list`
- `files.create`
- `files.update`
- `files.delete`
- `card-children.list`
- `card-children.add`
- `card-children.remove`
- `card-parents.list`
- `card-parents.add`
- `card-parents.remove`
- `projects.list`
- `projects.create`
- `projects.get`
- `projects.update`
- `projects.delete`
- `projects.cards.list`
- `projects.cards.add`
- `projects.cards.remove`
- `time-logs.list`
- `time-logs.create`
- `time-logs.update`
- `time-logs.delete`
- `documents.list`
- `documents.create`
- `documents.get`
- `documents.update`
- `documents.delete`
- `document-groups.list`
- `document-groups.create`
- `document-groups.get`
- `document-groups.update`
- `document-groups.delete`
- `tree.children.list`
- `tree.get`
- `card-types.list`
- `card-types.get`
- `card-types.create`
- `card-types.update`
- `card-types.delete`
- `custom-properties.list`
- `custom-properties.get`
- `custom-properties.create`
- `custom-properties.update`
- `custom-properties.delete`
- `custom-properties.select-values.list`
- `custom-properties.select-values.get`
- `custom-properties.select-values.create`
- `custom-properties.select-values.update`
- `custom-properties.select-values.delete`
- `space-users.list`
- `space-users.add`
- `space-users.update`
- `space-users.remove`
- `company-groups.list`
- `company-groups.create`
- `company-groups.get`
- `company-groups.update`
- `company-groups.delete`
- `group-users.list`
- `group-users.add`
- `group-users.remove`
- `roles.list`
- `roles.get`
- `card-subscribers.list`
- `card-subscribers.add`
- `card-subscribers.remove`
- `column-subscribers.list`
- `column-subscribers.add`
- `column-subscribers.remove`
- `webhooks.list`
- `webhooks.create`
- `webhooks.get`
- `webhooks.update`
- `webhooks.delete`
- `incoming-webhooks.list`
- `incoming-webhooks.create`
- `incoming-webhooks.update`
- `incoming-webhooks.delete`
- `automations.list`
- `automations.create`
- `automations.get`
- `automations.update`
- `automations.delete`
- `automations.copy`
- `workflows.list`
- `workflows.create`
- `workflows.get`
- `workflows.update`
- `workflows.delete`
- `api-keys.list`
- `api-keys.create`
- `api-keys.delete`
- `removed-cards.list`
- `removed-boards.list`
- `company.current`
- `calendars.list`
- `calendars.get`
- `user-timers.list`
- `user-timers.create`
- `user-timers.get`
- `user-timers.update`
- `user-timers.delete`

Additional implemented domain families beyond the representative subset:

- full `service-desk` surface, including requests, services, organizations, settings, stats, users, template answers, SLA policies, SLA rules, vote properties, org membership operations, and card/space SLA measurement commands
- full `charts` surface, including chart board discovery, sync chart endpoints, async chart endpoints, and compute-job commands
- full `audit_and_analytics` surface, including audit logs, card/space/company activity, saved filters, card location history, and bulk `space-activity-all`
- completion-tail commands required for full MCP parity: `cards.move`, `cards.list-all`, `sprints.*`, `company.update`

Parity status:

- canonical commands and MCP aliases match the full current sibling `kaiten-mcp` tool surface
- local parity regression verifies exact alias-set equality against the sibling repo, including both `_tool("...")` and `_tool(name="...")` declarations

MCP-compatible aliases already present for the same subset:

- `kaiten_list_spaces`
- `kaiten_get_space`
- `kaiten_create_space`
- `kaiten_update_space`
- `kaiten_delete_space`
- `kaiten_list_boards`
- `kaiten_get_board`
- `kaiten_create_board`
- `kaiten_update_board`
- `kaiten_delete_board`
- `kaiten_list_cards`
- `kaiten_get_card`
- `kaiten_create_card`
- `kaiten_update_card`
- `kaiten_delete_card`
- `kaiten_archive_card`
- `kaiten_list_columns`
- `kaiten_create_column`
- `kaiten_update_column`
- `kaiten_delete_column`
- `kaiten_list_subcolumns`
- `kaiten_create_subcolumn`
- `kaiten_update_subcolumn`
- `kaiten_delete_subcolumn`
- `kaiten_list_lanes`
- `kaiten_create_lane`
- `kaiten_update_lane`
- `kaiten_delete_lane`
- `kaiten_list_checklists`
- `kaiten_create_checklist`
- `kaiten_update_checklist`
- `kaiten_delete_checklist`
- `kaiten_list_checklist_items`
- `kaiten_create_checklist_item`
- `kaiten_update_checklist_item`
- `kaiten_delete_checklist_item`
- `kaiten_list_comments`
- `kaiten_create_comment`
- `kaiten_update_comment`
- `kaiten_delete_comment`
- `kaiten_list_external_links`
- `kaiten_create_external_link`
- `kaiten_update_external_link`
- `kaiten_delete_external_link`
- `kaiten_list_tags`
- `kaiten_create_tag`
- `kaiten_update_tag`
- `kaiten_delete_tag`
- `kaiten_add_card_tag`
- `kaiten_remove_card_tag`
- `kaiten_list_card_members`
- `kaiten_add_card_member`
- `kaiten_remove_card_member`
- `kaiten_list_users`
- `kaiten_get_current_user`
- `kaiten_list_card_blockers`
- `kaiten_get_card_blocker`
- `kaiten_create_card_blocker`
- `kaiten_update_card_blocker`
- `kaiten_delete_card_blocker`
- `kaiten_list_card_files`
- `kaiten_create_card_file`
- `kaiten_update_card_file`
- `kaiten_delete_card_file`
- `kaiten_list_card_children`
- `kaiten_add_card_child`
- `kaiten_remove_card_child`
- `kaiten_list_card_parents`
- `kaiten_add_card_parent`
- `kaiten_remove_card_parent`
- `kaiten_list_projects`
- `kaiten_create_project`
- `kaiten_get_project`
- `kaiten_update_project`
- `kaiten_delete_project`
- `kaiten_list_project_cards`
- `kaiten_add_project_card`
- `kaiten_remove_project_card`
- `kaiten_list_card_time_logs`
- `kaiten_create_time_log`
- `kaiten_update_time_log`
- `kaiten_delete_time_log`
- `kaiten_list_documents`
- `kaiten_create_document`
- `kaiten_get_document`
- `kaiten_update_document`
- `kaiten_delete_document`
- `kaiten_list_document_groups`
- `kaiten_create_document_group`
- `kaiten_get_document_group`
- `kaiten_update_document_group`
- `kaiten_delete_document_group`
- `kaiten_list_children`
- `kaiten_get_tree`
- `kaiten_list_card_types`
- `kaiten_get_card_type`
- `kaiten_create_card_type`
- `kaiten_update_card_type`
- `kaiten_delete_card_type`
- `kaiten_list_custom_properties`
- `kaiten_get_custom_property`
- `kaiten_create_custom_property`
- `kaiten_update_custom_property`
- `kaiten_delete_custom_property`
- `kaiten_list_select_values`
- `kaiten_get_select_value`
- `kaiten_create_select_value`
- `kaiten_update_select_value`
- `kaiten_delete_select_value`
- `kaiten_list_space_users`
- `kaiten_add_space_user`
- `kaiten_update_space_user`
- `kaiten_remove_space_user`
- `kaiten_list_company_groups`
- `kaiten_create_company_group`
- `kaiten_get_company_group`
- `kaiten_update_company_group`
- `kaiten_delete_company_group`
- `kaiten_list_group_users`
- `kaiten_add_group_user`
- `kaiten_remove_group_user`
- `kaiten_list_roles`
- `kaiten_get_role`
- `kaiten_list_card_subscribers`
- `kaiten_add_card_subscriber`
- `kaiten_remove_card_subscriber`
- `kaiten_list_column_subscribers`
- `kaiten_add_column_subscriber`
- `kaiten_remove_column_subscriber`
- `kaiten_list_webhooks`
- `kaiten_create_webhook`
- `kaiten_get_webhook`
- `kaiten_update_webhook`
- `kaiten_delete_webhook`
- `kaiten_list_incoming_webhooks`
- `kaiten_create_incoming_webhook`
- `kaiten_update_incoming_webhook`
- `kaiten_delete_incoming_webhook`
- `kaiten_list_automations`
- `kaiten_create_automation`
- `kaiten_get_automation`
- `kaiten_update_automation`
- `kaiten_delete_automation`
- `kaiten_copy_automation`
- `kaiten_list_workflows`
- `kaiten_create_workflow`
- `kaiten_get_workflow`
- `kaiten_update_workflow`
- `kaiten_delete_workflow`
- `kaiten_list_api_keys`
- `kaiten_create_api_key`
- `kaiten_delete_api_key`
- `kaiten_list_removed_cards`
- `kaiten_list_removed_boards`
- `kaiten_get_company`
- `kaiten_list_calendars`
- `kaiten_get_calendar`
- `kaiten_list_user_timers`
- `kaiten_create_user_timer`
- `kaiten_get_user_timer`
- `kaiten_update_user_timer`
- `kaiten_delete_user_timer`

### 3. Behavior already implemented

- `--json` returns stable success/error envelopes.
- Discovery commands work against the local registry, not against remote help output.
- Profiles are resolved from explicit `--profile`, then profile config, then `KAITEN_DOMAIN` / `KAITEN_TOKEN`.
- Mutation commands are blocked unless the selected profile is sandbox-marked or the domain is `sandbox`.
- Default list limits are injected locally where the registry defines them.
- Response transforms are applied locally:
  - `compact`
  - `fields`
  - base64 stripping
- Narrow response shaping is already supported for the implemented `spaces`, `boards`, and `cards` subset where the registry marks it as supported.
- Nested canonical resources are routed through real CLI subgroup paths:
  - `projects.cards.list` -> `kaiten projects cards list`
  - `projects.cards.add` -> `kaiten projects cards add`
  - `projects.cards.remove` -> `kaiten projects cards remove`
- Registry examples are checked locally against the actual Click command tree so example strings cannot silently drift away from real invocations.
- Document payload shaping now mirrors the MCP behavior locally:
  - `documents.create` and `document-groups.create` auto-generate `sort_order`
  - `documents.create` and `documents.update` convert markdown `text` into ProseMirror `data`
  - `documents.create` and `documents.update` sanitize unsupported list nodes and legacy mark names in raw ProseMirror input
- Tree commands are implemented as synthetic, bounded multi-request flows:
  - `tree.children.list` fetches spaces, documents, and document groups, then returns sorted direct children
  - `tree.get` fetches the same bounded entity set and builds a nested tree with optional `root_uid` and `depth`
- Company-level metadata domains now include parity behaviors for:
  - `card-types.list` default-limit injection
  - `custom-properties.list` default-limit injection
  - `custom-properties.select-values.list` default-limit injection
  - `custom-properties.select-values.delete` soft-delete via `PATCH ... {"deleted": true}`
- Group, role, and subscriber domains now include parity behaviors for:
  - `company-groups.list` default-limit injection
  - `roles.list` default-limit injection
  - `space-users.list`, `group-users.list`, `card-subscribers.list`, and `column-subscribers.list` compact shaping
  - `column-subscribers.add` default subscription `type = 1`
- Webhook and automation domains now include parity behaviors for:
  - `workflows.list` default-limit injection
  - `automations.copy` request-body remap from `target_space_id` to `targetSpaceId`
  - canonical and alias parity for `automations.list`
- The remaining lightweight utility domain now includes parity behaviors for:
  - `removed-cards.list` default-limit injection
  - `removed-boards.list` default-limit injection
  - canonical and alias parity for recycle-bin listing commands
- Tool-specific request shaping is already supported where parity requires it:
  - `projects.title -> name`
  - `comments.format -> type`
  - `card-children.add` request-body remap
  - `card-parents.add` request-body remap
  - `blockers.get` synthetic read via list-and-filter
  - `time-logs.create` default `role_id = -1`
- Live-campaign exclusions are tracked explicitly where sandbox behavior or credential safety make clean validation impossible:
  - `api-keys.create` is excluded because it can invalidate the active token and cannot be cleaned without testing key deletion.
  - `api-keys.delete` is excluded by explicit user instruction.
- Client behavior already follows the intended low-load discipline:
  - explicit timeouts
  - throttling
  - bounded retries
  - no live traffic in the default test run

## Guardrails In Force

### 1. Test gating

- Default `pytest` runs are local-only and must not perform outbound HTTP.
- Live API tests are opt-in only.
- Live tests are marked `live` and excluded from the default test command.
- Live validation starts only after green unit/integration tests.

### 2. Live API discipline

- Sandbox is the only allowed target for mutation validation.
- Live calls are sequential only.
- The current live target is a full phased validation campaign, not a representative smoke sample.
- Heavy or unbounded commands are still executed conservatively:
  - sequentially
  - with bounded request sizes and explicit pauses
  - only after lighter phases have already passed locally
- Where the real sandbox API is known to answer with structured `4xx`, the live suite verifies that error contract instead of forcing an artificial `200` expectation.

### 3. Cleanup and load limits

- Temporary live-test entities use a unique `codex-live-<timestamp>-<kind>` prefix.
- Created IDs are tracked for cleanup.
- Cleanup runs in reverse creation order.
- Cleanup failure is treated as a test failure and a bug to fix before broadening the suite.
- Full live campaign still stays within these limits:
  - bounded `limit`, `page_size`, and `max_pages` for list/bulk commands
  - at least `0.5s` pause between normal live commands
  - at least `1.0s` pause around heavy live commands
  - abort and recalibrate on repeated `429` or timeout behavior
  - treat unexpectedly large responses as overload signals and tighten the live command contract before rerunning

## Current Verification Baseline

### 1. Local verification

The repo already contains the expected test layers:

- CLI smoke and command resolution
- input parsing and validation
- JSON and human output
- profiles
- discovery
- executor request-building and error handling
- transforms
- rate-limit and timeout policy

These run without real HTTP by default.

### 2. Live verification

The repo now contains an opt-in full live suite against sandbox.

This live suite is a validation artifact, not a replacement for unit/integration coverage. It is currently in iterative calibration mode:

- full sequential campaign rather than narrow smoke
- strict teardown with failure-on-cleanup
- coverage tracked per canonical command
- expected `4xx` contracts verified where sandbox behavior is intentionally non-`200`
- local suite must be green before every rerun

## Remaining Work

There is no remaining functional implementation backlog relative to the current `kaiten-mcp` tool surface.

What remains is bounded follow-up work:

### 1. Preserve parity discipline for future MCP changes

If `kaiten-mcp` adds or changes tools later, confirm:

- auth model stays `KAITEN_DOMAIN` + `KAITEN_TOKEN`
- base URL stays `https://{domain}.kaiten.ru/api/latest`
- retry and throttling stay bounded
- error envelopes preserve `status_code`, `message`, `body`
- canonical command and MCP alias build the same execution plan
- `compact` / `fields` semantics match the local policy for that command

### 2. Grow live validation only after local confidence

No new live expectation joins the sandbox campaign until:

- local tests for that command are green
- the command has a clear cleanup or safe no-op/error-contract story if it mutates state
- the expected payload size is bounded

## Execution Order From Here

For each future maintenance slice:

1. Add or tighten local tests first.
2. Implement the minimal registry, parsing, executor, or transform change needed for those tests.
3. Run the default local suite, including the MCP alias parity regression.
4. Update [PARITY_CHECKLIST.md](PARITY_CHECKLIST.md) if the representative regression subset changed.
5. Only if the slice is explicitly safe, extend or recalibrate the opt-in sandbox live suite and rerun the full sequential campaign.
6. Reflect the updated baseline back into the then-current plan snapshot.

This order is mandatory. The repo should evolve by repeatedly re-entering this loop, not by widening the live API surface first.

## Assumptions And Defaults

- At the time of capture, `PLAN.md` was treated as the source-of-truth execution plan.
- Supporting review documents are informative and must stay aligned with this file.
- The CLI remains native and registry-driven rather than OpenAPI-generated or MCP-proxied.
- Default development and CI flows remain offline with respect to Kaiten HTTP.
- Sandbox credentials are used only for the opt-in live acceptance path after local confidence is established.
