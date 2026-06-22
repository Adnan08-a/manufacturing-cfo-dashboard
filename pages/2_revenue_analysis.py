"""Revenue Analysis -- trends, mix, growth, and revenue decomposition."""
import pandas as pd
import streamlit as st

from utils.styling import inject_page_theme, page_header, kpi_grid, section_title
from utils.app_state import render_sidebar_and_load
from utils.formatting import format_currency, format_pct
from utils.charts import trend_line, bar_compare, heatmap, driver_treemap
from utils.i18n import t

inject_page_theme()

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    t("nav.revenue_analysis"),
    t("revenue.title"),
    t("revenue.subtitle"),
)

total_revenue = df["Revenue"].sum()
avg_order_value = df["Revenue"].sum() / df["Units Sold"].sum() if df["Units Sold"].sum() else 0
n_months = df["Month"].nunique()
avg_monthly_revenue = total_revenue / n_months if n_months else 0
top_region = df.groupby("Region")["Revenue"].sum().idxmax()
top_product = df.groupby("Product")["Revenue"].sum().idxmax()

kpi_grid([
    {"label": t("kpi.total_revenue"), "value": format_currency(total_revenue)},
    {"label": t("kpi.avg_monthly_revenue"), "value": format_currency(avg_monthly_revenue)},
    {"label": t("kpi.avg_order_value"), "value": format_currency(avg_order_value)},
    {"label": t("kpi.units_sold"), "value": f"{df['Units Sold'].sum():,.0f}"},
    {"label": t("kpi.top_region"), "value": top_region},
    {"label": t("kpi.top_product"), "value": top_product},
])

# ----------------------------------------------------------------------------
granularity_display = {"monthly": t("revenue.monthly"), "daily": t("revenue.daily")}
view = st.radio(
    t("revenue.granularity"), ["monthly", "daily"],
    format_func=lambda v: granularity_display[v],
    horizontal=True, key="rev_granularity",
)
is_monthly = view == "monthly"

section_title(t("revenue.trend_by_month") if is_monthly else t("revenue.trend_by_day"), "📈")
if is_monthly:
    trend_df = df.groupby(["Month", "Region"], as_index=False)["Revenue"].sum()
    fig = trend_line(trend_df, "Month", "Revenue", color="Region", y_title=f"{t('kpi.revenue')} ($)")
else:
    trend_df = df.groupby(["Date", "Region"], as_index=False)["Revenue"].sum()
    fig = trend_line(trend_df, "Date", "Revenue", color="Region", y_title=f"{t('kpi.revenue')} ($)")
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    section_title(t("exec.revenue_by_region"), "🌍")
    by_region = df.groupby("Region", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    st.plotly_chart(
        bar_compare(by_region, "Region", "Revenue", color="Region", text_auto=True),
        width="stretch", config={"displayModeBar": False},
    )

with col2:
    section_title(t("revenue.by_product"), "📦")
    by_product = df.groupby("Product", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    st.plotly_chart(
        bar_compare(by_product, "Product", "Revenue", color="Product", text_auto=True),
        width="stretch", config={"displayModeBar": False},
    )

# ----------------------------------------------------------------------------
section_title(t("revenue.heatmap"), "🔥")
pivot = df.pivot_table(index="Region", columns="Product", values="Revenue", aggfunc="sum", fill_value=0)
st.plotly_chart(heatmap(pivot, value_suffix=""), width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title(t("revenue.driver_tree"), "🌳")
st.caption(t("revenue.driver_tree_caption"))
treemap_df = df.groupby(["Region", "Product"], as_index=False)["Revenue"].sum()
st.plotly_chart(
    driver_treemap(treemap_df, ["Region", "Product"], "Revenue"),
    width="stretch", config={"displayModeBar": False},
)

# ----------------------------------------------------------------------------
section_title(t("revenue.mom_growth"), "📊")
monthly = df.groupby("Month")["Revenue"].sum().sort_index()
growth = monthly.pct_change().fillna(0) * 100
growth_label = t("revenue.col_growth_pct")
growth_df = pd.DataFrame({"Month": growth.index, growth_label: growth.values})
fig_growth = bar_compare(growth_df, "Month", growth_label)
fig_growth.update_traces(marker_color=["#22C55E" if v >= 0 else "#F87171" for v in growth_df[growth_label]])
st.plotly_chart(fig_growth, width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title(t("revenue.detail_table"), "📋")
detail = df.groupby(["Region", "Product"]).agg(
    Revenue=("Revenue", "sum"), Units=("Units Sold", "sum"), Orders=("Revenue", "count"),
).reset_index().sort_values("Revenue", ascending=False)
detail["Revenue Share"] = (detail["Revenue"] / detail["Revenue"].sum() * 100).round(1).astype(str) + "%"
detail["Revenue"] = detail["Revenue"].apply(format_currency)
detail.columns = [t("sidebar.region"), t("sidebar.product"), t("kpi.revenue"),
                   t("revenue.col_units"), t("revenue.col_orders"), t("revenue.col_revenue_share")]
st.dataframe(detail, width="stretch", hide_index=True)
