"""
forecasting.py
---------------
Monthly time-series forecasting helpers for the Forecasting page.

Primary model: Holt-Winters exponential smoothing (trend + seasonal) via
statsmodels, which handles the trend/seasonality typical of revenue series.
Falls back to a simple linear trend extrapolation when there isn't enough
history for a seasonal model (statsmodels needs >= 2 full seasonal cycles).
"""
from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd


def monthly_series(df: pd.DataFrame, value_col: str = "Revenue") -> pd.Series:
    s = df.groupby("Month")[value_col].sum().sort_index()
    s.index = pd.DatetimeIndex(s.index)
    return s


def forecast_linear(series: pd.Series, periods: int) -> pd.DataFrame:
    """Simple linear-trend forecast with a naive +/-1 std-dev confidence band."""
    y = series.values.astype(float)
    x = np.arange(len(y))
    if len(y) < 2:
        flat = np.repeat(y[-1] if len(y) else 0, periods)
        future_idx = _future_index(series.index, periods)
        return pd.DataFrame({"forecast": flat, "lower": flat, "upper": flat}, index=future_idx)

    coeffs = np.polyfit(x, y, 1)
    trend = np.poly1d(coeffs)
    resid_std = float(np.std(y - trend(x))) if len(y) > 2 else float(np.std(y)) * 0.3

    future_x = np.arange(len(y), len(y) + periods)
    forecast = trend(future_x)
    forecast = np.clip(forecast, a_min=0, a_max=None)

    future_idx = _future_index(series.index, periods)
    return pd.DataFrame({
        "forecast": forecast,
        "lower": np.clip(forecast - 1.28 * resid_std, 0, None),
        "upper": forecast + 1.28 * resid_std,
    }, index=future_idx)


def forecast_holt_winters(series: pd.Series, periods: int, seasonal_periods: int = 12) -> Tuple[pd.DataFrame, str]:
    """Returns (forecast_df, model_used). Falls back to linear trend when the
    series is too short for a reliable seasonal model."""
    if len(series) < seasonal_periods * 2:
        return forecast_linear(series, periods), "Linear trend (insufficient history for seasonality)"

    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        model = ExponentialSmoothing(
            series, trend="add", seasonal="add", seasonal_periods=seasonal_periods,
            initialization_method="estimated",
        ).fit()
        forecast = model.forecast(periods)
        resid_std = float(np.std(model.resid))

        future_idx = _future_index(series.index, periods)
        df = pd.DataFrame({
            "forecast": np.clip(forecast.values, 0, None),
            "lower": np.clip(forecast.values - 1.28 * resid_std, 0, None),
            "upper": forecast.values + 1.28 * resid_std,
        }, index=future_idx)
        return df, "Holt-Winters (trend + seasonal)"
    except Exception:
        return forecast_linear(series, periods), "Linear trend (model fallback)"


def _future_index(index: pd.DatetimeIndex, periods: int) -> pd.DatetimeIndex:
    last = pd.Timestamp(index[-1])
    return pd.date_range(last + pd.DateOffset(months=1), periods=periods, freq="MS")
