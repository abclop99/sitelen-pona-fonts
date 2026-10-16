#!/usr/bin/env python3
"""Build a font from its multi-page Inkscape file.

fonts/<font>/glyphs.svg has one page per word in spec/words.tsv. Paths in
the "glyph" layer are centrelines and become strokes of one fixed weight
(round caps and joins); shapes in the "fill" layer are filled as drawn.
Clones of shared parts are followed to their originals. A word with nothing
drawn uses its geometric draft from the "drafts" layer (see drafts.py), and
a word with neither is left out of the font.

Two builds come out of the same drawings:
  mono   every glyph is MONO_ADVANCE wide, centred on the cell. A "<word>.mono" page replaces
         the word's page here when it exists, for glyphs that need a wider
         or differently proportioned drawing in a fixed-width cell.
  prop   each glyph is trimmed to its ink plus equal side bearings.

    python3 build/build.py --font standard
"""

import argparse
import base64
import datetime
import json
import xml.etree.ElementTree as ET

import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from fontTools.svgLib.path.shapes import PathBuilder

from common import (ASCENT, CELL, INKSCAPE_NS, IDENTITY, ROOT, SODIPODI_NS, STROKE, SVG_NS,
                    multiply, parse_transform, read_words)

FAMILY = {
    "standard": "SP Standard Draft",
}
SIDE_BEARING = 60     # each side, proportional build
MONO_ADVANCE = 900    # glyph width, mono build: the 800-wide ink box plus 50 a side
SPACE_PROP = 330      # word space, proportional build
LINE_GAP = 200

SHAPES = {"path", "line", "polyline", "polygon", "rect", "circle", "ellipse"}
ZERO_WIDTH = {
    0x200D: "zwj",
    0xF1995: "stack_joiner",
    0xF1996: "scale_joiner",
}


def local(tag):
    return tag.rsplit("}", 1)[-1]


def hidden(el):
    style = el.get("style", "").replace(" ", "")
    return "display:none" in style or el.get("display") == "none"


XLINK_HREF = "{http://www.w3.org/1999/xlink}href"


def element_paths(el, matrix, ids, depth=0):
    """Yield (svg path data, matrix) for every visible shape under el.

    <use> elements (Inkscape clones) are followed to the element they point
    at, so a shared part drawn once can be placed, scaled or mirrored in
    many glyphs. Strokes are applied after the transform, so a scaled clone
    keeps the same line weight.
    """
    if hidden(el):
        return
    matrix = multiply(matrix, parse_transform(el.get("transform")))
    tag = local(el.tag)
    if tag == "use":
        href = el.get("href") or el.get(XLINK_HREF) or ""
        target = ids.get(href.lstrip("#")) if href.startswith("#") else None
        if target is None or depth > 20:
            raise ValueError(f"clone points at missing element {href!r}")
        offset = (1, 0, 0, 1, float(el.get("x", 0)), float(el.get("y", 0)))
        yield from element_paths(target, multiply(matrix, offset), ids, depth + 1)
        return
    if tag in SHAPES:
        pb = PathBuilder()
        bare = ET.Element(el.tag, {k: v for k, v in el.attrib.items() if k != "transform"})
        pb.add_path_from_element(bare)
        for d in pb.paths:
            yield d, matrix
    for child in el:
        yield from element_paths(child, matrix, ids, depth)


def to_pathops(d, matrix):
    path = pathops.Path()
    parse_path(d, TransformPen(path.getPen(), matrix))
    return path


