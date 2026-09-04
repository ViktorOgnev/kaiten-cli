# kaiten-cli

`kaiten-cli` — это интерфейс командной строки для Kaiten. Он позволяет работать с данными и выполнять привычные действия прямо из терминала, без перехода в веб-интерфейс.

Его можно использовать самостоятельно или подключать к автоматизации: те же команды могут запускать человек, программа или LLM-агент.

Проект устанавливается напрямую из Git и использует тот же доменный слой, который ранее применялся в `kaiten-mcp`.

`kaiten-cli` работает самостоятельно: он не перенаправляет команды в MCP и не зависит от `kaiten-mcp` во время выполнения.

Источник истины для CLI — локальный реестр `src/kaiten_cli/registry/`.

## Быстрый старт

### Установка из Git

Рекомендуемый путь:

```bash
uv tool install git+https://github.com/ViktorOgnev/kaiten-cli.git
```

Альтернатива:

```bash
pipx install git+https://github.com/ViktorOgnev/kaiten-cli.git
```

Установка в локальное виртуальное окружение:

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

### Если команда `kaiten` не найдена

`uv tool` и `pipx` устанавливают исполняемые файлы в отдельный каталог. Если
после установки терминал сообщает, что команда не найдена, менеджер установки
должен добавить этот каталог в `PATH`.

Для установки через `uv`:

```bash
uv tool update-shell
```

Для установки через `pipx`:

```bash
pipx ensurepath
```

После этого терминал необходимо полностью закрыть и открыть заново, а затем
повторно выполнить `kaiten --version`.

Если команда по-прежнему не находится, фактический каталог исполняемых файлов
можно получить у того менеджера, через который установлен CLI:

```bash
uv tool dir --bin
pipx environment --value PIPX_BIN_DIR
```

На macOS и Linux с Bash или Zsh нужный каталог можно добавить в `PATH` текущего
терминала:

```bash
# uv
export PATH="$(uv tool dir --bin):$PATH"

# pipx
export PATH="$(pipx environment --value PIPX_BIN_DIR):$PATH"
```

Для постоянной настройки соответствующую строку `export PATH=...` необходимо
добавить в `~/.bashrc` для Bash или `~/.zshrc` для Zsh, а затем заново открыть
терминал.

В Windows PowerShell каталог можно добавить в `PATH` текущей сессии:

```powershell
# uv
$env:Path = "$(uv tool dir --bin);$env:Path"

# pipx
$env:Path = "$(pipx environment --value PIPX_BIN_DIR);$env:Path"
```

Для постоянной настройки в Windows каталог, выведенный менеджером, необходимо
добавить в пользовательскую переменную `Path`, а затем заново открыть терминал.
Для WSL применяется инструкция для Linux.

### Автодополнение команд

Обычная установка Python-пакета через `uv tool` или `pipx` не должна сама
изменять пользовательские настройки shell. После того как команда `kaiten`
стала доступна в `PATH`, автодополнение для текущего Bash или Zsh устанавливается
явной командой:

```bash
kaiten completion install
```

Команда определяет shell по переменной `SHELL`, создаёт статический completion-
скрипт и добавляет в `~/.bashrc` или `~/.zshrc` только маркированный блок
`kaiten-cli completion`. Повторный запуск обновляет этот блок без дублирования.
Перед изменением файлов доступен режим проверки:

```bash
kaiten completion install --dry-run
kaiten completion status
```

Если shell нужно указать явно:

```bash
kaiten completion install --shell zsh
kaiten completion install --shell bash
```

Click поддерживает Bash версии 4.4 и новее. На macOS системный Bash может быть
старее, а login-сессия Bash может не читать `~/.bashrc`; команда сообщит об этом
и предложит указать нужный startup-файл через `--config`.

После установки необходимо открыть новую сессию shell или выполнить команду,
которую напечатает CLI, например `exec zsh`. Проверить работу можно так:

```bash
kaiten cards <Tab>
kaiten cards list --<Tab>
```

Для ручной настройки можно вывести скрипт без изменения файлов:

```bash
kaiten completion source zsh
kaiten completion source bash
```

Удаление затрагивает только созданный скрипт и управляемый блок:

```bash
kaiten completion uninstall
```

Встроенная установка completion сейчас поддерживает Bash и Zsh. Для Fish и
PowerShell необходимо использовать отдельную ручную настройку.

### Рекомендации для LLM-агентов

Рекомендуемые сценарии работы агентов с CLI описаны в отдельных файлах навыков:

- [skills/kaiten-cli-heavy-data/SKILL.md](skills/kaiten-cli-heavy-data/SKILL.md)  
  Как избежать множества отдельных запросов, когда использовать массовое чтение, а когда создавать локальный снимок данных.
- [skills/kaiten-cli-metrics/SKILL.md](skills/kaiten-cli-metrics/SKILL.md)  
  Как рассчитывать канбан-метрики по локальному снимку данных и не запрашивать историю каждой карточки отдельно.
- [skills/kaiten-cli-mutations/SKILL.md](skills/kaiten-cli-mutations/SKILL.md)
  Как безопасно планировать и выполнять изменения с точным preview, возобновляемым manifest и проверкой изменённых полей.

### Обновление

Если CLI установлен по адресу ветки Git, обновление выполняется вручную:

```bash
uv tool upgrade kaiten-cli
pipx upgrade kaiten-cli
```

По умолчанию используется текущая версия из ветки `master`. Установку можно закрепить на конкретном выпуске с помощью тега:

```bash
uv tool install "git+https://github.com/ViktorOgnev/kaiten-cli.git@v0.1.28"
```

После успешной команды в интерактивном терминале CLI не чаще одного раза в сутки
проверяет стабильные теги `vX.Y.Z` в том же Git-репозитории. Если найден новый
релиз, появляется вопрос `Update now ...? [y/N]`. Основная команда к этому
моменту уже завершена; подтверждённое обновление применяется со следующего запуска.

Способ обновления соответствует способу установки:

