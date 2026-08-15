# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

The professional site for Osama Halabi (Associate Professor, Qatar University) and his XReality Lab research group (VR/AR/haptics). A generated static site: page chrome is hand-written Python string templates in `scripts/build.py`, all repeatable content (publications, awards, teaching, service, grants, projects, lab members) is data-driven from `Data/*.json`. No JS framework, no npm, no CDN dependencies — output is plain HTML/CSS/JS committed to the repo.

Light editorial direction ("paper & ink"): warm off-white background, near-black ink, one maroon accent (`#8a1538`, Qatar University), serif display face from a system font stack (no new webfont), IBM Plex Sans (self-hosted) for everything else.

This is the **second generation** of this site. The original navy/gold/particle-canvas design was rebuilt in a side-by-side `v2/` directory, verified, and promoted to the repo root — see `HANDOVER.md` for the full rationale (why light-not-navy, why the nav went from 8 items to 6, the two funding-math bugs the rebuild caught) and `v1-archive/` for the previous version's pages, in case anything needs to be recovered or compared.

**Not a git repository yet** — deployment (git init, GitHub Pages, DNS for osamahalabi.com) is still pending; see `PLAN.md` §7.

## Commands

- **After editing any `Data/*.json` file, regenerate the site:** `python scripts/build.py` (run from repo root). Reads `Data/*.json`, writes `index.html`, `research.html`, `publications.html`, `teaching.html`, `people.html`, `about.html`, `contact.html`, `404.html`, `sitemap.xml`, `robots.txt`.
- **Never hand-edit a generated HTML page directly** — those files are build output; edits will be silently overwritten the next time `build.py` runs. Edit the corresponding `Data/*.json` (content), the relevant `build_*()` function in `scripts/build.py` (structure), or `assets/css/style.css` (appearance) instead.
- **Refresh publications:** `python scripts/sync_orcid.py`, then rebuild.
- **Verify a change:** use the `/run-site` skill (`.claude/skills/run-site/`) — it builds the site, serves it over real HTTP, and drives it with Playwright against the machine's installed Edge: loads the home page, filters Research by theme, opens/closes the project detail drawer, and searches Publications, screenshotting each step. This is the actual verification loop, not just "open it in a browser" — for anything touching `research.js` or `site.js`, run it and look at the screenshots.
- No lint/test tooling beyond that. For image asset work (logo recoloring, background removal, headshot compositing), use Python with Pillow and numpy rather than looking for a JS/npm image pipeline — none exists here.

## Hard rules

1. **Never hand-edit a generated `.html` file.** Content → `Data/*.json`. Structure → the `build_*()` functions in `scripts/build.py`. Appearance → `assets/css/style.css`.
2. **Never edit `Data/*.json` to fix a display problem.** That data is the single source of truth (it's also what the archived v1 site read). Formatting belongs in `build.py` — see `prose()` for how the em-dash cleanup is done.
3. **Add new visual patterns to `style.css`, not inline `style=` attributes.** A few inline styles survive in `build.py`; they are debt, not precedent.
4. **Don't reintroduce the old (v1) decoration.** No radial gradients, no particle canvas, no glow drop-shadows, no second accent colour, no large border radii — `HANDOVER.md` §1 explains why they went.
5. **Colour is never the only channel.** Every theme-coloured badge carries its text label too.

## Architecture

- **`scripts/build.py`** — the site generator. `head()` / `masthead()` / `foot()` build the page chrome; `page_head()`, `chip()`, `search_box()`, and the table-builders are shared fragments; one `build_*()` function per page. `find_upward("Data", …)` walks upward from the script's location to find `Data/`, requiring `profile.json` to actually be present in the candidate directory (not just checking `isdir`) — a real bug hit during the promotion, where a `Data/` populated only by `copy_shared_assets()`'s own CV copy would otherwise shadow the real one. `copy_shared_assets()` copies `assets/img`, `assets/fonts`, and the CV in on first build and no-ops once source and destination are the same directory (true now that the site lives at the repo root).
- **`Data/*.json`** — source of truth for repeatable content: `profile.json`, `publications_orcid.json` (synced from ORCID via `sync_orcid.py`), `awards.json`, `grants.json`, `service.json`, `teaching.json`, `projects.json`, `members.json`. `THEME_RULES` in `build.py` maps project titles to subject themes for the Research page filters — adding a project to `projects.json` without a matching rule **fails the build on purpose**; don't add a silent fallback.
- **`assets/js/research.js`** — Research page filtering + the project detail drawer. Progressive enhancement: `build.py` renders every project's full detail into the page, and JS hides those sections only after adding `.js-drawer` to `<html>`. Without JS every project stays fully readable — preserve that.
- **`assets/js/site.js`** — mobile nav, plus a generic list filter driven by `[data-filterable]` / `[data-row]` / `data-facet-*` / `[data-group]`. Publications uses it.
- **`assets/css/style.css`** — tokens on `:root`, then components. Note `[hidden]{display:none !important}` near the top: components set `display:flex`/`grid`, which outranks the user-agent `[hidden]` rule, and without it filtered rows stay visible while the count says otherwise — a real bug the rebuild caught.
- **`assets/fonts/`** — self-hosted IBM Plex Sans woff2 files; the serif display face is a system-font stack (`"Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif` — zero bytes, no CDN). See `HANDOVER.md` §1 if you want to upgrade to a self-hosted IBM Plex Serif later.
- **`assets/img/headshot/`**, **`assets/img/projects/`** — real photos. The headshot is still composited on the old navy/gold background (`scripts/build_headshot.py`) and reads as a dark rectangle on this site's paper background — highest-priority open item, see `HANDOVER.md` §6.
- **`scripts/`** beyond `build.py`: `sync_orcid.py` (ORCID API sync), `build_headshot.py` (one-off headshot compositing), `harvest_research_page.py` (one-off recovery of `projects.json`/`members.json` from legacy saved pages in `Data/`) — all run manually, none part of the `build.py` pipeline.
- **`Logo/`** — several PNG variants of the XReality Lab logo mark from v1-era iterative editing. Not currently referenced by `build.py` (the masthead is a text wordmark now), but `xreality-logo-card-512.png` is the source to generate the still-missing `assets/img/favicon.png` from — see `HANDOVER.md` §6.
- **`v1-archive/`** — the previous site's generated pages, `lab/` subsection, `assets/`, and `scripts/build.py`, kept for reference/rollback. Not part of the live site; don't build from it.
- **`.claude/skills/run-site/`** — the `/run-site` verification skill (`SKILL.md` + `driver.py`), covering how to build, serve, and drive the site. Read its Gotchas section before debugging anything that looks like a console error or a build failure — several non-obvious ones are already documented there (the `find_upward` shadowing bug, the known `favicon.png` 404, a CSS-transition timing trap when screenshotting the drawer).

See `PLAN.md` for the full build history and outstanding items, `HANDOVER.md` for the v1→v2 rebuild rationale and behavior contract.

## Style

- Prefer a targeted change to a rewrite. Read before editing.
- UI copy: concise, specific, no marketing register. This is an academic site.
- Semantic HTML. Headings must nest properly; never put a heading inside a button (v1's project cards did — that's invalid, and it's why cards are `<article>` with a stretched `<a>` now).
- Run `python scripts/build.py` before handing back, and say what you verified.
- Reuse existing components and utilities before introducing new ones.

## Reviews

- Review feature branch diffs, not main.
- Group findings by severity: critical, important, nitpick.

## Safety

- Ask before destructive git operations.
- Do not commit unless explicitly requested.
- The repo is not under git yet — see `PLAN.md` §7.
