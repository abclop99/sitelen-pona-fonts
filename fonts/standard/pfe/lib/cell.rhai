// The cell every glyph sits in: the ink box, with a margin on either side.

// The advance: the ink box plus both margins.
fn advance() { params.margin_l + params.box_w + params.margin_r }

// The ink box: its edges and size, as a map (`box().left`, `box().width`).
fn box() {
    let l = params.margin_l;
    let b = params.box_b;
    #{
        left: l,
        right: l + params.box_w,
        bottom: b,
        top: b + params.box_h,
        width: params.box_w,
        height: params.box_h
    }
}

// sitelen pona centres on the midline, the middle of the ink box.
fn mid() { params.box_b + params.box_h / 2 }
