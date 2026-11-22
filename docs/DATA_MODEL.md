# Data model

The two databases are independent. D1 and local SQLite do not synchronize.

| Purpose | Hosted D1 | Local SQLite |
| --- | --- | --- |
| Reviewed ledger, amounts in paise, direction, import/archival markers | `pp_transactions` | `transactions` |
| Savings targets and tracked balances | `pp_goals` | `goals` |
| Contribution/withdrawal history | `pp_movements` | `goal_movements` |
| Category limit by owner/month | `pp_budgets` | `budgets` |
| Reversible import/idempotency history | `pp_batches` | `import_batches` |
| Illustrative invoice drafts | `pp_invoices` | `invoices` |
| Runtime metadata, cache, rate limits | `pp_state`, `pp_limits` | `app_meta`; process-local request/provider limits |

Financial records include an owner (`owner` hosted, `owner_id` local). The server selects the owner; clients do not choose a database owner in request payloads. Hosted sample owners use a random cookie and differ from managed signed-in identities. Local `demo` records are shared among visitors to that explicit local demo server; configured private sessions use server-verified Supabase identities.

Expenses and refunds are separate positive values with a direction; refunds subtract from spending in their recorded month. Transfers are excluded from income and spending. Goal movements track a balance without moving bank funds. Inspect `hosted/drizzle/*.sql` and `backend/app/database.py` for authoritative constraints and migrations. Export/deletion paths are owner-scoped; backup recovery has not been rehearsed in this audit.
