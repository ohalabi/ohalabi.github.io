"""
One-off / repeatable privacy check for Data/cv_Osama_Halabi.pdf, the CV
linked from About and Contact.

Run this manually after dropping in a freshly-exported CV, before it goes
live -- catches the two things that slip through most often when a Word
doc gets re-exported to PDF:
  * a personal (non-work) email address sitting in the contact line --
    profile.json already excludes home email/phone from the site's own
    data on purpose (see its "note" field); a CV that still prints one
    undoes that on the one document search engines actually index the
    full text of.
  * leftover authoring metadata (Grammarly document IDs, template author
    names, etc.) that Word/Acrobat exporters embed invisibly in the file.

Not part of the scripts/build.py pipeline -- run manually:
    python scripts/check_cv_privacy.py
"""
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
CV = ROOT / "Data" / "cv_Osama_Halabi.pdf"
WORK_DOMAIN = "qu.edu.qa"  # must match profile.json's contact.email_work domain
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IGNORE_META = {"/Producer", "/CreationDate", "/ModDate", "/Creator", "/Author"}


def main():
    if not CV.is_file():
        sys.exit(f"not found: {CV}")

    reader = PdfReader(str(CV))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    emails = sorted(set(EMAIL_RE.findall(text)))
    personal = [e for e in emails if WORK_DOMAIN not in e.lower()]
    work = [e for e in emails if WORK_DOMAIN in e.lower()]

    print(f"checked {CV.name} ({len(reader.pages)} pages)\n")

    if personal:
        print("FOUND non-work email address(es) in the CV body text:")
        for addr in personal:
            print(f"  - {addr}")
        print("  -> remove these from the source document before publishing.\n")
    else:
        print("OK: no non-work email addresses found in the body text.\n")

    if work:
        print(f"Work email ({', '.join(work)}) is present -- expected on a CV and")
        print("already public via the QU faculty directory, so this is normal.\n")

    meta = {k: v for k, v in (reader.metadata or {}).items() if v and k not in IGNORE_META}
    if meta:
        print("Other metadata fields present (consider stripping, e.g. Acrobat's")
        print("\"Remove Hidden Information\", before publishing):")
        for k, v in meta.items():
            print(f"  {k}: {v}")
    else:
        print("OK: no extra metadata fields found.")

    sys.exit(1 if personal else 0)


if __name__ == "__main__":
    main()
