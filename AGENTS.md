# kaiten-cli for Agents

This file only captures agent-specific guidance.

For install, human-oriented usage, and the full docs map, start with [README.md](README.md).  
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

## Config and precedence

Credential resolution order:

1. `--profile <name>`
2. active profile from config
3. `KAITEN_DOMAIN` + `KAITEN_TOKEN`

Recommended persistent setup:

```bash
kaiten profile add main --domain <company-subdomain> --token <api-token> --set-active
```

Sandbox setup:

```bash
kaiten profile add sandbox --domain sandbox --token <api-token> --sandbox --set-active
```

## Safety and efficiency

- Start with read-only commands.
- Mutations are blocked unless the selected profile is marked sandbox or uses the `sandbox` domain.
- Prefer `--compact` and `--fields` to reduce payload and token cost.
- Request-scoped cache for safe GETs is built in; enable `--cache-mode readwrite` only when you want short-lived cross-process reuse.
- Use `--verbose` when you need request-path and execution diagnostics; diagnostics stay in `stderr`.
- Use `--trace-file` or `KAITEN_TRACE_FILE` when you need a JSONL trace of real command cost across a longer workflow.
- Treat `aggregated` and `synthetic` tools as potentially more expensive than `direct_http`.
- For high-cardinality reads, follow the heavy-data skill instead of inventing a per-entity loop.
- For metrics workflows, follow the metrics skill instead of reconstructing raw history one card at a time.
- Prefer `space-topology.get`, `space-activity-all.get`, `card-children.batch-list`, `comments.batch-list`, and `card-location-history.batch-get` over manual orchestration loops.
- Live validation is opt-in and documented in [LIVE_VALIDATION.md](LIVE_VALIDATION.md).
