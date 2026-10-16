#!/usr/bin/env python3
"""Scale each glyph so it reaches the lines: its outer edge touches the ink box.

    python3 build/fit_sizes.py --font standard

A glyph is scaled until its taller side (or wider, for wide glyphs like
*linja*) spans the whole box, 100 to 900, and is centred along that side.
Words that share a linked part in the same place (parts.py) are sized
together, so the part stays put in all of them: the group as a whole fills
the box, and the part's original is scaled with it, so it still matches
the glyphs that clone it. Words built from the parts in SAME_SCALE are
scaled by the same amount, so those parts keep their relative sizes (the
open boxes stay as wide as the closed ones). Words in SMALL are meant to
stay small and grow by the typical amount instead.

Drawings are rescaled in place: path data, circles and path-effect points
change, the stroke width doesn't. Drafts made from shared parts are removed,
for link_parts.py to rebuild at the new size, and the scale of every word
is stored on its glyph sub-layer (data-size), which make_templates.py uses
to size references and new drafts and link_parts.py to place clones. Run those two
afterwards (fit_sizes prints the commands). A glyph that already fills the
box is left alone, so running it again is safe.
"""

import argparse
import re
import statistics
import xml.etree.ElementTree as ET

from build import read_pages
from check_glyphs import transform_d
from common import BOX, IDENTITY, ROOT, STROKE, load_sizes, multiply, parse_size, parse_transform, size_attr
from link_parts import XLINK, inverse, matrix_attr
from make_templates import INK, S, SODI
from parts import LINKS, PARTS

SMALL = {"lili"}
SAME_SCALE = [{"page", "big-box", "short-box", "side-box"}]
LO, HI = BOX[0] + STROKE / 2, BOX[1] - STROKE / 2    # where centrelines may go


def groups():
    """Words that must be scaled together because they share a part's place."""
    parent = {}

    def find(w):
        parent.setdefault(w, w)
        while parent[w] != w:
            w = parent[w]
        return w

    by_part = {}
    for word, spec in LINKS.items():
        find(word)
        for part, place in spec["parts"]:
            if place is None or place[0] == "matrix":
                by_part.setdefault(part, []).append(word)
    for words in by_part.values():
        for w in words[1:]:
            parent[find(w)] = find(words[0])
    out = {}
    for w in parent:
        out.setdefault(find(w), set()).add(w)
    return [g for g in out.values() if len(g) > 1]


def fit(bounds, small_scale=None, scale=None):
    """Matrix taking a centreline box (x0, y0, x1, y1) to fill the ink box
    (or to the given scale, still centred)."""
    x0, y0, x1, y1 = bounds
    w, h = x1 - x0, y1 - y0
    span = HI - LO
    if small_scale:
        s = small_scale
        cx, cy = 500 + s * ((x0 + x1) / 2 - 500), 500 + s * ((y0 + y1) / 2 - 500)
    else:
        s = scale or span / max(w, h)
        cx = 500 if w >= h else 500 + s * ((x0 + x1) / 2 - 500)
        cy = 500 if h >= w else 500 + s * ((y0 + y1) / 2 - 500)
    # Keep the other side inside the box too.
    cx = min(max(cx, LO + s * w / 2), HI - s * w / 2)
    cy = min(max(cy, LO + s * h / 2), HI - s * h / 2)
    return (s, 0, 0, s, cx - s * (x0 + x1) / 2, cy - s * (y0 + y1) / 2)


def conjugate(t, inner):
    """t expressed inside an element whose own transform is inner."""
    return multiply(inverse(inner), multiply(t, inner))


def bake(el, t, effects, skip_uses=()):
    """Apply a uniform scale-and-shift to an element's coordinates."""
    own = parse_transform(el.get("transform"))
    if own != IDENTITY and el.tag != S + "use":
        t = conjugate(t, own)
    tag = el.tag.rsplit("}", 1)[-1]
    s = t[0]
    pt = lambda x, y: (t[0] * x + t[4], t[3] * y + t[5])
    if tag == "path":
        el.set("d", transform_d(el.get("d"), t))
        if el.get(f"{INK}original-d"):
            el.set(f"{INK}original-d", transform_d(el.get(f"{INK}original-d"), t))
        for ref in re.findall(r"#([\w-]+)", el.get(f"{INK}path-effect", "")):
            effect = effects.get(ref)
            for key in ("start_point", "end_point", "center_point"):
                if effect is not None and effect.get(key):
                    x, y = (float(v) for v in effect.get(key).split(","))
                    effect.set(key, "%g,%g" % pt(x, y))
    elif tag in ("circle", "ellipse"):
        x, y = pt(float(el.get("cx", 0)), float(el.get("cy", 0)))
        el.set("cx", f"{x:g}")
        el.set("cy", f"{y:g}")
        for key in ("r", "rx", "ry"):
            if el.get(key):
                el.set(key, f"{float(el.get(key)) * s:g}")
    elif tag == "rect":
        x, y = pt(float(el.get("x", 0)), float(el.get("y", 0)))
        el.set("x", f"{x:g}")
        el.set("y", f"{y:g}")
        for key in ("width", "height", "rx", "ry"):
            if el.get(key):
                el.set(key, f"{float(el.get(key)) * s:g}")
    elif tag == "use":
        if el.get(f"{XLINK}href") not in skip_uses:
            el.set("transform", matrix_attr(multiply(t, own)))
    elif tag == "g":
        for child in el:
            bake(child, t, effects, skip_uses)


