from __future__ import annotations

import threading
import time

from ._errors import SMEPayError
from ._http import post_json

_AUTH_PATH = "/api/external/auth"
# Fetch a new token when less than this many seconds of its lifetime are left.
_REFRESH_MARGIN_SECONDS = 60.0


class TokenManager:
    """Logs in with client_id/client_secret and caches the access token.

    The lock is held during login, so concurrent threads share a single login.
    """

    def __init__(self, base_url: str, client_id: str, client_secret: str) -> None:
        self._base_url = base_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._lock = threading.Lock()
        self._token: str | None = None
        self._expires_at = 0.0

    def __repr__(self) -> str:
        return "TokenManager()"

    def get_token(self) -> str:
        """Return the cached token, or log in if there is none or it is about to expire."""
        with self._lock:
            if self._token and time.monotonic() < self._expires_at - _REFRESH_MARGIN_SECONDS:
                return self._token

            # Measured before the call so network time counts against the token's lifetime.
            started_at = time.monotonic()
            reply = post_json(
                self._base_url,
                _AUTH_PATH,
                {"client_id": self._client_id, "client_secret": self._client_secret},
            )
            token = reply.get("access_token")
            expires_in = reply.get("expires_in")
            if not isinstance(token, str) or not token or not isinstance(expires_in, (int, float)) or expires_in <= 0:
                raise SMEPayError(
                    "invalid_response",
                    "SMEPay auth reply did not contain an access token",
                    status_code=200,
                    raw=reply,
                )

            self._token = token
            self._expires_at = started_at + float(expires_in)
            return token

    def invalidate(self, token: str) -> None:
        """Drop the cached token if it is the one the server just rejected."""
        with self._lock:
            if self._token == token:
                self._token = None
                self._expires_at = 0.0
