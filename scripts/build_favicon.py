"""
One-off asset-generation script: crops the icon-only mark (no "XREALITY
LAB" wordmark) out of Logo/xreality-logo-clean-512.png for use as the
site favicon.

Why crop instead of using the full lockup: a favicon renders at 16-32px in
a browser tab. Baked-in wordmark text is illegible at that size regardless
of which logo variant you start from -- icon-only is the only thing that
reads. (This is a different call from the masthead logo, which deliberately
keeps the full lockup at ~34px next to the text wordmark -- see CLAUDE.md.)

Why "clean" (transparent) and not the "card" (white-background) variant:
transparent is the general best practice for favicons -- it adapts to
whatever chrome color the browser/OS puts behind it instead of imposing a
fixed backing plate. Traded off deliberately against one known downside:
the icon's own colors don't have much contrast on their own, so it can
read as faint against a dark tab bar. If that becomes a real problem again,
xreality-logo-card-512.png (opaque white backing) is the fallback -- see
git history around 2026-08 for that variant's own version of this script.

Why three output sizes instead of one 512px PNG: a bare `<link rel="icon"
href="favicon.png">` at 512px (~170KB) makes every browser tab download
170KB to draw a 16-32px square. Browsers pick the right file from the
`sizes` attribute, so we ship a small one for the tab (32px, a few KB) and
a separate larger one only for the one context that needs it (iOS
home-screen icons, 180px).

Not part of scripts/build.py (that script only handles JSON -> HTML).
Run manually with: python scripts/build_favicon.py
Outputs:
  assets/img/favicon-32.png       32x32,  tab icon
  assets/img/apple-touch-icon.png 180x180, iOS/Android home-screen icon
  assets/img/favicon.png          512x512, kept as a general-purpose source
                                   (e.g. og:image fallback, old bookmarks)
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Logo" / "xreality-logo-clean-512.png"
IMG_DIR = ROOT / "assets" / "img"


def main():
    im = Image.open(SRC).convert("RGBA")

    # icon occupies rows ~77-333 of the 512px source; the "XREALITY LAB"
    # wordmark sits below it (rows ~362-469) -- crop just the icon, found
    # by scanning the alpha channel for the gap between the two clusters.
    top, bottom = 70, 340
    left, right = 110, 476
    icon = im.crop((left, top, right, bottom))

    # pad to a square canvas (transparent) so it doesn't distort when
    # browsers/OSes resize it into their own (square) favicon slots
    w, h = icon.size
    side = max(w, h) + 32
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(icon, ((side - w) // 2, (side - h) // 2), icon)

    IMG_DIR.mkdir(parents=True, exist_ok=True)

    full = square.resize((512, 512), Image.LANCZOS)
    full.save(IMG_DIR / "favicon.png")

    small = square.resize((32, 32), Image.LANCZOS)
    small.save(IMG_DIR / "favicon-32.png", optimize=True)

    # iOS ignores alpha on home-screen icons and fills transparency with
    # black, so the touch icon gets an explicit white backing plate --
    # the one place "card" beats "clean" on purpose, not by accident.
    touch = Image.new("RGBA", square.size, (255, 255, 255, 255))
    touch.paste(square, (0, 0), square)
    touch = touch.convert("RGB").resize((180, 180), Image.LANCZOS)
    touch.save(IMG_DIR / "apple-touch-icon.png", optimize=True)

    for name, sized in (("favicon.png", full), ("favicon-32.png", small),
                         ("apple-touch-icon.png", touch)):
        n = (IMG_DIR / name).stat().st_size
        print(f"wrote {name} {sized.size} ({n/1024:.1f} KB)")


if __name__ == "__main__":
    main()
