"""
One-off asset-protection pass: stamps a small, semi-transparent watermark
onto the project photos/diagrams (assets/img/projects/*.webp) and the
headshot files, as a deterrent against casual, uncredited reuse of
research figures. Not real protection -- anyone with an image editor can
crop it out -- but it makes accidental reuse visibly sourced, which is
the actual failure mode being guarded against here.

Overwrites files in place. Not idempotent -- running twice double-stamps
the same file -- so only run once per source image. These files are
git-tracked, so `git checkout -- <path>` recovers the pre-watermark
original if a result looks wrong.

Not part of scripts/build.py's pipeline (that script only handles
JSON -> HTML) and not re-run automatically. Run by hand whenever new
project images or a new headshot are added:
  python scripts/watermark_images.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT / "assets" / "img" / "projects"
HEADSHOT_DIR = ROOT / "assets" / "img" / "headshot"

FONT_PATH = Path(r"C:\Windows\Fonts\segoeuib.ttf")
if not FONT_PATH.exists():
    FONT_PATH = Path(r"C:\Windows\Fonts\segoeui.ttf")

TEXT = "osamahalabi.com"
SIZE_FRAC = 0.032    # watermark text height, relative to the image's shorter side
MARGIN_FRAC = 0.03   # gap from the corner, same reference
TEXT_ALPHA = 110      # 0-255 -- deliberately faint, legible without dominating
SHADOW_ALPHA = 90     # dark shadow offset by 1px so it reads on light AND dark photos

HEADSHOT_FILES = [
    "osama-headshot-square.jpg",
    "osama-headshot-square-500.jpg",
    "osama-headshot-square-800.jpg",
    "osama-headshot-square-1200.jpg",
    "osama-headshot-wide.jpg",
]


def watermark(path, out_path=None):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    short_side = min(w, h)
    font = ImageFont.truetype(str(FONT_PATH), max(12, round(short_side * SIZE_FRAC)))

    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    bbox = draw.textbbox((0, 0), TEXT, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    margin = round(short_side * MARGIN_FRAC)
    x = w - tw - margin - bbox[0]
    y = h - th - margin - bbox[1]

    draw.text((x + 1, y + 1), TEXT, font=font, fill=(0, 0, 0, SHADOW_ALPHA))
    draw.text((x, y), TEXT, font=font, fill=(255, 255, 255, TEXT_ALPHA))

    out = Image.alpha_composite(im, layer).convert("RGB")
    dest = out_path or path
    if dest.suffix.lower() == ".webp":
        out.save(dest, "WEBP", quality=90)
    else:
        out.save(dest, quality=92)


def main():
    targets = sorted(PROJECTS_DIR.glob("*.webp"))
    targets += [HEADSHOT_DIR / name for name in HEADSHOT_FILES]
    n = 0
    for p in targets:
        if not p.exists():
            print("skip (missing):", p)
            continue
        watermark(p)
        n += 1
    print(f"watermarked {n} files")


if __name__ == "__main__":
    main()
