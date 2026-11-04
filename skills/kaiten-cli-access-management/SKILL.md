---
name: kaiten-cli-access-management
description: Select kaiten-cli API commands and parameters for entity creation and movement, users, groups, access assignments, and access roles. Explains required permissions, inheritance, and documented versus API-token extension routes. Does not interpret external access specifications or orchestrate reconciliation.
---

# Kaiten API access reference

Use this skill to select CLI capabilities and supply already chosen targets,
roles and parameters. External agents/harnesses own business rules, specification
interpretation, desired-state comparisons, scheduling and execution orchestration.
Do not add those mechanisms to the CLI or infer which access a person should have.

Pass `--locale ru` for Russian conversations, `--locale en` otherwise, before
the command name, including discovery. Prefer `--json`. Discover the family
once with `search-tools`, `describe`, and `examples` before using it.

## Choose the route

Prefer documented APIs at https://developers.kaiten.ru/:

- `tree-entities list`: objects readable by the token owner, not company inventory.
- `space-users list/add/update/remove`: space assignments.
- `company-groups.*`, `group-users.*`, `group-entities.*`: company groups,
  membership, and group-to-entity access. Group assignments use `entity_uid` and
  `role_ids` (array of UUIDs).
- `roles list`: available UUID access roles.
- `company-users update`, `company-groups create/update`: administrative
  `permissions` or `named_permissions`; use one format per request.
- `spaces.*`, `documents.*`, `document-groups.*`: entity operations, including
  placement via `parent_entity_uid` where described by the command.

Where those do not provide the requested operation, explicitly select these
undocumented ordinary API-token extensions:

- `admin-tree-entities list/list-all`: administrative metadata. `list` uses
  `parent_uid`, not `parent_entity_uid`; omit `user_id` for company inventory.
  `list-all` provides bounded flat pagination, not a transactional snapshot.
- `document-users`, `document-group-users`, `story-map-users`:
  `list/add/update/remove` direct assignments.
- `space-access-groups`, `document-access-groups`,
  `document-group-access-groups`, `story-map-access-groups`: `list` group access.
- `roles get/create/update/delete`: UUID access role definitions.
- `story-maps list/get/create/update/delete`: basic story map operations.

The 26 extension commands were live validated with an ordinary API token on an
authorized test company on 2026-11-04, including grant/revoke and cleanup.
Story-map creation supplies a missing sort_order as a Unix timestamp, matching
document creation. Other server versions still need compatibility checks.
Check `describe` for version/permission notes. Preserve 401/403/404/405 errors;
do not retry via browser sessions, Superadmin API, a different route, or a
self-grant. The server-blocked `PATCH /admin-tree-entities` is not exposed.

## Parameters and permissions

- User IDs are numeric. Direct assignments use `role_id` (UUID); groups use
  `role_ids` (array). `roles` controls entity access; numeric `user-roles`
  belongs to timesheets and is not interchangeable.
- Space/map user commands take numeric `space_id`/`map_id`. Document/folder
  user commands take UUID `document_uid`/`group_uid` (the latter is a folder).
  Every `*-access-groups list` takes the object's UUID `entity_uid`.
- Administrative listing needs `entitiesTree` or `members`. Managing document,
  folder or map users needs object `access_control` or `entitiesTree`.
  Group assignments and custom role writes need `members` and relevant modules.
  Entity creation/movement/deletion checks its own source/destination permissions.
- A token grants no extra rights; `profile probe` verifies authentication only.
  Module/license availability is separate from permissions. See command notes
  for invitation requirements; no role name guarantees every operation.
- `include_inherited_access=true` requests inherited access. `own_role_ids`
  describes direct user roles, `role_ids` can include inherited user roles.
  Group roles are separate: `own_groups_role_ids` is direct, `groups_role_ids`
  includes inheritance. These arrays can be null. `role_permissions` describes
  effective permissions. CLI returns server results, not a computed ACL.
  Removing one assignment may leave access through another group, an ancestor,
  or everyone access. Movement changes inheritance; shared role edits affect
  every assignment of that role.
  A nested object's author can have only inherited access; moving it to root
  or closing access can return 400 if no access controller would remain. Any
  caller-authorized direct grant is a separate command, not an automatic fallback.
- Role create needs the complete server `permissions` JSON. Role update merges
  supplied keys; use explicit `false` to remove a permission. System/locked
  role protections and replacement requirements remain server-enforced.
- Named company permissions are partial maps: omitted names are preserved.
  `false` removes a direct grant, not another group's grant. Inspect
  `own_named_permissions` versus effective `named_permissions`; unknown names
  may be ignored by the server. Never send numeric and named formats together.
  On the test company, writing named permissions to a temporary virtual user
  returned HTTP 500. Success for company-user permission writes remains
  unvalidated; do not retry an uncertain mutation without reading its state.

Examples (replace placeholders with targets already selected by the caller):

```bash
kaiten --locale ru --json --read-only document-users list --document-uid <uuid> --include-inherited-access true
kaiten --locale ru --json document-users add --document-uid <uuid> --user-id 123 --role-id <role_uuid>
kaiten --locale ru --json document-users update --document-uid <uuid> --user-id 123 --role-id <role_uuid>
kaiten --locale ru --json group-users add --group-uid <user_group_uuid> --user-id 123
kaiten --locale ru --json group-entities add --group-uid <user_group_uuid> --entity-uid <uuid> --role-ids '["<role_uuid>"]'
kaiten --locale ru --json story-maps update --map-id 10 --parent-entity-uid <folder_uuid>
```

For actual writes, follow the existing
[mutation skill](../kaiten-cli-mutations/SKILL.md), respecting authorization
already supplied for the current task. This reference does not authorize writes.
For operation examples and compatibility details read
[ACCESS_MANAGEMENT.md](../../docs/ACCESS_MANAGEMENT.md), or the
[published reference](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/ACCESS_MANAGEMENT.md)
when the skill is installed outside the repository.
