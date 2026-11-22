# Testing and QA

Use Python 3.12 and Node.js 24. Run from the repository root in a disposable checkout. Automated fixtures use synthetic data and clear provider credentials; do not point tests at a private database.

```bash
python -m venv backend/.venv
backend/.venv/bin/python -m pip install --upgrade pip setuptools
backend/.venv/bin/python -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
backend/.venv/bin/python -m pytest backend --cov=backend/app --cov-report=term --cov-fail-under=90
backend/.venv/bin/pip-audit
npm ci --prefix frontend
npm run test:coverage --prefix frontend
npm run build --prefix frontend
npm audit --prefix frontend --audit-level=moderate
npm ci --prefix hosted
npm test --prefix hosted
npm run test:server --prefix hosted
npm run build --prefix hosted
npm audit --prefix hosted --audit-level=moderate
```

On Windows, substitute `backend/.venv/Scripts/python.exe` / `pip-audit.exe` and `npm.cmd` as needed. This audit used an isolated environment under `/tmp`, not a committed virtual environment.

Worker tests use an in-memory SQLite-backed D1 adapter and synthetic identities. Provider retry/error tests use mocked HTTP responses. These do not prove the hosting gateway's identity-header behavior, real Google/Supabase acceptance or a backup restore. UI tests use jsdom; they are not a mobile-browser test suite. Builds perform TypeScript checks.

For actual executed results and remaining manual checks, read [the dated audit](AUDIT_2026-11-22.md). For recording, use [the demo plan](DEMO_VIDEO.md). Re-run affected tests after changing source, and verify production separately after an authorized deployment. Do not claim old tests cover a new deployed build.
