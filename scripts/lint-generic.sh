#!/usr/bin/env bash
# lint-generic.sh — Titan extraction Definition of Done (plan Section G, row 15).
#
# Fails (non-zero exit) if any company-identity residue from the reference
# implementation this harness was extracted from is found anywhere under
# this titan repo root (authoritative path: C:\codebase\titan after flatten;
# never scan the retired C:\codebase\generic tree), with two intentional exceptions:
#   - fixtures/**   the real-reference-data fidelity oracle (gitignored, never
#                    shipped — see fixtures/titan.config.ds.json's own
#                    _description)
#   - harness/.render/**  gitignored render-pipeline build output (titan-render.py
#                    / deploy-harness.sh scratch dirs) — never shipped, and
#                    legitimately contains every banned string when the DS
#                    fixture was last rendered through it for testing
# This script's OWN source is also excluded from the scan below — it has to
# name the banned patterns literally to check for them.
#
# Usage:
#   bash scripts/lint-generic.sh            # scan the whole tree
#   bash scripts/lint-generic.sh --verbose   # also print matched lines
#
# Exit codes: 0 = clean, 1 = one or more hits (see the printed report).

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

VERBOSE=0
[[ "${1:-}" == "--verbose" ]] && VERBOSE=1

FAIL=0

# ── Scope ────────────────────────────────────────────────────────────────
EXCLUDE_DIRS=(--exclude-dir=fixtures --exclude-dir=.render --exclude-dir=node_modules --exclude-dir=__pycache__ --exclude-dir=.git --exclude-dir=dist --exclude-dir=dist-electron --exclude-dir=release --exclude=lint-generic.sh)

report() {
  local label="$1"; shift
  local hits
  hits="$(grep -rniIE "${EXCLUDE_DIRS[@]}" "$@" . 2>/dev/null)"
  if [[ -n "$hits" ]]; then
    FAIL=1
    local count
    count="$(printf '%s\n' "$hits" | wc -l)"
    echo "FAIL  $label  ($count hit(s))"
    if [[ $VERBOSE -eq 1 ]]; then
      printf '%s\n' "$hits" | sed 's/^/        /'
    fi
  else
    echo "ok    $label"
  fi
}

echo "== Titan lint-generic — scanning $ROOT (excluding fixtures/**) =="
echo ""

# ── 1. Literal company-identity strings ─────────────────────────────────
report "Dentsply / dentsply"          -E "dentsply"
report "DS-AEM"                       -E "DS-AEM"
report "DS Ecommerce"                 -F "DS Ecommerce"
report "Slingshot / SLINGSHOT"        -iE "slingshot"
report "SLINGSHOT_ env prefix"        -E "SLINGSHOT_"
report "dentsplysironait (Jira site)" -F "dentsplysironait"
report "staging.dentsplysirona"       -E "staging\.dentsplysirona"

# Three real names (spelling taken verbatim from fixtures/titan.config.ds.json
# contacts.people — the only place they are allowed to appear).
report "Manoj Pammina"  -F "Manoj Pammina"
report "Bala Murugan"   -F "Bala Murugan"
report "Casey Regan"    -F "Casey Regan"

# ── 2. Bare "DS" outside the reviewed allowlist ─────────────────────────
# \bDS\b also matches DSO (dental service organisation — a real, retained
# domain term e.g. in designer-mode.md / qa-env.json) and a handful of other
# legitimate non-brand uses reviewed during the Phase 7 pass below. Every
# other bare "DS" found during that pass was a genuine org-identity leak and
# was fixed at the source — this allowlist is intentionally short.
#
# Allowlist (regex alternatives OK to immediately follow "DS"):
#   DSO           - dental service organisation (retained domain term)
#   DS_STORE      - macOS .DS_Store artifact, if ever referenced literally
ALLOW_RE='DSO|DS_STORE'
BARE_DS_HITS="$(grep -rnoIE "${EXCLUDE_DIRS[@]}" '\bDS\b[A-Za-z_]*' . 2>/dev/null | grep -viE "$ALLOW_RE")"
if [[ -n "$BARE_DS_HITS" ]]; then
  FAIL=1
  count="$(printf '%s\n' "$BARE_DS_HITS" | wc -l)"
  echo "FAIL  bare \\bDS\\b outside allowlist  ($count hit(s))"
  if [[ $VERBOSE -eq 1 ]]; then
    printf '%s\n' "$BARE_DS_HITS" | sed 's/^/        /'
  fi
else
  echo "ok    bare \\bDS\\b outside allowlist"
fi

# ── 3. ds- prefixed filenames under the app/asset trees ─────────────────
DS_FILES="$(find src dashboard electron assets -iname 'ds-*' 2>/dev/null)"
if [[ -n "$DS_FILES" ]]; then
  FAIL=1
  count="$(printf '%s\n' "$DS_FILES" | wc -l)"
  echo "FAIL  ds-* filenames in src/dashboard/electron/assets  ($count hit(s))"
  if [[ $VERBOSE -eq 1 ]]; then
    printf '%s\n' "$DS_FILES" | sed 's/^/        /'
  fi
else
  echo "ok    ds-* filenames in src/dashboard/electron/assets"
fi

# ── 4. Leftover ds- prefixed Tailwind/className tokens ──────────────────
# The de-branding pass (Phase 6 step 23 + Phase 7) renamed the palette keys
# themselves (ds-blue/ds-gray/ds-success/ds-warning/ds-danger/ds-white ->
# titan-*) everywhere they were used as a className. This checks the rename
# actually stuck, repo-wide, rather than re-trusting that one-time sweep.
CLASS_HITS="$(grep -rnoIE "${EXCLUDE_DIRS[@]}" --include='*.ts' --include='*.tsx' --include='*.html' --include='*.css' \
  '\bbg-ds-|\btext-ds-|\bborder-ds-|\bds-(blue|gray|success|warning|danger|white)\.' src dashboard electron 2>/dev/null)"
if [[ -n "$CLASS_HITS" ]]; then
  FAIL=1
  count="$(printf '%s\n' "$CLASS_HITS" | wc -l)"
  echo "FAIL  leftover ds-* className tokens  ($count hit(s))"
  if [[ $VERBOSE -eq 1 ]]; then
    printf '%s\n' "$CLASS_HITS" | sed 's/^/        /'
  fi
else
  echo "ok    leftover ds-* className tokens"
fi

# ── 5. Known DS brand hex literals ───────────────────────────────────────
# #0F62FE was the one DS-brand hex value called out by name during the
# Phase 6/7 palette audit (dashboard/tailwind.config.ts's old contrast
# comment against it). Any literal reintroduction of it is a brand leak,
# not a coincidence — it is not a common neutral placeholder value.
HEX_HITS="$(grep -rniIE "${EXCLUDE_DIRS[@]}" "0f62fe" src dashboard electron assets 2>/dev/null)"
if [[ -n "$HEX_HITS" ]]; then
  FAIL=1
  count="$(printf '%s\n' "$HEX_HITS" | wc -l)"
  echo "FAIL  known DS brand hex literal (#0F62FE)  ($count hit(s))"
  if [[ $VERBOSE -eq 1 ]]; then
    printf '%s\n' "$HEX_HITS" | sed 's/^/        /'
  fi
else
  echo "ok    known DS brand hex literal (#0F62FE)"
fi

echo ""
if [[ $FAIL -ne 0 ]]; then
  echo "RESULT: FAIL — one or more checks above found a hit. Re-run with --verbose to see lines."
  exit 1
else
  echo "RESULT: PASS — zero hits outside fixtures/**."
  exit 0
fi