def run(path):
    found, drafted = read_pages(path)
    drawn = set(found) - drafted
    # Outlines are stroked; their centrelines lie half a stroke inside.
    inner = {w: (p.bounds[0] + STROKE / 2, p.bounds[1] + STROKE / 2,
                 p.bounds[2] - STROKE / 2, p.bounds[3] - STROKE / 2) for w, p in found.items()}

    sizes = load_sizes(ET.parse(path).getroot())
    fits, notes = {}, []
    grouped = {w for g in groups() for w in g}
    units = [sorted(w for w in g if w in inner) for g in groups()]
    units = [u for u in units if u]
    units += [[w] for w in inner if w not in grouped and w not in SMALL]

    def union(u):
        b = [inner[w] for w in u]
        return min(x[0] for x in b), min(x[1] for x in b), max(x[2] for x in b), max(x[3] for x in b)

    scale = {}
    for parts in SAME_SCALE:
        users = {w for w, spec in LINKS.items()
                 for p, place in spec["parts"] if p in parts and (place is None or place[0] in ("matrix", "move"))}
        tied = [u for u in units if users & set(u)]
        if tied:
            # Compare against the drawings' original size: some may be scaled already.
            had = {u[0]: sizes.get(u[0], IDENTITY)[0] for u in tied}
            s = min(fit(union(u))[0] * had[u[0]] for u in tied)
            scale.update({u[0]: s / had[u[0]] for u in tied})
    for u in units:
        t = fit(union(u), scale=scale.get(u[0]))
        for w in u:
            fits[w] = t
    typical = statistics.median(t[0] for t in fits.values())
    for w in SMALL & set(inner):
        fits[w] = fit(inner[w], typical)

    tree = ET.parse(path)
    root = tree.getroot()
    effects = {e.get("id"): e for e in root.iter(f"{INK}path-effect")}
    layers = {g.get(f"{INK}label"): g for g in root.findall(S + "g")}
    subs = {g.get(f"{INK}label"): g for g in layers["glyph"] if g.get(f"{INK}groupmode") == "layer"}
    drafts = layers["drafts"]
    nv = root.find(f"{SODI}namedview")
    origin = {p.get(f"{INK}label"): (float(p.get("x")), float(p.get("y"))) for p in nv.findall(f"{INK}page")}
    part_els = {e.get("id")[5:]: e for e in layers["parts"].iter()
                if (e.get("id") or "").startswith("part-") and e.tag in (S + "path", S + "use")}
    changed = 0
    new_sizes = dict(sizes)
    for w, t in sorted(fits.items()):
        if abs(t[0] - 1) < 0.003 and abs(t[4]) < 1 and abs(t[5]) < 1:
            continue
        changed += 1
        managed = {f"#part-{p}" for p, _ in LINKS.get(w, {}).get("parts", [])}
        if w in drawn:
            for child in subs[w]:
                bake(child, t, effects, managed)
        for el in list(drafts):
            if (el.get(f"{INK}label") or "") == f"{w} draft":
                if el.tag == S + "g" and any(u.get(f"{XLINK}href") in managed for u in el.iter(S + "use")):
                    drafts.remove(el)      # link_parts.py rebuilds it at the new size
                else:
                    # Drafts carry their page's shift themselves.
                    ox, oy = origin[w]
                    page = (1, 0, 0, 1, ox, oy)
                    bake(el, multiply(page, multiply(t, inverse(page))), effects)
        new_sizes[w] = m = multiply(t, sizes.get(w, IDENTITY))
        subs[w].set("data-size", size_attr(m))
        notes.append(f"{w}: scaled {t[0]:.3f}" + (" (sized with its linked group)" if w in grouped else ""))

    # Each part's original is the size of the words that use it where it is,
    # so those clones are 1:1 and the part's page shows it as they do.
    delta = {}
    for part, el in sorted(part_els.items()):
        users = [w for w, spec in LINKS.items() for p, place in spec["parts"]
                 if p == part and (place is None or place[0] == "matrix") and w in new_sizes]
        if not users:
            continue
        had = parse_size(el.get("data-size"))
        t = multiply(new_sizes[users[0]], inverse(had))
        if abs(t[0] - 1) < 0.001 and abs(t[4]) < 0.5 and abs(t[5]) < 0.5:
            continue
        if el.tag == S + "path":
            bake(el, t, effects)
        delta[part] = t
        el.set("data-size", size_attr(new_sizes[users[0]]))
        notes.append(f"part {part}: scaled {t[0]:.3f} to match {users[0]}")
    # A part that clones another (the small hand is a clone of luka) keeps
    # the shape and place you gave it: undo the change to the part it
    # clones, then take its own.
    for part, spec in PARTS.items():
        el = part_els.get(part)
        if "clone" in spec and el is not None and (part in delta or spec["clone"] in delta):
            m = parse_transform(el.get("transform"))
            m = multiply(delta.get(part, IDENTITY), multiply(m, inverse(delta.get(spec["clone"], IDENTITY))))
            el.set("transform", matrix_attr(m))

    ET.indent(tree)
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    return changed, notes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--font", default="standard")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    changed, notes = run(ROOT / "fonts" / args.font / "glyphs.svg")
    if args.verbose:
        print("\n".join(notes))
    print(f"{changed} glyphs resized. Now run:\n"
          f"  python3 build/make_templates.py --font {args.font}\n"
          f"  python3 build/link_parts.py --font {args.font}")


if __name__ == "__main__":
    main()
