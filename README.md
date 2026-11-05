# kaiten-cli

`kaiten-cli` — интерфейс командной строки для Kaiten: работа с карточками,
документами и другими данными из терминала, скриптов и LLM-агентов.

## Установка

Выберите один способ установки. Homebrew управляет зависимостями на macOS и Linux;
для Python-окружений доступны pip, pipx и uv. Git позволяет выбрать ветку или тег.

### Установка через Homebrew

На macOS и Linux:

```bash
brew install ViktorOgnev/tap/kaiten-cli
kaiten --locale ru --version
```

Homebrew устанавливает Python, Node.js и зависимости CLI в управляемое
окружение. Отдельно устанавливать pipx или uv не требуется. Формула находится в
[публичном tap](https://github.com/ViktorOgnev/homebrew-tap); пока она не входит
в основной каталог Homebrew.

При переходе с pipx или uv сначала удалите прежнюю установку соответствующим
менеджером (`pipx uninstall kaiten-cli` или `uv tool uninstall kaiten-cli`).
Для pip используйте `python -m pip uninstall kaiten-cli` именно в прежнем
окружении. Эти команды не удаляют профили Kaiten. После установки проверьте
`command -v kaiten` и `type -a kaiten`: запускаемый файл должен принадлежать
Homebrew. При необходимости выполните `hash -r` или откройте новый терминал.
Обновляйте Homebrew-установку только через `brew upgrade`.

### Установка из PyPI

Требуется Python 3.11 или новее. Стабильные версии доступны в
[PyPI](https://pypi.org/project/kaiten-cli/), начиная с выпуска `0.3.3`.

Рекомендуемый путь:

```bash
pip install kaiten-cli
```

Установка CLI в отдельное окружение через pipx:

```bash
pipx install kaiten-cli
```

Альтернатива через uv:

```bash
uv tool install kaiten-cli
```

Для установки через pip можно предварительно создать и активировать виртуальное
окружение. На macOS и Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install kaiten-cli
```

В Windows PowerShell окружение активируется командой `.\.venv\Scripts\Activate.ps1`.

### Установка из Git

PyPI устанавливает опубликованный выпуск. Для установки текущего состояния
`master`, которое может содержать ещё не выпущенные изменения, используйте Git:

```bash
pip install git+https://github.com/ViktorOgnev/kaiten-cli.git
```

Для установки конкретного выпуска:

```bash
pip install "git+https://github.com/ViktorOgnev/kaiten-cli.git@v0.3.6"
```

Вместо `pip install` можно использовать `pipx install` или `uv tool install`.
Чтобы выбрать конкретный Python для pip, используйте `python -m pip install`.

### Дополнительные зависимости

Node.js 20+ нужен только для специального режима обновления документов.
Homebrew устанавливает его автоматически; при установке Python-пакета он нужен
отдельно. См. [работу с документами](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/USAGE.md#обновление-содержимого-документов).

### Проверка установки

```bash
kaiten --locale ru --version
kaiten --locale ru --help
kaiten --locale ru agent-help
kaiten --locale ru search-tools cards
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
повторно выполнить `kaiten --locale ru --version`.

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
kaiten --locale ru completion install
```

Команда определяет shell по переменной `SHELL`, создаёт статический completion-
скрипт и добавляет в `~/.bashrc` или `~/.zshrc` только маркированный блок
`kaiten-cli completion`. Повторный запуск обновляет этот блок без дублирования.
Перед изменением файлов доступен режим проверки:

```bash
kaiten --locale ru completion install --dry-run
kaiten --locale ru completion status
```

Если shell нужно указать явно:

```bash
kaiten --locale ru completion install --shell zsh
kaiten --locale ru completion install --shell bash
```

Click поддерживает Bash версии 4.4 и новее. На macOS системный Bash может быть
старее, а login-сессия Bash может не читать `~/.bashrc`; команда сообщит об этом
и предложит указать нужный startup-файл через `--config`.

После установки необходимо открыть новую сессию shell или выполнить команду,
которую напечатает CLI, например `exec zsh`. Проверить работу можно так:

```bash
kaiten --locale ru --read-only cards <Tab>
kaiten --locale ru --read-only cards list --<Tab>
```

Для ручной настройки можно вывести скрипт без изменения файлов:

```bash
kaiten --locale ru completion source zsh
kaiten --locale ru completion source bash
```

Удаление затрагивает только созданный скрипт и управляемый блок:

```bash
kaiten --locale ru completion uninstall
```

Встроенная установка completion сейчас поддерживает Bash и Zsh. Для Fish и
PowerShell необходимо использовать отдельную ручную настройку.

Если пакет установлен в текущем окружении Python, его также можно запустить как модуль:

```bash
python -m kaiten_cli --locale ru --help
```

## Настройка доступа

Для запросов к API нужны адрес компании Kaiten и API-токен пользователя.
Справка и локальное изучение команд доступны без токена.

Рекомендуемый путь: сохранить профиль и сделать его активным.

```bash
kaiten --locale ru profile add main --domain <company-subdomain-or-url> --token <api-token> --set-active
kaiten --locale ru profile show
```

`--domain` и `KAITEN_DOMAIN` принимают поддомен компании (`company`), полный адрес Kaiten (`https://company.kaiten.ru`) или другой адрес с портом для локальной установки и среды разработки.

Если для профиля требуется фиксированный срок хранения постоянного кэша вместо автоматического режима `auto`:

```bash
kaiten --locale ru profile add main \
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

Профили задают домен, токен и настройки кеша. Изменение данных блокируется через `--read-only` или `KAITEN_CLI_READ_ONLY=1`; проверки на реальном API включаются отдельно через `KAITEN_LIVE=1|true`.

### Режим только для чтения

По умолчанию обычный профиль может изменять данные. Для аналитики и работы агентов предусмотрен явный режим только для чтения:

```bash
kaiten --locale ru --read-only --json spaces list --compact --fields id,title
KAITEN_CLI_READ_ONLY=1 kaiten --locale ru --json cards get --card-id 123
```

Режим блокирует команды, которые изменяют данные в Kaiten. Операции с локальными снимками остаются доступны: они записывают данные только в локальную базу SQLite и обращаются к API Kaiten для чтения. Аналитические команды чтения `charts summary get`, `charts block-resolution get` и `charts due-dates get`, использующие POST-запросы, также разрешены. Команды `charts ... create`, создающие временную вычислительную задачу, блокируются. Команды `search-tools` и `describe` возвращают поле `read_only_allowed`, поэтому автоматизация не должна определять допустимость операции только по методу HTTP или полю `mutation`.

Подробности ограничений шлюза для агентов — в
[пользовательском руководстве](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/USAGE.md#шлюз-для-агентов).

### Проверка выбранного профиля

Перед изменениями можно проверить, что CLI разрешил ожидаемый профиль и что его
данные доступа проходят аутентификацию:

```bash
kaiten --locale ru --json --profile main --read-only profile probe
```

Команда выполняет только `GET /users/current`, принудительно обходит постоянный
кэш и возвращает обезличенные сведения о resolved profile. Она различает ошибки
конфигурации, 401, 403 и транспортные сбои, но не проверяет и не обещает наличие
произвольных прав на запись.

### Безопасный процесс изменений

Для мутаций используйте
[skills/kaiten-cli-mutations/SKILL.md](https://github.com/ViktorOgnev/kaiten-cli/blob/master/skills/kaiten-cli-mutations/SKILL.md):
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

### Переменные окружения

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `KAITEN_DOMAIN` | Без профиля | Поддомен компании (`company`), полный адрес Kaiten (`https://company.kaiten.ru`) или другой адрес сервера (`62.84.125.64:3200`, `http://localhost:3000`) |
| `KAITEN_TOKEN` | Без профиля | API-токен пользователя |
| `KAITEN_LIVE` | Нет | `1` или `true` для явного запуска проверки на реальном API с указанными данными доступа или профилем |
| `KAITEN_CLI_READ_ONLY` | Нет | `1` или `true`, чтобы блокировать команды, изменяющие данные Kaiten в текущем процессе |
| `KAITEN_CLI_STORAGE_READ_ONLY` | Нет | `1` или `true`, чтобы читать существующие локальные снимки без изменения схемы и данных и блокировать их создание, обновление и удаление; шлюз для агентов устанавливает значение автоматически |
| `KAITEN_CLI_UPDATE_CHECK` | Нет | `0`, `false`, `no` или `off`, чтобы отключить проверку новых тегов Git после выполнения команды |
| `KAITEN_CLI_CONFIG_PATH` | Нет | Путь к файлу профилей и настроек |
| `KAITEN_TRACE_FILE` | Нет | JSONL-файл для последовательной записи сведений о выполненных командах |

CLI читает переменные окружения текущего процесса и настройки сохранённого профиля.

## Первые команды

Справка и поиск возможностей не требуют подключения к Kaiten:

```bash
kaiten --locale ru --help
kaiten --locale ru agent-help
kaiten --locale ru search-tools cards
kaiten --locale ru describe cards.list
kaiten --locale ru examples cards.list
```

После настройки профиля можно проверить чтение. В примерах указан режим
`--read-only`, который блокирует изменение данных в Kaiten:

```bash
kaiten --locale ru --read-only --json spaces list --compact --fields id,title
kaiten --locale ru --read-only --json cards list --board-id <board_id> --limit 5 --fields id,title,state
kaiten --locale ru --read-only --json cards get --card-id <card_id> --compact
```

Для своего сценария используйте ID из Kaiten. Статистику запросов CLI возвращает
в `stats`, а диагностику по `--verbose` пишет отдельно в `stderr`:

```bash
kaiten --locale ru --read-only --json --verbose cards list --board-id <board_id> --limit 5
```

[Подробное руководство](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/USAGE.md) содержит специальные сценарии,
ограничения API и правила совместимости.

## Обновление CLI

Для установки через Homebrew:

```bash
brew update
brew upgrade kaiten-cli
```

Для установки из PyPI обновление выполняется вручную тем же менеджером:

```bash
python -m pip install --upgrade kaiten-cli
pipx upgrade kaiten-cli
uv tool upgrade kaiten-cli
```

Выберите команду своего менеджера; для pip используйте Python того окружения,
куда установлен пакет. Встроенное предложение обновиться для установок из PyPI
пока не поддерживается.

Для установки из Git-ветки `master` обновление выполняется вручную:

```bash
python -m pip install --upgrade git+https://github.com/ViktorOgnev/kaiten-cli.git
pipx upgrade kaiten-cli
uv tool upgrade kaiten-cli
```

Установка из Git без тега использует текущую версию из ветки `master`.
Установку можно закрепить на конкретном выпуске с помощью тега:

```bash
pip install "git+https://github.com/ViktorOgnev/kaiten-cli.git@v0.3.6"
```

При установке из Git CLI после успешной команды в интерактивном терминале
не чаще одного раза в сутки проверяет стабильные теги `vX.Y.Z` в том же
Git-репозитории. Если найден новый релиз, появляется вопрос `Update now ...? [y/N]`.
Основная команда к этому
моменту уже завершена; подтверждённое обновление применяется со следующего запуска.

Способ обновления соответствует способу установки:

- виртуальное окружение и pip → текущий `python -m pip install --upgrade <git-source>`;
- `pipx` → `pipx upgrade kaiten-cli`;
- `uv tool` → `uv tool upgrade kaiten-cli`.

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

## Язык вывода

`kaiten --locale ru --help` выводит справку по-русски, `--locale en` — по-английски.
Приоритет: явный `--locale` → `KAITEN_CLI_LOCALE` → `en`.
Системные `LANG`/`LC_ALL` и профиль не выбирают язык CLI. Флаг ставится перед
именем команды; агент передаёт его по языку текущего разговора.

```bash
kaiten --locale ru --json describe cards.list
kaiten --locale en search-tools карточки
KAITEN_CLI_LOCALE=ru kaiten --locale ru cards --help
```

Переводятся справка, описания инструментов и полей, рекомендации и собственные
ошибки CLI, в том числе в JSON. Имена команд, ключи JSON, коды ошибок, значения
перечислений и данные Kaiten сохраняются. Поиск понимает русские и английские
описания независимо от языка ответа. Для остальных языков агент использует `en`.

## Ввод данных и сокращение ответа

CLI поддерживает три способа передачи входных данных:

- обычные параметры командной строки: `kaiten --locale ru --read-only cards list --board-id 10 --limit 5`;
- `--from-file payload.json` (также `--input-file payload.json`) для полного объекта JSON из файла;
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

Правила страниц, ограничения и совместимость версий API описаны в
[руководстве по пагинации](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/USAGE.md#пагинация-публичного-api-с-октября-2026-года).

## Возможности

- Карточки, доски, пространства, участники, комментарии, связи и журналы времени.
- Документы, файлы, каталоги, аддоны и публичные ссылки.
- Дашборды, итерации, автоматизации и другие возможности API с учётом поддержки сервером.
- JSON для автоматизации, Markdown для экспорта, сокращение ответов через `--compact` и `--fields`.
- Массовое чтение, локальные снимки и расчёт метрик.

[Полный справочник команд и таблица модулей](https://github.com/ViktorOgnev/kaiten-cli/blob/master/COMMAND_REFERENCE.md#module-index).

## Работа с документами и файлами

Карточки и документы можно читать как JSON или сохранять в Markdown:

```bash
kaiten --locale ru --read-only --json documents get --document-uid <document_uid>
kaiten --locale ru --read-only --json documents get --document-uid <document_uid> --markdown --output ./document.md
kaiten --locale ru --read-only --json cards get --card-id <card_id> --markdown --output ./card.md
```

[Документы: чтение, экспорт и обновление](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/USAGE.md#документы-чтение-экспорт-и-обновление) —
подробные инструкции по содержимому документов, вложениям и совместимости серверов.

## Как работает кэш

В пределах одной команды одинаковые GET-запросы переиспользуются автоматически.
По умолчанию режим `auto` также сохраняет подходящие ответы на диске между запусками
и подбирает срок хранения с учётом стоимости чтения.

Для обычных сценариев флаги кэша не нужны. Когда требуется получить свежие данные,
используйте `refresh` один раз на границе обновления данных:

```bash
kaiten --locale ru --read-only --json --cache-mode refresh cards get --card-id <card_id>
```

Для повторной работы с одной выборкой предпочтительнее локальный снимок.
[Подробности кэша](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/USAGE.md#как-работает-кэш): режимы, сроки хранения,
состав локальной базы и очистка.

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
kaiten --locale ru --read-only --json card-location-history batch-get --card-ids '[101,102,103]' --workers 2
kaiten --locale ru --read-only --json cards batch-get --card-ids '[101,102,103]' --workers 2 --fields id,title,description
kaiten --locale ru --read-only --json time-logs batch-list --card-ids '[101,102,103]' --workers 2 --fields id,time_spent,for_date
kaiten --locale ru --read-only --json card-children batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,title
kaiten --locale ru --read-only --json comments batch-list --card-ids '[101,102,103]' --workers 2 --compact --fields id,text
kaiten --locale ru --read-only --json cards list-all --board-id 10 --selection active_only --fields id,title,state
kaiten --locale ru --read-only --json space-topology get --space-id 10
kaiten --locale ru --read-only --json cards get --card-id 101 --compact --fields id,title,state
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
kaiten --locale ru --read-only --json --trace-file ./kaiten-trace.jsonl cards list-all --board-id 10 --selection active_only
```

Трассировка обязательна для wrapper-сценария из трёх и более CLI-команд, более
чем десяти ожидаемых HTTP-запросов или неизбежного цикла. Локальная потоковая
сводка не обращается к Kaiten API и не возвращает argv или payload:

```bash
kaiten --locale ru --json trace summarize --file ./kaiten-trace.jsonl
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
kaiten --locale ru --read-only --json snapshot build --name team-basic --space-id 10 --preset basic
kaiten --locale ru --read-only --json query cards --snapshot team-basic --view summary --filter '{"board_ids":[10],"has_comments":true}' --fields id,title,has_comments
```

Команда `query metrics` рассчитывает метрики по тому же снимку без запросов к API.
[Подробности локальной аналитики](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/USAGE.md#локальная-аналитика-и-автоматические-сценарии):
наборы данных, аналитическое окно, обновление и очистка снимков.

## Рекомендации для LLM-агентов

Для работы с сущностями, пользователями, группами и правами используйте
[руководство по доступам](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/ACCESS_MANAGEMENT.md).
Оно различает документированные методы и расширения обычного API с токеном,
прямые и унаследованные назначения, административные права и роли объектов.
CLI принимает готовые параметры операций; внешние спецификации и регулярные
сценарии обрабатывает вызывающий агент или harness.

Рекомендуемые сценарии работы агентов с CLI описаны в отдельных файлах навыков:

- [skills/kaiten-cli-access-management/SKILL.md](https://github.com/ViktorOgnev/kaiten-cli/blob/master/skills/kaiten-cli-access-management/SKILL.md)
  Какие команды и параметры использовать для сущностей, пользователей, групп и ролей доступа, с учётом прав и наследования.

- [skills/kaiten-cli-heavy-data/SKILL.md](https://github.com/ViktorOgnev/kaiten-cli/blob/master/skills/kaiten-cli-heavy-data/SKILL.md)
  Как избежать множества отдельных запросов, когда использовать массовое чтение, а когда создавать локальный снимок данных.
- [skills/kaiten-cli-metrics/SKILL.md](https://github.com/ViktorOgnev/kaiten-cli/blob/master/skills/kaiten-cli-metrics/SKILL.md)
  Как рассчитывать канбан-метрики по локальному снимку данных и не запрашивать историю каждой карточки отдельно.
- [skills/kaiten-cli-mutations/SKILL.md](https://github.com/ViktorOgnev/kaiten-cli/blob/master/skills/kaiten-cli-mutations/SKILL.md)
  Как безопасно планировать и выполнять изменения с точным preview, возобновляемым manifest и проверкой изменённых полей.

## Устранение неполадок

Если появляется ошибка `Missing Kaiten credentials`:

```bash
kaiten --locale ru profile add main --domain <company-subdomain-or-url> --token <api-token> --set-active
kaiten --locale ru profile show
```

Если профиль уже сохранён, но не активен:

```bash
kaiten --locale ru profile list
kaiten --locale ru profile use <name>
```

## Карта документации

- [Подробное пользовательское руководство](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/USAGE.md) — документы, файлы, каталоги, аддоны, дерево, кэш и аналитика.
- [Документы: чтение, экспорт и обновление](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/USAGE.md#документы-чтение-экспорт-и-обновление) — отдельный раздел о работе с содержимым и вложениями.
- [COMMAND_REFERENCE.md](https://github.com/ViktorOgnev/kaiten-cli/blob/master/COMMAND_REFERENCE.md) — полный автоматически созданный справочник команд и псевдонимов MCP.
- [Разработка и проверки](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/CONTRIBUTING.md) — окружение, генерация документации, тесты и сравнение производительности.
- [Архитектура](https://github.com/ViktorOgnev/kaiten-cli/blob/master/ARCHITECTURE.md) — устройство CLI, реестр и режимы выполнения.
- [Руководство для агентов](https://github.com/ViktorOgnev/kaiten-cli/blob/master/AGENTS.md) — discovery, безопасность и эффективная работа с API.
- [Публикация в PyPI и сопровождение Homebrew](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/PYPI_PUBLISHING.md) — порядок выпуска и обновления tap.
- [Проверки на реальном API](https://github.com/ViktorOgnev/kaiten-cli/blob/master/LIVE_VALIDATION.md) — явно включаемые live-тесты.
- [Публичный API и ограничения паритета](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/public-api/README.md) — сохранённый снимок контракта и воспроизводимая офлайн-сверка.
- [Особенности тестового API](https://github.com/ViktorOgnev/kaiten-cli/blob/master/API_BEHAVIOR_MATRIX.md) — подтверждённое поведение тестового контура.
- [Протокол проверки обновления документов](https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/DOCUMENT_YJS_VERIFICATION.md) — результаты экспериментов и условия удаления временного транспорта.
- [Безопасность](https://github.com/ViktorOgnev/kaiten-cli/blob/master/SECURITY.md) — уязвимости и обращение с локальными данными доступа.

## Поддержка и лицензия

Kaiten CLI Community Edition — публичный проект сообщества, предназначенный для автоматизации работы с Kaiten и создания интеграций.

Проект поддерживает Виктор Огнев. Предложения по развитию, сообщения об ошибках и изменения от участников сообщества приветствуются.

На проект не распространяется стандартное коммерческое соглашение Kaiten об уровне обслуживания (SLA), если иное прямо не предусмотрено отдельным соглашением. По вопросам официальной корпоративной поддержки, усиления защиты локальной установки Kaiten, аудита безопасности или разработки индивидуальных интеграций можно обратиться в [Kaiten](https://kaiten.ru/contacts).

Проект распространяется под лицензией [MIT](https://github.com/ViktorOgnev/kaiten-cli/blob/master/LICENSE).
