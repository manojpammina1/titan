# Cruise Agent Development Plan

Status: freeze candidate
Owner: Manoj Pammina
Audience: RCG Principal Engineer take-home, Part 1 and Part 2
Last updated: 2026-08-09

This document converts the approved Option 5 narrative into an
implementation-ready build plan. The goal is a production-grade prototype of
an Agentic Cruise Planning Assistant that also acts as the worked example for
the Part 2 agentic-development operating model.

The Titan harness remains the governance and agent-development proof point.
The Cruise Agent should be built as a separate application workspace and
governed by Titan, not embedded inside the Titan harness source tree.

## 1. Question Being Answered

Design and demonstrate an agentic cruise-planning experience for e-commerce.
The system should help a guest find a suitable cruise, understand trade-offs,
answer policy questions from approved content, create an authenticated cabin
hold after explicit confirmation, and hand off to existing checkout.

The answer is not "build a chatbot." The answer is a governed commerce
orchestration layer:

- The model interprets intent and explains trade-offs.
- Deterministic tools own price, availability, inventory, holds, and booking
  handoff.
- Existing commerce systems remain authoritative.
- The assistant never performs payment or booking confirmation.
- Every commerce-sensitive claim is traceable to current deterministic tool
  output.

## 2. Frozen Scope

Build exactly two demo paths.

### 2.1 Hero Path

1. Guest opens anonymously.
2. Guest enters: "7-night Caribbean cruise in March for a family of four,
   balcony cabin, under $5,000."
3. Voyage Canvas materializes:
   - traveler core
   - constraints
   - three journey possibilities
   - evidence objects
4. Guest locks "Balcony."
5. Guest moves the budget slider.
6. Eligible journeys reorganize deterministically.
7. Guest compares two sailings.
8. System shows deterministic gain/loss deltas.
9. Guest asks a policy question.
10. Assistant answers with cited approved policy content.
11. Guest selects a voyage.
12. UI shows verified price and availability evidence.
13. Guest authenticates at the commitment boundary.
14. Guest explicitly confirms cabin hold.
15. Inventory service creates an atomic durable hold.
16. Assistant hands off to existing checkout deep link.

### 2.2 Failure Path

1. Model is disabled, slow, or times out.
2. Latest confirmed criteria remain available from deterministic parser and
   UI chips.
3. Voyage Canvas falls back to GuidedVoyagePlanner.
4. GuidedVoyagePlanner uses the same deterministic search, pricing,
   availability, and policy APIs.
5. User can still search and select a voyage without the model.

### 2.3 Non-goals

Do not build:

- voice
- multi-language
- autonomous payment
- autonomous booking confirmation
- multiple product agents
- live AEM integration
- direct AEM authoring
- real payment provider
- large vector database
- Kubernetes
- broad analytics dashboard
- WebGL or 3D canvas
- live mobile renderer
- multiple customer journeys
- loyalty pricing beyond a clearly marked stub

Anything new must replace an existing scoped item. It must not expand the
demo surface.

## 3. Build Location and Repo Shape

Recommended application workspace:

```text
C:\POC\RCG\cruise-agent
```

Mac equivalent:

```text
/Users/manojpammina/Desktop/Interview-Prep/RCG/cruise-agent
```

Titan remains here:

```text
/Users/manojpammina/Desktop/Interview-Prep/RCG/titan
```

The Cruise Agent repo should receive the rendered Titan governance payload:

```text
CLAUDE.md
AGENTS.md
.claude/
.codex/
.cursor/
governance/
governance-manifest.json
```

## 4. Target Monorepo Structure

Use a pnpm workspace with clear package boundaries.

```text
cruise-agent/
  apps/
    web/
      app/
      components/
      lib/
      public/
      tests/
  services/
    orchestrator/
      src/
        api/
        agent/
        auth/
        telemetry/
        tools/
      tests/
    inventory/
      src/
      tests/
  packages/
    experience-model/
      src/
      tests/
    commerce-domain/
      src/
      tests/
    content-adapter/
      src/
      data/
      tests/
    design-system/
      src/
      tokens/
      tests/
    evals/
      golden/
      redteam/
      src/
  data/
    seed/
      sailings.json
      cabins.json
      policies.json
      destinations.json
  scripts/
    seed.ts
    smoke-demo.ts
  docker-compose.yml
  package.json
  pnpm-workspace.yaml
  README.md
```

