# Piecewise Linear Regression — Equity Trend Analysis

Rolling **piecewise linear regression** ("lines combined analysis") of four major
US equities — **AAPL, GOOG, TSLA, V** — using real daily closing prices from
Yahoo! Finance (2026). Each price series is decomposed into statistically
distinct linear **trend segments**, each fit with ordinary least squares and
reported with full regression diagnostics.

This project reimplements, in open and reproducible Python, the methodology
behind a proprietary Windows analysis tool. The per-segment statistics
**exactly match** the reference tool's Excel output (validated in `tests/`).

> ⚠️ Academic / personal research project. Not investment advice.

---

## 📈 Data

| | |
|---|---|
| **Tickers** | AAPL, GOOG, TSLA, V |
| **Source** | Yahoo! Finance |
| **Frequency** | Daily closing price (USD) |
| **Period** | January 2, 2026 onward (rolling, updated weekly) |

## 🧠 Methodology

Each price series is split into contiguous windows where a single linear trend
holds. An OLS line `Y = a + b·X` is fit to each segment, with diagnostics:

| Metric | Definition |
|--------|------------|
| `SST`   | Σ(y − ȳ)²  — total sum of squares |
| `SSR`   | Σ(ŷ − ȳ)²  — regression sum of squares |
| `SSE`   | Σ(y − ŷ)²  — error sum of squares |
| `R²`    | SSR / SST |
| `MSE`   | SSE / (n − 2) |
| `σ̂`     | √MSE |

Two segmentation strategies are provided:

- **`fit_segments(y, breakpoints)`** — fits OLS to a *known* set of segments.
  Reproduces the reference tool's exact Excel numbers when given its breakpoints.
- **`auto_segment(y, min_len, max_segments)`** — detects breakpoints itself, using
  **dynamic programming** to find the partition that minimizes total SSE subject
  to a minimum segment length. A principled, fully reproducible stand-in for the
  reference tool's AI-driven breakpoint search.

## 📊 Selected Results (real fitted segments)

| Ticker | Segment | Slope | R² | Trend read |
|--------|:-------:|:-----:|:----:|------------|
| **GOOG** | 1 | +3.07 | **0.941** | Strong uptrend — durable Search / ad-market strength |
| **AAPL** | 2 | +1.82 | 0.869 | Steady advance on positive analyst commentary |
| **V**    | 5 | +2.74 | **0.912** | Defensive rotation into quality compounders |
| **TSLA** | 2 | −0.17 | 0.003 | Effectively flat — no reliable trend (low R²) |

Low-R² segments are reported honestly rather than over-fitted — the diagnostics
distinguish genuine trends from noise.

## ⚙️ Install

```bash
pip install -r requirements.txt
```

## 🚀 Quick start

```bash
# Run on bundled sample data (no network needed)
python examples/run_analysis.py

# Or pull live data from Yahoo! Finance
python examples/run_analysis.py --ticker AAPL --start 2026-01-02 --end 2026-03-04
```

```python
from piecewise_regression import auto_segment, fit_segments, summary_table

prices = [271.01, 267.26, 262.36, ...]      # daily closes

# Automatic breakpoint detection
segments = auto_segment(prices, min_len=6, max_segments=8)
print(summary_table(segments))

# Or reproduce an exact known segmentation
segments = fit_segments(prices, breakpoints=[11, 20, 28, 35])
```

## ✅ Validation

```bash
python tests/test_regression.py
```

Reconstructs AAPL's 2026-03-04 worksheet and confirms the fitted intercept,
slope, R², MSE, and σ̂ match the reference output to 1e-5.

## 🗂️ Project layout

```
src/
  piecewise_regression.py   # core fitting + diagnostics + DP segmentation
  data_loader.py            # CSV / Yahoo! Finance loaders
  report.py                 # Excel export + fitted-line plots
examples/
  run_analysis.py           # CLI runner
tests/
  test_regression.py        # validates against reference output
```

---
**Author:** Dennis Chen (陳雲皓) · [LinkedIn](https://linkedin.com/in/dennischen2507) · [GitHub](https://github.com/dennis20413)
