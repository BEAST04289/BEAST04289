#!/usr/bin/env python3
"""Fetch live GitHub numbers and render the animated stats cards in assets/stats/.

    GITHUB_TOKEN=... python scripts/github_stats.py --user BEAST04289

Runs on a schedule in GitHub Actions (.github/workflows/profile-stats.yml). Each data source
(profile, languages, search counts, contribution calendar) is fetched on its own; if one fails,
the last good values from assets/stats/data.json are reused, so a hiccup never ships an error
card. Works with the built-in GITHUB_TOKEN (public data); a PAT with read:user adds private
contribution counts. Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svgkit import (ACCENTS, CYAN, DIM, EDGE_HI, GOLD, GREEN, MUTED, PINK, SKY, SOFT, TEXT,  # noqa: E402
                    VIOLET, Svg, esc, fit_size, icon, text_width)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "stats"
API = "https://api.github.com"
# Vendored / build-system languages that say nothing about what someone writes.
NOISE_LANGS = {"Cython", "Fortran", "Meson", "Roff", "Smarty", "Makefile", "Batchfile", "Procfile", "CMake",
               "Jinja", "TeX", "Dockerfile", "PowerShell", "PLpgSQL", "Shell", "Jupyter Notebook", "Mako"}
LANG_COLORS = [CYAN, VIOLET, PINK, GOLD, GREEN, SKY]


# =================================================================================== fetching
class Fetcher:
    def __init__(self, user: str, token: str | None):
        self.user, self.token = user, token

    def _req(self, url: str, data: bytes | None = None, accept: str = "application/vnd.github+json"):
        headers = {"Accept": accept, "User-Agent": f"{self.user}-profile-stats",
                   "X-GitHub-Api-Version": "2022-11-28"}
        if self.token and "api.github.com" in url:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=40) as resp:
            return resp.read()

    def rest(self, path: str):
        return json.loads(self._req(API + path))

    def graphql(self, query: str, **variables):
        if not self.token:
            raise RuntimeError("GraphQL needs a token")
        body = json.dumps({"query": query, "variables": variables}).encode()
        out = json.loads(self._req(API + "/graphql", data=body))
        if out.get("errors") and not out.get("data"):
            raise RuntimeError(out["errors"][0].get("message", "GraphQL error"))
        return out

    # ---------------------------------------------------------------- groups
    def profile(self) -> dict:
        u = self.rest(f"/users/{self.user}")
        return {k: u.get(k) for k in ("login", "name", "public_repos", "followers", "created_at")}

    def languages(self) -> dict:
        repos, page = [], 1
        while True:
            batch = self.rest(f"/users/{self.user}/repos?type=owner&per_page=100&page={page}")
            repos += batch
            if len(batch) < 100:
                break
            page += 1
        share: dict[str, float] = {}
        counted = 0
        for r in repos:
            if r.get("fork"):
                continue
            langs = {k: v for k, v in self.rest(f"/repos/{r['full_name']}/languages").items() if k not in NOISE_LANGS}
            total = sum(langs.values())
            if not total:
                continue
            counted += 1  # every repo gets one equal vote, split by its own language mix
            for k, v in langs.items():
                share[k] = share.get(k, 0) + v / total
        items = sorted(((k, 100 * v / counted) for k, v in share.items()), key=lambda kv: -kv[1])
        return {"items": [[k, round(v, 2)] for k, v in items], "repos": counted}

    def search(self) -> dict:
        def count(q: str, kind: str = "issues"):
            return self.rest(f"/search/{kind}?per_page=100&q=" + urllib.parse.quote(q))
        u = self.user
        ext = count(f"is:pr author:{u} -user:{u} is:merged")
        upstream = sorted({i["repository_url"].split("/repos/")[1] for i in ext.get("items", [])})
        out = {"prs": count(f"is:pr author:{u}")["total_count"],
               "merged_prs": count(f"is:pr author:{u} is:merged")["total_count"],
               "issues": count(f"is:issue author:{u}")["total_count"],
               "upstream_merged": ext["total_count"], "upstream_repos": upstream}
        try:
            out["commits"] = count(f"author:{u}", "commits")["total_count"]
        except Exception as exc:  # commit search is the flakiest endpoint; never fatal
            print(f"::notice::commit search skipped ({exc})")
        return out

    def calendar(self, created_at: str | None) -> dict:
        """Daily contribution counts since the account was created, plus GraphQL totals if available."""
        today = dt.datetime.now(dt.timezone.utc).date()
        try:
            return self._calendar_graphql(today)
        except Exception as exc:
            print(f"::notice::GraphQL calendar unavailable ({exc}); reading the public contributions page")
        first_year = int((created_at or f"{today.year}")[:4])
        days: dict[str, int] = {}
        for year in range(first_year, today.year + 1):
            end = min(dt.date(year, 12, 31), today)
            html = self._req(f"https://github.com/users/{self.user}/contributions?from={year}-01-01&to={end}",
                             accept="text/html").decode("utf-8", "replace")
            days.update({k: v for k, v in parse_calendar_html(html).items() if k <= today.isoformat()})
        if not days:
            raise RuntimeError("no calendar data on the contributions page")
        return {"days": dict(sorted(days.items())), "totals": None}

    def _calendar_graphql(self, today: dt.date) -> dict:
        years = self.graphql("query($login:String!){user(login:$login){contributionsCollection{contributionYears}}}",
                             login=self.user)["data"]["user"]["contributionsCollection"]["contributionYears"]
        q = ("query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection("
             "from:$from,to:$to){totalCommitContributions totalIssueContributions totalPullRequestContributions "
             "totalPullRequestReviewContributions restrictedContributionsCount contributionCalendar{"
             "weeks{contributionDays{date contributionCount}}}}}}")
        days: dict[str, int] = {}
        totals = {"commits": 0, "issues": 0, "prs": 0, "reviews": 0, "restricted": 0}
        keys = {"commits": "totalCommitContributions", "issues": "totalIssueContributions",
                "prs": "totalPullRequestContributions", "reviews": "totalPullRequestReviewContributions",
                "restricted": "restrictedContributionsCount"}
        for year in sorted(years):
            end = f"{year}-12-31T23:59:59Z" if year < today.year else dt.datetime.now(dt.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ")
            cc = self.graphql(q, login=self.user, **{"from": f"{year}-01-01T00:00:00Z", "to": end}
                              )["data"]["user"]["contributionsCollection"]
            for k, field in keys.items():
                totals[k] += cc.get(field) or 0
            for week in cc["contributionCalendar"]["weeks"]:
                for d in week["contributionDays"]:
                    if d["date"] <= today.isoformat():
                        days[d["date"]] = d["contributionCount"]
        return {"days": dict(sorted(days.items())), "totals": totals}


def parse_calendar_html(html: str) -> dict[str, int]:
    cells = re.findall(r'data-date="(\d{4}-\d\d-\d\d)" id="(contribution-day-component-\d+-\d+)"', html)
    tips = {m.group(1): m.group(2) for m in
            re.finditer(r'<tool-tip[^>]*for="(contribution-day-component-\d+-\d+)"[^>]*>([^<]*)</tool-tip>', html)}
    out = {}
    for date, cid in cells:
        m = re.match(r"\s*(\d+) contribution", tips.get(cid, ""))
        out[date] = int(m.group(1)) if m else 0
    return out


# =================================================================================== metrics
def derive(data: dict) -> dict:
    today = dt.datetime.now(dt.timezone.utc).date()
    raw = {dt.date.fromisoformat(k): v for k, v in data["calendar"]["days"].items()}
    created = ((data.get("profile") or {}).get("created_at") or "")[:10]
    start = min(raw) if raw else today
    if created:
        start = max(start, dt.date.fromisoformat(created))
    series = []
    d = start
    while d <= today:
        series.append((d, raw.get(d, 0)))
        d += dt.timedelta(days=1)

    # longest streak
    best, run_start, run = (0, None, None), None, 0
    for d, c in series:
        if c > 0:
            run_start = d if run == 0 else run_start
            run += 1
            if run > best[0]:
                best = (run, run_start, d)
        else:
            run = 0
    # current streak (today may still be empty, so yesterday keeps it alive)
    cur, cur_end = 0, None
    idx = len(series) - 1
    if idx >= 0 and series[idx][1] == 0:
        idx -= 1
    while idx >= 0 and series[idx][1] > 0:
        cur += 1
        cur_end = cur_end or series[idx][0]
        idx -= 1
    cur_start = series[idx + 1][0] if cur else None

    year_ago = today - dt.timedelta(days=364)
    last_year = [(d, c) for d, c in series if d >= year_ago]
    weeks = []
    for i in range(52):
        chunk = last_year[i * 7:(i + 1) * 7]
        if chunk:
            weeks.append((chunk[0][0], sum(c for _, c in chunk)))
    busiest = max(series, key=lambda dc: dc[1]) if series else (today, 0)
    return {
        "today": today,
        "total_all": sum(c for _, c in series),
        "total_year": sum(c for _, c in last_year),
        "active_year": sum(1 for _, c in last_year if c),
        "longest": best, "current": (cur, cur_start, cur_end),
        "weeks": weeks, "busiest": busiest, "since": start,
    }


def fmt(n) -> str:
    return f"{n:,}" if isinstance(n, int) else str(n)


def nice_date(d: dt.date | None, year=True) -> str:
    if not d:
        return "—"
    return d.strftime("%b ") + str(d.day) + (d.strftime(", %Y") if year else "")


# =================================================================================== rendering
def _anim_css(s: Svg) -> None:
    s.css.append(
        "@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}"
        ".rise{animation:rise .8s cubic-bezier(.2,.8,.2,1) both}"
        "@keyframes fade{from{opacity:0}to{opacity:1}}.fade{animation:fade 1.1s ease both}"
        "@keyframes grow{from{transform:scaleX(0)}to{transform:none}}"
        ".grow{transform-box:fill-box;transform-origin:left center;animation:grow 1.3s cubic-bezier(.2,.8,.2,1) both}"
        "@keyframes ping{0%{transform:scale(1);opacity:.8}80%,100%{transform:scale(2.6);opacity:0}}"
        ".ping{transform-box:fill-box;transform-origin:center;animation:ping 1.8s cubic-bezier(0,0,.2,1) infinite}"
        "@keyframes draw{from{stroke-dashoffset:1000}to{stroke-dashoffset:0}}"
    )


def _card_header(s: Svg, x: float, y: float, ic: str, accent: str, title: str, sub: str) -> None:
    light, main, _ = ACCENTS[accent]
    s.add(f'<rect x="{x}" y="{y}" width="44" height="44" rx="12" fill="{main}" fill-opacity=".1" '
          f'stroke="{main}" stroke-opacity=".5"/>')
    s.add(icon(ic, x + 11, y + 11, 22, light, 1.8))
    s.add(s.text(x + 58, y + 21, title, "d7", 21, TEXT))
    s.add(s.text(x + 58, y + 40, sub, "m5", 12.5, DIM))


def render_overview(data: dict, m: dict) -> Svg:
    W, H = 600, 340
    srch, prof = data.get("search") or {}, data.get("profile") or {}
    totals = (data.get("calendar") or {}).get("totals") or {}
    commits = totals.get("commits") or srch.get("commits")
    # (icon, accent, value, label, unit) — unit "/yr" marks the rolling 12-month numbers
    tiles = [
        ("pulse", "cyan", fmt(m["total_year"]), "contributions", "/yr"),
        ("commit", "violet", fmt(commits) if commits is not None else "—", "commits", ""),
        ("pr", "pink", fmt(srch.get("prs", "—")), "pull requests", ""),
        ("merge", "gold", fmt(srch.get("merged_prs", "—")), "PRs merged", ""),
        ("repo", "green", fmt(prof.get("public_repos", "—")), "public repos", ""),
        ("calendar", "sky", fmt(m["active_year"]), "active days", "/yr"),
    ]
    s = Svg(W, H, "GitHub overview", "; ".join(f"{v} {k}{' in the last year' if u else ''}"
                                               for _, _, v, k, u in tiles))
    _anim_css(s)
    s.add(s.panel(10, 10, 580, 320, rx=20, accent=CYAN, glow_at=(0, 0), glow_op=.16))
    s.add(f'<rect x="40" y="10" width="64" height="3" rx="1.5" fill="{CYAN}"/>')
    since = prof.get("created_at", "")[:7]
    since_txt = dt.date.fromisoformat(since + "-01").strftime("%b %Y") if since else ""
    _card_header(s, 40, 34, "chart", "cyan", "GitHub Overview", f"@{data['user']} · on GitHub since {since_txt}")
    cw, chh = 520 / 3, 84
    for i, (ic, acc, val, label, unit) in enumerate(tiles):
        r, c = divmod(i, 3)
        x, y = 40 + c * cw, 104 + r * (chh + 12)
        light, main, deep = ACCENTS[acc]
        g = s.linear([(0, light), (.6, main), (1, deep)], 0, 0, .6, 1)
        vsize = fit_size(val, "d7", 32, cw - 70, 18)
        s.add(f'<g class="rise" style="animation-delay:{.1 + .08 * i:.2f}s">'
              f'<rect x="{x:.1f}" y="{y}" width="{cw - 12:.1f}" height="{chh}" rx="14" fill="#0b1222" '
              f'fill-opacity=".7" stroke="{EDGE_HI}" stroke-opacity=".55"/>'
              + icon(ic, x + 14, y + 14, 18, light, 1.7)
              + s.text(x + 39, y + 28, label.upper(), "m5", fit_size(label.upper(), "m5", 12, cw - 60, 9), MUTED,
                       ls=.4)
              + s.text(x + 14, y + 66, val, "d7", vsize, f"url(#{g})")
              + (s.text(x + 14 + text_width(val, "d7", vsize) + 5, y + 66, unit, "m5", 13, DIM) if unit else "")
              + "</g>")
    ups = srch.get("upstream_repos") or []
    if ups:
        line = "merged upstream → " + "  ·  ".join(ups)
        size = fit_size(line, "m5", 12.5, 520, 9.5)
        s.add(s.text(40, 314, line, "m5", size, MUTED, cls="fade", style="animation-delay:.8s"))
    return s


def render_languages(data: dict) -> Svg:
    W, H = 600, 340
    langs = (data.get("languages") or {}).get("items", [])
    repos = (data.get("languages") or {}).get("repos", 0)
    top = langs[:6]
    if len(langs) > 6:
        top = top[:5] + [["Other", round(100 - sum(v for _, v in top[:5]), 2)]]
    s = Svg(W, H, "Top languages", "; ".join(f"{k} {v:.1f}%" for k, v in top))
    _anim_css(s)
    s.add(s.panel(10, 10, 580, 320, rx=20, accent=VIOLET, glow_at=(1, 0), glow_op=.16))
    s.add(f'<rect x="40" y="10" width="64" height="3" rx="1.5" fill="{VIOLET}"/>')
    _card_header(s, 40, 34, "code", "violet", "Top Languages",
                 f"share of {repos} repos · each repo weighted equally")
    # stacked bar
    bx, by, bw, bh = 40, 104, 520, 14
    clip = s.clip_rect(bx, by, bw, bh, 7)
    s.add(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="7" fill="#1e293b"/>')
    s.add(f'<g clip-path="url(#{clip})">')
    x = bx
    total = sum(v for _, v in top) or 1
    for i, (name, v) in enumerate(top):
        w = bw * v / total
        col = LANG_COLORS[i % len(LANG_COLORS)]
        s.add(f'<rect class="grow" x="{x:.2f}" y="{by}" width="{w + .6:.2f}" height="{bh}" fill="{col}" '
              f'style="animation-delay:{.15 * i:.2f}s"/>')
        x += w
    s.add("</g>")
    # legend with mini bars
    colw = 250
    for i, (name, v) in enumerate(top):
        r, c = divmod(i, 2)
        lx, ly = 40 + c * (colw + 20), 164 + r * 58
        col = LANG_COLORS[i % len(LANG_COLORS)]
        pct = f"{v:.1f}%"
        s.add(f'<g class="rise" style="animation-delay:{.2 + .08 * i:.2f}s">'
              f'<circle cx="{lx + 6}" cy="{ly - 6}" r="5" fill="{col}"/>'
              + s.text(lx + 20, ly, name, "d5", fit_size(name, "d5", 17, colw - 90, 12), TEXT)
              + s.text(lx + colw, ly, pct, "m5", 15, SOFT, anchor="end")
              + f'<rect x="{lx}" y="{ly + 12}" width="{colw}" height="5" rx="2.5" fill="#1e293b"/>'
              + f'<rect class="grow" x="{lx}" y="{ly + 12}" width="{max(colw * v / 100, 5):.1f}" height="5" rx="2.5" '
                f'fill="{col}" style="animation-delay:{.45 + .1 * i:.2f}s"/>'
              + "</g>")
    return s


def render_activity(data: dict, m: dict) -> Svg:
    W, H = 1200, 360
    cur, cur_s, cur_e = m["current"]
    lng, lng_s, lng_e = m["longest"]
    s = Svg(W, H, "Contribution pulse",
            f"{m['total_year']} contributions in the last year; current streak {cur} days; longest streak {lng} days; "
            f"{m['total_all']} contributions since {nice_date(m['since'])}.")
    _anim_css(s)
    s.add(s.panel(10, 10, 1180, 340, rx=24, accent=PINK, glow_at=(1, 1), glow_op=.12))
    s.add(f'<rect x="40" y="10" width="64" height="3" rx="1.5" fill="{PINK}"/>')
    bd, bc = m["busiest"]
    _card_header(s, 40, 34, "pulse", "pink", "Contribution Pulse",
                 f"weekly contributions · last 52 weeks · busiest day {bc} on {nice_date(bd)}")
    updated = dt.datetime.now(dt.timezone.utc).strftime("%b %d, %Y · %H:%M UTC")
    s.add(s.text(1160, 55, f"updated {updated}", "m5", 12, DIM, anchor="end"))
    s.add(f'<circle cx="{1160 - text_width("updated " + updated, "m5", 12) - 12:.1f}" cy="51" r="4" fill="{GREEN}"/>'
          f'<circle class="ping" cx="{1160 - text_width("updated " + updated, "m5", 12) - 12:.1f}" cy="51" r="4" '
          f'fill="{GREEN}"/>')

    # KPI column
    kpis = [
        ("flame", "gold", f"{cur}", "current streak",
         ("day" if cur == 1 else "days") + (f" · {nice_date(cur_s, False)} – {nice_date(cur_e, False)}" if cur else "")),
        ("star", "violet", f"{lng}", "longest streak",
         ("day" if lng == 1 else "days") + (f" · {nice_date(lng_s, False)} – {nice_date(lng_e)}" if lng else "")),
        ("spark", "cyan", fmt(m["total_all"]), "total contributions", f"since {nice_date(m['since'])}"),
    ]
    for i, (ic, acc, val, label, sub) in enumerate(kpis):
        light, main, deep = ACCENTS[acc]
        y = 104 + i * 76
        g = s.linear([(0, light), (.6, main), (1, deep)], 0, 0, .6, 1)
        vw = text_width(val, "d7", 34)
        s.add(f'<g class="rise" style="animation-delay:{.1 + .1 * i:.2f}s">'
              f'<rect x="40" y="{y}" width="300" height="64" rx="14" fill="#0b1222" fill-opacity=".7" '
              f'stroke="{EDGE_HI}" stroke-opacity=".55"/>'
              + icon(ic, 54, y + 21, 22, light, 1.8)
              + s.text(90, y + 44, val, "d7", 34, f"url(#{g})")
              + s.text(90 + vw + 10, y + 30, label, "d5", 15, SOFT)
              + s.text(90 + vw + 10, y + 49, sub, "m5", fit_size(sub, "m5", 12, 240 - vw - 10, 9), DIM)
              + "</g>")

    # weekly area chart
    cx0, cy0, cw, ch = 380, 104, 780, 196
    weeks = m["weeks"]
    vmax = max([c for _, c in weeks] + [1])
    top = _nice_ceiling(vmax)
    for k in range(4):  # gridlines
        gy = cy0 + ch - ch * k / 3
        s.add(f'<line x1="{cx0}" y1="{gy:.1f}" x2="{cx0 + cw}" y2="{gy:.1f}" stroke="#1e293b" '
              f'stroke-dasharray="{"0" if k == 0 else "3 6"}"/>')
        s.add(s.text(cx0 - 10, gy + 4, fmt(round(top * k / 3)), "m5", 11, DIM, anchor="end"))
    n = len(weeks)
    pts = [(cx0 + cw * i / max(n - 1, 1), cy0 + ch - ch * c / top) for i, (_, c) in enumerate(weeks)]
    if len(pts) >= 2:
        line = _smooth(pts, cy0 + ch)
        area = line + f"L{pts[-1][0]:.1f} {cy0 + ch}L{pts[0][0]:.1f} {cy0 + ch}Z"
        stroke = s.linear([(0, CYAN), (.5, VIOLET), (1, PINK)], cx0, 0, cx0 + cw, 0, units="userSpaceOnUse")
        fill = s.linear([(0, VIOLET, .38), (1, VIOLET, 0)], 0, cy0, 0, cy0 + ch, units="userSpaceOnUse")
        glow = s.glow_filter(4)
        s.add(f'<path d="{area}" fill="url(#{fill})" class="fade" style="animation-delay:.9s"/>')
        s.add(f'<path d="{line}" stroke="url(#{stroke})" stroke-width="2.6" stroke-linecap="round" '
              f'stroke-linejoin="round" pathLength="1000" stroke-dasharray="1000" filter="url(#{glow})" '
              f'style="animation:draw 2.4s cubic-bezier(.4,0,.2,1) .2s both"/>')
        # peak + latest markers
        pi = max(range(n), key=lambda i: weeks[i][1])
        px, py = pts[pi]
        label = f"peak {weeks[pi][1]}/wk"
        if px < cx0 + 70:  # keep the label inside the plot and clear of the y-axis
            lx_, ly_, anchor = px + 12, py + 4, "start"
        elif px > cx0 + cw - 70:
            lx_, ly_, anchor = px - 12, py + 4, "end"
        else:
            lx_, ly_, anchor = px, py - 12, "middle"
        s.add(f'<g class="fade" style="animation-delay:1.8s"><circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" '
              f'fill="{VIOLET}"/>' + s.text(lx_, ly_, label, "m5", 12, "#c4b5fd", anchor=anchor) + "</g>")
        lx, ly = pts[-1]
        s.add(f'<g class="fade" style="animation-delay:2.4s"><circle cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" '
              f'fill="{PINK}"/><circle class="ping" cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="{PINK}"/></g>')
    # month labels
    last_month = None
    for i, (d, _) in enumerate(weeks):
        if d.month != last_month and i < n - 2:
            last_month = d.month
            x = cx0 + cw * i / max(n - 1, 1)
            s.add(s.text(x, cy0 + ch + 24, d.strftime("%b"), "m5", 12, DIM, anchor="middle"))
    return s


def _nice_ceiling(v: float) -> int:
    """Top of the y-axis: three equal, round gridline steps that cover v."""
    raw = max(v, 3) / 3
    mag = 10 ** math.floor(math.log10(raw))
    step = next(f * mag for f in (1, 2, 2.5, 5, 10) if f * mag >= raw)
    return math.ceil(step) * 3


def _smooth(pts: list[tuple[float, float]], floor: float) -> str:
    """Catmull-Rom spline through the points as cubic Beziers, clamped so it never dips below the baseline."""
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, min(p1[1] + (p2[1] - p0[1]) / 6, floor))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, min(p2[1] - (p3[1] - p1[1]) / 6, floor))
        d += f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d


# =================================================================================== main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "BEAST04289"))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--render-only", action="store_true", help="re-render from data.json without fetching")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cache_path = out / "data.json"
    data = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    data["user"] = args.user

    fresh = 0
    if not args.render_only:
        f = Fetcher(args.user, os.environ.get("GITHUB_TOKEN") or None)
        for key, fn in (("profile", f.profile), ("languages", f.languages), ("search", f.search),
                        ("calendar", lambda: f.calendar((data.get("profile") or {}).get("created_at")))):
            try:
                data[key] = fn()
                fresh += 1
                print(f"fetched {key}")
            except Exception as exc:
                print(f"::warning::{key} fetch failed ({exc}); keeping the last good values")
    if not data.get("calendar"):
        print("::error::no contribution data yet, nothing to render")
        return 0
    data["updated"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    m = derive(data)
    cards = {"overview.svg": render_overview(data, m), "languages.svg": render_languages(data),
             "activity.svg": render_activity(data, m)}
    for name, svg in cards.items():
        doc = svg.render()
        (out / name).write_text(doc, encoding="utf-8", newline="\n")
        print(f"  wrote {name} ({len(doc) / 1024:.1f} KB)")
    if fresh or args.render_only:
        cache_path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
