# Part 2 — Speaker Notes

**Visual deck (screenshots only):** open `docs/part2-deck/index.html` in a browser.
Use arrow keys or space to advance; `F` for fullscreen.

**Demo commands (if you run live instead of screenshots):** `docs/PART2-DEMO-MAP.md`

12 slides · ~29 minutes · then 15–20 minutes Q&A. Audience: Principal Engineers,
Architects, Engineering Managers. Every slide needs one sentence a Principal
respects and one an EM can act on.

**Delivery rules:** Never read the slide bullets aloud — they are anchors for the
room. Never type a command live; press up-arrow through pre-warmed history if
you demo live on top of the screenshots. When asked something you have not
verified, say so and say how you would find out.

---

## Slide 1 — Thesis and assumptions (2 min)

**Point:** Agents are untrusted workers. Deterministic systems stay authoritative.

**Say:** "One sentence you can hold me to: treat every agent — the one helping
an engineer write code and the one helping a guest plan a cruise — as an
untrusted worker. It can interpret, draft, summarize, and propose. It does not
get to be the system of record for anything that touches money, inventory, or a
control. Everything else in this plan is a consequence of that."

**Assumptions (state out loud):**
- Existing React SPAs, AEM, Node/Java + GraphQL, AWS, and SOX change control stay.
- No single-IDE mandate day one — one sanctioned floor, one policy overlay, one gateway.
- Titan harness is prior art, re-bound by config for RCG — not a product pitch.
- Guest feature is a prototype against simulated APIs; production calls authorized GraphQL only.

**Screenshot shows:** Cruise plan hero — every price tagged `pricing_tool` with `valid_until`.

**Trap:** Do not open with tooling or a file tree.

---

## Slide 2 — Why now (2 min)

**Point:** The choice is governed usage, not whether engineers use AI.

**Say:** "Assistants are already in use — uneven skill, no shared record. That is
a compliance risk before a quality risk. In SOX-regulated revenue systems,
'we cannot say which changes AI touched' is a finding waiting to happen. The
first 30 days buy control and a baseline, not velocity."

**Three failure modes:** shadow tools with production code; review as rubber
stamp on longer diffs; guest agent shipped without an eval gate.

**Screenshot shows:** Credential scan blocking a paste, exit 1.

**Q&A:** *"Isn't this slowing people down?"* → "Slightly, in two pilot teams for
30 days. The alternative is an audit where we cannot evidence pricing changes."

---

## Slide 3 — Tooling standard (3 min)

**Point:** Standardize the policy layer and runtime, not the editor.

**Say:** "Three layers. **Floor:** one sanctioned assistant under enterprise
agreement. **Overlay:** same protected paths, secret/PII scans, plugin allow-list,
telemetry on every agent. **Runtime:** model gateway on AWS — no vendor keys in apps."

**Selection criteria:** data residency, SSO, audit logs, no-training contract,
access review for SOX, cost controls, React + Java/Node coverage. "Winner = what
we can govern, not best autocomplete demo."

**Screenshot shows:** Enforcement matrix — 9 controls across Claude, Codex, Cursor.
Lead with the *advisory* rows — honesty beats a green dashboard.

**Q&A:** *"Why not mandate Copilot?"* → "Floor probably is Copilot. Overlay is
what makes it auditable."

---

## Slide 4 — 30/60/90 (3 min)

**Point:** All three pillars every horizon; explicit gate at each boundary.

**Say:** "Do not sequence pillars — adoption first, then process, then product,
and you get a year of enablement and no shipped agent."

- **Days 1–30:** 2 pilot teams, baseline, SOX posture, protected paths on revenue modules. *Gate: Security/Legal sign data handling; zero credential leaks.*
- **Days 31–60:** 4–6 teams, AI first-pass review in CI, guest feature behind flag. *Gate: evals green, fallback with model off, sample PRs pass audit walkthrough.*
- **Days 61–90:** Publish standard, dogfood or tiny anonymous traffic. *Gate: written kill-or-scale memo.*

