// sp.ale
glyph("sp.ale", 0xF1904);

const STROKE_RADIUS = 0.5 * params.stroke;

let b = box();
let middle = pt(b.left + b.width / 2, mid());
let left = pt(b.left + STROKE_RADIUS, middle.y);
let right = pt(b.right - STROKE_RADIUS, middle.y);

stroke(
       path(middle)
       .curve(left, DOWN) // TODO: Make fatter, with a param for how fat (for stretch)
       .curve(middle)
       .curve(right, DOWN) // TODO: Make fatter
       .cycle()
);
