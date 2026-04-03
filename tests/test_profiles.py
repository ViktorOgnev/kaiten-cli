from __future__ import annotations

from kaiten_cli.profiles import add_profile, list_profiles, remove_profile, resolve_profile, show_profile, use_profile


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

