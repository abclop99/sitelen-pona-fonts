# Shared spec (draft)

Everything the three fonts must agree on, so one text works in all of them. Each font shows what it can and falls back gracefully otherwise. This file is the source of truth for decisions. Rationale is in [docs/custom-font-feasibility.md](../docs/custom-font-feasibility.md); where the two differ, this file wins.

**Principle: appearance is the font's job, never the text's.** Text says *what* is written and optionally *how* words combine. Handwriting shortcuts, cursive joins, layout choices and alternate shapes are all applied by the font.

## Encoding
- Words and controls use the UCSUR sitelen pona block, U+F1900–U+F19FF.
- `ZWJ` (U+200D): combine, font chooses the layout. `U+F1995`: stack. `U+F1996`: scale.
- Cartouche: start `U+F1990`, end `U+F1991`, combining cartouche extension `U+F1992`.
- Long *pi*: start `U+F1993`, combining extension `U+F1994`.
- Long glyphs: start `U+F1997`, end `U+F1998`, combining extension `U+F1999`; reverse (extend left) start `U+F199A`, end `U+F199B`.
- Middle dot `U+F199C`, colon `U+F199D`.
- Check every codepoint against the UCSUR chart (https://www.kreativekorp.com/ucsur/charts/sitelen.html) before the build uses it. Word codepoints are **not** alphabetical after the original block.
- Nested structure (display font, the composer tool): Ideographic Description Characters (U+2FF0–U+2FFF, U+31EF) as optional extra input. TODO: confirm.

## asuki (ASCII) input
Match sitelen seli kiwen wherever possible:
- `-` or `+` combine, `^` stack, `*` scale
- `[` `]` cartouche, `..` middle dot, `::` colon
- `(` `)` extend right, `{` `}` extend left
- number suffix selects a variant (for example `ni2`)
- New syntax only for things seli kiwen lacks (nesting, forced side-by-side, inside, mirroring). Check the SPPTA ASCII Input Standard first and accept its form where it overlaps. TODO

## Designed combos
Curated list shared by all fonts (drawings differ per font). Rules: every component stays identifiable; the head word is the body and the modifier attaches; no fusion where order would be ambiguous; a stylistic set turns them off.

| Sequence | Idea | Notes |
|---|---|---|
| tomo + tawa | house with feet (larger *tawa* legs below *tomo*) | motivating example |

## Writing directions
- Vertical: glyphs upright; vertical forms for cartouches, extensions, punctuation. Direction particles (*li*, *e*, *la*, *pi*, *tawa*, *kama*, *tan*) get rotated forms tweaked to avoid collisions (for example rotated *li* vs *suli*). TODO: decide.
- RTL mirroring tiers:
  - must flip: *tawa*, *kama*, *li*, *la*, *tan*, *e*, *pi* and long-*pi*, extension starts and ends
  - flip for looks: side-facing glyphs (*kijetesantakalu*, *kala*, *soweli*, *waso*, *akesi*, …)
  - never flip: *ni*
  - Semi-cursive font: flip everything, with a dedicated RTL *ni* form.
- Boustrophedon: done by layout (test page or composer), using the mirror features.

## Open questions
- Font names
- Whether reversed boustrophedon lines mirror glyphs
- Handwriting font: body-aligned rather than midline-centred? (a possibility, not decided)
