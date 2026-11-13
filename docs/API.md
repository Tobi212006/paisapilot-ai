# API reference

Base URL: `http://127.0.0.1:8000`; interactive schema: `/docs`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Service health |
| GET | `/api/dashboard` | Spending totals and category breakdown |
| GET | `/api/transactions` | List local transactions |
| POST | `/api/transactions` | Add transaction |
| POST | `/api/safety/check` | Heuristic safety screening |
| POST | `/api/market/indicators` | Historical SMA and RSI |
| POST | `/api/business/gst-estimate` | Illustrative GST estimate |
| GET | `/api/invoices` | List invoice drafts |
| POST | `/api/invoices` | Create invoice draft |
| GET | `/api/goals` | List savings goals |
| POST | `/api/goals` | Create savings goal |

Example transaction body:
```json
{"description":"Groceries","amount":850,"category":"Food","occurred_on":"2026-11-13"}
```

Safety screening never establishes that a payment is fraudulent. Its response returns a risk band, numeric heuristic score, triggered rules and disclaimer.
