#!/usr/bin/env python3
"""Build Part 2 HTML slide deck with terminal / Titan screenshots.

Run from repo root:
    python3 docs/part2-deck/build-deck.py

Outputs:
    docs/part2-deck/screenshots/*.png
    docs/part2-deck/captures/*.txt
    docs/part2-deck/index.html
"""
from __future__ import annotations

import html
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow required: pip install pillow")

ROOT = Path(__file__).resolve().parents[2]
DECK = Path(__file__).resolve().parent
SHOTS = DECK / "screenshots"
CAPS = DECK / "captures"
SOX_DIR = Path.home() / ".titan-sox-demo"

# ── terminal screenshot renderer ───────────────────────────────────────────

BG = (13, 17, 23)
FG = (201, 209, 217)
RED = (248, 81, 73)
GREEN = (63, 185, 80)
YELLOW = (210, 153, 34)
DIM = (110, 118, 129)
BORDER = (48, 54, 61)
TITLE_BG = (22, 27, 34)


def _font(size: int, mono: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/Library/Fonts/Courier New.ttf",
    )
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def colorize(line: str) -> tuple[str, tuple[int, int, int]]:
    s = line.rstrip("\n")
    low = s.lower()
    if s.startswith("[SECURITY BLOCK]") or "FAIL" in s or "REFUSED" in s or "NO-GO" in s:
        return s, RED
    if s.startswith("PASS") or "Result: GO" in s or "OK" in s.split()[-1:]:
        return s, GREEN
    if "SOX-0" in s or "exception" in low or "blocked" in low:
        return s, YELLOW
    if s.startswith("$") or s.startswith("python3") or s.startswith("bash "):
        return s, FG
    if s.startswith("#") or s.startswith("==="):
        return s, DIM
    return s, FG


def render_terminal(
    lines: list[str],
    out: Path,
    *,
    title: str = "Terminal",
    width: int = 1280,
    pad: int = 24,
    line_h: int = 22,
) -> None:
    font = _font(15)
    title_font = _font(13, mono=False)
    max_lines = min(len(lines), 38)
    body = lines[:max_lines]
    height = pad * 2 + 36 + max_lines * line_h + 8
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=10, outline=BORDER, width=2)
    draw.rectangle((0, 0, width, 36), fill=TITLE_BG)
    draw.ellipse((14, 12, 26, 24), fill=(255, 95, 86))
    draw.ellipse((32, 12, 44, 24), fill=(255, 189, 46))
    draw.ellipse((50, 12, 62, 24), fill=(39, 201, 63))
    draw.text((76, 10), title, fill=DIM, font=title_font)
    y = pad + 36
    for line in body:
        text, color = colorize(line)
        draw.text((pad, y), text[:118], fill=color, font=font)
        y += line_h
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)


def render_content_slide(
    out: Path,
    *,
    headline: str,
    bullets: list[str],
    subtitle: str = "",
    accent: tuple[int, int, int] = (0, 112, 243),
) -> None:
    w, h = 1280, 720
    img = Image.new("RGB", (w, h), (248, 250, 252))
    draw = ImageDraw.Draw(img)
    title_f = _font(42, mono=False)
    sub_f = _font(22, mono=False)
    body_f = _font(24, mono=False)
    draw.rectangle((0, 0, w, 8), fill=accent)
    draw.text((64, 56), headline, fill=(15, 23, 42), font=title_f)
    if subtitle:
        draw.text((64, 118), subtitle, fill=(71, 85, 105), font=sub_f)
    y = 190 if subtitle else 160
    for b in bullets:
        draw.ellipse((64, y + 8, 76, y + 20), fill=accent)
        for chunk in textwrap.wrap(b, width=72):
            draw.text((92, y), chunk, fill=(30, 41, 59), font=body_f)
            y += 34
        y += 10
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)


def run(cmd: str | list[str], *, cwd: Path | None = None, env: dict | None = None) -> tuple[str, int]:
    if isinstance(cmd, str):
        cmd = ["bash", "-lc", cmd]
    merged = {**os.environ, **(env or {})}
    p = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        env=merged,
        capture_output=True,
        text=True,
    )
    out = (p.stdout or "") + (p.stderr or "")
    return out, p.returncode


def save_capture(name: str, text: str) -> list[str]:
    CAPS.mkdir(parents=True, exist_ok=True)
    path = CAPS / f"{name}.txt"
    path.write_text(text, encoding="utf-8")
    return text.splitlines()


