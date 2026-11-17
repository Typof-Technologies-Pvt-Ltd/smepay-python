# smepay

Official Python SDK for the SMEPay External API. Accept UPI payments in three calls; login, tokens and errors are handled for you.

Python 3.8+ · zero dependencies · thread-safe · type hints included.

```bash
pip install smepay
```

## Usage

```python
import os
import smepay

client = smepay.SMEPay(
    client_id=os.environ["SMEPAY_CLIENT_ID"],  # from the SMEPay dashboard
    client_secret=os.environ["SMEPAY_CLIENT_SECRET"],
    environment="test",  # "test" (default) or "live"
)

# 1. Create an order
order = client.payment.create(
    amount="100.50",  # string, in rupees
    order_id="ORD-1001",  # your reference, unique per order
    callback_url="https://yoursite.com/smepay/callback",
    customer_details={"name": "Asha", "mobile": "9876543210"},  # email or mobile required
)

# 2. Start the payment: show payment["qr_code"] (base64 PNG) or payment["intents"] (UPI app links)
payment = client.payment.initiate(slug=order["order_slug"])

# 3. Check the status (or use order_id=order["order_id"])
status = client.payment.get_status(external_reference_id="ORD-1001")
print(status["payment_status"], status.get("utr"))  # "SUCCESS", "123456789012"
```

Create one client and reuse it. Arguments and reply keys match the API exactly; replies are plain dicts. Each request waits at most 60 seconds.

| Method | Returns |
|---|---|
| `payment.create` | `order_slug`, `order_id` (SMEPay's), `ref_id` (yours), `payment_url`, `payment_status` |
| `payment.initiate` | `payment_link`, `qr_code`, `intents`, `expires_at`, `payment_status` |
| `payment.get_status` | `payment_status`, `amount`, `created_at`, `processed_at` (`None` until processed), `utr` |

`initiate` can be called again if a payment failed or expired. Alternatively, skip `initiate` and redirect the customer to `payment_url` (the hosted page); use one or the other per order.

**Statuses:** `CREATED` → `INITIATED` / `PENDING` → `SUCCESS` or `FAILED` / `EXPIRED`; also `SETTLED`, `REFUNDED`, `REFUND_PENDING`. Test-mode businesses get `TEST_SUCCESS`, `TEST_FAILED`, `TEST_PENDING`.

## Errors

Every failure raises `smepay.SMEPayError` with `code`, `message`, `status_code` (`None` if no reply) and `raw` (API reply).

```python
try:
    client.payment.create(...)
except smepay.SMEPayError as e:
    if e.code == "duplicate_order_id":
        ...
```

| Code | Meaning |
|---|---|
| `invalid_config` | Missing `client_id` / `client_secret`, or bad `environment` |
| `invalid_client_id`, `invalid_credentials` | Wrong credentials |
| `environment_mismatch` | `environment` doesn't match your business's mode |
| `ip_not_whitelisted` | Live: your server IP isn't whitelisted |
| `insufficient_wallet_balance`, `wallet_validation_failed` | Live: wallet balance too low |
| `invalid_request`, `validation_error` | Missing or invalid field |
| `amount_below_minimum`, `amount_exceeds_maximum` | Amount outside your allowed range |
| `duplicate_order_id` | `order_id` already used |
| `transaction_not_found` | No such order for your business |
| `payment_already_processed` | `initiate` on an order already paid / in progress |
| `network_error`, `timeout`, `invalid_response` | Couldn't reach SMEPay / no reply in 60s / unreadable reply |

Calls are never retried automatically, so a failed `create` is never sent twice.

## Test vs live

| | `test` | `live` |
|---|---|---|
| Server | `staging.smepay.in` | `extranet.smepay.in` |
| Money / fees | None | Real; fees from your SMEPay wallet |
| Requirements | — | Server IP whitelisted, wallet ≥ ₹10 |

## Webhooks

When a payment finishes, SMEPay POSTs `ref_id`, `transaction_id`, `status`, `amount`, `created_at`, `processed_at` and `utr` to your `callback_url`. Confirm with `payment.get_status` before marking an order paid.

## Security

Use the SDK only on your server. Keep `client_secret` in an environment variable, never in code. The SDK never logs your secret or token, and `repr(client)` doesn't show them.

## Example

[`examples/full_flow.py`](https://github.com/mahi-qwe/smepay-python/blob/main/examples/full_flow.py): put `SMEPAY_CLIENT_ID` / `SMEPAY_CLIENT_SECRET` in `.env`, then `set -a; source .env; set +a; python examples/full_flow.py`.

## License

MIT
