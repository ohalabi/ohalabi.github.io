# v2 handover

A rebuild of osamahalabi.com. Lives in `v2/` so the v1 site at the repo root is
untouched and you can put the two side by side before committing to anything.

**Nothing in `Data/` was modified.** Every publication, grant, award, project,
student and course still comes from the same eight JSON files v1 reads. Only the
presentation layer is new. If you decide v2 was a mistake, you lose an
afternoon, not your content.

---

## 1. What changed, and the reasoning

### Light, not navy

v1's radial-gradient navy + gold + cyan + particle canvas + glow shadows is,
feature for feature, the house style of AI-generated portfolio sites — which is
the exact outcome `PLAN.md` §1 says to avoid. But the stronger argument is about
the content: **54 of the site's images are screenshots, plots and system
diagrams captured on white backgrounds.** On navy they sit inside dark boxes and
read as holes in the page. On paper they read as figures in a journal. The
imagery is the best asset here, so the page defers to it.

Concretely removed: the radial gradient, `canvas#bg` and `particles.js`, the
gold drop-shadow glow, the second accent colour, 14px card radii, and
centre-aligned hero text. Concretely added: hairline rules, a sticky label rail
on data pages, a serif display face, and asymmetric two-column layouts.

### Six destinations, not twelve

v1 had 8 top-level nav items plus a 4-item sub-nav under XReality Lab. That put
`Research` two clicks deep under the lab while `Publications` sat at top level —
the two halves of one body of work, split apart.

| v1 | v2 |
|---|---|
| Home | `index.html` |
| About | `about.html` — now also absorbs Awards (42) and Service |
| XReality Lab → Overview | *gone* — it was a menu pointing at three pages |
| XReality Lab → Research | `research.html` — top level, with filters |
| XReality Lab → Grants | a funding section inside `research.html#funding` |
| XReality Lab → Members | `people.html` — top level |
| Publications | `publications.html` — now filterable |
| Teaching | `teaching.html` |
| Awards | folded into `about.html#awards` |
| Service | folded into `about.html#service` |
| Contact | `contact.html` |

XReality Lab survives as the brand — it's in the masthead and it's the eyebrow
on the Research page — it just isn't a nav silo any more.

Awards and Service moved into About because a 42-item awards page is a page
almost nobody browses, while the same 42 items are genuinely impressive sitting
inside a biography. Both still have their own anchors for linking.

### Serif display face, no new webfont

`--serif` is `"Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua",
Georgia, serif`. Palatino Linotype ships on Windows, Iowan Old Style on macOS,
Georgia everywhere. Zero bytes, no CDN, and none of them are default-AI-pick
faces. IBM Plex Sans (already self-hosted in `assets/fonts/`) still carries body
and UI text.

If you'd rather have one consistent face across platforms, **IBM Plex Serif** is
the natural upgrade — same superfamily as Plex Sans, designed to pair with it.
Download `ibm-plex-serif-400.woff2` and `-600.woff2`, drop them in
`assets/fonts/`, add two `@font-face` blocks, and put `"IBM Plex Serif"` at the
front of `--serif`. Nothing else changes.

---

## 2. Files

```
v2/
├── scripts/build.py           the generator — ~700 lines, stdlib only
├── assets/css/style.css       the whole design system
├── assets/js/site.js          mobile nav + the shared list filter
├── assets/js/research.js      project filtering + detail drawer
├── assets/img/, assets/fonts/ copied from the repo root on first build
├── index.html … 404.html      GENERATED — never hand-edit
├── sitemap.xml, robots.txt    GENERATED
├── CLAUDE.md                  instructions for you
└── HANDOVER.md                this file
```

Build: `cd v2 && python scripts/build.py`

`build.py` finds `Data/` by walking up from its own location, so it works
whether `v2/` sits beside the old site or is promoted to the repo root. Nothing
to edit when you move it.

---

## 3. The one new concept: project themes

`projects.json` groups the 27 projects into three categories — Core Research,
Laser Graphics & Visual Art, Foundational. Those are **eras**, not subjects, so
they can't answer "show me the haptics work". v2 adds a subject axis in
`build.py`:

```python
THEMES = {"haptics": "Haptics & Touch", "vr": "Virtual Reality",
          "ar": "Augmented Reality", "health": "Health & Accessibility",
          "mobility": "Driving & Mobility", "laser": "Laser Graphics & Art",
          "sensing": "Sensing & IoT"}

THEME_RULES = [("tactile footwear", "haptics"), ("firefighting", "vr"), ...]
```

First matching substring wins. **If a project matches no rule the build fails
loudly** rather than dropping it into an untagged bucket — so adding a project
to `projects.json` without tagging it is impossible to miss.

Current distribution: haptics 8, laser 5, vr 4, mobility 4, health 3, ar 2,
sensing 1. Sensing & IoT having one member is honest rather than tidy; merge it
if the single chip bothers you.

---

## 4. Behaviour contract

Everything below was verified in headless Chromium. Keep it working.

**Research page**

1. Subject and era filters compose (Haptics + Foundational → 5 results)
2. Search covers title, subject, era and all description text
3. Search debounced ~130 ms; result count in an `aria-live` region
4. Empty state offers one-click "clear all filters"
5. Cards are real `<a href="#slug">` links — crawlable, ⌘-clickable
6. Plain left-click opens the drawer instead of navigating
7. Opening a project sets `location.hash` and `document.title`
8. Cold-loading `research.html#firefighting-simulation…` opens that drawer
9. Back closes the drawer; Back again returns to the previous project
10. `Esc` closes, `←`/`→` walk prev/next **through the filtered list**
11. Tab is trapped inside the drawer while open; focus returns to the card
12. Body scroll locks while the drawer is open
13. **No-JS: all 27 cards and all 27 full detail sections render and are
    readable.** The details are only hidden once `research.js` confirms it ran,
    via `documentElement.classList.add("js-drawer")`. Don't move that hide into
    the stylesheet unconditionally.