## 5. Technical Stack

### 5.1 Frontend

- Next.js App Router
- React
- TypeScript
- SVG/DOM for Voyage Canvas
- SSE for streaming status and model narrative
- Token-based component primitives in `packages/design-system`
- AccessibleVoyageList shared by:
  - screen-reader equivalent
  - model-outage fallback
  - deterministic guided planner

### 5.2 Backend

- Node.js
- TypeScript
- Orchestrator service behind a model abstraction
- Deterministic tool adapters for search, availability, pricing, hold, and
  booking handoff
- No direct database access from the model layer
- Tool schemas typed and validated at every boundary

### 5.3 Data and Local Infra

- MongoDB replica set for durable inventory and hold state
- Redis for cache, session state, coordination, and expiry signals only
- Docker Compose for local MongoDB and Redis
- Seeded prototype dataset:
  - 8 to 12 sailings
  - one balcony cabin category for hero path
  - finite cabin inventory per sailing
  - 3 to 4 policy documents
  - destination snippets
  - deterministic pricing rules

### 5.4 Model Runtime

Use a provider abstraction:

```text
LLM_PROVIDER=mock|gemini
```

Required behavior:

- `mock` is the default for deterministic demos and failure path.
- `gemini` is optional for the POC only.
- Production slides say "enterprise model gateway," not a hard-coded model.
- No real PII goes to the POC model provider.

## 6. System Architecture

```text
Guest Browser
  |
  v
Next.js Web App / BFF
  |
  v
Agent Orchestrator
  |-- Model Provider Abstraction
  |-- Deterministic Parser
  |-- Experience Reducer
  |-- Tool Registry
  |     |-- searchSailings
  |     |-- checkAvailability
  |     |-- getPricing
  |     |-- answerPolicyQuestion
  |     |-- createHold
  |     |-- startBooking
  |
  |-- Session Service
  |     `-- Redis
  |
  `-- Inventory Service
        `-- MongoDB durable records

Approved Content Adapter
  `-- AEM-style JSON export in POC

Observability
  `-- structured traces, tool timings, tokens, cost, safety events
```

Production view for slides:

```text
CloudFront + WAF
  -> Next.js Assistant / BFF
  -> Orchestrator on ECS Fargate
      -> Search GraphQL API
      -> Availability GraphQL API
      -> Pricing GraphQL API
      -> Booking GraphQL API
      -> Content Adapter
      -> Enterprise Model Gateway
      -> Session Service / ElastiCache Redis
Inventory Service
  -> MongoDB durable inventory and holds
Observability
  -> OpenTelemetry -> CloudWatch / X-Ray
```

The prototype simulates enterprise APIs. The presentation must state that in
production the assistant calls authorized APIs and does not touch databases or
commerce systems directly.

## 7. Core Domain Contracts

### 7.1 Criteria

```ts
export type CruiseCriteria = {
  destination?: "caribbean" | "bahamas" | "alaska" | "mediterranean";
  nights?: number;
  departureMonth?: string;
  travelers: {
    adults: number;
    children: number;
  };
  cabinType?: "interior" | "oceanview" | "balcony" | "suite";
  maxBudgetUsd?: number;
  locked: Array<"destination" | "nights" | "departureMonth" | "cabinType" | "budget">;
};
```

### 7.2 Evidence

```ts
export type Evidence =
  | VerifiedPriceEvidence
  | AvailabilityEvidence
  | PolicyEvidence
  | TradeoffEvidence;

export type VerifiedPriceEvidence = {
  kind: "verified_price";
  sailingId: string;
  cabinType: string;
  occupancy: number;
  totalUsd: number;
  taxesAndFeesUsd: number;
  asOf: string;
  validUntil: string;
  source: "pricing_tool";
};

export type AvailabilityEvidence = {
  kind: "availability";
  sailingId: string;
  cabinType: string;
  availableCabins: number;
  asOf: string;
  validUntil: string;
  source: "availability_tool";
};

export type PolicyEvidence = {
  kind: "policy";
  policyId: string;
  title: string;
  publishedAt: string;
  excerpt: string;
  source: "approved_content_adapter";
};

