#!/usr/bin/env bash
# run-demo.sh — three-act SOX control demo, safe to run live in an interview.
#
# Everything runs against a throwaway git repo in a temp directory. The real
# repo is never touched. The hook and guard are the shipped Titan files, copied
# unmodified, so the block you see is the control firing rather than a mock.
#
#   Act 1  the control is declared once and bound to enforcement
#   Act 2  preventive control — a real `git commit` on a revenue path is blocked
#   Act 3  detective control — evidence bundle catches what bypassed the hook
#
# Usage:
#   bash demo/sox/run-demo.sh          # run and clean up
#   bash demo/sox/run-demo.sh --keep   # leave the temp repo for inspection
#
# Set SOX_DEMO_DIR to place the throwaway repo somewhere other than $TMPDIR
# (needed only where /tmp is not writable, e.g. a sandboxed agent shell).
set -uo pipefail

DEMO_DIR="$(cd "$(dirname "$0")" && pwd)"
TITAN_REPO="$(cd "$DEMO_DIR/../.." && pwd)"
HARNESS="$TITAN_REPO/harness"

KEEP=0
[ "${1:-}" = "--keep" ] && KEEP=1

# Fictional demo identity — no real person, no real email.
AUTHOR_NAME="Dana Reyes"
AUTHOR_EMAIL="dana.reyes@example.com"
APPROVER="Owen Marsh <owen.marsh@example.com>"

rule() { printf '%s\n' "------------------------------------------------------------------"; }
act()  { printf '\n=== %s ===\n\n' "$1"; }

for f in "$HARNESS/hooks/credential-scan.py" \
         "$HARNESS/scripts/path-guard.py" \
         "$HARNESS/scripts/sox-evidence.py" \
         "$HARNESS/adapters/codex/hooks/pre-commit" \
         "$DEMO_DIR/protected-paths.demo.json"; do
  [ -f "$f" ] || { echo "FAIL: missing $f" >&2; exit 1; }
done
command -v python >/dev/null 2>&1 || { echo "FAIL: 'python' not on PATH (the shipped pre-commit hook calls 'python')" >&2; exit 1; }

WORK="$(mktemp -d "${SOX_DEMO_DIR:-${TMPDIR:-/tmp}}/sox-demo.XXXXXX")" || {
  echo "FAIL: could not create a temp directory. Set SOX_DEMO_DIR to a writable path." >&2
  exit 1
}
cleanup() {
  if [ "$KEEP" -eq 1 ]; then
    printf '\nTemp repo kept at: %s\n' "$WORK"
  else
    rm -rf "$WORK"
  fi
}
trap cleanup EXIT

act "Act 1 — one policy, two enforcement points"
echo "Control declared once in governance/controls.yaml:"
rule
sed -n '/- id: protected-paths/,/from: path-guard/p' "$HARNESS/governance/controls.yaml"
rule
echo
echo "Bound to a real git hook (harness/adapters/codex/hooks/pre-commit):"
rule
grep -n 'path-guard.py' "$HARNESS/adapters/codex/hooks/pre-commit"
rule
echo
echo "Revenue-relevant globs the guard will enforce in this demo:"
python - "$DEMO_DIR/protected-paths.demo.json" <<'PY'
import json, sys
entry = next(p for p in json.load(open(sys.argv[1]))["paths"] if p["id"] == "revenue-relevant")
for glob in entry["globs"]:
    print(f"  {glob}")
print(f"  owners: {', '.join(entry['owners'])}")
PY

# ---- seed a throwaway repo wired with the real harness files ----------------
cd "$WORK" || exit 1
git init -q .

# Safety interlock. If `git init` did not produce a usable repo here, every git
# command below would silently fall through to an enclosing repository and
# commit demo junk into it. Refuse unless git resolves to exactly this
# directory. Compared with `pwd -P` so macOS /private symlinks do not trip it.
DEMO_TOP="$(git rev-parse --show-toplevel 2>/dev/null || true)"
DEMO_TOP_REAL=""
[ -n "$DEMO_TOP" ] && DEMO_TOP_REAL="$(cd "$DEMO_TOP" 2>/dev/null && pwd -P)"
if [ "$DEMO_TOP_REAL" != "$(pwd -P)" ]; then
  echo "FAIL: git resolved to '${DEMO_TOP_REAL:-nothing}' instead of the demo repo." >&2
  echo "      SOX_DEMO_DIR must be a writable path that is NOT inside a git repository." >&2
  exit 1
fi

