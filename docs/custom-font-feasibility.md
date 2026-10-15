# Making your own sitelen pona font: what it would take

> Planning notes, written as replies during the first planning discussion, so they address "you" (the repo owner). **Decisions live in [spec/README.md](../spec/README.md), which wins wherever the two differ.** "I believe" marks claims that weren't verified.

**Short answer:** very feasible. A basic font is a weekend with SP Font Maker. A polished font with all the usual features is a few weeks of evenings, and most of that time goes into drawing rather than technical work. The hard parts are your two ambitious ideas: **combining any glyph with any other** and **semi-cursive joining**. Both can be done in OpenType. Neither is a feature you switch on; you get them by building a system of smaller glyph variants with a script.

What I checked: the two wiki pages you linked (from your screenshots), and the internals of *sitelen seli kiwen juniko* (see [reference/README.md](../reference/README.md) for where to download it), which I inspected with fontTools. Where I say "I believe," I'm going from memory and didn't verify it.

---

## 1. Your ideas, ranked by difficulty

| Idea | Difficulty | Main cost |
|---|---|---|
| Custom glyph style (handwritten, simplified, semi-cursive look) | Easy technically, real drawing work | Drawing about 140 glyphs consistently |
| Narrow *seme* (and other non-square glyphs) | Trivial | It's just the advance width in a proportional font |
| Display / seal-inspired style | Easy technically, the hardest *design* work | Consistency rules across 140 glyphs |
| Alternate glyphs | Easy | One extra drawing each, plus one feature line |
| Hand-designed combined glyphs (walking-house *tomo tawa*) | Easy per glyph | One drawing plus one ligature rule each; scales linearly |
| "All the features of existing fonts" | Medium | Mostly copying feature code from seli kiwen |
| Stacking / side-by-side for *every* glyph | Medium | Script-generated half-size variants, plus positioning |
| Scaling / "inside" for many glyphs | Hard | Per-container inner boxes, plus small variants |
| Semi-cursive ligatures between glyphs | Hard | Join variants plus contextual rules; rendering varies by app |
| A font that both joins cursively *and* has flexible combos | Very hard | The two systems interact; build them as separate fonts |

---

## 2. Foundations

### Encoding (UCSUR)
Use the UCSUR sitelen pona block, **U+F1900–U+F19FF** (a Private Use Area agreement, not official Unicode). From seli kiwen's README and the guidelines page:

- `U+F1900…` are the words: the original block is alphabetical, but later additions (from about `U+F1978` on, such as *namako*, *kin*, *oko*) are in order of addition. Take codepoints from the UCSUR chart; never generate them by sorting the word list.
- `U+F1990` / `U+F1991`: cartouche start / end.
- `U+F1995`: **stacking joiner**. `U+F1996`: **scaling joiner**. A plain **ZWJ** (`U+200D`) means "combine however the font prefers."
- `U+F1997`/`F1998`: extend a glyph to the right (long *pi*, long glyphs). `U+F199A`/`F199B`: extend to the left.
- `U+F199C` / `U+F199D`: middle dot / colon.

Map at least these so your font is interchangeable with every other font. Anything beyond UCSUR (your own combos, alternates) should be reached *through* these codepoints with OpenType features, not given new codepoints. Then text you type stays readable in other fonts.

### ASCII input (the "asuki" approach)
Typing `toki` and seeing the glyph is done with ligature rules: the letters t·o·k·i become one glyph. The wiki says SP Font Maker now follows the **ASCII Input Standard** from the Sitelen Pona Publishers and Typographers Association. **Decision (15 Oct): match sitelen seli kiwen's *asuki* syntax wherever possible**, so text typed for seli kiwen works in your fonts:
- `-` or `+` to combine (font chooses the layout), `^` to stack, `*` to scale.
- `[` `]` for a cartouche, `..` for a middle dot, `::` for a colon.
- `(` `)` to extend a glyph to the right, `{` `}` to extend it to the left.
- A number appended to a word selects a variant (for example `ni2`).
- Anything seli kiwen has no syntax for (nesting, side-by-side forced, inside, mirror) needs new syntax. Pick characters seli kiwen doesn't already use, and check the SPPTA ASCII Input Standard (which SP Font Maker follows) first. Where it covers the same thing, accept its form too, so both kinds of input work.

A common approach is to ship two builds, as seli kiwen does: one that converts ASCII (*asuki*) and one that is UCSUR-only (*juniko*), so normal Latin text isn't converted by accident.

