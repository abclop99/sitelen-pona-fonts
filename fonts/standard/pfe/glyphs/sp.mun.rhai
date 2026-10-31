// sp.mun
glyph("sp.mun", 0xF193A);

let point_top = pt(200, mid() + 331);                        // the ink just meets the box
let point_low = pt(point_top.x, 2 * mid() - point_top.y);   // mirrored about the midline
let outer = pt(750, mid());
let inner = pt(500, mid());

stroke(
       path(point_top).corner()
       .curve(inner)
       .curve(point_low).corner()
       .curve(outer)
       .cycle()
);
