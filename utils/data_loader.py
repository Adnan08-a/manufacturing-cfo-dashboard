"""
data_loader.py
---------------
Loading, cleaning, enrichment, and filtering of the manufacturing dataset.

The dashboard ships with a bundled sample dataset (data/manufacturing_company_dataset.xlsx)
but also accepts a user-uploaded .xlsx/.csv file with the same schema, so the app
keeps working for any similarly-shaped manufacturing dataset.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence, Tuple

import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------------
# Paths & schema
# ----------------------------------------------------------------------------
APP_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = APP_ROOT / "data" / "manufacturing_company_dataset.xlsx"

REQUIRED_COLUMNS = [
    "Date", "Region", "Product", "Revenue", "Cost", "Profit", "Units Sold",
    "Customer Satisfaction", "Manufacturing Cost", "Labor Hours",
    "Machine Downtime (hours)", "Inventory Levels", "Order Lead Time (days)",
    "Return Rate (%)", "On-Time Delivery (%)",
]


# ----------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading manufacturing data...")
def load_data(uploaded_file=None) -> pd.DataFrame:
    """Load and enrich the manufacturing dataset.

    Parameters
    ----------
    uploaded_file:
        An optional Streamlit ``UploadedFile`` (.xlsx or .csv). When ``None``,
        the bundled sample dataset is used instead.
    """
    if uploaded_file is not None:
        name = uploaded_file.name.lower()
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_excel(DEFAULT_DATA_PATH)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            "The dataset is missing required column(s): " + ", ".join(missing)
        )

    return _enrich(df)


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived time and financial fields used throughout the app."""
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # Time helpers
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    df["MonthLabel"] = df["Date"].dt.strftime("%b %Y")
    df["Quarter"] = df["Date"].dt.to_period("Q").astype(str)
    df["Weekday"] = df["Date"].dt.day_name()

    # --- Financial KPI methodology -----------------------------------------
    # Gross Profit  = Revenue - COGS ("Cost")
    # EBITDA        = Gross Profit - Operating Expenses ("Manufacturing Cost")
    # Net Profit    = the dataset's reported "Profit" figure, used as-is
    # (See the Methodology note on the Executive Summary page for details.)
    df["Gross Profit"] = df["Revenue"] - df["Cost"]
    df["Gross Margin %"] = (df["Gross Profit"] / df["Revenue"]) * 100
    df["EBITDA"] = df["Gross Profit"] - df["Manufacturing Cost"]
    df["EBITDA Margin %"] = (df["EBITDA"] / df["Revenue"]) * 100
    df["Net Margin %"] = (df["Profit"] / df["Revenue"]) * 100
    df["Avg Order Value"] = df["Revenue"] / df["Units Sold"].replace(0, pd.NA)

    return df


# ----------------------------------------------------------------------------
# Filtering
# ----------------------------------------------------------------------------
def filter_data(
    df: pd.DataFrame,
    date_range: Optional[Tuple] = None,
    regions: Optional[Sequence[str]] = None,
    products: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """Apply the global Date / Region / Product filters."""
    out = df.copy()

    if date_range and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        out = out[(out["Date"] >= start) & (out["Date"] <= end)]

    if regions:
        out = out[out["Region"].isin(regions)]

    if products:
        out = out[out["Product"].isin(products)]

    return out


def get_prior_period(df: pd.DataFrame, date_range: Tuple) -> pd.DataFrame:
    """Return rows for the period immediately preceding ``date_range``,
    matched to the same length, for period-over-period comparisons."""
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    period_length = end - start
    prior_end = start - pd.Timedelta(days=1)
    prior_start = prior_end - period_length
    return df[(df["Date"] >= prior_start) & (df["Date"] <= prior_end)]


def get_year_ago_period(df: pd.DataFrame, date_range: Tuple) -> pd.DataFrame:
    """Return rows for the same calendar window one year earlier (YoY)."""
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    try:
        start_ya = start.replace(year=start.year - 1)
        end_ya = end.replace(year=end.year - 1)
    except ValueError:
        # Handles Feb 29 edge case
        start_ya = start - pd.DateOffset(years=1)
        end_ya = end - pd.DateOffset(years=1)
    return df[(df["Date"] >= start_ya) & (df["Date"] <= end_ya)]
