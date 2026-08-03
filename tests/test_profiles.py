from __future__ import annotations

import json
import stat

import httpx
import pytest
import respx
from httpx import Response

from kaiten_cli.app import main
from kaiten_cli.errors import ConfigError
from kaiten_cli.profiles import (
    add_profile,
    config_path,
    list_profiles,
    remove_profile,
    resolve_profile,
    save_config,
    show_profile,
    use_profile,
)
from kaiten_cli.runtime.client import KaitenClient


def test_profile_lifecycle(config_env):
    added = add_profile(
        "sandbox", domain="sandbox", token="secret-token", sandbox=True, set_active=True
    )
    assert added["active"] is True
    assert added["sandbox"] is True
    assert added["cache_mode"] == "auto"
    assert added["cache_ttl_seconds"] == 60
    assert added["token_masked"].endswith("oken")

    listed = list_profiles()
    assert listed[0]["name"] == "sandbox"

    shown = show_profile()
    assert shown["name"] == "sandbox"

    resolved = resolve_profile()
    assert resolved.domain == "sandbox"
    assert resolved.sandbox is True
    assert resolved.source == "active_profile"
    assert resolved.cache_mode == "auto"
    assert resolved.cache_ttl_seconds == 60

    use_profile("sandbox")
    removed = remove_profile("sandbox")
    assert removed["name"] == "sandbox"


