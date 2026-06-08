"""
data_loader.py
==============
Load daily closing-price series for analysis, from a local CSV or from
Yahoo! Finance (the original data source).
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pandas as pd


def load_csv(path: str, date_col: str = "Date", price_col: str = "Close") -> pd.DataFrame:
    """
    Load a price series from a CSV with at least a date and a close column.

    Returns a DataFrame with columns ['Date', 'Close'] sorted by date.
    """
    df = pd.read_csv(path)
    df = df[[date_col, price_col]].rename(columns={date_col: "Date", price_col: "Close"})
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.dropna().sort_values("Date").reset_index(drop=True)
    return df


def load_yahoo(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Download daily closing prices from Yahoo! Finance.

    Requires `yfinance` (pip install yfinance). Returns ['Date', 'Close'].
    """
    try:
        import yfinance as yf
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install yfinance to use load_yahoo: pip install yfinance") from exc

    raw = yf.download(ticker, start=start, end=end, progress=False)
    df = raw.reset_index()[["Date", "Close"]]
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.dropna().sort_values("Date").reset_index(drop=True)
    return df
