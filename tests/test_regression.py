"""
test_regression.py
===================
Validates that the per-segment diagnostics exactly reproduce the reference
Windows tool's Excel output (AAPL, week of 2026-03-04).

Run:  python -m pytest tests/ -v   (or)   python tests/test_regression.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from piecewise_regression import fit_segments

# AAPL 2026-03-04 worksheet: 41 closing prices.
AAPL = [
    271.01, 267.26, 262.36, 260.33, 259.04, 259.37, 260.25, 261.05, 259.96,
    258.21, 255.53, 246.70, 247.65, 248.35, 248.04, 255.41, 258.27, 256.44,
    258.28, 259.48, 270.01, 269.48, 276.49, 275.91, 278.12, 274.62, 273.68,
    275.50, 261.73, 255.78, 263.88, 264.35, 260.58, 264.58, 266.18, 272.14,
    274.23, 272.95, 264.18, 264.72, 263.75,
]

# Reference breakpoints (0-based first index of each new segment): the tool
# split this series as [1-11], [12-20], [21-28], [29-35], [36-41].
BREAKPOINTS = [11, 20, 28, 35]

# Expected diagnostics from the reference Excel (segment 1).
EXPECTED_SEG1 = dict(
    intercept=267.750909, slope=-1.074091, r2=0.680435,
    mse=6.622224, sigma=2.573368,
)


def test_segment1_matches_reference():
    segs = fit_segments(AAPL, BREAKPOINTS)
    s = segs[0]
    assert abs(s.intercept - EXPECTED_SEG1["intercept"]) < 1e-5
    assert abs(s.slope - EXPECTED_SEG1["slope"]) < 1e-5
    assert abs(s.r2 - EXPECTED_SEG1["r2"]) < 1e-5
    assert abs(s.mse - EXPECTED_SEG1["mse"]) < 1e-5
    assert abs(s.sigma - EXPECTED_SEG1["sigma"]) < 1e-5
    assert s.n == 11


def test_segment_count():
    segs = fit_segments(AAPL, BREAKPOINTS)
    assert len(segs) == 5
    assert [s.n for s in segs] == [11, 9, 8, 7, 6]


if __name__ == "__main__":
    test_segment1_matches_reference()
    test_segment_count()
    print("All tests passed - diagnostics match the reference output.")
