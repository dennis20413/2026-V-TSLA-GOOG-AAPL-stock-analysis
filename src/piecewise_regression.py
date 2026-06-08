"""
piecewise_regression.py
=======================
Piecewise linear regression ("lines combined analysis") for equity price series.

A price series is decomposed into contiguous linear trend segments. Each segment
is fit with ordinary least squares, and standard diagnostics are reported:

    Intercept, Slope, R2, MSE, Estimated Sigma, SST, SSR, SSE

The per-segment statistics exactly reproduce the reference Windows tool used to
generate the original Excel workbooks:

    SST   = sum((y - mean(y))**2)          total sum of squares
    SSR   = sum((yhat - mean(y))**2)       regression sum of squares
    SSE   = sum((y - yhat)**2)             error sum of squares
    R2    = SSR / SST
    MSE   = SSE / (n - 2)                  unbiased residual variance
    sigma = sqrt(MSE)

Two segmentation strategies are provided:

    1. fit_segments(...)        - fit given a known list of breakpoints
                                  (reproduces the exact reference output)
    2. auto_segment(...)        - automatically detect breakpoints via optimal
                                  dynamic-programming partitioning subject to a
                                  minimum-segment-length constraint
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

import numpy as np


@dataclass
class SegmentFit:
    """Diagnostics for a single fitted line segment."""
    index: int          # 1-based segment number
    start: int          # 0-based start index (inclusive)
    end: int            # 0-based end index (inclusive)
    n: int
    intercept: float
    slope: float
    r2: float
    mse: float
    sigma: float
    sst: float
    ssr: float
    sse: float

    @property
    def equation(self) -> str:
        return f"Y = {self.intercept:.6f} + {self.slope:.6f}*X"

    def predict(self, x: np.ndarray) -> np.ndarray:
        return self.intercept + self.slope * x


def _ols(x: np.ndarray, y: np.ndarray) -> SegmentFit:
    """Fit a single OLS line to (x, y) and compute reference diagnostics."""
    n = len(y)
    if n < 2:
        raise ValueError("A segment needs at least 2 points.")

    slope, intercept = np.polyfit(x, y, 1)
    yhat = intercept + slope * x
    ybar = y.mean()

    sst = float(np.sum((y - ybar) ** 2))
    ssr = float(np.sum((yhat - ybar) ** 2))
    sse = float(np.sum((y - yhat) ** 2))
    r2 = ssr / sst if sst > 0 else 0.0
    mse = sse / (n - 2) if n > 2 else 0.0
    sigma = float(np.sqrt(mse))

    return SegmentFit(
        index=0, start=0, end=0, n=n,
        intercept=float(intercept), slope=float(slope),
        r2=r2, mse=mse, sigma=sigma, sst=sst, ssr=ssr, sse=sse,
    )


def fit_segments(y: Sequence[float], breakpoints: Sequence[int]) -> List[SegmentFit]:
    """
    Fit independent OLS lines to segments defined by `breakpoints`.

    Parameters
    ----------
    y : sequence of float
        The series values (e.g., daily closing prices), ordered in time.
    breakpoints : sequence of int
        0-based indices marking the FIRST point of each new segment after the
        first. For a series split as [0..10], [11..19], [20..27] pass [11, 20].

    Returns
    -------
    list of SegmentFit
    """
    y = np.asarray(y, dtype=float)
    n = len(y)
    bounds = [0, *sorted(breakpoints), n]
    segments: List[SegmentFit] = []

    for i in range(len(bounds) - 1):
        s, e = bounds[i], bounds[i + 1]            # [s, e)
        ys = y[s:e]
        xs = np.arange(1, len(ys) + 1, dtype=float)  # local X = 1..m
        fit = _ols(xs, ys)
        fit.index = i + 1
        fit.start = s
        fit.end = e - 1
        segments.append(fit)

    return segments


def _segment_sse(y: np.ndarray) -> float:
    """SSE of a single OLS line fit to y (X = 1..n). Used by the DP optimizer."""
    n = len(y)
    if n < 2:
        return 0.0
    x = np.arange(1, n + 1, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    yhat = intercept + slope * x
    return float(np.sum((y - yhat) ** 2))


def auto_segment(
    y: Sequence[float],
    min_len: int = 6,
    max_segments: int = 8,
) -> List[SegmentFit]:
    """
    Automatically partition the series into linear segments.

    Uses dynamic programming to find the partition (into up to `max_segments`
    pieces, each at least `min_len` points) that minimizes total SSE. This is a
    principled, fully reproducible stand-in for the reference tool's AI-driven
    breakpoint search, which selects breakpoints to maximize overall accuracy.

    Parameters
    ----------
    y : sequence of float
    min_len : int
        Minimum number of points per segment.
    max_segments : int
        Maximum number of segments to allow.

    Returns
    -------
    list of SegmentFit
    """
    y = np.asarray(y, dtype=float)
    n = len(y)

    # Precompute SSE for every candidate segment [i, j).
    cost = np.full((n + 1, n + 1), np.inf)
    for i in range(n):
        for j in range(i + min_len, n + 1):
            cost[i, j] = _segment_sse(y[i:j])

    # dp[k][i] = min total SSE to cover y[0:i] using exactly k segments.
    INF = np.inf
    dp = np.full((max_segments + 1, n + 1), INF)
    back = np.full((max_segments + 1, n + 1), -1, dtype=int)
    dp[0, 0] = 0.0

    for k in range(1, max_segments + 1):
        for i in range(1, n + 1):
            for j in range(0, i - min_len + 1):
                if dp[k - 1, j] + cost[j, i] < dp[k, i]:
                    dp[k, i] = dp[k - 1, j] + cost[j, i]
                    back[k, i] = j

    # Choose the segment count with the best total SSE that fully covers the data.
    best_k = min(
        (k for k in range(1, max_segments + 1) if np.isfinite(dp[k, n])),
        key=lambda k: dp[k, n],
        default=1,
    )

    # Reconstruct breakpoints.
    cuts = []
    i, k = n, best_k
    while k > 0:
        j = back[k, i]
        cuts.append(j)
        i, k = j, k - 1
    cuts = sorted(set(cuts) - {0})

    return fit_segments(y, cuts)


def summary_table(segments: Sequence[SegmentFit]) -> str:
    """Return a plain-text diagnostics table matching the reference layout."""
    header = (
        f"{'Line':>4} {'N':>4} {'Intercept':>12} {'Slope':>10} "
        f"{'R2':>9} {'MSE':>10} {'Sigma':>9}"
    )
    rows = [header, "-" * len(header)]
    for s in segments:
        rows.append(
            f"{s.index:>4} {s.n:>4} {s.intercept:>12.6f} {s.slope:>10.6f} "
            f"{s.r2:>9.6f} {s.mse:>10.6f} {s.sigma:>9.6f}"
        )
    return "\n".join(rows)
