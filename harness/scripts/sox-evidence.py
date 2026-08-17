#!/usr/bin/env python3
"""SOX change-evidence bundle for a git range — the auditor-facing artifact.

Answers the four questions an ITGC walkthrough always asks about a release:
  1. Is every change traceable to an authorized request (ticket)?
  2. Does every change have an approver of record?
  3. Was the approver someone other than the author (segregation of duties)?
  4. Were revenue-relevant paths touched, and was that escalation approved?

Approver, AI assistance, and escalation reference are read from git trailers, so
the evidence is derived from the commit record itself rather than a side channel
that can drift:

    [CRUISE-101] Add fare comparison helper

    Reviewed-by: Owen Marsh <owen.marsh@example.com>
    AI-Assisted: yes (cursor, dev-mode)
    Escalation-Ref: SEC-2026-014

Exit code is 1 when any exception is found, so this runs as a CI gate as well as
a report. Revenue-relevant globs come from the same protected-paths.json that
path-guard.py enforces at commit time — one source of truth, two enforcement
points (client-side block, server-side evidence).

Usage:
    python3 sox-evidence.py --range origin/release/R2026-05..origin/release/R2026-06
    python3 sox-evidence.py --root /path/to/repo --range HEAD~5..HEAD --json bundle.json
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

CONTROL_ID = "sox-change-evidence"

# Unit / record separators — safe against any character a commit message allows.
_US = "\x1f"
_RS = "\x1e"

DEFAULT_TICKET_REGEX = r"\[([A-Z][A-Z0-9]*-\d+)\]"

EXCEPTIONS = {
    "SOX-01": "Change is not traceable to an authorized request (no ticket id in the subject)",
    "SOX-02": "No approver of record (missing Reviewed-by trailer)",
    "SOX-03": "Segregation of duties: the author approved their own change",
    "SOX-04": "Revenue-relevant path changed without an escalation approval reference",
}


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def find_protected_paths_file(root: Path) -> Path | None:
    for rel in (
        "data/protected-paths.json",
        ".claude/data/protected-paths.json",
        "titan/harness/data/protected-paths.json",
    ):
        candidate = root / rel
        if candidate.is_file():
            return candidate
    return None


def load_protected_entries(path: Path | None) -> list[dict]:
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("paths") or []


def protected_hit(file_path: str, entries: list[dict]) -> str:
    """Return the id of the first protected entry matching this file, else ""."""
    normalized = file_path.replace("\\", "/")
    for entry in entries:
        for glob in entry.get("globs") or []:
            if fnmatch.fnmatch(normalized, glob) or fnmatch.fnmatch(
                normalized, glob.lstrip("./")
            ):
                return entry.get("id") or glob
    return ""


def parse_trailer(body: str, key: str) -> str:
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(body)
    return match.group(1).strip() if match else ""


def identity_matches(author_name: str, author_email: str, approver: str) -> bool:
    """True when the Reviewed-by trailer names the commit author."""
    approver_lower = approver.lower()
    if author_email and author_email.lower() in approver_lower:
        return True
    return bool(author_name) and author_name.lower() in approver_lower


def commit_files(root: Path, sha: str) -> list[str]:
    out = git(root, "show", "--name-only", "--pretty=format:", sha)
    return [line.strip() for line in out.splitlines() if line.strip()]


def collect(root: Path, rev_range: str, entries: list[dict], ticket_regex: str) -> list[dict]:
    fmt = _US.join(["%H", "%h", "%an", "%ae", "%aI", "%s", "%B"]) + _RS
    raw = git(root, "log", "--no-merges", f"--format={fmt}", rev_range)
    ticket_pattern = re.compile(ticket_regex)

    commits: list[dict] = []
    for record in raw.split(_RS):
        record = record.strip("\n")
        if not record.strip():
            continue
        parts = record.split(_US)
        if len(parts) < 7:
            continue
        sha, short_sha, author, email, authored_at, subject, body = parts[:7]

        ticket_match = ticket_pattern.search(subject)
        ticket = ticket_match.group(1) if ticket_match else ""
        approver = parse_trailer(body, "Reviewed-by")
        ai_assisted = parse_trailer(body, "AI-Assisted")
        escalation_ref = parse_trailer(body, "Escalation-Ref")

        files = commit_files(root, sha)
        protected = sorted({hit for f in files if (hit := protected_hit(f, entries))})

        exceptions: list[str] = []
        if not ticket:
            exceptions.append("SOX-01")
        if not approver:
            exceptions.append("SOX-02")
        elif identity_matches(author, email, approver):
            exceptions.append("SOX-03")
        if protected and not escalation_ref:
            exceptions.append("SOX-04")

        commits.append(
            {
                "sha": sha,
                "short_sha": short_sha,
                "author": author,
                "author_email": email,
                "authored_at": authored_at,
                "subject": subject,
                "ticket": ticket,
                "approver": approver,
                "ai_assisted": ai_assisted,
                "escalation_ref": escalation_ref,
                "files_changed": len(files),
                "protected_paths_touched": protected,
                "exceptions": exceptions,
            }
        )
    return commits


def truncate(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1] + "…"


def report(commits: list[dict], rev_range: str, pp_file: Path | None) -> None:
    print(f"SOX change evidence — control {CONTROL_ID}")
    print(f"Range: {rev_range}")
    print(f"Revenue-relevant globs: {pp_file if pp_file else 'NONE FOUND (fail open)'}")
    print(f"Generated: {_dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds')}")
    print()

    header = f"{'Commit':<9} {'Ticket':<12} {'Author':<14} {'Approver':<16} {'AI':<5} {'Verdict'}"
    print(header)
    print("-" * len(header))
    for c in commits:
        verdict = "OK" if not c["exceptions"] else ",".join(c["exceptions"])
        print(
            f"{c['short_sha']:<9} "
            f"{truncate(c['ticket'] or '—', 12):<12} "
            f"{truncate(c['author'], 14):<14} "
            f"{truncate(c['approver'].split('<')[0].strip() or '—', 16):<16} "
            f"{truncate(c['ai_assisted'].split('(')[0].strip() or '—', 5):<5} "
            f"{verdict}"
        )

    flagged = [c for c in commits if c["exceptions"]]
    if flagged:
        print()
        print("Exceptions requiring disposition before release:")
        for c in flagged:
            print(f"  {c['short_sha']}  {truncate(c['subject'], 62)}")
            for code in c["exceptions"]:
                print(f"     {code}  {EXCEPTIONS[code]}")
                if code == "SOX-04":
                    print(f"           paths: {', '.join(c['protected_paths_touched'])}")

    print()
    ai_count = sum(1 for c in commits if c["ai_assisted"])
    print(
        f"Summary: {len(commits)} change(s) · {len(commits) - len(flagged)} clean · "
        f"{len(flagged)} with exceptions · {ai_count} declared AI-assisted"
    )
    if flagged:
        print("Result: NO-GO — every exception needs a documented disposition.")
    else:
        print("Result: GO — all changes ticketed, independently approved, escalations referenced.")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repo root (default: cwd)")
    parser.add_argument(
        "--range",
        dest="rev_range",
        default="HEAD~10..HEAD",
        help="Git revision range, e.g. release/PREV..release/THIS",
    )
    parser.add_argument(
        "--protected-paths",
        type=Path,
        help="Override protected-paths.json location",
    )
    parser.add_argument(
        "--ticket-regex",
        default=DEFAULT_TICKET_REGEX,
        help="Regex whose first group is the ticket id",
    )
    parser.add_argument("--json", type=Path, help="Also write the bundle as JSON")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    pp_file = args.protected_paths or find_protected_paths_file(root)
    entries = load_protected_entries(pp_file)

    try:
        commits = collect(root, args.rev_range, entries, args.ticket_regex)
    except RuntimeError as exc:
        sys.stderr.write(f"[sox-evidence] {exc}\n")
        return 2

    if not commits:
        print(f"[sox-evidence] No non-merge commits in {args.rev_range} — nothing to evidence.")
        return 0

    report(commits, args.rev_range, pp_file)

    if args.json:
        bundle = {
            "control": CONTROL_ID,
            "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "repo_root": str(root),
            "range": args.rev_range,
            "protected_paths_source": str(pp_file) if pp_file else None,
            "exception_codes": EXCEPTIONS,
            "commits": commits,
            "totals": {
                "changes": len(commits),
                "with_exceptions": sum(1 for c in commits if c["exceptions"]),
                "declared_ai_assisted": sum(1 for c in commits if c["ai_assisted"]),
            },
        }
        args.json.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
        print(f"\nJSON bundle: {args.json}")

    return 1 if any(c["exceptions"] for c in commits) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
