# Live Validation

Этот документ описывает, как устроена полная live-проверка `kaiten-cli` на реальных credentials с явным per-run gate.

Текущая матрица контрактов в основном собрана на sandbox tenant, но сам live harness не привязывается к домену, имени профиля или profile metadata автоматически.

## Базовые правила

- live suite запускается только после зелёного локального `pytest`
- live suite запускается только при явном `KAITEN_LIVE=1|true`
- live suite никогда не идёт в default test run
- выполнение строго последовательное, без параллельных API-вызовов
- между вызовами остаются паузы для соблюдения low-load discipline
- все mutation-сценарии обязаны иметь проверяемый teardown
- если cleanup падает, live test падает

## Outcome classes

Для live verification используются следующие статусы:

- `live_passed`
  Команда реально проходит по success-path на текущем live tenant.
- `live_passed_with_runtime_fix`
  Команда проходит на текущем live tenant, но для этого понадобился runtime shaping в CLI.
- `live_passed_as_expected_error`
  Живой API стабильно или условно возвращает ожидаемый `4xx`, и этот контракт проверяется как корректный.
- `synthetic_read`
  Прямой endpoint нестабилен или unsupported, но CLI честно собирает эквивалентный read из другого безопасного endpoint.
- `policy_excluded`
  Команда сознательно исключена из live validation по политике безопасности.

## Что считается успешной live-валидацией

Команда считается live-covered только если выполнено одно из условий:

1. success-path реально отработал и postcondition подтверждён;
2. documented expected-error-path реально отработал и статус соответствует контракту;
3. synthetic fallback реально отработал и вернул ожидаемые данные;
4. команда помечена `policy_excluded`.

Скрытых “ну это вроде нормально” сценариев быть не должно.

## Как устроен live harness

Файлы:

- [tests/live/conftest.py](tests/live/conftest.py)
- [tests/live/test_sandbox_live_full.py](tests/live/test_sandbox_live_full.py)

Harness делает следующее:

- создаёт run-scoped имена временных сущностей
- ведёт cleanup stack в обратном порядке
- использует только canonical commands для live coverage
- считает покрытие по всему registry surface, кроме policy exclusions
- различает normal success path и expected-error path

## Policy exclusions

Сейчас live validation не включает:

- `api-keys.create`
- `api-keys.delete`

Причина: clean teardown невозможен без тестирования удаления ключей, а удаление ключей пользователь запретил проверять live.

## Synthetic contracts

Сейчас один явный synthetic read:

- `projects.cards.list`
  - сначала CLI пробует `GET /projects/{project_id}/cards`
  - если live API отвечает `405`, CLI делает `GET /projects/{project_id}?with_cards_data=true`
  - затем извлекает embedded cards list из project payload

## Expected-error contracts

Некоторые команды считаются live-correct именно через documented `4xx`:

- `removed-boards.list` -> `405`
- `removed-cards.list` -> `405`
- `checklists.list` -> `405`
- `checklist-items.list` -> `405`
- `card-subscribers.list` -> `405`
- `column-subscribers.list` -> `405`

Есть и условные tenant'ы, где live API может разрешить success-path или вернуть ожидаемый `4xx`:

- `automations.copy`
- `sprints.*`
- `workflows.*`
- `service-desk.requests.*`
- `service-desk.sla-rules.*`
- `user-timers.*`
- `compute-jobs.cancel`

Отдельно зафиксирован automation contract:

- `automations.create` и `automations.update` проходят на success-path при e2e-shaped payload:
  - `trigger.type = card_created`
  - `action.type = add_assignee`
  - `action.created = <iso datetime>`
  - `action.data.variant = specific`
  - `action.data.userId = <current_user_id>`
- `automations.get` может возвращать `405` даже после успешного create
- `automations.copy` остаётся conditional sandbox contract

Также зафиксирован ещё один стабильный expected-error:

- `service-desk.users.update` -> `400`, если текущий live-пользователь не является Service Desk user

И один смешанный Service Desk contract:

- `service-desk.users.set-temp-password` может либо успешно отработать, либо вернуть `403/404/405`
- `service-desk.organization-users.update` может либо успешно отработать, либо вернуть `400/403/404/405` даже после успешного `organization-users.add`

Точные статусы и примечания см. в [API_BEHAVIOR_MATRIX.md](API_BEHAVIOR_MATRIX.md).

## Запуск

```bash
KAITEN_LIVE=true KAITEN_DOMAIN=<company-subdomain> KAITEN_TOKEN=... \
  .venv/bin/pytest -m live -o addopts='--disable-socket --allow-unix-socket' \
  tests/live/test_sandbox_live_full.py
```

Если credentials уже сохранены в обычном active profile, достаточно выставить только `KAITEN_LIVE=1|true`.

## Что делать при новом blocker-е

1. Сначала определить, это runtime bug, live API limitation или synthetic-fallback candidate.
2. Если это runtime bug — добавить/обновить offline test и чинить CLI.
3. Если это корректный expected error — зафиксировать его в `API_BEHAVIOR_MATRIX.md` и, если меняется объяснение системы, в `ARCHITECTURE.md`.
4. Если это честный synthetic candidate — сначала добавить failing offline test, потом реализовать fallback.
