# Разработка и проверки

[README](../README.md) описывает установку и начало работы, а
[пользовательское руководство](USAGE.md) — специальные сценарии CLI.

## Окружение разработчика

Требуется Python 3.11 или новее. Из корня клонированного репозитория:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

В Windows PowerShell активируйте окружение командой `.\.venv\Scripts\Activate.ps1`.
После активации вместо `.venv/bin/python` и `.venv/bin/pytest` используйте `python` и `pytest`.
Версию установленного пакета проверяйте отдельно от версии checkout.

Для сборки и проверки JavaScript-помощника нужен Node.js 20+ и npm.
Порядок работы с исходниками и lock-файлом описан в
[руководстве помощника](../js/document-yjs/README.md).

## Структура репозитория

- `src/kaiten_cli/registry/`
  Каталог всех инструментов. Здесь объявляются `ToolSpec`, основные имена команд, псевдонимы, схемы и метаданные.
- `src/kaiten_cli/runtime/`
  Исполняемый слой: формирование запросов, HTTP-клиент, кэш, трассировка, локальное хранилище снимков данных и выполнение составных команд.
- `src/kaiten_cli/runtime/support/`
  Вспомогательные модули исполняемого слоя с заданными ограничениями.
- `src/kaiten_cli/`
  Стабильный интерфейс пакета и общие компоненты: `app.py`, `discovery.py`, `profiles.py`, `models.py`, `errors.py`.

Если коротко: `registry` описывает инструменты, а `runtime` выполняет их команды.

## Документация и статические проверки

Реестр `src/kaiten_cli/registry/` — источник истины для команд CLI.
`COMMAND_REFERENCE.md`, включая таблицу модулей, генерируется из него.
README и пользовательское руководство редактируются вручную.

```bash
.venv/bin/python scripts/generate_reference_docs.py --write
.venv/bin/python scripts/generate_reference_docs.py --check
.venv/bin/python scripts/check_locales.py
.venv/bin/ruff check src tests scripts
.venv/bin/ruff format --check src tests scripts
```

Карта системы находится в [ARCHITECTURE.md](../ARCHITECTURE.md).

## Тесты

Базовая локальная проверка:

```bash
.venv/bin/pytest -q
```

Проверка на реальном API запускается отдельно и только после успешных локальных тестов. Для её включения требуется `KAITEN_LIVE=1|true`. Данные доступа можно передать через переменные окружения или обычный активный профиль:

```bash
KAITEN_LIVE=true KAITEN_DOMAIN=<company-subdomain-or-url> KAITEN_TOKEN=... \
  .venv/bin/pytest -m live -o addopts='--disable-socket --allow-unix-socket' \
  tests/live/test_sandbox_live_full.py
```

Полный порядок, условия запуска и очистка данных — в [LIVE_VALIDATION.md](../LIVE_VALIDATION.md).

## Сравнение производительности

Для воспроизводимого сравнения последовательных запросов, массового чтения и работы с локальным снимком предусмотрен отдельный сценарий проверки в репозитории:

```bash
.venv/bin/python scripts/benchmark_reference_workflows.py --spec path/to/workflows.json
```

Он запускает заданные команды CLI, измеряет размер ответа в стандартном выводе и общее время выполнения, а также сохраняет трассировку JSONL. Это позволяет сравнивать не только время ответа, но и фактическое значение `http_request_count`.

## Выпуски

- каждый пользовательский выпуск сопровождается увеличением версии CLI и тегом Git вида `vX.Y.Z`;
- push стабильного тега запускает полный CI и публикацию проверенных wheel/sdist в PyPI; порядок настройки и выпуска описан в [инструкции](PYPI_PUBLISHING.md);
- слияние PR или push в `master` выполняет CI без загрузки пакета в PyPI;
- установка из ветки не обновляется автоматически: требуется явный запуск `uv tool upgrade kaiten-cli` или `pipx upgrade kaiten-cli`;
- установка с `@vX.Y.Z` закреплена на указанном теге и не переключается на следующий тег автоматически.

Публикация, проверки артефактов и сопровождение Homebrew описаны в
[инструкции по выпускам](PYPI_PUBLISHING.md). Изменение описания в PyPI требует
нового выпуска: текст README включается в метаданные пакета при сборке.
