"""Human-facing registry module descriptions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModuleDocSpec:
    key: str
    label: str
    description: str


MODULE_SPECS: tuple[ModuleDocSpec, ...] = (
    ModuleDocSpec("cards", "Cards", "Cards, bulk reads and card workflows."),
    ModuleDocSpec("comments", "Comments", "Card comments and bulk comment reads."),
    ModuleDocSpec(
        "members",
        "Members and users",
        "Card members, users, groups and space users.",
    ),
    ModuleDocSpec("time_logs", "Time logs", "Time logs, work logs and related analytics inputs."),
    ModuleDocSpec("tags", "Tags", "Tags and card tag assignments."),
    ModuleDocSpec("checklists", "Checklists", "Checklists and checklist items."),
    ModuleDocSpec("blockers", "Blockers", "Card blockers and blocker relations."),
    ModuleDocSpec(
        "card_relations", "Card relations", "Parent/child/planned relations between cards."
    ),
    ModuleDocSpec("external_links", "External links", "External links attached to cards."),
    ModuleDocSpec(
        "files",
        "Card files",
        "Card files, attachments and beta Restricted Access Files.",
    ),
    ModuleDocSpec("subscribers", "Subscribers", "Card and column subscriptions."),
    ModuleDocSpec("spaces", "Spaces", "Spaces and top-level workspace reads."),
    ModuleDocSpec("boards", "Boards", "Boards and board-level operations."),
    ModuleDocSpec(
        "columns", "Columns and subcolumns", "Columns, subcolumns and related card structure."
    ),
    ModuleDocSpec("lanes", "Lanes", "Swimlanes and lane-level operations."),
    ModuleDocSpec("card_types", "Card types", "Card types and type metadata."),
    ModuleDocSpec(
        "custom_directories",
        "Catalogs",
        "Kaiten Catalogs: directories, fields, records and linked cards.",
    ),
    ModuleDocSpec(
        "custom_properties",
        "Custom properties",
        "Custom properties, select values, catalog-values and collective values.",
    ),
    ModuleDocSpec("documents", "Documents", "Documents and document groups."),
    ModuleDocSpec(
        "dashboards",
        "Dashboards",
        "Experimental dashboards, collaborators, widgets and compute jobs.",
    ),
    ModuleDocSpec("iterations", "Iterations", "Beta iterations, iteration cards and card history."),
    ModuleDocSpec("webhooks", "Webhooks", "Webhook configuration and delivery settings."),
    ModuleDocSpec(
        "automations", "Automations and workflows", "Automations, incoming webhooks and workflows."
    ),
    ModuleDocSpec(
        "addons",
        "Addons",
        "Addon catalog, space installation and per-card / per-user addon data.",
    ),
    ModuleDocSpec(
        "github_addon",
        "GitHub addon",
        "Pull requests, branches, commits and issues attached to cards by the GitHub addon.",
    ),
    ModuleDocSpec("projects", "Projects and sprints", "Projects, project cards and sprints."),
    ModuleDocSpec(
        "roles_and_groups", "Roles and groups", "Roles, groups and permission-related operations."
    ),
    ModuleDocSpec("scim", "SCIM", "SCIM v2 user and group provisioning."),
    ModuleDocSpec(
        "audit_and_analytics",
        "Audit and analytics",
        "Audit logs, activity, saved filters and analytics helpers.",
    ),
    ModuleDocSpec(
        "service_desk",
        "Service Desk",
        "Service Desk requests, users, SLA, organizations and settings.",
    ),
    ModuleDocSpec("charts", "Charts and analytics", "Chart endpoints and compute jobs."),
    ModuleDocSpec("tree", "Entity tree", "Entity tree and tree navigation commands."),
    ModuleDocSpec(
        "utilities", "Utilities", "Company, calendars, timers, api keys and removed entities."
    ),
    ModuleDocSpec(
        "snapshot",
        "Local snapshots",
        "Local-first snapshot build, refresh and management commands.",
    ),
    ModuleDocSpec(
        "query", "Local queries", "Local-only query and metrics commands over snapshots."
    ),
)

MODULE_SPECS_BY_KEY: dict[str, ModuleDocSpec] = {spec.key: spec for spec in MODULE_SPECS}
