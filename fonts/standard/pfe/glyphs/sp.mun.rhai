// sp.mun
glyph("sp.mun", 0xF193A);

// Glyph height: Should be a shared parameter
const GLYPH_HEIGHT = 800;

let point_top = pt(200, 725);
let point_low = pt(point_top.x, GLYPH_HEIGHT - point_top.y);
let outer = pt(750, 400);
let inner = pt(500, 400);

stroke(
       path(point_top).corner()
       .curve(inner)
       .curve(point_low).corner()
       .curve(outer)
       .cycle()
);
