// sp.monsuta
glyph("sp.monsuta", 0xF197D);

const BOX = box();                          // the ink box
const GLYPH_WIDTH = advance();              // advance width
const STROKE_RADIUS = 0.5 * params.stroke;  // half the pen, so the ink (not the centreline) meets the box
const EASE = -0.2;         // tooth spacing: < 0 wider in the middle, > 0 tighter, 0 even; keep within -0.5..1

/// Height of the zigzag's envelope at `x_frac` (0 to 1 across an advance-wide
/// span centred on the ink box), as a fraction of half the box height: a
/// parabola that is 0.5 in the middle, so the middle tip sits a quarter of the
/// box height from the midline, and 0 at the span's edges. The path ends at the
/// ink box, inside those, so its end points sit a little off the midline.
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
       let line_frac = i / segments;
       let x = lerp(
              global::BOX.left + global::STROKE_RADIUS,
              global::BOX.right - global::STROKE_RADIUS,
              ease_mid(line_frac, global::EASE),
       );

       // How far the box's middle sits from the advance's (0 with equal margins).
       let shift = (global::BOX.left + global::BOX.right) / 2 - global::GLYPH_WIDTH / 2;
       let glyph_frac = (x - shift) / global::GLYPH_WIDTH;

       let y = mid() +
              outline(glyph_frac) * global::BOX.height * 0.5;

       if i % 2 == 0 {
              point(x, 2 * mid() - y)
       } else {
              point(x, y)
       }
}

const N = 8; // Number of segments

let steps = [from(points(0, N))];
for i in 1..=N { steps.push(line().to(points(i, N))); }
stroke(path(steps));
