// sp.monsuta.
glyph("sp.monsuta", 0xF197D);

const GLYPH_HEIGHT = 800;  // ink box height (params.ink_t)
const GLYPH_WIDTH = 900;   // advance width (the ink box runs from 50 to 850)
const MARGIN_LR = 50;      // side bearing to the ink box (params.ink_l)
const STROKE_RADIUS = 25;  // half the pen, so the ink (not the centreline) meets the box
const EASE = -0.2;         // tooth spacing: < 0 wider in the middle, > 0 tighter, 0 even; keep within -0.5..1

/// Height of the zigzag's envelope at `x_frac` (0 to 1 across the glyph),
/// as a fraction of half the glyph height: a parabola that is 0.5 in the
/// middle and 0 at both edges, so the middle tip sits 200 units from the midline.
fn outline(x_frac) {
       0.5 - 2 * (x_frac - 0.5) ** 2
}

/// Maps 0..1 to 0..1, keeping 0, 0.5 and 1 fixed. `a = 0` is linear;
/// `a > 0` bunches points toward the middle, `a < 0` toward the ends.
/// Keep `a` within -0.5..1.
fn ease_mid(t, a) {
       (1.0 - a) * t + a * (4.0 * (t - 0.5) ** 3 + 0.5)
}

/// The `i`th of `segments + 1` zigzag points, left to right. Even points are
/// mirrored about the middle of the glyph, so the line alternates up and down.
/// `x` is spaced by `ease_mid` with `EASE`, so the teeth are wider in the middle
/// than at the ends.
fn points(i, segments) {
       const MARGIN = global::MARGIN_LR + global::STROKE_RADIUS;

       let line_frac = i / segments;
       let x = lerp(
              MARGIN,
              global::GLYPH_WIDTH - MARGIN,
              ease_mid(line_frac, global::EASE),
       );

       let glyph_frac = x / global::GLYPH_WIDTH;

       let y = 0.5 * global::GLYPH_HEIGHT +
              outline(glyph_frac) * global::GLYPH_HEIGHT * 0.5;

       if i % 2 == 0 {
              point(x, global::GLYPH_HEIGHT - y)
       } else {
              point(x, y)
       }
}

const N = 8; // Number of segments

let steps = [from(points(0, N))];
for i in 1..=N { steps.push(line().to(points(i, N))); }
stroke(path(steps));
