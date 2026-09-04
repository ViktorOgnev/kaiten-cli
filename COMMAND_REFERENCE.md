# Command Reference

> This file is generated from the local registry. Do not edit by hand.

`kaiten-cli` currently exposes **417** canonical commands across **35** registry modules.

## Conventions

- Canonical CLI form is rendered as `kaiten <namespace...> <action>`.
- MCP alias is shown inline for every command.
- All commands support `--json`, `--from-file` and `--stdin-json`; these global input modes are not repeated per command.
- `--json` success/error envelopes include top-level `stats` with duration, HTTP/API wait, cache counters, and grouped method/path-family aggregates.
- `--compact` and `--fields` only apply when the command metadata says they are supported.
- `Mutation` reflects the HTTP method; `Allowed in read-only mode` is the semantic policy used by `--read-only`; `Remote side effects` controls ambiguous-outcome handling and cache invalidation.
- Use `search-tools`, `describe` and `examples` when you need interactive discovery instead of scrolling the full page.
- Default cache mode is `auto`: cacheable safe reads use adaptive persistent TTLs, and heavy or dense repeated analytics are retained longer.
- Use `refresh` once at a freshness boundary, `off` for cache diagnostics, privacy or high-frequency polling, and `readwrite` only with an explicit fixed `--cache-ttl-seconds`.
- For read-heavy workflows, prefer bulk tools and the `snapshot` / `query` local-first path over per-entity loops.

## Module Index

