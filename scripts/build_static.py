#!/usr/bin/env python3
"""Generate the hand-designed, animated SVGs used by README.md.

    python scripts/build_static.py

Everything the artwork says lives in the CONTENT section below; edit it and re-run.
Live GitHub numbers are rendered separately by scripts/github_stats.py (GitHub Actions).
"""
from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svgkit import (ACCENTS, CYAN, DIM, EDGE, EDGE_HI, GOLD, GREEN, MUTED, PINK, SOFT, TEXT, VIOLET,  # noqa: E402
                    Svg, esc, fit_size, http_get, icon, legible, text_width, wrap)

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
# Simple Icons drops some brands over time, so a slug may pin its own release: "name@version".
SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@{}/icons/{}.svg"
SI_VERSION = "16.35.0"

# ============================================================================ CONTENT
NAME = "SHAURYA UPADHYAY"
FOCUS = ["Agentic AI", "RAG", "Graph Systems", "Data", "Cloud"]
TYPED = [
    "building agents that investigate, retrieve & act",
    "#1 of 28,017 in a live-proctored analytics test",
    "top 25 · TigerGraph × Hacker House Goa 2026",
    "top 100 of 1,400+ · XPRIZE Build with Gemini",
    "rank 14 of 2,200+ · IIT Madras Synaptix Frontier AI",
    "$5,000 Solana Foundation grantee · OWASP contributor",
]
CHIPS = [("dot", "Open to AI/ML & SWE internships", GREEN),
         ("cap", "B.Tech CSE · Manipal University Jaipur '29", CYAN)]
HERO_TAGS = {"left": ["LangGraph", "RAG", "Gemini", "FastAPI"],
             "right": ["TigerGraph", "GSQL", "Bedrock", "BigQuery"]}

# 4 x 3 wall; accents form a Latin square so every row and column has one of each colour.
ACHIEVEMENTS = [
    dict(icon="trophy", tag="ASSESSMENT", metric="#1", suffix="/ 28,017", title="Data Analytics Assessment",
         sub="Bluestock · top 0.004%", accent="gold"),
    dict(icon="graph", tag="HACKATHON", metric="Top 25", suffix="", title="TigerGraph × Hacker House",
         sub="Goa 2026 · fraud agents", accent="cyan"),
    dict(icon="globe", tag="GLOBAL", metric="Top 100", suffix="/ 1,400+", title="XPRIZE Build with Gemini",
         sub="top 7% worldwide", accent="violet"),
    dict(icon="coin", tag="GRANT", metric="$5,000", suffix="", title="Solana Foundation",
         sub="security audit subsidy", accent="pink"),
    dict(icon="target", tag="HACKATHON", metric="#14", suffix="/ 2,200+", title="IIT Madras Synaptix",
         sub="Frontier AI · top 1%", accent="pink"),
    dict(icon="merge", tag="OPEN SOURCE", metric="2", suffix="PRs merged", title="OWASP OpenCRE",
         sub="flagship · #837 · #993", accent="gold"),
    dict(icon="rocket", tag="HACKATHON", metric="Top 10", suffix="/ 232", title="100x School × Superteam",
         sub="India · $450 prize", accent="cyan"),
    dict(icon="code", tag="OPEN SOURCE", metric="#65", suffix="/ 2,055", title="OpenCode'25",
         sub="about the top 3%", accent="violet"),
    dict(icon="medal", tag="NATIONALS", metric="Finalist", suffix="", title="CraftNCode Nationals",
         sub="with Sarthi Kalyan", accent="violet"),
    dict(icon="users", tag="WIKIMEDIA", metric="Top 100", suffix="nationally", title="WikiTech: Road to Wiki",
         sub="selected · cohort 2", accent="pink"),
    dict(icon="award", tag="UNIVERSITY", metric="Award", suffix="2026", title="MUJ Student Excellence",
         sub="CSE · hackathon category", accent="gold"),
    dict(icon="cap", tag="SCHOLARSHIP", metric="Graduate", suffix="", title="AWS AI & ML Scholars",
         sub="fully funded nanodegree", accent="cyan"),
]

