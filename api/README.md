# Meridian mock API — Northlight Electronics systems

Plays the retailer's real systems (CRM, catalog, order/returns, receipts). **Operational data and
actions live here; policy lives in the Knowledge Store** — the AI reasons from the store and acts on
this API. Every executed action returns a real generated reference (`RMA-…`, `CR-…`, `ORD-…`); the
LLM never invents one, and a missing result renders as a visible ERROR, never fake data.

Live base: `https://aicoe.3ddesignview.com/demo/cognigy_copilot/mock_api_meridian/meridian_api.php`
Deploy: `python tools/deploy_api.py` (FTP creds file outside the repo — see the script header).

## Convention

`GET or POST meridian_api.php?action=<name>` — query params, form fields, and a raw JSON body are
merged (JSON wins). CORS open so the sandboxed tile iframe can call it. `?action=ping` lists actions.

## Actions

| Action | Params | Returns |
|---|---|---|
| `get_customer` | `customer_id`, `name` (name-first: a name spoken in chat beats a stale id) | `{customer}` — Maya Torres `cust_101` (Summit), Leo Martinez `cust_102` (Member contrast) |
| `get_products` | — | `{products:[Aero 14, Titan 16]}` — the catalog the comparison cards rank |
| `execute_batch` | `customerId`, `actions:[{action, params}]` (≤6; JSON body or url-encoded string) | `{executed:[{action, ref, ok, detail}]}` — **the deterministic Approve path: one HTTP call runs the whole approved plan** |
| `process_return_exception` | `orderRef, item, amount, clause, reason` | `rmaRef`, refund to immediate store credit |
| `apply_credit` | `amount, unit, reason` | `creditRef` |
| `place_order` | `sku, creditApplied, shipMethod` | `orderRef`, computed `total`, `shipDate` (3 PM same-day cutoff per MER-POL-04 §2.1) |
| `send_receipt` | `name, detail ('title — REF\|title — REF'), total, orderRef` | `docRef` + **short `receiptUrl`** (page built by `meridian_xapp.php`) |
| `escalate_case` | `summary, queue` | `handoffId` |

## meridian_xapp.php

Customer-facing receipt page, flat-file link shortener (`?shorten=1` / `?s=<id>`), and a same-origin
QR proxy (`?qr=<url>`) so CSP/attachment validators never see a third-party image host.

## On SMS (honesty note)

The Meridian Cognigy project has no SMS provider connection yet, so `send_receipt` does **not** claim
an SMS was sent — it returns a short receipt link the agent delivers in the live chat (genuinely
delivered, genuinely real). To add real SMS later: create a Textel connection in the project and add a
`sendTextelMms` node after the receipt action (the Skyway build has the reference pattern).
