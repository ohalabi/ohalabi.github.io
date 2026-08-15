"""
One-off asset-generation script: crops the icon-only mark (no "XREALITY
LAB" wordmark) out of Logo/xreality-logo-card-512.png for use as the
site favicon.

Why crop instead of using the full lockup: a favicon renders at 16-32px in
a browser tab. Baked-in wordmark text is illegible at that size regardless
of which logo variant you start from -- icon-only is the only thing that
reads. (This is a different call from the masthead logo, which deliberately
keeps the full lockup at ~34px next to the text wordmark -- see CLAUDE.md.)

Why the "card" (white-background) variant and not "clean" (transparent):
a transparent-background favicon disappears against a dark browser tab bar
(dark mode / dark OS theme) since the icon has no backing plate of its own.
The white card gives it a visible edge in both light and dark tab bars.

Not part of scripts/build.py (that script only handles JSON -> HTML).
Run manually with: python scripts/build_favicon.py
Outputs assets/img/favicon.png (opaque white background, 512x512).
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Logo" / "xreality-logo-card-512.png"
OUT = ROOT / "assets" / "img" / "favicon.png"


def main():
    im = Image.open(SRC).convert("RGBA")

    # icon occupies rows ~77-333 of the 512px source; the "XREALITY LAB"
    # wordmark sits below it (rows ~362-469) -- crop just the icon, found
    # by scanning the alpha channel for the gap between the two clusters.
    top, bottom = 70, 340
    left, right = 110, 476
    icon = im.crop((left, top, right, bottom))

    # pad to a square canvas (opaque white -- this card variant has no
    # transparency of its own) so it doesn't distort when browsers/OSes
    # resize it into their own (square) favicon slots
    w, h = icon.size
    side = max(w, h) + 32
    square = Image.new("RGBA", (side, side), (255, 255, 255, 255))
    square.paste(icon, ((side - w) // 2, (side - h) // 2), icon)
    square = square.convert("RGB").resize((512, 512), Image.LANCZOS)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    square.save(OUT)
    print("wrote", OUT, square.size)


if __name__ == "__main__":
    main()