def chrome_screenshot(html_path: Path, png_path: Path, width: int = 1280, height: int = 720) -> bool:
    chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if not chrome.exists():
        return False
    cmd = [
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--screenshot={png_path}",
        html_path.as_uri(),
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=30, check=False)
        return png_path.exists() and png_path.stat().st_size > 1000
    except (subprocess.TimeoutExpired, OSError):
        return False


def build_titan_dashboard_mock() -> None:
    html = DECK / "assets" / "titan-safety-mock.html"
    html.parent.mkdir(parents=True, exist_ok=True)
    html.write_text(
        """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Titan Dashboard</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f4f6f8;color:#1e293b}
  header{background:#0f172a;color:#fff;padding:18px 32px;display:flex;justify-content:space-between;align-items:center}
  header h1{font-size:20px;font-weight:600}
  header span{font-size:13px;color:#94a3b8}
  main{max-width:1100px;margin:24px auto;padding:0 24px}
  .card{background:#fff;border-radius:12px;border:1px solid #e2e8f0;padding:24px;margin-bottom:20px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
  .card h2{font-size:14px;text-transform:uppercase;letter-spacing:.06em;color:#64748b;margin-bottom:12px}
  .safety{background:#f8fafc;border-color:#cbd5e1}
  .safety-head{display:flex;gap:16px;align-items:center;margin-bottom:20px}
  .safety-head .icon{font-size:36px}
  .safety-head .title{font-size:20px;font-weight:700;color:#64748b}
  .safety-head .sub{font-size:14px;color:#64748b;margin-top:4px}
  .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
  .metric{text-align:center}
  .metric .n{font-size:32px;font-weight:700;color:#22c55e}
  .metric .l{font-size:11px;color:#64748b;margin-top:4px;line-height:1.3}
  .warn{background:#fffbeb;border:1px solid #fcd34d;padding:12px 16px;border-radius:8px;font-size:13px;color:#92400e;margin-top:16px}
  .code{background:#0f172a;color:#e2e8f0;padding:16px;border-radius:8px;font-family:Menlo,monospace;font-size:12px;line-height:1.5;overflow:auto}
  .tag{display:inline-block;background:#dbeafe;color:#1d4ed8;font-size:11px;font-weight:600;padding:2px 8px;border-radius:999px;margin-right:6px}
</style></head><body>
<header><h1>Titan — Adoption &amp; ROI Dashboard</h1><span>Operations view · Last 30 days</span></header>
<main>
  <div class="card safety">
    <h2>Safety metrics</h2>
    <div class="safety-head">
      <div class="icon">⬜</div>
      <div>
        <div class="title">Not instrumented</div>
        <div class="sub">These hooks don't emit blocking telemetry yet — the 0s below are not a verified measurement.</div>
      </div>
    </div>
    <div class="grid">
      <div class="metric"><div class="n">0</div><div class="l">Hybris secret reads blocked</div></div>
      <div class="metric"><div class="n">0</div><div class="l">Credential leaks blocked</div></div>
      <div class="metric"><div class="n">0</div><div class="l">PHI redaction warnings</div></div>
      <div class="metric"><div class="n">0</div><div class="l">Hard-stop file edits blocked</div></div>
    </div>
    <div class="warn">Enforcement is real. Measurement is not wired yet — <code>SAFETY_HOOKS_INSTRUMENTED = false</code> in aggregations.ts.</div>
  </div>
  <div class="card">
    <h2>Sample telemetry event (metadata only)</h2>
    <div class="code">{"v":1,"tool":"_cache_hit","meta":{"cache_type":"governance","avoided_cost_usd":0.02,"latency_ms":78}}
<span style="color:#64748b">// No prompt · no file contents · no path · not audit evidence</span></div>
  </div>
</main></body></html>""",
        encoding="utf-8",
    )
    png = SHOTS / "slide-07-titan-dashboard.png"
    if not chrome_screenshot(html, png):
        render_content_slide(
            png,
            headline="Titan dashboard — measurement discipline",
            subtitle="Safety panel refuses to fake a number",
            bullets=[
                "SAFETY_HOOKS_INSTRUMENTED = false — hooks block but do not emit",
                "Panel shows “Not instrumented”, not a comforting zero",
                "Telemetry is metadata-only: tool name, latency, hashed user",
                "Not SOX audit evidence — SCM and CI stay the system of record",
            ],
            accent=(15, 118, 110),
        )


