# Testing and QA

Backend:
```bash
cd backend
pip install -r requirements.txt
pytest
``

Frontend:
```bash
cd frontend
npm install
npm run build
``

Manual integration checklist:
- [ ] API status changes to connected when FastAPI starts.
- [ ] Dashboard totals are loaded from API.
- [ ] New transaction persists and updates totals.
- [ ] Invalid transaction amounts are rejected server-side.
- [ ] Safety response lists triggered rules and its limitations.
- [ ] Market calculations are labelled historical.
- [ ] GST output is labelled illustrative.
- [ ] Goals and invoice drafts persist after refresh.
- [ ] Mobile navigation and layout remain usable.
