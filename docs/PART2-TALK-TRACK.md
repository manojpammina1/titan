# Part 2 — Strategy Case Study: Talk Track

Enabling agentic development across a SOX-regulated e-commerce engineering org.
12 slides, 29 minutes of content, 15–20 minutes of Q&A after.

Audience is mixed: Principal Engineers, Architects, Engineering Managers. Every
slide needs one sentence a Principal respects and one an EM can act on.

## Timing

Every slide has one executable action behind it. Exact commands, expected
output, and what to say while it runs: `docs/PART2-DEMO-MAP.md`.

| # | Slide | Min | Cut first if long | Action on stage |
|---|---|---|---|---|
| 1 | Thesis and assumptions | 2 | no | `cruise_demo.py plan "<hero prompt>"` |
| 2 | Why now | 2 | yes → 1 | `credential-scan.py --scan-stdin` blocks a paste |
| 3 | Tooling standard | 3 | no | `titan-render.py` + `show-enforcement-matrix.py` |
| 4 | 30/60/90 | 3 | no | `deploy-harness.sh` onboards a repo |
| 5 | SDLC control matrix | 3 | no | `answer-cache.py` answers `?gov` at zero tokens |
| 6 | Safety, SOX, IP — live demo | 4 | never | `demo/sox/run-demo.sh`, three acts |
| 7 | Measurement | 3 | no | `npx vitest run` + the `false` flag + a real event |
| 8 | Worked example: architecture | 3 | no | `compare`, `ask` — citation and injection stripped |
| 9 | Worked example: evaluate and operate | 2 | no | `eval`, `--model off`, `hold`, `--concurrent 5` |
| 10 | Enablement and influence | 2 | yes → 1 | `sox-evidence.py` fails this repo |
| 11 | Risks and kill criteria | 2 | no | refusal + gate exit code |
| 12 | The ask | 1 | no | none — recap what already ran |

Three rules for delivery. Never read a slide aloud. Never type a command live —
press up-arrow through pre-warmed history. When you are asked something you have
not verified, say so and say how you would find out; the panel is scoring
judgment, not recall.

---

## Slide 1 — Thesis and assumptions (2 min)

**Point:** Agents are untrusted workers. Deterministic systems stay
authoritative. That single idea governs both how we build and what we ship.

**Say:** "I want to give you one sentence you can hold me to for the next
half hour. Treat every agent — the one helping an engineer write code and the
one helping a guest plan a cruise — as an untrusted worker. It can interpret,
draft, summarize, and propose. It does not get to be the system of record for
anything that touches money, inventory, or a control. Everything else in this
plan is a consequence of that."

Then state assumptions out loud, because the panel will otherwise spend Q&A
probing them:

- You already have React SPAs, AEM, Node and Java behind GraphQL, AWS, and an
  existing SOX change-control process. I am not proposing to replace any of it.
- I am not proposing a single-IDE mandate on day one. I am proposing one
  sanctioned floor, one policy overlay, and one model gateway.
- The harness I will show is prior art from an AEM and commerce deployment. For
  RCG it would be re-bound by config: org identity, repos, protected paths,
  contacts. It is not a product I am selling you.
- The guest-facing feature I use as the worked example is a designed prototype
  against simulated APIs. In production it calls authorized GraphQL services
  only.

**Trap:** Do not open with tooling, the repo, or a file tree. Open with the
governing idea.

---

## Slide 2 — Why now (2 min)

**Point:** The choice is not whether engineers use AI. It is whether that usage
is governed, measured, and defensible.

**Say:** "In an org this size, assistants are already in use — with uneven
skill, uneven quality, and no shared record of what they touched. That is the
actual risk, and it is a compliance risk before it is a quality risk. In a
SOX-regulated revenue system, 'a tool helped write this and we cannot say
which changes' is a finding waiting to happen. So the first 30 days of my plan
buy control and a baseline, not velocity."