- `uv tool` → `uv tool upgrade kaiten-cli`;
- `pipx` → `pipx upgrade kaiten-cli`;
- виртуальное окружение и pip → текущий `python -m pip install --upgrade <git-source>`.

Для установки, закреплённой на `@vX.Y.Z`, подтверждение заменяет текущий тег на
новый с помощью того же менеджера. Проверка не запускается в режиме `--json`,
в неинтерактивном терминале, для команд справки и версии, при настройке
автодополнения оболочки, для локальной установки в режиме `editable`, wheel-файла
или неизвестного источника. Ошибки сети и проверки тегов не влияют на результат
основной команды.

Разово отключить проверку можно флагом `--no-update-check`, постоянно —
переменной окружения:

```bash
export KAITEN_CLI_UPDATE_CHECK=0
```

Результат проверки и 24-часовой интервал хранятся локально в закрытом файле
`update-check.json` в каталоге кэша `kaiten-cli`. Данные доступа к Git в него не
записываются.

Если пакет установлен в текущем окружении Python, его также можно запустить как модуль:

```bash
python -m kaiten_cli --help
```

## Карта документации

- [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md)
  Полный автоматически созданный справочник по основным командам и их псевдонимам MCP.
- [ARCHITECTURE.md](ARCHITECTURE.md)
  Архитектурная карта, режимы выполнения и устройство документации.
- [AGENTS.md](AGENTS.md)
  Краткое руководство для агентов и порядок знакомства с возможностями CLI.
- [LIVE_VALIDATION.md](LIVE_VALIDATION.md)
  Как устроена явно включаемая проверка на реальном API.
- [API_BEHAVIOR_MATRIX.md](API_BEHAVIOR_MATRIX.md)
  Подтверждённые особенности API текущего тестового контура.
- [SECURITY.md](SECURITY.md)
  Правила сообщения об уязвимостях и обращения с локальными данными доступа.
- [skills/kaiten-cli-heavy-data/SKILL.md](skills/kaiten-cli-heavy-data/SKILL.md)
  Рекомендации по массовому чтению данных для LLM-агентов и автоматических сценариев.
- [skills/kaiten-cli-metrics/SKILL.md](skills/kaiten-cli-metrics/SKILL.md)
  Рекомендации по расчёту метрик для LLM-агентов и автоматических сценариев.
- [skills/kaiten-cli-mutations/SKILL.md](skills/kaiten-cli-mutations/SKILL.md)
  Безопасный процесс изменения карточек и других сущностей через CLI.

## Что уже есть

- основные команды вида `kaiten <namespace...> <action>`;
- совместимые с MCP псевдонимы, например `kaiten kaiten_list_cards`;
- вывод версии и запуск как модуля: `--version`, `python -m kaiten_cli`;
- единая структура успешных ответов и ошибок в режиме `--json`, включая статистику выполнения `stats`;
- команды поиска и изучения возможностей: `search-tools`, `describe`, `examples`;
- профили доступа и явное включение проверки на реальном API через `KAITEN_LIVE`;
- кэш GET-запросов в пределах одного запуска;
- адаптивный постоянный дисковый кэш в режиме `--cache-mode auto` для повторного чтения и ресурсоёмкой аналитики;
- локальные снимки данных в SQLite для автоматической аналитики и повторного построения отчётов;
- локальные команды `query cards` и `query metrics` для работы со снимками данных;
- экспорт карточек и документов в Markdown через команды `cards get` и `documents get`;
- HTTP-клиент с ограничением частоты запросов, повторными попытками и явными ограничениями времени ожидания;
- локальное сокращение ответов с помощью `compact`, `fields` и удаления данных в формате base64;
- полное соответствие набора инструментов текущему снимку локального реестра;
- автоматическая проверка набора псевдонимов по сохранённому эталону;
- полная проверка на реальном API с явным включением и обязательной очисткой тестовых данных.

## Дашборды, итерации и private files

Дашборды доступны как experimental-контракт: старые инсталляции Kaiten могут
вернуть `404` или `405`. CLI поддерживает CRUD, копирование, роли
`viewer`/`editor`, виджеты и compute jobs. Список виджетов читается через
`dashboards get --include widgets`, а polling compute job всегда обходит кэш.

```bash
kaiten --json dashboards list --fields id,title,is_public,role --compact
kaiten --json dashboards get --dashboard-id <dashboard_uuid> --include widgets
kaiten --json dashboard-widgets list --dashboard-id <dashboard_uuid> --fields id,title,source,visualization
kaiten --json dashboard-compute-jobs get --dashboard-id <dashboard_uuid> --job-id <job_id>
```

Iterations API и private files помечены как beta. Итерации требуют поддержки в
тарифе. Private files используют UUID сущностей и multipart `POST`; классическая
команда `files upload` по-прежнему использует прежний публичный `PUT`-контракт.

```bash
kaiten --json iterations list --space-uid <space_uuid> --status planned,active --with-data cards --compact
kaiten --json iteration-cards list --space-uid <space_uuid> --iteration-id <iteration_uuid>
kaiten --json card-iterations-history list --card-uid <card_uuid>
kaiten --json private-card-files upload --card-uid <card_uuid> --file ./report.pdf
kaiten --json files download --entity-type card --card-uid <card_uuid> --file-id <private_file_uuid>
```

Для полного экспорта пользователей компании используется bounded pagination:

```bash
kaiten --json company-users list-all --page-size 100 --max-pages 100 --fields id,uid,email,full_name --compact
```

Если последняя разрешённая страница заполнена полностью, команда завершится
ошибкой вместо возврата незаметно обрезанного списка.

## Экспорт в Markdown и работа с файлами

Экспорт в Markdown не требует отдельного метода API или отдельной команды. По умолчанию `cards get` и `documents get` возвращают JSON. Флаг `--markdown` преобразует тот же ответ в Markdown и сохраняет его в локальный файл `.md`.

```bash
kaiten --json documents get --document-uid <document_uid> --markdown --output ./document.md
kaiten --json cards get --card-id 123 --markdown --output ./card.md
```

