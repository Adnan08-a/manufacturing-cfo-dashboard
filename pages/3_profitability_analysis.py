"""Profitability Analysis -- margins, cost structure, and profitability by segment."""
import pandas as pd
import streamlit as st

from utils.styling import inject_page_theme, page_header, kpi_grid, section_title
from utils.app_state import render_sidebar_and_load
from utils.kpis import compute_kpis
from utils.formatting import format_currency, format_pct
from utils.charts import dual_metric_trend, bar_compare, heatmap, waterfall
from utils.i18n import t

inject_page_theme()

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    t("nav.profitability_analysis"),
    t("profit.title"),
    t("profit.subtitle"),
)

k = compute_kpis(df)

kpi_grid([
    {"label": t("kpi.gross_profit"), "value": format_currency(k["gross_profit"])},
    {"label": t("kpi.gross_margin"), "value": format_pct(k["gross_margin"])},
    {"label": t("kpi.ebitda"), "value": format_currency(k["ebitda"])},
    {"label": t("kpi.ebitda_margin"), "value": format_pct(k["ebitda_margin"])},
    {"label": t("kpi.net_profit"), "value": format_currency(k["net_profit"])},
    {"label": t("kpi.net_margin"), "value": format_pct(k["net_margin"])},
])

# ----------------------------------------------------------------------------
section_title(t("profit.margin_trend"), "📈")
monthly = df.groupby("Month", as_index=False).agg(
    Revenue=("Revenue", "sum"), GrossProfit=("Gross Profit", "sum"), EBITDA=("EBITDA", "sum"),
)
monthly["Gross Margin %"] = monthly["GrossProfit"] / monthly["Revenue"] * 100
monthly["EBITDA Margin %"] = monthly["EBITDA"] / monthly["Revenue"] * 100
fig = dual_metric_trend(
    monthly, "Month", "Revenue", "Gross Margin %",
    y1_title=f"{t('kpi.revenue')} ($)", y2_title=f"{t('kpi.gross_margin')} (%)",
)
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

fig2 = dual_metric_trend(
    monthly, "Month", "EBITDA", "EBITDA Margin %",
    y1_title=f"{t('kpi.ebitda')} ($)", y2_title=f"{t('kpi.ebitda_margin')} (%)",
)
st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    section_title(t("profit.margin_by_region"), "🌍")
    margin_region = df.groupby("Region", as_index=False).apply(
        lambda g: pd.Series({"Gross Margin %": g["Gross Profit"].sum() / g["Revenue"].sum() * 100})
    ).sort_values("Gross Margin %", ascending=False)
    st.plotly_chart(
        bar_compare(margin_region, "Region", "Gross Margin %", color="Region", text_auto=True),
        width="stretch", config={"displayModeBar": False},
    )

with col2:
    section_title(t("profit.margin_by_product"), "📦")
    margin_product = df.groupby("Product", as_index=False).apply(
        lambda g: pd.Series({"Gross Margin %": g["Gross Profit"].sum() / g["Revenue"].sum() * 100})
    ).sort_values("Gross Margin %", ascending=False)
    st.plotly_chart(
        bar_compare(margin_product, "Product", "Gross Margin %", color="Product", text_auto=True),
        width="stretch", config={"displayModeBar": False},
    )

# ----------------------------------------------------------------------------
section_title(t("profit.heatmap"), "🔥")
pivot = df.pivot_table(
    index="Region", columns="Product",
    values="Gross Profit", aggfunc="sum",
)
rev_pivot = df.pivot_table(index="Region", columns="Product", values="Revenue", aggfunc="sum")
margin_pivot = (pivot / rev_pivot * 100).round(1)
st.plotly_chart(heatmap(margin_pivot, value_suffix="%"), width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title(t("profit.cost_structure"), "🧱")
labels = [t("chart.revenue"), t("chart.cogs"), t("chart.gross_profit"), t("chart.operating_exp"), t("chart.ebitda")]
values = [k["revenue"], -k["cost"], k["gross_profit"], -(k["gross_profit"] - k["ebitda"]), k["ebitda"]]
measures = ["absolute", "relative", "total", "relative", "total"]
st.plotly_chart(waterfall(labels, values, measures), width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title(t("profit.detail_table"), "📋")
detail = df.groupby(["Region", "Product"]).agg(
    Revenue=("Revenue", "sum"), GrossProfit=("Gross Profit", "sum"),
    EBITDA=("EBITDA", "sum"), NetProfit=("Profit", "sum"),
).reset_index()
detail["Gross Margin %"] = (detail["GrossProfit"] / detail["Revenue"] * 100).round(1)
detail["EBITDA Margin %"] = (detail["EBITDA"] / detail["Revenue"] * 100).round(1)
detail = detail.sort_values("EBITDA Margin %", ascending=False)
for col in ["Revenue", "GrossProfit", "EBITDA", "NetProfit"]:
    detail[col] = detail[col].apply(format_currency)
detail.columns = [t("sidebar.region"), t("sidebar.product"), t("kpi.revenue"), t("kpi.gross_profit"),
                   t("kpi.ebitda"), t("kpi.net_profit"), t("kpi.gross_margin") + " %", t("kpi.ebitda_margin") + " %"]
st.dataframe(detail, width="stretch", hide_index=True)
