# Four-minute recording plan

Target 3:50–4:00, always **under five minutes**. This is a script, not a recorded or uploaded video. Use synthetic records and the sample workspace. Do not expose Connections exports, account details, developer tools, provider settings, notifications or keys.

| Time | Exact navigation and action | Narration |
| --- | --- | --- |
| 00:00–00:30 | Landing → Open workspace → Overview | “Hi, I’m Amit, presenting PaisaPilot AI for Arthaton 2026. Everyday financial records can be difficult to understand. PaisaPilot helps people in India review spending, plan budgets and learn payment safety. This demonstration uses synthetic data. It does not connect to a bank, move money or place trades.” |
| 00:30–01:10 | Overview → select the demonstration month → Inspect monthly evidence | “The dashboard shows recorded spending and cash flow. Expenses, income and refunds are kept separate, while transfers are excluded from spending. Here I can inspect the transactions behind the result. These totals describe entered records, not a verified bank balance. Financial arithmetic is deterministic and does not depend on an AI response.” |
| 01:10–01:55 | Transactions → Try sample month → Preview and review → inspect fields → confirm; Budget → Food → limit ₹1,000 → Save | “Imports are reviewed before saving. I can correct dates, amounts and categories, and check possible duplicates. Nothing is saved at the preview stage. After confirmation, the import can be undone and restored. I then set a category budget. The warning compares that limit with recorded spending rather than inventing a prediction.” |
| 01:55–02:40 | UPI Safety → enter `Please share your OTP to claim an urgent refund link` → run check | “The safety lab explains which language rules were triggered. This example requests a credential and combines urgency with a refund link. The score is an educational signal, not a probability that fraud occurred. The tool cannot verify a recipient. No warning does not establish safety. Never enter a real PIN, OTP, payment identifier or account detail.” |
| 02:40–03:20 | Learn → Building a budget → Explain this topic; if unavailable, show the actual error and Credit Coach | “Pip uses Gemini for a plain-language explanation of a selected educational topic. This request does not send transactions or account details. The source is shown, and cached replies in the repaired version are labelled. AI wording may be wrong and never changes the ledger. If the provider is unavailable, the app reports that honestly while the calculated tools remain available.” |
| 03:20–04:00 | Credit Coach → optionally Goals → GitHub README architecture table | “The hosted app uses React, TypeScript, a Cloudflare Worker and D1. The repository also includes a separate local FastAPI and SQLite runtime. Sample browser workspaces and signed-in private records use different owners. API validation, ownership checks and financial calculations have automated tests. Private sign-in and recovery still need acceptance checks. PaisaPilot’s goal is clarity and education, with visible evidence behind the numbers. Thank you.” |

## Recording checklist

- Rehearse once with the **deployed** app. Changes in a repair branch are not automatically live.
- Check Learn before recording. A successful Gemini-origin reply was observed on 22 November, but availability and cache freshness can change. Do not say every response is freshly generated.
- Prepare one expense/refund CSV for the current month; choose unique descriptions to avoid duplicates from rehearsals. Never use real financial data.
- Verify import confirmation, undo/restore, budget save and page reload before recording. Avoid repeated import confirmations while a request is pending.
- Set 1080p or readable equivalent, close private tabs and notifications, use a clear microphone, keep labels and amounts readable. Pause motion if helpful.
- Record the actual screen, not slides alone. Show the AI response or actual provider failure honestly. If no AI can be demonstrated, seek organizer guidance; an alternative calculator is not proof of AI functionality.
- Export a video shorter than 5:00. Upload to YouTube as **Public or Unlisted**, then verify playback without signing in. Add the verified URL to README before the deadline.
- Team lead submits once using registered team name/email, description, repository URL and video URL. Confirm authorship only if true. Save the form confirmation/edit link privately.
- Complete all pushes before **22 November 2026, 23:59 IST (18:29 UTC)**. Keep the repository public and video available through results. Do not push after cutoff.

## YouTube title

Arthaton 2026 – PaisaPilot AI | Explainable Budgeting & UPI Safety

## YouTube description

PaisaPilot AI is an India-focused educational finance prototype for Arthaton 2026. This working demonstration uses synthetic records to show reviewed imports, evidence-backed spending summaries, category budgets, payment-safety signals and Pip’s Gemini-powered explanations.

Live app: https://paisapilot-ai-amruta-launch.perfectturaco256.chatgpt.site/
Source: https://github.com/Tobi212006/paisapilot-ai

Hosted stack: React, TypeScript, Cloudflare Worker and D1. The repository separately includes a local React/Vite, FastAPI and SQLite runtime. Gemini provides optional educational explanations; arithmetic remains deterministic. Frankfurter supplies currency reference rates and MFapi supplies historical NAV data.

Educational prototype, not financial advice or a fraud verdict. No real-money trading, payments or bank access. Provider availability and private sign-in acceptance limitations are documented in the repository.

## Submission description (under the form’s 2,000-character limit)

PaisaPilot AI helps people in India understand their recorded spending and build better financial habits. Users preview and correct CSV or pasted transaction imports, inspect the evidence behind monthly income, expenses, refunds and cash flow, set category budgets and track savings goals. Its UPI Safety lab explains educational risk signals without claiming to confirm fraud. Pip uses Google Gemini to explain selected financial-literacy topics; private financial summaries require explicit consent and send only limited aggregate values. AI never changes financial records or executes transactions. Core arithmetic is deterministic and works without AI. The hosted application uses React, TypeScript, a Cloudflare Worker and D1, with a separate local FastAPI/SQLite runtime included in the public repository. Demonstrations use synthetic records. The project includes automated API, ownership-isolation, calculation and interface tests, plus documented limitations. It provides no real-money trading, bank access or payment execution.
