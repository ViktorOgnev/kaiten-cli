---
name: kaiten-cli-metrics
description: Use when collecting Kanban metrics or operational analytics through kaiten-cli. Helps choose between bulk cards, history, activity, and chart paths without falling into per-card loops.
---

# kaiten-cli metrics

Use this skill for lead time, cycle time, throughput, WIP, due-date performance, audit snapshots, and similar Kanban analytics.

## Source selection

- Prefer `cards list-all` when the metric can be computed from card fields.
- Use `card-location-history batch-get` only when the metric truly needs per-card movement history.
- Use chart tools when Kaiten already computes the metric server-side.

## Default workflow

### 1. Inspect the command surface

```bash
kaiten search-tools "lead time cards"
kaiten describe cards.list-all
kaiten describe card-location-history.batch-get
```

### 2. Start with bulk cards

For most metrics, begin with:

```bash
kaiten --json cards list-all \
  --board-id 10 \
  --selection all \
  --fields id,title,created,first_moved_to_in_progress_at,last_moved_to_done_at,state,condition,due_date,time_spent_sum,time_blocked_sum \
  --compact
```

Use `active_only` for WIP-oriented reads and `archived_only` for completion-oriented reads.

### 3. Escalate only if card fields are not enough

If the metric depends on detailed movement history:

```bash
kaiten --json card-location-history batch-get \
  --card-ids '[101,102,103]' \
  --workers 2 \
  --fields changed,column_id,subcolumn_id
```

## Anti-patterns

- Do not compute metrics by calling `card-location-history get` once per card.
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

## Quick decision rule

- WIP, throughput, lead/cycle time from card timestamps: `cards list-all`
- Per-column movement reconstruction: `card-location-history batch-get`
- Precomputed analytics: chart tools + `compute-jobs get`
