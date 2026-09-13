"""
One-off performance audit: measures real Core Web Vitals (LCP, CLS, FCP,
TTFB) plus page weight against the LIVE site by default -- production
network/CDN conditions are what actually affect ranking and real visitors,
not a localhost dev server.

Why not the Lighthouse CLI: this project has no npm/node dependency and
isn't adding one for a single diagnostic. Playwright (already used by
/run-site) drives the same Chromium engine Lighthouse itself uses; this
script reads the same underlying browser Performance APIs a Lighthouse
run computes its scores from (PerformanceObserver for LCP/CLS, the Paint
Timing API for FCP, Navigation Timing for TTFB) via a small page-injected
script, instead of running the full Lighthouse harness.

Not part of scripts/build.py. Run manually whenever a real read on
production performance is wanted (PLAN.md SS8: "periodic Lighthouse
re-check after content additions"):
  python scripts/check_web_vitals.py [base_url]
Defaults to https://osamahalabi.com; pass a local /run-site server URL
(e.g. http://127.0.0.1:PORT) to check a build before it ships instead.
"""
import sys

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "https://osamahalabi.com"
PAGES = ["index.html", "research.html", "publications.html"]

# Google's published Core Web Vitals thresholds (good / needs-improvement / poor)
THRESHOLDS = {
    "lcp": (2500, 4000),   # ms
    "cls": (0.1, 0.25),    # unitless
    "fcp": (1800, 3000),   # ms
    "ttfb": (800, 1800),   # ms
}

VITALS_SCRIPT = """
window.__vitals = {lcp: 0, cls: 0, fcp: 0};
new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const last = entries[entries.length - 1];
  if (last) window.__vitals.lcp = last.renderTime || last.loadTime || 0;
}).observe({type: 'largest-contentful-paint', buffered: true});
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (!entry.hadRecentInput) window.__vitals.cls += entry.value;
  }
}).observe({type: 'layout-shift', buffered: true});
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.name === 'first-contentful-paint') window.__vitals.fcp = entry.startTime;
  }
}).observe({type: 'paint', buffered: true});
"""


def rate(metric, value):
    good, poor = THRESHOLDS[metric]
    if value <= good:
        return "good"
    if value <= poor:
        return "needs-work"
    return "poor"


def audit(page, url):
    sizes = {"total": 0, "count": 0}

    def on_response(resp):
        length = resp.headers.get("content-length")
        if length and length.isdigit():
            sizes["total"] += int(length)
        sizes["count"] += 1

    page.on("response", on_response)
    page.add_init_script(VITALS_SCRIPT)
    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(1000)  # let LCP/CLS observers settle post-load
    vitals = page.evaluate("window.__vitals")
    nav = page.evaluate("""() => {
        const n = performance.getEntriesByType('navigation')[0];
        return n ? {ttfb: n.responseStart - n.requestStart} : null;
    }""")
    page.remove_listener("response", on_response)
    return vitals, nav, sizes


def main():
    print(f"auditing {BASE}\n")
    header = f"{'page':<20}{'LCP':>10}{'CLS':>8}{'FCP':>10}{'TTFB':>10}{'KB':>9}{'reqs':>6}"
    print(header)
    print("-" * len(header))
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page()
        for name in PAGES:
            url = f"{BASE.rstrip('/')}/{name}"
            vitals, nav, sizes = audit(page, url)
            ttfb = nav["ttfb"] if nav else None
            lcp_r, cls_r, fcp_r = rate("lcp", vitals["lcp"]), rate("cls", vitals["cls"]), rate("fcp", vitals["fcp"])
            ttfb_r = rate("ttfb", ttfb) if ttfb is not None else "?"
            print(
                f"{name:<20}{vitals['lcp']:>7.0f}{lcp_r[:2]:>3}"
                f"{vitals['cls']:>6.3f}{cls_r[:2]:>2}"
                f"{vitals['fcp']:>7.0f}{fcp_r[:2]:>3}"
                f"{(ttfb or 0):>7.0f}{ttfb_r[:2]:>3}"
                f"{sizes['total']/1024:>9.0f}{sizes['count']:>6}"
            )
        browser.close()
    print("\ngo/ne/po = good / needs-work / poor, per Google's published CWV thresholds.")
    print("KB/reqs are approximate (content-length header only, no compression accounting).")


if __name__ == "__main__":
    main()
