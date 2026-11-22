# Architecture, API status and verification

## Request flow

Hosted: React -> same-origin Worker API -> owner-scoped D1 records. General Pip topics -> Gemini; public FX -> Frankfurter; NAV history -> MFapi. Server secrets are not embedded in the frontend.

Local: React -> FastAPI -> owner-scoped SQLite. Optional Supabase verifies local sign-in; it is not the local transaction database. Never expose private local development servers through public tunnels.

## Connection status

| Integration | Implementation and evidence | Limit |
| --- | --- | --- |
| Hosted records / D1 | Persistent owner-scoped API; browser imports, reload persistence and budgets checked | Operator restore drill pending |
| Gemini / Pip | Server key configured; direct provider calls succeeded; final deployment includes timeout/caching repair | Gemini-origin answer observed in hosted Learn on 22 November; cache freshness unverified |
| Frankfurter | Hosted browser conversion verified | Dated reference rates; not trade quotes |
| MFapi | Provider requests verified locally, hosted adapter covered in contract tests | Full hosted fund journey pending |
| Managed hosted identity | Sign-in and workspace switching implemented; UI tests passed | Actual private sign-in acceptance/recovery pending |
| Local Supabase | Optional local JWT authentication adapter | Requires your own settings; not hosted identity |
| Upstox | Optional read-only adapter | Not connected; authorized token required |
| Bank / UPI sync | Manual/CSV/pasted-text import only | No direct bank connection |

## How conclusions are drawn

Money is stored/calculated in integer paise. Monthly views separate income, expenses, refunds and transfers. Transfers do not inflate income/spending; refunds reduce net spending. Review the selected month, entry list and evidence panel before interpreting a total. Missing transactions mean incomplete insights, not a bank balance.

Budget alerts compare recorded category spending with the saved budget. Goals total recorded movements. Safety alerts report matched risk signals and uncertainty; they cannot verify a recipient or prove a scam. Pip paraphrases curated educational topics or consented aggregates; its output may be wrong and does not alter underlying records.

## Recorded verification (16 November 2026)

- Local Python: 103 tests passed.
- Hosted React: 63 tests passed across nine files.
- Hosted Worker: 12 tests passed using a SQLite-backed D1 contract adapter, including owner separation and import behavior.
- Type checking and production builds passed. Hosted dependency audit reported zero known vulnerabilities at verification time.
- Live browser: landing/navigation, API-connected dashboard, import review/commit, undo/restore, budgets and currency conversion verified.
- Programmatic live probes encountered hosting bot protection; this is not evidence of an API failure or pass.
- A hosted Gemini-origin response was observed on 22 November. Private sign-in acceptance, full hosted fund journey and backup restore remain unverified. Automated tests do not establish production readiness or validate provider answers.

## Before real financial use

Rotate the previously exposed provider credential, confirm deployment secret storage and spending quotas, complete private sign-in and account recovery checks, rehearse a backup restore and perform an independent security/privacy review. Never commit real statements, secrets or exported private records. No real-money trading, payment initiation or investment execution is implemented.

## Source map

`hosted/worker/index.mjs`: hosted API and security boundaries. `hosted/db/` and `hosted/drizzle/`: schema and applied migration history. `hosted/tests/`: API contract tests. `hosted/src/test/`: UI tests. `backend/app/`: local FastAPI implementation. `backend/tests/`: local API tests. `scripts/run_local.py`: local launcher.

The hosted mirror comes from managed source commit `29c38a8f2bb61fea284732e6b9be4bc722249d01`. The live site is published independently; this repository is not an automatic deployment pipeline.

## 22 November repair audit

See [audit](AUDIT_2026-11-22.md), [compliance](HACKATHON_COMPLIANCE.md) and [recording plan](DEMO_VIDEO.md). Current branch verification supersedes historical test counts above. The live site remains managed source `29c38a8f2bb61fea284732e6b9be4bc722249d01`, version 3. Its application files match GitHub's original hosted mirror; README differs. Repair commits are not automatically deployed. PR #1's Python 3.12 change was reviewed separately and its GitHub CI succeeded; it has not been merged by this audit.
