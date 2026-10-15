#!/usr/bin/env python3
"""Create (or refresh) the multi-page Inkscape file a font is drawn in.

fonts/<font>/glyphs.svg has one page per word (Inkscape 1.2+), laid out in
a grid in spec/words.tsv order, plus a "parts" page first for shared pieces.
Its layers span every page:

  reference  locked, faint: jan Sonja's drawing from pu (linked file, see
             build/fetch_pu_reference.py); ku suli words use a reference font
  guides     locked: each page's ink box, midline and word name
  drafts     geometric first drafts (build/drafts.py). The build uses a
             word's draft only while nothing is drawn on its page in glyph
             or fill, so drawing a word replaces it
  parts      shared pieces, drawn on the parts page. Clone them (Alt+D) into
             words; the parts themselves never go into the font
  glyph      where you draw: open paths along the centre of each stroke.
             Each piece belongs to the page its centre is on
  fill       optional: shapes that should be filled instead of stroked

Rerunning rewrites only the reference and guides layers and the page list.
The drafts, parts, glyph and fill layers are kept as they are, and so are
pages you added yourself (for example a "seme.mono" page). A file without a
drafts layer gets one, with a draft on every page that has none.

    python3 build/make_templates.py --font standard
"""

import argparse
import statistics
import xml.etree.ElementTree as ET
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

from common import (BOX, CELL, GRID, INKSCAPE_NS, MIDLINE, ROOT, SODIPODI_NS,
                    STROKE, SVG_NS, page_origin, read_words)
from drafts import DRAFTS

ET.register_namespace("", SVG_NS)
ET.register_namespace("inkscape", INKSCAPE_NS)
ET.register_namespace("sodipodi", SODIPODI_NS)
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("xlink", XLINK_NS)

INK = f"{{{INKSCAPE_NS}}}"
SODI = f"{{{SODIPODI_NS}}}"
S = f"{{{SVG_NS}}}"

GLYPH_STYLE = (f"fill:none;stroke:#000000;stroke-width:{STROKE};"
               "stroke-linecap:round;stroke-linejoin:round")
FILL_STYLE = "fill:#000000;stroke:none"
DRAFT_STYLE = GLYPH_STYLE.replace("#000000", "#8e7cc3")
KEPT_LAYERS = ("drafts", "parts", "glyph", "fill")

# Relative to fonts/<font>/, where glyphs.svg lives.
PU_LINK = "../../reference/pu/downloads"
DEFAULT_REFERENCE = ROOT / "reference/sitelen-seli-kiwen/downloads/sitelenselikiwenjuniko.ttf"
# The tallest pu glyphs (jan, jelo) are about 25 viewBox units tall: fit
# those to the ink box, so the rest keep their size relative to them.
PU_SCALE = (BOX[1] - BOX[0]) / 25
PU_WIDTH, PU_HEIGHT = round(27.502 * PU_SCALE, 1), round(31.312 * PU_SCALE, 1)

# Simple starting shapes for a few words, so a first build has something in it.
# They are ordinary drawings: edit or replace them.
STARTERS = {
    "ala": "M 175,175 825,825 M 825,175 175,825",
    "tu": "M 380,175 V 825 M 620,175 V 825",
    "lupa": "M 250,225 V 525 A 250,250 0 0 0 750,525 V 225",
    "nena": "M 250,775 V 475 A 250,250 0 0 1 750,475 V 775",
    "pona": "M 175,375 Q 500,900 825,375",
    "ike": "M 175,625 Q 500,100 825,625",
}


class Reference:
    """Glyph outlines from a reference font, scaled into a page's box."""

    def __init__(self, path, words):
        self.font = TTFont(path)
        self.cmap = self.font.getBestCmap()
        self.glyphs = self.font.getGlyphSet()
        sizes = []
        for w in words:
            b = self._bounds(w["codepoint"])
            if b:
                sizes.append(max(b[2] - b[0], b[3] - b[1]))
        # Scale so the larger words fill the ink box; small words stay small.
        self.scale = (BOX[1] - BOX[0]) / statistics.quantiles(sizes, n=10)[-1]
        self.name = self.font["name"].getDebugName(4) or str(path)

    def _bounds(self, cp):
        name = self.cmap.get(cp)
        if not name:
            return None
        pen = BoundsPen(self.glyphs)
        self.glyphs[name].draw(pen)
        return pen.bounds

    def svg_path(self, cp, ox, oy):
        b = self._bounds(cp)
        if not b:
            return None
        # Shrink any glyph that would still overflow the box (wide words).
        s = min(self.scale, (BOX[1] - BOX[0]) / max(b[2] - b[0], b[3] - b[1]))
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        # Font y is up, SVG y is down; centre the glyph on its page.
        t = (s, 0, 0, -s, ox + CELL / 2 - s * cx, oy + MIDLINE + s * cy)
        pen = SVGPathPen(self.glyphs)
        self.glyphs[self.cmap[cp]].draw(TransformPen(pen, t))
        return pen.getCommands()


def layer(parent, label, style=None, locked=False):
    g = ET.SubElement(parent, S + "g", {
        "id": label,
        f"{INK}groupmode": "layer",
        f"{INK}label": label,
    })
    if style:
        g.set("style", style)
    if locked:
        g.set(f"{SODI}insensitive", "true")
    return g