`--output` может быть файлом или директорией. Если путь не передан, файл пишется в текущую директорию с именем из заголовка и ID. Существующий файл не перезаписывается без `--overwrite`.

Ссылки на вложения в Markdown нормализуются в Kaiten API-формат:

```text
/api/documents/<document_uid>/files/<file_uid>
/api/cards/<card_id_or_uid>/files/<file_uid>
```

Это ссылки для последующего использования, а не сами двоичные данные. Команда `files download` скачивает файл из карточки, документа или сохранённого Markdown. Она сама получает временную ссылку на хранилище и по умолчанию продолжает загрузку частично сохранённого файла `.part` с помощью HTTP Range, как `wget --continue`.

```bash
kaiten --json files download --entity-type document --document-uid <document_uid> --file-id <file_uid> --output ./downloads/
kaiten --json files download --entity-type card --card-id 123 --file-id <file_uid> --output ./downloads/
kaiten --json files download --url "https://hq.kaiten.ru/api/documents/<document_uid>/files/<file_uid>" --output ./downloads/
```

Команда `files upload` загружает локальный файл в карточку и отправляет `multipart/form-data` с полем `file` в публичный метод API Kaiten для файлов карточки.

```bash
kaiten --json files upload --card-id 123 --file ./report.json
```

Новый запуск CLI не использует результат предыдущей команды, оставшийся в памяти. По умолчанию режим `--cache-mode auto` сохраняет на диск ответы на подходящие запросы чтения и автоматически выбирает срок их хранения. Режим `--cache-mode refresh` следует использовать, когда важно получить актуальные данные.

```bash
kaiten --json --cache-mode refresh documents get --document-uid <document_uid> --markdown --output ./document.md --overwrite
```

## Каталоги

В интерфейсе Kaiten эта сущность называется «Каталоги»: это таблицы или базы данных, например со списками клиентов, контактов, оборудования или подрядчиков. В API для разработчиков тот же объект называется `custom-directories`, поэтому в CLI используются следующие команды:

```bash
kaiten --json custom-directories list --include-fields --include-records-count
kaiten --json custom-directory-fields list --directory-id <directory_uuid>
kaiten --json custom-directory-records list --directory-id <directory_uuid> --profile summary
kaiten --json custom-directory-records cards list --directory-id <directory_uuid> --record-id <record_uuid>
```

`custom-directories` управляет самим каталогом, `custom-directory-fields` — его колонками, а `custom-directory-records` — строками или записями. Поле карточки типа «Справочник» представлено как `custom-properties` с типом API `catalog`. Команды `custom-properties catalog-values ...` работают со значениями такого поля и не предназначены для создания, чтения, изменения или удаления каталогов.

Если в запросе указано только «каталог», «справочник» или `catalog`, перед изменением данных необходимо уточнить, какая сущность имеется в виду:

| Что имелось в виду | Пространство имён CLI |
|---|---|
| Раздел «Каталоги» в веб-интерфейсе, таблица с колонками и записями | `custom-directories`, `custom-directory-fields`, `custom-directory-records` |
| Само поле карточки типа «Справочник» с типом API `catalog` | `custom-properties` с `type=catalog` |
| Значения поля карточки типа «Справочник» с типом API `catalog` | `custom-properties catalog-values` |
| Папка/контейнер документов в дереве | `document-groups`, `tree` для чтения структуры |

## Аддоны и GitHub-аддон

Аддон хранит своё состояние карточки не во внешних ссылках, а в данных аддона:
одна общая строка на карточку плюс приватная строка на пользователя. Доступ к
этому хранилищу дают команды `card-addon-data` и `user-addon-data`, список
установленных аддонов – `addons list` и `space-addons list`.

Адресация идёт по UUID аддона, а не по имени. На self-hosted UUID детерминированно
выводится из пути монтирования, поэтому его можно получить локально, без запроса
к Kaiten:

```bash
kaiten --json addons uid --url-path /github          # /github -> 0ce23a01-560f-51e0-9982-1e3445dc5990
kaiten --json addons list --fields id,name
kaiten --json space-addons list --space-id <space_id> --fields id,name
```

GitHub-аддон показывает на карточке pull request'ы, ветки, коммиты и issues.
Отдельные команды `github-addon` читают и пишут именно его хранилище, сохраняя
формат виджета и дедуплицируя записи, поэтому запись из CLI неотличима от
добавленной через интерфейс аддона:

```bash
kaiten --json github-addon pulls list --card-id <card_id> --fields number,htmlUrl,state
gh api repos/OWNER/REPO/pulls/NUMBER > pull.json
kaiten --json github-addon pulls attach --card-id <card_id> --pull-json @pull.json --dry-run
kaiten --json github-addon pulls attach --card-id <card_id> --pull-json @pull.json
kaiten --json github-addon pulls detach --card-id <card_id> --number NUMBER --owner OWNER --repo REPO
```

Сам CLI в GitHub не ходит: объект PR, ветки, коммита или issue передаётся снаружи
(`gh api` или любой другой источник) и отображается в формат аддона.

Репозиторий – часть идентичности записи: виджет обновляет каждое вложение запросом
в GitHub по владельцу, репозиторию и номеру (имени, sha). Поэтому для веток,
коммитов и issues обязательны `--owner` и `--repo` – в ответе GitHub этих полей нет.
Для PR они берутся из `base.repo`; урезанный payload без него (например
`gh pr view --json id,number,url`) отклоняется, пока `--owner` и `--repo` не заданы
явно.

`detach` отказывается работать, если селектор попадает больше чем в одну запись:
номер PR или имя ветки уникальны только внутри репозитория. Уточните `--owner` и
`--repo` либо передайте `--all`, если удалить нужно все совпадения.

Запись требует права `card.update` в пространстве карточки и установленного там
GitHub-аддона. `--dry-run` выполняет чтение и показывает результат, ничего не
записывая; так как команда считается изменяющей, в режиме `--read-only` она
заблокирована – для безопасного осмотра используйте `github-addon ... list`,
это обычное чтение. PR у карточки могут лежать и во внешних ссылках, поэтому при
полном поиске стоит смотреть и `external-links list`.

