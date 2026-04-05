# API Behavior Matrix

Этот документ фиксирует живые sandbox-контракты для `kaiten-cli`.

## Default rule

Все canonical команды из registry, которые не перечислены ниже, считаются `live_passed`: они должны проходить по normal success-path в полном live suite.

## Validated success-path contracts with special notes

| Command | Verb / Path | Status | Notes |
|---------|-------------|--------|-------|
| `automations.create` | `POST /spaces/{space_id}/automations` | `live_passed` | Успешно проходит на sandbox с known-good payload: `trigger.type=card_created`, `action.type=add_assignee`, `created`, `data.variant`, `data.userId`. |
| `automations.update` | `PATCH /spaces/{space_id}/automations/{automation_id}` | `live_passed` | Успешно проходит для automation, созданной с known-good payload. |
| `automations.delete` | `DELETE /spaces/{space_id}/automations/{automation_id}` | `live_passed` | Успешный cleanup подтверждён в live validation. |

## Runtime-shaped contracts

| Command | Verb / Path | Status | Notes |
|---------|-------------|--------|-------|
| `boards.delete` | `DELETE /spaces/{space_id}/boards/{board_id}` | `live_passed_with_runtime_fix` | Sandbox требует `force`; CLI передаёт его в query и body. |

## Synthetic reads

| Command | Primary endpoint | Status | Fallback |
|---------|------------------|--------|----------|
| `projects.cards.list` | `GET /projects/{project_id}/cards` | `synthetic_read` | При `405` CLI делает `GET /projects/{project_id}?with_cards_data=true` и извлекает embedded cards list. |

## Stable expected-error contracts

| Command | Verb / Path | Status | Expected statuses | Notes |
|---------|-------------|--------|-------------------|-------|
| `removed-boards.list` | `GET /boards/removed` | `live_passed_as_expected_error` | `405` | Sandbox recycle-bin endpoint unsupported. |
| `removed-cards.list` | `GET /cards/removed` | `live_passed_as_expected_error` | `405` | Sandbox recycle-bin endpoint unsupported. |
| `checklists.list` | `GET /cards/{card_id}/checklists` | `live_passed_as_expected_error` | `405` | Direct checklist listing unsupported on sandbox. |
| `checklist-items.list` | `GET /cards/{card_id}/checklists/{checklist_id}/items` | `live_passed_as_expected_error` | `405` | Direct checklist-item listing unsupported on sandbox. |
| `card-subscribers.list` | `GET /cards/{card_id}/subscribers` | `live_passed_as_expected_error` | `405` | Direct subscriber listing unsupported on sandbox. |
| `column-subscribers.list` | `GET /columns/{column_id}/subscribers` | `live_passed_as_expected_error` | `405` | Direct subscriber listing unsupported on sandbox. |
| `service-desk.users.update` | `PATCH /service-desk/users/{user_id}` | `live_passed_as_expected_error` | `400`, `403`, `404`, `405` | Для текущего sandbox-аккаунта API возвращает `400 Should be service desk user`, если пользователь не является SD user. |
| `service-desk.organization-users.update` | `PATCH /service-desk/organizations/{organization_id}/users/{user_id}` | `live_passed_as_expected_error` | `400`, `403`, `404`, `405` | Обновление permissions для organization-user остаётся sandbox-dependent even after successful add. |

## Conditional success-or-error contracts

Эти команды остаются live-correct, даже если sandbox вместо success-path возвращает ожидаемый `4xx`.

| Command family | Status | Expected statuses | Notes |
|----------------|--------|-------------------|-------|
| `sprints.create` | `live_passed_as_expected_error` | `403`, `405` | Создание спринта зависит от sandbox permissions/capabilities. |
| `sprints.list` | `live_passed_as_expected_error` | `403`, `405` | Чтение списка спринтов зависит от sandbox permissions/capabilities. |
| `service-desk.users.set-temp-password` | `live_passed_as_expected_error` | `403`, `404`, `405` | На sandbox может либо успешно сработать, либо вернуть documented `403/404/405`; live suite принимает оба исхода. |
| `sprints.get`, `sprints.delete` | `live_passed_as_expected_error` | `403`, `404`, `405` | При недоступном create live suite валидирует sentinel error contract. |
| `sprints.update` | `live_passed_as_expected_error` | `403`, `404`, `405`, `500` | На sandbox update по sentinel sprint id может отдавать `500`; это зафиксировано как documented sandbox defect contract. |
| `automations.get` | `live_passed_as_expected_error` | `405` | GET-single для automation может быть unsupported даже после успешного create. |
| `automations.copy` | `live_passed_as_expected_error` | `400`, `403`, `404`, `405` | Даже при live-valid source automation copy остаётся sandbox-dependent. |
| `webhooks.get`, `webhooks.delete` | `live_passed_as_expected_error` | `404`, `405` | После create эти endpoints могут быть недоступны как отдельные singleton operations. |
| `workflows.create` | `live_passed_as_expected_error` | `403`, `405` | Создание workflow зависит от sandbox permissions/capabilities. |
| `workflows.get`, `workflows.update`, `workflows.delete` | `live_passed_as_expected_error` | `403`, `404`, `405` | При недоступном create live suite валидирует sentinel error contract. |
| `service-desk.requests.create` | `live_passed_as_expected_error` | `400`, `403`, `404`, `405` | Request creation permission-dependent. |
| `service-desk.requests.get`, `service-desk.requests.update`, `service-desk.requests.delete` | `live_passed_as_expected_error` | `403`, `404`, `405` | При недоступном create live suite валидирует sentinel error contract. |
| `service-desk.sla-rules.create` | `live_passed_as_expected_error` | `400`, `403`, `404`, `405` | SLA rule creation schema- and permission-dependent. |
| `service-desk.sla-rules.update`, `service-desk.sla-rules.delete` | `live_passed_as_expected_error` | `400`, `403`, `404`, `405` | При недоступном create live suite валидирует sentinel error contract. |
| `compute-jobs.cancel` | `live_passed_as_expected_error` | `400`, `404`, `409` | Cancel зависит от состояния compute job. |
| `user-timers.list` | `live_passed_as_expected_error` | `403`, `405` | Sandbox timer surface нестабилен. |
| `user-timers.create` | `live_passed_as_expected_error` | `400`, `403`, `405`, `409` | Timer creation зависит от sandbox semantics. |
| `user-timers.get`, `user-timers.update`, `user-timers.delete` | `live_passed_as_expected_error` | `403`, `404`, `405` | При недоступном create live suite валидирует sentinel error contract. |

## Policy exclusions

| Command | Status | Notes |
|---------|--------|-------|
| `api-keys.create` | `policy_excluded` | Создание ключей не тестируется live, потому что clean teardown потребовал бы testing delete. |
| `api-keys.delete` | `policy_excluded` | Явно исключено по пользовательской политике. |
