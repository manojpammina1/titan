# Cruise Agent Site Design Spec

Status: frozen
Owner: Candidate (Principal Engineer case study)
Audience: Titan-governed development agents
Last updated: 2026-08-09

This document is the UI and production-quality contract for the Agentic Cruise
Planning Assistant demo. Build only to this spec unless the development plan is
explicitly updated.

The experience is a cruise-planning workspace, not a marketing landing page.
The first screen must be the usable assistant experience.

## 1. Product Intent

Create a production-grade prototype that shows how a guest can plan a cruise
with an agentic assistant while commerce systems remain authoritative.

Primary promise:

"The assistant helps the guest make a confident cruise choice by turning
preferences into verified options, evidence-backed trade-offs, policy answers,
and a safe checkout handoff."

The design must make these boundaries visible:

- verified commerce data versus model narrative
- current evidence versus stale evidence
- anonymous planning versus authenticated commitment
- assistant guidance versus existing checkout authority
- model-assisted mode versus deterministic fallback mode

## 2. Design Principles

1. Dense but readable.
   - This is an operational e-commerce planning tool.
   - Avoid landing-page hero sections, decorative cards, and oversized copy.

2. Evidence-first.
   - Price, availability, policy, and comparison evidence must be visible near
     the decision it supports.

3. Deterministic before generative.
   - The UI may stream model narrative, but commerce-sensitive values render
     only after deterministic tool responses.

4. Accessible by design.
   - Canvas visuals must have an equivalent list representation.
   - Keyboard-only users must complete search, comparison, selection, and
     fallback.

5. Production-ready behavior.
   - Clear loading, stale, failure, retry, auth, and handoff states.
   - No hidden demo-only magic that would collapse in production.

## 3. Visual System

### 3.1 Tone

Quiet, premium, trust-oriented, and commerce-grade. The UI should feel like a
high-quality travel planning console, not a playful AI toy.

### 3.2 Color Tokens

```css
:root {
  --color-bg: #f6f8fb;
  --color-surface: #ffffff;
  --color-surface-subtle: #eef3f8;
  --color-border: #d8e0ea;
  --color-border-strong: #aeb9c7;
  --color-text: #172033;
  --color-text-muted: #5d6678;
  --color-accent: #005eb8;
  --color-accent-strong: #003f7d;
  --color-success: #15803d;
  --color-warning: #b45309;
  --color-danger: #b91c1c;
  --color-info: #0369a1;
  --color-focus: #f59e0b;
}
```

Rules:

- Use accent for primary actions, active selections, and verified evidence.
- Use warning for stale evidence, expiring holds, and partial verification.
- Use danger only for blocked actions and safety failures.
- Do not use color alone to communicate state.

### 3.3 Typography

Use system fonts.

```css
--font-sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
  "Segoe UI", sans-serif;

--text-app-title: 20px;
--text-page-heading: 18px;
--text-section-heading: 14px;
--text-body: 14px;
--text-meta: 12px;
--text-button: 14px;
```

Rules:

- Letter spacing must be `0`.
- Do not scale font size with viewport width.
- Buttons must not truncate labels at 320px width.

### 3.4 Spacing, Radius, and Elevation

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--radius-control: 6px;
--radius-card: 8px;
--shadow-surface: 0 1px 2px rgba(15, 23, 42, 0.08);
```

Rules:

- Cards use radius `8px` or less.
- Do not nest cards inside cards.
- Page sections are unframed layout regions, not decorative floating cards.

## 4. Page Shell

### 4.1 Desktop Layout

Minimum desktop target: `1280px`.

```text
 ---------------------------------------------------------------
| Top Bar                                                       |
| Royal Caribbean Cruise Planning Assistant   status/actions    |
 ---------------------------------------------------------------
| Left: Constraints | Center: Voyage Canvas       | Right: Evidence |
| width 280-320     | fluid min 560               | width 320-380   |
|                   |                             |                 |
| travelers         | current planning state      | verified price  |
| dates             | 3 journey options           | availability    |
| budget            | compare two                 | policy cites    |
| locked prefs      | selected voyage             | decision log    |
 ---------------------------------------------------------------
