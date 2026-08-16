"""
One-off enrichment: merges full author lists (and corrected work types)
from a personal Mendeley BibTeX export into Data/publications_orcid.json.

Why this exists: ORCID's public feed (what sync_orcid.py reads) has no
co-author list at all -- every citation on the site was crediting "Halabi,
O." alone, regardless of how many co-authors a paper actually had. ORCID's
feed also defaults ambiguous/older records to "journal-article", which
mis-typed dozens of pre-2010 conference papers site-wide (confirmed
against the CV's own [J#]/[C#] numbering). A personal Mendeley library
export has both fields, curated by hand -- this script cross-references it
in by DOI first, normalized title second, and leaves anything ambiguous
(duplicate titles, unmatched records) alone rather than guessing.

One record needed a manual override: Mendeley's own "merge duplicates"
feature had glued two differently-formatted author lists for the same
paper together (visible as a repeated/garbled author string). Fixed by
cross-checking the CV's own [C54] listing -- see AUTHOR_OVERRIDES below.

Not part of scripts/build.py's pipeline and not re-run by sync_orcid.py --
run by hand whenever a fresh Mendeley export is available:
  python scripts/enrich_from_mendeley.py "<path to .bib export>"
"""
import json
import re
import sys
from pathlib import Path

import bibtexparser

ROOT = Path(__file__).resolve().parent.parent
SITE_JSON = ROOT / "Data" / "publications_orcid.json"

TYPE_MAP = {
    "article":       "journal-article",
    "inproceedings": "conference-paper",
    "incollection":  "book-chapter",
    "book":          "book",
    "techreport":    "other",
    "misc":          "other",
}

AUTHOR_OVERRIDES = {
    "haptic interaction rendering technique for hiro an opposite human hand haptic interface robot": [
        ("Alhalabi", "Osama"), ("Daniulaitis", "Vytautas"), ("Kawasaki", "Haruhisa"),
        ("Tanaka", "Yuji"), ("Hori", "Takumi"),
    ],
}

# BibTeX (Mendeley's export format) has no native "patent" entry type, so
# the one patent in the library is filed as @misc same as everything else
# that isn't an article/inproceedings/incollection/book/techreport --
# TYPE_MAP alone can't tell it apart from a genuine miscellaneous item.
# Keyed by normalized title, same as AUTHOR_OVERRIDES.
TYPE_OVERRIDES = {
    "method and software of drawing vector oriented graphic for laser projector and a laser projector system": "patent",
}


def clean(s):
    if not s:
        return ""
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def norm_doi(d):
    if not d:
        return None
    d = d.lower().strip()
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d)


def norm_title(s):
    s = clean(s).lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_authors(raw, title_key):
    if title_key in AUTHOR_OVERRIDES:
        return [{"family": f, "given": g} for f, g in AUTHOR_OVERRIDES[title_key]]
    raw = clean(raw)
    if not raw:
        return []
    authors = []
    for seg in raw.split(" and "):
        seg = seg.strip()
        if not seg:
            continue
        if seg.count(",") == 1:
            fam, given = seg.split(",", 1)
            authors.append({"family": fam.strip(), "given": given.strip()})
        elif seg.count(",") >= 2:
            # Several pre-2010 Tohoku-conference records store multiple
            # "Lastname Initial(s)" authors joined by comma instead of the
            # BibTeX-standard " and " -- split further, one author per token.
            for tok in seg.split(","):
                tok = tok.strip()
                if not tok:
                    continue
                bits = tok.rsplit(" ", 1)
                if len(bits) == 2:
                    authors.append({"family": bits[0].strip(), "given": bits[1].strip()})
                else:
                    authors.append({"family": tok, "given": ""})
        else:
            authors.append({"family": seg, "given": ""})
    seen, deduped = set(), []
    for a in authors:
        key = (a["family"].lower(), a["given"].lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(a)
    return deduped


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/enrich_from_mendeley.py <path-to-mendeley.bib>")
    bib_path = Path(sys.argv[1])

    with open(bib_path, encoding="utf-8") as fh:
        db = bibtexparser.load(fh)

    site = json.loads(SITE_JSON.read_text(encoding="utf-8"))
    by_doi = {}
    by_title = {}
    for p in site:
        u = p.get("url") or ""
        if "doi.org/" in u:
            by_doi[norm_doi(u.split("doi.org/", 1)[1])] = p
        by_title.setdefault(norm_title(p["title"]), []).append(p)

    n_authors = n_type_fixed = 0
    unmatched, ambiguous = [], []
    for e in db.entries:
        title = clean(e.get("title"))
        tkey = norm_title(title)
        doi = norm_doi(e.get("doi"))
        target = by_doi.get(doi) if doi else None
        if not target:
            cands = by_title.get(tkey)
            if cands and len(cands) == 1:
                target = cands[0]
            elif cands:
                ambiguous.append((e["ENTRYTYPE"], e.get("year"), title, len(cands)))
        if not target:
            unmatched.append((e["ENTRYTYPE"], e.get("year"), title))
            continue

        authors = parse_authors(e.get("author", ""), tkey)
        if authors:
            target["authors"] = authors
            n_authors += 1

        correct_type = TYPE_OVERRIDES.get(tkey) or TYPE_MAP.get(e["ENTRYTYPE"])
        if correct_type and target.get("type") != correct_type:
            print(f"  type fix: {target['type']} -> {correct_type}  | {title[:70]}")
            target["type"] = correct_type
            n_type_fixed += 1

    SITE_JSON.write_text(json.dumps(site, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print()
    print(f"authors added/updated : {n_authors}")
    print(f"types corrected       : {n_type_fixed}")
    print(f"unmatched (no site entry found): {len(unmatched)}")
    for t in unmatched:
        print("  ", t)
    print(f"ambiguous (multiple site entries share this title, skipped): {len(ambiguous)}")
    for a in ambiguous:
        print("  ", a)


if __name__ == "__main__":
    main()
