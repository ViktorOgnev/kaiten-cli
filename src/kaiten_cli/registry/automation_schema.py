"""Offline schemas normalized from the public automation modal tables.

Unknown variants/fields remain open for newer or on-premises servers. The source
snapshot and normalization script are checked into the repository for review.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

AUTOMATION_SCHEMAS = json.loads(Path(__file__).with_name("automation_schemas.json").read_text())


def automation_properties():
    return {
        "trigger": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "hasToFireOnCardCreation": {"type": "boolean"},
                "data": {"type": "object"},
            },
            "description": "Trigger configuration. Known variants are checked; server extensions are preserved.",
            "x-variants": deepcopy(AUTOMATION_SCHEMAS["triggers"]),
        },
        "actions": {
            "type": "array",
            "minItems": 1,
            "maxItems": 10,
            "items": {"type": "object", "x-variants": deepcopy(AUTOMATION_SCHEMAS["actions"])},
            "description": "Ordered automation actions (1–10). Known variants are checked; server extensions are preserved.",
        },
        "conditions": {
            "type": "object",
            "description": "Recursive and/or groups: {clause, conditions: [groups or typed conditions]}. Empty object means no conditions.",
            "properties": {
                "clause": {"type": "string", "enum": ["and", "or"]},
                "conditions": {"type": "array", "items": {"type": "object"}},
            },
            "x-variants": deepcopy(AUTOMATION_SCHEMAS["conditions"]),
        },
    }
