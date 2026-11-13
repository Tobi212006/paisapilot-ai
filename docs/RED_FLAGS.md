# Known limitations and red flags

## High priority
- **No authentication or user isolation:** local demo records are shared. Do not deploy with personal data.
- **No bank/UPI connection:** data is synthetic or user-entered; never describe this as bank sync.
- **Heuristic safety screening:** keyword/amount rules can miss scams and produce false positives. It is not trained ML or a guarantee.
- **Assistant is not yet integrated:** the Learn page contains static financial-literacy guidance, not a connected AI model.
- **Historical market input only:** no live NSE data, investment recommendation or trading execution.
- **GST estimate is illustrative:** rates and treatment depend on transaction facts and current rules.
- **Invoice drafts are not automatically compliant tax invoices:** no GST registration checks, e-invoicing or e-way bill support.
- **No production security audit:** authentication, rate limiting, audit trail and deployment hardening are outstanding.

## Repository hygiene
Before publishing a release, scan current files and Git history for tokens, passwords, private keys, personal records, database files, uploads and logs. Keep secrets in local environment variables and rotate any credential accidentally committed.

## Claims to avoid
Do not claim 100% fraud protection, live bank sync, live stock prediction, guaranteed returns, automatic tax filing, or production readiness unless the capability is genuinely implemented and reviewed.
