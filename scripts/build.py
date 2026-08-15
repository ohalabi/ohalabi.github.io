#!/usr/bin/env python3
# =============================================================================
# build.py — static site generator for osamahalabi.com  (v2)
#
# Reads the SAME Data/*.json files as v1 — none of that content was touched,
# so nothing you curated in ORCID sync, CV extraction or the legacy-page
# harvest is lost. Only the presentation layer changed.
#
#   python scripts/build.py
#
# Path resolution walks upward to find Data/, so this works whether v2/ sits
# beside the old site or is promoted to the repo root. Nothing to edit when
# you move it.
#
# Rules of the road:
#   * Never hand-edit the generated .html files — they are overwritten.
#   * Content changes go in Data/*.json.
#   * Structural changes go in the build_* functions below.
#   * Visual changes go in assets/css/style.css, not in here.
# =============================================================================

import html
import json
import os
import re
import shutil
import sys
from datetime import date

# ----------------------------------------------------------------- paths ---
SCRIPTS  = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(SCRIPTS)


def find_upward(name, start, limit=4, marker=None):
    """Locate a directory by walking up from `start`.

    `marker`, if given, must exist inside the candidate directory too --
    without it, a `Data/` populated only by copy_shared_assets()'s own
    output (e.g. just the copied CV, on any build after the first) would
    satisfy `os.path.isdir` and shadow the real Data/ one level up.
    """
    cur = start
    for _ in range(limit):
        cand = os.path.join(cur, name)
        if os.path.isdir(cand) and (marker is None or os.path.isfile(os.path.join(cand, marker))):
            return cand
        cur = os.path.dirname(cur)
    return None


DATA_DIR = find_upward("Data", SITE_DIR, marker="profile.json")
if not DATA_DIR:
    sys.exit("build.py: could not find a Data/ directory with profile.json at or above %s" % SITE_DIR)
REPO_ROOT = os.path.dirname(DATA_DIR)

SITE_URL = "https://osamahalabi.com"
BUILT_ON = date.today().isoformat()
YEAR_NOW = date.today().year


