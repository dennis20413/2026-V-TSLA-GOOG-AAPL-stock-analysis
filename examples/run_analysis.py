"""
run_analysis.py
===============
Example: fetch a price series, segment it, print diagnostics, export results.

Usage:
    python run_analysis.py                 # uses bundled sample data
    python run_analysis.py --ticker AAPL --start 2026-01-02 --end 2026-03-04
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd

from piecewise_regression import auto_segment, fit_segments, summary_table
from report import segments_to_frame, to_excel


# AAPL daily closes, 2026-01-02 .. 2026-03-03 (Yahoo! Finance). Used as a
# self-contained example so the script runs without a network connection.
SAMPLE_AAPL = [
    271.01, 267.26, 262.36, 260.33, 259.04, 259.37, 260.25, 261.05, 259.96,
    258.21, 255.53, 246.70, 247.65, 248.35, 248.04, 255.41, 258.27, 256.44,
    258.28, 259.48, 270.01, 269.48, 276.49, 275.91, 278.12, 274.62, 273.68,
    275.50, 261.73, 255.78, 263.88, 264.35, 260.58, 264.58, 266.18, 272.14,
    274.23, 272.95, 264.18, 264.72, 263.75,
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Piecewise linear regression on a price series.")
    parser.add_argument("--ticker", help="Yahoo! Finance ticker (requires yfinance).")
    parser.add_argument("--start", help="Start date YYYY-MM-DD.")
    parser.add_argument("--end", help="End date YYYY-MM-DD.")
    parser.add_argument("--min-len", type=int, default=6, help="Minimum points per segment.")
    parser.add_argument("--max-segments", type=int, default=8, help="Maximum number of segments.")
    parser.add_argument("--out", default="output.xlsx", help="Excel output path.")
    args = parser.parse_args()

    if args.ticker:
        from data_loader import load_yahoo
        prices = load_yahoo(args.ticker, args.start, args.end)
        label = args.ticker
    else:
        prices = pd.DataFrame({
            "Date": pd.bdate_range("2026-01-02", periods=len(SAMPLE_AAPL)),
            "Close": SAMPLE_AAPL,
        })
        label = "AAPL (sample)"

    segments = auto_segment(
        prices["Close"].tolist(),
        min_len=args.min_len,
        max_segments=args.max_segments,
    )

    print(f"\nPiecewise linear regression — {label}")
    print(f"{len(prices)} points -> {len(segments)} segments\n")
    print(summary_table(segments))

    to_excel(args.out, prices, segments)
    print(f"\nWrote diagnostics to {args.out}")


if __name__ == "__main__":
    main()
