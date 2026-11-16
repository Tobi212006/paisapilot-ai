# Running PaisaPilot

Use Python 3.12 and Node 24. Run commands from the repository root.

## First setup

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
npm.cmd --prefix frontend ci
```

For private sign-in, copy backend/.env.example and frontend/.env.example to local env files and configure your own account settings. Preserve any settings you already have. Never put server API keys in frontend variables.

## Private workspace

```powershell
python scripts/run_local.py
```

Open http://127.0.0.1:5174/ and use Connections to sign in. Keep the terminal open. Supabase sessions are held in memory; reloading requires sign-in again. User records are stored in backend/paisa_pilot.db unless DATABASE_PATH is configured, not in Supabase Postgres.

## Isolated demonstration

```powershell
python scripts/run_local.py --demo
```

Open http://127.0.0.1:8001/. This builds a separate frontend and uses backend/demo.db. It never loads private account, Gemini, Groq or Upstox credentials. Imported demonstration data is shared by visitors, so use sample records only. Optional AI returns a clear unavailable message in this public-safe mode.

Use `--demo --port 8011` if the default demo port is occupied. Only expose the isolated demo with a temporary sharing tunnel; never tunnel the private workspace or the separate local AI-testing server. Temporary links require the computer and server processes to stay running.

## Verification

```powershell
backend/.venv/Scripts/python.exe -m pytest -c backend/pytest.ini backend/tests
npm.cmd --prefix frontend run test:coverage
npm.cmd --prefix frontend run build
```

For provider status, change into backend and run `.venv/Scripts/python.exe scripts/verify_connections.py`. The script prints statuses without keys or generated text. Provider/model availability and quotas can change; configured is not the same as verified.

## Backups

From backend, run `.venv/Scripts/python.exe scripts/backup_database.py paisa_pilot.db path/to/new-backup.db`. The backup refuses overwrites and checks integrity. Keep backups private. Database schema upgrades preserve legacy records in the demo owner; they do not assign old demo data to signed-in users.

## Optional Pip learning in the shared demo

Run `python scripts/run_local.py --demo --demo-ai` to enable curated general learning topics using the Gemini key from ignored backend/.env. The key stays server-side. Supabase/private records and stock credentials remain excluded; monthly financial-summary AI is blocked in this public mode. The shared demo has a global limit of 20 topic requests per hour plus individual request limits. Without --demo-ai, no provider key is loaded.
