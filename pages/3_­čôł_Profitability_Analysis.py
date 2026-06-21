"""Profitability Analysis -- margins, cost structure, and profitability by segment."""
import pandas as pd
import streamlit as st

from utils.styling import configure_page, page_header, kpi_grid, section_title
from utils.app_state import render_sidebar_and_load
from utils.kpis import compute_kpis
from utils.formatting import format_currency, format_pct
from utils.charts import dual_metric_trend, bar_compare, heatmap, waterfall

configure_page("Profitability Analysis", "📈")

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    "Profitability Analysis",
    "Margins, cost structure, and where profit is made",
    "Gross margin, EBITDA margin, and net margin trends, plus a segment-level profitability view.",
)

k = compute_kpis(df)

kpi_grid([
    {"label": "Gross Profit", "value": format_currency(k["gross_profit"])},
    {"label": "Gross Margin", "value": format_pct(k["gross_margin"])},
    {"label": "EBITDA", "value": format_currency(k["ebitda"])},
    {"label": "EBITDA Margin", "value": format_pct(k["ebitda_margin"])},
    {"label": "Net Profit", "value": format_currency(k["net_profit"])},
    {"label": "Net Margin", "value": format_pct(k["net_margin"])},
])

# ----------------------------------------------------------------------------
section_title("Margin trend over time", "📈")
monthly = df.groupby("Month", as_index=False).agg(
    Revenue=("Revenue", "sum"), GrossProfit=("Gross Profit", "sum"), EBITDA=("EBITDA", "sum"),
)
monthly["Gross Margin %"] = monthly["GrossProfit"] / monthly["Revenue"] * 100
monthly["EBITDA Margin %"] = monthly["EBITDA"] / monthly["Revenue"] * 100
fig = dual_metric_trend(
    monthly, "Month", "Revenue", "Gross Margin %",
    y1_title="Revenue ($)", y2_title="Gross Margin (%)",
)
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

fig2 = dual_metric_trend(
    monthly, "Month", "EBITDA", "EBITDA Margin %",
    y1_title="EBITDA ($)", y2_title="EBITDA Margin (%)",
)
st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    section_title("Gross margin by region", "🌍")
    margin_region = df.groupby("Region", as_index=False).apply(
        lambda g: pd.Series({"Gross Margin %": g["Gross Profit"].sum() / g["Revenue"].sum() * 100})
    ).sort_values("Gross Margin %", ascending=False)
    st.plotly_chart(
        bar_compare(margin_region, "Region", "Gross Margin %", color="Region", text_auto=True),
        width="stretch", config={"displayModeBar": False},
    )

with col2:
    section_title("Gross margin by product", "📦")
    margin_product = df.groupby("Product", as_index=False).apply(
        lambda g: pd.Series({"Gross Margin %": g["Gross Profit"].sum() / g["Revenue"].sum() * 100})
    ).sort_values("Gross Margin %", ascending=False)
    st.plotly_chart(
        bar_compare(margin_product, "Product", "Gross Margin %", color="Product", text_auto=True),
        width="stretch", config={"displayModeBar": False},
    )

# ----------------------------------------------------------------------------
section_title("Profitability heatmap: gross margin % by region × product", "🔥")
pivot = df.pivot_table(
    index="Region", columns="Product",
    values="Gross Profit", aggfunc="sum",
)
rev_pivot = df.pivot_table(index="Region", columns="Product", values="Revenue", aggfunc="sum")
margin_pivot = (pivot / rev_pivot * 100).round(1)
st.plotly_chart(heatmap(margin_pivot, value_suffix="%"), width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title("Cost structure: Revenue → COGS → Operating Exp. → EBITDA", "🧱")
labels = ["Revenue", "COGS", "Gross Profit", "Operating Exp.", "EBITDA"]
values = [k["revenue"], -k["cost"], k["gross_profit"], -(k["gross_profit"] - k["ebitda"]), k["ebitda"]]
measures = ["absolute", "relative", "total", "relative", "total"]
st.plotly_chart(waterfall(labels, values, measures), width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title("Profitability detail by segment", "📋")
detail = df.groupby(["Region", "Product"]).agg(
    Revenue=("Revenue", "sum"), GrossProfit=("Gross Profit", "sum"),
    EBITDA=("EBITDA", "sum"), NetProfit=("Profit", "sum"),
).reset_index()
detail["Gross Margin %"] = (detail["GrossProfit"] / detail["Revenue"] * 100).round(1)
detail["EBITDA Margin %"] = (detail["EBITDA"] / detail["Revenue"] * 100).round(1)
detail = detail.sort_values("EBITDA Margin %", ascending=False)
for col in ["Revenue", "GrossProfit", "EBITDA", "NetProfit"]:
    detail[col] = detail[col].apply(format_currency)
detail.columns = ["Region", "Product", "Revenue", "Gross Profit", "EBITDA", "Net Profit",
                   "Gross Margin %", "EBITDA Margin %"]
st.dataframe(detail, width="stretch", hide_index=True)
