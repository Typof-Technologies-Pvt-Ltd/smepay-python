"""Type hints for request and response data. All keys are exactly the API's.

Responses are plain dicts at runtime; these TypedDicts only give editors autocomplete.
"""

from __future__ import annotations

from typing import Dict, Literal, Optional, TypedDict

PaymentStatus = Literal[
    "CREATED",
    "INITIATED",
    "PENDING",
    "SUCCESS",
    "FAILED",
    "EXPIRED",
    "SETTLED",
    "REFUNDED",
    "REFUND_PENDING",
    # Test-mode businesses get these instead of SUCCESS / FAILED / PENDING.
    "TEST_SUCCESS",
    "TEST_FAILED",
    "TEST_PENDING",
]


class CustomerDetails(TypedDict, total=False):
    """Payer details; at least ``email`` or ``mobile`` is required."""

    name: str
    email: str
    mobile: str


class _CreateResponseBase(TypedDict):
    status: bool
    order_slug: str  # pass to payment.initiate(slug=...)
    order_id: str  # SMEPay's order ID
    amount: float
    payment_status: PaymentStatus
    payment_url: str  # hosted SMEPay payment page
    ref_id: str  # your order_id, echoed back
    customer_details: Dict[str, str]
    message: str


class CreateResponse(_CreateResponseBase, total=False):
    """Reply of payment.create."""

    callback_url: str


class InitiateResponse(TypedDict):
    """Reply of payment.initiate."""

    status: bool
    order_id: str  # SMEPay's order ID
    external_reference_id: str  # your order_id
    payment_link: str  # UPI payment link
    transaction_id: str
    qr_code: str  # base64-encoded PNG
    payment_status: PaymentStatus
    expires_at: int  # Unix seconds
    intents: Dict[str, str]  # UPI app key -> app payment link
    message: str


class _GetStatusResponseBase(TypedDict):
    status: bool
    external_reference_id: str  # your order_id
    order_id: str  # SMEPay's order ID
    payment_status: PaymentStatus
    amount: float
    created_at: int  # Unix seconds
    processed_at: Optional[int]  # Unix seconds; None until processed


class GetStatusResponse(_GetStatusResponseBase, total=False):
    """Reply of payment.get_status."""

    utr: str  # bank reference, when available
