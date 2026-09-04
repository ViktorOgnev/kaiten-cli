---
name: kaiten-cli-heavy-data
description: Use when working with large Kaiten reads, exports, audits, or repeated entity fetches through kaiten-cli. Helps choose bulk commands, response shaping, and cache mode to avoid N+1 process and API paths.
---

# kaiten-cli heavy data

Use this skill when the task smells like bulk reads, exports, audits, migrations, cross-board scans, or repeated card/history fetches.

## Core rules

- Start with discovery: `kaiten search-tools ...` and `kaiten describe ...`.
- Prefer one bulk CLI call over many one-shot CLI processes.
- If the workflow will reuse the same population more than once, prefer `snapshot build` once and then local `query cards` / `query metrics`.
- Keep local card reads in `query cards --view summary` by default; switch to `detail` or `evidence` only after narrowing the candidate set.
- Treat `aggregated` and `synthetic` tools as more expensive than `direct_http`.
- Reduce response size before asking the LLM to inspect it.
- When two or more entity IDs are known and `describe` reports a
  `bulk_alternative`, use the bulk command.
- When the same population is needed a second time, build a snapshot and query
  it locally.

## Anti-patterns

- Do not spawn `kaiten` once per card when a bulk tool exists.
- Do not loop over `card-children list` or `comments list` for every card in an investigation.
- Do not fetch full card objects for metrics or audits if `--fields` is enough.
- Do not repeat identical safe GET reads across multiple CLI calls without considering cache.
- Do not assume `cards.list` is the right bulk path; check `cards.list-all`.
- Do not rebuild the same space/board working set from Kaiten API if a local snapshot would answer the next questions.

## Preferred command choices

### Repeated read-heavy workflows

Use:

```bash
kaiten --json snapshot build --name team-basic --space-id 10 --preset basic
kaiten --json query cards --snapshot team-basic --view summary --filter '{"board_ids":[10]}' --fields id,title,state
```

Notes:

- Build the snapshot once when the report, audit, or export will ask several follow-up questions about the same working set.
- `query cards` does not call the Kaiten API.
- `summary` is the default local card view; use `detail` or `evidence` only for narrowed candidates.
- Escalate to `query metrics` when the follow-up questions are mostly aggregate rather than per-card.
- This path is explicit; ordinary transport commands are not silently rewritten to snapshot-backed reads.

### Bulk card population

Use:

```bash
kaiten --json cards list-all --board-id 10 --selection active_only --fields id,title,state --compact
```

Notes:

- `selection=all|active_only|archived_only` is the preferred bulk UX.
- Add `relations none` only when you really need to suppress nested objects at API level.
- `cards.list-all` fails on a full `max_pages` boundary instead of returning a partial population; increase `--max-pages` only after checking the expected size.

### Bulk location history

Use:

```bash
kaiten --json card-location-history batch-get --card-ids '[101,102,103]' --workers 2 --fields changed,column_id,subcolumn_id
```

Notes:

- Prefer this over repeating `card-location-history get`.
- The batch path keeps partial per-card failures in-band.
- Duplicate `card_id` values are deduplicated before network fetch.

### Bulk card details and work logs

Use:

```bash
kaiten --json cards batch-get --card-ids '[101,102,103]' --workers 2 --fields id,title,description
kaiten --json time-logs batch-list --card-ids '[101,102,103]' --workers 2 --fields id,time_spent,for_date
```

Notes:

- Prefer `cards.batch-get` over repeating `cards.get` after local candidate reduction.
- Prefer `time-logs.batch-list` over repeating `time-logs.list` when work-log analytics spans many cards.
- `time-logs.batch-list` paginates each card to completion; tune `--page-size` and `--max-pages` only when the defaults are unsuitable.

### Relation and comment evidence

Use:

```bash
kaiten --json card-children batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,title
kaiten --json comments batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,text
```

Notes:

- Prefer these over per-card `card-children list` and `comments list`.
- Both batch paths keep partial per-card failures in-band.
- Both paginate each card to completion and report a per-card error rather than return a truncated collection at the safety cap.

### Addon attachments across many cards

There is no bulk read for addon data: `card-addon-data get` and
`github-addon ... list` are per-card, one HTTP request each, and `describe`
reports no `bulk_alternative` for them. Narrow the population first, then read
attachments only for the cards that survived:

