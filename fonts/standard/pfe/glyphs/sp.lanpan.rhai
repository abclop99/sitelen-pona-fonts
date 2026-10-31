// sp.lanpan
glyph("sp.lanpan", 0xF1985);

draw(big_dot(), tf(1, 0, 0, 1, 180, -345));
stroke(
       path(pt(270, 595))
       .curve(pt(450, 415))
       .curve(pt(630, 595))
       .curve(pt(450, 775))
       .cycle()
);
stroke(
       path(pt(330, 450)).dir(200)
       .curve(pt(150, 57))
       .curve(pt(620, 215))
       .curve(pt(810, 25))
);