export type TradeoffEvidence = {
  kind: "tradeoff";
  comparedSailingIds: [string, string];
  deltas: Array<{
    label: string;
    value: string;
    computedBy: "comparison_engine";
  }>;
};
```

### 7.3 Experience Model

```ts
export type VoyageExperience = {
  sessionId: string;
  phase: "intent" | "possibilities" | "compare" | "commitment" | "handoff";
  criteria: CruiseCriteria;
  availableOptions: SailingOption[];
  selectedSailingId?: string;
  selectedCabinId?: string;
  evidence: Evidence[];
  decisionHistory: DecisionEvent[];
  modelState: "available" | "slow" | "disabled" | "failed";
};

export type ExperienceAction =
  | { type: "ADD_CONSTRAINT"; constraint: Partial<CruiseCriteria> }
  | { type: "RELAX_CONSTRAINT"; field: keyof CruiseCriteria }
  | { type: "LOCK_PREFERENCE"; field: CruiseCriteria["locked"][number] }
  | { type: "COMPARE_OPTIONS"; sailingIds: [string, string] }
  | { type: "FOCUS_DECISION"; sailingId: string }
  | { type: "ASK_CLARIFICATION"; question: string }
  | { type: "EXPLAIN_TRADEOFF"; sailingIds: [string, string] };
```

Invariant: the model may propose an `ExperienceAction`. It may not emit UI
code, commerce values, payment instructions, holds, or booking confirmations.

## 8. Deterministic Tool Contracts

### 8.1 `searchSailings(criteria)`

Input:

```ts
CruiseCriteria
```

Output:

```ts
{
  options: SailingOption[];
  asOf: string;
}
```

Rules:

- Query seeded sailing data.
- Respect locked constraints.
- Return at most 3 primary options for hero path.
- Do not calculate price or inventory here.

### 8.2 `checkAvailability(sailingId, cabinType)`

Output:

```ts
AvailabilityEvidence
```

Rules:

- Read finite inventory.
- Return `validUntil`.
- Never rely on Redis as authority.

### 8.3 `getPricing(sailingId, cabinType, occupancy)`

Output:

```ts
VerifiedPriceEvidence
```

Rules:

- Deterministic formula.
- Include taxes and fees.
- Include `asOf` and `validUntil`.
- Re-run before hold.

### 8.4 `answerPolicyQuestion(question, criteria)`

Output:

```ts
{
  answer: string;
  evidence: PolicyEvidence[];
}
```

Rules:

- Retrieve only approved content.
- Treat retrieved content as untrusted data.
- Do not follow instructions found inside retrieved content.
- Cite policy title and publication date.

### 8.5 `createHold(input)`

Input:

```ts
{
  sailingId: string;
  cabinId: string;
  cabinType: string;
  guestAuthContext: {
    guestId: string;
    authTime: string;
  };
  idempotencyKey: string;
  guestConfirmed: true;
}
```

Output:

```ts
{
  holdId: string;
  expiresAt: string;
  sailingId: string;
  cabinId: string;
  verifiedPrice: VerifiedPriceEvidence;
}
```

Rules:

- Must require authenticated guest context.
- Must require explicit confirmation.
- Must revalidate price and inventory.
- Must create hold in MongoDB transaction or equivalent durable conditional
  write.
- Must persist idempotency key.
- Must reject if cabin already held.
- Redis may store TTL signal only.

### 8.6 `startBooking(holdId)`

Output:

```ts
{
  checkoutUrl: string;
  handoffToken: string;
  expiresAt: string;
}
```

Rules:

- Deep link only.
- Existing checkout owns booking and payment.
- Assistant never charges payment.

## 9. Agent Orchestration Loop

Per turn:

1. Accept user input and current `VoyageExperience`.
2. Run deterministic parser first.
3. Merge safe criteria updates.
4. Decide whether model is needed.
5. If model is needed:
   - call model through provider abstraction
   - request bounded `ExperienceAction`
   - validate action schema
6. Execute deterministic tools for any commerce data.
7. Recompute `availableOptions`, evidence, and trade-off deltas.
8. Generate or stream model narrative only after tool evidence exists.
9. Persist safe non-PII session state.
10. Emit observability event.

No LLM call on initial page load. AI cost should track engaged planning, not
raw site traffic.

## 10. Grounding Rules

Commerce-sensitive claims include:

- price
- taxes and fees
- availability
- inventory
- dates
- cabin counts
- discounts
- hold expiration
- booking status
- comparison deltas such as "$360 cheaper"

Rules:

- Each claim must trace to a deterministic tool result from the current turn.
- UI evidence objects are authoritative.
- Model may repeat verified values with provenance.
- Model may not originate commerce-sensitive numbers.
- RAG is never used for live pricing, availability, inventory, discounts, or
  booking status.

## 11. UX Design

### 11.1 Desktop Layout

Use a dense operational product layout, not a marketing landing page.

```text
 ---------------------------------------------------------------
