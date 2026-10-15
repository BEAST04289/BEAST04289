#!/usr/bin/env python3
"""Generate the hand-designed, animated SVGs used by README.md.

    python scripts/build_static.py

Design rules: black/grey surfaces, hairline borders, no coloured glows — colour lives only in
words and numbers. Everything the artwork says lives in the CONTENT section below; edit and re-run.
Live GitHub numbers are rendered separately by scripts/github_stats.py (GitHub Actions).
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svgkit import (ACCENTS, DIM, EDGE, EDGE_HI, GREEN, MUTED, SOFT, TEXT,  # noqa: E402
                    Svg, esc, fit_size, http_get, icon, legible, text_width, wrap)

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
# Simple Icons drops some brands over time, so a slug may pin its own release: "name@version".
SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@{}/icons/{}.svg"
SI_VERSION = "16.35.0"
GRAD = ("#67e8f9", "#a78bfa", "#f472b6")   # the one gradient used for display words
TILE, TILE_EDGE = "#1b1b1b", "#2e2e2e"

# ============================================================================ CONTENT
NAME = "SHAURYA UPADHYAY"
FOCUS = ["AI Engineer", "RAG", "AI Agents", "Software Engineering"]
TYPED = [
    "building AI agents & RAG systems that ship",
    "#1 of 28,017 in a live-proctored analytics test",
    "top 100 of 1,400+ · XPRIZE Build with Gemini",
    "rank 14 of 2,200+ · IIT Madras Synaptix Frontier AI",
    "top 25 · TigerGraph × Hacker House Goa 2026",
    "$5,000 Solana Foundation grantee · OWASP contributor",
]
# availability pill: (tag, lead-in, roles in the gradient) + a quiet education chip next to it
STATUS = ("AVAILABLE", "Open to ", "AI/ML, SWE & SDE roles")
EDU_CHIP = "B.Tech CSE · MUJ '29"

# 4 x 3 wall; every row uses four different accents for its numbers.
ACHIEVEMENTS = [
    dict(icon="trophy", tag="ASSESSMENT", metric="#1", suffix="/ 28,017", title="Data Analytics Assessment",
         sub="Bluestock · top 0.004%", accent="gold"),
    dict(icon="globe", tag="GLOBAL", metric="Top 100", suffix="/ 1,400+", title="XPRIZE Build with Gemini",
         sub="top 7% worldwide", accent="violet"),
    dict(icon="target", tag="HACKATHON", metric="#14", suffix="/ 2,200+", title="IIT Madras Synaptix",
         sub="Frontier AI · top 1%", accent="pink"),
    dict(icon="spark", tag="HACKATHON", metric="Top 25", suffix="", title="TigerGraph × Hacker House",
         sub="Goa 2026 · agentic AI", accent="cyan"),
    dict(icon="coin", tag="GRANT", metric="$5,000", suffix="", title="Solana Foundation",
         sub="security audit subsidy", accent="green"),
    dict(icon="merge", tag="OPEN SOURCE", metric="2", suffix="PRs merged", title="OWASP OpenCRE",
         sub="flagship · #837 · #993", accent="sky"),
    dict(icon="rocket", tag="HACKATHON", metric="Top 10", suffix="/ 232", title="100x School × Superteam",
         sub="India · $450 prize", accent="gold"),
    dict(icon="code", tag="OPEN SOURCE", metric="#65", suffix="/ 2,055", title="OpenCode'25",
         sub="about the top 3%", accent="violet"),
    dict(icon="medal", tag="NATIONALS", metric="Finalist", suffix="", title="CraftNCode Nationals",
         sub="with Sarthi Kalyan", accent="pink"),
    dict(icon="users", tag="WIKIMEDIA", metric="Top 100", suffix="nationally", title="WikiTech: Road to Wiki",
         sub="selected · cohort 2", accent="cyan"),
    dict(icon="award", tag="UNIVERSITY", metric="Award", suffix="2026", title="MUJ Student Excellence",
         sub="CSE · hackathon category", accent="green"),
    dict(icon="cap", tag="SCHOLARSHIP", metric="Graduate", suffix="", title="AWS AI & ML Scholars",
         sub="fully funded nanodegree", accent="sky"),
]

PROJECTS = [
    dict(slug="sarthi-kalyan", name="Sarthi Kalyan", icon="users", accent="violet",
         category="MULTI-AGENT RAG ASSISTANT", award="TOP 100 / 1,400+ · XPRIZE",
         desc="Multi-agent system matching citizens to 750+ government welfare schemes with dual-mode "
              "retrieval, deployed on Google Cloud with WhatsApp and web interfaces.",
         metrics=[("750+", "schemes"), ("Top 7%", "XPRIZE global"), ("Finalist", "CraftNCode")],
         tech=["LangGraph", "Gemini", "FastAPI", "Next.js", "BigQuery"],
         repo="BEAST04289/SchemeBot"),
    dict(slug="iwebify", name="iWebify", icon="code", accent="pink",
         category="LLM APPLICATION COMPILER", award=None,
         desc="9-stage LangGraph pipeline that turns natural-language requirements into validated, "
              "executable app schemas, with a repair engine driven by exact Pydantic errors.",
         metrics=[("9", "pipeline stages"), ("20", "eval prompts"), ("4", "tracked KPIs")],
         tech=["LangGraph", "FastAPI", "Pydantic", "OpenRouter", "Docker"],
         repo="BEAST04289/iWEBIFY"),
    dict(slug="sentinel", name="Sentinel", icon="pulse", accent="green",
         category="RAG AGENT FOR FINANCIAL FILINGS", award="RANK 14 / 2,200+ · IIT MADRAS",
         desc="Agent that parses SEC filings and raises risk alerts, using local embeddings on "
              "ChromaDB + FAISS to cut inference API cost to zero.",
         metrics=[("150ms", "filing parse"), ("<7s", "risk alerts"), ("$0", "inference API")],
         tech=["LangGraph", "ChromaDB", "FAISS", "FastAPI"],
         repo="BEAST04289/Sentinel"),
    dict(slug="shield", name="SHIELD", icon="shield", accent="gold",
         category="ANTI-SCAM AI ON AWS", award=None,
         desc="Scam-detection platform for senior citizens with a DynamoDB Scam Fingerprint Network "
              "and Hindi voice-first, accessibility-focused interfaces.",
         metrics=[("4.2s", "was 8 minutes"), ("91%", "accuracy"), ("97%", "lower API cost")],
         tech=["Bedrock", "Textract", "Polly", "DynamoDB", "EC2"],
         repo="BEAST04289/AWS_AI-FOR-BHARAT"),
    dict(slug="casevera", name="CaseVera", icon="search", accent="cyan",
         category="AI INVESTIGATION AGENT", award="TOP 25 · HACKER HOUSE GOA",
         desc="Policy-constrained agent that investigates fraud alerts end to end — retrieval over past "
              "cases and policy, evidence with provenance, SAR narratives — with deterministic verdicts.",
         metrics=[("2 / 2", "fraud patterns"), ("20 / 20", "cases persisted"), ("273", "evidence records")],
         tech=["Python", "GraphRAG", "Vector search", "TigerGraph", "React"],
         repo="BEAST04289/CaseVera", live="casevera.vercel.app"),
    dict(slug="dugtrio", name="DugTrio", icon="bolt", accent="sky",
         category="VERIFIABLE SENTIMENT AGENT", award="TOP 10 / 232 · SUPERTEAM",
         desc="Telegram agent that scores crypto sentiment from X with RoBERTa and anchors every result "
              "on-chain as a verifiable IP asset.",
         metrics=[("$5,000", "Solana grant"), ("$450", "prize"), ("Top 10", "of 232 teams")],
         tech=["Python", "RoBERTa", "FastAPI", "Web3.py", "Story Protocol"],
         repo="BEAST04289/DugTrio"),
]

# (label, simple-icons slug or custom glyph, brand hex)
STACK = [
    ("LANGUAGES", "cyan", [("Python", "python", "3776AB"), ("Java", "openjdk", "ED8B00"),
                           ("C++", "cplusplus", "00599C"), ("C", "c", "A8B9CC"),
                           ("TypeScript", "typescript", "3178C6"), ("JavaScript", "javascript", "F7DF1E"),
                           ("SQL", "@database", "22D3EE"), ("Bash", "gnubash", "4EAA25")]),
    ("AI · LLMS", "violet", [("LangGraph", "langgraph", "1C3C3C"), ("Gemini", "googlegemini", "8E75B2"),
                             ("Bedrock", "amazonwebservices@14.15.0", "FF9900"), ("Hugging Face", "huggingface", "FFD21E"),
                             ("ChromaDB", "@chroma", "FFDE2D"), ("FAISS", "meta", "0467DF"),
                             ("Qdrant", "qdrant", "DC244C"), ("RAG", "@search", "A78BFA")]),
    ("DATA", "pink", [("PostgreSQL", "postgresql", "4169E1"), ("SQLite", "sqlite", "003B57"),
                      ("BigQuery", "googlebigquery", "669DF6"), ("Pandas", "pandas", "150458"),
                      ("NumPy", "numpy", "4DABCF"), ("Plotly", "plotly", "3F4F75"),
                      ("Streamlit", "streamlit", "FF4B4B"), ("TigerGraph", "@graph", "F58220")]),
    ("BACKEND · CLOUD", "gold", [("FastAPI", "fastapi", "009688"), ("Pydantic", "pydantic", "E92063"),
                                 ("Next.js", "nextdotjs", "FFFFFF"), ("React", "react", "61DAFB"),
                                 ("Docker", "docker", "2496ED"), ("AWS", "amazonwebservices@14.15.0", "FF9900"),
                                 ("Google Cloud", "googlecloud", "4285F4"), ("Linux", "linux", "FCC624")]),
]

BUTTONS = [("portfolio", "Portfolio", "@globe", "EDEDED"),
           ("linkedin", "LinkedIn", "linkedin@13.21.0", "0A66C2"),
           ("email", "Email", "gmail", "EA4335"),
           ("telegram", "Telegram", "telegram", "26A5E4")]

HEADERS = [
    ("achievements", "01", "HALL OF FAME", "ranks · grants · awards · open source"),
    ("projects", "02", "FEATURED PROJECTS", "AI agents · RAG · backend · cloud"),
    ("stack", "03", "TECH STACK", "languages · AI · data · cloud"),
    ("experience", "04", "EXPERIENCE", "industry · open source · community"),
    ("pulse", "05", "GITHUB STATS", "live numbers · refreshed daily by GitHub Actions"),
]

# ============================================================================ helpers
_icon_cache: dict[str, str] = {}


def brand_path(slug: str) -> str:
    if slug not in _icon_cache:
        name, _, version = slug.partition("@")
        svg = http_get(SIMPLE_ICONS.format(version or SI_VERSION, name)).decode()
        m = re.search(r'<path d="([^"]+)"', svg)
        if not m:
            raise RuntimeError(f"simple-icons: no path for {slug}")
        _icon_cache[slug] = m.group(1)
    return _icon_cache[slug]


def brand_glyph(slug: str, hex_: str, x: float, y: float, size: float) -> str:
    """Brand logo (24x24 artboard) with its top-left at (x, y)."""
    s = size / 24
    color = legible("#" + hex_, min_ratio=3.2)
    if slug == "@chroma":
        return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})">'
                f'<circle cx="8.6" cy="12" r="6.6" fill="#FFDE2D"/><circle cx="15.4" cy="12" r="6.6" fill="#327EFF"/>'
                f'<path d="M12 6.27A6.6 6.6 0 0 1 12 17.73A6.6 6.6 0 0 1 12 6.27Z" fill="#FF6446"/></g>')
    if slug.startswith("@"):
        return icon(slug[1:], x, y, size, color, width=2.2)
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})">'
            f'<path d="{brand_path(slug)}" fill="{color}"/></g>')


def write(name: str, svg: Svg) -> None:
    path = ASSETS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = svg.render()
    path.write_text(doc, encoding="utf-8", newline="\n")
    print(f"  {name:<34} {len(doc) / 1024:6.1f} KB")


def word_grad(s: Svg, x0: float, x1: float) -> str:
    return s.linear([(0, GRAD[0]), (.5, GRAD[1]), (1, GRAD[2])], f"{x0:.1f}", 0, f"{x1:.1f}", 0, units="userSpaceOnUse")


def keyframes_common(s: Svg) -> None:
    s.css.append(
        "@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}"
        ".rise{animation:rise .9s cubic-bezier(.2,.8,.2,1) both}"
        "@keyframes fade{from{opacity:0}to{opacity:1}}"
        ".fade{animation:fade 1.2s ease both}"
        "@keyframes ping{0%{transform:scale(1);opacity:.75}80%,100%{transform:scale(2.8);opacity:0}}"
        ".ping{transform-box:fill-box;transform-origin:center;animation:ping 1.8s cubic-bezier(0,0,.2,1) infinite}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
        ".blink{animation:blink 1.05s step-end infinite}"
    )


def dot_grid(s: Svg, x: float, y: float, w: float, h: float, cx=0.5, cy=0.45, r=0.6, gap=24, op=0.16) -> str:
    pat, msk = s.uid("p"), s.uid("m")
    fade = s.radial([(0, "#ffffff", 1), (0.6, "#ffffff", .4), (1, "#ffffff", 0)], cx=cx, cy=cy, r=r)
    s.defs.append(f'<pattern id="{pat}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse">'
                  f'<circle cx="{gap / 2}" cy="{gap / 2}" r="1" fill="#ffffff" fill-opacity="{op}"/></pattern>'
                  f'<mask id="{msk}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{fade})"/></mask>')
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pat})" mask="url(#{msk})"/>'


# ============================================================================ hero
def build_hero() -> Svg:
    W, H = 1200, 420
    s = Svg(W, H, "Shaurya Upadhyay: AI Engineer, RAG, AI Agents, Software Engineering",
            "Banner with Shaurya Upadhyay's name, focus areas and a typed line cycling through achievements.")
    keyframes_common(s)
    x0, y0, w, h = 10, 10, 1180, 400
    clip = s.clip_rect(x0, y0, w, h, 28)
    bg = s.linear([(0, "#0b0b0b"), (.5, "#121212"), (1, "#0b0b0b")], 0, 0, 1, 1)
    s.add(f'<g clip-path="url(#{clip})"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#{bg})"/>')
    s.add(dot_grid(s, x0, y0, w, h, r=0.62, op=0.17))
    # a soft spotlight drifting across the grid
    spot = s.radial([(0, "#ffffff", .085), (1, "#ffffff", 0)])
    s.css.append("@keyframes drift{0%,100%{transform:translateX(-260px)}50%{transform:translateX(260px)}}"
                 ".drift{animation:drift 16s ease-in-out infinite}")
    s.add(f'<ellipse class="drift" cx="600" cy="150" rx="420" ry="260" fill="url(#{spot})"/>')
    # thin horizon line
    hz = s.linear([(0, "#ffffff", 0), (.5, "#ffffff", .14), (1, "#ffffff", 0)], 0, 0, 1, 0)
    s.add(f'<rect x="{x0}" y="279" width="{w}" height="1" fill="url(#{hz})"/>')
    s.add("</g>")
    s.add(f'<rect x="{x0 + .5}" y="{y0 + .5}" width="{w - 1}" height="{h - 1}" rx="27.5" stroke="{EDGE}"/>')

    cx = W / 2
    ls = 6
    s.add('<g class="rise" style="animation-delay:.1s">'
          + s.text(cx + ls / 2, 116, "HEY THERE, I'M", "m5", 15, MUTED, anchor="middle", ls=ls) + "</g>")

    name_size, name_ls = 76, 2
    name_w = text_width(NAME, "d7", name_size, name_ls)
    ng = word_grad(s, cx - name_w / 2, cx + name_w / 2)
    shine = s.linear([(0, "#ffffff", 0), (.45, "#ffffff", 0), (.5, "#ffffff", .8), (.55, "#ffffff", 0),
                      (1, "#ffffff", 0)], cx - name_w / 2, 0, cx + name_w / 2, 0, units="userSpaceOnUse",
                     inner=f'<animateTransform attributeName="gradientTransform" type="translate" '
                           f'values="{-name_w:.0f} 0;{-name_w:.0f} 0;{name_w:.0f} 0" keyTimes="0;.55;1" '
                           f'dur="6s" repeatCount="indefinite"/>')
    nx = cx + name_ls / 2
    s.add('<g class="rise" style="animation-delay:.25s">'
          + s.text(nx, 200, NAME, "d7", name_size, f"url(#{ng})", anchor="middle", ls=name_ls)
          + s.text(nx, 200, NAME, "d7", name_size, f"url(#{shine})", anchor="middle", ls=name_ls)
          + "</g>")

    parts = []
    for i, f in enumerate(FOCUS):
        if i:
            parts.append('<tspan fill="#525252">  /  </tspan>')
        parts.append(f"<tspan>{esc(f)}</tspan>")
    s.use_chars("d5", "  /  ".join(FOCUS))
    s.add(f'<g class="rise" style="animation-delay:.4s"><text x="{cx}" y="248" class="d5" font-size="24" '
          f'fill="{SOFT}" text-anchor="middle">{"".join(parts)}</text></g>')

    # typing terminal pill (SMIL: text revealed along a growing path, like a typewriter)
    fs, cw = 19, 19 * 0.6
    max_chars = max(len(t) for t in TYPED)
    pill_w = 2 * 22 + 2 * cw + max_chars * cw + 14
    px, py, ph = cx - pill_w / 2, 296, 44
    s.add(f'<g class="rise" style="animation-delay:.55s">'
          f'<rect x="{px:.1f}" y="{py}" width="{pill_w:.1f}" height="{ph}" rx="12" fill="#0d0d0d" '
          f'stroke="{EDGE_HI}"/>')
    tx, ty = px + 22, py + 28.5
    s.add(s.text(tx, ty, "❯", "m7", fs, GREEN))
    tx += 2 * cw
    slot_type = [len(t) / 26 for t in TYPED]
    hold, erase, gap = 2.3, .55, .35
    slots = [st + hold + erase + gap for st in slot_type]
    total = sum(slots)
    cursor_pts: list[tuple[float, float]] = []
    t0 = 0.0
    for i, line in enumerate(TYPED):
        lw = len(line) * cw + 2
        a, b = t0 / total, (t0 + slot_type[i]) / total
        c, d = (t0 + slot_type[i] + hold) / total, (t0 + slot_type[i] + hold + erase) / total
        full, empty = f"M{tx:.1f} {ty:.1f} h{lw:.1f}", f"M{tx:.1f} {ty:.1f} h0"
        if i == 0:
            kt, vals, base = f"0;{b:.4f};{c:.4f};{d:.4f};1", [empty, full, full, empty, empty], full
        else:
            kt, vals, base = f"0;{a:.4f};{b:.4f};{c:.4f};{d:.4f};1", [empty, empty, full, full, empty, empty], empty
        s.defs.append(f'<path id="tp{i}" d="{base}"><animate attributeName="d" dur="{total:.2f}s" '
                      f'repeatCount="indefinite" keyTimes="{kt}" values="{";".join(vals)}"/></path>')
        s.use_chars("m5", line)
        s.add(f'<text class="m5" font-size="{fs}" fill="{TEXT}"><textPath href="#tp{i}" xlink:href="#tp{i}">'
              f'{esc(line)}</textPath></text>')
        cursor_pts += [(a, tx), (b, tx + lw), (c, tx + lw), (d, tx)]
        t0 += slots[i]
    cursor_pts.append((1.0, tx))
    kt = ";".join(f"{t:.4f}" for t, _ in cursor_pts)
    xs = ";".join(f"{x:.1f}" for _, x in cursor_pts)
    s.add(f'<g class="blink"><rect x="{tx + len(TYPED[0]) * cw + 2:.1f}" y="{ty - 16}" width="10" height="20" '
          f'rx="2" fill="{TEXT}" opacity=".85"><animate attributeName="x" dur="{total:.2f}s" '
          f'repeatCount="indefinite" keyTimes="{kt}" values="{xs}"/></rect></g></g>')

    # availability pill: a light sweeps along its hairline border; the roles carry the gradient
    tag, lead, roles = STATUS
    fs2 = 15.5
    tag_w = text_width(tag, "m7", 11, 2)
    lead_w, roles_w = text_width(lead, "d5", fs2), text_width(roles, "d7", fs2)
    pill_w = 18 + 9 + 12 + tag_w + 12 + 1 + 13 + lead_w + roles_w + 20
    edu_w = 40 + text_width(EDU_CHIP, "m5", 14) + 18
    gapc, py2, ph2 = 14, 352, 38
    x = cx - (pill_w + gapc + edu_w) / 2
    sheen = s.linear([(0, "#ffffff", 0), (.42, "#ffffff", 0), (.5, "#ffffff", .9), (.58, "#ffffff", 0), (1, "#ffffff", 0)],
                     f"{x:.1f}", 0, f"{x + pill_w:.1f}", 0, units="userSpaceOnUse",
                     inner=f'<animateTransform attributeName="gradientTransform" type="translate" '
                           f'values="{-pill_w:.0f} 0;{pill_w:.0f} 0;{pill_w:.0f} 0" keyTimes="0;.6;1" '
                           f'dur="4.5s" repeatCount="indefinite"/>')
    gloss = s.linear([(0, "#ffffff", .07), (.6, "#ffffff", .015)], 0, 0, 0, 1)
    mid = py2 + ph2 / 2
    s.add('<g class="rise" style="animation-delay:.7s">')
    s.add(f'<rect x="{x:.1f}" y="{py2}" width="{pill_w:.1f}" height="{ph2}" rx="{ph2 / 2}" fill="#0e0e0e"/>'
          f'<rect x="{x:.1f}" y="{py2}" width="{pill_w:.1f}" height="{ph2}" rx="{ph2 / 2}" fill="url(#{gloss})"/>'
          f'<rect x="{x + .5:.1f}" y="{py2 + .5}" width="{pill_w - 1:.1f}" height="{ph2 - 1}" rx="{(ph2 - 1) / 2}" '
          f'stroke="{EDGE_HI}"/>'
          f'<rect x="{x + .5:.1f}" y="{py2 + .5}" width="{pill_w - 1:.1f}" height="{ph2 - 1}" rx="{(ph2 - 1) / 2}" '
          f'stroke="url(#{sheen})" stroke-width="1.2"/>')
    dx = x + 22
    s.add(f'<circle cx="{dx:.1f}" cy="{mid}" r="4.5" fill="{GREEN}"/>'
          f'<circle class="ping" cx="{dx:.1f}" cy="{mid}" r="4.5" fill="{GREEN}"/>')
    tx2 = x + 39
    s.add(s.text(tx2, mid + 4, tag, "m7", 11, GREEN, ls=2))
    sx = tx2 + tag_w + 12
    s.add(f'<line x1="{sx:.1f}" y1="{mid - 8}" x2="{sx:.1f}" y2="{mid + 8}" stroke="#3a3a3a"/>')
    lx = sx + 14
    s.add(s.text(lx, mid + 5.5, lead, "d5", fs2, SOFT))
    rg = word_grad(s, lx + lead_w, lx + lead_w + roles_w)
    s.add(s.text(lx + lead_w, mid + 5.5, roles, "d7", fs2, f"url(#{rg})"))
    # education chip
    ex = x + pill_w + gapc
    s.add(f'<rect x="{ex:.1f}" y="{py2 + 2}" width="{edu_w:.1f}" height="{ph2 - 4}" rx="{(ph2 - 4) / 2}" fill="#141414" '
          f'stroke="{EDGE_HI}"/>')
    s.add(icon("cap", ex + 13, mid - 9, 18, MUTED, 1.7))
    s.add(s.text(ex + 38, mid + 5, EDU_CHIP, "m5", 14, SOFT))
    s.add("</g>")
    return s


# ============================================================================ section headers
def build_header(num: str, title: str, subtitle: str) -> Svg:
    W, H = 1200, 128
    s = Svg(W, H, title.title(), f"Section {num}: {title.title()} — {subtitle}")
    keyframes_common(s)
    s.add(s.panel(10, 6, 1180, 116, rx=22, glow_at=(.5, 0)))
    cx, ls, size = W / 2, 5, 34
    tw = text_width(title, "d7", size, ls)
    tg = word_grad(s, cx - tw / 2, cx + tw / 2)
    s.add(s.text(cx, 34, f"— {num} —", "m5", 12.5, DIM, anchor="middle", ls=3, cls="fade"))
    s.add(s.text(cx + ls / 2, 76, title, "d7", size, f"url(#{tg})", anchor="middle", ls=ls, cls="rise"))
    s.add(s.text(cx + 1, 104, subtitle, "m5", 13.5, MUTED, anchor="middle", ls=1.5, cls="fade",
                 style="animation-delay:.3s"))
    y = 63
    inner_l, inner_r = cx - tw / 2 - 34, cx + tw / 2 + 34
    gl = s.linear([(0, "#ffffff", 0), (1, "#ffffff", .28)], 46, 0, inner_l, 0, units="userSpaceOnUse")
    gr = s.linear([(0, "#ffffff", .28), (1, "#ffffff", 0)], inner_r, 0, 1154, 0, units="userSpaceOnUse")
    s.add(f'<path d="M46 {y}H{inner_l:.1f}" stroke="url(#{gl})"/>'
          f'<path d="M{inner_r:.1f} {y}H1154" stroke="url(#{gr})"/>')
    for xd in (inner_l + 8, inner_r - 8):
        s.add(f'<rect x="{xd - 4:.1f}" y="{y - 4}" width="8" height="8" fill="#525252" '
              f'transform="rotate(45 {xd:.1f} {y})"/>')
    glow = s.glow_filter(2.4)
    s.css.append(f"@keyframes sl{{0%{{transform:translateX(0);opacity:0}}10%{{opacity:1}}"
                 f"70%,100%{{transform:translateX(-{inner_l - 60:.0f}px);opacity:0}}}}"
                 f"@keyframes sr{{0%{{transform:translateX(0);opacity:0}}10%{{opacity:1}}"
                 f"70%,100%{{transform:translateX({1140 - inner_r:.0f}px);opacity:0}}}}")
    s.add(f'<circle cx="{inner_l:.1f}" cy="{y}" r="2.2" fill="#ffffff" filter="url(#{glow})" opacity="0" '
          f'style="animation:sl 4.5s ease-in 1s infinite"/>'
          f'<circle cx="{inner_r:.1f}" cy="{y}" r="2.2" fill="#ffffff" filter="url(#{glow})" opacity="0" '
          f'style="animation:sr 4.5s ease-in 1s infinite"/>')
    return s


# ============================================================================ hall of fame
def build_achievements() -> Svg:
    cols, cw, ch, gx, gy = 4, 280, 204, 20, 20
    rows = math.ceil(len(ACHIEVEMENTS) / cols)
    W, H = 1200, rows * ch + (rows - 1) * gy
    s = Svg(W, H, "Hall of fame",
            "; ".join(f"{a['metric']} {a['suffix']} {a['title']} ({a['sub']})".replace("  ", " ")
                      for a in ACHIEVEMENTS))
    keyframes_common(s)
    s.css.append("@keyframes sweep{0%{transform:translateX(-120px) skewX(-18deg)}"
                 "28%,100%{transform:translateX(420px) skewX(-18deg)}}")
    for i, a in enumerate(ACHIEVEMENTS):
        r, c = divmod(i, cols)
        x, y = 10 + c * (cw + gx), r * (ch + gy)
        light, main, deep = ACCENTS[a["accent"]]
        clip = s.clip_rect(x, y, cw, ch, 18)
        s.add(f'<g class="rise" style="animation-delay:{.08 * i:.2f}s">')
        s.add(s.panel(x, y, cw, ch, rx=18, glow_at=(0, 0)))
        band = s.linear([(0, "#ffffff", 0), (.5, "#ffffff", .05), (1, "#ffffff", 0)])
        s.add(f'<g clip-path="url(#{clip})"><rect x="{x}" y="{y}" width="90" height="{ch}" fill="url(#{band})" '
              f'style="animation:sweep 9s ease-in-out {1.2 + .35 * (r + c):.2f}s infinite;'
              f'transform-box:fill-box;transform-origin:center"/></g>')
        s.add(f'<rect x="{x + 20}" y="{y + 22}" width="44" height="44" rx="12" fill="{TILE}" stroke="{TILE_EDGE}"/>')
        s.add(icon(a["icon"], x + 30, y + 32, 24, MUTED, 1.8))
        s.add(s.text(x + cw - 20, y + 49, a["tag"], "m5", 12, DIM, anchor="end", ls=1.6))
        avail = cw - 40
        msize = 44
        while msize > 26:
            mw = text_width(a["metric"], "d7", msize)
            sw = text_width(a["suffix"], "d5", 18) + 9 if a["suffix"] else 0
            if mw + sw <= avail:
                break
            msize -= 1
        mg = s.text_grad(a["accent"], x + 20, y + 120, msize, text_width(a["metric"], "d7", msize))
        s.add(s.text(x + 20, y + 120, a["metric"], "d7", msize, f"url(#{mg})"))
        if a["suffix"]:
            s.add(s.text(x + 20 + text_width(a["metric"], "d7", msize) + 9, y + 120, a["suffix"], "d5", 18, MUTED))
        tsize = fit_size(a["title"], "d5", 18, avail, 14)
        s.add(s.text(x + 20, y + 153, a["title"], "d5", tsize, TEXT))
        ssize = fit_size(a["sub"], "m5", 13.5, avail, 11)
        s.add(s.text(x + 20, y + 180, a["sub"], "m5", ssize, DIM))
        s.add("</g>")
    return s


# ============================================================================ project cards
def build_project(p: dict) -> Svg:
    W, H = 600, 340
    s = Svg(W, H, f"{p['name']} — {p['category'].title()}",
            f"{p['name']}: {p['desc']} " + "; ".join(f"{v} {k}" for v, k in p["metrics"])
            + (f". Recognition: {p['award'].title()}." if p["award"] else "")
            + f" Tech: {', '.join(p['tech'])}.")
    keyframes_common(s)
    light, main, deep = ACCENTS[p["accent"]]
    x0, y0, w, h = 10, 10, 580, 320
    s.add('<g class="rise">')
    s.add(s.panel(x0, y0, w, h, rx=20, glow_at=(1, 0)))
    L, R = x0 + 30, x0 + w - 30
    s.add(f'<rect x="{L}" y="{y0 + 26}" width="50" height="50" rx="14" fill="{TILE}" stroke="{TILE_EDGE}"/>')
    s.add(icon(p["icon"], L + 12, y0 + 38, 26, SOFT, 1.9))
    s.add(s.text(L + 66, y0 + 54, p["name"], "d7", 29, TEXT))
    s.add(s.text(L + 67, y0 + 76, p["category"], "m5", 12.5, light, ls=1.2))
    name_right = L + 66 + text_width(p["name"], "d7", 29)
    if p["award"]:
        afs = 12
        aw = text_width(p["award"], "m7", afs, .6) + 42
        while name_right + 18 > R - aw and afs > 9.5:
            afs -= .5
            aw = text_width(p["award"], "m7", afs, .6) + 42
        ax = R - aw
        assert ax > name_right + 12, f"award pill collides with name on {p['name']}"
        s.add(f'<rect x="{ax:.1f}" y="{y0 + 26}" width="{aw:.1f}" height="27" rx="13.5" fill="{TILE}" '
              f'stroke="{TILE_EDGE}"/>')
        s.add(icon("trophy", ax + 9, y0 + 32, 15, "#fcd34d", 1.6))
        s.add(s.text(ax + 30, y0 + 44.5, p["award"], "m7", afs, "#fcd34d", ls=.6))
    lines = wrap(p["desc"], "d5", 16.5, R - L)
    assert len(lines) <= 3, f"description too long for {p['name']}: {lines}"
    for k, line in enumerate(lines):
        s.add(s.text(L, y0 + 118 + k * 24, line, "d5", 16.5, SOFT if k == 0 else MUTED,
                     cls="fade", style=f"animation-delay:{.15 + .1 * k:.2f}s"))
    my = y0 + 202
    colw = (R - L) / 3
    for k, (val, label) in enumerate(p["metrics"]):
        mx = L + k * colw
        if k:
            s.add(f'<line x1="{mx - 14:.1f}" y1="{my - 30}" x2="{mx - 14:.1f}" y2="{my + 22}" stroke="{EDGE_HI}"/>')
        vsize = fit_size(val, "d7", 30, colw - 26, 20)
        mg = s.text_grad(p["accent"], mx, my, vsize, text_width(val, "d7", vsize))
        s.add(f'<g class="rise" style="animation-delay:{.35 + .12 * k:.2f}s">'
              + s.text(mx, my, val, "d7", vsize, f"url(#{mg})")
              + s.text(mx + 1, my + 22, label.upper(), "m5", 12.5, DIM, ls=1) + "</g>")
    cx_, cy_ = L, y0 + 246
    for t in p["tech"]:
        tw = text_width(t, "m5", 12.5) + 22
        if cx_ + tw > R:
            break
        s.add(f'<rect x="{cx_:.1f}" y="{cy_}" width="{tw:.1f}" height="26" rx="13" fill="{TILE}" stroke="{TILE_EDGE}"/>')
        s.add(s.text(cx_ + 11, cy_ + 17.5, t, "m5", 12.5, SOFT))
        cx_ += tw + 8
    fy = y0 + h - 16
    s.add(s.text(L, fy, f"github.com/{p['repo']}", "m5", 12.5, DIM))
    if p.get("live"):
        label = "LIVE DEMO"
        lw = text_width(label, "m7", 12, 1.2)
        s.add(f'<circle cx="{R - lw - 14:.1f}" cy="{fy - 4.5}" r="4" fill="{GREEN}"/>'
              f'<circle class="ping" cx="{R - lw - 14:.1f}" cy="{fy - 4.5}" r="4" fill="{GREEN}"/>')
        s.add(s.text(R, fy, label, "m7", 12, GREEN, anchor="end", ls=1.2))
    else:
        s.add(s.text(R, fy, "VIEW REPO ↗", "m7", 12, MUTED, anchor="end", ls=1.2))
    s.add("</g>")
    return s


# ============================================================================ tech stack
def build_stack() -> Svg:
    tile, gap, cols = 116, 16, 4
    block_w = cols * tile + (cols - 1) * gap
    mid_gap = 1180 - 2 * 44 - 2 * block_w
    title_h, rows = 46, 2
    block_h = title_h + rows * tile + (rows - 1) * gap
    W = 1200
    H = 10 + 36 + 2 * block_h + 40 + 36 + 10
    s = Svg(W, H, "Tech stack", "; ".join(f"{cat}: {', '.join(t[0] for t in items)}" for cat, _, items in STACK))
    keyframes_common(s)
    s.add(s.panel(10, 10, 1180, H - 20, rx=24, glow_at=(.5, 0)))
    s.css.append("@keyframes pop{from{opacity:0;transform:scale(.86)}to{opacity:1;transform:none}}"
                 ".pop{transform-box:fill-box;transform-origin:center;animation:pop .6s cubic-bezier(.2,.9,.3,1.2) both}"
                 "@keyframes hl{0%,100%{opacity:0}5%{opacity:.5}14%{opacity:0}}")
    tile_fill = s.linear([(0, "#181818"), (1, "#111111")], 0, 0, 0, 1)
    n = 0
    for b, (cat, acc, items) in enumerate(STACK):
        br, bc = divmod(b, 2)
        bx = 10 + 44 + bc * (block_w + mid_gap)
        by = 10 + 36 + br * (block_h + 40)
        light, main, deep = ACCENTS[acc]
        s.add(f'<rect x="{bx}" y="{by + 7}" width="10" height="10" rx="2" fill="#525252" '
              f'transform="rotate(45 {bx + 5} {by + 12})"/>')
        s.add(s.text(bx + 22, by + 18, cat, "d7", 16, light, ls=3))
        lx = bx + 22 + text_width(cat, "d7", 16, 3) + 14
        lg = s.linear([(0, "#ffffff", .22), (1, "#ffffff", 0)], lx, 0, bx + block_w, 0, units="userSpaceOnUse")
        s.add(f'<path d="M{lx:.1f} {by + 12}H{bx + block_w}" stroke="url(#{lg})"/>')
        for k, (label, slug, hex_) in enumerate(items):
            r, c = divmod(k, cols)
            tx, ty = bx + c * (tile + gap), by + title_h + r * (tile + gap)
            s.add(f'<g class="pop" style="animation-delay:{.04 * n:.2f}s">'
                  f'<rect x="{tx}" y="{ty}" width="{tile}" height="{tile}" rx="18" fill="url(#{tile_fill})" stroke="{EDGE}"/>'
                  f'<rect x="{tx + .5}" y="{ty + .5}" width="{tile - 1}" height="{tile - 1}" rx="17.5" '
                  f'stroke="#ffffff" stroke-width="1.2" opacity="0" '
                  f'style="animation:hl 9s ease-in-out {2 + .18 * n:.2f}s infinite"/>'
                  + brand_glyph(slug, hex_, tx + (tile - 42) / 2, ty + 22, 42)
                  + s.text(tx + tile / 2, ty + 96, label, "m5", fit_size(label, "m5", 13.5, tile - 14, 10), SOFT,
                           anchor="middle")
                  + "</g>")
            n += 1
    return s


# ============================================================================ buttons
def build_button(label: str, slug: str, hex_: str) -> Svg:
    fs, H = 20, 64
    tw = text_width(label, "d7", fs, .5)
    W = int(30 + 28 + 14 + tw + 30 + 12)
    s = Svg(W, H, label, f"{label} button")
    s.add(s.panel(2, 2, W - 4, H - 4, rx=(H - 4) / 2, glow_at=(0, .5)))
    s.add(f'<rect x="2.5" y="2.5" width="{W - 5}" height="{H - 5}" rx="{(H - 5) / 2}" stroke="{EDGE_HI}"/>')
    clip = s.clip_rect(2, 2, W - 4, H - 4, (H - 4) / 2)
    band = s.linear([(0, "#ffffff", 0), (.5, "#ffffff", .1), (1, "#ffffff", 0)])
    s.css.append(f"@keyframes sh{{0%{{transform:translateX(-80px) skewX(-20deg)}}"
                 f"35%,100%{{transform:translateX({W + 40}px) skewX(-20deg)}}}}")
    s.add(f'<g clip-path="url(#{clip})"><rect x="0" y="0" width="60" height="{H}" fill="url(#{band})" '
          f'style="animation:sh 6s ease-in-out 1.5s infinite;transform-box:fill-box;transform-origin:center"/></g>')
    s.add(brand_glyph(slug, hex_, 30, (H - 28) / 2, 28))
    s.add(s.text(30 + 28 + 14, H / 2 + 7, label, "d7", fs, TEXT, ls=.5))
    return s


# ============================================================================ footer
def build_footer() -> Svg:
    W, H = 1200, 220
    s = Svg(W, H, "Thanks for visiting", "Thanks for stopping by! Let's build AI that ships.")
    keyframes_common(s)
    x0, y0, w, h = 10, 10, 1180, 200
    clip = s.clip_rect(x0, y0, w, h, 28)
    s.add(s.panel(x0, y0, w, h, rx=28, glow_at=(.5, 1)))
    s.add(f'<g clip-path="url(#{clip})">')
    s.add(dot_grid(s, x0, y0, w, h, cy=0.2, r=0.55, op=0.12))
    period = 300
    for k, (amp, base, dur, op) in enumerate([(10, 172, 14, .05), (13, 180, 10, .07), (9, 190, 7, .09)]):
        pts = [f"M0 {base}"]
        for xx in range(0, W + period + 1, 10):
            pts.append(f"L{xx} {base + amp * math.sin(2 * math.pi * xx / period + k):.1f}")
        pts.append(f"L{W + period} {H}L0 {H}Z")
        g = s.linear([(0, "#ffffff", op), (1, "#ffffff", op * .2)], 0, 0, 0, 1)
        s.css.append(f"@keyframes wv{k}{{from{{transform:translateX(0)}}to{{transform:translateX(-{period}px)}}}}")
        s.add(f'<path d="{"".join(pts)}" fill="url(#{g})" style="animation:wv{k} {dur}s linear infinite"/>')
    s.add("</g>")
    cx = W / 2
    title = "Thanks for stopping by!"
    tw = text_width(title, "d7", 34)
    tg = word_grad(s, cx - tw / 2, cx + tw / 2)
    s.add(s.text(cx, 82, title, "d7", 34, f"url(#{tg})", anchor="middle", cls="rise"))
    s.add(s.text(cx + .5, 118, "let's build AI that ships", "m5", 16, MUTED, anchor="middle",
                 ls=1, cls="fade", style="animation-delay:.3s"))
    return s


# ============================================================================ main
def main() -> None:
    print("building static artwork ->", ASSETS)
    write("hero.svg", build_hero())
    for key, num, title, sub in HEADERS:
        write(f"headers/{key}.svg", build_header(num, title, sub))
    write("achievements.svg", build_achievements())
    for p in PROJECTS:
        write(f"projects/{p['slug']}.svg", build_project(p))
    write("tech-stack.svg", build_stack())
    for key, label, slug, hex_ in BUTTONS:
        write(f"buttons/{key}.svg", build_button(label, slug, hex_))
    write("footer.svg", build_footer())


if __name__ == "__main__":
    main()
