# Architecture

`kaiten-cli` is organized around one core idea: the tool surface is declared once, in the registry, and every other layer consumes that metadata.

## System Map

Runtime flow:

`registry -> discovery/app -> input merge -> executor -> client -> transforms/output`

For high-cardinality reads there is one more path:

`registry -> discovery/app -> input merge -> executor -> execution context -> runtime behavior -> bulk worker pool -> per-worker clients`

Main layers:

- `src/kaiten_cli/registry/`
  Source of truth for the command catalog. Each tool is declared as a `ToolSpec` with canonical name, MCP alias, schema, examples, request metadata, response policy, and optional runtime behavior.
- `src/kaiten_cli/runtime/`
  Execution layer. Builds requests, resolves profiles and cache settings, applies sandbox safety rules, runs HTTP calls, handles synthetic and aggregated reads, and shapes responses.
- `src/kaiten_cli/runtime/support/`
  Domain-specific helpers used by runtime behaviors for documents, projects, tree aggregation, cards bulk pagination, relation/comment batch reads, activity pagination, and space topology aggregation.
- top-level `src/kaiten_cli/`
  Stable package surface and shared core: `app.py`, `discovery.py`, `profiles.py`, `models.py`, `errors.py`, entrypoints.

## Registry vs Runtime

This repo does not have two different sets of tools.

- `registry` defines the tools.
- `runtime` executes the tools.

If a command looks “special”, it is still a registry-defined tool. The only difference is that its `ToolSpec.runtime_behavior` points to a request shaper or custom executor in `src/kaiten_cli/runtime/behaviors.py`.

That means:

- `cards.list` is a registry tool with direct HTTP execution
- `projects.cards.list` is a registry tool with synthetic execution
- `cards.list-all` is a registry tool with aggregated execution

The command catalog stays centralized even when runtime semantics differ.

## Execution Context and Cache

Each CLI invocation builds one execution context for the selected profile.

- request-scoped cache is always enabled for safe GET reads
- identical in-flight GETs are deduplicated inside the same execution context
- persistent disk cache is opt-in through `--cache-mode` or profile defaults
- successful mutations clear persistent cache for the current profile/domain scope
- optional JSONL trace output can be appended through `--trace-file` or `KAITEN_TRACE_FILE`

This keeps the default one-shot CLI behavior intact, while reducing repeated entity reads in synthetic, aggregated, and worker-pooled paths.

The trace layer records command-level facts such as duration, real HTTP request count, retry/cache counters, and bulk metadata. It exists because outer Codex/session logs do not reliably see internal Kaiten subprocess calls from higher-level scripts.

## Execution Modes

- `direct_http`
  One request derived directly from `OperationSpec`.
- `synthetic`
  Runtime may use fallback logic or reshape API responses to preserve a stable tool contract.
- `aggregated`
  Runtime performs bounded multi-request collection and returns one logical result.
- `custom`
  Runtime uses a dedicated executor because the API contract does not map cleanly to a simple request/response flow.

Bulk reads are still registry-defined tools. The difference is that some aggregated tools now use a dedicated bulk execution path instead of repeated one-shot CLI invocations. Current examples include `cards.list-all`, `space-activity-all.get`, `space-topology.get`, `card-children.batch-list`, `comments.batch-list`, and `card-location-history.batch-get`.

## Docs Map

Primary docs:

- [README.md](README.md) for install, usage, config, and operator guidance
- [AGENTS.md](AGENTS.md) for agent-specific usage and safety shortcuts
- `skills/` for repo-local LLM workflows in `SKILL.md` format
- [LIVE_VALIDATION.md](LIVE_VALIDATION.md) for live test process
- [API_BEHAVIOR_MATRIX.md](API_BEHAVIOR_MATRIX.md) for documented sandbox contracts
- `ARCHITECTURE.md` for the system map

Historical artifacts:

- [docs/archive/](docs/archive/README.md)

`ARCHITECTURE_REVIEW.md` is intentionally kept out of tracked docs. It is an audit artifact, not the maintained architecture reference.

## Known Tradeoffs

- The manual registry is easy to inspect, but large and maintenance-heavy.
- Runtime behaviors are now explicit, but still centralized in one behavior module.
- Request-scoped cache is built in, but persistent cache deliberately stays conservative and opt-in.
- The CLI favors boundedness and predictability over maximum raw throughput, so bulk execution stays conservative by default.
- Live validation is explicit and well-documented, but sandbox contracts remain inherently unstable.
