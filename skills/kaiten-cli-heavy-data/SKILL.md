---
name: kaiten-cli-heavy-data
description: Use when working with large Kaiten reads, exports, audits, or repeated entity fetches through kaiten-cli. Helps choose bulk commands, response shaping, and cache mode to avoid N+1 process and API paths.
---

# kaiten-cli heavy data

Use this skill when the task smells like bulk reads, exports, audits, migrations, cross-board scans, or repeated card/history fetches.

## Core rules

- Start with discovery: `kaiten search-tools ...` and `kaiten describe ...`.
- Prefer one bulk CLI call over many one-shot CLI processes.
- Treat `aggregated` and `synthetic` tools as more expensive than `direct_http`.
- Reduce response size before asking the LLM to inspect it.

## Anti-patterns

- Do not spawn `kaiten` once per card when a bulk tool exists.
- Do not fetch full card objects for metrics or audits if `--fields` is enough.
- Do not repeat identical safe GET reads across multiple CLI calls without considering cache.
- Do not assume `cards.list` is the right bulk path; check `cards.list-all`.

## Preferred command choices

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

## Quick decision rule

- Need many cards: `cards list-all`
- Need many card histories: `card-location-history batch-get`
- Need one entity many times across multiple CLI calls: enable `--cache-mode readwrite`
- Need to understand the path first: `describe <tool>`
