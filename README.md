# sitelen-pona-fonts

Three related sitelen pona fonts that share one encoding, so the same text works in all of them (minus features a font doesn't have).

| Folder | Font | Style |
|---|---|---|
| `fonts/handwriting/` | *(name TBD)* | Semi-cursive script based on how sitelen pona could be handwritten at speed. Line style undecided |
| `fonts/combos/` | *(name TBD)* | Normal sitelen pona with added features: more automatic combinations (stacked, side by side, inside) and designed combos such as a walking-house *tomo tawa*. Could start as a modification of an existing open-licensed font |
| `fonts/display/` | *(name TBD)* | Display / formal script with unified styling, loosely inspired by seal script. Probably monospace, with nested combinations |

## Layout

```
spec/        shared encoding, asuki input syntax, combo list, mirroring tiers
docs/        feasibility write-up and design decisions
reference/   links and notes; downloaded reference fonts (git-ignored)
build/       build scripts (glyph SVGs + features -> TTF/WOFF2)
fonts/*/     per-font glyph sources and features
test/        HTML test page
```

## Status

Planning. Start with [docs/custom-font-feasibility.md](docs/custom-font-feasibility.md) and [spec/README.md](spec/README.md).

## Licenses

- Fonts and glyph sources: [SIL Open Font License 1.1](OFL.txt)
- Build scripts and tooling: [MIT](LICENSE-MIT.txt)
- If a font copies glyphs or feature code from another OFL font (for example sitelen seli kiwen), add that font's copyright line to its license notice, as OFL condition 2 requires.
- `reference/sitelen-seli-kiwen/` (README and license only; see [reference/README.md](reference/README.md) for the font files): by Kreative Software (jan Lepeka), OFL 1.1, see its own [OFL.txt](reference/sitelen-seli-kiwen/OFL.txt)
