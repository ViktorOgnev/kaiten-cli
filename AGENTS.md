# kaiten-cli for Agents

This file only captures agent-specific guidance.

For install, human-oriented usage, and the full docs map, start with [README.md](README.md).  
For the full command catalog, use [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md).  
For the system map, use [ARCHITECTURE.md](ARCHITECTURE.md).
For optimized LLM workflows, start with:

- [skills/kaiten-cli-heavy-data/SKILL.md](skills/kaiten-cli-heavy-data/SKILL.md)
- [skills/kaiten-cli-metrics/SKILL.md](skills/kaiten-cli-metrics/SKILL.md)

## Discovery-first flow

Prefer this sequence before calling mutations or heavy commands:

```bash
kaiten --help
kaiten search-tools cards
kaiten describe cards.list
kaiten examples cards.list
```

Use `--json` by default for machine-safe parsing:

```bash
kaiten --json spaces list --compact --fields id,title
```

If the workflow will ask many questions about the same space or board set, switch early to the local-first path:

```bash
kaiten --json snapshot build --name team-basic --space-id 10 --preset basic
kaiten --json query cards --snapshot team-basic --view summary --fields id,title,state
```

## Config and precedence

Credential resolution order:

1. `--profile <name>`
2. active profile from config
3. `KAITEN_DOMAIN` + `KAITEN_TOKEN`

Recommended persistent setup:

```bash
kaiten profile add main --domain <company-subdomain> --token <api-token> --set-active
```

## Safety and efficiency

- Start with read-only commands.
- Normal profiles can mutate; treat real credentials as real writes.
- `KAITEN_LIVE=1|true` is the explicit per-run gate for the live test suite.
- `profile add --sandbox` is deprecated compatibility metadata and does not affect mutations or live-test gating.
- Prefer `--compact` and `--fields` to reduce payload and token cost.
- Request-scoped cache for safe GETs is built in; enable `--cache-mode readwrite` only when you want short-lived cross-process reuse.
- Use `--verbose` when you need request-path and execution diagnostics; diagnostics stay in `stderr`.
- Use `--trace-file` or `KAITEN_TRACE_FILE` when you need a JSONL trace of real command cost across a longer workflow.
- Treat `aggregated` and `synthetic` tools as potentially more expensive than `direct_http`.
- For high-cardinality reads, follow the heavy-data skill instead of inventing a per-entity loop.
- For metrics workflows, follow the metrics skill instead of reconstructing raw history one card at a time.
- For repeated report or analytics questions on one working set, prefer `snapshot build` plus `query cards` / `query metrics` over re-fetching the same population.
- Keep `query cards` in `summary` view by default; use `detail` or `evidence` only after local candidate reduction.
- Treat `query metrics` as a generic local metrics layer unless a workflow explicitly defines tenant-specific flow semantics outside the CLI.
- Prefer `space-topology.get`, `cards.batch-get`, `time-logs.batch-list`, `space-activity-all.get`, `card-children.batch-list`, `comments.batch-list`, and `card-location-history.batch-get` over manual orchestration loops.
- Live validation is opt-in and documented in [LIVE_VALIDATION.md](LIVE_VALIDATION.md).
