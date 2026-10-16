#!/usr/bin/env python3
"""Look for problems in a font's glyphs.svg, and fix the safe ones.

    python3 build/check_glyphs.py --font standard          # report only
    python3 build/check_glyphs.py --font standard --fix    # also fix

Run make_templates.py first, so every piece sits in its page's sub-layer.

Reported:
  - ink that spills outside the solid red box
  - pieces in another page's sub-layer, or on no page at all
  - open paths whose ends almost meet (probably meant to be closed)
  - filled shapes in the glyph layer (the build strokes them anyway)

Fixed with --fix:
  - lines that are almost, but not quite, vertical or horizontal
  - stroke styles, so Inkscape shows every piece at the real weight
  - drafts on pages that have their own drawing (the build ignores them)
"""

import argparse
import math
import re
import xml.etree.ElementTree as ET

from build import element_paths, read_pages, to_pathops
from common import BOX, CELL, IDENTITY, ROOT, STROKE, parse_transform
from make_templates import ARGS, GLYPH_STYLE, INK, S, SODI

TOLERANCE = 5        # ink may overshoot the box by this much
NEAR_AXIS = 0.035    # a line this close to vertical/horizontal (slope) gets straightened
NEAR_AXIS_MAX = 20   # ... unless that moves its end by more than this
NEAR_CLOSED = 20     # open subpaths whose ends are closer than this
SHAPES = ("path", "circle", "ellipse", "rect", "line", "polyline", "polygon")


def absolute(d):
    """Parse path data into absolute segments: (cmd, [points]) with M L C Q A Z."""
    tokens = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", d)
    segs, i, cmd = [], 0, None
    cur = start = (0.0, 0.0)
    last_ctrl = None
    while i < len(tokens):
        if tokens[i].isalpha():
            cmd = tokens[i]
            i += 1
            if cmd in "Zz":
                segs.append(("Z", []))
                cur = start
                continue
        n = ARGS[cmd.lower()]
        v = [float(t) for t in tokens[i:i + n]]
        i += n
        rel = cmd.islower()
        ox, oy = cur if rel else (0.0, 0.0)
        low = cmd.lower()
        if low == "m":
            cur = start = (v[0] + ox, v[1] + oy)
            segs.append(("M", [cur]))
            cmd = "l" if rel else "L"
        elif low == "l":
            cur = (v[0] + ox, v[1] + oy)
            segs.append(("L", [cur]))
        elif low == "h":
            cur = (v[0] + (cur[0] if rel else 0), cur[1])
            segs.append(("L", [cur]))
        elif low == "v":
            cur = (cur[0], v[0] + (cur[1] if rel else 0))
            segs.append(("L", [cur]))
        elif low == "c":
            pts = [(v[k] + ox, v[k + 1] + oy) for k in (0, 2, 4)]
            segs.append(("C", pts))
            last_ctrl, cur = pts[1], pts[2]
        elif low == "s":
            c1 = (2 * cur[0] - last_ctrl[0], 2 * cur[1] - last_ctrl[1]) if last_ctrl else cur
            pts = [c1] + [(v[k] + ox, v[k + 1] + oy) for k in (0, 2)]
            segs.append(("C", pts))
            last_ctrl, cur = pts[1], pts[2]
        elif low == "q":
            pts = [(v[k] + ox, v[k + 1] + oy) for k in (0, 2)]
            segs.append(("Q", pts))
            last_ctrl, cur = pts[0], pts[1]
        elif low == "t":
            c1 = (2 * cur[0] - last_ctrl[0], 2 * cur[1] - last_ctrl[1]) if last_ctrl else cur
            pts = [c1, (v[0] + ox, v[1] + oy)]
            segs.append(("Q", pts))
            last_ctrl, cur = c1, pts[1]
        elif low == "a":
            cur = (v[5] + ox, v[6] + oy)
            segs.append(("A", v[:5] + [cur]))
        if low not in "csqt":
            last_ctrl = None
    return segs


def serialise(segs):
    f = lambda p: f"{round(p[0], 3):g},{round(p[1], 3):g}"
    out = []
    for cmd, pts in segs:
        if cmd == "Z":
            out.append("Z")
        elif cmd == "A":
            out.append("A " + " ".join(f"{x:g}" for x in pts[:5]) + " " + f(pts[5]))
        else:
            out.append(cmd + " " + " ".join(f(p) for p in pts))
    return " ".join(out)


