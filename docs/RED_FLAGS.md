# Known limitations and red flags

- The prior exposed provider credential is **not confirmed revoked**. Follow [SECURITY](SECURITY.md); a clean targeted repository scan does not settle an earlier exposure.
- The hosted AI reply was observed on 22 November, but cache freshness was not visible in the old UI and availability can change. Repairs and cache labels are in PR #2, not automatically deployed.
- Hosted sample records are per browser. Local demo records are shared by that local server's visitors. Real private sign-in/recovery and hosting identity-header assurance remain acceptance work.
- Manual/CSV/pasted-text inputs are not bank or UPI synchronization. Missing imports produce incomplete insights.
- UPI language/amount rules are educational heuristics. They can miss scams and trigger false positives. Their score is not a calibrated fraud probability.
- Currency data is a dated reference rate and NAV data is historical. Neither is an executable quote, fund recommendation or return guarantee. Stock authorization is not connected to the hosted demo. No trade execution exists.
- GST calculations and invoice drafts are illustrative. No registration checks, filing, e-invoicing or e-way bill support is claimed.
- Backup restore, a current real mobile-device walkthrough, independent security review and full production hardening remain unverified. Local quotas are process-local; backend dependency ranges are not a transitive lockfile.
- The required YouTube demonstration and final hackathon receipt have not been verified. Do not label the project submission READY until mandatory rules in [the compliance matrix](HACKATHON_COMPLIANCE.md) are satisfied.

Never claim guaranteed fraud protection, bank sync, stock prediction, guaranteed returns, automated tax filing or certified production readiness. Demonstrate synthetic data only and keep secrets out of Git, exports, screenshots and logs.