Name the three failure modes you are preventing: shadow tools with production
code in them, review becoming a rubber stamp because the diffs got longer, and
a guest-facing agent shipped without an evaluation gate.

**Q&A likely:** *"Isn't this just slowing people down?"* → "For 30 days,
slightly, in two pilot teams. The alternative is discovering in an audit that
we cannot evidence changes to pricing code. I would rather spend a month than
explain that."

---

## Slide 3 — Tooling standard (3 min)

**Point:** Standardize the *policy layer* and the *runtime*, not the editor.

**Say:** "Three layers. A **floor**: one sanctioned assistant under an
enterprise agreement, default for every engineer, so nobody has a reason to
paste production code into a consumer chat window. A **power path**: the
stronger agentic tools are allowed, but only through a governance overlay that
gives all of them the same protected paths, the same secret and PII scanning,
the same plugin allow-list, and the same telemetry. And a **runtime**: guest
and internal agents call a model gateway on AWS, never a vendor key embedded in
an application."

Selection criteria, said as a list you clearly did not invent on the spot: data
residency, SSO, audit logs, a no-training contractual term, access review that
survives SOX, cost controls, and coverage for both React and Java/Node. "The
winner is the stack we can govern, not the one with the best autocomplete
demo."

**Q&A likely:**
- *"Why not just mandate Copilot and be done?"* → "The floor probably is
  Copilot given the existing estate. But a floor alone gives you no protected
  paths, no evidence, and no agentic workflows. The overlay is the part that
  makes it auditable."
- *"Why not let every team choose?"* → "They can choose the editor. They cannot
  choose the policy. One rulebook rendered into each tool, or we get three
  different definitions of 'blocked'."

---

## Slide 4 — 30/60/90 (3 min)

**Point:** All three pillars move in every horizon, with a small blast radius
early and an explicit gate at each boundary.

**Say:** "The mistake is sequencing the pillars — adoption first, then process,
then product. That gives you a year of enablement and no shipped agent. Each
horizon moves all three, and each one has an exit gate I would hold myself to."

- **Days 1–30, prove control.** Two full-stack pilot teams on the overlay.
  Baseline captured before any claim: active users, cost per developer per day,
  rework, and the SOX posture. SDLC side: map AI usage to the existing change
  class and land real protected paths on revenue-relevant modules. Product
  side: architecture and threat model on paper, no guest traffic.
  *Gate: Security and Legal sign data handling; zero credential leaks.*
- **Days 31–60, wire the factory.** Four to six teams, champions, office hours.
  AI first-pass review and test-impact in CI. Build the guest feature behind a
  flag in a non-prod account with the eval suite running in CI.
  *Gate: evals green, fallback works with the model off, a sample of AI-touched
  PRs passes an audit walkthrough.*
- **Days 61–90, evidence or kill.** Publish the org standard, onboard the next
  wave, train EMs to read the dashboard. Dogfood the guest feature or expose a
  tiny slice of anonymous planning traffic.
  *Gate: a written kill-or-scale memo. No silent expansion.*

**Owners:** you as technical champion; a pilot EM accountable for team change;
Architect and SRE for the gateway; Security with Internal Audit for SOX;
Product for guest scope; QA for the eval suite. "These are role-based owners.
I do not know your org chart yet, and I would not pretend to."

**Q&A likely:** *"What if the pilot teams are your two friendliest teams?"* →
"That is a real bias. I would pick one enthusiastic team and one skeptical team
on purpose, because the skeptical team's objections are the actual rollout
plan."

---

## Slide 5 — SDLC control matrix (3 min)

**Point:** One line per stage stating what AI may do, what it may never do, and
who remains accountable.