**Owners:** you (champion), pilot EM, Architect/SRE (gateway), Security/Audit (SOX), QA (evals). Role-based — "I do not know your org chart yet."

**Screenshot shows:** Roadmap bullets + deploy-harness output (19 items, ~2s).

**Q&A:** *"Friendliest teams only?"* → "One enthusiastic, one skeptical on purpose."

---

## Slide 5 — SDLC control matrix (3 min)

**Point:** One line per stage — what AI may do, may never do, who is accountable.

**Say:** "Planning: drafts stories; PO owns backlog. Code: boilerplate and tests
inside allowed paths; no secrets or revenue modules without escalation. Review:
specialist first pass + adversarial verification; never approves its own work.
Test: finds missing scenarios; QA owns the gate. Docs/ops: drafts runbooks;
human executes production changes."

**Compressed:** "AI may draft. It may not approve, merge, deploy, hold inventory, or take payment."

**Screenshot shows:** `?gov` answered via answer-cache — model never called.

**Q&A:** *"15 automated reviewers = theater?"* → "First pass for the boring half.
If approval rates rise and escaped defects rise, cut the count."

---

## Slide 6 — Safety, SOX, IP — live demo (4 min)

**Point:** Compliance is a running control, not a policy paragraph.

**If live:** `SOX_DEMO_DIR="$HOME/.titan-sox-demo" bash demo/sox/run-demo.sh`
**If using screenshot:** narrate the three acts; do not talk over the visual.

**Frame first:** "AI-assisted code gets no exception — same change control.
Guest agent stays out of SOX scope: no payment, no booking confirmation, holds expire."

**Three acts:**
1. One policy → Claude deny-list, pre-commit, CI.
2. Preventive: commit to `services/pricing/` rejected.
3. Detective: four commits — one clean, self-approved, no ticket, `--no-verify` on revenue path → NO-GO, exit 1.

**Line that lands:** "Client-side hook is bypassable — evidence gate reads the committed record."

**Boundaries (volunteer before asked):**
- Approver from git trailer in demo; from PR API in production.
- `AI-Assisted` is self-declared disclosure.
- Telemetry is metadata-only — **not audit evidence. SCM and CI stay the system of record.**
- Proves the script CI would call; wiring the job is day-30.

**IP:** no training on code; secrets blocked before write; retrieved content = untrusted input.

---

## Slide 7 — Measurement (3 min)

**Point:** Adoption + stability counter-metrics; no self-reported speedup.

**Say:** "I will not claim 20% faster — METR found developers felt faster while
measuring slower. I measure: active users/day, % PRs with AI first pass, cost
per developer per active day, cost per merged PR (trend only), rework ratio."

**Honesty beat:** "Safety hooks block but four do not emit telemetry —
`SAFETY_HOOKS_INSTRUMENTED = false`. Panel shows 'Not instrumented', not zero.
Day-30 fix. Better a dashboard that refuses to fake a number."

**Guest agent gates:** grounded answer rate, zero hallucinated prices, zero
unauthorized tool calls, fallback with model off, no oversell.

**Screenshot shows:** Titan safety panel mock + vitest 15 passed.

**Q&A:** *"ROI for CFO?"* → "Cost per merged PR minus rework vs license spend,
paired with change-fail rate. No annualizing a two-week sample."

---

## Slide 8 — Worked example: architecture (3 min)

**Point:** Governed commerce orchestration, not a chatbot.

**Say:** "Guest: seven nights Caribbean, family of four, balcony, under $5k.
Model interprets and explains trade-offs — produces no numbers. Search, pricing,
availability, deltas, holds are deterministic tools with typed schemas."

**Boundary sequence:** anonymous planning first; evidence objects with validity
window; auth at commitment; session rotates on auth; hold only after explicit
confirmation; handoff to checkout. Cannot take payment or confirm booking — keeps
it out of SOX scope.

**Screenshot shows:** Compare deltas as subtraction; onboard-credit answer with
injection stripped.

**Q&A:** *"Why not complete booking?"* → "Small conversion gain vs mis-booked
cruise with model in audit path. Revisit at day 90 with eval data."

