"""Pull publications from the ORCID public API into Data/publications_orcid.json.

Run manually (`python scripts/sync_orcid.py`, then `python scripts/build.py`)
or let .github/workflows/sync-publications.yml run it on a schedule.

ORCID's feed has no co-author list and mis-types many older records, so
the existing file carries curated "authors"/"type" fields backfilled by
scripts/enrich_from_mendeley.py. This sync merges rather than overwrites:
records already in the file keep those curated fields (matched by DOI,
then normalized title), and records new to the file get their author
list from Crossref by DOI where one is available.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ORCID_ID = "0000-0002-2052-0500"
API_URL = f"https://pub.orcid.org/v3.0/{ORCID_ID}/works"
CROSSREF_URL = "https://api.crossref.org/works/"
USER_AGENT = "osamahalabi.com publication sync (https://osamahalabi.com)"
OUT_PATH = Path(__file__).resolve().parent.parent / "Data" / "publications_orcid.json"

# Fields curated by hand/Mendeley that ORCID can't be trusted to supply.
CURATED_FIELDS = ("authors", "type")

# Malformed records that come back from ORCID's own feed, not something
# a sync can filter by shape -- a publisher's placeholder/template
# metadata leaked into Crossref and ORCID picked it up verbatim. Skip by
# exact title so a routine re-sync doesn't silently reintroduce them.
KNOWN_GARBAGE_TITLES = {
    "Metadata of the chapter that will be visualized in Online",
}


def fetch_works():
    req = urllib.request.Request(API_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def extract_year(work_summary):
    date = work_summary.get("publication-date")
    if date and date.get("year"):
        return date["year"]["value"]
    return None


def extract_doi_url(work_summary):
    ext_ids = (work_summary.get("external-ids") or {}).get("external-id", [])
    for ext in ext_ids:
        if ext.get("external-id-type") == "doi":
            url = ext.get("external-id-url")
            if url and url.get("value"):
                return url["value"]
            return f"https://doi.org/{ext.get('external-id-value')}"
    return None


def norm_doi(url):
    if not url or "doi.org/" not in url:
        return None
    return url.split("doi.org/", 1)[1].strip().lower()


def norm_title(s):
    # [\W_], not [^a-z0-9]: several titles are Japanese and would all
    # normalize to "" and collide.
    s = re.sub(r"[\W_]+", " ", (s or "").lower())
    return re.sub(r"\s+", " ", s).strip()


def fetch_crossref_authors(doi):
    """Best effort: an empty list on any failure, never an exception."""
    try:
        req = urllib.request.Request(CROSSREF_URL + urllib.parse.quote(doi),
                                     headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            msg = json.load(resp)["message"]
    except Exception as exc:
        print(f"  Crossref lookup failed for {doi}: {exc}")
        return []
    return [{"family": a["family"], "given": a.get("given", "")}
            for a in msg.get("author", []) if a.get("family")]


def merge_curated(publications, existing):
    by_doi, by_title = {}, {}
    for p in existing:
        doi = norm_doi(p.get("url"))
        if doi:
            by_doi[doi] = p
        by_title.setdefault(norm_title(p["title"]), []).append(p)

    new = []
    for p in publications:
        doi = norm_doi(p.get("url"))
        old = by_doi.get(doi) if doi else None
        if not old:
            cands = by_title.get(norm_title(p["title"]), [])
            old = cands[0] if len(cands) == 1 else None
        if old:
            for k in CURATED_FIELDS:
                if k in old:
                    p[k] = old[k]
            continue
        new.append(p)
        if doi:
            authors = fetch_crossref_authors(doi)
            if authors:
                p["authors"] = authors
    return new


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Japanese titles vs. a cp1252 Windows console
    existing = json.loads(OUT_PATH.read_text(encoding="utf-8")) if OUT_PATH.exists() else []
    data = fetch_works()
    publications = []
    for group in data.get("group", []):
        summaries = group.get("work-summary", [])
        if not summaries:
            continue
        w = summaries[0]
        title = ((w.get("title") or {}).get("title") or {}).get("value")
        if not title or title in KNOWN_GARBAGE_TITLES:
            continue
        publications.append({
            "title": title,
            "year": extract_year(w),
            "type": w.get("type"),
            "journal": ((w.get("journal-title") or {}).get("value")),
            "url": extract_doi_url(w),
            "source": "orcid",
        })

    publications.sort(key=lambda p: (p["year"] or "0"), reverse=True)
    new = merge_curated(publications, existing)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(publications, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(publications)} publications from ORCID to {OUT_PATH}")
    print(f"New since last sync: {len(new)}")
    for p in new:
        n = len(p.get("authors", []))
        print(f"  [{p['year']}] {p['title']}  ({n} authors)" if n else
              f"  [{p['year']}] {p['title']}  (no author list -- needs Mendeley enrichment)")


if __name__ == "__main__":
    main()
