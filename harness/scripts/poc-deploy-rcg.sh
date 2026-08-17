#!/usr/bin/env bash
# poc-deploy-rcg.sh — deploy rendered Titan payloads to the RCG POC root (T12.6).
#
# Harness is ALWAYS resolved from this script's location (never guessed), so a
# double-nested checkout like C:\codebase\titan\titan cannot silently point
# HARNESS at the wrong tree.
#
# Deploy root (RCG_ROOT) resolution — in order:
#   1. $RCG_ROOT if set (recommended on Windows: RCG_ROOT=/c/POC/RCG)
#   2. Parent of the titan repo, ONLY if it looks like a real POC workspace
#      (has CLAUDE.md / AGENTS.md / .claude / titan.config.json). A bare nest
#      wrapper that only contains titan/ is rejected — that was the bug that
#      deployed into C:\codebase\titan instead of C:\POC\RCG.
#   3. Well-known demo path /c/POC/RCG or C:/POC/RCG if present and marked.
#   4. Titan repo root itself, ONLY if it already has POC markers.
#   5. Otherwise exit 1 with instructions.
set -euo pipefail

HARNESS="$(cd "$(dirname "$0")/.." && pwd)"
TITAN_REPO="$(cd "$HARNESS/.." && pwd)"

is_poc_root() {
  local d="$1"
  [ -n "$d" ] && [ -d "$d" ] || return 1
  [ -f "$d/titan.config.json" ] || [ -f "$d/CLAUDE.md" ] || \
    [ -f "$d/AGENTS.md" ] || [ -d "$d/.claude" ]
}

resolve_existing() {
  local cand="$1"
  [ -n "$cand" ] && [ -d "$cand" ] || return 1
  (cd "$cand" && pwd)
}

RCG_ROOT_RESOLVED=""
if [ -n "${RCG_ROOT:-}" ]; then
  RCG_ROOT_RESOLVED="$(resolve_existing "$RCG_ROOT")" || {
    echo "FAIL: RCG_ROOT=$RCG_ROOT is not a directory" >&2
    exit 1
  }
else
  PARENT="$(cd "$TITAN_REPO/.." && pwd)"
  if is_poc_root "$PARENT"; then
    RCG_ROOT_RESOLVED="$PARENT"
  else
    for cand in "/c/POC/RCG" "C:/POC/RCG" "/mnt/c/POC/RCG"; do
      if resolved="$(resolve_existing "$cand")" && is_poc_root "$resolved"; then
        RCG_ROOT_RESOLVED="$resolved"
        break
      fi
    done
  fi
  if [ -z "$RCG_ROOT_RESOLVED" ] && is_poc_root "$TITAN_REPO"; then
    RCG_ROOT_RESOLVED="$TITAN_REPO"
  fi
fi

if [ -z "$RCG_ROOT_RESOLVED" ]; then
  cat >&2 <<EOF
FAIL: cannot determine RCG POC deploy root.

  Titan source : $TITAN_REPO
  Parent       : $(cd "$TITAN_REPO/.." && pwd)
  Parent looks like a nest wrapper (has titan/ but no POC markers), so it was
  NOT chosen. That prevents deploying into C:\\codebase\\titan by accident.

Set the POC workspace explicitly, then re-run:

  export RCG_ROOT=/c/POC/RCG          # Git Bash / MSYS
  # or:  set RCG_ROOT=C:\\POC\\RCG    # cmd.exe
  bash $HARNESS/scripts/poc-deploy-rcg.sh

A valid RCG_ROOT contains at least one of: titan.config.json, CLAUDE.md,
AGENTS.md, or .claude/
EOF
  exit 1
fi

RCG_ROOT="$RCG_ROOT_RESOLVED"

CONFIG="${1:-}"
if [ -z "$CONFIG" ]; then
  if [ -f "$RCG_ROOT/titan.config.json" ]; then
    CONFIG="$RCG_ROOT/titan.config.json"
  elif [ -f "$TITAN_REPO/titan.config.json" ]; then
    CONFIG="$TITAN_REPO/titan.config.json"
  else
    CONFIG="$HARNESS/titan.config.example.json"
  fi
fi
OUT="$RCG_ROOT/.titan-out"

echo "== POC deploy =="
echo "  RCG_ROOT=$RCG_ROOT"
echo "  HARNESS=$HARNESS"
echo "  CONFIG=$CONFIG"

python3 "$HARNESS/scripts/titan-render.py" --config "$CONFIG" --target all --out "$OUT"

mkdir -p "$RCG_ROOT/.claude"/{hooks,scripts,data,commands,subagents}
cp -f "$OUT/CLAUDE.md" "$RCG_ROOT/CLAUDE.md"
cp -f "$OUT/AGENTS.md" "$RCG_ROOT/AGENTS.md"
cp -f "$OUT/governance-manifest.json" "$RCG_ROOT/governance-manifest.json"
cp -f "$OUT/settings.json" "$RCG_ROOT/.claude/settings.json"
cp -f "$OUT/data/"*.json "$RCG_ROOT/.claude/data/"
cp -f "$CONFIG" "$RCG_ROOT/.claude/titan.config.json"
cp -rf "$OUT/governance" "$RCG_ROOT/governance"
cp -rf "$OUT/.codex" "$RCG_ROOT/.codex"
mkdir -p "$RCG_ROOT/.cursor"
if cp -rf "$OUT/cursor-pack/"* "$RCG_ROOT/.cursor/" 2>/dev/null; then
  echo "  cursor-pack -> .cursor/"
else
  cp -rf "$OUT/cursor-pack" "$RCG_ROOT/cursor-pack"
  echo "  NOTE: copied cursor-pack/ (rename to .cursor/ if needed)"
fi
mkdir -p "$RCG_ROOT/.github/workflows"
cp -f "$OUT/.github/workflows/agent-governance.yml" "$RCG_ROOT/.github/workflows/"
cp -rf "$HARNESS/hooks/"*.py "$RCG_ROOT/.claude/hooks/"
cp -f "$HARNESS/scripts/path-guard.py" "$RCG_ROOT/.claude/scripts/"
cp -rf "$HARNESS/commands" "$RCG_ROOT/.claude/"
cp -rf "$HARNESS/subagents" "$RCG_ROOT/.claude/"
cp -f "$HARNESS/.mcp.json" "$RCG_ROOT/.mcp.json" 2>/dev/null || true
chmod +x "$RCG_ROOT/.codex/hooks/pre-commit" "$RCG_ROOT/.cursor/hooks/pre-tool-guard.sh" 2>/dev/null || true

if [ -d "$RCG_ROOT/.git" ]; then
  mkdir -p "$RCG_ROOT/.git/hooks"
  HOOK_DST="$RCG_ROOT/.git/hooks/pre-commit"
  HOOK_SRC="$RCG_ROOT/.codex/hooks/pre-commit"
  if [ -f "$HOOK_SRC" ]; then
    cp -f "$HOOK_SRC" "$HOOK_DST"
    chmod +x "$HOOK_DST"
    echo "  git pre-commit -> $HOOK_DST"
  else
    echo "  WARNING: $HOOK_SRC not found — pre-commit not installed" >&2
  fi
else
  echo "  NOTE: no .git/ — run 'git init' in $RCG_ROOT then re-run to install pre-commit"
fi

echo "Deployed. Run demo checks:"
echo "  python3 $RCG_ROOT/.claude/hooks/credential-scan.py --scan-file <file>"
echo "  node $RCG_ROOT/.codex/review.mjs"
