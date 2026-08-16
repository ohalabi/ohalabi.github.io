"""
One-off asset-generation script: composites the studio headshot
(Data/Doc. Osama_2.png, already real-alpha) onto a plain background for use
on the site.

v2 note: this used to build an elaborate navy/gold/cyan scene (radial
gradient, duotoned project-image mosaic, glowing VR-headset/pulse line art,
particle dots) matching the old v1 hero. That whole treatment violates this
site's actual hard rules now (CLAUDE.md: "no radial gradients ... no glow
drop-shadows, no second accent colour") and reads as a dark rectangle on
the new paper/ink background regardless. Replaced with a flat fill in
--paper-sunk (#f3f0ea, the same token style.css already uses for image
letterboxing), no gradient, no motifs -- just the subject.

Not part of scripts/build.py (that script only handles JSON -> HTML).
Run manually with: python scripts/build_headshot.py
Outputs assets/img/headshot/osama-headshot-square.jpg (primary, full-res
source for the home hero portrait), three downscaled square widths for its
srcset (osama-headshot-square-{500,800,1200}.jpg -- the hero box only ever
renders around 260-500px wide, so the 2060px original is 4-8x more pixels
than any screen uses), and osama-headshot-wide.jpg (og:image, landscape).
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "Data" / "Doc. Osama_2.png"
OUT_DIR = ROOT / "assets" / "img" / "headshot"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAPER_SUNK = (243, 240, 234)  # --paper-sunk
SQUARE_WIDTHS = (500, 800, 1200)


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
    sq = Image.new("RGB", (sq_size, sq_size), PAPER_SUNK)
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
    wide = Image.new("RGB", (WIDE_W, WIDE_H), PAPER_SUNK)
    wx = WIDE_W - SUBJ_W - max(80, side_pad)  # subject toward the right
    wide.paste(subject, (wx, TOP), subject)
    wide.save(OUT_DIR / "osama-headshot-wide.jpg", quality=92)
    print("saved wide:", wide.size)


if __name__ == "__main__":
    main()