PROJECTS = [
    dict(slug="casevera", name="CaseVera", icon="search", accent="cyan",
         category="AGENTIC FRAUD INVESTIGATION", award="TOP 25 · TIGERGRAPH × HHG GOA",
         desc="Policy-constrained investigation agent: multi-hop graph traversal, point-in-time GraphRAG, "
              "provenance-tracked evidence and SAR narratives written back to TigerGraph.",
         metrics=[("10", "GSQL queries"), ("2 / 2", "hidden patterns"), ("617K", "graph vertices")],
         tech=["TigerGraph", "GSQL", "GraphRAG", "Python", "React"],
         repo="BEAST04289/CaseVera", live="casevera.vercel.app"),
    dict(slug="sarthi-kalyan", name="Sarthi Kalyan", icon="users", accent="violet",
         category="AI WELFARE SCHEME AGENT", award="TOP 100 / 1,400+ · XPRIZE",
         desc="Multi-agent system matching citizens to 750+ government welfare schemes with dual-mode "
              "retrieval, on Google Cloud with WhatsApp and web interfaces.",
         metrics=[("750+", "schemes"), ("Top 7%", "XPRIZE global"), ("Finalist", "CraftNCode")],
         tech=["LangGraph", "Gemini", "FastAPI", "Next.js", "BigQuery"],
         repo="BEAST04289/SchemeBot"),
    dict(slug="iwebify", name="iWebify", icon="code", accent="pink",
         category="AI APPLICATION COMPILER", award=None,
         desc="9-stage compiler that turns natural-language requirements into validated, executable app "
              "schemas, with a targeted repair engine driven by exact Pydantic errors.",
         metrics=[("9", "pipeline stages"), ("20", "eval prompts"), ("4", "tracked KPIs")],
         tech=["LangGraph", "FastAPI", "Pydantic", "OpenRouter", "Docker"],
         repo="BEAST04289/iWEBIFY"),
    dict(slug="shield", name="SHIELD", icon="shield", accent="gold",
         category="ANTI-SCAM AI FOR SENIORS", award=None,
         desc="AWS scam-detection platform for senior citizens with a DynamoDB Scam Fingerprint Network "
              "and Hindi voice-first, accessibility-focused interfaces.",
         metrics=[("4.2s", "was 8 minutes"), ("91%", "accuracy"), ("97%", "lower API cost")],
         tech=["Bedrock", "Textract", "Polly", "DynamoDB", "EC2"],
         repo="BEAST04289/AWS_AI-FOR-BHARAT"),
    dict(slug="sentinel", name="Sentinel", icon="pulse", accent="green",
         category="FINANCIAL INTELLIGENCE AGENT", award="RANK 14 / 2,200+ · IIT MADRAS",
         desc="LangGraph agent that parses SEC filings and raises risk alerts, using local embeddings on "
              "ChromaDB + FAISS to cut inference API cost to zero.",
         metrics=[("150ms", "filing parse"), ("<7s", "risk alerts"), ("$0", "inference API")],
         tech=["LangGraph", "ChromaDB", "FAISS", "FastAPI"],
         repo="BEAST04289/Sentinel"),
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
    ("AI · AGENTS", "violet", [("LangGraph", "langgraph", "1C3C3C"), ("Gemini", "googlegemini", "8E75B2"),
                               ("Bedrock", "amazonwebservices@14.15.0", "FF9900"), ("Hugging Face", "huggingface", "FFD21E"),
                               ("ChromaDB", "@chroma", "FFDE2D"), ("FAISS", "meta", "0467DF"),
                               ("Qdrant", "qdrant", "DC244C"), ("RAG", "@search", "A78BFA")]),
    ("GRAPH · DATA", "pink", [("TigerGraph", "@graph", "F58220"), ("PostgreSQL", "postgresql", "4169E1"),
                              ("SQLite", "sqlite", "003B57"), ("BigQuery", "googlebigquery", "669DF6"),
                              ("Pandas", "pandas", "150458"), ("NumPy", "numpy", "4DABCF"),
                              ("Plotly", "plotly", "3F4F75"), ("Streamlit", "streamlit", "FF4B4B")]),
    ("BACKEND · CLOUD", "gold", [("FastAPI", "fastapi", "009688"), ("Pydantic", "pydantic", "E92063"),
                                 ("Next.js", "nextdotjs", "FFFFFF"), ("React", "react", "61DAFB"),
                                 ("Docker", "docker", "2496ED"), ("AWS", "amazonwebservices@14.15.0", "FF9900"),
                                 ("Google Cloud", "googlecloud", "4285F4"), ("Linux", "linux", "FCC624")]),
]

BUTTONS = [("linkedin", "LinkedIn", "linkedin@13.21.0", "0A66C2"),
           ("email", "Email", "gmail", "EA4335"),
           ("telegram", "Telegram", "telegram", "26A5E4")]

