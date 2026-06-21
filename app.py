"""
app.py
------
Landing page for the Manufacturing CFO Cockpit. Sets up the page theme,
loads data, renders global filters, and gives a quick orientation snapshot
before the user dives into the eight analysis pages in the sidebar.
"""
import streamlit as st

from utils.styling import configure_page, page_header, kpi_grid, section_title
from utils.app_state import render_sidebar_and_load
from utils.kpis import compute_kpis
from utils.formatting import format_currency, format_pct, format_number
from utils.charts import trend_line

configure_page("Home", "🏠")

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    "Manufacturing CFO Cockpit",
    "Welcome to your financial command center",
    "An end-to-end FP&A workspace covering revenue, profitability, operations, "
    "forecasting, scenario planning, variance, and AI-generated insights — built "
    "on your manufacturing performance data.",
)

k = compute_kpis(df)

kpi_grid([
    {"label": "Revenue", "value": format_currency(k["revenue"])},
    {"label": "Gross Profit", "value": format_currency(k["gross_profit"])},
    {"label": "EBITDA", "value": format_currency(k["ebitda"])},
    {"label": "Net Margin", "value": format_pct(k["net_margin"])},
    {"label": "Inventory Turns", "value": f"{k['inventory_turns']:.1f}x"},
    {"label": "Working Capital", "value": format_currency(k["working_capital"])},
])

col1, col2 = st.columns([2, 1])

with col1:
    section_title("Revenue trend", "📈")
    monthly = df.groupby("Month", as_index=False)["Revenue"].sum()
    fig = trend_line(monthly, "Month", "Revenue", title="", y_title="Revenue ($)")
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with col2:
    section_title("Navigate the cockpit", "🧭")
    nav_items = [
        ("📊", "Executive Summary", "Headline KPIs, P&L bridge, and auto-generated commentary."),
        ("💵", "Revenue Analysis", "Trends, mix, and growth by region and product."),
        ("📈", "Profitability Analysis", "Margins, cost structure, and profitability heatmaps."),
        ("⚙️", "Operational KPIs", "Quality, delivery, inventory, and labor efficiency."),
        ("🔮", "Forecasting", "Statistical revenue forecasts with adjustable horizon."),
        ("🎯", "Scenario Planning", "Stress-test price, cost, and volume assumptions."),
        ("📋", "Variance Analysis", "Actual vs. prior-period bridges and variance tables."),
        ("🧠", "AI Insights", "Automated insight cards and natural-language Q&A."),
    ]
    for icon, name, desc in nav_items:
        st.markdown(
            f"**{icon} {name}**  \n<span style='font-size:0.85rem;color:#9FB3CC'>{desc}</span>",
            unsafe_allow_html=True,
        )

st.markdown("---")

with st.expander("📐 KPI methodology & data notes"):
    st.markdown(
        """
        This dashboard derives a few standard FP&A metrics from the raw dataset. Since the
        sample dataset doesn't include a full chart of accounts, the following conventions
        are used consistently across every page:

        - **Gross Profit** = Revenue − Cost (COGS)
        - **Gross Margin %** = Gross Profit ÷ Revenue
        - **EBITDA** = Gross Profit − Manufacturing Cost (treated as operating expense)
        - **EBITDA Margin %** = EBITDA ÷ Revenue
        - **Net Profit** = the dataset's reported `Profit` figure, used as-is
        - **Net Margin %** = Net Profit ÷ Revenue
        - **Inventory Turns** (annualized) = (Total COGS ÷ Average Inventory Level) × (365 ÷ days in period)
        - **Working Capital** is approximated by average Inventory Levels, since the dataset
          doesn't include receivables/payables — treat it as an inventory-investment proxy
          rather than a full working-capital figure.

        Because this is a synthetic sample dataset, these derived metrics may not reconcile
        perfectly with one another — the formulas above are applied consistently so that
        period-over-period and segment-over-segment *comparisons* remain meaningful even
        where absolute reconciliation isn't guaranteed.
        """
    )

st.caption(
    f"Showing {format_number(k['record_count'])} records across "
    f"{len(regions)} region(s) and {len(products)} product(s)."
)
