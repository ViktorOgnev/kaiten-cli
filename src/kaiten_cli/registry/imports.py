"""Migration commands shared by terminal and agent discovery."""

from kaiten_cli.models import ExampleSpec, OperationSpec, RuntimeBehavior
from kaiten_cli.registry.base import make_tool
from kaiten_cli.runtime.imports.workflow import execute

WORK_DIR = {"type": "string", "description": "Private import workspace parent directory."}
PLAN_FIELDS = {
    "source": {"type": "string", "description": "Import source name from import sources."},
    "space_id": {"type": "integer", "minimum": 1, "description": "Target Kaiten space ID."},
    "space_uid": {
        "type": "string",
        "description": "Explicit target Kaiten space UUID if the public API omits it.",
    },
    "company_id": {"type": "integer", "minimum": 1, "description": "Target Kaiten company ID."},
    "input": {"type": "string", "description": "Path to the source export or package."},
    "boards": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Trello board IDs or URLs as a JSON array.",
    },
    "column_types": {
        "type": "object",
        "description": "Map Trello list IDs to Kaiten column types.",
    },
    "work_dir": WORK_DIR,
}
RUN_FIELDS = {
    "run": {"type": "string", "description": "Import run ID returned by import plan."},
    "work_dir": WORK_DIR,
}


def _command(action, description, fields, *, method="GET", profile=True, example=None):
    return make_tool(
        canonical_name=f"import.{action}",
        mcp_alias=f"kaiten_import_{action}",
        description=description,
        input_schema={
            "type": "object",
            "properties": fields,
            "required": ["run"] if "run" in fields else [],
        },
        operation=OperationSpec(method=method, path_template=f"/local/import/{action}"),
        runtime_behavior=RuntimeBehavior(
            execution_mode="custom",
            custom_executor=execute,
            cache_policy="none",
            requires_profile=profile,
            enforce_mutation_guard=False,
            remote_side_effects=False,
            apply_common_transforms=False,
        ),
        examples=(ExampleSpec(command=example, description=description),) if example else (),
    )


TOOLS = (
    _command(
        "sources",
        "List available migration sources and handoff modes.",
        {},
        profile=False,
        example="kaiten import sources",
    ),
    _command(
        "plan",
        "Preview a migration and pin its Kaiten target.",
        PLAN_FIELDS,
        example="kaiten --json import plan --source trello --input ./trello.json --space-id 123",
    ),
    _command(
        "run",
        "Guide a migration in an interactive terminal.",
        PLAN_FIELDS,
        method="POST",
        example="kaiten import run",
    ),
    _command(
        "credentials",
        "Enter the source credentials locally without echoing them.",
        RUN_FIELDS,
        method="POST",
        profile=False,
    ),
    _command(
        "prepare",
        "Prepare the local import package.",
        RUN_FIELDS,
        method="POST",
    ),
    _command(
        "open",
        "Open the official Convertinator or the Kaiten import interface.",
        {
            **RUN_FIELDS,
            "app_path": {
                "type": "string",
                "description": "Path to the installed Convertinator application.",
            },
        },
        method="POST",
    ),
    _command(
        "status",
        "Read the import report and reconcile target data.",
        {
            **RUN_FIELDS,
            "report": {"type": "string", "description": "Path to a terminal Convertinator report."},
        },
    ),
    _command(
        "cleanup",
        "Remove staged files while preserving import reports.",
        RUN_FIELDS,
        method="DELETE",
        profile=False,
    ),
)