**Say:** "This is the slide I would put on a wall. Planning: it drafts stories
and stress-tests a design; the PO still owns the backlog. Code: it writes
boilerplate, tests, and refactors inside allowed paths; it does not touch
secrets or revenue-relevant modules without escalation. Review: it does a
specialist first pass and an adversarial verification pass; it never approves or
merges its own work. Test: it finds missing scenarios and drafts fixtures; QA
still owns the gate, because a model declaring its own coverage sufficient is
not a control. Docs and ops: it drafts runbooks and triages logs with
redaction; a human executes anything that changes production."

Land the compressed version: "AI may draft. It may not approve, merge, deploy,
hold inventory, or take payment."

**Q&A likely:** *"You have 15 automated reviewers. Isn't that review theater?"*
→ "It is a first pass that catches the boring half so the human spends
attention on design and risk. If I saw approval rates rise while escaped
defects also rose, I would call that theater and cut the reviewer count."

---

## Slide 6 — Safety, SOX, IP — live demo (4 min)

**Point:** The compliance story is a running control, not a policy paragraph.

**Do not talk over this slide. Run it.**

```bash
bash demo/sox/run-demo.sh
```

**Frame it in two sentences first:** "Two scoping decisions do most of the work.
AI-assisted code gets no exception — it flows through the same change control,
because SOX cares about the change, not the keyboard. And the guest agent is
designed to stay out of SOX scope: it cannot take payment, cannot confirm a
booking, and its holds expire and reverse, so it never touches revenue
recognition."

Then narrate the three acts:

1. **One policy, two enforcement points.** "The control is declared once, and
   it is bound to a Claude deny-list, a git pre-commit hook, and CI. Here is
   the actual line in the hook that calls the guard."
2. **Preventive control.** A commit touching `services/pricing/fare-rules.ts`
   is rejected, naming the file and the rule that matched. "An agent editing a
   revenue module hits exactly this."
3. **Detective control.** Four changes land the way they really do under
   release pressure — one clean, one self-approved, one with no ticket or
   approver, and one revenue-relevant change pushed with `--no-verify`. The
   evidence gate returns NO-GO with four exceptions and a JSON bundle, exiting
   non-zero so it blocks the pipeline.

**The line that lands:** "A client-side hook is bypassable by any human under
pressure, and that is fine — which is why the evidence gate reads the committed
record instead of trusting the developer's machine. Preventive control for the
95% case, detective control for the hotfix at 2am."

**Volunteer the boundaries before anyone asks.** This is the most important 30
seconds in the deck:

- The approver here comes from a git trailer so the demo runs offline. In
  production it comes from the pull-request API — who clicked approve, and when.
- The AI-assisted marker is self-declared disclosure, not detection.
- The usage telemetry is deliberately pseudonymous and metadata-only, so it is
  **not** audit evidence and I would never offer it as such. The SOX system of
  record stays the SCM and CI.
- This proves the same script CI would call, not that CI calls it. Wiring that
  job is a day-30 task.

**IP and data, in one breath:** no training on our code, contractually; secrets
never reach a model because the scan runs before the write; retrieved content is
treated as untrusted input, which is the same reason prompt injection is
handled as a capability boundary rather than a prompt instruction.

**Q&A likely:**
- *"Who is accountable when AI-assisted code causes a restatement?"* → "The
  human who approved it. That never moves. The tooling exists to make sure
  there is always exactly one such name."
- *"Can you detect AI usage rather than trusting a self-declared flag?"* →
  "Only by using editor telemetry, which is pseudonymous by design. I would
  rather have an honest disclosure convention than a surveillance signal that
  fails an attribution test anyway."

---

## Slide 7 — Measurement (3 min)

**Point:** Adoption and value, paired with a stability counter-metric, and no
self-reported speedup.

**Say:** "I will not bring you a slide that says AI made us 20% faster. The
most rigorous study on this — a randomized trial with experienced developers —
found they *felt* about 20% faster while measuring slower. So I measure things
that are hard to flatter: active users per day, share of PRs with an AI first
pass, cost per developer per active day against the vendor's published average,
cost per merged PR as an internal trend with no industry benchmark claimed, and
the rework ratio — real money spent on turns where the engineer had to correct
the AI. That last one is the quality counter-metric, and it is the number I
would watch most."