### Monospace vs proportional
The guidelines page lists three options: monospace, proportional, and kerned (which it calls "rare… would not be recommended").

- **Semi-cursive must be proportional.** Joined glyphs need variable widths.
- **Display:** monospace (see §6). A square cell makes nested combinations predictable. Tall-narrow glyphs like *seme*, *mi*, *sina* and *ona* should be centred with padding in that cell, not stretched to fill it.
- **Kerning:** it depends on how irregular the shapes are. For blocky, regular glyphs, good side bearings do most of the work. But side bearings measure each glyph's outer box, not its visual mass, so a glyph that is thin, lopsided or has a long tail looks unevenly spaced next to its neighbours. You can see this in sitelen seli kiwen with *kala linja suli sewi*, which is proportional but not kerned. A semi-cursive font with exits, tails and lean will hit this constantly, so plan on **class-based kerning** there (see section 6). Joined pairs are the exception: their join anchors position them (section 4), so kerning only applies where glyphs don't join. In the more regular fonts, a few kerning pairs may be enough.
- **Narrow *seme*:** in a proportional font, *seme* gets its natural width. The wide *seme* comes from squaring it off for monospace. The guidelines say *seme* should **not** be differentiated from a question mark, so a narrow, ?-like *seme* fits the guidelines.

Seli kiwen confirms this works: it's proportional, with word widths ranging from about 320 to about 1080 units. *seme* is 722.

### Vertical metrics
Sitelen pona centres on a **midline**, not a baseline. Pick one em square (for example 1000 units), centre every glyph vertically, and set ascender and descender so line spacing stays comfortable when Latin text is mixed in. (The handwriting font might not follow this; see §6.)

---

## 3. Tools

| Tool | Good for | Notes |
|---|---|---|
| **SP Font Maker** (waso Keli) | Fastest route to a working handwritten font | You fill a paper or digital template, then a script builds the font. It covers *nimi pu*, *ku suli* (except *kokosila*), cartouche, dot, colon, quotes and custom words. Since August 2025 it **auto-generates stacked glyphs**; since 2026 it supports the ASCII Input Standard. Over 100 fonts have been made with it. **Limits:** you get its feature set and layout, with no custom OpenType and probably no cursive joining. |
| **FontForge** (free) | Full control, scriptable in Python | Clunky interface, but it does everything, and its Python API is good for generating variants. |
| **Glyphs** (Mac, paid) / **FontLab** (paid) | A nicer drawing experience | Glyphs has good smart components and feature-code tooling. |
| **fontTools / fontmake + UFO** (Python) | Building the font from scripts and feature files | This is how you'd generate thousands of combo variants. The source lives in git as text. |
| **Inkscape / any vector app** | Drawing | Draw in SVG, then import. |
| **Scanner + potrace** | Real handwriting | Fine for the handwritten style. Skip it for display. |

A practical pipeline once you outgrow SPFM: **draw each glyph as an SVG skeleton**, then **a Python script builds the font** (outlines, generated variants, feature code), then **fontmake or FontForge compiles** it.

**The tip that makes your combination ideas workable: draw centrelines, not outlines.** If each glyph is a monoline skeleton and the script expands it to a stroke, a half-size stacked glyph can be drawn at the **same stroke weight** as a full-size one. If you shrink finished outlines instead, the strokes get thinner and combos look spindly. A seal-script-inspired display style is monoline anyway, so this suits it perfectly. For the semi-cursive style, expand with a pen-shaped nib for some contrast.

---

## 4. How each feature works in OpenType

OpenType has two tables:

- **GSUB** swaps glyphs. Its tools: ligatures (several glyphs become one), contextual alternates (`calt`: "use variant B when followed by X"), and stylistic or character variants (`ss01`–`ss20`, `cv01`–`cv99`, `salt`, `rand`).
- **GPOS** moves glyphs. Its tools: kerning, mark attachment (anchors), and cursive attachment (joining an exit point to an entry point).

**GPOS can move glyphs but cannot resize them.** Any "smaller" or "squished" form must exist as its own pre-drawn glyph that GSUB swaps in.

For reference, seli kiwen does **everything in GSUB and has no GPOS table at all**. Every compound is a **pre-drawn glyph** (3,732 glyphs total), selected with `rlig` and `calt` and reached through `cv80–cv99` and `ss13–ss20` for variants. Mostly it uses chained-context lookups (85 of them). Its approach is "draw every combo you support." That's simple and looks great, but it doesn't scale to "everything."