def page_guides(g, label, ox, oy):
    lo, hi = BOX
    inset = lo + STROKE / 2
    ET.SubElement(g, S + "rect", {"x": str(ox + lo), "y": str(oy + lo),
                                  "width": str(hi - lo), "height": str(hi - lo)})
    ET.SubElement(g, S + "rect", {"x": str(ox + inset), "y": str(oy + inset),
                                  "width": str(CELL - 2 * inset),
                                  "height": str(CELL - 2 * inset),
                                  "style": "stroke-dasharray:8,8;stroke:#f4a6a6"})
    ET.SubElement(g, S + "path", {"d": f"M {ox},{oy + MIDLINE} h {CELL}",
                                  "style": "stroke:#6fa8dc"})
    ET.SubElement(g, S + "path", {"d": f"M {ox + CELL / 2},{oy} v {CELL}",
                                  "style": "stroke:#6fa8dc;stroke-dasharray:4,12"})
    text = ET.SubElement(g, S + "text", {"x": str(ox + 20), "y": str(oy + 60),
                                         "style": "font:40px sans-serif;fill:#999999;stroke:none"})
    text.text = label


def reference_art(g, word, ref, ox, oy):
    if word["set"] == "pu":
        # jan Sonja's drawing from pu, linked rather than copied into the repo.
        # Every file shares one 27.502 x 31.312 viewBox with the glyph
        # centred, so one placement fits all.
        href = f"{PU_LINK}/{word['word']}.svg"
        ET.SubElement(g, S + "image", {
            "href": href, f"{{{XLINK_NS}}}href": href,  # xlink for older Inkscape
            "x": str(round(ox + (CELL - PU_WIDTH) / 2, 1)),
            "y": str(round(oy + (CELL - PU_HEIGHT) / 2, 1)),
            "width": str(PU_WIDTH), "height": str(PU_HEIGHT),
            "preserveAspectRatio": "none",
        })
    elif ref:
        d = ref.svg_path(word["codepoint"], ox, oy)
        if d:
            ET.SubElement(g, S + "path", {"d": d, "style": "fill:#3d85c6;stroke:none"})


def write_file(path, words, ref):
    keep, own_pages, drawn = {}, [], set(STARTERS)
    labels = {"parts"} | {w["word"] for w in words}
    if path.exists():
        from build import read_pages
        found, drafted = read_pages(path)
        drawn |= set(found) - drafted
        old = ET.parse(path).getroot()
        for g in old.findall(S + "g"):
            if g.get(f"{INK}label") in KEPT_LAYERS:
                keep[g.get(f"{INK}label")] = g
        nv = old.find(f"{SODI}namedview")
        if nv is not None:
            own_pages = [p for p in nv.findall(f"{INK}page")
                         if p.get(f"{INK}label") not in labels]

    svg = ET.Element(S + "svg", {"width": str(CELL), "height": str(CELL),
                                 "viewBox": f"0 0 {CELL} {CELL}"})
    nv = ET.SubElement(svg, f"{SODI}namedview", {
        "id": "namedview", "pagecolor": "#ffffff", "showgrid": "true",
        f"{INK}document-units": "px", f"{INK}current-layer": "glyph",
    })
    ET.SubElement(nv, f"{INK}grid", {
        "id": "grid", "type": "xygrid", "units": "px", "originx": "0", "originy": "0",
        "spacingx": str(GRID), "spacingy": str(GRID),
        "empspacing": "4", "visible": "true", "enabled": "true",
    })
    pages = [("parts", None)] + [(w["word"], w) for w in words]
    for i, (label, _) in enumerate(pages):
        ox, oy = page_origin(i)
        ET.SubElement(nv, f"{INK}page", {"id": f"page-{label}", f"{INK}label": label,
                                         "x": str(ox), "y": str(oy),
                                         "width": str(CELL), "height": str(CELL)})
    nv.extend(own_pages)

    # Layer order matters: later layers draw on top.
    refs = layer(svg, "reference", "opacity:0.25", True)
    guides = layer(svg, "guides", "fill:none;stroke:#e06666;stroke-width:2", True)
    for i, (label, word) in enumerate(pages):
        ox, oy = page_origin(i)
        page_guides(guides, label, ox, oy)
        if word:
            reference_art(refs, word, ref, ox, oy)
    for p in own_pages:
        page_guides(guides, p.get(f"{INK}label"), float(p.get("x")), float(p.get("y")))

    for label, style in (("drafts", DRAFT_STYLE), ("parts", GLYPH_STYLE),
                         ("glyph", GLYPH_STYLE), ("fill", FILL_STYLE)):
        if label in keep:
            svg.append(keep[label])
            continue
        g = layer(svg, label, style)
        if label == "drafts":
            for i, (name, _) in enumerate(pages):
                if name in DRAFTS and name not in drawn:
                    ox, oy = page_origin(i)
                    ET.SubElement(g, S + "path", {"d": DRAFTS[name], "style": DRAFT_STYLE,
                                                  "transform": f"translate({ox},{oy})",
                                                  f"{INK}label": f"{name} draft"})
        if label == "glyph":
            for i, (name, _) in enumerate(pages):
                if name in STARTERS:
                    ox, oy = page_origin(i)
                    ET.SubElement(g, S + "path", {"d": STARTERS[name], "style": GLYPH_STYLE,
                                                  "transform": f"translate({ox},{oy})"})

    ET.indent(svg)
    ET.ElementTree(svg).write(path, encoding="UTF-8", xml_declaration=True)
    return len(pages)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--font", default="standard", help="folder under fonts/")
    ap.add_argument("--reference", default=DEFAULT_REFERENCE,
                    help="reference .ttf/.otf for words with no pu drawing")
    args = ap.parse_args()

    words = read_words()
    ref = Path(args.reference) if args.reference else None
    ref = Reference(ref, words) if ref and ref.exists() else None
    path = ROOT / "fonts" / args.font / "glyphs.svg"
    path.parent.mkdir(parents=True, exist_ok=True)
    n = write_file(path, words, ref)
    print(f"{path.relative_to(ROOT)}: {n} pages"
          + (f", reference font: {ref.name}" if ref else ", no reference font"))


if __name__ == "__main__":
    main()
