# Security and privacy

## Current baseline
- Pydantic validates API payloads.
- SQLite statements use bound parameters.
- CORS is configurable through `CORS_ORIGINS`.
- Local environment files and databases are ignored by Git.
- The demo does not require secrets or bank credentials.

## Required before public deployment
1. Add authentication, authorisation and per-user data isolation.
2. Enforce HTTPS, secure session handling, rate limits and audit logging.
3. Add migrations, backups, retention and deletion workflows.
4. Run dependency, secret, SAST and DAST scans.
5. Review consent, privacy notices, data minimisation and applicable Indian requirements with qualified counsel.
6. Use authorised sandbox/provider flows for any future financial integrations. Never collect bank passwords, UPI PINs or OTPs.
7. Complete a threat model and independent security review.

This project is not security-audited or production-ready.