### Custom glyphs / alternates
- Alternates: assign `cvNN` per word (for example `cv01` for *ni* direction) and `ssNN` for themed sets (for example "all-*pu* forms"). For random handwriting variation, use `rand`, but support is spotty. A `calt` cycle that picks variant 1, 2, 3 from context is more reliable.
- Many apps (Word, phones, chat apps) offer no way to turn on `cv` or `ss` features. Make sure the *default* glyph is the one you want most of the time.

### Hand-designed combos (walking-house *tomo tawa*)
One ligature rule each: `sub tomo zwj tawa by tomo_tawa.walking;`. You can add as many as you like.

The motivating example: seli kiwen's *tomo tawa* just scales *tawa* down to fit inside *tomo*. A designed version would be a house with feet, for example a larger *tawa* whose legs stick out below *tomo*. That's the difference between a *mechanical* combo (components placed in a box) and a *meaningful* one (the components interact the way the idea does).

Rules of thumb for meaningful combos, so meaning and word order stay clear:
- **Every component must stay identifiable.** A reader who doesn't know the combo should still be able to read off both words. Feet can stick out, but they should still read as *tawa*.
- **The head word is the body, the modifier attaches to it.** In *tomo tawa* the house is the thing and the movement modifies it, so *tomo* stays dominant and *tawa* becomes its legs. Then *tawa tomo* (if it ever came up) wouldn't look the same, and word order is preserved by which part is the body.
- **Don't fuse when order is ambiguous.** If you can't tell from the drawing which word comes first, use the generic stack instead.
- **Provide an escape hatch:** a stylistic set that turns designed combos off and falls back to the generic layout, for readers who prefer explicit forms or for teaching material.
- Keep the list curated and documented (a table of each combo, its components and order, and why it's drawn that way), so all three fonts can share one list even where their drawings differ. You can also make a hand-drawn combo *override* the generic stack-or-scale result, so you get a nice default for common combos and a generic fallback for everything else. This is the best design pattern for your idea list.

### Flexible stacking and side-by-side for everything
**Not N² ligatures.** With about 140 words, every pair would be about 20,000 drawings. Instead:

1. Have the script generate **per-glyph variants**: `word.top`, `word.bottom` (half height, same stroke weight) and `word.left`, `word.right` (half width).
2. GSUB rule: when a glyph is followed by the stacking joiner and another glyph, swap both for `.top` and `.bottom`.
3. Give the second glyph zero advance and shift it back under the first. Or give them a shared width, with mark attachment or a fixed offset.

That's about 140 × 4 generated glyphs, all scripted. It's the same principle as SP Font Maker's automatic stacking. The caveat is that a mechanical half-height squish looks bad for some glyphs (*seme*, *mi*, *lili*). Expect to hand-tune perhaps 10–20% of the variants. The script should use a hand-drawn override file if one exists.

**Choosing the layout automatically** for a plain ZWJ (stack versus side-by-side) can be done with glyph *classes*: tall-narrow glyphs go side-by-side, wide-flat glyphs stack. That's a few lines of feature code once the classes exist.

**Manual control** is free: the stacking joiner forces a stack, and you can define your own private sequence (for example in the ASCII syntax) for side-by-side.

### Scaling and "inside"
This is the hardest generic feature, because it only works for **container** glyphs (*tomo*, *poki*, *lupa*, *sitelen*, *nasin*, *insa*, *lipu*, *ilo*, …) and every container has a differently shaped hole.

- For each container, define an **inner box** (a rectangle, or one anchor point plus a maximum size), either as metadata in your source or as anchors.
- Generate **small variants** of every glyph at one or two sizes (`word.small`, perhaps `word.tiny`), again with matching stroke weight.
- GSUB: container + scaling joiner + glyph becomes `container` + `glyph.small`. GPOS mark attachment places `glyph.small` at the container's inner anchor.
- One fixed small size won't fit every hole. You either get a few sizes, with the container choosing via a class, or some combos look cramped. The wiki's guidelines say the same: use small glyphs plus alignment rather than merging every combination.

This is feasible for "everything inside about 15 containers" (about 15 anchors and about 140 small glyphs), well beyond the few select examples most fonts have. It's medium-hard if you accept a handful of awkward cases.

### Cartouches, long *pi*, long glyphs
The guidelines recommend **zero-width overlay pieces** filled in by contextual rules. Every glyph between the start and end marks gets a cartouche top and bottom piece (or an extension line) drawn under it, with no extra control characters. Seli kiwen does exactly this, and its author explicitly invites copying: *"Feel completely free to rip this font apart and steal code and ideas."* Copying its feature code is the fastest way to get this right.

In a **proportional** font the overlay pieces must match each glyph's width. Either generate one overlay per advance-width class, or (cleaner) make the cartouche line a cursive-attached segment stretched by repetition. Plan for this from the start; it's the main extra cost of not being monospace.

### Semi-cursive ligatures
This works like a script font (such as a connected English handwriting font), not like Arabic shaping. Unicode doesn't tell the font which glyphs join, so you decide.

1. Pick **one or two standard join heights** (for example the midline). That keeps the problem tractable.
2. For each word that can join, draw (or generate from the skeleton) up to four forms: `isolated`, `joins-right`, `joins-left`, `joins-both`. Many glyphs won't join on some side (closed shapes like *sike* or *lupa*); those simply have no such form.
3. **`calt`** picks the form from its neighbours: "if the next glyph can accept a left join, use my joins-right form."
4. **GPOS cursive attachment** (`curs`) snaps each glyph's exit point to the next glyph's entry point. This handles spacing, so you **don't need kerning** for joined pairs. Alternatively, draw the connector into the variant and space normally.
5. Optional: special **pair ligatures** for pairs that look better as a unit (*toki pona*, *mi wile*, …). It's the same mechanism as the custom combos.

Cost: roughly 140 × (up to) 4 variants, mostly generated by script, plus the design work of deciding *where* each glyph's strokes start and end. That design decision is the real work.

**Rendering caveat:** browsers, LibreOffice, InDesign and anything using HarfBuzz handle `calt` and `curs` well. **Word** applies `calt` only if you tick "contextual alternates" in Advanced font settings. Many phone and chat apps ignore OpenType features entirely, so you'd see the isolated forms. Make the isolated forms good on their own.

**Don't combine cursive with stacking or scaling in the same font** at first. Every joined variant would also need top, bottom and small forms, which multiplies everything. Your instinct to keep flexible combos to the display script is the right call.

---

## 5. Suggested plan

1. **Prototype the handwritten style with SP Font Maker.** Fill the template, get a working font with cartouches, ASCII input and auto-stacking, and live with it for a while. This tests the *drawings*, which matter most.
2. **Decide the semi-cursive rules on paper**: join heights, which glyphs join on which side, the narrower *seme*. Then move that style to a scripted pipeline (SVG skeletons, Python, fontmake). Lift cartouche and extension code from seli kiwen (OFL, with no Reserved Font Name, so reusing its code has no naming restriction; keep its copyright notice with anything copied).
3. **Display font as a separate project**, built from monoline skeletons from day one so generated stacked, side-by-side and small forms keep the stroke weight. Order: words, then cartouche and extensions, then generic stack and side-by-side, then containers with inside and scale, then hand-drawn combo overrides like walking-house *tomo tawa*.
4. Test text in a browser page with feature toggles (`font-feature-settings: "cv01" 1` and so on). This goes in `test/`.

### Forking versus starting fresh
- **Fork seli kiwen** if you want its full feature set right away and mainly plan to redraw. The catch: its compounds are 3,700 hand-drawn glyphs in seli kiwen's style. A restyled font would have to redraw them all or drop them, so you'd mostly keep its *feature code* and glyph naming, not its art.
- **Start simple with a scripted pipeline** if the flexible combination system is the point. That system is easier to build fresh than to retrofit onto seli kiwen's "draw every compound" design.

My recommendation: **SPFM for the first handwritten prototype, then a fresh scripted build that borrows seli kiwen's feature code** for each serious font.

---

## 6. Your three fonts (follow-up)

### Shared encoding: one text, three fonts
For the same text to work in all three, they all read the **same input**. Each font then shows as much of it as it can:

| In the text | Handwriting | Normal combos | Display |
|---|---|---|---|
| UCSUR words (`U+F1900…`) | yes | yes | yes |
| Cartouche, long *pi*, extension controls | yes | yes | yes |
| `ZWJ` (combine however the font prefers) | its own shorthand, or side by side | auto stack / side / inside | same as normal |
| `U+F1995` stack / `U+F1996` scale | does its best, or ignores | yes | yes |
| Special combos (`tomo ZWJ tawa`) | its own shorthand if one exists | walking house | its own drawing |
| Nested structure (see §7) | ignored: shows the words in order | first level | all levels |
| ASCII input (`toki`, `[ ]`, `-`, `^`, `*`) | same rules in all three | | |

The rule that makes this work: **appearance is the font's job, never the text's.** Handwriting shortcuts, cursive joins, stacked layouts and alternate shapes are all triggered automatically by the font from ordinary text. They are never typed as special characters. The only things in the text are *what* is combined and, optionally, *how*. Write one shared spec document for the encoding and the ASCII syntax first, so the three fonts can't drift apart.

### Font 1: handwriting / semi-cursive
- **Kerned: yes.** In a handwriting font, the glyph shapes vary in width, overhang and lean, so class-based kerning (groups like "open on the right" and "tall left stroke") is worth doing. It's the normal practice for script fonts. Draw the glyphs first and kern last. Kerning is the part that tools help with most (the kerning windows in Glyphs and FontLab, or MetricsMachine).
- **Possibility (not decided): align on the body, not the bounding box.** Semi-cursive glyphs needn't be centred on the midline. Like Latin handwriting with its x-height and ascenders, each glyph can have a main **body** that sits on or around the midline, with parts that hang above or below it. In *lon*, for example, the line could sit near the midline with the dot above it. This needs no OpenType feature; it's just where you place each outline. If you go this way, three consequences:
  - Define the body zone (the band the main strokes live in) as an explicit design rule, so the off-centre glyphs still look aligned with each other.
  - Join points should sit at body height, not box height. That keeps the cursive joins level.
  - Line spacing must allow room for the parts above and below the body, so set the vertical metrics from the tallest extents, not from the body.
- **Design work first, on paper:** stroke order and direction for each glyph, where the pen enters and exits, and a **confusables list**. Semi-cursive works because *fast* strokes still leave each glyph's key distinguishing feature intact. So decide which feature each confusable pair keeps, and never simplify it away. Start from the wiki's *Common pitfalls* list and add your own speed-writing risks:
  - *o* vs *sina* (your example): a quick *o* can't collapse into a dot-and-curve shape.
  - *mi* / *sina* / *ona* / *lape*: keep the circle small. A big loop written at speed makes these four merge.
  - *soko* vs *mama*: don't thicken *soko*'s stem.
  - up-arrow *epiku* vs directional *ni*.
  - flipped-*sin* *majuna* vs *sin* / *namako* (or use lotus *majuna*).
  - *seme*: a ?-like shape is fine, and the guidelines want it that way.
  - Keep the *pu* metaphors visible where you can; that's what keeps simplified forms recognizable.
- **Handwriting shortcuts = ligatures and contextual alternates.** Common pairs or phrases (*toki pona*, *mi wile*, *li*, *e*, *pi* before a modifier) can get their own fused forms through `liga` and `calt`. Each one is a drawing plus a rule. Start with about 20 shortcuts, not hundreds.
- **Natural variation:** two or three variants of common glyphs (*li*, *e*, *jan*, *toki*), cycled with `calt` so repeated words don't look stamped.
- **Combos:** keep this simple. Side by side with a joining stroke, plus hand-drawn shorthand for the few combos you'd actually write. No generic inside or scaling.

### Font 2: normal glyphs with flexible combos
- **"No separate glyphs" is half possible.** OpenType can only *move* glyphs at layout time, not resize them. So you have two options:
  1. **Contextual positioning (no per-combo glyphs):** one small or half variant per word, swapped in by context and placed with GPOS. With N words that's N × (a few sizes) glyphs, and every combination works. This is the scalable route.
  2. **Composite glyphs (a recipe per combo, no new drawing):** a TrueType composite glyph references other glyphs with a scale and offset. A script can emit thousands of these, and none of them need new outlines. Seli kiwen already has 1,199 composite glyphs. The limits: strokes shrink with the scaling, and a font holds at most **65,535 glyphs**. All pairs of about 140 words in 4 layouts is about 78,000, which is over the limit. So composites suit a curated list (the *ku suli* compounds, common phrases), and option 1 covers everything else.
- Use both: positioning as the general fallback, composites or hand drawings for nicer common combos, and real drawings for special ones like walking-house *tomo tawa*. One lookup order handles this: special drawing, then composite, then generic.
- **Proportional vs monospace:** build it **proportional** and also generate a **monospace build** from the same source. A script sets every advance width to one cell and recentres each glyph. Two output files from one source is cheap; maintaining two sources isn't.

### Font 3: display script (seal-inspired, nestable)
- **Monospace suits this font best.** A fixed square cell makes nesting easy: every sub-cell is a predictable fraction of the square.
- **Style:** monoline, drawn on a grid (for example 8×8 or 12×12 units of stroke spacing), with consistent corner and curve rules. That gives the seal-script feel through *regularity* rather than complexity. Building from monoline skeletons pays off most here, because generated half- and quarter-size forms keep the same stroke weight.
- **Nesting within the font:** **2 levels is realistic. 3 or more gets very hard.** At depth 2, a component can occupy one of about 9 cell shapes (width ∈ {1, ½, ¼} × height ∈ {1, ½, ¼}). Generate each word at each shape: about 140 × 9 ≈ 1,300 glyphs, which is fine. Containers get inner boxes at two sizes. The parsing rules ("this glyph is the 2nd child of a top/bottom split inside a left/right split") are finite-state GSUB contexts, so a script must generate them. Treat that as a prototype-and-see step. I haven't seen a sitelen pona font do depth 2 generically.
- **Arbitrary depth:** build a small **web composer** that reads the same text (words plus layout operators), lays out any depth recursively in JavaScript, and exports SVG or PNG from the display font's own skeletons. The font handles everyday text up to depth 2; the composer is the playground for building custom glyphs from components. It could share code with the test page in `test/`.

---

## 7. Do ⿱ ⿺ (Ideographic Description Characters) actually do anything?

**Mostly no.** They are only a way to *write down* how a character is built.

- Unicode defines IDCs (`U+2FF0–U+2FFF`, plus `U+31EF`) as **descriptive only**. The standard says renderers aren't expected to compose them into a glyph. Everywhere I know of, `⿱木木` shows as three separate characters.
- Where they *do* something, it's in tools rather than in text rendering: CJK character databases (CHISE, the IDS data in the Unicode Han database) and glyph engines such as GlyphWiki's KAGE, which builds glyphs from component descriptions. I believe a few experimental fonts compose IDS sequences with ligature tricks, but nothing mainstream does.
- **Sitelen seli kiwen** maps all 17 IDCs (I checked its cmap). It only draws them as visible symbols, which can appear inside cartouches. It doesn't compose with them. Its compounds use `ZWJ`, `U+F1995` and `U+F1996`.

**Should your fonts use them?** They're a reasonable choice for *nested* structure, because UCSUR's joiners can only express a flat chain (`A stack B scale C`) and can't say "this pair, as a unit, goes inside that". Tradeoffs:

- **Good:** they're real Unicode characters, so they're copyable, searchable, and show *something* in every font. In a font without support, `⿱ tomo ⿰ jan tawa` falls back to a readable description of the glyph. Prefix notation also nests without brackets.
- **Bad:** prefix notation is awkward for OpenType, since GSUB must look *ahead* to find where each sub-tree ends. That works for a fixed depth of 2 if a script generates the rules, but not beyond. It also means other sitelen pona fonts show the operators as visible symbols, so text written this way is less portable than plain `ZWJ` text.

**Recommendation:** use UCSUR joiners as the default in all three fonts, so ordinary text stays portable. Accept IDC sequences as an *extra* input in the display font (depth ≤ 2) and in the web composer (any depth). Make the ASCII syntax map to both.

---

## 8. Writing directions and boustrophedon (display font)

### What a font can and can't control
A font **draws** glyphs. The **app** decides line direction. So "supports vertical or right-to-left" means *the font provides the right glyphs and metrics, and an app that lays text out that way uses them.* Apps that can: browsers (CSS `writing-mode`, `direction`), InDesign and Illustrator (vertical type, OpenType features), Inkscape (vertical text), and some others. Word processors and chat apps mostly can't.

### Vertical (top to bottom)
- **Feasible, and a good fit for a monospace display font.** Sitelen pona glyphs stay **upright** in vertical text, as CJK characters do, so most glyphs need nothing.
- In the font: add **vertical metrics** (`vhea` / `vmtx`, with a square cell this is mechanical) and a **`vert` / `vrt2`** feature that swaps in vertical forms for the things that *do* change: cartouches (they run downwards), long *pi* and extension lines (vertical), the dot and colon, and quotation brackets (rotated, like 「」 in Japanese).
- In browsers, I believe Private Use characters default to upright in `writing-mode: vertical-rl` (their Unicode vertical orientation is "U"). Otherwise use `text-orientation: upright`.
- **Combos:** a combined glyph is one block whichever direction the text runs, so stacked or nested combos don't change. This is easy in a square-cell font and messier in a proportional one.
- **Direction-encoding glyphs in vertical text** (*li*, *e*, *la*, *pi*, *tawa*, *kama*, *tan*): kept upright, they still point right, which reads oddly in a column. Rotated 90°, some collide with other words (rotated *li* looks a lot like *suli*). Options:
  1. **Keep upright** (the CJK convention) and accept the oddness. Zero work.
  2. **Rotated `vert` forms plus a distinguishing tweak**, such as a rounded or open chevron for vertical *li*, so it never matches *suli*.
  3. **Purpose-drawn vertical forms** for just this handful of particles.
  - Default: try 2 in the display font. A script can catch collisions: rotate each glyph and compare it against every other glyph, flagging close matches.

### Right to left
- PUA characters count as **left-to-right** in Unicode's bidi algorithm, so an app won't run them right to left on its own. You force it with `dir="rtl"` plus `unicode-bidi: bidi-override` in CSS, or a right-to-left override character (`U+202E`) in plain text. Design apps have paragraph-direction settings that do the same.
- **Mirroring tiers (your call, 15 Oct):**
  - **Must flip (meaning depends on reading direction):** *tawa*, *kama*, *li*, *la*, *tan*, *e*, *pi* (and the long-*pi* line), plus extension starts and ends.
  - **Flip for looks:** animals and other side-facing glyphs (*kijetesantakalu*, *kala*, *soweli*, *waso*, *akesi*, …), so they face forward.
  - **Never flip:** *ni*. It points at something absolute on the page, so mirroring it would point it the wrong way.
  - **Doesn't matter:** the many near-symmetric glyphs (*jan*, *lon*, *sike*, *tomo*, …). Leave them.
  - Implementation: the two flip tiers become two features, `rtlm` (must flip, on by default in RTL) and a stylistic set for the cosmetic flips, so each can be toggled. A script generates mirrored outlines; hand-fix only the glyphs where a straight flip looks wrong.
- **Semi-cursive in RTL: flip everything**, because pen flow only works if the whole glyph is written right to left. The exception is *ni*: give it a dedicated RTL form whose stroke still flows leftward but whose arrow keeps pointing the right way. The join points mirror too. GPOS cursive attachment has a right-to-left lookup flag for exactly this case, so the joining system carries over.
- **Combos in RTL:** side-by-side order flips. Feature code runs in logical order while positioning applies visually, so test combos in RTL early.

### Boustrophedon
- **No font can do this alone**, because a font never knows where a line breaks. Every other line has to be set right to left (and usually mirrored) by whatever does the layout.
- What the font provides: the **mirrored stylistic set** from the RTL section. That's the whole font-side cost, and it's the same work as RTL.
- How to actually lay it out:
  - **Design programs:** break lines by hand. Set alternate lines to RTL and turn on the mirror set for those lines. Tedious but works today.
  - **Web page / the composer tool:** a little JavaScript can measure where lines wrap, then apply `direction: rtl` and the mirror feature to every second line. Vertical boustrophedon (alternating downward and upward columns) works the same way. This is the realistic way to make it pleasant, and it belongs in the same web composer as deep nesting (§6).
- **Quick way to see what it looks like:** a small web page can lay out text in any existing font, then mirror every second line. CSS can't target wrapped lines directly, so JavaScript first measures where the text wraps and wraps each visual line in its own element, then applies `transform: scaleX(-1)` to every second one. That mirrors all glyphs, *ni* included, so it's rough, but it's enough to judge readability on a wide page before any font work. With your own font, swap that for real RTL lines and the tiered mirror features above.

### Cost summary
| Direction | Font work | Works in |
|---|---|---|
| Horizontal LTR | none | everything |
| Vertical | vertical metrics + `vert` forms for cartouches, extensions, punctuation | browsers, InDesign/Illustrator, Inkscape |
| RTL | mirror set for directional glyphs; testing combos | anything that allows a direction override |
| Boustrophedon | same mirror set | design programs by hand; a web composer automatically |
