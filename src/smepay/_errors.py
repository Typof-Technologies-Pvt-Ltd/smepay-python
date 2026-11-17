from __future__ import annotations

from typing import Any

# Keys that must never appear in an error, even if an API reply echoes them.
_SENSITIVE_KEYS = {"access_token", "client_secret", "authorization"}


class SMEPayError(Exception):
    """Raised for every failed SDK call.

    API errors: ``code`` is the API's ``error`` field (e.g. ``"duplicate_order_id"``),
    ``status_code`` the HTTP status and ``raw`` the API reply.
    SDK-side errors use the codes ``"invalid_config"``, ``"network_error"``, ``"timeout"``
    and ``"invalid_response"``; ``status_code`` is ``None`` when no reply was received.
    """

    def __init__(self, code: str, message: str, status_code: int | None = None, raw: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.raw = _redact(raw)

    def __str__(self) -> str:
        if self.status_code is not None:
            return f"{self.code} (HTTP {self.status_code}): {self.message}"
        return f"{self.code}: {self.message}"

    def __repr__(self) -> str:
        return f"SMEPayError(code={self.code!r}, status_code={self.status_code!r}, message={self.message!r})"


def _redact(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    items: dict[Any, Any] = value  # pyright: ignore[reportUnknownVariableType]
    return {k: "[redacted]" if str(k).lower() in _SENSITIVE_KEYS else v for k, v in items.items()}
