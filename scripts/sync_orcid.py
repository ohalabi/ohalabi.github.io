"""Pull publications from the ORCID public API into Data/publications_orcid.json.

Run manually whenever you want to refresh: `python scripts/sync_orcid.py`
Does not touch Data/publications_manual.json (books, patents, items ORCID
doesn't have) -- run scripts/build.py afterward to merge both into the
final Data/publications.json used by the site.
"""
import json
import urllib.request
from pathlib import Path

ORCID_ID = "0000-0002-2052-0500"
API_URL = f"https://pub.orcid.org/v3.0/{ORCID_ID}/works"
OUT_PATH = Path(__file__).resolve().parent.parent / "Data" / "publications_orcid.json"


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


def main():
    data = fetch_works()
    publications = []
    for group in data.get("group", []):
        summaries = group.get("work-summary", [])
        if not summaries:
            continue
        w = summaries[0]
        title = ((w.get("title") or {}).get("title") or {}).get("value")
        if not title:
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

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(publications, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(publications)} publications from ORCID to {OUT_PATH}")


if __name__ == "__main__":
    main()
