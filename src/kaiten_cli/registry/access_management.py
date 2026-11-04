"""API-token extensions for entity metadata and access control.

Contracts: Kaiten routes/api.js and controllers adminTreeEntitiesController,
documents/baseDocumentUsers, storyMaps/{index,users}, TreeEntityGroupsBase,
treeEntityRolesController. These are ordinary API routes, not browser sessions.
"""

from __future__ import annotations

from kaiten_cli.models import (
    CACHE_POLICY_REQUEST_SCOPE,
    ExampleSpec,
    OperationSpec,
    ResponsePolicy,
    RuntimeBehavior,
)
from kaiten_cli.registry.base import make_tool, shaping_properties
from kaiten_cli.runtime.support.access_management import (
    execute_admin_list_all,
    story_map_create_request,
    validate_admin_list_all,
    validate_entity_user,
)


GUIDE = "Access management reference: https://github.com/ViktorOgnev/kaiten-cli/blob/master/docs/ACCESS_MANAGEMENT.md; agent skill: skills/kaiten-cli-access-management/SKILL.md."
EXTENSION = "Undocumented API-token extension derived from Kaiten server routes and controllers; validated on an authorized test company on 2026-11-04. Availability still depends on server version, permissions and modules. No browser or Superadmin authentication is used."
INHERITANCE = "Removing a direct assignment does not revoke access inherited from ancestors, groups, or everyone access."
ACL_PERMISSION = "Requires entity access_control permission or company entitiesTree permission; inviting a new company user needs additional invitation rights."
GROUP_PERMISSION = "Requires entity access_control permission or company entitiesTree/members permission. Use documented group-entities commands to change group assignments."
ROLE_PERMISSION = "Requires company members permission and the Groups module for writes. System roles and locked roles cannot be changed; deleting a used role may require replacing_role_id."
ROLE_KIND = "roles uses UUID tree-entity access roles; user-roles uses numeric timesheet roles and cannot assign entity permissions."
ROLE_PATCH = "PATCH permissions merges only supplied keys on the server; send false explicitly to remove a permission. A shared role change affects all its assignments."
READ = RuntimeBehavior(cache_policy=CACHE_POLICY_REQUEST_SCOPE)
UID = {"type": "string", "format": "uuid", "description": "Tree entity UID (UUID)."}
USER = {"type": "integer", "minimum": 1, "description": "User ID"}
ROLE = {"type": "string", "format": "uuid", "description": "Tree entity role ID (UUID)."}
INHERITED = {"type": "boolean", "description": "Include inherited access."}
ENTITY_TYPES = "space,document,document_group,story_map"
EXAMPLE_UID = "11111111-1111-4111-8111-111111111111"
SEARCH = (
    "доступ права пользователи группы роли администрирование",
    "access permissions membership",
)


def _tool(
    name,
    description,
    props,
    *,
    method="GET",
    path,
    required=(),
    query=(),
    body=(),
    notes=(),
    behavior=None,
    list_result=False,
    heavy=False,
    example=None,
    bulk=None,
):
    return make_tool(
        canonical_name=name,
        mcp_alias="kaiten_" + name.replace("-", "_").replace(".", "_"),
        description=description,
        input_schema={"type": "object", "properties": props, "required": list(required)},
        operation=OperationSpec(
            method=method,
            path_template=path,
            path_fields=tuple(field for field in props if "{" + field + "}" in path),
            query_fields=tuple(query),
            body_fields=tuple(body),
        ),
        response_policy=ResponsePolicy(
            compact_supported=True, fields_supported=True, result_kind="list", heavy=heavy
        )
        if list_result
        else ResponsePolicy(),
        runtime_behavior=behavior or (READ if method == "GET" else RuntimeBehavior()),
        usage_notes=(EXTENSION, *notes, GUIDE),
        search_terms=SEARCH
        + tuple(
            terms
            for prefix, terms in (
                ("document-users", "документ документы"),
                ("document-access", "документ документы"),
                ("document-group", "папка папки"),
                ("story-map", "карта карты историй"),
                ("admin-tree", "административное дерево инвентаризация"),
            )
            if name.startswith(prefix)
        ),
        examples=(ExampleSpec(command=example, description=description),) if example else (),
        bulk_alternative=bulk,
    )


