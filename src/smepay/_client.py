from __future__ import annotations

from typing import Any, Literal, Mapping

from ._auth import _TokenManager
from ._errors import SMEPayError
from ._http import post_json

Environment = Literal["test", "live"]

_BASE_URLS = {
    "test": "https://staging.smepay.in",
    "live": "https://extranet.smepay.in",
}

# 401 codes meaning the token itself was rejected; a fresh login may fix these.
_TOKEN_ERROR_CODES = {"invalid_token", "invalid_external_token", "invalid_token_type"}


class _ApiClient:
    """Authenticated POSTs with client_id added to every body."""

    def __init__(self, base_url: str, client_id: str, client_secret: str) -> None:
        self._base_url = base_url
        self._client_id = client_id
        self._auth = _TokenManager(base_url, client_id, client_secret)

    def __repr__(self) -> str:
        return "_ApiClient()"

    def post(self, path: str, params: Mapping[str, Any]) -> dict[str, Any]:
        body = {**params, "client_id": self._client_id}
        token = self._auth.get_token()
        try:
            return post_json(self._base_url, path, body, token=token)
        except SMEPayError as err:
            if err.status_code != 401 or err.code not in _TOKEN_ERROR_CODES:
                raise
        # Token rejected (e.g. server session lost): log in again once and repeat the call once.
        self._auth.invalidate(token)
        return post_json(self._base_url, path, body, token=self._auth.get_token())


class SMEPay:
    """SMEPay External API client. Thread-safe; create one and reuse it.

    >>> client = SMEPay(client_id="...", client_secret="...", environment="test")

    ``environment`` is ``"test"`` (default, staging.smepay.in) or ``"live"`` (extranet.smepay.in)
    and must match your business's mode on SMEPay. Bad config raises SMEPayError ``invalid_config``.
    """

    def __init__(self, *, client_id: str, client_secret: str, environment: Environment = "test") -> None:
        if not isinstance(client_id, str) or not client_id.strip():
            raise SMEPayError("invalid_config", "client_id is required")
        if not isinstance(client_secret, str) or not client_secret.strip():
            raise SMEPayError("invalid_config", "client_secret is required")
        if environment not in _BASE_URLS:
            raise SMEPayError("invalid_config", f'environment must be "test" or "live", got {environment!r}')

        self._environment: Environment = environment
        self._api = _ApiClient(_BASE_URLS[environment], client_id.strip(), client_secret.strip())

    @property
    def environment(self) -> Environment:
        """The SMEPay environment this client uses: "test" or "live"."""
        return self._environment

    def __repr__(self) -> str:
        return f"SMEPay(environment={self._environment!r})"
