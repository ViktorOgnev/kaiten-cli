# Публикация kaiten-cli в PyPI

Стабильные выпуски начиная с `0.3.3` публикуются push тега `vX.Y.Z`.
Обычный push в `master` и PR запускают CI без загрузки в PyPI.
Установка и ручное обновление описаны в [README](../README.md).

## Однократная настройка перед первым выпуском

Настройка аккаунтов, слияние PR и отправка тега выполняются отдельным этапом
после подготовки и проверки ветки публикации.

1. В настройках репозитория `ViktorOgnev/kaiten-cli` создать environment `pypi`:
   **Settings → Environments → New environment**.
2. В **Deployment branches and tags → Selected branches and tags** добавить
   правило типа **Tag** с шаблоном `v*`. Разрешение для веток не добавлять.
   При необходимости ручного контроля добавить required reviewer перед загрузкой.
3. Подтвердить email аккаунта PyPI и настроить обязательную двухфакторную
   аутентификацию, если она ещё не настроена. Секреты и коды восстановления
   сохраняются владельцем аккаунта, в репозиторий их не помещать.
4. В PyPI открыть [Publishing](https://pypi.org/manage/account/publishing/)
   и добавить pending publisher во вкладке GitHub:

   | Поле | Значение |
   |---|---|
   | PyPI Project Name | `kaiten-cli` |
   | Owner | `ViktorOgnev` |
   | Repository name | `kaiten-cli` |
   | Workflow name | `publish.yml` |
   | Environment name | `pypi` |

Имя workflow — только имя файла, без `.github/workflows/`. Название environment
должно совпадать в GitHub, PyPI и workflow. Pending publisher не резервирует имя
проекта; перед первым выпуском необходимо проверить доступность названия.
Проект появится при первой успешной публикации.

API-токен PyPI и repository secret для загрузки не нужны: используется
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).
Право `id-token: write` есть только у job загрузки; job не выполняет checkout,
код проекта или сборку. TestPyPI в этот процесс не входит.

## Порядок выпуска

1. Увеличить `__version__` в `src/kaiten_cli/__init__.py`, обновить инструкции,
   если меняются установка или требования, и провести изменения через PR в `master`.
2. После слияния дождаться успешного CI на выбранном коммите `master`.
   Первый выпуск из этой ветки — `0.3.3`. Последующие используют новую версию;
   существующий тег `v0.3.2` не меняется.
3. Обновить локальные ссылки и убедиться, что коммит, версия и будущий тег
   соответствуют друг другу. Для первого выпуска из чистого checkout:

   ```bash
   git fetch origin master --tags
   git switch master
   git merge --ff-only origin/master
   git status --short
   git rev-parse HEAD
   git tag -a v0.3.3 -m "Release v0.3.3"
   git push origin refs/tags/v0.3.3
   ```

   Перед `git tag` проверить, что рабочее дерево чистое и `HEAD` — согласованный
   коммит выпуска. Push тега запускает реальную публикацию. Выпуск не требует
   создания GitHub Release и не создаёт его автоматически.
4. В Actions открыть **Publish to PyPI** для этого тега. Если environment
   использует reviewer, подтвердить deployment после успешных проверок.
5. Дождаться успешной загрузки и выполнить проверки опубликованного пакета ниже.

## Что проверяет workflow

- `preflight` принимает только стабильный `vX.Y.Z`, проверяет совпадение версии
  исходников с тегом, совпадение `HEAD`, тега и triggering SHA, а также вхождение
  коммита в историю `origin/master`. Тег на несмерженной ветке отклоняется.
- GET метаданных версии PyPI должен вернуть `404`. Существующая версия,
  сетевой сбой, `403`, `429` или ошибка сервера останавливают публикацию.
- `checks` вызывает тот же CI на коммите тега: lint, форматирование, локализация,
  документация, тесты Python 3.11–3.14, coverage и аудит зависимостей.
- Сборка создаёт ровно wheel и sdist; `twine check --strict` проверяет описание,
  а `scripts/check_release.py artifacts` проверяет Name/Version обоих архивов
  и выводит SHA256 в summary job сборки.
- Wheel проверяется через pip, pipx и uv; sdist устанавливается в отдельное
  чистое окружение. Импорт, версия, справка и поиск инструментов проверяются без
  Kaiten credentials. Стоимость CLI-вызовов записывается в локальную trace.
- `publish` запускается только после успеха всего CI. Он скачивает артефакт
  `distribution` текущего запуска и загружает эти же файлы без пересборки.
  Параллельные запуски одного тега сериализуются; существующие файлы вызывают
  ошибку (`skip-existing: false`).

## Проверка после публикации

1. Открыть [проект в PyPI](https://pypi.org/project/kaiten-cli/) и проверить
   версию, описание, Python `>=3.11` и наличие wheel/sdist.
2. Прочитать JSON версии, например
   [0.3.3](https://pypi.org/pypi/kaiten-cli/0.3.3/json), и сравнить имена файлов
   и `digests.sha256` с SHA256 из Actions summary. При необходимости скачать
   артефакт `distribution` этого запуска и вычислить SHA256 независимо.
3. Вне исходников создать временное окружение и проверить установку из PyPI
   без локального кэша. Команды ниже предполагают отсутствие Kaiten credentials:

   ```bash
   python3 -m venv .verify-venv
   .verify-venv/bin/python -m pip install --no-cache-dir --index-url https://pypi.org/simple kaiten-cli==0.3.3
   .verify-venv/bin/python -I -c "import kaiten_cli; assert kaiten_cli.__version__ == '0.3.3'"
   export KAITEN_CLI_UPDATE_CHECK=0
   export KAITEN_TRACE_FILE="$PWD/install-smoke.jsonl"
   .verify-venv/bin/kaiten --locale ru --version
   .verify-venv/bin/kaiten --locale ru --help
   .verify-venv/bin/kaiten --locale ru search-tools cards
   .verify-venv/bin/kaiten --locale ru --json trace summarize --file "$KAITEN_TRACE_FILE"
   ```

## Ошибки и повторные запуски

До начала загрузки исправить причину сбоя и повторить запуск Actions. Если
ошибка требует изменения кода, провести исправление через `master` и выпустить
новую версию с новым тегом.

Если загрузка завершилась частично или результат неизвестен, сначала проверить
JSON версии, список файлов и SHA256 в PyPI. Существующая версия блокирует
повторную публикацию на preflight; автоматического пропуска файлов и дозагрузки
нет. Не удалять и не перезаписывать артефакты, не передвигать тег. Для исправления
пакета использовать новую patch-версию; необходимость yanking плохой версии
рассматривается отдельно.

Сбой установки после успешной загрузки не означает откат: опубликованные файлы
уже доступны пользователям. Зафиксировать результат проверки и готовить
исправляющий выпуск. Установки из PyPI пока обновляются только вручную;
встроенная проверка версий из Git не переключает источник установки на PyPI.
