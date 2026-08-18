# Part 2 presentation deck

Visual slide deck for the RCG Principal Engineer case study. **Screenshots only
on slides** — speaker notes live separately.

## Files

| File | Purpose |
|---|---|
| `Part2-Agentic-Development.pptx` | **PowerPoint deck** — light ocean theme, open in Keynote/PowerPoint |
| `index.html` | Browser presentation (← → navigate, F fullscreen) |
| `screenshots/` | PNG captures — terminal output + Titan dashboard mock |
| `captures/` | Raw text output used to generate screenshots |
| `build-deck.py` | Regenerate deck after demo or code changes |

## Open the deck

**PowerPoint (recommended):**
```bash
open docs/part2-deck/Part2-Agentic-Development.pptx
```

**Browser (matches PPT — 13 slides):**
```bash
open docs/part2-deck/index.html
# or serve locally:
python3 -m http.server 8765 --directory docs/part2-deck
```

## Speaker notes

`docs/PART2-SPEAKER-NOTES.md` — what to say, Q&A, timing. Keep this on a
second screen or printed; it is **not** embedded in the HTML deck.

## Regenerate

**PowerPoint:**
```bash
docs/part2-deck/.venv/bin/python docs/part2-deck/build-pptx.py
```

**Screenshots + HTML:**
```

This re-runs all demo commands, renders terminal PNGs, and rebuilds `index.html`.

## What's in the screenshots

| Slide | Screenshot source |
|---|---|
| 1 | `demo/cruise/cruise_demo.py plan` — hero path |
| 2 | `credential-scan.py --scan-stdin` block |
| 3 | `show-enforcement-matrix.py` — 3 agents |
| 4 | Roadmap graphic + `deploy-harness.sh` tail |
| 5 | `answer-cache.py` with `?gov` |
| 6 | `demo/sox/run-demo.sh` evidence table |
| 7 | Titan safety panel mock + `vitest run` |
| 8 | cruise `compare` + `ask` (injection stripped) |
| 9 | cruise `eval` + concurrent hold |
| 10 | `sox-evidence.py` on this repo |
| 11 | refusal + gate exit code |
| 12 | Three asks (content slide) |

## Export to PowerPoint / PDF

1. Open `index.html` in Chrome fullscreen and screenshot each slide, or
2. Print to PDF from Chrome (one slide per page — may need print CSS tweak), or
3. Import PNGs from `screenshots/` into your preferred slide tool.
