"""Shared constants and helpers for the template and build scripts.

Coordinates: every glyph SVG is a 1000 x 1000 cell (viewBox 0 0 1000 1000,
y pointing down, as in Inkscape). The font uses 1000 units per em with y up.
SVG y = 0 maps to font y = ASCENT and SVG y = 1000 to font y = ASCENT - 1000,
so the cell's midline (SVG y = 500) sits at font y = ASCENT - 500.
"""

import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDS_FILE = ROOT / "spec" / "words.tsv"

CELL = 1000          # cell size in SVG units = font units per em
ASCENT = 900         # font y of the top of the cell
MIDLINE = 500        # SVG y of the midline
BOX = (100, 900)     # outer edge of the ink: glyphs fill this square
STROKE = 40          # stroke width for centrelines
GRID = 25            # Inkscape grid spacing
PAGE_COLUMNS = 12    # pages per row in glyphs.svg
PAGE_GAP = 200       # space between pages


def page_origin(index):
    """Top-left corner of page number index in glyphs.svg."""
    step = CELL + PAGE_GAP
    return (index % PAGE_COLUMNS) * step, (index // PAGE_COLUMNS) * step


SVG_NS = "http://www.w3.org/2000/svg"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
SODIPODI_NS = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"


def read_words():
    """Return a list of dicts: codepoint (int), word, set, aliases (list)."""
    words = []
    for line in WORDS_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        words.append({
            "codepoint": int(cols[0][2:], 16),
            "word": cols[1],
            "set": cols[2],
            "aliases": cols[3].split(",") if len(cols) > 3 and cols[3] else [],
        })
    return words


# --- SVG transforms -------------------------------------------------------

def _mul(a, b):
    """Compose affine matrices (a, b, c, d, e, f): result applies b, then a."""
    a1, b1, c1, d1, e1, f1 = a
    a2, b2, c2, d2, e2, f2 = b
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


IDENTITY = (1, 0, 0, 1, 0, 0)


def parse_transform(text):
    """Parse an SVG transform attribute into one affine matrix."""
    m = IDENTITY
    if not text:
        return m
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", text):
        v = [float(x) for x in re.split(r"[\s,]+", args.strip()) if x]
        if name == "matrix":
            t = tuple(v)
        elif name == "translate":
            t = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif name == "scale":
            t = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
        elif name == "rotate":
            r = math.radians(v[0])
            t = (math.cos(r), math.sin(r), -math.sin(r), math.cos(r), 0, 0)
            if len(v) == 3:
                cx, cy = v[1], v[2]
                t = _mul(_mul((1, 0, 0, 1, cx, cy), t), (1, 0, 0, 1, -cx, -cy))
        elif name == "skewX":
            t = (1, 0, math.tan(math.radians(v[0])), 1, 0, 0)
        elif name == "skewY":
            t = (1, math.tan(math.radians(v[0])), 0, 1, 0, 0)
        else:
            raise ValueError(f"unsupported transform {name}")
        m = _mul(m, t)
    return m


def multiply(a, b):
    return _mul(a, b)



def load_sizes(root):
    """Per-word placement, {word: matrix}, from a glyphs.svg's glyph sub-layers.

    fit_sizes.py stores each word's scale as data-size="scale dx dy" on its
    sub-layer: the word's references, drafts and shared-part clones are
    scaled by that much about the page's top-left and then shifted, so the
    word fills the ink box. Keeping it in the file means it travels with
    the drawings it was measured from.
    """
    out = {}
    for layer in root.findall(f"{{{SVG_NS}}}g"):
        if layer.get(f"{{{INKSCAPE_NS}}}label") != "glyph":
            continue
        for sub in layer:
            if sub.get("data-size"):
                s, dx, dy = (float(v) for v in sub.get("data-size").split())
                out[sub.get(f"{{{INKSCAPE_NS}}}label")] = (s, 0, 0, s, dx, dy)
    return out
