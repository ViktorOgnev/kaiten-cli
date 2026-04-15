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
- low-load HTTP client: throttling, bounded retry, explicit timeouts
- локальные transforms: `compact`, `fields`, strip-base64
- полный паритет по набору инструментов с текущим sibling `kaiten-mcp`
- strict alias-set regression против sibling `kaiten-mcp` registry
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

CLI читает переменные окружения только из текущего процесса или из сохранённого profile-конфига.

## Первые команды

Read-only smoke после настройки окружения:

```bash
export KAITEN_DOMAIN=sandbox
export KAITEN_TOKEN=your-api-token

kaiten --json spaces list --compact --fields id,title
kaiten describe cards.create
```

Если нужен постоянный локальный профиль:

```bash
kaiten profile add sandbox --domain sandbox --token "$KAITEN_TOKEN" --sandbox --set-active
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

Дополнительные инженерные заметки:

- [LIVE_VALIDATION.md](/Users/name/work/kaiten-cli/LIVE_VALIDATION.md)
- [API_BEHAVIOR_MATRIX.md](/Users/name/work/kaiten-cli/API_BEHAVIOR_MATRIX.md)
- [AGENTS.md](/Users/name/work/kaiten-cli/AGENTS.md)

## Дисклеймер

Настоящий репозиторий и размещённое в нём программное обеспечение предоставляются по принципу “как есть” (“as is”) и “по мере доступности” (“as available”), без каких-либо гарантий, явных или подразумеваемых. Автор не предоставляет никаких заверений и гарантий в отношении корректности, надёжности, безопасности, пригодности для конкретных целей или отсутствия ошибок в данном решении.

Используя данный программный продукт, вы подтверждаете, что принимаете на себя все риски, связанные с его использованием, включая, но не ограничиваясь, прямыми, косвенными, случайными или последующими убытками.

Автор настоящего репозитория является единственным разработчиком и правообладателем данного кода. Данное решение разработано и распространяется независимо и не является официальным продуктом или услугой компании Kaiten Software.

Компания Kaiten Software не несёт никакой ответственности за качество работы, производительность, результаты использования или любые последствия, связанные с использованием данного решения. Любые упоминания Kaiten Software приведены исключительно в информационных целях и не означают одобрения, поддержки или аффилированности.
