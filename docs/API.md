# API reference

The hosted application uses its same-origin `/api` Worker. The local launcher's integrated demo is at `http://127.0.0.1:8001`; standalone API configuration is described in [RUNNING](RUNNING.md). FastAPI exposes `/docs` only outside production. The Worker does not expose FastAPI's schema.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health`, `/ready` | Service/storage readiness (runtime-specific health body) |
| GET | `/api/connections`, `/api/planning/provider` | Integration configuration, not provider health guarantees |
| GET | `/api/dashboard` | Current monthly summary |
| GET / POST | `/api/transactions` | Owner-scoped list / create |
| GET | `/api/planning/month?month=YYYY-MM` | Income, refunds, spending, budgets, comparisons and evidence |
| POST | `/api/planning/transactions/{id}` | Correct owned ledger entry |
| POST | `/api/review/preview` | Parse/map CSV or pasted text without saving |
| POST | `/api/review/commit` | Confirm reviewed rows with UUID idempotency key |
| GET | `/api/review/batches` | Import history |
| POST | `/api/review/batches/{uuid}` | Undo/restore an owned import |
| POST | `/api/planning/budgets` | Save category/month limit; zero removes it |
| GET / POST | `/api/goals` | List / create owned tracking goals |
| GET / POST | `/api/planning/goals/{id}/movements` | Contribution history / bounded tracking update |
| POST | `/api/assistant/explain` | Curated Gemini educational topic |
| POST | `/api/planning/explain` | Consented aggregate explanation; disabled in sample mode |
| POST | `/api/safety/check` | Educational language/amount signals |
| GET | `/api/currency?base=USD&quote=INR` | Dated reference conversion rate |
| GET | `/api/funds/search?q=...`, `/api/funds/{code}` | Historical public NAV explorer |
| GET | `/api/stocks/quote?instrument=...` | Optional local read-only adapter; unavailable hosted |
| POST | `/api/market/indicators` | Historical SMA/approximate RSI |
| POST | `/api/business/gst-estimate` | Illustrative GST arithmetic |
| GET / POST | `/api/invoices` | Owned illustrative drafts |
| GET | `/api/records/export` | Export selected workspace |
| POST | `/api/records/clear` | Destructive deletion with exact confirmation text |

Local requests use Supabase Bearer sessions when configured. Hosted private identity comes from the trusted hosting gateway; sample ownership comes from an HttpOnly cookie. Clients must never forge native identity headers. Writes use JSON; hosted writes reject a foreign Origin. API responses use no-store and safe errors with request IDs. 422 denotes invalid input, 429 quota/rate limits, 503 unavailable/configuration, 502 upstream failure and hosted 504 exhausted provider timeouts. Some details differ between runtimes; the UI adapter and contract tests are authoritative.

```json
{"description":"Synthetic groceries","amount":"850.00","category":"Food","occurred_on":"2026-11-22","direction":"expense"}
```

Never use real credentials or financial records to test these examples. UPI scores do not establish fraud, and provider configuration does not prove a successful live response.
