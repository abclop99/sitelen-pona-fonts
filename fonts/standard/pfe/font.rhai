// Font-wide choices, as hooks: functions with names pfe knows. Helpers go in lib/.

// Every glyph is a cell wide.
fn default_spacing(g) { cell() }

// 100 above and below the ink box, and the line gap of the Inkscape build.
fn metrics() { #{ ascender: params.ink_t + 100, descender: params.ink_b - 100, line_gap: 200 } }

// The preview's guides: the midline and the ink box.
fn guides(g) {
    [guide::horizontal(mid()), guide::horizontal(params.ink_b), guide::horizontal(params.ink_t),
     guide::vertical(params.ink_l), guide::vertical(params.ink_r)]
}

// The class typing rules use, and each word's code from the word list. The glyph scripts still
// give their own codes, which win, so for now this checks them against the list (a mismatch is a
// code_not_default warning); a word with no code point yet gets none.
fn glyph_defaults() {
    let out = #{};
    for w in data::words {
        out[`sp.${w.word}`] = #{ code: w.codepoint, classes: ["word"] };
    }
    out
}
