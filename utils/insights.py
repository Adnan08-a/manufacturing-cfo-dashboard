"""
insights.py
-----------
Two layers of "AI insight" generation:

1. A deterministic, rule-based commentary engine (`generate_executive_commentary`,
   `generate_insight_cards`) that runs entirely offline -- no API key required --
   by mining trends, outliers, and correlations from the filtered dataframe.

2. An optional live-LLM layer (`ask_claude`) that calls the Anthropic API for
   free-form Q&A when a key is available (via st.secrets or a session input).
   The dashboard works fully without this; it's an enhancement, not a dependency.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

from utils.kpis import compute_kpis, pct_change, pp_change
from utils.formatting import format_currency, format_pct

MODEL_NAME = "claude-sonnet-4-6"


# ----------------------------------------------------------------------------
# Rule-based executive commentary (Executive Summary page)
# ----------------------------------------------------------------------------
def generate_executive_commentary(df_curr: pd.DataFrame, df_prior: pd.DataFrame) -> list[str]:
    if df_curr.empty:
        return ["Not enough data in the selected filters to generate commentary."]

    kc = compute_kpis(df_curr)
    kp = compute_kpis(df_prior) if not df_prior.empty else None

    bullets = []

    # Revenue & profitability trend
    if kp:
        rev_chg = pct_change(kc["revenue"], kp["revenue"])
        if rev_chg is not None:
            verb = "grew" if rev_chg >= 0 else "declined"
            bullets.append(
                f"Revenue {verb} **{abs(rev_chg):.1f}%** versus the prior period to "
                f"**{format_currency(kc['revenue'])}**, with EBITDA margin at "
                f"**{format_pct(kc['ebitda_margin'])}** "
                f"({pp_change(kc['ebitda_margin'], kp['ebitda_margin']):+.1f} pts)."
            )
        else:
            bullets.append(f"Revenue for the period totaled **{format_currency(kc['revenue'])}**.")
    else:
        bullets.append(
            f"Revenue for the period totaled **{format_currency(kc['revenue'])}** with an "
            f"EBITDA margin of **{format_pct(kc['ebitda_margin'])}**."
        )

    # Top / bottom region
    by_region = df_curr.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
    if len(by_region) > 1:
        bullets.append(
            f"**{by_region.index[0]}** led all regions with "
            f"{format_currency(by_region.iloc[0])} in revenue, while "
            f"**{by_region.index[-1]}** trailed at {format_currency(by_region.iloc[-1])}."
        )

    # Top product by margin
    margin_by_product = (
        df_curr.groupby("Product").apply(
            lambda g: g["Gross Profit"].sum() / g["Revenue"].sum() * 100 if g["Revenue"].sum() else 0
        ).sort_values(ascending=False)
    )
    if len(margin_by_product) > 0:
        bullets.append(
            f"**{margin_by_product.index[0]}** carries the strongest gross margin at "
            f"**{margin_by_product.iloc[0]:.1f}%**, while "
            f"**{margin_by_product.index[-1]}** is lowest at {margin_by_product.iloc[-1]:.1f}%."
        )

    # Operational flags
    if kc["avg_on_time"] < 85:
        bullets.append(
            f"⚠️ On-time delivery averaged **{kc['avg_on_time']:.1f}%**, below the 85% service-level "
            f"target — a risk to customer retention if it persists."
        )
    if kc["avg_return_rate"] > 6:
        bullets.append(
            f"⚠️ Return rate is elevated at **{kc['avg_return_rate']:.1f}%**, worth a quality-control review."
        )
    if kc["inventory_turns"] < 4:
        bullets.append(
            f"Inventory is turning **{kc['inventory_turns']:.1f}x** annualized — slower turns tie up "
            f"working capital ({format_currency(kc['working_capital'])} average inventory on hand)."
        )

    return bullets


# ----------------------------------------------------------------------------
# Rule-based categorized insight cards (AI Insights page)
# ----------------------------------------------------------------------------
def generate_insight_cards(df: pd.DataFrame) -> list[dict]:
    """Returns a list of {category, tag, text} dicts spanning growth, risk,
    efficiency, and recommendation themes."""
    if df.empty or len(df) < 5:
        return [{"category": "recommendation", "tag": "Data",
                  "text": "Broaden the filters to generate richer insights — too few records selected."}]

    cards = []

    # --- Growth: best performing region/product combo ---
    combo = df.groupby(["Region", "Product"])["Revenue"].sum().sort_values(ascending=False)
    if len(combo) > 0:
        (top_region, top_product), top_rev = combo.index[0], combo.iloc[0]
        share = top_rev / df["Revenue"].sum() * 100
        cards.append({
            "category": "growth", "tag": "Growth driver",
            "text": (f"<b>{top_product} in {top_region}</b> is the single largest revenue "
                     f"combination at {format_currency(top_rev)} ({share:.1f}% of total revenue). "
                     f"Consider prioritizing capacity and marketing investment here."),
        })

    # --- Growth: month-over-month momentum ---
    monthly = df.groupby("Month")["Revenue"].sum().sort_index()
    if len(monthly) >= 3:
        recent_growth = pct_change(monthly.iloc[-1], monthly.iloc[-2])
        if recent_growth is not None and recent_growth > 5:
            cards.append({
                "category": "growth", "tag": "Momentum",
                "text": (f"Revenue accelerated <b>{recent_growth:.1f}%</b> month-over-month in "
                         f"{monthly.index[-1]:%B %Y}, the strongest recent reading in the series."),
            })

    # --- Risk: downtime vs on-time delivery correlation ---
    if df["Machine Downtime (hours)"].std() > 0 and df["On-Time Delivery (%)"].std() > 0:
        corr = df["Machine Downtime (hours)"].corr(df["On-Time Delivery (%)"])
        if corr < -0.15:
            cards.append({
                "category": "risk", "tag": "Operational risk",
                "text": (f"Machine downtime shows a negative correlation ({corr:.2f}) with on-time "
                         f"delivery — downtime spikes are likely contributing to missed delivery windows."),
            })

    # --- Risk: region/product with high return rate ---
    returns_by_product = df.groupby("Product")["Return Rate (%)"].mean().sort_values(ascending=False)
    if len(returns_by_product) > 0 and returns_by_product.iloc[0] > df["Return Rate (%)"].mean() + 1.5:
        cards.append({
            "category": "risk", "tag": "Quality risk",
            "text": (f"<b>{returns_by_product.index[0]}</b> has a return rate of "
                     f"{returns_by_product.iloc[0]:.1f}%, notably above the overall average of "
                     f"{df['Return Rate (%)'].mean():.1f}% — flag for quality review."),
        })

    # --- Efficiency: inventory levels vs turns by region ---
    inv_by_region = df.groupby("Region")["Inventory Levels"].mean().sort_values(ascending=False)
    if len(inv_by_region) > 1:
        cards.append({
            "category": "efficiency", "tag": "Working capital",
            "text": (f"<b>{inv_by_region.index[0]}</b> carries the highest average inventory level "
                     f"({inv_by_region.iloc[0]:,.0f} units) — review safety-stock policy for potential "
                     f"working-capital release."),
        })

    # --- Efficiency: labor hours vs units sold productivity ---
    prod_by_region = df.groupby("Region").apply(
        lambda g: g["Units Sold"].sum() / g["Labor Hours"].sum() if g["Labor Hours"].sum() else 0
    ).sort_values(ascending=False)
    if len(prod_by_region) > 1:
        cards.append({
            "category": "efficiency", "tag": "Labor productivity",
            "text": (f"<b>{prod_by_region.index[0]}</b> produces the most units sold per labor hour "
                     f"({prod_by_region.iloc[0]:.2f}), the benchmark for other regions to target."),
        })

    # --- Recommendation: satisfaction vs return rate ---
    if df["Customer Satisfaction"].mean() < 3.2:
        cards.append({
            "category": "recommendation", "tag": "Customer experience",
            "text": (f"Average customer satisfaction is {df['Customer Satisfaction'].mean():.1f}/5 — "
                     f"pair this with the quality and delivery findings above to prioritize a service "
                     f"recovery plan."),
        })

    cards.append({
        "category": "recommendation", "tag": "Next step",
        "text": ("Use the Scenario Planning page to stress-test a margin-improvement plan (price, "
                 "cost, or mix changes) against the trends identified here."),
    })

    return cards


# ----------------------------------------------------------------------------
# Optional: live LLM Q&A via the Anthropic API
# ----------------------------------------------------------------------------
def get_api_key() -> Optional[str]:
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    return st.session_state.get("anthropic_api_key_input") or None


def build_data_summary(df: pd.DataFrame) -> str:
    """A compact textual summary of the filtered dataset for LLM context."""
    if df.empty:
        return "No data in the current filter selection."
    k = compute_kpis(df)
    by_region = df.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
    by_product = df.groupby("Product")["Revenue"].sum().sort_values(ascending=False)
    lines = [
        f"Period: {df['Date'].min():%Y-%m-%d} to {df['Date'].max():%Y-%m-%d} ({len(df)} records)",
        f"Revenue: {format_currency(k['revenue'])}, Gross Profit: {format_currency(k['gross_profit'])} "
        f"({format_pct(k['gross_margin'])} margin), EBITDA: {format_currency(k['ebitda'])} "
        f"({format_pct(k['ebitda_margin'])} margin), Net Profit: {format_currency(k['net_profit'])} "
        f"({format_pct(k['net_margin'])} margin)",
        f"Units sold: {k['units_sold']:,.0f}, Avg order value: {format_currency(k['avg_order_value'])}",
        f"Inventory turns (annualized): {k['inventory_turns']:.1f}x, Avg inventory: {format_currency(k['avg_inventory'])}",
        f"Avg customer satisfaction: {k['avg_satisfaction']:.2f}/5, Avg on-time delivery: {k['avg_on_time']:.1f}%, "
        f"Avg return rate: {k['avg_return_rate']:.1f}%, Avg lead time: {k['avg_lead_time']:.1f} days",
        "Revenue by region: " + ", ".join(f"{r}: {format_currency(v)}" for r, v in by_region.items()),
        "Revenue by product: " + ", ".join(f"{p}: {format_currency(v)}" for p, v in by_product.items()),
    ]
    return "\n".join(lines)


def ask_claude(question: str, data_summary: str, api_key: str) -> str:
    """Calls the Anthropic API for a grounded answer about the filtered dataset.
    Raises on failure -- callers should catch and surface a friendly message."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = (
        "You are a senior FP&A analyst for a manufacturing company. Answer the "
        "user's question using ONLY the data summary provided below. Be concise, "
        "specific, and quantitative. If the summary doesn't contain enough detail "
        "to answer precisely, say so rather than guessing.\n\n"
        f"DATA SUMMARY:\n{data_summary}"
    )
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=700,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )
    parts = [block.text for block in response.content if getattr(block, "type", "") == "text"]
    return "\n".join(parts).strip() or "The model returned no text response."
