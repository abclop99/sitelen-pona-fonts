#!/usr/bin/env python3
"""Put the shared parts (parts.py) in a font's glyphs.svg and link glyphs to them.

    python3 build/link_parts.py --font standard

Each part gets its own page, "part-<name>", with its original in the parts
layer. A part whose source word is drawn takes that drawing; otherwise it
starts from a geometric draft. Every glyph listed in parts.py then gets
clones of its parts: a drawn glyph in its glyph sub-layer (replacing the
strokes the part came from), a draft as a group in the drafts layer.

Running it again leaves parts that already exist, and glyphs that already
use their parts, alone, so it is safe after you edit anything.
"""

import argparse
import math
import xml.etree.ElementTree as ET

from build import element_paths, read_pages, to_pathops
from check_glyphs import absolute, serialise, transform_d
from common import CELL, IDENTITY, ROOT, load_sizes, multiply, page_origin, parse_size, parse_transform, size_attr
from drafts import circle, ellipse
from make_templates import DRAFT_COLOUR, DRAFT_STYLE, GLYPH_STYLE, INK, S, SODI
from parts import LINKS, PARTS

XLINK = "{http://www.w3.org/1999/xlink}"
ET.register_namespace("xlink", XLINK[1:-1])
PRE = {"flipx": (-1, 0, 0, 1, 0, 0), "flipy": (1, 0, 0, -1, 0, 0),
       "rot90": (0, 1, -1, 0, 0, 0), "rot-90": (0, -1, 1, 0, 0, 0)}


def inverse(m):
    a, b, c, d, e, f = m
    det = a * d - b * c
    return (d / det, -b / det, -c / det, a / det, (c * f - d * e) / det, (b * e - a * f) / det)


def near_identity(m):
    return max(abs(x - y) for x, y in zip(m, IDENTITY)) < 1e-6


def matrix_attr(m):
    return "matrix(" + ",".join(f"{round(v, 6):g}" for v in m) + ")"


def element_d(el):
    tag = el.tag.rsplit("}", 1)[-1]
    if tag == "path":
        return el.get("d", "")
    if tag == "circle":
        return circle(float(el.get("cx", 0)), float(el.get("cy", 0)), float(el.get("r")))
    if tag == "ellipse":
        return ellipse(float(el.get("cx", 0)), float(el.get("cy", 0)), float(el.get("rx")), float(el.get("ry")))
    raise ValueError(f"can't split a <{tag}> into strokes")


def subpaths(d):
    """Split path data into absolute subpaths."""
    out, cur = [], []
    for seg in absolute(d):
        if seg[0] == "M" and cur:
            out.append(cur)
            cur = []
        cur.append(seg)
    if cur:
        out.append(cur)
    return [serialise(s) for s in out]


def leaves(sub):
    """Shapes in a sub-layer, in document order, with their subpaths."""
    for el in sub.iter():
        tag = el.tag.rsplit("}", 1)[-1]
        if tag in ("path", "circle", "ellipse"):
            yield el, subpaths(element_d(el))


def bbox(el, ids, pre=IDENTITY):
    b = [to_pathops(d, multiply(pre, m)).bounds for d, m in element_paths(el, IDENTITY, ids)]
    return min(x[0] for x in b), min(x[1] for x in b), max(x[2] for x in b), max(x[3] for x in b)


def place_matrix(box_from, kind, target):
    x0, y0, x1, y1 = box_from
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if kind == "move":
        sx = sy = 1
        tx, ty = target
    else:
        bx0, by0, bx1, by1 = target
        rx = (bx1 - bx0) / w if w > 1e-6 else None
        ry = (by1 - by0) / h if h > 1e-6 else None
        if kind == "fit":
            s = min(r for r in (rx, ry) if r is not None)
            sx = sy = s
        else:
            sx, sy = rx or 1, ry or 1
        tx, ty = (bx0 + bx1) / 2, (by0 + by1) / 2
    return (sx, 0, 0, sy, tx - sx * cx, ty - sy * cy)


