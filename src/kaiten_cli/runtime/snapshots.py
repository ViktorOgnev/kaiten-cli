"""Compatibility facade for local snapshot and query commands.

Implementations are split by responsibility: SQLite persistence, remote snapshot
building, and local query/metric execution. Registry imports remain stable here.
"""

from kaiten_cli.runtime.snapshot_build import (
    execute_snapshot_build,
    execute_snapshot_delete,
    execute_snapshot_list,
    execute_snapshot_refresh,
    execute_snapshot_show,
    validate_snapshot_build,
)
from kaiten_cli.runtime.snapshot_common import (
    DEFAULT_LOCAL_LIMIT,
    DETAIL_VIEW_FIELDS,
    EVIDENCE_VIEW_FIELDS,
    QUERY_CARD_VIEWS,
    QUERY_FILTER_KEYS,
    QUERY_GROUP_BY,
    QUERY_METRICS,
    SNAPSHOT_DB_SCHEMA_VERSION,
    SNAPSHOT_PRESETS,
    SNAPSHOT_SCHEMA_VERSION,
    SUMMARY_VIEW_FIELDS,
    VIEW_FIELDS,
    WINDOW_PRESETS,
)
from kaiten_cli.runtime.snapshot_query import (
    execute_query_cards,
    execute_query_metrics,
    validate_query_filter,
)
from kaiten_cli.runtime.snapshot_store import SnapshotStore, snapshot_db_path

__all__ = [
    "DEFAULT_LOCAL_LIMIT",
    "DETAIL_VIEW_FIELDS",
    "EVIDENCE_VIEW_FIELDS",
    "QUERY_CARD_VIEWS",
    "QUERY_FILTER_KEYS",
    "QUERY_GROUP_BY",
    "QUERY_METRICS",
    "SNAPSHOT_DB_SCHEMA_VERSION",
    "SNAPSHOT_PRESETS",
    "SNAPSHOT_SCHEMA_VERSION",
    "SUMMARY_VIEW_FIELDS",
    "SnapshotStore",
    "VIEW_FIELDS",
    "WINDOW_PRESETS",
    "execute_query_cards",
    "execute_query_metrics",
    "execute_snapshot_build",
    "execute_snapshot_delete",
    "execute_snapshot_list",
    "execute_snapshot_refresh",
    "execute_snapshot_show",
    "snapshot_db_path",
    "validate_query_filter",
    "validate_snapshot_build",
]
