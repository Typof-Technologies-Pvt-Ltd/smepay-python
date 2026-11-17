from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from typing import Any, Dict, Mapping, cast

from ._errors import SMEPayError
from ._version import __version__

# Fixed maximum per request; deliberately not configurable.
TIMEOUT_SECONDS = 60.0
# Longest slice of a non-JSON reply kept in SMEPayError.raw.
_RAW_TEXT_LIMIT = 500
# Cap on how much of a reply is read.
_MAX_REPLY_BYTES = 10 * 1024 * 1024


def post_json(
    base_url: str,
    path: str,
    body: Mapping[str, Any],
    token: str | None = None,
    timeout: float = TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """POST ``body`` as JSON and return the parsed reply. Raises SMEPayError on any failure."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"smepay-python/{__version__}",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        base_url + path,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(response.status)
            reply = response.read(_MAX_REPLY_BYTES)
    except urllib.error.HTTPError as err:  # non-2xx reply: still read its body
        status = err.code
        try:
            reply = err.read(_MAX_REPLY_BYTES)
        except (OSError, socket.timeout) as read_err:
            raise _transport_error(path, read_err, timeout) from read_err
        finally:
            err.close()
    except (urllib.error.URLError, OSError, socket.timeout) as err:
        raise _transport_error(path, err, timeout) from err

    text = reply.decode("utf-8", errors="replace")
    try:
        data = json.loads(text)
    except ValueError:
        raise SMEPayError(
            "invalid_response",
            f"SMEPay returned a non-JSON reply (HTTP {status}) for {path}",
            status_code=status,
            raw=text[:_RAW_TEXT_LIMIT],
        ) from None

    if status < 200 or status >= 300:
        raise _api_error(status, data)
    if not isinstance(data, dict):
        raise SMEPayError(
            "invalid_response",
            f"SMEPay reply for {path} was not a JSON object",
            status_code=status,
            raw=data,
        )
    return cast(Dict[str, Any], data)


def _api_error(status: int, data: Any) -> SMEPayError:
    """Build an SMEPayError from an API error reply: {error, message} or {error, errors}."""
    body = cast(Dict[str, Any], data) if isinstance(data, dict) else {}
    error = body.get("error")
    code = error if isinstance(error, str) and error else "api_error"

    message = f"SMEPay API error (HTTP {status})"
    if isinstance(body.get("message"), str) and body["message"]:
        message = body["message"]
    elif isinstance(body.get("errors"), str) and body["errors"]:
        message = body["errors"]
    elif body.get("errors") is not None:
        message = json.dumps(body["errors"])

    return SMEPayError(code, message, status_code=status, raw=data)


def _transport_error(path: str, err: BaseException, timeout: float) -> SMEPayError:
    """Map a failed send/read to a timeout or network_error SMEPayError."""
    reason = err.reason if isinstance(err, urllib.error.URLError) else err
    if isinstance(reason, (socket.timeout, TimeoutError)):
        return SMEPayError("timeout", f"Request to {path} timed out after {timeout:g}s")
    return SMEPayError("network_error", f"Could not reach SMEPay ({path}): {reason}")