Then the honesty beat: "One of these is not instrumented yet. The guard hooks
genuinely block, but four of them do not emit telemetry, so the safety panel
correctly renders 'not instrumented' rather than a comforting zero. Wiring that
is a day-30 task. I would rather show you a dashboard that refuses to fake a
number than one that reassures you."

For the guest agent, the gates are different and binary: grounded answer pass
rate, zero hallucinated prices, zero unauthorized tool calls, fallback success
with the model disabled, no oversell under concurrent holds, and every
injection case ignored.

**Q&A likely:** *"How do you prove ROI to a CFO?"* → "Cost per merged PR as a
trend, minus measured rework, against license spend — and I would pair it with
change-fail rate so nobody buys throughput with instability. I would not
annualize a two-week sample and call it savings."

---

## Slide 8 — Worked example: architecture (3 min)

**Point:** A governed commerce orchestration layer, not a chatbot.

**Demo:** `demo/cruise/cruise_demo.py` — `compare` shows deltas as subtraction
on tool output, `ask "tell me about onboard credit"` strips an injected
instruction out of retrieved content. A runnable slice against mock data, not
the production build. Commands and expected output in `docs/PART2-DEMO-MAP.md`.

**Say:** "The feature is an agentic cruise planning assistant. A guest says
'seven nights in the Caribbean in March, family of four, balcony, under five
thousand.' The model interprets that and explains trade-offs. It does not
produce a single number. Search, pricing, availability, comparison deltas, and
holds are deterministic tools behind typed schemas. The model never holds a
database handle or an unrestricted credential."

Walk the boundary sequence, because this is where the architects lean in:
anonymous planning first, so there is no reason to collect identity early;
evidence objects carry the price and availability with a timestamp and a
validity window, so a stale number is visibly stale; authentication happens at
the commitment boundary, not the front door; the session id rotates on
authentication and only safe planning state is copied forward; the hold is
created by the inventory service, atomically and idempotently, only after
explicit guest confirmation; then it hands off to existing checkout.

"Two things it deliberately cannot do: take payment, and confirm a booking.
That is what keeps it out of SOX scope and out of the incident that would end
the program."

**Q&A likely:** *"Why not let it complete the booking? That's the value."* →
"Because the marginal conversion gain is small and the downside is a
mis-booked cruise with a model in the audit path. I would revisit it at day 90
with eval data, not before."

---

## Slide 9 — Worked example: evaluate and operate (2 min)

**Point:** The eval suite is a merge gate, and the failure path is a product
feature.

**Demo:** `cruise_demo.py eval` — 10 golden and 8 red-team cases, non-zero exit
on failure. Then `plan --model off` for the outage path, the three-step `hold`
sequence for the auth gates, and `hold --concurrent 5` on a two-cabin sailing.
Mention that the suite caught a real defect during construction: seed fares made
the hero request unsatisfiable and the run reported NO-GO.

**Say:** "Ten golden cases and eight red-team cases run in CI. The red-team set
is the interesting half: policy content that says 'ignore previous
instructions', a guest asking for hidden discounts, a guest asking the
assistant to complete payment, a guest asking for someone else's booking, an
attempt to hold a cabin without logging in, a stale price that must revalidate
before the hold, two concurrent holds on the same cabin, and a call to a tool
that is not on the authorised list. Those are not
prompt-engineering fixes; each one is a capability boundary or a deterministic
check."

Then operations: every turn emits a trace with tool timings, token counts, cost,
whether the fallback fired, and any safety events. "And when the model is slow
or down, the experience degrades to a deterministic guided planner that calls
the same commerce APIs. The guest can still search, compare, and book. A model
outage is a degraded feature, not an outage."

**Q&A likely:** *"Who owns the golden set?"* → "QA owns it, Product contributes
cases, and it is a merge gate — so a regression is a build failure, not a
retrospective item."

