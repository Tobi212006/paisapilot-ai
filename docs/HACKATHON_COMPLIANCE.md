# Arthaton 2026 compliance matrix

## Publication update — 22 November 2026

The repairs are deployed as managed Site version 6, source `e100153629a8cc12e6bf2bc5f3cf7c8f01628aef`. The unavailable stock-quote form and stock connection listing are removed. Hosted sample records are labelled browser-isolated. Sample planning panels now offer Pip topic explanations instead of disabled aggregate-summary controls; sample totals remain blocked from external AI. Both UI suites (65 hosted / 62 local) and builds passed after this change. The earlier full run passed 112 backend and 17 hosted API contract tests.

Post-publication browser checks confirmed the corrected label, removed stock form, a Gemini-origin Learn reply, import arithmetic and reload persistence, and the new Pip topic controls in the evidence panel. A five-row synthetic import changed 7 entries to 12, spending ₹5,979 to ₹7,329, income to ₹30,000 and cash flow to ₹22,671; the ₹2,000 transfer was excluded. The embedded topic control was tested automatically; its presence, rather than a new reply from that exact control, was checked live. Private sign-in/recovery, real-device mobile acceptance, backup restore and prior credential revocation remain unverified. Video and submission are handled by the entrant and are not confirmed here.

The audit below records the earlier pre-publication state. Statements that repairs were not deployed describe that earlier state.


Checked 22 November 2026 against the [official submission form](https://docs.google.com/forms/d/e/1FAIpQLScnZP6-YLpjuIbnfUuGIYtpYrMeA8n7CNqslCC15zErQ6HnCw/viewform). Direct HTTPS retrieval succeeded; the search fetcher could not retrieve it. Both the rendered first-page text and embedded form schema were inspected. Rules below are paraphrased. Status is at this audit, not a promise of future compliance.

| Verified requirement | Evidence | Status | Required action / final verification |
| --- | --- | --- | --- |
| Public GitHub source repository | GitHub metadata: `Tobi212006/paisapilot-ai`, visibility public; unauthenticated clone succeeded | Pass | Keep public through results |
| Working code included | Separate hosted/local source, migrations, build scripts and passing automated checks | Pass | Repair branch must be reviewed; source checks do not prove all live journeys |
| README details purpose, run instructions, AI models and APIs | README, RUNNING, STATUS and audit additions | Pass on repair branch | Merge reviewed documentation before cutoff |
| YouTube demo public or unlisted, under five minutes, showing working app and AI | No submitted video URL was supplied or verified | Unverified | Record, upload and check anonymous playback; slides alone do not qualify |
| Include both repository and video links | Repository verified; video not verified | Unverified | Add real video URL to README and form; never use a placeholder |
| No real banking details, passwords, PAN, UPI IDs or API secrets in repository | Synthetic fixtures; targeted secret scan of 40 original GitHub commits/137 blobs and 3 managed-source commits/62 blobs found no Google-key, GitHub-token or private-key matches | Unverified overall | Pattern scan is not exhaustive. Prior exposed provider credential remains unresolved; owner must identify/revoke it and check other exposure locations. Code contains names of credential fields, not proof of actual credentials |
| No real trades | Inspected code contains educational calculations/read-only data; hosted stock execution not implemented | Pass for inspected scope | Do not add execution or use real-money transactions |
| Only pre-deadline commits; no pushes after 22 Nov 23:59 IST | Form cutoff reconfirmed; corresponds to 18:29 UTC | Unverified until freeze | Finish review/push/merge before cutoff, then freeze all pushes; local preparation after cutoff is not permission to push |
| Keep repository public and video available through results | Repository currently public; video unverified | Unverified future condition | Keep both available; form confirmation says results by 30 November |
| Team lead submits once for the team | Form instruction; no receipt inspected | Unverified | Team lead submits once using registered team name/email |
| Project description within 2,000 characters | Prepared description in DEMO_VIDEO.md | Pass for draft | Paste accurate description into form |
| Team confirms rule compliance and own work | Required confirmation in form | Unverified | Team must verify truth of authorship and all requirements before confirming |

LinkedIn sharing is encouraged by the form; it is not stated as mandatory. Four minutes is our recording target; the actual rule is **under five minutes**. The accessible form does not establish additional team-size, model-provider, judging-weight or licensing rules; none are invented here.

**Verdict: NOT READY for final submission.** A required video and submission receipt are unverified, and the prior credential revocation is not confirmed. The repair branch is tested, but is not the live deployment. See AUDIT_2026-11-22.md for security and verification boundaries.
