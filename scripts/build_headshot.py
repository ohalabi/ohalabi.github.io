"""
One-off asset-generation script: composites the studio headshot
(Data/Doc. Osama_2.png, already real-alpha) onto a background for use
on the site.

v2 note: this used to build an elaborate navy/gold/cyan scene (radial
gradient, duotoned project-image mosaic, glowing VR-headset/pulse line art,
particle dots) matching the old v1 hero. That whole treatment violated
this site's hard rules (CLAUDE.md: "no radial gradients ... no glow
drop-shadows, no second accent colour") and read as a dark rectangle on
the new paper/ink background regardless -- replaced with a flat fill in
--paper-sunk, no gradient, no motifs.

2026-08-17: swapped the flat fill for a neutral gray radial gradient
(GRAY_LIGHT center -> GRAY_DARK edges) per Qatar University's own
headshot photography standard. This is scoped to the photo asset only --
the gradient lives inside a composited JPEG, not in CSS -- so it isn't
the site-decoration radial-gradient CLAUDE.md's hard rule bans; that
rule is about the page's own visual language (the old v1 hero), not
about what backdrop a headshot photo uses.

Not part of scripts/build.py (that script only handles JSON -> HTML).
Run manually with: python scripts/build_headshot.py
Outputs assets/img/headshot/osama-headshot-square.jpg (primary, full-res
source for the home hero portrait), three downscaled square widths for its
srcset (osama-headshot-square-{500,800,1200}.jpg -- the hero box only ever
renders around 260-500px wide, so the 2060px original is 4-8x more pixels
than any screen uses), and osama-headshot-wide.jpg (og:image, landscape).

Note: watermark_images.py stamps these output files afterward -- re-run it
after this script to restore the watermark on the freshly regenerated JPEGs.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "Data" / "Doc. Osama_2.png"
OUT_DIR = ROOT / "assets" / "img" / "headshot"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SQUARE_WIDTHS = (500, 800, 1200)

# Qatar University studio backdrop: light gray behind the subject's head
# and shoulders, darkening toward the corners -- a radial vignette, not a
# flat fill or a site-decoration gradient (see module docstring).
GRAY_LIGHT = (214, 214, 214)
GRAY_DARK = (118, 118, 118)
CENTER = (0.5, 0.38)  # fraction of (width, height); slightly above true center


def gray_gradient(w, h):
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = CENTER[0] * w, CENTER[1] * h
    dx, dy = (xx - cx) / w, (yy - cy) / h
    dist = np.sqrt(dx ** 2 + dy ** 2)
    t = np.clip(dist / dist.max(), 0, 1) ** 1.15
    channels = [
        np.round(GRAY_LIGHT[i] + (GRAY_DARK[i] - GRAY_LIGHT[i]) * t).astype(np.uint8)
        for i in range(3)
    ]
    return Image.fromarray(np.stack(channels, axis=-1), "RGB")


def main():
    subject_full = Image.open(SOURCE).convert("RGBA")
    # same crop as before -- already tuned to frame head/shoulders well
    sx0, sy0, sx1, sy1 = 759, 85, 3868, 4998
    subject = subject_full.crop((sx0, sy0, sx1, sy1))

    SUBJ_H = 2000
    scale = SUBJ_H / subject.size[1]
    SUBJ_W = round(subject.size[0] * scale)
    subject = subject.resize((SUBJ_W, SUBJ_H), Image.LANCZOS)

    # -- square (primary: home hero portrait, .hero-portrait aspect-ratio:4/5
    #    on desktop crops this via object-fit:cover, aspect-ratio:1 on mobile) --
    TOP = 60
    side_pad = max(40, int(SUBJ_W * 0.12))
    sq_size = SUBJ_H + TOP
    sq = gray_gradient(sq_size, sq_size)
    sq.paste(subject, ((sq_size - SUBJ_W) // 2, TOP), subject)
    sq.save(OUT_DIR / "osama-headshot-square.jpg", quality=92)
    print("saved square:", sq.size)

    for w in SQUARE_WIDTHS:
        sized = sq.resize((w, w), Image.LANCZOS)
        out = OUT_DIR / f"osama-headshot-square-{w}.jpg"
        sized.save(out, quality=85)
        print(f"saved square-{w}:", sized.size, f"({out.stat().st_size/1024:.0f} KB)")

    # -- wide (og:image / twitter:card, conventional ~1.91:1 landscape) --
    WIDE_H = SUBJ_H + TOP + 40
    WIDE_W = round(WIDE_H * 1.91)
    wide = gray_gradient(WIDE_W, WIDE_H)
    wx = WIDE_W - SUBJ_W - max(80, side_pad)  # subject toward the right
    wide.paste(subject, (wx, TOP), subject)
    wide.save(OUT_DIR / "osama-headshot-wide.jpg", quality=92)
    print("saved wide:", wide.size)


if __name__ == "__main__":
    main()
