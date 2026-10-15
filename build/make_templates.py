#!/usr/bin/env python3
"""Create one Inkscape SVG template per word for a font.

Each template has three layers:
  reference  locked, faint: jan Sonja's drawing from pu (linked file, see
             build/fetch_pu_reference.py); other words use a reference font
  guides     locked: the ink box, the midline and the word's name
  glyph      where you draw: open paths along the centre of each stroke
  fill       optional: shapes that should be filled instead of stroked

Existing files keep their glyph and fill layers; only the reference and
guides layers are rewritten. So rerunning this with a different reference
font never touches your drawings.

    python3 build/make_templates.py --font combos --reference path/to/font.ttf
"""

import argparse
import statistics
import xml.etree.ElementTree as ET

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

from common import (BOX, CELL, GRID, INKSCAPE_NS, MIDLINE, ROOT, SODIPODI_NS,
                    STROKE, SVG_NS, read_words)

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

# Relative to fonts/<font>/glyphs/, where the templates live.
PU_LINK = "../../../reference/pu/downloads"
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
    """Glyph outlines from a reference font, scaled into the template's box."""

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

    def svg_path(self, cp):
        b = self._bounds(cp)
        if not b:
            return None
        # Shrink any glyph that would still overflow the box (wide words).
        s = min(self.scale, (BOX[1] - BOX[0]) / max(b[2] - b[0], b[3] - b[1]))
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        # Font y is up, SVG y is down; centre the glyph in the cell.
        t = (s, 0, 0, -s, CELL / 2 - s * cx, MIDLINE + s * cy)
        pen = SVGPathPen(self.glyphs)
        self.glyphs[self.cmap[cp]].draw(TransformPen(pen, t))
        return pen.getCommands()


def layer(parent, label, style=None, locked=False):
    g = ET.SubElement(parent, f"{{{SVG_NS}}}g", {
        "id": label,
        f"{INK}groupmode": "layer",
        f"{INK}label": label,
    })
    if style:
        g.set("style", style)
    if locked:
        g.set(f"{SODI}insensitive", "true")
    return g


def guides_layer(svg, word):
    g = layer(svg, "guides", "fill:none;stroke:#e06666;stroke-width:2", True)
    lo, hi = BOX
    inset = lo + STROKE / 2
    ET.SubElement(g, S + "rect", {"x": str(lo), "y": str(lo), "width": str(hi - lo),
                              "height": str(hi - lo)})
    ET.SubElement(g, S + "rect", {"x": str(inset), "y": str(inset),
                              "width": str(CELL - 2 * inset), "height": str(CELL - 2 * inset),
                              "style": "stroke-dasharray:8,8;stroke:#f4a6a6"})
    ET.SubElement(g, S + "path", {"d": f"M 0,{MIDLINE} H {CELL}", "style": "stroke:#6fa8dc"})
    ET.SubElement(g, S + "path", {"d": f"M {CELL / 2},0 V {CELL}",
                              "style": "stroke:#6fa8dc;stroke-dasharray:4,12"})
    text = ET.SubElement(g, S + "text", {"x": "20", "y": "60",
                                     "style": "font:40px sans-serif;fill:#999999;stroke:none"})
    text.text = word["word"]


def reference_layer(svg, word, ref):
    g = layer(svg, "reference", "opacity:0.25", True)
    if word["set"] == "pu":
        # jan Sonja's drawing from pu, linked rather than copied into the repo.
        # build/fetch_pu_reference.py downloads the files. Every file shares
        # one 27.502 x 31.312 viewBox with the glyph centred, so one placement
        # fits all.
        ET.SubElement(g, S + "image", {
            "href": f"{PU_LINK}/{word['word']}.svg",
            f"{{{XLINK_NS}}}href": f"{PU_LINK}/{word['word']}.svg",  # older Inkscape
            "x": str(round((CELL - PU_WIDTH) / 2, 1)),
            "y": str(round((CELL - PU_HEIGHT) / 2, 1)),
            "width": str(PU_WIDTH), "height": str(PU_HEIGHT),
            "preserveAspectRatio": "none",
        })
    # Words with no pu drawing (nimi ku suli) fall back to the reference font.
    d = ref.svg_path(word["codepoint"]) if ref and word["set"] != "pu" else None
    if d:
        ET.SubElement(g, S + "path", {"d": d, "style": "fill:#3d85c6;stroke:none"})


def new_svg(word):
    svg = ET.Element(f"{{{SVG_NS}}}svg", {
        "width": str(CELL), "height": str(CELL),
        "viewBox": f"0 0 {CELL} {CELL}",
    })
    nv = ET.SubElement(svg, f"{SODI}namedview", {
        "id": "namedview", "pagecolor": "#ffffff",
        f"{INK}document-units": "px", f"{INK}current-layer": "glyph",
        "showgrid": "true",
    })
    ET.SubElement(nv, f"{INK}grid", {
        "id": "grid", "type": "xygrid", "units": "px",
        "originx": "0", "originy": "0",
        "spacingx": str(GRID), "spacingy": str(GRID),
        "empspacing": "4", "visible": "true", "enabled": "true",
    })
    return svg


def write_template(path, word, ref):
    keep = {}
    if path.exists():
        old = ET.parse(path).getroot()
        for g in old.findall(f"{{{SVG_NS}}}g"):
            label = g.get(f"{INK}label")
            if label in ("glyph", "fill"):
                keep[label] = g
        svg = old
        for g in list(svg.findall(f"{{{SVG_NS}}}g")):
            svg.remove(g)
    else:
        svg = new_svg(word)

    # Layer order matters: later layers draw on top.
    reference_layer(svg, word, ref)
    guides_layer(svg, word)
    if "glyph" in keep:
        svg.append(keep["glyph"])
    else:
        g = layer(svg, "glyph", GLYPH_STYLE)
        if word["word"] in STARTERS:
            ET.SubElement(g, S + "path", {"d": STARTERS[word["word"]], "style": GLYPH_STYLE})
    if "fill" in keep:
        svg.append(keep["fill"])
    else:
        layer(svg, "fill", FILL_STYLE)

    ET.indent(svg)
    ET.ElementTree(svg).write(path, encoding="UTF-8", xml_declaration=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--font", default="combos", help="folder under fonts/")
    ap.add_argument("--reference", help="reference .ttf/.otf for the faint layer")
    ap.add_argument("words", nargs="*", help="only these words (default: all)")
    args = ap.parse_args()

    words = read_words()
    if args.words:
        words = [w for w in words if w["word"] in args.words]
    ref = Reference(args.reference, read_words()) if args.reference else None
    out = ROOT / "fonts" / args.font / "glyphs"
    out.mkdir(parents=True, exist_ok=True)
    for w in words:
        for path in [out / f"{w['word']}.svg", out / f"{w['word']}.mono.svg"]:
            if path.name.endswith(".mono.svg") and not path.exists():
                continue
            write_template(path, w, ref)
    print(f"{len(words)} templates in {out.relative_to(ROOT)}"
          + (f", reference: {ref.name}" if ref else ", no reference font"))


if __name__ == "__main__":
    main()
