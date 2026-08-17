# Path consolidation (Windows demo layout)

Code defects D1–D6 are closed in this repo. The remaining P1 risk is
**two divergent local copies** on a Windows machine:

| Path | Role | Status |
|------|------|--------|
| `C:\codebase\titan\titan` | Nested git clone with T12 + render gates | **Authoritative — keep / flatten** |
| `C:\codebase\generic` | Pre-T12 extraction tree | **Stale — retire** |
| `C:\POC\RCG` | POC demo workspace (receives deploy) | **Deploy target only** |

Do not treat `C:\codebase\titan` (the nest wrapper) or `generic` as the
source of truth. `poc-deploy-rcg.sh` will refuse to deploy into a nest
wrapper that has no POC markers; set `RCG_ROOT` explicitly.

## 1. Refresh local JSON baselines (cosmetic Windows CRLF)

If the snapshot gate is red locally but CI is green:

```bash
git -C /c/codebase/titan/titan checkout -- harness/tests/snapshots
cd /c/codebase/titan/titan/harness
bash scripts/verify-claude-snapshot.sh
```

## 2. Flatten `titan\titan` → `C:\codebase\titan`

Run in Git Bash **after** committing/pushing any work in the nested clone.
This replaces the wrapper directory with the real repo contents.

```bash
# Stop anything using the tree, then:
NEST=/c/codebase/titan/titan
WRAP=/c/codebase/titan
BACKUP=/c/codebase/titan-nest-backup-$(date +%Y%m%d)

# Safety: nested path must be a git repo with our harness
test -d "$NEST/.git" && test -f "$NEST/harness/scripts/titan-render.py"

# Move wrapper aside, promote nested repo
mv "$WRAP" "$BACKUP"
mv "$BACKUP/titan" "$WRAP"
# Optional: remove backup once you confirm gates pass
# rm -rf "$BACKUP"

cd /c/codebase/titan
git status
bash scripts/lint-generic.sh
(cd harness && bash scripts/verify-claude-snapshot.sh)
```

After flatten, the single source path is `C:\codebase\titan`.

## 3. Retire `C:\codebase\generic`

```bash
# Confirm it is the old tree (no T12 adapters)
ls /c/codebase/generic/harness/adapters 2>/dev/null || echo "no adapters/ (expected for stale tree)"

# Rename first (soft delete); remove after a successful demo week
mv /c/codebase/generic /c/codebase/generic.RETIRED-$(date +%Y%m%d)
# rm -rf /c/codebase/generic.RETIRED-*
```

Update any local planning docs that still say `C:\codebase\generic`
(`IMPLEMENTATION_PLAN.md`, `T12_TITAN_AGENT_NEUTRAL.md`, plan files) to
`C:\codebase\titan`.

## 4. Deploy to `C:\POC\RCG` (not the codebase nest)

```bash
export RCG_ROOT=/c/POC/RCG
bash /c/codebase/titan/harness/scripts/poc-deploy-rcg.sh
# or, before flatten:
# bash /c/codebase/titan/titan/harness/scripts/poc-deploy-rcg.sh
```

`poc-deploy-rcg.sh` also auto-detects `/c/POC/RCG` when that directory
already has POC markers (`CLAUDE.md`, `AGENTS.md`, `.claude/`, or
`titan.config.json`). It will **not** treat a bare `...\titan` wrapper as
the deploy root.

## 5. Mac / this workspace

Layout `Interview-Prep/RCG/titan` already matches the preferred shape
(POC parent + `titan/` child). No flatten needed here; deploy with:

```bash
# from anywhere
RCG_ROOT=/Users/manojpammina/Desktop/Interview-Prep/RCG \
  bash titan/harness/scripts/poc-deploy-rcg.sh
```
