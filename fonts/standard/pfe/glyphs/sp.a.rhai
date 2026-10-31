// sp.a
glyph("sp.a", 0xF1900);

draw(stem(), tf(1, 0, 0, 1, 0, 0));

let a_line_start = pt(579, 25);
let a_line_end = pt(461, 199);
let a_curve_end = lerp(a_line_start, a_line_end, 0.7);

stroke(
       path(a_line_start)
       .line(a_line_end)
       .curve(pt(350, 164))
       .curve(pt(359, 35))
       .curve(a_curve_end, dir(60))
);