```

CSS grid:

```css
.app-shell {
  min-height: 100dvh;
  display: grid;
  grid-template-rows: 56px 1fr;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(280px, 320px) minmax(560px, 1fr) minmax(320px, 380px);
  gap: 16px;
  padding: 16px;
}
```

### 4.2 Tablet Layout

For `768px` to `1199px`:

- Top bar remains.
- Constraints become collapsible left drawer.
- Evidence rail becomes right drawer or bottom panel.
- Center canvas remains primary.

### 4.3 Mobile Layout

For `320px` to `767px`:

- Do not attempt a full three-pane canvas.
- Render decision-lens sequence:
  1. constraints
  2. options
  3. evidence
  4. compare
  5. commitment
- AccessibleVoyageList is the primary mobile representation.
- Mobile can be a responsive implementation or static mock for the interview,
  but desktop must be fully functional.

## 5. Required Screen States

| State | UI behavior |
|---|---|
| `anonymous_empty` | Prompt input, deterministic defaults, empty canvas with no fake results. |
| `understanding` | Streaming status, stop-generation control, no commerce values until tools respond. |
| `results_ready` | Three options, constraint chips, evidence cards with freshness. |
| `budget_changed` | Options recomputed, visible note that results were reverified. |
| `compare_active` | Two-option comparison with deterministic gain/loss deltas. |
| `policy_answer` | Policy answer with citations and published date. |
| `auth_required` | Modal blocks hold creation, explains why auth is required. |
| `hold_pending` | Confirmation step; no hold until explicit user confirmation. |
| `hold_created` | Hold timer, hold id, expiration, checkout handoff. |
| `model_failed` | GuidedVoyagePlanner active, criteria preserved. |
| `stale_price` | Price visually marked stale; hold requires revalidation. |
| `availability_changed` | Explain change; disable stale selected cabin; offer alternatives. |

## 6. Component Contracts

### 6.1 TopBar

Purpose:

- Identify product.
- Show model/fallback status.
- Provide stop-generation control.

Consumes:

- `sessionMode`
- `modelState`
- `traceId`

Actions:

- `onStopGeneration`
- `onToggleModelFailureDemo`

Accessibility:

- Status text is exposed to screen readers.
- Stop button has explicit accessible name.

Acceptance:

- User can see whether model mode or fallback mode is active.
- Stop generation is keyboard reachable.

### 6.2 ConstraintPanel

Purpose:

- Show current planning criteria and locked preferences.

Consumes:

- `CruiseCriteria`
- `locked[]`

Actions:

- `onUpdateCriteria`
- `onLockPreference`
- `onUnlockPreference`

Accessibility:

- Budget slider has label, min, max, current value, and keyboard support.
- Locked preferences are announced as toggles.

Acceptance:

- Budget change recomputes options deterministically.
- Locked cabin type cannot be changed by model action.

### 6.3 VoyageCanvas

Purpose:

- Show adaptive planning state, options, comparison, and commitment sequence.

Consumes:

- `VoyageExperience`

Actions:

- `onSelectSailing`
- `onCompare`
- `onFocusDecision`

Accessibility:

- Every visual object has a semantic equivalent in AccessibleVoyageList.
- Canvas does not trap focus.

Acceptance:

- Shows exactly three primary options in hero path.
- Does not render model-generated commerce values.
- No text overlap at `1280x720`, `1440x900`, and `1920x1080`.

### 6.4 JourneyPossibility

Purpose:

- Present a candidate sailing with summary and decision actions.

Consumes:

- `SailingOption`
- `VerifiedPriceEvidence`
- `AvailabilityEvidence`

Actions:

- `onSelect`
- `onCompareToggle`

Rules:

- Price block is hidden until verified price exists.
- Availability block is hidden until availability evidence exists.

Acceptance:

- `asOf` and `validUntil` are visible.
- Compare checkbox/button is keyboard reachable.
- Selected state is not color-only.

### 6.5 EvidenceRail

Purpose:

- Centralize evidence and decision history.

Consumes:

- `Evidence[]`
- `DecisionEvent[]`

Rules:

- Group evidence by selected or focused sailing.
- Mark stale evidence.
- Do not display uncited policy answers.

Acceptance:

- Every commerce-sensitive claim in canvas has matching evidence.
- Evidence cards remain readable at right-rail width `320px`.

### 6.6 VerifiedPriceEvidenceCard

Consumes:

- `sailingId`
- `cabinType`
- `totalUsd`
- `taxesAndFeesUsd`
- `asOf`
- `validUntil`
- `source`

Rules:

- Must show "verified at" and "valid until."
- Must never render model-generated prices.
- Must visually and textually distinguish stale evidence.

Acceptance:

- Price appears only after `getPricing()` response.
- Stale state appears after expiry.
- Screen reader can identify total price and validity window.

### 6.7 AvailabilityEvidenceCard

Rules:

- Show cabin type, available cabin count, freshness, and source.
- If available cabins reaches zero, disable hold action.

Acceptance:

- Hold cannot proceed on stale or unavailable cabin evidence.

### 6.8 PolicyEvidenceCard

Rules:

- Show policy title.
- Show publication date.
- Show short excerpt.
- Link citation to the answer.

Acceptance:

- Policy answer is not shown without at least one citation.
- Retrieved content instructions are never rendered as system instructions.

### 6.9 CompareTwoPanel

Rules:

- Compare exactly two sailings.
- Deltas come from comparison engine only.
- Use short, scannable trade-offs rather than a giant table.

Acceptance:

- Price delta, itinerary delta, cabin/ship highlights, and constraint match
  are computed values.
- Model may narrate but not compute deltas.

### 6.10 AuthBoundaryModal

Purpose:

- Explain why login is required before hold.

Rules:

- Trigger only when user attempts hold or save-like stateful action.
- Do not ask for auth during generic planning.

Acceptance:

- Hold API cannot be called without auth context.
- Modal is keyboard accessible and focus trapped correctly while open.

### 6.11 ConfirmHoldPanel

Rules:

- Show selected sailing, cabin type, price snapshot, expiration policy.
- Require explicit confirmation button.
- Disable if evidence is stale until revalidated.

Acceptance:

- Hold is created only after confirmation.
- Shows hold expiration countdown after success.

### 6.12 GuidedVoyagePlanner

Purpose:

- Deterministic fallback when model is unavailable.

Rules:

- Use same deterministic APIs as Voyage Canvas.
- Preserve latest confirmed criteria.
- Must not feel like an error page.

Acceptance:

- User can search, compare basic options, and select a voyage without model.

### 6.13 AccessibleVoyageList

Purpose:

- Semantic equivalent of the canvas.

Rules:

- Same data, same actions, same evidence links.
- Used for screen-reader equivalent and mobile/fallback display.

Acceptance:

- Keyboard-only user can complete search and select a sailing.

## 7. Performance and Core Web Vitals

### 7.1 Targets

Production-grade targets for local demo and deployed mock build:

| Metric | Target |
|---|---|
| LCP | <= 2.5s on simulated Fast 4G / mid-tier mobile |
| INP | <= 200ms |
| CLS | <= 0.05 |
| TTFB | <= 800ms for initial shell |
| First route JS | <= 180 KB gzip, excluding framework |
| Total initial CSS | <= 45 KB gzip |
| Hero path deterministic API p95 | <= 500ms local |
| Hold creation p95 local | <= 700ms |

### 7.2 LCP Strategy

LCP element should be stable application shell content, not a remote hero image.

Required:

- Server-render top shell and initial prompt/constraints area.
- Avoid large above-the-fold images.
- Avoid blocking web fonts; use system fonts.
- Use skeletons with fixed dimensions for canvas regions.
- Stream status after shell renders.
- Load heavy eval/debug widgets below the fold or behind toggles.

Forbidden:

- full-bleed marketing hero image as first screen
- autoplay video
- large client-only canvas before shell
- layout-shifting cards with unknown heights

### 7.3 JavaScript Strategy

Required:

- Keep first screen lightweight.
- Lazy-load:
  - trace/debug panel
  - eval summary panel
  - optional policy detail modal
  - non-critical icons
- Use route-level code splitting.
- Avoid large charting libraries in the app demo.
- Do not bundle seed data into the client.

### 7.4 API Performance

Required:

- Deterministic parser runs before model call.
- Search, pricing, availability can run in parallel after criteria is known.
- Compare deltas are computed server-side or in a shared deterministic package.
- Hold API revalidates price and availability in one server flow.
- Cache approved policy content in memory for local demo.

### 7.5 Rendering Stability

Required:

- Fixed grid columns on desktop.
- Stable min-heights for option cards and evidence cards.
- Reserve space for streaming status.
- Use fixed-size icons.
- Do not resize buttons when loading; swap label content inside stable width.

## 8. SEO and Discoverability

The assistant itself is an interactive app, but production-grade e-commerce
still needs indexable, shareable, and understandable metadata.

### 8.1 Page Metadata

Required for app shell:

```text
title: Royal Caribbean Cruise Planning Assistant
description: Plan and compare cruise options with verified pricing, availability, and policy guidance.
canonical: /cruise-planning-assistant
robots: noindex for demo, index for production after legal/content approval
openGraph title and description
```

Demo environment:

- Use `robots: noindex,nofollow`.
- Avoid implying this is an official public RCG product.

Production discussion:

- Public marketing/detail pages remain SEO-first.
- Assistant route supports discoverability and rich metadata.
- Cruise detail pages should stay crawlable independent of the assistant.

### 8.2 Structured Data

For production slides only, mention possible schema use:

- `TravelAgency`
- `TouristTrip`
- `Offer`
- `FAQPage` for approved policy FAQ content

Do not overbuild structured data in the POC. A metadata implementation is
enough for the demo.

### 8.3 Content Rendering Rules

- Policy answers must not replace canonical policy pages.
- Assistant answers cite approved content and link back to canonical pages in
  production.
- Dynamic personalized results should not be indexed.

## 9. Accessibility Requirements

Target: WCAG 2.2 AA.

### 9.1 Keyboard

Required:

- All controls reachable by keyboard.
- Logical focus order:
  1. top actions
  2. prompt/criteria
  3. canvas options
  4. evidence links
  5. commitment actions
- Escape closes modal/drawer.
- Arrow keys operate sliders and segmented controls where appropriate.

### 9.2 Focus

Required:

- Visible focus ring using `--color-focus`.
- Focus moves to first result summary when results render.
- Focus returns to triggering control when modal closes.
- Auth modal traps focus.

### 9.3 Screen Reader

Required:

- Streaming status uses `aria-live="polite"`.
- Hold success uses assertive announcement.
- Evidence cards have descriptive labels.
- Price validity window is announced.
- Compare result explains which two sailings are being compared.

### 9.4 Motion

Required:

- Respect `prefers-reduced-motion`.
- Animations are optional, short, and non-essential.
- No animated content that blocks task completion.

### 9.5 Contrast and Semantics

Required:

- 4.5:1 contrast for normal text.
- 3:1 contrast for large text and UI indicators.
- Real buttons for actions.
- Real form controls for inputs.
- No div-only interactive controls.

## 10. Resilience and Failure UX

### 10.1 Model Failure

Behavior:

- Show concise status: "AI guidance is temporarily unavailable. Guided search
  is still available."
- Preserve criteria.
- Switch to GuidedVoyagePlanner.
- Do not lose selected constraints.

### 10.2 Pricing Failure

Behavior:

- Do not show stale price as current.
- Show: "Live pricing is unavailable. Try again before holding a cabin."
- Disable hold until price is verified.

### 10.3 Availability Change

Behavior:

- Explain that availability changed.
- Mark previous selection unavailable.
- Offer next available alternative.
- Do not blame the model.

### 10.4 Policy Retrieval Failure

Behavior:

- Show: "I cannot verify this policy right now."
- Link to fallback support/contact placeholder in production discussion.
- Do not hallucinate policy.

## 11. Privacy and Data Display

Rules:

- Do not display full guest identity in demo.
- Use fictional guest name after demo login.
- Do not collect payment data.
- Do not expose trace IDs as user-facing primary content; put them in debug
  drawer or evidence metadata.
- Logs must not contain raw PII or payment data.

## 12. Analytics and Observability UX

Demo UI should expose a compact trace/evidence drawer, not a full analytics
dashboard.

Show:

- model provider: mock/gemini/none
- tool calls executed
- tool latency
- fallback used
- evidence count
- safety events

Do not show:

- raw prompts
- raw model response with hidden instructions
- secrets
- API keys

## 13. Production Benefit Callouts

These benefits should be visible in the UI or demo narration:

- Lower hallucination risk: commerce values come from tools.
- Higher conversion confidence: evidence and freshness shown at decision time.
- Lower AI cost: no model call on page load.
- Better resilience: deterministic fallback still completes planning.
- Better compliance: auth and explicit confirmation before hold.
- Better operations: trace per turn, tool timings, and fallback indicators.
- Better accessibility: canvas has equivalent list interface.
- Better SEO posture: canonical cruise/policy content remains indexable;
  assistant route uses proper metadata and avoids indexing personalized state.

## 14. Build Acceptance Gates

### 14.1 Functional Gates

- Hero path completes in under 3 minutes.
- Failure path works with `LLM_PROVIDER=mock` and forced model failure.
- Hold requires authenticated demo guest.
- Hold requires explicit confirmation.
- Checkout handoff appears only after hold success.

### 14.2 Evidence Gates

- No price appears without `VerifiedPriceEvidence`.
- No availability appears without `AvailabilityEvidence`.
- No policy answer appears without `PolicyEvidence`.
- Compare deltas come only from comparison engine.
- Stale evidence cannot create hold without revalidation.

### 14.3 Accessibility Gates

- Keyboard-only hero path passes.
- Keyboard-only fallback path passes.
- Auth modal focus trap passes.
- `aria-live` status is present.
- Axe has no serious or critical violations.
- Reduced-motion mode is respected.

### 14.4 Performance Gates

Run Lighthouse against local production build.

Minimum local targets:

- Performance: 90+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 90+
- LCP: <= 2.5s
- CLS: <= 0.05
- INP/TBT proxy acceptable in Lighthouse

Use production build, not dev server:

```bash
pnpm build
pnpm start
pnpm lighthouse
```

### 14.5 Security Gates

- Prompt injection red-team test passes.
- Payment request is refused or handed off.
- Hold without auth is rejected.
- Hold without explicit confirmation is rejected.
- Concurrent hold for same cabin cannot oversell.
- Logs do not include raw PII or secrets.

## 15. Agent Instructions

Development agents must follow this order:

1. Read `docs/CRUISE_AGENT_DEVELOPMENT_PLAN.md`.
2. Read this design spec.
3. Work only on assigned workstream.
4. Do not introduce new journeys.
5. Do not change architecture.
6. Keep all commerce-sensitive values deterministic.
7. Add tests for every acceptance gate touched.
8. Run relevant gates before reporting complete.

If a detail is missing:

- choose the smallest implementation consistent with this spec
- document the assumption in the PR/summary
- do not add new product scope

## 16. Freeze Checklist

This design spec can be frozen when:

- layout is approved
- required states are approved
- component contracts are approved
- performance budgets are approved
- SEO/noindex behavior is approved
- WCAG 2.2 AA target is approved
- production benefit callouts are approved
- no new user journeys are requested
