"""Josh Ball Art — print derivation pipeline (masters -> print-ready files).

The master on disk is never touched: full-res, native ratio, untouched.
Per-size aspect-ratio handling is sourced from
`garage/research/joshballart-phase0-print-partner-2026-07-21.md`: "8x10
(4:5) vs 11x14 vs 16x20 (4:5) crop differently — file prep must derive
per-size crops, not one master crop." Each size center-crops the image to
match ITS OWN exact aspect ratio, then scales uniformly to fill the
printable area — the crop only ever trims a thin strip off one pair of
opposite edges; the scale step never stretches/warps, since the crop
already matches the target ratio before scaling. Sheets auto-rotate to
match image orientation (a landscape image gets a 20x16 sheet, not 16x20).

Borders are exact, not "at least," and sized for how these prints actually
get displayed: a standard off-the-shelf frame+mat combo (11x14 matted to
7.5x9.5 for an 8x10; 16x20 matted to 10.5x13.5 for an 11x14; 20x24 matted
to 15.5x19.5 for a 16x20 — verified real pre-cut mat dimensions, a flat
~0.25in overlap per side regardless of frame size). Border widths are kept
modest so only a slim, consistent sliver of white peeks out from under
that mat rather than a wide gap — see
garage/research/print-border-mat-compatibility-2026-07-25.md for the full
math. 8x10 is uniform on all 4 sides; 11x14/16x20 keep a light
"bottom-weighted" mat touch (+0.125in on the bottom only) — see SHEETS.

Resolution honesty: the image's EFFECTIVE DPI (cropped source pixels /
printed inches, per size) is measured and flagged: >=300 excellent ·
>=200 acceptable (FinerWorks floor) · <200 FAIL. Never upscaled, ever —
only downsampling is allowed, since downsampling discards excess real
pixels while upscaling would invent detail the sensor never captured.
>=300: the crop is downsampled to the standard 300 DPI shipping grid.
200-299: the crop ships at its own native, un-resized pixel size, and
the whole sheet (border math included) is built at that true DPI
instead of a hardcoded 300, so physical sheet inches stay exact and the
file's own DPI tag is honest for that specific file. <200: still
written (for visual inspection) but as `{size}_DO-NOT-SELL.jpg`, never
passed off as a sellable file under the plain `{size}.jpg` name.

Output per master: ready/{name}/{size}.jpg (sRGB JPEG q95, DPI tag =
300 when excellent, true native eff_dpi when acceptable; FAIL sizes go
to {size}_DO-NOT-SELL.jpg instead) + proofs/{name}-proof.jpg contact
sheet + a printed DPI/crop report.

Two-stage master storage: candidates/ holds a master as soon as it clears
this pipeline, before any physical print has been ordered and approved by
the artist; masters/ is promotion-only — move a file there by hand once a
real print is in hand and confirmed good. Both folders are scanned when no
file args are given.

Usage:
  .venv/Scripts/python.exe garage/prints/derive_prints.py            # all candidates + masters
  .venv/Scripts/python.exe garage/prints/derive_prints.py <file>...  # specific
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
CANDIDATES, MASTERS, READY, PROOFS = (
    ROOT / "candidates", ROOT / "masters", ROOT / "ready", ROOT / "proofs")
DPI = 300
# (name, short side, long side, border on left/right/top, border on bottom) in inches
SHEETS = [
    ("8x10", 8, 10, 0.3, 0.3),
    ("11x14", 11, 14, 0.5, 0.625),
    ("16x20", 16, 20, 1.0, 1.125),
]


def derive(master_path: Path) -> list[str]:
    img = Image.open(master_path)
    img = img.convert("RGB")  # print files ship flattened sRGB
    iw, ih = img.size
    image_ratio = iw / ih
    landscape = iw >= ih
    out_dir = READY / master_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    report, sheet_files = [], []

    for name, s_short, s_long, border_lrt, border_bottom in SHEETS:
        sw_in, sh_in = (s_long, s_short) if landscape else (s_short, s_long)
        content_w = sw_in - 2 * border_lrt
        content_h = sh_in - border_lrt - border_bottom
        target_ratio = content_w / content_h

        # crop to the target ratio first (never stretch), then scale uniformly
        if image_ratio > target_ratio:
            crop_w, crop_h = round(ih * target_ratio), ih
        else:
            crop_w, crop_h = iw, round(iw / target_ratio)
        left, top = (iw - crop_w) // 2, (ih - crop_h) // 2
        cropped = img.crop((left, top, left + crop_w, top + crop_h))

        eff_dpi = crop_w / content_w  # = crop_h / content_h, by construction
        verdict = ("excellent" if eff_dpi >= 300 else
                   "acceptable" if eff_dpi >= 200 else "FAIL — too small")

        # Never upscale past native resolution — only downsampling is
        # allowed. >=300: safe to downsample the crop's real pixels down
        # to the 300 DPI shipping standard (discards excess detail,
        # invents nothing). <300: ship the crop at its own native pixel
        # size — the whole sheet is built at that true DPI instead of a
        # hardcoded 300, so the file's DPI tag stays honest and sheet
        # inches stay exact.
        if eff_dpi >= 300:
            sheet_dpi = DPI
            placed = cropped.resize((round(content_w * sheet_dpi), round(content_h * sheet_dpi)), Image.LANCZOS)
        else:
            sheet_dpi = eff_dpi
            placed = cropped

        sheet = Image.new("RGB", (round(sw_in * sheet_dpi), round(sh_in * sheet_dpi)), "white")
        sheet.paste(placed, (round(border_lrt * sheet_dpi), round(border_lrt * sheet_dpi)))
        sheet_files.append((name, sheet, verdict))

        fail_note = ""
        if verdict.startswith("FAIL"):
            out = out_dir / f"{name}_DO-NOT-SELL.jpg"
            fail_note = "  [DO-NOT-SELL — below FinerWorks' 200 DPI floor]"
        else:
            out = out_dir / f"{name}.jpg"
        sheet.save(out, "JPEG", quality=95, dpi=(round(sheet_dpi), round(sheet_dpi)))

        crop_note = ""
        if crop_w < iw:
            crop_note = f"  (cropped {(iw - crop_w) / iw * 100:.1f}% off left+right)"
        elif crop_h < ih:
            crop_note = f"  (cropped {(ih - crop_h) / ih * 100:.1f}% off top+bottom)"
        report.append(f"  {name:6} sheet {sw_in}x{sh_in}\"  border {border_lrt}\"/{border_bottom}\"b"
                      f"  image {content_w:.1f}x{content_h:.1f}\"  effective {eff_dpi:.0f} DPI"
                      f"  -> {verdict}{crop_note}{fail_note}")

    # proof contact sheet: the three layouts side by side, scaled down
    PROOFS.mkdir(exist_ok=True)
    thumb_h = 700
    thumbs = []
    for name, sheet, verdict in sheet_files:
        t = sheet.copy()
        t.thumbnail((thumb_h * 2, thumb_h), Image.LANCZOS)
        thumbs.append((name, t, verdict))
    total_w = sum(t.width for _, t, _ in thumbs) + 40 * (len(thumbs) + 1)
    proof = Image.new("RGB", (total_w, thumb_h + 110), (34, 36, 40))
    d = ImageDraw.Draw(proof)
    x = 40
    for name, t, verdict in thumbs:
        proof.paste(t, (x, 40))
        color = (120, 220, 150) if "FAIL" not in verdict else (240, 120, 110)
        d.text((x, thumb_h + 55), f"{name}  ·  {verdict}", fill=color)
        x += t.width + 40
    proof_path = PROOFS / f"{master_path.stem}-proof.jpg"
    proof.save(proof_path, "JPEG", quality=90)
    report.append(f"  proof: {proof_path}")
    return report


def main(args: list[str]) -> None:
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    MASTERS.mkdir(parents=True, exist_ok=True)
    exts = (".tif", ".tiff", ".jpg", ".jpeg", ".png")
    targets = ([Path(a) for a in args] if args else
               sorted(p for folder in (CANDIDATES, MASTERS) for p in folder.iterdir()
                      if p.suffix.lower() in exts))
    if not targets:
        print(f"No masters found in {CANDIDATES} or {MASTERS} — drop a "
              f"flattened full-res export in candidates/ first.")
        return
    for m in targets:
        print(f"\n{m.name}  ({Image.open(m).size[0]}x{Image.open(m).size[1]} px)")
        for line in derive(m):
            print(line)


if __name__ == "__main__":
    main(sys.argv[1:])