def _entity_users(namespace, base, id_name, id_schema, example_id):
    target = {id_name: id_schema}
    command = namespace.replace(".", " ")
    selector = f"--{id_name.replace('_', '-')} {example_id}"
    yield _tool(
        f"{namespace}.list",
        "List users with access to an entity.",
        {**target, "include_inherited_access": INHERITED, **shaping_properties()},
        path=base,
        required=(id_name,),
        query=("include_inherited_access",),
        list_result=True,
        notes=(ACL_PERMISSION, INHERITANCE),
        example=f"kaiten --json {command} list {selector} --include-inherited-access true",
    )
    attributes = {
        "user_id": USER,
        "role_id": ROLE,
        "email": {"type": "string", "description": "User email address"},
        "guest": {"type": "boolean", "description": "Set true to invite the user as a guest"},
        "send_email": {"type": "boolean", "description": "Whether to send email or not"},
        "operator_comment": {"type": "string", "description": "Operator's comment"},
    }
    yield _tool(
        f"{namespace}.add",
        "Assign an entity role to a user.",
        {**target, **attributes},
        method="POST",
        path=base,
        required=(id_name,),
        body=tuple(attributes),
        behavior=RuntimeBehavior(payload_validator=validate_entity_user),
        notes=(ACL_PERMISSION,),
        example=f"kaiten --json {command} add {selector} --user-id 7 --role-id {EXAMPLE_UID}",
    )
    yield _tool(
        f"{namespace}.update",
        "Change a user's direct entity role.",
        {**target, "user_id": USER, "role_id": ROLE},
        method="PATCH",
        path=base + "/{user_id}",
        required=(id_name, "user_id", "role_id"),
        body=("role_id",),
        notes=(ACL_PERMISSION, INHERITANCE),
        example=f"kaiten --json {command} update {selector} --user-id 7 --role-id {EXAMPLE_UID}",
    )
    yield _tool(
        f"{namespace}.remove",
        "Remove a user's direct entity role.",
        {**target, "user_id": USER},
        method="DELETE",
        path=base + "/{user_id}",
        required=(id_name, "user_id"),
        notes=(ACL_PERMISSION, INHERITANCE),
        example=f"kaiten --json {command} remove {selector} --user-id 7",
    )


ADMIN_PROPS = {
    "parent_uid": UID,
    "query": {"type": "string", "description": "Search query."},
    "user_id": USER,
    "group_uid": {"type": "string", "format": "uuid", "description": "Group UID"},
    "role_id": ROLE,
    "entity_types": {
        "type": "string",
        "description": "Comma-separated entity types: space, document, document_group, story_map.",
    },
    "access": {"type": "string", "enum": ["for_everyone", "by_invite"]},
    "relations": {"type": "string", "description": "Comma-separated server relation names."},
    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
    "offset": {"type": "integer", "minimum": 0},
    **shaping_properties(),
}
ADMIN_NOTES = (
    "Requires company entitiesTree or members permission. Returns metadata, not content access. user_id filters by that user's visibility; omit it for company inventory.",
    "Without parent_uid or other filters, list returns roots. entity_types requests a flat list. Administrative parent_uid differs from public tree-entities parent_entity_uid.",
    "Offset pagination is not an atomic snapshot; concurrent creates, renames, moves and access changes may cause omissions. Archived/protected entities are not a complete event history.",
)


