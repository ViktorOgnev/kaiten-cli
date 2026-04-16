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

### Relation and comment evidence

Use:

```bash
kaiten --json card-children batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,title
kaiten --json comments batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,text
```

Notes:

- Prefer these over per-card `card-children list` and `comments list`.
- Both batch paths keep partial per-card failures in-band.

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

Safe GET reads already use request-scoped cache inside one CLI invocation.

Enable persistent cache only when the workflow repeatedly launches separate CLI processes for the same safe reads:

```bash
kaiten --json --cache-mode readwrite --cache-ttl-seconds 60 cards get --card-id 123
```

Use `refresh` when correctness matters more than reuse:

```bash
kaiten --json --cache-mode refresh spaces list --compact --fields id,title
```

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

For longer workflows, record a command trace:

```bash
kaiten --json --trace-file ./kaiten-trace.jsonl cards list-all --board-id 10 --selection active_only
```

Trace helps explain real HTTP cost when outer agent logs only show the wrapper script.

## Quick decision rule

- Need many cards: `cards list-all`
- Need many card details for narrowed candidates: `cards batch-get`
- Need many work-log reads: `time-logs batch-list`
- Need many child relations: `card-children batch-list`
- Need many comment reads: `comments batch-list`
- Need one space topology snapshot: `space-topology get`
- Need many card histories: `card-location-history batch-get`
- Need many follow-up questions on one working set: `snapshot build` -> `query cards` / `query metrics`
- Need one entity many times across multiple CLI calls: enable `--cache-mode readwrite`
- Need to understand the path first: `describe <tool>`
