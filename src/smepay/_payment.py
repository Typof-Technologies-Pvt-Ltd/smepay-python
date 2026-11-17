from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from ._types import CreateResponse, CustomerDetails, GetStatusResponse, InitiateResponse

if TYPE_CHECKING:
    from ._client import ApiClient


class PaymentResource:
    """Payment calls: create → initiate → get_status."""

    def __init__(self, api: ApiClient) -> None:
        self._api = api

    def __repr__(self) -> str:
        return "PaymentResource()"

    def create(
        self,
        *,
        amount: str,
        order_id: str,
        callback_url: str,
        customer_details: CustomerDetails,
    ) -> CreateResponse:
        """Create a payment order. Next step: ``initiate(slug=reply["order_slug"])``.

        :param amount: amount in rupees, as a string, e.g. ``"100.50"``
        :param order_id: your own reference; must be unique for your business
        :param callback_url: URL that receives the payment result webhook
        :param customer_details: ``{"name", "email", "mobile"}``; email or mobile required
        """
        body = {
            "amount": amount,
            "order_id": order_id,
            "callback_url": callback_url,
            "customer_details": dict(customer_details),
        }
        return cast(CreateResponse, self._api.post("/api/external/order/create", body))

    def initiate(self, *, slug: str) -> InitiateResponse:
        """Start the payment for an order; returns the UPI link, QR code and app intents.

        :param slug: ``order_slug`` from ``create``
        """
        return cast(InitiateResponse, self._api.post("/api/external/order/initiate", {"slug": slug}))

    def get_status(
        self,
        *,
        order_id: str | None = None,
        external_reference_id: str | None = None,
        callback_url: str | None = None,
    ) -> GetStatusResponse:
        """Fetch the current payment status of an order.

        Pass ``order_id`` (SMEPay's) or ``external_reference_id`` (yours); the latter is used first if both are given.
        ``callback_url`` is saved only if the order has none yet.
        """
        body: dict[str, Any] = {}
        if order_id is not None:
            body["order_id"] = order_id
        if external_reference_id is not None:
            body["external_reference_id"] = external_reference_id
        if callback_url is not None:
            body["callback_url"] = callback_url
        return cast(GetStatusResponse, self._api.post("/api/external/order/status", body))