def read_pages(svg_file):
    """Return ({page label: outline}, drafted labels), outlines as pathops.Paths.

    Each top-level piece of the glyph and fill layers (a path, a clone, a
    group) belongs to the page its centre is on. A page with nothing in those
    layers uses its piece of the drafts layer instead, if it has one. The
    parts layer is not read directly: its pieces only reach the font through
    clones.
    """
    root = ET.parse(svg_file).getroot()
    ids = {e.get("id"): e for e in root.iter() if e.get("id")}
    ink = f"{{{INKSCAPE_NS}}}"
    pages = {}
    nv = root.find(f"{{{SODIPODI_NS}}}namedview")
    for p in (nv.findall(f"{ink}page") if nv is not None else []):
        pages[p.get(f"{ink}label")] = tuple(float(p.get(k)) for k in ("x", "y", "width", "height"))

    def page_of(x, y):
        for label, (px, py, pw, ph) in pages.items():
            if px <= x <= px + pw and py <= y <= py + ph:
                return label
        return None

    def pieces(layer, matrix):
        matrix = multiply(matrix, parse_transform(layer.get("transform")))
        for child in layer:
            if local(child.tag) == "g" and child.get(f"{ink}groupmode") == "layer":
                yield from pieces(child, matrix)
            elif not hidden(child):
                yield child, matrix

    pieces_by_page = {}
    for g in root.findall(f"{{{SVG_NS}}}g"):
        kind = g.get(f"{ink}label")
        if kind not in ("glyph", "fill", "drafts") or hidden(g):
            continue
        for child, matrix in pieces(g, IDENTITY):
            shapes = list(element_paths(child, matrix, ids))
            if not shapes:
                continue
            whole = pathops.Path()
            for d, m in shapes:
                parse_path(d, TransformPen(whole.getPen(), m))
            x0, y0, x1, y1 = whole.bounds
            label = page_of((x0 + x1) / 2, (y0 + y1) / 2)
            if label is None:
                print(f"warning: a piece in the {kind} layer at ({x0:.0f}, {y0:.0f}) is on no page")
                continue
            px, py = pages[label][:2]
            for d, m in shapes:
                p = to_pathops(d, multiply((1, 0, 0, 1, -px, -py), m))
                if kind in ("glyph", "drafts"):
                    p.stroke(STROKE, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
                    p.convertConicsToQuads()
                key = "drafts" if kind == "drafts" else "drawn"
                pieces_by_page.setdefault((key, label), []).append(p)

    found = {"drawn": {}, "drafts": {}}
    for (key, label), ps in pieces_by_page.items():
        out = pathops.Path()
        pathops.union(ps, out.getPen())
        if out.bounds != (0, 0, 0, 0):
            found[key][label] = out
    drafted = set(found["drafts"]) - set(found["drawn"])
    return {**found["drafts"], **found["drawn"]}, drafted


def make_ttglyph(path, dx):
    """Flip SVG coordinates into font coordinates, shift by dx, convert to quadratics."""
    rec = RecordingPen()
    path.draw(TransformPen(rec, (1, 0, 0, -1, dx, ASCENT)))
    area = AreaPen()
    rec.replay(area)
    pen = TTGlyphPen(None)
    # TrueType wants clockwise outer contours (negative area in AreaPen terms).
    rec.replay(Cu2QuPen(pen, max_err=1, reverse_direction=area.value > 0))
    return pen.glyph()


def empty_glyph():
    return TTGlyphPen(None).glyph()


def notdef(width):
    pen = TTGlyphPen(None)
    m, top, bottom = 100, ASCENT - 100, ASCENT - CELL + 100
    pen.moveTo((m, bottom)); pen.lineTo((m, top)); pen.lineTo((width - m, top))
    pen.lineTo((width - m, bottom)); pen.closePath()
    i = 40
    pen.moveTo((m + i, bottom + i)); pen.lineTo((width - m - i, bottom + i))
    pen.lineTo((width - m - i, top - i)); pen.lineTo((m + i, top - i)); pen.closePath()
    return pen.glyph()


def build(font, mode, words, outdir, drawings):
    family = FAMILY.get(font, f"SP {font.title()} Draft")
    style = "Mono" if mode == "mono" else "Regular"
    fullname = f"{family} Mono" if mode == "mono" else family

    order = [".notdef", "space", "ideographic_space", *ZERO_WIDTH.values()]
    full = MONO_ADVANCE if mode == "mono" else CELL
    glyphs = {".notdef": notdef(full), "space": empty_glyph(),
              "ideographic_space": empty_glyph()}
    metrics = {".notdef": (full, 100), "space": (full if mode == "mono" else SPACE_PROP, 0),
               "ideographic_space": (full, 0)}
    cmap = {0x20: "space", 0x3000: "ideographic_space"}
    for cp, name in ZERO_WIDTH.items():
        glyphs[name] = empty_glyph()
        metrics[name] = (0, 0)
        cmap[cp] = name

    drawn, missing = [], []
    for w in words:
        path = drawings.get(w["word"])
        if mode == "mono":
            path = drawings.get(f"{w['word']}.mono", path)
        if path is None:
            missing.append(w["word"])
            continue
        xmin, _, xmax, _ = path.bounds
        if mode == "mono":
            dx, advance = (MONO_ADVANCE - CELL) / 2, MONO_ADVANCE
        else:
            dx = SIDE_BEARING - xmin
            advance = round(xmax - xmin + 2 * SIDE_BEARING)
        name = w["word"]
        glyphs[name] = make_ttglyph(path, dx)
        order.append(name)
        cmap[w["codepoint"]] = name
        drawn.append(name)
        metrics[name] = (advance, 0)

    fb = FontBuilder(CELL, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    glyf = fb.font["glyf"]
    hmtx = {}
    for name in order:
        g = glyf[name]
        g.recalcBounds(glyf)
        lsb = getattr(g, "xMin", 0) if g.numberOfContours else 0
        hmtx[name] = (metrics[name][0], lsb)
    fb.setupHorizontalMetrics(hmtx)
    descent = ASCENT - CELL
    fb.setupHorizontalHeader(ascent=ASCENT, descent=descent, lineGap=LINE_GAP)
    fb.setupNameTable({
        "familyName": family if mode == "prop" else fullname,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{fullname.replace(' ', '')}-draft",
        "fullName": fullname,
        "psName": fullname.replace(" ", "") + "-Regular",
        "version": "Version 0.001",
        "copyright": "Glyphs licensed under the SIL Open Font License 1.1",
        "licenseDescription": "SIL Open Font License 1.1",
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupOS2(
        sTypoAscender=ASCENT, sTypoDescender=descent, sTypoLineGap=LINE_GAP,
        usWinAscent=ASCENT + LINE_GAP // 2, usWinDescent=-descent + LINE_GAP // 2,
        fsSelection=0x40 | 0x80,  # REGULAR, USE_TYPO_METRICS
        achVendID="NONE", version=4,
    )
    fb.setupPost(isFixedPitch=1 if mode == "mono" else 0)
    if mode == "mono":
        fb.font["post"].isFixedPitch = 1
    fb.setupMaxp()

    outdir.mkdir(parents=True, exist_ok=True)
    stem = f"{fullname.replace(' ', '')}"
    ttf = outdir / f"{stem}.ttf"
    fb.save(ttf)
    fb.font.flavor = "woff2"
    fb.font.save(outdir / f"{stem}.woff2")
    print(f"{ttf.relative_to(ROOT)}: {len(drawn)} of {len(words)} words")
    return drawn, missing, stem


def write_test_page(font, words, drawn, drafted, outdir, stems):
    """Write a self-contained test page with both builds embedded."""
    data = {
        "family": FAMILY.get(font, font),
        "built": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "words": [{"word": w["word"], "cp": w["codepoint"], "aliases": w["aliases"],
                   "drawn": w["word"] in drawn, "draft": w["word"] in drafted}
                  for w in words],
        "fonts": {mode: base64.b64encode((outdir / f"{stem}.woff2").read_bytes()).decode()
                  for mode, stem in stems.items()},
    }
    template = (ROOT / "test" / "template.html").read_text(encoding="utf-8")
    page = outdir / "test.html"
    page.write_text(template.replace("/*DATA*/null", json.dumps(data)), encoding="utf-8")
    print(f"{page.relative_to(ROOT)}: open in a browser")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--font", default="standard", help="folder under fonts/")
    ap.add_argument("--out", default=None, help="output folder (default dist/<font>)")
    args = ap.parse_args()

    words = read_words()
    outdir = ROOT / (args.out or f"dist/{args.font}")
    known = {w["word"] for w in words}
    drawings, drafted = read_pages(ROOT / "fonts" / args.font / "glyphs.svg")
    for label in sorted(drawings):
        if label.removesuffix(".mono") not in known:
            print(f"warning: page {label!r} is not a word in spec/words.tsv")
    stems = {}
    for mode in ("mono", "prop"):
        drawn, missing, stems[mode] = build(args.font, mode, words, outdir, drawings)
    write_test_page(args.font, words, set(drawn), drafted, outdir, stems)
    print(f"{len(set(drawn) - drafted)} drawn, {len(drafted & set(drawn))} still drafts")
    if missing:
        print(f"not drawn yet ({len(missing)}): {' '.join(missing)}")


if __name__ == "__main__":
    main()
