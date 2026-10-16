# Drawing glyphs

A whole font is one Inkscape file, `fonts/<font>/glyphs.svg`, with one page per word (Inkscape 1.2 or newer). Open it, draw, save, and run the build.

## What's in the file

The first page, **parts**, is for shared pieces. Then come the words, in the order of `spec/words.tsv`, twelve to a row; each page is named after its word (Inkscape's Pages panel lists them).

| Layer | What it's for |
|---|---|
| `reference` | Locked and faint: jan Sonja's drawing of each word from *pu* (the official forms), to follow or ignore |
| `guides` | Locked: each page's ink box (solid red), the box for centrelines (dashed), the midline (blue) and the word's name |
| `drafts` | Geometric first drafts of every word (purple), from `build/drafts.py`. The build uses a word's draft until you draw that word in `glyph` or `fill` |
| `parts` | Shared pieces, drawn on the parts page: a head, an eye, an arrow… They never go into the font themselves |
| `glyph` | **Draw here.** Open paths along the centre of each stroke. It has one sub-layer per page, named after the word and shifted onto that page, so coordinates inside it run from 0 to 1000 with (500, 500) at the page centre. Pick the word's sub-layer before drawing (clicking a shape already in it does this too). A piece belongs to the page its centre is on, whichever sub-layer it is in |
| `fill` | Optional: shapes that should be filled as drawn instead of stroked |

The solid red square is where the ink should end up. Keep centrelines inside the dashed square, which is inset by half a stroke, so the stroked result lands on the solid one.

## Drafts

Every word starts with a geometric draft made of straight lines, circles and arcs, so the font is complete from the start. A draft is used only while the word's page has nothing in the `glyph` and `fill` layers. To make a word your own, either edit its draft in place (it's in the `drafts` layer), or draw it in `glyph` and delete the draft so the two don't overlap on screen. The test page marks words that are still drafts with a dashed border.

## Shared parts

Shapes that several words share, such as the three rays of *toki*, *sona*, *pana* and *kalama*, the mouth of *uta*, *loje* and *moku*, or the tally marks, are drawn once and cloned. `build/parts.py` lists every part and where each word places it, and `python3 build/link_parts.py --font standard` sets them up: each part gets its own page at the end of the file (`part-rays`, `part-mouth`, …) with its original in the `parts` layer, and each word that uses it gets clones in place of those strokes.

- **To change a part, edit the original on its part page.** Every clone follows, in the same place relative to its page. A part taken from one of your drawings starts black; one from a draft starts purple.
- **Don't move the clones.** Where each clone sits is set in `parts.py`, and running `link_parts.py` again puts any clone that was dragged back in its place. To place a part differently in one word, change that word's entry in `parts.py`.
- **Keep Inkscape's clone setting at its default:** Preferences ▸ Behavior ▸ Clones ▸ "When the original moves" ▸ *Move in parallel*.
- A draft that is made only of parts counts as drawn once all of its parts are black. A draft with its own strokes counts as drawn when those are recoloured too.
- The small hand (`part-hand`) is a clone of `part-luka`: reshape *luka* on its page, and move, scale or squash the small hand by selecting the clone on `part-hand` (the clones in *pali*, *moku* and the rest follow it).
- Each part page shows a word's reference behind the part (its `ref` in `parts.py`, such as *kama* for the legs), lined up the way that word uses it. A purple part is redrawn from `parts.py` when its shape there changes; a black one is yours and is left alone.
- *toki-pona*, the toki pona logo, is a part made of other parts: *toki*'s rays and head with *pona*'s smile inside. Edit those parts, not the clones on its page. It isn't a UCSUR word, so it has no glyph of its own yet; *pu* uses it on its cover.

The build strokes after placing, so a scaled clone keeps the same line weight in the font, even though Inkscape shows its stroke scaled. Don't delete a part that still has clones: the build stops with an error naming the missing piece. For a one-off shared piece you can still clone by hand: select it, `Alt+D`, and move the clone to the word's page in the `glyph` layer.

