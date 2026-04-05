# kaiten-cli

Нативный CLI для работы с [Kaiten](https://kaiten.ru), построенный как отдельный execution surface поверх того же доменного слоя, который раньше использовался для `kaiten-mcp`.

Проект не является MCP proxy и не импортирует `kaiten-mcp` в runtime.  
Источник истины для CLI — локальный registry в `src/kaiten_cli/registry/`.

## Что уже есть

- canonical commands: `kaiten <namespace...> <action>`
- MCP-compatible aliases: `kaiten kaiten_list_cards`
- `--json` с жёстким success/error envelope
- discovery-команды: `search-tools`, `describe`, `examples`
- profiles и sandbox mutation guard
- low-load HTTP client: throttling, bounded retry, explicit timeouts
- локальные transforms: `compact`, `fields`, strip-base64
- полный functional parity с текущим `kaiten-mcp`
- full live validation campaign на sandbox с teardown discipline

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

## Установка

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

После установки доступны:

```bash
.venv/bin/kaiten --help
.venv/bin/kaiten --json spaces list
.venv/bin/kaiten describe cards.create
```

## Примеры

```bash
.venv/bin/kaiten --json spaces list --compact --fields id,title
.venv/bin/kaiten --json boards list --space-id 679103 --compact
.venv/bin/kaiten --json cards create --title "Live task" --board-id 1540185
.venv/bin/kaiten --json projects cards list --project-id <uuid> --compact
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

Подробности и статусные классы см. в:

- [PLAN.md](/Users/name/work/kaiten-cli/PLAN.md)
- [LIVE_VALIDATION.md](/Users/name/work/kaiten-cli/LIVE_VALIDATION.md)
- [API_BEHAVIOR_MATRIX.md](/Users/name/work/kaiten-cli/API_BEHAVIOR_MATRIX.md)

## Дисклеймер

Настоящий репозиторий и размещённое в нём программное обеспечение предоставляются по принципу “как есть” (“as is”) и “по мере доступности” (“as available”), без каких-либо гарантий, явных или подразумеваемых. Автор не даёт гарантий корректности, надёжности, безопасности, пригодности для конкретной задачи и отсутствия ошибок.

Используя этот CLI, вы принимаете на себя все риски, связанные с его применением, включая прямые, косвенные, случайные и последующие убытки.

Данное решение разрабатывается и распространяется независимо и не является официальным продуктом или услугой компании Kaiten Software.
