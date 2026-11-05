# Сущности, пользователи и права доступа

CLI предоставляет операции API Kaiten. Внешний агент или harness выбирает
операции и передаёт готовые параметры. CLI не читает спецификации доступа,
не вычисляет желаемое состояние, не планирует переназначения и не запускает
регулярную синхронизацию.

## Выбор методов

Сначала используйте документированные методы
[developers.kaiten.ru](https://developers.kaiten.ru/). Если они не предоставляют
нужную операцию, доступны явно обозначенные расширения обычного API с токеном.
Команды не используют браузерную сессию или Superadmin API и не переходят на
другой маршрут после отказа в доступе. Серверных доработок для этих команд нет.

| Задача | Команды | Контракт |
|---|---|---|
| Доступное пользователю дерево | `tree-entities list` | [Публичный](https://developers.kaiten.ru/tree-entities/get-list-of-entities) |
| Полный административный листинг метаданных | `admin-tree-entities list`, `list-all` | Недокументированное расширение |
| Пользователи пространства | `space-users list/add/update/remove` | [Публичный](https://developers.kaiten.ru/space-users/invite-user-to-space) |
| Пользователи документа, папки, карты историй | `document-users`, `document-group-users`, `story-map-users`: `list/add/update/remove` | Недокументированные расширения |
| Группы компании и их пользователи | `company-groups.*`, `group-users.*` | [Публичный](https://developers.kaiten.ru/group-users/add-user-to-group) |
| Назначения групп сущностям | `group-entities list/list-all/add/update/remove` | [Публичный](https://developers.kaiten.ru/group-entities/add-entity); `list-all` агрегирует страницы в CLI |
| Группы с доступом к конкретному объекту | `space-access-groups`, `document-access-groups`, `document-group-access-groups`, `story-map-access-groups`: `list` | Недокументированные расширения |
| Список ролей доступа | `roles list` | [Публичный](https://developers.kaiten.ru/tree-entity-roles/get-list-of-tree-entity-roles) |
| Чтение и изменение роли доступа | `roles get/create/update/delete` | Недокументированное расширение |
| Административные разрешения пользователей и групп | `company-users update`, `company-groups create/update` | [Публичные именованные права](https://developers.kaiten.ru/company-permissions) |
| Пространства, документы и папки | `spaces.*`, `documents.*`, `document-groups.*` | Публичные методы |
| Базовые операции карт историй | `story-maps list/get/create/update/delete` | Недокументированные расширения |

Источники расширений: серверные `routes/api.js`,
`adminTreeEntitiesController`, `documents/baseDocumentUsers`, `TreeEntityGroupsBase`,
`storyMaps/index`, `storyMaps/users` и `treeEntityRolesController`, сверенные
3 ноября 2026 года. Это проверка кода, а не установленной версии сервера.
Все 26 новых команд проверены с обычным API-токеном на тестовой компании
4 ноября 2026 года, включая выдачу и отзыв прав и проверяемую очистку. Именованные
административные разрешения группы также проверены. Запись таких разрешений
виртуальному пользователю вернула HTTP 500 и остаётся неподтверждённой;
это не свидетельство успешной настройки прав обычного пользователя компании.
Доступность зависит от версии, прав и тарифа. `describe`
показывает контракт и статус проверки. Не поддерживаемый сервером метод может
вернуть ошибку; CLI сохраняет её без обходного запроса.
[Результаты live-проверки](ACCESS_MANAGEMENT_LIVE.md).

## Полный список назначений группы

`group-entities list --group-uid <uuid> --limit 100 --offset 0` читает одну
страницу. Если `limit/offset` не переданы, CLI сохраняет поведение сервера.
Для полного списка используйте `group-entities list-all` с тем же `group_uid`:

```bash
kaiten --locale ru --json --read-only group-entities list-all --group-uid <group_uuid> --page-size 100 --max-pages 100 --fields uid,title --compact
```

Команда агрегирует документированный GET `/company/groups/{group_uid}/entities`.
`page_size` — 1–100, `max_pages` — 1–1000; оба по умолчанию 100. Пустая или
короткая страница завершает чтение. Повтор UID, некорректный ответ, страница
больше запрошенной или полная страница на пределе запросов дают явную ошибку
вместо успешного частичного списка. Нужен сервер с поддержкой `limit/offset`;
legacy fallback отсутствует. Параллельные изменения могут сдвинуть страницы:
это не атомарный снимок. `--fields` и `--compact` сокращают локальный вывод после
загрузки всех страниц, а не HTTP-ответ.

Для назначения группе доступа к пространствам достаточно административных
метаданных и UUID объектов: выгружать карточки, документы и вложения не нужно.
Выбор целевых объектов и ролей, сравнение назначений и регулярность запусков
определяет внешний агент; CLI предоставляет чтение и отдельные операции API.

## Права запускающего пользователя

API-токен действует от имени пользователя. Успешный `profile probe` проверяет
авторизацию, но не произвольные права записи. Нельзя выводить возможности только
из названия «администратор»: учитывайте конкретные разрешения.

- Административный листинг: `entitiesTree` **или** `members`. Этот листинг
  не предоставляет доступ к содержимому найденных объектов.
- Управление пользователями документов, папок и карт историй: разрешение
  `access_control` объекта **или** административное `entitiesTree`.
  Для пространства добавление также допускается с `members`; другие действия
  проверяются отдельно. При приглашении нового пользователя компании нужны
  дополнительные права приглашения; лицензия и ограничения компании сохраняются.
- Назначения групп сущностям и создание/изменение ролей: административное
  `members` и доступность соответствующих модулей. Чтение групп объекта также
  допускается с его `access_control` или административным `entitiesTree`/`members`.
- Создание сущности проверяет права в месте назначения; перемещение — права
  источника и назначения. Административный листинг не отменяет эти проверки.
- Для карт историй необходим соответствующий модуль. Создание требует платного
  доступа и права создания в месте назначения; удаление — права удаления объекта.

CLI не выдаёт запускающему пользователю дополнительные права автоматически.

## Идентификаторы и наследование

`user_id` — числовой ID пользователя компании. `role_id` в `roles` и назначениях
доступа — UUID роли из `/tree-entity-roles`. `user-roles` — другое семейство:
числовые роли для учёта времени; оно не назначает разрешения сущностям.

Для пользователей пространства и карты историй нужны числовые `space_id` и
`map_id`. Для пользователей документа и папки — `document_uid` и `group_uid`
(UUID папки, не группы пользователей). Все команды `*-access-groups list`
принимают `entity_uid`, включая пространства и карты историй.

`include_inherited_access=true` запрашивает у сервера унаследованный доступ.
В ответах назначения `own_role_ids` обозначает прямые роли пользователя,
`role_ids` — его роли с учётом наследования. Групповые роли передаются отдельно:
`own_groups_role_ids` — прямые назначения групп на объекте, `groups_role_ids` —
групповые роли с учётом наследования. Эти массивы могут быть `null`.
`role_permissions` содержит итоговые разрешения. Конкретный состав
ответа зависит от метода. CLI не вычисляет собственную модель наследования.
Удаление прямого назначения может сохранить доступ через предка, группу или
общий доступ. Изменение родителя может изменить итоговые разрешения, а изменение
общей роли затрагивает все её назначения.

У вложенной сущности автор может иметь только унаследованные права. Перемещение
в корень или закрытие доступа сервер отклоняет с HTTP 400, если после операции
не останется управляющего доступом. Когда это предусмотрено задачей вызывающего
агента, прямое назначение делается отдельной командой `*-users update` до
перемещения. CLI не выдаёт его автоматически.

`story-maps create` подставляет текущую Unix-метку времени в `sort_order`, если
позиция не передана, как при создании документов. Это проверенное исправление
совместимости для сервера, возвращавшего HTTP 500 без позиции. Явное значение
позиции сохраняется; разрешения от себя CLI не добавляет.

## Примеры операций

Обнаружение команд и контрактов не изменяет Kaiten:

```bash
kaiten --locale ru --json search-tools доступ
kaiten --locale ru --json describe document-users.add
kaiten --locale ru --json examples group-entities.add
kaiten --locale ru --json --profile main --read-only profile probe
```

Чтение текущих назначений:

```bash
kaiten --locale ru --json --read-only document-users list --document-uid <document_uuid> --include-inherited-access true
kaiten --locale ru --json --read-only document-access-groups list --entity-uid <document_uuid> --include-inherited-access true
kaiten --locale ru --json --read-only roles list
```

Ниже — примеры **записей** с уже выбранными внешним агентом целями и ролями.
Порядок авторизации и проверки записей описан в
[mutation skill](../skills/kaiten-cli-mutations/SKILL.md).

```bash
kaiten --locale ru --json document-users add --document-uid <document_uuid> --user-id 123 --role-id <role_uuid>
kaiten --locale ru --json document-users update --document-uid <document_uuid> --user-id 123 --role-id <other_role_uuid>
kaiten --locale ru --json group-users add --group-uid <user_group_uuid> --user-id 123
kaiten --locale ru --json group-entities add --group-uid <user_group_uuid> --entity-uid <entity_uuid> --role-ids '["<role_uuid>"]'
kaiten --locale ru --json story-maps update --map-id 10 --parent-entity-uid <folder_uuid>
kaiten --locale ru --json story-maps update --map-id 10 --parent-entity-uid null
```

`roles create` принимает `name` и полный объект серверных `permissions`.
Структуру можно посмотреть через `roles get`; JSON-ответ CLI содержит оболочку,
поэтому не передавайте его целиком в `--from-file`. Подготовленный файл ввода
должен содержать только параметры команды: `name`, `permissions` и, если нужен,
`new_permissions_default_value`. Сервер проверяет полноту и сочетания разрешений.
CLI не добавляет разрешения или значения по умолчанию от себя.

```bash
kaiten --locale ru --json --from-file role.json roles create
kaiten --locale ru --json roles update --role-id <role_uuid> --permissions '{"document":{"read":false}}'
kaiten --locale ru --json roles delete --role-id <role_uuid> --replacing-role-id <replacement_role_uuid>
```

PATCH роли объединяет переданные ключи с сохранёнными на сервере. Чтобы убрать
разрешение, передайте `false` явно. Системные и заблокированные роли защищены
сервером; CLI не обходит эти ограничения.

Именованные права компании также изменяются частично:

```bash
kaiten --locale ru --json company-users update --user-id 123 --named-permissions '{"entitiesTree":true,"members":false}'
kaiten --locale ru --json company-groups update --group-uid <user_group_uuid> --named-permissions '{"entitiesTree":true}'
```

`permissions` — числовая маска; `named_permissions` — карта имён в `true/false`.
Передавайте один формат за запрос, в том числе при использовании `payload`.
Числовая маска не описывает права, доступные только по имени. `false` убирает
прямое назначение, но не отменяет доступ через другую группу. Для проверки
прямых назначений в ответе пользователя смотрите `own_named_permissions`,
для итоговых — `named_permissions`. Неизвестное имя может быть проигнорировано
сервером; успешный HTTP-ответ сам по себе не подтверждает выдачу такого права.

## Административный листинг

```bash
kaiten --locale ru --json --read-only admin-tree-entities list --limit 100 --offset 0
kaiten --locale ru --json --read-only admin-tree-entities list --parent-uid <entity_uuid> --limit 100 --offset 0
kaiten --locale ru --json --read-only admin-tree-entities list-all --max-pages 100 --fields uid,title,entity_type,parent_entity_uid
```

`list` читает одну страницу. Без фильтров это корни; `parent_uid` выбирает детей.
Это другое имя параметра, чем `parent_entity_uid` публичного `tree-entities`.
Фильтр `user_id` ограничивает выдачу доступом выбранного пользователя.

`list-all` запрашивает плоский список всех четырёх типов через `entity_types`,
без обхода каждого родителя. Размер страницы по умолчанию 100 (1–100), предел
страниц — 100 (1–1000). Повтор UID, неправильный ответ и достижение предела с
полной страницей завершаются ошибкой вместо неполного успешного результата.
Это постраничное чтение, не атомарный снимок и не журнал событий: параллельные
изменения могут приводить к пропускам. Архивные и защищённые объекты не следует
считать полным охватом инвентаризации.

Новые чтения расширений по умолчанию используют только кеш текущего вызова,
не постоянный кеш. Фильтрация `--fields` сокращает вывод, а не серверный ответ.
Для длинных внешних сценариев используйте штатную трассировку CLI.
`PATCH /admin-tree-entities` намеренно отсутствует: он запрещён сервером для
публичного API.

Для выбора команд агентом предназначен
[справочный скилл](../skills/kaiten-cli-access-management/SKILL.md).
