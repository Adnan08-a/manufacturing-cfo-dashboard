"""Revenue Analysis -- trends, mix, growth, and revenue decomposition."""
import pandas as pd
import streamlit as st

from utils.styling import configure_page, page_header, kpi_grid, section_title
from utils.app_state import render_sidebar_and_load
from utils.formatting import format_currency, format_pct
from utils.charts import trend_line, bar_compare, heatmap, driver_treemap

configure_page("Revenue Analysis", "💵")

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    "Revenue Analysis",
    "Where revenue is coming from -- and how it's moving",
    "Trend, regional and product mix, growth rates, and a full revenue decomposition.",
)

total_revenue = df["Revenue"].sum()
avg_order_value = df["Revenue"].sum() / df["Units Sold"].sum() if df["Units Sold"].sum() else 0
n_months = df["Month"].nunique()
avg_monthly_revenue = total_revenue / n_months if n_months else 0
top_region = df.groupby("Region")["Revenue"].sum().idxmax()
top_product = df.groupby("Product")["Revenue"].sum().idxmax()

kpi_grid([
    {"label": "Total Revenue", "value": format_currency(total_revenue)},
    {"label": "Avg Monthly Revenue", "value": format_currency(avg_monthly_revenue)},
    {"label": "Avg Order Value", "value": format_currency(avg_order_value)},
    {"label": "Units Sold", "value": f"{df['Units Sold'].sum():,.0f}"},
    {"label": "Top Region", "value": top_region},
    {"label": "Top Product", "value": top_product},
])

# ----------------------------------------------------------------------------
view = st.radio("Trend granularity", ["Monthly", "Daily"], horizontal=True, key="rev_granularity")

section_title("Revenue trend by " + ("month" if view == "Monthly" else "day"), "📈")
if view == "Monthly":
    trend_df = df.groupby(["Month", "Region"], as_index=False)["Revenue"].sum()
    fig = trend_line(trend_df, "Month", "Revenue", color="Region", y_title="Revenue ($)")
else:
    trend_df = df.groupby(["Date", "Region"], as_index=False)["Revenue"].sum()
    fig = trend_line(trend_df, "Date", "Revenue", color="Region", y_title="Revenue ($)")
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    section_title("Revenue by region", "🌍")
    by_region = df.groupby("Region", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    st.plotly_chart(
        bar_compare(by_region, "Region", "Revenue", color="Region", text_auto=True),
        width="stretch", config={"displayModeBar": False},
    )

with col2:
    section_title("Revenue by product", "📦")
    by_product = df.groupby("Product", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    st.plotly_chart(
        bar_compare(by_product, "Product", "Revenue", color="Product", text_auto=True),
        width="stretch", config={"displayModeBar": False},
    )

# ----------------------------------------------------------------------------
section_title("Region × product revenue heatmap", "🔥")
pivot = df.pivot_table(index="Region", columns="Product", values="Revenue", aggfunc="sum", fill_value=0)
st.plotly_chart(heatmap(pivot, value_suffix=""), width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title("Revenue decomposition (driver tree)", "🌳")
st.caption("Box size = revenue contribution. Click a region to drill into its products.")
treemap_df = df.groupby(["Region", "Product"], as_index=False)["Revenue"].sum()
st.plotly_chart(
    driver_treemap(treemap_df, ["Region", "Product"], "Revenue"),
    width="stretch", config={"displayModeBar": False},
)

# ----------------------------------------------------------------------------
section_title("Month-over-month growth", "📊")
monthly = df.groupby("Month")["Revenue"].sum().sort_index()
growth = monthly.pct_change().fillna(0) * 100
growth_df = pd.DataFrame({"Month": growth.index, "Growth %": growth.values})
fig_growth = bar_compare(growth_df, "Month", "Growth %")
fig_growth.update_traces(marker_color=["#22C55E" if v >= 0 else "#F87171" for v in growth_df["Growth %"]])
st.plotly_chart(fig_growth, width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title("Revenue detail by region & product", "📋")
detail = df.groupby(["Region", "Product"]).agg(
    Revenue=("Revenue", "sum"), Units=("Units Sold", "sum"), Orders=("Revenue", "count"),
).reset_index().sort_values("Revenue", ascending=False)
detail["Revenue Share"] = (detail["Revenue"] / detail["Revenue"].sum() * 100).round(1).astype(str) + "%"
detail["Revenue"] = detail["Revenue"].apply(format_currency)
st.dataframe(detail, width="stretch", hide_index=True)
