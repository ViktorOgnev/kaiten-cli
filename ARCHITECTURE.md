# Architecture

`kaiten-cli` is organized around one core idea: the tool surface is declared once, in the registry, and every other layer consumes that metadata.

## System Map

Runtime flow:

`registry -> discovery/app -> input merge -> executor -> client -> transforms/output`

Main layers:

- `src/kaiten_cli/registry/`
  Source of truth for the command catalog. Each tool is declared as a `ToolSpec` with canonical name, MCP alias, schema, examples, request metadata, response policy, and optional runtime behavior.
- `src/kaiten_cli/runtime/`
  Execution layer. Builds requests, applies sandbox safety rules, runs HTTP calls, handles synthetic and aggregated reads, and shapes responses.
- `src/kaiten_cli/runtime/support/`
  Domain-specific helpers used by runtime behaviors for documents, projects, tree aggregation, cards bulk pagination, and activity pagination.
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

## Execution Modes

- `direct_http`
  One request derived directly from `OperationSpec`.
- `synthetic`
  Runtime may use fallback logic or reshape API responses to preserve a stable tool contract.
- `aggregated`
  Runtime performs bounded multi-request collection and returns one logical result.
- `custom`
  Runtime uses a dedicated executor because the API contract does not map cleanly to a simple request/response flow.

## Docs Map

Primary docs:

- [README.md](README.md) for install, usage, config, and operator guidance
- [AGENTS.md](AGENTS.md) for agent-specific usage and safety shortcuts
- [LIVE_VALIDATION.md](LIVE_VALIDATION.md) for live test process
- [API_BEHAVIOR_MATRIX.md](API_BEHAVIOR_MATRIX.md) for documented sandbox contracts
- `ARCHITECTURE.md` for the system map

Historical artifacts:

- [docs/archive/](docs/archive/README.md)

`ARCHITECTURE_REVIEW.md` is intentionally kept out of tracked docs. It is an audit artifact, not the maintained architecture reference.

## Known Tradeoffs

- The manual registry is easy to inspect, but large and maintenance-heavy.
- Runtime behaviors are now explicit, but still centralized in one behavior module.
- The CLI favors boundedness and predictability over maximum raw throughput.
- Live validation is explicit and well-documented, but sandbox contracts remain inherently unstable.
