"""Shared parts: shapes drawn once and cloned into every glyph that uses them.

link_parts.py puts each part on its own page ("part-<name>") in the parts
layer and replaces the shared piece of each glyph with an Inkscape clone of
it, so editing the part changes every glyph at once. The build follows the
clones and strokes after transforming, so a scaled clone keeps the weight.

PARTS: name -> where the original comes from.
  src   (word, [subpath numbers]): taken from that word's drawing when it
        is drawn (subpaths counted in document order across its sub-layer).
  fit   box to scale the source into (uniformly, centred), or
  at    point to move the source's centre to; the default for both is to
        keep it where it is on the word's page.
  d     the shape to use when the source word is not drawn yet.
  clone another part to clone instead of drawing a shape (with fit).

LINKS: word -> the clones it is built from, and its own strokes.
  parts  list of (part, place). place is None for the part exactly where it
         is on its own page (the glyphs then share its position), or one of
           ("fit", box)          scale uniformly into box, centred
           ("stretch", box)      scale each way to fill box
           ("move", (x, y))      keep the size, centre on (x, y)
           ("matrix", m)         an explicit transform
         with an optional third item: a rotation or mirror applied first,
         "flipx", "flipy", "rot90" (clockwise) or "rot-90".
  own    the word's other strokes while it is a draft.
  drop   for a drawn word, the subpaths the clones replace ("all" for all);
         a word that is a part's source drops that part's subpaths itself.
"""

from drafts import BLUNT, DRAFTS, arm, bowl, circle, closed, dot, ellipse, heart, j, line, rays, rect

PARTS = {
    "legs": dict(src=("kama", [0]), d=DRAFTS["kama"]),
    "rays": dict(src=("kalama", [1, 2, 3]), d=rays(200, 350, 175)),
    "mouth": dict(src=("kalama", [0]), fit=(350, 175, 650, 375), d=bowl(350, 650, 175, 200)),
    "closed-mouth": dict(src=("pona", [0]), d="M 275,400 C 350,675 650,675 725,400"),
    "small-triangle": dict(src=("jelo", [5]), d=closed((500, 520), (290, 850), (710, 850))),
    "big-triangle": dict(d=closed((500, 175), (800, 800), (200, 800))),
    "luka": dict(d=arm(350, 750, 225, 825)),
    "hand": dict(clone="luka", fit=(300, 450, 650, 825)),
    "heart": dict(d=heart(500, 225, 600, 600)),
    "palisa": dict(d=ellipse(500, 500, 75, 325, BLUNT)),
    "loop": dict(d="M 365,500 A 135,135 0 1 1 404.5,595.5"),
    "page": dict(d=rect(225, 175, 775, 825)),
    "big-box": dict(d=line((225, 175), (225, 825), (775, 825), (775, 175))),
    "short-box": dict(src=("insa", [0]), d=line((225, 375), (225, 625), (775, 625), (775, 375))),
    "side-box": dict(d=line((275, 175), (425, 175), (425, 825), (275, 825))),
    "hammer": dict(src=("ilo", [0, 1]), d=j(rect(275, 200, 725, 475), line((500, 200), (500, 825)))),
    "wave": dict(d="M 150,450 C 275,550 375,600 500,525 C 625,450 750,375 850,550"),
    "arrowhead": dict(src=("alasa", [0]), d=line((725, 425), (800, 500), (725, 575))),
    "shaft": dict(d=line((500, 150), (500, 850))),
    "stem": dict(src=("a", [0]), d=line((500, 175), (500, 575))),
    "tally": dict(src=("tu", [0]), at=(500, 500), d=line((500, 200), (500, 800))),
    "big-circle": dict(src=("ijo", [0]), d=circle(500, 500, 300)),
}


def shift(dx, dy=0):
    return ("matrix", (1, 0, 0, 1, dx, dy))