```bash
kaiten --json query cards --snapshot team-basic --view summary --fields id,title
kaiten --json --trace-file ./kaiten-trace.jsonl github-addon pulls list --card-id 101 --fields number,htmlUrl,state
```

Notes:

- A per-card loop is unavoidable here, so it is exactly the case the tracing rule
  below is written for: record a trace and check the real request count.
- Addon attachments are not part of the card entity and are not stored in a
  snapshot; `cards list-all` and `query cards` never return them.
- A card can also reference a PR through `external-links list`. Read both when the
  question is "every PR this card references".
- Resolve the addon UUID once with `space-addons list` and pass `--addon-uid` in
  the loop: without it every empty card costs two extra lookups while the command
  checks whether the derived UUID was the right one, and a card whose space
  cannot be read fails the whole call rather than reporting an empty list.

### Space topology

Use:

```bash
kaiten --json space-topology get --space-id 10
```

Notes:

- Prefer this over a script that separately calls `boards list`, `columns list`, and `lanes list`.
- Use it at the start of report scaffolding to lock board/column/lane IDs once.

## Response shaping

Default shaping order:

1. `--fields` to keep only needed fields
2. `--compact` to strip heavy fields and simplify user objects
3. `--json` for machine-safe parsing

Example:

```bash
kaiten --json cards get --card-id 123 --compact --fields id,title,state
```

## Cache guidance

Safe GET reads already use request-scoped cache inside one CLI invocation, and the CLI defaults to `--cache-mode auto` for cacheable cross-process reuse.

For heavy LLM/script analytics, keep `auto` unless freshness is critical. Batch and aggregated reads store longer-lived cache chunks, and dense same-family entity loops such as many `/cards/<id>` reads are extended after enough recent writes.

```bash
kaiten --json card-location-history batch-get --card-ids '[101,102,103]' --workers 2 --fields changed,column_id
```

Keep all four modes and choose them deliberately:

- `--cache-mode auto`: default for ordinary, batch, heavy, and agent workflows; omit the
  flag.
- `--cache-mode refresh`: one freshness-critical command that must bypass the saved answer;
  never put it inside an entity loop.
- `--cache-mode off`: cache debugging, privacy-sensitive reads, or high-churn polling.
- `--cache-mode readwrite`: fixed-TTL automation; always pair it with an explicit
  `--cache-ttl-seconds`.

Use `refresh` once when correctness matters more than reuse:

```bash
kaiten --json --cache-mode refresh spaces list --compact --fields id,title
```

For a reused snapshot, prefer `snapshot refresh` once over adding
`--cache-mode refresh` to every source read.

## Diagnostics

When the path looks unexpectedly slow, rerun with:

```bash
kaiten --json --verbose ...
```

Check for:

- `execution_mode`
- `cache_policy`
- `cache: request hit/miss`
- `cache: disk hit/miss/bypass`
- `retry:` messages
- final `stats:` summary with duration, HTTP request count, API wait, and cache hits

Every `--json` response also includes top-level `stats`. Use `stats.http_request_count`, `stats.api_wait_ms`, `stats.cache_hits`, and `stats.groups` before deciding to rerun or widen a heavy query.

For longer workflows, record a command trace:

```bash
kaiten --json --trace-file ./kaiten-trace.jsonl cards list-all --board-id 10 --selection active_only
```

Trace persists the same runtime stats across commands and helps explain real HTTP cost when outer agent logs only show the wrapper script.

Tracing is required when a wrapper runs at least three CLI commands, the
workflow is expected to exceed ten HTTP requests, or an external loop is
unavoidable. Summarize the trace locally:

```bash
kaiten --json trace summarize --file ./kaiten-trace.jsonl
```

## Quick decision rule

- Need many cards: `cards list-all`
- Need many card details for narrowed candidates: `cards batch-get`
- Need many work-log reads: `time-logs batch-list`
- Need many child relations: `card-children batch-list`
- Need many comment reads: `comments batch-list`
- Need one space topology snapshot: `space-topology get`
- Need many card histories: `card-location-history batch-get`
- Need addon attachments for many cards: no bulk path exists; narrow the card set first, then loop with a trace
- Need many follow-up questions on one working set: `snapshot build` -> `query cards` / `query metrics`
- Need one entity many times across multiple CLI calls: keep default `--cache-mode auto`; use `--cache-mode readwrite` only for a fixed TTL
- Need to understand the path first: `describe <tool>`
