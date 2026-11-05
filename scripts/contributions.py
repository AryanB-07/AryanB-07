"""Draw assets/contributions.svg from the public contribution calendar. Standard library only."""
import datetime as dt
import re
import sys
import urllib.request
from pathlib import Path

USER = "AryanB-07"
BG, DIM, EDGE, VIOLET = "#0b0e1a", "#8590a8", "#2a3350", "#8b5cf6"
LEVELS = ["#151a2c", "#2c4a9e", "#5b8bf5", "#8b5cf6", "#e46ad6"]
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
CELL, GAP, X0, Y0 = 15, 3, 23, 72
W, DUR = 1000, 9


def fetch():
    req = urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                                 headers={"X-Requested-With": "XMLHttpRequest", "User-Agent": "profile-graph"})
    html = urllib.request.urlopen(req, timeout=30).read().decode()
    days = {}
    for tag in re.findall(r"<td[^>]*data-date=[^>]*>", html):
        date = re.search(r'data-date="([\d-]+)"', tag)
        level = re.search(r'data-level="(\d)"', tag)
        if date and level:
            days[dt.date.fromisoformat(date.group(1))] = int(level.group(1))
    if len(days) < 300:
        sys.exit(f"expected a year of days, got {len(days)}: did GitHub's markup change?")
    return days


def build(days, animated):
    first = min(days)
    first -= dt.timedelta(days=(first.weekday() + 1) % 7)
    weeks = max((d - first).days // 7 for d in days) + 1
    h = Y0 + 7 * (CELL + GAP) + 20
    width = weeks * (CELL + GAP) - GAP
    cells, months = "", ""
    seen = None
    for day, level in sorted(days.items()):
        col, row = (day - first).days // 7, (day.weekday() + 1) % 7
        x, y = X0 + col * (CELL + GAP), Y0 + row * (CELL + GAP)
        inner = ""
        if animated and level:
            at = col / weeks * 0.8
            inner = (f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" '
                     f'keyTimes="0;{at:.3f};{at + 0.03:.3f};{at + 0.14:.3f};1" values="0.6;0.6;1;0.6;0.6"/>')
        cells += f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{LEVELS[level]}">{inner}</rect>'
        if day.day <= 7 and row == 0 and day.month != seen and col < weeks - 2:
            seen = day.month
            months += f'<text x="{x}" y="{Y0 - 10}" font-family="{MONO}" font-size="13" fill="{DIM}">{day:%b}</text>'
    scan = ""
    if animated:
        scan = (f'<rect y="{Y0 - 4}" width="2" height="{7 * (CELL + GAP) + 5}" rx="1" fill="{VIOLET}" x="{X0}" opacity="0.8">'
                f'<animate attributeName="x" dur="{DUR}s" repeatCount="indefinite" keyTimes="0;0.8;1" values="{X0};{X0 + width};{X0 + width}"/>'
                f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" keyTimes="0;0.8;0.82;0.98;1" values="0.8;0.8;0;0;0.8"/></rect>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="contribution graph for the last year">'
            f'<title>contributions</title><rect width="{W}" height="{h}" rx="16" fill="{BG}"/>'
            f'<rect x="0.75" y="0.75" width="{W - 1.5}" height="{h - 1.5}" rx="15.5" fill="none" stroke="{EDGE}" stroke-width="1.5"/>'
            f'<circle cx="26" cy="26" r="5" fill="{EDGE}"/><circle cx="44" cy="26" r="5" fill="{EDGE}"/><circle cx="62" cy="26" r="5" fill="{EDGE}"/>'
            f'<text x="{W - 24}" y="31" text-anchor="end" font-family="{MONO}" font-size="14" fill="{DIM}">contributions</text>'
            f"{months}{cells}{scan}</svg>\n")


days = fetch()
root = Path(__file__).resolve().parent.parent / "assets"
(root / "contributions.svg").write_text(build(days, True))
(root / "static" / "contributions.svg").write_text(build(days, False))
