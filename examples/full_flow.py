"""Full flow: create → initiate → get_status.

Credentials come from environment variables (keep them in a .env file, never commit it):

    SMEPAY_CLIENT_ID=...
    SMEPAY_CLIENT_SECRET=...
    SMEPAY_ENVIRONMENT=test          # optional: "test" (default) or "live"
    SMEPAY_CALLBACK_URL=https://...  # optional: where the result webhook is sent

Run (with smepay installed, e.g. `pip install smepay` or `pip install -e .`):

    set -a; source .env; set +a
    python examples/full_flow.py
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime

import smepay


def main() -> int:
    environment = os.environ.get("SMEPAY_ENVIRONMENT", "test")
    try:
        client = smepay.SMEPay(
            client_id=os.environ.get("SMEPAY_CLIENT_ID", ""),
            client_secret=os.environ.get("SMEPAY_CLIENT_SECRET", ""),
            environment="live" if environment == "live" else "test",
        )
        print("Environment:", client.environment)

        # 1. Create the order. order_id is your own reference and must be unique.
        order = client.payment.create(
            amount="1.00",
            order_id=f"DEMO-{int(time.time() * 1000)}",
            callback_url=os.environ.get("SMEPAY_CALLBACK_URL", "https://example.com/smepay/callback"),
            customer_details={"name": "Demo Customer", "mobile": "9999999999"},
        )
        print("\n1. create")
        print("   order_id (SMEPay):", order["order_id"])
        print("   ref_id (yours):   ", order["ref_id"])
        print("   order_slug:       ", order["order_slug"])
        print("   payment_status:   ", order["payment_status"])
        print("   payment_url:      ", order["payment_url"])

        # 2. Start the payment: show the QR code or UPI app links to the customer.
        payment = client.payment.initiate(slug=order["order_slug"])
        print("\n2. initiate")
        print("   payment_status:   ", payment["payment_status"])
        print("   payment_link:     ", payment["payment_link"])
        print("   qr_code:           base64,", len(payment["qr_code"]), "chars")
        print("   intents:          ", ", ".join(sorted(payment["intents"])) or "(none)")
        print("   expires_at:       ", datetime.fromtimestamp(payment["expires_at"]).isoformat())

        # 3. Check the status by your reference (or by SMEPay's order_id).
        status = client.payment.get_status(external_reference_id=order["ref_id"])
        print("\n3. get_status")
        print("   payment_status:   ", status["payment_status"])
        print("   amount:           ", status["amount"])
        processed_at = status["processed_at"]
        print(
            "   processed_at:     ", datetime.fromtimestamp(processed_at).isoformat() if processed_at else "(not yet)"
        )
        print("   utr:              ", status.get("utr") or "(none yet)")
    except smepay.SMEPayError as err:
        print(f"\nSMEPayError [{err.code}] (HTTP {err.status_code}): {err.message}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
