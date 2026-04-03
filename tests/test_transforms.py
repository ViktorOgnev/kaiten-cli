from __future__ import annotations

from kaiten_cli.transforms import compact_response, select_fields, strip_base64


def test_compact_response_simplifies_and_strips():
    data = {
        "description": "large text",
        "owner": {"id": 1, "full_name": "Alice", "avatar_url": "data:image/png;base64,abc"},
        "members": [{"id": 2, "full_name": "Bob"}],
    }
    result = compact_response(data, compact=True)
    assert "description" not in result
    assert result["owner"] == {"id": 1, "full_name": "Alice"}
    assert result["members"] == [{"id": 2, "full_name": "Bob"}]


def test_strip_base64_replaces_payload():
    data, count = strip_base64({"avatar": "data:image/png;base64,abc"})
    assert count == 1
    assert data["avatar"].startswith("[base64")


def test_select_fields_filters_dict_and_list():
    data = [{"id": 1, "title": "A", "state": 2}]
    assert select_fields(data, "id,title") == [{"id": 1, "title": "A"}]

