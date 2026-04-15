from __future__ import annotations

from kaiten_cli.errors import ValidationError
from kaiten_cli.runtime.output import render_error, render_success


def test_render_success_human_dict():
    output = render_success("cards.get", {"id": 1, "title": "Task"}, False)
    assert '"title": "Task"' in output


def test_render_error_human():
    output = render_error("cards.get", ValidationError("bad field"), False)
    assert "Validation error" in output
    assert "bad field" in output
