# Architecture

Two independent runtimes share the React design. They are not combined at deployment.

| Runtime | Source | Request path | Identity |
| --- | --- | --- | --- |
| Hosted website | `hosted/` | React → same-origin Cloudflare Worker → D1 | Managed platform identity for private records; random cookie for browser sample workspace |
| Local application | `frontend/`, `backend/`, `scripts/` | React/Vite → FastAPI → SQLite | Optional server-verified Supabase sessions; explicit local demo mode shares sample records |

The live version is deployed from a separate managed source repository. The GitHub repository is a submission mirror. A GitHub push does not deploy the website. See [STATUS](STATUS.md) and [the dated audit](AUDIT_2026-11-22.md) for exact source provenance and which changes are live.

## Hosted boundaries

`hosted/worker/index.mjs` serves API routes and embedded static assets. Queries bind values and include the selected owner. The gateway must inject trusted identity headers and prevent visitor spoofing. The random sample cookie is HttpOnly, Secure and SameSite. Writes require JSON and same-origin requests, and request/AI quotas apply. D1 migrations live in `hosted/drizzle/`; contract tests use an in-memory adapter, not production D1.

## Local boundaries

`backend/app/main.py` mounts domain routers, guardrails, CORS and readiness checks. `database.py` initializes/migrates SQLite, and `schemas.py` validates requests. `auth.py` verifies configured Supabase sessions server-side. Local sample mode is suitable for a loopback development server. The launcher builds a separate frontend; `frontend/src/api.ts` controls API access. See [RUNNING](RUNNING.md) for ports and environment configuration.

## Calculations and integrations

Reviewed imports, budgets, refunds, cash flow and goal movements use deterministic logic and integer paise. AI never writes the ledger. Gemini receives either a fixed educational topic or, after explicit private-workspace consent, six aggregate values. The local runtime optionally supports Groq aggregate explanations. Frankfurter supplies dated currency reference rates; MFapi supplies historical NAV data. The local Upstox adapter requires authorization and is read-only; the hosted stock endpoint is unavailable. No bank sync, real-money trading or payments are implemented.

Provider failures retain the calculated evidence. Explanations are bounded and may be wrong. Backups, recovery, real private sign-in and gateway identity assumptions need operator acceptance before real financial use.
