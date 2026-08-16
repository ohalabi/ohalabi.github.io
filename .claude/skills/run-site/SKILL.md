---
name: run-site
description: Build, serve, and drive osamahalabi.com — filter the Research page's theme chips, open/close its project detail drawer, search Publications, and screenshot the result. Use when asked to run the site, start the site, build the site, take a screenshot of it, or verify a change actually works in a browser.
---

The site is a generated static site (Python f-strings in `scripts/build.py`,
no framework, no npm) with one real interactive surface: `research.html`'s
theme/era filter chips + a slide-in project detail drawer, and a simpler
search-box filter on `publications.html`. Drive it via
`.claude/skills/run-site/driver.py` — a Playwright script that builds the
site, serves it over real HTTP, and clicks through both.

This skill was authored as `run-v2` while the redesign lived side-by-side
with the old site in a `v2/` subdirectory, then moved here (and renamed)
when `v2/` was promoted to the repo root. All paths below are relative to
the **repo root** — that's also where this skill's driver now resolves
paths from (`.claude/skills/run-site/driver.py`, 4 parents up).

Verified on Windows (Git Bash) with Python 3.14 and Microsoft Edge already
installed. If running on Linux, see the Gotchas note on the Playwright
browser channel before trusting the driver unmodified.

## Prerequisites

```bash
python -m pip install playwright
```

No `playwright install` / browser download needed — the driver launches
the **system-installed Edge** via Playwright's `channel="msedge"`, which
this repo's Windows environment already has. (See Gotchas if that channel
isn't available on your machine.)

## Build

```bash
python scripts/build.py
```

Writes `index.html`, `research.html`, `publications.html`, `teaching.html`,
`people.html`, `about.html`, `contact.html`, `404.html`, `sitemap.xml`,
`robots.txt` into the repo root. Prints a project/publication/grant/people/
award count line — sanity-check it's non-zero.

The driver (below) runs this build step itself, so you don't need to run
it separately unless you just want the build without the browser pass.

## Run (agent path)

```bash
python .claude/skills/run-site/driver.py
```

This one command builds the site, serves the repo root over
`http://127.0.0.1:<a free port>/` (a background
`http.server.ThreadingHTTPServer` thread — not `file://`, so it matches how
GitHub Pages actually serves it), and drives it with Playwright against the
system Edge:

1. loads `index.html`, checks the title
2. loads `research.html`, confirms all 50 `.pcard` elements are present
   and `research.js` ran (`<html class="js-drawer">`)
3. clicks the "Haptics & Touch" filter chip, asserts exactly 11 cards are
   now visible and the chip's `aria-pressed` flips to `"true"`
4. clicks a card to open the detail drawer, asserts the drawer's content
   matches the clicked project, closes it, resets filters
5. on `publications.html`, types "haptic" into the search box and reads
   back the "N publications shown" count
6. collects console errors and any HTTP response ≥400, filtering out the
   one **known** issue (see Gotchas) so a genuinely new failure still
   fails the run

Exits 0 and prints `PASS -- screenshots in <path>` on success; prints
`FAIL: <reason>` per failed assertion and exits 1 otherwise.

Screenshots land in `.claude/skills/run-site/screenshots/`:

| file | what it shows |
|---|---|
| `01_home.png` | home page, full load |
| `02_research_all.png` | Research page, unfiltered (50 cards) |
| `03_research_filtered_haptics.png` | after clicking the "Haptics & Touch" chip |
| `04_research_drawer_open.png` | detail drawer open, settled (post-transition) |
| `05_publications_filtered.png` | Publications page, search box filtered to "haptic" |

## Run (human path)

```bash
python scripts/build.py
python -m http.server 8000
# open http://localhost:8000/index.html in a browser; Ctrl-C to stop
```

## Gotchas

- **`find_upward("Data", …)` used to break on the second build.** This bit
  while the site still lived in `v2/` and is why the fix below exists, but
  the underlying shape of the bug can recur if `scripts/build.py` is ever
  moved again: `copy_shared_assets()` copies `cv_Osama_Halabi.pdf` into
  `<script's own dir>/Data/` on a successful build. If a `Data/` directory
  ever exists *above* the real one, `find_upward` used to match it via a
  bare `os.path.isdir` check before ever reaching the real `Data/*.json`.
  Fixed by requiring `marker="profile.json"` — the candidate directory must
  actually contain it, not just exist. If `FileNotFoundError: ...
  Data\profile.json` reappears, this is why; check the fix wasn't reverted.
- **`assets/img/favicon.png` used to 404 on every page — fixed.** It was
  referenced in `build.py`'s `<head>` from the start but never generated.
  `scripts/build_favicon.py` now crops the icon-only mark (no "XREALITY
  LAB" wordmark — illegible at the 16-32px a favicon actually renders at)
  out of `Logo/xreality-logo-clean-512.png` and writes it. `driver.py`'s
  `KNOWN_404S` allowlist is empty again (was a one-entry tuple for this) —
  if it ever needs an entry again, that's a deliberate decision each time,
  not a rubber stamp.
- **The favicon has gone transparent → white-card → transparent.** It first
  shipped cropped from `xreality-logo-clean-512.png` (transparent
  background); switched to `xreality-logo-card-512.png` (opaque white)
  because the transparent version was faint against a dark browser tab bar;
  switched back to transparent (2026-08-16) as the better general default.
  If tab-bar visibility comes up again, the card variant is the known
  fallback — don't rediscover this from scratch.
- **The drawer screenshot needs a post-transition wait.** `.drawer` is
  `position:fixed` with `transition:transform .38s`; `driver.py` waits for
  the `.open` class (added synchronously by `research.js`) but that fires
  at the *start* of the CSS transition, not the end. Screenshotting
  immediately caught it mid-slide, cut off at the viewport edge. Fixed
  with an explicit `page.wait_for_timeout(450)` after the class appears —
  if you add more drawer-adjacent screenshots, they need the same wait.
- **Playwright's `channel="msedge"` needs system Edge, not a download.**
  This avoided a Chromium download (`playwright install`) by pointing at
  the Edge already on this Windows machine. On a container/Linux box
  without Edge, switch to `p.chromium.launch(headless=True)` (default
  channel) and run `python -m playwright install chromium` first — untested
  in this session, since the target machine already had Edge.
- **`python3` on this machine lacks Pillow/Playwright; `python` has them.**
  Two Python installs are on PATH here (`python` → 3.14 with packages,
  `python3` → 3.12, bare). Not specific to this site, but if a command
  silently fails with `ModuleNotFoundError`, check which `python` ran.

## Troubleshooting

- **`FileNotFoundError: ... Data\profile.json`**: see the `find_upward`
  Gotcha above — the fix should already be in `scripts/build.py`; if this
  recurs, it was reverted.
- **Driver reports `FAIL: N unexpected failed HTTP response(s)`**: read
  the printed list. `KNOWN_404S` in `driver.py` is currently empty, so any
  failure here is a real regression, not noise.
- **Driver hangs / times out launching the browser**: confirm Edge is
  actually installed (`playwright` needs `channel="msedge"` to resolve to
  a real binary) — this doesn't install a browser for you the way the
  default Chromium channel does.
