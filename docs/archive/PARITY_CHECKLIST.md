# Parity Checklist

Archived note: this is a historical representative checklist, not a current source of truth.

This file tracks the representative parity subset only.
It is not a full list of implemented commands; the archived execution baseline lives in [PLAN.md](PLAN.md).

As of `2026-04-15`, full tool-set alias parity with the current sibling `kaiten-mcp` registry is satisfied locally.
This checklist remains intentionally narrower: it tracks the representative regression subset rather than every implemented command.
Full sandbox live validation is now tracked in the archived [PLAN.md](PLAN.md) snapshot.
Special sandbox API contracts and synthetic fallbacks are tracked in [API_BEHAVIOR_MATRIX.md](../../API_BEHAVIOR_MATRIX.md).
The strict parity regression now compares the exact alias sets from both repos and supports both `_tool("...")` and `_tool(name="...")` declarations.

Representative subset for parity checks against `kaiten-mcp`:

- `company.current`
- `calendars.list`
- `users.current`
- `users.list`
- `spaces.list`
- `boards.list`
- `columns.list`
- `lanes.list`
- `cards.list`
- `cards.get`
- `cards.create`
- `cards.update`
- `cards.delete`
- `planned-relations.add`

For each command verify:

- auth model uses `KAITEN_DOMAIN` + `KAITEN_TOKEN`
- base URL is `https://{domain}.kaiten.ru/api/latest`
- rate limit delay matches MCP discipline class
- retries honor `Retry-After` and cap retry count
- error surface includes `status_code`, `message`, `body`
- `compact` and `fields` semantics match the reference where supported
- canonical command and MCP alias build the same request plan

Initial heavy denylist:

- bulk auto-pagination commands
- activity/history aggregation commands
- analytics and chart commands
- async compute-job flows
- commands without hard response size bounds