---

## Slide 10 — Enablement and influence (2 min)

**Point:** Adoption is designed as policy and pairing, not encouragement.

**Say:** "Two-speed rollout. Champions pair with skeptics, and the skeptics get
the honest on-ramp: tests, documentation, and review comments for two weeks
before production code. That is not a demotion, it is where the tool is most
reliably good. EMs get the leadership view of the dashboard, not raw token
charts, because the question they actually have is whether the investment is
sticking. Offshore and outsourced teams use the same overlay and the same
briefing format — no second-class governance, or the governance means nothing."

The influence move, stated plainly: "I would not open the EM staff meeting with
a model bake-off. I would open with blocked secrets and measured rework cost.
Those two numbers change the conversation from preference to risk."

**Q&A likely:** *"What about your most senior skeptic who refuses?"* → "I would
give them the review-quality problem to own. Skeptics make excellent owners of
the guardrails, and it converts opposition into authorship."

---

## Slide 11 — Risks and kill criteria (2 min)

**Point:** Name what you would stop, not just what you would start.

**Say:** "Four risks I would flag on day one. Review becoming a rubber stamp —
watched via escaped defects and change-fail rate, not vibes. Cost drift —
capped per session and per team, with alerts. Vendor lock-in — mitigated by the
gateway and by keeping policy in an agent-neutral layer, which is why the same
rules render into three different tools today. And over-reach on the guest
feature, where the pressure will be to let it book."

Kill criteria, said as commitments: "I pause org expansion if change-fail rate
rises, if a secret leaks, or if review quality degrades. I kill or roll back the
guest feature if any eval safety metric fails, if a hold ever oversells, or if
cost per session exceeds the cap without a Product trade-off. And the trade-off
I am explicitly making: slower adoption in the first 30 days in exchange for an
audit trail I can defend. If you want speed without that, I am the wrong
Principal for this."

**Q&A likely:** *"What if leadership overrules you and wants autonomous
booking?"* → "Then I want it behind a separate control review with Audit in the
room, a hard transaction limit, and a documented owner. I would not refuse — I
would make the risk explicit and priced."

---

## Slide 12 — The ask (1 min)

**Point:** Three specific things, then stop talking.

**Say:** "Three asks. A pilot mandate for two teams with capacity protected for
30 days and no OKR penalty. Named time from Security, Legal, and Internal Audit
in the first two weeks, because the SOX walkthrough is the dependency with the
longest lead. And a day-90 decision forum with the authority to scale or kill —
so this ends in a decision rather than drifting into a permanent pilot."

Close on the reusable part: "The transferable asset here is not the cruise
planner. It is the operating model — typed tools, grounded answers, evals as
gates, observability, a deterministic fallback, and human accountability at
exactly the right boundaries."

---

## Cross-cutting Q&A

Answers you should have ready regardless of which slide triggers them.

**"How is this different from just turning on Copilot?"** A floor gives you
autocomplete. This gives you protected paths, evidence, evals, and a
measurement discipline. The second list is what survives an audit.

**"What is your biggest risk of failure?"** Adoption theater — tools installed,
dashboards green, and review quality quietly degrading. That is why the rework
ratio and change-fail rate are on the same slide as adoption.

**"What would you do differently from your last rollout?"** Instrument the
guardrails on day one. I have controls that genuinely block but do not report,
which means I can prove enforcement in a demo and not in a metric. That is
backwards, and it is a day-30 fix in this plan.

**"How do you handle a hallucinated price reaching a guest?"** It cannot, by
construction — commerce values render only from deterministic tool responses,
and the eval suite asserts on that. If it did happen, it would be a P1, a
rollback via the flag, and a new red-team case before the fix ships.

**"Who does this make redundant?"** Nobody. It moves review effort from
mechanical checks to design and risk, and it makes offshore briefs sharper. If I
thought it replaced engineers I would say so.
