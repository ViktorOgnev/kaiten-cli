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
kaiten search-tools cards
```

### Skills для LLM и агентов

Если агент работает с этим CLI через git-репозиторий, оптимальные workflow описаны в skills format, а не размазаны по длинным prose docs:

- [skills/kaiten-cli-heavy-data/SKILL.md](skills/kaiten-cli-heavy-data/SKILL.md)  
  Как не строить N+1 path, как выбирать bulk tools, shaping и cache mode для тяжёлых чтений.
- [skills/kaiten-cli-metrics/SKILL.md](skills/kaiten-cli-metrics/SKILL.md)  
  Как собирать Kanban-метрики через текущий CLI без поштучных history loops.

### Обновление

Если CLI уже установлен из branch-based git URL, обновление подтягивается вручную:

```bash
uv tool upgrade kaiten-cli
pipx upgrade kaiten-cli
```

По умолчанию установка идёт с текущего `master`. Если нужен зафиксированный релиз, можно pin'иться на tag:

```bash
uv tool install "git+https://github.com/ViktorOgnev/kaiten-cli.git@v0.1.3"
```

Если пакет установлен в текущий Python environment, доступен и module entrypoint:

```bash
python -m kaiten_cli --help
```

## Что уже есть

- canonical commands: `kaiten <namespace...> <action>`
- MCP-compatible aliases: `kaiten kaiten_list_cards`
- `--version` и module entrypoint: `python -m kaiten_cli`
- `--json` с жёстким success/error envelope
- discovery-команды: `search-tools`, `describe`, `examples`
- profiles и sandbox mutation guard
- request-scoped GET cache внутри одного execution path
- opt-in persistent disk cache с коротким TTL для safe reference/entity reads
- low-load HTTP client: throttling, bounded retry, explicit timeouts
- локальные transforms: `compact`, `fields`, strip-base64
- полный паритет по набору инструментов с текущим локальным registry snapshot
- strict alias-set regression против checked-in snapshot
- full live validation campaign на sandbox с teardown discipline

## Структура репозитория

- `src/kaiten_cli/registry/`
  Каталог всех инструментов. Здесь объявляются `ToolSpec`, canonical names, aliases, schemas и metadata.
- `src/kaiten_cli/runtime/`
  Исполняемый слой: request building, HTTP client, transforms, synthetic и aggregated execution.
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
- Для bulk population по карточкам используйте `cards.list-all --selection all|active_only|archived_only`.
- `cards.list-all --selection active_only` нормализован в CLI как `all_cards - archived_subset`, чтобы не перекладывать эту логику на внешний скрипт.
- Если workflow состоит из многих повторных reference/entity GET, включайте `--cache-mode readwrite` с коротким TTL вместо повторных identical reads.

Примеры:

```bash
kaiten --json card-location-history batch-get --card-ids '[101,102,103]' --workers 2
kaiten --json cards list-all --board-id 10 --selection active_only --fields id,title,state
kaiten --json --cache-mode readwrite cards get --card-id 101 --compact --fields id,title,state
```

## Первые команды

Read-only smoke после настройки доступа:

```bash
kaiten --json spaces list --compact --fields id,title
kaiten describe cards.create
kaiten search-tools "project cards"
```

Если нужна диагностика без загрязнения JSON stdout:

```bash
kaiten --json --verbose cards list --board-id 10 --limit 5
```

Verbose diagnostics пишутся в `stderr` и показывают resolved profile source, request path, timeout class и custom execution path.

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

Карта документации:

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [AGENTS.md](AGENTS.md)
- [skills/kaiten-cli-heavy-data/SKILL.md](skills/kaiten-cli-heavy-data/SKILL.md)
- [skills/kaiten-cli-metrics/SKILL.md](skills/kaiten-cli-metrics/SKILL.md)
- [LIVE_VALIDATION.md](LIVE_VALIDATION.md)
- [API_BEHAVIOR_MATRIX.md](API_BEHAVIOR_MATRIX.md)
- [docs/archive/](docs/archive/README.md)

`README.md` остаётся source of truth для установки, настройки и повседневного использования CLI. Архитектурная карта живёт в `ARCHITECTURE.md`. Исторические plan/review артефакты вынесены в `docs/archive/`.

Релизная политика:

- каждый пользовательский релиз сопровождается bump версии в CLI и git tag вида `vX.Y.Z`
- branch-based install не обновляется автоматически; нужен явный `uv tool upgrade kaiten-cli` или `pipx upgrade kaiten-cli`
- install с `@vX.Y.Z` считается pinned и сам на следующий tag не переключается

## Дисклеймер

Настоящий репозиторий и размещённое в нём программное обеспечение предоставляются по принципу “как есть” (“as is”) и “по мере доступности” (“as available”), без каких-либо гарантий, явных или подразумеваемых. Автор не предоставляет никаких заверений и гарантий в отношении корректности, надёжности, безопасности, пригодности для конкретных целей или отсутствия ошибок в данном решении.

Используя данный программный продукт, вы подтверждаете, что принимаете на себя все риски, связанные с его использованием, включая, но не ограничиваясь, прямыми, косвенными, случайными или последующими убытками.

Автор настоящего репозитория является единственным разработчиком и правообладателем данного кода. Данное решение разработано и распространяется независимо и не является официальным продуктом или услугой компании Kaiten Software.

Компания Kaiten Software не несёт никакой ответственности за качество работы, производительность, результаты использования или любые последствия, связанные с использованием данного решения. Любые упоминания Kaiten Software приведены исключительно в информационных целях и не означают одобрения, поддержки или аффилированности.