---

## Slide 9 — Evaluate and operate (2 min)

**Point:** Eval suite = merge gate; failure path = product feature.

**Say:** "10 golden + 8 red-team in CI. Red-team: injected instructions, hidden
discounts, payment requests, other guest's booking, hold without auth, stale
price revalidation, concurrent holds, unauthorised tool call. Each is a capability
boundary, not a prompt fix."

**Operations:** traces with tool timings, tokens, cost, fallback flag. Model off
→ same commerce APIs → degraded, not down.

**Admit:** Suite caught a real defect — seed fares made hero unsatisfiable, run
reported NO-GO. Data regression evals exist to catch.

**Screenshot shows:** 18/18 PASS + concurrent hold no-oversell.

**Q&A:** *"Who owns golden set?"* → "QA owns, Product contributes, merge gate."

---

## Slide 10 — Enablement and influence (2 min)

**Point:** Policy and pairing, not encouragement.

**Say:** "Champions pair with skeptics; skeptics get tests/docs/review for two
weeks before production code — not a demotion. EMs get leadership dashboard view.
Offshore gets same overlay — no second-class governance."

**Influence move:** "Open with blocked secrets and rework cost, not a model bake-off."

**Screenshot shows:** `sox-evidence.py` failing this repo's last 3 commits — self-indictment.

**Q&A:** *"Senior skeptic refuses?"* → "Give them review quality / guardrails to own."

---

## Slide 11 — Risks and kill criteria (2 min)

**Point:** Name what you stop, not just what you start.

**Say:** "Review rubber stamp — watch escaped defects + change-fail rate. Cost
drift — caps + alerts. Vendor lock-in — gateway + agent-neutral policy. Guest
over-reach — pressure to let it book."

**Kill criteria:** pause expansion if change-fail rises, secret leaks, review
degrades. Kill/rollback guest feature if eval fails, oversell, cost cap blown.
Trade-off: slower first 30 days for defensible audit trail.

**Screenshot shows:** Refusal + gate exit code 0 today, 1 on failure.

**Q&A:** *"Leadership wants autonomous booking?"* → "Separate control review,
Audit in room, transaction limit, documented owner."

---

## Slide 12 — The ask (1 min)

**Point:** Three asks, then stop.

**Say:** "Pilot mandate — two teams, 30 days, capacity protected. Security,
Legal, Internal Audit in weeks 1–2 — SOX walkthrough is longest-lead dependency.
Day-90 forum with authority to scale or kill."

**Close:** "Transferable asset is the operating model — typed tools, grounded
answers, eval gates, observability, fallback, human accountability at the
right boundaries."

**No screenshot** — recap artifacts they already saw.

---

## Cross-cutting Q&A

**vs Copilot alone?** Floor = autocomplete. Overlay = protected paths, evidence,
evals, measurement. Second list survives audit.

**Biggest failure risk?** Adoption theater — tools installed, review quietly degrades.
Rework ratio + change-fail on same slide as adoption.

**What would you do differently?** Instrument guardrails day one — can prove
enforcement in demo but not metric yet.

**Hallucinated price to guest?** Cannot by construction — values only from tools,
eval asserts it. P1, flag rollback, new red-team case before fix ships.

**Who becomes redundant?** Nobody — review moves from mechanical to design/risk.

---

## Timing cheat sheet

| Slide | Min | Cut first? |
|---|---|---|
| 1 Thesis | 2 | no |
| 2 Why now | 2 | yes → 1 |
| 3 Tooling | 3 | no |
| 4 30/60/90 | 3 | no |
| 5 SDLC | 3 | no |
| 6 SOX demo | 4 | **never** |
| 7 Measurement | 3 | no |
| 8 Architecture | 3 | no |
| 9 Eval/ops | 2 | no |
| 10 Enablement | 2 | yes → 1 |
| 11 Risks | 2 | no |
| 12 Ask | 1 | no |

**Total:** 29 min content + 15–20 min Q&A
