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

// Each word's code and the class typing rules use, from the word list. A word with no code
// point yet is left unencoded.
fn glyph_defaults() {
    let out = #{};
    for w in data::words {
        out[`sp.${w.word}`] = if w.codepoint != "" { #{ code: w.codepoint, classes: ["word"] } } else { #{ classes: ["word"] } };
    }
    out
}
