#!/usr/bin/env python3
"""
Driver for osamahalabi.com (c:/Users/ohala/Claude Code/my-website).

Formerly "the v2 site" -- promoted to the repo root once the redesign was
signed off; this skill moved from v2/.claude/skills/run-v2/ to
.claude/skills/run-site/ along with it. See HANDOVER.md for the rebuild
rationale and v1-archive/ for the previous (navy) site this replaced.

Builds the site, serves it over real HTTP (not file:// -- research.html's
data-search attributes and the drawer both work fine under file://, but
serving matches how GitHub Pages will actually serve it), drives it with
Playwright against the machine's installed Edge (no Chromium download
needed -- `channel="msedge"`), and exercises the one interactive surface
that matters here: research.html's theme-filter chips + detail drawer.

Usage (from the repo root):
    python .claude/skills/run-site/driver.py

Screenshots land in .claude/skills/run-site/screenshots/. Exits non-zero if
any page fails to load, a console error fires, or the interaction
assertions fail (chip filtering the grid, drawer opening/closing).
"""
import http.server
import socket
import subprocess
import sys
import threading
from pathlib import Path

# .claude/skills/run-site/driver.py -> repo root (4 parents up)
SITE_DIR = Path(__file__).resolve().parents[3]
SKILL_DIR = Path(__file__).resolve().parent
SHOTS_DIR = SKILL_DIR / "screenshots"


def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def build():
    print("== build ==")
    r = subprocess.run([sys.executable, "scripts/build.py"], cwd=SITE_DIR,
                        capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit("build.py failed")


def serve(port):
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(SITE_DIR), **kw)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def main():
    SHOTS_DIR.mkdir(exist_ok=True)
    build()

    port = free_port()
    httpd = serve(port)
    base = f"http://127.0.0.1:{port}"
    print(f"== serving {base} ==")

    from playwright.sync_api import sync_playwright

    failures = []
    console_errors = []
    failed_responses = []  # (status, url) for any 4xx/5xx

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 900})
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("response", lambda r: failed_responses.append((r.status, r.url)) if r.status >= 400 else None)
        page.on("pageerror", lambda e: console_errors.append(str(e)))

        # -- home --------------------------------------------------------
        page.goto(f"{base}/index.html", wait_until="networkidle")
        if "Osama Halabi" not in page.title():
            failures.append(f"home: unexpected title {page.title()!r}")
        page.screenshot(path=str(SHOTS_DIR / "01_home.png"))

        # -- research: initial state -------------------------------------
        page.goto(f"{base}/research.html", wait_until="networkidle")
        page.wait_for_selector("html.js-drawer", timeout=3000)  # research.js ran
        all_count = page.locator(".pcard").count()
        if all_count != 50:
            failures.append(f"research: expected 50 .pcard on load, got {all_count}")
        page.screenshot(path=str(SHOTS_DIR / "02_research_all.png"))

        # -- research: click the "Haptics & Touch" chip -------------------
        page.click('.chip[data-kind="theme"][data-val="haptics"]')
        page.wait_for_timeout(150)  # render() is synchronous but let layout settle
        visible = page.locator(".pcard:visible").count()
        if visible != 11:
            failures.append(f"research: haptics chip should show 11 cards, got {visible}")
        chip_pressed = page.get_attribute('.chip[data-val="haptics"]', "aria-pressed")
        if chip_pressed != "true":
            failures.append(f"research: haptics chip aria-pressed={chip_pressed!r}, expected true")
        page.screenshot(path=str(SHOTS_DIR / "03_research_filtered_haptics.png"))

        # -- research: open a card's detail drawer ------------------------
        page.click('.pcard[data-theme="haptics"] h3 a')
        page.wait_for_selector("#drawer.open", timeout=2000)
        page.wait_for_timeout(450)  # .drawer{transition:transform .38s} -- let the slide-in finish
        drawer_text = page.inner_text("#drawer")
        if "Tactile Footwear" not in drawer_text:
            failures.append("research: drawer opened but doesn't contain expected project title")
        page.screenshot(path=str(SHOTS_DIR / "04_research_drawer_open.png"))

        # -- close the drawer, reset filters -------------------------------
        page.click("#drawer-close")
        page.wait_for_timeout(150)
        if "open" in (page.get_attribute("#drawer", "class") or ""):
            failures.append("research: drawer did not close")
        page.click('.chip[data-kind="theme"][data-val="all"]')
        page.wait_for_timeout(150)

        # -- publications: search box filters the list --------------------
        page.goto(f"{base}/publications.html", wait_until="networkidle")
        search = page.locator('input[type="search"], input[placeholder*="Search" i]').first
        search.fill("haptic")
        page.wait_for_timeout(200)
        shown_text = page.locator("text=/\\d+ publications shown/i").first.inner_text()
        page.screenshot(path=str(SHOTS_DIR / "05_publications_filtered.png"))
        print(f"publications filter: {shown_text!r}")

        browser.close()

    httpd.shutdown()

    # assets/img/favicon.png was a known-missing file (see SKILL.md Gotchas
    # history) -- fixed by scripts/build_favicon.py. Nothing allowlisted now;
    # if a new persistent 404 shows up, decide deliberately whether it's
    # another known issue before adding it back here.
    KNOWN_404S = ()
    new_failed = [(s, u) for s, u in failed_responses if not u.endswith(KNOWN_404S)]

    print("\n== failed HTTP responses ==")
    if failed_responses:
        for s, u in failed_responses:
            flag = "" if (s, u) in new_failed else "  (known -- see Gotchas)"
            print(f" - {s} {u}{flag}")
    else:
        print("(none)")
    if new_failed:
        failures.append(f"{len(new_failed)} unexpected failed HTTP response(s), see above")

    print("\n== console errors ==")
    if console_errors:
        for e in console_errors:
            print(" -", e)
    else:
        print("(none)")
    # every console error observed here was the browser's own resource-load
    # message for the favicon 404 above, not a JS exception -- if that stops
    # being true (a real page error appears) this should fail the run too
    if console_errors and not failed_responses:
        failures.append(f"{len(console_errors)} console error(s) with no matching failed response, see above")

    print("\n== result ==")
    if failures:
        for f in failures:
            print("FAIL:", f)
        sys.exit(1)
    print(f"PASS -- screenshots in {SHOTS_DIR}")


if __name__ == "__main__":
    main()
