"""Generates assets/stats-{dark,light}.svg from the GitHub contribution calendar.

Run: GH_TOKEN=... python3 scripts/stats.py   (stdlib only; runs daily in Actions)
"""
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

LOGIN = os.environ.get("STATS_LOGIN", "iluvcashnhash")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

W, H = 1200, 270
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SERIF = "Georgia,'Times New Roman',serif"
PALETTES = {
    "dark": dict(bg="#07080c", ink="#e8e6df", dim="#8b90a0", faint="#2a2e3a", glow="#f3d9a4", accent="#9fb4ff"),
    "light": dict(bg="#f7f5ef", ink="#1b1d24", dim="#6d7080", faint="#d8d4c8", glow="#d99a3a", accent="#3e5bd6"),
}

QUERY = """query($login:String!){user(login:$login){
  repositories(ownerAffiliations:OWNER,privacy:PUBLIC){totalCount}
  contributionsCollection{contributionCalendar{totalContributions
    weeks{contributionDays{contributionCount date}}}}}}"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def streaks(days):
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    # today may still be empty: the streak is alive if yesterday counted
    i = len(counts) - 1
    if counts[i] == 0:
        i -= 1
    current = 0
    while i >= 0 and counts[i]:
        current += 1
        i -= 1
    return current, longest


def plural(n, one, few, many):
    n = abs(n) % 100
    if 10 < n < 20:
        return many
    n %= 10
    return one if n == 1 else few if 2 <= n <= 4 else many


def fmt(n):
    return f"{n:,}".replace(",", " ")


def build(theme, user):
    p = PALETTES[theme]
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    total = cal["totalContributions"]
    current, longest = streaks(days)
    active = sum(1 for d in days if d["contributionCount"])
    best = max(days, key=lambda d: d["contributionCount"])
    repos = user["repositories"]["totalCount"]

    figures = [
        (fmt(total), plural(total, "вклад", "вклада", "вкладов") + " за год"),
        (str(current), plural(current, "день", "дня", "дней") + " подряд сейчас"),
        (str(longest), "самая длинная серия"),
        (f"{active}/{len(days)}", "активных дней"),
        (str(best["contributionCount"]), "рекорд за день"),
    ]

    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
      f'aria-label="Активность на GitHub: {total} вкладов за год, серия {current}, рекорд серии {longest}">'
      "<title>Активность на GitHub</title>")
    a("<style>")
    a(".f{animation:up .8s cubic-bezier(.2,.7,.2,1) both}@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}")
    a(".d{animation:on .5s ease-out both}@keyframes on{from{opacity:0}}")
    a(".hot{animation:tw 2.8s ease-in-out infinite alternate}@keyframes tw{to{opacity:.35}}")
    a("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    a("</style>")
    a(f'<rect width="{W}" height="{H}" rx="14" fill="{p["bg"]}"/>')

    # figures
    col = (W - 56) / len(figures)
    for i, (num, label) in enumerate(figures):
        x = 28 + i * col
        a(f'<g class="f" style="animation-delay:{i * 0.08:.2f}s">')
        a(f'<text x="{x:.0f}" y="66" font-family="{SERIF}" font-size="40" fill="{p["ink"]}">{num}</text>')
        a(f'<text x="{x:.0f}" y="90" font-family="{MONO}" font-size="11" letter-spacing="1.5" fill="{p["dim"]}">{label}</text>')
        a("</g>")

    # the year as a field of stars: one dot per day
    top, step = 126, 16
    left = (W - (len(weeks) - 1) * step) / 2
    peak = max(1, best["contributionCount"])
    n = 0
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            wd = dt.date.fromisoformat(d["date"]).weekday()  # Mon=0
            x, y = left + wi * step, top + wd * step
            c = d["contributionCount"]
            delay = f'style="animation-delay:{0.3 + wi * 0.012:.2f}s"'
            if c == 0:
                a(f'<circle class="d" {delay} cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="{p["faint"]}"/>')
            else:
                t = (c / peak) ** 0.5
                r = 2.2 + 3.8 * t
                fill = p["glow"] if t > 0.6 else p["ink"]
                hot = " hot" if t > 0.6 else ""
                a(f'<circle class="d{hot}" {delay} cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" opacity="{0.35 + 0.65 * t:.2f}"/>')
            n += 1

    foot = top + 7 * step + 10
    first = dt.date.fromisoformat(days[0]["date"])
    last = dt.date.fromisoformat(days[-1]["date"])
    months = "янв фев мар апр май июн июл авг сен окт ноя дек".split()
    a(f'<text x="{left:.0f}" y="{foot:.0f}" font-family="{MONO}" font-size="10" fill="{p["dim"]}" letter-spacing="1">{months[first.month - 1]} {first.year}</text>')
    a(f'<text x="{W / 2:.0f}" y="{foot:.0f}" font-family="{MONO}" font-size="10" fill="{p["dim"]}" letter-spacing="1" text-anchor="middle">{repos} {plural(repos, "публичный репозиторий", "публичных репозитория", "публичных репозиториев")} · обновлено {last:%d.%m.%Y}</text>')
    a(f'<text x="{W - left:.0f}" y="{foot:.0f}" font-family="{MONO}" font-size="10" fill="{p["dim"]}" letter-spacing="1" text-anchor="end">{months[last.month - 1]} {last.year}</text>')
    a("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("set GH_TOKEN")
    user = fetch()
    root = Path(__file__).resolve().parent.parent / "assets"
    for theme in PALETTES:
        (root / f"stats-{theme}.svg").write_text(build(theme, user), encoding="utf-8")
        print("wrote", f"assets/stats-{theme}.svg")