def test_profile_config_is_private_and_atomically_replaced(config_env):
    add_profile("main", domain="sandbox", token="secret-token", set_active=True)
    path = config_path()
    first_inode = path.stat().st_ino

    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700

    add_profile("second", domain="sandbox", token="second-token")

    assert path.stat().st_ino != first_inode
    assert (
        json.loads(path.read_text(encoding="utf-8"))["profiles"]["second"]["token"]
        == "second-token"
    )
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_profile_load_repairs_permissive_file_mode(config_env):
    add_profile("main", domain="sandbox", token="secret-token", set_active=True)
    path = config_path()
    path.chmod(0o644)

    assert show_profile()["name"] == "main"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_profile_load_reports_corrupt_json_as_config_error(config_env):
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{broken", encoding="utf-8")

    with pytest.raises(ConfigError, match="Unable to read Kaiten CLI config"):
        show_profile()


def test_config_override_preserves_existing_parent_mode(monkeypatch, tmp_path):
    shared_directory = tmp_path / "shared-config"
    shared_directory.mkdir(mode=0o755)
    shared_directory.chmod(0o755)
    monkeypatch.setenv("KAITEN_CLI_CONFIG_PATH", str(shared_directory / "config.json"))

    save_config({"active_profile": None, "profiles": {}})

    assert stat.S_IMODE(shared_directory.stat().st_mode) == 0o755
    assert stat.S_IMODE(config_path().stat().st_mode) == 0o600


def test_resolve_profile_uses_env_fallback(config_env, monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")
    resolved = resolve_profile()
    assert resolved.domain == "sandbox"
    assert resolved.token == "env-token"
    assert resolved.sandbox is False
    assert resolved.source == "environment"
    assert resolved.cache_mode == "auto"
    assert resolved.cache_ttl_seconds == 60


def test_profile_add_normalizes_kaiten_url_domain(config_env):
    added = add_profile(
        "main",
        domain="https://Sandbox.kaiten.ru/space/1/boards",
        token="secret-token",
        set_active=True,
    )

    shown = show_profile("main")
    resolved = resolve_profile()

    assert added["domain"] == "sandbox"
    assert shown["domain"] == "sandbox"
    assert resolved.domain == "sandbox"
    assert KaitenClient(domain=resolved.domain, token=resolved.token).base_url == (
        "https://sandbox.kaiten.ru/api/latest"
    )


def test_resolve_profile_normalizes_existing_full_kaiten_domain(config_env):
    save_config(
        {
            "active_profile": "main",
            "profiles": {
                "main": {
                    "domain": "https://sandbox.kaiten.ru",
                    "token": "secret-token",
                    "sandbox": False,
                }
            },
        }
    )

    shown = show_profile()
    resolved = resolve_profile()

    assert shown["domain"] == "sandbox"
    assert resolved.domain == "sandbox"


def test_resolve_profile_preserves_custom_host_with_port(config_env):
    add_profile("dev", domain="62.84.125.64:3200", token="secret-token", set_active=True)

    resolved = resolve_profile()
    client = KaitenClient(domain=resolved.domain, token=resolved.token)

    assert resolved.domain == "62.84.125.64:3200"
    assert client.root_url == "https://62.84.125.64:3200"
    assert client.base_url == "https://62.84.125.64:3200/api/latest"


def test_resolve_profile_preserves_http_custom_host(config_env):
    add_profile("dev", domain="http://localhost:3000", token="secret-token", set_active=True)

    resolved = resolve_profile()
    client = KaitenClient(domain=resolved.domain, token=resolved.token)

    assert resolved.domain == "http://localhost:3000"
    assert client.root_url == "http://localhost:3000"
    assert client.base_url == "http://localhost:3000/api/latest"


def test_resolve_profile_env_normalizes_full_kaiten_url(config_env, monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "https://sandbox.kaiten.ru")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")

    resolved = resolve_profile()

    assert resolved.domain == "sandbox"


def test_resolve_profile_env_domain_does_not_imply_test_metadata(config_env, monkeypatch):
    monkeypatch.setenv("KAITEN_DOMAIN", "sandbox")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")

    resolved = resolve_profile()

    assert resolved.domain == "sandbox"
    assert resolved.sandbox is False


def test_profile_add_and_resolve_cache_settings(config_env):
    add_profile(
        "main",
        domain="sandbox",
        token="secret-token",
        sandbox=True,
        cache_mode="readwrite",
        cache_ttl_seconds=120,
        set_active=True,
    )

    shown = show_profile("main")
    resolved = resolve_profile()

    assert shown["cache_mode"] == "readwrite"
    assert shown["cache_ttl_seconds"] == 120
    assert resolved.cache_mode == "readwrite"
    assert resolved.cache_ttl_seconds == 120


def test_resolve_profile_cli_cache_overrides_profile_defaults(config_env):
    add_profile(
        "main",
        domain="sandbox",
        token="secret-token",
        sandbox=True,
        cache_mode="readwrite",
        cache_ttl_seconds=120,
        set_active=True,
    )

    resolved = resolve_profile("main", cache_mode_override="refresh", cache_ttl_seconds_override=15)

    assert resolved.cache_mode == "refresh"
    assert resolved.cache_ttl_seconds == 15


def test_resolve_profile_explicit_profile_beats_active_and_env(config_env, monkeypatch):
    add_profile("main", domain="active-tenant", token="active-token", set_active=True)
    add_profile("sandbox", domain="sandbox", token="sandbox-token", sandbox=True)
    monkeypatch.setenv("KAITEN_DOMAIN", "env-tenant")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")

    resolved = resolve_profile("sandbox")

    assert resolved.name == "sandbox"
    assert resolved.domain == "sandbox"
    assert resolved.token == "sandbox-token"
    assert resolved.sandbox is True
    assert resolved.source == "explicit_profile"


def test_resolve_profile_active_profile_beats_env(config_env, monkeypatch):
    add_profile("main", domain="active-tenant", token="active-token", set_active=True)
    monkeypatch.setenv("KAITEN_DOMAIN", "env-tenant")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")

    resolved = resolve_profile()

    assert resolved.name == "main"
    assert resolved.domain == "active-tenant"
    assert resolved.token == "active-token"
    assert resolved.source == "active_profile"


def test_resolve_profile_uses_env_when_profiles_exist_but_none_active(config_env, monkeypatch):
    save_config(
        {
            "active_profile": None,
            "profiles": {
                "main": {
                    "domain": "active-tenant",
                    "token": "active-token",
                    "sandbox": False,
                }
            },
        }
    )
    monkeypatch.setenv("KAITEN_DOMAIN", "env-tenant")
    monkeypatch.setenv("KAITEN_TOKEN", "env-token")

    resolved = resolve_profile()

    assert resolved.name is None
    assert resolved.domain == "env-tenant"
    assert resolved.token == "env-token"
    assert resolved.source == "environment"


def test_resolve_profile_guides_setup_when_missing(config_env, monkeypatch):
    monkeypatch.delenv("KAITEN_DOMAIN", raising=False)
    monkeypatch.delenv("KAITEN_TOKEN", raising=False)

    with pytest.raises(ConfigError) as excinfo:
        resolve_profile()

    message = str(excinfo.value)
    assert f"Config file: {config_path()}" in message
    assert (
        "kaiten profile add main --domain <company-subdomain-or-url> --token <api-token> --set-active"
        in message
    )
    assert "export KAITEN_DOMAIN=<company-subdomain-or-url>" in message
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


@respx.mock
def test_profile_probe_is_fresh_read_only_and_anonymized(config_env, capsys):
    add_profile(
        "main",
        domain="private-tenant",
        token="secret-token",
        cache_mode="readwrite",
        cache_ttl_seconds=120,
        set_active=True,
    )
    route = respx.get("https://private-tenant.kaiten.ru/api/latest/users/current").mock(
        return_value=Response(
            200,
            json={
                "id": 42,
                "full_name": "Private User",
                "email": "private@example.com",
            },
        )
    )

    assert main(["--json", "--profile", "main", "--read-only", "profile", "probe"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert route.call_count == 1
    assert payload["data"] == {
        "profile": {
            "name": "main",
            "source": "explicit_profile",
            "domain_configured": True,
            "cache_mode": "readwrite",
            "cache_ttl_seconds": 120,
        },
        "authentication": {
            "ok": True,
            "probe_cache_mode": "off",
        },
        "capability_scope": "authentication_only",
        "write_permissions": "not_checked",
    }
    assert payload["stats"]["cache"] == {
        "mode": "off",
        "policy": "request_scope",
        "ttl_seconds": None,
    }
    rendered = json.dumps(payload)
    assert "private-tenant" not in rendered
    assert "Private User" not in rendered
    assert "private@example.com" not in rendered
    assert "secret-token" not in rendered
    assert '"user_id"' not in rendered


@pytest.mark.parametrize("status_code", [401, 403, 503])
@respx.mock
def test_profile_probe_preserves_http_failure_class(
    status_code, config_env, capsys
):
    add_profile("main", domain="sandbox", token="secret-token", set_active=True)
    respx.get("https://sandbox.kaiten.ru/api/latest/users/current").mock(
        return_value=Response(status_code, json={"message": "probe failed"})
    )

    assert main(["--json", "--profile", "main", "profile", "probe"]) == 4
    payload = json.loads(capsys.readouterr().out)

    assert payload["command"] == "profile.probe"
    assert payload["error"]["type"] == "api_error"
    assert payload["error"]["status_code"] == status_code


@respx.mock
def test_profile_probe_preserves_transport_failure(config_env, capsys):
    add_profile("main", domain="sandbox", token="secret-token", set_active=True)
    respx.get("https://sandbox.kaiten.ru/api/latest/users/current").mock(
        side_effect=httpx.ConnectError("offline")
    )

    assert main(["--json", "--profile", "main", "profile", "probe"]) == 5
    payload = json.loads(capsys.readouterr().out)

    assert payload["command"] == "profile.probe"
    assert payload["error"]["type"] == "transport_error"
