"""Shared design tokens and SVG helpers for the profile README artwork.

Every SVG in this repo is rendered by GitHub as an <img>, which means:
  * no JavaScript, no external fonts/images/stylesheets, no foreignObject;
  * CSS @keyframes and SMIL animations work;
  * fonts must be embedded (we inline tiny per-image WOFF2 subsets from Google Fonts).
The fully visible state is always the default; animations only ever start from hidden.
Standard library only, so the GitHub Action needs no pip install.
"""
from __future__ import annotations

import base64
import itertools
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from xml.sax.saxutils import escape as _xml_escape

# --------------------------------------------------------------------------- palette
INK = "#05080f"
PANEL_A = "#0f172a"
PANEL_B = "#090e1b"
EDGE = "#1e293b"
EDGE_HI = "#334155"
TEXT = "#e2e8f0"
SOFT = "#cbd5e1"
MUTED = "#94a3b8"
DIM = "#64748b"
CYAN = "#22d3ee"
SKY = "#38bdf8"
VIOLET = "#a78bfa"
PINK = "#f472b6"
GOLD = "#fbbf24"
GREEN = "#34d399"

# name -> (light, main, deep); used for per-card accent gradients
ACCENTS = {
    "cyan": ("#a5f3fc", "#22d3ee", "#0891b2"),
    "violet": ("#ddd6fe", "#a78bfa", "#7c3aed"),
    "pink": ("#fbcfe8", "#f472b6", "#db2777"),
    "gold": ("#fde68a", "#fbbf24", "#d97706"),
    "green": ("#a7f3d0", "#34d399", "#059669"),
    "sky": ("#bae6fd", "#38bdf8", "#0284c7"),
}
AURORA = (CYAN, VIOLET, PINK)

# --------------------------------------------------------------------------- fonts
# alias -> (Google Fonts family, weight, CSS fallback stack)
FONTS = {
    "d5": ("Space Grotesk", 500, "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"),
    "d7": ("Space Grotesk", 700, "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"),
    "m5": ("JetBrains Mono", 500, "ui-monospace,SFMono-Regular,Consolas,'Liberation Mono',monospace"),
    "m7": ("JetBrains Mono", 700, "ui-monospace,SFMono-Regular,Consolas,'Liberation Mono',monospace"),
}

# Advance widths (units per 1000 em) measured from the Space Grotesk static instances.
_SG_CHARS = (" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
             "abcdefghijklmnopqrstuvwxyz{|}~·×—–→↗←•₹’‘“”…°±≤≥′∕⁄")
_SG5 = ("255,276,470,632,609,765,598,273,389,383,530,620,273,443,276,379,645,435,598,606,630,599,615,559,611,"
        "615,276,276,620,620,620,579,1020,632,663,643,665,559,537,661,656,254,602,618,544,874,667,673,603,673,"
        "632,609,588,669,619,887,641,617,577,347,379,347,620,620,288,577,641,592,641,584,439,640,615,256,258,"
        "551,256,857,615,615,641,641,387,525,458,614,544,792,593,614,519,449,249,449,620,203,620,899,595,800,"
        "617,800,380,638,273,273,470,470,739,388,620,620,620,217,398,644")
_SG7 = ("254,298,514,636,606,758,591,294,398,390,540,620,294,432,298,388,648,452,594,608,636,600,618,554,600,"
        "618,298,298,620,620,620,578,1014,634,664,644,666,554,534,662,656,264,610,626,542,882,670,676,604,676,"
        "632,606,588,672,618,898,644,624,576,358,388,358,620,620,296,578,638,586,638,577,436,638,616,266,268,"
        "564,266,854,616,612,638,638,396,524,456,616,548,784,592,616,518,466,258,466,620,218,620,888,584,800,"
        "620,800,400,622,294,294,514,514,798,394,620,620,620,232,409,638")
