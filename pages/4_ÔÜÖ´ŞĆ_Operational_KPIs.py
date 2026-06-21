"""Operational KPIs -- quality, delivery, inventory, and labor efficiency."""
import pandas as pd
import streamlit as st

from utils.styling import configure_page, page_header, kpi_grid, section_title
from utils.app_state import render_sidebar_and_load
from utils.kpis import compute_kpis
from utils.formatting import format_currency, format_pct, format_number
from utils.charts import trend_line, bar_compare, gauge, scatter_corr, correlation_heatmap, box_distribution

configure_page("Operational KPIs", "⚙️")

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    "Operational KPIs",
    "The shop-floor metrics that drive the P&L",
    "Quality, on-time delivery, inventory efficiency, machine uptime, and labor productivity.",
)

k = compute_kpis(df)

kpi_grid([
    {"label": "Units Sold", "value": format_number(k["units_sold"])},
    {"label": "Inventory Turns", "value": f"{k['inventory_turns']:.1f}x"},
    {"label": "Avg Inventory", "value": format_currency(k["avg_inventory"])},
    {"label": "Avg Lead Time", "value": f"{k['avg_lead_time']:.1f} days"},
    {"label": "Avg Downtime", "value": f"{k['avg_downtime']:.1f} hrs"},
    {"label": "Total Labor Hours", "value": format_number(k["total_labor_hours"])},
])

# ----------------------------------------------------------------------------
section_title("Service-level gauges", "🎯")
g1, g2, g3 = st.columns(3)
with g1:
    st.plotly_chart(
        gauge(k["avg_on_time"], "On-Time Delivery", target=90),
        width="stretch", config={"displayModeBar": False},
    )
with g2:
    st.plotly_chart(
        gauge(k["avg_satisfaction"] * 20, "Customer Satisfaction (scaled to 100)", target=80),
        width="stretch", config={"displayModeBar": False},
    )
with g3:
    st.plotly_chart(
        gauge(max(0, 100 - k["avg_return_rate"] * 10), "Quality Index (100 - 10×return rate)", target=80),
        width="stretch", config={"displayModeBar": False},
    )

# ----------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    section_title("Inventory levels over time", "📦")
    inv_trend = df.groupby("Month", as_index=False)["Inventory Levels"].mean()
    st.plotly_chart(
        trend_line(inv_trend, "Month", "Inventory Levels", y_title="Avg Inventory"),
        width="stretch", config={"displayModeBar": False},
    )

with col2:
    section_title("Units sold over time", "📦")
    units_trend = df.groupby("Month", as_index=False)["Units Sold"].sum()
    st.plotly_chart(
        trend_line(units_trend, "Month", "Units Sold", y_title="Units"),
        width="stretch", config={"displayModeBar": False},
    )

# ----------------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    section_title("On-time delivery by region", "🚚")
    otd_region = df.groupby("Region", as_index=False)["On-Time Delivery (%)"].mean().sort_values(
        "On-Time Delivery (%)", ascending=False)
    st.plotly_chart(
        bar_compare(otd_region, "Region", "On-Time Delivery (%)", color="Region", text_auto=True),
        width="stretch", config={"displayModeBar": False},
    )

with col4:
    section_title("Return rate by product", "↩️")
    rr_product = df.groupby("Product", as_index=False)["Return Rate (%)"].mean().sort_values(
        "Return Rate (%)", ascending=False)
    st.plotly_chart(
        bar_compare(rr_product, "Product", "Return Rate (%)", color="Product", text_auto=True),
        width="stretch", config={"displayModeBar": False},
    )

# ----------------------------------------------------------------------------
section_title("Machine downtime vs. on-time delivery", "🔧")
st.caption("Each point is one order/record; trendline highlights the relationship between downtime and service level.")
st.plotly_chart(
    scatter_corr(df, "Machine Downtime (hours)", "On-Time Delivery (%)", color="Region",
                 trendline=True),
    width="stretch", config={"displayModeBar": False},
)

# ----------------------------------------------------------------------------
section_title("Operational metric correlations", "🔗")
op_cols = ["Customer Satisfaction", "Labor Hours", "Machine Downtime (hours)",
           "Inventory Levels", "Order Lead Time (days)", "Return Rate (%)", "On-Time Delivery (%)"]
st.plotly_chart(
    correlation_heatmap(df, op_cols),
    width="stretch", config={"displayModeBar": False},
)

# ----------------------------------------------------------------------------
section_title("Order lead time distribution by product", "⏱️")
st.plotly_chart(
    box_distribution(df, "Product", "Order Lead Time (days)"),
    width="stretch", config={"displayModeBar": False},
)

# ----------------------------------------------------------------------------
section_title("Operational scorecard by region", "📋")
scorecard = df.groupby("Region").agg(
    **{
        "On-Time %": ("On-Time Delivery (%)", "mean"),
        "Return Rate %": ("Return Rate (%)", "mean"),
        "Avg Lead Time (d)": ("Order Lead Time (days)", "mean"),
        "Avg Downtime (h)": ("Machine Downtime (hours)", "mean"),
        "Avg Satisfaction": ("Customer Satisfaction", "mean"),
        "Avg Inventory": ("Inventory Levels", "mean"),
    }
).round(2).reset_index()
st.dataframe(scorecard, width="stretch", hide_index=True)
