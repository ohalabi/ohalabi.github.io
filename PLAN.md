# osamahalabi.com — Build Plan

Osama Halabi's professional site: integrated personal/professor site + XReality Lab (VR/AR/haptics research group). Hand-designed HTML/CSS with a small content-build pipeline for data-driven sections (see §1a), deployed via GitHub Pages to osamahalabi.com. Same repo as the current "coming soon" placeholder — this plan replaces it. (The XReality Lab name/brand stays as the research-group identity within the site even though the personal domain is osamahalabi.com, not xreality.world.)

> **Superseded by a rebuild.** §1–5 below document the original navy/gold design (build phases A–E) and are kept as a decision log — that site's generated pages now live in `v1-archive/` for reference/rollback, not at the repo root. It was rebuilt with a light "paper & ink" editorial direction in a side-by-side `v2/` directory, verified, and **promoted to the repo root as the live site**. Full rebuild rationale, the new site map, and a behavior contract live in `HANDOVER.md` — read that first for anything about the *current* site's design or architecture. §6 (QA), §7 (deploy), §8 (maintenance), and §9 (tools) below still apply and have been updated to match the promoted site; "Immediate next step" at the bottom reflects the current state.

## 1. Non-negotiables (decided)

- One integrated site: you (Associate Prof. Osama Halabi) as the lead frame, XReality Lab as your research group within it — not two separate sites.
- Domain: **osamahalabi.com** (not xreality.world).
- Tech: hand-designed HTML/CSS for page chrome and layout (no framework, no CDN deps, CSS variables for theme, matching the current repo's visual architecture) + a minimal Python content-build script for data-driven lists — see §1a.
- Keep the navy/gold palette as the starting point; refine, don't replace, unless design exploration (Phase 3) says otherwise.
- Must NOT look AI-generated: no generic hero-gradient-with-blob template, no default Inter/Poppins-and-glassmorphism look, no stock photography, no cookie-cutter rounded-card grids. Real photos, real project imagery, an opinionated layout, and your own UI/UX judgment should drive the final look — treat this as a design collaboration, not a template fill-in.

## 1a. Maintainability architecture (updated — content updates need to be easy)

Pure hand-edited static HTML doesn't scale well once you're regularly adding publications/awards/courses, and gives ORCID/Scholar data nowhere to land. Revised approach — **implemented as of this session**:

- **Page chrome stays hand-crafted HTML/CSS** (nav, footer, layout, `assets/css/style.css`) — this is what keeps the site from looking templated, and it rarely changes.
- **Repeatable content lives in `Data/*.json`** (matches the folder you already created for the CV — Windows treats `Data`/`data` as the same folder, and since GitHub Pages is case-sensitive Linux, everything consistently uses `Data/` capitalized): `profile.json`, `publications_orcid.json`, `awards.json`, `grants.json`, `service.json`, `teaching.json`, `projects.json`, `members.json`. Edit these directly — plain JSON, no markup to fight with.
- **`scripts/build.py`** (stdlib only) reads `Data/*.json` and generates all 11 static HTML pages (7 at the repo root, 4 under `lab/`). Run it after any data edit: `python scripts/build.py`.
- **`scripts/sync_orcid.py`** pulls your works from the ORCID public API into `Data/publications_orcid.json`. Run manually whenever you want to refresh: `python scripts/sync_orcid.py` then `python scripts/build.py`. ORCID coverage turned out excellent — 145 of your 148 CV-listed works are already there.
- **Google Scholar — caveat still applies**: no official API, scraping breaks/violates ToS. Not automated. ORCID is the source of truth; Scholar/ResearchGate stay as profile links only.

## 2. Information architecture (site map) — two-level nav

Top level (main nav): Home, About, **XReality Lab**, Publications, Teaching, Awards, Service, Contact.

`XReality Lab` (`lab/index.html`) is a section landing page with its own second-level sub-nav (a sticky bar under the main nav) linking to four pages living in `lab/`:

- **`lab/index.html` (Overview)** — lab description, quick-link cards into the three sections below, project/grant counts
- **`lab/research.html`** — research interests + full project list, grouped by theme (Core Research, Laser Graphics & Visual Art, Foundational Projects) — merged from a separate Projects page since they overlapped
- **`lab/grants.html`** — full funded-research/grants list
- **`lab/members.html`** — direct-supervision roster (34 entries: PhD/M.Sc./B.Sc. plus a small "Internship Supervision" group), grouped and sorted newest/ongoing-first; base list recovered from `Data/Osama Halabi - Supervision.html`'s embedded Google Sheet, cross-referenced and extended from a QU Digital Measures Vita export (`Data/members.json`). Committee-member roles (not direct supervision) were intentionally excluded.

Remaining top-level pages, unchanged in structure:
- **Home** — hero (name, title, one-line positioning), highlights strip
- **About / Bio** — career narrative, education, current position, CV download (PDF)
- **Publications** — publication list only, synced from ORCID
- **Teaching** — courses taught, materials, etc; split into Lecture Courses and Project/Thesis/Practical-Training Supervision (the latter recurs almost every term and would otherwise drown out the actual taught courses)
- **Awards** — recognitions/honors
- **Service** — boards/editorial roles, conference committees, reviewer service, invited talks/exhibitions, public/university service, from `Data/service.json`
- **Contact** — email, LinkedIn, office/lab location, maybe a simple mailto CTA rather than a form (no backend)

`scripts/build.py` handles the relative-path rewriting between root pages and `lab/*` pages automatically (see the `rel()` helper) — editing data files and re-running the script is all that's needed to keep both levels in sync.

## 3. Content I need from you before drafting

Your old sites (QU faculty page, Google Sites) were built in integrated editors with no HTML export option — that's fine, no need to fight with them. Just cut-and-paste the text content whenever convenient (page by page, section by section, no need to gather it all at once), and send photos/CV/files as they're ready.

- [x] CV — you added `Data/cv_Osama_Halabi.pdf`. Pulled into `Data/profile.json`, `awards.json`, `grants.json`, `service.json`, `teaching.json` (excluded DOB/marital status/nationality/home email/home phone as not appropriate for a public professional site — flag if you actually want any of those shown).
- [x] ORCID iD — `0000-0002-2052-0500`, synced (145 publications).
- [x] GitHub account — `github.com/ohalabi` (repo not yet created/pushed — that's §7, still pending).
- [x] Project photos/diagrams — recovered from `Data/Osama Halabi - Research.html` (a saved copy of the old Google Sites research page) via `scripts/harvest_research_page.py`; 54 real images now live in `assets/img/projects/` and appear on the Research page, correctly matched per-project (the DOM order needed a non-obvious fix — see script comments).
- [x] Professional headshot — `scripts/build_headshot.py` composited the studio photo (`Data/Doc. Osama_2.png`) onto a generated navy/gold/cyan background; square variant is live on the About page header. Wide variant generated but not yet used anywhere (Home hero still uses the logo/particle treatment from the original coming-soon page — a real Phase D pass could put it there).
- [x] Google Scholar (`scholar.google.com/citations?user=jYUTRTcAAAAJ`) and ResearchGate (`researchgate.net/profile/Osama-Halabi`) — confirmed correct: Scholar shows Osama Halabi, Qatar University (verified `qu.edu.qa` email), matching research interests, 1,924 citations; ResearchGate confirms the same name/title/department via search index (direct fetch 403'd on bot protection, but the match is unambiguous).
- [ ] Courses taught: descriptions/materials beyond the table already pulled from the CV (`Data/teaching.json` has course codes/names/levels/semesters; no syllabi or descriptions yet)
- [x] Lab members — recovered from `Data/Osama Halabi - Supervision.html`, then cross-referenced against a QU Digital Measures Vita export and corrected per your feedback (Hala/Somaya moved to M.Sc. as completed theses, Committee-Member roles removed as not direct supervision). 34 entries across PhD/M.Sc./B.Sc./Internship Supervision. Photos not included, add later if wanted.
- [x] Lab projects — 27 projects with real photos/diagrams (54 images), recovered from `Data/Osama Halabi - Research.html` via `scripts/harvest_research_page.py`, on `lab/research.html`. Grants have their own full list on `lab/grants.html` (no longer just a projects proxy).
- [ ] Preferred public contact details (currently using `ohalabi@qu.edu.qa` only — confirm that's right, and whether you want an office/lab location listed)
- [ ] Confirm domain registrar for osamahalabi.com (needed only at deploy time, for DNS)

## 4. Design direction process (this is where your design/UX skills lead)

1. Quick style conversation: typography pairing, layout tone (minimal/editorial vs. dense/technical), how "playful" the VR/AR side of the lab should feel vs. how formal the professor side should feel.
2. I can use the `ui-ux-pro-max` skill to propose 2-3 concrete style directions (palette refinements, font pairings) grounded in your navy/gold starting point — you pick or steer.
3. Build a static style-tile / component sandbox first (buttons, nav, section headers, publication list item, lab card) before wiring up full pages — cheaper to iterate on than full pages.
4. Use the `impeccable` skill for a UX/hierarchy/accessibility pass once pages take shape.

## 5. Build phases (with example Claude Code prompts)

**Phase A — Skeleton & design system — DONE**
- `assets/css/style.css`: navy/gold tokens extended with spacing scale, type scale, nav + sub-nav components, cards, entry lists, data tables, project-card/gallery grid.
- `scripts/build.py`: generates all 11 pages from `Data/*.json` — `index.html`, `about.html`, `publications.html`, `teaching.html`, `awards.html`, `service.html`, `contact.html` at root, plus `lab/index.html`, `lab/research.html`, `lab/grants.html`, `lab/members.html` in the `lab/` subdirectory (two-level nav, see §2). The `rel()` helper rewrites asset/nav paths depending on directory depth.
- Logo bug fixed: pages originally referenced a root-level logo file that didn't exist (all PNGs live under `Logo/`) and separately, the transparent "clean" logo variant was unreadable against the navy background (verified by compositing both variants onto `--navy-900`) — now uses `Logo/xreality-logo-card-512.png` (white badge) at the correct path everywhere.
- **Intentionally plain visual design** — this phase was structure + data plumbing, not the design pass. §4 (design direction) still hasn't happened; recommend doing that next, before this starts to feel "finished."

**Phase B — Home page — DONE (functional, not designed)**
- Hero keeps the particle canvas + logo, shows real name/positioning/stats instead of "Coming Soon." Still uses the original coming-soon layout verbatim — a real Phase B design pass (per §4) would rethink this rather than just swap text.

**Phase C — Content pages — DONE for all data-backed sections**
- Publications: 145 ORCID-synced entries grouped by year (`publications.html`). Done.
- Teaching: course table from CV (`teaching.html`). Extended with the full registrar assignment-history export through Fall 2026 (`Data/assignment_history.csv`, raw reference copy) and split into **Lecture Courses** vs **Project, Thesis & Practical Training Supervision** per university, since the supervision load recurs almost every term and was drowning out the actual taught courses in one flat table. Course materials/syllabi links still pending.
- Awards: 42 entries from CV (`awards.html`). Done.
- About: bio, education, positions, memberships, languages, CV download, headshot, link to the new Service page. Done.
- XReality Lab (`lab/`): Overview with quick-link cards + live counts; Research page with interests + full project list (27 projects, real photos, grouped by theme); Grants page (30 full funded-research entries); Members page (34 direct-supervision entries across PhD/M.Sc./B.Sc./Internship Supervision, newest-first). All done with real data.
- Service (`service.html`) — **DONE**: `Data/service.json` (boards/editorial roles, 37 conference committees, reviewer service, invited talks, invited exhibitions, public service, university service) now gets its own page, added to top-level nav. Resolves the "worth deciding" note from the previous version of this plan.
- Contact: email + social links only — still needs your confirmation on what's public (see §3).

**Phase C.5 — ORCID sync — DONE**
- `scripts/sync_orcid.py` pulls from the ORCID public API, writes `Data/publications_orcid.json`. Books, the patent, and edited volumes from the CV all turned out to already be in ORCID — no manual supplement file needed.

**Phase C.6 — Content harvesting from old sites — DONE**
- `scripts/harvest_research_page.py` parses a locally saved copy of the old Google Sites research page (`Data/Osama Halabi - Research.html`) into `Data/projects.json` — 27 projects with real bullet-point/paragraph descriptions and 54 correctly-matched images now in `assets/img/projects/`. The DOM's image-to-heading order needed a non-obvious fix (images preceded their own heading, not followed it) — caught by visually checking a few images against their assigned project, not just trusting the parse.
- `Data/members.json` similarly recovered from `Data/Osama Halabi - Supervision.html`'s embedded Google Sheet, then cross-referenced against a QU Digital Measures Vita export for updates/new entries, with your corrections applied (completed theses moved to M.Sc., committee-member roles removed as not direct supervision).

**Phase D — Design direction — APPLIED**
- Piloted in a standalone `design-preview.html` sandbox first (per §4), then applied to the real site once approved.
- Typography: swapped from the system font stack to **Unbounded** (self-hosted, reserved for short/large moments only — hero name, page `<h1>`s, section eyebrow labels) + **IBM Plex Sans** (self-hosted, everything else — body text and all longer headings, so long publication/project titles stay legible). First pass used Space Grotesk + Inter but both are flagged as the current "default AI pick" fonts by the project's design-quality checker, so swapped before applying.
- Color: added a **cyan accent** (`--cyan` / `--cyan-bright`) alongside gold, with a rule of thumb — gold stays reserved for identity (bio, CV, awards, primary CTAs), cyan marks lab/research/tech moments (XReality Lab sub-nav active state, lab overview quick-link cards, project-card hover).
- Toned down the button hover glow from a diffuse 24px halo to a tighter elevation-style shadow — the diffuse-halo version was flagged as a generated-UI tell, even though it originated in the pre-existing coming-soon page rather than this pass.
- Fonts self-hosted in `assets/fonts/` (5 woff2 files) rather than linked from Google Fonts CDN, to keep the site's no-CDN-dependency architecture.
- **Not done yet**: the decorative grid/blueprint background idea from the preview was cut (flagged as a generated-UI signature not tied to real content) and never made it into the real site — fine, wasn't essential to begin with.

**Phase E — Polish pass — DONE** (2026-08-15, run against the promoted v2 site rather than the v1 build this section originally described — see the superseded-note at the top of this file)
- Ran `/impeccable audit`: scored 15/20 (Good) — Accessibility 3/4, Performance 2/4, Responsive 3/4, Theming 4/4, Implementation Integrity 3/4.
- Fixed every finding: WebP-converted `assets/img/projects/` (54 MB → 5.5 MB, 89.8% smaller — this also closes the WebP item under §5 Phase C.6/HANDOVER §6); rewrote the home page mission-band's generic "groundbreaking... cutting-edge... innovate solutions for tomorrow" copy to something specific; fixed a stale "Twenty-seven projects" meta description (project count is dynamic now); fixed heading-hierarchy skips (site footer `h4`→`h3`, Publications' year headings `h3`→`h2`, since that page had no `h2` at all); fixed sub-3:1 border contrast on buttons/filter chips/search inputs against the paper background (new `--rule-3` token, WCAG 1.4.11); bumped mobile touch targets on chips/nav-toggle toward 44px; fixed the mission-band logo link's accessible name (was announcing "XReality Lab", now "XReality Lab — go to Research").
- Responsive check done via `/run-site` screenshots plus ad hoc Playwright checks at 390px/1400px across Research, About, Contact, Publications.
- Re-ran the detector after fixes: zero findings, down from one.

**Phase F — Post-launch refinement pass — DONE (2026-08-16)**, against a pasted external audit ("osamahalabi.com — refinement audit," Tier 1/2/3):
- Tier 1 (defects): mobile horizontal-scroll fix (`.railed > *{min-width:0}` — CSS grid's `min-width:auto` trap with wide children); mobile tap-target padding on search input/jump-nav links/footer links; favicon resized into a proper `favicon-32.png` + `apple-touch-icon.png` pair instead of one bare 512px link; responsive `srcset`/`sizes` + explicit `width`/`height` attributes added to every `<img>` site-wide via a new stdlib PNG/JPEG/WebP header parser (`image_size()`/`img_attrs()` in `build.py`) for CLS; headshot background already handled by Phase E/history item 1.
  - Fixing CLS this way regressed the hero layout twice (the HTML `height` attribute silently overrode `.hero-portrait`'s CSS `aspect-ratio`, stretching the portrait to 1200px tall) — resolved by switching `.hero` to `align-items:stretch` and the portrait to `width:100%;height:100%;object-fit:cover` so it always exactly matches the text column's height, no fixed aspect-ratio needed.
- Tier 2 (layout/hierarchy): mission statement promoted to a single prominent paragraph (dropped the redundant `<h2>` above it); Home's 4-up project card blurbs shortened independently of Research's 3-up cards (`.project-grid.featured .pcard p{-webkit-line-clamp:2}`); Publications got a sticky year rail (`.pub-year-rail`) with `IntersectionObserver`-driven scroll-spy, kept in sync with the existing type/search filter via a `MutationObserver` watching for `[hidden]` changes rather than coupling to that filter's code; universal `:target,[id]{scroll-margin-top:96px}` fallback added alongside the page's existing more specific values.
- Tier 3 (structured data & citations): JSON-LD (§6, above); per-publication citation export — `<details class="cite">` on every entry with APA and BibTeX panels, one-click copy buttons (`navigator.clipboard`, feature-detected), and a site-wide `publications.bib` download link. Citations only credited "Halabi, O." at first (ORCID's feed carries no co-author data) — see Phase G.

**Phase G — Publication data integrity — DONE (2026-08-16/17)**
- Compared the CV (`Data/cv_Osama_Halabi.pdf`) against the live publication list; flagged (not silently fixed) type mismatches for the user to arbitrate, since some (Springer LNCS conference-vs-book-chapter) are genuinely ambiguous.
- Built `scripts/enrich_from_mendeley.py`: merges full author lists and corrected work types from a personal Mendeley `.bib` export into `Data/publications_orcid.json` (DOI-first, normalized-title-second matching; ambiguous/unmatched records reported, not guessed). Handles a Mendeley "merge duplicates" corruption artifact (hardcoded `AUTHOR_OVERRIDES` for one paper, cross-checked against the CV's own `[C54]`) and ~27 pre-2010 records with comma-joined (not `" and "`-joined) multi-author strings. Designed to be re-run after every future `sync_orcid.py` refresh, since that script fully overwrites the JSON rather than merging — validated across three re-sync cycles in practice.
- Filtered a garbage placeholder ORCID record (`KNOWN_GARBAGE_TITLES` in `sync_orcid.py`) and removed 3 duplicate entries (two from a non-breaking-space title variant and an exact 2008 duplicate, one from the user's own ORCID edit creating a second copy of the patent record).
- The one patent record now correctly typed `"patent"` throughout the pipeline (was defaulting to `"other"` on every ORCID sync, and separately would have reverted on every Mendeley re-enrichment without an explicit `TYPE_OVERRIDES` entry, since Mendeley's own BibTeX export has no native patent type either).
- **Final state: 153 publications**, 0 duplicate groups, 0 garbage entries, 138/153 with full author lists (the other 15 are ORCID-only records without a Mendeley match — mostly older Japanese-language entries).

**Phase H — Scraping/reuse deterrents — DONE (2026-08-17)**
- `robots.txt` (generated by `build_meta()` in `build.py`, not hand-edited) now `Disallow`s 13 named AI-training/scraping crawlers (GPTBot, ChatGPT-User, Google-Extended, CCBot, anthropic-ai, ClaudeBot, Claude-Web, Bytespider, PerplexityBot, Applebot-Extended, Meta-ExternalAgent, Diffbot, Omgilibot) while leaving `User-agent: *` `Allow: /` for normal search indexing. Voluntary by nature — only affects crawlers that honor it.
- `site.js` blocks the right-click context menu on `<img>` elements only (not the whole page) — a deterrent against casual "Save Image As," not real protection (dev tools/view-source bypass it trivially).
- New `scripts/watermark_images.py`: stamps a faint bottom-right `osamahalabi.com` mark (size/margin scaled to each image, ~3.2% of the shorter side) onto all 120 `assets/img/projects/*.webp` files and the 5 headshot files. Not idempotent — re-running double-stamps — and not part of the `build.py` pipeline; run by hand when new project images or a new headshot are added. Files are git-tracked, so any single result is recoverable via `git checkout -- <path>`.
- Considered and ruled out: Fawkes (facial-recognition cloaking) — the `fawkes` PyPI package pins `tensorflow==2.4.1`, which has no wheel for the Python 3.14 on this machine and would need a separate legacy Python environment; also flagged as reduced-effectiveness against post-2021 facial recognition systems in independent research. The standalone SAND Lab desktop binary remains an option if the user wants to run it themselves outside this pipeline.

**Phase I — Headshot background — DONE (2026-08-17)**
- Per Qatar University's own headshot photography standard, `scripts/build_headshot.py`'s flat `--paper-sunk` fill was replaced with a light-center/dark-edge gray radial gradient (`gray_gradient()`, numpy-generated), scoped to the composited photo asset only — not a site-wide CSS treatment, so it doesn't reintroduce the radial-gradient decoration `CLAUDE.md`'s hard rules ban (that rule is about the page's own visual language, the old v1 hero — see `HANDOVER.md` §1). All 5 headshot output files regenerated and rewatermarked (Phase H's script must be re-run after any `build_headshot.py` regeneration).

**Phase J — Visitor analytics — DONE (2026-08-19)**
- Added [GoatCounter](https://www.goatcounter.com/) (free, cookieless, no personal-data collection) — the user's own tracking snippet rendered in `foot()` via a new `GOATCOUNTER_SITE` constant near the top of `build.py`, on every page.
- The footer colophon previously claimed "No framework, no CDN, no tracking" — no longer accurate once this went in, so it was reworded to name GoatCounter explicitly and note the no-cookies/no-personal-data property, rather than leave a false claim live on the site.
- Resolves the "optional lightweight analytics" item that had been sitting open in §8 since launch.

**Phase K — SEO verification pass — DONE (2026-09-13)**
- Real-world SEO strategy discussion: since this is a name-based academic site rather than a competitive keyword, ranking is mostly about (1) Google/Bing actually indexing it via Search Console/Webmaster Tools submission — still needs the user's own account, not automatable from here, (2) backlinks from authoritative sources (ORCID/Scholar/ResearchGate/QU faculty page), (3) technical health (speed, no dead links, structured data — all already done or checked below), (4) freshness.
- **Core Web Vitals, measured for real** (closes the long-open "Lighthouse/PageSpeed unverified" item): no Lighthouse/npm install added — `scripts/check_web_vitals.py` (new) drives the system Edge via Playwright and reads the browser's own `PerformanceObserver`/Paint Timing/Navigation Timing APIs directly (the same primitives Lighthouse's scores are computed from) against the **live** site. Result, against `index.html`/`research.html`/`publications.html`: **LCP, CLS, FCP, and TTFB all rate "good"** on Google's published thresholds — CLS is a flat 0.000 on every page (direct payoff of Phase F's `width`/`height` image-attribute fix), `research.html` loads only ~19 requests despite ~50 project cards (native lazy-loading working correctly), and page weight is a few hundred KB thanks to the earlier WebP conversion.
- **Dead-link check** (closes the "verify external links" item): `scripts/check_dead_links.py` (new) confirmed the site has exactly two sources of outbound links — the 89 publication DOI/URLs in `Data/publications_orcid.json` and the 5 `profile.json` social links (`grants.json`/`awards.json`/`teaching.json`/`projects.json`/`members.json`/`service.json` carry no link fields at all, checked directly). Of 94 checked, 77 resolved cleanly and 17 were flagged (`403`/`999`/`503` from Tandfonline, MDPI, ACM, Inderscience, LinkedIn, ResearchGate) — cross-verified all 15 flagged DOIs against Crossref's bot-tolerant API and every one is genuinely valid and title-matched. **Actual result: 0 broken links.** The flags are entirely publisher/platform anti-bot layers blocking a scripted request's TLS fingerprint, not real link rot — a real visitor's browser passes through fine.
- **Freshness**: re-ran `sync_orcid.py` → `enrich_from_mendeley.py` → `build.py` end-to-end as a live rehearsal of the §8 maintenance workflow. ORCID had nothing new (still 153), and the full round-trip left `Data/publications_orcid.json` byte-identical to before — confirms the sync+enrich pairing is safely idempotent when nothing changed upstream, not just when it does.

## 6. QA checklist before launch

- [ ] Cross-browser check (Chrome, Firefox, Safari if available) — still only automated-verified in Edge, via the `/run-site` skill; nothing in this session's Phase E work touched this
- [x] Mobile responsiveness at real breakpoints — verified via `/run-site` screenshots (390px) plus ad hoc Playwright checks throughout Phase E; touch targets on chips/nav-toggle bumped toward 44px
- [x] `prefers-reduced-motion` respected — `HANDOVER.md` §4 behavior contract
- [x] Accessibility — Phase E's `/impeccable audit` pass: WCAG contrast computed and fixed for interactive borders (new `--rule-3` token), alt text audited (correct throughout — decorative images empty-alt, content images descriptive), keyboard nav confirmed (`:focus-visible` outline sitewide, skip link, proper `aria-expanded`/`aria-controls` on mobile nav), heading hierarchy fixed (no more skipped levels on any page)
- [x] Performance — `assets/img/projects/` converted to WebP (54 MB → 5.5 MB, 89.8% smaller), old PNG/JPG/GIF originals deleted after verifying every reference resolved. **Verified (Phase K, 2026-09-13)**: `scripts/check_web_vitals.py` measured real Core Web Vitals against the live site — LCP/CLS/FCP/TTFB all rate "good" on Home, Research, and Publications.
- [x] All external links (Scholar, ORCID, LinkedIn, DOIs) verified — **Phase K, 2026-09-13**: `scripts/check_dead_links.py` checked all 94 outbound links the site actually contains (89 publication DOIs + 5 profile links; grants/awards/teaching/projects/members/service carry no link fields). 0 genuinely broken — the 17 flagged were publisher/platform bot-protection (Crossref-confirmed valid), not dead links.
- [x] 404 page — `404.html`, generated
- [x] `sitemap.xml` + `robots.txt` for search indexing — generated
- [x] Basic SEO: meta description per page and Open Graph tags generated per-page in `build.py`; favicon fixed (`assets/img/favicon.png`, sourced from `Logo/xreality-logo-clean-512.png`, transparent) — the "still missing" note this bullet used to carry was stale, see `HANDOVER.md` §6
- [x] `schema.org` JSON-LD `Person`/`ScholarlyArticle`/`Book`/`Chapter`/`Dataset`/`Patent` structured data — done (Phase F, 2026-08-16); `person_jsonld()` on Home/About, `publications_jsonld()` (a `@graph`) on Publications, DOIs as `PropertyValue` identifiers, full author arrays where known

## 7. Deployment & domain — LIVE as of 2026-08-16

**osamahalabi.com is live**, served by GitHub Pages with a valid Let's Encrypt certificate (`CN=osamahalabi.com`, issued via Let's Encrypt, expires 2026-11-13 — GitHub auto-renews before then). `http://` and `www.` both redirect to the canonical `https://osamahalabi.com`.

- [x] `v1-archive/`'s fate decided — deleted (2026-08-15, 15 MB).
- [x] `git init` this repo, first commit (2026-08-15) — 475 files, `.gitignore` excludes machine-local state, raw content-harvest sources (~55MB, not needed to build/serve), and (for now) the CV PDF, see below.
- [x] GitHub repo created (public): `github.com/ohalabi/ohalabi.github.io` — named for GitHub's user-site convention, serves from `main` branch root automatically.
- [x] GitHub Pages enabled, deploying from `main` / root.
- [x] Custom domain `osamahalabi.com` added in Pages settings + `CNAME` file committed to the repo.
- [x] GoDaddy DNS pointed: 4 `A` records (`@` → `185.199.108.153`/`.109`/`.110`/`.111`, GitHub Pages' fixed IPs) + `CNAME` (`www` → `ohalabi.github.io`).
- [x] Account-level domain verification (`github.com/settings/pages` → Verified domains → TXT record) — this was the actual blocker holding up the certificate; not something the original checklist anticipated, worth remembering if the domain or account ever changes.
- [x] HTTPS enforced — confirmed via `curl`: correct cert, HTTP→HTTPS redirect working, page loads with the right title.
- [x] **CV PDF decision made (2026-08-16): not distributed at all, by choice.** Rather than waiting on a cleaned re-export, both download buttons were removed — Home hero's "Curriculum vitae (PDF)" is now "Request CV" (links to Contact), About's "Full CV (PDF)" is now "Request full CV" (same). `copy_shared_assets()` no longer copies the PDF into the build at all (was previously copied in on first build, now the copy block is deleted outright with a comment explaining why). `Data/cv_Osama_Halabi.pdf` stays `.gitignore`'d and was never committed (`git log --all -- Data/cv_Osama_Halabi.pdf` returns nothing) — confirmed the personal Gmail address in it has never been on the live site. `scripts/check_cv_privacy.py` still exists for whenever a cleaned export is ready and a real download link is wanted again, but that's no longer blocking anything.
- [x] Repo actually pushed and live-iterated on — well past the original "not yet created/pushed" state: `git init` (2026-08-15), multiple commits since (polish pass, publication data cleanup, scraping deterrents, headshot background), each verified locally via `/run-site` before pushing.
- [x] **Private-repo attempt (2026-08-17), reverted.** Confirmed via GitHub's Billing/education-benefits pages that the account has Pro access; switched the repo to private, but GitHub Pages' publishing-source setting (Settings → Pages → Build and deployment → Source/Branch) got reset to unconfigured in the process, taking the live site down. Switched back to public and walked through re-enabling Pages (source: Deploy from a branch → `main` → `/root`) — the `CNAME` file itself was untouched throughout (still committed, `osamahalabi.com`), only the repo-settings toggle was affected. **Worth knowing if private is tried again**: expect to manually reconfigure both the publishing source and re-verify the custom domain afterward; it isn't carried across automatically.
- [x] GitHub Action for publications (2026-09-25): `.github/workflows/sync-publications.yml` runs `sync_orcid.py` every Monday 03:00 UTC (or on demand from the Actions tab); only when `Data/publications_orcid.json` actually changed does it run `build.py` and commit, since `build.py` date-stamps every page and would otherwise commit weekly. `sync_orcid.py` now merges instead of overwriting: it keeps the Mendeley-curated `authors`/`type` fields on existing records and fills `authors` for new DOIs from Crossref. New records with no DOI still need `enrich_from_mendeley.py` by hand. Pull before pushing local work, since the bot commits to `main`.

## 8. Post-launch / maintenance

- [ ] Routine content updates: edit the relevant `data/*.json` file, run `build.py`, commit, push — no HTML editing needed for publications/awards/teaching/lab entries
- [ ] Publications: run `sync_orcid.py` whenever you want to refresh from ORCID (or automate on a schedule once comfortable with it), then **immediately** re-run `scripts/enrich_from_mendeley.py "<path to Mendeley .bib export>"` — `sync_orcid.py` fully overwrites `Data/publications_orcid.json` rather than merging, so author lists and the patent's corrected type get wiped on every sync unless re-applied (Phase G)
- [ ] Google Scholar-only papers: manually paste BibTeX exports into `data/publications.json` as needed (no reliable automated path — see §1a)
- [x] Lightweight analytics — GoatCounter added (Phase J, 2026-08-19); privacy-friendly, no Google Analytics dependency
- [ ] Periodic performance re-check after content additions — `python scripts/check_web_vitals.py` (Phase K); no Lighthouse/npm install needed
- [ ] Periodic dead-link re-check after adding new publications — `python scripts/check_dead_links.py` (Phase K)

## 9. Tools / skills / suggestions

**Claude Code skills already available, worth using during the build:**
- `ui-ux-pro-max` — style/palette/typography exploration grounded in your existing theme
- `impeccable` — UX/hierarchy/accessibility/polish review passes
- `dataviz` — only if you want any citation/publication-stats chart
- `/run-site` (project skill, `.claude/skills/run-site/`) — builds the site, serves it over real HTTP, and drives it with Playwright: filters Research by theme, opens/closes the project detail drawer, searches Publications, screenshots each step. This is the actual verification loop now, not just eyeballing — see its `SKILL.md` for the full behavior it checks and known issues it already accounts for.
- `code-review` — sanity check before pushing to GitHub

**External tools worth having:**
- Python (already used in this repo, stdlib is enough for the build script; Pillow/numpy for image work) — the content-build pipeline in §1a
- `scripts/check_web_vitals.py` (Phase K) — real Core Web Vitals via Playwright/Edge against the live site, no Lighthouse/npm install
- `scripts/check_dead_links.py` (Phase K) — checks every outbound link the site contains; cross-verify any flagged DOI against `api.crossref.org` before assuming it's actually broken (publisher bot-protection false-positives easily)
- ORCID public API (`pub.orcid.org`) — automated publication sync, free, no key needed for public data
- Semantic Scholar API — optional second automated source, also gives citation counts
- GoatCounter (Phase J) — visitor analytics, already wired in
- Google Search Console / Bing Webmaster Tools — not automatable from here (needs the user's own account + domain verification), but the highest-impact remaining SEO step: submit `sitemap.xml`, see actual indexing status and search queries
- Cloudflare (optional) — if you want DNS/CDN/extra HTTPS options beyond GitHub Pages' built-in cert
- `gh` CLI (you already have Bash access to it) — repo creation/push from here directly when ready

## Next steps (pick up here)

**osamahalabi.com is live** (§7) and has had three full rounds of post-launch refinement since (Phases F–K: layout/CLS/mobile fixes, structured data, citation export, publication data-integrity cleanup, scraping deterrents, headshot background, analytics, SEO verification). What's left, roughly in priority order:

1. [ ] **Submit to Google Search Console + Bing Webmaster Tools** — the highest-impact remaining SEO step, and the one thing here that genuinely needs the user's own account (domain verification, sitemap submission). Not automatable from this side; talked through in Phase K but not yet done.
2. [ ] Cross-browser check — Chrome/Firefox/Safari; only Edge has been automated-verified so far, via `/run-site` (§6).
3. [ ] Decide: office/lab location on the Contact page — the original open question from §3, still unanswered.
4. [ ] The ~14 remaining CV-vs-site publication type mismatches flagged in Phase G (mostly Springer LNCS conference-vs-book-chapter judgment calls) — needs the user's call, not a mechanical fix.
5. [ ] The 15 publications still missing full author lists (ORCID-only, no Mendeley match — Phase G) — would need either a fresh Mendeley export covering them or manual entry.
6. [ ] Decide whether to ever re-add a real CV download — Phase H replaced both buttons with "Request CV" permanently; revisit only if a cleaned export (no personal email, stripped metadata) becomes available and the user wants a direct download again.
7. [ ] Optional: work through the rest of `HANDOVER.md` §6 — project descriptions read as objective statements rather than outcome summaries, projects have no year field (more valuable now at 50 projects spanning 2001–2027 than when this was first noted), no project↔publication linking.
8. [x] GitHub Action: weekly ORCID sync + rebuild + commit when publications change (§7).
9. [ ] Optional: retry the private-repo switch now that the Pages-reset gotcha (§7) is documented — reconfigure Settings → Pages source and custom domain immediately after flipping visibility, don't assume it carries over.
10. [ ] Ongoing habits — see §8: routine content edits are `Data/*.json` → `build.py` → commit → push (Pages auto-redeploys); `sync_orcid.py` + immediately re-run `scripts/enrich_from_mendeley.py` whenever publications need a refresh (ORCID sync fully overwrites, doesn't merge — confirmed idempotent when nothing's changed, Phase K); `scripts/watermark_images.py` after adding new project images or a new headshot; periodic `check_web_vitals.py`/`check_dead_links.py` re-checks after big content additions.

---

<details>
<summary>History: how the site got here (expand)</summary>

**The v2 rebuild is now the live site**, promoted from `v2/` to the repo root (the old navy/gold site was archived in `v1-archive/`, since deleted — §7). All 10 generated pages (`index.html`, `research.html`, `publications.html`, `teaching.html`, `people.html`, `about.html`, `contact.html`, `404.html`, `sitemap.xml`, `robots.txt`) build from the same `Data/*.json` as before — no content was re-entered. Verified end-to-end (build → serve → click through Research filters and the project drawer → search Publications) via the `/run-site` skill. See `HANDOVER.md` for the full rebuild rationale and §6 there for the known-gaps list this next-steps section is drawn from. Order this actually happened in:

1. [x] **Headshot fixed** — `scripts/build_headshot.py` rewritten to drop the old navy/gold/glow composite (which violated this site's own "no gradients, no glow" rule anyway) for a flat `--paper-sunk` fill, matching the rest of the site. `osama-headshot-square.jpg` (regenerated) is now what the home hero actually uses — the old script only ever produced `-wide.jpg` for that slot, an aspect-ratio mismatch against `.hero-portrait`'s 4:5 box.
2. [x] **Logo added to the masthead** — `xreality-logo-clean-512.png` (the real-alpha lockup, not the white-badge card variant v1 needed for navy contrast — the light paper background doesn't need that crutch) now sits next to the text wordmark on every page.
3. [x] **Favicon added** — `scripts/build_favicon.py` (new) crops an icon-only mark (no baked-in wordmark — illegible at the 16-32px a favicon actually renders at) into `assets/img/favicon.png`. Switched from transparent (`Logo/xreality-logo-clean-512.png`) to opaque-white (`Logo/xreality-logo-card-512.png`) after the transparent version proved faint against a dark browser tab bar, then back to transparent (2026-08-16) as the better general default — see `HANDOVER.md` §6 item 6 for the current reasoning.
4. [x] Google Scholar/ResearchGate URLs confirmed (§3). [x] Public contact **security** — `ohalabi@qu.edu.qa` on `contact.html` no longer sits in the page source as a scrapable plain address/`mailto:` link; it ships as split `data-user`/`data-domain` attributes and gets assembled client-side by `site.js` on load, with a `<noscript>` fallback. Also caught and flagged (not fixed — it's your file to re-export) a personal Gmail address sitting in plain text in `Data/cv_Osama_Halabi.pdf`; `scripts/check_cv_privacy.py` checks for that (and stray metadata) on every future CV update. **Still open**: whether to list an office/lab location (§3 original question, unrelated to the security work).
5. [x] **WebP conversion done**: `assets/img/projects/` converted from PNG/JPG/GIF to WebP, 54 MB → 5.5 MB (89.8% smaller); originals deleted after verifying every `Data/projects.json` reference resolved. [ ] Still open from `HANDOVER.md` §6: project descriptions are objective statements rather than outcome summaries, projects have no year field (so no chronological sort/active-state — more valuable now than when this was written, since the project count has grown from 27 to 50, spanning 2001–2027), and there's still no project↔publication linking.
6. [x] **Phase E polish pass done** — see §5 above: `/impeccable audit` (15/20, "Good") run and every finding fixed (image weight, generic copy, heading hierarchy, border contrast, touch targets, a link's accessible name); responsive-checked via `/run-site` and ad hoc Playwright screenshots at 390px/1400px.
7. [x] `v1-archive/` deleted (15 MB) — was the one loose end blocking git init, since GitHub Pages would otherwise have served it publicly at `osamahalabi.com/v1-archive/...`.
8. [x] **§7 deployment done — osamahalabi.com is live** (2026-08-16). See §7 for the full record, including the account-level domain-verification step that wasn't in the original checklist and turned out to be the actual blocker on HTTPS.

</details>
