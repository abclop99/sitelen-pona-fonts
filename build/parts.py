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
  ref   the word whose reference is shown on the part's page (default: the
        first word in LINKS that uses it).
  parts the part is made of other parts, placed as in LINKS (a group of
        clones; edit the parts it is made of).
  black start black (as drawn) rather than as a purple draft.

LINKS: word -> the clones it is built from, and its own strokes.
  parts  list of (part, place). place is None for the part exactly where it
         is on its own page (the glyphs then share its position), or one of
           ("fit", box)          scale uniformly into box, centred
           ("stretch", box)      scale each way to fill box
           ("move", (x, y))      keep the size, centre on (x, y)
           ("matrix", m)         an explicit transform
           ("at", (x, y))        centre on (x, y) at the part's own size
                                 (for dots, so they are all alike)
         with an optional third item: a rotation or mirror applied first,
         "flipx", "flipy", "rot90" (clockwise) or "rot-90".
  own    the word's other strokes while it is a draft.
  drop   for a drawn word, the subpaths the clones replace ("all" for all);
         a word that is a part's source drops that part's subpaths itself.
"""

from common import CELL, guide_scale, multiply, scale_d

PARTS = {
    "legs": dict(ref="kama",
                 src=("kama", [0]),
                 d="M 120,850.8 L 383.1,850.8 L 558.5,149.2 L 880,821.5 L 704.6,850.8"),
    "rays": dict(ref="kalama",
                 src=("kalama", [1, 2, 3]),
                 d="M 234.8,180.6 L 354.2,332.1 M 500,104.8 L 500,332.1 M 765.2,180.6 L 645.8,332.1"),
    "mouth": dict(ref="uta",
                  src=("kalama", [0]),
                  fit=(350, 175, 650, 375),
                  d="M 342.6,163 L 657.4,163 C 657.4,278.4 615.4,372.8 500,372.8"
                    " C 384.6,372.8 342.6,278.4 342.6,163 Z"),
    "closed-mouth": dict(ref="pona",
                         src=("pona", [0]),
                         d="M 120,331.1 C 246.7,795.6 753.3,795.6 880,331.1"),
    "small-triangle": dict(ref="loje",
                           src=("jelo", [5]),
                           d="M 500,524.9 L 279.7,871.1 L 720.3,871.1 Z"),
    "big-triangle": dict(ref="kule", d="M 500,120 L 864.8,880 L 135.2,880 Z"),
    "luka": dict(ref="luka",
                 d="M 310,373.3 C 310,234 424,120 563.3,120 C 702.7,120 816.7,234 816.7,373.3"
                   " L 816.7,880 M 183.3,658.3 L 310,880 L 310,373.3"),
    "hand": dict(clone="luka", fit=(300, 450, 650, 825)),
    "heart": dict(ref="pilin",
                  d="M 500,291.3 C 371.2,32.3 120,80 120,347.1 C 120,536.8 375,700 500,880"
                    " M 500,291.3 C 628.8,32.3 880,80 880,347.1 C 880,536.8 625,700 500,880"),
    "palisa": dict(ref="palisa",
                   d="M 412.3,500 C 412.3,709.9 443.9,880 500,880"
                     " C 556.1,880 587.7,709.9 587.7,500 C 587.7,290.1 556.1,120 500,120"
                     " C 443.9,120 412.3,290.1 412.3,500 Z"),
    "pointer": dict(ref="mi",
                    d="M 322.7,880 C 329,595 367,405 373.3,278.3 A 158.3 158.3 0 1 1 419.7,390.3"),
    "person-head": dict(ref="jan",
                        src=("jan", [0]),
                        d="M 190.4,429.6 C 190.4,600.7 329,739.3 500,739.3"
                          " C 671,739.3 809.6,600.7 809.6,429.6 C 809.6,258.6 671,120 500,120"
                          " C 329,120 190.4,258.6 190.4,429.6 Z"),
    "page": dict(ref="lipu", d="M 182.4,124.6 L 817.6,124.6 L 817.6,875.4 L 182.4,875.4 Z"),
    "head": dict(ref="toki",
                 d="M 236.9,616.9 C 236.9,762.3 354.7,880 500,880"
                   " C 645.3,880 763.1,762.3 763.1,616.9 C 763.1,471.6 645.3,353.8 500,353.8"
                   " C 354.7,353.8 236.9,471.6 236.9,616.9 Z"),
    # The toki pona logo: toki with pona's smile inside. Not a UCSUR word,
    # so for now it is only a part (pu's cover, and later a "toki pona" ligature).
    "toki-pona": dict(parts=[("rays", ("fit", (295.38, 120, 704.62, 266.15))),
                             ("head", None),
                             ("closed-mouth", ("fit", (388.92, 564.31, 611.08, 722.15)))]),
    "big-box": dict(ref="poki", d="M 182.4,124.6 L 182.4,875.4 L 817.6,875.4 L 817.6,124.6"),
    "short-box": dict(ref="insa",
                      src=("insa", [0]),
                      d="M 182.4,341.2 L 182.4,629.9 L 817.6,629.9 L 817.6,341.2"),
    "side-box": dict(ref="sinpin", d="M 240.1,124.6 L 413.4,124.6 L 413.4,875.4 L 240.1,875.4"),
    "hammer": dict(ref="ilo",
                   src=("ilo", [0, 1]),
                   d="M 226.4,120 L 773.6,120 L 773.6,454.4 L 226.4,454.4 Z M 500,120 L 500,880"),
    "wave": dict(ref="linja",
                 d="M 120,445.7 C 255.7,554.3 364.3,608.6 500,527.1"
                   " C 635.7,445.7 771.4,364.3 880,554.3"),
    "arrowhead": dict(ref="alasa", src=("alasa", [0]), d="M 700.4,299 L 845.9,444.6 L 700.4,590.2"),
    "sin": dict(ref="sin",
                src=("sin", [0, 1, 2]),
                d="M 500,258.2 L 500,500 M 120,672.7 L 396.4,672.7 M 603.6,672.7 L 880,672.7"),
    "shaft": dict(d="M 500,120 L 500,879.9"),
    "stem": dict(ref="a", src=("a", [0]), d="M 499.6,120 L 499.6,531.9"),
    "tally": dict(ref="wan", src=("tu", [0]), at=(500, 500), d="M 500,120 L 500,880"),
    "big-circle": dict(ref="ijo",
                       src=("ijo", [0]),
                       d="M 120,500 C 120,709.9 290.1,880 500,880 C 709.9,880 880,709.9 880,500"
                         " C 880,290.1 709.9,120 500,120 C 290.1,120 120,290.1 120,500 Z"),
    "small-circle": dict(ref="suno",
                         d="M 266.93,500 C 266.93,628.69 371.31,733.07 500,733.07"
                           " C 628.69,733.07 733.07,628.69 733.07,500"
                           " C 733.07,371.31 628.69,266.93 500,266.93"
                           " C 371.31,266.93 266.93,371.31 266.93,500 Z"),
    # Dots: placed with ("at", (x, y)) and never scaled, so every dot is the
    # same size. In drawn glyphs, link_parts.py swaps your dots for these.
    "dot": dict(ref="",
                black=True,
                d="M 492,500 C 492,504.4 495.6,508 500,508 C 504.4,508 508,504.4 508,500"
                  " C 508,495.6 504.4,492 500,492 C 495.6,492 492,495.6 492,500 Z M 500,500 h 0.1"),
    "big-dot": dict(ref="",
                    black=True,
                    d="M 482,500 C 482,509.9 490.1,518 500,518 C 509.9,518 518,509.9 518,500"
                      " C 518,490.1 509.9,482 500,482 C 490.1,482 482,490.1 482,500 Z M 500,500"
                      " h 0.1"),
}

LINKS = {
    # Legs: tawa is kama mirrored
    "kama": dict(parts=[("legs", ("matrix", (0.9286, 0, 0, 0.9286, 8.5658, 35.7093)))]),
    "tawa": dict(parts=[("legs", ("matrix", (-0.9286, 0, 0, 0.9286, 991.43, 35.7093)))],
                 drop="all"),
    # Emitters
    "kalama": dict(parts=[("rays", ("matrix", (0.9631, 0, 0, 0.9631, 18.471, 19.0738))),
                          ("mouth", ("fit", (208.16, 484.8, 791.84, 886.08)))]),
    "pana": dict(parts=[("rays", ("fit", (317.81, 177.26, 682.19, 333.43))),
                        ("hand", ("matrix", (0.9924, 0, 0, 0.9924, 3.7881, 15.4845)))]),
    "toki": dict(parts=[("rays", ("matrix", (0.6431, 0, 0, 0.6431, 178.4676, 52.6083))),
                        ("head", None)]),
    "kokosila": dict(parts=[("rays", ("matrix", (0.6431, 0, 0, 0.6431, 178.4676, 52.6083))),
                            ("head", None)],
                     own="M 120,792.3 L 880,470.8"),
    "epiku": dict(parts=[("rays", ("fit", (265.51, 117.91, 734.49, 323.08)))],
                  own="M 206.9,440.3 C 206.9,683.1 338.1,880 500,880"
                      " C 661.9,880 793.1,683.1 793.1,440.3"),
    "sona": dict(parts=[("rays", ("matrix", (0.6245, 0, 0, 0.6245, 187.7473, 54.5532))),
                        ("page", ("fit", (301.29, 375.48, 698.71, 914.84)))]),
    # Mouths: loje and moku share the mouth's place
    "uta": dict(parts=[("mouth", ("matrix", (2.4149, 0, 0, 2.4149, -707.4465, -236.878))),
                       ("big-dot", ("at", (500, 826.88)))],
                own=""),
    "loje": dict(parts=[("mouth", ("matrix", (0.9924, 0, 0, 0.9924, 3.7896, 15.4851))),
                        ("small-triangle", ("matrix", (0.9924, 0, 0, 0.9924, 3.7882, 15.4845)))]),
    "moku": dict(parts=[("mouth", ("matrix", (0.9924, 0, 0, 0.9924, 3.7896, 15.4851))),
                        ("hand", ("matrix", (0.9924, 0, 0, 0.9924, 3.7881, 15.4845)))]),
    "pona": dict(parts=[("closed-mouth", None)]),
    "ike": dict(parts=[("closed-mouth", ("matrix", (1, 0, 0, -1, 0.0003, 1000.0016)))], drop="all"),
    # Colour triangles
    "jelo": dict(parts=[("small-triangle", ("matrix", (0.9924, 0, 0, 0.9924, 3.7882, 15.4845)))],
                 own="M 375.1,317.8 C 375.1,386.8 431,442.7 500,442.7"
                     " C 569,442.7 624.9,386.8 624.9,317.8 C 624.9,248.8 569,192.9 500,192.9"
                     " C 431,192.9 375.1,248.8 375.1,317.8 Z M 500,192.9 L 500,120 M 375.1,317.8"
                     " L 302.2,317.8 M 624.9,317.8 L 697.8,317.8 M 500,442.7 L 500,536.4"),
    "laso": dict(parts=[("small-triangle", ("matrix", (0.9924, 0, 0, 0.9924, 3.7882, 15.4845)))],
                 own="M 500,437.5 C 447.9,255.3 291.8,229.3 291.8,333.4"
                     " C 291.8,411.5 421.9,437.5 500,437.5 M 500,437.5"
                     " C 552.1,255.3 708.2,229.3 708.2,333.4 C 708.2,411.5 578.1,437.5 500,437.5"
                     " M 500,437.5 L 500,536.4"),
    "kule": dict(parts=[("big-triangle", None)], own="M 120,515.2 L 880,515.2"),
    "pimeja": dict(parts=[("big-triangle", None)],
                   own="M 317.6,500.6 L 597.3,880 M 682.4,500.6 L 402.7,880"),
    "walo": dict(parts=[("big-triangle", None)],
                 own="M 196,424 L 341.9,454.4 M 804,424 L 658.1,454.4"),
    # Hands: the small hand is a smaller clone of luka, in one place
    "luka": dict(parts=[("luka", None)]),
    "pali": dict(parts=[("hand", ("matrix", (0.9924, 0, 0, 0.9924, 3.7881, 15.4845)))],
                 own="M 369.9,333.4 C 369.9,405.3 428.2,463.6 500,463.6"
                     " C 571.8,463.6 630.1,405.3 630.1,333.4 C 630.1,261.6 571.8,203.3 500,203.3"
                     " C 428.2,203.3 369.9,261.6 369.9,333.4 Z"),
    "kepeken": dict(parts=[("hammer", ("matrix", (0.4757, 0, 0, 0.4757, 262.1776, 95.6015))),
                           ("hand", ("matrix", (0.9924, 0, 0, 0.9924, 3.7881, 15.4845)))]),
    "ilo": dict(parts=[("hammer", None)]),
    # Hearts and sticks
    "pilin": dict(parts=[("heart", None)]),
    "olin": dict(parts=[("heart", ("fit", (315, 120, 685, 490))),
                        ("heart", ("fit", (315, 510, 685, 880)))]),
    # A heart without its point: the arms round off and flow into the stick
    "unpa": dict(parts=[("palisa", ("fit", (427.13, 255.35, 572.88, 880)))],
                 own="M 500,556.3 C 445,556.3 218.8,391.8 218.8,264.7 C 218.8,73.9 375,75 500,249.1"
                     " C 625,75 781.2,73.9 781.2,264.7 C 781.2,391.8 555,556.3 500,556.3"),
    "palisa": dict(parts=[("palisa", None)]),
    # Pointing hands: one hand, flipped and turned
    "mi": dict(parts=[("pointer", None)]),
    "sina": dict(parts=[("pointer", ("matrix", (1, 0, 0, -1, -0.0011, 999.9961)))]),
    "ona": dict(parts=[("pointer", ("matrix", (0, -1, -1, 0, 999.9961, 999.9971)))]),
    # People and animal heads
    "jan": dict(parts=[("person-head", None)]),
    "mije": dict(parts=[("person-head", None)],
                 own="M 173.5,878.3 L 173.5,793.9 L 826.5,793.9 L 826.5,878.3"),
    # Boxes
    "lipu": dict(parts=[("page", None)]),
    "sitelen": dict(parts=[("page", None),
                           ("dot", ("at", (326.65, 500))),
                           ("dot", ("at", (500, 500))),
                           ("dot", ("at", (673.35, 500)))],
                    own=""),
    "pu": dict(parts=[("page", None), ("toki-pona", ("fit", (361.32, 338.2, 638.68, 731.13)))]),
    "ku": dict(parts=[("page", None), ("big-dot", ("at", (586.62, 615.5)))],
               own="M 731,269 L 355.6,413.4 L 442.2,875.4"),
    "poki": dict(parts=[("big-box", None)]),
    "open": dict(parts=[("big-box", None)], own="M 182.4,644.4 L 817.6,644.4"),
    "insa": dict(parts=[("short-box", ("matrix", (1.0006, 0, 0, 1.0006, -0.2786, 14.1641))),
                        ("big-dot", ("at", (500, 442.22)))],
                 own=""),
    "anpa": dict(parts=[("short-box", ("matrix", (1.0006, 0, 0, 1.0006, -0.2802, -40.1511))),
                        ("big-dot", ("at", (500, 731.13)))],
                 drop=[0],
                 own=""),
    "poka": dict(parts=[("short-box", ("matrix", (1.0006, 0, 0, 1.0006, -62.4736, 14.165))),
                        ("big-dot", ("at", (861.93, 471.11)))],
                 own=""),
    "sinpin": dict(parts=[("side-box", None), ("big-dot", ("at", (644.46, 500)))], own=""),
    "monsi": dict(parts=[("side-box", ("matrix", (-1.0006, 0, 0, 1.0006, 1000.2772, -0.2784))),
                         ("big-dot", ("at", (355.54, 500)))],
                  own=""),
    # Waves
    "linja": dict(parts=[("wave", None)]),
    "telo": dict(parts=[("wave", ("stretch", (120, 207.69, 880, 441.54), "flipy")),
                        ("wave", ("stretch", (120, 558.46, 880, 792.3), "flipy"))]),
    "kon": dict(parts=[("wave", ("stretch", (236.92, 120, 412.31, 880), "rot90")),
                       ("wave", ("stretch", (558.46, 120, 733.85, 880), "rot90"))]),
    # Arrows
    "alasa": dict(parts=[("arrowhead", ("matrix", (0.6525, 0, 0, 0.6525, 328.0008, 209.9059)))],
                  own="M 151.7,500 L 880,500 M 373.3,120 C 753.3,183.3 753.3,816.7 373.3,880 Z"),
    "ni": dict(parts=[("shaft", None),
                      ("arrowhead", ("matrix", (0, 0.5593, -0.5593, 0, 748.6481, 391.1126)))]),
    "nasin": dict(parts=[("shaft", None),
                         ("arrowhead", ("matrix", (0, -0.5593, 0.5593, 0, 251.3475, 907.4532)))]),
    "tan": dict(parts=[("arrowhead", ("matrix", (0, 0.9966, -0.9966, 0, 708.1286, -116.7638)))],
                own="M 880,705 C 880,397.5 743.4,295 572.5,295 C 401.7,295 265.1,397.5 265.1,705"),
    # Rays
    "sin": dict(parts=[("sin", None)]),
    "namako": dict(parts=[("sin", ("fit", (151.58, 120, 848.42, 500)))],
                   own="M 500,657.9 L 500,880"),
    # Punctuation stems
    "a": dict(parts=[("stem", ("matrix", (1.0934, 0, 0, 1.0934, -46.2993, -11.2072)))],
              own="M 545,778.7 C 545,711.1 432.4,699.9 432.4,778.7"
                  " C 432.4,857.5 545,846.2 545,778.7 L 584.4,851.9"),
    "o": dict(parts=[("stem", ("matrix", (1.0934, 0, 0, 1.0934, -46.2993, -11.2072)))],
              own="M 415.6,784.3 C 415.6,830.9 453.4,868.7 500,868.7"
                  " C 546.6,868.7 584.4,830.9 584.4,784.3 C 584.4,737.7 546.6,699.9 500,699.9"
                  " C 453.4,699.9 415.6,737.7 415.6,784.3 Z"),
    "kin": dict(parts=[("stem", None)],
                own="M 416.8,796.8 L 583.2,796.8 M 457.8,724.7 L 542.2,868.9 M 542.2,724.7"
                    " L 457.8,868.9"),
    "n": dict(parts=[("stem", ("matrix", (1.0934, 0, 0, 1.0934, -46.2993, -11.2072)))],
              own="M 359.3,880 L 359.3,739.3 C 359.3,654.8 415.6,626.7 471.9,626.7"
                  " C 556.3,626.7 612.6,683 612.6,739.3 L 612.6,880"),
    # Tally marks, all in the same places
    "wan": dict(parts=[("tally", None)], own="M 341.7,278.3 L 500,120"),
    "tu": dict(parts=[("tally", ("matrix", (1, 0, 0, 1, -126.667, 0))),
                      ("tally", ("matrix", (1, 0, 0, 1, 126.667, 0)))],
               drop="all"),
    "mute": dict(parts=[("tally", ("matrix", (1, 0, 0, 1, -190.0005, 0))),
                        ("tally", None),
                        ("tally", ("matrix", (1, 0, 0, 1, 190.0005, 0)))]),
    "nanpa": dict(parts=[("tally", ("matrix", (1, 0, 0, 1, -158.3338, 0))),
                         ("tally", ("matrix", (1, 0, 0, 1, 158.3337, 0))),
                         ("tally", ("matrix", (0, 1, -1, 0, 1000.004, -158.3338))),
                         ("tally", ("matrix", (0, 1, -1, 0, 1000.004, 158.3337)))]),
    # Big circles
    "ijo": dict(parts=[("big-circle", None)]),
    "moli": dict(parts=[("big-circle", None)],
                 own="M 278.3,373.3 L 436.7,626.7 M 436.7,373.3 L 278.3,626.7 M 563.3,373.3"
                     " L 721.7,626.7 M 721.7,373.3 L 563.3,626.7"),
    "ma": dict(parts=[("big-circle", None)], own="M 500,120 L 500,880 M 120,500 L 880,500"),
    "tenpo": dict(parts=[("big-circle", None)], own="M 500,246.7 L 500,500 L 626.7,500"),
    "sike": dict(parts=[("big-circle", None), ("big-circle", ("fit", (310, 310, 690, 690)))]),
    # Small circles: the sun and tonsi's head
    "suno": dict(parts=[("small-circle", None)],
                 own="M 500,120 L 500,266.93 M 500,733.07 L 500,880 M 120,500 L 266.93,500"
                     " M 733.07,500 L 880,500"),
    "tonsi": dict(parts=[("small-circle", ("move", (500, 411.33)))],
                  own="M 323.17,259.54 L 160.53,120 M 676.83,259.54 L 839.47,120 M 500,644.4 L 500,880"),
    "mu": dict(parts=[("person-head", ("fit", (180.37, 240.75, 819.63, 880))),
                      ("big-dot", ("at", (500, 666.91)))],
               own="M 201.7,205.2 C 201.7,252.3 239.9,290.5 286.9,290.5"
                   " C 333.9,290.5 372.1,252.3 372.1,205.2 C 372.1,158.2 333.9,120 286.9,120"
                   " C 239.9,120 201.7,158.2 201.7,205.2 Z M 627.9,205.2"
                   " C 627.9,252.3 666.1,290.5 713.1,290.5 C 760.1,290.5 798.3,252.3 798.3,205.2"
                   " C 798.3,158.2 760.1,120 713.1,120 C 666.1,120 627.9,158.2 627.9,205.2 Z"),
    "mani": dict(parts=[("person-head", ("fit", (202.61, 285.22, 797.39, 880)))],
                 own="M 289.8,372.5 C 202.6,318.3 136.5,219.1 136.5,120 M 710.2,372.5"
                     " C 797.4,318.3 863.5,219.1 863.5,120"),
    "akesi": dict(parts=[("dot", ("at", (409.76, 128.02))), ("dot", ("at", (590.24, 128.02)))],
                  own="M 379.7,549.1 C 379.7,731.9 433.6,880 500,880"
                      " C 566.4,880 620.3,731.9 620.3,549.1 C 620.3,366.4 566.4,218.3 500,218.3"
                      " C 433.6,218.3 379.7,366.4 379.7,549.1 Z M 259.4,368.7 L 740.6,368.7"
                      " M 259.4,549.1 L 740.6,549.1 M 259.4,729.6 L 740.6,729.6"),
    "lon": dict(parts=[("big-dot", ("at", (500, 383.08)))], own="M 120,587.7 L 880,587.7"),
    "lukin": dict(parts=[("big-dot", ("at", (500, 500)))],
                  own="M 120,500 C 120,597.3 290.1,652 500,652 C 709.9,652 880,597.3 880,500"
                      " C 880,402.7 709.9,348 500,348 C 290.1,348 120,402.7 120,500 Z"),
    "pipi": dict(parts=[("dot", ("at", (413.23, 128.01))), ("dot", ("at", (586.77, 128.01)))],
                 own="M 500,243.7 L 500,880 M 355.4,359.4 L 644.6,359.4 M 355.4,561.9"
                     " L 644.6,561.9 M 355.4,735.4 L 644.6,735.4"),
    "seli": dict(parts=[("big-dot", ("at", (500, 861.93)))],
                 own="M 500,120 L 500,690.7 M 271.7,291.2 L 385.9,633.6 M 728.3,291.2 L 614.1,633.6"),
    "seme": dict(parts=[("big-dot", ("at", (500, 861.96)))],
                 own="M 307.6,284.9 C 307.6,147.5 445,120 527.5,120"
                     " C 664.9,120 719.8,229.9 692.4,312.4 C 664.9,422.3 500,477.2 500,669.6"),
    "soweli": dict(parts=[("dot", ("at", (677.07, 322.92)))],
                   own="M 316.6,159.1 L 611.5,159.1 C 808.1,159.1 906.5,257.4 873.7,355.7"
                       " C 840.9,421.2 742.6,454 611.5,421.2 C 578.8,421.2 578.8,454 578.8,486.8"
                       " L 578.8,880 M 120,617.8 L 120,880 M 251.1,617.8 L 251.1,880"
                       " M 414.9,617.8 L 414.9,880"),
    "suwi": dict(parts=[("big-dot", ("at", (500, 733.85)))],
                 own="M 120,529.2 L 236.9,295.4 L 353.8,529.2 M 646.2,529.2 L 763.1,295.4"
                     " L 880,529.2"),
    "waso": dict(parts=[("dot", ("at", (475.45, 482.47))), ("dot", ("at", (394.77, 482.47)))],
                 own="M 324.6,120 L 704.6,616.9 L 383.1,616.9 L 383.1,880"),
    "kipisi": dict(parts=[("big-dot", ("at", (223.64, 189.09))), ("big-dot", ("at", (776.36, 810.91)))],
                   own="M 154.5,880 L 845.5,120"),
    "kijetesantakalu": dict(parts=[("dot", ("at", (598.52, 418.94))),
                                   ("dot", ("at", (682.97, 418.94)))],
                            own="M 373.3,837.8 L 373.3,303 C 457.8,190.4 626.7,190.4 739.3,303"
                                " L 880,443.7 L 739.3,500 L 739.3,837.8 M 514.1,556.3"
                                " L 514.1,837.8 M 626.7,556.3 L 626.7,837.8 M 373.3,584.4"
                                " L 204.4,584.4 C 148.1,584.4 120,640.7 120,710.6"
                                " C 120,781.5 148.1,837.8 204.4,837.8 L 373.3,837.8 M 260.7,584.4"
                                " L 260.7,837.8"),
    "meso": dict(parts=[("dot", ("at", (500, 500)))],
                 own="M 266.2,120 L 266.2,880 M 733.8,120 L 733.8,880"),
    "lanpan": dict(parts=[("big-dot", ("at", (682.4, 849.6)))],
                   own="M 317.6,302.4 C 317.6,403.1 399.3,484.8 500,484.8"
                       " C 600.7,484.8 682.4,403.1 682.4,302.4 C 682.4,201.7 600.7,120 500,120"
                       " C 399.3,120 317.6,201.7 317.6,302.4 Z M 378.4,454.4"
                       " C 165.6,545.6 104.8,758.4 196,849.6"
                       " C 287.2,940.8 439.2,758.4 621.6,697.6"
                       " C 773.6,636.8 864.8,758.4 864.8,880"),
}


def _fit_to_guides():
    """The shapes and places above were drawn with centrelines at DESIGN_INSET
    (120-880); scale them about the cell centre onto the current guides.
    Dots keep their size: only where they go changes."""
    k = guide_scale()
    t = CELL / 2 * (1 - k)
    scale, unscale = (k, 0, 0, k, t, t), (1 / k, 0, 0, 1 / k, -t / k, -t / k)
    pts = lambda v: tuple(round(t + x * k, 2) for x in v)

    def place(p):
        if p is None:
            return None
        kind, v, *rest = p
        if kind == "matrix":
            v = tuple(round(x, 4) for x in multiply(scale, multiply(v, unscale)))
        return (kind, pts(v), *rest) if kind != "matrix" else (kind, v, *rest)

    for name, spec in PARTS.items():
        if name not in ("dot", "big-dot") and "d" in spec:
            spec["d"] = scale_d(spec["d"], k)
        for key in ("fit", "at"):
            if key in spec:
                spec[key] = pts(spec[key])
        if "parts" in spec:
            spec["parts"] = [(part, place(p)) for part, p in spec["parts"]]
    for spec in LINKS.values():
        if spec.get("own"):
            spec["own"] = scale_d(spec["own"], k)
        spec["parts"] = [(part, place(p)) for part, p in spec["parts"]]


_fit_to_guides()