| Area | Module | Count | Section |
|---|---|---:|---|
| Карточки | `cards` | 15 | [Open](#module-cards) |
| Комментарии | `comments` | 5 | [Open](#module-comments) |
| Участники и пользователи | `members` | 7 | [Open](#module-members) |
| Логи времени | `time_logs` | 6 | [Open](#module-time-logs) |
| Теги | `tags` | 7 | [Open](#module-tags) |
| Чеклисты | `checklists` | 17 | [Open](#module-checklists) |
| Блокировки | `blockers` | 12 | [Open](#module-blockers) |
| Связи карточек | `card_relations` | 10 | [Open](#module-card-relations) |
| Внешние ссылки | `external_links` | 4 | [Open](#module-external-links) |
| Файлы карточек | `files` | 18 | [Open](#module-files) |
| Подписчики | `subscribers` | 6 | [Open](#module-subscribers) |
| Пространства | `spaces` | 6 | [Open](#module-spaces) |
| Доски | `boards` | 6 | [Open](#module-boards) |
| Колонки и подколонки | `columns` | 8 | [Open](#module-columns) |
| Дорожки | `lanes` | 4 | [Open](#module-lanes) |
| Типы карточек | `card_types` | 8 | [Open](#module-card-types) |
| Каталоги / Custom directories | `custom_directories` | 16 | [Open](#module-custom-directories) |
| Кастомные свойства | `custom_properties` | 25 | [Open](#module-custom-properties) |
| Документы | `documents` | 13 | [Open](#module-documents) |
| Дашборды | `dashboards` | 16 | [Open](#module-dashboards) |
| Итерации | `iterations` | 9 | [Open](#module-iterations) |
| Вебхуки | `webhooks` | 9 | [Open](#module-webhooks) |
| Автоматизации и воркфлоу | `automations` | 11 | [Open](#module-automations) |
| Аддоны | `addons` | 10 | [Open](#module-addons) |
| GitHub-аддон | `github_addon` | 12 | [Open](#module-github-addon) |
| Проекты и спринты | `projects` | 13 | [Open](#module-projects) |
| Роли и группы | `roles_and_groups` | 31 | [Open](#module-roles-and-groups) |
| SCIM | `scim` | 8 | [Open](#module-scim) |
| Аудит и аналитика | `audit_and_analytics` | 12 | [Open](#module-audit-and-analytics) |
| Service Desk | `service_desk` | 47 | [Open](#module-service-desk) |
| Графики и аналитика | `charts` | 15 | [Open](#module-charts) |
| Дерево сущностей | `tree` | 9 | [Open](#module-tree) |
| Утилиты | `utilities` | 15 | [Open](#module-utilities) |
| Локальные snapshots | `snapshot` | 5 | [Open](#module-snapshot) |
| Локальные запросы | `query` | 2 | [Open](#module-query) |

## Full Reference

<a id="module-cards"></a>
## Карточки (`cards`) — 15 commands

Карточки, bulk reads и card-heavy workflows.

**Namespace tree**

```text
card-allowed-users
  list
card-baselines
  list
card-service-desk-external-recipients
  add
  remove
cards
  archive
  batch-get
  batch-update
  create
  delete
  get
  list
  list-all
  move
  move-by-url
  update
```

### `card-allowed-users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-allowed-users list` |
| MCP alias | `kaiten_list_card_allowed_users` |
| Description | List one page of users allowed to access a card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/allowed-users` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID. |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default 50, max 100). |
| `offset` | `integer` | no | — | >= 0 | Pagination offset. |

**Examples**

- List card allowed users.: `kaiten --json card-allowed-users list --card-id 123 --compact`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This direct command returns one page; increase offset to read subsequent pages.

### `card-baselines.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-baselines list` |
| MCP alias | `kaiten_list_card_baselines` |
| Description | List card baselines. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/baselines` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID. |

**Examples**

- List baselines for a card.: `kaiten --json card-baselines list --card-id 123`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-service-desk-external-recipients.add`

| Field | Value |
|---|---|
| CLI command | `kaiten card-service-desk-external-recipients add` |
| MCP alias | `kaiten_add_card_sd_external_recipient` |
| Description | Add a Service Desk external recipient to a card. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/sd-external-recipients` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID. |
| `email` | `string` | yes | — | — | External recipient email. |
| `name` | `string` | no | — | — | External recipient display name. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Add a Service Desk external recipient.: `kaiten --json card-service-desk-external-recipients add --card-id 123 --email user@example.com`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-service-desk-external-recipients.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten card-service-desk-external-recipients remove` |
| MCP alias | `kaiten_remove_card_sd_external_recipient` |
| Description | Remove a Service Desk external recipient from a card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/sd-external-recipients/{email}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID. |
| `email` | `string` | yes | — | — | External recipient email. |

**Examples**

- Remove a Service Desk external recipient.: `kaiten --json card-service-desk-external-recipients remove --card-id 123 --email user@example.com`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `cards.archive`

| Field | Value |
|---|---|
| CLI command | `kaiten cards archive` |
| MCP alias | `kaiten_archive_card` |
| Description | Archive a Kaiten card (set condition to archived). |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer|string` | yes | — | — | Card ID or key |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, nested user objects) |
| `fields` | `string` | no | — | — | Comma-separated field names to keep in the response. Example: 'id,title,state' |

**Examples**

- Archive a card.: `kaiten cards archive --card-id 123`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `cards.batch-get`

| Field | Value |
|---|---|
| CLI command | `kaiten cards batch-get` |
| MCP alias | `kaiten_batch_get_cards` |
| Description | Fetch multiple cards by ID with bounded worker concurrency. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `aggregated` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/cards/batch` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_ids` | `array` | yes | — | — | Card IDs to fetch |
| `workers` | `integer` | no | — | — | Parallel workers (default 2, max 6) |
| `compact` | `boolean` | no | — | — | Strip heavy nested fields from card payloads |
| `fields` | `string` | no | — | — | Comma-separated card field names to keep |

**Examples**

- Fetch several cards in one CLI call.: `kaiten --json cards batch-get --card-ids '[1,2,3]'`
- Fetch narrowed card detail payloads with bounded concurrency.: `kaiten --json cards batch-get --card-ids '[1,2,3]' --workers 2 --compact --fields id,title,state,description`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.
- Use this bulk path for detail enrichment after local candidate reduction or before building evidence-heavy snapshots.

### `cards.batch-update`

| Field | Value |
|---|---|
| CLI command | `kaiten cards batch-update` |
| MCP alias | `kaiten_batch_update_cards` |
| Description | Batch update cards matching criteria. Kaiten runs the update as a background job. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `board_id` | `integer` | no | — | — | Criteria board ID. |
| `column_id` | `integer` | no | — | — | Criteria column ID. |
| `lane_id` | `integer` | no | — | — | Criteria lane ID. |
| `owner_id` | `integer` | no | — | — | Criteria owner user ID. |
| `type_id` | `integer` | no | — | — | Criteria card type ID. |
| `condition` | `integer` | no | `1`, `2` | — | Criteria condition: 1=active, 2=archived. |
| `attributes` | `object` | yes | — | — | Attributes to change on matching cards. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Batch update matching cards.: `kaiten --json cards batch-update --board-id 10 --attributes '{"owner_id":7}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This endpoint updates all cards matching the criteria and returns a background job ID.
- Use narrow criteria first; this is intentionally separate from per-card cards.update.

### `cards.create`

| Field | Value |
|---|---|
| CLI command | `kaiten cards create` |
| MCP alias | `kaiten_create_card` |
| Description | Create a new Kaiten card. Title max 1024 chars, description max 32768 chars. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `title` | `string` | yes | — | — | Card title (1-1024 chars) |
| `board_id` | `integer` | yes | — | — | Target board ID |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, nested user objects) |
| `fields` | `string` | no | — | — | Comma-separated field names to keep in the response. Example: 'id,title,state' |
| `column_id` | `integer` | no | — | — | Target column ID |
| `lane_id` | `integer` | no | — | — | Target lane ID |
| `description` | `string` | no | — | — | Card description (max 32768) |
| `due_date` | `string|null` | no | — | — | Deadline (ISO 8601) |
| `asap` | `boolean` | no | — | — | ASAP marker |
| `size_text` | `string` | no | — | — | Size (e.g. S, M, L, 1, 23.45) |
| `owner_id` | `integer` | no | — | — | Owner user ID |
| `type_id` | `integer` | no | — | — | Card type ID |
| `external_id` | `string` | no | — | — | External ID (max 1024) |
| `sort_order` | `number` | no | — | — | Position in cell |
| `position` | `integer` | no | `1`, `2` | — | 1=first, 2=last in cell |
| `properties` | `object` | no | — | — | Custom properties as {id_N: value} |
| `tags` | `array` | no | — | — | Tags to attach |
| `sprint_id` | `integer` | no | — | — | Sprint ID to assign card to |
| `planned_start` | `string|null` | no | — | — | Planned start date (ISO 8601) |
| `planned_end` | `string|null` | no | — | — | Planned end date (ISO 8601) |
| `responsible_id` | `integer` | no | — | — | Responsible user ID |
| `condition` | `integer` | no | `1`, `2` | — | 1=active, 2=archived |
| `due_date_time_present` | `boolean` | no | — | — | True if due_date includes time component |
| `expires_later` | `boolean` | no | — | — | Expires later flag |
| `estimate_workload` | `integer` | no | — | — | Estimated workload in minutes (resource planning) |
| `child_card_ids` | `array` | no | — | — | Child card IDs to link (max 1) |
| `parent_card_ids` | `array` | no | — | — | Parent card IDs to link (max 1) |
| `project_id` | `string` | no | — | — | Project UUID to attach card to |

**Examples**

- Create a card.: `kaiten --json cards create --title "Smoke task" --board-id 10`
- Create a card with a narrow response.: `kaiten --json cards create --title "Smoke task" --board-id 10 --compact --fields id,title,state`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `cards.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten cards delete` |
| MCP alias | `kaiten_delete_card` |
| Description | Soft-delete a Kaiten card (sets condition to deleted). Cards with time logs cannot be deleted. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer|string` | yes | — | — | Card ID or key |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, nested user objects) |
| `fields` | `string` | no | — | — | Comma-separated field names to keep in the response. Example: 'id,title,state' |

**Examples**

- Delete a card.: `kaiten cards delete --card-id 123`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `cards.get`

| Field | Value |
|---|---|
| CLI command | `kaiten cards get` |
| MCP alias | `kaiten_get_card` |
| Description | Get a Kaiten card by ID. Supports numeric ID or card key (e.g. PROJ-123). |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/cards/{card_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer|string` | yes | — | — | Card ID or key (e.g. PROJ-123) |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, nested user objects) |
| `fields` | `string` | no | — | — | Comma-separated field names to keep in the response. Example: 'id,title,state' |
| `markdown` | `boolean` | no | — | — | Save the card as Markdown instead of returning JSON. |
| `output` | `string` | no | — | — | Markdown output file or directory. Defaults to the current working directory. |
| `overwrite` | `boolean` | no | — | — | Replace an existing Markdown output file. |

**Examples**

- Get a card by numeric ID.: `kaiten cards get --card-id 123`
- Get a narrow card response.: `kaiten --json cards get --card-id 123 --compact --fields id,title,state`
- Save a card as Markdown.: `kaiten --json cards get --card-id 123 --markdown --output ./card.md`

**Notes**

- Bulk alternative: `cards.batch-get`
- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This is a per-card entity read and becomes expensive when repeated over large card populations.
- For detail enrichment after candidate reduction, prefer cards.batch-get over one-card-at-a-time loops.
- `--markdown` does the same card GET, renders the result locally, and saves a Markdown file instead of returning the card JSON.
- `--markdown` keeps card attachment links as Kaiten `/api/cards/<card>/files/<file_id>` URLs.
- Use `--output` for the target file/directory and `--overwrite` to replace an existing Markdown file.
- Separate CLI processes do not share in-memory results, so default `--cache-mode auto` persists repeated safe card reads.

### `cards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten cards list` |
| MCP alias | `kaiten_list_cards` |
| Description | Search and list Kaiten cards with filtering. Conditions: 1=active, 2=archived. States: 1=queued, 2=inProgress, 3=done. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Full-text search query |
| `space_id` | `integer` | no | — | — | Filter by space ID |
| `board_id` | `integer` | no | — | — | Filter by board ID |
| `column_id` | `integer` | no | — | — | Filter by column ID |
| `lane_id` | `integer` | no | — | — | Filter by lane ID |
| `condition` | `integer` | no | `1`, `2` | — | 1=active, 2=archived |
| `type_id` | `integer` | no | — | — | Filter by card type ID |
| `owner_id` | `integer` | no | — | — | Filter by owner user ID |
| `responsible_id` | `integer` | no | — | — | Filter by responsible user ID |
| `tag_ids` | `string` | no | — | — | Comma-separated tag IDs |
| `member_ids` | `string` | no | — | — | Comma-separated member IDs |
| `states` | `string` | no | — | — | Comma-separated states (1=queued,2=inProgress,3=done) |
| `created_after` | `string` | no | — | — | ISO datetime filter |
| `created_before` | `string` | no | — | — | ISO datetime filter |
| `updated_after` | `string` | no | — | — | ISO datetime filter |
| `updated_before` | `string` | no | — | — | ISO datetime filter |
| `first_moved_in_progress_after` | `string` | no | — | — | ISO datetime filter for first move into in-progress state |
| `first_moved_in_progress_before` | `string` | no | — | — | ISO datetime filter for first move into in-progress state |
| `last_moved_to_done_at_after` | `string` | no | — | — | ISO datetime filter for last move to done column |
| `last_moved_to_done_at_before` | `string` | no | — | — | ISO datetime filter for last move to done column |
| `due_date_after` | `string` | no | — | — | ISO datetime filter |
| `due_date_before` | `string` | no | — | — | ISO datetime filter |
| `tag` | `string` | no | — | — | Filter by tag name |
| `type_ids` | `string` | no | — | — | Comma-separated card type IDs |
| `owner_ids` | `string` | no | — | — | Comma-separated owner user IDs |
| `responsible_ids` | `string` | no | — | — | Comma-separated responsible user IDs |
| `column_ids` | `string` | no | — | — | Comma-separated column IDs |
| `exclude_board_ids` | `string` | no | — | — | Comma-separated board IDs to exclude |
| `exclude_lane_ids` | `string` | no | — | — | Comma-separated lane IDs to exclude |
| `exclude_column_ids` | `string` | no | — | — | Comma-separated column IDs to exclude |
| `exclude_owner_ids` | `string` | no | — | — | Comma-separated owner IDs to exclude |
| `exclude_card_ids` | `string` | no | — | — | Comma-separated card IDs to exclude |
| `organization_ids` | `string` | no | — | — | Comma-separated Service Desk organization IDs |
| `additional_card_fields` | `string` | no | — | — | Comma-separated extra fields to request. Supported by API: description |
| `search_fields` | `string` | no | — | — | Comma-separated fields to search in for version=2 |
| `start_position` | `string` | no | — | — | Search cursor for version=2 pagination |
| `filter` | `string` | no | — | — | Encoded Kaiten filter query |
| `order_by` | `string` | no | — | — | Sort field list |
| `order_direction` | `string` | no | — | — | Sort direction list |
| `external_id` | `string` | no | — | — | External ID filter |
| `version` | `integer` | no | — | — | Search version. Use 2 for OpenSearch result/position response. |
| `overdue` | `boolean` | no | — | — | Filter overdue cards |
| `asap` | `boolean` | no | — | — | Filter ASAP cards |
| `done_on_time` | `boolean` | no | — | — | Filter cards done on time |
| `with_due_date` | `boolean` | no | — | — | Filter cards with due date |
| `is_request` | `boolean` | no | — | — | Filter Service Desk request cards |
| `include_search_preview` | `boolean` | no | — | — | Include search preview objects for version=2 |
| `visible` | `string` | no | — | — | JSON-encoded visibility filter |
| `archived` | `boolean` | no | — | — | Include archived |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default 50, max 100) |
| `offset` | `integer` | no | — | >= 0 | Pagination offset |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, nested user objects) |
| `relations` | `string` | no | — | — | Comma-separated relations to include (members,type,custom_properties,...) or 'none' to exclude all. Default: include all. |
| `fields` | `string` | no | — | — | Comma-separated field names to return per card. Strips everything else. Example: 'id,title,created,last_moved_to_done_at' |

**Examples**

- List cards on a board.: `kaiten --json cards list --board-id 10 --limit 5 --compact`
- Search cards by query.: `kaiten cards list --query "bug" --fields id,title,state`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `cards.list-all`

| Field | Value |
|---|---|
| CLI command | `kaiten cards list-all` |
| MCP alias | `kaiten_list_all_cards` |
| Description | Fetch all cards matching filters with automatic pagination. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `aggregated` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/cards` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Full-text search query |
| `space_id` | `integer` | no | — | — | Filter by space ID |
| `board_id` | `integer` | no | — | — | Filter by board ID |
| `column_id` | `integer` | no | — | — | Filter by column ID |
| `lane_id` | `integer` | no | — | — | Filter by lane ID |
| `condition` | `integer` | no | `1`, `2` | — | 1=active, 2=archived |
| `type_id` | `integer` | no | — | — | Filter by card type ID |
| `owner_id` | `integer` | no | — | — | Filter by owner user ID |
| `responsible_id` | `integer` | no | — | — | Filter by responsible user ID |
| `tag_ids` | `string` | no | — | — | Comma-separated tag IDs |
| `member_ids` | `string` | no | — | — | Comma-separated member IDs |
| `states` | `string` | no | — | — | Comma-separated states (1=queued,2=inProgress,3=done) |
| `created_after` | `string` | no | — | — | ISO datetime filter |
| `created_before` | `string` | no | — | — | ISO datetime filter |
| `updated_after` | `string` | no | — | — | ISO datetime filter |
| `updated_before` | `string` | no | — | — | ISO datetime filter |
| `first_moved_in_progress_after` | `string` | no | — | — | ISO datetime filter for first move into in-progress state |
| `first_moved_in_progress_before` | `string` | no | — | — | ISO datetime filter for first move into in-progress state |
| `last_moved_to_done_at_after` | `string` | no | — | — | ISO datetime filter for last move to done column |
| `last_moved_to_done_at_before` | `string` | no | — | — | ISO datetime filter for last move to done column |
| `due_date_after` | `string` | no | — | — | ISO datetime filter |
| `due_date_before` | `string` | no | — | — | ISO datetime filter |
| `tag` | `string` | no | — | — | Filter by tag name |
| `type_ids` | `string` | no | — | — | Comma-separated type IDs |
| `owner_ids` | `string` | no | — | — | Comma-separated owner IDs |
| `responsible_ids` | `string` | no | — | — | Comma-separated responsible IDs |
| `column_ids` | `string` | no | — | — | Comma-separated column IDs |
| `exclude_board_ids` | `string` | no | — | — | Comma-separated board IDs to exclude |
| `exclude_lane_ids` | `string` | no | — | — | Comma-separated lane IDs to exclude |
| `exclude_column_ids` | `string` | no | — | — | Comma-separated column IDs to exclude |
| `exclude_owner_ids` | `string` | no | — | — | Comma-separated owner IDs to exclude |
| `exclude_card_ids` | `string` | no | — | — | Comma-separated card IDs to exclude |
| `organization_ids` | `string` | no | — | — | Comma-separated Service Desk organization IDs |
| `additional_card_fields` | `string` | no | — | — | Comma-separated extra fields to request. Supported by API: description |
| `search_fields` | `string` | no | — | — | Comma-separated fields to search in for version=2 |
| `start_position` | `string` | no | — | — | Search cursor for version=2 pagination |
| `filter` | `string` | no | — | — | Encoded Kaiten filter query |
| `order_by` | `string` | no | — | — | Sort field list |
| `order_direction` | `string` | no | — | — | Sort direction list |
| `external_id` | `string` | no | — | — | External ID filter |
| `version` | `integer` | no | — | — | Search version. Use 2 for OpenSearch result/position response. |
| `overdue` | `boolean` | no | — | — | Filter overdue cards |
| `asap` | `boolean` | no | — | — | Filter ASAP cards |
| `done_on_time` | `boolean` | no | — | — | Filter cards done on time |
| `with_due_date` | `boolean` | no | — | — | Filter cards with due date |
| `is_request` | `boolean` | no | — | — | Filter Service Desk request cards |
| `include_search_preview` | `boolean` | no | — | — | Include search preview objects for version=2 |
| `visible` | `string` | no | — | — | JSON-encoded visibility filter |
| `archived` | `boolean` | no | — | — | Include archived |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default 50, max 100) |
| `offset` | `integer` | no | — | >= 0 | Pagination offset |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (default true for bulk) |
| `relations` | `string` | no | — | — | Relations to include or 'none' to exclude all nested objects (default 'none' for bulk). |
| `fields` | `string` | no | — | — | Comma-separated field names to return per card after pagination. |
| `selection` | `string` | no | `all`, `active_only`, `archived_only` | — | Normalized bulk selection: all, active_only, or archived_only. |
| `page_size` | `integer` | no | — | >= 1, <= 100 | Cards per page (default 100, max 100) |
| `max_pages` | `integer` | no | — | >= 1, <= 1000 | Safety limit on pages to fetch (default 50, max 1000) |

**Examples**

- Fetch all matching cards with bounded pagination.: `kaiten --json cards list-all --board-id 10 --page-size 20 --max-pages 2`
- Fetch only active cards via normalized bulk selection.: `kaiten --json cards list-all --board-id 10 --selection active_only --fields id,title`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- For bulk reads, prefer selection=all|active_only|archived_only over raw archived/condition filters.
- active_only is computed as all_cards minus the archived subset to match the documented bulk CLI behavior.
- If max_pages is reached on a full page, the command fails instead of returning a partial card list.

### `cards.move`

| Field | Value |
|---|---|
| CLI command | `kaiten cards move` |
| MCP alias | `kaiten_move_card` |
| Description | Move a Kaiten card to a different board, column, or lane. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer|string` | yes | — | — | Card ID or key |
| `board_id` | `integer` | no | — | — | Target board ID |
| `column_id` | `integer` | no | — | — | Target column ID |
| `lane_id` | `integer` | no | — | — | Target lane ID |
| `sort_order` | `number` | no | — | — | Position in cell |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, nested user objects) |
| `fields` | `string` | no | — | — | Comma-separated field names to keep in the response. Example: 'id,title,state' |

**Examples**

- Move a card.: `kaiten --json cards move --card-id 123 --column-id 10`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `cards.move-by-url`

| Field | Value |
|---|---|
| CLI command | `kaiten cards move-by-url` |
| MCP alias | `kaiten_move_card_by_url` |
| Description | Move a Kaiten card by resolving card and target Kaiten UI URLs. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `aggregated` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/move-by-url` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_url` | `string` | yes | — | — | Kaiten card URL containing /boards/card/<id-or-key> |
| `target_url` | `string` | yes | — | — | Kaiten board URL with focus=column and focusId=<column_id> |
| `lane_id` | `integer` | no | — | — | Target lane ID; required for boards with multiple lanes. |
| `sort_order` | `number` | no | — | — | Position in cell |
| `dry_run` | `boolean` | no | — | — | Resolve the move target without patching the card |
| `verify` | `boolean` | no | — | — | Fetch the card after moving and verify its final location |
| `compact` | `boolean` | no | — | — | Return compact card response without heavy fields |
| `fields` | `string` | no | — | — | Comma-separated card fields to keep inside the returned card |

**Examples**

- Move a card by resolving card and target UI URLs.: `kaiten --json cards move-by-url --card-url "https://hq.kaiten.ru/space/1/boards/card/STORY-1" --target-url "https://hq.kaiten.ru/space/2/boards?focus=column&focusId=10" --lane-id 20`
- Preview the resolved move target without changing the card.: `kaiten --json cards move-by-url --card-url "https://hq.kaiten.ru/space/1/boards/card/STORY-1" --target-url "https://hq.kaiten.ru/space/2/boards?focus=column&focusId=10" --dry-run`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The command does discovery inside the target space, then calls cards.move semantics.
- URL hosts must match the resolved profile domain; profiles are not auto-selected.
- When the target board has multiple lanes, pass --lane-id explicitly.
- `--fields` and `--compact` apply to the returned card inside the result envelope.

### `cards.update`

| Field | Value |
|---|---|
| CLI command | `kaiten cards update` |
| MCP alias | `kaiten_update_card` |
| Description | Update a Kaiten card. Use condition=2 to archive, set column_id/board_id to move. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer|string` | yes | — | — | Card ID or key |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, nested user objects) |
| `fields` | `string` | no | — | — | Comma-separated field names to keep in the response. Example: 'id,title,state' |
| `title` | `string` | no | — | — | New title |
| `description` | `string|null` | no | — | — | New description |
| `board_id` | `integer` | no | — | — | Move to board |
| `column_id` | `integer` | no | — | — | Move to column |
| `lane_id` | `integer` | no | — | — | Move to lane |
| `sort_order` | `number` | no | — | — | Position in cell |
| `owner_id` | `integer` | no | — | — | New owner user ID |
| `type_id` | `integer` | no | — | — | Card type ID |
| `condition` | `integer` | no | `1`, `2` | — | 1=active, 2=archived |
| `due_date` | `string|null` | no | — | — | Deadline (ISO 8601 or null) |
| `asap` | `boolean` | no | — | — | ASAP marker |
| `size_text` | `string|null` | no | — | — | Size |
| `blocked` | `boolean` | no | — | — | Set to false to unblock |
| `external_id` | `string|null` | no | — | — | External ID |
| `properties` | `object` | no | — | — | Custom properties as {id_N: value} |
| `sprint_id` | `integer|null` | no | — | — | Sprint ID (null to remove) |
| `planned_start` | `string|null` | no | — | — | Planned start date (ISO 8601) |
| `planned_end` | `string|null` | no | — | — | Planned end date (ISO 8601) |
| `state` | `integer` | no | `1`, `2`, `3` | — | Card state: 1=queued, 2=inProgress, 3=done |
| `block_reason` | `string|null` | no | — | — | Block reason text (null to clear) |
| `locked` | `string|null` | no | — | — | Lock identifier (null to unlock) |
| `due_date_time_present` | `boolean` | no | — | — | True if due_date includes time component |
| `expires_later` | `boolean` | no | — | — | Expires later flag |
| `estimate_workload` | `integer` | no | — | — | Estimated workload in minutes (resource planning) |
| `child_card_ids` | `array` | no | — | — | Child card IDs to link |
| `parent_card_ids` | `array` | no | — | — | Parent card IDs to link |

**Examples**

- Update a card.: `kaiten cards update --card-id 123 --title "Renamed"`
- Update a card with a narrow response.: `kaiten --json cards update --card-id 123 --title "Renamed" --compact --fields id,title,state`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `aggregated` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/cards/comments/batch` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_ids` | `array` | yes | — | — | Card IDs to inspect |
| `workers` | `integer` | no | — | — | Parallel workers (default 2, max 6) |
| `page_size` | `integer` | no | — | >= 1, <= 100 | Comments per request (default 100, max 100). |
| `max_pages` | `integer` | no | — | >= 1, <= 1000 | Safety limit per card (default 100, max 1000). |
| `compact` | `boolean` | no | — | — | Strip heavy fields from comment payloads |
| `fields` | `string` | no | — | — | Comma-separated field names to keep for each comment |

**Examples**

- Fetch comments for several cards in one CLI call.: `kaiten --json comments batch-list --card-ids '[1,2,3]'`
- Fetch narrowed comment payloads with bounded concurrency.: `kaiten --json comments batch-list --card-ids '[1,2,3]' --workers 2 --compact --fields id,text`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.
- Each card is paginated to completion; a full max_pages boundary becomes a per-card error instead of a partial comment list.
- Use this bulk path when you need comment evidence across many cards.

### `comments.create`

| Field | Value |
|---|---|
| CLI command | `kaiten comments create` |
| MCP alias | `kaiten_create_comment` |
| Description | Add a comment to a card. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/comments` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card to comment on. |
| `text` | `string` | yes | — | — | Comment text. For format=html send HTML content. |
| `format` | `string` | no | `markdown`, `html` | — | Comment format. 'markdown' (default) stores raw markdown, 'html' switches the request to HTML mode. |
| `internal` | `boolean` | no | — | — | Mark the comment as internal (visible only to team). |

**Examples**

- Create a markdown comment.: `kaiten --json comments create --card-id 10 --text "Looks good"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `comments.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten comments delete` |
| MCP alias | `kaiten_delete_comment` |
| Description | Delete a comment from a card (author only). |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/comments/{comment_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `comment_id` | `integer` | yes | — | — | ID of the comment to delete. |

**Examples**

- Delete a comment.: `kaiten --json comments delete --card-id 10 --comment-id 20`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `comments.list`

| Field | Value |
|---|---|
| CLI command | `kaiten comments list` |
| MCP alias | `kaiten_list_comments` |
| Description | List one page of comments on a card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/comments` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card whose comments to list. |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default 50, max 100). |
| `offset` | `integer` | no | — | >= 0 | Pagination offset. |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, nested user objects). |

**Examples**

- List comments on a card.: `kaiten --json comments list --card-id 10 --compact`

**Notes**

- Bulk alternative: `comments.batch-list`
- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This direct command returns one page; increase offset to read subsequent pages.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/comments/{comment_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `comment_id` | `integer` | yes | — | — | ID of the comment to update. |
| `text` | `string` | yes | — | — | New comment text. For format=html send HTML content. |
| `format` | `string` | no | `markdown`, `html` | — | Comment format. 'html' switches the request to HTML mode, 'markdown' switches back to markdown. |

**Examples**

- Update a comment.: `kaiten --json comments update --card-id 10 --comment-id 20 --text "Updated"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

<a id="module-members"></a>
## Участники и пользователи (`members`) — 7 commands

Участники карточек, пользователи, группы и space users.

**Namespace tree**

```text
card-members
  add
  list
  remove
  update
users
  current
  list
  update
```

### `card-members.add`

| Field | Value |
|---|---|
| CLI command | `kaiten card-members add` |
| MCP alias | `kaiten_add_card_member` |
| Description | Add a member to a card. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/members` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `user_id` | `integer` | yes | — | — | ID of the user to add as a member. |

**Examples**

- Add a member to a card.: `kaiten --json card-members add --card-id 10 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-members.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-members list` |
| MCP alias | `kaiten_list_card_members` |
| Description | List all members assigned to a card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/members` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, etc.). |

**Examples**

- List members on a card.: `kaiten --json card-members list --card-id 10 --compact`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-members.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten card-members remove` |
| MCP alias | `kaiten_remove_card_member` |
| Description | Remove a member from a card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/members/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `user_id` | `integer` | yes | — | — | ID of the user to remove. |

**Examples**

- Remove a member from a card.: `kaiten --json card-members remove --card-id 10 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-members.update`

| Field | Value |
|---|---|
| CLI command | `kaiten card-members update` |
| MCP alias | `kaiten_update_card_member` |
| Description | Update a card member role. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/members/{member_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `member_id` | `integer` | yes | — | — | Card member ID from Kaiten. |
| `role_id` | `string` | no | — | — | Role ID to assign. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Update a card member role.: `kaiten --json card-members update --card-id 10 --member-id 7 --role-id role-uuid`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `users.current`

| Field | Value |
|---|---|
| CLI command | `kaiten users current` |
| MCP alias | `kaiten_get_current_user` |
| Description | Get the current authenticated Kaiten user profile. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/users/current` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- Get the current user.: `kaiten --json users current`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten users list` |
| MCP alias | `kaiten_list_users` |
| Description | List users from the generic /users endpoint. For paginated administrative Members exports, prefer company-users.list. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/users` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `type` | `string` | no | `all`, `shared`, `domain` | — | User visibility scope supported by the Kaiten API. |
| `query` | `string` | no | — | — | Search filter for user names or emails. |
| `access_type_permissions` | `string` | no | `member`, `guest` | — | Filter by Kaiten access type when supported by the endpoint. |
| `ids` | `string` | no | — | — | Comma-separated user IDs. |
| `uids` | `string` | no | — | — | Comma-separated user UUIDs. |
| `exclude_directly_added_members_by_entity_uid` | `string` | no | — | — | Exclude users directly added to the given entity UID. |
| `limit` | `integer` | no | — | — | Maximum number of users to return (default 50). |
| `offset` | `integer` | no | — | — | Number of users to skip (for pagination). |
| `include_inactive` | `boolean` | no | — | — | Include inactive (deactivated) users in results. |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, etc.). |

**Examples**

- Search users by name.: `kaiten --json users list --query "alice" --compact`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This command maps to `/users`. Use `company-users.list` for the paginated administrative Members section (`/company/users?for_members_section=true`).

### `users.update`

| Field | Value |
|---|---|
| CLI command | `kaiten users update` |
| MCP alias | `kaiten_update_user` |
| Description | Update a user. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `user_id` | `integer` | yes | — | — | User ID. |
| `full_name` | `string` | no | — | — | Full name. |
| `email` | `string` | no | — | — | Email. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Update a user.: `kaiten --json users update --user-id 7 --full-name "Alice Smith"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

<a id="module-time-logs"></a>
## Логи времени (`time_logs`) — 6 commands

Time logs, work logs и related analytics inputs.

**Namespace tree**

```text
time-logs
  batch-list
  create
  delete
  list
  update
timesheet
  list
```

### `time-logs.batch-list`

| Field | Value |
|---|---|
| CLI command | `kaiten time-logs batch-list` |
| MCP alias | `kaiten_batch_list_time_logs` |
| Description | Fetch time logs for multiple cards with bounded worker concurrency. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `aggregated` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/cards/time-logs/batch` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_ids` | `array` | yes | — | — | Card IDs to inspect |
| `workers` | `integer` | no | — | — | Parallel workers (default 2, max 6) |
| `page_size` | `integer` | no | — | >= 1, <= 100 | Time logs per request (default 100, max 100). |
| `max_pages` | `integer` | no | — | >= 1, <= 1000 | Safety limit per card (default 100, max 1000). |
| `for_date` | `string` | no | — | — | Optional YYYY-MM-DD filter passed to each per-card request. |
| `personal` | `boolean` | no | — | — | Only include the current user's time logs. |
| `compact` | `boolean` | no | — | — | Strip heavy nested fields from time-log payloads |
| `fields` | `string` | no | — | — | Comma-separated field names to keep for each time log |

**Examples**

- Fetch time logs for several cards in one CLI call.: `kaiten --json time-logs batch-list --card-ids '[1,2,3]'`
- Fetch narrowed time-log payloads with bounded concurrency.: `kaiten --json time-logs batch-list --card-ids '[1,2,3]' --workers 2 --fields id,time_spent,for_date`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.
- Each card is paginated to completion; a full max_pages boundary becomes a per-card error instead of a partial time-log list.
- Use this bulk path for work-log analytics and snapshot builds instead of repeating time-logs.list for every card.

### `time-logs.create`

| Field | Value |
|---|---|
| CLI command | `kaiten time-logs create` |
| MCP alias | `kaiten_create_time_log` |
| Description | Log time spent on a card. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/time-logs` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `time_spent` | `integer` | yes | — | — | Time spent in minutes (minimum 1). |
| `role_id` | `integer` | no | — | — | Role ID for the time log. Use -1 for the default role. |
| `for_date` | `string` | no | — | — | Date for the time log (YYYY-MM-DD). Defaults to today. |
| `comment` | `string` | no | — | — | Optional comment for the time log. |

**Examples**

- Create a time log entry.: `kaiten --json time-logs create --card-id 10 --time-spent 15 --comment "Analysis"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `time-logs.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten time-logs delete` |
| MCP alias | `kaiten_delete_time_log` |
| Description | Delete a time log entry from a card (author only). |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/time-logs/{time_log_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `time_log_id` | `integer` | yes | — | — | ID of the time log to delete. |

**Examples**

- Delete a time log.: `kaiten --json time-logs delete --card-id 10 --time-log-id 20`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `time-logs.list`

| Field | Value |
|---|---|
| CLI command | `kaiten time-logs list` |
| MCP alias | `kaiten_list_card_time_logs` |
| Description | List one page of time logs for a card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/time-logs` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `for_date` | `string` | no | — | — | Filter by date (YYYY-MM-DD). |
| `personal` | `boolean` | no | — | — | Return only the current user's time logs. |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default 50, max 100). |
| `offset` | `integer` | no | — | >= 0 | Pagination offset. |
| `compact` | `boolean` | no | — | — | Strip heavy nested fields from time-log payloads. |
| `fields` | `string` | no | — | — | Comma-separated field names to keep for each time log. |

**Examples**

- List time logs on a card.: `kaiten --json time-logs list --card-id 10`

**Notes**

- Bulk alternative: `time-logs.batch-list`
- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This direct command returns one page; increase offset to read subsequent pages.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/time-logs/{time_log_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `time_log_id` | `integer` | yes | — | — | ID of the time log to update. |
| `time_spent` | `integer` | no | — | — | Updated time spent in minutes. |
| `role_id` | `integer` | no | — | — | Updated role ID. |
| `comment` | `string` | no | — | — | Updated comment. |
| `for_date` | `string` | no | — | — | Updated date (YYYY-MM-DD). |

**Examples**

- Update a time log.: `kaiten --json time-logs update --card-id 10 --time-log-id 20 --time-spent 20`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `timesheet.list`

| Field | Value |
|---|---|
| CLI command | `kaiten timesheet list` |
| MCP alias | `kaiten_list_timesheet` |
| Description | List time logs across cards from the company timesheet endpoint. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/time-logs` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `user_id` | `integer` | no | — | — | Filter by user ID. |
| `card_id` | `integer` | no | — | — | Filter by card ID. |
| `for_date` | `string` | no | — | — | Filter by date (YYYY-MM-DD). |
| `date_from` | `string` | no | — | — | Start date filter. |
| `date_to` | `string` | no | — | — | End date filter. |
| `limit` | `integer` | no | — | — | Max results. |
| `offset` | `integer` | no | — | — | Pagination offset. |
| `compact` | `boolean` | no | — | — | Strip heavy nested fields from time-log payloads. |
| `fields` | `string` | no | — | — | Comma-separated field names to keep for each time log. |

**Examples**

- List company time logs.: `kaiten --json timesheet list --limit 50`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

<a id="module-tags"></a>
## Теги (`tags`) — 7 commands

Теги и операции привязки тегов к карточкам.

**Namespace tree**

```text
card-tags
  add
  list
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/tags` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `name` | `string` | yes | — | — | Tag name (1-255 chars) |

**Examples**

- Add a tag to a card.: `kaiten --json card-tags add --card-id 10 --name "backend"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-tags.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-tags list` |
| MCP alias | `kaiten_list_card_tags` |
| Description | List tags attached to a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/tags` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |

**Examples**

- List tags on a card.: `kaiten --json card-tags list --card-id 10`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-tags.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten card-tags remove` |
| MCP alias | `kaiten_remove_card_tag` |
| Description | Remove a tag from a Kaiten card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/tags/{tag_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `tag_id` | `integer` | yes | — | — | Tag ID |

**Examples**

- Remove a tag from a card.: `kaiten --json card-tags remove --card-id 10 --tag-id 20`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `tags.create`

| Field | Value |
|---|---|
| CLI command | `kaiten tags create` |
| MCP alias | `kaiten_create_tag` |
| Description | Create a new Kaiten tag. Color is assigned randomly by the server (1-17). |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/tags` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Tag name (1-255 chars, must be unique within the company) |

**Examples**

- Create a company tag.: `kaiten --json tags create --name "backend"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `tags.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten tags delete` |
| MCP alias | `kaiten_delete_tag` |
| Description | Delete a Kaiten tag. Requires company tag management permission. May be blocked if an async operation is in progress. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/tags/{tag_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `tag_id` | `integer` | yes | — | — | Tag ID |

**Examples**

- Delete a company tag.: `kaiten --json tags delete --tag-id 10`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `tags.list`

| Field | Value |
|---|---|
| CLI command | `kaiten tags list` |
| MCP alias | `kaiten_list_tags` |
| Description | List Kaiten tags. Note: API may return empty for company-level tags; tags are primarily card-scoped. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/tags` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Search filter (matches by name) |
| `space_id` | `integer` | no | — | — | Filter tags by space (only tags used on cards in this space) |
| `ids` | `string` | no | — | — | Comma-separated tag IDs to fetch specific tags |
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- Search tags by name.: `kaiten --json tags list --query "backend"`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `tags.update`

| Field | Value |
|---|---|
| CLI command | `kaiten tags update` |
| MCP alias | `kaiten_update_tag` |
| Description | Update a Kaiten tag (name and/or color). Requires company tag management permission. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/tags/{tag_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `tag_id` | `integer` | yes | — | — | Tag ID |
| `name` | `string` | no | — | — | New tag name (1-255 chars) |
| `color` | `integer` | no | — | — | Color index (1-17) |

**Examples**

- Update a company tag.: `kaiten --json tags update --tag-id 10 --name "backend"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

<a id="module-checklists"></a>
## Чеклисты (`checklists`) — 17 commands

Чеклисты и checklist items.

**Namespace tree**

```text
checklist-cards
  list
checklist-items
  create
  delete
  list
  update
checklists
  create
  delete
  get
  list
  update
space-template-checklist-items
  create
  delete
  update
space-template-checklists
  create
  delete
  list
  update
```

### `checklist-cards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten checklist-cards list` |
| MCP alias | `kaiten_list_checklist_cards` |
| Description | List cards that share a checklist. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/checklists/{checklist_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `checklist_id` | `integer` | yes | — | — | Checklist ID. |
| `only_shared_cards` | `boolean` | no | — | — | Return only shared cards. |

**Examples**

- List cards with a checklist.: `kaiten --json checklist-cards list --checklist-id 20 --only-shared-cards`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `checklist-items.create`

| Field | Value |
|---|---|
| CLI command | `kaiten checklist-items create` |
| MCP alias | `kaiten_create_checklist_item` |
| Description | Create an item in a checklist on a Kaiten card. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/checklists/{checklist_id}/items` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | no | — | — | Optional card ID for the legacy nested route. |
| `checklist_id` | `integer` | yes | — | — | Checklist ID |
| `text` | `string` | yes | — | — | Item text |
| `checked` | `boolean` | no | — | — | Whether the item is checked |
| `sort_order` | `number` | no | — | — | Sort order |
| `user_id` | `integer` | no | — | — | Assigned user ID |
| `due_date` | `string` | no | — | — | Due date (ISO 8601 format) |

**Examples**

- Create a checklist item through the official top-level route.: `kaiten --json checklist-items create --checklist-id 20 --text "Ship it"`
- Create through the compatible legacy nested route.: `kaiten --json checklist-items create --card-id 10 --checklist-id 20 --text "Ship it"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- --card-id is optional and preserves the legacy nested route.

### `checklist-items.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten checklist-items delete` |
| MCP alias | `kaiten_delete_checklist_item` |
| Description | Delete an item from a checklist on a Kaiten card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/checklists/{checklist_id}/items/{item_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | no | — | — | Optional card ID for the legacy nested route. |
| `checklist_id` | `integer` | yes | — | — | Checklist ID |
| `item_id` | `integer` | yes | — | — | Checklist item ID |

**Examples**

- Delete a checklist item.: `kaiten --json checklist-items delete --checklist-id 20 --item-id 30`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- --card-id is optional and preserves the legacy nested route.

### `checklist-items.list`

| Field | Value |
|---|---|
| CLI command | `kaiten checklist-items list` |
| MCP alias | `kaiten_list_checklist_items` |
| Description | List all items in a checklist on a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `synthetic` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `checklist_id` | `integer` | yes | — | — | Checklist ID |

**Examples**

- List checklist items.: `kaiten --json checklist-items list --card-id 10 --checklist-id 20`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Direct checklist item listing is unsupported on sandbox; this command reads the card and extracts items from the matching embedded checklist.
- Live contract: `synthetic_read`; expected statuses: `405`
- Live note: Direct checklist item listing returns 405 on sandbox; the CLI reads GET /cards/{card_id} and extracts embedded checklist items.

### `checklist-items.update`

| Field | Value |
|---|---|
| CLI command | `kaiten checklist-items update` |
| MCP alias | `kaiten_update_checklist_item` |
| Description | Update an item in a checklist on a Kaiten card. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/checklists/{checklist_id}/items/{item_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | no | — | — | Optional card ID for the legacy nested route. |
| `checklist_id` | `integer` | yes | — | — | Checklist ID |
| `item_id` | `integer` | yes | — | — | Checklist item ID |
| `text` | `string` | no | — | — | Item text |
| `checked` | `boolean` | no | — | — | Whether the item is checked |
| `sort_order` | `number` | no | — | — | Sort order |
| `user_id` | `integer` | no | — | — | Assigned user ID |
| `due_date` | `string` | no | — | — | Due date (ISO 8601 format) |

**Examples**

- Update a checklist item.: `kaiten --json checklist-items update --checklist-id 20 --item-id 30 --checked`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- --card-id is optional and preserves the legacy nested route.

### `checklists.create`

| Field | Value |
|---|---|
| CLI command | `kaiten checklists create` |
| MCP alias | `kaiten_create_checklist` |
| Description | Create a checklist on a Kaiten card. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/checklists` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `name` | `string` | yes | — | — | Checklist name |
| `sort_order` | `number` | no | — | — | Sort order |

**Examples**

- Create a checklist.: `kaiten --json checklists create --card-id 10 --name "Ready for QA"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `checklists.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten checklists delete` |
| MCP alias | `kaiten_delete_checklist` |
| Description | Delete a checklist from a Kaiten card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/checklists/{checklist_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `checklist_id` | `integer` | yes | — | — | Checklist ID |

**Examples**

- Delete a checklist.: `kaiten --json checklists delete --card-id 10 --checklist-id 20`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `checklists.get`

| Field | Value |
|---|---|
| CLI command | `kaiten checklists get` |
| MCP alias | `kaiten_get_checklist` |
| Description | Get one checklist with its items from a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/cards/{card_id}/checklists/{checklist_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID. |
| `checklist_id` | `integer` | yes | — | — | Checklist ID. |
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Get one checklist with items.: `kaiten --json checklists get --card-id 10 --checklist-id 20 --fields id,name,items`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `checklists.list`

| Field | Value |
|---|---|
| CLI command | `kaiten checklists list` |
| MCP alias | `kaiten_list_checklists` |
| Description | List all checklists on a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `synthetic` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |

**Examples**

- List checklists on a card.: `kaiten --json checklists list --card-id 10`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Direct checklist listing is unsupported on sandbox; this command reads the card and extracts embedded checklists.
- Live contract: `synthetic_read`; expected statuses: `405`
- Live note: Direct checklist listing returns 405 on sandbox; the CLI reads GET /cards/{card_id} and extracts embedded checklists.

### `checklists.update`

| Field | Value |
|---|---|
| CLI command | `kaiten checklists update` |
| MCP alias | `kaiten_update_checklist` |
| Description | Update a checklist on a Kaiten card. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/checklists/{checklist_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `checklist_id` | `integer` | yes | — | — | Checklist ID |
| `name` | `string` | no | — | — | Checklist name |
| `sort_order` | `number` | no | — | — | Sort order |

**Examples**

- Update a checklist.: `kaiten --json checklists update --card-id 10 --checklist-id 20 --name "Ready for QA"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-template-checklist-items.create`

| Field | Value |
|---|---|
| CLI command | `kaiten space-template-checklist-items create` |
| MCP alias | `kaiten_create_space_template_checklist_item` |
| Description | Create an item in a space template checklist. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_uid}/template-checklists/{template_checklist_uid}/items` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UID. |
| `template_checklist_uid` | `string` | yes | — | — | Template checklist UID. |
| `text` | `string` | yes | — | — | Checklist item text. |
| `sort_order` | `number` | no | — | — | Sort order. |

**Examples**

- Create a space template checklist item.: `kaiten --json space-template-checklist-items create --space-uid space-uuid --template-checklist-uid tmpl-uuid --text "Reviewed"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-template-checklist-items.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten space-template-checklist-items delete` |
| MCP alias | `kaiten_delete_space_template_checklist_item` |
| Description | Delete an item from a space template checklist. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_uid}/template-checklists/{template_checklist_uid}/items/{item_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UID. |
| `template_checklist_uid` | `string` | yes | — | — | Template checklist UID. |
| `item_uid` | `string` | yes | — | — | Template checklist item UID. |

**Examples**

- Delete a space template checklist item.: `kaiten --json space-template-checklist-items delete --space-uid space-uuid --template-checklist-uid tmpl-uuid --item-uid item-uuid`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-template-checklist-items.update`

| Field | Value |
|---|---|
| CLI command | `kaiten space-template-checklist-items update` |
| MCP alias | `kaiten_update_space_template_checklist_item` |
| Description | Update an item in a space template checklist. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_uid}/template-checklists/{template_checklist_uid}/items/{item_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UID. |
| `template_checklist_uid` | `string` | yes | — | — | Template checklist UID. |
| `item_uid` | `string` | yes | — | — | Template checklist item UID. |
| `text` | `string` | no | — | — | Checklist item text. |
| `sort_order` | `number` | no | — | — | Sort order. |

**Examples**

- Update a space template checklist item.: `kaiten --json space-template-checklist-items update --space-uid space-uuid --template-checklist-uid tmpl-uuid --item-uid item-uuid --text "Reviewed"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-template-checklists.create`

| Field | Value |
|---|---|
| CLI command | `kaiten space-template-checklists create` |
| MCP alias | `kaiten_create_space_template_checklist` |
| Description | Create a template checklist for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_uid}/template-checklists` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UID. |
| `name` | `string` | yes | — | — | Template checklist name. |
| `sort_order` | `number` | no | — | — | Sort order. |

**Examples**

- Create a space template checklist.: `kaiten --json space-template-checklists create --space-uid space-uuid --name "Definition of Done"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-template-checklists.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten space-template-checklists delete` |
| MCP alias | `kaiten_delete_space_template_checklist` |
| Description | Delete a template checklist from a space. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_uid}/template-checklists/{template_checklist_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UID. |
| `template_checklist_uid` | `string` | yes | — | — | Template checklist UID. |

**Examples**

- Delete a space template checklist.: `kaiten --json space-template-checklists delete --space-uid space-uuid --template-checklist-uid tmpl-uuid`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-template-checklists.list`

| Field | Value |
|---|---|
| CLI command | `kaiten space-template-checklists list` |
| MCP alias | `kaiten_list_space_template_checklists` |
| Description | List template checklists for a space. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/spaces/{space_uid}/template-checklists` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UID. |

**Examples**

- List space template checklists.: `kaiten --json space-template-checklists list --space-uid space-uuid`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-template-checklists.update`

| Field | Value |
|---|---|
| CLI command | `kaiten space-template-checklists update` |
| MCP alias | `kaiten_update_space_template_checklist` |
| Description | Update a template checklist for a space. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_uid}/template-checklists/{template_checklist_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UID. |
| `template_checklist_uid` | `string` | yes | — | — | Template checklist UID. |
| `name` | `string` | no | — | — | Template checklist name. |
| `sort_order` | `number` | no | — | — | Sort order. |

**Examples**

- Update a space template checklist.: `kaiten --json space-template-checklists update --space-uid space-uuid --template-checklist-uid tmpl-uuid --name "Ready"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

<a id="module-blockers"></a>
## Блокировки (`blockers`) — 12 commands

Блокировки карточек и blocker relations.

**Namespace tree**

```text
blocker-categories
  add
  list
  remove
blocker-users
  add
  list
  remove
blockers
  create
  delete
  get
  list
  update
current-user-blockers
  list
```

### `blocker-categories.add`

| Field | Value |
|---|---|
| CLI command | `kaiten blocker-categories add` |
| MCP alias | `kaiten_add_blocker_category` |
| Description | Add a category to a blocker. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/blockers/{blocker_id}/categories` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `blocker_id` | `integer` | yes | — | — | Blocker ID. |
| `category_uuid` | `string` | yes | — | — | Category UUID. |

**Examples**

- Add a blocker category.: `kaiten --json blocker-categories add --blocker-id 20 --category-uuid cat-uuid`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `blocker-categories.list`

| Field | Value |
|---|---|
| CLI command | `kaiten blocker-categories list` |
| MCP alias | `kaiten_list_blocker_categories` |
| Description | List blocker categories. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/categories` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- List blocker categories.: `kaiten --json blocker-categories list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `blocker-categories.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten blocker-categories remove` |
| MCP alias | `kaiten_remove_blocker_category` |
| Description | Remove a category from a blocker. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/blockers/{blocker_id}/categories/{category_uuid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `blocker_id` | `integer` | yes | — | — | Blocker ID. |
| `category_uuid` | `string` | yes | — | — | Category UUID. |

**Examples**

- Remove a blocker category.: `kaiten --json blocker-categories remove --blocker-id 20 --category-uuid cat-uuid`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `blocker-users.add`

| Field | Value |
|---|---|
| CLI command | `kaiten blocker-users add` |
| MCP alias | `kaiten_add_blocker_user` |
| Description | Add a user to a blocker. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/blockers/{blocker_id}/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `blocker_id` | `integer` | yes | — | — | Blocker ID. |
| `user_id` | `integer` | yes | — | — | User ID. |

**Examples**

- Add a blocker user.: `kaiten --json blocker-users add --blocker-id 20 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `blocker-users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten blocker-users list` |
| MCP alias | `kaiten_list_blocker_users` |
| Description | List users attached to a blocker. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/blockers/{blocker_id}/users` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `blocker_id` | `integer` | yes | — | — | Blocker ID. |

**Examples**

- List blocker users.: `kaiten --json blocker-users list --blocker-id 20 --compact`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `blocker-users.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten blocker-users remove` |
| MCP alias | `kaiten_remove_blocker_user` |
| Description | Remove a user from a blocker. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/blockers/{blocker_id}/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `blocker_id` | `integer` | yes | — | — | Blocker ID. |
| `user_id` | `integer` | yes | — | — | User ID. |

**Examples**

- Remove a blocker user.: `kaiten --json blocker-users remove --blocker-id 20 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `blockers.create`

| Field | Value |
|---|---|
| CLI command | `kaiten blockers create` |
| MCP alias | `kaiten_create_card_blocker` |
| Description | Create a blocker on a card. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/blockers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card to add a blocker to. |
| `reason` | `string` | no | — | — | Reason for the blocker. |
| `blocker_card_id` | `integer` | no | — | — | ID of the card that blocks this one. |

**Examples**

- Create a blocker on a card.: `kaiten --json blockers create --card-id 10 --reason "Waiting for review"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `blockers.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten blockers delete` |
| MCP alias | `kaiten_delete_card_blocker` |
| Description | Delete a blocker from a card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/blockers/{blocker_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `blocker_id` | `integer` | yes | — | — | ID of the blocker to delete. |

**Examples**

- Delete a blocker.: `kaiten --json blockers delete --card-id 10 --blocker-id 20`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `blockers.get`

| Field | Value |
|---|---|
| CLI command | `kaiten blockers get` |
| MCP alias | `kaiten_get_card_blocker` |
| Description | Get a specific blocker on a card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/blockers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `blocker_id` | `integer` | yes | — | — | ID of the blocker to retrieve. |

**Examples**

- Get a blocker by filtering the blocker list.: `kaiten --json blockers get --card-id 10 --blocker-id 20`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `blockers.list`

| Field | Value |
|---|---|
| CLI command | `kaiten blockers list` |
| MCP alias | `kaiten_list_card_blockers` |
| Description | List all blockers on a card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/blockers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card whose blockers to list. |

**Examples**

- List blockers on a card.: `kaiten --json blockers list --card-id 10`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `blockers.update`

| Field | Value |
|---|---|
| CLI command | `kaiten blockers update` |
| MCP alias | `kaiten_update_card_blocker` |
| Description | Update a blocker on a card. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/blockers/{blocker_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the card. |
| `blocker_id` | `integer` | yes | — | — | ID of the blocker to update. |
| `reason` | `string` | no | — | — | New reason for the blocker. |

**Examples**

- Update a blocker.: `kaiten --json blockers update --card-id 10 --blocker-id 20 --reason "Waiting for review"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `current-user-blockers.list`

| Field | Value |
|---|---|
| CLI command | `kaiten current-user-blockers list` |
| MCP alias | `kaiten_list_current_user_blockers` |
| Description | List blocker cards assigned to the current user. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/users/current/blockers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- List current user blockers.: `kaiten --json current-user-blockers list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/children` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the parent card. |
| `child_card_id` | `integer` | yes | — | — | ID of the card to add as a child. |

**Examples**

- Add a child card relation.: `kaiten --json card-children add --card-id 10 --child-card-id 11`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-children.batch-list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-children batch-list` |
| MCP alias | `kaiten_batch_list_card_children` |
| Description | Fetch child-card relations for multiple parent cards with bounded worker concurrency. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `aggregated` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/cards/children/batch` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_ids` | `array` | yes | — | — | Parent card IDs to inspect |
| `workers` | `integer` | no | — | — | Parallel workers (default 2, max 6) |
| `page_size` | `integer` | no | — | >= 1, <= 100 | Child cards per request (default 100, max 100). |
| `max_pages` | `integer` | no | — | >= 1, <= 1000 | Safety limit per card (default 100, max 1000). |
| `compact` | `boolean` | no | — | — | Strip heavy nested fields from child card payloads |
| `fields` | `string` | no | — | — | Comma-separated field names to keep for each child card |

**Examples**

- Fetch child-card relations for several parent cards.: `kaiten --json card-children batch-list --card-ids '[1,2,3]'`
- Fetch narrowed child-card payloads with bounded concurrency.: `kaiten --json card-children batch-list --card-ids '[1,2,3]' --workers 2 --compact --fields id,title`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The command returns items, errors, and meta so partial per-card failures stay visible without aborting the whole batch.
- Each card is paginated to completion; a full max_pages boundary becomes a per-card error instead of a partial child-card list.
- Use this bulk path for relation-heavy investigations instead of per-parent card-children.list loops.

### `card-children.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-children list` |
| MCP alias | `kaiten_list_card_children` |
| Description | List one page of child cards for a given card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/children` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the parent card. |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default 50, max 100). |
| `offset` | `integer` | no | — | >= 0 | Pagination offset. |

**Examples**

- List child cards.: `kaiten --json card-children list --card-id 10`

**Notes**

- Bulk alternative: `card-children.batch-list`
- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This direct command returns one page; increase offset to read subsequent pages.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/children/{child_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the parent card. |
| `child_id` | `integer` | yes | — | — | ID of the child card to remove. |

**Examples**

- Remove a child card relation.: `kaiten --json card-children remove --card-id 10 --child-id 11`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-parents.add`

| Field | Value |
|---|---|
| CLI command | `kaiten card-parents add` |
| MCP alias | `kaiten_add_card_parent` |
| Description | Add a parent card to a given card. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/parents` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the child card. |
| `parent_card_id` | `integer` | yes | — | — | ID of the card to add as a parent. |

**Examples**

- Add a parent card relation.: `kaiten --json card-parents add --card-id 10 --parent-card-id 11`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-parents.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-parents list` |
| MCP alias | `kaiten_list_card_parents` |
| Description | List one page of parent cards for a given card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/parents` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the child card. |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default 50, max 100). |
| `offset` | `integer` | no | — | >= 0 | Pagination offset. |

**Examples**

- List parent cards.: `kaiten --json card-parents list --card-id 10`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This direct command returns one page; increase offset to read subsequent pages.

### `card-parents.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten card-parents remove` |
| MCP alias | `kaiten_remove_card_parent` |
| Description | Remove a parent card from a given card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/parents/{parent_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the child card. |
| `parent_id` | `integer` | yes | — | — | ID of the parent card to remove. |

**Examples**

- Remove a parent card relation.: `kaiten --json card-parents remove --card-id 10 --parent-id 11`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `planned-relations.add`

| Field | Value |
|---|---|
| CLI command | `kaiten planned-relations add` |
| MCP alias | `kaiten_add_planned_relation` |
| Description | Create a planned relation (successor link) between two cards on Timeline/Gantt. The source card becomes a predecessor and the target card becomes its successor. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/planned-relation` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the source (predecessor) card. |
| `target_card_id` | `integer` | yes | — | — | ID of the target (successor) card. |
| `type` | `string` | no | `end-start` | — | Relation type. Defaults to 'end-start'. |

**Examples**

- Create a finish-to-start planned relation.: `kaiten --json planned-relations add --card-id 10 --target-card-id 11`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `planned-relations.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten planned-relations remove` |
| MCP alias | `kaiten_remove_planned_relation` |
| Description | Remove a planned relation (successor link) between two cards. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/planned-relation/{target_card_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the source (predecessor) card. |
| `target_card_id` | `integer` | yes | — | — | ID of the target (successor) card to unlink. |

**Examples**

- Remove a planned relation.: `kaiten --json planned-relations remove --card-id 10 --target-card-id 11`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `planned-relations.update`

| Field | Value |
|---|---|
| CLI command | `kaiten planned-relations update` |
| MCP alias | `kaiten_update_planned_relation` |
| Description | Update the lag/lead gap of a planned relation between two cards. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/planned-relation/{target_card_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | ID of the source (predecessor) card. |
| `target_card_id` | `integer` | yes | — | — | ID of the target (successor) card. |
| `gap` | `integer|null` | yes | — | — | Distance between cards (-1000..1000). Positive = lag, negative = lead. null to clear. |
| `gap_type` | `string|null` | yes | `hours`, `days` | — | Unit of the gap: 'hours', 'days', or null to clear. |

**Examples**

- Set a 2-day lag for a planned relation.: `kaiten --json planned-relations update --card-id 10 --target-card-id 11 --gap 2 --gap-type days`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/external-links` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `url` | `string` | yes | — | — | URL of the external link |
| `description` | `string` | no | — | — | Description of the external link |

**Examples**

- Attach an external link to a card.: `kaiten --json external-links create --card-id 10 --url "https://example.com"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `external-links.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten external-links delete` |
| MCP alias | `kaiten_delete_external_link` |
| Description | Delete an external link from a Kaiten card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/external-links/{link_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `link_id` | `integer` | yes | — | — | External link ID |

**Examples**

- Delete a card external link.: `kaiten --json external-links delete --card-id 10 --link-id 20`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `external-links.list`

| Field | Value |
|---|---|
| CLI command | `kaiten external-links list` |
| MCP alias | `kaiten_list_external_links` |
| Description | List all external links on a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/external-links` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |

**Examples**

- List external links on a card.: `kaiten --json external-links list --card-id 10`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `external-links.update`

| Field | Value |
|---|---|
| CLI command | `kaiten external-links update` |
| MCP alias | `kaiten_update_external_link` |
| Description | Update an external link on a Kaiten card. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/external-links/{link_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `link_id` | `integer` | yes | — | — | External link ID |
| `url` | `string` | no | — | — | URL of the external link |
| `description` | `string` | no | — | — | Description of the external link |

**Examples**

- Update a card external link.: `kaiten --json external-links update --card-id 10 --link-id 20 --description "Spec"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

<a id="module-files"></a>
## Файлы карточек (`files`) — 18 commands

Файлы, вложения и beta Restricted Access Files карточек.

**Namespace tree**

```text
files
  create
  delete
  download
  list
  update
  upload
private-card-files
  delete
  get
  update
  upload
private-comment-files
  delete
  get
  update
  upload
private-custom-property-files
  delete
  get
  update
  upload
```

### `files.create`

| Field | Value |
|---|---|
| CLI command | `kaiten files create` |
| MCP alias | `kaiten_create_card_file` |
| Description | Create a file attachment on a card by URL. This registers an external file link as a card attachment (does not upload binary data). File types: 1=attachment, 2=googleDrive, 3=dropBox, 4=box, 5=oneDrive, 6=yandexDisk. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/files` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID. |
| `url` | `string` | yes | — | — | URL of the file. |
| `name` | `string` | yes | — | — | Display name of the file. |
| `type` | `integer` | no | `1`, `2`, `3`, `4`, `5`, `6` | — | File type: 1=attachment, 2=googleDrive, 3=dropBox, 4=box, 5=oneDrive, 6=yandexDisk. |
| `size` | `integer` | no | — | — | File size in bytes. |
| `sort_order` | `number` | no | — | — | Sort order of the file in the list. |
| `custom_property_id` | `integer` | no | — | — | Custom property ID to associate the file with. |
| `card_cover` | `boolean` | no | — | — | Set this file as the card cover image. |

**Examples**

- Attach a URL-backed file to a card.: `kaiten --json files create --card-id 10 --url "https://example.com/a.png" --name "a.png"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `files.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten files delete` |
| MCP alias | `kaiten_delete_card_file` |
| Description | Delete a file attachment from a card. Files on blocked cards cannot be deleted. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID. |
| `file_id` | `integer` | yes | — | — | File ID. |

**Examples**

- Delete a card file.: `kaiten --json files delete --card-id 10 --file-id 20`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `files.download`

| Field | Value |
|---|---|
| CLI command | `kaiten files download` |
| MCP alias | `kaiten_download_file` |
| Description | Download a Kaiten file attachment to disk. Supports card, document, comment, custom property, and conversation message file endpoints, plus Kaiten /api/... URLs. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/files/download` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `url` | `string` | no | — | — | Kaiten /api/... file URL, internal /files/... URL, or direct http(s) URL. |
| `entity_type` | `string` | no | `card`, `document`, `comment`, `custom_property`, `conversation_message` | — | Attachment owner type when not passing --url. |
| `file_id` | `string|integer` | no | — | — | File identifier. UUID values may include the original extension. |
| `card_id` | `string|integer` | no | — | — | Card ID for card, comment, or custom property files. |
| `card_uid` | `string` | no | — | — | Card UID for card, comment, or custom property files. |
| `card_id_or_uid` | `string` | no | — | — | Card ID or UID for card, comment, or custom property files. |
| `document_uid` | `string` | no | — | — | Document UID for document files. |
| `comment_uid` | `string` | no | — | — | Comment UID for comment files. |
| `custom_property_uid` | `string` | no | — | — | Custom property UID for custom property files. |
| `conversation_uid` | `string` | no | — | — | Conversation UID for conversation message files. |
| `conversation_message_uid` | `string` | no | — | — | Conversation message UID for conversation message files. |
| `output` | `string` | no | — | — | Output file or directory. Defaults to the current working directory. |
| `name` | `string` | no | — | — | Preferred local filename when --output is a directory or omitted. |
| `overwrite` | `boolean` | no | — | — | Replace an existing output file. |
| `continue` | `boolean` | no | — | — | Resume an existing .part file with HTTP Range. Enabled by default. |

**Examples**

- Download a document attachment into the current directory.: `kaiten --json files download --entity-type document --document-uid <document_uid> --file-id <file_uid>`
- Download a card attachment into a directory.: `kaiten --json files download --entity-type card --card-id 123 --file-id <file_uid> --output ./downloads/`
- Download a Restricted Access card file with streaming and resume.: `kaiten --json files download --entity-type card --card-uid <card_uid> --file-id <private_file_uid> --output ./downloads/`
- Download a Restricted Access comment file.: `kaiten --json files download --entity-type comment --card-uid <card_uid> --comment-uid <comment_uid> --file-id <private_file_uid>`
- Download a Restricted Access custom-property file.: `kaiten --json files download --entity-type custom_property --card-uid <card_uid> --custom-property-uid <property_uid> --file-id <private_file_uid>`
- Download from a Kaiten report/browser file URL.: `kaiten --json files download --url "https://hq.kaiten.ru/api/documents/<document_uid>/files/<file_uid>" --output ./file.bin --overwrite`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- By default the command writes to the current working directory.
- Downloads stream to <target>.part first and are renamed into place only after completion.
- Existing .part files are resumed with HTTP Range by default, similar to wget --continue.
- For Kaiten file endpoints the command resolves a short-lived storage URL internally and does not print it.
- Restricted Access card/comment/custom-property downloads use the same streaming, resume, and signed-URL refresh flow.
- The signed storage URL is neither returned nor sent the Kaiten bearer token.

### `files.list`

| Field | Value |
|---|---|
| CLI command | `kaiten files list` |
| MCP alias | `kaiten_list_card_files` |
| Description | List all file attachments on a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/files` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID. |

**Examples**

- List card files.: `kaiten --json files list --card-id 10`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `files.update`

| Field | Value |
|---|---|
| CLI command | `kaiten files update` |
| MCP alias | `kaiten_update_card_file` |
| Description | Update a file attachment on a card (name, URL, sort order, cover, etc.). |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID. |
| `file_id` | `integer` | yes | — | — | File ID. |
| `url` | `string` | no | — | — | New URL of the file. |
| `name` | `string` | no | — | — | New display name. |
| `type` | `integer` | no | `1`, `2`, `3`, `4`, `5`, `6` | — | File type: 1=attachment, 2=googleDrive, 3=dropBox, 4=box, 5=oneDrive, 6=yandexDisk. |
| `size` | `integer` | no | — | — | File size in bytes. |
| `sort_order` | `number` | no | — | — | Sort order of the file in the list. |
| `custom_property_id` | `integer` | no | — | — | Custom property ID to associate the file with. |
| `card_cover` | `boolean` | no | — | — | Set this file as the card cover image. |

**Examples**

- Update a card file attachment.: `kaiten --json files update --card-id 10 --file-id 20 --name "a-v2.png"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `files.upload`

| Field | Value |
|---|---|
| CLI command | `kaiten files upload` |
| MCP alias | `kaiten_upload_card_file` |
| Description | Upload a local binary file to a Kaiten card using multipart/form-data. |
| Method | `PUT` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/files` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID. |
| `file` | `string` | yes | — | — | Local file path to upload. |

**Examples**

- Upload a local file to a card.: `kaiten --json files upload --card-id 123 --file ./report.json`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Uploads the local file as multipart/form-data field `file`.
- The uploaded filename is the local file basename.
- This command uses the legacy card-file upload contract, not Restricted Access Files.
- When the company forbids legacy Public API uploads, Kaiten returns HTTP 403 with code PUBLIC_API_LEGACY_FILE_UPLOAD_DISABLED; use private-card-files upload with a card UUID.

### `private-card-files.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten private-card-files delete` |
| MCP alias | `kaiten_delete_private_card_file` |
| Description | Delete a beta Restricted Access card file. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_uid}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `file_id` | `string` | yes | — | — | Restricted Access file UUID. |

**Examples**

- Delete a Restricted Access card file.: `kaiten --json private-card-files delete --card-uid <card_uid> --file-id <file_uid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten documents this beta family as Restricted Access Files; the historical `private-*` command namespace is preserved for compatibility.

### `private-card-files.get`

| Field | Value |
|---|---|
| CLI command | `kaiten private-card-files get` |
| MCP alias | `kaiten_get_private_card_file` |
| Description | Get Restricted Access card-file metadata and a short-lived signed URL. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_uid}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `file_id` | `string` | yes | — | — | Restricted Access file UUID. |

**Examples**

- Read Restricted Access card-file metadata.: `kaiten --json private-card-files get --card-uid <card_uid> --file-id <file_uid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten documents this beta family as Restricted Access Files; the historical `private-*` command namespace is preserved for compatibility.
- The metadata response contains a short-lived signed URL. Do not store or cache it; request fresh metadata immediately before downloading.

### `private-card-files.update`

| Field | Value |
|---|---|
| CLI command | `kaiten private-card-files update` |
| MCP alias | `kaiten_update_private_card_file` |
| Description | Update a Restricted Access card file name or card-cover flag. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_uid}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `file_id` | `string` | yes | — | — | Restricted Access file UUID. |
| `name` | `string` | no | — | — | New file name. |
| `card_cover` | `boolean` | no | — | — | Use this image as the card cover. |

**Examples**

- Rename a Restricted Access card file.: `kaiten --json private-card-files update --card-uid <card_uid> --file-id <file_uid> --name "report-final.pdf"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten documents this beta family as Restricted Access Files; the historical `private-*` command namespace is preserved for compatibility.

### `private-card-files.upload`

| Field | Value |
|---|---|
| CLI command | `kaiten private-card-files upload` |
| MCP alias | `kaiten_upload_private_card_file` |
| Description | Upload a beta Restricted Access file to a card using multipart POST. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_uid}/files` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `file` | `string` | yes | — | — | Local file path to upload. |

**Examples**

- Upload a Restricted Access card file.: `kaiten --json private-card-files upload --card-uid <card_uid> --file ./report.pdf`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten documents this beta family as Restricted Access Files; the historical `private-*` command namespace is preserved for compatibility.
- Beta endpoint; availability depends on Restricted Access Files settings in the Kaiten installation.
- Uses multipart/form-data field `file` with POST; classic files.upload remains PUT.

### `private-comment-files.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten private-comment-files delete` |
| MCP alias | `kaiten_delete_private_comment_file` |
| Description | Delete a beta Restricted Access comment file. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_uid}/comments/{comment_uid}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `comment_uid` | `string` | yes | — | — | Comment UUID. |
| `file_id` | `string` | yes | — | — | Restricted Access file UUID. |

**Examples**

- Delete a Restricted Access comment file.: `kaiten --json private-comment-files delete --card-uid <card_uid> --comment-uid <comment_uid> --file-id <file_uid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten documents this beta family as Restricted Access Files; the historical `private-*` command namespace is preserved for compatibility.

### `private-comment-files.get`

| Field | Value |
|---|---|
| CLI command | `kaiten private-comment-files get` |
| MCP alias | `kaiten_get_private_comment_file` |
| Description | Get Restricted Access comment-file metadata and a short-lived signed URL. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_uid}/comments/{comment_uid}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `comment_uid` | `string` | yes | — | — | Comment UUID, or `new` before the comment is created. |
| `file_id` | `string` | yes | — | — | Restricted Access file UUID. |

**Examples**

- Read Restricted Access comment-file metadata.: `kaiten --json private-comment-files get --card-uid <card_uid> --comment-uid <comment_uid> --file-id <file_uid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten documents this beta family as Restricted Access Files; the historical `private-*` command namespace is preserved for compatibility.
- The metadata response contains a short-lived signed URL. Do not store or cache it; request fresh metadata immediately before downloading.

### `private-comment-files.update`

| Field | Value |
|---|---|
| CLI command | `kaiten private-comment-files update` |
| MCP alias | `kaiten_update_private_comment_file` |
| Description | Update a Restricted Access comment file name or card-cover flag. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_uid}/comments/{comment_uid}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `comment_uid` | `string` | yes | — | — | Comment UUID, or `new` before the comment is created. |
| `file_id` | `string` | yes | — | — | Restricted Access file UUID. |
| `name` | `string` | no | — | — | New file name. |
| `card_cover` | `boolean` | no | — | — | Use this image as the card cover; requires card update permission. |

**Examples**

- Rename a Restricted Access comment file.: `kaiten --json private-comment-files update --card-uid <card_uid> --comment-uid <comment_uid> --file-id <file_uid> --name "evidence-final.png"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten documents this beta family as Restricted Access Files; the historical `private-*` command namespace is preserved for compatibility.

### `private-comment-files.upload`

| Field | Value |
|---|---|
| CLI command | `kaiten private-comment-files upload` |
| MCP alias | `kaiten_upload_private_comment_file` |
| Description | Upload a beta Restricted Access file to a card comment using multipart POST. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_uid}/comments/{comment_uid}/files` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `comment_uid` | `string` | yes | — | — | Comment UUID. |
| `file` | `string` | yes | — | — | Local file path to upload. |

**Examples**

- Upload a Restricted Access comment file.: `kaiten --json private-comment-files upload --card-uid <card_uid> --comment-uid <comment_uid> --file ./evidence.png`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten documents this beta family as Restricted Access Files; the historical `private-*` command namespace is preserved for compatibility.

### `private-custom-property-files.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten private-custom-property-files delete` |
| MCP alias | `kaiten_delete_private_custom_property_file` |
| Description | Delete a beta Restricted Access custom-property file. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_uid}/custom-properties/{property_uid}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `property_uid` | `string` | yes | — | — | Custom property UUID. |
| `file_id` | `string` | yes | — | — | Restricted Access file UUID. |

**Examples**

- Delete a Restricted Access custom-property file.: `kaiten --json private-custom-property-files delete --card-uid <card_uid> --property-uid <property_uid> --file-id <file_uid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten documents this beta family as Restricted Access Files; the historical `private-*` command namespace is preserved for compatibility.

### `private-custom-property-files.get`

| Field | Value |
|---|---|
| CLI command | `kaiten private-custom-property-files get` |
| MCP alias | `kaiten_get_private_custom_property_file` |
| Description | Get Restricted Access custom-property file metadata and a short-lived signed URL. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_uid}/custom-properties/{property_uid}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `property_uid` | `string` | yes | — | — | Custom property UUID. |
| `file_id` | `string` | yes | — | — | Restricted Access file UUID. |

**Examples**

- Read Restricted Access custom-property file metadata.: `kaiten --json private-custom-property-files get --card-uid <card_uid> --property-uid <property_uid> --file-id <file_uid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten documents this beta family as Restricted Access Files; the historical `private-*` command namespace is preserved for compatibility.
- The metadata response contains a short-lived signed URL. Do not store or cache it; request fresh metadata immediately before downloading.

### `private-custom-property-files.update`

| Field | Value |
|---|---|
| CLI command | `kaiten private-custom-property-files update` |
| MCP alias | `kaiten_update_private_custom_property_file` |
| Description | Update a Restricted Access custom-property file name or card-cover flag. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_uid}/custom-properties/{property_uid}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `property_uid` | `string` | yes | — | — | Custom property UUID. |
| `file_id` | `string` | yes | — | — | Restricted Access file UUID. |
| `name` | `string` | no | — | — | New file name. |
| `card_cover` | `boolean` | no | — | — | Use this image as the card cover. |

**Examples**

- Rename a Restricted Access custom-property file.: `kaiten --json private-custom-property-files update --card-uid <card_uid> --property-uid <property_uid> --file-id <file_uid> --name "contract-final.pdf"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten documents this beta family as Restricted Access Files; the historical `private-*` command namespace is preserved for compatibility.

### `private-custom-property-files.upload`

| Field | Value |
|---|---|
| CLI command | `kaiten private-custom-property-files upload` |
| MCP alias | `kaiten_upload_private_custom_property_file` |
| Description | Upload a beta Restricted Access file to a card custom property using multipart POST. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_uid}/custom-properties/{property_uid}/files` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `property_uid` | `string` | yes | — | — | Custom property UUID. |
| `file` | `string` | yes | — | — | Local file path to upload. |

**Examples**

- Upload a Restricted Access custom-property file.: `kaiten --json private-custom-property-files upload --card-uid <card_uid> --property-uid <property_uid> --file ./contract.pdf`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten documents this beta family as Restricted Access Files; the historical `private-*` command namespace is preserved for compatibility.

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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/subscribers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `user_id` | `integer` | yes | — | — | User ID to subscribe |

**Examples**

- Add a card subscriber.: `kaiten --json card-subscribers add --card-id 10 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-subscribers.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-subscribers list` |
| MCP alias | `kaiten_list_card_subscribers` |
| Description | List all subscribers of a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/subscribers` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields. |

**Examples**

- List card subscribers.: `kaiten --json card-subscribers list --card-id 10 --compact`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/subscribers/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `user_id` | `integer` | yes | — | — | User ID to unsubscribe |

**Examples**

- Remove a card subscriber.: `kaiten --json card-subscribers remove --card-id 10 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `column-subscribers.add`

| Field | Value |
|---|---|
| CLI command | `kaiten column-subscribers add` |
| MCP alias | `kaiten_add_column_subscriber` |
| Description | Add a subscriber to a Kaiten column. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/columns/{column_id}/subscribers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `column_id` | `integer` | yes | — | — | Column ID |
| `user_id` | `integer` | yes | — | — | User ID to subscribe |
| `type` | `integer` | no | — | — | Subscription type (1=all, 2=mentions only). |

**Examples**

- Add a column subscriber.: `kaiten --json column-subscribers add --column-id 10 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `column-subscribers.list`

| Field | Value |
|---|---|
| CLI command | `kaiten column-subscribers list` |
| MCP alias | `kaiten_list_column_subscribers` |
| Description | List all subscribers of a Kaiten column. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/columns/{column_id}/subscribers` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `column_id` | `integer` | yes | — | — | Column ID |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields. |

**Examples**

- List column subscribers.: `kaiten --json column-subscribers list --column-id 10 --compact`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/columns/{column_id}/subscribers/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `column_id` | `integer` | yes | — | — | Column ID |
| `user_id` | `integer` | yes | — | — | User ID to unsubscribe |

**Examples**

- Remove a column subscriber.: `kaiten --json column-subscribers remove --column-id 10 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `aggregated` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/spaces/{space_id}/topology` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |

**Examples**

- Fetch board topology for a space.: `kaiten --json space-topology get --space-id 123`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Use this for report scaffolding instead of separate boards.list, columns.list, and lanes.list loops.

### `spaces.create`

| Field | Value |
|---|---|
| CLI command | `kaiten spaces create` |
| MCP alias | `kaiten_create_space` |
| Description | Create a new Kaiten space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `title` | `string` | yes | — | — | Space title |
| `description` | `string` | no | — | — | Space description |
| `access` | `string` | no | `for_everyone`, `by_invite` | — | Access type (default: for_everyone) |
| `external_id` | `string` | no | — | — | External ID |
| `parent_entity_uid` | `string` | no | — | — | Parent entity UID for nesting spaces |
| `sort_order` | `number` | no | — | — | Sort order |

**Examples**

- Create a space.: `kaiten spaces create --title "CLI smoke"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `spaces.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten spaces delete` |
| MCP alias | `kaiten_delete_space` |
| Description | Delete a Kaiten space. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |

**Examples**

- Delete a space.: `kaiten spaces delete --space-id 123`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `spaces.get`

| Field | Value |
|---|---|
| CLI command | `kaiten spaces get` |
| MCP alias | `kaiten_get_space` |
| Description | Get a Kaiten space by ID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/spaces/{space_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |

**Examples**

- Get a space by ID.: `kaiten spaces get --space-id 123`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `spaces.list`

| Field | Value |
|---|---|
| CLI command | `kaiten spaces list` |
| MCP alias | `kaiten_list_spaces` |
| Description | List one page of Kaiten spaces with explicit limit/offset pagination. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/spaces` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `archived` | `boolean` | no | — | — | Include archived spaces |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default 50, max 100) |
| `offset` | `integer` | no | — | >= 0 | Pagination offset |
| `fields` | `string` | no | — | — | Comma-separated field names to keep in the response. Example: 'id,title' |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, nested user objects) |

**Examples**

- List spaces as machine-readable JSON.: `kaiten --json spaces list`
- List spaces with a narrow response surface.: `kaiten --json spaces list --compact --fields id,title`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This direct command returns one page; increase offset to read subsequent pages.
- Use tree.get or tree.children.list when a complete hierarchy is required.

### `spaces.update`

| Field | Value |
|---|---|
| CLI command | `kaiten spaces update` |
| MCP alias | `kaiten_update_space` |
| Description | Update a Kaiten space. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `title` | `string` | no | — | — | New title |
| `description` | `string` | no | — | — | New description |
| `access` | `string` | no | `for_everyone`, `by_invite` | — | Access type |
| `external_id` | `string` | no | — | — | External ID |
| `parent_entity_uid` | `string` | no | — | — | Parent entity UID for nesting spaces |
| `sort_order` | `number` | no | — | — | Sort order |

**Examples**

- Update a space.: `kaiten spaces update --space-id 123 --title "Updated"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

<a id="module-boards"></a>
## Доски (`boards`) — 6 commands

Boards and board-level operations.

**Namespace tree**

```text
boards
  create
  delete
  get
  list
  place-existing
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/boards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `title` | `string` | yes | — | — | Board title |
| `description` | `string` | no | — | — | Board description |
| `external_id` | `string` | no | — | — | External ID |
| `top` | `number` | no | — | — | Top position (px) |
| `left` | `number` | no | — | — | Left position (px) |
| `sort_order` | `number` | no | — | — | Sort order |
| `default_card_type_id` | `integer` | no | — | — | Default card type ID for new cards |

**Examples**

- Create a board.: `kaiten boards create --space-id 1 --title "Smoke"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `boards.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten boards delete` |
| MCP alias | `kaiten_delete_board` |
| Description | Delete a Kaiten board. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/boards/{board_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `board_id` | `integer` | yes | — | — | Board ID |
| `force` | `boolean` | no | — | — | Force deletion when the board contains child entities |

**Examples**

- Delete a board.: `kaiten boards delete --space-id 1 --board-id 10 --force`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Live contract: `live_passed_with_runtime_fix`; expected statuses: —
- Live note: Sandbox requires the force flag for board deletion; the CLI injects the live-safe request shape.

### `boards.get`

| Field | Value |
|---|---|
| CLI command | `kaiten boards get` |
| MCP alias | `kaiten_get_board` |
| Description | Get a Kaiten board by ID, optionally through its space-scoped Public API route. Returns board placement data, columns and lanes. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/boards/{board_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `board_id` | `integer` | yes | — | — | Board ID |
| `space_id` | `integer` | no | — | — | Optional space ID. When provided, use the documented /spaces/{space_id}/boards/{board_id} route. |

**Examples**

- Get a board.: `kaiten boards get --board-id 10`
- Get a board through the space-scoped Public API route.: `kaiten --json boards get --space-id 1 --board-id 10`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Without --space-id the command preserves the existing GET /boards/{board_id} behavior.
- With --space-id it uses GET /spaces/{space_id}/boards/{board_id} from the current Public API documentation.
- Cards are not part of this command's guaranteed response contract and disappear from both Public API routes on 2026-11-01.
- Fetch active board cards with cards.list-all using board_id and condition=1; this command never performs that extra request implicitly.

### `boards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten boards list` |
| MCP alias | `kaiten_list_boards` |
| Description | List boards in a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/spaces/{space_id}/boards` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `fields` | `string` | no | — | — | Comma-separated field names to keep in the response. Example: 'id,title' |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, nested user objects) |

**Examples**

- List boards in a space.: `kaiten boards list --space-id 1 --compact`
- List boards with narrow fields.: `kaiten --json boards list --space-id 1 --fields id,title`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `boards.place-existing`

| Field | Value |
|---|---|
| CLI command | `kaiten boards place-existing` |
| MCP alias | `kaiten_place_existing_board` |
| Description | Place an existing board into a target space without moving it from its current primary space. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/boards/{board_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Target space ID |
| `board_id` | `integer` | yes | — | — | Existing board ID |
| `top` | `number` | no | — | — | Top position (px). Defaults to 0. |
| `left` | `number` | no | — | — | Left position (px). Defaults to 0. |
| `sort_order` | `number` | no | — | — | Sort order |

**Examples**

- Show an existing board in another space without moving it.: `kaiten --json boards place-existing --space-id 2 --board-id 10`
- Place an existing board at an explicit position.: `kaiten --json boards place-existing --space-id 2 --board-id 10 --top 0 --left 560 --sort-order 2`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This uses Kaiten's place-existing-board behavior and does not send move_from_space_id.
- This command is intentionally separate from Kaiten's move_from_space_id board-move behavior.

### `boards.update`

| Field | Value |
|---|---|
| CLI command | `kaiten boards update` |
| MCP alias | `kaiten_update_board` |
| Description | Update a Kaiten board. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/boards/{board_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `board_id` | `integer` | yes | — | — | Board ID |
| `title` | `string` | no | — | — | New title |
| `description` | `string` | no | — | — | New description |
| `external_id` | `string` | no | — | — | External ID |
| `top` | `number` | no | — | — | Top position (px) |
| `left` | `number` | no | — | — | Left position (px) |
| `sort_order` | `number` | no | — | — | Sort order |
| `default_card_type_id` | `integer` | no | — | — | Default card type ID for new cards |

**Examples**

- Update a board.: `kaiten boards update --space-id 1 --board-id 10 --title "Updated"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/boards/{board_id}/columns` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `board_id` | `integer` | yes | — | — | Board ID |
| `title` | `string` | yes | — | — | Column title |
| `type` | `integer` | yes | `1`, `2`, `3` | — | Column type: 1=queue, 2=in_progress, 3=done |
| `wip_limit` | `integer` | no | — | — | WIP limit |
| `wip_limit_type` | `integer` | no | — | — | WIP limit type (1=cards count, 2=size sum) |
| `col_count` | `integer` | no | — | — | Number of sub-columns to split into |
| `sort_order` | `number` | no | — | — | Sort order |

**Examples**

- Create a board column.: `kaiten --json columns create --board-id 10 --title "Doing" --type 2`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `columns.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten columns delete` |
| MCP alias | `kaiten_delete_column` |
| Description | Delete a column from a Kaiten board. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/boards/{board_id}/columns/{column_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `board_id` | `integer` | yes | — | — | Board ID |
| `column_id` | `integer` | yes | — | — | Column ID |

**Examples**

- Delete a board column.: `kaiten --json columns delete --board-id 10 --column-id 20`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `columns.list`

| Field | Value |
|---|---|
| CLI command | `kaiten columns list` |
| MCP alias | `kaiten_list_columns` |
| Description | List columns on a Kaiten board. Column types: 1=queue, 2=in_progress, 3=done. Response includes: wip_limit, wip_limit_type (1=cards count, 2=size sum), last_moved_warning_after_days, archive_after_days, card_hide_after_days. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/boards/{board_id}/columns` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `board_id` | `integer` | yes | — | — | Board ID |

**Examples**

- List columns on a board.: `kaiten --json columns list --board-id 10`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `columns.update`

| Field | Value |
|---|---|
| CLI command | `kaiten columns update` |
| MCP alias | `kaiten_update_column` |
| Description | Update a column on a Kaiten board. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/boards/{board_id}/columns/{column_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `board_id` | `integer` | yes | — | — | Board ID |
| `column_id` | `integer` | yes | — | — | Column ID |
| `title` | `string` | no | — | — | New title |
| `type` | `integer` | no | `1`, `2`, `3` | — | Column type |
| `wip_limit` | `integer` | no | — | — | WIP limit |
| `wip_limit_type` | `integer` | no | — | — | WIP limit type (1=cards count, 2=size sum) |
| `col_count` | `integer` | no | — | — | Number of sub-columns to split into |
| `sort_order` | `number` | no | — | — | Sort order |

**Examples**

- Rename a board column.: `kaiten --json columns update --board-id 10 --column-id 20 --title "Review"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `subcolumns.create`

| Field | Value |
|---|---|
| CLI command | `kaiten subcolumns create` |
| MCP alias | `kaiten_create_subcolumn` |
| Description | Create a subcolumn inside a Kaiten column. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/columns/{column_id}/subcolumns` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `column_id` | `integer` | yes | — | — | Column ID |
| `title` | `string` | yes | — | — | Subcolumn title |
| `sort_order` | `number` | no | — | — | Sort order |
| `wip_limit` | `integer` | no | — | — | WIP limit |
| `col_count` | `integer` | no | — | — | Number of sub-columns to split into |

**Examples**

- Create a subcolumn.: `kaiten --json subcolumns create --column-id 20 --title "Blocked"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `subcolumns.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten subcolumns delete` |
| MCP alias | `kaiten_delete_subcolumn` |
| Description | Delete a subcolumn from a Kaiten column. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/columns/{column_id}/subcolumns/{subcolumn_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `column_id` | `integer` | yes | — | — | Column ID |
| `subcolumn_id` | `integer` | yes | — | — | Subcolumn ID |

**Examples**

- Delete a subcolumn.: `kaiten --json subcolumns delete --column-id 20 --subcolumn-id 30`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `subcolumns.list`

| Field | Value |
|---|---|
| CLI command | `kaiten subcolumns list` |
| MCP alias | `kaiten_list_subcolumns` |
| Description | List all subcolumns of a Kaiten column. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/columns/{column_id}/subcolumns` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `column_id` | `integer` | yes | — | — | Column ID |

**Examples**

- List subcolumns for a column.: `kaiten --json subcolumns list --column-id 20`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `subcolumns.update`

| Field | Value |
|---|---|
| CLI command | `kaiten subcolumns update` |
| MCP alias | `kaiten_update_subcolumn` |
| Description | Update a subcolumn of a Kaiten column. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/columns/{column_id}/subcolumns/{subcolumn_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `column_id` | `integer` | yes | — | — | Column ID |
| `subcolumn_id` | `integer` | yes | — | — | Subcolumn ID |
| `title` | `string` | no | — | — | New title |
| `sort_order` | `number` | no | — | — | Sort order |
| `wip_limit` | `integer` | no | — | — | WIP limit |
| `col_count` | `integer` | no | — | — | Number of sub-columns to split into |

**Examples**

- Update a subcolumn.: `kaiten --json subcolumns update --column-id 20 --subcolumn-id 30 --title "Blocked"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/boards/{board_id}/lanes` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `board_id` | `integer` | yes | — | — | Board ID |
| `title` | `string` | yes | — | — | Lane title |
| `sort_order` | `number` | no | — | — | Sort order |
| `row_count` | `integer` | no | — | — | Number of sub-rows to split into |
| `wip_limit` | `integer` | no | — | — | WIP limit |
| `wip_limit_type` | `integer` | no | — | — | WIP limit type (1=cards count, 2=size sum) |
| `default_card_type_id` | `integer` | no | — | — | Default card type ID for new cards in this lane |

**Examples**

- Create a board lane.: `kaiten --json lanes create --board-id 10 --title "Backend"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `lanes.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten lanes delete` |
| MCP alias | `kaiten_delete_lane` |
| Description | Delete a lane from a Kaiten board. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/boards/{board_id}/lanes/{lane_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `board_id` | `integer` | yes | — | — | Board ID |
| `lane_id` | `integer` | yes | — | — | Lane ID |

**Examples**

- Delete a lane.: `kaiten --json lanes delete --board-id 10 --lane-id 20`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `lanes.list`

| Field | Value |
|---|---|
| CLI command | `kaiten lanes list` |
| MCP alias | `kaiten_list_lanes` |
| Description | List lanes (swimlanes) on a Kaiten board. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/boards/{board_id}/lanes` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `board_id` | `integer` | yes | — | — | Board ID |

**Examples**

- List lanes on a board.: `kaiten --json lanes list --board-id 10`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `lanes.update`

| Field | Value |
|---|---|
| CLI command | `kaiten lanes update` |
| MCP alias | `kaiten_update_lane` |
| Description | Update a lane on a Kaiten board. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/boards/{board_id}/lanes/{lane_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `board_id` | `integer` | yes | — | — | Board ID |
| `lane_id` | `integer` | yes | — | — | Lane ID |
| `title` | `string` | no | — | — | New title |
| `sort_order` | `number` | no | — | — | Sort order |
| `row_count` | `integer` | no | — | — | Number of sub-rows to split into |
| `wip_limit` | `integer` | no | — | — | WIP limit |
| `wip_limit_type` | `integer` | no | — | — | WIP limit type (1=cards count, 2=size sum) |
| `default_card_type_id` | `integer` | no | — | — | Default card type ID for new cards in this lane |
| `condition` | `integer` | no | `1`, `2` | — | 1=active, 2=archived |

**Examples**

- Update a lane.: `kaiten --json lanes update --board-id 10 --lane-id 20 --title "Backend"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

<a id="module-card-types"></a>
## Типы карточек (`card_types`) — 8 commands

Card types and type metadata.

**Namespace tree**

```text
card-types
  create
  delete
  get
  list
  update
card-types.tree-entities
  add
  list
  remove
```

### `card-types.create`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types create` |
| MCP alias | `kaiten_create_card_type` |
| Description | Create a Kaiten card type. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/card-types` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Type name (1-64 chars) |
| `letter` | `string` | yes | — | — | Single letter or emoji |
| `color` | `integer` | yes | — | — | Color (2-25) |
| `description_template` | `string` | no | — | — | Template for card description |

**Examples**

- Create a card type.: `kaiten --json card-types create --name "Feature" --letter F --color 3`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-types.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types delete` |
| MCP alias | `kaiten_delete_card_type` |
| Description | Delete a Kaiten card type. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/card-types/{type_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `type_id` | `integer` | yes | — | — | Card type ID to delete |
| `replace_type_id` | `integer` | yes | — | — | Replacement card type ID |
| `has_to_replace_in_automation` | `boolean` | no | — | — | Replace this type in automations. |
| `has_to_replace_in_restriction` | `boolean` | no | — | — | Replace this type in restrictions. |
| `has_to_replace_in_workflow` | `boolean` | no | — | — | Replace this type in workflows. |

**Examples**

- Delete a card type with replacement.: `kaiten --json card-types delete --type-id 42 --replace-type-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-types.get`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types get` |
| MCP alias | `kaiten_get_card_type` |
| Description | Get a Kaiten card type by ID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/card-types/{type_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `type_id` | `integer` | yes | — | — | Card type ID |

**Examples**

- Get a card type.: `kaiten --json card-types get --type-id 42`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-types.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types list` |
| MCP alias | `kaiten_list_card_types` |
| Description | List Kaiten card types. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/card-types` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Search filter |
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- List card types.: `kaiten --json card-types list --query "bug"`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-types.tree-entities.add`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types tree-entities add` |
| MCP alias | `kaiten_add_card_type_tree_entity` |
| Description | Attach a tree entity to a card type. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/card-types/{type_id}/tree-entities` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `type_id` | `integer` | yes | — | — | Card type ID |
| `tree_entity_uid` | `string` | yes | — | — | Tree entity UID |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Attach a tree entity to a card type.: `kaiten --json card-types tree-entities add --type-id 42 --tree-entity-uid entity-uuid`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-types.tree-entities.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types tree-entities list` |
| MCP alias | `kaiten_list_card_type_tree_entities` |
| Description | List tree entities attached to a card type. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/card-types/{type_id}/tree-entities` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `type_id` | `integer` | yes | — | — | Card type ID |

**Examples**

- List card type tree entities.: `kaiten --json card-types tree-entities list --type-id 42`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-types.tree-entities.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types tree-entities remove` |
| MCP alias | `kaiten_remove_card_type_tree_entity` |
| Description | Remove a tree entity from a card type. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/card-types/{type_id}/tree-entities/{tree_entity_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `type_id` | `integer` | yes | — | — | Card type ID |
| `tree_entity_uid` | `string` | yes | — | — | Tree entity UID |

**Examples**

- Remove a tree entity from a card type.: `kaiten --json card-types tree-entities remove --type-id 42 --tree-entity-uid entity-uuid`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-types.update`

| Field | Value |
|---|---|
| CLI command | `kaiten card-types update` |
| MCP alias | `kaiten_update_card_type` |
| Description | Update a Kaiten card type. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/card-types/{type_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `type_id` | `integer` | yes | — | — | Card type ID |
| `name` | `string` | no | — | — | New name |
| `letter` | `string` | no | — | — | New letter |
| `color` | `integer` | no | — | — | New color (2-25) |
| `description_template` | `string` | no | — | — | Description template |

**Examples**

- Update a card type.: `kaiten --json card-types update --type-id 42 --name "Bug"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

<a id="module-custom-directories"></a>
## Каталоги / Custom directories (`custom_directories`) — 16 commands

Kaiten Catalogs: directories, fields, records and linked cards.

**Namespace tree**

```text
custom-directories
  create
  delete
  get
  list
  update
custom-directory-fields
  create
  delete
  get
  list
  update
custom-directory-records
  create
  delete
  get
  list
  update
custom-directory-records.cards
  list
```

### `custom-directories.create`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directories create` |
| MCP alias | `kaiten_create_custom_directory` |
| Description | Create a Kaiten Catalog (custom directory). |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-directories` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Directory name. |
| `description` | `string|null` | no | — | — | Directory description. |
| `settings` | `object` | no | — | — | Directory settings, for example multi_select or allow_editing. |
| `fields` | `array` | no | — | — | Initial directory fields, when supported by the API. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. Merged into the request body. |

**Examples**

- Create a Catalog.: `kaiten --json custom-directories create --name "Contacts" --settings '{"multi_select":false,"allow_editing":true}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directories.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directories delete` |
| MCP alias | `kaiten_delete_custom_directory` |
| Description | Delete a Kaiten Catalog (custom directory). |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-directories/{directory_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |

**Examples**

- Delete a Catalog.: `kaiten --json custom-directories delete --directory-id dir-uuid`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directories.get`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directories get` |
| MCP alias | `kaiten_get_custom_directory` |
| Description | Get a Kaiten Catalog (custom directory). |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/company/custom-directories/{directory_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `include_fields` | `boolean` | no | — | — | Include directory field definitions. |
| `include_author` | `boolean` | no | — | — | Include author user object. |
| `include_records_count` | `boolean` | no | — | — | Include records_count. |

**Examples**

- Get a Catalog.: `kaiten --json custom-directories get --directory-id dir-uuid`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directories.list`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directories list` |
| MCP alias | `kaiten_list_custom_directories` |
| Description | List Kaiten Catalogs (custom directories). |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/custom-directories` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `include_fields` | `boolean` | no | — | — | Include directory field definitions. |
| `include_author` | `boolean` | no | — | — | Include author user object. |
| `include_records_count` | `boolean` | no | — | — | Include records_count. |
| `query` | `string` | no | — | — | Search by directory name. |
| `conditions` | `array` | no | — | — | Condition filters, for example ["active", "inactive", "removed"]. |
| `limit` | `integer` | no | — | — | Max results, capped by Kaiten at 200. |
| `offset` | `integer` | no | — | — | Pagination offset. |

**Examples**

- List Catalogs with field metadata and record counts.: `kaiten --json custom-directories list --include-fields --include-records-count`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directories.update`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directories update` |
| MCP alias | `kaiten_update_custom_directory` |
| Description | Update a Kaiten Catalog (custom directory). |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-directories/{directory_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `name` | `string` | no | — | — | Directory name. |
| `description` | `string|null` | no | — | — | Directory description. |
| `settings` | `object` | no | — | — | Directory settings. |
| `condition` | `string` | no | `active`, `inactive`, `removed` | — | Directory condition. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. Merged into the request body. |

**Examples**

- Update a Catalog.: `kaiten --json custom-directories update --directory-id dir-uuid --name "Clients"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directory-fields.create`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directory-fields create` |
| MCP alias | `kaiten_create_custom_directory_field` |
| Description | Create a field (column) in a Kaiten Catalog. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-directories/{directory_id}/fields` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `name` | `string` | yes | — | — | Field name. |
| `type` | `string` | yes | — | — | Field type, for example string, email, phone, or catalog. |
| `required` | `boolean` | no | — | — | Whether the field is required. |
| `is_display` | `boolean` | no | — | — | Whether the field is used as display value. |
| `sort_order` | `number` | no | — | — | Field sort order. |
| `settings` | `object` | no | — | — | Type-specific field settings. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. Merged into the request body. |

**Examples**

- Create a Catalog field.: `kaiten --json custom-directory-fields create --directory-id dir-uuid --name Email --type email`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directory-fields.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directory-fields delete` |
| MCP alias | `kaiten_delete_custom_directory_field` |
| Description | Delete a field (column) from a Kaiten Catalog. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-directories/{directory_id}/fields/{field_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `field_id` | `string` | yes | — | — | Custom directory field ID (UUID). |

**Examples**

- Delete a Catalog field.: `kaiten --json custom-directory-fields delete --directory-id dir-uuid --field-id field-uuid`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directory-fields.get`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directory-fields get` |
| MCP alias | `kaiten_get_custom_directory_field` |
| Description | Get a field (column) of a Kaiten Catalog. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/company/custom-directories/{directory_id}/fields/{field_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `field_id` | `string` | yes | — | — | Custom directory field ID (UUID). |

**Examples**

- Get a Catalog field.: `kaiten --json custom-directory-fields get --directory-id dir-uuid --field-id field-uuid`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directory-fields.list`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directory-fields list` |
| MCP alias | `kaiten_list_custom_directory_fields` |
| Description | List fields (columns) of a Kaiten Catalog. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/custom-directories/{directory_id}/fields` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `include_author` | `boolean` | no | — | — | Include author user object. |
| `conditions` | `array` | no | — | — | Condition filters, for example ["active", "inactive", "removed"]. |

**Examples**

- List Catalog fields.: `kaiten --json custom-directory-fields list --directory-id dir-uuid`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directory-fields.update`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directory-fields update` |
| MCP alias | `kaiten_update_custom_directory_field` |
| Description | Update a field (column) in a Kaiten Catalog. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-directories/{directory_id}/fields/{field_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `field_id` | `string` | yes | — | — | Custom directory field ID (UUID). |
| `name` | `string` | no | — | — | Field name. |
| `required` | `boolean` | no | — | — | Whether the field is required. |
| `is_display` | `boolean` | no | — | — | Whether the field is used as display value. |
| `sort_order` | `number` | no | — | — | Field sort order. |
| `condition` | `string` | no | `active`, `inactive`, `removed` | — | Field condition. |
| `settings` | `object` | no | — | — | Type-specific field settings. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. Merged into the request body. |

**Examples**

- Update a Catalog field.: `kaiten --json custom-directory-fields update --directory-id dir-uuid --field-id field-uuid --required`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directory-records.cards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directory-records cards list` |
| MCP alias | `kaiten_list_custom_directory_record_cards` |
| Description | List cards linked to a Kaiten Catalog record. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/custom-directories/{directory_id}/records/{record_id}/cards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `record_id` | `string` | yes | — | — | Custom directory record ID (UUID). |
| `filter` | `string` | no | — | — | Base64-encoded JSON card filter. |
| `limit` | `integer` | no | — | — | Max results, capped by Kaiten at 100. |
| `offset` | `integer` | no | — | — | Pagination offset. |

**Examples**

- List cards linked to a Catalog record.: `kaiten --json custom-directory-records cards list --directory-id dir-uuid --record-id record-uuid`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directory-records.create`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directory-records create` |
| MCP alias | `kaiten_create_custom_directory_record` |
| Description | Create a record (row) in a Kaiten Catalog. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-directories/{directory_id}/records` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `values` | `object|array` | yes | — | — | Field values for the record. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. Merged into the request body. |

**Examples**

- Create a Catalog record.: `kaiten --json custom-directory-records create --directory-id dir-uuid --values '{"field-uuid":"Alice"}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directory-records.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directory-records delete` |
| MCP alias | `kaiten_delete_custom_directory_record` |
| Description | Delete a record (row) from a Kaiten Catalog. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-directories/{directory_id}/records/{record_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `record_id` | `string` | yes | — | — | Custom directory record ID (UUID). |

**Examples**

- Delete a Catalog record.: `kaiten --json custom-directory-records delete --directory-id dir-uuid --record-id record-uuid`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directory-records.get`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directory-records get` |
| MCP alias | `kaiten_get_custom_directory_record` |
| Description | Get a record (row) from a Kaiten Catalog. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/company/custom-directories/{directory_id}/records/{record_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `record_id` | `string` | yes | — | — | Custom directory record ID (UUID). |
| `profile` | `string` | no | `none`, `summary`, `details`, `full` | — | Controls included relations. |

**Examples**

- Get a Catalog record.: `kaiten --json custom-directory-records get --directory-id dir-uuid --record-id record-uuid`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directory-records.list`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directory-records list` |
| MCP alias | `kaiten_list_custom_directory_records` |
| Description | List records (rows) of a Kaiten Catalog. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/custom-directories/{directory_id}/records` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `query` | `string` | no | — | — | Quick search by record display value. |
| `profile` | `string` | no | `none`, `summary`, `details`, `full` | — | Controls included relations. |
| `include_values` | `boolean` | no | — | — | Legacy flag to include values array. |
| `include_author` | `boolean` | no | — | — | Include author user object. |
| `conditions` | `array` | no | — | — | Condition filters, for example ["active", "inactive", "removed"]. |
| `filters` | `object` | no | — | — | Advanced field-based filters as JSON. |
| `filter_operator` | `string` | no | `and`, `or` | — | Boolean operator for filters. |
| `limit` | `integer` | no | — | — | Max results, capped by Kaiten at 100. |
| `offset` | `integer` | no | — | — | Pagination offset. |

**Examples**

- List Catalog records.: `kaiten --json custom-directory-records list --directory-id dir-uuid --profile summary`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

### `custom-directory-records.update`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-directory-records update` |
| MCP alias | `kaiten_update_custom_directory_record` |
| Description | Update a record (row) in a Kaiten Catalog. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-directories/{directory_id}/records/{record_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `directory_id` | `string` | yes | — | — | Custom directory ID (UUID). |
| `record_id` | `string` | yes | — | — | Custom directory record ID (UUID). |
| `values` | `object|array` | no | — | — | Field values for the record. |
| `condition` | `string` | no | `active`, `inactive`, `removed` | — | Record condition. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. Merged into the request body. |

**Examples**

- Update a Catalog record.: `kaiten --json custom-directory-records update --directory-id dir-uuid --record-id record-uuid --values '{"field-uuid":"Bob"}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Kaiten UI calls this feature `Каталоги`; Developers API calls it `custom-directories`; users may also call it `справочник`, `catalog`, or `directory`.
- For a `справочник-таблица`, `справочник таблица`, or `табличный справочник`, use these commands.
- Use these commands for table/database-like catalogs with fields and records, such as clients, contacts, equipment, or contractors.
- `custom-directories` manages the catalog itself, `custom-directory-fields` manages table columns, and `custom-directory-records` manages table rows.
- Do not confuse this with `custom-properties catalog-values`, which manages values for custom fields of type catalog.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.
- If a request says only `каталог`, `справочник`, or `catalog` before a mutation, clarify whether it means UI `Каталоги`, a card field of type `Справочник` (`custom-properties.*`), its values (`custom-properties catalog-values`), or document groups.
- The Developers API marks custom directories, fields, and records as beta; parameters and response formats may change.

<a id="module-custom-properties"></a>
## Кастомные свойства (`custom_properties`) — 25 commands

Custom properties, select values, catalog-values and collective values.

**Namespace tree**

```text
custom-properties
  create
  delete
  get
  list
  update
custom-properties.catalog-values
  create
  delete
  get
  list
  update
custom-properties.collective-score-values
  create
  list
  update
custom-properties.collective-vote-values
  create
  delete
  list
  update
custom-properties.select-values
  create
  delete
  get
  list
  update
custom-properties.tree-entities
  add
  list
  remove
```

### `custom-properties.catalog-values.create`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties catalog-values create` |
| MCP alias | `kaiten_create_catalog_value` |
| Description | Create a catalog property value for a catalog-typed custom property. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-properties/{property_id}/catalog-values` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `name` | `string` | no | — | — | Catalog value display name |
| `value` | `object` | yes | — | — | Catalog value fields keyed by field UID. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Create a catalog property value.: `kaiten --json custom-properties catalog-values create --property-id 5 --value '{"field-uuid":"Alice"}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- These are catalog property values: values/options of a catalog-typed custom property, identified by `property_id`.
- Значения поля карточки типа `Справочник` / `справочник` are managed by these commands.
- Use these commands for values/options of a card field of type `Справочник` / `справочник`.
- Use these commands when the request is about property catalog options/values, not the UI catalog table itself (`custom-directories`).
- For UI catalog tables use custom-directories, custom-directory-fields, and custom-directory-records.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.

### `custom-properties.catalog-values.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties catalog-values delete` |
| MCP alias | `kaiten_delete_catalog_value` |
| Description | Delete a catalog property value for a catalog-typed custom property. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-properties/{property_id}/catalog-values/{value_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `value_id` | `integer` | yes | — | — | Catalog value ID |

**Examples**

- Delete a catalog property value.: `kaiten --json custom-properties catalog-values delete --property-id 5 --value-id 10`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- These are catalog property values: values/options of a catalog-typed custom property, identified by `property_id`.
- Значения поля карточки типа `Справочник` / `справочник` are managed by these commands.
- Use these commands for values/options of a card field of type `Справочник` / `справочник`.
- Use these commands when the request is about property catalog options/values, not the UI catalog table itself (`custom-directories`).
- For UI catalog tables use custom-directories, custom-directory-fields, and custom-directory-records.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.

### `custom-properties.catalog-values.get`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties catalog-values get` |
| MCP alias | `kaiten_get_catalog_value` |
| Description | Get a catalog property value for a catalog-typed custom property. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/company/custom-properties/{property_id}/catalog-values/{value_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `value_id` | `integer` | yes | — | — | Catalog value ID |

**Examples**

- Get a catalog property value.: `kaiten --json custom-properties catalog-values get --property-id 5 --value-id 10`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- These are catalog property values: values/options of a catalog-typed custom property, identified by `property_id`.
- Значения поля карточки типа `Справочник` / `справочник` are managed by these commands.
- Use these commands for values/options of a card field of type `Справочник` / `справочник`.
- Use these commands when the request is about property catalog options/values, not the UI catalog table itself (`custom-directories`).
- For UI catalog tables use custom-directories, custom-directory-fields, and custom-directory-records.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.

### `custom-properties.catalog-values.list`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties catalog-values list` |
| MCP alias | `kaiten_list_catalog_values` |
| Description | List catalog property values for a catalog-typed custom property. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/custom-properties/{property_id}/catalog-values` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `query` | `string` | no | — | — | Text search filter by catalog values |
| `conditions` | `string` | no | — | — | Condition filter: active or inactive |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results |
| `offset` | `integer` | no | — | >= 0 | Pagination offset |

**Examples**

- List catalog property values.: `kaiten --json custom-properties catalog-values list --property-id 5`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- These are catalog property values: values/options of a catalog-typed custom property, identified by `property_id`.
- Значения поля карточки типа `Справочник` / `справочник` are managed by these commands.
- Use these commands for values/options of a card field of type `Справочник` / `справочник`.
- Use these commands when the request is about property catalog options/values, not the UI catalog table itself (`custom-directories`).
- For UI catalog tables use custom-directories, custom-directory-fields, and custom-directory-records.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.

### `custom-properties.catalog-values.update`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties catalog-values update` |
| MCP alias | `kaiten_update_catalog_value` |
| Description | Update a catalog property value for a catalog-typed custom property. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-properties/{property_id}/catalog-values/{value_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `value_id` | `integer` | yes | — | — | Catalog value ID |
| `name` | `string` | no | — | — | Catalog value display name |
| `value` | `object` | no | — | — | Catalog value fields keyed by field UID. |
| `condition` | `string` | no | `active`, `inactive` | — | Value condition |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Update a catalog property value.: `kaiten --json custom-properties catalog-values update --property-id 5 --value-id 10 --name "Alice"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- These are catalog property values: values/options of a catalog-typed custom property, identified by `property_id`.
- Значения поля карточки типа `Справочник` / `справочник` are managed by these commands.
- Use these commands for values/options of a card field of type `Справочник` / `справочник`.
- Use these commands when the request is about property catalog options/values, not the UI catalog table itself (`custom-directories`).
- For UI catalog tables use custom-directories, custom-directory-fields, and custom-directory-records.
- Do not confuse this with document folders/containers; those use `document-groups.*` and tree navigation.

### `custom-properties.collective-score-values.create`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties collective-score-values create` |
| MCP alias | `kaiten_create_collective_score_value` |
| Description | Create a collective score value for a card custom property. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/custom-properties/{property_id}/collective-score-values` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `property_id` | `integer` | yes | — | — | Property ID |
| `value` | `string|number|object` | yes | — | — | Score value. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Create a collective score value.: `kaiten --json custom-properties collective-score-values create --card-id 10 --property-id 5 --value 8`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.collective-score-values.list`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties collective-score-values list` |
| MCP alias | `kaiten_list_collective_score_values` |
| Description | List collective score values for a card custom property. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/custom-properties/{property_id}/collective-score-values` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `property_id` | `integer` | yes | — | — | Property ID |

**Examples**

- List collective score values.: `kaiten --json custom-properties collective-score-values list --card-id 10 --property-id 5`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.collective-score-values.update`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties collective-score-values update` |
| MCP alias | `kaiten_update_collective_score_value` |
| Description | Update a collective score value for a card custom property. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/custom-properties/{property_id}/collective-score-values/{value_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `property_id` | `integer` | yes | — | — | Property ID |
| `value_id` | `integer` | yes | — | — | Score value ID |
| `value` | `string|number|object` | no | — | — | Score value. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Update a collective score value.: `kaiten --json custom-properties collective-score-values update --card-id 10 --property-id 5 --value-id 1 --value 9`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.collective-vote-values.create`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties collective-vote-values create` |
| MCP alias | `kaiten_create_collective_vote_value` |
| Description | Create a collective vote value for a card custom property. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/custom-properties/{property_id}/collective-vote-values` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `property_id` | `integer` | yes | — | — | Property ID |
| `value` | `string|number|object` | yes | — | — | Vote value. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Create a collective vote value.: `kaiten --json custom-properties collective-vote-values create --card-id 10 --property-id 5 --value 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.collective-vote-values.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties collective-vote-values delete` |
| MCP alias | `kaiten_delete_collective_vote_value` |
| Description | Delete a collective vote value for a card custom property. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/custom-properties/{property_id}/collective-vote-values/{value_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `property_id` | `integer` | yes | — | — | Property ID |
| `value_id` | `integer` | yes | — | — | Vote value ID |

**Examples**

- Delete a collective vote value.: `kaiten --json custom-properties collective-vote-values delete --card-id 10 --property-id 5 --value-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.collective-vote-values.list`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties collective-vote-values list` |
| MCP alias | `kaiten_list_collective_vote_values` |
| Description | List collective vote values for a card custom property. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/custom-properties/{property_id}/collective-vote-values` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `property_id` | `integer` | yes | — | — | Property ID |

**Examples**

- List collective vote values.: `kaiten --json custom-properties collective-vote-values list --card-id 10 --property-id 5`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.collective-vote-values.update`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties collective-vote-values update` |
| MCP alias | `kaiten_update_collective_vote_value` |
| Description | Update a collective vote value for a card custom property. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/custom-properties/{property_id}/collective-vote-values/{value_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `property_id` | `integer` | yes | — | — | Property ID |
| `value_id` | `integer` | yes | — | — | Vote value ID |
| `value` | `string|number|object` | no | — | — | Vote value. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Update a collective vote value.: `kaiten --json custom-properties collective-vote-values update --card-id 10 --property-id 5 --value-id 1 --value 2`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.create`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties create` |
| MCP alias | `kaiten_create_custom_property` |
| Description | Create a company custom property. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-properties` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Property name (1-255 chars) |
| `type` | `string` | yes | `string`, `number`, `date`, `email`, `checkbox`, `select`, `formula`, `url`, `collective_score`, `vote`, `collective_vote`, `catalog`, `phone`, `user`, `attachment` | — | Property type |
| `show_on_facade` | `boolean` | no | — | — | Show on card facade |
| `multi_select` | `boolean` | no | — | — | Enable multi-select |
| `colorful` | `boolean` | no | — | — | Enable colors for select values |
| `multiline` | `boolean` | no | — | — | Multiline text field |
| `values_creatable_by_users` | `boolean` | no | — | — | Allow regular users to create values |
| `values_type` | `string` | no | `number`, `text` | — | Values type (required for collective_score) |
| `vote_variant` | `string` | no | `rating`, `scale`, `emoji_set` | — | Vote variant (required for vote/collective_vote) |
| `color` | `integer` | no | — | — | Color index |
| `data` | `object` | no | — | — | Type-specific data; required for vote/collective_vote and some other typed properties |

**Examples**

- Create a custom property.: `kaiten --json custom-properties create --name Status --type select`
- Create a card field of type Catalog/Справочник.: `kaiten --json custom-properties create --name "Client" --type catalog`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- A card field of type `Справочник` / `справочник` is a Kaiten custom property with API type `catalog`.
- Само поле карточки типа `Справочник` / `справочник` is managed by `custom-properties.*`.
- Use `custom-properties.*` to list, create, update, get, or delete the card field definition itself.
- Allowed entries/options are managed separately from the field definition.
- Do not confuse this with UI catalog tables (`custom-directories`) or document groups.

### `custom-properties.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties delete` |
| MCP alias | `kaiten_delete_custom_property` |
| Description | Delete a custom property. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-properties/{property_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |

**Examples**

- Delete a custom property.: `kaiten --json custom-properties delete --property-id 5`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- A card field of type `Справочник` / `справочник` is a Kaiten custom property with API type `catalog`.
- Само поле карточки типа `Справочник` / `справочник` is managed by `custom-properties.*`.
- Use `custom-properties.*` to list, create, update, get, or delete the card field definition itself.
- Allowed entries/options are managed separately from the field definition.
- Do not confuse this with UI catalog tables (`custom-directories`) or document groups.

### `custom-properties.get`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties get` |
| MCP alias | `kaiten_get_custom_property` |
| Description | Get a custom property by ID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/company/custom-properties/{property_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |

**Examples**

- Get a custom property.: `kaiten --json custom-properties get --property-id 5`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- A card field of type `Справочник` / `справочник` is a Kaiten custom property with API type `catalog`.
- Само поле карточки типа `Справочник` / `справочник` is managed by `custom-properties.*`.
- Use `custom-properties.*` to list, create, update, get, or delete the card field definition itself.
- Allowed entries/options are managed separately from the field definition.
- Do not confuse this with UI catalog tables (`custom-directories`) or document groups.

### `custom-properties.list`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties list` |
| MCP alias | `kaiten_list_custom_properties` |
| Description | List company custom properties. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/custom-properties` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `include_values` | `boolean` | no | — | — | Deprecated compatibility input. false is ignored; true is rejected. Use select-values.list or catalog-values.list instead. |
| `include_author` | `boolean` | no | — | — | Include author user object |
| `types` | `string` | no | — | — | Comma-separated type names to filter |
| `conditions` | `string` | no | — | — | Comma-separated conditions to filter |
| `query` | `string` | no | — | — | Search filter by name |
| `order_by` | `string` | no | — | — | Sort column |
| `order_direction` | `string` | no | — | — | Sort direction (asc or desc) |
| `board_id` | `integer` | no | — | — | Filter properties available on a specific board |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results |
| `offset` | `integer` | no | — | >= 0 | Pagination offset |

**Examples**

- List custom properties.: `kaiten --json custom-properties list --types select`
- List card fields of type Catalog/Справочник.: `kaiten --json custom-properties list --types catalog`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- A card field of type `Справочник` / `справочник` is a Kaiten custom property with API type `catalog`.
- Само поле карточки типа `Справочник` / `справочник` is managed by `custom-properties.*`.
- Use `custom-properties.*` to list, create, update, get, or delete the card field definition itself.
- Allowed entries/options are managed separately from the field definition.
- Do not confuse this with UI catalog tables (`custom-directories`) or document groups.
- include_values is retained only as a migration input: false is ignored and true fails with replacement command guidance.

### `custom-properties.select-values.create`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties select-values create` |
| MCP alias | `kaiten_create_select_value` |
| Description | Create a select value for a custom property. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-properties/{property_id}/select-values` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `value` | `string` | yes | — | — | Select value text |
| `color` | `integer` | no | — | — | Color index |
| `sort_order` | `number` | no | — | — | Sort order (float) |

**Examples**

- Create a select value.: `kaiten --json custom-properties select-values create --property-id 3 --value High`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.select-values.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties select-values delete` |
| MCP alias | `kaiten_delete_select_value` |
| Description | Delete (soft) a select value through the official DELETE route. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-properties/{property_id}/select-values/{value_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `value_id` | `integer` | yes | — | — | Select value ID |

**Examples**

- Soft-delete a select value.: `kaiten --json custom-properties select-values delete --property-id 3 --value-id 10`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.select-values.get`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties select-values get` |
| MCP alias | `kaiten_get_select_value` |
| Description | Get a single select value by ID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/company/custom-properties/{property_id}/select-values/{value_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `value_id` | `integer` | yes | — | — | Select value ID |

**Examples**

- Get a select value.: `kaiten --json custom-properties select-values get --property-id 3 --value-id 10`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.select-values.list`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties select-values list` |
| MCP alias | `kaiten_list_select_values` |
| Description | List select values for a custom property. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/custom-properties/{property_id}/select-values` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `query` | `string` | no | — | — | Search filter by value text |
| `order_by` | `string` | no | `id`, `sort_order`, `match_query_priority` | — | Sort order mode |
| `conditions` | `string` | no | — | — | Comma-separated conditions |
| `v2_select_search` | `boolean` | no | — | — | Use v2 search mode |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results |
| `offset` | `integer` | no | — | >= 0 | Pagination offset |

**Examples**

- List select values.: `kaiten --json custom-properties select-values list --property-id 3`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.select-values.update`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties select-values update` |
| MCP alias | `kaiten_update_select_value` |
| Description | Update a select value for a custom property. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-properties/{property_id}/select-values/{value_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `value_id` | `integer` | yes | — | — | Select value ID |
| `value` | `string` | no | — | — | New value text |
| `condition` | `string` | no | `active`, `inactive` | — | Value status |
| `color` | `integer` | no | — | — | Color index |
| `sort_order` | `number` | no | — | — | Sort order (float) |

**Examples**

- Update a select value.: `kaiten --json custom-properties select-values update --property-id 3 --value-id 10 --value Critical`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.tree-entities.add`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties tree-entities add` |
| MCP alias | `kaiten_add_custom_property_tree_entity` |
| Description | Attach a tree entity to a custom property. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-properties/{property_id}/tree-entities` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `tree_entity_uid` | `string` | yes | — | — | Tree entity UID |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Attach a tree entity to a custom property.: `kaiten --json custom-properties tree-entities add --property-id 5 --tree-entity-uid entity-uuid`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.tree-entities.list`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties tree-entities list` |
| MCP alias | `kaiten_list_custom_property_tree_entities` |
| Description | List tree entities attached to a custom property. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/custom-properties/{property_id}/tree-entities` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |

**Examples**

- List custom property tree entities.: `kaiten --json custom-properties tree-entities list --property-id 5`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.tree-entities.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties tree-entities remove` |
| MCP alias | `kaiten_remove_custom_property_tree_entity` |
| Description | Remove a tree entity from a custom property. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-properties/{property_id}/tree-entities/{tree_entity_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `tree_entity_uid` | `string` | yes | — | — | Tree entity UID |

**Examples**

- Remove a tree entity from a custom property.: `kaiten --json custom-properties tree-entities remove --property-id 5 --tree-entity-uid entity-uuid`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `custom-properties.update`

| Field | Value |
|---|---|
| CLI command | `kaiten custom-properties update` |
| MCP alias | `kaiten_update_custom_property` |
| Description | Update a custom property. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/custom-properties/{property_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `property_id` | `integer` | yes | — | — | Property ID |
| `name` | `string` | no | — | — | New name |
| `condition` | `string` | no | `active`, `inactive` | — | Status |
| `show_on_facade` | `boolean` | no | — | — | Show on card facade |
| `multi_select` | `boolean` | no | — | — | Multi-select mode |
| `colorful` | `boolean` | no | — | — | Enable colors |
| `multiline` | `boolean` | no | — | — | Multiline mode |
| `values_creatable_by_users` | `boolean` | no | — | — | Allow users to create values |
| `is_used_as_progress` | `boolean` | no | — | — | Use this formula property as progress |
| `color` | `integer` | no | — | — | Color index |
| `data` | `object` | no | — | — | Type-specific data |
| `fields_settings` | `object` | no | — | — | Catalog fields configuration |

**Examples**

- Update a custom property.: `kaiten --json custom-properties update --property-id 5 --name Priority`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- A card field of type `Справочник` / `справочник` is a Kaiten custom property with API type `catalog`.
- Само поле карточки типа `Справочник` / `справочник` is managed by `custom-properties.*`.
- Use `custom-properties.*` to list, create, update, get, or delete the card field definition itself.
- Allowed entries/options are managed separately from the field definition.
- Do not confuse this with UI catalog tables (`custom-directories`) or document groups.

<a id="module-documents"></a>
## Документы (`documents`) — 13 commands

Documents and document groups.

**Namespace tree**

```text
document-files
  get-url
  upload
document-groups
  create
  delete
  get
  list
  update
document-schemas
  get
documents
  create
  delete
  get
  list
  update
```

### `document-files.get-url`

| Field | Value |
|---|---|
| CLI command | `kaiten document-files get-url` |
| MCP alias | `kaiten_get_document_file_url` |
| Description | Resolve a document file to a short-lived signed download URL. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/documents/{document_uid}/files/{file_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `document_uid` | `string` | yes | — | — | Document UID |
| `file_id` | `string` | yes | — | — | Document file UID without extension |

**Examples**

- Resolve a private document file URL for download.: `kaiten --json document-files get-url --document-uid doc-1 --file-id file-1`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Uses `prevent_redirect=true`, so the response is JSON with a short-lived signed storage URL instead of an HTTP redirect.

### `document-files.upload`

| Field | Value |
|---|---|
| CLI command | `kaiten document-files upload` |
| MCP alias | `kaiten_upload_document_file` |
| Description | Upload a local binary file to a Kaiten document using multipart/form-data. |
| Method | `PUT` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/documents/{document_uid}/files` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `document_uid` | `string` | yes | — | — | Document UID. |
| `file` | `string` | yes | — | — | Local file path to upload. |

**Examples**

- Upload a local file to a document.: `kaiten --json document-files upload --document-uid doc-1 --file ./screenshot.png`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Uploads the local file as multipart/form-data field `file`.
- The returned `id` can be used as a ProseMirror image node `attrs.fileId`.

### `document-groups.create`

| Field | Value |
|---|---|
| CLI command | `kaiten document-groups create` |
| MCP alias | `kaiten_create_document_group` |
| Description | Create a new Kaiten document group. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/document-groups` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `title` | `string` | yes | — | — | Group title |
| `parent_entity_uid` | `string` | no | — | — | Parent group UID for nesting |
| `sort_order` | `integer` | no | — | — | Sort order (auto-generated if not provided) |

**Examples**

- Create a document group.: `kaiten --json document-groups create --title "Engineering"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Document groups are document folders/containers in the sidebar tree.
- Use `document-groups.*` when a request says document catalog, folder, or container.
- They do not manage UI catalog tables (`custom-directories`) or `custom-properties catalog-values`.
- Documents can be placed into a group with `parent_entity_uid`; tree commands read groups together with documents and spaces.

### `document-groups.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten document-groups delete` |
| MCP alias | `kaiten_delete_document_group` |
| Description | Delete a Kaiten document group. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/document-groups/{group_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Document group UID |

**Examples**

- Delete a document group.: `kaiten --json document-groups delete --group-uid grp-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Document groups are document folders/containers in the sidebar tree.
- Use `document-groups.*` when a request says document catalog, folder, or container.
- They do not manage UI catalog tables (`custom-directories`) or `custom-properties catalog-values`.
- Documents can be placed into a group with `parent_entity_uid`; tree commands read groups together with documents and spaces.

### `document-groups.get`

| Field | Value |
|---|---|
| CLI command | `kaiten document-groups get` |
| MCP alias | `kaiten_get_document_group` |
| Description | Get a Kaiten document group by UID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/document-groups/{group_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Document group UID |

**Examples**

- Get a document group.: `kaiten --json document-groups get --group-uid grp-1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Document groups are document folders/containers in the sidebar tree.
- Use `document-groups.*` when a request says document catalog, folder, or container.
- They do not manage UI catalog tables (`custom-directories`) or `custom-properties catalog-values`.
- Documents can be placed into a group with `parent_entity_uid`; tree commands read groups together with documents and spaces.

### `document-groups.list`

| Field | Value |
|---|---|
| CLI command | `kaiten document-groups list` |
| MCP alias | `kaiten_list_document_groups` |
| Description | List Kaiten document groups. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/document-groups` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Search filter |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default: 50, max: 100) |
| `offset` | `integer` | no | — | >= 0 | Pagination offset |

**Examples**

- List document groups.: `kaiten --json document-groups list --query "Engineering"`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Document groups are document folders/containers in the sidebar tree.
- Use `document-groups.*` when a request says document catalog, folder, or container.
- They do not manage UI catalog tables (`custom-directories`) or `custom-properties catalog-values`.
- Documents can be placed into a group with `parent_entity_uid`; tree commands read groups together with documents and spaces.

### `document-groups.update`

| Field | Value |
|---|---|
| CLI command | `kaiten document-groups update` |
| MCP alias | `kaiten_update_document_group` |
| Description | Update a Kaiten document group. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/document-groups/{group_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Document group UID |
| `title` | `string` | no | — | — | New group title |

**Examples**

- Update a document group.: `kaiten --json document-groups update --group-uid grp-1 --title "Docs"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Document groups are document folders/containers in the sidebar tree.
- Use `document-groups.*` when a request says document catalog, folder, or container.
- They do not manage UI catalog tables (`custom-directories`) or `custom-properties catalog-values`.
- Documents can be placed into a group with `parent_entity_uid`; tree commands read groups together with documents and spaces.

### `document-schemas.get`

| Field | Value |
|---|---|
| CLI command | `kaiten document-schemas get` |
| MCP alias | `kaiten_get_document_schema` |
| Description | Get a document data schema. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/document-schemas/{schema_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `schema_id` | `integer` | yes | — | — | Document schema ID. |

**Examples**

- Get a document data schema.: `kaiten --json document-schemas get --schema-id 1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `documents.create`

| Field | Value |
|---|---|
| CLI command | `kaiten documents create` |
| MCP alias | `kaiten_create_document` |
| Description | Create a new Kaiten document. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/documents` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `title` | `string` | yes | — | — | Document title |
| `text` | `string` | no | — | — | Markdown content converted to ProseMirror. |
| `data` | `object` | no | — | — | Raw ProseMirror JSON. |
| `parent_entity_uid` | `string` | no | — | — | Parent document group UID |
| `sort_order` | `integer` | no | — | — | Sort order (auto-generated if not provided) |
| `key` | `string` | no | — | — | Unique key identifier |

**Examples**

- Create a document from markdown.: `kaiten --json documents create --title "Spec" --text "# Header"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- `parent_entity_uid` places the document under a document group/container in the sidebar tree.
- Do not use document parent fields for UI catalog tables (`custom-directories`) or `custom-properties catalog-values`.

### `documents.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten documents delete` |
| MCP alias | `kaiten_delete_document` |
| Description | Delete a Kaiten document. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/documents/{document_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `document_uid` | `string` | yes | — | — | Document UID |

**Examples**

- Delete a document.: `kaiten --json documents delete --document-uid doc-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `documents.get`

| Field | Value |
|---|---|
| CLI command | `kaiten documents get` |
| MCP alias | `kaiten_get_document` |
| Description | Get a Kaiten document by UID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/documents/{document_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `document_uid` | `string` | yes | — | — | Document UID |
| `markdown` | `boolean` | no | — | — | Save the document body as Markdown instead of returning JSON. |
| `output` | `string` | no | — | — | Markdown output file or directory. Defaults to the current working directory. |
| `overwrite` | `boolean` | no | — | — | Replace an existing Markdown output file. |

**Examples**

- Get a document.: `kaiten --json documents get --document-uid doc-1`
- Save a document as Markdown.: `kaiten --json documents get --document-uid doc-1 --markdown --output ./doc.md`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- `--markdown` does the same document GET, renders the result locally, and saves a Markdown file instead of returning the document JSON.
- `--markdown` keeps document file links as Kaiten `/api/documents/<uid>/files/<file_id>` URLs.
- Use `--output` for the target file/directory and `--overwrite` to replace an existing Markdown file.
- Separate CLI processes do not share in-memory results, so default `--cache-mode auto` persists repeated safe document reads.

### `documents.list`

| Field | Value |
|---|---|
| CLI command | `kaiten documents list` |
| MCP alias | `kaiten_list_documents` |
| Description | List Kaiten documents. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/documents` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Search filter |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default: 50, max: 100) |
| `offset` | `integer` | no | — | >= 0 | Pagination offset |
| `version` | `integer` | no | — | — | Search version. Use 2 for OpenSearch result/position response. |
| `condition` | `integer` | no | — | — | Filter condition for version=2 |
| `search_fields` | `string` | no | — | — | Comma-separated API search fields for version=2. Sent as Kaiten query parameter 'fields'. |
| `start_position` | `string` | no | — | — | Search cursor for version=2 pagination. |
| `include_search_preview` | `boolean` | no | — | — | Include search preview objects for version=2. |
| `fields` | `string` | no | — | — | Comma-separated field names to keep in the response. Example: 'uid,title' |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, nested user objects) |

**Examples**

- List documents.: `kaiten --json documents list --query "Design"`
- List documents with a narrow response surface.: `kaiten --json documents list --compact --fields uid,title`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `documents.update`

| Field | Value |
|---|---|
| CLI command | `kaiten documents update` |
| MCP alias | `kaiten_update_document` |
| Description | Update a Kaiten document. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/documents/{document_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `document_uid` | `string` | yes | — | — | Document UID |
| `title` | `string` | no | — | — | New document title |
| `text` | `string` | no | — | — | Markdown content converted to ProseMirror. |
| `data` | `object` | no | — | — | Raw ProseMirror JSON. |
| `parent_entity_uid` | `string` | no | — | — | New parent group UID |
| `sort_order` | `integer` | no | — | — | Sort order |
| `key` | `string` | no | — | — | Unique key identifier |

**Examples**

- Update a document body.: `kaiten --json documents update --document-uid doc-1 --text "**bold**"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- `parent_entity_uid` places the document under a document group/container in the sidebar tree.
- Do not use document parent fields for UI catalog tables (`custom-directories`) or `custom-properties catalog-values`.

<a id="module-dashboards"></a>
## Дашборды (`dashboards`) — 16 commands

Experimental dashboards, collaborators, widgets and compute jobs.

**Namespace tree**

```text
dashboard-compute-jobs
  create
  get
dashboard-users
  add
  list
  remove
  update
dashboard-widgets
  create
  delete
  list
  update
dashboards
  clone
  create
  delete
  get
  list
  update
```

### `dashboard-compute-jobs.create`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboard-compute-jobs create` |
| MCP alias | `kaiten_create_dashboard_compute_job` |
| Description | Queue computation for up to 100 widgets on an accessible dashboard. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/dashboards/{dashboard_id}/compute-jobs` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |
| `widget_ids` | `array` | yes | — | — | JSON array containing 1 to 100 widget UUIDs. |
| `force` | `boolean` | no | — | — | Force recomputation. |

**Examples**

- Queue widget computation and receive a compute_job_id.: `kaiten --json dashboard-compute-jobs create --dashboard-id <dashboard_uuid> --widget-ids '["<widget_uuid>"]'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- A successful queue operation returns HTTP 202.

### `dashboard-compute-jobs.get`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboard-compute-jobs get` |
| MCP alias | `kaiten_get_dashboard_compute_job` |
| Description | Poll a dashboard compute job without reusing cached status. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/dashboards/{dashboard_id}/compute-jobs/{job_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |
| `job_id` | `string|integer` | yes | — | — | Compute job ID returned by create. |
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Poll queued/running/completed/failed status.: `kaiten --json dashboard-compute-jobs get --dashboard-id <dashboard_uuid> --job-id 123`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- Polling bypasses both request and persistent cache.

### `dashboard-users.add`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboard-users add` |
| MCP alias | `kaiten_add_dashboard_user` |
| Description | Grant a company user viewer or editor access to a dashboard. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/dashboards/{dashboard_id}/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |
| `user_uid` | `string` | yes | — | — | Company user UUID. |
| `role` | `string` | yes | `viewer`, `editor` | — | Dashboard role. |

**Examples**

- Grant view access.: `kaiten --json dashboard-users add --dashboard-id <dashboard_uuid> --user-uid <user_uuid> --role viewer`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- The user must already belong to the company.

### `dashboard-users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboard-users list` |
| MCP alias | `kaiten_list_dashboard_users` |
| Description | List users with explicit access to a dashboard. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/dashboards/{dashboard_id}/users` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |
| `limit` | `integer` | no | — | — | Maximum users to return (server cap 50). |
| `offset` | `integer` | no | — | — | Pagination offset. |
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- List dashboard collaborators.: `kaiten --json dashboard-users list --dashboard-id <dashboard_uuid> --fields user_uid,role`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- Only owners and editors can list or manage access.

### `dashboard-users.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboard-users remove` |
| MCP alias | `kaiten_remove_dashboard_user` |
| Description | Revoke a collaborator's explicit dashboard access. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/dashboards/{dashboard_id}/users/{user_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |
| `user_uid` | `string` | yes | — | — | Company user UUID. |

**Examples**

- Remove explicit dashboard access.: `kaiten --json dashboard-users remove --dashboard-id <dashboard_uuid> --user-uid <user_uuid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- The dashboard owner cannot be removed.

### `dashboard-users.update`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboard-users update` |
| MCP alias | `kaiten_update_dashboard_user` |
| Description | Change a dashboard collaborator role. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/dashboards/{dashboard_id}/users/{user_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |
| `user_uid` | `string` | yes | — | — | Company user UUID. |
| `role` | `string` | yes | `viewer`, `editor` | — | New dashboard role. |

**Examples**

- Promote a collaborator to editor.: `kaiten --json dashboard-users update --dashboard-id <dashboard_uuid> --user-uid <user_uuid> --role editor`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- The owner role cannot be changed or downgraded.

### `dashboard-widgets.create`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboard-widgets create` |
| MCP alias | `kaiten_create_dashboard_widget` |
| Description | Create a widget without freezing the evolving source/config schema client-side. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/dashboards/{dashboard_id}/widgets` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |
| `title` | `string` | yes | — | — | Widget title. |
| `source` | `string` | yes | — | — | Widget source; current examples include metric, cardList, distribution, cardsTrend. |
| `visualization` | `string` | yes | — | — | Visualization identifier accepted by the current Kaiten installation. |
| `config` | `object` | yes | — | — | Source-specific widget config JSON. |

**Examples**

- Create a card-list widget using server-validated config.: `kaiten --json dashboard-widgets create --dashboard-id <dashboard_uuid> --title "Cards" --source cardList --visualization table --config '{"filter":{}}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- Source, visualization and config are validated by Kaiten because their schema changes quickly.
- Current sources include distribution, cardsTrend, velocity, throughput, cycleTimeTrends, burndown, cfd, cycleTime, controlChart, blockResolutionTime, metric, fieldSum, sprintProgress, cardList, dueDates and timeSpent. Current visualizations include bar, horizontalBar, pie, donut, table, line, area, stackedArea, scatter, percentileHistogram, number, numberTrend and battery. Values are intentionally not client-enumerated because the dashboard schema is experimental.

### `dashboard-widgets.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboard-widgets delete` |
| MCP alias | `kaiten_delete_dashboard_widget` |
| Description | Delete a dashboard widget. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/dashboards/{dashboard_id}/widgets/{widget_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |
| `widget_id` | `string` | yes | — | — | Widget UUID. |

**Examples**

- Delete a widget.: `kaiten --json dashboard-widgets delete --dashboard-id <dashboard_uuid> --widget-id <widget_uuid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.

### `dashboard-widgets.list`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboard-widgets list` |
| MCP alias | `kaiten_list_dashboard_widgets` |
| Description | List dashboard widgets through dashboards.get?include=widgets. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `synthetic` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/dashboards/{dashboard_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Extract widgets from a dashboard read.: `kaiten --json dashboard-widgets list --dashboard-id <dashboard_uuid> --fields id,title,source,visualization`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.

### `dashboard-widgets.update`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboard-widgets update` |
| MCP alias | `kaiten_update_dashboard_widget` |
| Description | Update a dashboard widget; config is merged by the server. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/dashboards/{dashboard_id}/widgets/{widget_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |
| `widget_id` | `string` | yes | — | — | Widget UUID. |
| `title` | `string` | no | — | — | Widget title. |
| `source` | `string` | no | — | — | Widget source. |
| `visualization` | `string` | no | — | — | Visualization identifier. |
| `config` | `object` | no | — | — | Partial config merged by Kaiten. |

**Examples**

- Rename a widget.: `kaiten --json dashboard-widgets update --dashboard-id <dashboard_uuid> --widget-id <widget_uuid> --title "Open cards"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- Current sources include distribution, cardsTrend, velocity, throughput, cycleTimeTrends, burndown, cfd, cycleTime, controlChart, blockResolutionTime, metric, fieldSum, sprintProgress, cardList, dueDates and timeSpent. Current visualizations include bar, horizontalBar, pie, donut, table, line, area, stackedArea, scatter, percentileHistogram, number, numberTrend and battery. Values are intentionally not client-enumerated because the dashboard schema is experimental.

### `dashboards.clone`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboards clone` |
| MCP alias | `kaiten_clone_dashboard` |
| Description | Create a personal dashboard copy with new widget IDs. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/dashboards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `source_dashboard_id` | `string` | yes | — | — | Accessible source dashboard UUID. |
| `title` | `string` | yes | — | — | Title for the new dashboard. |
| `is_public` | `boolean` | no | — | — | Override copied visibility; otherwise inherit it. |

**Examples**

- Clone an accessible dashboard into a personal copy.: `kaiten --json dashboards clone --source-dashboard-id <dashboard_uuid> --title "My copy"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- Clone copies layout, filter and widgets with fresh widget IDs; shared users are not copied.

### `dashboards.create`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboards create` |
| MCP alias | `kaiten_create_dashboard` |
| Description | Create a private or public dashboard owned by the current user. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/dashboards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `title` | `string` | yes | — | — | Dashboard title. |
| `is_public` | `boolean` | no | — | — | Make the dashboard visible company-wide (default false). |

**Examples**

- Create a private dashboard.: `kaiten --json dashboards create --title "Team health"`
- Create a public dashboard.: `kaiten --json dashboards create --title "Company metrics" --is-public`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- Only the owner can change title/publicity or delete a dashboard; editors can change layout/filter and manage users/widgets, while viewers have read access.

### `dashboards.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboards delete` |
| MCP alias | `kaiten_delete_dashboard` |
| Description | Archive a dashboard owned by the current user. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/dashboards/{dashboard_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |

**Examples**

- Archive an owned dashboard.: `kaiten --json dashboards delete --dashboard-id <dashboard_uuid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- Only the dashboard owner can delete it.

### `dashboards.get`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboards get` |
| MCP alias | `kaiten_get_dashboard` |
| Description | Get a dashboard and optionally include its widgets. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/dashboards/{dashboard_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |
| `include` | `string` | no | — | — | Comma-separated relations to include; currently widgets. |
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Get dashboard configuration and widgets.: `kaiten --json dashboards get --dashboard-id <dashboard_uuid> --include widgets`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- Only the owner can change title/publicity or delete a dashboard; editors can change layout/filter and manage users/widgets, while viewers have read access.

### `dashboards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboards list` |
| MCP alias | `kaiten_list_dashboards` |
| Description | List dashboards visible to the current user, including public dashboards. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/dashboards` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `search` | `string` | no | — | — | Search dashboard titles. |
| `limit` | `integer` | no | — | — | Maximum dashboards to return (server cap 50). |
| `offset` | `integer` | no | — | — | Pagination offset. |
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Find visible dashboards by title.: `kaiten --json dashboards list --search "Requests" --fields id,title,is_public,role --compact`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.

### `dashboards.update`

| Field | Value |
|---|---|
| CLI command | `kaiten dashboards update` |
| MCP alias | `kaiten_update_dashboard` |
| Description | Update dashboard metadata, filter, or layout. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/dashboards/{dashboard_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `dashboard_id` | `string` | yes | — | — | Dashboard UUID. |
| `title` | `string` | no | — | — | New title (owner only). |
| `is_public` | `boolean` | no | — | — | New visibility (owner only). |
| `filter` | `object|null` | no | — | — | Dashboard filter JSON; use null to clear it. |
| `layout` | `object` | no | — | — | Responsive dashboard layout keyed by breakpoint and widget UUID. |

**Examples**

- Update an editable dashboard layout.: `kaiten --json dashboards update --dashboard-id <dashboard_uuid> --layout '{"lg":{}}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Dashboards are experimental and not yet documented in the public REST catalog; older Kaiten installations may return 404 or 405.
- Only the owner can change title/publicity or delete a dashboard; editors can change layout/filter and manage users/widgets, while viewers have read access.

<a id="module-iterations"></a>
## Итерации (`iterations`) — 9 commands

Beta iterations, iteration cards and card history.

**Namespace tree**

```text
card-iterations-history
  list
iteration-cards
  add
  list
  remove
iterations
  create
  delete
  get
  list
  update
```

### `card-iterations-history.list`

| Field | Value |
|---|---|
| CLI command | `kaiten card-iterations-history list` |
| MCP alias | `kaiten_list_card_iterations_history` |
| Description | List iteration membership history for a card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_uid}/iterations-history` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_uid` | `string` | yes | — | — | Card UUID. |
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Inspect a card's iteration history.: `kaiten --json card-iterations-history list --card-uid <card_uuid> --fields iteration_id,status,added_at,removed_at`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Iterations are beta and require a Kaiten tariff with the Iterations feature enabled.

### `iteration-cards.add`

| Field | Value |
|---|---|
| CLI command | `kaiten iteration-cards add` |
| MCP alias | `kaiten_add_iteration_card` |
| Description | Add an active card from the space primary boards to an iteration. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_uid}/iterations/{iteration_id}/cards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UUID. |
| `iteration_id` | `string` | yes | — | — | Iteration UUID. |
| `card_uid` | `string` | yes | — | — | Card UUID. |

**Examples**

- Add a card to a planned or active iteration.: `kaiten --json iteration-cards add --space-uid <space_uuid> --iteration-id <iteration_uuid> --card-uid <card_uuid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Iterations are beta and require a Kaiten tariff with the Iterations feature enabled.
- Only active cards on a primary board of the same space can be added.

### `iteration-cards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten iteration-cards list` |
| MCP alias | `kaiten_list_iteration_cards` |
| Description | List active or removed card relations for an iteration. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/spaces/{space_uid}/iterations/{iteration_id}/cards` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UUID. |
| `iteration_id` | `string` | yes | — | — | Iteration UUID. |
| `status` | `string` | no | `active`, `removed` | — | Relation status filter. |
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- List active iteration cards.: `kaiten --json iteration-cards list --space-uid <space_uuid> --iteration-id <iteration_uuid> --status active --fields card_uid,status`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Iterations are beta and require a Kaiten tariff with the Iterations feature enabled.

### `iteration-cards.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten iteration-cards remove` |
| MCP alias | `kaiten_remove_iteration_card` |
| Description | Remove a card from a non-closed iteration. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_uid}/iterations/{iteration_id}/cards/{card_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UUID. |
| `iteration_id` | `string` | yes | — | — | Iteration UUID. |
| `card_uid` | `string` | yes | — | — | Card UUID. |

**Examples**

- Remove a card from an open iteration.: `kaiten --json iteration-cards remove --space-uid <space_uuid> --iteration-id <iteration_uuid> --card-uid <card_uuid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Iterations are beta and require a Kaiten tariff with the Iterations feature enabled.
- Cards cannot be removed from a closed iteration.

### `iterations.create`

| Field | Value |
|---|---|
| CLI command | `kaiten iterations create` |
| MCP alias | `kaiten_create_iteration` |
| Description | Create a planned iteration in a space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_uid}/iterations` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UUID. |
| `title` | `string` | yes | — | — | Iteration title. |
| `goal` | `string` | no | — | — | Iteration goal. |
| `start_date` | `string` | no | — | — | ISO 8601 start date. |
| `finish_date` | `string` | no | — | — | ISO 8601 finish date. |

**Examples**

- Create a dated planned iteration.: `kaiten --json iterations create --space-uid <space_uuid> --title "Iteration 12" --start-date 2026-08-03 --finish-date 2026-08-17`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Iterations are beta and require a Kaiten tariff with the Iterations feature enabled.

### `iterations.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten iterations delete` |
| MCP alias | `kaiten_delete_iteration` |
| Description | Delete an iteration and optionally move its cards to another iteration. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_uid}/iterations/{iteration_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UUID. |
| `iteration_id` | `string` | yes | — | — | Iteration UUID. |
| `new_iteration_id` | `string` | no | — | — | Target planned/active iteration for cards before deletion. |

**Examples**

- Delete and move cards to a valid target iteration.: `kaiten --json iterations delete --space-uid <space_uuid> --iteration-id <iteration_uuid> --new-iteration-id <target_uuid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Iterations are beta and require a Kaiten tariff with the Iterations feature enabled.
- The transfer target must belong to the same space and be planned or active.

### `iterations.get`

| Field | Value |
|---|---|
| CLI command | `kaiten iterations get` |
| MCP alias | `kaiten_get_iteration` |
| Description | Get an iteration by UUID within a space. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/spaces/{space_uid}/iterations/{iteration_id}` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UUID. |
| `iteration_id` | `string` | yes | — | — | Iteration UUID. |
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Read one iteration.: `kaiten --json iterations get --space-uid <space_uuid> --iteration-id <iteration_uuid>`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Iterations are beta and require a Kaiten tariff with the Iterations feature enabled.

### `iterations.list`

| Field | Value |
|---|---|
| CLI command | `kaiten iterations list` |
| MCP alias | `kaiten_list_iterations` |
| Description | List iterations in a space with bounded pagination and optional cards data. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/spaces/{space_uid}/iterations` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UUID. |
| `status` | `string` | no | — | — | Comma-separated statuses: planned, active, closed. |
| `with_data` | `string` | no | `cards` | — | Include related cards. |
| `limit` | `integer` | no | — | — | Maximum iterations to return (server cap 100). |
| `offset` | `integer` | no | — | — | Pagination offset. |
| `order` | `string` | no | `asc`, `desc` | — | Result order. |
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- List current iterations and their cards.: `kaiten --json iterations list --space-uid <space_uuid> --status planned,active --with-data cards --fields id,title,status,start_date,finish_date`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Iterations are beta and require a Kaiten tariff with the Iterations feature enabled.

### `iterations.update`

| Field | Value |
|---|---|
| CLI command | `kaiten iterations update` |
| MCP alias | `kaiten_update_iteration` |
| Description | Update iteration metadata, dates, status, or card transfer target. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_uid}/iterations/{iteration_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_uid` | `string` | yes | — | — | Space UUID. |
| `iteration_id` | `string` | yes | — | — | Iteration UUID. |
| `title` | `string` | no | — | — | New title. |
| `goal` | `string` | no | — | — | New goal. |
| `status` | `string` | no | `planned`, `active`, `closed` | — | Next iteration status. |
| `start_date` | `string` | no | — | — | ISO 8601 start date. |
| `finish_date` | `string` | no | — | — | ISO 8601 finish date. |
| `actual_finish_date` | `string` | no | — | — | ISO 8601 actual finish date when closing. |
| `new_iteration_id` | `string` | no | — | — | Target planned/active iteration for remaining cards. |

**Examples**

- Activate a dated planned iteration.: `kaiten --json iterations update --space-uid <space_uuid> --iteration-id <iteration_uuid> --status active`
- Close an iteration and transfer remaining cards.: `kaiten --json iterations update --space-uid <space_uuid> --iteration-id <iteration_uuid> --status closed --new-iteration-id <target_uuid>`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Iterations are beta and require a Kaiten tariff with the Iterations feature enabled.
- Statuses move forward only: planned -> active -> closed; activation requires start/finish dates and invalid transitions are rejected by Kaiten.

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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/webhooks` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `board_id` | `integer` | yes | — | — | Board ID |
| `column_id` | `integer` | yes | — | — | Column ID |
| `lane_id` | `integer` | yes | — | — | Lane ID |
| `owner_id` | `integer` | yes | — | — | Owner user ID |
| `type_id` | `integer` | no | — | — | Card type ID |
| `position` | `integer` | no | — | — | Position in the column |
| `format` | `integer` | no | `1`, `2`, `3`, `4`, `5`, `6`, `7` | — | Payload format |

**Examples**

- Create an incoming webhook.: `kaiten --json incoming-webhooks create --space-id 1 --board-id 2 --column-id 3 --lane-id 4 --owner-id 5`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `incoming-webhooks.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten incoming-webhooks delete` |
| MCP alias | `kaiten_delete_incoming_webhook` |
| Description | Delete an incoming card-creation webhook from a Kaiten space. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/webhooks/{webhook_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `webhook_id` | `string` | yes | — | — | Webhook ID (hash string) |

**Examples**

- Delete an incoming webhook.: `kaiten --json incoming-webhooks delete --space-id 1 --webhook-id hook-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `incoming-webhooks.list`

| Field | Value |
|---|---|
| CLI command | `kaiten incoming-webhooks list` |
| MCP alias | `kaiten_list_incoming_webhooks` |
| Description | List incoming card-creation webhooks for a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/spaces/{space_id}/webhooks` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |

**Examples**

- List incoming webhooks.: `kaiten --json incoming-webhooks list --space-id 1`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `incoming-webhooks.update`

| Field | Value |
|---|---|
| CLI command | `kaiten incoming-webhooks update` |
| MCP alias | `kaiten_update_incoming_webhook` |
| Description | Update an incoming card-creation webhook in a Kaiten space. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/webhooks/{webhook_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `webhook_id` | `string` | yes | — | — | Webhook ID (hash string) |
| `board_id` | `integer` | no | — | — | Board ID |
| `column_id` | `integer` | no | — | — | Column ID |
| `lane_id` | `integer` | no | — | — | Lane ID |
| `owner_id` | `integer` | no | — | — | Owner user ID |
| `type_id` | `integer` | no | — | — | Card type ID |
| `position` | `integer` | no | — | — | Position in the column |
| `format` | `integer` | no | `1`, `2`, `3`, `4`, `5`, `6`, `7` | — | Payload format |

**Examples**

- Update an incoming webhook.: `kaiten --json incoming-webhooks update --space-id 1 --webhook-id hook-1 --position 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `webhooks.create`

| Field | Value |
|---|---|
| CLI command | `kaiten webhooks create` |
| MCP alias | `kaiten_create_webhook` |
| Description | Create an external webhook for a Kaiten space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/external-webhooks` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `url` | `string` | yes | — | — | Webhook URL |

**Examples**

- Create an external webhook.: `kaiten --json webhooks create --space-id 1 --url "https://example.test"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `webhooks.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten webhooks delete` |
| MCP alias | `kaiten_delete_webhook` |
| Description | Delete an external webhook from a Kaiten space. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/external-webhooks/{webhook_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `webhook_id` | `integer` | yes | — | — | Webhook ID |

**Examples**

- Delete an external webhook.: `kaiten --json webhooks delete --space-id 1 --webhook-id 2`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/spaces/{space_id}/external-webhooks/{webhook_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `webhook_id` | `integer` | yes | — | — | Webhook ID |

**Examples**

- Get an external webhook.: `kaiten --json webhooks get --space-id 1 --webhook-id 2`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/spaces/{space_id}/external-webhooks` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |

**Examples**

- List external webhooks.: `kaiten --json webhooks list --space-id 1`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `webhooks.update`

| Field | Value |
|---|---|
| CLI command | `kaiten webhooks update` |
| MCP alias | `kaiten_update_webhook` |
| Description | Update an external webhook for a Kaiten space. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/external-webhooks/{webhook_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `webhook_id` | `integer` | yes | — | — | Webhook ID |
| `url` | `string` | no | — | — | Webhook URL |
| `enabled` | `boolean` | no | — | — | Whether the webhook is enabled |

**Examples**

- Update an external webhook.: `kaiten --json webhooks update --space-id 1 --webhook-id 2 --enabled`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/automations/{automation_id}/copy` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Source space ID |
| `automation_id` | `string` | yes | — | — | Automation ID (UUID) |
| `target_space_id` | `integer` | yes | — | — | Target space ID |

**Examples**

- Copy an automation.: `kaiten --json automations copy --space-id 1 --automation-id auto-1 --target-space-id 2`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/automations` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `name` | `string` | yes | — | — | Automation name |
| `trigger` | `object` | yes | — | — | Trigger configuration |
| `actions` | `array` | yes | — | — | Action configurations |
| `conditions` | `object` | no | — | — | Conditions configuration |
| `type` | `string` | no | `on_action`, `on_date`, `on_demand`, `on_workflow` | — | Automation type |
| `sort_order` | `number` | no | — | — | Sort position |
| `source_automation_id` | `string` | no | — | — | Automation ID to clone from |

**Examples**

- Create an automation using the known live-valid add_assignee payload shape.: `kaiten --json automations create --space-id 1 --name Auto --type on_action --trigger '{"type":"card_created"}' --actions '[{"type":"add_assignee","created":"2026-01-01T00:00:00+00:00","data":{"variant":"specific","userId":42}}]'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/automations/{automation_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `automation_id` | `string` | yes | — | — | Automation ID (UUID) |

**Examples**

- Delete an automation.: `kaiten --json automations delete --space-id 1 --automation-id auto-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/spaces/{space_id}/automations/{automation_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `automation_id` | `string` | yes | — | — | Automation ID (UUID) |

**Examples**

- Get an automation.: `kaiten --json automations get --space-id 1 --automation-id auto-1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Live contract: `live_passed_as_expected_error`; expected statuses: `405`
- Live note: Automation GET-single may return 405 even after successful creation; the live suite validates that contract explicitly.

### `automations.list`

| Field | Value |
|---|---|
| CLI command | `kaiten automations list` |
| MCP alias | `kaiten_list_automations` |
| Description | List one page of automations for a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/spaces/{space_id}/automations` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default 50, max 100) |
| `offset` | `integer` | no | — | >= 0 | Pagination offset |

**Examples**

- List space automations.: `kaiten --json automations list --space-id 1`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This direct command returns one page; increase offset to read subsequent pages.

### `automations.update`

| Field | Value |
|---|---|
| CLI command | `kaiten automations update` |
| MCP alias | `kaiten_update_automation` |
| Description | Update an automation in a Kaiten space. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/automations/{automation_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `automation_id` | `string` | yes | — | — | Automation ID (UUID) |
| `name` | `string` | no | — | — | New automation name |
| `trigger` | `object` | no | — | — | New trigger configuration |
| `actions` | `array` | no | — | — | New action configurations |
| `conditions` | `object` | no | — | — | New conditions configuration |
| `status` | `string` | no | `active`, `disabled` | — | Automation status |
| `sort_order` | `number` | no | — | — | Sort position |

**Examples**

- Disable an automation.: `kaiten --json automations update --space-id 1 --automation-id auto-1 --status disabled`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/workflows` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Workflow name |
| `stages` | `array` | yes | — | — | Workflow stages |
| `transitions` | `array` | yes | — | — | Workflow transitions |

**Examples**

- Create a workflow.: `kaiten --json workflows create --name Flow --stages '[{"id":"1","name":"Todo","type":"queue"}]' --transitions '[{"id":"t1"}]'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/workflows/{workflow_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `workflow_id` | `string` | yes | — | — | Workflow ID (UUID) |

**Examples**

- Delete a workflow.: `kaiten --json workflows delete --workflow-id wf-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/company/workflows/{workflow_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `workflow_id` | `string` | yes | — | — | Workflow ID (UUID) |

**Examples**

- Get a workflow.: `kaiten --json workflows get --workflow-id wf-1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/workflows` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `limit` | `integer` | no | — | — | Maximum number of results |
| `offset` | `integer` | no | — | — | Offset for pagination |

**Examples**

- List workflows.: `kaiten --json workflows list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `workflows.update`

| Field | Value |
|---|---|
| CLI command | `kaiten workflows update` |
| MCP alias | `kaiten_update_workflow` |
| Description | Update a company workflow. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/workflows/{workflow_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `workflow_id` | `string` | yes | — | — | Workflow ID (UUID) |
| `name` | `string` | no | — | — | New workflow name |
| `stages` | `array` | no | — | — | Updated stages |
| `transitions` | `array` | no | — | — | Updated transitions |

**Examples**

- Update a workflow.: `kaiten --json workflows update --workflow-id wf-1 --name Flow2`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`
- Live note: When workflow creation is unavailable, the live suite validates the documented 403/404/405 error contract on a sentinel workflow id.

<a id="module-addons"></a>
## Аддоны (`addons`) — 10 commands

Addon catalog, space installation and per-card / per-user addon data.

**Namespace tree**

```text
addons
  list
  uid
card-addon-data
  get
  set
company-addons
  list
space-addons
  install
  list
  uninstall
user-addon-data
  get
  set
```

### `addons.list`

| Field | Value |
|---|---|
| CLI command | `kaiten addons list` |
| MCP alias | `kaiten_list_addons` |
| Description | List the published Kaiten addon catalog. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/addons` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Find the UUID of a published addon by its name.: `kaiten --json addons list --fields id,name`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The endpoint returns every non-archived addon with status published, without a company filter; an addon a company registered privately is not in this list.
- addon_uid is the addon's UUID, not its name. Take it from space-addons.list for the space you are working in, or from company-addons.list; addons.list only shows the published catalog and omits an addon registered privately by a company.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: Addon commands were added after the last live campaign; the live suite exercises them on read and documented-error paths, but no full live run has confirmed them yet.

### `addons.uid`

| Field | Value |
|---|---|
| CLI command | `kaiten addons uid` |
| MCP alias | `kaiten_derive_addon_uid` |
| Description | Derive an addon UUID locally from its mount path, without calling Kaiten. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/local/addons/uid` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `url_path` | `string` | yes | — | — | Addon mount path, for example /github. |

**Examples**

- Derive the GitHub addon UUID used by the addons-data endpoints.: `kaiten --json addons uid --url-path /github`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Local computation only: UUID v5 of the normalized path under the fixed Kaiten addons namespace, the same derivation the platform uses.
- Deriving the UUID from a mount path is a guess: Kaiten stamps a derived UUID only on on-premises installations whose addon iframe path is non-empty, and stores a random UUID otherwise. Verify it against space-addons.list before relying on it.
- The platform derives from the path of the addon's iframe_initial_url, so pass that path: an addon served from https://host/github/index.html derives from /github/index.html, not /github.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: Addon commands were added after the last live campaign; the live suite exercises them on read and documented-error paths, but no full live run has confirmed them yet.

### `card-addon-data.get`

| Field | Value |
|---|---|
| CLI command | `kaiten card-addon-data get` |
| MCP alias | `kaiten_get_card_addon_data` |
| Description | Read the addon data rows stored on a card for one addon. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/addons-data/{addon_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | yes | — | — | Addon UUID |

**Examples**

- Read the GitHub addon state stored on a card.: `kaiten --json card-addon-data get --card-id 10 --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- addon_uid is the addon's UUID, not its name. Take it from space-addons.list for the space you are working in, or from company-addons.list; addons.list only shows the published catalog and omits an addon registered privately by a company.
- Returns every row the current user may see: the shared row (user_uid is null) plus their own private row, if either exists.
- Shared data is one row per card visible to everyone (writing it needs card.update); private data is a per-user row that only its owner reads and writes (card.read is enough).
- Live contract: `live_not_validated`; expected statuses: —
- Live note: Addon commands were added after the last live campaign; the live suite exercises them on read and documented-error paths, but no full live run has confirmed them yet.

### `card-addon-data.set`

| Field | Value |
|---|---|
| CLI command | `kaiten card-addon-data set` |
| MCP alias | `kaiten_set_card_addon_data` |
| Description | Write addon data on a card in the shared or private scope. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/addons-data/{addon_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | yes | — | — | Addon UUID |
| `type` | `string` | yes | `shared`, `private` | — | Data scope: shared for the whole card, private for the current user. |
| `data` | `object` | yes | — | — | Addon data object merged over the stored row by top-level key. |

**Examples**

- Replace one addon key on a card.: `kaiten --json card-addon-data set --card-id 10 --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990 --type shared --data '{"attachedPulls": []}'`
- Write an addon data object from a file.: `kaiten --json card-addon-data set --card-id 10 --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990 --type shared --data @payload.json`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- addon_uid is the addon's UUID, not its name. Take it from space-addons.list for the space you are working in, or from company-addons.list; addons.list only shows the published catalog and omits an addon registered privately by a company.
- The server shallow-merges data over the stored row by top-level key, so send the full replacement value for every key you set and omit keys you want to keep untouched.
- Shared data is one row per card visible to everyone (writing it needs card.update); private data is a per-user row that only its owner reads and writes (card.read is enough).
- The addon must be installed in the card's space before its per-card data can be written; otherwise the shared write is rejected with a permission error.
- The shared row has no version or ETag, so a read-modify-write races with the addon UI and with another CLI run; keep the read and the write close together and re-read before retrying.
- For the GitHub addon prefer the github-addon commands: they keep the exact widget payload shape and dedup attachments instead of overwriting the whole key.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: Addon commands were added after the last live campaign; the live suite exercises them on read and documented-error paths, but no full live run has confirmed them yet.

### `company-addons.list`

| Field | Value |
|---|---|
| CLI command | `kaiten company-addons list` |
| MCP alias | `kaiten_list_company_addons` |
| Description | List the addons registered by the current company, published or not. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/addons` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Find the UUID of an addon the company registered itself.: `kaiten --json company-addons list --fields id,name,status,iframe_initial_url`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This is where a privately registered addon lives; addons.list only covers the published catalog.
- addon_uid is the addon's UUID, not its name. Take it from space-addons.list for the space you are working in, or from company-addons.list; addons.list only shows the published catalog and omits an addon registered privately by a company.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: Addon commands were added after the last live campaign; the live suite exercises them on read and documented-error paths, but no full live run has confirmed them yet.

### `space-addons.install`

| Field | Value |
|---|---|
| CLI command | `kaiten space-addons install` |
| MCP alias | `kaiten_install_space_addon` |
| Description | Install an addon into a Kaiten space or update its space settings. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/addons/{addon_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `addon_uid` | `string` | yes | — | — | Addon UUID |
| `settings` | `object` | no | — | — | Space-level addon settings object; omit to only install. |

**Examples**

- Install the GitHub addon into a space.: `kaiten --json space-addons install --space-id 1 --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- addon_uid is the addon's UUID, not its name. Take it from space-addons.list for the space you are working in, or from company-addons.list; addons.list only shows the published catalog and omits an addon registered privately by a company.
- Installing an already installed addon without settings is rejected as a no-op; pass settings when you only need to update configuration.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: Addon commands were added after the last live campaign; the live suite exercises them on read and documented-error paths, but no full live run has confirmed them yet.

### `space-addons.list`

| Field | Value |
|---|---|
| CLI command | `kaiten space-addons list` |
| MCP alias | `kaiten_list_space_addons` |
| Description | List addons installed in a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/spaces/{space_id}/addons` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `compact` | `boolean` | no | — | — | Return compact output without heavy nested fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Check which addons a space has installed.: `kaiten --json space-addons list --space-id 1 --fields id,name`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- addon_uid is the addon's UUID, not its name. Take it from space-addons.list for the space you are working in, or from company-addons.list; addons.list only shows the published catalog and omits an addon registered privately by a company.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: Addon commands were added after the last live campaign; the live suite exercises them on read and documented-error paths, but no full live run has confirmed them yet.

### `space-addons.uninstall`

| Field | Value |
|---|---|
| CLI command | `kaiten space-addons uninstall` |
| MCP alias | `kaiten_uninstall_space_addon` |
| Description | Remove an addon from a Kaiten space. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/addons/{addon_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `addon_uid` | `string` | yes | — | — | Addon UUID |

**Examples**

- Detach an addon from a space.: `kaiten --json space-addons uninstall --space-id 1 --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Uninstalling hides the addon in that space; per-card data rows written earlier are not deleted by this call.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: Addon commands were added after the last live campaign; the live suite exercises them on read and documented-error paths, but no full live run has confirmed them yet.

### `user-addon-data.get`

| Field | Value |
|---|---|
| CLI command | `kaiten user-addon-data get` |
| MCP alias | `kaiten_get_user_addon_data` |
| Description | Read the current user's company-level addon data for one addon. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/users/current/addons-data/{addon_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `addon_uid` | `string` | yes | — | — | Addon UUID |

**Examples**

- Read the current user's addon-level settings.: `kaiten --json user-addon-data get --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- addon_uid is the addon's UUID, not its name. Take it from space-addons.list for the space you are working in, or from company-addons.list; addons.list only shows the published catalog and omits an addon registered privately by a company.
- This store is per user and per company; it holds addon-level user state, not per-card state.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: Addon commands were added after the last live campaign; the live suite exercises them on read and documented-error paths, but no full live run has confirmed them yet.

### `user-addon-data.set`

| Field | Value |
|---|---|
| CLI command | `kaiten user-addon-data set` |
| MCP alias | `kaiten_set_user_addon_data` |
| Description | Write the current user's company-level addon data for one addon. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/users/current/addons-data/{addon_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `addon_uid` | `string` | yes | — | — | Addon UUID |
| `data` | `object` | yes | — | — | Addon data object merged over the stored row by top-level key. |

**Examples**

- Reset one key of the current user's addon state.: `kaiten --json user-addon-data set --addon-uid 0ce23a01-560f-51e0-9982-1e3445dc5990 --data '{"selectedRepo": null}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- addon_uid is the addon's UUID, not its name. Take it from space-addons.list for the space you are working in, or from company-addons.list; addons.list only shows the published catalog and omits an addon registered privately by a company.
- The server shallow-merges data over the stored row by top-level key, so send the full replacement value for every key you set and omit keys you want to keep untouched.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: Addon commands were added after the last live campaign; the live suite exercises them on read and documented-error paths, but no full live run has confirmed them yet.

<a id="module-github-addon"></a>
## GitHub-аддон (`github_addon`) — 12 commands

Pull requests, branches, commits and issues attached to cards by the GitHub addon.

**Namespace tree**

```text
github-addon.branches
  attach
  detach
  list
github-addon.commits
  attach
  detach
  list
github-addon.issues
  attach
  detach
  list
github-addon.pulls
  attach
  detach
  list
```

### `github-addon.branches.attach`

| Field | Value |
|---|---|
| CLI command | `kaiten github-addon branches attach` |
| MCP alias | `kaiten_attach_github_branch` |
| Description | Attach a branch to a card through the GitHub addon. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/addons-data` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | no | — | — | GitHub addon UUID; derived from the mount path when omitted. |
| `addon_url_path` | `string` | no | — | — | GitHub addon mount path used to derive the UUID (default /github). |
| `branch_json` | `object` | yes | — | — | Raw GitHub REST branch object. |
| `owner` | `string` | yes | — | — | GitHub repository owner login. |
| `repo` | `string` | yes | — | — | GitHub repository name. |
| `dry_run` | `boolean` | no | — | — | Report the resulting change without writing it. |

**Examples**

- Attach a branch fetched with gh api repos/OWNER/REPO/branches/NAME.: `kaiten --json github-addon branches attach --card-id 10 --owner acme --repo web --branch-json @branch.json`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The addon UUID is appended to the path at runtime, so the path template above stops at addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path (default /github).
- Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten stores a random one. When a derived UUID finds no data row the command asks the card's space which addons it has and retries with the registered UUID, so an empty answer is not silently an answer about the wrong addon.
- That fallback costs two extra reads (the card and its space addons) for every card that has no data row, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid explicitly.
- Pass the raw GitHub REST object from gh api repos/OWNER/REPO/..., not gh pr view --json: the latter returns GraphQL fields (a string node id, camelCase names) that this mapping rejects. The CLI never calls GitHub itself, so the payload is the only source of the title, state and author the widget shows when it cannot reach GitHub.
- A REST branch object carries no repository, so --owner and --repo are required and form the stored branch identity.
- The card widget re-reads every attachment from GitHub by owner, repository and number/name/sha, so the repository is part of the stored identity: a wrong or missing value leaves an entry that can never resolve again.
- Already attached entries are detected by owner/repo/branch, matching the addon UI.
- The write needs card.update in the card's space and the GitHub addon installed there; otherwise Kaiten rejects the shared row update.
- The shared row has no version or ETag: a simultaneous change from the addon UI or another CLI run can be lost. Re-read before retrying.
- --dry-run reads the current attachments and reports the outcome without writing; it is still classified as a mutation, so it is blocked by --read-only.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: GitHub addon commands were added after the last live campaign. The live suite covers reads and dry runs; a real attach/detach needs a tenant with the addon installed and has not been live-validated yet.

### `github-addon.branches.detach`

| Field | Value |
|---|---|
| CLI command | `kaiten github-addon branches detach` |
| MCP alias | `kaiten_detach_github_branch` |
| Description | Detach a branch from a card in the GitHub addon. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/addons-data` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | no | — | — | GitHub addon UUID; derived from the mount path when omitted. |
| `addon_url_path` | `string` | no | — | — | GitHub addon mount path used to derive the UUID (default /github). |
| `branch_name` | `string` | no | — | — | Branch name. |
| `pseudo_id` | `string` | no | — | — | Stored branch identity in owner/repo/branch form. |
| `owner` | `string` | no | — | — | GitHub repository owner login. Optional filter. |
| `repo` | `string` | no | — | — | GitHub repository name. Optional filter. |
| `all` | `boolean` | no | — | — | Allow removing every attachment the selectors match, not just one. |
| `dry_run` | `boolean` | no | — | — | Report the resulting change without writing it. |

**Examples**

- Detach one branch from a card.: `kaiten --json github-addon branches detach --card-id 10 --branch-name feature/login --owner acme --repo web`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The addon UUID is appended to the path at runtime, so the path template above stops at addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path (default /github).
- Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten stores a random one. When a derived UUID finds no data row the command asks the card's space which addons it has and retries with the registered UUID, so an empty answer is not silently an answer about the wrong addon.
- That fallback costs two extra reads (the card and its space addons) for every card that has no data row, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid explicitly.
- Provide --pseudo-id or --branch-name; --owner and --repo narrow the match when the same branch name exists in several repositories.
- A selector that matches several attachments is rejected as ambiguous; narrow it with --owner and --repo, or pass --all when removing every match is what you want.
- Detaching the last entry stores null for the key rather than an empty array, which is what the addon UI writes and what hides the widget section on the card.
- The shared row has no version or ETag: a simultaneous change from the addon UI or another CLI run can be lost. Re-read before retrying.
- --dry-run reads the current attachments and reports the outcome without writing; it is still classified as a mutation, so it is blocked by --read-only.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: GitHub addon commands were added after the last live campaign. The live suite covers reads and dry runs; a real attach/detach needs a tenant with the addon installed and has not been live-validated yet.

### `github-addon.branches.list`

| Field | Value |
|---|---|
| CLI command | `kaiten github-addon branches list` |
| MCP alias | `kaiten_list_card_github_branches` |
| Description | List branches attached to a card through the GitHub addon. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/addons-data` |
| Compact | `no` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | no | — | — | GitHub addon UUID; derived from the mount path when omitted. |
| `addon_url_path` | `string` | no | — | — | GitHub addon mount path used to derive the UUID (default /github). |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Read the branches attached to a card.: `kaiten --json github-addon branches list --card-id 10 --fields branchName,htmlUrl`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The addon UUID is appended to the path at runtime, so the path template above stops at addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path (default /github).
- Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten stores a random one. When a derived UUID finds no data row the command asks the card's space which addons it has and retries with the registered UUID, so an empty answer is not silently an answer about the wrong addon.
- That fallback costs two extra reads (the card and its space addons) for every card that has no data row, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid explicitly.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: GitHub addon commands were added after the last live campaign. The live suite covers reads and dry runs; a real attach/detach needs a tenant with the addon installed and has not been live-validated yet.

### `github-addon.commits.attach`

| Field | Value |
|---|---|
| CLI command | `kaiten github-addon commits attach` |
| MCP alias | `kaiten_attach_github_commit` |
| Description | Attach a commit to a card through the GitHub addon. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/addons-data` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | no | — | — | GitHub addon UUID; derived from the mount path when omitted. |
| `addon_url_path` | `string` | no | — | — | GitHub addon mount path used to derive the UUID (default /github). |
| `commit_json` | `object` | yes | — | — | Raw GitHub REST commit object. |
| `owner` | `string` | yes | — | — | GitHub repository owner login. |
| `repo` | `string` | yes | — | — | GitHub repository name. |
| `dry_run` | `boolean` | no | — | — | Report the resulting change without writing it. |

**Examples**

- Attach a commit fetched with gh api repos/OWNER/REPO/commits/SHA.: `kaiten --json github-addon commits attach --card-id 10 --owner acme --repo web --commit-json @commit.json`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The addon UUID is appended to the path at runtime, so the path template above stops at addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path (default /github).
- Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten stores a random one. When a derived UUID finds no data row the command asks the card's space which addons it has and retries with the registered UUID, so an empty answer is not silently an answer about the wrong addon.
- That fallback costs two extra reads (the card and its space addons) for every card that has no data row, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid explicitly.
- Pass the raw GitHub REST object from gh api repos/OWNER/REPO/..., not gh pr view --json: the latter returns GraphQL fields (a string node id, camelCase names) that this mapping rejects. The CLI never calls GitHub itself, so the payload is the only source of the title, state and author the widget shows when it cannot reach GitHub.
- The stored author prefers the linked GitHub account and falls back to the git author name, exactly as the addon does.
- Already attached entries are detected by commit sha.
- The write needs card.update in the card's space and the GitHub addon installed there; otherwise Kaiten rejects the shared row update.
- The shared row has no version or ETag: a simultaneous change from the addon UI or another CLI run can be lost. Re-read before retrying.
- --dry-run reads the current attachments and reports the outcome without writing; it is still classified as a mutation, so it is blocked by --read-only.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: GitHub addon commands were added after the last live campaign. The live suite covers reads and dry runs; a real attach/detach needs a tenant with the addon installed and has not been live-validated yet.

### `github-addon.commits.detach`

| Field | Value |
|---|---|
| CLI command | `kaiten github-addon commits detach` |
| MCP alias | `kaiten_detach_github_commit` |
| Description | Detach a commit from a card in the GitHub addon. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/addons-data` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | no | — | — | GitHub addon UUID; derived from the mount path when omitted. |
| `addon_url_path` | `string` | no | — | — | GitHub addon mount path used to derive the UUID (default /github). |
| `sha` | `string` | no | — | — | Full commit sha as stored. |
| `owner` | `string` | no | — | — | GitHub repository owner login. Optional filter. |
| `repo` | `string` | no | — | — | GitHub repository name. Optional filter. |
| `all` | `boolean` | no | — | — | Allow removing every attachment the selectors match, not just one. |
| `dry_run` | `boolean` | no | — | — | Report the resulting change without writing it. |

**Examples**

- Detach one commit from a card.: `kaiten --json github-addon commits detach --card-id 10 --sha 3f1a2bc4d5e6f708192a3b4c5d6e7f8091a2b3c4`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The addon UUID is appended to the path at runtime, so the path template above stops at addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path (default /github).
- Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten stores a random one. When a derived UUID finds no data row the command asks the card's space which addons it has and retries with the registered UUID, so an empty answer is not silently an answer about the wrong addon.
- That fallback costs two extra reads (the card and its space addons) for every card that has no data row, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid explicitly.
- --sha is required and matched in full; short shas do not match stored entries.
- A selector that matches several attachments is rejected as ambiguous; narrow it with --owner and --repo, or pass --all when removing every match is what you want.
- Detaching the last entry stores null for the key rather than an empty array, which is what the addon UI writes and what hides the widget section on the card.
- The shared row has no version or ETag: a simultaneous change from the addon UI or another CLI run can be lost. Re-read before retrying.
- --dry-run reads the current attachments and reports the outcome without writing; it is still classified as a mutation, so it is blocked by --read-only.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: GitHub addon commands were added after the last live campaign. The live suite covers reads and dry runs; a real attach/detach needs a tenant with the addon installed and has not been live-validated yet.

### `github-addon.commits.list`

| Field | Value |
|---|---|
| CLI command | `kaiten github-addon commits list` |
| MCP alias | `kaiten_list_card_github_commits` |
| Description | List commits attached to a card through the GitHub addon. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/addons-data` |
| Compact | `no` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | no | — | — | GitHub addon UUID; derived from the mount path when omitted. |
| `addon_url_path` | `string` | no | — | — | GitHub addon mount path used to derive the UUID (default /github). |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Read the commits attached to a card.: `kaiten --json github-addon commits list --card-id 10 --fields sha,htmlUrl,message`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The addon UUID is appended to the path at runtime, so the path template above stops at addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path (default /github).
- Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten stores a random one. When a derived UUID finds no data row the command asks the card's space which addons it has and retries with the registered UUID, so an empty answer is not silently an answer about the wrong addon.
- That fallback costs two extra reads (the card and its space addons) for every card that has no data row, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid explicitly.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: GitHub addon commands were added after the last live campaign. The live suite covers reads and dry runs; a real attach/detach needs a tenant with the addon installed and has not been live-validated yet.

### `github-addon.issues.attach`

| Field | Value |
|---|---|
| CLI command | `kaiten github-addon issues attach` |
| MCP alias | `kaiten_attach_github_issue` |
| Description | Attach an issue to a card through the GitHub addon. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/addons-data` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | no | — | — | GitHub addon UUID; derived from the mount path when omitted. |
| `addon_url_path` | `string` | no | — | — | GitHub addon mount path used to derive the UUID (default /github). |
| `issue_json` | `object` | yes | — | — | Raw GitHub REST issue object. |
| `owner` | `string` | yes | — | — | GitHub repository owner login. |
| `repo` | `string` | yes | — | — | GitHub repository name. |
| `dry_run` | `boolean` | no | — | — | Report the resulting change without writing it. |

**Examples**

- Attach an issue fetched with gh api repos/OWNER/REPO/issues/NUMBER.: `kaiten --json github-addon issues attach --card-id 10 --owner acme --repo web --issue-json @issue.json`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The addon UUID is appended to the path at runtime, so the path template above stops at addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path (default /github).
- Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten stores a random one. When a derived UUID finds no data row the command asks the card's space which addons it has and retries with the registered UUID, so an empty answer is not silently an answer about the wrong addon.
- That fallback costs two extra reads (the card and its space addons) for every card that has no data row, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid explicitly.
- Pass the raw GitHub REST object from gh api repos/OWNER/REPO/..., not gh pr view --json: the latter returns GraphQL fields (a string node id, camelCase names) that this mapping rejects. The CLI never calls GitHub itself, so the payload is the only source of the title, state and author the widget shows when it cannot reach GitHub.
- GitHub returns pull requests from the issues endpoint too; a payload with a pull_request field is rejected, attach it as a pull request instead.
- Already attached entries are detected by GitHub numeric id and left untouched.
- The write needs card.update in the card's space and the GitHub addon installed there; otherwise Kaiten rejects the shared row update.
- The shared row has no version or ETag: a simultaneous change from the addon UI or another CLI run can be lost. Re-read before retrying.
- --dry-run reads the current attachments and reports the outcome without writing; it is still classified as a mutation, so it is blocked by --read-only.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: GitHub addon commands were added after the last live campaign. The live suite covers reads and dry runs; a real attach/detach needs a tenant with the addon installed and has not been live-validated yet.

### `github-addon.issues.detach`

| Field | Value |
|---|---|
| CLI command | `kaiten github-addon issues detach` |
| MCP alias | `kaiten_detach_github_issue` |
| Description | Detach an issue from a card in the GitHub addon. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/addons-data` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | no | — | — | GitHub addon UUID; derived from the mount path when omitted. |
| `addon_url_path` | `string` | no | — | — | GitHub addon mount path used to derive the UUID (default /github). |
| `issue_id` | `integer` | no | — | — | GitHub numeric issue id. |
| `number` | `integer` | no | — | — | Issue number. |
| `owner` | `string` | no | — | — | GitHub repository owner login. Optional filter. |
| `repo` | `string` | no | — | — | GitHub repository name. Optional filter. |
| `all` | `boolean` | no | — | — | Allow removing every attachment the selectors match, not just one. |
| `dry_run` | `boolean` | no | — | — | Report the resulting change without writing it. |

**Examples**

- Detach one issue from a card.: `kaiten --json github-addon issues detach --card-id 10 --number 7 --owner acme --repo web`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The addon UUID is appended to the path at runtime, so the path template above stops at addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path (default /github).
- Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten stores a random one. When a derived UUID finds no data row the command asks the card's space which addons it has and retries with the registered UUID, so an empty answer is not silently an answer about the wrong addon.
- That fallback costs two extra reads (the card and its space addons) for every card that has no data row, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid explicitly.
- Provide --issue-id or --number; --owner and --repo narrow the match when the same number exists in several repositories.
- A selector that matches several attachments is rejected as ambiguous; narrow it with --owner and --repo, or pass --all when removing every match is what you want.
- Detaching the last entry stores null for the key rather than an empty array, which is what the addon UI writes and what hides the widget section on the card.
- The shared row has no version or ETag: a simultaneous change from the addon UI or another CLI run can be lost. Re-read before retrying.
- --dry-run reads the current attachments and reports the outcome without writing; it is still classified as a mutation, so it is blocked by --read-only.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: GitHub addon commands were added after the last live campaign. The live suite covers reads and dry runs; a real attach/detach needs a tenant with the addon installed and has not been live-validated yet.

### `github-addon.issues.list`

| Field | Value |
|---|---|
| CLI command | `kaiten github-addon issues list` |
| MCP alias | `kaiten_list_card_github_issues` |
| Description | List issues attached to a card through the GitHub addon. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/addons-data` |
| Compact | `no` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | no | — | — | GitHub addon UUID; derived from the mount path when omitted. |
| `addon_url_path` | `string` | no | — | — | GitHub addon mount path used to derive the UUID (default /github). |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Read the issues attached to a card.: `kaiten --json github-addon issues list --card-id 10 --fields number,htmlUrl,state`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The addon UUID is appended to the path at runtime, so the path template above stops at addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path (default /github).
- Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten stores a random one. When a derived UUID finds no data row the command asks the card's space which addons it has and retries with the registered UUID, so an empty answer is not silently an answer about the wrong addon.
- That fallback costs two extra reads (the card and its space addons) for every card that has no data row, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid explicitly.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: GitHub addon commands were added after the last live campaign. The live suite covers reads and dry runs; a real attach/detach needs a tenant with the addon installed and has not been live-validated yet.

### `github-addon.pulls.attach`

| Field | Value |
|---|---|
| CLI command | `kaiten github-addon pulls attach` |
| MCP alias | `kaiten_attach_github_pull` |
| Description | Attach a pull request to a card through the GitHub addon. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/addons-data` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | no | — | — | GitHub addon UUID; derived from the mount path when omitted. |
| `addon_url_path` | `string` | no | — | — | GitHub addon mount path used to derive the UUID (default /github). |
| `pull_json` | `object` | yes | — | — | Raw GitHub REST pull request object. |
| `owner` | `string` | no | — | — | GitHub repository owner login. Required when the payload carries no repository. |
| `repo` | `string` | no | — | — | GitHub repository name. Required when the payload carries no repository. |
| `dry_run` | `boolean` | no | — | — | Report the resulting change without writing it. |

**Examples**

- Attach a PR fetched with gh api repos/OWNER/REPO/pulls/NUMBER.: `kaiten --json github-addon pulls attach --card-id 10 --pull-json @pull.json`
- Preview the attachment without writing it.: `kaiten --json github-addon pulls attach --card-id 10 --pull-json @pull.json --dry-run`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The addon UUID is appended to the path at runtime, so the path template above stops at addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path (default /github).
- Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten stores a random one. When a derived UUID finds no data row the command asks the card's space which addons it has and retries with the registered UUID, so an empty answer is not silently an answer about the wrong addon.
- That fallback costs two extra reads (the card and its space addons) for every card that has no data row, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid explicitly.
- Pass the raw GitHub REST object from gh api repos/OWNER/REPO/..., not gh pr view --json: the latter returns GraphQL fields (a string node id, camelCase names) that this mapping rejects. The CLI never calls GitHub itself, so the payload is the only source of the title, state and author the widget shows when it cannot reach GitHub.
- The card widget re-reads every attachment from GitHub by owner, repository and number/name/sha, so the repository is part of the stored identity: a wrong or missing value leaves an entry that can never resolve again.
- The repository is read from base.repo. A REST payload trimmed with --jq can lose it; then pass --owner and --repo. Output of gh pr view --json is a different schema entirely and is not accepted with or without them.
- Already attached entries are detected by GitHub numeric id and left untouched.
- The write needs card.update in the card's space and the GitHub addon installed there; otherwise Kaiten rejects the shared row update.
- The shared row has no version or ETag: a simultaneous change from the addon UI or another CLI run can be lost. Re-read before retrying.
- --dry-run reads the current attachments and reports the outcome without writing; it is still classified as a mutation, so it is blocked by --read-only.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: GitHub addon commands were added after the last live campaign. The live suite covers reads and dry runs; a real attach/detach needs a tenant with the addon installed and has not been live-validated yet.

### `github-addon.pulls.detach`

| Field | Value |
|---|---|
| CLI command | `kaiten github-addon pulls detach` |
| MCP alias | `kaiten_detach_github_pull` |
| Description | Detach a pull request from a card in the GitHub addon. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/addons-data` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | no | — | — | GitHub addon UUID; derived from the mount path when omitted. |
| `addon_url_path` | `string` | no | — | — | GitHub addon mount path used to derive the UUID (default /github). |
| `pull_id` | `integer` | no | — | — | GitHub numeric pull request id. |
| `number` | `integer` | no | — | — | Pull request number. |
| `owner` | `string` | no | — | — | GitHub repository owner login. Optional filter. |
| `repo` | `string` | no | — | — | GitHub repository name. Optional filter. |
| `all` | `boolean` | no | — | — | Allow removing every attachment the selectors match, not just one. |
| `dry_run` | `boolean` | no | — | — | Report the resulting change without writing it. |

**Examples**

- Detach one PR from a card.: `kaiten --json github-addon pulls detach --card-id 10 --number 42 --owner acme --repo web`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The addon UUID is appended to the path at runtime, so the path template above stops at addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path (default /github).
- Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten stores a random one. When a derived UUID finds no data row the command asks the card's space which addons it has and retries with the registered UUID, so an empty answer is not silently an answer about the wrong addon.
- That fallback costs two extra reads (the card and its space addons) for every card that has no data row, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid explicitly.
- Provide --pull-id or --number; --owner and --repo narrow the match when the same number exists in several repositories.
- A selector that matches several attachments is rejected as ambiguous; narrow it with --owner and --repo, or pass --all when removing every match is what you want.
- A selector that matches nothing leaves the stored data untouched.
- Detaching the last entry stores null for the key rather than an empty array, which is what the addon UI writes and what hides the widget section on the card.
- The shared row has no version or ETag: a simultaneous change from the addon UI or another CLI run can be lost. Re-read before retrying.
- --dry-run reads the current attachments and reports the outcome without writing; it is still classified as a mutation, so it is blocked by --read-only.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: GitHub addon commands were added after the last live campaign. The live suite covers reads and dry runs; a real attach/detach needs a tenant with the addon installed and has not been live-validated yet.

### `github-addon.pulls.list`

| Field | Value |
|---|---|
| CLI command | `kaiten github-addon pulls list` |
| MCP alias | `kaiten_list_card_github_pulls` |
| Description | List pull requests attached to a card through the GitHub addon. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/addons-data` |
| Compact | `no` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `addon_uid` | `string` | no | — | — | GitHub addon UUID; derived from the mount path when omitted. |
| `addon_url_path` | `string` | no | — | — | GitHub addon mount path used to derive the UUID (default /github). |
| `fields` | `string` | no | — | — | Comma-separated field names to return. |

**Examples**

- Read the PR links attached to a card.: `kaiten --json github-addon pulls list --card-id 10 --fields number,htmlUrl,state`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The addon UUID is appended to the path at runtime, so the path template above stops at addons-data. It is --addon-uid when given, otherwise derived from --addon-url-path (default /github).
- Derivation only reproduces the real UUID on an on-premises installation; elsewhere Kaiten stores a random one. When a derived UUID finds no data row the command asks the card's space which addons it has and retries with the registered UUID, so an empty answer is not silently an answer about the wrong addon.
- That fallback costs two extra reads (the card and its space addons) for every card that has no data row, so in a loop resolve the UUID once with space-addons.list and pass --addon-uid explicitly.
- When the UUID was derived, holds no data and the space cannot be asked, the command fails instead of returning an empty list that could mean either "nothing attached" or "wrong addon".
- Returns the stored attachedPulls entries; an uninstalled addon or a card without attachments both yield an empty list.
- Card PR references can also live in external links; check external-links.list too when you need every PR referenced by a card.
- Live contract: `live_not_validated`; expected statuses: —
- Live note: GitHub addon commands were added after the last live campaign. The live suite covers reads and dry runs; a real attach/detach needs a tenant with the addon installed and has not been live-validated yet.

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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/projects/{project_id}/cards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `project_id` | `string` | yes | — | — | Project ID (UUID) |
| `card_id` | `integer` | yes | — | — | Card ID to add |

**Examples**

- Add a card to a project.: `kaiten --json projects cards add --project-id p1 --card-id 10`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `projects.cards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten projects cards list` |
| MCP alias | `kaiten_list_project_cards` |
| Description | List cards in a Kaiten project. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `synthetic` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/projects/{project_id}/cards` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `project_id` | `string` | yes | — | — | Project ID (UUID) |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields (avatars, nested user objects). |

**Examples**

- List project cards.: `kaiten --json projects cards list --project-id p1 --compact`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/projects/{project_id}/cards/{card_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `project_id` | `string` | yes | — | — | Project ID (UUID) |
| `card_id` | `integer` | yes | — | — | Card ID to remove |

**Examples**

- Remove a card from a project.: `kaiten --json projects cards remove --project-id p1 --card-id 10`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `projects.create`

| Field | Value |
|---|---|
| CLI command | `kaiten projects create` |
| MCP alias | `kaiten_create_project` |
| Description | Create a new Kaiten project. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/projects` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `title` | `string` | yes | — | — | Project title (stored as 'name') |
| `description` | `string` | no | — | — | Project description |
| `work_calendar_id` | `string` | no | — | — | Work calendar UUID to attach to the project |
| `settings` | `object` | no | — | — | Project settings |
| `properties` | `object` | no | — | — | Custom property values as {id_<N>: value} pairs |

**Examples**

- Create a project.: `kaiten --json projects create --title "Platform"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `projects.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten projects delete` |
| MCP alias | `kaiten_delete_project` |
| Description | Delete a Kaiten project. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/projects/{project_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `project_id` | `string` | yes | — | — | Project ID (UUID) |

**Examples**

- Delete a project.: `kaiten --json projects delete --project-id p1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `projects.get`

| Field | Value |
|---|---|
| CLI command | `kaiten projects get` |
| MCP alias | `kaiten_get_project` |
| Description | Get a Kaiten project by ID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/projects/{project_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `project_id` | `string` | yes | — | — | Project ID (UUID) |
| `with_cards_data` | `boolean` | no | — | — | Include full card data with path info and custom properties |

**Examples**

- Get a project by ID.: `kaiten --json projects get --project-id p1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `projects.list`

| Field | Value |
|---|---|
| CLI command | `kaiten projects list` |
| MCP alias | `kaiten_list_projects` |
| Description | List all Kaiten projects in the company. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/projects` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- List company projects.: `kaiten --json projects list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `projects.update`

| Field | Value |
|---|---|
| CLI command | `kaiten projects update` |
| MCP alias | `kaiten_update_project` |
| Description | Update a Kaiten project. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/projects/{project_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `project_id` | `string` | yes | — | — | Project ID (UUID) |
| `title` | `string` | no | — | — | Project title (stored as 'name') |
| `description` | `string` | no | — | — | Project description |
| `condition` | `string` | no | `active`, `inactive` | — | Project condition (active or inactive) |
| `work_calendar_id` | `string` | no | — | — | Work calendar UUID to attach to the project |
| `settings` | `object` | no | — | — | Project settings |
| `properties` | `object` | no | — | — | Custom property values as {id_<N>: value} pairs; set a key to null to clear it |

**Examples**

- Update a project.: `kaiten --json projects update --project-id p1 --title "Platform"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `sprints.create`

| Field | Value |
|---|---|
| CLI command | `kaiten sprints create` |
| MCP alias | `kaiten_create_sprint` |
| Description | Create a new Kaiten sprint. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/sprints` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `title` | `string` | yes | — | — | Sprint title |
| `board_id` | `integer` | yes | — | — | Board ID for the sprint |
| `goal` | `string` | no | — | — | Sprint goal |
| `start_date` | `string` | no | — | — | Start date (ISO 8601) |
| `finish_date` | `string` | no | — | — | Finish date (ISO 8601) |

**Examples**

- Create a sprint.: `kaiten --json sprints create --title "Sprint 1" --board-id 10`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/sprints/{sprint_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `sprint_id` | `integer` | yes | — | — | Sprint ID |

**Examples**

- Delete a sprint.: `kaiten --json sprints delete --sprint-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/sprints/{sprint_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `sprint_id` | `integer` | yes | — | — | Sprint ID |
| `exclude_deleted_cards` | `boolean` | no | — | — | Exclude deleted cards from the sprint summary |

**Examples**

- Get a sprint.: `kaiten --json sprints get --sprint-id 1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/sprints` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `active` | `boolean` | no | — | — | Filter by active/inactive |
| `limit` | `integer` | no | — | — | Max results (max 100) |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- List sprints.: `kaiten --json sprints list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/sprints/{sprint_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `sprint_id` | `integer` | yes | — | — | Sprint ID |
| `title` | `string` | no | — | — | Sprint title |
| `goal` | `string` | no | — | — | Sprint goal |
| `start_date` | `string` | no | — | — | Start date (ISO 8601) |
| `finish_date` | `string` | no | — | — | Finish date (ISO 8601) |
| `active` | `boolean` | no | — | — | Set to false to finish/complete the sprint |
| `archive_done_cards` | `boolean` | no | — | — | Archive completed cards when finishing a sprint |

**Examples**

- Update a sprint.: `kaiten --json sprints update --sprint-id 1 --active false`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Live contract: `live_passed_as_expected_error`; expected statuses: `403`, `404`, `405`, `500`
- Live note: When sprint creation is unavailable or the created sprint id cannot be resolved, sandbox may return 403/404/405 or 500 on a sentinel sprint id; the live suite validates that documented defect contract explicitly.

<a id="module-roles-and-groups"></a>
## Роли и группы (`roles_and_groups`) — 31 commands

Roles, groups and permission-related operations.

**Namespace tree**

```text
company-groups
  create
  delete
  get
  list
  update
company-users
  list
  list-all
  remove-virtual
  update
group-admins
  add
  list
  remove
group-entities
  add
  list
  remove
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
  get
  list
  remove
  update
user-roles
  create
  delete
  get
  list
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/groups` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Group name |

**Examples**

- Create a company group.: `kaiten --json company-groups create --name "Engineering"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `company-groups.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten company-groups delete` |
| MCP alias | `kaiten_delete_company_group` |
| Description | Delete a company group in Kaiten. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/groups/{group_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |

**Examples**

- Delete a company group.: `kaiten --json company-groups delete --group-uid grp-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `company-groups.get`

| Field | Value |
|---|---|
| CLI command | `kaiten company-groups get` |
| MCP alias | `kaiten_get_company_group` |
| Description | Get a company group by UID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/company/groups/{group_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |

**Examples**

- Get a company group.: `kaiten --json company-groups get --group-uid grp-1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `company-groups.list`

| Field | Value |
|---|---|
| CLI command | `kaiten company-groups list` |
| MCP alias | `kaiten_list_company_groups` |
| Description | List company groups in Kaiten. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/groups` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Search query |
| `limit` | `integer` | no | — | — | Max results to return |
| `offset` | `integer` | no | — | — | Offset for pagination |

**Examples**

- List company groups.: `kaiten --json company-groups list --query "Engineering"`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `company-groups.update`

| Field | Value |
|---|---|
| CLI command | `kaiten company-groups update` |
| MCP alias | `kaiten_update_company_group` |
| Description | Update a company group in Kaiten. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/groups/{group_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |
| `name` | `string` | no | — | — | New group name |

**Examples**

- Update a company group.: `kaiten --json company-groups update --group-uid grp-1 --name "Docs"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `company-users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten company-users list` |
| MCP alias | `kaiten_list_company_users` |
| Description | List company users from the administrative Members section. Defaults to for_members_section=true with paginated limit/offset. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/users` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `for_members_section` | `boolean` | no | — | — | Use the administrative Members section response shape (default true). |
| `query` | `string` | no | — | — | Search by email or full name. |
| `limit` | `integer` | no | — | >= 1, <= 100 | Maximum number of users to return (default 100). |
| `offset` | `integer` | no | — | >= 0 | Number of users to skip (default 0). |
| `only_records_count` | `boolean` | no | — | — | Return only the filtered user count. |
| `access_type_permissions` | `string` | no | `member`, `guest`, `denied` | — | Filter by Kaiten access type. |
| `sd_access_type` | `string` | no | `any`, `has_access`, `has_no_access` | — | Filter by Service Desk access. |
| `take_licence` | `string` | no | `any`, `yes`, `no` | — | Filter by users who take a paid license. |
| `temporarily_inactive_status` | `string` | no | `all_users`, `only_temporarily_inactive_users`, `only_active_users` | — | Filter by temporary deactivation status. |
| `group_ids` | `array` | no | — | — | JSON array of company group IDs. |
| `permissions` | `array` | no | — | — | JSON array of company permission criteria. |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return per user. |

**Examples**

- List administrative company members.: `kaiten --json company-users list --limit 100 --offset 0 --compact`
- Count company members including temporarily inactive users.: `kaiten --json company-users list --only-records-count --temporarily-inactive-status all_users`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Use this command for paginated administrative member exports. `users.list` is a generic users endpoint and may not be reliable for full member paging.

### `company-users.list-all`

| Field | Value |
|---|---|
| CLI command | `kaiten company-users list-all` |
| MCP alias | `kaiten_list_all_company_users` |
| Description | List all administrative company users with bounded pagination and no silent truncation. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `aggregated` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/company/users` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `for_members_section` | `boolean` | no | — | — | Use the administrative Members response shape (default true). |
| `query` | `string` | no | — | — | Search by email or full name. |
| `page_size` | `integer` | no | — | >= 1, <= 100 | Users per request (1..100, default 100). |
| `max_pages` | `integer` | no | — | >= 1, <= 1000 | Safety cap for requests; a full final page causes an error instead of truncation (default 100). |
| `access_type_permissions` | `string` | no | `member`, `guest`, `denied` | — | Filter by Kaiten access type. |
| `sd_access_type` | `string` | no | `any`, `has_access`, `has_no_access` | — | Filter by Service Desk access. |
| `take_licence` | `string` | no | `any`, `yes`, `no` | — | Filter by paid-license usage. |
| `temporarily_inactive_status` | `string` | no | `all_users`, `only_temporarily_inactive_users`, `only_active_users` | — | Filter by temporary deactivation status. |
| `group_ids` | `array` | no | — | — | JSON array of group IDs. |
| `permissions` | `array` | no | — | — | JSON array of company permission criteria. |
| `compact` | `boolean` | no | — | — | Return compact output without heavy fields. |
| `fields` | `string` | no | — | — | Comma-separated field names to return per user. |

**Examples**

- Read every company user within an explicit safety cap.: `kaiten --json company-users list-all --page-size 100 --max-pages 100 --fields id,uid,email,full_name --compact`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Uses at most 100 users per request for forward compatibility.
- If max_pages is reached on a full page, the command fails instead of returning a partial list.

### `company-users.remove-virtual`

| Field | Value |
|---|---|
| CLI command | `kaiten company-users remove-virtual` |
| MCP alias | `kaiten_remove_virtual_company_user` |
| Description | Remove a virtual company user. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `user_id` | `integer` | yes | — | — | Virtual user ID |

**Examples**

- Remove a virtual company user.: `kaiten --json company-users remove-virtual --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `company-users.update`

| Field | Value |
|---|---|
| CLI command | `kaiten company-users update` |
| MCP alias | `kaiten_update_company_user` |
| Description | Update a company user. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `user_id` | `integer` | yes | — | — | User ID |
| `full_name` | `string` | no | — | — | Full name |
| `email` | `string` | no | — | — | Email |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Update a company user.: `kaiten --json company-users update --user-id 7 --full-name "Alice Smith"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `group-admins.add`

| Field | Value |
|---|---|
| CLI command | `kaiten group-admins add` |
| MCP alias | `kaiten_add_group_admin` |
| Description | Add an admin to a company group. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/groups/{group_uid}/admins` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |
| `user_id` | `integer` | yes | — | — | User ID to add as admin |

**Examples**

- Add a group admin.: `kaiten --json group-admins add --group-uid grp-1 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `group-admins.list`

| Field | Value |
|---|---|
| CLI command | `kaiten group-admins list` |
| MCP alias | `kaiten_list_group_admins` |
| Description | List admins of a company group. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/groups/{group_uid}/admins` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields. |

**Examples**

- List group admins.: `kaiten --json group-admins list --group-uid grp-1 --compact`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `group-admins.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten group-admins remove` |
| MCP alias | `kaiten_remove_group_admin` |
| Description | Remove an admin from a company group. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/groups/{group_uid}/admins/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |
| `user_id` | `integer` | yes | — | — | User ID to remove |

**Examples**

- Remove a group admin.: `kaiten --json group-admins remove --group-uid grp-1 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `group-entities.add`

| Field | Value |
|---|---|
| CLI command | `kaiten group-entities add` |
| MCP alias | `kaiten_add_group_entity` |
| Description | Attach a tree entity to a company group. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/groups/{group_uid}/entities` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |
| `entity_uid` | `string` | yes | — | — | Tree entity UID |
| `role_ids` | `array` | yes | — | — | Tree entity role IDs. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Attach a group entity.: `kaiten --json group-entities add --group-uid grp-1 --entity-uid entity-1 --role-ids '["role-1"]'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `group-entities.list`

| Field | Value |
|---|---|
| CLI command | `kaiten group-entities list` |
| MCP alias | `kaiten_list_group_entities` |
| Description | List tree entities attached to a company group. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/company/groups/{group_uid}/entities` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |

**Examples**

- List group entities.: `kaiten --json group-entities list --group-uid grp-1`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `group-entities.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten group-entities remove` |
| MCP alias | `kaiten_remove_group_entity` |
| Description | Remove a tree entity from a company group. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/groups/{group_uid}/entities/{entity_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |
| `entity_uid` | `string` | yes | — | — | Tree entity UID |

**Examples**

- Remove a group entity.: `kaiten --json group-entities remove --group-uid grp-1 --entity-uid entity-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `group-entities.update`

| Field | Value |
|---|---|
| CLI command | `kaiten group-entities update` |
| MCP alias | `kaiten_update_group_entity` |
| Description | Update a tree entity attached to a company group. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/company/groups/{group_uid}/entities/{entity_uid}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |
| `entity_uid` | `string` | yes | — | — | Tree entity UID |
| `role_ids` | `array` | no | — | — | Tree entity role IDs. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Update a group entity.: `kaiten --json group-entities update --group-uid grp-1 --entity-uid entity-1 --role-ids '["role-1"]'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `group-users.add`

| Field | Value |
|---|---|
| CLI command | `kaiten group-users add` |
| MCP alias | `kaiten_add_group_user` |
| Description | Add a user to a company group. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/groups/{group_uid}/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |
| `user_id` | `integer` | yes | — | — | User ID to add |

**Examples**

- Add a user to a group.: `kaiten --json group-users add --group-uid grp-1 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `group-users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten group-users list` |
| MCP alias | `kaiten_list_group_users` |
| Description | List one page of users in a company group. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/groups/{group_uid}/users` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default 50, max 100) |
| `offset` | `integer` | no | — | >= 0 | Pagination offset |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields. |

**Examples**

- List group users.: `kaiten --json group-users list --group-uid grp-1 --compact`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This direct command returns one page; increase offset to read subsequent pages.

### `group-users.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten group-users remove` |
| MCP alias | `kaiten_remove_group_user` |
| Description | Remove a user from a company group. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/groups/{group_uid}/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_uid` | `string` | yes | — | — | Group UID |
| `user_id` | `integer` | yes | — | — | User ID to remove |

**Examples**

- Remove a user from a group.: `kaiten --json group-users remove --group-uid grp-1 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `roles.get`

| Field | Value |
|---|---|
| CLI command | `kaiten roles get` |
| MCP alias | `kaiten_get_role` |
| Description | Get a role by ID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/tree-entity-roles/{role_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `role_id` | `string` | yes | — | — | Role ID (UUID) |

**Examples**

- Get a role.: `kaiten --json roles get --role-id role-1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `roles.list`

| Field | Value |
|---|---|
| CLI command | `kaiten roles list` |
| MCP alias | `kaiten_list_roles` |
| Description | List available roles in Kaiten. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/tree-entity-roles` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Search query |
| `limit` | `integer` | no | — | — | Max results to return |
| `offset` | `integer` | no | — | — | Offset for pagination |

**Examples**

- List roles.: `kaiten --json roles list --query "admin"`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-users.add`

| Field | Value |
|---|---|
| CLI command | `kaiten space-users add` |
| MCP alias | `kaiten_add_space_user` |
| Description | Add a user to a Kaiten space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `user_id` | `integer` | yes | — | — | User ID to add |
| `role_id` | `string` | no | — | — | Role ID (UUID) to assign |

**Examples**

- Add a user to a space.: `kaiten --json space-users add --space-id 1 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-users.get`

| Field | Value |
|---|---|
| CLI command | `kaiten space-users get` |
| MCP alias | `kaiten_get_space_user` |
| Description | Get a user in a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/spaces/{space_id}/users/{user_id}` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `user_id` | `integer` | yes | — | — | User ID |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields. |

**Examples**

- Get a space user.: `kaiten --json space-users get --space-id 1 --user-id 7 --compact`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten space-users list` |
| MCP alias | `kaiten_list_space_users` |
| Description | List one page of users in a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/spaces/{space_id}/users` |
| Compact | `yes` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `limit` | `integer` | no | — | >= 1, <= 100 | Max results (default 50, max 100) |
| `offset` | `integer` | no | — | >= 0 | Pagination offset |
| `compact` | `boolean` | no | — | — | Return compact response without heavy fields. |

**Examples**

- List space users.: `kaiten --json space-users list --space-id 1 --compact`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This direct command returns one page; increase offset to read subsequent pages.

### `space-users.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten space-users remove` |
| MCP alias | `kaiten_remove_space_user` |
| Description | Remove a user from a Kaiten space. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `user_id` | `integer` | yes | — | — | User ID to remove |

**Examples**

- Remove a user from a space.: `kaiten --json space-users remove --space-id 1 --user-id 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-users.update`

| Field | Value |
|---|---|
| CLI command | `kaiten space-users update` |
| MCP alias | `kaiten_update_space_user` |
| Description | Update a user's role in a Kaiten space. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/spaces/{space_id}/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `user_id` | `integer` | yes | — | — | User ID to update |
| `role_id` | `string` | no | — | — | New role ID (UUID) |

**Examples**

- Update a space user role.: `kaiten --json space-users update --space-id 1 --user-id 7 --role-id 9`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `user-roles.create`

| Field | Value |
|---|---|
| CLI command | `kaiten user-roles create` |
| MCP alias | `kaiten_create_user_role` |
| Description | Create a user role. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/user-roles` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Role name |
| `permissions` | `object` | no | — | — | Role permissions JSON. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Create a user role.: `kaiten --json user-roles create --name "Manager"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `user-roles.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten user-roles delete` |
| MCP alias | `kaiten_delete_user_role` |
| Description | Delete a user role. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/user-roles/{role_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `role_id` | `integer` | yes | — | — | User role ID |

**Examples**

- Delete a user role.: `kaiten --json user-roles delete --role-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `user-roles.get`

| Field | Value |
|---|---|
| CLI command | `kaiten user-roles get` |
| MCP alias | `kaiten_get_user_role` |
| Description | Get a user role. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/user-roles/{role_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `role_id` | `integer` | yes | — | — | User role ID |

**Examples**

- Get a user role.: `kaiten --json user-roles get --role-id 1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `user-roles.list`

| Field | Value |
|---|---|
| CLI command | `kaiten user-roles list` |
| MCP alias | `kaiten_list_user_roles` |
| Description | List user roles. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/user-roles` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Search query |
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- List user roles.: `kaiten --json user-roles list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `user-roles.update`

| Field | Value |
|---|---|
| CLI command | `kaiten user-roles update` |
| MCP alias | `kaiten_update_user_role` |
| Description | Update a user role. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/user-roles/{role_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `role_id` | `integer` | yes | — | — | User role ID |
| `name` | `string` | no | — | — | Role name |
| `permissions` | `object` | no | — | — | Role permissions JSON. |
| `payload` | `object` | no | — | — | Extra JSON body fields from the Kaiten API docs. |

**Examples**

- Update a user role.: `kaiten --json user-roles update --role-id 1 --name "Manager"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

<a id="module-scim"></a>
## SCIM (`scim`) — 8 commands

SCIM v2 user and group provisioning.

**Namespace tree**

```text
scim.groups
  create
  get
  list
  update
scim.users
  create
  get
  list
  update
```

### `scim.groups.create`

| Field | Value |
|---|---|
| CLI command | `kaiten scim groups create` |
| MCP alias | `kaiten_create_scim_group` |
| Description | Create a SCIM group. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/scim/v2/Groups` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `payload` | `object` | yes | — | — | SCIM JSON payload. Sent as the request body. |

**Examples**

- Create a SCIM group.: `kaiten --json scim groups create --payload '{"displayName":"Engineering"}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `scim.groups.get`

| Field | Value |
|---|---|
| CLI command | `kaiten scim groups get` |
| MCP alias | `kaiten_get_scim_group` |
| Description | Get a SCIM group. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/scim/v2/Groups/{group_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_id` | `string` | yes | — | — | SCIM group ID. |

**Examples**

- Get a SCIM group.: `kaiten --json scim groups get --group-id group-id`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `scim.groups.list`

| Field | Value |
|---|---|
| CLI command | `kaiten scim groups list` |
| MCP alias | `kaiten_list_scim_groups` |
| Description | List SCIM groups. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/scim/v2/Groups` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `start_index` | `integer` | no | — | — | SCIM start index. |
| `count` | `integer` | no | — | — | SCIM page size. |
| `filter` | `string` | no | — | — | SCIM filter expression. |

**Examples**

- List SCIM groups.: `kaiten --json scim groups list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `scim.groups.update`

| Field | Value |
|---|---|
| CLI command | `kaiten scim groups update` |
| MCP alias | `kaiten_update_scim_group` |
| Description | Update a SCIM group. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/scim/v2/Groups/{group_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `group_id` | `string` | yes | — | — | SCIM group ID. |
| `payload` | `object` | yes | — | — | SCIM JSON payload. Sent as the request body. |

**Examples**

- Update a SCIM group.: `kaiten --json scim groups update --group-id group-id --payload '{"displayName":"Ops"}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `scim.users.create`

| Field | Value |
|---|---|
| CLI command | `kaiten scim users create` |
| MCP alias | `kaiten_create_scim_user` |
| Description | Create a SCIM user. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/scim/v2/Users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `payload` | `object` | yes | — | — | SCIM JSON payload. Sent as the request body. |

**Examples**

- Create a SCIM user.: `kaiten --json scim users create --payload '{"userName":"alice@example.com"}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `scim.users.get`

| Field | Value |
|---|---|
| CLI command | `kaiten scim users get` |
| MCP alias | `kaiten_get_scim_user` |
| Description | Get a SCIM user. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/scim/v2/Users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `user_id` | `string` | yes | — | — | SCIM user ID. |

**Examples**

- Get a SCIM user.: `kaiten --json scim users get --user-id user-id`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `scim.users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten scim users list` |
| MCP alias | `kaiten_list_scim_users` |
| Description | List SCIM users. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/scim/v2/Users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `start_index` | `integer` | no | — | — | SCIM start index. |
| `count` | `integer` | no | — | — | SCIM page size. |
| `filter` | `string` | no | — | — | SCIM filter expression. |

**Examples**

- List SCIM users.: `kaiten --json scim users list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `scim.users.update`

| Field | Value |
|---|---|
| CLI command | `kaiten scim users update` |
| MCP alias | `kaiten_update_scim_user` |
| Description | Update a SCIM user. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/scim/v2/Users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `user_id` | `string` | yes | — | — | SCIM user ID. |
| `payload` | `object` | yes | — | — | SCIM JSON payload. Sent as the request body. |

**Examples**

- Update a SCIM user.: `kaiten --json scim users update --user-id user-id --payload '{"active":false}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/audit-logs` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `categories` | `string` | no | — | — | Comma-separated log categories |
| `actions` | `string` | no | — | — | Comma-separated audit actions |
| `from` | `string` | no | — | — | Start of date range filter |
| `to` | `string` | no | — | — | End of date range filter |
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- List audit logs.: `kaiten --json audit-logs list --limit 10`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-activity.get`

| Field | Value |
|---|---|
| CLI command | `kaiten card-activity get` |
| MCP alias | `kaiten_get_card_activity` |
| Description | Get activity feed for a Kaiten card. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/activity` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- Get card activity.: `kaiten --json card-activity get --card-id 1`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-location-history.batch-get`

| Field | Value |
|---|---|
| CLI command | `kaiten card-location-history batch-get` |
| MCP alias | `kaiten_batch_get_card_location_history` |
| Description | Fetch location history for multiple cards with bounded worker concurrency. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `aggregated` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/cards/location-history/batch` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_ids` | `array` | yes | — | — | Card IDs to fetch |
| `workers` | `integer` | no | — | — | Parallel workers (default 2, max 6) |
| `fields` | `string` | no | — | — | Comma-separated field names to keep for each history row |

**Examples**

- Fetch history for several cards in one CLI call.: `kaiten --json card-location-history batch-get --card-ids '[1,2,3]'`
- Fetch projected history rows with bounded concurrency.: `kaiten --json card-location-history batch-get --card-ids '[1,2,3]' --workers 2 --fields changed,column_id,subcolumn_id`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/cards/{card_id}/location-history` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |

**Examples**

- Get card location history.: `kaiten --json card-location-history get --card-id 1`

**Notes**

- Bulk alternative: `card-location-history.batch-get`
- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/company/activity` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `actions` | `string` | no | — | — | Comma-separated action types |
| `created_after` | `string` | no | — | — | Filter activities after this datetime |
| `created_before` | `string` | no | — | — | Filter activities before this datetime |
| `author_id` | `integer` | no | — | — | Filter by author user ID |
| `cursor_created` | `string` | no | — | — | Cursor datetime |
| `cursor_id` | `integer` | no | — | — | Cursor ID |
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |
| `compact` | `boolean` | no | — | — | Strip heavy fields |
| `fields` | `string` | no | — | — | Comma-separated field names to keep |

**Examples**

- Get company activity.: `kaiten --json company-activity get --limit 10`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `saved-filters.create`

| Field | Value |
|---|---|
| CLI command | `kaiten saved-filters create` |
| MCP alias | `kaiten_create_saved_filter` |
| Description | Create a saved filter. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/saved-filters` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Filter name |
| `filter` | `object` | yes | — | — | Filter criteria object |
| `shared` | `boolean` | no | — | — | Whether the filter is shared with the team |

**Examples**

- Create a saved filter.: `kaiten --json saved-filters create --name MyFilter --filter '{}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `saved-filters.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten saved-filters delete` |
| MCP alias | `kaiten_delete_saved_filter` |
| Description | Delete a saved filter. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/saved-filters/{filter_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `filter_id` | `integer` | yes | — | — | Filter ID |

**Examples**

- Delete a saved filter.: `kaiten --json saved-filters delete --filter-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `saved-filters.get`

| Field | Value |
|---|---|
| CLI command | `kaiten saved-filters get` |
| MCP alias | `kaiten_get_saved_filter` |
| Description | Get a saved filter by ID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/saved-filters/{filter_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `filter_id` | `integer` | yes | — | — | Filter ID |

**Examples**

- Get a saved filter.: `kaiten --json saved-filters get --filter-id 1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `saved-filters.list`

| Field | Value |
|---|---|
| CLI command | `kaiten saved-filters list` |
| MCP alias | `kaiten_list_saved_filters` |
| Description | List saved filters. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/saved-filters` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- List saved filters.: `kaiten --json saved-filters list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `saved-filters.update`

| Field | Value |
|---|---|
| CLI command | `kaiten saved-filters update` |
| MCP alias | `kaiten_update_saved_filter` |
| Description | Update a saved filter. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/saved-filters/{filter_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `filter_id` | `integer` | yes | — | — | Filter ID |
| `name` | `string` | no | — | — | Filter name |
| `filter` | `object` | no | — | — | Filter criteria object |
| `shared` | `boolean` | no | — | — | Whether the filter is shared with the team |

**Examples**

- Update a saved filter.: `kaiten --json saved-filters update --filter-id 1 --name Renamed`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-activity-all.get`

| Field | Value |
|---|---|
| CLI command | `kaiten space-activity-all get` |
| MCP alias | `kaiten_get_all_space_activity` |
| Description | Fetch all space activity with automatic pagination. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `aggregated` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/spaces/{space_id}/activity` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `actions` | `string` | no | — | — | Comma-separated action types |
| `created_after` | `string` | no | — | — | Filter activities after this datetime |
| `created_before` | `string` | no | — | — | Filter activities before this datetime |
| `author_id` | `integer` | no | — | — | Filter by author user ID |
| `page_size` | `integer` | no | — | — | Events per page (default 100, max 100) |
| `max_pages` | `integer` | no | — | — | Safety limit on pages to fetch |
| `compact` | `boolean` | no | — | — | Strip heavy fields; defaults to true for bulk |
| `fields` | `string` | no | — | — | Comma-separated field names to keep |

**Examples**

- Fetch all space activity with bounded pagination.: `kaiten --json space-activity-all get --space-id 1 --page-size 20 --max-pages 2`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Use this aggregated path for report windows instead of building manual offset loops around space-activity.get.

### `space-activity.get`

| Field | Value |
|---|---|
| CLI command | `kaiten space-activity get` |
| MCP alias | `kaiten_get_space_activity` |
| Description | Get activity feed for a Kaiten space. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/spaces/{space_id}/activity` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `actions` | `string` | no | — | — | Comma-separated action types |
| `created_after` | `string` | no | — | — | Filter activities after this datetime |
| `created_before` | `string` | no | — | — | Filter activities before this datetime |
| `author_id` | `integer` | no | — | — | Filter by author user ID |
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |
| `compact` | `boolean` | no | — | — | Strip heavy fields |
| `fields` | `string` | no | — | — | Comma-separated field names to keep |

**Examples**

- Get space activity.: `kaiten --json space-activity get --space-id 1 --limit 10`

**Notes**

- Bulk alternative: `space-activity-all.get`
- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/cards/{card_id}/sla-rules-measurements` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |

**Examples**

- Get card SLA measurements.: `kaiten --json card-sla-measurements get --card-id 1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-slas.attach`

| Field | Value |
|---|---|
| CLI command | `kaiten card-slas attach` |
| MCP alias | `kaiten_attach_card_sla` |
| Description | Attach an SLA policy to a card. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/slas` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `sla_id` | `string` | yes | — | — | SLA ID (UUID) |

**Examples**

- Attach an SLA to a card.: `kaiten --json card-slas attach --card-id 1 --sla-id sla-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `card-slas.detach`

| Field | Value |
|---|---|
| CLI command | `kaiten card-slas detach` |
| MCP alias | `kaiten_detach_card_sla` |
| Description | Detach an SLA policy from a card. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/cards/{card_id}/slas/{sla_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID |
| `sla_id` | `string` | yes | — | — | SLA ID (UUID) |

**Examples**

- Detach an SLA from a card.: `kaiten --json card-slas detach --card-id 1 --sla-id sla-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.organization-users.add`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organization-users add` |
| MCP alias | `kaiten_add_sd_org_user` |
| Description | Add a user to a Service Desk organization. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/organizations/{organization_id}/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | — | Organization ID |
| `user_id` | `integer` | yes | — | — | User ID |
| `permissions` | `integer` | no | — | — | Permission bitmask |

**Examples**

- Add an organization user.: `kaiten --json service-desk organization-users add --organization-id 1 --user-id 2`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.organization-users.batch-add`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organization-users batch-add` |
| MCP alias | `kaiten_batch_add_sd_org_users` |
| Description | Add multiple users to a Service Desk organization. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/organizations/{organization_id}/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | — | Organization ID |
| `user_ids` | `array` | yes | — | — | User IDs |

**Examples**

- Batch-add organization users.: `kaiten --json service-desk organization-users batch-add --organization-id 1 --user-ids '[1,2]'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.organization-users.batch-remove`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organization-users batch-remove` |
| MCP alias | `kaiten_batch_remove_sd_org_users` |
| Description | Remove multiple users from a Service Desk organization. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/organizations/{organization_id}/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | — | Organization ID |
| `user_ids` | `array` | yes | — | — | User IDs |

**Examples**

- Batch-remove organization users.: `kaiten --json service-desk organization-users batch-remove --organization-id 1 --user-ids '[1,2]'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.organization-users.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organization-users remove` |
| MCP alias | `kaiten_remove_sd_org_user` |
| Description | Remove a user from a Service Desk organization. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/organizations/{organization_id}/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | — | Organization ID |
| `user_id` | `integer` | yes | — | — | User ID |

**Examples**

- Remove an organization user.: `kaiten --json service-desk organization-users remove --organization-id 1 --user-id 2`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.organization-users.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organization-users update` |
| MCP alias | `kaiten_update_sd_org_user` |
| Description | Update a user's permissions in a Service Desk organization. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/organizations/{organization_id}/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | — | Organization ID |
| `user_id` | `integer` | yes | — | — | User ID |
| `permissions` | `integer` | no | — | — | Permission bitmask |

**Examples**

- Update organization-user permissions.: `kaiten --json service-desk organization-users update --organization-id 1 --user-id 2 --permissions 7`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/organizations` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Organization name |
| `description` | `string` | no | — | — | Organization description |

**Examples**

- Create an organization.: `kaiten --json service-desk organizations create --name Org`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.organizations.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organizations delete` |
| MCP alias | `kaiten_delete_sd_organization` |
| Description | Delete a Service Desk organization. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/organizations/{organization_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | — | Organization ID |

**Examples**

- Delete an organization.: `kaiten --json service-desk organizations delete --organization-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.organizations.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organizations get` |
| MCP alias | `kaiten_get_sd_organization` |
| Description | Get a Service Desk organization by ID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/service-desk/organizations/{organization_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | — | Organization ID |

**Examples**

- Get an organization.: `kaiten --json service-desk organizations get --organization-id 1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.organizations.list`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organizations list` |
| MCP alias | `kaiten_list_sd_organizations` |
| Description | List Service Desk organizations. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/service-desk/organizations` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Search filter |
| `includeUsers` | `boolean` | no | — | — | Include organization users |
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- List organizations.: `kaiten --json service-desk organizations list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.organizations.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk organizations update` |
| MCP alias | `kaiten_update_sd_organization` |
| Description | Update a Service Desk organization. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/organizations/{organization_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `organization_id` | `integer` | yes | — | — | Organization ID |
| `name` | `string` | no | — | — | Organization name |
| `description` | `string` | no | — | — | Organization description |

**Examples**

- Update an organization.: `kaiten --json service-desk organizations update --organization-id 1 --name Org2`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.requests.create`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk requests create` |
| MCP alias | `kaiten_create_sd_request` |
| Description | Create a new Service Desk request. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/requests` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `title` | `string` | yes | — | — | Request title |
| `service_id` | `integer` | yes | — | — | Service ID |
| `description` | `string` | no | — | — | Request description |
| `priority` | `string` | no | — | — | Request priority |

**Examples**

- Create a request.: `kaiten --json service-desk requests create --title "Help" --service-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/requests/{request_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `request_id` | `integer` | yes | — | — | Request ID |

**Examples**

- Delete a request.: `kaiten --json service-desk requests delete --request-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/service-desk/requests/{request_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `request_id` | `integer` | yes | — | — | Request ID |

**Examples**

- Get a request.: `kaiten --json service-desk requests get --request-id 1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/service-desk/requests` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Search filter |
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- List Service Desk requests.: `kaiten --json service-desk requests list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.requests.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk requests update` |
| MCP alias | `kaiten_update_sd_request` |
| Description | Update a Service Desk request. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/requests/{request_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `request_id` | `integer` | yes | — | — | Request ID |
| `title` | `string` | no | — | — | Request title |
| `description` | `string` | no | — | — | Request description |
| `priority` | `string` | no | — | — | Request priority |

**Examples**

- Update a request.: `kaiten --json service-desk requests update --request-id 1 --priority high`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/services` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Service name |
| `board_id` | `integer` | yes | — | — | Board ID |
| `position` | `integer` | yes | — | — | Sort position |
| `description` | `string` | no | — | — | Service description |
| `template_description` | `string` | no | — | — | Default description template |
| `lng` | `string` | yes | `en`, `ru` | — | Language code |
| `display_status` | `string` | no | `by_column`, `by_state` | — | How status is displayed |
| `column_id` | `integer` | no | — | — | Default column ID |
| `lane_id` | `integer` | no | — | — | Default lane ID |
| `type_id` | `integer` | no | — | — | Card type ID |
| `email_settings` | `integer` | no | — | — | Email settings bitmask |
| `fields_settings` | `object` | no | — | — | Request form fields configuration |
| `settings` | `object` | no | — | — | Additional settings |
| `allow_to_add_external_recipients` | `boolean` | no | — | — | Allow external recipients |
| `hide_in_list` | `boolean` | no | — | — | Hide service in list |
| `is_default` | `boolean` | no | — | — | Set as default service |

**Examples**

- Create a service.: `kaiten --json service-desk services create --name Support --board-id 1 --position 1 --lng en`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.services.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk services delete` |
| MCP alias | `kaiten_delete_sd_service` |
| Description | Archive a Service Desk service. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/services/{service_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `service_id` | `integer` | yes | — | — | Service ID |

**Examples**

- Archive a service.: `kaiten --json service-desk services delete --service-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.services.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk services get` |
| MCP alias | `kaiten_get_sd_service` |
| Description | Get a Service Desk service by ID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/service-desk/services/{service_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `service_id` | `integer` | yes | — | — | Service ID |

**Examples**

- Get a service.: `kaiten --json service-desk services get --service-id 1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.services.list`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk services list` |
| MCP alias | `kaiten_list_sd_services` |
| Description | List Service Desk services. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/service-desk/services` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Search filter |
| `include_archived` | `boolean` | no | — | — | Include archived services |
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- List services.: `kaiten --json service-desk services list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.services.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk services update` |
| MCP alias | `kaiten_update_sd_service` |
| Description | Update a Service Desk service. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/services/{service_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `service_id` | `integer` | yes | — | — | Service ID |
| `name` | `string` | no | — | — | Service name |
| `description` | `string` | no | — | — | Service description |
| `template_description` | `string` | no | — | — | Default description template |
| `lng` | `string` | no | — | — | Language code |
| `display_status` | `string` | no | `by_column`, `by_state` | — | How status is displayed |
| `board_id` | `integer` | no | — | — | Board ID |
| `column_id` | `integer` | no | — | — | Default column ID |
| `lane_id` | `integer` | no | — | — | Default lane ID |
| `type_id` | `integer` | no | — | — | Card type ID |
| `position` | `integer` | no | — | — | Sort position |
| `email_settings` | `integer` | no | — | — | Email settings bitmask |
| `fields_settings` | `object` | no | — | — | Request form fields configuration |
| `settings` | `object` | no | — | — | Additional settings |
| `archived` | `boolean` | no | — | — | Archive or unarchive service |
| `allow_to_add_external_recipients` | `boolean` | no | — | — | Allow external recipients |
| `hide_in_list` | `boolean` | no | — | — | Hide service in list |

**Examples**

- Update a service.: `kaiten --json service-desk services update --service-id 1 --archived`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.settings.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk settings get` |
| MCP alias | `kaiten_get_sd_settings` |
| Description | Get current Service Desk settings. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/sd-settings/current` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- Get Service Desk settings.: `kaiten --json service-desk settings get`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.settings.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk settings update` |
| MCP alias | `kaiten_update_sd_settings` |
| Description | Update Service Desk settings. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/sd-settings/current` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `service_desk_settings` | `object` | yes | — | — | Service Desk configuration object |

**Examples**

- Update Service Desk settings.: `kaiten --json service-desk settings update --service-desk-settings '{}'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.sla-rules.create`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla-rules create` |
| MCP alias | `kaiten_create_sla_rule` |
| Description | Create a rule within an SLA policy. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/sla/{sla_id}/rules` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `sla_id` | `string` | yes | — | — | SLA ID (UUID) |
| `type` | `string` | no | — | — | Rule type |
| `calendar_id` | `string` | no | — | — | Calendar ID |
| `start_column_uid` | `string` | no | — | — | Start column UID |
| `finish_column_uid` | `string` | no | — | — | Finish column UID |
| `estimated_time` | `integer` | no | — | — | Target time in seconds |
| `notification_settings` | `object` | no | — | — | Notification configuration |

**Examples**

- Create an SLA rule.: `kaiten --json service-desk sla-rules create --sla-id sla-1 --type response`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/sla/{sla_id}/rules/{rule_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `sla_id` | `string` | yes | — | — | SLA ID (UUID) |
| `rule_id` | `string` | yes | — | — | Rule ID |

**Examples**

- Delete an SLA rule.: `kaiten --json service-desk sla-rules delete --sla-id sla-1 --rule-id rule-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/sla/{sla_id}/rules/{rule_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `sla_id` | `string` | yes | — | — | SLA ID (UUID) |
| `rule_id` | `string` | yes | — | — | Rule ID |
| `type` | `string` | no | — | — | Rule type |
| `calendar_id` | `string` | no | — | — | Calendar ID |
| `start_column_uid` | `string` | no | — | — | Start column UID |
| `finish_column_uid` | `string` | no | — | — | Finish column UID |
| `estimated_time` | `integer` | no | — | — | Target time in seconds |
| `notification_settings` | `object` | no | — | — | Notification configuration |

**Examples**

- Update an SLA rule.: `kaiten --json service-desk sla-rules update --sla-id sla-1 --rule-id rule-1 --estimated-time 60`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/sla` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | SLA policy name |
| `rules` | `array` | yes | — | — | SLA rules |
| `notification_settings` | `object` | no | — | — | Notification configuration |
| `v2` | `boolean` | no | — | — | Use v2 SLA format |

**Examples**

- Create an SLA policy.: `kaiten --json service-desk sla create --name SLA --rules '[]'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.sla.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla delete` |
| MCP alias | `kaiten_delete_sd_sla` |
| Description | Delete a Service Desk SLA policy. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/sla/{sla_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `sla_id` | `string` | yes | — | — | SLA ID (UUID) |

**Examples**

- Delete an SLA policy.: `kaiten --json service-desk sla delete --sla-id sla-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.sla.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla get` |
| MCP alias | `kaiten_get_sd_sla` |
| Description | Get a Service Desk SLA policy by ID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/service-desk/sla/{sla_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `sla_id` | `string` | yes | — | — | SLA ID (UUID) |

**Examples**

- Get an SLA policy.: `kaiten --json service-desk sla get --sla-id sla-1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.sla.list`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla list` |
| MCP alias | `kaiten_list_sd_sla` |
| Description | List Service Desk SLA policies. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/service-desk/sla` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- List SLA policies.: `kaiten --json service-desk sla list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.sla.recalculate`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla recalculate` |
| MCP alias | `kaiten_recalculate_sla` |
| Description | Trigger recalculation of SLA measurements. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/sla/{sla_id}/recalculate-measurements` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `sla_id` | `string` | yes | — | — | SLA ID (UUID) |

**Examples**

- Recalculate SLA measurements.: `kaiten --json service-desk sla recalculate --sla-id sla-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.sla.stats`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla stats` |
| MCP alias | `kaiten_get_sd_sla_stats` |
| Description | Get Service Desk SLA statistics. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/service-desk/sla-stats` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `date_from` | `string` | no | — | — | Start date (ISO format) |
| `date_to` | `string` | no | — | — | End date (ISO format) |
| `sla_id` | `string` | no | — | — | SLA ID |
| `service_id` | `integer` | no | — | — | Service ID |
| `responsible_id` | `integer` | no | — | — | Responsible user ID |
| `card_type_ids` | `string` | no | — | — | JSON array of card type IDs |
| `tag_ids` | `string` | no | — | — | JSON array of tag IDs |

**Examples**

- Get Service Desk SLA statistics.: `kaiten --json service-desk sla stats --sla-id sla-1`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.sla.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk sla update` |
| MCP alias | `kaiten_update_sd_sla` |
| Description | Update a Service Desk SLA policy. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/sla/{sla_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `sla_id` | `string` | yes | — | — | SLA ID (UUID) |
| `name` | `string` | no | — | — | SLA policy name |
| `status` | `string` | no | — | — | SLA status |
| `notification_settings` | `object` | no | — | — | Notification configuration |
| `should_delete_sla_from_cards` | `boolean` | no | — | — | Remove SLA from cards when deactivating |

**Examples**

- Update an SLA policy.: `kaiten --json service-desk sla update --sla-id sla-1 --status inactive`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.stats.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk stats get` |
| MCP alias | `kaiten_get_sd_stats` |
| Description | Get Service Desk statistics. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/service-desk/stats` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `date_from` | `string` | no | — | — | Start date (ISO format) |
| `date_to` | `string` | no | — | — | End date (ISO format) |
| `service_id` | `integer` | no | — | — | Service ID |
| `report` | `boolean` | no | — | — | Enable report mode |

**Examples**

- Get Service Desk statistics.: `kaiten --json service-desk stats get --date-from 2026-01-01`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.template-answers.create`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk template-answers create` |
| MCP alias | `kaiten_create_sd_template_answer` |
| Description | Create a Service Desk template answer. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/template-answers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Template name |
| `text` | `string` | yes | — | — | Template answer text |

**Examples**

- Create a template answer.: `kaiten --json service-desk template-answers create --name Hello --text "Hi"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.template-answers.delete`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk template-answers delete` |
| MCP alias | `kaiten_delete_sd_template_answer` |
| Description | Delete a Service Desk template answer. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/template-answers/{template_answer_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `template_answer_id` | `string` | yes | — | — | Template answer ID (UUID) |

**Examples**

- Delete a template answer.: `kaiten --json service-desk template-answers delete --template-answer-id ta-1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.template-answers.get`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk template-answers get` |
| MCP alias | `kaiten_get_sd_template_answer` |
| Description | Get a Service Desk template answer by ID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/service-desk/template-answers/{template_answer_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `template_answer_id` | `string` | yes | — | — | Template answer ID (UUID) |

**Examples**

- Get a template answer.: `kaiten --json service-desk template-answers get --template-answer-id ta-1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.template-answers.list`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk template-answers list` |
| MCP alias | `kaiten_list_sd_template_answers` |
| Description | List Service Desk template answers. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/service-desk/template-answers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- List template answers.: `kaiten --json service-desk template-answers list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.template-answers.update`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk template-answers update` |
| MCP alias | `kaiten_update_sd_template_answer` |
| Description | Update a Service Desk template answer. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/template-answers/{template_answer_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `template_answer_id` | `string` | yes | — | — | Template answer ID (UUID) |
| `name` | `string` | no | — | — | Template name |
| `text` | `string` | no | — | — | Template answer text |

**Examples**

- Update a template answer.: `kaiten --json service-desk template-answers update --template-answer-id ta-1 --text "Hello"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.users.list`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk users list` |
| MCP alias | `kaiten_list_sd_users` |
| Description | List Service Desk users. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/service-desk/users` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Search filter |
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |
| `include_paid_users` | `boolean` | no | — | — | Include paid users |
| `include_all_sd_users` | `boolean` | no | — | — | Include all SD users |

**Examples**

- List Service Desk users.: `kaiten --json service-desk users list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.users.set-temp-password`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk users set-temp-password` |
| MCP alias | `kaiten_set_sd_user_temp_password` |
| Description | Generate a temporary password for a Service Desk user. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/users/set-temporary-password/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `user_id` | `integer` | yes | — | — | User ID |

**Examples**

- Generate a temporary password.: `kaiten --json service-desk users set-temp-password --user-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/users/{user_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `user_id` | `integer` | yes | — | — | User ID |
| `full_name` | `string` | no | — | — | User full name |
| `lng` | `string` | no | — | — | Language code |

**Examples**

- Update a Service Desk user.: `kaiten --json service-desk users update --user-id 1 --full-name "Alice"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/services/{service_id}/vote-properties` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `service_id` | `integer` | yes | — | — | Service ID |
| `id` | `integer` | yes | — | — | Custom property ID |

**Examples**

- Add a vote property.: `kaiten --json service-desk vote-properties add --service-id 1 --id 2`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `service-desk.vote-properties.remove`

| Field | Value |
|---|---|
| CLI command | `kaiten service-desk vote-properties remove` |
| MCP alias | `kaiten_remove_service_vote_property` |
| Description | Remove a vote property from a Service Desk service. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/service-desk/services/{service_id}/vote-properties/{property_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `service_id` | `integer` | yes | — | — | Service ID |
| `property_id` | `integer` | yes | — | — | Vote property ID |

**Examples**

- Remove a vote property.: `kaiten --json service-desk vote-properties remove --service-id 1 --property-id 2`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `space-sla-measurements.get`

| Field | Value |
|---|---|
| CLI command | `kaiten space-sla-measurements get` |
| MCP alias | `kaiten_get_space_sla_measurements` |
| Description | Get SLA rule measurements for all cards in a space. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/spaces/{space_id}/sla-rules-measurements` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |

**Examples**

- Get space SLA measurements.: `kaiten --json space-sla-measurements get --space-id 1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/charts/block-resolution-time-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `category_ids` | `array` | no | — | — | Filter by blocker category IDs |

**Examples**

- Get blocker resolution data.: `kaiten --json charts block-resolution get --space-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.
- This is a read-only analytics request even though the Kaiten API uses POST to submit filters.

### `charts.boards.get`

| Field | Value |
|---|---|
| CLI command | `kaiten charts boards get` |
| MCP alias | `kaiten_get_chart_boards` |
| Description | Get board structure for chart configuration in a space. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/charts/{space_id}/boards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |

**Examples**

- Get chart board structure.: `kaiten --json charts boards get --space-id 1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `charts.cfd.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts cfd create` |
| MCP alias | `kaiten_chart_cfd` |
| Description | Build a Cumulative Flow Diagram (CFD) for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/charts/cfd` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `date_from` | `string` | yes | — | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | — | End date (ISO 8601) |
| `tags` | `array` | no | — | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | — | Filter by card type IDs |
| `group_by` | `string` | no | — | — | Grouping mode |
| `cardTypes` | `array` | no | — | — | Filter by card type IDs (alternative field name used by CFD) |
| `selectedLanes` | `array` | no | — | — | Filter by lane IDs |

**Examples**

- Build a Cumulative Flow Diagram (CFD) for a space.: `kaiten --json charts cfd create`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.
- This request can create a transient compute job, so global read-only mode blocks it.

### `charts.control.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts control create` |
| MCP alias | `kaiten_chart_control` |
| Description | Build a Control Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/charts/control-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `date_from` | `string` | yes | — | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | — | End date (ISO 8601) |
| `tags` | `array` | no | — | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | — | Filter by card type IDs |
| `group_by` | `string` | no | — | — | Grouping mode |
| `start_columns` | `array` | yes | — | — | Start column IDs (required) |
| `end_columns` | `array` | yes | — | — | End column IDs (required) |
| `start_column_lanes` | `object` | yes | — | — | Mapping of start column ID to array of lane IDs, e.g. {"10": [1, 2]} |
| `end_column_lanes` | `object` | yes | — | — | Mapping of end column ID to array of lane IDs, e.g. {"20": [3, 4]} |

**Examples**

- Build a Control Chart for a space.: `kaiten --json charts control create`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.
- This request can create a transient compute job, so global read-only mode blocks it.

### `charts.cycle-time.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts cycle-time create` |
| MCP alias | `kaiten_chart_cycle_time` |
| Description | Build a Cycle Time Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/charts/cycle-time-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `date_from` | `string` | yes | — | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | — | End date (ISO 8601) |
| `tags` | `array` | no | — | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | — | Filter by card type IDs |
| `group_by` | `string` | no | — | — | Grouping mode |
| `start_column` | `integer` | yes | — | — | Start column ID |
| `end_column` | `integer` | yes | — | — | End column ID |

**Examples**

- Build a Cycle Time Chart for a space.: `kaiten --json charts cycle-time create`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.
- This request can create a transient compute job, so global read-only mode blocks it.

### `charts.due-dates.get`

| Field | Value |
|---|---|
| CLI command | `kaiten charts due-dates get` |
| MCP alias | `kaiten_chart_due_dates` |
| Description | Get due dates analysis for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/charts/due-dates` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `card_date_from` | `string` | yes | — | — | Card date range start (ISO 8601) |
| `card_date_to` | `string` | yes | — | — | Card date range end (ISO 8601) |
| `checklist_item_date_from` | `string` | yes | — | — | Checklist item date range start (ISO 8601) |
| `checklist_item_date_to` | `string` | yes | — | — | Checklist item date range end (ISO 8601) |
| `due_date` | `string` | no | — | — | Due date filter (ISO 8601) |
| `responsible_id` | `integer` | no | — | — | Responsible user ID |
| `tz_offset` | `integer` | no | — | — | Timezone offset in minutes |
| `lane_ids` | `array` | no | — | — | Filter by lane IDs |
| `column_ids` | `array` | no | — | — | Filter by column IDs |
| `card_type_ids` | `array` | no | — | — | Filter by card type IDs |
| `tag_ids` | `array` | no | — | — | Filter by tag IDs |

**Examples**

- Get due-date analysis.: `kaiten --json charts due-dates get --space-id 1 --card-date-from 2026-01-01 --card-date-to 2026-01-31 --checklist-item-date-from 2026-01-01 --checklist-item-date-to 2026-01-31`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.
- This is a read-only analytics request even though the Kaiten API uses POST to submit filters.

### `charts.lead-time.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts lead-time create` |
| MCP alias | `kaiten_chart_lead_time` |
| Description | Build a Lead Time Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/charts/lead-time` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `date_from` | `string` | yes | — | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | — | End date (ISO 8601) |
| `tags` | `array` | no | — | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | — | Filter by card type IDs |
| `group_by` | `string` | no | — | — | Grouping mode |
| `start_columns` | `array` | yes | — | — | Start column IDs (required) |
| `end_columns` | `array` | yes | — | — | End column IDs (required) |
| `start_column_lanes` | `object` | yes | — | — | Mapping of start column ID to array of lane IDs, e.g. {"10": [1, 2]} |
| `end_column_lanes` | `object` | yes | — | — | Mapping of end column ID to array of lane IDs, e.g. {"20": [3, 4]} |

**Examples**

- Build a Lead Time Chart for a space.: `kaiten --json charts lead-time create`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.
- This request can create a transient compute job, so global read-only mode blocks it.

### `charts.sales-funnel.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts sales-funnel create` |
| MCP alias | `kaiten_chart_sales_funnel` |
| Description | Build a Sales Funnel Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/charts/sales-funnel` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `date_from` | `string` | yes | — | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | — | End date (ISO 8601) |
| `tags` | `array` | no | — | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | — | Filter by card type IDs |
| `group_by` | `string` | no | — | — | Grouping mode |
| `board_configs` | `array` | yes | — | — | Array of board configuration objects. |

**Examples**

- Build a Sales Funnel Chart for a space.: `kaiten --json charts sales-funnel create`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.
- This request can create a transient compute job, so global read-only mode blocks it.

### `charts.spectral.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts spectral create` |
| MCP alias | `kaiten_chart_spectral` |
| Description | Build a Spectral Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/charts/spectral-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `date_from` | `string` | yes | — | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | — | End date (ISO 8601) |
| `tags` | `array` | no | — | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | — | Filter by card type IDs |
| `group_by` | `string` | no | — | — | Grouping mode |
| `start_columns` | `array` | yes | — | — | Start column IDs (required) |
| `end_columns` | `array` | yes | — | — | End column IDs (required) |
| `start_column_lanes` | `object` | yes | — | — | Mapping of start column ID to array of lane IDs, e.g. {"10": [1, 2]} |
| `end_column_lanes` | `object` | yes | — | — | Mapping of end column ID to array of lane IDs, e.g. {"20": [3, 4]} |

**Examples**

- Build a Spectral Chart for a space.: `kaiten --json charts spectral create`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.
- This request can create a transient compute job, so global read-only mode blocks it.

### `charts.summary.get`

| Field | Value |
|---|---|
| CLI command | `kaiten charts summary get` |
| MCP alias | `kaiten_chart_summary` |
| Description | Get done-card summary for a space within a date range. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/charts/summary` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `date_from` | `string` | yes | — | — | Start date (ISO 8601) |
| `date_to` | `string` | yes | — | — | End date (ISO 8601) |
| `done_columns` | `array` | yes | — | — | Array of done column IDs |

**Examples**

- Get a done-card summary.: `kaiten --json charts summary get --space-id 1 --date-from 2026-01-01 --date-to 2026-01-31 --done-columns '[10,11]'`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.
- This is a read-only analytics request even though the Kaiten API uses POST to submit filters.

### `charts.task-distribution.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts task-distribution create` |
| MCP alias | `kaiten_chart_task_distribution` |
| Description | Build a Task Distribution Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/charts/task-distribution-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `timezone` | `string` | no | — | — | Timezone name (e.g. Europe/Moscow) |
| `includeArchivedCards` | `boolean` | no | — | — | Include archived cards |
| `only_asap_cards` | `boolean` | no | — | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | — | Filter by card type IDs |
| `itemsFilter` | `object` | no | — | — | Additional filter object for items |

**Examples**

- Build a Task Distribution Chart for a space.: `kaiten --json charts task-distribution create`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.
- This request can create a transient compute job, so global read-only mode blocks it.

### `charts.throughput-capacity.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts throughput-capacity create` |
| MCP alias | `kaiten_chart_throughput_capacity` |
| Description | Build a Throughput Capacity Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/charts/throughput-capacity-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `date_from` | `string` | yes | — | — | Start date (ISO 8601) |
| `date_to` | `string` | no | — | — | End date (ISO 8601) |
| `tags` | `array` | no | — | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | — | Filter by card type IDs |
| `group_by` | `string` | no | — | — | Grouping mode |
| `end_column` | `integer` | yes | — | — | End (done) column ID |

**Examples**

- Build a Throughput Capacity Chart for a space.: `kaiten --json charts throughput-capacity create`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.
- This request can create a transient compute job, so global read-only mode blocks it.

### `charts.throughput-demand.create`

| Field | Value |
|---|---|
| CLI command | `kaiten charts throughput-demand create` |
| MCP alias | `kaiten_chart_throughput_demand` |
| Description | Build a Throughput Demand Chart for a space. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/charts/throughput-demand-chart` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `space_id` | `integer` | yes | — | — | Space ID |
| `date_from` | `string` | yes | — | — | Start date (ISO 8601) |
| `date_to` | `string` | no | — | — | End date (ISO 8601) |
| `tags` | `array` | no | — | — | Filter by tag IDs |
| `only_asap_cards` | `boolean` | no | — | — | Include only ASAP (expedite) cards |
| `card_types` | `array` | no | — | — | Filter by card type IDs |
| `group_by` | `string` | no | — | — | Grouping mode |
| `start_column` | `integer` | yes | — | — | Start (input) column ID |

**Examples**

- Build a Throughput Demand Chart for a space.: `kaiten --json charts throughput-demand create`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- Some tenants return 404 or feature-unavailable responses for chart endpoints even when the CLI surface is present.
- If chart endpoints are unavailable, fall back to cards.list-all, space-activity-all.get, or card-location-history.batch-get instead of probing more chart variants.
- This request can create a transient compute job, so global read-only mode blocks it.

### `compute-jobs.cancel`

| Field | Value |
|---|---|
| CLI command | `kaiten compute-jobs cancel` |
| MCP alias | `kaiten_cancel_compute_job` |
| Description | Cancel a running or queued compute job. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/users/current/compute-jobs/{job_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `job_id` | `integer` | yes | — | — | Compute job ID |

**Examples**

- Cancel a compute job.: `kaiten --json compute-jobs cancel --job-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/users/current/compute-jobs/{job_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `job_id` | `integer` | yes | — | — | Compute job ID |

**Examples**

- Get compute job status.: `kaiten --json compute-jobs get --job-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

<a id="module-tree"></a>
## Дерево сущностей (`tree`) — 9 commands

Entity tree and tree navigation commands.

**Namespace tree**

```text
tree
  get
tree-entities
  list
tree-entities.share
  batch-enable
  batch-get
  disable
  enable
  get
  update
tree.children
  list
```

### `tree-entities.list`

| Field | Value |
|---|---|
| CLI command | `kaiten tree-entities list` |
| MCP alias | `kaiten_list_tree_entities` |
| Description | List tree entities from Kaiten. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/tree-entities` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `query` | `string` | no | — | — | Search query. |
| `limit` | `integer` | no | — | — | Max results. |
| `offset` | `integer` | no | — | — | Pagination offset. |

**Examples**

- List tree entities.: `kaiten --json tree-entities list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `tree-entities.share.batch-enable`

| Field | Value |
|---|---|
| CLI command | `kaiten tree-entities share batch-enable` |
| MCP alias | `kaiten_batch_enable_tree_entity_shares` |
| Description | Idempotently enable public links for explicit tree entity UUIDs. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `aggregated` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/tree-entities/share/batch` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `entity_uids` | `array` | yes | — | — | Explicit tree entity UUIDs to process in input order. |
| `expired_at` | `string|null` | no | — | — | Future ISO-8601 expiration timestamp; pass null to remove expiration. |
| `workers` | `integer` | no | — | — | Parallel workers (default 2, max 6). |

**Examples**

- Publish several entities and return every public link.: `kaiten --json tree-entities share batch-enable --entity-uids '["11111111-1111-4111-8111-111111111111","22222222-2222-4222-8222-222222222222"]' --workers 2`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The share UID returned by Kaiten is converted into a ready-to-use public link at `<profile-origin>/p/<share-uid>`.
- GET works for already published entities and requires read access; enable, update, and disable require the entity share permission.
- Supported tree entity types are spaces, documents, document groups, and story maps.
- This is shared-entity publication, not the legacy document `public` field or knowledge-base public-site publishing.
- Only explicit entity UUIDs are accepted; the command does not publish an inferred query result or subtree.
- The result contains ordered items, per-entity errors, and changed/unchanged counters so partial failures remain visible and reruns stay safe.

### `tree-entities.share.batch-get`

| Field | Value |
|---|---|
| CLI command | `kaiten tree-entities share batch-get` |
| MCP alias | `kaiten_batch_get_tree_entity_shares` |
| Description | Get public sharing states and links for explicit tree entity UUIDs. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `aggregated` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/tree-entities/share/batch` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `entity_uids` | `array` | yes | — | — | Explicit tree entity UUIDs to process in input order. |
| `workers` | `integer` | no | — | — | Parallel workers (default 2, max 6). |

**Examples**

- Get public links for several entities with bounded concurrency.: `kaiten --json tree-entities share batch-get --entity-uids '["11111111-1111-4111-8111-111111111111","22222222-2222-4222-8222-222222222222"]'`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The share UID returned by Kaiten is converted into a ready-to-use public link at `<profile-origin>/p/<share-uid>`.
- GET works for already published entities and requires read access; enable, update, and disable require the entity share permission.
- Supported tree entity types are spaces, documents, document groups, and story maps.
- This is shared-entity publication, not the legacy document `public` field or knowledge-base public-site publishing.
- The command deduplicates UUIDs, preserves first-seen order, and returns per-entity errors without hiding successful links.

### `tree-entities.share.disable`

| Field | Value |
|---|---|
| CLI command | `kaiten tree-entities share disable` |
| MCP alias | `kaiten_disable_tree_entity_share` |
| Description | Idempotently disable a tree entity public link. |
| Method | `DELETE` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/tree-entities/{entity_uid}/share` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `entity_uid` | `string` | yes | — | — | Tree entity UUID for a space, document, document group, or story map. |

**Examples**

- Disable a public link without failing when it is already disabled.: `kaiten --json tree-entities share disable --entity-uid 11111111-1111-4111-8111-111111111111`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The share UID returned by Kaiten is converted into a ready-to-use public link at `<profile-origin>/p/<share-uid>`.
- GET works for already published entities and requires read access; enable, update, and disable require the entity share permission.
- Supported tree entity types are spaces, documents, document groups, and story maps.
- This is shared-entity publication, not the legacy document `public` field or knowledge-base public-site publishing.

### `tree-entities.share.enable`

| Field | Value |
|---|---|
| CLI command | `kaiten tree-entities share enable` |
| MCP alias | `kaiten_enable_tree_entity_share` |
| Description | Idempotently enable a public link for a tree entity. |
| Method | `POST` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/tree-entities/{entity_uid}/share` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `entity_uid` | `string` | yes | — | — | Tree entity UUID for a space, document, document group, or story map. |
| `expired_at` | `string|null` | no | — | — | Future ISO-8601 expiration timestamp; pass null to remove expiration. |

**Examples**

- Enable sharing and return the public link.: `kaiten --json tree-entities share enable --entity-uid 11111111-1111-4111-8111-111111111111`
- Enable sharing with an expiration timestamp.: `kaiten --json tree-entities share enable --entity-uid 11111111-1111-4111-8111-111111111111 --expired-at "2099-01-01T00:00:00Z"`

**Notes**

- Bulk alternative: `tree-entities.share.batch-enable`
- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The share UID returned by Kaiten is converted into a ready-to-use public link at `<profile-origin>/p/<share-uid>`.
- GET works for already published entities and requires read access; enable, update, and disable require the entity share permission.
- Supported tree entity types are spaces, documents, document groups, and story maps.
- This is shared-entity publication, not the legacy document `public` field or knowledge-base public-site publishing.
- Repeated execution is safe: active shares are returned unchanged, while disabled or expired shares are reactivated using the existing share UID.

### `tree-entities.share.get`

| Field | Value |
|---|---|
| CLI command | `kaiten tree-entities share get` |
| MCP alias | `kaiten_get_tree_entity_share` |
| Description | Get the public sharing state and ready-to-use public link for a tree entity. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/tree-entities/{entity_uid}/share` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `entity_uid` | `string` | yes | — | — | Tree entity UUID for a space, document, document group, or story map. |

**Examples**

- Get an existing public link without changing sharing state.: `kaiten --json tree-entities share get --entity-uid 11111111-1111-4111-8111-111111111111`

**Notes**

- Bulk alternative: `tree-entities.share.batch-get`
- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The share UID returned by Kaiten is converted into a ready-to-use public link at `<profile-origin>/p/<share-uid>`.
- GET works for already published entities and requires read access; enable, update, and disable require the entity share permission.
- Supported tree entity types are spaces, documents, document groups, and story maps.
- This is shared-entity publication, not the legacy document `public` field or knowledge-base public-site publishing.

### `tree-entities.share.update`

| Field | Value |
|---|---|
| CLI command | `kaiten tree-entities share update` |
| MCP alias | `kaiten_update_tree_entity_share` |
| Description | Idempotently set or clear a tree entity public-link expiration. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/tree-entities/{entity_uid}/share` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `entity_uid` | `string` | yes | — | — | Tree entity UUID for a space, document, document group, or story map. |
| `expired_at` | `string|null` | yes | — | — | Future ISO-8601 expiration timestamp; pass null to remove expiration. |

**Examples**

- Set a public-link expiration timestamp.: `kaiten --json tree-entities share update --entity-uid 11111111-1111-4111-8111-111111111111 --expired-at "2099-01-01T00:00:00Z"`
- Remove the public-link expiration timestamp.: `kaiten --json tree-entities share update --entity-uid 11111111-1111-4111-8111-111111111111 --expired-at null`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- The share UID returned by Kaiten is converted into a ready-to-use public link at `<profile-origin>/p/<share-uid>`.
- GET works for already published entities and requires read access; enable, update, and disable require the entity share permission.
- Supported tree entity types are spaces, documents, document groups, and story maps.
- This is shared-entity publication, not the legacy document `public` field or knowledge-base public-site publishing.

### `tree.children.list`

| Field | Value |
|---|---|
| CLI command | `kaiten tree children list` |
| MCP alias | `kaiten_list_children` |
| Description | List direct children of an entity in the Kaiten sidebar tree. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `aggregated` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/tree/children` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `parent_entity_uid` | `string` | no | — | — | Parent entity UID. Omit to list root-level entities. |

**Examples**

- List direct tree children.: `kaiten --json tree children list --parent-entity-uid root-1`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This aggregated command builds its local catalog from `/spaces`, `/documents`, and `/document-groups`.
- Here `catalog` means an internal fetched entity index for tree assembly, not UI catalog tables (`custom-directories`) and not `custom-properties catalog-values`.
- Use `document-groups.*` to create, update, or delete document folder containers; tree commands are read-only aggregate views.
- `/spaces`, `/documents`, and `/document-groups` are paginated internally with `limit=100` and `offset=0,100,...` until a short page is returned.
- No pagination options are required or accepted for this command; callers control only `parent_entity_uid` for children listing or `root_uid`/`depth` for nested tree output.
- If the internal pagination safety cap is reached with full pages, the command fails instead of returning a silently truncated tree.
- Visible entities whose `parent_entity_uid` is missing or inaccessible in the fetched catalog are promoted to root-level output.

### `tree.get`

| Field | Value |
|---|---|
| CLI command | `kaiten tree get` |
| MCP alias | `kaiten_get_tree` |
| Description | Build a nested entity tree from the Kaiten sidebar. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `aggregated` |
| Cache policy | `persistent_heavy` |
| Cache strategy | `heavy_persistent` |
| Path template | `/tree` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `root_uid` | `string` | no | — | — | Start tree from this entity UID. Omit for full tree from roots. |
| `depth` | `integer` | no | — | — | Max recursion depth (0 = unlimited). Default: 0. |

**Examples**

- Build a bounded entity tree.: `kaiten --json tree get --depth 1`

**Notes**

- Cache guidance: Default auto mode stores this expensive read path in persistent cache with a long adaptive TTL, especially for closed historical windows and repeated analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once when the same heavy window must be rebuilt from Kaiten API; do not put refresh inside a loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- This aggregated command builds its local catalog from `/spaces`, `/documents`, and `/document-groups`.
- Here `catalog` means an internal fetched entity index for tree assembly, not UI catalog tables (`custom-directories`) and not `custom-properties catalog-values`.
- Use `document-groups.*` to create, update, or delete document folder containers; tree commands are read-only aggregate views.
- `/spaces`, `/documents`, and `/document-groups` are paginated internally with `limit=100` and `offset=0,100,...` until a short page is returned.
- No pagination options are required or accepted for this command; callers control only `parent_entity_uid` for children listing or `root_uid`/`depth` for nested tree output.
- If the internal pagination safety cap is reached with full pages, the command fails instead of returning a silently truncated tree.
- Visible entities whose `parent_entity_uid` is missing or inaccessible in the fetched catalog are promoted to root-level output.

<a id="module-utilities"></a>
## Утилиты (`utilities`) — 15 commands

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
  socket-token
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/api-keys` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Name for the API key |

**Examples**

- Create an API key.: `kaiten --json api-keys create --name "local-dev"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/api-keys/{key_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `key_id` | `integer` | yes | — | — | API key ID |

**Examples**

- Delete an API key.: `kaiten --json api-keys delete --key-id 1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/api-keys` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- List API keys.: `kaiten --json api-keys list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `calendars.get`

| Field | Value |
|---|---|
| CLI command | `kaiten calendars get` |
| MCP alias | `kaiten_get_calendar` |
| Description | Get a specific calendar by ID. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/calendars/{calendar_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `calendar_id` | `string` | yes | — | — | Calendar ID (UUID) |

**Examples**

- Get a calendar by ID.: `kaiten --json calendars get --calendar-id cal-1`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `calendars.list`

| Field | Value |
|---|---|
| CLI command | `kaiten calendars list` |
| MCP alias | `kaiten_list_calendars` |
| Description | List calendars. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/calendars` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- List calendars.: `kaiten --json calendars list --limit 5`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `company.current`

| Field | Value |
|---|---|
| CLI command | `kaiten company current` |
| MCP alias | `kaiten_get_company` |
| Description | Get current company information. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/companies/current` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- Get current company information.: `kaiten --json company current`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `company.socket-token`

| Field | Value |
|---|---|
| CLI command | `kaiten company socket-token` |
| MCP alias | `kaiten_get_company_socket_token` |
| Description | Get a websocket JWT for the current user. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/token-please` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- Get a websocket JWT.: `kaiten --json company socket-token`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `company.update`

| Field | Value |
|---|---|
| CLI command | `kaiten company update` |
| MCP alias | `kaiten_update_company` |
| Description | Update current company information. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/companies/current` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | no | — | — | Company name |

**Examples**

- Update current company information.: `kaiten --json company update --name "Acme"`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `removed-boards.list`

| Field | Value |
|---|---|
| CLI command | `kaiten removed-boards list` |
| MCP alias | `kaiten_list_removed_boards` |
| Description | List removed boards from the recycle bin. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/removed/boards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- List removed boards.: `kaiten --json removed-boards list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/removed/cards` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `limit` | `integer` | no | — | — | Max results |
| `offset` | `integer` | no | — | — | Pagination offset |

**Examples**

- List removed cards.: `kaiten --json removed-cards list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/user-timers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `card_id` | `integer` | yes | — | — | Card ID to start timer for |

**Examples**

- Create a user timer.: `kaiten --json user-timers create --card-id 10`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/user-timers/{timer_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `timer_id` | `integer` | yes | — | — | Timer ID |

**Examples**

- Delete a user timer.: `kaiten --json user-timers delete --timer-id 10`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `persistent_opt_in` |
| Cache strategy | `entity_or_reference_persistent` |
| Path template | `/user-timers/{timer_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `timer_id` | `integer` | yes | — | — | Timer ID |

**Examples**

- Get a user timer.: `kaiten --json user-timers get --timer-id 10`

**Notes**

- Cache guidance: Default auto mode reuses persistent cache for repeated safe entity/reference reads and extends dense same-family loops.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: Use --cache-mode refresh once to force a fresh API read and rewrite the cache; do not put refresh inside an entity loop.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `direct_http` |
| Cache policy | `request_scope` |
| Cache strategy | `request_scope` |
| Path template | `/user-timers` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- List user timers.: `kaiten --json user-timers list`

**Notes**

- Cache guidance: Identical safe GETs are deduplicated inside one CLI execution; use bulk/snapshot tools for repeated cross-process analytics.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No disk cache is read by default for this command.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `no` |
| Remote side effects | `yes` |
| Execution mode | `direct_http` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/user-timers/{timer_id}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `timer_id` | `integer` | yes | — | — | Timer ID |
| `paused` | `boolean` | no | — | — | Whether the timer is paused |

**Examples**

- Pause a user timer.: `kaiten --json user-timers update --timer-id 10 --paused`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/local/snapshots/{name}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Stable snapshot name. |
| `space_id` | `integer` | yes | — | — | Source space ID. |
| `board_ids` | `array` | no | — | — | Optional board IDs to keep inside the snapshot. |
| `preset` | `string` | no | `basic`, `analytics`, `evidence`, `full` | — | Snapshot scope preset. |
| `window_start` | `string` | no | — | — | Window start timestamp for analytics/full snapshots. |
| `window_end` | `string` | no | — | — | Window end timestamp for analytics/full snapshots. |

**Examples**

- Build a reusable local snapshot with topology and cards.: `kaiten --json snapshot build --name team-basic --space-id 10 --preset basic`
- Build an analytics snapshot with bounded activity and history data.: `kaiten --json snapshot build --name team-q1 --space-id 10 --preset analytics --window-start 2026-01-01T00:00:00Z --window-end 2026-03-31T23:59:59Z`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/local/snapshots/{name}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Snapshot name. |

**Examples**

- Delete a local snapshot.: `kaiten --json snapshot delete --name team-q1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `snapshot.list`

| Field | Value |
|---|---|
| CLI command | `kaiten snapshot list` |
| MCP alias | `kaiten_snapshot_list` |
| Description | List locally stored snapshots with schema version and dataset counts. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/local/snapshots` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

_No tool-specific arguments._

**Examples**

- Show available local snapshots.: `kaiten --json snapshot list`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

### `snapshot.refresh`

| Field | Value |
|---|---|
| CLI command | `kaiten snapshot refresh` |
| MCP alias | `kaiten_snapshot_refresh` |
| Description | Rebuild an existing local snapshot in place using its stored snapshot definition. |
| Method | `PATCH` |
| Mutation | `yes` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/local/snapshots/{name}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `yes` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Snapshot name to rebuild. |

**Examples**

- Refresh a previously built snapshot.: `kaiten --json snapshot refresh --name team-q1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- refresh reuses the stored snapshot spec and rebuilds datasets in place; v1 is rebuild-oriented, not incremental.
- refresh clears the current profile/domain HTTP cache first so the rebuilt snapshot comes from fresh Kaiten API reads.

### `snapshot.show`

| Field | Value |
|---|---|
| CLI command | `kaiten snapshot show` |
| MCP alias | `kaiten_snapshot_show` |
| Description | Show local snapshot metadata, schema version, dataset counts, and the last build trace summary. |
| Method | `GET` |
| Mutation | `no` |
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/local/snapshots/{name}` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `name` | `string` | yes | — | — | Snapshot name. |

**Examples**

- Inspect snapshot metadata and dataset counts.: `kaiten --json snapshot show --name team-q1`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.

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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/local/query/cards` |
| Compact | `yes` |
| Fields | `yes` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `snapshot` | `string` | yes | — | — | Snapshot name. |
| `filter` | `object` | no | — | — | Local filter object for card selection. |
| `view` | `string` | no | `summary`, `detail`, `evidence` | — | Local output view. summary is the default and keeps payloads narrow for repeated analytics and LLM workflows. |
| `fields` | `string` | no | — | — | Comma-separated card or derived field names to keep. |
| `limit` | `integer` | no | — | — | Max returned rows. Default 100. |
| `offset` | `integer` | no | — | — | Pagination offset. |
| `compact` | `boolean` | no | — | — | Return a compact card response. |

**Examples**

- Filter cards locally by board and derived flags in summary view.: `kaiten --json query cards --snapshot team-basic --filter '{"board_ids":[10],"has_children":true}' --fields id,title,has_children`
- Search local evidence text without extra API calls.: `kaiten --json query cards --snapshot team-basic --view evidence --filter '{"comment_text_query":"blocked"}' --compact --fields id,title,comment_text`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
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
| Allowed in read-only mode | `yes` |
| Remote side effects | `no` |
| Execution mode | `custom` |
| Cache policy | `none` |
| Cache strategy | `none` |
| Path template | `/local/query/metrics` |
| Compact | `no` |
| Fields | `no` |
| Heavy | `no` |

**Arguments**

| Argument | Type | Required | Enum | Constraints | Description |
|---|---|---|---|---|---|
| `snapshot` | `string` | yes | — | — | Snapshot name. |
| `metric` | `string` | yes | `count`, `wip`, `throughput`, `lead_time`, `cycle_time`, `aging` | — | Metric to compute locally. |
| `filter` | `object` | no | — | — | Optional local filter object applied before metrics. |
| `group_by` | `string|null` | no | `board_id`, `column_id`, `lane_id`, `type_id`, `owner_id`, `responsible_id`, `state`, `condition`, `None` | — | Optional grouping field. |

**Examples**

- Compute throughput locally over the snapshot window.: `kaiten --json query metrics --snapshot team-q1 --metric throughput --group-by board_id`
- Compute local WIP aging for a reduced candidate set.: `kaiten --json query metrics --snapshot team-basic --metric aging --filter '{"board_ids":[10],"has_comments":true}' --group-by column_id`

**Notes**

- Cache guidance: This command does not use persistent cache; use it for mutations, polling, downloads, or local-only reads.
- Cache modes: `auto`, `off`, `readwrite`, `refresh`; default/recommended: `auto`.
- Refresh hint: No cache refresh is needed.
- Off hint: Use --cache-mode off only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Readwrite hint: Use --cache-mode readwrite with an explicit --cache-ttl-seconds value when a fixed TTL is required.
- throughput, lead_time, and cycle_time use the snapshot window when it exists; basic snapshots fall back to all locally known done transitions.
- For repeated report generation, query metrics after snapshot build instead of re-fetching topology, cards, and history on every run.
