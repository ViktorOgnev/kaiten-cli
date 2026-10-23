# Публикация kaiten-cli в PyPI

Стабильные выпуски начиная с `0.3.3` публикуются push тега `vX.Y.Z`.
Обычный push в `master` и PR запускают CI без загрузки в PyPI.
Установка и ручное обновление описаны в [README](../README.md).

## Состоявшийся первый выпуск

`0.3.3` опубликована **2026-10-23**:

- [Пакет в PyPI](https://pypi.org/project/kaiten-cli/0.3.3/).
- [Успешный запуск публикации](https://github.com/ViktorOgnev/kaiten-cli/actions/runs/39952014820).
- Аннотированный тег `v0.3.3` указывает на коммит `18abe81aa52ad6a1cec0334452194691b06ad4f4`.
- SHA256 wheel и sdist сверены между артефактом Actions, метаданными PyPI и
  скачанными файлами. Установка из PyPI в чистое окружение, импорт и запуск CLI прошли.

Первоначальная настройка GitHub environment `pypi` и доверенного издателя PyPI
выполнена. Для следующих выпусков используется эта же связь; создавать pending
publisher заново или повторно отправлять тег `v0.3.3` не требуется.

## Конфигурация доверенного издателя

Эти параметры нужны для проверки существующей настройки или её восстановления:

1. В настройках репозитория `ViktorOgnev/kaiten-cli` создать environment `pypi`:
   **Settings → Environments → New environment**.
2. В **Deployment branches and tags → Selected branches and tags** добавить
   правило типа **Tag** с шаблоном `v*`. Разрешение для веток не добавлять.
   При необходимости ручного контроля добавить required reviewer перед загрузкой.
3. Подтвердить email аккаунта PyPI и настроить обязательную двухфакторную
   аутентификацию, если она ещё не настроена. Секреты и коды восстановления
   сохраняются владельцем аккаунта, в репозиторий их не помещать.
4. Для существующего проекта открыть **Manage → Publishing** в PyPI и проверить
   GitHub publisher. При первоначальной настройке ещё не существующего проекта
   pending publisher добавляется через [Publishing аккаунта](https://pypi.org/manage/account/publishing/).
   Параметры текущей связи:

   | Поле | Значение |
   |---|---|
   | PyPI project | `kaiten-cli` |
   | Owner | `ViktorOgnev` |
   | Repository name | `kaiten-cli` |
   | Workflow name | `publish.yml` |
   | Environment name | `pypi` |

Имя workflow — только имя файла, без `.github/workflows/`. Название environment
должно совпадать в GitHub, PyPI и workflow. Pending publisher применяется только
до создания проекта: он не резервирует название и при первом использовании
становится обычным издателем. Проект `kaiten-cli` уже существует.

API-токен PyPI и repository secret для загрузки не нужны: используется
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).
Право `id-token: write` есть только у job загрузки; job не выполняет checkout,
код проекта или сборку. TestPyPI в этот процесс не входит.

## Порядок следующего выпуска

1. Увеличить `__version__` в `src/kaiten_cli/__init__.py`, обновить инструкции,
   если меняются установка или требования, и провести изменения через PR в `master`.
2. После слияния дождаться успешного CI на выбранном коммите `master`.
   Следующий выпуск должен иметь новую, ещё не опубликованную версию.
   Существующие теги и опубликованные файлы не меняются.
3. Обновить локальные ссылки и убедиться, что коммит, версия и будущий тег
   соответствуют друг другу. Выполнять из чистого checkout. В строке
   `RELEASE_VERSION=X.Y.Z` заменить `X.Y.Z` на новую версию из `__version__`:

   ```bash
   git fetch origin master --tags
   git switch master
   git merge --ff-only origin/master
   git status --short
   git rev-parse HEAD
   export RELEASE_VERSION=X.Y.Z
   git tag -a "v${RELEASE_VERSION}" -m "Release v${RELEASE_VERSION}"
   python scripts/check_release.py preflight --tag "v${RELEASE_VERSION}" --commit "$(git rev-parse HEAD)"
   git push origin "refs/tags/v${RELEASE_VERSION}"
   ```

   Перед `git tag` проверить, что рабочее дерево чистое и `HEAD` — согласованный
   коммит выпуска. Отправлять тег только после успешного preflight.
   Push тега запускает реальную публикацию. Выпуск не требует
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
2. Прочитать JSON выпущенной версии по адресу
   `https://pypi.org/pypi/kaiten-cli/<RELEASE_VERSION>/json` и сравнить имена файлов
   и `digests.sha256` с SHA256 из Actions summary. При необходимости скачать
   артефакт `distribution` этого запуска и вычислить SHA256 независимо.
3. Вне исходников создать временное окружение и проверить установку из PyPI
   без локального кэша. В строке `RELEASE_VERSION=X.Y.Z` указать выпущенную версию.
   Команды ниже предполагают отсутствие Kaiten credentials:

   ```bash
   export RELEASE_VERSION=X.Y.Z
   python3 -m venv .verify-venv
   .verify-venv/bin/python -m pip --isolated install --no-cache-dir --index-url https://pypi.org/simple "kaiten-cli==${RELEASE_VERSION}"
   .verify-venv/bin/python -I -c "import os, kaiten_cli; assert kaiten_cli.__version__ == os.environ['RELEASE_VERSION']"
   export KAITEN_CLI_UPDATE_CHECK=0
   export KAITEN_TRACE_FILE="$PWD/install-smoke.jsonl"
   .verify-venv/bin/kaiten --locale ru --version
   .verify-venv/bin/kaiten --locale ru --help
   .verify-venv/bin/kaiten --locale ru search-tools cards
   .verify-venv/bin/kaiten --locale ru --json trace summarize --file "$KAITEN_TRACE_FILE"
   ```

Описание проекта в PyPI входит в метаданные собранного пакета. Изменение README
в репозитории появится в описании следующего выпуска; уже опубликованная `0.3.3`
сохраняет прежние метаданные. Для исправления только документации новый выпуск
пакета не требуется.

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
