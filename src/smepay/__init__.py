"""Official Python SDK for the SMEPay External API.

Wraps the three payment calls (create, initiate, get status) and handles
authentication, token reuse and errors for you. Use it only on your server.
"""

from ._client import Environment, SMEPay
from ._errors import SMEPayError
from ._payment import PaymentResource
from ._types import (
    CreateResponse,
    CustomerDetails,
    GetStatusResponse,
    InitiateResponse,
    PaymentStatus,
)
from ._version import __version__

__all__ = [
    "CreateResponse",
    "CustomerDetails",
    "Environment",
    "GetStatusResponse",
    "InitiateResponse",
    "PaymentResource",
    "PaymentStatus",
    "SMEPay",
    "SMEPayError",
    "__version__",
]
