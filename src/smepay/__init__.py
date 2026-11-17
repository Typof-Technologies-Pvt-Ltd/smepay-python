"""Official Python SDK for the SMEPay External API.

Wraps the three payment calls (create, initiate, get status) and handles
authentication, token reuse and errors for you. Use it only on your server.
"""

from ._errors import SMEPayError
from ._version import __version__

__all__ = ["SMEPayError", "__version__"]