## Инструменты

<!-- BEGIN GENERATED COMMAND SUMMARY -->
В `kaiten-cli` доступно **410** основных инструментов. Количество модулей реестра: **35**. Полный список команд: [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md).

| Область | Модуль | Инструментов | Справочник |
|---|---|---:|---|
| Карточки | `cards` | 15 | [Раздел](COMMAND_REFERENCE.md#module-cards) |
| Комментарии | `comments` | 5 | [Раздел](COMMAND_REFERENCE.md#module-comments) |
| Участники и пользователи | `members` | 7 | [Раздел](COMMAND_REFERENCE.md#module-members) |
| Логи времени | `time_logs` | 6 | [Раздел](COMMAND_REFERENCE.md#module-time-logs) |
| Теги | `tags` | 7 | [Раздел](COMMAND_REFERENCE.md#module-tags) |
| Чеклисты | `checklists` | 17 | [Раздел](COMMAND_REFERENCE.md#module-checklists) |
| Блокировки | `blockers` | 12 | [Раздел](COMMAND_REFERENCE.md#module-blockers) |
| Связи карточек | `card_relations` | 10 | [Раздел](COMMAND_REFERENCE.md#module-card-relations) |
| Внешние ссылки | `external_links` | 4 | [Раздел](COMMAND_REFERENCE.md#module-external-links) |
| Файлы карточек | `files` | 12 | [Раздел](COMMAND_REFERENCE.md#module-files) |
| Подписчики | `subscribers` | 6 | [Раздел](COMMAND_REFERENCE.md#module-subscribers) |
| Пространства | `spaces` | 6 | [Раздел](COMMAND_REFERENCE.md#module-spaces) |
| Доски | `boards` | 6 | [Раздел](COMMAND_REFERENCE.md#module-boards) |
| Колонки и подколонки | `columns` | 8 | [Раздел](COMMAND_REFERENCE.md#module-columns) |
| Дорожки | `lanes` | 4 | [Раздел](COMMAND_REFERENCE.md#module-lanes) |
| Типы карточек | `card_types` | 8 | [Раздел](COMMAND_REFERENCE.md#module-card-types) |
| Каталоги | `custom_directories` | 16 | [Раздел](COMMAND_REFERENCE.md#module-custom-directories) |
| Пользовательские свойства | `custom_properties` | 25 | [Раздел](COMMAND_REFERENCE.md#module-custom-properties) |
| Документы | `documents` | 13 | [Раздел](COMMAND_REFERENCE.md#module-documents) |
| Дашборды | `dashboards` | 16 | [Раздел](COMMAND_REFERENCE.md#module-dashboards) |
| Итерации | `iterations` | 9 | [Раздел](COMMAND_REFERENCE.md#module-iterations) |
| Вебхуки | `webhooks` | 9 | [Раздел](COMMAND_REFERENCE.md#module-webhooks) |
| Автоматизации и рабочие процессы | `automations` | 11 | [Раздел](COMMAND_REFERENCE.md#module-automations) |
| Проекты и спринты | `projects` | 13 | [Раздел](COMMAND_REFERENCE.md#module-projects) |
| Роли и группы | `roles_and_groups` | 31 | [Раздел](COMMAND_REFERENCE.md#module-roles-and-groups) |
| SCIM | `scim` | 8 | [Раздел](COMMAND_REFERENCE.md#module-scim) |
| Аудит и аналитика | `audit_and_analytics` | 12 | [Раздел](COMMAND_REFERENCE.md#module-audit-and-analytics) |
| Service Desk | `service_desk` | 47 | [Раздел](COMMAND_REFERENCE.md#module-service-desk) |
| Графики и аналитика | `charts` | 15 | [Раздел](COMMAND_REFERENCE.md#module-charts) |
| Дерево сущностей | `tree` | 9 | [Раздел](COMMAND_REFERENCE.md#module-tree) |
| Утилиты | `utilities` | 15 | [Раздел](COMMAND_REFERENCE.md#module-utilities) |
| Локальные снимки | `snapshot` | 5 | [Раздел](COMMAND_REFERENCE.md#module-snapshot) |
| Локальные запросы | `query` | 2 | [Раздел](COMMAND_REFERENCE.md#module-query) |
| Аддоны | `addons` | 9 | [Раздел](COMMAND_REFERENCE.md#module-addons) |
| GitHub-аддон | `github_addon` | 12 | [Раздел](COMMAND_REFERENCE.md#module-github-addon) |
| **Итого** | **35** | **410** | [Полный справочник](COMMAND_REFERENCE.md) |
<!-- END GENERATED COMMAND SUMMARY -->

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

## Требования

- Python >= 3.11
- учётная запись Kaiten или отдельный тестовый контур с токеном API
- токен API Kaiten

## Переменные окружения

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `KAITEN_DOMAIN` | Да | Поддомен компании (`company`), полный адрес Kaiten (`https://company.kaiten.ru`) или другой адрес сервера (`62.84.125.64:3200`, `http://localhost:3000`) |
| `KAITEN_TOKEN` | Да | API-токен пользователя |
| `KAITEN_LIVE` | Нет | `1` или `true` для явного запуска проверки на реальном API с указанными данными доступа или профилем |
| `KAITEN_CLI_READ_ONLY` | Нет | `1` или `true`, чтобы блокировать команды, изменяющие данные Kaiten в текущем процессе |
| `KAITEN_CLI_STORAGE_READ_ONLY` | Нет | `1` или `true`, чтобы читать существующие локальные снимки без изменения схемы и данных и блокировать их создание, обновление и удаление; шлюз для агентов устанавливает значение автоматически |
| `KAITEN_CLI_UPDATE_CHECK` | Нет | `0`, `false`, `no` или `off`, чтобы отключить проверку новых тегов Git после выполнения команды |
| `KAITEN_CLI_CONFIG_PATH` | Нет | Путь к файлу профилей и настроек |
| `KAITEN_TRACE_FILE` | Нет | JSONL-файл для последовательной записи сведений о выполненных командах |

CLI читает переменные окружения текущего процесса и настройки сохранённого профиля.

## Настройка доступа

Рекомендуемый путь: сохранить профиль и сделать его активным.

```bash
kaiten profile add main --domain <company-subdomain-or-url> --token <api-token> --set-active
kaiten profile show
```

`--domain` и `KAITEN_DOMAIN` принимают поддомен компании (`company`), полный адрес Kaiten (`https://company.kaiten.ru`) или другой адрес с портом для локальной установки и среды разработки.

Если для профиля требуется фиксированный срок хранения постоянного кэша вместо автоматического режима `auto`:

```bash
kaiten profile add main \
  --domain <company-subdomain-or-url> \
  --token <api-token> \
  --cache-mode readwrite \
  --cache-ttl-seconds 60 \
  --set-active
```

Временная настройка через переменные окружения:

```bash
export KAITEN_DOMAIN=<company-subdomain-or-url>
export KAITEN_TOKEN=<api-token>
```

Параметр `--sandbox` команды `profile add` сохранён только для обратной совместимости и считается устаревшим. Он не разрешает изменение данных и не влияет на запуск проверок на реальном API.

### Режим только для чтения

По умолчанию обычный профиль может изменять данные. Для аналитики и работы агентов предусмотрен явный режим только для чтения:

```bash
kaiten --read-only --json spaces list --compact --fields id,title
KAITEN_CLI_READ_ONLY=1 kaiten --json cards get --card-id 123
```

Режим блокирует команды, которые изменяют данные в Kaiten. Операции с локальными снимками остаются доступны: они записывают данные только в локальную базу SQLite и обращаются к API Kaiten для чтения. Аналитические команды чтения `charts summary get`, `charts block-resolution get` и `charts due-dates get`, использующие POST-запросы, также разрешены. Команды `charts ... create`, создающие временную вычислительную задачу, блокируются. Команды `search-tools` и `describe` возвращают поле `read_only_allowed`, поэтому автоматизация не должна определять допустимость операции только по методу HTTP или полю `mutation`.

Шлюз для агентов передаёт дочернему процессу CLI переменные `KAITEN_CLI_READ_ONLY=1` и `KAITEN_CLI_STORAGE_READ_ONLY=1`, ограничивает файловую систему режимом чтения и отключает пользовательские настройки и правила Codex. Поэтому процесс может читать существующие локальные снимки, но не может создавать, обновлять или удалять их. Это защита от случайной записи, а не полная граница безопасности: процесс Codex сохраняет доступ к оболочке и данным доступа Kaiten. Шлюз следует использовать только для доверенного ввода и, по возможности, с учётной записью, серверные права которой не допускают запись. При доступе не только с локального компьютера обязательны токен Bearer, обратный прокси-сервер с TLS или закрытая сеть, а также ограничения соединений и времени ожидания на уровне прокси-сервера. Встроенный сервер не поддерживает TLS самостоятельно.

### Проверка выбранного профиля

Перед изменениями можно проверить, что CLI разрешил ожидаемый профиль и что его
данные доступа проходят аутентификацию:

```bash
kaiten --json --profile main --read-only profile probe
```

Команда выполняет только `GET /users/current`, принудительно обходит постоянный
кэш и возвращает обезличенные сведения о resolved profile. Она различает ошибки
конфигурации, 401, 403 и транспортные сбои, но не проверяет и не обещает наличие
произвольных прав на запись.

### Безопасный процесс изменений

Для мутаций используйте
[skills/kaiten-cli-mutations/SKILL.md](skills/kaiten-cli-mutations/SKILL.md):
discovery → read-only investigation → точный preview → явная авторизация →
возобновляемый manifest → малые пачки → field-scoped readback. Универсального
автоматического mutation runner в CLI нет: для повторяющихся операций сначала
используются этот процесс и существующие batch-команды.

### Приоритет конфигурации

CLI определяет данные доступа в следующем порядке:

1. `--profile <name>`
2. активный профиль из файла настроек
3. `KAITEN_DOMAIN` и `KAITEN_TOKEN` из переменных окружения

Сохранённый активный профиль имеет приоритет над переменными окружения, если явно не передан другой `--profile`. Это правило одинаково для локального использования и работы агентов.

## Ввод данных и сокращение ответа

CLI поддерживает три способа передачи входных данных:

- обычные параметры командной строки: `kaiten cards list --board-id 10 --limit 5`;
- `--from-file payload.json` для полного объекта JSON из файла;
- `--stdin-json` для объекта JSON из стандартного ввода.

Сложные объекты и массивы можно передавать как значение параметра JSON или вынести в файл. Для большого тела запроса `--from-file` обычно надёжнее и требует меньше токенов LLM, чем длинная строка аргументов.

Чтобы сократить время выполнения, размер ответа и расход токенов при последующей обработке:

- следует использовать `--compact`, если команда поддерживает этот параметр;
- набор полей можно ограничить через `--fields id,title,...`;
- поля в формате base64 автоматически удаляются из ответа.

Некоторые команды выполняют больше одного прямого запроса:

- `direct_http`: один HTTP-запрос к API Kaiten;
- `synthetic`: результат формируется по запасному сценарию или с учётом структуры ответа;
- `aggregated`: CLI выполняет ограниченную постраничную загрузку или несколько запросов чтения и объединяет результат.

Команды `describe <tool>` и `search-tools <query>` показывают эти метаданные. Их рекомендуется проверять перед запуском ресурсоёмких команд.

## Дерево сущностей

`tree.get` и `tree.children.list` относятся к типу `aggregated`: они собирают локальный каталог пространств, документов и групп документов, а затем строят дерево.

- `/spaces` читается одним запросом.
- `/documents` и `/document-groups` читаются внутренней пагинацией по `limit=500` с `offset=0,500,1000...` до первой короткой страницы.
- Пользователю не нужно и нельзя передавать `limit`, `offset`, `page-size` или `max-pages` для `tree.get`: публичные параметры остаются `root_uid` и `depth`.
- Если внутренний защитный предел достигнут на полной странице, CLI завершает работу с ошибкой и не возвращает незаметно обрезанное дерево.
- Видимые сущности с отсутствующим или недоступным `parent_entity_uid` показываются на верхнем уровне полного дерева.

Примеры:

```bash
kaiten --json tree get --depth 1
kaiten --json tree get --root-uid <uid> --depth 0
kaiten --json --cache-mode refresh tree get --depth 1
```

### Публичные ссылки на сущности дерева

Команды `tree-entities share` позволяют получить уже существующую публичную ссылку или управлять публикацией пространства, документа, группы документов или карты историй. CLI возвращает готовый URL вида `<адрес-профиля>/p/<share-uid>`; это отдельный механизм общих сущностей, не поле `public` документа и не публикация публичной базы знаний.

Получение и создание одной ссылки идемпотентны:

```bash
kaiten --json tree-entities share get --entity-uid <entity-uuid>
kaiten --json tree-entities share enable --entity-uid <entity-uuid>
kaiten --json tree-entities share update --entity-uid <entity-uuid> --expired-at "2099-01-01T00:00:00Z"
kaiten --json tree-entities share update --entity-uid <entity-uuid> --expired-at null
kaiten --json tree-entities share disable --entity-uid <entity-uuid>
```

Для массовой публикации передаётся явный массив UUID. CLI не публикует автоматически найденное поддерево, удаляет дубликаты с сохранением исходного порядка и возвращает успешные элементы, ошибки по отдельным сущностям и счётчики `changed`/`unchanged`:

```bash
kaiten --json tree-entities share batch-get --entity-uids '["<entity-uuid-1>","<entity-uuid-2>"]'
kaiten --json tree-entities share batch-enable --entity-uids '["<entity-uuid-1>","<entity-uuid-2>"]' --workers 2
```

Число параллельных работников ограничено диапазоном от 1 до 6, по умолчанию используется 2. Повторный запуск безопасен: активные ссылки возвращаются без изменений, а отключённые или истёкшие ссылки реактивируются с прежним `share-uid`.

## Как работает кэш

В CLI есть два вида кэша. Автоматический режим `auto` позволяет повторно использовать данные, сохранённые на диске.

- В пределах одного запуска (`request-scoped`)
  Работает автоматически внутри одного запуска `kaiten`.
- Постоянный (`persistent`)
  Сохраняется между запусками CLI. В режиме `auto` используется для подходящих запросов чтения, а срок хранения выбирается с учётом стоимости запроса.

### Что происходит без флагов

Если запустить обычную команду вроде:

```bash
kaiten --json cards get --card-id 123
```

CLI работает в режиме `--cache-mode auto`: запросы чтения сущностей и справочных данных могут использовать дисковый кэш, а ресурсоёмкие составные и пакетные команды получают более длительный срок хранения. Кэш в пределах одного запуска также предотвращает повторные и одновременно выполняемые одинаковые GET-запросы.

### Когда кэш особенно полезен

- Одиночный запрос
  Для одного GET-запроса польза кэша обычно незаметна.
- Составные команды типов `aggregated` и `synthetic`
  Встроенный кэш исключает повторные чтения внутри одного запуска.
- Сценарий терминала или LLM-агента
  Если один и тот же GET-запрос выполняется из нескольких процессов CLI, режим `auto` сохраняет пригодный для повторного использования дисковый кэш.
- Ресурсоёмкая аналитика
  Для команды, которая загружает много страниц, выполняет много запросов по карточкам или читает закрытый исторический период, срок хранения автоматически увеличивается.
- Плотные циклы чтения сущностей
  Если внешний сценарий недавно выполнил много однотипных запросов, например `/cards/<id>`, режим `auto` увеличивает срок хранения для этой группы записей.

### Режимы постоянного кэша

- `--cache-mode auto`
  Рекомендуемый режим по умолчанию. Для обычного workflow флаг можно не
  указывать. Режим читает и записывает дисковый кэш для подходящих запросов
  чтения; срок хранения зависит от правил кэширования, размера ответа и давности
  запрошенного периода.
- `--cache-mode off`
  Использует кэш только в пределах текущего запуска. Предназначен для диагностики
  кэша, privacy-требований и высокочастотного polling быстро меняющихся данных.
- `--cache-mode readwrite`
  Читает и записывает постоянный дисковый кэш с фиксированным сроком. Этот режим
  всегда следует сопровождать осмысленным `--cache-ttl-seconds`.
- `--cache-mode refresh`
  Не использует сохранённый ответ, запрашивает данные из API и обновляет кэш.
  Применяется один раз перед freshness-critical результатом, а не к каждому
  вызову и никогда не внутри цикла по сущностям. Для снимка используйте
  `snapshot refresh`.
- `--cache-ttl-seconds`
  Задаёт срок хранения постоянного кэша. Значение можно передать отдельной команде или сохранить в профиле.

### Что кэшируется и что нет

Постоянный кэш учитывает стоимость запросов:

- подходит для чтения справочных данных и отдельных сущностей;
- полезен для обычных команд `*.get`, команд получения списков, пакетного чтения и составной постраничной загрузки;
- для ресурсоёмких команд, включая `cards.list-all`, `space-activity-all.get`, `card-location-history.batch-get`, `comments.batch-list`, `card-children.batch-list` и `time-logs.batch-list`, режим `auto` устанавливает более длительный срок хранения, чтобы повторный сценарий не собирал тот же массив заново;
- для плотных серий однотипных запросов срок хранения увеличивается по группе путей, чтобы внешний сценарий не потерял уже собранную выборку слишком быстро;
- не предназначен для частого опроса быстро меняющихся данных;
- очищается после успешной команды, изменяющей данные текущего профиля и домена;
- при несовместимой схеме SQLite или повреждённом файле автоматически удаляется и создаётся заново.

Ключ кэша строится по исходным параметрам запроса API: `profile/domain + credential fingerprint + method + path + params`. Параметры `compact` и `fields` в ключ не входят, поскольку применяются после получения ответа API.

### Состав и очистка локального кэша

Постоянный кэш содержит исходные ответы API Kaiten и может включать названия, описания, пользовательские данные и другие закрытые поля. Файл `http-cache.sqlite3` хранится в стандартном пользовательском каталоге кэша операционной системы: `~/Library/Caches/kaiten-cli/` в macOS или `${XDG_CACHE_HOME:-~/.cache}/kaiten-cli/` в Linux. Доступ к файлу получает только текущий пользователь. Файл нельзя прикладывать к сообщению об ошибке, отчёту или Git-репозиторию без предварительной очистки данных.

- `--cache-mode off` отключает чтение и запись постоянного кэша для текущего запуска.
- `--cache-mode refresh` обновляет данные конкретного запроса, но не очищает всё хранилище.
- Для полной очистки необходимо завершить процессы `kaiten` и удалить `http-cache.sqlite3`. CLI создаст файл заново при следующем подходящем запросе чтения.

### Примеры

Повторное чтение в режиме `auto`:

```bash
kaiten --json cards get --card-id 123 --compact --fields id,title,state
```

Принудительное получение актуальных данных:

```bash
kaiten --json --cache-mode refresh spaces list --compact --fields id,title
```

Пример, в котором режим `auto` сохраняет ответы по отдельным карточкам для повторных сценариев с пересекающимися идентификаторами:

```bash
kaiten --json card-location-history batch-get --card-ids '[101,102,103]' --workers 2 --fields changed,column_id
```

Рекомендации по массовому чтению больших объёмов данных приведены в [skills/kaiten-cli-heavy-data/SKILL.md](skills/kaiten-cli-heavy-data/SKILL.md), а по аналитическим сценариям — в [skills/kaiten-cli-metrics/SKILL.md](skills/kaiten-cli-metrics/SKILL.md).

## Массовое чтение данных

Если требуется выполнить сотни однотипных запросов, не следует запускать отдельный процесс `kaiten` для каждого объекта.

- Для массового получения истории перемещений предназначена команда `card-location-history.batch-get`, которая заменяет цикл из `card-location-history.get`.
- Для дополнения карточек подробными данными предназначена `cards.batch-get`, которая заменяет цикл из `cards.get`.
- Для анализа журналов времени предназначена `time-logs.batch-list`, которая заменяет цикл из `time-logs.list`.
- Для исследования связей карточек предназначена `card-children.batch-list`, которая заменяет цикл из `card-children.list`.
- Для массового чтения комментариев предназначена `comments.batch-list`, которая заменяет цикл из `comments.list`.
- Для получения полной выборки карточек предназначена `cards.list-all --selection all|active_only|archived_only`.
- Для построения структуры пространства предназначена `space-topology.get`, которая заменяет последовательность `boards.list`, `columns.list` и `lanes.list`.
- `cards.list-all --selection active_only` представлена в CLI как `all_cards - archived_subset`, поэтому внешнему сценарию не требуется воспроизводить эту логику.
- Для множества повторных GET-запросов к справочным данным и сущностям следует сохранять режим `--cache-mode auto`. Режим `--cache-mode readwrite` нужен только при фиксированном сроке хранения.

Примеры:

```bash
kaiten --json card-location-history batch-get --card-ids '[101,102,103]' --workers 2
kaiten --json cards batch-get --card-ids '[101,102,103]' --workers 2 --fields id,title,description
kaiten --json time-logs batch-list --card-ids '[101,102,103]' --workers 2 --fields id,time_spent,for_date
kaiten --json card-children batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,title
kaiten --json comments batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,text
kaiten --json cards list-all --board-id 10 --selection active_only --fields id,title,state
kaiten --json space-topology get --space-id 10
kaiten --json cards get --card-id 101 --compact --fields id,title,state
```

## Сбор данных для исследований и отчётов

При построении отчёта агентом или внешней программой сначала следует собрать данные с помощью массовых команд, а затем переходить к обработке:

- `space-topology.get` получает доски, колонки и дорожки одним вызовом CLI;
- `cards.list-all` формирует исходную выборку карточек;
- `cards.batch-get` дополняет карточки подробными данными после локального сужения выборки;
- `time-logs.batch-list` получает журналы времени без отдельного цикла по каждой карточке;
- `space-activity-all.get` заменяет ручную постраничную загрузку через `space-activity.get`;
- `card-children.batch-list` и `comments.batch-list` заменяют отдельные циклы чтения связей и комментариев каждой карточки;
- `card-location-history.batch-get` используется только тогда, когда действительно нужна история перемещений.

Для последующего анализа стоимости и эффективности сценария можно включить трассировку команд:

```bash
kaiten --json --trace-file ./kaiten-trace.jsonl cards list-all --board-id 10 --selection active_only
```

Трассировка обязательна для wrapper-сценария из трёх и более CLI-команд, более
чем десяти ожидаемых HTTP-запросов или неизбежного цикла. Локальная потоковая
сводка не обращается к Kaiten API и не возвращает argv или payload:

```bash
kaiten --json trace summarize --file ./kaiten-trace.jsonl
```

Обычный ответ `--json` уже содержит раздел верхнего уровня `stats`: длительность
команды, фактическое количество HTTP-запросов к API, время ожидания API,
количество попаданий и промахов кэша, фактические `mode`, `policy`,
`ttl_seconds`, а также сводные данные по методам и группам путей. Трассировка
записывает ту же безопасную статистику в JSONL и добавляет сведения о пакетной
обработке, например `requested_count`, `unique_count` и `workers`.

Если у команды указан `bulk_alternative`, уже два ID следует обрабатывать
batch-командой. Если одна population нужна второй раз, её следует сохранить в
снимок и продолжить через `query`. Discovery (`search-tools`, `describe`,
`examples`) выполняется один раз для незнакомого семейства, мутации или
ресурсоёмкой команды.

## Локальная аналитика и автоматические сценарии

Если одна и та же рабочая выборка используется многократно, не следует повторно запрашивать её из API Kaiten на каждом шаге. Данные можно один раз сохранить в локальный снимок, а затем рассчитывать показатели и применять фильтры без обращения к API:

1. `snapshot build` сохраняет рабочую выборку в локальную базу SQLite.
2. `query cards --view summary` фильтрует данные и сокращает выборку локально.
3. `query metrics` локально рассчитывает количество карточек, WIP, пропускную способность, сквозное время выполнения, время цикла и возраст карточек.
4. `query cards --view detail|evidence` раскрывает подробности только для уже сокращённой выборки.
5. Отдельные команды изменения данных через API Kaiten выполняются после локального анализа, если они необходимы.

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

- `snapshot build` и `snapshot refresh` один раз читают данные выбранной области из API Kaiten и сохраняют их локально.
- В версии 1 команда `snapshot refresh` полностью пересобирает снимок и не выполняет частичную синхронизацию изменений.
- `snapshot show` и `snapshot list` показывают `schema_version`, чтобы версию локальной схемы можно было учитывать при будущих миграциях.
- Хранилище снимков считается производным локальным состоянием. Если база SQLite повреждена или несовместима с новой схемой CLI, она создаётся заново. Старые снимки в таком случае теряются.
- `query cards` и `query metrics` работают без обращения к API Kaiten.
- По умолчанию `query cards` использует представление `summary`. Представления `detail` и `evidence` нужны только для раскрытия уже сокращённой выборки.
- Набор `basic` сохраняет структуру пространства и краткую выборку карточек.
- Набор `analytics` добавляет активность пространства, историю перемещений карточек и журналы времени.
- Набор `evidence` добавляет подробные данные карточек, дочерние связи и комментарии.
- Набор `full` объединяет данные наборов `analytics` и `evidence`.
- В текущем виде `query metrics` является общим локальным слоем расчёта метрик и не содержит правил потока, зависящих от конкретной организации.
- Локальный сценарий включается явно. Обычные транспортные команды не переключаются на работу со снимками автоматически.

Хранилище снимков также содержит рабочие данные Kaiten: в зависимости от выбранного набора это могут быть карточки, комментарии, история перемещений и журналы времени. Файл `snapshots.sqlite3` хранится в стандартном пользовательском каталоге данных операционной системы: `~/Library/Application Support/kaiten-cli/` в macOS или `${XDG_DATA_HOME:-~/.local/share}/kaiten-cli/` в Linux. Доступ к нему получает только текущий пользователь.

- Удалить один набор данных: `kaiten --json snapshot delete --name <name>`.
- Для полной очистки необходимо завершить процессы `kaiten` и удалить `snapshots.sqlite3`. Это безвозвратно удалит все локальные снимки, но не изменит данные в Kaiten.

Этот способ рекомендуется для LLM-агентов и автоматических сценариев, которые многократно работают с одной и той же группой карточек.

## Первые команды

Проверка чтения после настройки доступа:

```bash
kaiten --json spaces list --compact --fields id,title
kaiten describe cards.create
kaiten search-tools "project cards"
kaiten snapshot list --json
```

Диагностические сообщения можно вывести отдельно от JSON в стандартном выводе:

```bash
kaiten --json --verbose cards list --board-id 10 --limit 5
```

Подробные диагностические сообщения записываются в `stderr` и показывают источник выбранного профиля, путь запроса, класс ограничения времени ожидания, специальный способ выполнения и краткую статистику команды.

Для последующего анализа длинного сценария можно сохранить трассировку:

```bash
kaiten --json --trace-file ./kaiten-trace.jsonl card-location-history batch-get --card-ids '[101,102,103]'
kaiten --json trace summarize --file ./kaiten-trace.jsonl
```

Трассировка не заменяет ответ команды в стандартном выводе: режим `--json` по-прежнему возвращает `data` и `stats`, а дополнительные сведения записываются в отдельный JSONL-файл.

## Устранение неполадок

Если появляется ошибка `Missing Kaiten credentials`:

```bash
kaiten profile add main --domain <company-subdomain-or-url> --token <api-token> --set-active
kaiten profile show
```

Если профиль уже сохранён, но не активен:

```bash
kaiten profile list
kaiten profile use <name>
```

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

## Сравнение производительности

Для воспроизводимого сравнения последовательных запросов, массового чтения и работы с локальным снимком предусмотрен отдельный сценарий проверки в репозитории:

```bash
.venv/bin/python scripts/benchmark_reference_workflows.py --spec path/to/workflows.json
```

Он запускает заданные команды CLI, измеряет размер ответа в стандартном выводе и общее время выполнения, а также сохраняет трассировку JSONL. Это позволяет сравнивать не только время ответа, но и фактическое значение `http_request_count`.

`README.md` остаётся источником истины для установки, настройки и повседневного использования CLI. Полный каталог команд находится в `COMMAND_REFERENCE.md`, а архитектурная карта — в `ARCHITECTURE.md`.

Релизная политика:

- каждый пользовательский выпуск сопровождается увеличением версии CLI и тегом Git вида `vX.Y.Z`;
- установка из ветки не обновляется автоматически: требуется явный запуск `uv tool upgrade kaiten-cli` или `pipx upgrade kaiten-cli`;
- установка с `@vX.Y.Z` закреплена на указанном теге и не переключается на следующий тег автоматически.

## Статус проекта

Kaiten CLI Community Edition — публичный проект сообщества, предназначенный для автоматизации работы с Kaiten и создания интеграций.

Проект поддерживает Виктор Огнев. Предложения по развитию, сообщения об ошибках и изменения от участников сообщества приветствуются.

На проект не распространяется стандартное коммерческое соглашение Kaiten об уровне обслуживания (SLA), если иное прямо не предусмотрено отдельным соглашением. По вопросам официальной корпоративной поддержки, усиления защиты локальной установки Kaiten, аудита безопасности или разработки индивидуальных интеграций можно обратиться в [Kaiten](https://kaiten.ru/contacts).