git config user.name  "$AUTHOR_NAME"
git config user.email "$AUTHOR_EMAIL"
git config commit.gpgsign false

mkdir -p .claude/hooks .claude/scripts .claude/data apps/web services/tax services/pricing
cp "$HARNESS/hooks/credential-scan.py" .claude/hooks/
[ -f "$HARNESS/hooks/titan_config.py" ] && cp "$HARNESS/hooks/titan_config.py" .claude/hooks/
cp "$HARNESS/scripts/path-guard.py" .claude/scripts/
cp "$DEMO_DIR/protected-paths.demo.json" .claude/data/protected-paths.json
cp "$HARNESS/adapters/codex/hooks/pre-commit" .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# The harness overlay is wiring, not demo content — keep it untracked so the
# commits below contain only application files.
printf '.claude/\nsox-evidence.json\n' > .gitignore

echo "cruise commerce demo repo" > README.md
git add -A
git commit -q -m "[CRUISE-100] Seed demo repo

Reviewed-by: $APPROVER
" || { echo "FAIL: seed commit was rejected — demo cannot continue" >&2; exit 1; }
BASE="$(git rev-parse HEAD)" || exit 1

act "Act 2 — preventive control: the commit is blocked"
echo "A developer (or an agent acting as one) edits a revenue-relevant module:"
echo "  services/pricing/fare-rules.ts"
echo
echo 'export const baseFare = 1899;' > services/pricing/fare-rules.ts
git add -A
git commit -m "[CRUISE-103] Adjust base fare rules" 2>&1 | sed 's/^/  | /'
STATUS=${PIPESTATUS[0]}
echo
case "$STATUS" in
  1)
    echo "RESULT: commit rejected by the shipped pre-commit hook (exit 1)."
    echo "        The same path-guard.py runs in CI, so this is not a local-only opinion."
    ;;
  0)
    echo "RESULT: UNEXPECTED — commit succeeded. Check protected-paths.demo.json globs."
    exit 1
    ;;
  *)
    echo "RESULT: ERROR — git failed with exit $STATUS for a reason other than the policy."
    exit 1
    ;;
esac
git reset -q
rm -f services/pricing/fare-rules.ts

act "Act 3 — detective control: evidence catches what bypassed the hook"
echo "Four changes now land the way they really do under release pressure."
echo

# A — fully compliant, AI-assisted and declared.
printf 'export const compareFares = () => {};\n' > apps/web/compare.ts
git add -A
git commit -q -m "[CRUISE-101] Add fare comparison helper

Reviewed-by: $APPROVER
AI-Assisted: yes (cursor, dev-mode)
" || { echo "FAIL: compliant commit was unexpectedly rejected" >&2; exit 1; }
echo "  1. [CRUISE-101] ticketed, independently approved, AI use declared"

# B — self-approved: author is also the reviewer.
printf 'export const seed = [];\n' > apps/web/seed.ts
git add -A
git commit -q -m "[CRUISE-102] Refresh sailing seed data

Reviewed-by: $AUTHOR_NAME <$AUTHOR_EMAIL>
AI-Assisted: yes (claude, dev-mode)
" || { echo "FAIL: self-approved commit was rejected for the wrong reason" >&2; exit 1; }
echo "  2. [CRUISE-102] approved by its own author"

# C — no ticket, no approver.
printf 'export const patch = true;\n' > apps/web/patch.ts
git add -A
git commit -q -m "Quick fix so the build goes green" \
  || { echo "FAIL: untracked-policy commit was rejected for the wrong reason" >&2; exit 1; }
echo "  3. no ticket, no approver of record"

# D — revenue path landed with --no-verify, the classic hotfix bypass.
printf 'export const roundHalfUp = (n: number) => n;\n' > services/tax/rounding.ts
git add -A
git commit -q --no-verify -m "[CRUISE-104] Correct tax rounding for onboard credits

Reviewed-by: $APPROVER
AI-Assisted: yes (cursor, dev-mode)
"
echo "  4. [CRUISE-104] revenue-relevant path, committed with --no-verify"

echo
echo "Server-side evidence for the release range:"
rule
python "$HARNESS/scripts/sox-evidence.py" \
  --root "$WORK" \
  --range "$BASE..HEAD" \
  --json "$WORK/sox-evidence.json"
GATE=$?
rule
echo
echo "Gate exit code: $GATE  (non-zero blocks the release pipeline)"
echo "Machine-readable bundle written for the auditor: sox-evidence.json"
echo
echo "The point: a client-side hook is bypassable by a human under pressure."
echo "The evidence gate is not, because it reads the committed record itself."
