"""Executive Summary -- headline KPIs, P&L bridge, and auto-generated commentary."""
import pandas as pd
import streamlit as st

from utils.styling import inject_page_theme, page_header, kpi_grid, section_title
from utils.app_state import render_sidebar_and_load
from utils.data_loader import get_prior_period
from utils.kpis import compute_kpis, pct_change
from utils.formatting import format_currency, format_pct, format_delta
from utils.charts import trend_line, waterfall, bar_compare, donut
from utils.insights import generate_executive_commentary
from utils.i18n import t

inject_page_theme()

df_full, df, date_range, regions, products = render_sidebar_and_load()
df_prior = get_prior_period(df_full, date_range)
df_prior = df_prior[df_prior["Region"].isin(regions) & df_prior["Product"].isin(products)]

page_header(
    t("nav.executive_summary"),
    t("exec.title"),
    t(
        "exec.subtitle",
        start=f"{pd.Timestamp(date_range[0]):%b %d, %Y}",
        end=f"{pd.Timestamp(date_range[1]):%b %d, %Y}",
        n_regions=len(regions), n_products=len(products),
    ),
)

k = compute_kpis(df)
kp = compute_kpis(df_prior) if not df_prior.empty else None


def _delta(curr, prior):
    if kp is None:
        return None, "neutral"
    chg = pct_change(curr, prior)
    if chg is None:
        return None, "neutral"
    return format_delta(chg), ("positive" if chg >= 0 else "negative")


d_rev, s_rev = _delta(k["revenue"], kp["revenue"] if kp else None)
d_gp, s_gp = _delta(k["gross_profit"], kp["gross_profit"] if kp else None)
d_eb, s_eb = _delta(k["ebitda"], kp["ebitda"] if kp else None)
d_nm, s_nm = _delta(k["net_margin"], kp["net_margin"] if kp else None)
d_it, s_it = _delta(k["inventory_turns"], kp["inventory_turns"] if kp else None)
d_wc, s_wc = _delta(k["working_capital"], kp["working_capital"] if kp else None)

kpi_grid([
    {"label": t("kpi.revenue"), "value": format_currency(k["revenue"]), "delta": d_rev, "delta_sign": s_rev},
    {"label": t("kpi.gross_profit"), "value": format_currency(k["gross_profit"]), "delta": d_gp, "delta_sign": s_gp},
    {"label": t("kpi.ebitda"), "value": format_currency(k["ebitda"]), "delta": d_eb, "delta_sign": s_eb},
    {"label": t("kpi.net_margin"), "value": format_pct(k["net_margin"]), "delta": d_nm, "delta_sign": s_nm},
    {"label": t("kpi.inventory_turns"), "value": f"{k['inventory_turns']:.1f}x", "delta": d_it, "delta_sign": s_it},
    {"label": t("kpi.working_capital"), "value": format_currency(k["working_capital"]), "delta": d_wc, "delta_sign": s_wc},
])

# ----------------------------------------------------------------------------
left, right = st.columns([1.5, 1])

with left:
    section_title(t("home.revenue_trend"), "📈")
    monthly = df.groupby("Month", as_index=False)["Revenue"].sum()
    fig = trend_line(monthly, "Month", "Revenue", y_title=f"{t('kpi.revenue')} ($)")
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with right:
    section_title(t("exec.revenue_mix"), "🥧")
    by_product = df.groupby("Product", as_index=False)["Revenue"].sum()
    st.plotly_chart(donut(by_product, "Product", "Revenue"), width="stretch",
                     config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title(t("exec.pl_bridge"), "🌉")
labels = [t("chart.revenue"), t("chart.cogs"), t("chart.gross_profit"), t("chart.operating_exp"), t("chart.ebitda")]
values = [k["revenue"], -k["cost"], k["gross_profit"], -(k["gross_profit"] - k["ebitda"]), k["ebitda"]]
measures = ["absolute", "relative", "total", "relative", "total"]
st.plotly_chart(
    waterfall(labels, values, measures, height=420),
    width="stretch", config={"displayModeBar": False},
)

# ----------------------------------------------------------------------------
col_a, col_b = st.columns(2)

with col_a:
    section_title(t("exec.revenue_by_region"), "🌍")
    by_region = df.groupby("Region", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    st.plotly_chart(
        bar_compare(by_region, "Region", "Revenue", color="Region"),
        width="stretch", config={"displayModeBar": False},
    )

with col_b:
    section_title(t("exec.top_bottom"), "🏆")
    perf = df.groupby(["Region", "Product"]).agg(
        Revenue=("Revenue", "sum"), Gross_Margin=("Gross Margin %", "mean")
    ).reset_index().sort_values("Revenue", ascending=False)
    perf["Revenue"] = perf["Revenue"].apply(format_currency)
    perf["Gross_Margin"] = perf["Gross_Margin"].round(1).astype(str) + "%"
    perf.columns = [t("sidebar.region"), t("sidebar.product"), t("kpi.revenue"), t("exec.col_avg_gross_margin")]
    st.dataframe(
        pd.concat([perf.head(3), perf.tail(3)]),
        width="stretch", hide_index=True, height=240,
    )

# ----------------------------------------------------------------------------
section_title(t("exec.commentary"), "🧠")
st.caption(t("exec.commentary_caption"))
commentary = generate_executive_commentary(df, df_prior)
for line in commentary:
    st.markdown(f"- {line}")
