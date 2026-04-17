# kaiten-cli

Нативный git-installable CLI для работы с [Kaiten](https://kaiten.ru), построенный как отдельный execution surface поверх того же доменного слоя, который раньше использовался для `kaiten-mcp`.

Проект не является MCP proxy и не импортирует `kaiten-mcp` в runtime.  
Источник истины для CLI — локальный registry в `src/kaiten_cli/registry/`.

## Быстрый старт

### Установка из git

Рекомендуемый путь:

```bash
uv tool install git+https://github.com/ViktorOgnev/kaiten-cli.git
```

Альтернатива:

```bash
pipx install git+https://github.com/ViktorOgnev/kaiten-cli.git
```

Fallback в локальную virtualenv:

```bash
python3 -m venv .venv
.venv/bin/pip install "git+https://github.com/ViktorOgnev/kaiten-cli.git"
```

### Проверка установки

```bash
kaiten --version
kaiten --help
kaiten agent-help
kaiten search-tools cards
```

### Skills для LLM и агентов

Если агент работает с этим CLI через git-репозиторий, оптимальные workflow описаны в skills format, а не размазаны по длинным prose docs:

- [skills/kaiten-cli-heavy-data/SKILL.md](skills/kaiten-cli-heavy-data/SKILL.md)  
  Как не строить N+1 path, когда идти в bulk reads, а когда уже пора собирать локальный snapshot.
- [skills/kaiten-cli-metrics/SKILL.md](skills/kaiten-cli-metrics/SKILL.md)  
  Как собирать Kanban-метрики через snapshot/query слой и не возвращаться к per-card history loops.

### Обновление

Если CLI уже установлен из branch-based git URL, обновление подтягивается вручную:

```bash
uv tool upgrade kaiten-cli
pipx upgrade kaiten-cli
```

По умолчанию установка идёт с текущего `master`. Если нужен зафиксированный релиз, можно pin'иться на tag:

```bash
uv tool install "git+https://github.com/ViktorOgnev/kaiten-cli.git@v0.1.6"
```

Если пакет установлен в текущий Python environment, доступен и module entrypoint:

```bash
python -m kaiten_cli --help
```

## Карта документации

- [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md)
  Полный generated справочник по всем canonical командам и MCP aliases на одной странице.
- [ARCHITECTURE.md](ARCHITECTURE.md)
  Архитектурная карта, execution modes и docs model.
- [AGENTS.md](AGENTS.md)
  Короткий agent-facing guide и discovery-first flow.
- [LIVE_VALIDATION.md](LIVE_VALIDATION.md)
  Как устроен live harness и sandbox validation.
- [API_BEHAVIOR_MATRIX.md](API_BEHAVIOR_MATRIX.md)
  Зафиксированные sandbox/API contracts.
- [skills/kaiten-cli-heavy-data/SKILL.md](skills/kaiten-cli-heavy-data/SKILL.md)
  Heavy-data workflow guidance для LLM и headless scripts.
- [skills/kaiten-cli-metrics/SKILL.md](skills/kaiten-cli-metrics/SKILL.md)
  Metrics workflow guidance для LLM и headless scripts.

## Что уже есть

- canonical commands: `kaiten <namespace...> <action>`
- MCP-compatible aliases: `kaiten kaiten_list_cards`
- `--version` и module entrypoint: `python -m kaiten_cli`
- `--json` с жёстким success/error envelope
- discovery-команды: `search-tools`, `describe`, `examples`
- profiles и sandbox mutation guard
- request-scoped GET cache внутри одного execution path
- opt-in persistent disk cache с коротким TTL для safe reference/entity reads
- persistent local sqlite snapshots для headless analytics и repeated report workflows
- local-only `query cards` / `query metrics` поверх snapshot storage
- low-load HTTP client: throttling, bounded retry, explicit timeouts
- локальные transforms: `compact`, `fields`, strip-base64
- полный паритет по набору инструментов с текущим локальным registry snapshot
- strict alias-set regression против checked-in snapshot
- full live validation campaign на sandbox с teardown discipline

## Инструменты

<!-- BEGIN GENERATED COMMAND SUMMARY -->
В `kaiten-cli` сейчас **259** canonical инструментов в **29** registry modules. Полный список команд: [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md).

| Область | Модуль | Кол-во | Справочник |
|---|---|---:|---|
| Карточки | `cards` | 9 | [Раздел](COMMAND_REFERENCE.md#module-cards) |
| Комментарии | `comments` | 5 | [Раздел](COMMAND_REFERENCE.md#module-comments) |
| Участники и пользователи | `members` | 5 | [Раздел](COMMAND_REFERENCE.md#module-members) |
| Логи времени | `time_logs` | 5 | [Раздел](COMMAND_REFERENCE.md#module-time-logs) |
| Теги | `tags` | 6 | [Раздел](COMMAND_REFERENCE.md#module-tags) |
| Чеклисты | `checklists` | 8 | [Раздел](COMMAND_REFERENCE.md#module-checklists) |
| Блокировки | `blockers` | 5 | [Раздел](COMMAND_REFERENCE.md#module-blockers) |
| Связи карточек | `card_relations` | 10 | [Раздел](COMMAND_REFERENCE.md#module-card-relations) |
| Внешние ссылки | `external_links` | 4 | [Раздел](COMMAND_REFERENCE.md#module-external-links) |
| Файлы карточек | `files` | 4 | [Раздел](COMMAND_REFERENCE.md#module-files) |
| Подписчики | `subscribers` | 6 | [Раздел](COMMAND_REFERENCE.md#module-subscribers) |
| Пространства | `spaces` | 6 | [Раздел](COMMAND_REFERENCE.md#module-spaces) |
| Доски | `boards` | 5 | [Раздел](COMMAND_REFERENCE.md#module-boards) |
| Колонки и подколонки | `columns` | 8 | [Раздел](COMMAND_REFERENCE.md#module-columns) |
| Дорожки | `lanes` | 4 | [Раздел](COMMAND_REFERENCE.md#module-lanes) |
| Типы карточек | `card_types` | 5 | [Раздел](COMMAND_REFERENCE.md#module-card-types) |
| Кастомные свойства | `custom_properties` | 10 | [Раздел](COMMAND_REFERENCE.md#module-custom-properties) |
| Документы | `documents` | 10 | [Раздел](COMMAND_REFERENCE.md#module-documents) |
| Вебхуки | `webhooks` | 9 | [Раздел](COMMAND_REFERENCE.md#module-webhooks) |
| Автоматизации и воркфлоу | `automations` | 11 | [Раздел](COMMAND_REFERENCE.md#module-automations) |
| Проекты и спринты | `projects` | 13 | [Раздел](COMMAND_REFERENCE.md#module-projects) |
| Роли и группы | `roles_and_groups` | 14 | [Раздел](COMMAND_REFERENCE.md#module-roles-and-groups) |
| Аудит и аналитика | `audit_and_analytics` | 12 | [Раздел](COMMAND_REFERENCE.md#module-audit-and-analytics) |
| Service Desk | `service_desk` | 47 | [Раздел](COMMAND_REFERENCE.md#module-service-desk) |
| Графики и аналитика | `charts` | 15 | [Раздел](COMMAND_REFERENCE.md#module-charts) |
| Дерево сущностей | `tree` | 2 | [Раздел](COMMAND_REFERENCE.md#module-tree) |
| Утилиты | `utilities` | 14 | [Раздел](COMMAND_REFERENCE.md#module-utilities) |
| Локальные snapshots | `snapshot` | 5 | [Раздел](COMMAND_REFERENCE.md#module-snapshot) |
| Локальные запросы | `query` | 2 | [Раздел](COMMAND_REFERENCE.md#module-query) |
| **Итого** | **29 modules** | **259** | [Полный справочник](COMMAND_REFERENCE.md) |
<!-- END GENERATED COMMAND SUMMARY -->

## Структура репозитория

- `src/kaiten_cli/registry/`
  Каталог всех инструментов. Здесь объявляются `ToolSpec`, canonical names, aliases, schemas и metadata.
- `src/kaiten_cli/runtime/`
  Исполняемый слой: request building, HTTP client, cache, trace, local snapshot store, synthetic и aggregated execution.
- `src/kaiten_cli/runtime/support/`
  Вспомогательные bounded helper-модули для runtime.
- `src/kaiten_cli/`
  Stable package surface и shared core: `app.py`, `discovery.py`, `profiles.py`, `models.py`, `errors.py`.

Если коротко: `registry` описывает инструменты, `runtime` их исполняет.

## Требования

- Python >= 3.11
- Kaiten sandbox или другой безопасный тестовый аккаунт
- API token Kaiten

## Переменные окружения

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `KAITEN_DOMAIN` | Да | Домен компании (`sandbox` для `https://sandbox.kaiten.ru`) |
| `KAITEN_TOKEN` | Да | API-токен пользователя |
| `KAITEN_LIVE` | Нет | `1` для opt-in live validation |
| `KAITEN_CLI_CONFIG_PATH` | Нет | Путь до файла profiles/config |
| `KAITEN_TRACE_FILE` | Нет | JSONL-файл для append-only command trace |

CLI читает переменные окружения только из текущего процесса или из сохранённого profile-конфига.

## Настройка доступа

Рекомендуемый путь: сохранить профиль и сделать его активным.

```bash
kaiten profile add main --domain <company-subdomain> --token <api-token> --set-active
kaiten profile show
```

Если работаешь с sandbox:

```bash
kaiten profile add sandbox --domain sandbox --token <api-token> --sandbox --set-active
```

Если нужен opt-in persistent cache для этого profile:

```bash
kaiten profile add main \
  --domain <company-subdomain> \
  --token <api-token> \
  --cache-mode readwrite \
  --cache-ttl-seconds 60 \
  --set-active
```

Временный fallback через переменные окружения:

```bash
export KAITEN_DOMAIN=<company-subdomain>
export KAITEN_TOKEN=<api-token>
```

### Приоритет конфигурации

CLI резолвит credentials в таком порядке:

1. `--profile <name>`
2. активный profile из config
3. `KAITEN_DOMAIN` + `KAITEN_TOKEN` из environment

Это важно и для локального использования, и для агентов: сохранённый active profile имеет приоритет над env fallback, если явно не передан другой `--profile`.

## Ввод и shaping ответа

CLI поддерживает три режима входного payload:

- обычные CLI options: `kaiten cards list --board-id 10 --limit 5`
- `--from-file payload.json` для полного JSON payload из файла
- `--stdin-json` для JSON payload из stdin

Для сложных объектов и массивов можно передавать JSON прямо в option-значении или вынести их в файл. Если нужно дословно передать большое тело запроса, `--from-file` обычно надёжнее и дешевле для LLM-агента, чем длинная строка аргументов.

Для уменьшения latency, размера ответа и downstream token cost:

- используйте `--compact`, если команда его поддерживает
- ограничивайте поля через `--fields id,title,...`
- учитывайте, что base64-поля автоматически срезаются из ответа

Часть команд работает не как прямой single-request passthrough:

- `direct_http`: один HTTP-вызов к Kaiten API
- `synthetic`: результат собирается из fallback или shape-specific runtime logic
- `aggregated`: CLI делает bounded pagination или несколько чтений и агрегирует результат

`describe <tool>` и `search-tools <query>` показывают эти metadata, что полезно перед вызовом тяжёлых команд.

## Как работает кэш

В CLI есть два разных кэша.

- `request-scoped`
  Работает автоматически внутри одного запуска `kaiten`.
- `persistent`
  Живёт между разными CLI-процессами и включается только через `--cache-mode` или profile defaults.

### Что происходит без флагов

Если запустить обычную команду вроде:

```bash
kaiten --json cards get --card-id 123
```

то persistent cache не используется. При этом safe GET reads внутри одного execution path всё равно защищены request-scoped cache и in-flight dedup. Это особенно полезно для `synthetic` и `aggregated` команд, где CLI сам может прийти к одному и тому же `GET` несколько раз.

### Когда пользователь реально видит выгоду

- `single call`
  Для обычного one-shot `GET` кэш почти незаметен.
- `aggregated` или `synthetic`
  Встроенный request-scoped cache экономит повторные чтения внутри одного запуска.
- `shell/LLM workflow`
  Если один и тот же safe `GET` вызывается много раз из разных CLI-процессов, имеет смысл включать persistent cache.

### Режимы persistent cache

- `--cache-mode off`
  Только request-scoped cache внутри текущего запуска. Это default.
- `--cache-mode readwrite`
  Читать и записывать короткоживущий persistent disk cache.
- `--cache-mode refresh`
  Игнорировать disk read, сходить в API и перезаписать cache.
- `--cache-ttl-seconds`
  TTL для persistent cache. Можно задавать на команду или сохранить в profile.

### Что кэшируется и что нет

Persistent cache deliberately conservative:

- подходит для safe reference/entity reads;
- полезен для типичных `*.get` и небольших discovery list-команд;
- не предназначен для polling и volatile reads;
- очищается после успешных mutation-команд для текущего profile/domain.
- при несовместимой локальной sqlite-схеме или повреждённом файле persistent cache автоматически удаляется и создаётся заново.

Ключ кэша строится по raw API request: `profile/domain + method + path + params`. `compact` и `fields` в ключ не входят, потому что это post-processing уже после ответа API.

### Примеры

Включить short-lived persistent cache для repeated reads:

```bash
kaiten --json --cache-mode readwrite --cache-ttl-seconds 60 cards get --card-id 123 --compact --fields id,title,state
```

Принудительно обновить stale read:

```bash
kaiten --json --cache-mode refresh spaces list --compact --fields id,title
```

Сценарий, где обычно достаточно встроенного request-scoped behavior:

```bash
kaiten --json card-location-history batch-get --card-ids '[101,102,103]' --workers 2 --fields changed,column_id
```

Для bulk/read-heavy workflows смотри [skills/kaiten-cli-heavy-data/SKILL.md](skills/kaiten-cli-heavy-data/SKILL.md), для аналитических сценариев — [skills/kaiten-cli-metrics/SKILL.md](skills/kaiten-cli-metrics/SKILL.md).

## High-cardinality reads

Если сценарий требует сотни однотипных чтений, не спаунь `kaiten` отдельным процессом на каждый объект.

- Для массовой истории перемещений используйте `card-location-history.batch-get`, а не цикл из `card-location-history.get`.
- Для detail enrichment по карточкам используйте `cards.batch-get`, а не цикл из `cards.get`.
- Для work-log analytics используйте `time-logs.batch-list`, а не цикл из `time-logs.list`.
- Для relation-heavy расследований используйте `card-children.batch-list`, а не цикл из `card-children.list`.
- Для comment-heavy расследований используйте `comments.batch-list`, а не цикл из `comments.list`.
- Для bulk population по карточкам используйте `cards.list-all --selection all|active_only|archived_only`.
- Для topology scaffolding используйте `space-topology.get`, а не связку из `boards.list`, `columns.list` и `lanes.list`.
- `cards.list-all --selection active_only` нормализован в CLI как `all_cards - archived_subset`, чтобы не перекладывать эту логику на внешний скрипт.
- Если workflow состоит из многих повторных reference/entity GET, включайте `--cache-mode readwrite` с коротким TTL вместо повторных identical reads.

Примеры:

```bash
kaiten --json card-location-history batch-get --card-ids '[101,102,103]' --workers 2
kaiten --json cards batch-get --card-ids '[101,102,103]' --workers 2 --fields id,title,description
kaiten --json time-logs batch-list --card-ids '[101,102,103]' --workers 2 --fields id,time_spent,for_date
kaiten --json card-children batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,title
kaiten --json comments batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,text
kaiten --json cards list-all --board-id 10 --selection active_only --fields id,title,state
kaiten --json space-topology get --space-id 10
kaiten --json --cache-mode readwrite cards get --card-id 101 --compact --fields id,title,state
```

## Investigation and report workflows

Если агент или внешний скрипт строит отчёт, сначала собери дешёвые bulk primitives, а уже потом переходи к постобработке:

- `space-topology.get` для boards + columns + lanes в одном CLI вызове
- `cards.list-all` для population
- `cards.batch-get` для detail enrichment только после локального сужения candidate set
- `time-logs.batch-list` для work logs без per-card loops
- `space-activity-all.get` вместо ручной пагинации вокруг `space-activity.get`
- `card-children.batch-list` и `comments.batch-list` вместо per-card relation/comment loops
- `card-location-history.batch-get` только когда действительно нужна история перемещений

Если нужно потом разбирать, почему путь оказался дорогим или неоптимальным, включай command trace:

```bash
kaiten --json --trace-file ./kaiten-trace.jsonl cards list-all --board-id 10 --selection active_only
```

Trace пишет JSONL со временем выполнения, количеством реальных HTTP-запросов, retry/cache counters и batch metadata вроде `requested_count` / `unique_count` / `workers`.

## Local-first analytics and headless workflows

Если нужно много раз читать одну и ту же рабочую выборку, не задавай Kaiten API один и тот же вопрос заново на каждом шаге. Собери локальный snapshot один раз, дальше считай и фильтруй локально:

1. `snapshot build` для сборки working set в локальный sqlite
2. `query cards --view summary` для локальной выборки по фильтрам и candidate reduction
3. `query metrics` для локальных count / WIP / throughput / lead time / cycle time / aging
4. `query cards --view detail|evidence` только для уже narrowed candidate set
5. Только потом, если нужно, отдельные mutation-команды Kaiten API

Базовый пример:

```bash
kaiten --json snapshot build --name team-basic --space-id 10 --preset basic
kaiten --json query cards --snapshot team-basic --view summary --filter '{"board_ids":[10],"has_comments":true}' --fields id,title,has_comments
```

Аналитический пример с окном:

```bash
kaiten --json snapshot build \
  --name team-q1 \
  --space-id 10 \
  --preset analytics \
  --window-start 2026-01-01T00:00:00Z \
  --window-end 2026-03-31T23:59:59Z

kaiten --json query metrics --snapshot team-q1 --metric throughput --group-by board_id
```

Что важно:

- `snapshot build` и `snapshot refresh` читают Kaiten API один раз на выбранный scope и сохраняют datasets локально.
- `snapshot refresh` в v1 rebuild-oriented: он пересобирает snapshot целиком, а не делает incremental sync.
- `snapshot show` и `snapshot list` показывают `schema_version`, чтобы локальная схема была versioned и пригодной для будущих migrations.
- snapshot storage считается derived local state: если локальный sqlite store несовместим с новой схемой CLI или повреждён, он автоматически пересоздаётся. Старые snapshots в таком случае теряются.
- `query cards` и `query metrics` не ходят в Kaiten API вообще.
- `query cards` по умолчанию работает в `summary` view; `detail` и `evidence` используются только когда нужно раскрыть narrowed candidate set.
- `basic` preset сохраняет topology + card population summary.
- `analytics` добавляет space activity, card location history и time logs.
- `evidence` добавляет detail-enriched cards, child relations и comments.
- `full` объединяет analytics + evidence.
- `query metrics` в текущем виде generic: это локальный общий metric layer, а не tenant-specific flow profile engine.
- Local-first path остаётся explicit. Обычные transport-команды не подменяются snapshot behavior автоматически.

Для LLM и headless scripts это preferred path, когда вопросы повторяются над одной и той же группой карточек.

## Первые команды

Read-only smoke после настройки доступа:

```bash
kaiten --json spaces list --compact --fields id,title
kaiten describe cards.create
kaiten search-tools "project cards"
kaiten snapshot list --json
```

Если нужна диагностика без загрязнения JSON stdout:

```bash
kaiten --json --verbose cards list --board-id 10 --limit 5
```

Verbose diagnostics пишутся в `stderr` и показывают resolved profile source, request path, timeout class и custom execution path.

Если нужна post-hoc трассировка длинного сценария:

```bash
kaiten --json --trace-file ./kaiten-trace.jsonl card-location-history batch-get --card-ids '[101,102,103]'
```

Это не меняет stdout-ответ команды: trace уходит только в отдельный JSONL-файл.

## Troubleshooting

Если видишь `Missing Kaiten credentials`:

```bash
kaiten profile add main --domain <company-subdomain> --token <api-token> --set-active
kaiten profile show
```

Если профиль уже сохранён, но не активен:

```bash
kaiten profile list
kaiten profile use <name>
```

## Тесты

Локальный baseline:

```bash
.venv/bin/pytest -q
```

Live validation на sandbox запускается отдельно и только после зелёных локальных тестов:

```bash
KAITEN_LIVE=1 KAITEN_DOMAIN=sandbox KAITEN_TOKEN=... \
  .venv/bin/pytest -m live -o addopts='--disable-socket --allow-unix-socket' \
  tests/live/test_sandbox_live_full.py
```

## Performance reference workflows

Для воспроизводимого сравнения `naive loop -> bulk transport -> snapshot/query` есть repo-level harness:

```bash
.venv/bin/python scripts/benchmark_reference_workflows.py --spec path/to/workflows.json
```

Он запускает заданные CLI-команды, собирает stdout bytes, wall time и trace JSONL, чтобы сравнивать не только latency, но и реальный `http_request_count`.

`README.md` остаётся source of truth для установки, настройки и повседневного использования CLI. Полный каталог команд живёт в `COMMAND_REFERENCE.md`, а архитектурная карта — в `ARCHITECTURE.md`.

Релизная политика:

- каждый пользовательский релиз сопровождается bump версии в CLI и git tag вида `vX.Y.Z`
- branch-based install не обновляется автоматически; нужен явный `uv tool upgrade kaiten-cli` или `pipx upgrade kaiten-cli`
- install с `@vX.Y.Z` считается pinned и сам на следующий tag не переключается

## Дисклеймер

Настоящий репозиторий и размещённое в нём программное обеспечение предоставляются по принципу “как есть” (“as is”) и “по мере доступности” (“as available”), без каких-либо гарантий, явных или подразумеваемых. Автор не предоставляет никаких заверений и гарантий в отношении корректности, надёжности, безопасности, пригодности для конкретных целей или отсутствия ошибок в данном решении.

Используя данный программный продукт, вы подтверждаете, что принимаете на себя все риски, связанные с его использованием, включая, но не ограничиваясь, прямыми, косвенными, случайными или последующими убытками.

Автор настоящего репозитория является единственным разработчиком и правообладателем данного кода. Данное решение разработано и распространяется независимо и не является официальным продуктом или услугой компании Kaiten Software.

Компания Kaiten Software не несёт никакой ответственности за качество работы, производительность, результаты использования или любые последствия, связанные с использованием данного решения. Любые упоминания Kaiten Software приведены исключительно в информационных целях и не означают одобрения, поддержки или аффилированности.
