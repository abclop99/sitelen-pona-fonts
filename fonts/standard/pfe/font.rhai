// Font-wide choices, as hooks: functions with names pfe knows. Helpers go in lib/.

// Every glyph is a cell wide.
fn default_spacing(g) { advance() }

// 100 above and below the ink box, and the line gap of the Inkscape build.
fn metrics() { #{ ascender: box().top + 100, descender: box().bottom - 100, line_gap: 200 } }

// The preview's guides: the midline and the ink box.
fn guides(g) {
    let b = box();
    [guide::horizontal(mid()), guide::horizontal(b.bottom), guide::horizontal(b.top),
     guide::vertical(b.left), guide::vertical(b.right)]
}

// The class for typing rules to use (none yet), and each word's code from the word list. The glyph
// scripts still give their own codes, which win, so for now this checks them against the list (a
// mismatch is a code_not_default warning); a word with no code point yet gets none.
fn glyph_defaults() {
    let out = #{};
    for w in data::words {
        out[`sp.${w.word}`] = #{ code: w.codepoint, classes: ["word"] };
    }
    out
}
