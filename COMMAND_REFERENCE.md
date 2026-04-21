# Command Reference

> This file is generated from the local registry. Do not edit by hand.

`kaiten-cli` currently exposes **259** canonical commands across **29** registry modules.

## Conventions

- Canonical CLI form is rendered as `kaiten <namespace...> <action>`.
- MCP alias is shown inline for every command.
- All commands support `--json`, `--from-file` and `--stdin-json`; these global input modes are not repeated per command.
- `--compact` and `--fields` only apply when the command metadata says they are supported.
- Use `search-tools`, `describe` and `examples` when you need interactive discovery instead of scrolling the full page.
- For read-heavy workflows, prefer bulk tools and the `snapshot` / `query` local-first path over per-entity loops.

## Module Index

| Area | Module | Count | Section |
|---|---|---:|---|
| Карточки | `cards` | 9 | [Open](#module-cards) |
| Комментарии | `comments` | 5 | [Open](#module-comments) |
| Участники и пользователи | `members` | 5 | [Open](#module-members) |
| Логи времени | `time_logs` | 5 | [Open](#module-time-logs) |
| Теги | `tags` | 6 | [Open](#module-tags) |
| Чеклисты | `checklists` | 8 | [Open](#module-checklists) |
| Блокировки | `blockers` | 5 | [Open](#module-blockers) |
| Связи карточек | `card_relations` | 10 | [Open](#module-card-relations) |
| Внешние ссылки | `external_links` | 4 | [Open](#module-external-links) |
| Файлы карточек | `files` | 4 | [Open](#module-files) |
| Подписчики | `subscribers` | 6 | [Open](#module-subscribers) |
| Пространства | `spaces` | 6 | [Open](#module-spaces) |
| Доски | `boards` | 5 | [Open](#module-boards) |
| Колонки и подколонки | `columns` | 8 | [Open](#module-columns) |
| Дорожки | `lanes` | 4 | [Open](#module-lanes) |
| Типы карточек | `card_types` | 5 | [Open](#module-card-types) |
| Кастомные свойства | `custom_properties` | 10 | [Open](#module-custom-properties) |
| Документы | `documents` | 10 | [Open](#module-documents) |
| Вебхуки | `webhooks` | 9 | [Open](#module-webhooks) |
| Автоматизации и воркфлоу | `automations` | 11 | [Open](#module-automations) |
| Проекты и спринты | `projects` | 13 | [Open](#module-projects) |
| Роли и группы | `roles_and_groups` | 14 | [Open](#module-roles-and-groups) |
| Аудит и аналитика | `audit_and_analytics` | 12 | [Open](#module-audit-and-analytics) |
| Service Desk | `service_desk` | 47 | [Open](#module-service-desk) |
| Графики и аналитика | `charts` | 15 | [Open](#module-charts) |
| Дерево сущностей | `tree` | 2 | [Open](#module-tree) |
| Утилиты | `utilities` | 14 | [Open](#module-utilities) |
| Локальные snapshots | `snapshot` | 5 | [Open](#module-snapshot) |
| Локальные запросы | `query` | 2 | [Open](#module-query) |

## Full Reference

<a id="module-cards"></a>
## Карточки (`cards`) — 9 commands

Карточки, bulk reads и card-heavy workflows.

**Namespace tree**

```text
cards
  archive
  batch-get
  create
  delete
  get
  list
  list-all
  move
  update
```

### `cards.archive`

| Field | Value |
|---|---|
| CLI command | `kaiten cards archive` |
| MCP alias | `kaiten_archive_card` |
| Description | Archive a Kaiten card (set condition to archived). |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer|string` | yes | — | Card ID or key |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, nested user objects) |
| `fields` | `string` | no | — | Comma-separated field names to keep in the response. Example: 'id,title,state' |

**Examples**

- Archive a card.: `kaiten cards archive --card-id 123`

### `cards.batch-get`

| Field | Value |
|---|---|
| CLI command | `kaiten cards batch-get` |
| MCP alias | `kaiten_batch_get_cards` |
| Description | Fetch multiple cards by ID with bounded worker concurrency. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `aggregated` |
| Cache policy | `request_scope` |
| Path template | `/cards/batch` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_ids` | `array` | yes | — | Card IDs to fetch |
| `workers` | `integer` | no | — | Parallel workers (default 2, max 6) |
| `compact` | `boolean` | no | — | Strip heavy nested fields from card payloads |
| `fields` | `string` | no | — | Comma-separated card field names to keep |

**Examples**

- Fetch several cards in one CLI call.: `kaiten cards batch-get --card-ids '[1,2,3]' --json`
- Fetch narrowed card detail payloads with bounded concurrency.: `kaiten cards batch-get --card-ids '[1,2,3]' --workers 2 --compact --fields id,title,state,description --json`

**Notes**

- The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.
- Use this bulk path for detail enrichment after local candidate reduction or before building evidence-heavy snapshots.

### `cards.create`

| Field | Value |
|---|---|
| CLI command | `kaiten cards create` |
| MCP alias | `kaiten_create_card` |
| Description | Create a new Kaiten card. Title max 1024 chars, description max 32768 chars. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `title` | `string` | yes | — | Card title (1-1024 chars) |
| `board_id` | `integer` | yes | — | Target board ID |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, nested user objects) |
| `fields` | `string` | no | — | Comma-separated field names to keep in the response. Example: 'id,title,state' |
| `column_id` | `integer` | no | — | Target column ID |
| `lane_id` | `integer` | no | — | Target lane ID |
| `description` | `string` | no | — | Card description (max 32768) |
| `due_date` | `string|null` | no | — | Deadline (ISO 8601) |
| `asap` | `boolean` | no | — | ASAP marker |
| `size_text` | `string` | no | — | Size (e.g. S, M, L, 1, 23.45) |
| `owner_id` | `integer` | no | — | Owner user ID |
| `type_id` | `integer` | no | — | Card type ID |
| `external_id` | `string` | no | — | External ID (max 1024) |
| `sort_order` | `number` | no | — | Position in cell |
| `position` | `integer` | no | `1`, `2` | 1=first, 2=last in cell |
| `properties` | `object` | no | — | Custom properties as {id_N: value} |
| `tags` | `array` | no | — | Tags to attach |
| `sprint_id` | `integer` | no | — | Sprint ID to assign card to |
| `planned_start` | `string|null` | no | — | Planned start date (ISO 8601) |
| `planned_end` | `string|null` | no | — | Planned end date (ISO 8601) |
| `responsible_id` | `integer` | no | — | Responsible user ID |
| `condition` | `integer` | no | `1`, `2` | 1=active, 2=archived |
| `due_date_time_present` | `boolean` | no | — | True if due_date includes time component |
| `expires_later` | `boolean` | no | — | Expires later flag |
| `estimate_workload` | `integer` | no | — | Estimated workload in minutes (resource planning) |
| `child_card_ids` | `array` | no | — | Child card IDs to link (max 1) |
| `parent_card_ids` | `array` | no | — | Parent card IDs to link (max 1) |
| `project_id` | `string` | no | — | Project UUID to attach card to |

**Examples**

- Create a card.: `kaiten cards create --title "Smoke task" --board-id 10 --json`
- Create a card with a narrow response.: `kaiten cards create --title "Smoke task" --board-id 10 --compact --fields id,title,state --json`

### `cards.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten cards delete` |
| MCP alias | `kaiten_delete_card` |
| Description | Soft-delete a Kaiten card (sets condition to deleted). Cards with time logs cannot be deleted. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer|string` | yes | — | Card ID or key |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, nested user objects) |
| `fields` | `string` | no | — | Comma-separated field names to keep in the response. Example: 'id,title,state' |

**Examples**

- Delete a card.: `kaiten cards delete --card-id 123`

### `cards.get`

| Field | Value |
|---|---|
| CLI command | `kaiten cards get` |
| MCP alias | `kaiten_get_card` |
| Description | Get a Kaiten card by ID. Supports numeric ID or card key (e.g. PROJ-123). |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/cards/{card_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer|string` | yes | — | Card ID or key (e.g. PROJ-123) |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, nested user objects) |
| `fields` | `string` | no | — | Comma-separated field names to keep in the response. Example: 'id,title,state' |

**Examples**

- Get a card by numeric ID.: `kaiten cards get --card-id 123`
- Get a narrow card response.: `kaiten cards get --card-id 123 --compact --fields id,title,state --json`

**Notes**

- Bulk alternative: `cards.batch-get`
- This is a per-card entity read and becomes expensive when repeated over large card populations.
- For detail enrichment after candidate reduction, prefer cards.batch-get over one-card-at-a-time loops.

### `cards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten cards list` |
| MCP alias | `kaiten_list_cards` |
| Description | Search and list Kaiten cards with filtering. Conditions: 1=active, 2=archived. States: 1=queued, 2=inProgress, 3=done. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Full-text search query |
| `space_id` | `integer` | no | — | Filter by space ID |
| `board_id` | `integer` | no | — | Filter by board ID |
| `column_id` | `integer` | no | — | Filter by column ID |
| `lane_id` | `integer` | no | — | Filter by lane ID |
| `condition` | `integer` | no | `1`, `2` | 1=active, 2=archived |
| `type_id` | `integer` | no | — | Filter by card type ID |
| `owner_id` | `integer` | no | — | Filter by owner user ID |
| `responsible_id` | `integer` | no | — | Filter by responsible user ID |
| `tag_ids` | `string` | no | — | Comma-separated tag IDs |
| `member_ids` | `string` | no | — | Comma-separated member IDs |
| `states` | `string` | no | — | Comma-separated states (1=queued,2=inProgress,3=done) |
| `created_after` | `string` | no | — | ISO datetime filter |
| `created_before` | `string` | no | — | ISO datetime filter |
| `updated_after` | `string` | no | — | ISO datetime filter |
| `updated_before` | `string` | no | — | ISO datetime filter |
| `due_date_after` | `string` | no | — | ISO datetime filter |
| `due_date_before` | `string` | no | — | ISO datetime filter |
| `external_id` | `string` | no | — | External ID filter |
| `overdue` | `boolean` | no | — | Filter overdue cards |
| `asap` | `boolean` | no | — | Filter ASAP cards |
| `archived` | `boolean` | no | — | Include archived |
| `limit` | `integer` | no | — | Max results (default 50, max 100) |
| `offset` | `integer` | no | — | Pagination offset |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, nested user objects) |
| `relations` | `string` | no | — | Comma-separated relations to include (members,type,custom_properties,...) or 'none' to exclude all. Default: include all. |
| `fields` | `string` | no | — | Comma-separated field names to return per card. Strips everything else. Example: 'id,title,created,last_moved_to_done_at' |

**Examples**

- List cards on a board.: `kaiten cards list --board-id 10 --limit 5 --compact --json`
- Search cards by query.: `kaiten cards list --query "bug" --fields id,title,state`

### `cards.list-all`

| Field | Value |
|---|---|
| CLI command | `kaiten cards list-all` |
| MCP alias | `kaiten_list_all_cards` |
| Description | Fetch all cards matching filters with automatic pagination. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `aggregated` |
| Cache policy | `request_scope` |
| Path template | `/cards` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Full-text search query |
| `space_id` | `integer` | no | — | Filter by space ID |
| `board_id` | `integer` | no | — | Filter by board ID |
| `column_id` | `integer` | no | — | Filter by column ID |
| `lane_id` | `integer` | no | — | Filter by lane ID |
| `condition` | `integer` | no | `1`, `2` | 1=active, 2=archived |
| `type_id` | `integer` | no | — | Filter by card type ID |
| `owner_id` | `integer` | no | — | Filter by owner user ID |
| `responsible_id` | `integer` | no | — | Filter by responsible user ID |
| `tag_ids` | `string` | no | — | Comma-separated tag IDs |
| `member_ids` | `string` | no | — | Comma-separated member IDs |
| `states` | `string` | no | — | Comma-separated states (1=queued,2=inProgress,3=done) |
| `created_after` | `string` | no | — | ISO datetime filter |
| `created_before` | `string` | no | — | ISO datetime filter |
| `updated_after` | `string` | no | — | ISO datetime filter |
| `updated_before` | `string` | no | — | ISO datetime filter |
| `due_date_after` | `string` | no | — | ISO datetime filter |
| `due_date_before` | `string` | no | — | ISO datetime filter |
| `external_id` | `string` | no | — | External ID filter |
| `overdue` | `boolean` | no | — | Filter overdue cards |
| `asap` | `boolean` | no | — | Filter ASAP cards |
| `archived` | `boolean` | no | — | Include archived |
| `limit` | `integer` | no | — | Max results (default 50, max 100) |
| `offset` | `integer` | no | — | Pagination offset |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (default true for bulk) |
| `relations` | `string` | no | — | Relations to include or 'none' to exclude all nested objects (default 'none' for bulk). |
| `fields` | `string` | no | — | Comma-separated field names to return per card after pagination. |
| `owner_ids` | `string` | no | — | Comma-separated owner IDs |
| `responsible_ids` | `string` | no | — | Comma-separated responsible IDs |
| `column_ids` | `string` | no | — | Comma-separated column IDs |
| `type_ids` | `string` | no | — | Comma-separated type IDs |
| `selection` | `string` | no | `all`, `active_only`, `archived_only` | Normalized bulk selection: all, active_only, or archived_only. |
| `page_size` | `integer` | no | — | Cards per page (default 100, max 100) |
| `max_pages` | `integer` | no | — | Safety limit on pages to fetch (default 50) |

**Examples**

- Fetch all matching cards with bounded pagination.: `kaiten cards list-all --board-id 10 --page-size 20 --max-pages 2 --json`
- Fetch only active cards via normalized bulk selection.: `kaiten cards list-all --board-id 10 --selection active_only --fields id,title --json`

**Notes**

- For bulk reads, prefer selection=all|active_only|archived_only over raw archived/condition filters.
- active_only is computed as all_cards minus the archived subset to match the documented bulk CLI behavior.

### `cards.move`

| Field | Value |
|---|---|
| CLI command | `kaiten cards move` |
| MCP alias | `kaiten_move_card` |
| Description | Move a Kaiten card to a different board, column, or lane. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer|string` | yes | — | Card ID or key |
| `board_id` | `integer` | no | — | Target board ID |
| `column_id` | `integer` | no | — | Target column ID |
| `lane_id` | `integer` | no | — | Target lane ID |
| `sort_order` | `number` | no | — | Position in cell |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, nested user objects) |
| `fields` | `string` | no | — | Comma-separated field names to keep in the response. Example: 'id,title,state' |

**Examples**

- Move a card.: `kaiten cards move --card-id 123 --column-id 10 --json`

### `cards.update`

| Field | Value |
|---|---|
| CLI command | `kaiten cards update` |
| MCP alias | `kaiten_update_card` |
| Description | Update a Kaiten card. Use condition=2 to archive, set column_id/board_id to move. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer|string` | yes | — | Card ID or key |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, nested user objects) |
| `fields` | `string` | no | — | Comma-separated field names to keep in the response. Example: 'id,title,state' |
| `title` | `string` | no | — | New title |
| `description` | `string|null` | no | — | New description |
| `board_id` | `integer` | no | — | Move to board |
| `column_id` | `integer` | no | — | Move to column |
| `lane_id` | `integer` | no | — | Move to lane |
| `sort_order` | `number` | no | — | Position in cell |
| `owner_id` | `integer` | no | — | New owner user ID |
| `type_id` | `integer` | no | — | Card type ID |
| `condition` | `integer` | no | `1`, `2` | 1=active, 2=archived |
| `due_date` | `string|null` | no | — | Deadline (ISO 8601 or null) |
| `asap` | `boolean` | no | — | ASAP marker |
| `size_text` | `string|null` | no | — | Size |
| `blocked` | `boolean` | no | — | Set to false to unblock |
| `external_id` | `string|null` | no | — | External ID |
| `properties` | `object` | no | — | Custom properties as {id_N: value} |
| `sprint_id` | `integer|null` | no | — | Sprint ID (null to remove) |
| `planned_start` | `string|null` | no | — | Planned start date (ISO 8601) |
| `planned_end` | `string|null` | no | — | Planned end date (ISO 8601) |
| `state` | `integer` | no | `1`, `2`, `3` | Card state: 1=queued, 2=inProgress, 3=done |
| `block_reason` | `string|null` | no | — | Block reason text (null to clear) |
| `locked` | `string|null` | no | — | Lock identifier (null to unlock) |
| `due_date_time_present` | `boolean` | no | — | True if due_date includes time component |
| `expires_later` | `boolean` | no | — | Expires later flag |
| `estimate_workload` | `integer` | no | — | Estimated workload in minutes (resource planning) |
| `child_card_ids` | `array` | no | — | Child card IDs to link |
| `parent_card_ids` | `array` | no | — | Parent card IDs to link |

**Examples**

- Update a card.: `kaiten cards update --card-id 123 --title "Renamed"`
- Update a card with a narrow response.: `kaiten cards update --card-id 123 --title "Renamed" --compact --fields id,title,state --json`

<a id="module-comments"></a>
## Комментарии (`comments`) — 5 commands

Комментарии карточек и comment-heavy reads.

**Namespace tree**

```text
comments
  batch-list
  create
  delete
  list
  update
```

### `comments.batch-list`

| Field | Value |
|---|---|
| CLI command | `kaiten comments batch-list` |
| MCP alias | `kaiten_batch_list_comments` |
| Description | Fetch comments for multiple cards with bounded worker concurrency. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `aggregated` |
| Cache policy | `request_scope` |
| Path template | `/cards/comments/batch` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_ids` | `array` | yes | — | Card IDs to inspect |
| `workers` | `integer` | no | — | Parallel workers (default 2, max 6) |
| `compact` | `boolean` | no | — | Strip heavy fields from comment payloads |
| `fields` | `string` | no | — | Comma-separated field names to keep for each comment |

**Examples**

- Fetch comments for several cards in one CLI call.: `kaiten comments batch-list --card-ids '[1,2,3]' --json`
- Fetch narrowed comment payloads with bounded concurrency.: `kaiten comments batch-list --card-ids '[1,2,3]' --workers 2 --compact --fields id,text --json`

**Notes**

- The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.
- Use this bulk path when you need comment evidence across many cards.

### `comments.create`

| Field | Value |
|---|---|
| CLI command | `kaiten comments create` |
| MCP alias | `kaiten_create_comment` |
| Description | Add a comment to a card. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/comments` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card to comment on. |
| `text` | `string` | yes | — | Comment text. For format=html send HTML content. |
| `format` | `string` | no | `markdown`, `html` | Comment format. 'markdown' (default) stores raw markdown, 'html' switches the request to HTML mode. |
| `internal` | `boolean` | no | — | Mark the comment as internal (visible only to team). |

**Examples**

- Create a markdown comment.: `kaiten comments create --card-id 10 --text "Looks good" --json`

### `comments.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten comments delete` |
| MCP alias | `kaiten_delete_comment` |
| Description | Delete a comment from a card (author only). |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/comments/{comment_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card. |
| `comment_id` | `integer` | yes | — | ID of the comment to delete. |

**Examples**

- Delete a comment.: `kaiten comments delete --card-id 10 --comment-id 20 --json`

### `comments.list`

| Field | Value |
|---|---|
| CLI command | `kaiten comments list` |
| MCP alias | `kaiten_list_comments` |
| Description | List all comments on a card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/comments` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card whose comments to list. |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, nested user objects). |

**Examples**

- List comments on a card.: `kaiten comments list --card-id 10 --compact --json`

**Notes**

- Bulk alternative: `comments.batch-list`
- This is a per-card read and becomes expensive when repeated across large card populations.
- For report and investigation workflows, prefer comments.batch-list over one-card-at-a-time loops.

### `comments.update`

| Field | Value |
|---|---|
| CLI command | `kaiten comments update` |
| MCP alias | `kaiten_update_comment` |
| Description | Update a comment on a card (author only). |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/comments/{comment_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card. |
| `comment_id` | `integer` | yes | — | ID of the comment to update. |
| `text` | `string` | yes | — | New comment text. For format=html send HTML content. |
| `format` | `string` | no | `markdown`, `html` | Comment format. 'html' switches the request to HTML mode, 'markdown' switches back to markdown. |

**Examples**

- Update a comment.: `kaiten comments update --card-id 10 --comment-id 20 --text "Updated" --json`

<a id="module-members"></a>
## Участники и пользователи (`members`) — 5 commands

Участники карточек, пользователи, группы и space users.

**Namespace tree**

```text
card-members
  add
  list
  remove
users
  current
  list
```

### `card-members.add`

| Field | Value |
|---|---|
| CLI command | `kaiten card-members add` |
| MCP alias | `kaiten_add_card_member` |
| Description | Add a member to a card. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/members` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card. |
| `user_id` | `integer` | yes | — | ID of the user to add as a member. |

**Examples**

- Add a member to a card.: `kaiten card-members add --card-id 10 --user-id 7 --json`

### `card-members.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-members list` |
| MCP alias | `kaiten_list_card_members` |
| Description | List all members assigned to a card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/members` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card. |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, etc.). |

**Examples**

- List members on a card.: `kaiten card-members list --card-id 10 --compact --json`

### `card-members.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten card-members remove` |
| MCP alias | `kaiten_remove_card_member` |
| Description | Remove a member from a card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/members/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card. |
| `user_id` | `integer` | yes | — | ID of the user to remove. |

**Examples**

- Remove a member from a card.: `kaiten card-members remove --card-id 10 --user-id 7 --json`

### `users.current`

| Field | Value |
|---|---|
| CLI command | `kaiten users current` |
| MCP alias | `kaiten_get_current_user` |
| Description | Get the current authenticated Kaiten user profile. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/users/current` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- Get the current user.: `kaiten users current --json`

### `users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten users list` |
| MCP alias | `kaiten_list_users` |
| Description | List company users. Supports search, pagination, and filtering inactive users. Response includes: last_request_date, activated, role, created. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/users` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Search filter for user names or emails. |
| `limit` | `integer` | no | — | Maximum number of users to return (default 50). |
| `offset` | `integer` | no | — | Number of users to skip (for pagination). |
| `include_inactive` | `boolean` | no | — | Include inactive (deactivated) users in results. |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, etc.). |

**Examples**

- Search users by name.: `kaiten users list --query "alice" --compact --json`

<a id="module-time-logs"></a>
## Логи времени (`time_logs`) — 5 commands

Time logs, work logs и related analytics inputs.

**Namespace tree**

```text
time-logs
  batch-list
  create
  delete
  list
  update
```

### `time-logs.batch-list`

| Field | Value |
|---|---|
| CLI command | `kaiten time-logs batch-list` |
| MCP alias | `kaiten_batch_list_time_logs` |
| Description | Fetch time logs for multiple cards with bounded worker concurrency. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `aggregated` |
| Cache policy | `request_scope` |
| Path template | `/cards/time-logs/batch` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_ids` | `array` | yes | — | Card IDs to inspect |
| `workers` | `integer` | no | — | Parallel workers (default 2, max 6) |
| `for_date` | `string` | no | — | Optional YYYY-MM-DD filter passed to each per-card request. |
| `personal` | `boolean` | no | — | Only include the current user's time logs. |
| `compact` | `boolean` | no | — | Strip heavy nested fields from time-log payloads |
| `fields` | `string` | no | — | Comma-separated field names to keep for each time log |

**Examples**

- Fetch time logs for several cards in one CLI call.: `kaiten time-logs batch-list --card-ids '[1,2,3]' --json`
- Fetch narrowed time-log payloads with bounded concurrency.: `kaiten time-logs batch-list --card-ids '[1,2,3]' --workers 2 --fields id,time_spent,for_date --json`

**Notes**

- The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.
- Use this bulk path for work-log analytics and snapshot builds instead of repeating time-logs.list for every card.

### `time-logs.create`

| Field | Value |
|---|---|
| CLI command | `kaiten time-logs create` |
| MCP alias | `kaiten_create_time_log` |
| Description | Log time spent on a card. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/time-logs` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card. |
| `time_spent` | `integer` | yes | — | Time spent in minutes (minimum 1). |
| `role_id` | `integer` | no | — | Role ID for the time log. Use -1 for the default role. |
| `for_date` | `string` | no | — | Date for the time log (YYYY-MM-DD). Defaults to today. |
| `comment` | `string` | no | — | Optional comment for the time log. |

**Examples**

- Create a time log entry.: `kaiten time-logs create --card-id 10 --time-spent 15 --comment "Analysis" --json`

### `time-logs.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten time-logs delete` |
| MCP alias | `kaiten_delete_time_log` |
| Description | Delete a time log entry from a card (author only). |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/time-logs/{time_log_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card. |
| `time_log_id` | `integer` | yes | — | ID of the time log to delete. |

**Examples**

- Delete a time log.: `kaiten time-logs delete --card-id 10 --time-log-id 20 --json`

### `time-logs.list`

| Field | Value |
|---|---|
| CLI command | `kaiten time-logs list` |
| MCP alias | `kaiten_list_card_time_logs` |
| Description | List time logs for a card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/time-logs` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card. |
| `for_date` | `string` | no | — | Filter by date (YYYY-MM-DD). |
| `personal` | `boolean` | no | — | Return only the current user's time logs. |
| `compact` | `boolean` | no | — | Strip heavy nested fields from time-log payloads. |
| `fields` | `string` | no | — | Comma-separated field names to keep for each time log. |

**Examples**

- List time logs on a card.: `kaiten time-logs list --card-id 10 --json`

**Notes**

- Bulk alternative: `time-logs.batch-list`
- This is a per-card read and becomes expensive when repeated across large card populations.
- For analytics snapshots and work-log investigations, prefer time-logs.batch-list over one-card-at-a-time loops.

### `time-logs.update`

| Field | Value |
|---|---|
| CLI command | `kaiten time-logs update` |
| MCP alias | `kaiten_update_time_log` |
| Description | Update a time log entry on a card (author only). |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/time-logs/{time_log_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card. |
| `time_log_id` | `integer` | yes | — | ID of the time log to update. |
| `time_spent` | `integer` | no | — | Updated time spent in minutes. |
| `role_id` | `integer` | no | — | Updated role ID. |
| `comment` | `string` | no | — | Updated comment. |
| `for_date` | `string` | no | — | Updated date (YYYY-MM-DD). |

**Examples**

- Update a time log.: `kaiten time-logs update --card-id 10 --time-log-id 20 --time-spent 20 --json`

<a id="module-tags"></a>
## Теги (`tags`) — 6 commands

Теги и операции привязки тегов к карточкам.

**Namespace tree**

```text
card-tags
  add
  remove
tags
  create
  delete
  list
  update
```

### `card-tags.add`

| Field | Value |
|---|---|
| CLI command | `kaiten card-tags add` |
| MCP alias | `kaiten_add_card_tag` |
| Description | Add a tag to a Kaiten card by name. Creates the tag if it doesn't exist. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/tags` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `name` | `string` | yes | — | Tag name (1-255 chars) |

**Examples**

- Add a tag to a card.: `kaiten card-tags add --card-id 10 --name "backend" --json`

### `card-tags.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten card-tags remove` |
| MCP alias | `kaiten_remove_card_tag` |
| Description | Remove a tag from a Kaiten card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/tags/{tag_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `tag_id` | `integer` | yes | — | Tag ID |

**Examples**

- Remove a tag from a card.: `kaiten card-tags remove --card-id 10 --tag-id 20 --json`

### `tags.create`

| Field | Value |
|---|---|
| CLI command | `kaiten tags create` |
| MCP alias | `kaiten_create_tag` |
| Description | Create a new Kaiten tag. Color is assigned randomly by the server (1-17). |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/tags` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Tag name (1-255 chars, must be unique within the company) |

**Examples**

- Create a company tag.: `kaiten tags create --name "backend" --json`

### `tags.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten tags delete` |
| MCP alias | `kaiten_delete_tag` |
| Description | Delete a Kaiten tag. Requires company tag management permission. May be blocked if an async operation is in progress. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/tags/{tag_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `tag_id` | `integer` | yes | — | Tag ID |

**Examples**

- Delete a company tag.: `kaiten tags delete --tag-id 10 --json`

### `tags.list`

| Field | Value |
|---|---|
| CLI command | `kaiten tags list` |
| MCP alias | `kaiten_list_tags` |
| Description | List Kaiten tags. Note: API may return empty for company-level tags; tags are primarily card-scoped. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/tags` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Search filter (matches by name) |
| `space_id` | `integer` | no | — | Filter tags by space (only tags used on cards in this space) |
| `ids` | `string` | no | — | Comma-separated tag IDs to fetch specific tags |
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- Search tags by name.: `kaiten tags list --query "backend" --json`

### `tags.update`

| Field | Value |
|---|---|
| CLI command | `kaiten tags update` |
| MCP alias | `kaiten_update_tag` |
| Description | Update a Kaiten tag (name and/or color). Requires company tag management permission. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/tags/{tag_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `tag_id` | `integer` | yes | — | Tag ID |
| `name` | `string` | no | — | New tag name (1-255 chars) |
| `color` | `integer` | no | — | Color index (1-17) |

**Examples**

- Update a company tag.: `kaiten tags update --tag-id 10 --name "backend" --json`

<a id="module-checklists"></a>
## Чеклисты (`checklists`) — 8 commands

Чеклисты и checklist items.

**Namespace tree**

```text
checklist-items
  create
  delete
  list
  update
checklists
  create
  delete
  list
  update
```

### `checklist-items.create`

| Field | Value |
|---|---|
| CLI command | `kaiten checklist-items create` |
| MCP alias | `kaiten_create_checklist_item` |
| Description | Create an item in a checklist on a Kaiten card. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/checklists/{checklist_id}/items` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `checklist_id` | `integer` | yes | — | Checklist ID |
| `text` | `string` | yes | — | Item text |
| `checked` | `boolean` | no | — | Whether the item is checked |
| `sort_order` | `number` | no | — | Sort order |
| `user_id` | `integer` | no | — | Assigned user ID |
| `due_date` | `string` | no | — | Due date (ISO 8601 format) |

**Examples**

- Create a checklist item.: `kaiten checklist-items create --card-id 10 --checklist-id 20 --text "Ship it" --json`

### `checklist-items.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten checklist-items delete` |
| MCP alias | `kaiten_delete_checklist_item` |
| Description | Delete an item from a checklist on a Kaiten card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/checklists/{checklist_id}/items/{item_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `checklist_id` | `integer` | yes | — | Checklist ID |
| `item_id` | `integer` | yes | — | Checklist item ID |

**Examples**

- Delete a checklist item.: `kaiten checklist-items delete --card-id 10 --checklist-id 20 --item-id 30 --json`

### `checklist-items.list`

| Field | Value |
|---|---|
| CLI command | `kaiten checklist-items list` |
| MCP alias | `kaiten_list_checklist_items` |
| Description | List all items in a checklist on a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/checklists/{checklist_id}/items` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `checklist_id` | `integer` | yes | — | Checklist ID |

**Examples**

- List checklist items.: `kaiten checklist-items list --card-id 10 --checklist-id 20 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `405`
- Live note: Sandbox returns 405 for checklist item listing; the live suite validates the expected error path.

### `checklist-items.update`

| Field | Value |
|---|---|
| CLI command | `kaiten checklist-items update` |
| MCP alias | `kaiten_update_checklist_item` |
| Description | Update an item in a checklist on a Kaiten card. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/checklists/{checklist_id}/items/{item_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `checklist_id` | `integer` | yes | — | Checklist ID |
| `item_id` | `integer` | yes | — | Checklist item ID |
| `text` | `string` | no | — | Item text |
| `checked` | `boolean` | no | — | Whether the item is checked |
| `sort_order` | `number` | no | — | Sort order |
| `user_id` | `integer` | no | — | Assigned user ID |
| `due_date` | `string` | no | — | Due date (ISO 8601 format) |

**Examples**

- Update a checklist item.: `kaiten checklist-items update --card-id 10 --checklist-id 20 --item-id 30 --checked --json`

### `checklists.create`

| Field | Value |
|---|---|
| CLI command | `kaiten checklists create` |
| MCP alias | `kaiten_create_checklist` |
| Description | Create a checklist on a Kaiten card. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/checklists` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `name` | `string` | yes | — | Checklist name |
| `sort_order` | `number` | no | — | Sort order |

**Examples**

- Create a checklist.: `kaiten checklists create --card-id 10 --name "Ready for QA" --json`

### `checklists.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten checklists delete` |
| MCP alias | `kaiten_delete_checklist` |
| Description | Delete a checklist from a Kaiten card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/checklists/{checklist_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `checklist_id` | `integer` | yes | — | Checklist ID |

**Examples**

- Delete a checklist.: `kaiten checklists delete --card-id 10 --checklist-id 20 --json`

### `checklists.list`

| Field | Value |
|---|---|
| CLI command | `kaiten checklists list` |
| MCP alias | `kaiten_list_checklists` |
| Description | List all checklists on a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/checklists` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |

**Examples**

- List checklists on a card.: `kaiten checklists list --card-id 10 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `405`
- Live note: Sandbox returns 405 for checklist listing; the live suite validates the expected error path.

### `checklists.update`

| Field | Value |
|---|---|
| CLI command | `kaiten checklists update` |
| MCP alias | `kaiten_update_checklist` |
| Description | Update a checklist on a Kaiten card. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/checklists/{checklist_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `checklist_id` | `integer` | yes | — | Checklist ID |
| `name` | `string` | no | — | Checklist name |
| `sort_order` | `number` | no | — | Sort order |

**Examples**

- Update a checklist.: `kaiten checklists update --card-id 10 --checklist-id 20 --name "Ready for QA" --json`

<a id="module-blockers"></a>
## Блокировки (`blockers`) — 5 commands

Блокировки карточек и blocker relations.

**Namespace tree**

```text
blockers
  create
  delete
  get
  list
  update
```

### `blockers.create`

| Field | Value |
|---|---|
| CLI command | `kaiten blockers create` |
| MCP alias | `kaiten_create_card_blocker` |
| Description | Create a blocker on a card. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/blockers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card to add a blocker to. |
| `reason` | `string` | no | — | Reason for the blocker. |
| `blocker_card_id` | `integer` | no | — | ID of the card that blocks this one. |

**Examples**

- Create a blocker on a card.: `kaiten blockers create --card-id 10 --reason "Waiting for review" --json`

### `blockers.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten blockers delete` |
| MCP alias | `kaiten_delete_card_blocker` |
| Description | Delete a blocker from a card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/blockers/{blocker_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card. |
| `blocker_id` | `integer` | yes | — | ID of the blocker to delete. |

**Examples**

- Delete a blocker.: `kaiten blockers delete --card-id 10 --blocker-id 20 --json`

### `blockers.get`

| Field | Value |
|---|---|
| CLI command | `kaiten blockers get` |
| MCP alias | `kaiten_get_card_blocker` |
| Description | Get a specific blocker on a card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `custom` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/blockers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card. |
| `blocker_id` | `integer` | yes | — | ID of the blocker to retrieve. |

**Examples**

- Get a blocker by filtering the blocker list.: `kaiten blockers get --card-id 10 --blocker-id 20 --json`

### `blockers.list`

| Field | Value |
|---|---|
| CLI command | `kaiten blockers list` |
| MCP alias | `kaiten_list_card_blockers` |
| Description | List all blockers on a card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/blockers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card whose blockers to list. |

**Examples**

- List blockers on a card.: `kaiten blockers list --card-id 10 --json`

### `blockers.update`

| Field | Value |
|---|---|
| CLI command | `kaiten blockers update` |
| MCP alias | `kaiten_update_card_blocker` |
| Description | Update a blocker on a card. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/blockers/{blocker_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the card. |
| `blocker_id` | `integer` | yes | — | ID of the blocker to update. |
| `reason` | `string` | no | — | New reason for the blocker. |

**Examples**

- Update a blocker.: `kaiten blockers update --card-id 10 --blocker-id 20 --reason "Waiting for review" --json`

<a id="module-card-relations"></a>
## Связи карточек (`card_relations`) — 10 commands

Parent/child/planned relations between cards.

**Namespace tree**

```text
card-children
  add
  batch-list
  list
  remove
card-parents
  add
  list
  remove
planned-relations
  add
  remove
  update
```

### `card-children.add`

| Field | Value |
|---|---|
| CLI command | `kaiten card-children add` |
| MCP alias | `kaiten_add_card_child` |
| Description | Add a child card to a given card. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/children` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the parent card. |
| `child_card_id` | `integer` | yes | — | ID of the card to add as a child. |

**Examples**

- Add a child card relation.: `kaiten card-children add --card-id 10 --child-card-id 11 --json`

### `card-children.batch-list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-children batch-list` |
| MCP alias | `kaiten_batch_list_card_children` |
| Description | Fetch child-card relations for multiple parent cards with bounded worker concurrency. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `aggregated` |
| Cache policy | `request_scope` |
| Path template | `/cards/children/batch` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_ids` | `array` | yes | — | Parent card IDs to inspect |
| `workers` | `integer` | no | — | Parallel workers (default 2, max 6) |
| `compact` | `boolean` | no | — | Strip heavy nested fields from child card payloads |
| `fields` | `string` | no | — | Comma-separated field names to keep for each child card |

**Examples**

- Fetch child-card relations for several parent cards.: `kaiten card-children batch-list --card-ids '[1,2,3]' --json`
- Fetch narrowed child-card payloads with bounded concurrency.: `kaiten card-children batch-list --card-ids '[1,2,3]' --workers 2 --compact --fields id,title --json`

**Notes**

- The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.
- Use this bulk path for relation-heavy investigations instead of per-parent card-children.list loops.

### `card-children.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-children list` |
| MCP alias | `kaiten_list_card_children` |
| Description | List all child cards of a given card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/children` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the parent card. |

**Examples**

- List child cards.: `kaiten card-children list --card-id 10 --json`

**Notes**

- Bulk alternative: `card-children.batch-list`
- This is a per-card read and becomes expensive when repeated across many parent cards.
- For investigation and reporting workflows, prefer card-children.batch-list over one-card-at-a-time loops.

### `card-children.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten card-children remove` |
| MCP alias | `kaiten_remove_card_child` |
| Description | Remove a child card from a given card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/children/{child_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the parent card. |
| `child_id` | `integer` | yes | — | ID of the child card to remove. |

**Examples**

- Remove a child card relation.: `kaiten card-children remove --card-id 10 --child-id 11 --json`

### `card-parents.add`

| Field | Value |
|---|---|
| CLI command | `kaiten card-parents add` |
| MCP alias | `kaiten_add_card_parent` |
| Description | Add a parent card to a given card. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/parents` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the child card. |
| `parent_card_id` | `integer` | yes | — | ID of the card to add as a parent. |

**Examples**

- Add a parent card relation.: `kaiten card-parents add --card-id 10 --parent-card-id 11 --json`

### `card-parents.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-parents list` |
| MCP alias | `kaiten_list_card_parents` |
| Description | List all parent cards of a given card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/parents` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the child card. |

**Examples**

- List parent cards.: `kaiten card-parents list --card-id 10 --json`

### `card-parents.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten card-parents remove` |
| MCP alias | `kaiten_remove_card_parent` |
| Description | Remove a parent card from a given card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/parents/{parent_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the child card. |
| `parent_id` | `integer` | yes | — | ID of the parent card to remove. |

**Examples**

- Remove a parent card relation.: `kaiten card-parents remove --card-id 10 --parent-id 11 --json`

### `planned-relations.add`

| Field | Value |
|---|---|
| CLI command | `kaiten planned-relations add` |
| MCP alias | `kaiten_add_planned_relation` |
| Description | Create a planned relation (successor link) between two cards on Timeline/Gantt. The source card becomes a predecessor and the target card becomes its successor. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/planned-relation` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the source (predecessor) card. |
| `target_card_id` | `integer` | yes | — | ID of the target (successor) card. |
| `type` | `string` | no | `end-start` | Relation type. Defaults to 'end-start'. |

**Examples**

- Create a finish-to-start planned relation.: `kaiten planned-relations add --card-id 10 --target-card-id 11 --json`

### `planned-relations.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten planned-relations remove` |
| MCP alias | `kaiten_remove_planned_relation` |
| Description | Remove a planned relation (successor link) between two cards. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/planned-relation/{target_card_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the source (predecessor) card. |
| `target_card_id` | `integer` | yes | — | ID of the target (successor) card to unlink. |

**Examples**

- Remove a planned relation.: `kaiten planned-relations remove --card-id 10 --target-card-id 11 --json`

### `planned-relations.update`

| Field | Value |
|---|---|
| CLI command | `kaiten planned-relations update` |
| MCP alias | `kaiten_update_planned_relation` |
| Description | Update the lag/lead gap of a planned relation between two cards. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/planned-relation/{target_card_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | ID of the source (predecessor) card. |
| `target_card_id` | `integer` | yes | — | ID of the target (successor) card. |
| `gap` | `integer|null` | yes | — | Distance between cards (-1000..1000). Positive = lag, negative = lead. null to clear. |
| `gap_type` | `string|null` | yes | `hours`, `days` | Unit of the gap: 'hours', 'days', or null to clear. |

**Examples**

- Set a 2-day lag for a planned relation.: `kaiten planned-relations update --card-id 10 --target-card-id 11 --gap 2 --gap-type days --json`

<a id="module-external-links"></a>
## Внешние ссылки (`external_links`) — 4 commands

External links attached to cards.

**Namespace tree**

```text
external-links
  create
  delete
  list
  update
```

### `external-links.create`

| Field | Value |
|---|---|
| CLI command | `kaiten external-links create` |
| MCP alias | `kaiten_create_external_link` |
| Description | Create an external link on a Kaiten card. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/external-links` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `url` | `string` | yes | — | URL of the external link |
| `description` | `string` | no | — | Description of the external link |

**Examples**

- Attach an external link to a card.: `kaiten external-links create --card-id 10 --url "https://example.com" --json`

### `external-links.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten external-links delete` |
| MCP alias | `kaiten_delete_external_link` |
| Description | Delete an external link from a Kaiten card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/external-links/{link_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `link_id` | `integer` | yes | — | External link ID |

**Examples**

- Delete a card external link.: `kaiten external-links delete --card-id 10 --link-id 20 --json`

### `external-links.list`

| Field | Value |
|---|---|
| CLI command | `kaiten external-links list` |
| MCP alias | `kaiten_list_external_links` |
| Description | List all external links on a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/external-links` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |

**Examples**

- List external links on a card.: `kaiten external-links list --card-id 10 --json`

### `external-links.update`

| Field | Value |
|---|---|
| CLI command | `kaiten external-links update` |
| MCP alias | `kaiten_update_external_link` |
| Description | Update an external link on a Kaiten card. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/external-links/{link_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `link_id` | `integer` | yes | — | External link ID |
| `url` | `string` | no | — | URL of the external link |
| `description` | `string` | no | — | Description of the external link |

**Examples**

- Update a card external link.: `kaiten external-links update --card-id 10 --link-id 20 --description "Spec" --json`

<a id="module-files"></a>
## Файлы карточек (`files`) — 4 commands

Файлы и вложения карточек.

**Namespace tree**

```text
files
  create
  delete
  list
  update
```

### `files.create`

| Field | Value |
|---|---|
| CLI command | `kaiten files create` |
| MCP alias | `kaiten_create_card_file` |
| Description | Create a file attachment on a card by URL. This registers an external file link as a card attachment (does not upload binary data). File types: 1=attachment, 2=googleDrive, 3=dropBox, 4=box, 5=oneDrive, 6=yandexDisk. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/files` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID. |
| `url` | `string` | yes | — | URL of the file. |
| `name` | `string` | yes | — | Display name of the file. |
| `type` | `integer` | no | `1`, `2`, `3`, `4`, `5`, `6` | File type: 1=attachment, 2=googleDrive, 3=dropBox, 4=box, 5=oneDrive, 6=yandexDisk. |
| `size` | `integer` | no | — | File size in bytes. |
| `sort_order` | `number` | no | — | Sort order of the file in the list. |
| `custom_property_id` | `integer` | no | — | Custom property ID to associate the file with. |
| `card_cover` | `boolean` | no | — | Set this file as the card cover image. |

**Examples**

- Attach a URL-backed file to a card.: `kaiten files create --card-id 10 --url "https://example.com/a.png" --name "a.png" --json`

### `files.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten files delete` |
| MCP alias | `kaiten_delete_card_file` |
| Description | Delete a file attachment from a card. Files on blocked cards cannot be deleted. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID. |
| `file_id` | `integer` | yes | — | File ID. |

**Examples**

- Delete a card file.: `kaiten files delete --card-id 10 --file-id 20 --json`

### `files.list`

| Field | Value |
|---|---|
| CLI command | `kaiten files list` |
| MCP alias | `kaiten_list_card_files` |
| Description | List all file attachments on a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/files` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID. |

**Examples**

- List card files.: `kaiten files list --card-id 10 --json`

### `files.update`

| Field | Value |
|---|---|
| CLI command | `kaiten files update` |
| MCP alias | `kaiten_update_card_file` |
| Description | Update a file attachment on a card (name, URL, sort order, cover, etc.). |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID. |
| `file_id` | `integer` | yes | — | File ID. |
| `url` | `string` | no | — | New URL of the file. |
| `name` | `string` | no | — | New display name. |
| `type` | `integer` | no | `1`, `2`, `3`, `4`, `5`, `6` | File type: 1=attachment, 2=googleDrive, 3=dropBox, 4=box, 5=oneDrive, 6=yandexDisk. |
| `size` | `integer` | no | — | File size in bytes. |
| `sort_order` | `number` | no | — | Sort order of the file in the list. |
| `custom_property_id` | `integer` | no | — | Custom property ID to associate the file with. |
| `card_cover` | `boolean` | no | — | Set this file as the card cover image. |

**Examples**

- Update a card file attachment.: `kaiten files update --card-id 10 --file-id 20 --name "a-v2.png" --json`

<a id="module-subscribers"></a>
## Подписчики (`subscribers`) — 6 commands

Подписки на карточки и колонки.

**Namespace tree**

```text
card-subscribers
  add
  list
  remove
column-subscribers
  add
  list
  remove
```

### `card-subscribers.add`

| Field | Value |
|---|---|
| CLI command | `kaiten card-subscribers add` |
| MCP alias | `kaiten_add_card_subscriber` |
| Description | Add a subscriber to a Kaiten card. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/subscribers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `user_id` | `integer` | yes | — | User ID to subscribe |

**Examples**

- Add a card subscriber.: `kaiten card-subscribers add --card-id 10 --user-id 7 --json`

### `card-subscribers.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-subscribers list` |
| MCP alias | `kaiten_list_card_subscribers` |
| Description | List all subscribers of a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/subscribers` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `compact` | `boolean` | no | — | Return compact response without heavy fields. |

**Examples**

- List card subscribers.: `kaiten card-subscribers list --card-id 10 --compact --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `405`
- Live note: Sandbox returns 405 for card subscriber listing; the live suite validates the expected error path.

### `card-subscribers.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten card-subscribers remove` |
| MCP alias | `kaiten_remove_card_subscriber` |
| Description | Remove a subscriber from a Kaiten card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/subscribers/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `user_id` | `integer` | yes | — | User ID to unsubscribe |

**Examples**

- Remove a card subscriber.: `kaiten card-subscribers remove --card-id 10 --user-id 7 --json`

### `column-subscribers.add`

| Field | Value |
|---|---|
| CLI command | `kaiten column-subscribers add` |
| MCP alias | `kaiten_add_column_subscriber` |
| Description | Add a subscriber to a Kaiten column. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/columns/{column_id}/subscribers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `column_id` | `integer` | yes | — | Column ID |
| `user_id` | `integer` | yes | — | User ID to subscribe |
| `type` | `integer` | no | — | Subscription type (1=all, 2=mentions only). |

**Examples**

- Add a column subscriber.: `kaiten column-subscribers add --column-id 10 --user-id 7 --json`

### `column-subscribers.list`

| Field | Value |
|---|---|
| CLI command | `kaiten column-subscribers list` |
| MCP alias | `kaiten_list_column_subscribers` |
| Description | List all subscribers of a Kaiten column. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/columns/{column_id}/subscribers` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `column_id` | `integer` | yes | — | Column ID |
| `compact` | `boolean` | no | — | Return compact response without heavy fields. |

**Examples**

- List column subscribers.: `kaiten column-subscribers list --column-id 10 --compact --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `405`
- Live note: Sandbox returns 405 for column subscriber listing; the live suite validates the expected error path.

### `column-subscribers.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten column-subscribers remove` |
| MCP alias | `kaiten_remove_column_subscriber` |
| Description | Remove a subscriber from a Kaiten column. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/columns/{column_id}/subscribers/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `column_id` | `integer` | yes | — | Column ID |
| `user_id` | `integer` | yes | — | User ID to unsubscribe |

**Examples**

- Remove a column subscriber.: `kaiten column-subscribers remove --column-id 10 --user-id 7 --json`

<a id="module-spaces"></a>
## Пространства (`spaces`) — 6 commands

Spaces and top-level workspace reads.

**Namespace tree**

```text
space-topology
  get
spaces
  create
  delete
  get
  list
  update
```

### `space-topology.get`

| Field | Value |
|---|---|
| CLI command | `kaiten space-topology get` |
| MCP alias | `kaiten_get_space_topology` |
| Description | Fetch boards with their columns and lanes for a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `aggregated` |
| Cache policy | `request_scope` |
| Path template | `/spaces/{space_id}/topology` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |

**Examples**

- Fetch board topology for a space.: `kaiten space-topology get --space-id 123 --json`

**Notes**

- Use this for report scaffolding instead of separate boards.list, columns.list, and lanes.list loops.

### `spaces.create`

| Field | Value |
|---|---|
| CLI command | `kaiten spaces create` |
| MCP alias | `kaiten_create_space` |
| Description | Create a new Kaiten space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `title` | `string` | yes | — | Space title |
| `description` | `string` | no | — | Space description |
| `access` | `string` | no | `for_everyone`, `by_invite` | Access type (default: for_everyone) |
| `external_id` | `string` | no | — | External ID |
| `parent_entity_uid` | `string` | no | — | Parent entity UID for nesting spaces |
| `sort_order` | `number` | no | — | Sort order |

**Examples**

- Create a space.: `kaiten spaces create --title "CLI smoke"`

### `spaces.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten spaces delete` |
| MCP alias | `kaiten_delete_space` |
| Description | Delete a Kaiten space. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |

**Examples**

- Delete a space.: `kaiten spaces delete --space-id 123`

### `spaces.get`

| Field | Value |
|---|---|
| CLI command | `kaiten spaces get` |
| MCP alias | `kaiten_get_space` |
| Description | Get a Kaiten space by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/spaces/{space_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |

**Examples**

- Get a space by ID.: `kaiten spaces get --space-id 123`

### `spaces.list`

| Field | Value |
|---|---|
| CLI command | `kaiten spaces list` |
| MCP alias | `kaiten_list_spaces` |
| Description | List all Kaiten spaces. Returns array of space objects with id, title, description, access type. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/spaces` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `archived` | `boolean` | no | — | Include archived spaces |
| `fields` | `string` | no | — | Comma-separated field names to keep in the response. Example: 'id,title' |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, nested user objects) |

**Examples**

- List spaces as machine-readable JSON.: `kaiten spaces list --json`
- List spaces with a narrow response surface.: `kaiten spaces list --compact --fields id,title --json`

### `spaces.update`

| Field | Value |
|---|---|
| CLI command | `kaiten spaces update` |
| MCP alias | `kaiten_update_space` |
| Description | Update a Kaiten space. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `title` | `string` | no | — | New title |
| `description` | `string` | no | — | New description |
| `access` | `string` | no | `for_everyone`, `by_invite` | Access type |
| `external_id` | `string` | no | — | External ID |
| `parent_entity_uid` | `string` | no | — | Parent entity UID for nesting spaces |
| `sort_order` | `number` | no | — | Sort order |

**Examples**

- Update a space.: `kaiten spaces update --space-id 123 --title "Updated"`

<a id="module-boards"></a>
## Доски (`boards`) — 5 commands

Boards and board-level operations.

**Namespace tree**

```text
boards
  create
  delete
  get
  list
  update
```

### `boards.create`

| Field | Value |
|---|---|
| CLI command | `kaiten boards create` |
| MCP alias | `kaiten_create_board` |
| Description | Create a new board in a Kaiten space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/boards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `title` | `string` | yes | — | Board title |
| `description` | `string` | no | — | Board description |
| `external_id` | `string` | no | — | External ID |
| `top` | `number` | no | — | Top position (px) |
| `left` | `number` | no | — | Left position (px) |
| `sort_order` | `number` | no | — | Sort order |
| `default_card_type_id` | `integer` | no | — | Default card type ID for new cards |

**Examples**

- Create a board.: `kaiten boards create --space-id 1 --title "Smoke"`

### `boards.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten boards delete` |
| MCP alias | `kaiten_delete_board` |
| Description | Delete a Kaiten board. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/boards/{board_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `board_id` | `integer` | yes | — | Board ID |
| `force` | `boolean` | no | — | Force deletion when the board contains child entities |

**Examples**

- Delete a board.: `kaiten boards delete --space-id 1 --board-id 10 --force`

**Notes**

- Live contract: `live_passed_with_runtime_fix`; expected statuses: —
- Live note: Sandbox requires the force flag for board deletion; the CLI injects the live-safe request shape.

### `boards.get`

| Field | Value |
|---|---|
| CLI command | `kaiten boards get` |
| MCP alias | `kaiten_get_board` |
| Description | Get a Kaiten board by ID. Returns board with columns and lanes. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/boards/{board_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `board_id` | `integer` | yes | — | Board ID |

**Examples**

- Get a board.: `kaiten boards get --board-id 10`

### `boards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten boards list` |
| MCP alias | `kaiten_list_boards` |
| Description | List boards in a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/spaces/{space_id}/boards` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `fields` | `string` | no | — | Comma-separated field names to keep in the response. Example: 'id,title' |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, nested user objects) |

**Examples**

- List boards in a space.: `kaiten boards list --space-id 1 --compact`
- List boards with narrow fields.: `kaiten boards list --space-id 1 --fields id,title --json`

### `boards.update`

| Field | Value |
|---|---|
| CLI command | `kaiten boards update` |
| MCP alias | `kaiten_update_board` |
| Description | Update a Kaiten board. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/boards/{board_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `board_id` | `integer` | yes | — | Board ID |
| `title` | `string` | no | — | New title |
| `description` | `string` | no | — | New description |
| `external_id` | `string` | no | — | External ID |
| `top` | `number` | no | — | Top position (px) |
| `left` | `number` | no | — | Left position (px) |
| `sort_order` | `number` | no | — | Sort order |
| `default_card_type_id` | `integer` | no | — | Default card type ID for new cards |

**Examples**

- Update a board.: `kaiten boards update --space-id 1 --board-id 10 --title "Updated"`

<a id="module-columns"></a>
## Колонки и подколонки (`columns`) — 8 commands

Columns, subcolumns and related card structure.

**Namespace tree**

```text
columns
  create
  delete
  list
  update
subcolumns
  create
  delete
  list
  update
```

### `columns.create`

| Field | Value |
|---|---|
| CLI command | `kaiten columns create` |
| MCP alias | `kaiten_create_column` |
| Description | Create a column on a Kaiten board. Type: 1=queue, 2=in_progress, 3=done. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/boards/{board_id}/columns` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `board_id` | `integer` | yes | — | Board ID |
| `title` | `string` | yes | — | Column title |
| `type` | `integer` | yes | `1`, `2`, `3` | Column type: 1=queue, 2=in_progress, 3=done |
| `wip_limit` | `integer` | no | — | WIP limit |
| `wip_limit_type` | `integer` | no | — | WIP limit type (1=cards count, 2=size sum) |
| `col_count` | `integer` | no | — | Number of sub-columns to split into |
| `sort_order` | `number` | no | — | Sort order |

**Examples**

- Create a board column.: `kaiten columns create --board-id 10 --title "Doing" --type 2 --json`

### `columns.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten columns delete` |
| MCP alias | `kaiten_delete_column` |
| Description | Delete a column from a Kaiten board. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/boards/{board_id}/columns/{column_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `board_id` | `integer` | yes | — | Board ID |
| `column_id` | `integer` | yes | — | Column ID |

**Examples**

- Delete a board column.: `kaiten columns delete --board-id 10 --column-id 20 --json`

### `columns.list`

| Field | Value |
|---|---|
| CLI command | `kaiten columns list` |
| MCP alias | `kaiten_list_columns` |
| Description | List columns on a Kaiten board. Column types: 1=queue, 2=in_progress, 3=done. Response includes: wip_limit, wip_limit_type (1=cards count, 2=size sum), last_moved_warning_after_days, archive_after_days, card_hide_after_days. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/boards/{board_id}/columns` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `board_id` | `integer` | yes | — | Board ID |

**Examples**

- List columns on a board.: `kaiten columns list --board-id 10 --json`

### `columns.update`

| Field | Value |
|---|---|
| CLI command | `kaiten columns update` |
| MCP alias | `kaiten_update_column` |
| Description | Update a column on a Kaiten board. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/boards/{board_id}/columns/{column_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `board_id` | `integer` | yes | — | Board ID |
| `column_id` | `integer` | yes | — | Column ID |
| `title` | `string` | no | — | New title |
| `type` | `integer` | no | `1`, `2`, `3` | Column type |
| `wip_limit` | `integer` | no | — | WIP limit |
| `wip_limit_type` | `integer` | no | — | WIP limit type (1=cards count, 2=size sum) |
| `col_count` | `integer` | no | — | Number of sub-columns to split into |
| `sort_order` | `number` | no | — | Sort order |

**Examples**

- Rename a board column.: `kaiten columns update --board-id 10 --column-id 20 --title "Review" --json`

### `subcolumns.create`

| Field | Value |
|---|---|
| CLI command | `kaiten subcolumns create` |
| MCP alias | `kaiten_create_subcolumn` |
| Description | Create a subcolumn inside a Kaiten column. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/columns/{column_id}/subcolumns` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `column_id` | `integer` | yes | — | Column ID |
| `title` | `string` | yes | — | Subcolumn title |
| `sort_order` | `number` | no | — | Sort order |
| `wip_limit` | `integer` | no | — | WIP limit |
| `col_count` | `integer` | no | — | Number of sub-columns to split into |

**Examples**

- Create a subcolumn.: `kaiten subcolumns create --column-id 20 --title "Blocked" --json`

### `subcolumns.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten subcolumns delete` |
| MCP alias | `kaiten_delete_subcolumn` |
| Description | Delete a subcolumn from a Kaiten column. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/columns/{column_id}/subcolumns/{subcolumn_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `column_id` | `integer` | yes | — | Column ID |
| `subcolumn_id` | `integer` | yes | — | Subcolumn ID |

**Examples**

- Delete a subcolumn.: `kaiten subcolumns delete --column-id 20 --subcolumn-id 30 --json`

### `subcolumns.list`

| Field | Value |
|---|---|
| CLI command | `kaiten subcolumns list` |
| MCP alias | `kaiten_list_subcolumns` |
| Description | List all subcolumns of a Kaiten column. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/columns/{column_id}/subcolumns` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `column_id` | `integer` | yes | — | Column ID |

**Examples**

- List subcolumns for a column.: `kaiten subcolumns list --column-id 20 --json`

### `subcolumns.update`

| Field | Value |
|---|---|
| CLI command | `kaiten subcolumns update` |
| MCP alias | `kaiten_update_subcolumn` |
| Description | Update a subcolumn of a Kaiten column. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/columns/{column_id}/subcolumns/{subcolumn_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `column_id` | `integer` | yes | — | Column ID |
| `subcolumn_id` | `integer` | yes | — | Subcolumn ID |
| `title` | `string` | no | — | New title |
| `sort_order` | `number` | no | — | Sort order |
| `wip_limit` | `integer` | no | — | WIP limit |
| `col_count` | `integer` | no | — | Number of sub-columns to split into |

**Examples**

- Update a subcolumn.: `kaiten subcolumns update --column-id 20 --subcolumn-id 30 --title "Blocked" --json`

<a id="module-lanes"></a>
## Дорожки (`lanes`) — 4 commands

Swimlanes and lane-level operations.

**Namespace tree**

```text
lanes
  create
  delete
  list
  update
```

### `lanes.create`

| Field | Value |
|---|---|
| CLI command | `kaiten lanes create` |
| MCP alias | `kaiten_create_lane` |
| Description | Create a lane (swimlane) on a Kaiten board. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/boards/{board_id}/lanes` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `board_id` | `integer` | yes | — | Board ID |
| `title` | `string` | yes | — | Lane title |
| `sort_order` | `number` | no | — | Sort order |
| `row_count` | `integer` | no | — | Number of sub-rows to split into |
| `wip_limit` | `integer` | no | — | WIP limit |
| `wip_limit_type` | `integer` | no | — | WIP limit type (1=cards count, 2=size sum) |
| `default_card_type_id` | `integer` | no | — | Default card type ID for new cards in this lane |

**Examples**

- Create a board lane.: `kaiten lanes create --board-id 10 --title "Backend" --json`

### `lanes.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten lanes delete` |
| MCP alias | `kaiten_delete_lane` |
| Description | Delete a lane from a Kaiten board. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/boards/{board_id}/lanes/{lane_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `board_id` | `integer` | yes | — | Board ID |
| `lane_id` | `integer` | yes | — | Lane ID |

**Examples**

- Delete a lane.: `kaiten lanes delete --board-id 10 --lane-id 20 --json`

### `lanes.list`

| Field | Value |
|---|---|
| CLI command | `kaiten lanes list` |
| MCP alias | `kaiten_list_lanes` |
| Description | List lanes (swimlanes) on a Kaiten board. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/boards/{board_id}/lanes` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `board_id` | `integer` | yes | — | Board ID |

**Examples**

- List lanes on a board.: `kaiten lanes list --board-id 10 --json`

### `lanes.update`

| Field | Value |
|---|---|
| CLI command | `kaiten lanes update` |
| MCP alias | `kaiten_update_lane` |
| Description | Update a lane on a Kaiten board. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/boards/{board_id}/lanes/{lane_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `board_id` | `integer` | yes | — | Board ID |
| `lane_id` | `integer` | yes | — | Lane ID |
| `title` | `string` | no | — | New title |
| `sort_order` | `number` | no | — | Sort order |
| `row_count` | `integer` | no | — | Number of sub-rows to split into |
| `wip_limit` | `integer` | no | — | WIP limit |
| `wip_limit_type` | `integer` | no | — | WIP limit type (1=cards count, 2=size sum) |
| `default_card_type_id` | `integer` | no | — | Default card type ID for new cards in this lane |
| `condition` | `integer` | no | `1`, `2` | 1=active, 2=archived |

**Examples**

- Update a lane.: `kaiten lanes update --board-id 10 --lane-id 20 --title "Backend" --json`

<a id="module-card-types"></a>
## Типы карточек (`card_types`) — 5 commands

Card types and type metadata.

**Namespace tree**

```text
card-types
  create
  delete
  get
  list
  update
```

### `card-types.create`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types create` |
| MCP alias | `kaiten_create_card_type` |
| Description | Create a Kaiten card type. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/card-types` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Type name (1-64 chars) |
| `letter` | `string` | yes | — | Single letter or emoji |
| `color` | `integer` | yes | — | Color (2-25) |
| `description_template` | `string` | no | — | Template for card description |

**Examples**

- Create a card type.: `kaiten card-types create --name "Feature" --letter F --color 3 --json`

### `card-types.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types delete` |
| MCP alias | `kaiten_delete_card_type` |
| Description | Delete a Kaiten card type. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/card-types/{type_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `type_id` | `integer` | yes | — | Card type ID to delete |
| `replace_type_id` | `integer` | yes | — | Replacement card type ID |
| `has_to_replace_in_automation` | `boolean` | no | — | Replace this type in automations. |
| `has_to_replace_in_restriction` | `boolean` | no | — | Replace this type in restrictions. |
| `has_to_replace_in_workflow` | `boolean` | no | — | Replace this type in workflows. |

**Examples**

- Delete a card type with replacement.: `kaiten card-types delete --type-id 42 --replace-type-id 1 --json`

### `card-types.get`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types get` |
| MCP alias | `kaiten_get_card_type` |
| Description | Get a Kaiten card type by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/card-types/{type_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `type_id` | `integer` | yes | — | Card type ID |

**Examples**

- Get a card type.: `kaiten card-types get --type-id 42 --json`

### `card-types.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types list` |
| MCP alias | `kaiten_list_card_types` |
| Description | List Kaiten card types. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/card-types` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Search filter |
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List card types.: `kaiten card-types list --query "bug" --json`

### `card-types.update`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types update` |
| MCP alias | `kaiten_update_card_type` |
| Description | Update a Kaiten card type. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/card-types/{type_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `type_id` | `integer` | yes | — | Card type ID |
| `name` | `string` | no | — | New name |
| `letter` | `string` | no | — | New letter |
| `color` | `integer` | no | — | New color (2-25) |
| `description_template` | `string` | no | — | Description template |

**Examples**

- Update a card type.: `kaiten card-types update --type-id 42 --name "Bug" --json`

<a id="module-custom-properties"></a>
## Кастомные свойства (`custom_properties`) — 10 commands

Custom properties and select values.

**Namespace tree**

```text
custom-properties
  create
  delete
  get
  list
  update
custom-properties.select-values
  create
  delete
  get
  list
  update
```

### `custom-properties.create`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties create` |
| MCP alias | `kaiten_create_custom_property` |
| Description | Create a company custom property. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/custom-properties` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Property name (1-255 chars) |
| `type` | `string` | yes | `string`, `number`, `date`, `email`, `checkbox`, `select`, `formula`, `url`, `collective_score`, `vote`, `collective_vote`, `catalog`, `phone`, `user`, `attachment` | Property type |
| `show_on_facade` | `boolean` | no | — | Show on card facade |
| `multi_select` | `boolean` | no | — | Enable multi-select |
| `colorful` | `boolean` | no | — | Enable colors for select values |
| `multiline` | `boolean` | no | — | Multiline text field |
| `values_creatable_by_users` | `boolean` | no | — | Allow regular users to create values |
| `values_type` | `string` | no | `number`, `text` | Values type (required for collective_score) |
| `vote_variant` | `string` | no | `rating`, `scale`, `emoji_set` | Vote variant (required for vote/collective_vote) |
| `color` | `integer` | no | — | Color index |
| `data` | `object` | no | — | Type-specific data; required for vote/collective_vote and some other typed properties |

**Examples**

- Create a custom property.: `kaiten custom-properties create --name Status --type select --json`

### `custom-properties.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties delete` |
| MCP alias | `kaiten_delete_custom_property` |
| Description | Delete a custom property. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/custom-properties/{property_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `property_id` | `integer` | yes | — | Property ID |

**Examples**

- Delete a custom property.: `kaiten custom-properties delete --property-id 5 --json`

### `custom-properties.get`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties get` |
| MCP alias | `kaiten_get_custom_property` |
| Description | Get a custom property by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/company/custom-properties/{property_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `property_id` | `integer` | yes | — | Property ID |

**Examples**

- Get a custom property.: `kaiten custom-properties get --property-id 5 --json`

### `custom-properties.list`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties list` |
| MCP alias | `kaiten_list_custom_properties` |
| Description | List company custom properties. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/company/custom-properties` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `include_values` | `boolean` | no | — | Include select/catalog values |
| `include_author` | `boolean` | no | — | Include author user object |
| `types` | `string` | no | — | Comma-separated type names to filter |
| `conditions` | `string` | no | — | Comma-separated conditions to filter |
| `query` | `string` | no | — | Search filter by name |
| `order_by` | `string` | no | — | Sort column |
| `order_direction` | `string` | no | — | Sort direction (asc or desc) |
| `board_id` | `integer` | no | — | Filter properties available on a specific board |
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List custom properties.: `kaiten custom-properties list --types select --json`

### `custom-properties.select-values.create`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties select-values create` |
| MCP alias | `kaiten_create_select_value` |
| Description | Create a select value for a custom property. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/custom-properties/{property_id}/select-values` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `property_id` | `integer` | yes | — | Property ID |
| `value` | `string` | yes | — | Select value text |
| `color` | `integer` | no | — | Color index |
| `sort_order` | `number` | no | — | Sort order (float) |

**Examples**

- Create a select value.: `kaiten custom-properties select-values create --property-id 3 --value High --json`

### `custom-properties.select-values.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties select-values delete` |
| MCP alias | `kaiten_delete_select_value` |
| Description | Delete (soft) a select value by marking it as deleted. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/custom-properties/{property_id}/select-values/{value_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `property_id` | `integer` | yes | — | Property ID |
| `value_id` | `integer` | yes | — | Select value ID |

**Examples**

- Soft-delete a select value.: `kaiten custom-properties select-values delete --property-id 3 --value-id 10 --json`

### `custom-properties.select-values.get`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties select-values get` |
| MCP alias | `kaiten_get_select_value` |
| Description | Get a single select value by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/company/custom-properties/{property_id}/select-values/{value_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `property_id` | `integer` | yes | — | Property ID |
| `value_id` | `integer` | yes | — | Select value ID |

**Examples**

- Get a select value.: `kaiten custom-properties select-values get --property-id 3 --value-id 10 --json`

### `custom-properties.select-values.list`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties select-values list` |
| MCP alias | `kaiten_list_select_values` |
| Description | List select values for a custom property. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/company/custom-properties/{property_id}/select-values` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `property_id` | `integer` | yes | — | Property ID |
| `query` | `string` | no | — | Search filter by value text |
| `order_by` | `string` | no | `id`, `sort_order`, `match_query_priority` | Sort order mode |
| `conditions` | `string` | no | — | Comma-separated conditions |
| `v2_select_search` | `boolean` | no | — | Use v2 search mode |
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List select values.: `kaiten custom-properties select-values list --property-id 3 --json`

### `custom-properties.select-values.update`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties select-values update` |
| MCP alias | `kaiten_update_select_value` |
| Description | Update a select value for a custom property. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/custom-properties/{property_id}/select-values/{value_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `property_id` | `integer` | yes | — | Property ID |
| `value_id` | `integer` | yes | — | Select value ID |
| `value` | `string` | no | — | New value text |
| `condition` | `string` | no | `active`, `inactive` | Value status |
| `color` | `integer` | no | — | Color index |
| `sort_order` | `number` | no | — | Sort order (float) |

**Examples**

- Update a select value.: `kaiten custom-properties select-values update --property-id 3 --value-id 10 --value Critical --json`

### `custom-properties.update`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties update` |
| MCP alias | `kaiten_update_custom_property` |
| Description | Update a custom property. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/custom-properties/{property_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `property_id` | `integer` | yes | — | Property ID |
| `name` | `string` | no | — | New name |
| `condition` | `string` | no | `active`, `inactive` | Status |
| `show_on_facade` | `boolean` | no | — | Show on card facade |
| `multi_select` | `boolean` | no | — | Multi-select mode |
| `colorful` | `boolean` | no | — | Enable colors |
| `multiline` | `boolean` | no | — | Multiline mode |
| `values_creatable_by_users` | `boolean` | no | — | Allow users to create values |
| `is_used_as_progress` | `boolean` | no | — | Use this formula property as progress |
| `color` | `integer` | no | — | Color index |
| `data` | `object` | no | — | Type-specific data |
| `fields_settings` | `object` | no | — | Catalog fields configuration |

**Examples**

- Update a custom property.: `kaiten custom-properties update --property-id 5 --name Priority --json`

<a id="module-documents"></a>
## Документы (`documents`) — 10 commands

Documents and document groups.

**Namespace tree**

```text
document-groups
  create
  delete
  get
  list
  update
documents
  create
  delete
  get
  list
  update
```

### `document-groups.create`

| Field | Value |
|---|---|
| CLI command | `kaiten document-groups create` |
| MCP alias | `kaiten_create_document_group` |
| Description | Create a new Kaiten document group. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/document-groups` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `title` | `string` | yes | — | Group title |
| `parent_entity_uid` | `string` | no | — | Parent group UID for nesting |
| `sort_order` | `integer` | no | — | Sort order (auto-generated if not provided) |

**Examples**

- Create a document group.: `kaiten document-groups create --title "Engineering" --json`

### `document-groups.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten document-groups delete` |
| MCP alias | `kaiten_delete_document_group` |
| Description | Delete a Kaiten document group. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/document-groups/{group_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `group_uid` | `string` | yes | — | Document group UID |

**Examples**

- Delete a document group.: `kaiten document-groups delete --group-uid grp-1 --json`

### `document-groups.get`

| Field | Value |
|---|---|
| CLI command | `kaiten document-groups get` |
| MCP alias | `kaiten_get_document_group` |
| Description | Get a Kaiten document group by UID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/document-groups/{group_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `group_uid` | `string` | yes | — | Document group UID |

**Examples**

- Get a document group.: `kaiten document-groups get --group-uid grp-1 --json`

### `document-groups.list`

| Field | Value |
|---|---|
| CLI command | `kaiten document-groups list` |
| MCP alias | `kaiten_list_document_groups` |
| Description | List Kaiten document groups. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/document-groups` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Search filter |
| `limit` | `integer` | no | — | Max results (default: 50) |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List document groups.: `kaiten document-groups list --query "Engineering" --json`

### `document-groups.update`

| Field | Value |
|---|---|
| CLI command | `kaiten document-groups update` |
| MCP alias | `kaiten_update_document_group` |
| Description | Update a Kaiten document group. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/document-groups/{group_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `group_uid` | `string` | yes | — | Document group UID |
| `title` | `string` | no | — | New group title |

**Examples**

- Update a document group.: `kaiten document-groups update --group-uid grp-1 --title "Docs" --json`

### `documents.create`

| Field | Value |
|---|---|
| CLI command | `kaiten documents create` |
| MCP alias | `kaiten_create_document` |
| Description | Create a new Kaiten document. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/documents` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `title` | `string` | yes | — | Document title |
| `text` | `string` | no | — | Markdown content converted to ProseMirror. |
| `data` | `object` | no | — | Raw ProseMirror JSON. |
| `parent_entity_uid` | `string` | no | — | Parent document group UID |
| `sort_order` | `integer` | no | — | Sort order (auto-generated if not provided) |
| `key` | `string` | no | — | Unique key identifier |

**Examples**

- Create a document from markdown.: `kaiten documents create --title "Spec" --text "# Header" --json`

### `documents.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten documents delete` |
| MCP alias | `kaiten_delete_document` |
| Description | Delete a Kaiten document. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/documents/{document_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `document_uid` | `string` | yes | — | Document UID |

**Examples**

- Delete a document.: `kaiten documents delete --document-uid doc-1 --json`

### `documents.get`

| Field | Value |
|---|---|
| CLI command | `kaiten documents get` |
| MCP alias | `kaiten_get_document` |
| Description | Get a Kaiten document by UID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/documents/{document_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `document_uid` | `string` | yes | — | Document UID |

**Examples**

- Get a document.: `kaiten documents get --document-uid doc-1 --json`

### `documents.list`

| Field | Value |
|---|---|
| CLI command | `kaiten documents list` |
| MCP alias | `kaiten_list_documents` |
| Description | List Kaiten documents. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/documents` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Search filter |
| `limit` | `integer` | no | — | Max results (default: 50) |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List documents.: `kaiten documents list --query "Design" --json`

### `documents.update`

| Field | Value |
|---|---|
| CLI command | `kaiten documents update` |
| MCP alias | `kaiten_update_document` |
| Description | Update a Kaiten document. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/documents/{document_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `document_uid` | `string` | yes | — | Document UID |
| `title` | `string` | no | — | New document title |
| `text` | `string` | no | — | Markdown content converted to ProseMirror. |
| `data` | `object` | no | — | Raw ProseMirror JSON. |
| `parent_entity_uid` | `string` | no | — | New parent group UID |
| `sort_order` | `integer` | no | — | Sort order |
| `key` | `string` | no | — | Unique key identifier |

**Examples**

- Update a document body.: `kaiten documents update --document-uid doc-1 --text "**bold**" --json`

<a id="module-webhooks"></a>
## Вебхуки (`webhooks`) — 9 commands

Webhook configuration and delivery settings.

**Namespace tree**

```text
incoming-webhooks
  create
  delete
  list
  update
webhooks
  create
  delete
  get
  list
  update
```

### `incoming-webhooks.create`

| Field | Value |
|---|---|
| CLI command | `kaiten incoming-webhooks create` |
| MCP alias | `kaiten_create_incoming_webhook` |
| Description | Create an incoming card-creation webhook for a Kaiten space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/webhooks` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `board_id` | `integer` | yes | — | Board ID |
| `column_id` | `integer` | yes | — | Column ID |
| `lane_id` | `integer` | yes | — | Lane ID |
| `owner_id` | `integer` | yes | — | Owner user ID |
| `type_id` | `integer` | no | — | Card type ID |
| `position` | `integer` | no | — | Position in the column |
| `format` | `integer` | no | `1`, `2`, `3`, `4`, `5`, `6`, `7` | Payload format |

**Examples**

- Create an incoming webhook.: `kaiten incoming-webhooks create --space-id 1 --board-id 2 --column-id 3 --lane-id 4 --owner-id 5 --json`

### `incoming-webhooks.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten incoming-webhooks delete` |
| MCP alias | `kaiten_delete_incoming_webhook` |
| Description | Delete an incoming card-creation webhook from a Kaiten space. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/webhooks/{webhook_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `webhook_id` | `string` | yes | — | Webhook ID (hash string) |

**Examples**

- Delete an incoming webhook.: `kaiten incoming-webhooks delete --space-id 1 --webhook-id hook-1 --json`

### `incoming-webhooks.list`

| Field | Value |
|---|---|
| CLI command | `kaiten incoming-webhooks list` |
| MCP alias | `kaiten_list_incoming_webhooks` |
| Description | List incoming card-creation webhooks for a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/spaces/{space_id}/webhooks` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |

**Examples**

- List incoming webhooks.: `kaiten incoming-webhooks list --space-id 1 --json`

### `incoming-webhooks.update`

| Field | Value |
|---|---|
| CLI command | `kaiten incoming-webhooks update` |
| MCP alias | `kaiten_update_incoming_webhook` |
| Description | Update an incoming card-creation webhook in a Kaiten space. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/webhooks/{webhook_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `webhook_id` | `string` | yes | — | Webhook ID (hash string) |
| `board_id` | `integer` | no | — | Board ID |
| `column_id` | `integer` | no | — | Column ID |
| `lane_id` | `integer` | no | — | Lane ID |
| `owner_id` | `integer` | no | — | Owner user ID |
| `type_id` | `integer` | no | — | Card type ID |
| `position` | `integer` | no | — | Position in the column |
| `format` | `integer` | no | `1`, `2`, `3`, `4`, `5`, `6`, `7` | Payload format |

**Examples**

- Update an incoming webhook.: `kaiten incoming-webhooks update --space-id 1 --webhook-id hook-1 --position 1 --json`

### `webhooks.create`

| Field | Value |
|---|---|
| CLI command | `kaiten webhooks create` |
| MCP alias | `kaiten_create_webhook` |
| Description | Create an external webhook for a Kaiten space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/external-webhooks` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `url` | `string` | yes | — | Webhook URL |

**Examples**

- Create an external webhook.: `kaiten webhooks create --space-id 1 --url "https://example.test" --json`

### `webhooks.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten webhooks delete` |
| MCP alias | `kaiten_delete_webhook` |
| Description | Delete an external webhook from a Kaiten space. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/external-webhooks/{webhook_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `webhook_id` | `integer` | yes | — | Webhook ID |

**Examples**

- Delete an external webhook.: `kaiten webhooks delete --space-id 1 --webhook-id 2 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `404`, `405`
- Live note: Webhook DELETE may return 404/405 even after successful creation; the live suite validates that contract explicitly.

### `webhooks.get`

| Field | Value |
|---|---|
| CLI command | `kaiten webhooks get` |
| MCP alias | `kaiten_get_webhook` |
| Description | Get a specific external webhook for a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/spaces/{space_id}/external-webhooks/{webhook_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `webhook_id` | `integer` | yes | — | Webhook ID |

**Examples**

- Get an external webhook.: `kaiten webhooks get --space-id 1 --webhook-id 2 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `404`, `405`
- Live note: Webhook GET may return 404/405 even after successful creation; the live suite validates that contract explicitly.

### `webhooks.list`

| Field | Value |
|---|---|
| CLI command | `kaiten webhooks list` |
| MCP alias | `kaiten_list_webhooks` |
| Description | List all external webhooks for a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/spaces/{space_id}/external-webhooks` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |

**Examples**

- List external webhooks.: `kaiten webhooks list --space-id 1 --json`

### `webhooks.update`

| Field | Value |
|---|---|
| CLI command | `kaiten webhooks update` |
| MCP alias | `kaiten_update_webhook` |
| Description | Update an external webhook for a Kaiten space. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/external-webhooks/{webhook_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `webhook_id` | `integer` | yes | — | Webhook ID |
| `url` | `string` | no | — | Webhook URL |
| `enabled` | `boolean` | no | — | Whether the webhook is enabled |

**Examples**

- Update an external webhook.: `kaiten webhooks update --space-id 1 --webhook-id 2 --enabled --json`

<a id="module-automations"></a>
## Автоматизации и воркфлоу (`automations`) — 11 commands

Automations, incoming webhooks and workflows.

**Namespace tree**

```text
automations
  copy
  create
  delete
  get
  list
  update
workflows
  create
  delete
  get
  list
  update
```

### `automations.copy`

| Field | Value |
|---|---|
| CLI command | `kaiten automations copy` |
| MCP alias | `kaiten_copy_automation` |
| Description | Copy an automation to another space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/automations/{automation_id}/copy` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Source space ID |
| `automation_id` | `string` | yes | — | Automation ID (UUID) |
| `target_space_id` | `integer` | yes | — | Target space ID |

**Examples**

- Copy an automation.: `kaiten automations copy --space-id 1 --automation-id auto-1 --target-space-id 2 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `400`, `403`, `404`, `405`
- Live note: Automation copy remains sandbox-dependent even with a live-valid source automation; the live suite accepts success or a documented 400/403/404/405 contract.

### `automations.create`

| Field | Value |
|---|---|
| CLI command | `kaiten automations create` |
| MCP alias | `kaiten_create_automation` |
| Description | Create a new automation in a Kaiten space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/automations` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `name` | `string` | yes | — | Automation name |
| `trigger` | `object` | yes | — | Trigger configuration |
| `actions` | `array` | yes | — | Action configurations |
| `conditions` | `object` | no | — | Conditions configuration |
| `type` | `string` | no | `on_action`, `on_date`, `on_demand`, `on_workflow` | Automation type |
| `sort_order` | `number` | no | — | Sort position |
| `source_automation_id` | `string` | no | — | Automation ID to clone from |

**Examples**

- Create an automation using the known live-valid add_assignee payload shape.: `kaiten automations create --space-id 1 --name Auto --type on_action --trigger '{"type":"card_created"}' --actions '[{"type":"add_assignee","created":"2026-01-01T00:00:00+00:00","data":{"variant":"specific","userId":42}}]' --json`

**Notes**

- Live contract: `live_passed`; expected statuses: —
- Live note: Automation creation passes on sandbox when the payload matches the known live-valid add_assignee shape derived from kaiten-mcp e2e.

### `automations.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten automations delete` |
| MCP alias | `kaiten_delete_automation` |
| Description | Delete an automation from a Kaiten space. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/automations/{automation_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `automation_id` | `string` | yes | — | Automation ID (UUID) |

**Examples**

- Delete an automation.: `kaiten automations delete --space-id 1 --automation-id auto-1 --json`

**Notes**

- Live contract: `live_passed`; expected statuses: —
- Live note: Automation delete passes on sandbox for automations created during live validation; cleanup is verified.

### `automations.get`

| Field | Value |
|---|---|
| CLI command | `kaiten automations get` |
| MCP alias | `kaiten_get_automation` |
| Description | Get a specific automation in a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/spaces/{space_id}/automations/{automation_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `automation_id` | `string` | yes | — | Automation ID (UUID) |

**Examples**

- Get an automation.: `kaiten automations get --space-id 1 --automation-id auto-1 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `405`
- Live note: Automation GET-single may return 405 even after successful creation; the live suite validates that contract explicitly.

### `automations.list`

| Field | Value |
|---|---|
| CLI command | `kaiten automations list` |
| MCP alias | `kaiten_list_automations` |
| Description | List all automations for a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/spaces/{space_id}/automations` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |

**Examples**

- List space automations.: `kaiten automations list --space-id 1 --json`

### `automations.update`

| Field | Value |
|---|---|
| CLI command | `kaiten automations update` |
| MCP alias | `kaiten_update_automation` |
| Description | Update an automation in a Kaiten space. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/automations/{automation_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `automation_id` | `string` | yes | — | Automation ID (UUID) |
| `name` | `string` | no | — | New automation name |
| `trigger` | `object` | no | — | New trigger configuration |
| `actions` | `array` | no | — | New action configurations |
| `conditions` | `object` | no | — | New conditions configuration |
| `status` | `string` | no | `active`, `disabled` | Automation status |
| `sort_order` | `number` | no | — | Sort position |

**Examples**

- Disable an automation.: `kaiten automations update --space-id 1 --automation-id auto-1 --status disabled --json`

**Notes**

- Live contract: `live_passed`; expected statuses: —
- Live note: Automation update passes on sandbox for automations created with the known live-valid add_assignee payload shape.

### `workflows.create`

| Field | Value |
|---|---|
| CLI command | `kaiten workflows create` |
| MCP alias | `kaiten_create_workflow` |
| Description | Create a new company workflow. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/workflows` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Workflow name |
| `stages` | `array` | yes | — | Workflow stages |
| `transitions` | `array` | yes | — | Workflow transitions |

**Examples**

- Create a workflow.: `kaiten workflows create --name Flow --stages '[{"id":"1","name":"Todo","type":"queue"}]' --transitions '[{"id":"t1"}]' --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `405`
- Live note: Workflow creation is permission-dependent on sandbox; the live suite accepts either success or a documented 403/405 error.

### `workflows.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten workflows delete` |
| MCP alias | `kaiten_delete_workflow` |
| Description | Delete a company workflow. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/workflows/{workflow_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `workflow_id` | `string` | yes | — | Workflow ID (UUID) |

**Examples**

- Delete a workflow.: `kaiten workflows delete --workflow-id wf-1 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: When workflow creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel workflow id.

### `workflows.get`

| Field | Value |
|---|---|
| CLI command | `kaiten workflows get` |
| MCP alias | `kaiten_get_workflow` |
| Description | Get a specific company workflow by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/company/workflows/{workflow_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `workflow_id` | `string` | yes | — | Workflow ID (UUID) |

**Examples**

- Get a workflow.: `kaiten workflows get --workflow-id wf-1 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: When workflow creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel workflow id.

### `workflows.list`

| Field | Value |
|---|---|
| CLI command | `kaiten workflows list` |
| MCP alias | `kaiten_list_workflows` |
| Description | List company workflows. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/company/workflows` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `limit` | `integer` | no | — | Maximum number of results |
| `offset` | `integer` | no | — | Offset for pagination |

**Examples**

- List workflows.: `kaiten workflows list --json`

### `workflows.update`

| Field | Value |
|---|---|
| CLI command | `kaiten workflows update` |
| MCP alias | `kaiten_update_workflow` |
| Description | Update a company workflow. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/workflows/{workflow_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `workflow_id` | `string` | yes | — | Workflow ID (UUID) |
| `name` | `string` | no | — | New workflow name |
| `stages` | `array` | no | — | Updated stages |
| `transitions` | `array` | no | — | Updated transitions |

**Examples**

- Update a workflow.: `kaiten workflows update --workflow-id wf-1 --name Flow2 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: When workflow creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel workflow id.

<a id="module-projects"></a>
## Проекты и спринты (`projects`) — 13 commands

Projects, project cards and sprints.

**Namespace tree**

```text
projects
  create
  delete
  get
  list
  update
projects.cards
  add
  list
  remove
sprints
  create
  delete
  get
  list
  update
```

### `projects.cards.add`

| Field | Value |
|---|---|
| CLI command | `kaiten projects cards add` |
| MCP alias | `kaiten_add_project_card` |
| Description | Add a card to a Kaiten project. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/projects/{project_id}/cards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `project_id` | `string` | yes | — | Project ID (UUID) |
| `card_id` | `integer` | yes | — | Card ID to add |

**Examples**

- Add a card to a project.: `kaiten projects cards add --project-id p1 --card-id 10 --json`

### `projects.cards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten projects cards list` |
| MCP alias | `kaiten_list_project_cards` |
| Description | List cards in a Kaiten project. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `synthetic` |
| Cache policy | `request_scope` |
| Path template | `/projects/{project_id}/cards` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `project_id` | `string` | yes | — | Project ID (UUID) |
| `compact` | `boolean` | no | — | Return compact response without heavy fields (avatars, nested user objects). |

**Examples**

- List project cards.: `kaiten projects cards list --project-id p1 --compact --json`

**Notes**

- Live contract: `synthetic_read`; expected statuses: `405`
- Live note: If GET /projects/{project_id}/cards returns 405, the CLI falls back to GET /projects/{project_id}?with_cards_data=true and extracts the embedded cards list.

### `projects.cards.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten projects cards remove` |
| MCP alias | `kaiten_remove_project_card` |
| Description | Remove a card from a Kaiten project. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/projects/{project_id}/cards/{card_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `project_id` | `string` | yes | — | Project ID (UUID) |
| `card_id` | `integer` | yes | — | Card ID to remove |

**Examples**

- Remove a card from a project.: `kaiten projects cards remove --project-id p1 --card-id 10 --json`

### `projects.create`

| Field | Value |
|---|---|
| CLI command | `kaiten projects create` |
| MCP alias | `kaiten_create_project` |
| Description | Create a new Kaiten project. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/projects` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `title` | `string` | yes | — | Project title (stored as 'name') |
| `description` | `string` | no | — | Project description |
| `work_calendar_id` | `string` | no | — | Work calendar UUID to attach to the project |
| `settings` | `object` | no | — | Project settings |
| `properties` | `object` | no | — | Custom property values as {id_<N>: value} pairs |

**Examples**

- Create a project.: `kaiten projects create --title "Platform" --json`

### `projects.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten projects delete` |
| MCP alias | `kaiten_delete_project` |
| Description | Delete a Kaiten project. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/projects/{project_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `project_id` | `string` | yes | — | Project ID (UUID) |

**Examples**

- Delete a project.: `kaiten projects delete --project-id p1 --json`

### `projects.get`

| Field | Value |
|---|---|
| CLI command | `kaiten projects get` |
| MCP alias | `kaiten_get_project` |
| Description | Get a Kaiten project by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/projects/{project_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `project_id` | `string` | yes | — | Project ID (UUID) |
| `with_cards_data` | `boolean` | no | — | Include full card data with path info and custom properties |

**Examples**

- Get a project by ID.: `kaiten projects get --project-id p1 --json`

### `projects.list`

| Field | Value |
|---|---|
| CLI command | `kaiten projects list` |
| MCP alias | `kaiten_list_projects` |
| Description | List all Kaiten projects in the company. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/projects` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- List company projects.: `kaiten projects list --json`

### `projects.update`

| Field | Value |
|---|---|
| CLI command | `kaiten projects update` |
| MCP alias | `kaiten_update_project` |
| Description | Update a Kaiten project. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/projects/{project_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `project_id` | `string` | yes | — | Project ID (UUID) |
| `title` | `string` | no | — | Project title (stored as 'name') |
| `description` | `string` | no | — | Project description |
| `condition` | `string` | no | `active`, `inactive` | Project condition (active or inactive) |
| `work_calendar_id` | `string` | no | — | Work calendar UUID to attach to the project |
| `settings` | `object` | no | — | Project settings |
| `properties` | `object` | no | — | Custom property values as {id_<N>: value} pairs; set a key to null to clear it |

**Examples**

- Update a project.: `kaiten projects update --project-id p1 --title "Platform" --json`

### `sprints.create`

| Field | Value |
|---|---|
| CLI command | `kaiten sprints create` |
| MCP alias | `kaiten_create_sprint` |
| Description | Create a new Kaiten sprint. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/sprints` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `title` | `string` | yes | — | Sprint title |
| `board_id` | `integer` | yes | — | Board ID for the sprint |
| `goal` | `string` | no | — | Sprint goal |
| `start_date` | `string` | no | — | Start date (ISO 8601) |
| `finish_date` | `string` | no | — | Finish date (ISO 8601) |

**Examples**

- Create a sprint.: `kaiten sprints create --title "Sprint 1" --board-id 10 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `405`
- Live note: Sprint creation is permission-dependent on sandbox; the live suite accepts either success or a documented 403/405 error.

### `sprints.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten sprints delete` |
| MCP alias | `kaiten_delete_sprint` |
| Description | Delete a Kaiten sprint. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/sprints/{sprint_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `sprint_id` | `integer` | yes | — | Sprint ID |

**Examples**

- Delete a sprint.: `kaiten sprints delete --sprint-id 1 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: Sprint deletion is often unavailable on sandbox; the live suite accepts the documented 403/404/405 contract.

### `sprints.get`

| Field | Value |
|---|---|
| CLI command | `kaiten sprints get` |
| MCP alias | `kaiten_get_sprint` |
| Description | Get a Kaiten sprint by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/sprints/{sprint_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `sprint_id` | `integer` | yes | — | Sprint ID |
| `exclude_deleted_cards` | `boolean` | no | — | Exclude deleted cards from the sprint summary |

**Examples**

- Get a sprint.: `kaiten sprints get --sprint-id 1 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: When sprint creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel sprint id.

### `sprints.list`

| Field | Value |
|---|---|
| CLI command | `kaiten sprints list` |
| MCP alias | `kaiten_list_sprints` |
| Description | List Kaiten sprints. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/sprints` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `active` | `boolean` | no | — | Filter by active/inactive |
| `limit` | `integer` | no | — | Max results (max 100) |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List sprints.: `kaiten sprints list --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `405`
- Live note: Sprint listing is permission-dependent on sandbox; the live suite accepts either success or a documented 403/405 error.

### `sprints.update`

| Field | Value |
|---|---|
| CLI command | `kaiten sprints update` |
| MCP alias | `kaiten_update_sprint` |
| Description | Update a Kaiten sprint. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/sprints/{sprint_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `sprint_id` | `integer` | yes | — | Sprint ID |
| `title` | `string` | no | — | Sprint title |
| `goal` | `string` | no | — | Sprint goal |
| `start_date` | `string` | no | — | Start date (ISO 8601) |
| `finish_date` | `string` | no | — | Finish date (ISO 8601) |
| `active` | `boolean` | no | — | Set to false to finish/complete the sprint |
| `archive_done_cards` | `boolean` | no | — | Archive completed cards when finishing a sprint |

**Examples**

- Update a sprint.: `kaiten sprints update --sprint-id 1 --active false --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`, `500`
- Live note: When sprint creation is unavailable or the created sprint id cannot be resolved, sandbox may return 403/404/405 or 500 on a sentinel sprint id; the live suite validates that documented defect contract explicitly.

<a id="module-roles-and-groups"></a>
## Роли и группы (`roles_and_groups`) — 14 commands

Roles, groups and permission-related operations.

**Namespace tree**

```text
company-groups
  create
  delete
  get
  list
  update
group-users
  add
  list
  remove
roles
  get
  list
space-users
  add
  list
  remove
  update
```

### `company-groups.create`

| Field | Value |
|---|---|
| CLI command | `kaiten company-groups create` |
| MCP alias | `kaiten_create_company_group` |
| Description | Create a new company group in Kaiten. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/groups` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Group name |

**Examples**

- Create a company group.: `kaiten company-groups create --name "Engineering" --json`

### `company-groups.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten company-groups delete` |
| MCP alias | `kaiten_delete_company_group` |
| Description | Delete a company group in Kaiten. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/groups/{group_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `group_uid` | `string` | yes | — | Group UID |

**Examples**

- Delete a company group.: `kaiten company-groups delete --group-uid grp-1 --json`

### `company-groups.get`

| Field | Value |
|---|---|
| CLI command | `kaiten company-groups get` |
| MCP alias | `kaiten_get_company_group` |
| Description | Get a company group by UID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/company/groups/{group_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `group_uid` | `string` | yes | — | Group UID |

**Examples**

- Get a company group.: `kaiten company-groups get --group-uid grp-1 --json`

### `company-groups.list`

| Field | Value |
|---|---|
| CLI command | `kaiten company-groups list` |
| MCP alias | `kaiten_list_company_groups` |
| Description | List company groups in Kaiten. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/company/groups` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Search query |
| `limit` | `integer` | no | — | Max results to return |
| `offset` | `integer` | no | — | Offset for pagination |

**Examples**

- List company groups.: `kaiten company-groups list --query "Engineering" --json`

### `company-groups.update`

| Field | Value |
|---|---|
| CLI command | `kaiten company-groups update` |
| MCP alias | `kaiten_update_company_group` |
| Description | Update a company group in Kaiten. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/company/groups/{group_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `group_uid` | `string` | yes | — | Group UID |
| `name` | `string` | no | — | New group name |

**Examples**

- Update a company group.: `kaiten company-groups update --group-uid grp-1 --name "Docs" --json`

### `group-users.add`

| Field | Value |
|---|---|
| CLI command | `kaiten group-users add` |
| MCP alias | `kaiten_add_group_user` |
| Description | Add a user to a company group. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/groups/{group_uid}/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `group_uid` | `string` | yes | — | Group UID |
| `user_id` | `integer` | yes | — | User ID to add |

**Examples**

- Add a user to a group.: `kaiten group-users add --group-uid grp-1 --user-id 7 --json`

### `group-users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten group-users list` |
| MCP alias | `kaiten_list_group_users` |
| Description | List users in a company group. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/groups/{group_uid}/users` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `group_uid` | `string` | yes | — | Group UID |
| `compact` | `boolean` | no | — | Return compact response without heavy fields. |

**Examples**

- List group users.: `kaiten group-users list --group-uid grp-1 --compact --json`

### `group-users.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten group-users remove` |
| MCP alias | `kaiten_remove_group_user` |
| Description | Remove a user from a company group. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/groups/{group_uid}/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `group_uid` | `string` | yes | — | Group UID |
| `user_id` | `integer` | yes | — | User ID to remove |

**Examples**

- Remove a user from a group.: `kaiten group-users remove --group-uid grp-1 --user-id 7 --json`

### `roles.get`

| Field | Value |
|---|---|
| CLI command | `kaiten roles get` |
| MCP alias | `kaiten_get_role` |
| Description | Get a role by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/tree-entity-roles/{role_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `role_id` | `string` | yes | — | Role ID (UUID) |

**Examples**

- Get a role.: `kaiten roles get --role-id role-1 --json`

### `roles.list`

| Field | Value |
|---|---|
| CLI command | `kaiten roles list` |
| MCP alias | `kaiten_list_roles` |
| Description | List available roles in Kaiten. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/tree-entity-roles` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Search query |
| `limit` | `integer` | no | — | Max results to return |
| `offset` | `integer` | no | — | Offset for pagination |

**Examples**

- List roles.: `kaiten roles list --query "admin" --json`

### `space-users.add`

| Field | Value |
|---|---|
| CLI command | `kaiten space-users add` |
| MCP alias | `kaiten_add_space_user` |
| Description | Add a user to a Kaiten space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `user_id` | `integer` | yes | — | User ID to add |
| `role_id` | `string` | no | — | Role ID (UUID) to assign |

**Examples**

- Add a user to a space.: `kaiten space-users add --space-id 1 --user-id 7 --json`

### `space-users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten space-users list` |
| MCP alias | `kaiten_list_space_users` |
| Description | List users of a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/spaces/{space_id}/users` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `compact` | `boolean` | no | — | Return compact response without heavy fields. |

**Examples**

- List space users.: `kaiten space-users list --space-id 1 --compact --json`

### `space-users.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten space-users remove` |
| MCP alias | `kaiten_remove_space_user` |
| Description | Remove a user from a Kaiten space. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `user_id` | `integer` | yes | — | User ID to remove |

**Examples**

- Remove a user from a space.: `kaiten space-users remove --space-id 1 --user-id 7 --json`

### `space-users.update`

| Field | Value |
|---|---|
| CLI command | `kaiten space-users update` |
| MCP alias | `kaiten_update_space_user` |
| Description | Update a user's role in a Kaiten space. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/spaces/{space_id}/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `user_id` | `integer` | yes | — | User ID to update |
| `role_id` | `string` | no | — | New role ID (UUID) |

**Examples**

- Update a space user role.: `kaiten space-users update --space-id 1 --user-id 7 --role-id 9 --json`

<a id="module-audit-and-analytics"></a>
## Аудит и аналитика (`audit_and_analytics`) — 12 commands

Audit logs, activity, saved filters and analytics helpers.

**Namespace tree**

```text
audit-logs
  list
card-activity
  get
card-location-history
  batch-get
  get
company-activity
  get
saved-filters
  create
  delete
  get
  list
  update
space-activity
  get
space-activity-all
  get
```

### `audit-logs.list`

| Field | Value |
|---|---|
| CLI command | `kaiten audit-logs list` |
| MCP alias | `kaiten_list_audit_logs` |
| Description | List Kaiten audit logs for the company. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/audit-logs` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `categories` | `string` | no | — | Comma-separated log categories |
| `actions` | `string` | no | — | Comma-separated audit actions |
| `from` | `string` | no | — | Start of date range filter |
| `to` | `string` | no | — | End of date range filter |
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List audit logs.: `kaiten audit-logs list --limit 10 --json`

### `card-activity.get`

| Field | Value |
|---|---|
| CLI command | `kaiten card-activity get` |
| MCP alias | `kaiten_get_card_activity` |
| Description | Get activity feed for a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/activity` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- Get card activity.: `kaiten card-activity get --card-id 1 --json`

### `card-location-history.batch-get`

| Field | Value |
|---|---|
| CLI command | `kaiten card-location-history batch-get` |
| MCP alias | `kaiten_batch_get_card_location_history` |
| Description | Fetch location history for multiple cards with bounded worker concurrency. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `aggregated` |
| Cache policy | `request_scope` |
| Path template | `/cards/location-history/batch` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_ids` | `array` | yes | — | Card IDs to fetch |
| `workers` | `integer` | no | — | Parallel workers (default 2, max 6) |
| `fields` | `string` | no | — | Comma-separated field names to keep for each history row |

**Examples**

- Fetch history for several cards in one CLI call.: `kaiten card-location-history batch-get --card-ids '[1,2,3]' --json`
- Fetch projected history rows with bounded concurrency.: `kaiten card-location-history batch-get --card-ids '[1,2,3]' --workers 2 --fields changed,column_id,subcolumn_id --json`

**Notes**

- The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.
- Use conservative workers to avoid shifting the bottleneck from process startup to API rate limiting.

### `card-location-history.get`

| Field | Value |
|---|---|
| CLI command | `kaiten card-location-history get` |
| MCP alias | `kaiten_get_card_location_history` |
| Description | Get location history of a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/cards/{card_id}/location-history` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |

**Examples**

- Get card location history.: `kaiten card-location-history get --card-id 1 --json`

**Notes**

- Bulk alternative: `card-location-history.batch-get`
- This is a per-card read and becomes expensive when repeated hundreds of times.
- For high-cardinality reads, use card-location-history.batch-get instead of spawning one CLI process per card.

### `company-activity.get`

| Field | Value |
|---|---|
| CLI command | `kaiten company-activity get` |
| MCP alias | `kaiten_get_company_activity` |
| Description | Get company-wide activity feed. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/company/activity` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `actions` | `string` | no | — | Comma-separated action types |
| `created_after` | `string` | no | — | Filter activities after this datetime |
| `created_before` | `string` | no | — | Filter activities before this datetime |
| `author_id` | `integer` | no | — | Filter by author user ID |
| `cursor_created` | `string` | no | — | Cursor datetime |
| `cursor_id` | `integer` | no | — | Cursor ID |
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |
| `compact` | `boolean` | no | — | Strip heavy fields |
| `fields` | `string` | no | — | Comma-separated field names to keep |

**Examples**

- Get company activity.: `kaiten company-activity get --limit 10 --json`

### `saved-filters.create`

| Field | Value |
|---|---|
| CLI command | `kaiten saved-filters create` |
| MCP alias | `kaiten_create_saved_filter` |
| Description | Create a saved filter. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/saved-filters` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Filter name |
| `filter` | `object` | yes | — | Filter criteria object |
| `shared` | `boolean` | no | — | Whether the filter is shared with the team |

**Examples**

- Create a saved filter.: `kaiten saved-filters create --name MyFilter --filter '{}' --json`

### `saved-filters.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten saved-filters delete` |
| MCP alias | `kaiten_delete_saved_filter` |
| Description | Delete a saved filter. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/saved-filters/{filter_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `filter_id` | `integer` | yes | — | Filter ID |

**Examples**

- Delete a saved filter.: `kaiten saved-filters delete --filter-id 1 --json`

### `saved-filters.get`

| Field | Value |
|---|---|
| CLI command | `kaiten saved-filters get` |
| MCP alias | `kaiten_get_saved_filter` |
| Description | Get a saved filter by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/saved-filters/{filter_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `filter_id` | `integer` | yes | — | Filter ID |

**Examples**

- Get a saved filter.: `kaiten saved-filters get --filter-id 1 --json`

### `saved-filters.list`

| Field | Value |
|---|---|
| CLI command | `kaiten saved-filters list` |
| MCP alias | `kaiten_list_saved_filters` |
| Description | List saved filters. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/saved-filters` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List saved filters.: `kaiten saved-filters list --json`

### `saved-filters.update`

| Field | Value |
|---|---|
| CLI command | `kaiten saved-filters update` |
| MCP alias | `kaiten_update_saved_filter` |
| Description | Update a saved filter. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/saved-filters/{filter_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `filter_id` | `integer` | yes | — | Filter ID |
| `name` | `string` | no | — | Filter name |
| `filter` | `object` | no | — | Filter criteria object |
| `shared` | `boolean` | no | — | Whether the filter is shared with the team |

**Examples**

- Update a saved filter.: `kaiten saved-filters update --filter-id 1 --name Renamed --json`

### `space-activity-all.get`

| Field | Value |
|---|---|
| CLI command | `kaiten space-activity-all get` |
| MCP alias | `kaiten_get_all_space_activity` |
| Description | Fetch all space activity with automatic pagination. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `aggregated` |
| Cache policy | `request_scope` |
| Path template | `/spaces/{space_id}/activity` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `actions` | `string` | no | — | Comma-separated action types |
| `created_after` | `string` | no | — | Filter activities after this datetime |
| `created_before` | `string` | no | — | Filter activities before this datetime |
| `author_id` | `integer` | no | — | Filter by author user ID |
| `page_size` | `integer` | no | — | Events per page (default 100, max 100) |
| `max_pages` | `integer` | no | — | Safety limit on pages to fetch |
| `compact` | `boolean` | no | — | Strip heavy fields; defaults to true for bulk |
| `fields` | `string` | no | — | Comma-separated field names to keep |

**Examples**

- Fetch all space activity with bounded pagination.: `kaiten space-activity-all get --space-id 1 --page-size 20 --max-pages 2 --json`

**Notes**

- Use this aggregated path for report windows instead of building manual offset loops around space-activity.get.

### `space-activity.get`

| Field | Value |
|---|---|
| CLI command | `kaiten space-activity get` |
| MCP alias | `kaiten_get_space_activity` |
| Description | Get activity feed for a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/spaces/{space_id}/activity` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `actions` | `string` | no | — | Comma-separated action types |
| `created_after` | `string` | no | — | Filter activities after this datetime |
| `created_before` | `string` | no | — | Filter activities before this datetime |
| `author_id` | `integer` | no | — | Filter by author user ID |
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |
| `compact` | `boolean` | no | — | Strip heavy fields |
| `fields` | `string` | no | — | Comma-separated field names to keep |

**Examples**

- Get space activity.: `kaiten space-activity get --space-id 1 --limit 10 --json`

**Notes**

- Bulk alternative: `space-activity-all.get`
- This low-level endpoint is useful for targeted page reads, but report workflows usually want the bounded bulk path.
- Prefer space-activity-all.get over manual offset loops when collecting a full investigation window.

<a id="module-service-desk"></a>
## Service Desk (`service_desk`) — 47 commands

Service Desk requests, users, SLA, organizations and settings.

**Namespace tree**

```text
card-sla-measurements
  get
card-slas
  attach
  detach
service-desk.organization-users
  add
  batch-add
  batch-remove
  remove
  update
service-desk.organizations
  create
  delete
  get
  list
  update
service-desk.requests
  create
  delete
  get
  list
  update
service-desk.services
  create
  delete
  get
  list
  update
service-desk.settings
  get
  update
service-desk.sla
  create
  delete
  get
  list
  recalculate
  stats
  update
service-desk.sla-rules
  create
  delete
  update
service-desk.stats
  get
service-desk.template-answers
  create
  delete
  get
  list
  update
service-desk.users
  list
  set-temp-password
  update
service-desk.vote-properties
  add
  remove
space-sla-measurements
  get
```

### `card-sla-measurements.get`

| Field | Value |
|---|---|
| CLI command | `kaiten card-sla-measurements get` |
| MCP alias | `kaiten_get_card_sla_measurements` |
| Description | Get SLA rule measurements for a card. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/cards/{card_id}/sla-rules-measurements` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |

**Examples**

- Get card SLA measurements.: `kaiten card-sla-measurements get --card-id 1 --json`

### `card-slas.attach`

| Field | Value |
|---|---|
| CLI command | `kaiten card-slas attach` |
| MCP alias | `kaiten_attach_card_sla` |
| Description | Attach an SLA policy to a card. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/slas` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `sla_id` | `string` | yes | — | SLA ID (UUID) |

**Examples**

- Attach an SLA to a card.: `kaiten card-slas attach --card-id 1 --sla-id sla-1 --json`

### `card-slas.detach`

| Field | Value |
|---|---|
| CLI command | `kaiten card-slas detach` |
| MCP alias | `kaiten_detach_card_sla` |
| Description | Detach an SLA policy from a card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/cards/{card_id}/slas/{sla_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID |
| `sla_id` | `string` | yes | — | SLA ID (UUID) |

**Examples**

- Detach an SLA from a card.: `kaiten card-slas detach --card-id 1 --sla-id sla-1 --json`

### `service-desk.organization-users.add`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organization-users add` |
| MCP alias | `kaiten_add_sd_org_user` |
| Description | Add a user to a Service Desk organization. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/organizations/{organization_id}/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | Organization ID |
| `user_id` | `integer` | yes | — | User ID |
| `permissions` | `integer` | no | — | Permission bitmask |

**Examples**

- Add an organization user.: `kaiten service-desk organization-users add --organization-id 1 --user-id 2 --json`

### `service-desk.organization-users.batch-add`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organization-users batch-add` |
| MCP alias | `kaiten_batch_add_sd_org_users` |
| Description | Add multiple users to a Service Desk organization. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/organizations/{organization_id}/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | Organization ID |
| `user_ids` | `array` | yes | — | User IDs |

**Examples**

- Batch-add organization users.: `kaiten service-desk organization-users batch-add --organization-id 1 --user-ids '[1,2]' --json`

### `service-desk.organization-users.batch-remove`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organization-users batch-remove` |
| MCP alias | `kaiten_batch_remove_sd_org_users` |
| Description | Remove multiple users from a Service Desk organization. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/organizations/{organization_id}/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | Organization ID |
| `user_ids` | `array` | yes | — | User IDs |

**Examples**

- Batch-remove organization users.: `kaiten service-desk organization-users batch-remove --organization-id 1 --user-ids '[1,2]' --json`

### `service-desk.organization-users.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organization-users remove` |
| MCP alias | `kaiten_remove_sd_org_user` |
| Description | Remove a user from a Service Desk organization. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/organizations/{organization_id}/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | Organization ID |
| `user_id` | `integer` | yes | — | User ID |

**Examples**

- Remove an organization user.: `kaiten service-desk organization-users remove --organization-id 1 --user-id 2 --json`

### `service-desk.organization-users.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organization-users update` |
| MCP alias | `kaiten_update_sd_org_user` |
| Description | Update a user's permissions in a Service Desk organization. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/organizations/{organization_id}/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | Organization ID |
| `user_id` | `integer` | yes | — | User ID |
| `permissions` | `integer` | no | — | Permission bitmask |

**Examples**

- Update organization-user permissions.: `kaiten service-desk organization-users update --organization-id 1 --user-id 2 --permissions 7 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `400`, `403`, `404`, `405`
- Live note: Updating Service Desk organization-user permissions remains sandbox-dependent; the live suite accepts success or a documented 400/403/404/405 contract.

### `service-desk.organizations.create`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organizations create` |
| MCP alias | `kaiten_create_sd_organization` |
| Description | Create a Service Desk organization. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/organizations` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Organization name |
| `description` | `string` | no | — | Organization description |

**Examples**

- Create an organization.: `kaiten service-desk organizations create --name Org --json`

### `service-desk.organizations.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organizations delete` |
| MCP alias | `kaiten_delete_sd_organization` |
| Description | Delete a Service Desk organization. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/organizations/{organization_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | Organization ID |

**Examples**

- Delete an organization.: `kaiten service-desk organizations delete --organization-id 1 --json`

### `service-desk.organizations.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organizations get` |
| MCP alias | `kaiten_get_sd_organization` |
| Description | Get a Service Desk organization by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/service-desk/organizations/{organization_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | Organization ID |

**Examples**

- Get an organization.: `kaiten service-desk organizations get --organization-id 1 --json`

### `service-desk.organizations.list`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organizations list` |
| MCP alias | `kaiten_list_sd_organizations` |
| Description | List Service Desk organizations. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/service-desk/organizations` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Search filter |
| `includeUsers` | `boolean` | no | — | Include organization users |
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List organizations.: `kaiten service-desk organizations list --json`

### `service-desk.organizations.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organizations update` |
| MCP alias | `kaiten_update_sd_organization` |
| Description | Update a Service Desk organization. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/organizations/{organization_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | Organization ID |
| `name` | `string` | no | — | Organization name |
| `description` | `string` | no | — | Organization description |

**Examples**

- Update an organization.: `kaiten service-desk organizations update --organization-id 1 --name Org2 --json`

### `service-desk.requests.create`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk requests create` |
| MCP alias | `kaiten_create_sd_request` |
| Description | Create a new Service Desk request. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/requests` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `title` | `string` | yes | — | Request title |
| `service_id` | `integer` | yes | — | Service ID |
| `description` | `string` | no | — | Request description |
| `priority` | `string` | no | — | Request priority |

**Examples**

- Create a request.: `kaiten service-desk requests create --title "Help" --service-id 1 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `400`, `403`, `404`, `405`
- Live note: Service Desk request creation is permission-dependent; the live suite accepts either success or a documented 400/403/404/405 contract.

### `service-desk.requests.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk requests delete` |
| MCP alias | `kaiten_delete_sd_request` |
| Description | Delete a Service Desk request. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/requests/{request_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `request_id` | `integer` | yes | — | Request ID |

**Examples**

- Delete a request.: `kaiten service-desk requests delete --request-id 1 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: When request creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel request id.

### `service-desk.requests.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk requests get` |
| MCP alias | `kaiten_get_sd_request` |
| Description | Get a Service Desk request by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/service-desk/requests/{request_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `request_id` | `integer` | yes | — | Request ID |

**Examples**

- Get a request.: `kaiten service-desk requests get --request-id 1 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: When request creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel request id.

### `service-desk.requests.list`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk requests list` |
| MCP alias | `kaiten_list_sd_requests` |
| Description | List Service Desk requests. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/service-desk/requests` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Search filter |
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List Service Desk requests.: `kaiten service-desk requests list --json`

### `service-desk.requests.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk requests update` |
| MCP alias | `kaiten_update_sd_request` |
| Description | Update a Service Desk request. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/requests/{request_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `request_id` | `integer` | yes | — | Request ID |
| `title` | `string` | no | — | Request title |
| `description` | `string` | no | — | Request description |
| `priority` | `string` | no | — | Request priority |

**Examples**

- Update a request.: `kaiten service-desk requests update --request-id 1 --priority high --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: When request creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel request id.

### `service-desk.services.create`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk services create` |
| MCP alias | `kaiten_create_sd_service` |
| Description | Create a new Service Desk service. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/services` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Service name |
| `board_id` | `integer` | yes | — | Board ID |
| `position` | `integer` | yes | — | Sort position |
| `description` | `string` | no | — | Service description |
| `template_description` | `string` | no | — | Default description template |
| `lng` | `string` | yes | `en`, `ru` | Language code |
| `display_status` | `string` | no | `by_column`, `by_state` | How status is displayed |
| `column_id` | `integer` | no | — | Default column ID |
| `lane_id` | `integer` | no | — | Default lane ID |
| `type_id` | `integer` | no | — | Card type ID |
| `email_settings` | `integer` | no | — | Email settings bitmask |
| `fields_settings` | `object` | no | — | Request form fields configuration |
| `settings` | `object` | no | — | Additional settings |
| `allow_to_add_external_recipients` | `boolean` | no | — | Allow external recipients |
| `hide_in_list` | `boolean` | no | — | Hide service in list |
| `is_default` | `boolean` | no | — | Set as default service |

**Examples**

- Create a service.: `kaiten service-desk services create --name Support --board-id 1 --position 1 --lng en --json`

### `service-desk.services.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk services delete` |
| MCP alias | `kaiten_delete_sd_service` |
| Description | Archive a Service Desk service. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/services/{service_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `service_id` | `integer` | yes | — | Service ID |

**Examples**

- Archive a service.: `kaiten service-desk services delete --service-id 1 --json`

### `service-desk.services.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk services get` |
| MCP alias | `kaiten_get_sd_service` |
| Description | Get a Service Desk service by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/service-desk/services/{service_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `service_id` | `integer` | yes | — | Service ID |

**Examples**

- Get a service.: `kaiten service-desk services get --service-id 1 --json`

### `service-desk.services.list`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk services list` |
| MCP alias | `kaiten_list_sd_services` |
| Description | List Service Desk services. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/service-desk/services` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Search filter |
| `include_archived` | `boolean` | no | — | Include archived services |
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List services.: `kaiten service-desk services list --json`

### `service-desk.services.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk services update` |
| MCP alias | `kaiten_update_sd_service` |
| Description | Update a Service Desk service. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/services/{service_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `service_id` | `integer` | yes | — | Service ID |
| `name` | `string` | no | — | Service name |
| `description` | `string` | no | — | Service description |
| `template_description` | `string` | no | — | Default description template |
| `lng` | `string` | no | — | Language code |
| `display_status` | `string` | no | `by_column`, `by_state` | How status is displayed |
| `board_id` | `integer` | no | — | Board ID |
| `column_id` | `integer` | no | — | Default column ID |
| `lane_id` | `integer` | no | — | Default lane ID |
| `type_id` | `integer` | no | — | Card type ID |
| `position` | `integer` | no | — | Sort position |
| `email_settings` | `integer` | no | — | Email settings bitmask |
| `fields_settings` | `object` | no | — | Request form fields configuration |
| `settings` | `object` | no | — | Additional settings |
| `archived` | `boolean` | no | — | Archive or unarchive service |
| `allow_to_add_external_recipients` | `boolean` | no | — | Allow external recipients |
| `hide_in_list` | `boolean` | no | — | Hide service in list |

**Examples**

- Update a service.: `kaiten service-desk services update --service-id 1 --archived --json`

### `service-desk.settings.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk settings get` |
| MCP alias | `kaiten_get_sd_settings` |
| Description | Get current Service Desk settings. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/sd-settings/current` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- Get Service Desk settings.: `kaiten service-desk settings get --json`

### `service-desk.settings.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk settings update` |
| MCP alias | `kaiten_update_sd_settings` |
| Description | Update Service Desk settings. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/sd-settings/current` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `service_desk_settings` | `object` | yes | — | Service Desk configuration object |

**Examples**

- Update Service Desk settings.: `kaiten service-desk settings update --service-desk-settings '{}' --json`

### `service-desk.sla-rules.create`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla-rules create` |
| MCP alias | `kaiten_create_sla_rule` |
| Description | Create a rule within an SLA policy. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/sla/{sla_id}/rules` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `sla_id` | `string` | yes | — | SLA ID (UUID) |
| `type` | `string` | no | — | Rule type |
| `calendar_id` | `string` | no | — | Calendar ID |
| `start_column_uid` | `string` | no | — | Start column UID |
| `finish_column_uid` | `string` | no | — | Finish column UID |
| `estimated_time` | `integer` | no | — | Target time in seconds |
| `notification_settings` | `object` | no | — | Notification configuration |

**Examples**

- Create an SLA rule.: `kaiten service-desk sla-rules create --sla-id sla-1 --type response --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `400`, `403`, `404`, `405`
- Live note: SLA rule creation is permission- and schema-dependent; the live suite accepts either success or a documented 400/403/404/405 contract.

### `service-desk.sla-rules.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla-rules delete` |
| MCP alias | `kaiten_delete_sla_rule` |
| Description | Delete a rule from an SLA policy. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/sla/{sla_id}/rules/{rule_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `sla_id` | `string` | yes | — | SLA ID (UUID) |
| `rule_id` | `string` | yes | — | Rule ID |

**Examples**

- Delete an SLA rule.: `kaiten service-desk sla-rules delete --sla-id sla-1 --rule-id rule-1 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `400`, `403`, `404`, `405`
- Live note: When SLA-rule creation is unavailable, the live suite validates the documented 400/403/404/405 error contract on a sentinel rule id.

### `service-desk.sla-rules.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla-rules update` |
| MCP alias | `kaiten_update_sla_rule` |
| Description | Update a rule within an SLA policy. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/sla/{sla_id}/rules/{rule_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `sla_id` | `string` | yes | — | SLA ID (UUID) |
| `rule_id` | `string` | yes | — | Rule ID |
| `type` | `string` | no | — | Rule type |
| `calendar_id` | `string` | no | — | Calendar ID |
| `start_column_uid` | `string` | no | — | Start column UID |
| `finish_column_uid` | `string` | no | — | Finish column UID |
| `estimated_time` | `integer` | no | — | Target time in seconds |
| `notification_settings` | `object` | no | — | Notification configuration |

**Examples**

- Update an SLA rule.: `kaiten service-desk sla-rules update --sla-id sla-1 --rule-id rule-1 --estimated-time 60 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `400`, `403`, `404`, `405`
- Live note: When SLA-rule creation is unavailable, the live suite validates the documented 400/403/404/405 error contract on a sentinel rule id.

### `service-desk.sla.create`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla create` |
| MCP alias | `kaiten_create_sd_sla` |
| Description | Create a Service Desk SLA policy. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/sla` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | SLA policy name |
| `rules` | `array` | yes | — | SLA rules |
| `notification_settings` | `object` | no | — | Notification configuration |
| `v2` | `boolean` | no | — | Use v2 SLA format |

**Examples**

- Create an SLA policy.: `kaiten service-desk sla create --name SLA --rules '[]' --json`

### `service-desk.sla.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla delete` |
| MCP alias | `kaiten_delete_sd_sla` |
| Description | Delete a Service Desk SLA policy. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/sla/{sla_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `sla_id` | `string` | yes | — | SLA ID (UUID) |

**Examples**

- Delete an SLA policy.: `kaiten service-desk sla delete --sla-id sla-1 --json`

### `service-desk.sla.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla get` |
| MCP alias | `kaiten_get_sd_sla` |
| Description | Get a Service Desk SLA policy by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/service-desk/sla/{sla_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `sla_id` | `string` | yes | — | SLA ID (UUID) |

**Examples**

- Get an SLA policy.: `kaiten service-desk sla get --sla-id sla-1 --json`

### `service-desk.sla.list`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla list` |
| MCP alias | `kaiten_list_sd_sla` |
| Description | List Service Desk SLA policies. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/service-desk/sla` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List SLA policies.: `kaiten service-desk sla list --json`

### `service-desk.sla.recalculate`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla recalculate` |
| MCP alias | `kaiten_recalculate_sla` |
| Description | Trigger recalculation of SLA measurements. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/sla/{sla_id}/recalculate-measurements` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `sla_id` | `string` | yes | — | SLA ID (UUID) |

**Examples**

- Recalculate SLA measurements.: `kaiten service-desk sla recalculate --sla-id sla-1 --json`

### `service-desk.sla.stats`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla stats` |
| MCP alias | `kaiten_get_sd_sla_stats` |
| Description | Get Service Desk SLA statistics. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/service-desk/sla-stats` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `date_from` | `string` | no | — | Start date (ISO format) |
| `date_to` | `string` | no | — | End date (ISO format) |
| `sla_id` | `string` | no | — | SLA ID |
| `service_id` | `integer` | no | — | Service ID |
| `responsible_id` | `integer` | no | — | Responsible user ID |
| `card_type_ids` | `string` | no | — | JSON array of card type IDs |
| `tag_ids` | `string` | no | — | JSON array of tag IDs |

**Examples**

- Get Service Desk SLA statistics.: `kaiten service-desk sla stats --sla-id sla-1 --json`

### `service-desk.sla.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla update` |
| MCP alias | `kaiten_update_sd_sla` |
| Description | Update a Service Desk SLA policy. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/sla/{sla_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `sla_id` | `string` | yes | — | SLA ID (UUID) |
| `name` | `string` | no | — | SLA policy name |
| `status` | `string` | no | — | SLA status |
| `notification_settings` | `object` | no | — | Notification configuration |
| `should_delete_sla_from_cards` | `boolean` | no | — | Remove SLA from cards when deactivating |

**Examples**

- Update an SLA policy.: `kaiten service-desk sla update --sla-id sla-1 --status inactive --json`

### `service-desk.stats.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk stats get` |
| MCP alias | `kaiten_get_sd_stats` |
| Description | Get Service Desk statistics. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/service-desk/stats` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `date_from` | `string` | no | — | Start date (ISO format) |
| `date_to` | `string` | no | — | End date (ISO format) |
| `service_id` | `integer` | no | — | Service ID |
| `report` | `boolean` | no | — | Enable report mode |

**Examples**

- Get Service Desk statistics.: `kaiten service-desk stats get --date-from 2026-01-01 --json`

### `service-desk.template-answers.create`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk template-answers create` |
| MCP alias | `kaiten_create_sd_template_answer` |
| Description | Create a Service Desk template answer. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/template-answers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Template name |
| `text` | `string` | yes | — | Template answer text |

**Examples**

- Create a template answer.: `kaiten service-desk template-answers create --name Hello --text "Hi" --json`

### `service-desk.template-answers.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk template-answers delete` |
| MCP alias | `kaiten_delete_sd_template_answer` |
| Description | Delete a Service Desk template answer. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/template-answers/{template_answer_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `template_answer_id` | `string` | yes | — | Template answer ID (UUID) |

**Examples**

- Delete a template answer.: `kaiten service-desk template-answers delete --template-answer-id ta-1 --json`

### `service-desk.template-answers.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk template-answers get` |
| MCP alias | `kaiten_get_sd_template_answer` |
| Description | Get a Service Desk template answer by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/service-desk/template-answers/{template_answer_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `template_answer_id` | `string` | yes | — | Template answer ID (UUID) |

**Examples**

- Get a template answer.: `kaiten service-desk template-answers get --template-answer-id ta-1 --json`

### `service-desk.template-answers.list`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk template-answers list` |
| MCP alias | `kaiten_list_sd_template_answers` |
| Description | List Service Desk template answers. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/service-desk/template-answers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- List template answers.: `kaiten service-desk template-answers list --json`

### `service-desk.template-answers.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk template-answers update` |
| MCP alias | `kaiten_update_sd_template_answer` |
| Description | Update a Service Desk template answer. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/template-answers/{template_answer_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `template_answer_id` | `string` | yes | — | Template answer ID (UUID) |
| `name` | `string` | no | — | Template name |
| `text` | `string` | no | — | Template answer text |

**Examples**

- Update a template answer.: `kaiten service-desk template-answers update --template-answer-id ta-1 --text "Hello" --json`

### `service-desk.users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk users list` |
| MCP alias | `kaiten_list_sd_users` |
| Description | List Service Desk users. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/service-desk/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `query` | `string` | no | — | Search filter |
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |
| `include_paid_users` | `boolean` | no | — | Include paid users |
| `include_all_sd_users` | `boolean` | no | — | Include all SD users |

**Examples**

- List Service Desk users.: `kaiten service-desk users list --json`

### `service-desk.users.set-temp-password`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk users set-temp-password` |
| MCP alias | `kaiten_set_sd_user_temp_password` |
| Description | Generate a temporary password for a Service Desk user. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/users/set-temporary-password/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `user_id` | `integer` | yes | — | User ID |

**Examples**

- Generate a temporary password.: `kaiten service-desk users set-temp-password --user-id 1 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: Temporary password generation may succeed or return a documented 403/404/405 sandbox error; the live suite accepts both outcomes.

### `service-desk.users.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk users update` |
| MCP alias | `kaiten_update_sd_user` |
| Description | Update a Service Desk user profile. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `user_id` | `integer` | yes | — | User ID |
| `full_name` | `string` | no | — | User full name |
| `lng` | `string` | no | — | Language code |

**Examples**

- Update a Service Desk user.: `kaiten service-desk users update --user-id 1 --full-name "Alice" --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `400`, `403`, `404`, `405`
- Live note: The current live account is not a Service Desk user, so update may return 400 'Should be service desk user'; the live suite validates that documented contract.

### `service-desk.vote-properties.add`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk vote-properties add` |
| MCP alias | `kaiten_add_service_vote_property` |
| Description | Add a custom property as a vote property for a Service Desk service. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/services/{service_id}/vote-properties` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `service_id` | `integer` | yes | — | Service ID |
| `id` | `integer` | yes | — | Custom property ID |

**Examples**

- Add a vote property.: `kaiten service-desk vote-properties add --service-id 1 --id 2 --json`

### `service-desk.vote-properties.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk vote-properties remove` |
| MCP alias | `kaiten_remove_service_vote_property` |
| Description | Remove a vote property from a Service Desk service. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/service-desk/services/{service_id}/vote-properties/{property_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `service_id` | `integer` | yes | — | Service ID |
| `property_id` | `integer` | yes | — | Vote property ID |

**Examples**

- Remove a vote property.: `kaiten service-desk vote-properties remove --service-id 1 --property-id 2 --json`

### `space-sla-measurements.get`

| Field | Value |
|---|---|
| CLI command | `kaiten space-sla-measurements get` |
| MCP alias | `kaiten_get_space_sla_measurements` |
| Description | Get SLA rule measurements for all cards in a space. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/spaces/{space_id}/sla-rules-measurements` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |

**Examples**

- Get space SLA measurements.: `kaiten space-sla-measurements get --space-id 1 --json`

<a id="module-charts"></a>
## Графики и аналитика (`charts`) — 15 commands

Chart endpoints and compute jobs.

**Namespace tree**

```text
charts.block-resolution
  get
charts.boards
  get
charts.cfd
  create
charts.control
  create
charts.cycle-time
  create
charts.due-dates
  get
charts.lead-time
  create
charts.sales-funnel
  create
charts.spectral
  create
charts.summary
  get
charts.task-distribution
  create
charts.throughput-capacity
  create
charts.throughput-demand
  create
compute-jobs
  cancel
  get
```

### `charts.block-resolution.get`

| Field | Value |
|---|---|
| CLI command | `kaiten charts block-resolution get` |
| MCP alias | `kaiten_chart_block_resolution` |
| Description | Get blocker resolution time data for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/charts/block-resolution-time-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `category_ids` | `array` | no | — | Filter by blocker category IDs |

**Examples**

- Get blocker resolution data.: `kaiten charts block-resolution get --space-id 1 --json`

**Notes**

- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.

### `charts.boards.get`

| Field | Value |
|---|---|
| CLI command | `kaiten charts boards get` |
| MCP alias | `kaiten_get_chart_boards` |
| Description | Get board structure for chart configuration in a space. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/charts/{space_id}/boards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |

**Examples**

- Get chart board structure.: `kaiten charts boards get --space-id 1 --json`

### `charts.cfd.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts cfd create` |
| MCP alias | `kaiten_chart_cfd` |
| Description | Build a Cumulative Flow Diagram (CFD) for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/charts/cfd` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `date_from` | `string` | yes | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | End date (ISO 8601) |
| `tags` | `array` | no | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | Filter by card type IDs |
| `group_by` | `string` | no | — | Grouping mode |
| `cardTypes` | `array` | no | — | Filter by card type IDs (alternative field name used by CFD) |
| `selectedLanes` | `array` | no | — | Filter by lane IDs |

**Examples**

- Build a Cumulative Flow Diagram (CFD) for a space.: `kaiten charts cfd create --json`

**Notes**

- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.

### `charts.control.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts control create` |
| MCP alias | `kaiten_chart_control` |
| Description | Build a Control Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/charts/control-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `date_from` | `string` | yes | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | End date (ISO 8601) |
| `tags` | `array` | no | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | Filter by card type IDs |
| `group_by` | `string` | no | — | Grouping mode |
| `start_columns` | `array` | yes | — | Start column IDs (required) |
| `end_columns` | `array` | yes | — | End column IDs (required) |
| `start_column_lanes` | `object` | yes | — | Mapping of start column ID to array of lane IDs, e.g. {"10": [1, 2]} |
| `end_column_lanes` | `object` | yes | — | Mapping of end column ID to array of lane IDs, e.g. {"20": [3, 4]} |

**Examples**

- Build a Control Chart for a space.: `kaiten charts control create --json`

**Notes**

- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.

### `charts.cycle-time.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts cycle-time create` |
| MCP alias | `kaiten_chart_cycle_time` |
| Description | Build a Cycle Time Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/charts/cycle-time-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `date_from` | `string` | yes | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | End date (ISO 8601) |
| `tags` | `array` | no | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | Filter by card type IDs |
| `group_by` | `string` | no | — | Grouping mode |
| `start_column` | `integer` | yes | — | Start column ID |
| `end_column` | `integer` | yes | — | End column ID |

**Examples**

- Build a Cycle Time Chart for a space.: `kaiten charts cycle-time create --json`

**Notes**

- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.

### `charts.due-dates.get`

| Field | Value |
|---|---|
| CLI command | `kaiten charts due-dates get` |
| MCP alias | `kaiten_chart_due_dates` |
| Description | Get due dates analysis for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/charts/due-dates` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `card_date_from` | `string` | yes | — | Card date range start (ISO 8601) |
| `card_date_to` | `string` | yes | — | Card date range end (ISO 8601) |
| `checklist_item_date_from` | `string` | yes | — | Checklist item date range start (ISO 8601) |
| `checklist_item_date_to` | `string` | yes | — | Checklist item date range end (ISO 8601) |
| `due_date` | `string` | no | — | Due date filter (ISO 8601) |
| `responsible_id` | `integer` | no | — | Responsible user ID |
| `tz_offset` | `integer` | no | — | Timezone offset in minutes |
| `lane_ids` | `array` | no | — | Filter by lane IDs |
| `column_ids` | `array` | no | — | Filter by column IDs |
| `card_type_ids` | `array` | no | — | Filter by card type IDs |
| `tag_ids` | `array` | no | — | Filter by tag IDs |

**Examples**

- Get due-date analysis.: `kaiten charts due-dates get --space-id 1 --card-date-from 2026-01-01 --card-date-to 2026-01-31 --checklist-item-date-from 2026-01-01 --checklist-item-date-to 2026-01-31 --json`

**Notes**

- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.

### `charts.lead-time.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts lead-time create` |
| MCP alias | `kaiten_chart_lead_time` |
| Description | Build a Lead Time Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/charts/lead-time` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `date_from` | `string` | yes | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | End date (ISO 8601) |
| `tags` | `array` | no | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | Filter by card type IDs |
| `group_by` | `string` | no | — | Grouping mode |
| `start_columns` | `array` | yes | — | Start column IDs (required) |
| `end_columns` | `array` | yes | — | End column IDs (required) |
| `start_column_lanes` | `object` | yes | — | Mapping of start column ID to array of lane IDs, e.g. {"10": [1, 2]} |
| `end_column_lanes` | `object` | yes | — | Mapping of end column ID to array of lane IDs, e.g. {"20": [3, 4]} |

**Examples**

- Build a Lead Time Chart for a space.: `kaiten charts lead-time create --json`

**Notes**

- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.

### `charts.sales-funnel.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts sales-funnel create` |
| MCP alias | `kaiten_chart_sales_funnel` |
| Description | Build a Sales Funnel Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/charts/sales-funnel` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `date_from` | `string` | yes | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | End date (ISO 8601) |
| `tags` | `array` | no | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | Filter by card type IDs |
| `group_by` | `string` | no | — | Grouping mode |
| `board_configs` | `array` | yes | — | Array of board configuration objects. |

**Examples**

- Build a Sales Funnel Chart for a space.: `kaiten charts sales-funnel create --json`

**Notes**

- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.

### `charts.spectral.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts spectral create` |
| MCP alias | `kaiten_chart_spectral` |
| Description | Build a Spectral Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/charts/spectral-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `date_from` | `string` | yes | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | End date (ISO 8601) |
| `tags` | `array` | no | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | Filter by card type IDs |
| `group_by` | `string` | no | — | Grouping mode |
| `start_columns` | `array` | yes | — | Start column IDs (required) |
| `end_columns` | `array` | yes | — | End column IDs (required) |
| `start_column_lanes` | `object` | yes | — | Mapping of start column ID to array of lane IDs, e.g. {"10": [1, 2]} |
| `end_column_lanes` | `object` | yes | — | Mapping of end column ID to array of lane IDs, e.g. {"20": [3, 4]} |

**Examples**

- Build a Spectral Chart for a space.: `kaiten charts spectral create --json`

**Notes**

- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.

### `charts.summary.get`

| Field | Value |
|---|---|
| CLI command | `kaiten charts summary get` |
| MCP alias | `kaiten_chart_summary` |
| Description | Get done-card summary for a space within a date range. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/charts/summary` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `date_from` | `string` | yes | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | End date (ISO 8601) |
| `done_columns` | `array` | yes | — | Array of done column IDs |

**Examples**

- Get a done-card summary.: `kaiten charts summary get --space-id 1 --date-from 2026-01-01 --date-to 2026-01-31 --done-columns '[10,11]' --json`

**Notes**

- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.

### `charts.task-distribution.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts task-distribution create` |
| MCP alias | `kaiten_chart_task_distribution` |
| Description | Build a Task Distribution Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/charts/task-distribution-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `timezone` | `string` | no | — | Timezone name (e.g. Europe/Moscow) |
| `includeArchivedCards` | `boolean` | no | — | Include archived cards |
| `only_asap_cards` | `boolean` | no | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | Filter by card type IDs |
| `itemsFilter` | `object` | no | — | Additional filter object for items |

**Examples**

- Build a Task Distribution Chart for a space.: `kaiten charts task-distribution create --json`

**Notes**

- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.

### `charts.throughput-capacity.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts throughput-capacity create` |
| MCP alias | `kaiten_chart_throughput_capacity` |
| Description | Build a Throughput Capacity Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/charts/throughput-capacity-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `date_from` | `string` | yes | — | Start date (ISO 8601) |
| `date_to` | `string` | no | — | End date (ISO 8601) |
| `tags` | `array` | no | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | Filter by card type IDs |
| `group_by` | `string` | no | — | Grouping mode |
| `end_column` | `integer` | yes | — | End (done) column ID |

**Examples**

- Build a Throughput Capacity Chart for a space.: `kaiten charts throughput-capacity create --json`

**Notes**

- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.

### `charts.throughput-demand.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts throughput-demand create` |
| MCP alias | `kaiten_chart_throughput_demand` |
| Description | Build a Throughput Demand Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/charts/throughput-demand-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `space_id` | `integer` | yes | — | Space ID |
| `date_from` | `string` | yes | — | Start date (ISO 8601) |
| `date_to` | `string` | no | — | End date (ISO 8601) |
| `tags` | `array` | no | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | Filter by card type IDs |
| `group_by` | `string` | no | — | Grouping mode |
| `start_column` | `integer` | yes | — | Start (input) column ID |

**Examples**

- Build a Throughput Demand Chart for a space.: `kaiten charts throughput-demand create --json`

**Notes**

- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.

### `compute-jobs.cancel`

| Field | Value |
|---|---|
| CLI command | `kaiten compute-jobs cancel` |
| MCP alias | `kaiten_cancel_compute_job` |
| Description | Cancel a running or queued compute job. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/users/current/compute-jobs/{job_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `job_id` | `integer` | yes | — | Compute job ID |

**Examples**

- Cancel a compute job.: `kaiten compute-jobs cancel --job-id 1 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `400`, `404`, `409`
- Live note: Canceling a compute job can legitimately return 400/404/409 depending on backend state; the live suite accepts that contract.

### `compute-jobs.get`

| Field | Value |
|---|---|
| CLI command | `kaiten compute-jobs get` |
| MCP alias | `kaiten_get_compute_job` |
| Description | Get the status and result of an asynchronous compute job. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/users/current/compute-jobs/{job_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `job_id` | `integer` | yes | — | Compute job ID |

**Examples**

- Get compute job status.: `kaiten compute-jobs get --job-id 1 --json`

<a id="module-tree"></a>
## Дерево сущностей (`tree`) — 2 commands

Entity tree and tree navigation commands.

**Namespace tree**

```text
tree
  get
tree.children
  list
```

### `tree.children.list`

| Field | Value |
|---|---|
| CLI command | `kaiten tree children list` |
| MCP alias | `kaiten_list_children` |
| Description | List direct children of an entity in the Kaiten sidebar tree. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `aggregated` |
| Cache policy | `request_scope` |
| Path template | `/tree/children` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `parent_entity_uid` | `string` | no | — | Parent entity UID. Omit to list root-level entities. |

**Examples**

- List direct tree children.: `kaiten tree children list --parent-entity-uid root-1 --json`

### `tree.get`

| Field | Value |
|---|---|
| CLI command | `kaiten tree get` |
| MCP alias | `kaiten_get_tree` |
| Description | Build a nested entity tree from the Kaiten sidebar. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `aggregated` |
| Cache policy | `request_scope` |
| Path template | `/tree` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `root_uid` | `string` | no | — | Start tree from this entity UID. Omit for full tree from roots. |
| `depth` | `integer` | no | — | Max recursion depth (0 = unlimited). Default: 0. |

**Examples**

- Build a bounded entity tree.: `kaiten tree get --depth 1 --json`

<a id="module-utilities"></a>
## Утилиты (`utilities`) — 14 commands

Company, calendars, timers, api keys and removed entities.

**Namespace tree**

```text
api-keys
  create
  delete
  list
calendars
  get
  list
company
  current
  update
removed-boards
  list
removed-cards
  list
user-timers
  create
  delete
  get
  list
  update
```

### `api-keys.create`

| Field | Value |
|---|---|
| CLI command | `kaiten api-keys create` |
| MCP alias | `kaiten_create_api_key` |
| Description | Create a new API key. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/api-keys` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Name for the API key |

**Examples**

- Create an API key.: `kaiten api-keys create --name "local-dev" --json`

**Notes**

- Live contract: `policy_excluded`; expected statuses: —
- Live note: Creating API keys is excluded from live validation because teardown would require testing key deletion.

### `api-keys.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten api-keys delete` |
| MCP alias | `kaiten_delete_api_key` |
| Description | Delete an API key. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/api-keys/{key_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `key_id` | `integer` | yes | — | API key ID |

**Examples**

- Delete an API key.: `kaiten api-keys delete --key-id 1 --json`

**Notes**

- Live contract: `policy_excluded`; expected statuses: —
- Live note: Deleting API keys is explicitly excluded from live validation by user instruction.

### `api-keys.list`

| Field | Value |
|---|---|
| CLI command | `kaiten api-keys list` |
| MCP alias | `kaiten_list_api_keys` |
| Description | List all API keys for the current user. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/api-keys` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- List API keys.: `kaiten api-keys list --json`

### `calendars.get`

| Field | Value |
|---|---|
| CLI command | `kaiten calendars get` |
| MCP alias | `kaiten_get_calendar` |
| Description | Get a specific calendar by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/calendars/{calendar_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `calendar_id` | `string` | yes | — | Calendar ID (UUID) |

**Examples**

- Get a calendar by ID.: `kaiten calendars get --calendar-id cal-1 --json`

### `calendars.list`

| Field | Value |
|---|---|
| CLI command | `kaiten calendars list` |
| MCP alias | `kaiten_list_calendars` |
| Description | List calendars. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/calendars` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List calendars.: `kaiten calendars list --limit 5 --json`

### `company.current`

| Field | Value |
|---|---|
| CLI command | `kaiten company current` |
| MCP alias | `kaiten_get_company` |
| Description | Get current company information. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/companies/current` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- Get current company information.: `kaiten company current --json`

### `company.update`

| Field | Value |
|---|---|
| CLI command | `kaiten company update` |
| MCP alias | `kaiten_update_company` |
| Description | Update current company information. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/companies/current` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | no | — | Company name |

**Examples**

- Update current company information.: `kaiten company update --name "Acme" --json`

### `removed-boards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten removed-boards list` |
| MCP alias | `kaiten_list_removed_boards` |
| Description | List removed boards from the recycle bin. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/removed/boards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List removed boards.: `kaiten removed-boards list --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `405`
- Live note: Sandbox returns 405 for recycle-bin board listing; the live suite validates that contract explicitly.

### `removed-cards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten removed-cards list` |
| MCP alias | `kaiten_list_removed_cards` |
| Description | List removed cards from the recycle bin. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/removed/cards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `limit` | `integer` | no | — | Max results |
| `offset` | `integer` | no | — | Pagination offset |

**Examples**

- List removed cards.: `kaiten removed-cards list --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `405`
- Live note: Sandbox returns 405 for recycle-bin card listing; the live suite validates that contract explicitly.

### `user-timers.create`

| Field | Value |
|---|---|
| CLI command | `kaiten user-timers create` |
| MCP alias | `kaiten_create_user_timer` |
| Description | Create a new user timer for a card. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/user-timers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `card_id` | `integer` | yes | — | Card ID to start timer for |

**Examples**

- Create a user timer.: `kaiten user-timers create --card-id 10 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `400`, `403`, `405`, `409`
- Live note: User-timer creation remains sandbox-dependent; the live suite accepts either success or a documented 400/403/405/409 contract.

### `user-timers.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten user-timers delete` |
| MCP alias | `kaiten_delete_user_timer` |
| Description | Delete a user timer. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/user-timers/{timer_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `timer_id` | `integer` | yes | — | Timer ID |

**Examples**

- Delete a user timer.: `kaiten user-timers delete --timer-id 10 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: When timer creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel timer id.

### `user-timers.get`

| Field | Value |
|---|---|
| CLI command | `kaiten user-timers get` |
| MCP alias | `kaiten_get_user_timer` |
| Description | Get a specific user timer by ID. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Path template | `/user-timers/{timer_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `timer_id` | `integer` | yes | — | Timer ID |

**Examples**

- Get a user timer.: `kaiten user-timers get --timer-id 10 --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: When timer creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel timer id.

### `user-timers.list`

| Field | Value |
|---|---|
| CLI command | `kaiten user-timers list` |
| MCP alias | `kaiten_list_user_timers` |
| Description | List all user timers. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Path template | `/user-timers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- List user timers.: `kaiten user-timers list --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `405`
- Live note: User-timer listing remains sandbox-dependent; the live suite accepts either success or a documented 403/405 error path.

### `user-timers.update`

| Field | Value |
|---|---|
| CLI command | `kaiten user-timers update` |
| MCP alias | `kaiten_update_user_timer` |
| Description | Update a user timer (e.g. pause or resume). |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Path template | `/user-timers/{timer_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `timer_id` | `integer` | yes | — | Timer ID |
| `paused` | `boolean` | no | — | Whether the timer is paused |

**Examples**

- Pause a user timer.: `kaiten user-timers update --timer-id 10 --paused --json`

**Notes**

- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: When timer creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel timer id.

<a id="module-snapshot"></a>
## Локальные snapshots (`snapshot`) — 5 commands

Local-first snapshot build, refresh and management commands.

**Namespace tree**

```text
snapshot
  build
  delete
  list
  refresh
  show
```

### `snapshot.build`

| Field | Value |
|---|---|
| CLI command | `kaiten snapshot build` |
| MCP alias | `kaiten_snapshot_build` |
| Description | Build a persistent local sqlite snapshot for headless reads, analytics, and report workflows. |
| Method | `POST` |
| Mutation | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Path template | `/local/snapshots/{name}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Stable snapshot name. |
| `space_id` | `integer` | yes | — | Source space ID. |
| `board_ids` | `array` | no | — | Optional board IDs to keep inside the snapshot. |
| `preset` | `string` | no | `basic`, `analytics`, `evidence`, `full` | Snapshot scope preset. |
| `window_start` | `string` | no | — | Window start timestamp for analytics/full snapshots. |
| `window_end` | `string` | no | — | Window end timestamp for analytics/full snapshots. |

**Examples**

- Build a reusable local snapshot with topology and cards.: `kaiten snapshot build --name team-basic --space-id 10 --preset basic --json`
- Build an analytics snapshot with bounded activity and history data.: `kaiten snapshot build --name team-q1 --space-id 10 --preset analytics --window-start 2026-01-01T00:00:00Z --window-end 2026-03-31T23:59:59Z --json`

**Notes**

- Build one snapshot, then run repeated local query cards/query metrics commands without extra Kaiten API calls.
- analytics and full presets require window_start/window_end because throughput and history are window-bound datasets.

### `snapshot.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten snapshot delete` |
| MCP alias | `kaiten_snapshot_delete` |
| Description | Delete a local snapshot from sqlite storage. |
| Method | `DELETE` |
| Mutation | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Path template | `/local/snapshots/{name}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Snapshot name. |

**Examples**

- Delete a local snapshot.: `kaiten snapshot delete --name team-q1 --json`

### `snapshot.list`

| Field | Value |
|---|---|
| CLI command | `kaiten snapshot list` |
| MCP alias | `kaiten_snapshot_list` |
| Description | List locally stored snapshots with schema version and dataset counts. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Path template | `/local/snapshots` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- Show available local snapshots.: `kaiten snapshot list --json`

### `snapshot.refresh`

| Field | Value |
|---|---|
| CLI command | `kaiten snapshot refresh` |
| MCP alias | `kaiten_snapshot_refresh` |
| Description | Rebuild an existing local snapshot in place using its stored snapshot definition. |
| Method | `PATCH` |
| Mutation | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Path template | `/local/snapshots/{name}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Snapshot name to rebuild. |

**Examples**

- Refresh a previously built snapshot.: `kaiten snapshot refresh --name team-q1 --json`

**Notes**

- refresh reuses the stored snapshot spec and rebuilds datasets in place; v1 is rebuild-oriented, not incremental.

### `snapshot.show`

| Field | Value |
|---|---|
| CLI command | `kaiten snapshot show` |
| MCP alias | `kaiten_snapshot_show` |
| Description | Show local snapshot metadata, schema version, dataset counts, and the last build trace summary. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Path template | `/local/snapshots/{name}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `name` | `string` | yes | — | Snapshot name. |

**Examples**

- Inspect snapshot metadata and dataset counts.: `kaiten snapshot show --name team-q1 --json`

<a id="module-query"></a>
## Локальные запросы (`query`) — 2 commands

Local-only query and metrics commands over snapshots.

**Namespace tree**

```text
query
  cards
  metrics
```

### `query.cards`

| Field | Value |
|---|---|
| CLI command | `kaiten query cards` |
| MCP alias | `kaiten_query_cards` |
| Description | Run local card filtering against a stored snapshot without calling the Kaiten API. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Path template | `/local/query/cards` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `snapshot` | `string` | yes | — | Snapshot name. |
| `filter` | `object` | no | — | Local filter object for card selection. |
| `view` | `string` | no | `summary`, `detail`, `evidence` | Local output view. summary is the default and keeps payloads narrow for repeated analytics and LLM workflows. |
| `fields` | `string` | no | — | Comma-separated card or derived field names to keep. |
| `limit` | `integer` | no | — | Max returned rows. Default 100. |
| `offset` | `integer` | no | — | Pagination offset. |
| `compact` | `boolean` | no | — | Return a compact card response. |

**Examples**

- Filter cards locally by board and derived flags in summary view.: `kaiten query cards --snapshot team-basic --filter '{"board_ids":[10],"has_children":true}' --fields id,title,has_children --json`
- Search local evidence text without extra API calls.: `kaiten query cards --snapshot team-basic --view evidence --filter '{"comment_text_query":"blocked"}' --compact --fields id,title,comment_text --json`

**Notes**

- query cards never calls the Kaiten API; build or refresh the snapshot first.
- summary is the default view and keeps local card payloads narrow for LLM and report workflows.
- Use text_query, child_text_query, and comment_text_query to reduce candidate sets locally before involving an LLM.

### `query.metrics`

| Field | Value |
|---|---|
| CLI command | `kaiten query metrics` |
| MCP alias | `kaiten_query_metrics` |
| Description | Compute local metrics over a stored snapshot without calling the Kaiten API. |
| Method | `GET` |
| Mutation | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Path template | `/local/query/metrics` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Description |
|---|---|---|---|---|
| `snapshot` | `string` | yes | — | Snapshot name. |
| `metric` | `string` | yes | `count`, `wip`, `throughput`, `lead_time`, `cycle_time`, `aging` | Metric to compute locally. |
| `filter` | `object` | no | — | Optional local filter object applied before metrics. |
| `group_by` | `string|null` | no | `board_id`, `column_id`, `lane_id`, `type_id`, `owner_id`, `responsible_id`, `state`, `condition`, `None` | Optional grouping field. |

**Examples**

- Compute throughput locally over the snapshot window.: `kaiten query metrics --snapshot team-q1 --metric throughput --group-by board_id --json`
- Compute local WIP aging for a reduced candidate set.: `kaiten query metrics --snapshot team-basic --metric aging --filter '{"board_ids":[10],"has_comments":true}' --group-by column_id --json`

**Notes**

- throughput, lead_time, and cycle_time use the snapshot window when it exists; basic snapshots fall back to all locally known done transitions.
- For repeated report generation, query metrics after snapshot build instead of re-fetching topology, cards, and history on every run.
