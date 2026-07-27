"""Regression tests for garage/prints/derive_prints.py's per-size crop and
border geometry — see CLAUDE.md's "encode the decision as a test" convention.
Source of the requirement: garage/research/joshballart-phase0-print-partner-
2026-07-21.md ("crop differently per size") plus
garage/research/print-border-mat-compatibility-2026-07-25.md (borders sized
to a real ~0.25in standard mat overlap, not generic no-mat print margins):
8x10 = 0.3in on all four sides; 11x14 = 0.5in left/right/top, 0.625in
bottom; 16x20 = 1.0in left/right/top, 1.125in bottom (bottom-weighted mat
convention). The image must never be stretched/warped to fit.
"""

import importlib.util
import sys
from pathlib import Path

import pytest
from PIL import Image

MODULE_PATH = Path(__file__).parent.parent / "garage" / "prints" / "derive_prints.py"
DPI = 300
FILL = (200, 30, 30)  # solid, non-white fill so border vs. content is unambiguous


def _load_module():
    spec = importlib.util.spec_from_file_location("derive_prints", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def dp(tmp_path, monkeypatch):
    module = _load_module()
    monkeypatch.setattr(module, "READY", tmp_path / "ready")
    monkeypatch.setattr(module, "PROOFS", tmp_path / "proofs")
    return module


def _is_white(px):
    return all(c >= 245 for c in px)


def _is_fill(px):
    return all(abs(c - f) <= 15 for c, f in zip(px, FILL))


def _make_source(tmp_path, name, w, h):
    path = tmp_path / name
    Image.new("RGB", (w, h), FILL).save(path)
    return path


def _assert_borders(sheet_path, sw_in, sh_in, border_left, border_top,
                     border_right, border_bottom):
    """Open the produced sheet and check each edge's border matches spec."""
    img = Image.open(sheet_path).convert("RGB")
    w_px, h_px = img.size
    assert w_px == round(sw_in * DPI)
    assert h_px == round(sh_in * DPI)
    cx, cy = w_px // 2, h_px // 2
    probe = 10  # px offset from the expected border/content boundary

    left_px = round(border_left * DPI)
    assert _is_white(img.getpixel((left_px - probe, cy)))
    assert _is_fill(img.getpixel((left_px + probe, cy)))

    right_px = w_px - round(border_right * DPI)
    assert _is_white(img.getpixel((right_px + probe, cy)))
    assert _is_fill(img.getpixel((right_px - probe, cy)))

    top_px = round(border_top * DPI)
    assert _is_white(img.getpixel((cx, top_px - probe)))
    assert _is_fill(img.getpixel((cx, top_px + probe)))

    bottom_px = h_px - round(border_bottom * DPI)
    assert _is_white(img.getpixel((cx, bottom_px + probe)))
    assert _is_fill(img.getpixel((cx, bottom_px - probe)))


@pytest.mark.parametrize("w, h", [(6000, 6000), (4500, 6000), (6000, 4500)])
def test_8x10_border_uniform_all_sides(dp, tmp_path, w, h):
    """8x10 gets 0.3in on every side, regardless of the source photo's shape."""
    src = _make_source(tmp_path, f"src_{w}x{h}.jpg", w, h)
    dp.derive(src)
    sheet = dp.READY / src.stem / "8x10.jpg"
    landscape = w >= h
    sw_in, sh_in = (10, 8) if landscape else (8, 10)
    _assert_borders(sheet, sw_in, sh_in, 0.3, 0.3, 0.3, 0.3)


@pytest.mark.parametrize("name, w, h", [
    ("11x14", 6000, 6000), ("11x14", 4500, 6000), ("11x14", 6000, 4500),
    ("16x20", 6000, 6000), ("16x20", 4500, 6000), ("16x20", 6000, 4500),
])
def test_11x14_and_16x20_bottom_weighted(dp, tmp_path, name, w, h):
    """11x14/16x20 keep a light bottom-weighted mat touch — bottom border is
    always 0.125in more than left/right/top, never equal to them."""
    src = _make_source(tmp_path, f"src_{name}_{w}x{h}.jpg", w, h)
    dp.derive(src)
    sheet = dp.READY / src.stem / f"{name}.jpg"
    long_side = {"11x14": 14, "16x20": 20}[name]
    short_side = {"11x14": 11, "16x20": 16}[name]
    border_lrt = {"11x14": 0.5, "16x20": 1.0}[name]
    border_bottom = {"11x14": 0.625, "16x20": 1.125}[name]
    landscape = w >= h
    sw_in, sh_in = (long_side, short_side) if landscape else (short_side, long_side)
    _assert_borders(sheet, sw_in, sh_in, border_lrt, border_lrt, border_lrt, border_bottom)


def test_crop_never_stretches_aspect_ratio(dp, tmp_path):
    """The cropped region must already match the sheet's content ratio before
    scaling — scaling is then uniform (same factor both axes), so nothing
    gets stretched out of shape."""
    src = _make_source(tmp_path, "src_stretch_check.jpg", 4500, 6000)
    dp.derive(src)
    for name, sw, sh, b_lrt, b_bottom in dp.SHEETS:
        sheet_path = dp.READY / src.stem / f"{name}.jpg"
        img = Image.open(sheet_path)
        content_w = img.width - 2 * round(b_lrt * DPI)
        content_h = img.height - round(b_lrt * DPI) - round(b_bottom * DPI)
        expected_ratio = (sw - 2 * b_lrt) / (sh - b_lrt - b_bottom)
        actual_ratio = content_w / content_h
        assert actual_ratio == pytest.approx(expected_ratio, rel=0.01)


def test_excellent_tier_still_downsamples_to_300dpi(dp, tmp_path):
    """A comfortably high-res master must still land on the standard 300 DPI
    grid + 300 DPI tag, unchanged by the never-upscale fix — this is a
    no-regression check on the untouched >=300 DPI branch."""
    src = _make_source(tmp_path, "src_excellent.jpg", 6000, 6000)
    dp.derive(src)
    landscape = True  # square source, iw >= ih
    for name, s_short, s_long, b_lrt, b_bottom in dp.SHEETS:
        sw_in, sh_in = (s_long, s_short) if landscape else (s_short, s_long)
        img = Image.open(dp.READY / src.stem / f"{name}.jpg")
        assert img.size == (round(sw_in * DPI), round(sh_in * DPI))
        assert img.info["dpi"] == pytest.approx((DPI, DPI), abs=1)


def test_acceptable_tier_ships_native_resolution_no_upscale(dp, tmp_path):
    """A crop landing in the 200-299 DPI band must not be upscaled to 300;
    the sheet ships at the crop's own true eff_dpi instead."""
    # Sized so 16x20's eff_dpi lands exactly on 250.0; 8x10 (~473) and
    # 11x14 (~347) for this same source are safely excellent, isolating the
    # acceptable-tier behavior to just the one size.
    src = _make_source(tmp_path, "src_acceptable.jpg", 3500, 4469)
    dp.derive(src)
    sheet_path = dp.READY / src.stem / "16x20.jpg"
    img = Image.open(sheet_path)
    assert img.size == (4000, 5000)  # 16*250, 20*250 -- NOT 16*300, 20*300
    assert img.info["dpi"] == pytest.approx((250, 250), abs=1)


def test_fail_tier_writes_do_not_sell_file(dp, tmp_path):
    """A crop below 200 DPI must not produce a plain, sellable ready file --
    it's saved under a DO-NOT-SELL name instead, and noted in the report.
    Other sizes for the same master are unaffected, proving the FAIL branch
    is isolated to the one undersized dimension."""
    # Sized so 16x20's eff_dpi lands exactly on 150.0; 8x10 (~283.8) and
    # 11x14 (~208.2) for this same source are both "acceptable" and must
    # still be written normally.
    src = _make_source(tmp_path, "src_fail.jpg", 2100, 2681)
    report = dp.derive(src)
    out_dir = dp.READY / src.stem
    assert not (out_dir / "16x20.jpg").exists()
    assert (out_dir / "16x20_DO-NOT-SELL.jpg").exists()
    assert any("16x20" in line and "FAIL" in line and "DO-NOT-SELL" in line for line in report)
    assert (out_dir / "8x10.jpg").exists()
    assert (out_dir / "11x14.jpg").exists()
