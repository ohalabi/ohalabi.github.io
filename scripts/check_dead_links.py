"""
One-off link-integrity check: verifies every outbound link the built site
actually contains still resolves. There are exactly two sources of
outbound <a href> on the whole site: publication DOI/URLs
(Data/publications_orcid.json) and the profile social links
(Data/profile.json). Checked directly and confirmed empty of any url/link
field: grants.json, awards.json, teaching.json, projects.json,
members.json, service.json.

Not a build-time check, and a "BROKEN" result here is a signal to
spot-check by hand, not an automatic verdict -- publisher servers
routinely block scripted requests (Cloudflare challenges, bare 403s) for
links that work fine in a real browser. Follows redirects (a DOI always
redirects through doi.org to the publisher) and sends a normal browser
User-Agent to cut down on that false-positive rate.

Not part of scripts/build.py. Run manually, per PLAN.md SS6's "verify
external links" item:
  python scripts/check_dead_links.py
"""
import concurrent.futures
import json
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
TIMEOUT = 20
WORKERS = 6
CTX = ssl.create_default_context()


def check(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as resp:
            return resp.status, resp.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.geturl()
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def main():
    pubs = json.loads((ROOT / "Data" / "publications_orcid.json").read_text(encoding="utf-8"))
    profile = json.loads((ROOT / "Data" / "profile.json").read_text(encoding="utf-8"))

    targets = []
    for p in pubs:
        if p.get("url"):
            targets.append((p["url"], p["title"][:60], "publication"))
    for key, url in profile.get("social", {}).items():
        if key.startswith("_") or not url:
            continue
        targets.append((url, key, "profile"))

    n_pub = sum(1 for t in targets if t[2] == "publication")
    n_prof = sum(1 for t in targets if t[2] == "profile")
    print(f"checking {len(targets)} outbound links ({n_pub} publications, {n_prof} profile links)\n")

    broken = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(check, url): (url, label, kind) for url, label, kind in targets}
        for fut in concurrent.futures.as_completed(futures):
            url, label, kind = futures[fut]
            status, detail = fut.result()
            ok = isinstance(status, int) and 200 <= status < 400
            if not ok:
                broken.append((kind, label, url, status, detail))

    print(f"resolved cleanly: {len(targets) - len(broken)}/{len(targets)}\n")
    if broken:
        print(f"{len(broken)} flagged -- spot-check by hand, publisher bot-protection can false-positive here:")
        for kind, label, url, status, detail in sorted(broken, key=lambda b: b[0]):
            print(f"  [{kind:11}] {label}")
            print(f"      {url}")
            print(f"      status={status}  {detail or ''}")
    else:
        print("nothing flagged.")


if __name__ == "__main__":
    main()
