# PaisaPilot visual experience

The landing page combines the character-led composition of the supplied Mainframe reference with the generous typography, rounded feature surfaces, and clear calls to action of the supplied Halo reference. The content is adapted for financial literacy in India rather than stablecoin earnings or agency services.

## Identity

- Navy `#10182B`, ivory `#F5F6FA`, violet `#7657F6`.
- Custom pilot-arrow P mark, shared by the navigation, workspace, and favicon.
- Pip: original local SVG character, with a violet visor and rupee badge. CSS animates the character and floating details. Optional Gemini topic explanations are separate from the mascot and send no financial records.
- Supporting cast: Mint (savings jar), Chip (credit card), and Sentinel (shield), all local SVG artwork. Automatic selection follows Asia/Kolkata time: Pip 05:00–11:59, Mint 12:00–16:59, Chip 17:00–21:59, Sentinel 22:00–04:59. Budget/Goals prefer Mint, Credit Coach prefers Chip, and UPI Safety prefers Sentinel. Manual selection overrides the default until the view changes or Auto is selected.
- DM Sans, with Arial/system fallbacks when the optional Google Fonts stylesheet is unavailable.

## Experience

The landing page introduces the product, links feature cards directly to existing workspace screens, introduces Pip, explains the workflow, and answers common questions. All product launch buttons open the existing React workspace. The workspace logo and back button return to the landing page. The dashboard retains its FastAPI data connection and shares the new palette.

Mobile navigation exposes the same section links and workspace action. FAQ buttons expose expanded state and controlled answer regions. CSS provides visible keyboard focus and a reduced-motion alternative. Local vector artwork avoids dependencies on remote background video.

The illustrative landing spending card is labelled demo data. API-backed totals appear in the workspace. No bank integrations, yield promises, partner endorsements, or implemented conversational assistant are implied.

## Verification

- Frontend TypeScript and production build.
- Existing backend test suite.
- Browser: landing-to-workspace navigation, API-connected dashboard, UPI safety request and response, return home, FAQ interaction.
- Phone-width layout at 390 pixels: no horizontal document overflow; mobile navigation opens and closes.

The landing hero now uses a locally vendored React Bits Dark Veil shader in navy/violet, with the original license retained under `frontend/src/vendor/react-bits/`. Motion section reveals, card hover lighting, and character halos add depth. A persistent pause/resume preference and device reduced-motion support control continuous animation. The shader pauses when offscreen or the document is hidden and has a static gradient fallback if WebGL2 is unavailable. No curved 3D feature carousel is implemented.

The workspace navigation can be closed completely and reopened from Menu. Desktop preference is remembered. At phone widths it starts closed and opens as a modal drawer with focus containment, inert main content, Escape/backdrop dismissal, and automatic close after selecting a tool. Finance forms and charts retain steady, readable surfaces.

## Current completion
The original shared dashboard is preserved. New monthly evidence, budgets, transaction review and contributions extend the existing interface. Optional monthly AI shares only displayed aggregate totals after explicit consent, separately from general learning prompts. See COMPLETION.md for current verification and limitations.
