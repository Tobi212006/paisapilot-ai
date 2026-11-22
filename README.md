# PaisaPilot AI

**Understand your spending. See the evidence. Build better money habits.**

[Open the live demo](https://paisapilot-ai-amruta-launch.perfectturaco256.chatgpt.site) · [Judge walkthrough](docs/JUDGING.md) · [Architecture and API status](docs/STATUS.md) · [Local setup](docs/RUNNING.md)

PaisaPilot is an India-focused educational finance MVP for the **AI for Finance** hackathon theme. It combines reviewed transaction imports, transparent budgeting, savings goals and payment-safety education with Pip, an optional AI explainer. All demonstrations use synthetic records. No real-money trading is provided.

![PaisaPilot landing page](docs/screenshots/landing.jpg)

## What you can try

- Review CSV or pasted transaction/SMS text before importing; correct mappings and amounts, inspect duplicates, undo and restore an import.
- Compare monthly income, expenses, refunds and cash flow. Evidence panels expose the records, arithmetic and assumptions behind totals.
- Set category budgets and record savings-goal contributions with history.
- Explore explainable UPI risk signals, credit-card arithmetic, illustrative GST/invoice drafts, mutual-fund NAV history and currency reference rates.
- Navigate with a collapsible sidebar. Pip, Mint, Chip and Sentinel introduce relevant tools; motion can be paused and respects reduced-motion preferences.
- Export or delete workspace records. The hosted demo uses isolated browser workspaces; managed sign-in is implemented for private workspaces.

Pip adds plain-language explanations to deterministic calculations. AI does not calculate the financial ledger or execute payments. General explanations send a fixed topic only. Private financial summaries require consent and send six aggregate values, not transaction descriptions or account numbers.

![Original dashboard with synthetic records](docs/screenshots/dashboard.jpg)

## Two runtimes, clearly separated

| Source | Purpose | Backend / storage |
| --- | --- | --- |
| `hosted/` | Source snapshot of the permanent live website | Cloudflare Worker, D1 SQLite, platform-managed sign-in |
| `frontend/`, `backend/`, `scripts/` | Independently runnable local app | React/Vite, FastAPI, owner-scoped SQLite, optional Supabase sign-in |

The live website does **not** run FastAPI or use Supabase for its hosted database. This GitHub repository is the submission mirror; pushing here does not automatically redeploy the managed site. No private local records, account keys or database files are included.

## Run locally

Use Python 3.12 and Node.js 24. From the repository root on Windows:

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
npm.cmd --prefix frontend ci
python scripts/run_local.py --demo
```

Open **http://127.0.0.1:8001/**. Keep the terminal running. This isolated local sample mode needs no account keys; optional external AI is disabled by default. It differs from the hosted per-browser demo: local sample records are shared by visitors to that local server. See [full setup](docs/RUNNING.md) for private sign-in and backup commands.

To reproduce the hosted source checks (its backend requires the managed Worker/D1 environment):

```powershell
cd hosted
npm.cmd ci
npm.cmd run test
npm.cmd run test:server
npm.cmd run build
```

`npm run dev` in `hosted/` serves frontend assets only; use the live site for its hosted API or the FastAPI instructions above for a complete local app.

## Verification and honest limits

Current repair checks: **112 FastAPI tests, 62 local UI tests, 65 hosted UI tests and 17 hosted API contract tests passed**; both production builds passed. Hosted contract tests use a SQLite-backed D1 adapter, not a live Cloudflare environment. See [verification details](docs/STATUS.md).

Live browser checks covered dashboard loading, import preview/commit, undo/restore, saved budgets and currency conversion. A Gemini-origin reply was observed in the hosted Learn screen on 22 November; cache freshness and the repaired branch’s production behavior remain unverified. Private sign-in acceptance and backup recovery drills also remain pending. Upstox is not connected. There is no automatic bank/UPI sync, tax filing, full portfolio analysis or backtesting engine.

UPI screening is an educational heuristic, not confirmed fraud detection. Reference rates and NAVs are dated data, not executable quotes. GST and credit calculations are illustrations, not filing or lending advice. This MVP is not certified production financial infrastructure.

## Screenshots and attribution

Screenshots show synthetic demonstration data. Dashboard and mobile captures are from the local runtime sharing the hosted design; the credit screen is a hosted capture. They document actual screens rather than design mockups.

[Mobile layout](docs/screenshots/mobile.jpg) · [Hosted credit screen](docs/screenshots/hosted-credit.jpg)

Dark Veil is adapted from React Bits; its attribution and MIT license are retained in each frontend's `src/vendor/react-bits/`. Other dependencies retain their respective licenses. Mascots are local SVG components. See [design notes](docs/DESIGN.md).

## Arthaton 2026 submission preparation

[Compliance matrix](docs/HACKATHON_COMPLIANCE.md) · [Current audit and tests](docs/AUDIT_2026-11-22.md) · [Four-minute recording script](docs/DEMO_VIDEO.md)

The official form was rechecked on 22 November: submissions and code pushes close at **23:59 IST on 22 November 2026**. The YouTube demonstration must be public or unlisted and **under five minutes**, showing the working app and AI. No video URL or final submission receipt has been verified; this is not yet a completed submission. Keep the repository and video available until results.

Pip uses Google Gemini `generateContent`: the hosted source defaults to `gemini-3.5-flash-lite`; the separate local source defaults to `gemini-3.1-flash-lite`. `GEMINI_MODEL` can override the default server-side; production's configured override was not inspected. Both identifiers were present in Google's official model documentation at audit time; that does not establish account entitlement. Never set a provider key in a `VITE_*` variable. The hosted request has at most two attempts within a 45-second deadline; the local Gemini request has at most two within 25 seconds. Quota and configuration failures are not retried.

A Gemini-origin explanation was observed in the hosted Learn screen on 22 November; its cache freshness was not visible in the old UI. The repaired UI labels cache hits. Private sign-in/recovery and backup restore remain unverified, and the previously exposed credential must still be identified and revoked by its owner. No repair-branch change is claimed deployed.

Fresh live evidence: [persisted dashboard](docs/screenshots/audit-2026-11-22/live-overview.jpg), [budget warning](docs/screenshots/audit-2026-11-22/live-budget.jpg), and [Pip explanation](docs/screenshots/audit-2026-11-22/live-pip.jpg). These show the existing deployed version with synthetic data; the repaired branch is not yet deployed.