LINKS = {
    # Legs: tawa is kama mirrored
    "kama": dict(parts=[("legs", None)]),
    "tawa": dict(parts=[("legs", ("matrix", (-1, 0, 0, 1, 1000, 0)))], drop="all"),
    # Emitters
    "kalama": dict(parts=[("rays", None), ("mouth", ("fit", (300, 450, 700, 725)))]),
    "pana": dict(parts=[("rays", ("fit", (325, 175, 675, 325))), ("hand", None)]),
    "toki": dict(parts=[("rays", ("fit", (325, 175, 675, 300)))], own=circle(500, 600, 225)),
    "sona": dict(parts=[("rays", ("fit", (300, 150, 700, 275))), ("page", ("fit", (325, 375, 675, 850)))]),
    # Mouths: loje and moku share the mouth's place
    "uta": dict(parts=[("mouth", ("fit", (250, 290, 750, 600)))], own=dot(500, 700)),
    "loje": dict(parts=[("mouth", None), ("small-triangle", None)]),
    "moku": dict(parts=[("mouth", None), ("hand", None)]),
    "pona": dict(parts=[("closed-mouth", None)]),
    "ike": dict(parts=[("closed-mouth", ("matrix", (1, 0, 0, -1, 0, 1000)))], drop="all"),
    # Colour triangles
    "jelo": dict(parts=[("small-triangle", None)],
                 own=j(circle(500, 310, 120), line((500, 190), (500, 120)), line((380, 310), (310, 310)),
                       line((620, 310), (690, 310)), line((500, 430), (500, 520)))),
    "laso": dict(parts=[("small-triangle", None)],
                 own=j("M 500,425 C 450,250 300,225 300,325 C 300,400 425,425 500,425",
                       "M 500,425 C 550,250 700,225 700,325 C 700,400 575,425 500,425",
                       line((500, 425), (500, 520)))),
    "kule": dict(parts=[("big-triangle", None)], own=line((175, 500), (825, 500))),
    "pimeja": dict(parts=[("big-triangle", None)],
                   own=j(line((350, 488), (580, 800)), line((650, 488), (420, 800)))),
    "walo": dict(parts=[("big-triangle", None)],
                 own=j(line((250, 425), (370, 450)), line((750, 425), (630, 450)))),
    # Hands: the small hand is a smaller clone of luka, in one place
    "luka": dict(parts=[("luka", None)]),
    "pali": dict(parts=[("hand", None)], own=circle(500, 325, 125)),
    "kepeken": dict(parts=[("hammer", ("fit", (375, 150, 625, 500))), ("hand", None)]),
    "ilo": dict(parts=[("hammer", None)]),
    # Hearts and sticks
    "pilin": dict(parts=[("heart", None)]),
    "olin": dict(parts=[("heart", ("fit", (290, 120, 710, 490))), ("heart", ("fit", (290, 505, 710, 875)))]),
    "unpa": dict(parts=[("heart", ("fit", (230, 125, 770, 590))), ("palisa", ("fit", (430, 255, 570, 855)))]),
    "palisa": dict(parts=[("palisa", None)]),
    # Pointing hands: one loop, turned
    "mi": dict(parts=[("loop", shift(25, -165))], own="M 390,800 V 335"),
    "sina": dict(parts=[("loop", ("matrix", (1, 0, 0, -1, 15, 1155)))], own="M 380,175 V 655"),
    "ona": dict(parts=[("loop", ("matrix", (0, -1, -1, 0, 1185, 1000)))],
                own="M 175,325 A 574.5,574.5 0 0 0 685,635"),
    # Boxes
    "lipu": dict(parts=[("page", None)]),
    "sitelen": dict(parts=[("page", None)], own=j(dot(350, 500), dot(500, 500), dot(650, 500))),
    "pu": dict(parts=[("page", None)], own=j(circle(500, 575, 90), rays(375, 450, 100))),
    "ku": dict(parts=[("page", None)], own=j(line((700, 300), (375, 425), (450, 825)), dot(575, 600))),
    "poki": dict(parts=[("big-box", None)]),
    "open": dict(parts=[("big-box", None)], own=line((225, 625), (775, 625))),
    "insa": dict(parts=[("short-box", None)], own=dot(500, 450)),
    "anpa": dict(parts=[("short-box", ("move", (500, 453)))], own=dot(500, 700), drop=[0]),
    "poka": dict(parts=[("short-box", ("move", (425, 500)))], own=dot(800, 475)),
    "sinpin": dict(parts=[("side-box", None)], own=dot(625, 500)),
    "monsi": dict(parts=[("side-box", ("matrix", (-1, 0, 0, 1, 1000, 0)))], own=dot(375, 500)),
    # Waves
    "linja": dict(parts=[("wave", None)]),
    "telo": dict(parts=[("wave", ("stretch", (175, 250, 825, 450), "flipy")),
                        ("wave", ("stretch", (175, 550, 825, 750), "flipy"))]),
    "kon": dict(parts=[("wave", ("stretch", (275, 175, 425, 825), "rot90")),
                       ("wave", ("stretch", (550, 175, 700, 825), "rot90"))]),
    # Arrows
    "alasa": dict(parts=[("arrowhead", None)],
                  own=j(line((225, 500), (800, 500)), "M 400,200 C 700,250 700,750 400,800 Z")),
    "ni": dict(parts=[("shaft", None), ("arrowhead", ("move", (500, 798), "rot90"))]),
    "nasin": dict(parts=[("shaft", None), ("arrowhead", ("move", (500, 477), "rot-90"))]),
    # Punctuation stems
    "a": dict(parts=[("stem", None)],
              own="M 540,760 C 540,700 440,690 440,760 C 440,830 540,820 540,760 L 575,825"),
    "n": dict(parts=[("stem", None)],
              own="M 375,850 V 725 C 375,650 425,625 475,625 C 550,625 600,675 600,725 V 850"),
    # Tally marks, all in the same places
    "wan": dict(parts=[("tally", None)], own=line((375, 325), (500, 200))),
    "tu": dict(parts=[("tally", shift(-100)), ("tally", shift(100))], drop="all"),
    "mute": dict(parts=[("tally", shift(-150)), ("tally", None), ("tally", shift(150))]),
    "nanpa": dict(parts=[("tally", shift(-125)), ("tally", shift(125)),
                         ("tally", ("matrix", (0, 1, -1, 0, 1000, -125))),
                         ("tally", ("matrix", (0, 1, -1, 0, 1000, 125)))]),
    # Big circles
    "ijo": dict(parts=[("big-circle", None)]),
    "moli": dict(parts=[("big-circle", None)],
                 own=j(line((325, 400), (450, 600)), line((450, 400), (325, 600)),
                       line((550, 400), (675, 600)), line((675, 400), (550, 600)))),
    "ma": dict(parts=[("big-circle", None)], own=j(line((500, 200), (500, 800)), line((200, 500), (800, 500)))),
}
