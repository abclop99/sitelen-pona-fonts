// Placing shared parts. Each part function returns its paths in its own page's coordinates;
// these draw them moved, scaled or mirrored by a transform. Strokes are applied after the
// transform, so a scaled part keeps the same line weight.

fn draw(paths, t) {
    for q in paths {
        stroke(q.transform(t));
    }
}

fn draw_fill(paths, t) {
    for q in paths {
        let shape = if q.closed { q } else { q.close() };
        fill(shape.transform(t));
    }
}

fn place(paths, t) {
    paths.map(|q| q.transform(t))
}
