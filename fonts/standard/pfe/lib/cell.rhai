// The cell every glyph sits in, and its midline.

// The advance: the ink box centred in the cell, with ink_l on either side.
fn cell() { params.ink_l + params.ink_r }

// sitelen pona centres on the midline, the middle of the ink box.
fn mid() { (params.ink_b + params.ink_t) / 2 }
