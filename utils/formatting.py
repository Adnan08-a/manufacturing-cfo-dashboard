"""
formatting.py
-------------
Small, dependency-free formatting helpers for executive-friendly numbers.
"""
from __future__ import annotations

from typing import Optional


def format_currency(value: Optional[float], decimals: int = 1) -> str:
    if value is None:
        return "--"
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000_000:
        return f"{sign}${value / 1_000_000_000:.{decimals}f}B"
    if value >= 1_000_000:
        return f"{sign}${value / 1_000_000:.{decimals}f}M"
    if value >= 1_000:
        return f"{sign}${value / 1_000:.{decimals}f}K"
    return f"{sign}${value:.2f}"


def format_number(value: Optional[float], decimals: int = 0) -> str:
    if value is None:
        return "--"
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}{value / 1_000_000:.{max(decimals, 1)}f}M"
    if value >= 1_000:
        return f"{sign}{value / 1_000:.{max(decimals, 1)}f}K"
    return f"{sign}{value:,.{decimals}f}"


def format_pct(value: Optional[float], decimals: int = 1, signed: bool = False) -> str:
    if value is None:
        return "--"
    sign = "+" if (signed and value > 0) else ""
    return f"{sign}{value:.{decimals}f}%"


def format_delta(value: Optional[float], suffix: str = "%") -> str:
    """Small helper for st.metric-style deltas, e.g. '+3.2%' / '-1.4%'."""
    if value is None:
        return ""
    arrow = "▲" if value >= 0 else "▼"
    return f"{arrow} {abs(value):.1f}{suffix}"