def centre(el, ids):
    x0, y0, x1, y1 = bbox(el, ids)
    return (x0 + x1) / 2, (y0 + y1) / 2


def swap_dots(sub, ids):
    """Replace the dots in a drawing (a tiny ring with a point in it, as
    drafts.dot draws them) with clones of the dot parts. Returns how many."""
    els = list(leaves(sub))
    flat = [(el, i, d, to_pathops(d, parse_transform(el.get("transform"))).bounds)
            for el, sps in els for i, d in enumerate(sps)]
    rings = [f for f in flat if 2 < max(f[3][2] - f[3][0], f[3][3] - f[3][1]) < 45]
    points = [f for f in flat if max(f[3][2] - f[3][0], f[3][3] - f[3][1]) <= 2]
    gone, found = set(), []
    for ring in rings:
        b = ring[3]
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        point = next((p for p in points if abs((p[3][0] + p[3][2]) / 2 - cx) < 4
                      and abs((p[3][1] + p[3][3]) / 2 - cy) < 4 and id(p) not in gone), None)
        if point is None:
            continue
        gone |= {id(ring), id(point)}
        found.append(("big-dot" if b[2] - b[0] >= 28 else "dot", cx, cy))
    if not found:
        return 0
    drop = {(id(f[0]), f[1]) for f in flat if id(f) in gone}
    for el, sps in els:
        keep = [d for i, d in enumerate(sps) if (id(el), i) not in drop]
        if len(keep) == len(sps):
            continue
        parent = next(p for p in sub.iter() if el in list(p))
        if not keep:
            parent.remove(el)
            continue
        for k in [k for k in el.attrib if any(t in k for t in ("path-effect", "original-d", "nodetypes"))]:
            del el.attrib[k]
        el.set("d", " ".join(keep))
    for part, cx, cy in found:
        px, py = centre(ids[f"part-{part}"], ids)
        ET.SubElement(sub, S + "use", {f"{XLINK}href": f"#part-{part}", f"{INK}label": part,
                                       "transform": matrix_attr((1, 0, 0, 1, cx - px, cy - py))})
    return len(found)


def placement(part, place, ids, part_size):
    """Clone transform putting a part where a parts.py placement says."""
    pre = PRE[place[2]] if place and len(place) > 2 else IDENTITY
    # Placements are written for the part as parts.py draws it, before
    # fit_sizes.py scaled the original: undo that scale first.
    unscale = inverse(part_size[part])
    if place is None:
        return unscale
    if place[0] == "matrix":
        return multiply(place[1], multiply(pre, unscale))
    pre = multiply(pre, unscale)
    return multiply(place_matrix(bbox(ids[f"part-{part}"], ids, pre), place[0], place[1]), pre)


