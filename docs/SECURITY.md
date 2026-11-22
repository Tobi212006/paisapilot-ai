# Security and privacy

## Implemented boundaries

- Hosted: platform-injected identity selects owner-scoped D1 records. The hosting gateway must strip visitor-supplied identity headers; direct public access to the Worker outside that gateway is unsupported. The sample workspace uses a random HttpOnly, Secure, SameSite cookie and is separate from private records.
- Local: FastAPI validates Supabase sessions server-side when configured; owner-scoped SQLite queries use bound parameters. Explicit unauthenticated demo mode is for loopback development and shares sample records among that server's visitors.
- API inputs, amounts and dates are validated; ledger calculations use integer paise. Import batches are atomic and reversible. Ownership tests cover records, imports and goals.
- Hosted writes require same-origin JSON; API methods are checked. CSP, framing protections, response request IDs, body-size limits and request/AI quotas are implemented. Local CORS is configured via CORS_ORIGINS. Local quotas are process-local, not distributed enforcement.
- Provider secrets remain server-side. Curated Pip topics exclude workspace records. Private aggregate explanations require consent; sample workspaces cannot send financial summaries.
- AI failure does not alter records. Hosted Gemini has at most two attempts inside 45 seconds; local Gemini has at most two inside 25 seconds. No retries for bad requests, credentials/models or quota errors. Hosted malformed/truncated/thought-only replies are rejected, and cache hits are labelled in the repaired UI.
- Workspace export and explicit deletion are implemented. Do not use destructive endpoints to test real records.

## Prior credential exposure: unresolved

Existing project documentation reports a previously exposed provider credential. This audit found no matching Google API key, GitHub token or private-key block in the fetched GitHub or managed-source history using the documented targeted patterns. This is **not proof of absence of every secret**, and does not demonstrate that the previously exposed key was revoked. The old credential was not available for safe validity testing. A successful current Pip reply does not establish which credential was used or whether any older credential remains valid.

The credential owner must:

1. Identify the exposed key in Google AI Studio / Google Cloud using its key resource and exposure context. Do not paste it into a chat, issue, screenshot or terminal command.
2. Review usage and quota/billing, then revoke the exposed key in the provider console. Record the key resource ID, revocation time and operator confirmation without the secret value.
3. Create a restricted replacement if needed, apply appropriate API/quota restrictions and store it as server-side `GEMINI_API_KEY` in Sites. Confirm a supported `GEMINI_MODEL`. Update ignored local environment settings separately if used.
4. Verify the old key is rejected and the replacement works through Learn, with a synthetic/general topic. Do not report resolution from a source-code deletion alone.
5. If another exposure location is found, remove it carefully; coordinate any history rewrite rather than force-pushing or invalidating the submission.

Credential changes and production deployment require the user's authorization. None were performed in this audit.

## Remaining acceptance work

Complete real private sign-in/account recovery and cross-account acceptance, gateway identity-header assurance, backup/restore drill, independent security/privacy review, broader secret/PII scanning, retention policy and distributed/local deployment safeguards before real financial use. Expired hosted rate-limit rows do not currently have a scheduled cleanup; deployment operators should monitor growth. Backend requirement ranges are not a full transitive lockfile.

Tests and dependency audits provide bounded evidence, not ASVS certification or a complete penetration test. This educational prototype is not certified production financial infrastructure. Use synthetic records; never enter bank passwords, PINs, OTPs, PANs or real payment identifiers in demonstrations.