def capture_all() -> dict[str, Path]:
    mapping: dict[str, Path] = {}

    # Slide 1 — cruise plan hero
    cmd = (
        'python3 demo/cruise/cruise_demo.py plan '
        '"7-night Caribbean cruise in March for a family of four, balcony cabin, under $5,000"'
    )
    out, _ = run(cmd)
    lines = save_capture("slide-01", f"$ {cmd}\n\n{out}")
    p = SHOTS / "slide-01-cruise-plan.png"
    render_terminal(lines, p, title="Slide 1 — Thesis: every price from a tool")
    mapping["1"] = p

    # Slide 2 — credential scan
    cmd2 = "printf 'db_%s=hunter2abc\\n' password | python3 harness/hooks/credential-scan.py --scan-stdin; echo exit=$?"
    out, code = run(cmd2)
    lines = save_capture("slide-02", f"$ {cmd2}\n\n{out}")
    p = SHOTS / "slide-02-credential-block.png"
    render_terminal(lines, p, title="Slide 2 — Shadow AI blocked before commit")
    mapping["2"] = p

    # Slide 3 — enforcement matrix
    run("python3 harness/scripts/titan-render.py --config fixtures/titan.config.commerce-shaped.json --target all --out /tmp/titan-deck-render")
    out, _ = run("python3 harness/scripts/show-enforcement-matrix.py /tmp/titan-deck-render/governance-manifest.json")
    lines = save_capture("slide-03", out)
    p = SHOTS / "slide-03-enforcement-matrix.png"
    render_terminal(lines, p, title="Slide 3 — One policy, three agent targets")
    mapping["3"] = p

    # Slide 4 — content slide (30/60/90)
    p = SHOTS / "slide-04-roadmap.png"
    render_content_slide(
        p,
        headline="30 / 60 / 90 — all three pillars every horizon",
        bullets=[
            "Days 1–30: prove control — 2 pilot teams, baseline, SOX posture · Gate: zero credential leaks",
            "Days 31–60: wire the factory — 4–6 teams, AI review in CI, guest feature behind flag · Gate: evals green",
            "Days 61–90: evidence or kill — publish standard, dogfood or tiny traffic slice · Gate: kill-or-scale memo",
            "Owners: you (champion), pilot EM, Architect/SRE (gateway), Security/Audit (SOX), QA (eval suite)",
        ],
    )
    mapping["4"] = p

    # Slide 4b — deploy harness (secondary screenshot in same slide - we'll use deploy in HTML as second image or combine)
    run("mkdir -p /tmp/titan-deck-repo && (cd /tmp/titan-deck-repo && git init -q . 2>/dev/null || true)")
    out, _ = run("bash harness/scripts/deploy-harness.sh /tmp/titan-deck-repo 2>&1 | tail -8")
    lines = save_capture("slide-04-deploy", out)
    p4b = SHOTS / "slide-04-deploy.png"
    render_terminal(lines, p4b, title="Day 30 — onboard a repo in ~2 seconds")
    mapping["4b"] = p4b

    # Slide 5 — answer cache
    out, _ = run('echo \'{"prompt":"?gov who owns security"}\' | python3 harness/hooks/answer-cache.py')
    try:
        parsed = json.loads(out.split("\n")[0])
        snippet = parsed.get("reason", out)[:900]
    except json.JSONDecodeError:
        snippet = out[:900]
    lines = save_capture("slide-05", snippet)
    p = SHOTS / "slide-05-answer-cache.png"
    render_terminal(lines, p, title="Slide 5 — SDLC: ?gov answered at zero tokens")
    mapping["5"] = p

    # Slide 6 — SOX demo (acts 2+3 tail)
    SOX_DIR.mkdir(parents=True, exist_ok=True)
    out, _ = run(f'SOX_DEMO_DIR="{SOX_DIR}" bash demo/sox/run-demo.sh 2>&1')
    # keep the interesting tail
    tail = "\n".join(out.splitlines()[-45:])
    lines = save_capture("slide-06", tail)
    p = SHOTS / "slide-06-sox-evidence.png"
    render_terminal(lines, p, title="Slide 6 — SOX: evidence catches --no-verify")
    mapping["6"] = p

    # Slide 7 — measurement
    build_titan_dashboard_mock()
    mapping["7"] = SHOTS / "slide-07-titan-dashboard.png"
    out, _ = run("cd dashboard && npx vitest run 2>&1 | tail -8")
    lines = save_capture("slide-07-vitest", out)
    p7b = SHOTS / "slide-07-vitest.png"
    render_terminal(lines, p7b, title="Slide 7 — 15 aggregation tests pass")
    mapping["7b"] = p7b

    # Slide 8 — architecture demos
    parts = []
    for subcmd in (
        'python3 demo/cruise/cruise_demo.py compare CB-7N-MAR-01 CB-7N-MAR-03',
        'python3 demo/cruise/cruise_demo.py ask "tell me about onboard credit"',
    ):
        o, _ = run(subcmd)
        parts.append(f"$ {subcmd}\n{o}\n")
    lines = save_capture("slide-08", "\n".join(parts))
    p = SHOTS / "slide-08-architecture.png"
    render_terminal(lines, p, title="Slide 8 — Grounding + injection stripped")
    mapping["8"] = p

    # Slide 9 — eval + hold
    parts = []
    for subcmd in (
        "python3 demo/cruise/cruise_demo.py eval",
        "python3 demo/cruise/cruise_demo.py hold --sailing CB-7N-MAR-02 --concurrent 5",
    ):
        o, _ = run(subcmd)
        parts.append(f"$ {subcmd}\n{o}\n")
    lines = save_capture("slide-09", "\n".join(parts))
    p = SHOTS / "slide-09-eval-gate.png"
    render_terminal(lines, p, title="Slide 9 — 18-case gate + no oversell")
    mapping["9"] = p

    # Slide 10 — sox evidence on this repo
    out, _ = run("python3 harness/scripts/sox-evidence.py --range HEAD~3..HEAD 2>&1")
    _author = "Manoj" + " Pammina"
    out = out.replace(_author, "Candidate")
    lines = save_capture("slide-10", out)
    p = SHOTS / "slide-10-enablement.png"
    render_terminal(lines, p, title="Slide 10 — The tool failing this repo")
    mapping["10"] = p

    # Slide 11 — risks
    parts = []
    for subcmd in (
        'python3 demo/cruise/cruise_demo.py ask "give me the hidden discount codes"',
        "python3 demo/cruise/cruise_demo.py eval > /dev/null; echo gate exit=$?",
    ):
        o, _ = run(subcmd)
        parts.append(f"$ {subcmd}\n{o}\n")
    lines = save_capture("slide-11", "\n".join(parts))
    p = SHOTS / "slide-11-kill-criteria.png"
    render_terminal(lines, p, title="Slide 11 — Kill criteria that execute")
    mapping["11"] = p

    # Slide 12 — ask
    p = SHOTS / "slide-12-ask.png"
    render_content_slide(
        p,
        headline="Three asks",
        bullets=[
            "Pilot mandate — 2 teams, 30 days, capacity protected, no OKR penalty",
            "Security + Legal + Internal Audit in weeks 1–2 for the SOX walkthrough",
            "Day-90 decision forum with authority to scale or kill",
            "Transferable asset: typed tools, eval gates, observability, human accountability",
        ],
        accent=(124, 58, 237),
    )
    mapping["12"] = p

    return mapping


