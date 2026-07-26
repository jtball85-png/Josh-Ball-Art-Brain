# Print border sizing — matching real off-the-shelf frame+mat combos

Date: 2026-07-25 · Garage decision record · Follow-up to
`finerworks-paper-recommendation-2026-07-25.md` and the "Steve" print-pipeline
pass.

## Problem

The pipeline's first border spec (0.5" for 8x10, 1.0"/1.25" for 11x14/16x20)
was sized off general fine-art advice for prints sold **without** a mat,
where the built-in white margin has to visually do the mat's job on its
own. The CEO mocked up the actual prints behind real standard pre-cut mats
(Studio Decor Belmont, Frame Destination and similar off-the-shelf combos)
and found 11x14 and 16x20 showed far too much white peeking out from under
the mat — because that spec didn't account for a mat sitting on top at all.

## Real standard mat openings (verified)

| Frame | Mat opening | Matted print | Overlap (each side) |
|---|---|---|---|
| 11×14 | 7.5"×9.5" | 8×10 | 0.25" |
| 16×20 | 10.5"×13.5" | 11×14 | 0.25" |
| 20×24 | 15.5"×19.5" | 16×20 | 0.25" |

The key finding: **the overlap is a flat ~0.25" per side regardless of
frame size** — it does not scale up the way the original border spec did.
A frame-size-scaled border (1"–1.25" on the two larger sizes) massively
overshoots that fixed 0.25" once a real mat is added, leaving 0.75"–1.0"
of border still showing instead of a thin, intentional sliver.

## Decision

Border widths are sized around the real 0.25" overlap plus a deliberately
thin, mostly-uniform peek — not around generic no-mat print margins:

| Print size | Border L/R/Top | Border bottom | Peek after 0.25" mat overlap |
|---|---|---|---|
| 8×10 | 0.3" | 0.3" | 0.05" (small safety margin over 0.25", so mat-cutting tolerance never crops the photo) |
| 11×14 | 0.5" | 0.625" | 0.25" sides/top, 0.375" bottom |
| 16×20 | 1.0" | 1.125" | 0.75" sides/top, 0.875" bottom |

Notes on the specific numbers:
- The CEO's own first pass at these numbers (0.25"/0.5"/1") was exactly
  right in spirit — simple, doesn't scale as aggressively as the original
  spec — but 8x10 at exactly 0.25" leaves **zero** nominal peek once the
  0.25" mat overlap is subtracted, meaning any real-world mat-cutting
  tolerance could crop into the actual photo rather than just the border.
  Nudged to 0.3" for a hair of safety margin.
- 11x14 and 16x20 keep a light "bottom-weighted mat" touch — bottom gets
  +0.125" over left/right/top — per the CEO's preference to keep that
  traditional detail, just at a smaller increment than the original
  +0.25" now that the base borders themselves are much thinner.
- 16x20's peek (0.75"–0.875") is larger in absolute terms than 8x10's
  (0.05") and 11x14's (0.25"/0.375") — this was the CEO's explicit choice
  (1" base border for 16x20) and reads fine at that physical size; flagging
  it here only so a future session doesn't "fix" it back toward uniformity
  without knowing it was deliberate.

## Where this is implemented

`garage/prints/derive_prints.py`'s `SHEETS` constant, enforced by
`tests/test_derive_prints.py` (pixel-checks the actual produced border
width on all four edges, per the CLAUDE.md convention of encoding a
research decision as a test at build time).

## FinerWorks-specific ordering note (CEO decision, 2026-07-25)

FinerWorks' own order form has two different ways to add white space, and
they are NOT interchangeable:
- **Their "border" checkbox** adds the border *outside* the size you
  select — the cut sheet grows bigger than the nominal size (their own
  example: a 20×16 print + 0.5" border becomes a 21×17 cut sheet, not
  20×16).
- **"Borderless" + an embedded margin** — upload a file that already *is*
  the exact final paper size, with the white margin baked into the image
  itself (exactly what `derive_prints.py` outputs) — the cut sheet comes
  out exactly 8×10/11×14/16×20 as intended.

**Decision: always order FinerWorks prints as "borderless" at checkout.**
Our files already have the margin embedded — checking their border option
too would either double the margin or produce a non-standard, oversized
cut sheet instead of the intended 8×10/11×14/16×20. This is a manual step
the CEO does at order time (no live FinerWorks connector exists yet), but
it's easy to forget, hence written down here.

FinerWorks' own support docs also recommend 0.5" or 1" border specifically
for matted prints (matches our 11x14/16x20 base numbers) — the extra
margin isn't just cosmetic peek, it also gives enough paper to tape the
print to the mat's backing board so it doesn't shift or fall through the
window. 8x10 (0.3") sits a bit thinner than either of their two presets;
that's an accepted tradeoff for now, not an oversight (see decision above).
