# sitelen-pona-fonts

Three related sitelen pona fonts that share one encoding, so the same text works in all of them (minus features a font doesn't have).

| Folder | Font | Style |
|---|---|---|
| `fonts/handwriting/` | *(name TBD)* | Semi-cursive script based on how sitelen pona could be handwritten at speed. Line style undecided |
| `fonts/standard/` | *(name TBD)* | Normal sitelen pona close to the *pu* forms, with clean, even monoline strokes, plus added features: automatic combinations (stacked, side by side, inside) and designed combos such as a walking-house *tomo tawa* |
| `fonts/display/` | *(name TBD)* | Display / formal script with unified styling, loosely inspired by seal script. Probably monospace, with nested combinations |

## Layout

```
spec/        shared encoding (words.tsv), asuki input syntax, combo list, mirroring tiers
docs/        feasibility write-up, design decisions, notes
reference/   links and notes; downloaded reference fonts (git-ignored)
fonts/*/     per-font sources
```

The standard font is written as code for [pfe](https://github.com/abclop99/parametric-font-engine), a parametric font engine: `fonts/standard/pfe/` holds `font.toml` (font info, parameters, where the word list is), `font.rhai` (metrics, spacing, preview guides, and each word's class and expected code from `spec/words.tsv`), shared parts in `lib/` and one script per word. It needs pfe 0.4. With `pfe` installed:

```
pfe preview fonts/standard/pfe   # live preview in the browser
pfe build fonts/standard/pfe     # UFO + TTF in fonts/standard/pfe/build/
```

or open the folder in VS Code with the pfe extension for diagnostics and a preview that follows the cursor.

## Status

The standard font has all 137 words (*nimi pu* and *ku suli*), imported from earlier drawings and now being rewritten as parametric code. Next: typing features (ASCII input, cartouches, long *pi*), then combos. Background: [docs/custom-font-feasibility.md](docs/custom-font-feasibility.md) and [spec/README.md](spec/README.md).

## Licenses

- Fonts and glyph sources: [SIL Open Font License 1.1](OFL.txt)
- The standard font's glyph forms follow jan Sonja's (Sonja Lang's) handwriting in *Toki Pona: The Language of Good* (*pu*). Many were traced, then adjusted, from the vectorizations on Wikimedia Commons ("&lt;Word&gt; - sitelen pona in Sonja Lang's handwriting.svg", by LiliCharlie and Sonja Lang), which are dedicated to the public domain (CC0). See the [comparison page](https://sona.pona.la/wiki/Comparison_of_jan_Sonja%27s_handwriting_and_linja_pona) on sona pona.
- Some *ku suli* glyphs (words with no drawing in *pu*) are traced from sitelen seli kiwen (Copyright (c) 2022 Kreative Software, OFL 1.1), so its copyright line is in [OFL.txt](OFL.txt) and in the font.
- Scripts or tooling added to this repo (none yet; the font is built with pfe, which has its own repo): [MIT](LICENSE-MIT.txt)
- If a font copies glyphs or feature code from another OFL font (for example sitelen seli kiwen), add that font's copyright line to its license notice, as OFL condition 2 requires.
- `reference/sitelen-seli-kiwen/` (README and license only; see [reference/README.md](reference/README.md) for the font files): by Kreative Software (jan Lepeka), OFL 1.1, see its own [OFL.txt](reference/sitelen-seli-kiwen/OFL.txt)
