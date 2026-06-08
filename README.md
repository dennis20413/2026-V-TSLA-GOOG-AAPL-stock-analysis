# Piecewise Linear Regression — Rolling Equity Trend Analysis

Rolling **weekly piecewise linear regression** analysis of four major US equities — **AAPL, GOOG, TSLA, V** — using real daily closing prices from Yahoo! Finance (2026). Each equity's price series is decomposed into statistically distinct linear trend segments, with full regression diagnostics and a narrative explanation per segment.

> ⚠️ Academic / personal research project. Not investment advice.

---

## 🎯 Objective

Turn noisy daily price series into **interpretable trend regimes**: detect where the underlying linear trend changes, fit a separate regression to each segment, and quantify the strength of each trend with standard diagnostics (R², MSE, σ).

## 📈 Data

| | |
|---|---|
| **Tickers** | AAPL, GOOG, TSLA, V |
| **Source** | Yahoo! Finance |
| **Frequency** | Daily closing price (USD) |
| **Period** | January 2, 2026 onward (rolling, updated weekly) |
| **Snapshots** | One worksheet per week (e.g., `20260304`, `20260311`, …) |

## 🧠 Methodology

1. **Ingest** daily closing prices per ticker.
2. **Segment** the series into contiguous windows where a single linear trend holds (breakpoint detection).
3. **Fit** an ordinary least-squares line `Y = a + bX` to each segment independently.
4. **Diagnose** each segment with R², MSE, estimated σ, and the SST / SSR / SSE decomposition.
5. **Annotate** each segment with a qualitative driver (e.g., macro, sector, company-specific news).
6. **Report** results as Excel workbooks and PowerPoint summaries, refreshed weekly.

## 📊 Selected Results (real fitted segments)

| Ticker | Segment | Slope | R² | Trend read |
|--------|:-------:|:-----:|:----:|------------|
| **GOOG** | 1 | +3.07 | **0.941** | Strong uptrend — durable Search / ad-market strength |
| **AAPL** | 2 | +1.82 | 0.869 | Steady advance on positive analyst commentary |
| **V**    | 5 | +2.74 | **0.912** | Defensive rotation into quality compounders |
| **TSLA** | 2 | −0.17 | 0.003 | Effectively flat — no reliable trend (low R²) |

*Low-R² segments (e.g., TSLA's flat week) are reported honestly rather than over-fitted — the diagnostics distinguish genuine trends from noise.*

## 🗂️ Repository Contents

```
.
├── AAPL.xlsx     # per-week regression workbooks (prices, fitted line, segment diagnostics)
├── GOOG.xlsx
├── TSLA.xlsx
├── V.xlsx
├── AAPL.pptx     # weekly chart + narrative summary decks
├── GOOG.pptx
├── TSLA.pptx
├── V.pptx
└── README.md
```

Each workbook sheet reports, per segment: **Data Number, Intercept, Slope, R², MSE, Estimated Sigma, Start/End Date, and Factors/Reasons.**

## 🧰 Tech Stack

`Python` · `pandas` · `NumPy` · `statsmodels` / least-squares regression · `Excel` · `PowerPoint`

## 📌 Roadmap
- [ ] Add the Python source that generates the segmentation and diagnostics (`src/`)
- [ ] Publish reproducible notebooks with fitted-line overlays on price charts
- [ ] Add out-of-sample validation of detected breakpoints
- [ ] Backtest a simple trend-following signal derived from segment slopes

---
**Author:** Dennis Chen (陳雲皓) · [LinkedIn](https://linkedin.com/in/dennischen2507) · [GitHub](https://github.com/dennis20413)
