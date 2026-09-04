# kaiten-cli for Agents

This file only captures agent-specific guidance.

For install, human-oriented usage, and the full docs map, start with [README.md](README.md).  
For the full command catalog, use [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md).  
For the system map, use [ARCHITECTURE.md](ARCHITECTURE.md).
For optimized LLM workflows, start with:

- [skills/kaiten-cli-heavy-data/SKILL.md](skills/kaiten-cli-heavy-data/SKILL.md)
- [skills/kaiten-cli-metrics/SKILL.md](skills/kaiten-cli-metrics/SKILL.md)
- [skills/kaiten-cli-mutations/SKILL.md](skills/kaiten-cli-mutations/SKILL.md)

## Discovery-first flow

Prefer this sequence before calling mutations or heavy commands:

```bash
kaiten --help
kaiten search-tools cards
kaiten describe cards.list
kaiten examples cards.list
```

Run discovery once per unfamiliar command family, mutation workflow, or heavy
read. Reuse the discovered contract inside the same workflow instead of
repeating `describe` before every call.

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
kaiten profile add main --domain <company-subdomain-or-url> --token <api-token> --set-active
```

## Safety and efficiency

- Start with read-only commands.
- Normal profiles can mutate; treat real credentials as real writes.
- For analysis-only workflows, use global `--read-only` or `KAITEN_CLI_READ_ONLY=1`; this blocks remote mutations while allowing local snapshot lifecycle operations and the POST-backed chart retrieval commands reported with `read_only_allowed=true`.
- `KAITEN_LIVE=1|true` is the explicit per-run gate for the live test suite.
- `profile add --sandbox` is deprecated compatibility metadata and does not affect mutations or live-test gating.
- Prefer `--compact` and `--fields` to reduce payload and token cost.
- Request-scoped cache for safe GETs is built in; default `--cache-mode auto` also persists cacheable safe reads across CLI processes.
- Omit `--cache-mode` for ordinary workflows: this keeps the default `auto`.
- Use `--cache-mode refresh` once at a freshness boundary; never put it inside an entity loop. For a reused local working set, prefer `snapshot refresh`.
- Use `--cache-mode off` only for cache debugging, privacy-sensitive reads, or high-churn polling.
- Use `--cache-mode readwrite` only with an explicit, meaningful `--cache-ttl-seconds` when a fixed TTL is required.
- Heavy/batch reads and dense repeated entity reads get longer adaptive TTLs in `auto`; do not force tiny TTLs in wrapper scripts unless freshness is the main requirement.
- JSON responses include top-level `stats`; check `http_request_count`, `api_wait_ms`, cache counters, and grouped path families before repeating expensive calls.
- Use `--verbose` when you need request-path and execution diagnostics; diagnostics stay in `stderr`.
- Use `--trace-file` or `KAITEN_TRACE_FILE` when you need a JSONL trace of real command cost across a longer workflow.
- Trace is required for wrappers with at least three CLI commands, expected runs above ten HTTP requests, or unavoidable loops. Review it with `kaiten --json trace summarize --file <trace.jsonl>`.
- Treat `aggregated` and `synthetic` tools as potentially more expensive than `direct_http`.
- For high-cardinality reads, follow the heavy-data skill instead of inventing a per-entity loop.
- For metrics workflows, follow the metrics skill instead of reconstructing raw history one card at a time.
- For repeated report or analytics questions on one working set, prefer `snapshot build` plus `query cards` / `query metrics` over re-fetching the same population.
- Keep `query cards` in `summary` view by default; use `detail` or `evidence` only after local candidate reduction.
- Treat `query metrics` as a generic local metrics layer unless a workflow explicitly defines tenant-specific flow semantics outside the CLI.
- Prefer `space-topology.get`, `cards.batch-get`, `time-logs.batch-list`, `space-activity-all.get`, `card-children.batch-list`, `comments.batch-list`, and `card-location-history.batch-get` over manual orchestration loops.
- When two or more entity IDs are known and `describe` reports `bulk_alternative`, use the bulk command.
- When the same population is needed a second time, build a snapshot and continue with local `query cards` / `query metrics`.
- Before a live mutation, use `kaiten --json --profile <name> --read-only profile probe`, then follow the mutation skill: discovery, read-only investigation, exact preview, authorization, resumable manifest, small batches, and field-scoped readback.
- Addon state lives outside the normal card fields: use `card-addon-data` / `user-addon-data` for raw addon storage, and the `github-addon` commands for PRs, branches, commits and issues shown on a card.
- Attaching a PR to a card usually means the GitHub addon, not `external-links create`; check both sources when looking for every PR a card references.
- The GitHub addon UUID is derived from its mount path only on on-premises Kaiten; elsewhere it is random. `addons uid` returns the derived guess, `space-addons list` and `company-addons list` return the real one, and the `github-addon` commands re-resolve it from the card's space when the guess finds no data.
- Live validation is opt-in and documented in [LIVE_VALIDATION.md](LIVE_VALIDATION.md).