HEADERS = [
    ("achievements", "01", "HALL OF FAME", "ranks · grants · awards · open source"),
    ("projects", "02", "FEATURED BUILDS", "agents · graphs · retrieval · cloud"),
    ("stack", "03", "TECH ARSENAL", "the tools I ship with"),
    ("experience", "04", "EXPERIENCE", "industry · open source · community"),
    ("pulse", "05", "GITHUB PULSE", "live numbers · refreshed daily by GitHub Actions"),
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


# ============================================================================ hero
def build_hero() -> Svg:
    W, H = 1200, 420
    s = Svg(W, H, "Shaurya Upadhyay: Agentic AI, RAG, Graph Systems, Data and Cloud",
            "Animated banner with Shaurya Upadhyay's name, focus areas, a typed line cycling through "
            "achievements, and a live graph network in the background.")
    keyframes_common(s)
    x0, y0, w, h = 10, 10, 1180, 400
    clip = s.clip_rect(x0, y0, w, h, 28)
    bg = s.linear([(0, "#050913"), (0.5, "#0a1024"), (1, "#0d0a20")], 0, 0, 1, 1)
    s.add(f'<g clip-path="url(#{clip})"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#{bg})"/>')

    # aurora blobs drifting slowly
    s.css.append(
        "@keyframes dA{0%,100%{transform:translate(0,0)}50%{transform:translate(70px,36px)}}"
        "@keyframes dB{0%,100%{transform:translate(0,0)}50%{transform:translate(-64px,44px)}}"
        "@keyframes dC{0%,100%{transform:translate(0,0)}50%{transform:translate(52px,-34px)}}"
        ".dA{animation:dA 19s ease-in-out infinite}.dB{animation:dB 23s ease-in-out infinite}"
        ".dC{animation:dC 27s ease-in-out infinite}")
    for cx, cy, r, col, op, cls in [(150, 40, 360, CYAN, .26, "dA"), (1070, 70, 340, VIOLET, .30, "dB"),
                                    (620, 500, 440, PINK, .17, "dC")]:
        g = s.radial([(0, col, op), (1, col, 0)])
        s.add(f'<circle class="{cls}" cx="{cx}" cy="{cy}" r="{r}" fill="url(#{g})"/>')

    # faint grid that fades out towards the edges
    pat, msk = s.uid("p"), s.uid("m")
    fade = s.radial([(0, "#ffffff", 1), (0.7, "#ffffff", .35), (1, "#ffffff", 0)], r=0.62)
    s.defs.append(f'<pattern id="{pat}" width="40" height="40" patternUnits="userSpaceOnUse">'
                  f'<path d="M40 0H0V40" stroke="#94a3b8" stroke-opacity=".08"/></pattern>'
                  f'<mask id="{msk}"><rect x="0" y="0" width="{W}" height="{H}" fill="url(#{fade})"/></mask>')
    s.add(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#{pat})" mask="url(#{msk})"/>')

    # ---- knowledge-graph network in the two side gutters
    rnd = random.Random(42)
    anchors = {"left": [(152, 88), (184, 196), (142, 286), (196, 356)],
               "right": [(1048, 80), (1018, 186), (1060, 280), (1022, 352)]}
    nodes: list[tuple[float, float, str, str | None]] = []
    for side, (lo, hi) in (("left", (34, 214)), ("right", (986, 1166))):
        pts = [(x, y, side, tag) for (x, y), tag in zip(anchors[side], HERO_TAGS[side])]
        tries = 0
        while len(pts) < 13 and tries < 4000:
            tries += 1
            p = (rnd.uniform(lo, hi), rnd.uniform(34, 386))
            label_clear = all(not (q[3] and abs(p[1] - q[1]) < 24 and
                                   (q[0] - 112 < p[0] < q[0] + 14 if side == "left" else q[0] - 14 < p[0] < q[0] + 112))
                              for q in pts)
            if label_clear and all(math.dist(p, q[:2]) > 50 for q in pts):
                pts.append((p[0], p[1], side, None))
        nodes += pts
    edges = set()
    for i, a in enumerate(nodes):
        near = sorted((math.dist(a[:2], b[:2]), j) for j, b in enumerate(nodes) if j != i and b[2] == a[2])
        for d, j in near[:3]:
            if d < 150:
                edges.add(tuple(sorted((i, j))))
    edges = sorted(edges)
    edge_grad = s.linear([(0, CYAN, .55), (1, VIOLET, .55)], 0, 0, 1, 1)
    s.add('<g stroke-width="1">')
    for i, j in edges:
        (ax, ay, *_), (bx, by, *_) = nodes[i], nodes[j]
        s.add(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="url(#{edge_grad})" '
              f'stroke-opacity=".38"/>')
    # two long arcs linking the clusters across the top: "retrieval" flowing between worlds
    r0 = sum(1 for n in nodes if n[2] == "left")  # first right-cluster node (its anchors come first)
    arcs = [f"M{nodes[0][0]:.0f} {nodes[0][1]:.0f} C 420 -6, 780 -6, {nodes[r0][0]:.0f} {nodes[r0][1]:.0f}",
            f"M{nodes[3][0]:.0f} {nodes[3][1]:.0f} C 430 420, 770 420, {nodes[r0 + 3][0]:.0f} {nodes[r0 + 3][1]:.0f}"]
    for k, d in enumerate(arcs):
        s.add(f'<path id="arc{k}" d="{d}" stroke="url(#{edge_grad})" stroke-opacity=".22" stroke-dasharray="3 7"/>')
    s.add("</g>")

    glow = s.glow_filter(2.6)
    s.css.append("@keyframes tw{0%,100%{opacity:.5}50%{opacity:1}}")
    for i, (x, y, side, tag) in enumerate(nodes):
        col = [CYAN, VIOLET, PINK, "#7dd3fc"][i % 4] if side == "left" else [VIOLET, PINK, CYAN, "#c4b5fd"][i % 4]
        r = 4.2 if tag else rnd.choice((2.2, 2.6, 3.0))
        dur, delay = rnd.uniform(2.6, 4.8), rnd.uniform(-4, 0)
        s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" filter="url(#{glow})" '
              f'style="animation:tw {dur:.2f}s ease-in-out {delay:.2f}s infinite"/>')
        if tag:
            s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" stroke="{col}" stroke-opacity=".35"/>')
            if side == "left":
                s.add(s.text(x - 16, y + 4.5, tag, "m5", 13, "#7c8aa3", anchor="end"))
            else:
                s.add(s.text(x + 16, y + 4.5, tag, "m5", 13, "#7c8aa3"))

    # packets travelling along edges (CSS, so prefers-reduced-motion stops them)
    for k, (i, j) in enumerate(rnd.sample(edges, 16)):
        (ax, ay, *_), (bx, by, *_) = nodes[i], nodes[j]
        if rnd.random() < .5:
            ax, ay, bx, by = bx, by, ax, ay
        dur = math.dist((ax, ay), (bx, by)) / 38 + 1.2
        s.css.append(f"@keyframes pk{k}{{0%{{transform:translate({ax:.0f}px,{ay:.0f}px);opacity:0}}"
                     f"15%,85%{{opacity:1}}100%{{transform:translate({bx:.0f}px,{by:.0f}px);opacity:0}}}}")
        s.add(f'<circle r="2.3" fill="#e0f2fe" filter="url(#{glow})" opacity="0" '
              f'style="animation:pk{k} {dur:.2f}s linear {rnd.uniform(-6, 0):.2f}s infinite"/>')
    for k in range(2):  # pulses riding the long arcs (SMIL motion along a curve)
        for n, delay in enumerate((0, 3.5)):
            s.add(f'<circle r="2.6" fill="{[CYAN, PINK][k]}" filter="url(#{glow})" opacity="0">'
                  f'<animateMotion dur="7s" begin="{delay + k * 1.7:.1f}s" repeatCount="indefinite" '
                  f'keyPoints="{"0;1" if k == 0 else "1;0"}" keyTimes="0;1" calcMode="linear">'
                  f'<mpath href="#arc{k}" xlink:href="#arc{k}"/></animateMotion>'
                  f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="7s" '
                  f'begin="{delay + k * 1.7:.1f}s" repeatCount="indefinite"/></circle>')
    s.add("</g>")  # end clip

    # ---- border
    border = s.linear([(0, CYAN, .7), (.5, VIOLET, .25), (1, PINK, .7)], 0, 0, 1, 1)
    s.add(f'<rect x="{x0 + .75}" y="{y0 + .75}" width="{w - 1.5}" height="{h - 1.5}" rx="27.5" '
          f'stroke="url(#{border})" stroke-width="1.5"/>')

    # ---- headline block
    cx = W / 2
    ls = 6
    s.add(f'<g class="rise" style="animation-delay:.1s">'
          + s.text(cx + ls / 2, 124, "HEY THERE, I'M", "m5", 15, "#67e8f9", anchor="middle", ls=ls) + "</g>")

    name_size, name_ls = 76, 2
    name_w = text_width(NAME, "d7", name_size, name_ls)
    ng = s.linear([(0, "#67e8f9"), (.48, "#a78bfa"), (1, "#f472b6")], cx - name_w / 2, 0, cx + name_w / 2, 0,
                  units="userSpaceOnUse")
    shine = s.linear([(0, "#ffffff", 0), (.45, "#ffffff", 0), (.5, "#ffffff", .85), (.55, "#ffffff", 0),
                      (1, "#ffffff", 0)], cx - name_w / 2, 0, cx + name_w / 2, 0, units="userSpaceOnUse",
                     inner=f'<animateTransform attributeName="gradientTransform" type="translate" '
                           f'values="{-name_w:.0f} 0;{-name_w:.0f} 0;{name_w:.0f} 0" keyTimes="0;.55;1" '
                           f'dur="6s" repeatCount="indefinite"/>')
    blur = s.uid("f")
    s.defs.append(f'<filter id="{blur}" x="-20%" y="-60%" width="140%" height="220%">'
                  f'<feGaussianBlur stdDeviation="16"/></filter>')
    nx = cx + name_ls / 2
    s.add(f'<g class="rise" style="animation-delay:.25s">'
          + s.text(nx, 208, NAME, "d7", name_size, VIOLET, anchor="middle", ls=name_ls,
                   extra=f'opacity=".45" filter="url(#{blur})"')
          + s.text(nx, 208, NAME, "d7", name_size, f"url(#{ng})", anchor="middle", ls=name_ls)
          + s.text(nx, 208, NAME, "d7", name_size, f"url(#{shine})", anchor="middle", ls=name_ls)
          + "</g>")

    # focus line with coloured separators
    seps = [CYAN, VIOLET, PINK, GOLD]
    parts = []
    for i, f in enumerate(FOCUS):
        if i:
            parts.append(f'<tspan fill="{seps[(i - 1) % 4]}">  ·  </tspan>')
        parts.append(f"<tspan>{f}</tspan>")
    s.use_chars("d5", "  ·  ".join(FOCUS))
    s.add(f'<g class="rise" style="animation-delay:.4s"><text x="{cx}" y="258" class="d5" font-size="25" '
          f'fill="{SOFT}" text-anchor="middle">{"".join(parts)}</text></g>')

    # ---- typing terminal pill (SMIL: text revealed along a growing path, like a typewriter)
    fs, cw = 19, 19 * 0.6
    max_chars = max(len(t) for t in TYPED)
    pill_w = 2 * 22 + 2 * cw + max_chars * cw + 14
    px, py, ph = cx - pill_w / 2, 290, 44
    s.add(f'<g class="rise" style="animation-delay:.55s">'
          f'<rect x="{px:.1f}" y="{py}" width="{pill_w:.1f}" height="{ph}" rx="12" fill="#0b1222" '
          f'fill-opacity=".72" stroke="{EDGE_HI}" stroke-opacity=".7"/>')
    tx, ty = px + 22, py + 28.5
    s.add(s.text(tx, ty, "❯", "m7", fs, GREEN))
    tx += 2 * cw
    slot_type = [len(t) / 26 for t in TYPED]  # ~26 chars per second
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
          f'rx="2" fill="{CYAN}" opacity=".85"><animate attributeName="x" dur="{total:.2f}s" '
          f'repeatCount="indefinite" keyTimes="{kt}" values="{xs}"/></rect></g></g>')

    # ---- chips
    cfs = 14.5
    widths = [44 + text_width(t, "m5", cfs) + 18 for _, t, _ in CHIPS]
    gapc = 16
    x = cx - (sum(widths) + gapc * (len(CHIPS) - 1)) / 2
    s.add('<g class="rise" style="animation-delay:.7s">')
    for (kind, label, col), cwid in zip(CHIPS, widths):
        s.add(f'<rect x="{x:.1f}" y="352" width="{cwid:.1f}" height="34" rx="17" fill="{col}" fill-opacity=".08" '
              f'stroke="{col}" stroke-opacity=".45"/>')
        if kind == "dot":
            s.add(f'<circle cx="{x + 22:.1f}" cy="369" r="4.5" fill="{col}"/>'
                  f'<circle class="ping" cx="{x + 22:.1f}" cy="369" r="4.5" fill="{col}"/>')
        else:
            s.add(icon(kind, x + 13, 360, 18, col, 1.7))
        s.add(s.text(x + 38, 374, label, "m5", cfs, TEXT))
        x += cwid + gapc
    s.add("</g>")
    return s


# ============================================================================ section headers
def build_header(num: str, title: str, subtitle: str) -> Svg:
    W, H = 1200, 128
    s = Svg(W, H, title.title(), f"Section {num}: {title.title()} — {subtitle}")
    keyframes_common(s)
    s.add(s.panel(10, 6, 1180, 116, rx=22))
    cx, ls, size = W / 2, 5, 34
    tw = text_width(title, "d7", size, ls)
    tg = s.linear([(0, "#67e8f9"), (.5, "#a78bfa"), (1, "#f472b6")], cx - tw / 2, 0, cx + tw / 2, 0,
                  units="userSpaceOnUse")
    s.add(s.text(cx, 34, f"— {num} —", "m5", 12.5, "#67e8f9", anchor="middle", ls=3, cls="fade"))
    s.add(s.text(cx + ls / 2, 76, title, "d7", size, f"url(#{tg})", anchor="middle", ls=ls, cls="rise"))
    s.add(s.text(cx + 1, 104, subtitle, "m5", 13.5, MUTED, anchor="middle", ls=1.5, cls="fade",
                 style="animation-delay:.3s"))
    # symmetric rails with diamonds and outward-travelling sparks
    y = 63
    inner_l, inner_r = cx - tw / 2 - 34, cx + tw / 2 + 34
    gl = s.linear([(0, VIOLET, 0), (1, CYAN, .9)], 46, 0, inner_l, 0, units="userSpaceOnUse")
    gr = s.linear([(0, PINK, .9), (1, VIOLET, 0)], inner_r, 0, 1154, 0, units="userSpaceOnUse")
    s.add(f'<path d="M46 {y}H{inner_l:.1f}" stroke="url(#{gl})" stroke-width="1.5"/>'
          f'<path d="M{inner_r:.1f} {y}H1154" stroke="url(#{gr})" stroke-width="1.5"/>')
    for xd, col in ((inner_l + 8, CYAN), (inner_r - 8, PINK)):
        s.add(f'<rect x="{xd - 4.5:.1f}" y="{y - 4.5}" width="9" height="9" fill="{col}" '
              f'transform="rotate(45 {xd:.1f} {y})"/>')
    glow = s.glow_filter(2.4)
    s.css.append(f"@keyframes sl{{0%{{transform:translateX(0);opacity:0}}10%{{opacity:1}}"
                 f"70%,100%{{transform:translateX(-{inner_l - 60:.0f}px);opacity:0}}}}"
                 f"@keyframes sr{{0%{{transform:translateX(0);opacity:0}}10%{{opacity:1}}"
                 f"70%,100%{{transform:translateX({1140 - inner_r:.0f}px);opacity:0}}}}")
    s.add(f'<circle cx="{inner_l:.1f}" cy="{y}" r="2.6" fill="#a5f3fc" filter="url(#{glow})" opacity="0" '
          f'style="animation:sl 4.5s ease-in 1s infinite"/>'
          f'<circle cx="{inner_r:.1f}" cy="{y}" r="2.6" fill="#fbcfe8" filter="url(#{glow})" opacity="0" '
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
                 "28%,100%{transform:translateX(420px) skewX(-18deg)}}"
                 "@keyframes halo{0%,100%{opacity:.25}50%{opacity:.7}}")
    for i, a in enumerate(ACHIEVEMENTS):
        r, c = divmod(i, cols)
        x, y = 10 + c * (cw + gx), r * (ch + gy)
        light, main, deep = ACCENTS[a["accent"]]
        clip = s.clip_rect(x, y, cw, ch, 18)
        s.add(f'<g class="rise" style="animation-delay:{.08 * i:.2f}s">')
        s.add(s.panel(x, y, cw, ch, rx=18, accent=main, glow_at=(0, 0), glow_op=.2))
        # shimmer sweep, staggered along the diagonal
        band = s.linear([(0, "#ffffff", 0), (.5, "#ffffff", .07), (1, "#ffffff", 0)])
        s.add(f'<g clip-path="url(#{clip})"><rect x="{x}" y="{y}" width="90" height="{ch}" fill="url(#{band})" '
              f'style="animation:sweep 9s ease-in-out {1.2 + .35 * (r + c):.2f}s infinite;'
              f'transform-box:fill-box;transform-origin:center" opacity=".9"/></g>')
        s.add(f'<rect x="{x + 22}" y="{y}" width="52" height="3" rx="1.5" fill="{main}"/>')
        # icon tile
        s.add(f'<rect x="{x + 20}" y="{y + 22}" width="44" height="44" rx="12" fill="{main}" fill-opacity=".1" '
              f'stroke="{main}" stroke-opacity=".45"/>'
              f'<rect x="{x + 20}" y="{y + 22}" width="44" height="44" rx="12" stroke="{light}" stroke-opacity=".6" '
              f'style="animation:halo 4s ease-in-out {.3 * i:.1f}s infinite" opacity=".25"/>')
        s.add(icon(a["icon"], x + 30, y + 32, 24, light, 1.8))
        s.add(s.text(x + cw - 20, y + 49, a["tag"], "m5", 12, light, anchor="end", ls=1.6,
                     extra='opacity=".85"'))
        # metric (+ suffix) auto-fitted to the card width
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
def build_project(p: dict, index: int) -> Svg:
    W, H = 600, 340
    s = Svg(W, H, f"{p['name']} — {p['category'].title()}",
            f"{p['name']}: {p['desc']} " + "; ".join(f"{v} {k}" for v, k in p["metrics"])
            + (f". Recognition: {p['award'].title()}." if p["award"] else "")
            + f" Tech: {', '.join(p['tech'])}.")
    keyframes_common(s)
    light, main, deep = ACCENTS[p["accent"]]
    x0, y0, w, h = 10, 10, 580, 320
    s.add('<g class="rise">')
    s.add(s.panel(x0, y0, w, h, rx=20, accent=main, glow_at=(1, 0), glow_op=.2))
    s.add(f'<rect x="{x0 + 30}" y="{y0}" width="64" height="3" rx="1.5" fill="{main}"/>')
    L, R = x0 + 30, x0 + w - 30
    # icon tile + name + category
    s.add(f'<rect x="{L}" y="{y0 + 26}" width="50" height="50" rx="14" fill="{main}" fill-opacity=".1" '
          f'stroke="{main}" stroke-opacity=".5"/>')
    s.add(icon(p["icon"], L + 12, y0 + 38, 26, light, 1.9))
    s.add(s.text(L + 66, y0 + 54, p["name"], "d7", 29, TEXT))
    s.add(s.text(L + 67, y0 + 76, p["category"], "m5", 13, light, ls=1.3))
    name_right = L + 66 + text_width(p["name"], "d7", 29)
    if p["award"]:
        afs = 12
        aw = text_width(p["award"], "m7", afs, .6) + 42
        while name_right + 18 > R - aw and afs > 9.5:
            afs -= .5
            aw = text_width(p["award"], "m7", afs, .6) + 42
        ax = R - aw
        assert ax > name_right + 12, f"award pill collides with name on {p['name']}"
        s.add(f'<rect x="{ax:.1f}" y="{y0 + 26}" width="{aw:.1f}" height="27" rx="13.5" fill="{GOLD}" '
              f'fill-opacity=".1" stroke="{GOLD}" stroke-opacity=".55"/>')
        s.add(icon("trophy", ax + 9, y0 + 32, 15, GOLD, 1.6))
        s.add(s.text(ax + 30, y0 + 44.5, p["award"], "m7", afs, "#fde68a", ls=.6))
    # description
    lines = wrap(p["desc"], "d5", 16.5, R - L)
    assert len(lines) <= 3, f"description too long for {p['name']}: {lines}"
    for k, line in enumerate(lines):
        s.add(s.text(L, y0 + 118 + k * 24, line, "d5", 16.5, SOFT if k == 0 else MUTED,
                     cls="fade", style=f"animation-delay:{.15 + .1 * k:.2f}s"))
    # metrics strip
    my = y0 + 202
    colw = (R - L) / 3
    for k, (val, label) in enumerate(p["metrics"]):
        mx = L + k * colw
        if k:
            s.add(f'<line x1="{mx - 14:.1f}" y1="{my - 30}" x2="{mx - 14:.1f}" y2="{my + 22}" stroke="{EDGE_HI}" '
                  f'stroke-opacity=".7"/>')
        vsize = fit_size(val, "d7", 30, colw - 26, 20)
        mg = s.text_grad(p["accent"], mx, my, vsize, text_width(val, "d7", vsize))
        s.add(f'<g class="rise" style="animation-delay:{.35 + .12 * k:.2f}s">'
              + s.text(mx, my, val, "d7", vsize, f"url(#{mg})")
              + s.text(mx + 1, my + 22, label.upper(), "m5", 12.5, DIM, ls=1) + "</g>")
    # tech chips
    cx_, cy_ = L, y0 + 246
    for t in p["tech"]:
        tw = text_width(t, "m5", 12.5) + 22
        if cx_ + tw > R:
            break
        s.add(f'<rect x="{cx_:.1f}" y="{cy_}" width="{tw:.1f}" height="26" rx="13" fill="#1e293b" '
              f'fill-opacity=".55" stroke="{EDGE_HI}" stroke-opacity=".8"/>')
        s.add(s.text(cx_ + 11, cy_ + 17.5, t, "m5", 12.5, SOFT))
        cx_ += tw + 8
    # footer
    fy = y0 + h - 16
    s.add(s.text(L, fy, f"github.com/{p['repo']}", "m5", 12.5, DIM))
    if p.get("live"):
        label = "LIVE DEMO"
        lw = text_width(label, "m7", 12, 1.2)
        s.add(f'<circle cx="{R - lw - 14:.1f}" cy="{fy - 4.5}" r="4" fill="{GREEN}"/>'
              f'<circle class="ping" cx="{R - lw - 14:.1f}" cy="{fy - 4.5}" r="4" fill="{GREEN}"/>')
        s.add(s.text(R, fy, label, "m7", 12, GREEN, anchor="end", ls=1.2))
    else:
        s.add(s.text(R, fy, "VIEW REPO ↗", "m7", 12, light, anchor="end", ls=1.2, extra='opacity=".8"'))
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
    s.add(s.panel(10, 10, 1180, H - 20, rx=24, accent=VIOLET, glow_at=(.5, 0), glow_op=.1))
    s.css.append("@keyframes pop{from{opacity:0;transform:scale(.86)}to{opacity:1;transform:none}}"
                 ".pop{transform-box:fill-box;transform-origin:center;animation:pop .6s cubic-bezier(.2,.9,.3,1.2) both}"
                 "@keyframes hl{0%,100%{opacity:0}5%{opacity:1}14%{opacity:0}}")
    tile_fill = s.linear([(0, "#131c31"), (1, "#0b1222")], 0, 0, 0, 1)
    n = 0
    for b, (cat, acc, items) in enumerate(STACK):
        br, bc = divmod(b, 2)
        bx = 10 + 44 + bc * (block_w + mid_gap)
        by = 10 + 36 + br * (block_h + 40)
        light, main, deep = ACCENTS[acc]
        s.add(f'<rect x="{bx}" y="{by + 7}" width="10" height="10" rx="2" fill="{main}" '
              f'transform="rotate(45 {bx + 5} {by + 12})"/>')
        s.add(s.text(bx + 22, by + 18, cat, "d7", 16, TEXT, ls=3))
        lx = bx + 22 + text_width(cat, "d7", 16, 3) + 14
        lg = s.linear([(0, main, .8), (1, main, 0)], lx, 0, bx + block_w, 0, units="userSpaceOnUse")
        s.add(f'<path d="M{lx:.1f} {by + 12}H{bx + block_w}" stroke="url(#{lg})"/>')
        for k, (label, slug, hex_) in enumerate(items):
            r, c = divmod(k, cols)
            tx, ty = bx + c * (tile + gap), by + title_h + r * (tile + gap)
            s.add(f'<g class="pop" style="animation-delay:{.04 * n:.2f}s">'
                  f'<rect x="{tx}" y="{ty}" width="{tile}" height="{tile}" rx="18" fill="url(#{tile_fill})" '
                  f'stroke="{EDGE}" />'
                  f'<rect x="{tx + .5}" y="{ty + .5}" width="{tile - 1}" height="{tile - 1}" rx="17.5" '
                  f'stroke="{main}" stroke-width="1.5" opacity="0" '
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
    color = legible("#" + hex_, min_ratio=3.5)
    s.add(s.panel(2, 2, W - 4, H - 4, rx=(H - 4) / 2, accent=color, glow_at=(0, .5), glow_op=.22))
    border = s.linear([(0, color, .85), (1, VIOLET, .35)], 0, 0, 1, 0)
    s.add(f'<rect x="2.75" y="2.75" width="{W - 5.5}" height="{H - 5.5}" rx="{(H - 5.5) / 2}" '
          f'stroke="url(#{border})" stroke-width="1.5"/>')
    clip = s.clip_rect(2, 2, W - 4, H - 4, (H - 4) / 2)
    band = s.linear([(0, "#ffffff", 0), (.5, "#ffffff", .12), (1, "#ffffff", 0)])
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
    s = Svg(W, H, "Thanks for visiting", "Thanks for stopping by! Let's build systems that reason, retrieve and act.")
    keyframes_common(s)
    x0, y0, w, h = 10, 10, 1180, 200
    clip = s.clip_rect(x0, y0, w, h, 28)
    s.add(s.panel(x0, y0, w, h, rx=28, accent=VIOLET, glow_at=(.5, 1), glow_op=.18))
    s.add(f'<g clip-path="url(#{clip})">')
    period = 300
    for k, (col, amp, base, dur, op) in enumerate([(CYAN, 10, 172, 14, .22), (VIOLET, 13, 180, 10, .26),
                                                   (PINK, 9, 190, 7, .3)]):
        pts = [f"M0 {base}"]
        for xx in range(0, W + period + 1, 10):
            pts.append(f"L{xx} {base + amp * math.sin(2 * math.pi * xx / period + k):.1f}")
        pts.append(f"L{W + period} {H}L0 {H}Z")
        g = s.linear([(0, col, op), (1, col, op * .2)], 0, 0, 0, 1)
        s.css.append(f"@keyframes wv{k}{{from{{transform:translateX(0)}}to{{transform:translateX(-{period}px)}}}}")
        s.add(f'<path d="{"".join(pts)}" fill="url(#{g})" style="animation:wv{k} {dur}s linear infinite"/>')
    s.add("</g>")
    cx = W / 2
    title = "Thanks for stopping by!"
    tw = text_width(title, "d7", 34)
    tg = s.linear([(0, "#67e8f9"), (.5, "#a78bfa"), (1, "#f472b6")], cx - tw / 2, 0, cx + tw / 2, 0,
                  units="userSpaceOnUse")
    s.add(s.text(cx, 82, title, "d7", 34, f"url(#{tg})", anchor="middle", cls="rise"))
    s.add(s.text(cx + .5, 118, "let's build systems that reason, retrieve & act", "m5", 16, SOFT, anchor="middle",
                 ls=1, cls="fade", style="animation-delay:.3s"))
    return s


# ============================================================================ main
def main() -> None:
    print("building static artwork ->", ASSETS)
    write("hero.svg", build_hero())
    for key, num, title, sub in HEADERS:
        write(f"headers/{key}.svg", build_header(num, title, sub))
    write("achievements.svg", build_achievements())
    for i, p in enumerate(PROJECTS):
        write(f"projects/{p['slug']}.svg", build_project(p, i))
    write("tech-stack.svg", build_stack())
    for key, label, slug, hex_ in BUTTONS:
        write(f"buttons/{key}.svg", build_button(label, slug, hex_))
    write("footer.svg", build_footer())


if __name__ == "__main__":
    main()
