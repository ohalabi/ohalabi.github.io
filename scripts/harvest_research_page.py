"""One-off harvester: parse the saved 'Osama Halabi - Research.html' (a
Chrome "Save As -> Webpage, Complete" copy of the old Google Sites research
page) into structured project data with real image references.

Run once (or whenever the source HTML is replaced):
    python scripts/harvest_research_page.py

Writes Data/projects_harvested.json for manual review/merge into
Data/projects.json, and copies the referenced images into
assets/img/projects/ with slugified, descriptive filenames.
"""
import json
import re
import shutil
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_HTML = ROOT / "Data" / "Osama Halabi - Research.html"
SRC_FILES_DIR = ROOT / "Data" / "Osama Halabi - Research_files"
OUT_JSON = ROOT / "Data" / "projects_harvested.json"
IMG_OUT_DIR = ROOT / "assets" / "img" / "projects"

SKIP_TAGS = {"script", "style", "svg", "button"}


class ResearchPageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.events = []  # list of ('heading'|'img'|'text', value)
        self.skip_depth = 0
        self.skip_stack = []  # tags currently causing a skip
        self.in_h3_depth = 0
        self.h3_buffer = []
        self.text_buffer = []
        self.block_tags = {"li", "p"}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in SKIP_TAGS or attrs.get("aria-label") == "Copy heading link" or attrs.get("role") == "button":
            self.skip_depth += 1
            self.skip_stack.append(tag)
            return
        if tag == "h3":
            self.in_h3_depth += 1
            self.h3_buffer = []
        if tag == "img" and self.skip_depth == 0:
            src = attrs.get("src", "")
            if src:
                self.events.append(("img", src))
        if tag == "br":
            self.text_buffer.append("\n")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self.skip_stack and tag == self.skip_stack[-1]:
            self.skip_stack.pop()
            self.skip_depth -= 1
            return
        if tag == "h3" and self.in_h3_depth > 0:
            self.in_h3_depth -= 1
            if self.in_h3_depth == 0:
                text = "".join(self.h3_buffer).strip()
                text = re.sub(r"\s+", " ", text)
                if text:
                    self.events.append(("heading", text))
        if tag in self.block_tags:
            text = "".join(self.text_buffer).strip()
            text = re.sub(r"[ \t]+", " ", text)
            if text:
                self.events.append(("text", text))
            self.text_buffer = []

    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        if self.in_h3_depth > 0:
            self.h3_buffer.append(data)
        else:
            self.text_buffer.append(data)


def main():
    raw = SRC_HTML.read_text(encoding="utf-8", errors="replace")
    start = raw.find("Skip to navigation")
    end = raw.find(">Google Sites<")
    if start == -1 or end == -1:
        raise SystemExit("Could not find main-content boundaries in source HTML")
    main_html = raw[start:end]

    parser = ResearchPageParser()
    parser.feed(main_html)
    events = parser.events

    # Segment by heading. NOTE: in the saved DOM, each row's image block
    # actually precedes its own heading (confirmed by visually checking
    # image content against project descriptions -- naive "attach to most
    # recently seen heading" put every project's images one project early).
    # So images are buffered and only attached to the *next* heading as it
    # starts, not the current one.
    projects = []
    current = None
    pending_images = []
    for kind, value in events:
        if kind == "img":
            pending_images.append(value)
        elif kind == "heading":
            if current:
                projects.append(current)
            current = {"title": unescape(value), "images": pending_images, "text": []}
            pending_images = []
        elif current is None:
            continue
        elif kind == "text":
            t = unescape(value).strip()
            if len(t) > 2 and t.lower() not in {"copy heading link"}:
                current["text"].append(t)
    if current:
        projects.append(current)
    if pending_images:
        print(f"WARNING: {len(pending_images)} trailing images after the last heading were not attached to any project")

    # copy images with descriptive names, build slug map
    IMG_OUT_DIR.mkdir(parents=True, exist_ok=True)
    seen_src = {}
    for p in projects:
        slug = re.sub(r"[^a-z0-9]+", "-", p["title"].lower()).strip("-")[:60]
        new_names = []
        for i, src in enumerate(p["images"]):
            fname = src.split("/")[-1]  # e.g. "unnamed(6).png"
            src_path = SRC_FILES_DIR / fname
            if not src_path.exists():
                continue
            ext = src_path.suffix
            new_name = f"{slug}-{i+1}{ext}"
            dest = IMG_OUT_DIR / new_name
            if fname not in seen_src:
                shutil.copyfile(src_path, dest)
                seen_src[fname] = new_name
            new_names.append(seen_src[fname])
        p["image_files"] = new_names

    OUT_JSON.write_text(json.dumps(projects, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Parsed {len(projects)} project blocks -> {OUT_JSON}")
    total_imgs = sum(len(p["image_files"]) for p in projects)
    print(f"Copied {total_imgs} images -> {IMG_OUT_DIR}")


if __name__ == "__main__":
    main()