_WIDTHS = {
    "d5": dict(zip(_SG_CHARS, map(int, _SG5.split(",")))),
    "d7": dict(zip(_SG_CHARS, map(int, _SG7.split(",")))),
}


def text_width(s: str, font: str, size: float, ls: float = 0.0) -> float:
    """Rendered width of `s` in px (kerning ignored, letter-spacing included)."""
    if font.startswith("m"):  # JetBrains Mono is strictly monospaced at 600/1000
        units = 600 * len(s)
    else:
        table = _WIDTHS[font]
        units = sum(table.get(ch, 600) for ch in s)
    return units * size / 1000 + ls * len(s)


def fit_size(s: str, font: str, size: float, max_w: float, min_size: float = 8, ls: float = 0) -> float:
    """Largest font size <= size that keeps `s` within max_w."""
    while size > min_size and text_width(s, font, size, ls) > max_w:
        size -= 0.5
    return size


def wrap(s: str, font: str, size: float, max_w: float) -> list[str]:
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if cur and text_width(trial, font, size) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def esc(s: str) -> str:
    return _xml_escape(str(s), {'"': "&quot;"})


# --------------------------------------------------------------------------- colour helpers
def _rgb(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def mix(c1: str, c2: str, t: float) -> str:
    a, b = _rgb(c1), _rgb(c2)
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def _lum(c: str) -> float:
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = _rgb(c)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(c1: str, c2: str) -> float:
    l1, l2 = sorted((_lum(c1), _lum(c2)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def legible(c: str, bg: str = PANEL_B, min_ratio: float = 4.0) -> str:
    """Lighten a (brand) colour until it reads on the dark panels."""
    t = 0.0
    out = c
    while contrast(out, bg) < min_ratio and t < 1:
        t += 0.05
        out = mix(c, "#ffffff", t)
    return out


# --------------------------------------------------------------------------- network
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def http_get(url: str, headers: dict | None = None, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


_face_cache: dict[tuple[str, str], str] = {}


def font_faces(alias: str, chars: set[str]) -> str:
    """@font-face rules with a WOFF2 subset (only `chars`) inlined as a data URI.

    Returns "" when Google Fonts is unreachable; the CSS fallback stack then takes over.
    """
    family, weight, _ = FONTS[alias]
    text = "".join(sorted(set(chars) | {" "}))
    key = (alias, text)
    if key in _face_cache:
        return _face_cache[key]
    url = ("https://fonts.googleapis.com/css2?family=" + family.replace(" ", "+")
           + f":wght@{weight}&display=block&text=" + urllib.parse.quote(text, safe=""))
    try:
        css = http_get(url).decode()
        faces = []
        for src in re.findall(r"url\((https://[^)]+)\)\s*format\('woff2'\)", css):
            data = base64.b64encode(http_get(src)).decode()
            faces.append(f"@font-face{{font-family:'{alias}';font-weight:{weight};font-display:block;"
                         f"src:url(data:font/woff2;base64,{data}) format('woff2')}}")
        out = "".join(faces)
    except Exception as exc:  # network trouble must never break the build
        print(f"::warning::font subset for {family} {weight} unavailable ({exc}); using fallback stack")
        out = ""
    _face_cache[key] = out
    return out


# --------------------------------------------------------------------------- icons
# 24x24 stroke icons (drawn for this profile; stroke-linecap/linejoin round).
ICONS = {
    "trophy": "M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0zM7 6H4.5a2.5 2.5 0 0 0 2.6 4.4M17 6h2.5a2.5 2.5 0 0 1-2.6 4.4",
    "graph": "M6 6.5a2.5 2.5 0 1 0 0 .01M18 5a2.5 2.5 0 1 0 0 .01M12 19.5a2.5 2.5 0 1 0 0 .01M8.3 7.6l2.6 9.4M15.8 6.6l-2.6 10.5M8.5 6.2l7-1",
    "globe": "M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18M3 12h18M12 3c2.8 2.9 3.8 5.9 3.8 9s-1 6.1-3.8 9M12 3C9.2 5.9 8.2 8.9 8.2 12s1 6.1 3.8 9",
    "coin": "M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18M15 8.8c-.6-.9-1.7-1.4-3-1.4-1.8 0-3 .9-3 2.2 0 3.1 6.2 1.6 6.2 4.8 0 1.4-1.3 2.3-3.2 2.3-1.4 0-2.6-.5-3.2-1.5M12 5.8v1.6M12 16.7v1.5",
    "target": "M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18M12 7a5 5 0 1 0 0 10a5 5 0 1 0 0-10M12 11a1 1 0 1 0 0 2a1 1 0 1 0 0-2",
    "merge": "M6 3.5a2.5 2.5 0 1 0 0 5a2.5 2.5 0 1 0 0-5M6 15.5a2.5 2.5 0 1 0 0 5a2.5 2.5 0 1 0 0-5M18 13.5a2.5 2.5 0 1 0 0 5a2.5 2.5 0 1 0 0-5M6 8.5v7M6 8.5c0 4 4 7.5 9.5 7.5",
    "rocket": "M5 15c-1.5 1.2-2 4-2 6 2 0 4.8-.5 6-2M9 14.9 14.5 9.5M12.5 5.5C15 3.5 18 3 21 3c0 3-.5 6-2.5 8.5L12 18l-6-6zM6.5 12.5H3l2.5-3.5h4.5M11.5 17.5V21l3.5-2.5V14",
    "code": "M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16",
    "medal": "M7.2 3h3.6l2 4.2M16.8 3h-3.6L11.6 6.4M12 9a6 6 0 1 0 0 12a6 6 0 1 0 0-12M12 12.2l1 2 2.2.3-1.6 1.6.4 2.2-2-1.1-2 1.1.4-2.2-1.6-1.6 2.2-.3z",
    "users": "M9 4a3.5 3.5 0 1 0 0 7a3.5 3.5 0 1 0 0-7M2.5 20c.6-3.4 3.3-5.5 6.5-5.5s5.9 2.1 6.5 5.5M16 4.3a3.3 3.3 0 0 1 0 6.4M18.5 14.9c1.6.8 2.7 2.6 3 5.1",
    "award": "M12 2.8a6.2 6.2 0 1 0 0 12.4a6.2 6.2 0 1 0 0-12.4M8.4 14l-1.6 7.2L12 18.6l5.2 2.6L15.6 14M12 6.2l1.1 2.2 2.4.4-1.7 1.7.4 2.4-2.2-1.2-2.2 1.2.4-2.4-1.7-1.7 2.4-.4z",
    "cap": "M2 9.5 12 5l10 4.5-10 4.5zM6 11.3v4.6c0 1.6 2.7 3.1 6 3.1s6-1.5 6-3.1v-4.6M22 9.5v5.5",
    "bolt": "M13 2 4 14h7l-1 8 9-12h-7z",
    "spark": "M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8",
    "flame": "M12 22c3.9 0 7-2.8 7-6.8 0-4.6-3.6-6.6-4.6-10.2-.5 2.1-1.6 3.4-3 4.3.2-2.6-1-5-3-6.3.4 3.9-3.4 6.2-3.4 11.1C5 19.2 8.1 22 12 22zM12 22c-1.7 0-3-1.3-3-3.1 0-2.2 1.9-3 2.4-4.9 1.2 1 3.6 2.4 3.6 4.9 0 1.8-1.3 3.1-3 3.1z",
    "commit": "M12 8a4 4 0 1 0 0 8a4 4 0 1 0 0-8M2 12h6M16 12h6",
    "pr": "M6 3.5a2.5 2.5 0 1 0 0 5a2.5 2.5 0 1 0 0-5M6 15.5a2.5 2.5 0 1 0 0 5a2.5 2.5 0 1 0 0-5M18 15.5a2.5 2.5 0 1 0 0 5a2.5 2.5 0 1 0 0-5M6 8.5v7M18 15.5V9a3 3 0 0 0-3-3h-4M13 3.5 10.5 6 13 8.5",
    "check": "M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18M8 12.3l2.7 2.7L16.2 9.5",
    "repo": "M5 4.5A1.5 1.5 0 0 1 6.5 3H19v15H6.5A1.5 1.5 0 0 0 5 19.5zM5 19.5A1.5 1.5 0 0 0 6.5 21H19v-3M9 7h6",
    "calendar": "M4 6h16v15H4zM4 10h16M8 3v5M16 3v5M8 14h2M12 14h2M16 14h.01M8 17.5h2M12 17.5h2",
    "pulse": "M3 12h4l3-7 4 14 3-7h4",
    "star": "M12 3.2l2.7 5.6 6.1.8-4.5 4.2 1.1 6-5.4-2.9-5.4 2.9 1.1-6-4.5-4.2 6.1-.8z",
    "pin": "M12 21s-6.5-5.6-6.5-11A6.5 6.5 0 0 1 18.5 10c0 5.4-6.5 11-6.5 11zM12 7.5a2.5 2.5 0 1 0 0 5a2.5 2.5 0 1 0 0-5",
    "database": "M12 3c4.4 0 8 1.3 8 3s-3.6 3-8 3-8-1.3-8-3 3.6-3 8-3zM4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3",
}


ICONS["shield"] = "M12 3 4.5 6v5.5c0 4.6 3.2 8.3 7.5 9.5 4.3-1.2 7.5-4.9 7.5-9.5V6zM8.8 12l2.3 2.3 4.3-4.6"
ICONS["search"] = "M10.5 4a6.5 6.5 0 1 0 0 13a6.5 6.5 0 1 0 0-13M15.3 15.3 20 20"
ICONS["chart"] = "M4 20V10M10 20V4M16 20v-7M22 20H2"


def icon(name: str, x: float, y: float, size: float, color: str, width: float = 1.8, extra: str = "") -> str:
    """Stroke icon whose top-left corner sits at (x, y); stroke width stays `width` px at any size."""
    s = size / 24
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})" {extra}>'
            f'<path d="{ICONS[name]}" fill="none" stroke="{color}" stroke-width="{width / s:.2f}" '
            f'stroke-linecap="round" stroke-linejoin="round"/></g>')


# --------------------------------------------------------------------------- document builder
BASE_CSS = (
    "text{dominant-baseline:auto}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}"
)


def _stops(stops) -> str:
    """(offset, colour[, opacity]) tuples -> <stop/> elements."""
    out = []
    for stop in stops:
        o, c = stop[0], stop[1]
        op = stop[2] if len(stop) > 2 else None
        extra = "" if op is None else f' stop-opacity="{op:g}"'
        out.append(f'<stop offset="{o:g}" stop-color="{c}"{extra}/>')
    return "".join(out)


class Svg:
    """Tiny SVG document builder that tracks which glyphs each font needs."""

    def __init__(self, w: int, h: int, title: str, desc: str = ""):
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.defs: list[str] = []
        self.css: list[str] = []
        self.body: list[str] = []
        self.chars: dict[str, set[str]] = defaultdict(set)
        self._ids = itertools.count()

    # ids are prefixed so several SVGs never collide (they are separate images anyway)
    def uid(self, prefix: str = "i") -> str:
        return f"{prefix}{next(self._ids)}"

    def add(self, *parts: str) -> None:
        self.body.extend(parts)

    def text(self, x: float, y: float, s: str, font: str = "d5", size: float = 16, fill: str = TEXT,
             anchor: str | None = None, ls: float | None = None, cls: str | None = None,
             style: str | None = None, extra: str = "") -> str:
        self.chars[font].update(s)
        attrs = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'class="{font}{" " + cls if cls else ""}"',
                 f'font-size="{size:g}"', f'fill="{fill}"']
        if anchor:
            attrs.append(f'text-anchor="{anchor}"')
        if ls:
            attrs.append(f'letter-spacing="{ls:g}"')
        if style:
            attrs.append(f'style="{style}"')
        if extra:
            attrs.append(extra)
        return f"<text {' '.join(attrs)}>{esc(s)}</text>"

    def use_chars(self, font: str, s: str) -> None:
        self.chars[font].update(s)

    def linear(self, stops, x1=0, y1=0, x2=1, y2=0, units: str | None = None, extra: str = "", inner: str = "") -> str:
        gid = self.uid("g")
        u = f' gradientUnits="{units}"' if units else ""
        st = _stops(stops)
        self.defs.append(f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u} {extra}>{st}{inner}</linearGradient>')
        return gid

    def text_grad(self, accent: str, x: float, baseline: float, size: float, width: float) -> str:
        """Diagonal accent sheen for a big number, pinned to the text's own box in user space.

        objectBoundingBox gradients on <text> resolve against different boxes in WebKit vs Blink/Gecko
        (WebKit renders them almost entirely in the lightest stop), so coordinates are explicit here.
        """
        light, main, deep = ACCENTS[accent]
        return self.linear([(0, light), (.45, main), (1, deep)], f"{x:.1f}", f"{baseline - size * .78:.1f}",
                           f"{x + max(width, size):.1f}", f"{baseline:.1f}", units="userSpaceOnUse")

    def radial(self, stops, cx=0.5, cy=0.5, r=0.5, units: str | None = None) -> str:
        gid = self.uid("r")
        u = f' gradientUnits="{units}"' if units else ""
        st = _stops(stops)
        self.defs.append(f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}"{u}>{st}</radialGradient>')
        return gid

    def glow_filter(self, std: float = 3.0) -> str:
        fid = self.uid("f")
        self.defs.append(
            f'<filter id="{fid}" x="-100%" y="-100%" width="300%" height="300%">'
            f'<feGaussianBlur stdDeviation="{std}" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
        return fid

    def clip_rect(self, x, y, w, h, rx=0) -> str:
        cid = self.uid("c")
        self.defs.append(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath>')
        return cid

    def panel(self, x, y, w, h, rx=18, accent: str | None = None, glow_at=(0.0, 0.0), glow_op=0.16) -> str:
        """Dark card: diagonal fill, hairline border, optional accent glow from a corner."""
        fill = self.linear([(0, PANEL_A), (1, PANEL_B)], 0, 0, 1, 1)
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#{fill})"/>']
        if accent:
            g = self.radial([(0, accent, glow_op), (1, accent, 0)], cx=glow_at[0], cy=glow_at[1], r=0.9)
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#{g})"/>')
        out.append(f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{rx - .5}" '
                   f'fill="none" stroke="{EDGE}" stroke-opacity=".9"/>')
        return "".join(out)

    def render(self, embed_fonts: bool = True) -> str:
        faces = "".join(font_faces(a, cs) for a, cs in self.chars.items() if cs) if embed_fonts else ""
        families = "".join(
            f".{a}{{font-family:'{a}','{fam}',{stack};font-weight:{wt}}}"
            for a, (fam, wt, stack) in FONTS.items() if a in self.chars)
        css = faces + families + BASE_CSS + "".join(self.css)
        doc = (
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="t d" fill="none">'
            f'<title id="t">{esc(self.title)}</title><desc id="d">{esc(self.desc or self.title)}</desc>'
            f"<style>{css}</style><defs>{''.join(self.defs)}</defs>{''.join(self.body)}</svg>"
        )
        ET.fromstring(doc)  # raise on malformed XML before anything is written
        return doc


def validate(path: str) -> None:
    ET.parse(path)
