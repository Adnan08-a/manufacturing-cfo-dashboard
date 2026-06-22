"""Operational KPIs -- quality, delivery, inventory, and labor efficiency."""
import pandas as pd
import streamlit as st

from utils.styling import inject_page_theme, page_header, kpi_grid, section_title
from utils.app_state import render_sidebar_and_load
from utils.kpis import compute_kpis
from utils.formatting import format_currency, format_pct, format_number
from utils.charts import trend_line, bar_compare, gauge, scatter_corr, correlation_heatmap, box_distribution
from utils.i18n import t

inject_page_theme()

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    t("nav.operational_kpis"),
    t("ops.title"),
    t("ops.subtitle"),
)

k = compute_kpis(df)

kpi_grid([
    {"label": t("kpi.units_sold"), "value": format_number(k["units_sold"])},
    {"label": t("kpi.inventory_turns"), "value": f"{k['inventory_turns']:.1f}x"},
    {"label": t("kpi.avg_inventory"), "value": format_currency(k["avg_inventory"])},
    {"label": t("kpi.avg_lead_time"), "value": f"{k['avg_lead_time']:.1f} {t('unit.days')}"},
    {"label": t("kpi.avg_downtime"), "value": f"{k['avg_downtime']:.1f} {t('unit.hrs')}"},
    {"label": t("kpi.total_labor_hours"), "value": format_number(k["total_labor_hours"])},
])

# ----------------------------------------------------------------------------
section_title(t("ops.gauges"), "🎯")
g1, g2, g3 = st.columns(3)
with g1:
    st.plotly_chart(
        gauge(k["avg_on_time"], t("ops.gauge_on_time"), target=90),
        width="stretch", config={"displayModeBar": False},
    )
with g2:
    st.plotly_chart(
        gauge(k["avg_satisfaction"] * 20, t("ops.gauge_satisfaction"), target=80),
        width="stretch", config={"displayModeBar": False},
    )
with g3:
    st.plotly_chart(
        gauge(max(0, 100 - k["avg_return_rate"] * 10), t("ops.gauge_quality"), target=80),
        width="stretch", config={"displayModeBar": False},
    )

# ----------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    section_title(t("ops.inventory_over_time"), "📦")
    inv_trend = df.groupby("Month", as_index=False)["Inventory Levels"].mean()
    st.plotly_chart(
        trend_line(inv_trend, "Month", "Inventory Levels", y_title=t("kpi.avg_inventory")),
        width="stretch", config={"displayModeBar": False},
    )

with col2:
    section_title(t("ops.units_over_time"), "📦")
    units_trend = df.groupby("Month", as_index=False)["Units Sold"].sum()
    st.plotly_chart(
        trend_line(units_trend, "Month", "Units Sold", y_title=t("kpi.units_sold")),
        width="stretch", config={"displayModeBar": False},
    )

# ----------------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    section_title(t("ops.otd_by_region"), "🚚")
    otd_region = df.groupby("Region", as_index=False)["On-Time Delivery (%)"].mean().sort_values(
        "On-Time Delivery (%)", ascending=False)
    st.plotly_chart(
        bar_compare(otd_region, "Region", "On-Time Delivery (%)", color="Region", text_auto=True),
        width="stretch", config={"displayModeBar": False},
    )

with col4:
    section_title(t("ops.return_by_product"), "↩️")
    rr_product = df.groupby("Product", as_index=False)["Return Rate (%)"].mean().sort_values(
        "Return Rate (%)", ascending=False)
    st.plotly_chart(
        bar_compare(rr_product, "Product", "Return Rate (%)", color="Product", text_auto=True),
        width="stretch", config={"displayModeBar": False},
    )

# ----------------------------------------------------------------------------
section_title(t("ops.downtime_vs_otd"), "🔧")
st.caption(t("ops.downtime_caption"))
st.plotly_chart(
    scatter_corr(df, "Machine Downtime (hours)", "On-Time Delivery (%)", color="Region",
                 trendline=True),
    width="stretch", config={"displayModeBar": False},
)

# ----------------------------------------------------------------------------
section_title(t("ops.correlations"), "🔗")
op_cols = ["Customer Satisfaction", "Labor Hours", "Machine Downtime (hours)",
           "Inventory Levels", "Order Lead Time (days)", "Return Rate (%)", "On-Time Delivery (%)"]
st.plotly_chart(
    correlation_heatmap(df, op_cols),
    width="stretch", config={"displayModeBar": False},
)

# ----------------------------------------------------------------------------
section_title(t("ops.lead_time_dist"), "⏱️")
st.plotly_chart(
    box_distribution(df, "Product", "Order Lead Time (days)"),
    width="stretch", config={"displayModeBar": False},
)

# ----------------------------------------------------------------------------
section_title(t("ops.scorecard"), "📋")
scorecard = df.groupby("Region").agg(
    **{
        t("ops.col_on_time_pct"): ("On-Time Delivery (%)", "mean"),
        t("ops.col_return_rate_pct"): ("Return Rate (%)", "mean"),
        t("ops.col_avg_lead_time_d"): ("Order Lead Time (days)", "mean"),
        t("ops.col_avg_downtime_h"): ("Machine Downtime (hours)", "mean"),
        t("ops.col_avg_satisfaction"): ("Customer Satisfaction", "mean"),
        t("ops.col_avg_inventory"): ("Inventory Levels", "mean"),
    }
).round(2).reset_index()
scorecard = scorecard.rename(columns={"Region": t("sidebar.region")})
st.dataframe(scorecard, width="stretch", hide_index=True)
