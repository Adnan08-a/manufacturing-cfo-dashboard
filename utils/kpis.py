"""
kpis.py
-------
Computation of headline FP&A KPIs from a (filtered) dataframe.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd

KPI_KEYS = [
    "revenue", "cost", "gross_profit", "gross_margin", "ebitda",
    "ebitda_margin", "net_profit", "net_margin", "units_sold",
    "avg_order_value", "inventory_turns", "working_capital", "avg_inventory",
    "avg_satisfaction", "avg_on_time", "avg_return_rate", "avg_lead_time",
    "avg_downtime", "total_labor_hours", "record_count",
]


def empty_kpis() -> dict:
    return {k: 0.0 for k in KPI_KEYS}


def compute_kpis(df: pd.DataFrame) -> dict:
    """Aggregate headline KPIs over the given (already filtered) dataframe."""
    if df is None or df.empty:
        return empty_kpis()

    revenue = float(df["Revenue"].sum())
    cost = float(df["Cost"].sum())
    gross_profit = float(df["Gross Profit"].sum())
    manufacturing_cost = float(df["Manufacturing Cost"].sum())
    ebitda = gross_profit - manufacturing_cost
    net_profit = float(df["Profit"].sum())
    units_sold = float(df["Units Sold"].sum())
    avg_inventory = float(df["Inventory Levels"].mean())

    days = max((df["Date"].max() - df["Date"].min()).days, 1)
    inventory_turns = (cost / avg_inventory) * (365 / days) if avg_inventory else 0.0

    return {
        "revenue": revenue,
        "cost": cost,
        "gross_profit": gross_profit,
        "gross_margin": (gross_profit / revenue * 100) if revenue else 0.0,
        "ebitda": ebitda,
        "ebitda_margin": (ebitda / revenue * 100) if revenue else 0.0,
        "net_profit": net_profit,
        "net_margin": (net_profit / revenue * 100) if revenue else 0.0,
        "units_sold": units_sold,
        "avg_order_value": (revenue / units_sold) if units_sold else 0.0,
        "inventory_turns": inventory_turns,
        "working_capital": avg_inventory,
        "avg_inventory": avg_inventory,
        "avg_satisfaction": float(df["Customer Satisfaction"].mean()),
        "avg_on_time": float(df["On-Time Delivery (%)"].mean()),
        "avg_return_rate": float(df["Return Rate (%)"].mean()),
        "avg_lead_time": float(df["Order Lead Time (days)"].mean()),
        "avg_downtime": float(df["Machine Downtime (hours)"].mean()),
        "total_labor_hours": float(df["Labor Hours"].sum()),
        "record_count": float(len(df)),
    }


def pct_change(current: float, prior: Optional[float]) -> Optional[float]:
    """Percent change of current vs prior; None when prior is unusable."""
    if prior is None or prior == 0 or pd.isna(prior):
        return None
    return (current - prior) / abs(prior) * 100


def pp_change(current: float, prior: Optional[float]) -> Optional[float]:
    """Percentage-point change (for already-percent metrics like margins)."""
    if prior is None or pd.isna(prior):
        return None
    return current - prior
