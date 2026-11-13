# PaisaPilot AI
**Your Money. Your Move.** — *Spend Smarter. Spot Scams. Grow Wiser.*

An India-first financial literacy and planning prototype for students, young professionals, households and small businesses.

## Features
- **Smart Budgeting:** local transaction records, category summaries and demo spending insights.
- **UPI Safety Lab:** explainable keyword/amount risk signals. Educational heuristic only; not bank-grade fraud detection.
- **Finance Assistant:** financial-literacy guidance; not a personalised investment adviser.
- **Market Lab:** historical CSV price indicators (SMA and RSI); no live feed or trading.
- **Business Desk:** illustrative GST estimator and invoice drafts; verify tax treatment independently.
- **Goals & Reports:** local savings goals and dashboard summaries.

## Stack
React, TypeScript, Vite, Tailwind CSS, Framer Motion, Recharts, FastAPI, Pydantic, SQLite, Pytest.

## Run locally
### Backend (Python 3.11+)
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API: http://127.0.0.1:8000 · Swagger: http://127.0.0.1:8000/docs

### Frontend (Node.js 20+)
```bash
cd frontend
npm install
npm run dev
```
Vite: http://localhost:5173

Optional: copy `backend/.env.example` and `frontend/.env.example` to local env files. Never commit secrets or real financial data.

## Design system
- Deep Teal `#063D3B` — 60% primary
- Soft Peach `#F6B99F` — 30% secondary
- Electric Violet `#7B2DFF` — 10% accent

## Documentation
- [Architecture](docs/ARCHITECTURE.md)
- [API reference](docs/API.md)
- [Data model](docs/DATA_MODEL.md)
- [Security and privacy](docs/SECURITY.md)
- [Testing and QA](docs/TESTING.md)
- [Roadmap](docs/ROADMAP.md)
- [Known limitations / red flags](docs/RED_FLAGS.md)
- [Contribution guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Implementation status
| Capability | Status |
|---|---|
| FastAPI + SQLite foundation | Implemented |
| Transactions and dashboard totals | Implemented |
| Explainable UPI risk heuristics | Implemented; not ML |
| Rule-based financial education assistant | Planned |
| Historical SMA/RSI calculations | Implemented |
| Illustrative GST estimate + invoice drafts | Implemented |
| Savings goals | Implemented |
| Authentication / user data isolation | Not implemented |
| Bank, UPI, broker integrations | Not implemented |
| Live market data / trading | Not implemented |
| Production security audit | Not completed |

## Safety and disclaimer
This is an educational prototype, not a bank, financial adviser, broker, tax practitioner or fraud-reporting authority. No bank or UPI credentials, PINs, OTPs or card details should ever be entered. Outputs may be incomplete or incorrect; independently verify important decisions. Do not use with real personal financial records until authentication, access controls, privacy safeguards and security review are implemented.
