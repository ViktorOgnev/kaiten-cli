"""Helpers for turning profile domains into Kaiten HTTP origins."""

from __future__ import annotations

from urllib.parse import urlparse

KAITEN_HOST_SUFFIX = ".kaiten.ru"


def _with_parse_scheme(value: str) -> str:
    return value if "://" in value else f"//{value}"


def _host_with_port(raw_value: str) -> str:
    parsed = urlparse(_with_parse_scheme(raw_value))
    host = (parsed.hostname or "").lower()
    if not host:
        return raw_value.strip().strip("/").lower()
    try:
        port = parsed.port
    except ValueError:
        port = None
    return f"{host}:{port}" if port is not None else host


def normalize_profile_domain(value: str) -> str:
    """Normalize saved/env domain values without losing custom host intent."""

    raw = str(value or "").strip()
    if not raw:
        return ""

    parsed = urlparse(_with_parse_scheme(raw))
    host = (parsed.hostname or "").lower()
    host_with_port = _host_with_port(raw)
    if host.endswith(KAITEN_HOST_SUFFIX):
        return host[: -len(KAITEN_HOST_SUFFIX)]

    scheme = parsed.scheme.lower()
    if scheme and scheme != "https":
        return f"{scheme}://{host_with_port}"
    return host_with_port


def _is_kaiten_tenant_name(value: str) -> bool:
    return "." not in value and ":" not in value and not value.startswith(("http://", "https://"))


def profile_origin(domain: str) -> str:
    normalized = normalize_profile_domain(domain)
    if normalized.startswith(("http://", "https://")):
        return normalized.rstrip("/")
    if _is_kaiten_tenant_name(normalized):
        return f"https://{normalized}.kaiten.ru"
    return f"https://{normalized}"


def profile_api_base_url(domain: str, *, api_version: str) -> str:
    return f"{profile_origin(domain)}/api/{api_version}"
