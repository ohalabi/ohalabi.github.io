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

## 6. QA checklist before launch

- [ ] Cross-browser check (Chrome, Firefox, Safari if available) — still only automated-verified in Edge, via the `/run-site` skill; nothing in this session's Phase E work touched this
- [x] Mobile responsiveness at real breakpoints — verified via `/run-site` screenshots (390px) plus ad hoc Playwright checks throughout Phase E; touch targets on chips/nav-toggle bumped toward 44px
- [x] `prefers-reduced-motion` respected — `HANDOVER.md` §4 behavior contract
- [x] Accessibility — Phase E's `/impeccable audit` pass: WCAG contrast computed and fixed for interactive borders (new `--rule-3` token), alt text audited (correct throughout — decorative images empty-alt, content images descriptive), keyboard nav confirmed (`:focus-visible` outline sitewide, skip link, proper `aria-expanded`/`aria-controls` on mobile nav), heading hierarchy fixed (no more skipped levels on any page)
- [x] Performance — `assets/img/projects/` converted to WebP (54 MB → 5.5 MB, 89.8% smaller), old PNG/JPG/GIF originals deleted after verifying every reference resolved. **Still open**: an actual Lighthouse/PageSpeed run hasn't happened — the image fix should move the score a lot, but it's unverified
- [ ] All external links (Scholar, ORCID, LinkedIn, DOIs) verified — Scholar/ResearchGate profile URLs confirmed earlier (§3), but not every publication DOI or grant link
- [x] 404 page — `404.html`, generated
- [x] `sitemap.xml` + `robots.txt` for search indexing — generated
- [x] Basic SEO: meta description per page and Open Graph tags generated per-page in `build.py`; favicon fixed (`assets/img/favicon.png`, sourced from `Logo/xreality-logo-clean-512.png`, transparent) — the "still missing" note this bullet used to carry was stale, see `HANDOVER.md` §6
- [ ] Optional: `schema.org` JSON-LD `Person`/`ScholarlyArticle` structured data — helps academic search visibility, not done

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
- [ ] **CV PDF is a 404 on the live site right now** — `Data/cv_Osama_Halabi.pdf` was deliberately excluded from the repo (see `.gitignore`) because it still had a personal Gmail address in it as of the last check. Both the home hero's "Curriculum vitae (PDF)" button and About's "Full CV (PDF)" button point at it. Send an updated export (Gmail line removed, ideally metadata stripped too — `scripts/check_cv_privacy.py` verifies both) and I'll add it back and push.
- [ ] Optional later: GitHub Action to run `build.py` (and `sync_orcid.py`) automatically on push/schedule instead of running locally each time.

## 8. Post-launch / maintenance

- [ ] Routine content updates: edit the relevant `data/*.json` file, run `build.py`, commit, push — no HTML editing needed for publications/awards/teaching/lab entries
- [ ] Publications: run `sync_orcid.py` whenever you want to refresh from ORCID (or automate on a schedule once comfortable with it)
- [ ] Google Scholar-only papers: manually paste BibTeX exports into `data/publications.json` as needed (no reliable automated path — see §1a)
- [ ] Optional lightweight analytics (privacy-friendly, e.g. Plausible/GoatCounter) — skip Google Analytics if you want to keep the site dependency-free
- [ ] Periodic Lighthouse re-check after content additions

## 9. Tools / skills / suggestions

**Claude Code skills already available, worth using during the build:**
- `ui-ux-pro-max` — style/palette/typography exploration grounded in your existing theme
- `impeccable` — UX/hierarchy/accessibility/polish review passes
- `dataviz` — only if you want any citation/publication-stats chart
- `/run-site` (project skill, `.claude/skills/run-site/`) — builds the site, serves it over real HTTP, and drives it with Playwright: filters Research by theme, opens/closes the project detail drawer, searches Publications, screenshots each step. This is the actual verification loop now, not just eyeballing — see its `SKILL.md` for the full behavior it checks and known issues it already accounts for.
- `code-review` — sanity check before pushing to GitHub

**External tools worth having:**
- Python (already used in this repo, stdlib is enough for the build script; Pillow/numpy for image work) — the content-build pipeline in §1a
- Lighthouse (Chrome DevTools or CLI) — performance/accessibility audits pre-launch
- ORCID public API (`pub.orcid.org`) — automated publication sync, free, no key needed for public data
- Semantic Scholar API — optional second automated source, also gives citation counts
- Cloudflare (optional) — if you want DNS/CDN/extra HTTPS options beyond GitHub Pages' built-in cert
- `gh` CLI (you already have Bash access to it) — repo creation/push from here directly when ready

## Next steps (pick up here)

**osamahalabi.com is live** (§7) — the site itself is done and deployed. What's left is cleanup and polish, roughly in priority order:

1. [ ] **Fix the live CV 404** — send an updated `cv_Osama_Halabi.pdf` export with the personal Gmail line removed (ideally metadata stripped too). Run `python scripts/check_cv_privacy.py` against it; once it passes, add it back to the repo and push. This is the only thing actually broken on the live site right now (§7).
2. [ ] Cross-browser check — Chrome/Firefox/Safari; only Edge has been automated-verified so far, via `/run-site` (§6).
3. [ ] Run an actual Lighthouse/PageSpeed pass — the WebP conversion (54MB→5.5MB) should move this a lot, but it's unverified (§6).
4. [ ] Verify external links — every publication DOI and grant link, not just the Scholar/ORCID/ResearchGate profile URLs already confirmed (§6).
5. [ ] Decide: office/lab location on the Contact page — the original open question from §3, still unanswered.
6. [ ] Optional: `schema.org` JSON-LD structured data for academic search visibility (§6).
7. [ ] Optional: work through the rest of `HANDOVER.md` §6 — project descriptions read as objective statements rather than outcome summaries, projects have no year field (more valuable now at 50 projects spanning 2001–2027 than when this was first noted), no project↔publication linking.
8. [ ] Optional: GitHub Action to run `build.py` (and `sync_orcid.py`) automatically on push/schedule instead of running locally each time (§7).
9. [ ] Ongoing habits once any of the above lands — see §8: routine content edits are `Data/*.json` → `build.py` → commit → push (Pages auto-redeploys), `sync_orcid.py` whenever publications need a refresh, periodic Lighthouse re-checks after big content additions.

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
