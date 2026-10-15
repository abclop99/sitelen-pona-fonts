# Drawing glyphs

Each word has its own SVG in `fonts/<font>/glyphs/`, for example `fonts/standard/glyphs/toki.svg`. Open it in Inkscape, draw, save, and run the build.

## What's in a template

| Layer | What it's for |
|---|---|
| `reference` | Locked and faint: jan Sonja's drawing of the word from *pu* (the official forms), to follow or ignore |
| `guides` | Locked: the ink box (solid red), the box for centrelines (dashed), the midline (blue) and the word's name |
| `glyph` | **Draw here.** Open paths along the centre of each stroke |
| `fill` | Optional: shapes that should be filled as drawn instead of stroked |

The solid red square is where the ink should end up. Keep centrelines inside the dashed square, which is inset by half a stroke, so the stroked result lands on the solid one.

## How to draw

- **Draw centrelines, not outlines.** One path down the middle of each stroke. The build gives every path the same stroke weight (`STROKE` in `build/common.py`, 70 units) with round ends and joins, whatever stroke width the path has in Inkscape.
- **Build from simple pieces.** Use the Bezier pen (`B`) for lines and curves, the ellipse tool (`E`) for circles, and the rectangle tool (`R`) for boxes. With snapping on, points land on the 25-unit grid, which keeps sizes and curves consistent across words.
- **Preview the real weight.** Give your paths `stroke-width: 70`, round caps and round joins, and no fill (Fill and Stroke, `Ctrl+Shift+F`). Inkscape remembers the last style per tool, so you only set it once.
- **Dots** are a path with a single tiny segment; the round caps turn it into a dot.
- **Filled areas** (if a glyph has any) go in the `fill` layer and are filled exactly as drawn.
- **The midline matters.** Sitelen pona centres on the midline, not a baseline, so keep each glyph visually centred on the blue line unless it is meant to sit high or low.
- Anything hidden, and anything outside the `glyph` and `fill` layers, is ignored.

## Words that need a different drawing in monospace

The monospace build puts every glyph in a full-width cell. If a word looks wrong there (for example a narrow *seme* that looks lost, or a wide glyph that looks cramped), copy `seme.svg` to `seme.mono.svg` and change the copy. The monospace build uses `.mono.svg` when it exists; the proportional build always uses the plain file.

## Building and testing

You need Python 3 with two libraries, installed once:

```
python3 -m pip install -r build/requirements.txt
python3 build/build.py --font standard
```

This writes `dist/standard/` with a monospace and a proportional font (`.ttf` and `.woff2`) and `test.html`. Open `test.html` in a browser to type toki pona and see it in both builds, plus a grid of every word. Words that aren't drawn yet show as their Latin name in a dashed box.

Every push also builds the fonts on GitHub. The **Build fonts** run on the Actions tab has a `fonts` download with the same files, so you can check a build without installing anything.

## Getting the reference drawings

The reference layer links to `reference/pu/downloads/<word>.svg`: jan Sonja's handwritten forms from *pu*, as hosted on Wikimedia Commons. They are linked rather than copied into the repo, so they need downloading once (git ignores the folder):

```
python3 build/fetch_pu_reference.py
```

If Commons is unreachable, save the sona pona page "Comparison of Madame Lang's handwriting and linja pona" as `.mhtml` after scrolling to the bottom (so every image has loaded), then run `python3 build/fetch_pu_reference.py --from-mhtml page.mhtml`.

The *ku suli* words (*kin, namako, oko, …*) have no drawing in *pu*, so their reference comes from a font instead (sitelen seli kiwen, OFL, shown in blue). Rerunning only rewrites the `reference` and `guides` layers, never `glyph` or `fill`:

```
python3 build/make_templates.py --font standard --reference reference/sitelen-seli-kiwen/downloads/sitelenselikiwenjuniko.ttf
```