**Publications page** — type chips + search over 145 entries; year headings hide
when every entry under them is filtered out; Reset clears everything.

**Both** — `prefers-reduced-motion` collapses transitions; there's a print
stylesheet, because committees print these pages more often than you'd think.

---

## 5. Two bugs this rebuild found in the funding maths

Both were in how v1 would have totalled `grants.json`, and both produced a wrong
public number. `money()` in `build.py` now handles them and says why:

- **`$1,049,427.58`** — stripping all non-digits turned the cents into two extra
  digits, reporting that single award as **$104,942,758** and the site total as
  $113.83M.
- **`¥5,000,000`** — a Japanese award was being summed as though it were
  dollars. Rather than bake in a historical exchange rate, non-USD awards are
  now excluded from USD totals, still listed in the table, and disclosed in the
  table caption.

Correct total: **$4.93M across 31 awards**, 5 currently active worth $1.58M.
Active/completed status is derived from the award period against the current
year, never stored — so it can't go stale.

---

## 6. Known gaps — deliberately left for you

1. **The headshot is composited on navy.** `build_headshot.py` put it on a
   navy/gold background for the dark site; on paper it reads as a dark
   rectangle. Re-run that script with a light background — the source is
   `Data/Doc. Osama_2.png`. Highest-value single fix on the site.
2. **Project text is objectives, not abstracts.** The harvested bullets read as
   aims ("To design and implement a haptic insole that…"). They work, but a
   two-sentence outcome paragraph per project would be much stronger. Add an
   `"overview"` key to each project in `projects.json`; `build.py` should prefer
   it over `bullets[0]` for the card blurb.
3. **Projects have no year.** So they can't sort chronologically and no
   active/completed state is shown. Add `"years"` to `projects.json` and it
   becomes a third filter almost for free.
4. **No project ↔ publication link.** You have 145 publications and 27 projects
   and no mapping between them. A `"projectId"` on publication entries would let
   the drawer list a project's papers from the same source that builds
   `/publications` — no citation strings duplicated and drifting.
5. ~~Confirm the Google Scholar and ResearchGate URLs~~ — **done**, both verified
   (Scholar: name/affiliation/research-interests match; ResearchGate: matched
   via search index, direct fetch 403'd on bot protection).
6. ~~`favicon.png` doesn't exist yet.~~ — **done**, `scripts/build_favicon.py`
   crops an icon-only mark (a favicon renders at 16-32px, so any baked-in
   wordmark is illegible regardless of which lockup it comes from —
   icon-only is what actually reads at that size). Originally sourced from
   `Logo/xreality-logo-clean-512.png` (transparent background); switched to
   `Logo/xreality-logo-card-512.png` (opaque white background, the card
   variant this note originally passed over) after the transparent version
   turned out to disappear against a dark browser tab bar.
7. **Image weight.** `assets/img/projects/` is ~20 MB of PNGs, several over
   700 KB. Convert to WebP with the existing Pillow pipeline before launch —
   this is the main Lighthouse item.
8. **Lab members have no photos**, and `people.html` has room for them.

---

## 7. Promoting v2 to the site root — DONE

This happened. One thing the plan above got wrong, for whoever reads this
next: `mv v2/* .` alone doesn't work once `assets/` and `scripts/` already
exist at the root (both v1 and v2 have their own) — a plain `mv` of a
directory onto an existing directory of the same name nests it
(`assets/assets/`) rather than replacing it. What actually ran:

```bash
# from the repo root
mkdir v1-archive
mv index.html about.html publications.html teaching.html \
   awards.html service.html contact.html design-preview.html \
   lab assets v1-archive/                 # whole v1 assets/ dir, archived
mkdir v1-archive/scripts
mv scripts/build.py v1-archive/scripts/build.py   # only build.py -- the other
                                                    # three scripts (sync_orcid.py,
                                                    # build_headshot.py,
                                                    # harvest_research_page.py)
                                                    # were never duplicated into
                                                    # v2/scripts/ and stayed put

mv v2/about.html v2/contact.html v2/index.html v2/people.html \
   v2/publications.html v2/research.html v2/teaching.html \
   v2/404.html v2/sitemap.xml v2/robots.txt .
mv v2/assets .                              # now safe -- root's assets/ is gone
mv v2/scripts/build.py scripts/build.py     # root's scripts/ still has the other 3

rm -rf v2/Data                              # just a copied CV, not source content
mv v2/.claude/skills/run-v2 .claude/skills/run-site   # renamed; see its SKILL.md
mv v2/HANDOVER.md HANDOVER.md               # this file
# v2/CLAUDE.md's content became the new root CLAUDE.md (hand-merged, not moved)
rm -rf v2

python scripts/build.py                     # confirms DATA_DIR still resolves
```

`build.py` itself needed no edits: `find_upward("Data", …)` resolves the same
from the repo root, and `copy_shared_assets()` is now a genuine no-op since
source and destination are the same directory.

**Since resolved, both were deliberately left open at promotion time**:
`v1-archive/` would have been publicly served as-is by GitHub Pages (see
`PLAN.md` §7) — deleted 2026-08-15, 15 MB, no longer an issue. The favicon
404 is also fixed (§6 item 6 below) — `driver.py`'s `KNOWN_404S` allowlist
is empty again.

Then work through `PLAN.md` §6 (QA) and §7 (deploy). The 404 page, `sitemap.xml`
and `robots.txt` from that checklist are already generated.
