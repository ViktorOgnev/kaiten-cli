---
name: kaiten-cli-metrics
description: Use when collecting Kanban metrics or operational analytics through kaiten-cli. Helps choose between bulk cards, history, activity, and chart paths without falling into per-card loops.
---

# kaiten-cli metrics

Use this skill for lead time, cycle time, throughput, WIP, due-date performance, audit snapshots, and similar Kanban analytics.

## Source selection

- Prefer `cards list-all` when the metric can be computed from card fields.
- Prefer `snapshot build` plus `query metrics` when the same metric space will be queried repeatedly.
- Keep local card inspection in `query cards --view summary` by default; only escalate to `detail` or `evidence` for narrowed candidates.
- Prefer `space-topology get` to resolve board/column/lane structure before collecting metric data.
- Prefer `space-activity-all get` over manual offset loops around `space-activity get`.
- Use `card-location-history batch-get` only when the metric truly needs per-card movement history.
- Use `time-logs batch-list` when the metric truly depends on per-card work logs.
- Use chart tools when Kaiten already computes the metric server-side.

## Default workflow

### 1. Inspect the command surface

```bash
kaiten search-tools "lead time cards"
kaiten describe space-topology.get
kaiten describe cards.list-all
kaiten describe card-location-history.batch-get
```

### 2. If the workflow repeats, snapshot first

For repeated report generation or headless analytics:

```bash
kaiten --json snapshot build \
  --name team-q1 \
  --space-id 10 \
  --preset analytics \
  --window-start 2026-01-01T00:00:00Z \
  --window-end 2026-03-31T23:59:59Z

kaiten --json query metrics --snapshot team-q1 --metric throughput --group-by board_id
```

`query metrics` is local-only after the snapshot is built.
Its semantics are intentionally generic in this phase; tenant-specific flow profiles should be layered on top later rather than guessed automatically.
`analytics` snapshots now include local time-log data, so repeated work-log questions should stay on the snapshot/query path.

### 3. Start with bulk cards when a snapshot is too expensive or unnecessary

For most metrics, begin with:

```bash
kaiten --json cards list-all \
  --board-id 10 \
  --selection all \
  --fields id,title,created,first_moved_to_in_progress_at,last_moved_to_done_at,state,condition,due_date,time_spent_sum,time_blocked_sum \
  --compact
```

Use `active_only` for WIP-oriented reads and `archived_only` for completion-oriented reads.

### 4. Escalate only if card fields are not enough

If the metric depends on detailed movement history:

```bash
kaiten --json card-location-history batch-get \
  --card-ids '[101,102,103]' \
  --workers 2 \
  --fields changed,column_id,subcolumn_id
```

If the metric depends on relation or comment evidence across many cards:

```bash
kaiten --json card-children batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,title
kaiten --json comments batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,text
```

If the metric depends on work logs or you need detail enrichment for a narrowed candidate set:

```bash
kaiten --json time-logs batch-list --card-ids '[101,102,103]' --workers 2 --fields id,time_spent,for_date
kaiten --json cards batch-get --card-ids '[101,102,103]' --workers 2 --fields id,title,description
```

## Anti-patterns

- Do not compute metrics by calling `card-location-history get` once per card.
- Do not compute evidence-based metrics by looping over `card-children list` or `comments list`.
- Do not fetch full card payloads if timing fields are enough.
- Do not build a shell loop of repeated `kaiten cards get` when `cards list-all` already gives the population.
- Do not ignore `describe` metadata; check `execution_mode`, `bulk_alternative`, and `cache_policy`.

## Cache guidance for metrics workflows

- Same-process repeats are already covered by request-scoped cache.
- For multi-step scripts that invoke `kaiten` many times, enable short-lived persistent cache on reference/entity reads.
- Use `refresh` before a final report if data freshness is critical.

Examples:

```bash
kaiten --json --cache-mode readwrite boards list --compact --fields id,title
kaiten --json --cache-mode readwrite columns list --board-id 10 --compact --fields id,title
```

## When to use charts

Prefer chart endpoints when you need precomputed analytics instead of reconstructing them client-side:

- CFD
- control chart
- lead time chart
- cycle time chart
- throughput charts

Use chart submission plus `compute-jobs get` polling only for the chart result itself. Do not expect `compute-jobs get` to benefit from persistent cache.

If the tenant returns `404` or feature-unavailable responses on chart tools, switch early to `cards.list-all`, `space-activity-all.get`, and `card-location-history.batch-get` instead of probing more chart variants.

## Trace for long analytics runs

When a report is orchestrated by a shell or Python wrapper, enable trace output on the expensive CLI steps:

```bash
kaiten --json --trace-file ./kaiten-trace.jsonl card-location-history batch-get --card-ids '[101,102,103]'
```

The trace reveals real HTTP request counts even when the outer agent log only sees the wrapper command.

## Quick decision rule

- WIP, throughput, lead/cycle time from card timestamps: `cards list-all`
- Repeated report or dashboard iterations on one window: `snapshot build` -> `query metrics`
- Need work logs across many cards: `time-logs batch-list`
- Need detail enrichment after local narrowing: `cards batch-get`
- Topology bootstrap: `space-topology get`
- Activity window export: `space-activity-all get`
- Relation/comment evidence across many cards: `card-children batch-list` / `comments batch-list`
- Per-column movement reconstruction: `card-location-history batch-get`
- Precomputed analytics: chart tools + `compute-jobs get`
