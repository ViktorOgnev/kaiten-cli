from __future__ import annotations

import pytest

from kaiten_cli.errors import ConfigError
from kaiten_cli.profiles import add_profile, config_path, list_profiles, remove_profile, resolve_profile, show_profile, use_profile


def test_profile_lifecycle(config_env):
    added = add_profile("sandbox", domain="sandbox", token="secret-token", sandbox=True, set_active=True)
    assert added["active"] is True
    assert added["sandbox"] is True
    assert added["token_masked"].endswith("oken")

    listed = list_profiles()
    assert listed[0]["name"] == "sandbox"

    shown = show_profile()
    assert shown["name"] == "sandbox"

    resolved = resolve_profile()
    assert resolved.domain == "sandbox"
    assert resolved.sandbox is True

    use_profile("sandbox")
    removed = remove_profile("sandbox")
    assert removed["name"] == "sandbox"


def test_resolve_profile_uses_env_fallback(config_env, monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")
    resolved = resolve_profile()
    assert resolved.domain == "sandbox"
    assert resolved.token == "env-token"


def test_resolve_profile_guides_setup_when_missing(config_env, monkeypatch):
    monkeypatch.delenv("KAITEN_DOMAIN", raising=False)
    monkeypatch.delenv("KAITEN_TOKEN", raising=False)

    with pytest.raises(ConfigError) as excinfo:
        resolve_profile()

    message = str(excinfo.value)
    assert f"Config file: {config_path()}" in message
    assert "kaiten profile add main --domain <company-subdomain> --token <api-token> --set-active" in message
    assert "export KAITEN_DOMAIN=<company-subdomain>" in message
    assert "kaiten --json spaces list --compact --fields id,title" in message


def test_resolve_profile_unknown_profile_guides_listing(config_env, monkeypatch):
    monkeypatch.delenv("KAITEN_DOMAIN", raising=False)
    monkeypatch.delenv("KAITEN_TOKEN", raising=False)
    add_profile("sandbox", domain="sandbox", token="secret-token", sandbox=True, set_active=True)

    with pytest.raises(ConfigError) as excinfo:
        resolve_profile("prod")

    message = str(excinfo.value)
    assert "Unknown profile: prod" in message
    assert "kaiten profile list" in message
    assert "kaiten profile use <name>" in message
