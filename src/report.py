"""
report.py
=========
Export piecewise-regression results to Excel and render a chart with the
fitted segment lines overlaid on the price series.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd

from piecewise_regression import SegmentFit


def segments_to_frame(segments: Sequence[SegmentFit], dates: Sequence = None) -> pd.DataFrame:
    """Build a tidy diagnostics DataFrame, one row per segment."""
    rows = []
    for s in segments:
        row = {
            "Line": s.index,
            "Data Number": s.n,
            "Intercept": round(s.intercept, 6),
            "Slope": round(s.slope, 6),
            "R2": round(s.r2, 6),
            "MSE": round(s.mse, 6),
            "Estimated Sigma": round(s.sigma, 6),
        }
        if dates is not None:
            row["Start Date"] = pd.to_datetime(dates[s.start]).date()
            row["End Date"] = pd.to_datetime(dates[s.end]).date()
        rows.append(row)
    return pd.DataFrame(rows)


def to_excel(path: str, prices: pd.DataFrame, segments: Sequence[SegmentFit]) -> None:
    """Write prices + per-segment diagnostics to an Excel workbook."""
    diag = segments_to_frame(segments, dates=prices["Date"].tolist())
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        prices.to_excel(writer, sheet_name="Prices", index=False)
        diag.to_excel(writer, sheet_name="Segments", index=False)


def plot(prices: pd.DataFrame, segments: Sequence[SegmentFit], title: str = "", save: str = None):
    """Plot the closing price with each fitted segment line overlaid."""
    import matplotlib.pyplot as plt

    y = prices["Close"].to_numpy(dtype=float)
    x = np.arange(1, len(y) + 1)

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(x, y, color="#444", lw=1.2, label="Close")

    for s in segments:
        xs = np.arange(1, s.n + 1)
        seg_x = x[s.start:s.end + 1]
        ax.plot(seg_x, s.predict(xs), lw=2.2, label=f"Seg {s.index} (R²={s.r2:.2f})")

    ax.set_title(title)
    ax.set_xlabel("Trading day")
    ax.set_ylabel("Close (USD)")
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    if save:
        fig.savefig(save, dpi=150)
    return fig
