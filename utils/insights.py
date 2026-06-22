"""
insights.py
-----------
Two layers of "AI insight" generation:

1. A deterministic, rule-based commentary engine (`generate_executive_commentary`,
   `generate_insight_cards`) that runs entirely offline -- no API key required --
   by mining trends, outliers, and correlations from the filtered dataframe.
   All output text goes through utils.i18n.t() so it renders in whichever
   language is currently selected.

2. An optional live-LLM layer (`ask_claude`) that calls the Anthropic API for
   free-form Q&A when a key is available (via st.secrets or a session input).
   The dashboard works fully without this; it's an enhancement, not a dependency.
   The answer language follows the dashboard's current language setting.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

from utils.kpis import compute_kpis, pct_change, pp_change
from utils.formatting import format_currency, format_pct
from utils.i18n import t, get_lang

MODEL_NAME = "claude-sonnet-4-6"


# ----------------------------------------------------------------------------
# Rule-based executive commentary (Executive Summary page)
# ----------------------------------------------------------------------------
def generate_executive_commentary(df_curr: pd.DataFrame, df_prior: pd.DataFrame) -> list[str]:
    if df_curr.empty:
        return [t("commentary.no_data")]

    kc = compute_kpis(df_curr)
    kp = compute_kpis(df_prior) if not df_prior.empty else None

    bullets = []

    # Revenue & profitability trend
    if kp:
        rev_chg = pct_change(kc["revenue"], kp["revenue"])
        if rev_chg is not None:
            verb = t("commentary.verb_grew") if rev_chg >= 0 else t("commentary.verb_declined")
            bullets.append(t(
                "commentary.revenue_change",
                verb=verb, pct=abs(rev_chg),
                revenue=format_currency(kc["revenue"]),
                margin=format_pct(kc["ebitda_margin"]),
                delta=pp_change(kc["ebitda_margin"], kp["ebitda_margin"]),
            ))
        else:
            bullets.append(t("commentary.revenue_total_only", revenue=format_currency(kc["revenue"])))
    else:
        bullets.append(t(
            "commentary.revenue_total_with_margin",
            revenue=format_currency(kc["revenue"]),
            margin=format_pct(kc["ebitda_margin"]),
        ))

    # Top / bottom region
    by_region = df_curr.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
    if len(by_region) > 1:
        bullets.append(t(
            "commentary.region_lead_trail",
            top=by_region.index[0], top_rev=format_currency(by_region.iloc[0]),
            bottom=by_region.index[-1], bottom_rev=format_currency(by_region.iloc[-1]),
        ))

    # Top product by margin
    margin_by_product = (
        df_curr.groupby("Product").apply(
            lambda g: g["Gross Profit"].sum() / g["Revenue"].sum() * 100 if g["Revenue"].sum() else 0
        ).sort_values(ascending=False)
    )
    if len(margin_by_product) > 0:
        bullets.append(t(
            "commentary.product_margin",
            top=margin_by_product.index[0], top_pct=margin_by_product.iloc[0],
            bottom=margin_by_product.index[-1], bottom_pct=margin_by_product.iloc[-1],
        ))

    # Operational flags
    if kc["avg_on_time"] < 85:
        bullets.append(t("commentary.low_on_time", pct=kc["avg_on_time"]))
    if kc["avg_return_rate"] > 6:
        bullets.append(t("commentary.high_return", pct=kc["avg_return_rate"]))
    if kc["inventory_turns"] < 4:
        bullets.append(t(
            "commentary.low_turns",
            turns=kc["inventory_turns"], wc=format_currency(kc["working_capital"]),
        ))

    return bullets


# ----------------------------------------------------------------------------
# Rule-based categorized insight cards (AI Insights page)
# ----------------------------------------------------------------------------
def generate_insight_cards(df: pd.DataFrame) -> list[dict]:
    """Returns a list of {category, tag, text} dicts spanning growth, risk,
    efficiency, and recommendation themes."""
    if df.empty or len(df) < 5:
        return [{"category": "recommendation", "tag": t("insight.few_records_tag"),
                  "text": t("insight.few_records_text")}]

    cards = []

    # --- Growth: best performing region/product combo ---
    combo = df.groupby(["Region", "Product"])["Revenue"].sum().sort_values(ascending=False)
    if len(combo) > 0:
        (top_region, top_product), top_rev = combo.index[0], combo.iloc[0]
        share = top_rev / df["Revenue"].sum() * 100
        cards.append({
            "category": "growth", "tag": t("insight.growth_driver_tag"),
            "text": t(
                "insight.growth_driver_text",
                product=top_product, region=top_region,
                revenue=format_currency(top_rev), share=share,
            ),
        })

    # --- Growth: month-over-month momentum ---
    monthly = df.groupby("Month")["Revenue"].sum().sort_index()
    if len(monthly) >= 3:
        recent_growth = pct_change(monthly.iloc[-1], monthly.iloc[-2])
        if recent_growth is not None and recent_growth > 5:
            cards.append({
                "category": "growth", "tag": t("insight.momentum_tag"),
                "text": t(
                    "insight.momentum_text",
                    pct=recent_growth, month=f"{monthly.index[-1]:%B %Y}",
                ),
            })

    # --- Risk: downtime vs on-time delivery correlation ---
    if df["Machine Downtime (hours)"].std() > 0 and df["On-Time Delivery (%)"].std() > 0:
        corr = df["Machine Downtime (hours)"].corr(df["On-Time Delivery (%)"])
        if corr < -0.15:
            cards.append({
                "category": "risk", "tag": t("insight.op_risk_tag"),
                "text": t("insight.op_risk_text", corr=corr),
            })

    # --- Risk: region/product with high return rate ---
    returns_by_product = df.groupby("Product")["Return Rate (%)"].mean().sort_values(ascending=False)
    if len(returns_by_product) > 0 and returns_by_product.iloc[0] > df["Return Rate (%)"].mean() + 1.5:
        cards.append({
            "category": "risk", "tag": t("insight.quality_risk_tag"),
            "text": t(
                "insight.quality_risk_text",
                product=returns_by_product.index[0], pct=returns_by_product.iloc[0],
                avg=df["Return Rate (%)"].mean(),
            ),
        })

    # --- Efficiency: inventory levels vs turns by region ---
    inv_by_region = df.groupby("Region")["Inventory Levels"].mean().sort_values(ascending=False)
    if len(inv_by_region) > 1:
        cards.append({
            "category": "efficiency", "tag": t("insight.working_capital_tag"),
            "text": t(
                "insight.working_capital_text",
                region=inv_by_region.index[0], level=inv_by_region.iloc[0],
            ),
        })

    # --- Efficiency: labor hours vs units sold productivity ---
    prod_by_region = df.groupby("Region").apply(
        lambda g: g["Units Sold"].sum() / g["Labor Hours"].sum() if g["Labor Hours"].sum() else 0
    ).sort_values(ascending=False)
    if len(prod_by_region) > 1:
        cards.append({
            "category": "efficiency", "tag": t("insight.labor_prod_tag"),
            "text": t(
                "insight.labor_prod_text",
                region=prod_by_region.index[0], value=prod_by_region.iloc[0],
            ),
        })

    # --- Recommendation: satisfaction vs return rate ---
    if df["Customer Satisfaction"].mean() < 3.2:
        cards.append({
            "category": "recommendation", "tag": t("insight.cx_tag"),
            "text": t("insight.cx_text", value=df["Customer Satisfaction"].mean()),
        })

    cards.append({
        "category": "recommendation", "tag": t("insight.next_step_tag"),
        "text": t("insight.next_step_text"),
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
    """A compact textual summary of the filtered dataset for LLM context.
    Kept in English regardless of UI language -- this is internal model
    context, not user-facing text, and English keeps the model's numeric
    reasoning most reliable."""
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
    Raises on failure -- callers should catch and surface a friendly message.
    Answers in Bosnian when the dashboard's language is set to Bosnian."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    language_instruction = (
        "\n\nRespond in Bosnian (bosanski jezik)." if get_lang() == "bs" else ""
    )
    system_prompt = (
        "You are a senior FP&A analyst for a manufacturing company. Answer the "
        "user's question using ONLY the data summary provided below. Be concise, "
        "specific, and quantitative. If the summary doesn't contain enough detail "
        "to answer precisely, say so rather than guessing."
        f"{language_instruction}\n\n"
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