def _tools():
    yield _tool(
        "admin-tree-entities.list",
        "List one page of administrative tree metadata.",
        ADMIN_PROPS,
        path="/admin-tree-entities",
        query=tuple(k for k in ADMIN_PROPS if k not in ("compact", "fields")),
        list_result=True,
        notes=ADMIN_NOTES,
        example="kaiten --json admin-tree-entities list --limit 100 --offset 0 --fields uid,title,entity_type,parent_entity_uid",
        bulk="admin-tree-entities.list-all",
    )
    yield _tool(
        "admin-tree-entities.list-all",
        "Read a bounded flat administrative tree inventory.",
        {
            "page_size": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "description": "Page size (default 100, max 100).",
            },
            "max_pages": {
                "type": "integer",
                "minimum": 1,
                "maximum": 1000,
                "description": "Maximum pages (default 100, max 1000).",
            },
            **shaping_properties(),
        },
        path="/admin-tree-entities",
        list_result=True,
        heavy=True,
        notes=ADMIN_NOTES
        + (
            "Reads all pages with entity_types=space,document,document_group,story_map. Repeated entities, malformed pages and a reached page cap fail instead of returning a partial inventory.",
        ),
        behavior=RuntimeBehavior(
            execution_mode="aggregated",
            custom_executor=execute_admin_list_all,
            payload_validator=validate_admin_list_all,
            cache_policy=CACHE_POLICY_REQUEST_SCOPE,
        ),
        example="kaiten --json admin-tree-entities list-all --max-pages 100 --fields uid,title,entity_type,parent_entity_uid",
    )
    for namespace, path, key, schema, value in (
        ("document-users", "/documents/{document_uid}/users", "document_uid", UID, EXAMPLE_UID),
        (
            "document-group-users",
            "/document-groups/{group_uid}/users",
            "group_uid",
            UID,
            EXAMPLE_UID,
        ),
        (
            "story-map-users",
            "/story-maps/{map_id}/users",
            "map_id",
            {"type": "integer", "minimum": 1, "description": "Story map ID."},
            "10",
        ),
    ):
        yield from _entity_users(namespace, path, key, schema, value)
    for namespace, path in (
        ("space-access-groups", "/spaces/{entity_uid}/groups"),
        ("document-access-groups", "/documents/{entity_uid}/groups"),
        ("document-group-access-groups", "/document-groups/{entity_uid}/groups"),
        ("story-map-access-groups", "/story-maps/{entity_uid}/groups"),
    ):
        yield _tool(
            f"{namespace}.list",
            "List group access to an entity.",
            {
                "entity_uid": UID,
                "include_inherited_access": INHERITED,
                "with_current_user_as_admin_check": {
                    "type": "boolean",
                    "description": "Include whether the current user administers each group.",
                },
                **shaping_properties(),
            },
            path=path,
            required=("entity_uid",),
            query=("include_inherited_access", "with_current_user_as_admin_check"),
            list_result=True,
            notes=(GROUP_PERMISSION, INHERITANCE),
            example=f"kaiten --json {namespace} list --entity-uid {EXAMPLE_UID} --include-inherited-access true",
        )
    role_props = {
        "name": {"type": "string", "minLength": 1, "maxLength": 128, "description": "Role name"},
        "permissions": {
            "type": "object",
            "description": "Tree entity permissions JSON; create requires the complete server permission structure, update accepts a partial object.",
        },
        "new_permissions_default_value": {
            "type": "boolean",
            "description": "Grant newly introduced permissions by default.",
        },
    }
    yield _tool(
        "roles.create",
        "Create a tree entity access role.",
        role_props,
        method="POST",
        path="/tree-entity-roles",
        required=("name", "permissions"),
        body=tuple(role_props),
        notes=(ROLE_PERMISSION, ROLE_KIND),
        example="kaiten --json --from-file role.json roles create",
    )
    yield _tool(
        "roles.update",
        "Update a tree entity access role.",
        {"role_id": ROLE, **role_props, "sort_order": {"type": "number"}},
        method="PATCH",
        path="/tree-entity-roles/{role_id}",
        required=("role_id",),
        body=(*role_props, "sort_order"),
        notes=(ROLE_PERMISSION, ROLE_KIND, ROLE_PATCH),
        example=f'kaiten --json roles update --role-id {EXAMPLE_UID} --permissions \'{{"document":{{"read":false}}}}\'',
    )
    yield _tool(
        "roles.delete",
        "Delete a tree entity access role.",
        {"role_id": ROLE, "replacing_role_id": ROLE},
        method="DELETE",
        path="/tree-entity-roles/{role_id}",
        required=("role_id",),
        body=("replacing_role_id",),
        notes=(ROLE_PERMISSION, ROLE_KIND),
        example=f"kaiten --json roles delete --role-id {EXAMPLE_UID}",
    )
    story_props = {
        "title": {"type": "string", "minLength": 1, "maxLength": 256, "description": "Title"},
        "description": {
            "type": ["string", "null"],
            "maxLength": 32768,
            "description": "Description",
        },
        "access": {"type": "string", "enum": ["for_everyone", "by_invite"]},
        "parent_entity_uid": {
            "type": ["string", "null"],
            "description": "Parent tree entity UID; null moves to the company root.",
        },
        "for_everyone_access_role_id": ROLE,
        "sort_order": {"type": "number", "exclusiveMinimum": 0},
        "key": {
            "type": ["string", "null"],
            "description": "Company-unique story map key; null clears the key.",
        },
    }
    map_id = {"map_id": {"type": "integer", "minimum": 1, "description": "Story map ID."}}
    story_notes = (
        "Requires the Story maps module. Reads use object read permission, updates use update permission (or entitiesTree for metadata); moves require source/destination move/create rights. Creation requires paid access and create permission at the destination; deletion requires object delete permission.",
        "Listing includes only readable story maps. Moving an entity changes inherited access. Deletion refuses active child entities; there is no automatic force or self-grant fallback.",
    )
    yield _tool(
        "story-maps.list",
        "List readable story maps.",
        {
            "query": {"type": "string"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            "offset": {"type": "integer", "minimum": 0},
            **shaping_properties(),
        },
        path="/story-maps",
        query=("query", "limit", "offset"),
        list_result=True,
        notes=story_notes,
        example="kaiten --json story-maps list --limit 100 --offset 0",
    )
    yield _tool(
        "story-maps.get",
        "Get a story map.",
        map_id,
        path="/story-maps/{map_id}",
        required=("map_id",),
        notes=story_notes,
        example="kaiten --json story-maps get --map-id 10",
    )
    yield _tool(
        "story-maps.create",
        "Create a story map.",
        story_props,
        method="POST",
        path="/story-maps",
        required=("title",),
        behavior=RuntimeBehavior(request_shaper=story_map_create_request),
        body=tuple(story_props),
        notes=story_notes
        + (
            "Creation supplies sort_order as the current Unix timestamp when omitted, matching document creation; this avoids HTTP 500 on server versions requiring an explicit position. Explicit sort_order is preserved.",
        ),
        example='kaiten --json story-maps create --title "Project roadmap" --access by_invite',
    )
    yield _tool(
        "story-maps.update",
        "Update or move a story map.",
        {**map_id, **story_props},
        method="PATCH",
        path="/story-maps/{map_id}",
        required=("map_id",),
        body=tuple(story_props),
        notes=story_notes,
        example="kaiten --json story-maps update --map-id 10 --parent-entity-uid null",
    )
    yield _tool(
        "story-maps.delete",
        "Delete a story map.",
        map_id,
        method="DELETE",
        path="/story-maps/{map_id}",
        required=("map_id",),
        notes=story_notes,
        example="kaiten --json story-maps delete --map-id 10",
    )


TOOLS = tuple(_tools())