def load(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as fh:
        return json.load(fh)


profile  = load("profile.json")
projects = load("projects.json")
grants   = load("grants.json")
awards   = load("awards.json")
members  = load("members.json")
teaching = load("teaching.json")
service  = load("service.json")
pubs     = load("publications_orcid.json")


# ------------------------------------------------------------- utilities ---
def e(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def prose(s):
    """escape + light typographic cleanup. The CV and Google Sites imports are
    full of ASCII double hyphens standing in for em dashes; they look like a
    typo once the text is set in a serif face."""
    s = str(s or "")
    s = re.sub(r"\s--\s", " — ", s)
    s = re.sub(r"(?<=[a-z])--(?=[a-z])", "—", s)
    return e(s)


def year_field(v):
    """Some service entries (conference_committees) store `years` as a JSON
    list of individual years rather than a '2020-present'-style string --
    e.g. 12 separate entries for one long-running committee. Rendered
    straight through e(), that list's Python repr ("['2009', '2010', ...]")
    wrapped character-by-character in the narrow key column and produced
    towering whitespace next to a one-line title. Collapse consecutive runs
    into ranges instead: ['2009','2010','2011','2013'] -> '2009-2011, 2013'."""
    if not isinstance(v, list):
        return v
    ys = sorted(int(y) for y in v)
    runs, start = [], ys[0]
    prev = ys[0]
    for y in ys[1:]:
        if y == prev + 1:
            prev = y
            continue
        runs.append((start, prev))
        start = prev = y
    runs.append((start, prev))
    return ", ".join(str(a) if a == b else f"{a}–{b}" for a, b in runs)


def slug(s):
    s = re.sub(r"[‐-―]", "-", str(s).lower())
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def money(s):
    """'$120,000' -> 120000. Returns 0 for anything that is not a plain USD
    figure.

    Two traps this closes, both of which produced a wrong headline number:
      * '$1,049,427.58' — stripping all non-digits turned the cents into two
        extra digits and reported that award as $104,942,758.
      * '¥5,000,000' — a Japanese award summed as if it were dollars. Rather
        than bake in a historical exchange rate, non-USD awards are excluded
        from USD totals and disclosed separately. See non_usd_grants()."""
    raw = str(s or "").strip()
    if not raw.startswith("$"):
        return 0
    num = re.sub(r"[^0-9.]", "", raw)
    if not num or num.count(".") > 1:
        return 0
    try:
        return int(round(float(num)))
    except ValueError:
        return 0


def non_usd_grants():
    return [g for g in grants if not str(g.get("amount") or "").strip().startswith("$")]


def usd(n):
    if n >= 1_000_000:
        return "$%.2fM" % (n / 1_000_000)
    if n >= 1_000:
        return "$%dK" % round(n / 1_000)
    return "$%d" % n


def end_year(period):
    yrs = re.findall(r"(19|20)\d{2}", str(period or ""))
    full = re.findall(r"(?:19|20)\d{2}", str(period or ""))
    if not full:
        return 0
    if re.search(r"present|ongoing|current", str(period), re.I):
        return 9999
    return int(full[-1])


# =============================================================================
# PROJECT THEMES
# -----------------------------------------------------------------------------
# projects.json carries three broad categories from the legacy site. Those are
# eras, not subjects, so they can't answer "show me the haptics work". These
# rules add a subject axis. Matched against the lowercased title, first hit
# wins, and the build FAILS if a project matches nothing — so a project added
# later can never silently land in an untagged bucket.
# =============================================================================
THEMES = {
    "haptics":  "Haptics & Touch",
    "vr":       "Virtual Reality",
    "ar":       "Augmented Reality",
    "health":   "Health & Accessibility",
    "mobility": "Driving & Mobility",
    "laser":    "Laser Graphics & Art",
    "sensing":  "Sensing & IoT",
}

THEME_RULES = [
    ("wearable telexistence",         "haptics"),
    ("recycling infrastructure",      "vr"),
    ("remote robot operation",        "haptics"),
    ("disaster preparedness",         "vr"),
    ("digital citizenship",           "vr"),
    ("obese",                         "health"),
    ("covid-19",                      "health"),
    ("avatar actions",                "vr"),
    ("health coaching",               "health"),
    ("telexistence robotic arm",      "haptics"),
    ("olfactory display",             "ar"),
    ("public speaking",               "vr"),
    ("gait monitoring",               "health"),
    ("creative scape",                "vr"),
    ("cultural heritage",             "vr"),
    ("remote education",              "vr"),
    ("gamification",                  "ar"),
    ("motion blending",               "haptics"),
    ("hand rehabilitation",           "health"),
    ("cybersecurity fundamentals",    "vr"),
    ("language learning",             "vr"),
    ("evacuation simulation",         "vr"),
    ("search and rescue",             "vr"),
    ("tactile footwear",              "haptics"),
    ("water monitoring",              "sensing"),
    ("firefighting",                  "vr"),
    ("virtual fixtures",              "health"),
    ("autism",                        "health"),
    ("redirected walking",            "vr"),
    ("response times",                "mobility"),
    ("driver activity",               "mobility"),
    ("tactile feedback in driving",   "mobility"),
    ("haptic seat",                   "mobility"),
    ("olfactory",                     "health"),
    ("pedestrian navigation",         "ar"),
    ("crowd simulation",              "vr"),
    ("blind people",                  "ar"),
    ("multidimensional visual aid",   "haptics"),
    ("laser",                         "laser"),
    ("haptic science encyclopedia",   "haptics"),
    ("hiro",                          "haptics"),
    ("vr-based training",             "vr"),
    ("network delay",                 "haptics"),
    ("cooperative virtual workspace", "haptics"),
]

CATEGORY_LABELS = {
    "core-research-projects":     "Core Research",
    "laser-graphics-visual-art":  "Laser & Art",
    "foundational-projects":      "Foundational",
}

# Shown large on the home page. Substring match against the title.
FEATURED = [
    "tactile footwear",
    "firefighting",
    "blind people",
    "driver activity",
]


def theme_for(title):
    low = title.lower()
    for needle, key in THEME_RULES:
        if needle in low:
            return key
    raise SystemExit(
        "build.py: no theme rule matches project %r.\n"
        "Add a (substring, theme) rule to THEME_RULES. Themes: %s"
        % (title, ", ".join(THEMES))
    )


def build_project_index():
    out = []
    for cat in projects["categories"]:
        cat_id = slug(cat["name"])
        for p in cat["projects"]:
            title = p["title"]
            th = theme_for(title)
            bullets = [b for b in (p.get("bullets") or []) if b.strip()]
            out.append({
                "id":        slug(title),
                "title":     title,
                "cat":       cat_id,
                "cat_label": CATEGORY_LABELS.get(cat_id, cat["name"]),
                "theme":     th,
                "theme_label": THEMES[th],
                "bullets":   bullets,
                "images":    p.get("images") or [],
                "url":       p.get("url"),
                "featured":  any(f in title.lower() for f in FEATURED),
            })
    return out


PROJECTS = build_project_index()


# =============================================================================
# PAGE CHROME
# =============================================================================
NAV = [
    ("Research",     "research.html"),
    ("Publications", "publications.html"),
    ("Teaching",     "teaching.html"),
    ("People",       "people.html"),
    ("About",        "about.html"),
    ("Contact",      "contact.html"),
]


def head(title, desc, page, extra_css="", scripts=()):
    js = "\n  ".join(
        '<script src="assets/js/%s" defer></script>' % s for s in ("site.js",) + tuple(scripts)
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}/{page}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE_URL}/{page}">
<meta property="og:image" content="{SITE_URL}/assets/img/headshot/osama-headshot-wide.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.png">
<link rel="stylesheet" href="assets/css/style.css">
{extra_css}<style>
/* Detail sections are only hidden once research.js confirms the drawer works.
   Without JS they stay visible and every project is fully readable. */
.js-drawer #project-details{{display:none}}
</style>
  {js}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
{masthead(page)}
<main id="main">
"""


def masthead(page):
    links = "".join(
        '<li><a href="%s"%s>%s</a></li>'
        % (href, ' aria-current="page"' if href == page else "", e(label))
        for label, href in NAV
    )
    return f"""<header class="masthead">
  <div class="masthead-inner">
    <a class="wordmark" href="index.html">
      <img class="wordmark-logo" src="Logo/xreality-logo-clean-512.png" alt="">
      <b>Osama Halabi</b><span>XReality Lab &middot; Qatar University</span>
    </a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="primary-nav">Menu</button>
    <ul class="nav" id="primary-nav">{links}</ul>
  </div>
</header>"""


def foot():
    s = profile["social"]
    return f"""</main>
<footer class="site-footer">
  <div class="footer-inner">
    <div>
      <h3>Osama Halabi</h3>
      <p style="color:var(--muted);font-size:var(--t-base)">
        Associate Professor, Department of Computer Science and Engineering,
        College of Engineering, Qatar University, Doha.
      </p>
      <p class="colophon">Built from a JSON dataset with a 400-line Python generator.
      No framework, no CDN, no tracking. Updated {BUILT_ON}.</p>
    </div>
    <div>
      <h3>Sections</h3>
      <ul>{"".join('<li><a href="%s">%s</a></li>' % (h, e(l)) for l, h in NAV)}</ul>
    </div>
    <div>
      <h3>Elsewhere</h3>
      <ul>
        <li><a href="{e(s['orcid'])}">ORCID</a></li>
        <li><a href="{e(s['google_scholar'])}">Google Scholar</a></li>
        <li><a href="{e(s['researchgate'])}">ResearchGate</a></li>
        <li><a href="{e(s['linkedin'])}">LinkedIn</a></li>
        <li><a href="{e(s['qu_faculty_page'])}">QU faculty page</a></li>
      </ul>
    </div>
  </div>
</footer>
</body>
</html>
"""


def write(page, body):
    path = os.path.join(SITE_DIR, page)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    print("  %-22s %6.1f KB" % (page, len(body.encode("utf-8")) / 1024))


# =============================================================================
# SHARED FRAGMENTS
# =============================================================================
def page_head(eyebrow, title, lede="", nav=""):
    return f"""<div class="wrap">
  <div class="page-head">
    <p class="eyebrow">{e(eyebrow)}</p>
    <h1 class="title">{e(title)}</h1>
    {'<p class="lede">%s</p>' % prose(lede) if lede else ""}
    {nav}
  </div>
</div>"""


def chip(kind, val, label, n=None, scope=None, pressed=False):
    return (
        '<button class="chip" data-kind="%s" data-val="%s"%s aria-pressed="%s">%s%s</button>'
        % (kind, val,
           ' data-scope="%s"' % scope if scope else "",
           "true" if pressed else "false",
           e(label),
           '<span class="n">%d</span>' % n if n is not None else "")
    )


def search_box(target=None, label="Search"):
    attr = ' data-search-for="%s"' % target if target else ' id="q"'
    return f"""<div class="search">
  <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
  <input type="search" placeholder="{e(label)}…" aria-label="{e(label)}"{attr}>
</div>"""


def grant_state(g):
    ey = end_year(g.get("period"))
    on = ey >= YEAR_NOW
    return '<span class="state%s">%s</span>' % (" on" if on else "", "Active" if on else "Completed")


# =============================================================================
# HOME
# =============================================================================
def build_home():
    active = [g for g in grants if end_year(g.get("period")) >= YEAR_NOW]
    active_total = sum(money(g.get("amount")) for g in active)
    total_all = sum(money(g.get("amount")) for g in grants)

    feat = [p for p in PROJECTS if p["featured"]][:4]
    recent = sorted(pubs, key=lambda p: p.get("year") or "", reverse=True)[:6]

    feat_html = "".join(f"""
      <article class="pcard" data-theme="{p['theme']}">
        <div class="pcard-media{'' if p['images'] else ' empty'}">
          {'<img src="%s" alt="" loading="lazy">' % e(p["images"][0]) if p["images"] else placeholder_svg()}
        </div>
        <div class="pcard-body">
          <span class="tag">{e(p['theme_label'])}</span>
          <h3><a href="research.html#{p['id']}">{e(p['title'])}</a></h3>
        </div>
      </article>""" for p in feat)

    pub_html = "".join(f"""
      <li class="entry">
        <div class="k">{e(p.get('year',''))}</div>
        <div class="t"><b>{e(p['title'])}</b>
          <span class="m">{e(p.get('journal') or '')}</span></div>
      </li>""" for p in recent)

    body = head(
        "Osama Halabi — Virtual Reality, Haptics & Human-Computer Interaction",
        "Osama Halabi is an Associate Professor at Qatar University working on virtual "
        "reality, haptics and multimodal interaction. XReality Lab.",
        "index.html",
    )

    body += f"""<div class="wrap">
  <section class="hero">
    <div>
      <h1>Systems you can feel.</h1>
      <p class="standfirst">{e(profile['positioning_line'])} Twenty-five years of building
      haptic interfaces, immersive training environments and multimodal systems —
      at JAIST, Gifu, Iwate, and now Doha.</p>
      <p class="affil">{e(profile['title'])}, {e(profile['department'])},<br>
      {e(profile['university'])}, {e(profile['location'])}</p>
      <div class="actions">
        <a class="btn btn-primary" href="research.html">Browse the research</a>
        <a class="btn" href="Data/cv_Osama_Halabi.pdf">Curriculum vitae (PDF)</a>
      </div>
    </div>
    <img class="hero-portrait" src="assets/img/headshot/osama-headshot-square.jpg"
         alt="Osama Halabi">
  </section>

  <section class="band mission-band">
    <a class="lab-mark-link" href="research.html" aria-label="XReality Lab — go to Research">
      <img class="lab-mark" src="Logo/xreality-logo-clean-512.png" alt="" aria-hidden="true">
    </a>
    <div class="mission-band-text">
      <h2 class="section-title">Haptics, VR, and human-centered interaction</h2>
      <p class="section-note">XReality Lab builds haptic interfaces, virtual and augmented
        reality systems, and multimodal training and accessibility tools — plus a laser
        graphics and visual-art practice dating back to 2001.</p>
    </div>
  </section>

  <section class="band">
    <div class="figures">
      <div class="figure"><b>{len(pubs)}</b><span>Publications</span></div>
      <div class="figure"><b>{len(PROJECTS)}</b><span>Projects</span></div>
      <div class="figure"><b>{usd(total_all)}</b><span>Research funding</span></div>
      <div class="figure"><b>{len(members_flat())}</b><span>Students supervised</span></div>
      <div class="figure"><b>Top 2%</b><span>Scientists worldwide, 2025</span></div>
    </div>
  </section>

  <section class="band">
    <h2 class="section-title">Selected work</h2>
    <p class="section-note">Four of {len(PROJECTS)} projects. The rest, with filters by
      subject and era, are on the <a href="research.html">Research</a> page.</p>
    <div class="project-grid featured">{feat_html}</div>
  </section>

  <section class="band">
    <div class="railed">
      <div class="rail">
        <h2>Current funding</h2>
        <p>{len(active)} active {"award" if len(active) == 1 else "awards"},
           {usd(active_total)} — of {usd(total_all)} across {len(grants)} awards since 2007.</p>
      </div>
      <div>
        <div class="table-scroll">
          <table class="data">
            <thead><tr><th>Period</th><th>Project</th><th>Role</th><th>Amount</th><th>Status</th></tr></thead>
            <tbody>
            {"".join(f'''<tr>
              <td class="num">{e(g.get('period',''))}</td>
              <td class="col-title">{e(g.get('title',''))}<span class="code-sub">{e(g.get('code',''))}</span></td>
              <td>{e(g.get('role',''))}</td>
              <td class="num">{e(g.get('amount',''))}</td>
              <td>{grant_state(g)}</td>
            </tr>''' for g in sorted(active, key=lambda x: end_year(x.get("period")), reverse=True))}
            </tbody>
          </table>
        </div>
        <p style="margin-top:var(--s4)"><a href="research.html#funding">All {len(grants)} awards &rarr;</a></p>
      </div>
    </div>
  </section>

  <section class="band">
    <div class="railed">
      <div class="rail">
        <h2>Recent publications</h2>
        <p>{len(pubs)} works, synced from ORCID.</p>
      </div>
      <div>
        <ul class="entries">{pub_html}</ul>
        <p style="margin-top:var(--s5)"><a href="publications.html">All publications &rarr;</a></p>
      </div>
    </div>
  </section>
</div>"""
    body += foot()
    write("index.html", body)


def placeholder_svg():
    return ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="1"/>'
            '<path d="M3 15l5-4 4 3 3-2 6 5"/><circle cx="8.5" cy="9.5" r="1.2"/></svg>')


def members_flat():
    out = []
    for g in members:
        out.extend(g["students"])
    return out


# =============================================================================
# RESEARCH
# =============================================================================
def build_research():
    theme_counts, cat_counts = {}, {}
    for p in PROJECTS:
        theme_counts[p["theme"]] = theme_counts.get(p["theme"], 0) + 1
        cat_counts[p["cat"]] = cat_counts.get(p["cat"], 0) + 1

    theme_chips = chip("theme", "all", "All", len(PROJECTS), pressed=True) + "".join(
        chip("theme", k, v, theme_counts[k])
        for k, v in THEMES.items() if theme_counts.get(k)
    )
    cat_chips = chip("cat", "all", "Any era", pressed=True) + "".join(
        chip("cat", slug(c["name"]), CATEGORY_LABELS.get(slug(c["name"]), c["name"]), cat_counts[slug(c["name"])])
        for c in projects["categories"]
    )

    cards, details = [], []
    for p in PROJECTS:
        haystack = " ".join([p["title"], p["theme_label"], p["cat_label"]] + p["bullets"]).lower()
        lead = p["images"][0] if p["images"] else None
        cards.append(f"""
      <article class="pcard" data-id="{p['id']}" data-theme="{p['theme']}" data-cat="{p['cat']}"
               data-search="{e(haystack)}">
        <div class="pcard-media{'' if lead else ' empty'}">
          {'<img src="%s" alt="" loading="lazy">' % e(lead) if lead else placeholder_svg()}
        </div>
        <div class="pcard-body">
          <span class="tag">{e(p['theme_label'])}</span>
          <h3><a href="#{p['id']}">{e(p['title'])}</a></h3>
          <p>{prose(p['bullets'][0]) if p['bullets'] else ''}</p>
          <div class="pcard-foot">
            <span>{e(p['cat_label'])}</span>
            <span class="count">{len(p['images'])} {'image' if len(p['images']) == 1 else 'images'}</span>
          </div>
        </div>
      </article>""")

        plates = "".join(f"""
          <figure class="plate"><img src="{e(src)}" alt="{e(p['title'])} — figure {i+1}" loading="lazy">
            <figcaption>Fig. {i+1}</figcaption></figure>""" for i, src in enumerate(p["images"]))

        details.append(f"""
      <article data-id="{p['id']}" data-theme="{p['theme']}"
               data-theme-label="{e(p['theme_label'])}" id="detail-{p['id']}">
        <h2>{e(p['title'])}</h2>
        <dl class="meta-grid">
          <div><dt>Subject</dt><dd>{e(p['theme_label'])}</dd></div>
          <div><dt>Era</dt><dd>{e(p['cat_label'])}</dd></div>
          <div><dt>Figures</dt><dd>{len(p['images'])}</dd></div>
          {'<div><dt>Website</dt><dd><a href="%s" target="_blank" rel="noopener">%s ↗</a></dd></div>' % (e(p['url']), e(re.sub(r'^https?://(www\.)?', '', p['url']).rstrip('/'))) if p.get('url') else ''}
        </dl>
        <h4>Description</h4>
        <div class="body-copy">{"".join('<p>%s</p>' % prose(b) for b in p['bullets'])}</div>
        {'<h4>Figures</h4><div class="plates">%s</div>' % plates if plates else ''}
      </article>""")

    grants_sorted = sorted(grants, key=lambda g: end_year(g.get("period")), reverse=True)
    total_all = sum(money(g.get("amount")) for g in grants)
    n_active = sum(1 for g in grants if end_year(g.get("period")) >= YEAR_NOW)

    body = head(
        "Research — Osama Halabi",
        f"{len(PROJECTS)} projects in haptics, virtual and augmented reality, driving "
        "simulation, accessibility and laser graphics, with funding history.",
        "research.html",
        scripts=("research.js",),
    )

    body += f"""<div class="wrap">
  <div class="page-head research-masthead">
    <div class="research-masthead-text">
      <p class="eyebrow">XReality Lab</p>
      <h1 class="title">Research</h1>
      <p class="lede">{prose(profile["lab_description"])}</p>
      <nav class="jump-nav" aria-label="Jump to section on this page">
        <a href="#project-grid">Projects ({len(PROJECTS)})</a>
        <a href="#funding">Funding ({len(grants)})</a>
        <a href="#research-interests">Research interests</a>
      </nav>
    </div>
    <img class="lab-mark" src="Logo/xreality-logo-clean-512.png" alt="XReality Lab">
  </div>
</div>"""

    body += f"""
<nav class="toolbar" aria-label="Filter projects">
  <div class="toolbar-inner">
    <div class="chips" role="group" aria-label="Filter by subject">{theme_chips}</div>
    <div class="rule-v" aria-hidden="true"></div>
    <div class="chips" role="group" aria-label="Filter by era">{cat_chips}</div>
    {search_box()}
  </div>
</nav>

<div class="wrap">
  <p class="result-line" id="result-count" role="status" aria-live="polite"></p>
  <div class="project-grid" id="project-grid">{"".join(cards)}
    <div class="empty-state" id="empty-state" hidden>
      <b>Nothing matches that.</b>
      <p>Try a different subject, or <button class="btn" id="clear-filters"
         style="margin-top:var(--s4)">clear all filters</button></p>
    </div>
  </div>

  <div id="project-details">
    <h2 class="section-title" style="margin-bottom:var(--s5)">Project details</h2>
    {"".join(details)}
  </div>

  <section class="band" id="funding">
    <h2 class="section-title">Funding</h2>
    <p class="section-note">{len(grants)} competitive awards, {usd(total_all)} total.
       {n_active} currently active.</p>
    <div class="table-scroll">
      <table class="data">
        <caption>Source: <code>Data/grants.json</code>. Status is derived from the award
          period against the current year, not stored — so it never goes stale.
          {"The %d yen-denominated award%s below %s listed but excluded from the USD total."
           % (len(non_usd_grants()), "" if len(non_usd_grants()) == 1 else "s",
              "is" if len(non_usd_grants()) == 1 else "are") if non_usd_grants() else ""}</caption>
        <thead><tr><th>Period</th><th>Project</th><th>Role</th><th>Amount</th><th>Status</th></tr></thead>
        <tbody>
        {"".join(f'''<tr>
          <td class="num">{e(g.get('period',''))}</td>
          <td class="col-title">{e(g.get('title',''))}<span class="code-sub">{e(g.get('code',''))}</span></td>
          <td>{e(g.get('role',''))}</td>
          <td class="num">{e(g.get('amount',''))}</td>
          <td>{grant_state(g)}</td></tr>''' for g in grants_sorted)}
        </tbody>
      </table>
    </div>
  </section>

  <section class="band" id="research-interests">
    <h2 class="section-title">Research interests</h2>
    <ul class="taglist">{"".join('<li>%s</li>' % e(x) for x in profile['research_interests'])}</ul>
  </section>
</div>

<div class="scrim" id="scrim"></div>
<aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="Project detail" tabindex="-1">
  <div class="drawer-bar">
    <span id="drawer-kicker"></span>
    <button class="iconbtn" id="drawer-copy" title="Copy link to this project" aria-label="Copy link to this project">
      <svg viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>
    </button>
    <button class="iconbtn" id="drawer-close" title="Close (Esc)" aria-label="Close">
      <svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>
    </button>
  </div>
  <div class="drawer-scroll" id="drawer-scroll"></div>
</aside>"""
    body += foot()
    write("research.html", body)


# =============================================================================
# PUBLICATIONS
# =============================================================================
PUB_TYPES = {
    "journal-article":  "Journal",
    "conference-paper": "Conference",
    "book-chapter":     "Chapter",
    "book":             "Book",
    "data-set":         "Dataset",
    "other":            "Other",
}


def build_publications():
    counts = {}
    for p in pubs:
        counts[p.get("type", "other")] = counts.get(p.get("type", "other"), 0) + 1

    chips_html = chip("type", "all", "All", len(pubs), scope="pub-list", pressed=True) + "".join(
        chip("type", k, v, counts[k], scope="pub-list")
        for k, v in PUB_TYPES.items() if counts.get(k)
    )

    by_year = {}
    for p in pubs:
        by_year.setdefault(str(p.get("year") or "n.d."), []).append(p)

    rows = []
    for year in sorted(by_year, reverse=True):
        items = by_year[year]
        rows.append(
            '<div class="year-head" data-group><h2>%s</h2><span>%d</span></div>' % (e(year), len(items))
        )
        rows.append('<ul class="entries">')
        for p in items:
            t = p.get("type", "other")
            hay = " ".join(filter(None, [p.get("title"), p.get("journal"), year])).lower()
            link = p.get("url")
            title = e(p["title"])
            rows.append(f"""<li class="entry" data-row data-facet-type="{e(t)}" data-search="{e(hay)}">
              <div class="k">{e(year)}</div>
              <div class="t">
                <span class="ptype">{e(PUB_TYPES.get(t, t))}</span>
                <b>{('<a href="%s">%s</a>' % (e(link), title)) if link else title}</b>
                <span class="m"><em>{e(p.get('journal') or '')}</em></span>
              </div></li>""")
        rows.append("</ul>")

    body = head(
        "Publications — Osama Halabi",
        "%d peer-reviewed publications in virtual reality, haptics and human-computer "
        "interaction, synced from ORCID." % len(pubs),
        "publications.html",
    )
    body += page_head(
        "%d works" % len(pubs), "Publications",
        "Synced from ORCID (%s). Journal articles, conference papers, chapters, "
        "edited volumes and a patent." % profile["social"]["orcid"].rsplit("/", 1)[-1],
    )
    body += f"""
<nav class="toolbar" aria-label="Filter publications">
  <div class="toolbar-inner">
    <div class="chips" role="group" aria-label="Filter by type">{chips_html}</div>
    {search_box("pub-list", "Search titles and venues")}
  </div>
</nav>
<div class="wrap">
  <p class="result-line"><span data-count-for="pub-list"></span> shown ·
     <button class="chip" data-clear-for="pub-list">Reset</button></p>
  <div id="pub-list" data-filterable data-noun="publication">
    {"".join(rows)}
    <div class="empty-state" data-empty hidden>
      <b>No publications match that.</b><p>Try a broader search term.</p>
    </div>
  </div>
  <p class="section-note" style="margin-top:var(--s7)">
    ORCID is the source of truth for this list — run <code>python scripts/sync_orcid.py</code>
    then <code>python scripts/build.py</code> to refresh it.
  </p>
</div>"""
    body += foot()
    write("publications.html", body)


# =============================================================================
# TEACHING
# =============================================================================
def build_teaching():
    lectures = [t for t in teaching if t.get("category") == "lecture"]
    supervision = [t for t in teaching if t.get("category") == "supervision"]

    def table(rows, caption):
        return f"""<div class="table-scroll"><table class="data">
        <caption>{caption}</caption>
        <thead><tr><th>Code</th><th>Course</th><th>Level</th><th>Institution</th><th>Terms taught</th></tr></thead>
        <tbody>{"".join(f'''<tr>
          <td class="code">{e(r.get('code',''))}</td>
          <td>{e(r.get('name',''))}</td>
          <td>{e(r.get('level',''))}</td>
          <td>{e(r.get('university',''))}</td>
          <td class="num" style="white-space:normal">{e(r.get('times_taught',''))}</td>
        </tr>''' for r in rows)}</tbody></table></div>"""

    body = head(
        "Teaching — Osama Halabi",
        "Courses taught at Qatar University and Iwate University: HCI, game design, "
        "computer graphics, multimedia systems and programming.",
        "teaching.html",
    )
    body += page_head(
        "Qatar University · Iwate University", "Teaching",
        "Graduate and undergraduate courses since 2006, plus project, thesis and "
        "practical-training supervision.",
    )
    body += f"""<div class="wrap">
  <section class="band">
    <div class="railed">
      <div class="rail"><h2>Lecture courses</h2>
        <p>{len(lectures)} distinct courses across two universities.</p></div>
      <div>{table(lectures, "Term codes: F = Fall, S = Spring, followed by the two-digit year.")}</div>
    </div>
  </section>
  <section class="band">
    <div class="railed">
      <div class="rail"><h2>Supervision</h2>
        <p>Project, thesis and practical-training supervision — recurring almost every term,
           so it is listed separately rather than mixed into the course table.</p></div>
      <div>{table(supervision, "See the People page for the individual students and thesis titles.")}</div>
    </div>
  </section>
</div>"""
    body += foot()
    write("teaching.html", body)


# =============================================================================
# PEOPLE
# =============================================================================
def build_people():
    total = len(members_flat())
    blocks = []
    for g in members:
        studs = sorted(g["students"], key=lambda s: str(s.get("year") or ""), reverse=True)
        blocks.append(f"""<section class="band">
      <div class="railed">
        <div class="rail"><h2>{e(g['level'])}</h2><p>{len(studs)}
          {"person" if len(studs) == 1 else "people"}</p></div>
        <div><ul class="entries">{"".join(f'''
          <li class="entry">
            <div class="k">{e(s.get('year',''))}</div>
            <div class="t"><b>{e(s.get('names',''))}</b>
              <span class="m">{e(s.get('title',''))}</span>
              <span class="m">{e(s.get('role',''))} &middot; {e(s.get('university',''))}</span>
            </div></li>''' for s in studs)}</ul></div>
      </div></section>""")

    body = head(
        "People — Osama Halabi",
        "%d students and researchers supervised at Qatar University and Iwate "
        "University, from B.Sc. projects to postdoctoral research." % total,
        "people.html",
    )
    body += page_head(
        "%d supervised" % total, "People",
        "Direct supervision only — postdoctoral researchers, doctoral and master's "
        "students, undergraduate projects and research internships. Committee "
        "memberships are not listed here.",
    )
    body += '<div class="wrap">' + "".join(blocks) + "</div>"
    body += foot()
    write("people.html", body)


# =============================================================================
# ABOUT  (bio + education + positions + awards + service)
# =============================================================================
def build_about():
    edu = "".join(f"""<div>
      <dt>{e(x['year'])}</dt>
      <dd><b>{e(x['degree'])}</b><br>
        <span style="color:var(--muted)">{e(x['institution'])}, {e(x['location'])}</span>
        {'<br><span style="color:var(--muted);font-size:var(--t-base)">%s</span>' % e(x['detail']) if x.get('detail') else ''}
      </dd></div>""" for x in profile["education"])

    pos = "".join(f"""<div>
      <dt>{e(x['dates'])}</dt>
      <dd><b>{e(x['title'])}</b>, {e(x['institution'])}<br>
        <span style="color:var(--muted);font-size:var(--t-base)">{e(x.get('department',''))} — {e(x.get('location',''))}</span>
      </dd></div>""" for x in profile["positions_held"])

    aw = "".join(f"""<li class="entry">
      <div class="k">{e(a.get('year',''))}</div>
      <div class="t"><b>{e(a.get('title',''))}</b>
        <span class="m">{prose(a.get('description',''))}</span></div></li>"""
      for a in sorted(awards, key=lambda a: str(a.get("year") or ""), reverse=True))

    SERVICE_SECTIONS = [
        ("boards_and_editorial",  "Boards & editorial roles", ("years", "role", "organization")),
        ("conference_committees", "Conference committees",    ("years", "role", "conference")),
        ("reviewer_service",      "Reviewer service",         ("years", "role", "organization")),
        ("invited_talks",         "Invited talks",            ("year", "title", "venue")),
        ("invited_exhibitions",   "Invited exhibitions",      ("year", "title", "venue")),
        ("public_service",        "Public service",           ("years", "role", "organization")),
        ("university_service",    "University service",       ("years", "role", "committee")),
    ]
    svc, svc_nav = [], []
    for key, label, (kfield, tfield, mfield) in SERVICE_SECTIONS:
        items = service.get(key) or []
        if not items:
            continue
        anchor = "svc-" + slug(label)
        svc_nav.append((anchor, label, len(items)))
        svc.append(f'<h3 class="sub" id="{anchor}">{e(label)} <span style="color:var(--muted);font-size:var(--t-sm);font-weight:400">({len(items)})</span></h3>')
        svc.append('<ul class="entries">' + "".join(f"""<li class="entry">
          <div class="k">{e(year_field(it.get(kfield,'')))}</div>
          <div class="t"><b>{e(it.get(tfield,''))}</b>
            <span class="m">{e(it.get(mfield,''))}{(' &middot; ' + e(it['date'])) if it.get('date') else ''}</span>
          </div></li>""" for it in items) + "</ul>")

    body = head(
        "About — Osama Halabi",
        "Associate Professor at Qatar University. Ph.D. JAIST. Twenty-five years in "
        "virtual reality, haptics and human-computer interaction across Japan and Qatar.",
        "about.html",
    )
    body += page_head("Biography", "About", profile["professional_summary"], nav=f"""
    <nav class="jump-nav" aria-label="Jump to section on this page">
      <a href="#glance">At a glance</a>
      <a href="#education">Education</a>
      <a href="#positions">Positions</a>
      <a href="#awards">Awards ({len(awards)})</a>
      <a href="#service">Service ({sum(n for _, _, n in svc_nav)})</a>
    </nav>""")
    body += f"""<div class="wrap">
  <section class="band" id="glance">
    <div class="railed">
      <div class="rail"><h2>At a glance</h2></div>
      <div>
        <div class="cols">
          <div>
            <h4 style="font-size:var(--t-xs);letter-spacing:.11em;text-transform:uppercase;color:var(--muted);margin-bottom:var(--s3)">Memberships</h4>
            <ul class="taglist" style="flex-direction:column;align-items:flex-start">
              {"".join('<li>%s</li>' % e(m) for m in profile['professional_memberships'])}
            </ul>
          </div>
          <div>
            <h4 style="font-size:var(--t-xs);letter-spacing:.11em;text-transform:uppercase;color:var(--muted);margin-bottom:var(--s3)">Languages</h4>
            <dl class="def">{"".join('<div><dt>%s</dt><dd>%s</dd></div>' % (e(l['language']), e(l['level'])) for l in profile['languages'])}</dl>
          </div>
        </div>
        <div class="actions">
          <a class="btn btn-primary" href="Data/cv_Osama_Halabi.pdf">Full CV (PDF)</a>
          <a class="btn" href="{e(profile['social']['orcid'])}">ORCID</a>
          <a class="btn" href="{e(profile['social']['google_scholar'])}">Google Scholar</a>
        </div>
      </div>
    </div>
  </section>

  <section class="band" id="education">
    <div class="railed">
      <div class="rail"><h2>Education</h2></div>
      <div><dl class="def">{edu}</dl></div>
    </div>
  </section>

  <section class="band" id="positions">
    <div class="railed">
      <div class="rail"><h2>Positions</h2></div>
      <div><dl class="def">{pos}</dl></div>
    </div>
  </section>

  <section class="band" id="awards">
    <div class="railed">
      <div class="rail"><h2>Awards &amp; honours</h2><p>{len(awards)} recognitions.</p></div>
      <div><ul class="entries">{aw}</ul></div>
    </div>
  </section>

  <section class="band" id="service">
    <div class="railed">
      <div class="rail"><h2>Service</h2>
        <p>Editorial boards, programme committees, reviewing, invited talks and
           exhibitions, and university service.</p>
        <nav class="jump-nav vertical" aria-label="Jump to service subsection">
          {"".join(f'<a href="#{a}">{e(label)} ({n})</a>' for a, label, n in svc_nav)}
        </nav>
      </div>
      <div>{"".join(svc)}</div>
    </div>
  </section>
</div>"""
    body += foot()
    write("about.html", body)


# =============================================================================
# CONTACT + 404
# =============================================================================
def build_contact():
    s = profile["social"]
    # split so the address never appears whole (or as a working mailto:) in
    # the static HTML -- harvesting bots scrape raw markup and essentially
    # never execute JS, so site.js re-assembling it client-side on load
    # keeps real visitors' experience identical while giving scrapers
    # nothing to regex for. See site.js's "email reveal" block.
    email_user, email_domain = profile["contact"]["email_work"].split("@", 1)
    body = head("Contact — Osama Halabi",
                "Contact Osama Halabi, Associate Professor, Department of Computer Science "
                "and Engineering, Qatar University.", "contact.html")
    body += page_head("Get in touch", "Contact")
    body += f"""<div class="wrap">
  <section class="band">
    <div class="railed">
      <div class="rail"><h2>Email</h2></div>
      <div>
        <p style="font-size:var(--t-lg)">
          <a class="email-link" href="#" rel="nofollow noopener"
             data-user="{e(email_user)}" data-domain="{e(email_domain)}">Show email address</a>
        </p>
        <noscript><p>Email: {e(email_user)} [at] {e(email_domain)}</p></noscript>
        <p class="callout" style="margin-top:var(--s5)">
          I am glad to hear from prospective graduate students with a background in
          computer graphics, HCI or robotics — please include a CV and a short note on
          which of the projects on the <a href="research.html">Research</a> page interests
          you and why.</p>
      </div>
    </div>
  </section>
  <section class="band">
    <div class="railed">
      <div class="rail"><h2>Elsewhere</h2></div>
      <div><dl class="def">
        <div><dt>ORCID</dt><dd><a href="{e(s['orcid'])}">{e(s['orcid'].rsplit('/',1)[-1])}</a></dd></div>
        <div><dt>Google Scholar</dt><dd><a href="{e(s['google_scholar'])}">Profile</a></dd></div>
        <div><dt>ResearchGate</dt><dd><a href="{e(s['researchgate'])}">Profile</a></dd></div>
        <div><dt>LinkedIn</dt><dd><a href="{e(s['linkedin'])}">Profile</a></dd></div>
        <div><dt>University</dt><dd><a href="{e(s['qu_faculty_page'])}">QU faculty page</a></dd></div>
      </dl></div>
    </div>
  </section>
  <section class="band">
    <div class="railed">
      <div class="rail"><h2>Address</h2></div>
      <div><p>{e(profile['department'])}<br>{e(profile['college'])}<br>
        {e(profile['university'])}<br>{e(profile['location'])}</p></div>
    </div>
  </section>
</div>"""
    body += foot()
    write("contact.html", body)


def build_404():
    body = head("Page not found — Osama Halabi", "That page does not exist.", "404.html")
    body += """<div class="wrap"><div class="page-head" style="border:none">
  <p class="eyebrow">404</p>
  <h1 class="title">That page doesn&rsquo;t exist.</h1>
  <p class="lede">It may have moved when the site was rebuilt. The research projects,
    publications and people pages all have working in-page links.</p>
  <div class="actions">
    <a class="btn btn-primary" href="index.html">Home</a>
    <a class="btn" href="research.html">Research</a>
    <a class="btn" href="publications.html">Publications</a>
  </div>
</div></div>"""
    body += foot()
    write("404.html", body)


def build_meta():
    pages = ["index.html"] + [h for _, h in NAV]
    urls = "".join(
        "  <url><loc>%s/%s</loc><lastmod>%s</lastmod></url>\n" % (SITE_URL, p, BUILT_ON)
        for p in pages
    )
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % urls)
    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE_URL)


def copy_shared_assets():
    """v2 is a real site root. Images and fonts live at the repo root in the
    current layout; copy them in if they are not here yet. Once v2/ is promoted
    to the repo root this becomes a no-op."""
    for sub in ("img", "fonts"):
        src = os.path.join(REPO_ROOT, "assets", sub)
        dst = os.path.join(SITE_DIR, "assets", sub)
        if os.path.isdir(src) and os.path.abspath(src) != os.path.abspath(dst) and not os.path.isdir(dst):
            shutil.copytree(src, dst)
            print("  copied assets/%s" % sub)
    # the CV is linked from the home and about pages
    src_cv = os.path.join(DATA_DIR, "cv_Osama_Halabi.pdf")
    dst_dir = os.path.join(SITE_DIR, "Data")
    if os.path.isfile(src_cv) and os.path.abspath(DATA_DIR) != os.path.abspath(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)
        dst_cv = os.path.join(dst_dir, "cv_Osama_Halabi.pdf")
        if not os.path.isfile(dst_cv):
            shutil.copy2(src_cv, dst_cv)
            print("  copied Data/cv_Osama_Halabi.pdf")


# =============================================================================
def main():
    print("build.py")
    print("  data   %s" % DATA_DIR)
    print("  output %s" % SITE_DIR)
    copy_shared_assets()
    build_home()
    build_research()
    build_publications()
    build_teaching()
    build_people()
    build_about()
    build_contact()
    build_404()
    build_meta()
    print("  %d projects, %d publications, %d grants, %d people, %d awards"
          % (len(PROJECTS), len(pubs), len(grants), len(members_flat()), len(awards)))


if __name__ == "__main__":
    main()