## How to draw

- **Draw centrelines, not outlines.** One path down the middle of each stroke. The build gives every path the same stroke weight (`STROKE` in `build/common.py`, 40 units) with round ends and joins, whatever stroke width the path has in Inkscape.
- **Build from simple pieces.** Use the Bezier pen (`B`) for lines and curves, the ellipse tool (`E`) for circles, and the rectangle tool (`R`) for boxes. With snapping on, points land on the 25-unit grid, which keeps sizes and curves consistent across words.
- **Preview the real weight.** Give your paths `stroke-width: 40`, round caps and round joins, and no fill (Fill and Stroke, `Ctrl+Shift+F`). Inkscape remembers the last style per tool, so you only set it once.
- **Dots** are a path with a single tiny segment; the round caps turn it into a dot.
- **Filled areas** (if a glyph has any) go in the `fill` layer and are filled exactly as drawn.
- **The midline matters.** Sitelen pona centres on the midline, not a baseline, so keep each glyph visually centred on the blue line unless it is meant to sit high or low.
- **Groups are fine.** A group counts as one piece, so it belongs to the page its centre is on.
- Anything hidden, anything off the pages, and anything outside the `glyph` and `fill` layers is ignored (the build warns about pieces that are on no page).

## Words that need a different drawing in monospace

The monospace build puts every glyph in a full-width cell. If a word looks wrong there (for example a narrow *seme* that looks lost, or a wide glyph that looks cramped), add a page (Pages tool, `Shift+F7`) with the same size, name it `seme.mono`, and draw the monospace version on it. The monospace build uses a `.mono` page when one exists; the proportional build always uses the plain page.

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

The *ku suli* words (*kin, namako, oko, …*) have no drawing in *pu*, so their reference comes from a font instead (sitelen seli kiwen, OFL, shown in blue). Those outlines are stored in the file itself.

## Snapping to the grid

The grid is 25 units, and every page starts on a grid line, so the same grid point has the same coordinates on every page. Turn snapping on (`%`, or the magnet at the top right) and make sure snapping to grids is enabled in its menu; then points land on round numbers like 175 or 500.

## Glyph sizes

The red box is the topline and baseline: a glyph's outer edge should touch it on its longer side (top and bottom for tall glyphs, left and right for wide ones like *linja*). `python3 build/fit_sizes.py --font standard` scales every glyph that falls short and centres it along that side. Words that share a linked part in the same place are scaled together so the part stays put, which can leave some of them a little short, and the part's own page is scaled to match, so it looks the way those glyphs show it. Glyphs made of boxes are all scaled by the same amount, so the open boxes stay as wide as the closed ones. Small glyphs (*lili*) grow by the typical amount instead. Each word's scale is kept on its page's sub-layer (`data-size`), and the references, drafts and part clones on that page follow it. Run `make_templates.py` and `link_parts.py` afterwards. The checker lists big glyphs that don't reach the lines.

## Checking the file

`python3 build/check_glyphs.py --font standard` lists likely mistakes: ink past the red box, pieces on the wrong page or on no page, paths whose ends almost meet, and filled shapes in the glyph layer (which come out a stroke-width bigger). With `--fix` it also straightens lines that are nearly vertical or horizontal, gives every piece the standard stroke style, removes drafts under pages you have drawn, and drops unused path effects. Run `make_templates.py` (and `link_parts.py`) first: they move loose pieces, and drawings accidentally made in the drafts layer, into their pages' sub-layers.

## Regenerating the file

`python3 build/make_templates.py --font standard` rewrites the `reference` and `guides` layers and the word pages, for example after a word is added to `spec/words.tsv`. It keeps the drawings in `drafts`, `parts`, `glyph` and `fill`, and pages you added yourself. Shapes lying loose in `glyph` are moved into their page's sub-layer, without changing where they are. It reads the ku suli reference from `reference/sitelen-seli-kiwen/downloads/sitelenselikiwenjuniko.ttf` (or `--reference other.ttf`); without that file those words lose their reference.
