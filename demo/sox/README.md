# SOX control demo — 90 seconds, live

A runnable answer to "how do you keep AI-assisted development SOX-compliant?"
Nothing is mocked: the block comes from the shipped `pre-commit` hook calling
the shipped `path-guard.py`, and the evidence comes from parsing the real git
record.

```bash
bash demo/sox/run-demo.sh          # run and clean up
bash demo/sox/run-demo.sh --keep   # leave the temp repo to poke at
```

Everything happens in a throwaway repo under `$TMPDIR`. Your real repos are
never touched. Re-runnable as many times as you like, offline, no network, no
model call.

Set `SOX_DEMO_DIR` only if `/tmp` is not writable, and point it somewhere
**outside any git repository**. The script asserts that git resolves to the
throwaway repo and aborts otherwise — without that interlock, a failed
`git init` would let every commit below fall through into the enclosing repo.

## What each act proves

**Act 1 — one policy, two enforcement points.** The `protected-paths` control is
declared once in `governance/controls.yaml` and bound to a Claude deny-list, a
git pre-commit hook, and CI. Point at the `path-guard.py` line in the hook: the
policy is not prose in a wiki, it is wired.

**Act 2 — preventive control.** A change to `services/pricing/fare-rules.ts` is
staged and `git commit` is rejected with the offending path and the entry id
that matched. This is the control an agent hits too — an assistant editing a
revenue-relevant module cannot land it.

**Act 3 — detective control.** Four changes then land the way they really do
under release pressure: one fully compliant, one self-approved, one with no
ticket or approver, and one revenue-relevant change pushed through with
`--no-verify`. `sox-evidence.py` reads the committed record and returns a
NO-GO with four exceptions and a JSON bundle, exiting non-zero so it gates the
pipeline.

## The line that lands

> A client-side hook is bypassable by any human under pressure, and that is
> fine — that is why the evidence gate reads the committed record instead of
> trusting the developer's machine. Preventive control for the 95% case,
> detective control for the hotfix at 2am.

## Exception codes

| Code | Meaning |
|---|---|
| `SOX-01` | Change is not traceable to an authorized request (no ticket id) |
| `SOX-02` | No approver of record (missing `Reviewed-by` trailer) |
| `SOX-03` | Segregation of duties: the author approved their own change |
| `SOX-04` | Revenue-relevant path changed with no escalation approval reference |

Evidence is derived from git trailers, so it cannot drift from the commit:

```
[CRUISE-101] Add fare comparison helper

Reviewed-by: Owen Marsh <owen.marsh@example.com>
AI-Assisted: yes (cursor, dev-mode)
Escalation-Ref: SEC-2026-014
```

## Be honest about the boundaries

State these before anyone asks — volunteering them is the point of the demo.

- **Trailers are a stand-in for the SCM's approval record.** In production the
  approver comes from the pull-request API (who clicked approve, when), not
  from a line a developer typed. The demo uses trailers so it runs offline.
- **`AI-Assisted` is self-declared.** It is a disclosure convention, not
  detection. Detection would need editor telemetry that is deliberately
  pseudonymous, which is the wrong source for an audit trail.
- **Titan telemetry is not audit evidence.** It is metadata-only and hashed by
  design. The SOX system of record is the SCM plus CI, with their retention.
- **The demo protected-paths file is a fixture** with fictional owners. Real
  globs and owners live in `titan.config.json` and are rendered from there.
- **This demo does not prove the guard runs in CI.** It proves the same script
  is the one CI would call. Wiring the CI job is a day-30 task.

## Files involved

| File | Role |
|---|---|
| `demo/sox/run-demo.sh` | The three-act driver |
| `demo/sox/protected-paths.demo.json` | Fixture — revenue-relevant globs, fictional owners |
| `harness/scripts/sox-evidence.py` | Evidence bundle generator and CI gate |
| `harness/scripts/path-guard.py` | Preventive guard (shipped, unmodified) |
| `harness/adapters/codex/hooks/pre-commit` | The hook that calls it (shipped, unmodified) |
| `harness/governance/controls.yaml` | Where the control is declared once |

`sox-evidence.py` is not demo-only. Run it against any range:

```bash
python3 harness/scripts/sox-evidence.py \
  --range origin/release/R2026-05..origin/release/R2026-06 \
  --json bundle.json
```