def transform_d(d, m):
    """Apply a scale-and-translate (or mirror) matrix to path data."""
    a, b, c, dd, e, f = m
    pt = lambda p: (a * p[0] + c * p[1] + e, b * p[0] + dd * p[1] + f)
    k = math.sqrt(abs(a * dd - b * c))
    flip = a * dd - b * c < 0
    out = []
    for cmd, pts in absolute(d):
        if cmd == "A":
            rx, ry, rot, large, sweep, end = pts
            out.append(("A", [rx * k, ry * k, rot, large, (1 - sweep) if flip else sweep, pt(end)]))
        else:
            out.append((cmd, [pt(p) for p in pts]))
    return serialise(out)


def straighten(segs):
    """Make nearly vertical/horizontal straight lines exactly so. Returns count."""
    fixed = 0
    prev = None
    for k, (cmd, pts) in enumerate(segs):
        end = pts[-1] if pts else None
        if cmd == "L" and prev is not None:
            dx, dy = end[0] - prev[0], end[1] - prev[1]
            if dx and abs(dx) <= NEAR_AXIS * abs(dy) and abs(dx) <= NEAR_AXIS_MAX:
                segs[k] = ("L", [(prev[0], end[1])])
                fixed += 1
            elif dy and abs(dy) <= NEAR_AXIS * abs(dx) and abs(dy) <= NEAR_AXIS_MAX:
                segs[k] = ("L", [(end[0], prev[1])])
                fixed += 1
            end = segs[k][1][-1]
        if cmd != "Z" and end is not None:
            prev = end
    return fixed


def near_closed(segs):
    """Gaps between the start and end of open subpaths that almost meet."""
    gaps, start, cur, closed, n = [], None, None, False, 0
    for cmd, pts in segs + [("M", [None])]:
        if cmd == "M":
            if start and cur and not closed and n > 1:  # one segment is a line or a dot
                gap = math.dist(start, cur)
                if 0.5 < gap < NEAR_CLOSED:
                    gaps.append(gap)
            start, cur, closed, n = pts[0], pts[0], False, 0
        elif cmd == "Z":
            closed = True
        else:
            cur, n = pts[-1], n + 1
    return gaps


def check_leaf(el, kind, where, fix, notes, fixes):
    """Checks and fixes for one shape (groups are walked by the caller)."""
    tag = el.tag.rsplit("}", 1)[-1]
    if tag not in SHAPES or "display:none" in el.get("style", "").replace(" ", ""):
        return
    name = el.get("id", "?")
    style = el.get("style", "")
    filled = re.search(r"(^|;)fill:(?!none)", style)
    if kind == "glyph" and filled:
        notes.append(f"{where}: {name} is filled, but the glyph layer strokes every shape, "
                     f"so it comes out {STROKE // 2} units bigger all round")
    if tag == "path":
        segs = absolute(el.get("d", ""))
        for gap in near_closed(segs):
            notes.append(f"{where}: {name} has ends {gap:.0f} apart; close it if it "
                         "should be one loop (Path ▸ Join, or end with Z)")
        n = straighten(segs)
        if n and fix:
            el.set("d", serialise(segs))
            fixes.append(f"{where}: straightened {n} almost-straight line(s) in {name}")
        elif n:
            notes.append(f"{where}: {name} has {n} line(s) slightly off vertical/horizontal")
    if fix and kind == "glyph" and not filled and style != GLYPH_STYLE:
        el.set("style", GLYPH_STYLE)
        fixes.append(f"{where}: set {name} to the standard stroke style")


