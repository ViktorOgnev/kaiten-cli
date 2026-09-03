"""Human-facing registry module descriptions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModuleDocSpec:
    key: str
    label: str
    description: str


MODULE_SPECS: tuple[ModuleDocSpec, ...] = (
    ModuleDocSpec("cards", "Карточки", "Карточки, bulk reads и card-heavy workflows."),
    ModuleDocSpec("comments", "Комментарии", "Комментарии карточек и comment-heavy reads."),
    ModuleDocSpec(
        "members",
        "Участники и пользователи",
        "Участники карточек, пользователи, группы и space users.",
    ),
    ModuleDocSpec("time_logs", "Логи времени", "Time logs, work logs и related analytics inputs."),
    ModuleDocSpec("tags", "Теги", "Теги и операции привязки тегов к карточкам."),
    ModuleDocSpec("checklists", "Чеклисты", "Чеклисты и checklist items."),
    ModuleDocSpec("blockers", "Блокировки", "Блокировки карточек и blocker relations."),
    ModuleDocSpec(
        "card_relations", "Связи карточек", "Parent/child/planned relations between cards."
    ),
    ModuleDocSpec("external_links", "Внешние ссылки", "External links attached to cards."),
    ModuleDocSpec("files", "Файлы карточек", "Файлы и вложения карточек."),
    ModuleDocSpec("subscribers", "Подписчики", "Подписки на карточки и колонки."),
    ModuleDocSpec("spaces", "Пространства", "Spaces and top-level workspace reads."),
    ModuleDocSpec("boards", "Доски", "Boards and board-level operations."),
    ModuleDocSpec(
        "columns", "Колонки и подколонки", "Columns, subcolumns and related card structure."
    ),
    ModuleDocSpec("lanes", "Дорожки", "Swimlanes and lane-level operations."),
    ModuleDocSpec("card_types", "Типы карточек", "Card types and type metadata."),
    ModuleDocSpec(
        "custom_directories",
        "Каталоги / Custom directories",
        "Kaiten Catalogs: directories, fields, records and linked cards.",
    ),
    ModuleDocSpec(
        "custom_properties",
        "Кастомные свойства",
        "Custom properties, select values, catalog-values and collective values.",
    ),
    ModuleDocSpec("documents", "Документы", "Documents and document groups."),
    ModuleDocSpec(
        "dashboards",
        "Дашборды",
        "Experimental dashboards, collaborators, widgets and compute jobs.",
    ),
    ModuleDocSpec(
        "iterations", "Итерации", "Beta iterations, iteration cards and card history."
    ),
    ModuleDocSpec("webhooks", "Вебхуки", "Webhook configuration and delivery settings."),
    ModuleDocSpec(
        "automations", "Автоматизации и воркфлоу", "Automations, incoming webhooks and workflows."
    ),
    ModuleDocSpec("projects", "Проекты и спринты", "Projects, project cards and sprints."),
    ModuleDocSpec(
        "roles_and_groups", "Роли и группы", "Roles, groups and permission-related operations."
    ),
    ModuleDocSpec("scim", "SCIM", "SCIM v2 user and group provisioning."),
    ModuleDocSpec(
        "audit_and_analytics",
        "Аудит и аналитика",
        "Audit logs, activity, saved filters and analytics helpers.",
    ),
    ModuleDocSpec(
        "service_desk",
        "Service Desk",
        "Service Desk requests, users, SLA, organizations and settings.",
    ),
    ModuleDocSpec("charts", "Графики и аналитика", "Chart endpoints and compute jobs."),
    ModuleDocSpec("tree", "Дерево сущностей", "Entity tree and tree navigation commands."),
    ModuleDocSpec(
        "utilities", "Утилиты", "Company, calendars, timers, api keys and removed entities."
    ),
    ModuleDocSpec(
        "snapshot",
        "Локальные snapshots",
        "Local-first snapshot build, refresh and management commands.",
    ),
    ModuleDocSpec(
        "query", "Локальные запросы", "Local-only query and metrics commands over snapshots."
    ),
    ModuleDocSpec(
        "addons",
        "Аддоны",
        "Addon catalog, space installation and per-card / per-user addon data.",
    ),
    ModuleDocSpec(
        "github_addon",
        "GitHub-аддон",
        "Pull requests, branches, commits and issues attached to cards by the GitHub addon.",
    ),
)

MODULE_SPECS_BY_KEY: dict[str, ModuleDocSpec] = {spec.key: spec for spec in MODULE_SPECS}