def link(path):
    found, drafted = read_pages(path)
    drawn = set(found) - drafted
    tree = ET.parse(path)
    root = tree.getroot()
    sizes = load_sizes(root)
    nv = root.find(f"{SODI}namedview")
    pages = {p.get(f"{INK}label"): (float(p.get("x")), float(p.get("y"))) for p in nv.findall(f"{INK}page")}
    layers = {g.get(f"{INK}label"): g for g in root.findall(S + "g")}
    glyph_subs = {g.get(f"{INK}label"): g for g in layers["glyph"]
                  if g.get(f"{INK}groupmode") == "layer"}
    ids = {e.get("id"): e for e in root.iter() if e.get("id")}
    notes = []

    def word_subpaths(word):
        return [(el, i, d) for el, sps in leaves(glyph_subs[word]) for i, d in enumerate(sps)]

    # Parts: one page and one original each.
    parts_layer = layers["parts"]
    part_subs = {g.get(f"{INK}label"): g for g in parts_layer if g.get(f"{INK}groupmode") == "layer"}
    src_map = {}      # part -> matrix from its source word's page to the part's page
    part_size = {}    # part -> how much fit_sizes.py has scaled its original (data-size)
    for name, spec in PARTS.items():
        label = f"part-{name}"
        if label not in pages:
            taken = set(pages.values())
            ox, oy = next(page_origin(i) for i in range(10 ** 4) if page_origin(i) not in taken)
            ET.SubElement(nv, f"{INK}page", {"x": f"{ox:g}", "y": f"{oy:g}", "width": f"{CELL}",
                                              "height": f"{CELL}", "id": f"page-{label}", f"{INK}label": label})
            pages[label] = (ox, oy)
        if label not in part_subs:
            ox, oy = pages[label]
            part_subs[label] = ET.SubElement(parts_layer, S + "g", {
                "id": f"parts-{name}", f"{INK}groupmode": "layer", f"{INK}label": label,
                "transform": f"translate({ox:g},{oy:g})"})
        pid = f"part-{name}"
        if pid in ids and "parts" in spec and ids[pid].tag != S + "g":
            # It used to be drawn as one shape; parts.py now builds it from parts.
            old = ids.pop(pid)
            part_subs[label].remove(old)
        if pid in ids:
            el = ids[pid]
            part_size[name] = size = parse_size(el.get("data-size"))
            if el.get("data-home") and spec.get("src", ("",))[0] in drawn:
                src_map[name] = parse_transform(el.get("data-home"))
            elif "d" in spec and DRAFT_COLOUR in el.get("style", "").lower() and el.get("data-spec") != spec["d"]:
                # A drafted part follows parts.py until you draw it (turn it black).
                el.set("d", transform_d(spec["d"], size) if not near_identity(size) else spec["d"])
                el.set("data-spec", spec["d"])
                notes.append(f"part {name}: redrawn from parts.py")
            continue
        part_size[name] = IDENTITY
        sub = part_subs[label]
        if "parts" in spec:
            # Made of other parts: a group of their clones, filled in below.
            el = ET.SubElement(sub, S + "g", {"id": pid, f"{INK}label": name})
            notes.append(f"part {name}: made from {', '.join(p for p, *_ in spec['parts'])}")
        elif "clone" in spec:
            target = ids[f"part-{spec['clone']}"]
            m = place_matrix(bbox(target, ids), "fit", spec["fit"])
            el = ET.SubElement(sub, S + "use", {f"{XLINK}href": f"#part-{spec['clone']}",
                                                "transform": matrix_attr(m), "id": pid, f"{INK}label": name})
        elif "src" in spec and spec["src"][0] in drawn:
            word, nums = spec["src"]
            sps = [d for _, _, d in word_subpaths(word)]
            d = " ".join(sps[n] for n in nums)
            m = IDENTITY
            probe = ET.Element(S + "path", {"d": d})
            if "fit" in spec:
                m = place_matrix(bbox(probe, ids), "fit", spec["fit"])
            elif "at" in spec:
                m = place_matrix(bbox(probe, ids), "move", spec["at"])
            el = ET.SubElement(sub, S + "path", {"d": transform_d(d, m) if m != IDENTITY else d,
                                                 "style": GLYPH_STYLE, "id": pid, f"{INK}label": name,
                                                 "data-home": matrix_attr(m)})
            src_map[name] = parse_transform(matrix_attr(m))
            if word in sizes:
                # The drawing is already scaled (fit_sizes.py), so the part is too.
                size = multiply(src_map[name], multiply(sizes[word], inverse(src_map[name])))
                el.set("data-size", size_attr(size))
                part_size[name] = size
            notes.append(f"part {name}: taken from your {word}")
        else:
            el = ET.SubElement(sub, S + "path", {"d": spec["d"], "data-spec": spec["d"],
                                                 "style": GLYPH_STYLE if spec.get("black") else DRAFT_STYLE,
                                                 "id": pid, f"{INK}label": name})
            notes.append(f"part {name}: drafted")
        ids[pid] = el

    # Parts that parts.py no longer has, and nothing clones, are removed.
    used = {u.get(f"{XLINK}href") for u in root.iter(S + "use")}
    for label, sub in list(part_subs.items()):
        name = label.removeprefix("part-")
        if name not in PARTS and f"#part-{name}" not in used:
            parts_layer.remove(sub)
            page = next((p for p in nv.findall(f"{INK}page") if p.get(f"{INK}label") == label), None)
            if page is not None:
                nv.remove(page)
            notes.append(f"part {name}: removed (no longer used)")

    # Parts made of other parts: their clones are always put back in place.
    for name, spec in PARTS.items():
        if "parts" in spec:
            g = ids[f"part-{name}"]
            for child in list(g):
                g.remove(child)
            for part, place in spec["parts"]:
                m = multiply(part_size[name], placement(part, place, ids, part_size))
                attrs = {f"{XLINK}href": f"#part-{part}", f"{INK}label": part}
                if not near_identity(m):
                    attrs["transform"] = matrix_attr(m)
                ET.SubElement(g, S + "use", attrs)

    # Dots in your drawings become clones of the dot parts.
    for word in sorted(drawn):
        if word in glyph_subs:
            n = swap_dots(glyph_subs[word], ids)
            if n:
                notes.append(f"{word}: {n} dot(s) now clone the dot parts")

    # ...and are the size parts.py asks for (a dot or a big dot), in the same place.
    for word in sorted(drawn):
        kinds = {item[0] for item in LINKS.get(word, {}).get("parts", []) if item[1] and item[1][0] == "at"}
        if len(kinds) != 1 or word not in glyph_subs:
            continue
        kind = kinds.pop()
        n = 0
        for u in glyph_subs[word].iter(S + "use"):
            href = u.get(f"{XLINK}href")
            if href in ("#part-dot", "#part-big-dot") and href != f"#part-{kind}":
                old = parse_transform(u.get("transform"))
                ox, oy = centre(ids[href[1:]], ids)
                nx, ny = centre(ids[f"part-{kind}"], ids)
                u.set(f"{XLINK}href", f"#part-{kind}")
                u.set(f"{INK}label", kind)
                u.set("transform", matrix_attr((1, 0, 0, 1, old[0] * ox + old[2] * oy + old[4] - nx,
                                                old[1] * ox + old[3] * oy + old[5] - ny)))
                n += 1
        if n:
            notes.append(f"{word}: {n} dot(s) now {'big' if kind == 'big-dot' else 'small'}")

    # Glyphs: clones of their parts.
    drafts_layer = layers["drafts"]
    draft_els = {(e.get(f"{INK}label") or "").removesuffix(" draft"): e for e in drafts_layer}
    for word, spec in LINKS.items():
        if word not in pages:
            continue
        matrices, used_home = [], set()
        for item in spec["parts"]:
            part, place = item[0], item[1]
            if place and place[0] == "at":
                if word in drawn:
                    continue     # a drawing's own dots are swapped for clones below
                x, y = place[1]
                sz = sizes.get(word, IDENTITY)
                cx, cy = centre(ids[f"part-{part}"], ids)
                matrices.append((part, (1, 0, 0, 1, sz[0] * x + sz[4] - cx, sz[3] * y + sz[5] - cy)))
                continue
            pre = PRE[place[2]] if place and len(place) > 2 else IDENTITY
            src = PARTS[part].get("src")
            if word in drawn and src and src[0] == word and part in src_map and part not in used_home:
                # The drawing's own place (undoing fit_sizes.py's scale of the part).
                m = multiply(inverse(src_map[part]), inverse(part_size[part]))
                used_home.add(part)
            else:
                m = placement(part, place, ids, part_size)
            matrices.append((part, multiply(sizes.get(word, IDENTITY), m)))

        current = glyph_subs.get(word) if word in drawn else draft_els.get(word)
        wanted = {f"#part-{p}" for p, _ in matrices}
        linked = [u for u in (current.iter(S + "use") if current is not None else [])
                  if u.get(f"{XLINK}href") in wanted]
        if linked and word not in drawn and [u.get(f"{XLINK}href") for u in linked] != [f"#part-{p}" for p, _ in matrices]:
            linked = []     # parts.py changed what this draft is made of: rebuild it below
        if linked:
            # Already linked: put any clone that has been moved back in its place.
            if [u.get(f"{XLINK}href") for u in linked] != [f"#part-{p}" for p, _ in matrices]:
                notes.append(f"{word}: its clones don't match parts.py; left as they are")
                continue
            moved = 0
            for u, (part, m) in zip(linked, matrices):
                have = parse_transform(u.get("transform"))
                if max(abs(x - y) for x, y in zip(have, m)) > 0.01:
                    if near_identity(m):
                        u.attrib.pop("transform", None)
                    else:
                        u.set("transform", matrix_attr(m))
                    moved += 1
            if moved:
                notes.append(f"{word}: put {moved} moved clone(s) back in place")
            continue

        uses = []
        for part, m in matrices:
            attrs = {f"{XLINK}href": f"#part-{part}", f"{INK}label": part}
            if not near_identity(m):
                attrs["transform"] = matrix_attr(m)
            uses.append(ET.Element(S + "use", attrs))

        if word in drawn:
            sub = glyph_subs[word]
            drop = spec.get("drop", [])
            if not matrices:
                continue
            if not drop and not any((PARTS[p].get("src") or ("",))[0] == word for p, *_ in spec["parts"]):
                notes.append(f"{word}: left alone (drawn, and parts.py doesn't say what the parts replace)")
                continue
            gone = set(range(10 ** 6)) if drop == "all" else set(drop)
            for part, *_ in spec["parts"]:
                src = PARTS[part].get("src")
                if src and src[0] == word and part in src_map:
                    gone |= set(src[1])
            if drop == "all":
                for child in list(sub):
                    sub.remove(child)
            n = 0
            for el, sps in list(leaves(sub)):
                keep = [d for i, d in enumerate(sps, n) if i not in gone]
                n += len(sps)
                if len(keep) == len(sps):
                    continue
                parent = next(p for p in sub.iter() if el in list(p))
                if not keep:
                    parent.remove(el)
                    continue
                for k in [k for k in el.attrib if any(t in k for t in ("path-effect", "original-d", "nodetypes"))]:
                    del el.attrib[k]
                el.set("d", " ".join(keep))
            for i, u in enumerate(uses):
                sub.insert(i, u)
            notes.append(f"{word}: your drawing now uses {', '.join(p for p, *_ in spec['parts'])}")
        else:
            old = draft_els.get(word)
            ox, oy = pages[word]
            g = ET.Element(S + "g", {f"{INK}label": f"{word} draft", "transform": f"translate({ox:g},{oy:g})",
                                     "id": f"draft-{word}"})
            g.extend(uses)
            if spec.get("own"):
                own = spec["own"]
                if word in sizes:
                    own = transform_d(own, sizes[word])
                ET.SubElement(g, S + "path", {"d": own, "style": DRAFT_STYLE})
            if old is not None:
                drafts_layer.insert(list(drafts_layer).index(old), g)
                drafts_layer.remove(old)
            else:
                drafts_layer.append(g)
            notes.append(f"{word}: draft rebuilt from {', '.join(p for p, *_ in spec['parts'])}")

    ET.indent(tree)
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    return notes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--font", default="standard")
    args = ap.parse_args()
    for line in link(ROOT / "fonts" / args.font / "glyphs.svg"):
        print(line)


if __name__ == "__main__":
    main()