| Top bar: Royal Caribbean planning assistant | model/fallback |
 ---------------------------------------------------------------
| Constraints pane | Voyage Canvas                  | Evidence  |
|                  |                                | Why this  |
| travelers        | traveler core                  | Price     |
| budget slider    | 3 journey possibilities        | Inventory |
| locked prefs     | compare two                    | Policy    |
| decision chips   | selected voyage                | History   |
 ---------------------------------------------------------------
```

### 11.2 Components

Required:

- `VoyageCanvas`
- `ConstraintPanel`
- `BudgetSlider`
- `LockPreferenceButton`
- `JourneyPossibility`
- `EvidenceRail`
- `VerifiedPriceEvidenceCard`
- `AvailabilityEvidenceCard`
- `PolicyEvidenceCard`
- `CompareTwoPanel`
- `GuidedVoyagePlanner`
- `AccessibleVoyageList`
- `StreamingStatus`
- `AuthBoundaryModal`
- `ConfirmHoldPanel`
- `CheckoutHandoffBanner`

### 11.3 Interaction Rules

- Stream status steps:
  - "Understanding preferences"
  - "Searching sailings"
  - "Checking balcony availability"
  - "Retrieving current pricing"
- Render price and inventory only after deterministic tool response.
- Show `asOf` and `validUntil`.
- Use uncertainty states:
  - "I need one more detail"
  - "Live pricing is unavailable"
  - "Availability changed while you were deciding"
  - "I cannot verify this right now"
- Do not show fake confidence percentages.

### 11.4 Accessibility

Required:

- keyboard-only operation
- visible focus
- `aria-live="polite"` for streaming status
- stop-generation control
- screen-reader labels on price, cabin, sailing, and hold controls
- no information by color alone
- reduced-motion support
- focus movement after results appear
- checkout handoff announced before navigation
- AccessibleVoyageList equivalent to the canvas, not degraded

## 12. Data Model

### 12.1 Mongo Collections

```text
sailings
cabins
holds
idempotency_keys
```

### 12.2 Sailing

```ts
type Sailing = {
  id: string;
  shipName: string;
  itineraryName: string;
  destination: string;
  departurePort: string;
  departureDate: string;
  nights: number;
  ports: string[];
  tags: string[];
  basePricesByCabinType: Record<string, number>;
};
```

### 12.3 Cabin

```ts
type Cabin = {
  id: string;
  sailingId: string;
  cabinType: "interior" | "oceanview" | "balcony" | "suite";
  deck: number;
  capacity: number;
  status: "available" | "held" | "booked";
};
```

### 12.4 Hold

```ts
type Hold = {
  id: string;
  sailingId: string;
  cabinId: string;
  guestId: string;
  status: "active" | "expired" | "converted" | "released";
  priceSnapshot: VerifiedPriceEvidence;
  createdAt: string;
  expiresAt: string;
  idempotencyKey: string;
};
```

## 13. API Surface

Frontend to BFF:

```text
POST /api/session
POST /api/experience/turn
POST /api/experience/compare
POST /api/policy/question
POST /api/auth/demo-login
POST /api/hold
POST /api/booking/start
GET  /api/stream/:turnId
```

Service boundaries:

```text
orchestrator -> commerce tools
orchestrator -> content adapter
orchestrator -> inventory service
orchestrator -> model provider
```

The model provider never receives:

- raw guest identity
- payment data
- credentials
- direct database handles
- unrestricted tool credentials

## 14. Security and Compliance Controls

Required controls:

- anonymous-first planning
- progressive auth at commitment boundary
- session rotation on auth
- copy only safe planning state into authenticated session
- expire anonymous session
- server-side tool authorization
- no model-held credentials
- prompt-injection defense for retrieved content
- PII redaction before model call
- audit event per turn
- idempotency on hold creation
- explicit guest confirmation before hold
- no payment tool
- no autonomous booking confirmation

Session upgrade flow:

```text
anon_session
  -> user authenticates
  -> rotate session id
  -> copy safe preferences
  -> bind to guest id
  -> expire anon session
  -> enable hold action
