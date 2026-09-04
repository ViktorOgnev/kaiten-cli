# API Behavior Matrix

Этот документ фиксирует API-контракты для `kaiten-cli`, ранее наблюдавшиеся на live test tenant и закодированные в текущем live harness.

Запуск live suite по-прежнему gated только через `KAITEN_LIVE=1|true`; special-case по домену или profile metadata для этого не используется.

## Verification metadata

| Поле | Значение |
|------|----------|
| Contract baseline | `kaiten-cli v0.1.23` |
| Tenant class | Kaiten sandbox test tenant |
| Текущий аудит | `2026-07-09`; live suite **не запускался** |
| Последняя полная live campaign | `TBD`: дата и commit не подтверждены в репозитории |
| Источник до следующего live run | checked-in contracts и `tests/live/`; записи ниже нельзя считать повторно подтверждёнными текущим аудитом |

После следующей полной live campaign эту таблицу нужно обновить точными датой, commit SHA, версией CLI и tenant class. Secrets, tenant URL и идентификаторы тестовых сущностей сюда не записываются.

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
| `checklists.list` | `GET /cards/{card_id}` | `synthetic_read` | Replaces unsupported direct `GET /cards/{card_id}/checklists` by extracting embedded `checklists`. |
| `checklist-items.list` | `GET /cards/{card_id}` | `synthetic_read` | Replaces unsupported direct `GET /cards/{card_id}/checklists/{checklist_id}/items` by extracting matching checklist `items`. |

## Stable expected-error contracts

| Command | Verb / Path | Status | Expected statuses | Notes |
|---------|-------------|--------|-------------------|-------|
| `removed-boards.list` | `GET /boards/removed` | `live_passed_as_expected_error` | `405` | Sandbox recycle-bin endpoint unsupported. |
| `removed-cards.list` | `GET /cards/removed` | `live_passed_as_expected_error` | `405` | Sandbox recycle-bin endpoint unsupported. |
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

## Not yet live-validated

Эти команды добавлены после последней полной live campaign. Сценарии для них уже есть в
`tests/live/`, но прогона, подтверждающего контракт, не было, поэтому default rule
`live_passed` на них не распространяется.

| Command family | Verb / Path | Status | Notes |
|----------------|-------------|--------|-------|
| `addons.list` | `GET /addons` | `live_not_validated` | Каталог опубликованных аддонов без фильтра по компании; live suite принимает success или `403/405`. |
| `company-addons.list` | `GET /company/addons` | `live_not_validated` | Аддоны, зарегистрированные самой компанией, включая неопубликованные. |
| `addons.uid` | локальная команда | `live_not_validated` | UUID v5 считается локально, обращения к API нет; проверяется совпадение с эталонным UID `/github`. |
| `space-addons.list` | `GET /spaces/{space_id}/addons` | `live_not_validated` | Требует права `space.addons.read`. |
| `space-addons.install`, `space-addons.uninstall` | `PATCH` / `DELETE /spaces/{space_id}/addons/{addon_uid}` | `live_not_validated` | В live suite проверяются только на sentinel UID, чтобы не менять набор аддонов реального пространства. Sentinel подобран так, чтобы проходить `uuidIdRule`, иначе probe подтверждал бы 404 от несовпадения маршрута, а не контракт эндпоинта. |
| `card-addon-data.get`, `user-addon-data.get` | `GET .../addons-data/{addon_uid}` | `live_not_validated` | Чтение; для неустановленного аддона возможен пустой ответ или `403/404/405`. |
| `card-addon-data.set`, `user-addon-data.set` | `PATCH .../addons-data/{addon_uid}` | `live_not_validated` | Запись проверяется только на sentinel UID: реальная запись требует установленного аддона и `card.update`. |
| `github-addon.*.list` | `GET /cards/{card_id}/addons-data/{addon_uid}` | `live_not_validated` | Чтение shared-ключей `attachedPulls`, `attachedBranches`, `attachedCommits`, `attachedIssues`. При пустом ответе на выведенный UID дополнительно читаются `GET /cards/{id}` и `GET /spaces/{id}/addons`, чтобы взять реально зарегистрированный UID. |
| `github-addon.*.attach`, `github-addon.*.detach` | `PATCH /cards/{card_id}/addons-data/{addon_uid}` | `live_not_validated` | Live suite покрывает только `--dry-run`: реальная запись изменила бы данные аддона на живой карточке. |

## Policy exclusions

| Command | Status | Notes |
|---------|--------|-------|
| `api-keys.create` | `policy_excluded` | Создание ключей не тестируется live, потому что clean teardown потребовал бы testing delete. |
| `api-keys.delete` | `policy_excluded` | Явно исключено по пользовательской политике. |