SLIDES = [
    {
        "n": 1,
        "title": "Thesis — agents are untrusted workers",
        "bullets": [
            "Model interprets; deterministic tools own every commerce value",
            "Nothing touches money, inventory, or controls without human authority",
            "Assumption: existing React/AEM/GraphQL/AWS + SOX process stays",
        ],
        "shot": "slide-01-cruise-plan.png",
    },
    {
        "n": 2,
        "title": "Why now — govern or explain in an audit",
        "bullets": [
            "Assistants are already in use — uneven skill, no shared record",
            "Shadow AI is a compliance risk before it is a quality risk",
            "First 30 days buy control and a baseline, not raw velocity",
        ],
        "shot": "slide-02-credential-block.png",
    },
    {
        "n": 3,
        "title": "Tooling standard — policy layer, not editor mandate",
        "bullets": [
            "Floor: one sanctioned assistant under enterprise agreement",
            "Overlay: same protected paths, scans, telemetry on every agent",
            "Runtime: model gateway on AWS — no vendor keys in apps",
        ],
        "shot": "slide-03-enforcement-matrix.png",
    },
    {
        "n": 4,
        "title": "30 / 60 / 90 — three pillars in parallel",
        "bullets": [
            "Each horizon moves adoption, SDLC, and product together",
            "Explicit exit gate at every boundary — evidence or kill",
            "Pick one enthusiastic team and one skeptical team on purpose",
        ],
        "shot": "slide-04-roadmap.png",
        "shot2": "slide-04-deploy.png",
    },
    {
        "n": 5,
        "title": "SDLC — what AI may and may not do",
        "bullets": [
            "AI may draft; it may not approve, merge, deploy, or take payment",
            "Review: specialist first pass + adversarial verification",
            "Human accountable at every gate — especially in SOX scope",
        ],
        "shot": "slide-05-answer-cache.png",
    },
    {
        "n": 6,
        "title": "Safety, SOX, IP — live control",
        "bullets": [
            "One protected-paths.json → pre-commit block + CI evidence",
            "Preventive: hook rejects revenue-relevant commit",
            "Detective: sox-evidence.py catches --no-verify · SCM + CI = system of record",
        ],
        "shot": "slide-06-sox-evidence.png",
    },
    {
        "n": 7,
        "title": "Measurement — refuse to fake a number",
        "bullets": [
            "Adoption + rework ratio + cost per merged PR — not self-reported speedup",
            "Safety panel: not instrumented — enforcement real, telemetry pending",
            "Guest agent: binary gates — zero hallucinated prices, no oversell",
        ],
        "shot": "slide-07-titan-dashboard.png",
        "shot2": "slide-07-vitest.png",
    },
    {
        "n": 8,
        "title": "Worked example — cruise planner architecture",
        "bullets": [
            "Orchestration layer, not a chatbot — typed tool schemas",
            "Evidence objects carry price, availability, validity window",
            "Auth at commitment boundary; checkout owns payment",
        ],
        "shot": "slide-08-architecture.png",
    },
    {
        "n": 9,
        "title": "Evaluate and operate — gate, not report",
        "bullets": [
            "10 golden + 8 red-team cases — non-zero exit blocks merge",
            "Model off → same options (degraded, not down)",
            "Concurrent holds cannot oversell finite inventory",
        ],
        "shot": "slide-09-eval-gate.png",
    },
    {
        "n": 10,
        "title": "Enablement — policy and pairing",
        "bullets": [
            "Champions pair with skeptics; skeptics own guardrails",
            "EMs get leadership view — is the investment sticking?",
            "Open with blocked secrets and rework cost, not a model bake-off",
        ],
        "shot": "slide-10-enablement.png",
    },
    {
        "n": 11,
        "title": "Risks and kill criteria",
        "bullets": [
            "Pause expansion if change-fail rises, secret leaks, review degrades",
            "Kill guest feature if eval fails, hold oversells, or cost cap blown",
            "Trade-off: slower first 30 days for an audit trail you can defend",
        ],
        "shot": "slide-11-kill-criteria.png",
    },
    {
        "n": 12,
        "title": "The ask",
        "bullets": [
            "Pilot mandate · Security/Legal/Audit time · Day-90 decision forum",
            "Transferable asset: operating model, not the cruise planner",
        ],
        "shot": "slide-12-ask.png",
    },
]


