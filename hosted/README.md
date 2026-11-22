# PaisaPilot hosted launch

This source preserves the original PaisaPilot React design and adds a standalone hosted Worker API with D1 persistence and platform-managed ChatGPT sign-in. The original FastAPI/Supabase local application is retained in the repository root backend/, frontend/ and scripts/ directories.

- `npm run test:server`: hosted API integration tests with SQLite-backed D1 contract adapter.
- `npm run test:coverage`: React component and system tests.
- `npm run build`: type-check, build React assets, embed them in the Worker, and package schema migrations.
- `npm run db:generate`: generate append-only schema migrations before future schema changes.

Runtime secrets are configured in Sites, never in source: GEMINI_API_KEY and GEMINI_MODEL. Pip general learning sends only a curated topic. Financial-summary AI requires private sign-in and explicit data-sharing consent. A Gemini-origin reply was observed in the hosted Learn screen on 22 November; cache freshness and deployment of the repaired branch remain unverified. See ../docs/STATUS.md and ../docs/AUDIT_2026-11-22.md.

Sample workspaces use a random HttpOnly cookie and contain synthetic records, separate from native signed-in user records. Imported messages are locally parsed; no full SMS text is stored or sent to AI. Use export before deleting data. Limits apply to demo records and AI calls.

Upstox remains unavailable without its authorized token; no real-money trading or automatic bank synchronization is implemented. D1 is managed persistent storage. The operator must still verify platform backup/recovery policies before relying on this service for important financial records.

The repaired hosted default model is `gemini-3.5-flash-lite`, overridable by server-side `GEMINI_MODEL`; runtime override was not read in this audit. Its provider request uses at most two attempts within 45 seconds. Quota/configuration failures are final, malformed/truncated answers fail safely, and the repaired UI labels cached replies. No production deployment or credential replacement was performed.