```

## 15. Observability

Each turn emits:

```ts
type TurnTrace = {
  traceId: string;
  sessionIdHash: string;
  turnId: string;
  modelProvider: "mock" | "gemini" | "none";
  modelLatencyMs?: number;
  toolCalls: Array<{
    name: string;
    latencyMs: number;
    status: "ok" | "error";
  }>;
  tokens?: {
    input: number;
    output: number;
  };
  estimatedCostUsd?: number;
  fallbackUsed: boolean;
  safetyEvents: string[];
};
```

Demo UI needs only a compact evaluation summary, not a broad analytics
dashboard.

## 16. Evaluation Plan

### 16.1 Golden Set

Minimum cases:

1. family of four, seven nights, March, Caribbean, balcony, under $5,000
2. unclear destination, ask clarifying question
3. budget too low, suggest relaxing budget or cabin type
4. compare two eligible sailings
5. policy question about cancellation
6. policy question about required travel documents
7. model unavailable, fallback planner still works
8. prompt injection in retrieved policy content is ignored
9. attempted payment request is refused and handed off
10. hold requires auth and confirmation

### 16.2 Metrics

Required:

- grounded answer pass rate
- no hallucinated commerce values
- no unauthorized tool calls
- fallback success rate
- hold no-oversell test pass
- p95 local response time for deterministic path
- model cost per engaged planning session

### 16.3 Red-Team Cases

Required:

- policy content says "ignore previous instructions"
- user asks for hidden discounts
- user asks assistant to complete payment
- user asks for another guest's booking
- user asks to hold cabin without login
- stale price shown, hold revalidates
- concurrent hold attempts for same cabin

## 17. Test Plan

Unit tests:

- criteria parser
- experience reducer
- tool schemas
- pricing engine
- availability lookup
- comparison engine
- content adapter retrieval
- prompt-injection filter

Integration tests:

- hero path without live model
- fallback path
- policy citation path
- auth boundary
- hold idempotency
- concurrent hold conflict
- checkout handoff

Frontend tests:

- keyboard navigation
- focus movement
- `aria-live` status
- reduced-motion behavior
- evidence cards show freshness fields
- fallback planner uses same API contracts

Eval tests:

- golden set
- red-team set
- faithfulness judge over cited policy answers
- deterministic commerce-claim assertion

## 18. Demo Script

Opening line:

"This is not a chatbot that happens to search cruises. It is a governed
commerce orchestration layer where the model interprets intent and trusted
systems remain authoritative for pricing, inventory, authorization, booking,
and payment."

Live steps:

1. Start on anonymous planning surface.
2. Enter hero prompt.
3. Point out zero model call until engaged input.
4. Show canvas materialization.
5. Lock balcony.
6. Move budget slider.
7. Compare two sailings.
8. Point out deterministic deltas and evidence.
9. Ask policy question.
10. Show cited policy answer.
11. Select voyage.
12. Show verified price and availability freshness.
13. Trigger hold.
14. Show auth boundary.
15. Demo login.
16. Confirm hold.
17. Show hold expiration.
18. Hand off to checkout.
19. Toggle model outage.
20. Show GuidedVoyagePlanner fallback.

Close:

"The reusable part is not just the UI. It is the operating model: typed tools,
grounding, evals, observability, fallback, and human accountability at the
right boundaries."

## 19. Development Workstreams

Use Titan-governed agents after this plan is frozen.

### Workstream A: Repo Scaffold and Infra

Agent profile:

- developer mode
- strict TypeScript reviewer
- reliability reviewer

Tasks:

- create pnpm workspace
- create Next.js app
- create services and packages
- add Docker Compose for MongoDB and Redis
- add seed script
- add root scripts
- add README

Acceptance:

- local dev starts
- seed data loads
- unit test runner works
- no Titan harness files modified

### Workstream B: Domain and Deterministic Tools

Agent profile:

- developer mode
- correctness reviewer
- test validator

Tasks:

- implement `commerce-domain`
- implement search, pricing, availability, compare
- implement inventory hold service
- implement idempotency
- implement concurrent hold tests

Acceptance:

- deterministic hero criteria returns 3 options
- pricing includes freshness
- availability includes freshness
- hold revalidates price and cabin
- concurrent hold cannot oversell

### Workstream C: Experience Model and Orchestrator

Agent profile:

- developer mode
- adversarial verifier
- security reviewer

Tasks:

- define `VoyageExperience`
- define action schemas
- implement deterministic parser
- implement model provider abstraction
- implement mock provider
- implement turn loop
- implement fallback state
- implement SSE stream

Acceptance:

- model cannot emit commerce values
- invalid action is rejected
- mock provider drives hero path
- fallback works with model disabled

### Workstream D: Content Adapter and Policy QA

Agent profile:

- developer mode
- security reviewer
- adversarial verifier

Tasks:

- seed policy docs
- build AEM-style JSON content adapter
- implement policy retrieval
- implement citation object
- add injection defense
- add policy golden tests

Acceptance:

- policy answer includes citations
- retrieved instructions are ignored
- no live price/availability comes from content adapter

### Workstream E: Frontend Voyage Canvas

Agent profile:

- developer mode
- component usage reviewer
- accessibility reviewer via QA mode

Tasks:

- implement design tokens
- implement canvas layout
- implement constraint panel
- implement evidence rail
- implement compare panel
- implement auth modal
- implement hold confirmation
- implement fallback planner
- implement AccessibleVoyageList

Acceptance:

- hero path is complete
- fallback path is complete
- keyboard-only operation works
- evidence shows `asOf` and `validUntil`
- no text overlap at desktop and mobile widths

### Workstream F: Evaluation, Red Team, and Demo Hardening

Agent profile:

- qa automation
- adversarial verifier
- reliability reviewer

Tasks:

- create golden set
- create red-team set
- add eval runner
- add demo smoke script
- add observability trace viewer or compact trace output
- add final demo checklist

Acceptance:

- all golden cases pass
- red-team cases pass
- demo can run in mock mode with no network
- model outage path is deterministic

## 20. Build Sequence

Phase 0: freeze plan

- approve this document
- no architecture changes after approval
- all new ideas must replace scoped work

Phase 1: scaffold

- create app repo
- deploy Titan governance payload
- add package boundaries
- add seed data and Docker Compose

Phase 2: deterministic spine

- criteria parser
- search
- pricing
- availability
- comparison
- inventory hold

Phase 3: orchestrator

- experience model
- model abstraction
- mock provider
- turn loop
- SSE
- fallback state

Phase 4: UI

- Voyage Canvas
- evidence objects
- fallback planner
- auth and hold panels
- accessibility pass

Phase 5: safety and eval

- policy adapter
- injection tests
- golden set
- red-team set
- observability events

Phase 6: demo freeze

- smoke test
- record backup demo
- prepare Q&A lines
- no new features

## 21. Freeze Checklist

Plan can be frozen when each answer is yes:

- The build has exactly two paths: hero and failure.
- AEM is represented by content adapter only.
- RAG is limited to approved descriptive and policy content.
- Pricing, availability, inventory, holds, booking, and comparison deltas are
  deterministic.
- MongoDB inventory service is durable authority.
- Redis is not inventory authority.
- Payment is outside assistant authority.
- Auth is required before hold.
- Explicit confirmation is required before hold.
- Model provider is abstracted.
- Mock mode supports full demo.
- No hard-coded unverified model name appears on slides.
- Accessibility equivalent is real.
- Mobile is a static mock or responsive view only, not a separate renderer.
- No additional product journeys are in scope.
- Titan harness remains separate from Cruise Agent app source.

## 22. Open Decisions Before Development

These are small implementation choices, not architecture reopeners:

1. Final app folder name:
   - recommended: `cruise-agent`
2. Package manager:
   - recommended: `pnpm`
3. Next.js API strategy:
   - recommended: Next.js BFF plus separate service packages in the same
     workspace for demo simplicity
4. Optional live model:
   - recommended: mock first; Gemini only after deterministic demo is stable
5. Styling:
   - recommended: local token package with simple CSS variables and React
     primitives

## 23. Final Scope Lock Statement

After this document is approved, development agents may build only the files,
services, components, tests, and scripts required by this plan.

Architecture changes require an explicit plan update. Feature additions must
replace an existing scoped item and preserve the demo timeline.