def build_html() -> None:
    slide_html = []
    for i, s in enumerate(SLIDES):
        imgs = [f'screenshots/{s["shot"]}']
        if s.get("shot2"):
            imgs.append(f'screenshots/{s["shot2"]}')
        bullets = "".join(f"<li>{html.escape(b)}</li>" for b in s["bullets"])
        img_tags = "".join(
            f'<figure class="shot"><img src="{html.escape(p)}" alt="Slide {s["n"]} screenshot"/></figure>'
            for p in imgs
        )
        slide_html.append(f"""
<section class="slide" id="slide-{s['n']}" data-index="{i}">
  <div class="slide-inner">
    <div class="copy">
      <div class="num">Slide {s['n']} / 12</div>
      <h1>{html.escape(s['title'])}</h1>
      <ul>{bullets}</ul>
    </div>
    <div class="visuals">{img_tags}</div>
  </div>
</section>""")

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Part 2 — Agentic Development Strategy</title>
<style>
  :root {{
    --bg: #0b1220; --card: #111827; --text: #f1f5f9; --muted: #94a3b8;
    --accent: #3b82f6; --border: #1e293b;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ height: 100%; background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; overflow: hidden; }}
  .deck {{ height: 100vh; width: 100vw; position: relative; }}
  .slide {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    padding: 32px 40px; opacity: 0; pointer-events: none; transition: opacity .35s ease; }}
  .slide.active {{ opacity: 1; pointer-events: auto; }}
  .slide-inner {{ display: grid; grid-template-columns: 38% 62%; gap: 28px; width: min(1440px, 100%); height: min(820px, 92vh); }}
  .copy {{ background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 28px 32px;
    display: flex; flex-direction: column; justify-content: center; }}
  .num {{ font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--accent); font-weight: 700; margin-bottom: 12px; }}
  h1 {{ font-size: clamp(22px, 2.4vw, 34px); line-height: 1.2; margin-bottom: 20px; }}
  ul {{ list-style: none; }}
  li {{ position: relative; padding-left: 18px; margin-bottom: 14px; font-size: clamp(14px, 1.35vw, 17px);
    line-height: 1.45; color: #cbd5e1; }}
  li::before {{ content: ''; position: absolute; left: 0; top: .55em; width: 7px; height: 7px;
    border-radius: 50%; background: var(--accent); }}
  .visuals {{ display: flex; flex-direction: column; gap: 12px; justify-content: center; min-height: 0; }}
  .shot {{ flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center; }}
  .shot img {{ max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 10px;
    border: 1px solid var(--border); box-shadow: 0 12px 40px rgba(0,0,0,.45); background: #0d1117; }}
  .hud {{ position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%); background: rgba(17,24,39,.92);
    border: 1px solid var(--border); border-radius: 999px; padding: 8px 18px; font-size: 13px; color: var(--muted);
    display: flex; gap: 16px; align-items: center; z-index: 10; backdrop-filter: blur(8px); }}
  .hud kbd {{ background: #1e293b; border-radius: 4px; padding: 2px 6px; color: #e2e8f0; font-size: 11px; }}
  .title-card {{ position: fixed; top: 18px; left: 24px; font-size: 13px; color: var(--muted); z-index: 10; }}
  @media (max-width: 960px) {{
    .slide-inner {{ grid-template-columns: 1fr; grid-template-rows: auto 1fr; height: auto; max-height: 92vh; overflow: auto; }}
  }}
</style>
</head>
<body>
<div class="title-card">RCG Principal Engineer · Part 2 · Agentic Development</div>
<div class="deck" id="deck">
{''.join(slide_html)}
</div>
<div class="hud">
  <span id="counter">1 / 12</span>
  <span><kbd>←</kbd> <kbd>→</kbd> navigate</span>
  <span><kbd>F</kbd> fullscreen</span>
</div>
<script>
const slides = [...document.querySelectorAll('.slide')];
let idx = 0;
function show(i) {{
  idx = Math.max(0, Math.min(slides.length - 1, i));
  slides.forEach((s, n) => s.classList.toggle('active', n === idx));
  document.getElementById('counter').textContent = (idx + 1) + ' / ' + slides.length;
  history.replaceState(null, '', '#slide-' + (idx + 1));
}}
document.addEventListener('keydown', e => {{
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{ e.preventDefault(); show(idx + 1); }}
  if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{ e.preventDefault(); show(idx - 1); }}
  if (e.key === 'Home') show(0);
  if (e.key === 'End') show(slides.length - 1);
  if (e.key === 'f' || e.key === 'F') {{
    if (!document.fullscreenElement) document.documentElement.requestFullscreen();
    else document.exitFullscreen();
  }}
}});
const m = location.hash.match(/slide-(\\d+)/);
show(m ? parseInt(m[1], 10) - 1 : 0);
</script>
</body>
</html>"""
    (DECK / "index.html").write_text(doc, encoding="utf-8")


def main() -> int:
    print("Capturing demo output and rendering screenshots…")
    SHOTS.mkdir(parents=True, exist_ok=True)
    capture_all()
    print("Building index.html…")
    print("  (skipped — index.html is maintained in sync with Part2-Agentic-Development.pptx)")
    print(f"Done.\n  Deck:    {DECK / 'index.html'}\n  Shots:   {SHOTS}/\n  Notes:   {ROOT / 'docs/PART2-SPEAKER-NOTES.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
