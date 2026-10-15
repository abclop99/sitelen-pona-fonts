# sitelen-pona-fonts

Three related sitelen pona fonts that share one encoding, so the same text works in all of them (minus features a font doesn't have).

| Folder | Font | Style |
|---|---|---|
| `fonts/handwriting/` | *(name TBD)* | Semi-cursive script based on how sitelen pona could be handwritten at speed. Line style undecided |
| `fonts/combos/` | *(name TBD)* | Normal sitelen pona with added features: more automatic combinations (stacked, side by side, inside) and designed combos such as a walking-house *tomo tawa*. Could start as a modification of an existing open-licensed font |
| `fonts/display/` | *(name TBD)* | Display / formal script with unified styling, loosely inspired by seal script. Probably monospace, with nested combinations |

## Layout

```
spec/        shared encoding, word list (words.tsv), asuki syntax, combo list, mirroring
docs/        feasibility write-up and design decisions
reference/   links and notes; downloaded reference fonts (git-ignored)
build/       make_templates.py (Inkscape templates), build.py (SVGs -> TTF/WOFF2 + test page)
fonts/*/     per-font glyph sources and features
test/        test page template (the build writes dist/<font>/test.html)
```

## Status

Working on the first font: a clean, standard-looking font in `fonts/combos/` (monospace or proportional still undecided; the build makes both). It becomes the base of the combos font.

1. Templates and build pipeline. **Done:** see [docs/drawing-glyphs.md](docs/drawing-glyphs.md).
2. Draw the words, about 20 common ones first, then the rest of the 137.
3. Typing features: ASCII input, cartouches, long *pi*.
4. Combos: automatic stacking and side by side, then designed combos like walking-house *tomo tawa*.

Alongside, handwriting shortcuts collect in [docs/handwriting-shortcuts.md](docs/handwriting-shortcuts.md) for the handwriting font later. Background: [docs/custom-font-feasibility.md](docs/custom-font-feasibility.md) and [spec/README.md](spec/README.md).

## Licenses

- Fonts and glyph sources: [SIL Open Font License 1.1](OFL.txt)
- Build scripts and tooling: [MIT](LICENSE-MIT.txt)
- The templates' reference layer for the *ku suli* words contains outlines from sitelen seli kiwen (Copyright Kreative Software, OFL 1.1). It is a tracing guide only and never reaches a built font.
- If a font copies glyphs or feature code from another OFL font (for example sitelen seli kiwen), add that font's copyright line to its license notice, as OFL condition 2 requires.
- `reference/sitelen-seli-kiwen/` (README and license only; see [reference/README.md](reference/README.md) for the font files): by Kreative Software (jan Lepeka), OFL 1.1, see its own [OFL.txt](reference/sitelen-seli-kiwen/OFL.txt)