def check(path, fix):
    tree = ET.parse(path)
    root = tree.getroot()
    ids = {e.get("id"): e for e in root.iter() if e.get("id")}
    nv = root.find(f"{SODI}namedview")
    pages = {p.get(f"{INK}label"): (float(p.get("x")), float(p.get("y")))
             for p in nv.findall(f"{INK}page")}
    layers = {g.get(f"{INK}label"): g for g in root.findall(S + "g")}
    notes, fixes = [], []

    def page_at(x, y):
        return next((l for l, (px, py) in pages.items()
                     if px <= x <= px + CELL and py <= y <= py + CELL), None)

    def bounds(el, matrix):
        shapes = list(element_paths(el, matrix, ids))
        if not shapes:
            return None
        b = [to_pathops(d, m).bounds for d, m in shapes]
        return min(x[0] for x in b), min(x[1] for x in b), max(x[2] for x in b), max(x[3] for x in b)

    for kind in ("glyph", "fill"):
        layer = layers.get(kind)
        if layer is None:
            continue
        for sub in layer:
            in_sub = sub.get(f"{INK}groupmode") == "layer"
            label = sub.get(f"{INK}label") if in_sub else None
            matrix = parse_transform(sub.get("transform")) if in_sub else IDENTITY
            for el in (list(sub) if in_sub else [sub]):
                name = el.get("id", "?")
                b = bounds(el, matrix)
                if b is None:
                    continue
                at = page_at((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
                where = at or label or "?"
                if at is None:
                    notes.append(f"{where}: {name} is on no page, so the build ignores it")
                elif label and at != label:
                    notes.append(f"{at}: {name} is in the {label} layer but sits on the {at} page")
                for leaf in el.iter():
                    check_leaf(leaf, kind, where, fix, notes, fixes)

    drawn, drafted = read_pages(path)
    own = set(drawn) - drafted
    for label, p in drawn.items():
        x0, y0, x1, y1 = p.bounds
        lo, hi = BOX[0] - TOLERANCE, BOX[1] + TOLERANCE
        if x0 < lo or y0 < lo or x1 > hi or y1 > hi:
            sides = [s for s, bad in (("left", x0 < lo), ("top", y0 < lo),
                                      ("right", x1 > hi), ("bottom", y1 > hi)) if bad]
            notes.append(f"{label}: ink goes past the red box on the {', '.join(sides)} "
                         f"({x0:.0f}, {y0:.0f} to {x1:.0f}, {y1:.0f}; the box is {BOX[0]}-{BOX[1]})")

    # Big glyphs should reach the lines (fit_sizes.py does that); words that
    # share a linked part are sized as a group, so some of them stop short.
    from fit_sizes import SAME_SCALE, SMALL, groups
    from parts import LINKS
    grouped = {w: g for g in groups() for w in g}
    tied = {w: ", ".join(sorted(parts)) for parts in SAME_SCALE for w, spec in LINKS.items()
            if any(p in parts and (pl is None or pl[0] in ("matrix", "move")) for p, pl in spec["parts"])}
    span = BOX[1] - BOX[0]
    for label, p in drawn.items():
        x0, y0, x1, y1 = p.bounds
        size = max(x1 - x0, y1 - y0)
        if label not in SMALL and 0.7 * span <= size < span - 2 * TOLERANCE:
            if label in grouped:
                why = f" (sized with {', '.join(sorted(grouped[label] - {label}))}, which share its parts)"
            elif label in tied:
                why = f" (scaled like the other glyphs made of {tied[label]})"
            else:
                why = "; python3 build/fit_sizes.py fits it"
            notes.append(f"{label}: doesn't reach the lines ({size:.0f} of {span}){why}")

    drafts = layers.get("drafts")
    if drafts is not None:
        for el in list(drafts):
            word = (el.get(f"{INK}label") or "").removesuffix(" draft")
            if word in own:
                if fix:
                    drafts.remove(el)
                    fixes.append(f"{word}: removed the unused draft (your drawing replaces it)")
                else:
                    notes.append(f"{word}: still has a draft under your drawing")

    defs = root.find(S + "defs")
    if defs is not None:
        used = set(re.findall(r"#([\w-]+)", " ".join(
            e.get(f"{INK}path-effect", "") for e in root.iter())))
        for effect in list(defs.findall(f"{INK}path-effect")):
            if effect.get("id") not in used:
                if fix:
                    defs.remove(effect)
                    fixes.append(f"removed the unused path effect {effect.get('id')}")

    if fix and fixes:
        ET.indent(tree)
        tree.write(path, encoding="UTF-8", xml_declaration=True)
    return notes, fixes


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--font", default="standard")
    ap.add_argument("--fix", action="store_true", help="apply the safe fixes")
    args = ap.parse_args()
    notes, fixes = check(ROOT / "fonts" / args.font / "glyphs.svg", args.fix)
    for line in fixes:
        print("fixed:", line)
    for line in sorted(notes):
        print("check:", line)
    if not notes and not fixes:
        print("no problems found")


if __name__ == "__main__":
    main()
