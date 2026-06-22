"""
app.py
------
Entry point and navigation router for the Manufacturing CFO Cockpit.

Uses Streamlit's st.navigation/st.Page API so that page titles and icons are
set explicitly in code rather than parsed from filenames -- this avoids any
cross-platform filename-encoding issues with emoji (a real pitfall when a
repo is cloned/extracted on Windows). st.set_page_config() is called exactly
once here, via apply_base_config(); individual pages call inject_page_theme()
instead.
"""
import streamlit as st

from utils.styling import apply_base_config
from utils.i18n import language_switcher, t

apply_base_config()
language_switcher()

pages = {
    t("nav.section_overview"): [
        st.Page("pages/home.py", title=t("nav.home"), icon="🏠", default=True),
        st.Page("pages/1_executive_summary.py", title=t("nav.executive_summary"), icon="📊"),
    ],
    t("nav.section_analysis"): [
        st.Page("pages/2_revenue_analysis.py", title=t("nav.revenue_analysis"), icon="💵"),
        st.Page("pages/3_profitability_analysis.py", title=t("nav.profitability_analysis"), icon="📈"),
        st.Page("pages/4_operational_kpis.py", title=t("nav.operational_kpis"), icon="⚙️"),
    ],
    t("nav.section_planning"): [
        st.Page("pages/5_forecasting.py", title=t("nav.forecasting"), icon="🔮"),
        st.Page("pages/6_scenario_planning.py", title=t("nav.scenario_planning"), icon="🎯"),
        st.Page("pages/7_variance_analysis.py", title=t("nav.variance_analysis"), icon="📋"),
    ],
    t("nav.section_ai"): [
        st.Page("pages/8_ai_insights.py", title=t("nav.ai_insights"), icon="🧠"),
    ],
}

pg = st.navigation(pages)
pg.run()
