"""Application error types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class CliError(Exception):
    """Base CLI error."""

    message: str
    exit_code: int
    error_type: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.error_type, "message": self.message}

    def __str__(self) -> str:
        return self.message


class ValidationError(CliError):
    def __init__(self, message: str):
        super().__init__(message=message, exit_code=2, error_type="validation_error")


class ConfigError(CliError):
    def __init__(self, message: str):
        super().__init__(message=message, exit_code=3, error_type="config_error")


class ApiError(CliError):
    def __init__(self, status_code: int, message: str, body: Any = None):
        super().__init__(message=message, exit_code=4, error_type="api_error")
        self.status_code = status_code
        self.body = body

    def to_dict(self) -> dict[str, Any]:
        payload = super().to_dict()
        payload["status_code"] = self.status_code
        payload["body"] = self.body
        return payload


class TransportError(CliError):
    def __init__(self, message: str):
        super().__init__(message=message, exit_code=5, error_type="transport_error")


class InternalError(CliError):
    def __init__(self, message: str):
        super().__init__(message=message, exit_code=70, error_type="internal_error")

