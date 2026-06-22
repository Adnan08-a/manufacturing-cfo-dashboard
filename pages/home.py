"""
home.py
-------
Landing page for the Manufacturing CFO Cockpit. Loads data, renders global
filters, and gives a quick orientation snapshot before the user dives into
the eight analysis pages in the sidebar.
"""
import streamlit as st

from utils.styling import inject_page_theme, page_header, kpi_grid, section_title
from utils.app_state import render_sidebar_and_load
from utils.kpis import compute_kpis
from utils.formatting import format_currency, format_pct, format_number
from utils.charts import trend_line
from utils.i18n import t

inject_page_theme()

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    t("home.eyebrow"),
    t("home.title"),
    t("home.subtitle"),
)

k = compute_kpis(df)

kpi_grid([
    {"label": t("kpi.revenue"), "value": format_currency(k["revenue"])},
    {"label": t("kpi.gross_profit"), "value": format_currency(k["gross_profit"])},
    {"label": t("kpi.ebitda"), "value": format_currency(k["ebitda"])},
    {"label": t("kpi.net_margin"), "value": format_pct(k["net_margin"])},
    {"label": t("kpi.inventory_turns"), "value": f"{k['inventory_turns']:.1f}x"},
    {"label": t("kpi.working_capital"), "value": format_currency(k["working_capital"])},
])

col1, col2 = st.columns([2, 1])

with col1:
    section_title(t("home.revenue_trend"), "📈")
    monthly = df.groupby("Month", as_index=False)["Revenue"].sum()
    fig = trend_line(monthly, "Month", "Revenue", title="", y_title=f"{t('kpi.revenue')} ($)")
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with col2:
    section_title(t("home.navigate"), "🧭")
    nav_items = [
        ("📊", t("nav.executive_summary"), t("home.nav_desc.executive_summary")),
        ("💵", t("nav.revenue_analysis"), t("home.nav_desc.revenue_analysis")),
        ("📈", t("nav.profitability_analysis"), t("home.nav_desc.profitability_analysis")),
        ("⚙️", t("nav.operational_kpis"), t("home.nav_desc.operational_kpis")),
        ("🔮", t("nav.forecasting"), t("home.nav_desc.forecasting")),
        ("🎯", t("nav.scenario_planning"), t("home.nav_desc.scenario_planning")),
        ("📋", t("nav.variance_analysis"), t("home.nav_desc.variance_analysis")),
        ("🧠", t("nav.ai_insights"), t("home.nav_desc.ai_insights")),
    ]
    for icon, name, desc in nav_items:
        st.markdown(
            f"**{icon} {name}**  \n<span style='font-size:0.85rem;color:#9FB3CC'>{desc}</span>",
            unsafe_allow_html=True,
        )

st.markdown("---")

with st.expander(t("home.methodology_title")):
    st.markdown(t("home.methodology_body"))

st.caption(t(
    "home.footer_caption",
    records=format_number(k["record_count"]),
    regions=len(regions),
    products=len(products),
))
