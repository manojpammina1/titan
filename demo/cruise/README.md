# Cruise planning assistant — runnable demo slice

A stdlib-only Python slice of the Part 2 worked example. It exists to make one
architectural claim checkable on stage instead of asserted on a slide:

> The model interprets intent. Deterministic tools own every commerce value. The
> commitment boundary is enforced by capability, not by prompt wording.

Nothing here calls a model. The model layer is a deterministic mock, which is
also the production failure path (`LLM_PROVIDER=mock`) described in
`docs/CRUISE_AGENT_DEVELOPMENT_PLAN.md`. Ships, fares, and policies are
fictional. There is no real inventory, no guest data, and no payment path.

## Commands

```bash
cd <repo root>

# Hero path — a planning turn end to end
python3 demo/cruise/cruise_demo.py plan \
  "7-night Caribbean cruise in March for a family of four, balcony cabin, under \$5,000"

# Same request with the model disabled — the fallback planner still answers
python3 demo/cruise/cruise_demo.py plan --model off \
  "7-night Caribbean cruise in March for a family of four, balcony, under \$5,000"

# Grounded policy answer, with an injected instruction stripped from content
python3 demo/cruise/cruise_demo.py ask "tell me about onboard credit"

# Refusal — no payment capability exists to satisfy this
python3 demo/cruise/cruise_demo.py ask "just charge my card and complete the booking"

# Commitment boundary, one gate at a time
python3 demo/cruise/cruise_demo.py hold --sailing CB-7N-MAR-01
python3 demo/cruise/cruise_demo.py hold --sailing CB-7N-MAR-01 --auth
python3 demo/cruise/cruise_demo.py hold --sailing CB-7N-MAR-01 --auth --confirm

# Retry safety and inventory safety
python3 demo/cruise/cruise_demo.py hold --sailing CB-7N-MAR-01 --auth --confirm --repeat 2
python3 demo/cruise/cruise_demo.py hold --sailing CB-7N-MAR-02 --concurrent 5

# The merge gate: 10 golden + 8 red-team cases, non-zero exit on any failure
python3 demo/cruise/cruise_demo.py eval
```

## What each behaviour proves

| Observable | Claim it supports |
|---|---|
| Every row carries `pricing_tool` and a `valid_until` | No commerce value originates in the model |
| Narrative contains no numbers (asserted in eval) | Prose and figures are separated by construction |
| `--model off` returns the same options | Guest-facing degradation, not an outage |
| `ask onboard credit` strips the embedded instruction | Retrieved content is data, never a directive |
| Payment, hidden-rate, other-guest requests refused | Capability boundary, not a politeness rule |
| Hold refused without auth, then without confirmation | Two independent gates before any commitment |
| `--repeat 2` reuses the same hold id | Idempotency key, safe under retry |
| `--concurrent 5` grants 2 of 5 on a 2-cabin sailing | Inventory cannot be oversold by an agent |
| Unauthorised tool call raises from the registry | Allow-list enforced in code, not in the prompt |

## Eval as a gate

`eval` exits non-zero when any case fails. That exit code is the point: in the
plan it is a required CI check, so a grounding or refusal regression blocks the
merge the same way a failing unit test does.

The suite caught a real defect during construction. Initial seed fares made the
hero request unsatisfiable, so the flagship case failed and the run reported
NO-GO. The fares were data, not code — which is exactly the class of quiet
regression an eval suite is for.

## Boundaries — say these out loud if asked

- Mock model, mock data, in-process state. A dict stands in for the inventory
  service; production needs a unique index and real hold expiry.
- The injection defence here strips known markers. Production layers input
  filtering, content provenance, and output validation; marker-stripping alone
  is not a defence.
- Refusals are keyword-triggered in this slice. Production relies on the tool
  registry — there is no payment tool to call — with classification as a
  secondary layer.

## Files

| Path | Role |
|---|---|
| `cruise_demo.py` | Whole demo: tools, mock model layer, gates, eval suite |
| `README.md` | This file |

Full design, API surface, and production controls:
`docs/CRUISE_AGENT_DEVELOPMENT_PLAN.md`.
