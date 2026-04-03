"""Response transforms copied conceptually from kaiten-mcp."""

from __future__ import annotations

from typing import Any

DEFAULT_LIMIT = 50
SIMPLIFY_FIELDS = {"owner", "responsible", "author", "user", "created_by", "updated_by"}
SIMPLIFY_LIST_FIELDS = {"members", "responsibles", "owners", "subscribers", "participants"}
STRIP_FIELDS = {"description"}


def _is_base64_avatar(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("data:")


def _simplify_user(user: Any) -> Any:
    if not isinstance(user, dict):
        return user
    result: dict[str, Any] = {}
    if "id" in user:
        result["id"] = user["id"]
    if "full_name" in user:
        result["full_name"] = user["full_name"]
    elif "username" in user:
        result["full_name"] = user["username"]
    return result or user


def _compact_dict(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in data.items():
        if key in STRIP_FIELDS:
            continue
        if key == "avatar_url" and _is_base64_avatar(value):
            continue
        if key == "avatar" and _is_base64_avatar(value):
            continue
        if key in SIMPLIFY_FIELDS and isinstance(value, dict):
            result[key] = _simplify_user(value)
        elif key in SIMPLIFY_LIST_FIELDS and isinstance(value, list):
            result[key] = [
                _simplify_user(item) if isinstance(item, dict) else item for item in value
            ]
        elif isinstance(value, dict):
            result[key] = _compact_dict(value)
        elif isinstance(value, list):
            result[key] = _compact_list(value)
        else:
            result[key] = value
    return result


def _compact_list(data: list[Any]) -> list[Any]:
    result: list[Any] = []
    for item in data:
        if isinstance(item, dict):
            result.append(_compact_dict(item))
        elif isinstance(item, list):
            result.append(_compact_list(item))
        else:
            result.append(item)
    return result


def compact_response(data: Any, compact: bool = False) -> Any:
    if not compact:
        return data
    if isinstance(data, dict):
        return _compact_dict(data)
    if isinstance(data, list):
        return _compact_list(data)
    return data


def _strip_b64_value(value: str) -> str:
    size_kb = len(value) // 1024
    return f"[base64 ~{size_kb}KB, omitted]"


def _strip_b64_dict(data: dict[str, Any], counter: list[int]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str) and value.startswith("data:"):
            result[key] = _strip_b64_value(value)
            counter[0] += 1
        elif isinstance(value, dict):
            result[key] = _strip_b64_dict(value, counter)
        elif isinstance(value, list):
            result[key] = _strip_b64_list(value, counter)
        else:
            result[key] = value
    return result


def _strip_b64_list(data: list[Any], counter: list[int]) -> list[Any]:
    result: list[Any] = []
    for item in data:
        if isinstance(item, dict):
            result.append(_strip_b64_dict(item, counter))
        elif isinstance(item, list):
            result.append(_strip_b64_list(item, counter))
        else:
            result.append(item)
    return result


def strip_base64(data: Any) -> tuple[Any, int]:
    counter = [0]
    if isinstance(data, dict):
        return _strip_b64_dict(data, counter), counter[0]
    if isinstance(data, list):
        return _strip_b64_list(data, counter), counter[0]
    return data, 0


def select_fields(data: Any, fields_str: str | None) -> Any:
    if not fields_str:
        return data

    keys = {field.strip() for field in fields_str.split(",") if field.strip()}
    if isinstance(data, list):
        return [{k: v for k, v in item.items() if k in keys} for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if k in keys}
    return data

