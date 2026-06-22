"""
i18n.py
-------
Lightweight internationalization for the dashboard: English and Bosnian.

`t(key, **kwargs)` looks up `key` in the current language (stored in
st.session_state, persists across pages like the other filters) and formats
it with any keyword arguments via str.format(). Falls back to English, then
to the raw key, if a translation is missing.

Scope note: only app-authored UI text (labels, headers, captions, generated
commentary) is translated. Data values that come from the dataset itself
(Region/Product names such as "Asia" or "Product A") are left as-is, since
a user could upload their own dataset with arbitrary category values that
we have no way to translate correctly.
"""
from __future__ import annotations

import streamlit as st

LANG_KEY = "app_language"
DEFAULT_LANG = "en"
LANGUAGES = {"en": "English", "bs": "Bosanski"}


def get_lang() -> str:
    return st.session_state.get(LANG_KEY, DEFAULT_LANG)


def t(key: str, **kwargs) -> str:
    lang = get_lang()
    template = STRINGS.get(lang, {}).get(key)
    if template is None:
        template = STRINGS[DEFAULT_LANG].get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


def language_switcher() -> None:
    """Renders the language toggle. Call once, near the top of app.py's
    sidebar, before anything else reads t() on the current run."""
    with st.sidebar:
        current = get_lang()
        choice = st.radio(
            "🌐 Language / Jezik",
            options=list(LANGUAGES.keys()),
            format_func=lambda k: LANGUAGES[k],
            horizontal=True,
            index=list(LANGUAGES.keys()).index(current),
            key=LANG_KEY,
            label_visibility="collapsed",
        )


# ============================================================================
# Translation strings
# ============================================================================
STRINGS = {
    "en": {
        # --- Navigation / app shell -----------------------------------
        "nav.section_overview": "Overview",
        "nav.section_analysis": "Analysis",
        "nav.section_planning": "Planning",
        "nav.section_ai": "AI",
        "nav.home": "Home",
        "nav.executive_summary": "Executive Summary",
        "nav.revenue_analysis": "Revenue Analysis",
        "nav.profitability_analysis": "Profitability Analysis",
        "nav.operational_kpis": "Operational KPIs",
        "nav.forecasting": "Forecasting",
        "nav.scenario_planning": "Scenario Planning",
        "nav.variance_analysis": "Variance Analysis",
        "nav.ai_insights": "AI Insights",

        # --- Sidebar -----------------------------------------------------
        "sidebar.brand_title": "🏭 CFO Cockpit",
        "sidebar.brand_caption": "Manufacturing performance & planning",
        "sidebar.data_source": "📁 Data source",
        "sidebar.upload_label": "Upload your own dataset",
        "sidebar.upload_help": "Same schema as the bundled sample. Leave empty to use the sample dataset.",
        "sidebar.upload_caption": "Columns expected: Date, Region, Product, Revenue, Cost, Profit, "
                                   "Units Sold, Customer Satisfaction, Manufacturing Cost, Labor Hours, "
                                   "Machine Downtime, Inventory Levels, Order Lead Time, Return Rate, "
                                   "On-Time Delivery.",
        "sidebar.filters": "🔎 Filters",
        "sidebar.date_range": "Date range",
        "sidebar.region": "Region",
        "sidebar.product": "Product",
        "sidebar.reset_filters": "↺ Reset filters",
        "sidebar.dataset_caption": "Dataset: {n} records · {start} – {end}",
        "sidebar.no_data_warning": "No data matches the current filters. Adjust the filters in the sidebar.",
        "sidebar.load_error": "Could not load dataset: {error}",

        # --- Common / KPI labels (reused across pages) --------------------
        "kpi.revenue": "Revenue",
        "kpi.gross_profit": "Gross Profit",
        "kpi.ebitda": "EBITDA",
        "kpi.net_margin": "Net Margin",
        "kpi.net_profit": "Net Profit",
        "kpi.gross_margin": "Gross Margin",
        "kpi.ebitda_margin": "EBITDA Margin",
        "kpi.inventory_turns": "Inventory Turns",
        "kpi.working_capital": "Working Capital",
        "kpi.units_sold": "Units Sold",
        "kpi.total_revenue": "Total Revenue",
        "kpi.avg_monthly_revenue": "Avg Monthly Revenue",
        "kpi.avg_order_value": "Avg Order Value",
        "kpi.top_region": "Top Region",
        "kpi.top_product": "Top Product",
        "kpi.avg_inventory": "Avg Inventory",
        "kpi.avg_lead_time": "Avg Lead Time",
        "kpi.avg_downtime": "Avg Downtime",
        "kpi.total_labor_hours": "Total Labor Hours",
        "unit.days": "days",
        "unit.hrs": "hrs",

        # --- Chart / P&L line-item labels ---------------------------------
        "chart.revenue": "Revenue",
        "chart.cogs": "COGS",
        "chart.gross_profit": "Gross Profit",
        "chart.operating_exp": "Operating Exp.",
        "chart.ebitda": "EBITDA",

        # --- Home page -----------------------------------------------------
        "home.eyebrow": "Manufacturing CFO Cockpit",
        "home.title": "Welcome to your financial command center",
        "home.subtitle": "An end-to-end FP&A workspace covering revenue, profitability, operations, "
                          "forecasting, scenario planning, variance, and AI-generated insights — built "
                          "on your manufacturing performance data.",
        "home.revenue_trend": "Revenue trend",
        "home.navigate": "Navigate the cockpit",
        "home.nav_desc.executive_summary": "Headline KPIs, P&L bridge, and auto-generated commentary.",
        "home.nav_desc.revenue_analysis": "Trends, mix, and growth by region and product.",
        "home.nav_desc.profitability_analysis": "Margins, cost structure, and profitability heatmaps.",
        "home.nav_desc.operational_kpis": "Quality, delivery, inventory, and labor efficiency.",
        "home.nav_desc.forecasting": "Statistical revenue forecasts with adjustable horizon.",
        "home.nav_desc.scenario_planning": "Stress-test price, cost, and volume assumptions.",
        "home.nav_desc.variance_analysis": "Actual vs. prior-period bridges and variance tables.",
        "home.nav_desc.ai_insights": "Automated insight cards and natural-language Q&A.",
        "home.methodology_title": "📐 KPI methodology & data notes",
        "home.methodology_body": """
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
""",
        "home.footer_caption": "Showing {records} records across {regions} region(s) and {products} product(s).",

        # --- Executive Summary ----------------------------------------------
        "exec.title": "Performance at a glance",
        "exec.subtitle": "{start} – {end} · {n_regions} region(s) · {n_products} product(s), "
                          "vs. the prior period of equal length.",
        "exec.revenue_mix": "Revenue mix by product",
        "exec.pl_bridge": "P&L bridge: Revenue to EBITDA",
        "exec.revenue_by_region": "Revenue by region",
        "exec.top_bottom": "Top & bottom performers",
        "exec.commentary": "Executive commentary",
        "exec.commentary_caption": "Generated automatically from the metrics above -- no manual write-up needed.",
        "exec.col_avg_gross_margin": "Avg Gross Margin",

        # --- Revenue Analysis -------------------------------------------------
        "revenue.title": "Where revenue is coming from -- and how it's moving",
        "revenue.subtitle": "Trend, regional and product mix, growth rates, and a full revenue decomposition.",
        "revenue.granularity": "Trend granularity",
        "revenue.monthly": "Monthly",
        "revenue.daily": "Daily",
        "revenue.trend_by_month": "Revenue trend by month",
        "revenue.trend_by_day": "Revenue trend by day",
        "revenue.by_product": "Revenue by product",
        "revenue.heatmap": "Region × product revenue heatmap",
        "revenue.driver_tree": "Revenue decomposition (driver tree)",
        "revenue.driver_tree_caption": "Box size = revenue contribution. Click a region to drill into its products.",
        "revenue.mom_growth": "Month-over-month growth",
        "revenue.detail_table": "Revenue detail by region & product",
        "revenue.col_units": "Units",
        "revenue.col_orders": "Orders",
        "revenue.col_revenue_share": "Revenue Share",
        "revenue.col_growth_pct": "Growth %",

        # --- Profitability Analysis -------------------------------------------
        "profit.title": "Margins, cost structure, and where profit is made",
        "profit.subtitle": "Gross margin, EBITDA margin, and net margin trends, plus a segment-level "
                            "profitability view.",
        "profit.margin_trend": "Margin trend over time",
        "profit.margin_by_region": "Gross margin by region",
        "profit.margin_by_product": "Gross margin by product",
        "profit.heatmap": "Profitability heatmap: gross margin % by region × product",
        "profit.cost_structure": "Cost structure: Revenue → COGS → Operating Exp. → EBITDA",
        "profit.detail_table": "Profitability detail by segment",

        # --- Operational KPIs --------------------------------------------------
        "ops.title": "The shop-floor metrics that drive the P&L",
        "ops.subtitle": "Quality, on-time delivery, inventory efficiency, machine uptime, and labor productivity.",
        "ops.gauges": "Service-level gauges",
        "ops.gauge_on_time": "On-Time Delivery",
        "ops.gauge_satisfaction": "Customer Satisfaction (scaled to 100)",
        "ops.gauge_quality": "Quality Index (100 - 10×return rate)",
        "ops.inventory_over_time": "Inventory levels over time",
        "ops.units_over_time": "Units sold over time",
        "ops.otd_by_region": "On-time delivery by region",
        "ops.return_by_product": "Return rate by product",
        "ops.downtime_vs_otd": "Machine downtime vs. on-time delivery",
        "ops.downtime_caption": "Each point is one order/record; trendline highlights the relationship "
                                 "between downtime and service level.",
        "ops.correlations": "Operational metric correlations",
        "ops.lead_time_dist": "Order lead time distribution by product",
        "ops.scorecard": "Operational scorecard by region",
        "ops.col_on_time_pct": "On-Time %",
        "ops.col_return_rate_pct": "Return Rate %",
        "ops.col_avg_lead_time_d": "Avg Lead Time (d)",
        "ops.col_avg_downtime_h": "Avg Downtime (h)",
        "ops.col_avg_satisfaction": "Avg Satisfaction",
        "ops.col_avg_inventory": "Avg Inventory",

        # --- Forecasting -----------------------------------------------------
        "forecast.title": "Where performance is headed",
        "forecast.subtitle": "Statistical forecasts of revenue and EBITDA, built on the filtered history. "
                              "Use the controls below to change the horizon and forecasting method.",
        "forecast.info": "Forecasts use **filtered, unfiltered-by-date history** (the full dataset for the "
                          "selected regions/products) so the model has as much history as possible -- the "
                          "date filter sets the *forecast horizon*, not the training window.",
        "forecast.metric_label": "Metric to forecast",
        "forecast.horizon_label": "Forecast horizon (months)",
        "forecast.model_label": "Model",
        "forecast.model_auto": "Auto (Holt-Winters)",
        "forecast.model_linear": "Linear trend",
        "forecast.no_history_warning": "Not enough monthly history in the current filters to build a forecast.",
        "forecast.model_used_caption": "Model used: **{model}** · trained on {n} months of history.",
        "forecast.kpi_last_actual": "Last actual {metric}",
        "forecast.kpi_total": "Forecast total ({horizon}mo)",
        "forecast.kpi_monthly_avg": "Forecast monthly avg",
        "forecast.kpi_implied_trend": "Implied trend vs. recent avg",
        "forecast.chart_title": "{metric} forecast",
        "forecast.actual_label": "Actual",
        "forecast.forecast_label": "Forecast",
        "forecast.confidence_band": "Confidence band",
        "forecast.detail_table": "Forecast detail",
        "forecast.col_forecast": "Forecast",
        "forecast.col_low": "Low (≈10th pct)",
        "forecast.col_high": "High (≈90th pct)",
        "forecast.download_btn": "⬇️ Download forecast as CSV",
        "forecast.model_used_linear_insufficient": "Linear trend (insufficient history for seasonality)",
        "forecast.model_used_holt_winters": "Holt-Winters (trend + seasonal)",
        "forecast.model_used_fallback": "Linear trend (model fallback)",
        "forecast.model_used_manual": "Linear trend (manual selection)",
        "metric.revenue": "Revenue",
        "metric.ebitda": "EBITDA",
        "metric.gross_profit": "Gross Profit",

        # --- Scenario Planning --------------------------------------------------
        "scenario.title": "Stress-test the plan before the market does",
        "scenario.subtitle": "Adjust price, volume, cost, and opex assumptions to see the projected impact "
                              "on Revenue, Gross Profit, and EBITDA versus the current filtered baseline.",
        "scenario.drivers_header": "Scenario drivers",
        "scenario.price_change": "Price change (%)",
        "scenario.volume_change": "Volume change (%)",
        "scenario.cogs_change": "Unit COGS rate change (%)",
        "scenario.cogs_help": "Change in cost per unit, e.g. from input cost inflation or supplier negotiation.",
        "scenario.opex_change": "Operating expense change (%)",
        "scenario.opex_help": "Change in manufacturing/operating overhead, independent of volume.",
        "scenario.baseline_vs_scenario": "Baseline vs. scenario",
        "scenario.baseline_label": "Baseline (current filters)",
        "scenario.scenario_label": "Scenario",
        "scenario.ebitda_bridge": "EBITDA bridge: baseline → scenario",
        "scenario.bridge_baseline_ebitda": "Baseline EBITDA",
        "scenario.bridge_price_effect": "Price effect",
        "scenario.bridge_volume_effect": "Volume effect (net)",
        "scenario.bridge_cogs_effect": "COGS rate effect",
        "scenario.bridge_opex_effect": "Opex effect",
        "scenario.bridge_scenario_ebitda": "Scenario EBITDA",
        "scenario.sensitivity_header": "Driver sensitivity (illustrative ±10%, independent of sliders above)",
        "scenario.sensitivity_caption": "Ranks which lever moves EBITDA the most, holding all else at baseline.",
        "scenario.driver_price": "Price ±10%",
        "scenario.driver_volume": "Volume ±10%",
        "scenario.driver_cogs": "COGS rate ±10%",
        "scenario.driver_opex": "Opex ±10%",
        "scenario.favorable": "Favorable",
        "scenario.unfavorable": "Unfavorable",
        "scenario.ebitda_impact_axis": "EBITDA impact ($)",
        "scenario.summary_text": "At the current slider settings, the scenario shifts EBITDA by "
                                  "**{delta}** ({pct:+.1f}%) versus baseline, moving the EBITDA margin "
                                  "from **{m0}** to **{m1}**.",

        # --- Variance Analysis ---------------------------------------------------
        "variance.title": "Actual vs. expected -- and why",
        "variance.subtitle": "Compare the filtered period against the prior period or the same period last "
                              "year, with a full revenue bridge and segment-level variance detail.",
        "variance.compare_label": "Compare current period against",
        "variance.compare_prior": "Prior period (equal length)",
        "variance.compare_yoy": "Same period last year",
        "variance.no_comp_data": "No comparison-period data available for the selected filters/date range.",
        "variance.period_caption": "Current: {c_start} – {c_end}  ·  Comparison: {p_start} – {p_end}",
        "variance.bridge_title": "Revenue variance bridge by region",
        "variance.bridge_start_label": "Prior/Comp. Revenue",
        "variance.bridge_end_label": "Current Revenue",
        "variance.heatmap_title": "Variance heatmap: revenue % change by region × product",
        "variance.detail_table": "Variance detail by region & product",
        "variance.col_current": "Current",
        "variance.col_comparison": "Comparison",
        "variance.col_dollar_variance": "$ Variance",
        "variance.col_pct_variance": "% Variance",

        # --- AI Insights -------------------------------------------------------
        "ai.title": "Automated read on the numbers",
        "ai.subtitle": "Statistical insight generation runs automatically on every page load -- no API key "
                        "required. Connect an Anthropic API key below to unlock free-form Q&A on top.",
        "ai.cards_header": "Insight cards",
        "ai.cards_caption": "Generated from trends, outliers, and correlations in the filtered dataset.",
        "ai.tab_all": "All",
        "ai.cat_growth": "Growth",
        "ai.cat_risk": "Risk",
        "ai.cat_efficiency": "Efficiency",
        "ai.cat_recommendation": "Recommendation",
        "ai.no_insights_in_cat": "No insights in this category for the current filters.",
        "ai.ask_header": "Ask a question about this data",
        "ai.secret_key_success": "Using the Anthropic API key configured in this app's secrets.",
        "ai.no_key_warning": "No Anthropic API key detected in secrets. Paste a key below to use it for "
                              "this session only (it is not stored or sent anywhere except directly to the "
                              "Anthropic API), or add `ANTHROPIC_API_KEY` to your Streamlit secrets for "
                              "persistent access.",
        "ai.session_key_expander": "Add a session API key",
        "ai.session_key_input_label": "Anthropic API key",
        "ai.session_key_success": "Key set for this session. Ask your question below.",
        "ai.question_label": "Your question",
        "ai.question_placeholder": "e.g. Which region should we prioritize for margin improvement?",
        "ai.ask_button": "Ask",
        "ai.analyzing_spinner": "Analyzing the filtered data...",
        "ai.api_error": "Couldn't get an answer from the Anthropic API: {error}",
        "ai.need_key_info": "Add an API key above to enable live Q&A.",
        "ai.what_data_expander": "What data does the AI see?",
        "ai.what_data_caption": "Only an aggregated text summary of the currently filtered data (KPIs and "
                                 "revenue by region/product) is sent -- never the raw row-level dataset.",
        "ai.answer_tag": "🧠 AI answer",

        # --- Auto-generated executive commentary --------------------------------
        "commentary.no_data": "Not enough data in the selected filters to generate commentary.",
        "commentary.revenue_change": "Revenue {verb} **{pct:.1f}%** versus the prior period to "
                                      "**{revenue}**, with EBITDA margin at **{margin}** ({delta:+.1f} pts).",
        "commentary.verb_grew": "grew",
        "commentary.verb_declined": "declined",
        "commentary.revenue_total_only": "Revenue for the period totaled **{revenue}**.",
        "commentary.revenue_total_with_margin": "Revenue for the period totaled **{revenue}** with an "
                                                 "EBITDA margin of **{margin}**.",
        "commentary.region_lead_trail": "**{top}** led all regions with {top_rev} in revenue, while "
                                         "**{bottom}** trailed at {bottom_rev}.",
        "commentary.product_margin": "**{top}** carries the strongest gross margin at **{top_pct:.1f}%**, "
                                      "while **{bottom}** is lowest at {bottom_pct:.1f}%.",
        "commentary.low_on_time": "⚠️ On-time delivery averaged **{pct:.1f}%**, below the 85% service-level "
                                   "target — a risk to customer retention if it persists.",
        "commentary.high_return": "⚠️ Return rate is elevated at **{pct:.1f}%**, worth a quality-control review.",
        "commentary.low_turns": "Inventory is turning **{turns:.1f}x** annualized — slower turns tie up "
                                 "working capital ({wc} average inventory on hand).",

        # --- Auto-generated insight cards ---------------------------------------
        "insight.few_records_tag": "Data",
        "insight.few_records_text": "Broaden the filters to generate richer insights — too few records selected.",
        "insight.growth_driver_tag": "Growth driver",
        "insight.growth_driver_text": "<b>{product} in {region}</b> is the single largest revenue "
                                       "combination at {revenue} ({share:.1f}% of total revenue). Consider "
                                       "prioritizing capacity and marketing investment here.",
        "insight.momentum_tag": "Momentum",
        "insight.momentum_text": "Revenue accelerated <b>{pct:.1f}%</b> month-over-month in {month}, the "
                                  "strongest recent reading in the series.",
        "insight.op_risk_tag": "Operational risk",
        "insight.op_risk_text": "Machine downtime shows a negative correlation ({corr:.2f}) with on-time "
                                 "delivery — downtime spikes are likely contributing to missed delivery windows.",
        "insight.quality_risk_tag": "Quality risk",
        "insight.quality_risk_text": "<b>{product}</b> has a return rate of {pct:.1f}%, notably above the "
                                      "overall average of {avg:.1f}% — flag for quality review.",
        "insight.working_capital_tag": "Working capital",
        "insight.working_capital_text": "<b>{region}</b> carries the highest average inventory level "
                                         "({level:,.0f} units) — review safety-stock policy for potential "
                                         "working-capital release.",
        "insight.labor_prod_tag": "Labor productivity",
        "insight.labor_prod_text": "<b>{region}</b> produces the most units sold per labor hour "
                                    "({value:.2f}), the benchmark for other regions to target.",
        "insight.cx_tag": "Customer experience",
        "insight.cx_text": "Average customer satisfaction is {value:.1f}/5 — pair this with the quality and "
                            "delivery findings above to prioritize a service recovery plan.",
        "insight.next_step_tag": "Next step",
        "insight.next_step_text": "Use the Scenario Planning page to stress-test a margin-improvement plan "
                                   "(price, cost, or mix changes) against the trends identified here.",
    },

    "bs": {
        # --- Navigation / app shell -----------------------------------
        "nav.section_overview": "Pregled",
        "nav.section_analysis": "Analiza",
        "nav.section_planning": "Planiranje",
        "nav.section_ai": "AI",
        "nav.home": "Početna",
        "nav.executive_summary": "Izvršni sažetak",
        "nav.revenue_analysis": "Analiza prihoda",
        "nav.profitability_analysis": "Analiza profitabilnosti",
        "nav.operational_kpis": "Operativni KPI-jevi",
        "nav.forecasting": "Prognoza",
        "nav.scenario_planning": "Planiranje scenarija",
        "nav.variance_analysis": "Analiza odstupanja",
        "nav.ai_insights": "AI uvidi",

        # --- Sidebar -----------------------------------------------------
        "sidebar.brand_title": "🏭 CFO Kokpit",
        "sidebar.brand_caption": "Performanse i planiranje proizvodnje",
        "sidebar.data_source": "📁 Izvor podataka",
        "sidebar.upload_label": "Učitaj svoj skup podataka",
        "sidebar.upload_help": "Ista struktura kao priloženi uzorak. Ostavi prazno za korištenje uzorka podataka.",
        "sidebar.upload_caption": "Očekivane kolone: Date, Region, Product, Revenue, Cost, Profit, "
                                   "Units Sold, Customer Satisfaction, Manufacturing Cost, Labor Hours, "
                                   "Machine Downtime, Inventory Levels, Order Lead Time, Return Rate, "
                                   "On-Time Delivery.",
        "sidebar.filters": "🔎 Filteri",
        "sidebar.date_range": "Vremenski period",
        "sidebar.region": "Regija",
        "sidebar.product": "Proizvod",
        "sidebar.reset_filters": "↺ Resetuj filtere",
        "sidebar.dataset_caption": "Skup podataka: {n} zapisa · {start} – {end}",
        "sidebar.no_data_warning": "Nema podataka za odabrane filtere. Prilagodi filtere u bočnoj traci.",
        "sidebar.load_error": "Nije moguće učitati skup podataka: {error}",

        # --- Common / KPI labels (reused across pages) --------------------
        "kpi.revenue": "Prihod",
        "kpi.gross_profit": "Bruto dobit",
        "kpi.ebitda": "EBITDA",
        "kpi.net_margin": "Neto marža",
        "kpi.net_profit": "Neto dobit",
        "kpi.gross_margin": "Bruto marža",
        "kpi.ebitda_margin": "EBITDA marža",
        "kpi.inventory_turns": "Obrt zaliha",
        "kpi.working_capital": "Obrtni kapital",
        "kpi.units_sold": "Prodane jedinice",
        "kpi.total_revenue": "Ukupan prihod",
        "kpi.avg_monthly_revenue": "Prosj. mjesečni prihod",
        "kpi.avg_order_value": "Prosj. vrijednost narudžbe",
        "kpi.top_region": "Najbolja regija",
        "kpi.top_product": "Najbolji proizvod",
        "kpi.avg_inventory": "Prosječne zalihe",
        "kpi.avg_lead_time": "Prosj. vrijeme isporuke",
        "kpi.avg_downtime": "Prosječan zastoj",
        "kpi.total_labor_hours": "Ukupno radnih sati",
        "unit.days": "dana",
        "unit.hrs": "h",

        # --- Chart / P&L line-item labels ---------------------------------
        "chart.revenue": "Prihod",
        "chart.cogs": "COGS (trošak prodaje)",
        "chart.gross_profit": "Bruto dobit",
        "chart.operating_exp": "Operativni troškovi",
        "chart.ebitda": "EBITDA",

        # --- Home page -----------------------------------------------------
        "home.eyebrow": "CFO Kokpit za proizvodnju",
        "home.title": "Dobrodošli u svoj finansijski kontrolni centar",
        "home.subtitle": "Sveobuhvatan FP&A radni prostor koji pokriva prihode, profitabilnost, operacije, "
                          "prognoze, planiranje scenarija, analizu odstupanja i AI uvide — izgrađen na "
                          "podacima o performansama tvoje proizvodnje.",
        "home.revenue_trend": "Trend prihoda",
        "home.navigate": "Navigacija kroz kokpit",
        "home.nav_desc.executive_summary": "Ključni KPI-jevi, P&L most i automatski generisan komentar.",
        "home.nav_desc.revenue_analysis": "Trendovi, struktura i rast po regiji i proizvodu.",
        "home.nav_desc.profitability_analysis": "Marže, struktura troškova i toplotne mape profitabilnosti.",
        "home.nav_desc.operational_kpis": "Kvalitet, isporuka, zalihe i efikasnost rada.",
        "home.nav_desc.forecasting": "Statističke prognoze prihoda sa podesivim horizontom.",
        "home.nav_desc.scenario_planning": "Testiraj pretpostavke o cijeni, troškovima i obimu.",
        "home.nav_desc.variance_analysis": "Poređenje stvarnog sa prethodnim periodom i tabele odstupanja.",
        "home.nav_desc.ai_insights": "Automatske kartice uvida i pitanja-odgovori na prirodnom jeziku.",
        "home.methodology_title": "📐 Metodologija KPI-jeva i napomene o podacima",
        "home.methodology_body": """
Ovaj dashboard izračunava nekoliko standardnih FP&A metrika na osnovu izvornog skupa
podataka. Pošto uzorak podataka ne sadrži kompletan kontni plan, sljedeće konvencije
se dosljedno koriste na svakoj stranici:

- **Bruto dobit** = Prihod − Trošak (COGS)
- **Bruto marža %** = Bruto dobit ÷ Prihod
- **EBITDA** = Bruto dobit − Proizvodni trošak (tretiran kao operativni trošak)
- **EBITDA marža %** = EBITDA ÷ Prihod
- **Neto dobit** = vrijednost iz kolone `Profit` u skupu podataka, korištena bez izmjene
- **Neto marža %** = Neto dobit ÷ Prihod
- **Obrt zaliha** (godišnji nivo) = (Ukupan COGS ÷ Prosječan nivo zaliha) × (365 ÷ broj dana u periodu)
- **Obrtni kapital** je aproksimiran prosječnim nivoom zaliha, pošto skup podataka ne
  sadrži potraživanja/obaveze — posmatraj ga kao indikator uloženog kapitala u zalihe,
  a ne kao potpunu vrijednost obrtnog kapitala.

Pošto je ovo sintetički uzorak podataka, ove izvedene metrike se možda neće savršeno
slagati međusobno — gornje formule se dosljedno primjenjuju kako bi *poređenja* iz
perioda u period i iz segmenta u segment ostala smislena, čak i kada apsolutno
podudaranje nije garantovano.
""",
        "home.footer_caption": "Prikazano {records} zapisa za {regions} regija/-e i {products} proizvod(a).",

        # --- Executive Summary ----------------------------------------------
        "exec.title": "Performanse na prvi pogled",
        "exec.subtitle": "{start} – {end} · {n_regions} regija/-e · {n_products} proizvod(a), u odnosu na "
                          "prethodni period iste dužine.",
        "exec.revenue_mix": "Struktura prihoda po proizvodu",
        "exec.pl_bridge": "P&L most: od prihoda do EBITDA-e",
        "exec.revenue_by_region": "Prihod po regiji",
        "exec.top_bottom": "Najbolji i najslabiji učinak",
        "exec.commentary": "Komentar rukovodstva",
        "exec.commentary_caption": "Generisano automatski na osnovu gornjih metrika -- nije potrebno ručno pisanje.",
        "exec.col_avg_gross_margin": "Prosj. bruto marža",

        # --- Revenue Analysis -------------------------------------------------
        "revenue.title": "Odakle dolazi prihod -- i kako se kreće",
        "revenue.subtitle": "Trend, regionalna i proizvodna struktura, stope rasta i potpuna dekompozicija prihoda.",
        "revenue.granularity": "Granularnost trenda",
        "revenue.monthly": "Mjesečno",
        "revenue.daily": "Dnevno",
        "revenue.trend_by_month": "Trend prihoda po mjesecu",
        "revenue.trend_by_day": "Trend prihoda po danu",
        "revenue.by_product": "Prihod po proizvodu",
        "revenue.heatmap": "Toplotna mapa prihoda: regija × proizvod",
        "revenue.driver_tree": "Dekompozicija prihoda (stablo pokretača)",
        "revenue.driver_tree_caption": "Veličina polja = doprinos prihodu. Klikni na regiju za detalje po proizvodima.",
        "revenue.mom_growth": "Rast iz mjeseca u mjesec",
        "revenue.detail_table": "Detalji prihoda po regiji i proizvodu",
        "revenue.col_units": "Jedinice",
        "revenue.col_orders": "Narudžbe",
        "revenue.col_revenue_share": "Udio u prihodu",
        "revenue.col_growth_pct": "Rast %",

        # --- Profitability Analysis -------------------------------------------
        "profit.title": "Marže, struktura troškova i gdje se ostvaruje dobit",
        "profit.subtitle": "Trendovi bruto marže, EBITDA marže i neto marže, te pregled profitabilnosti "
                            "po segmentima.",
        "profit.margin_trend": "Trend marže kroz vrijeme",
        "profit.margin_by_region": "Bruto marža po regiji",
        "profit.margin_by_product": "Bruto marža po proizvodu",
        "profit.heatmap": "Toplotna mapa profitabilnosti: bruto marža % po regiji × proizvodu",
        "profit.cost_structure": "Struktura troškova: Prihod → COGS → Operativni troškovi → EBITDA",
        "profit.detail_table": "Detalji profitabilnosti po segmentu",

        # --- Operational KPIs --------------------------------------------------
        "ops.title": "Pogonske metrike koje pokreću P&L",
        "ops.subtitle": "Kvalitet, isporuka na vrijeme, efikasnost zaliha, rad mašina i produktivnost rada.",
        "ops.gauges": "Indikatori nivoa usluge",
        "ops.gauge_on_time": "Isporuka na vrijeme",
        "ops.gauge_satisfaction": "Zadovoljstvo kupaca (na skali do 100)",
        "ops.gauge_quality": "Indeks kvaliteta (100 - 10×stopa povrata)",
        "ops.inventory_over_time": "Nivo zaliha kroz vrijeme",
        "ops.units_over_time": "Prodane jedinice kroz vrijeme",
        "ops.otd_by_region": "Isporuka na vrijeme po regiji",
        "ops.return_by_product": "Stopa povrata po proizvodu",
        "ops.downtime_vs_otd": "Zastoj mašina naspram isporuke na vrijeme",
        "ops.downtime_caption": "Svaka tačka je jedna narudžba/zapis; linija trenda prikazuje odnos između "
                                 "zastoja i nivoa usluge.",
        "ops.correlations": "Korelacije operativnih metrika",
        "ops.lead_time_dist": "Distribucija vremena isporuke narudžbe po proizvodu",
        "ops.scorecard": "Operativna kartica rezultata po regiji",
        "ops.col_on_time_pct": "Na vrijeme %",
        "ops.col_return_rate_pct": "Stopa povrata %",
        "ops.col_avg_lead_time_d": "Prosj. vrijeme isporuke (d)",
        "ops.col_avg_downtime_h": "Prosj. zastoj (h)",
        "ops.col_avg_satisfaction": "Prosj. zadovoljstvo",
        "ops.col_avg_inventory": "Prosj. zalihe",

        # --- Forecasting -----------------------------------------------------
        "forecast.title": "Kuda performanse idu",
        "forecast.subtitle": "Statističke prognoze prihoda i EBITDA-e, zasnovane na filtriranoj istoriji. "
                              "Koristi kontrole ispod za promjenu horizonta i metode prognoziranja.",
        "forecast.info": "Prognoze koriste **filtriranu istoriju bez filtera po datumu** (kompletan skup "
                          "podataka za odabrane regije/proizvode) kako bi model imao što više istorijskih "
                          "podataka -- filter datuma određuje *horizont prognoze*, a ne period treniranja modela.",
        "forecast.metric_label": "Metrika za prognozu",
        "forecast.horizon_label": "Horizont prognoze (mjeseci)",
        "forecast.model_label": "Model",
        "forecast.model_auto": "Automatski (Holt-Winters)",
        "forecast.model_linear": "Linearni trend",
        "forecast.no_history_warning": "Nema dovoljno mjesečne istorije u trenutnim filterima za izradu prognoze.",
        "forecast.model_used_caption": "Korišten model: **{model}** · treniran na {n} mjeseci istorije.",
        "forecast.kpi_last_actual": "Posljednji stvarni {metric}",
        "forecast.kpi_total": "Ukupna prognoza ({horizon}mj)",
        "forecast.kpi_monthly_avg": "Prosječna mjesečna prognoza",
        "forecast.kpi_implied_trend": "Implicirani trend vs. nedavni prosjek",
        "forecast.chart_title": "Prognoza: {metric}",
        "forecast.actual_label": "Stvarno",
        "forecast.forecast_label": "Prognoza",
        "forecast.confidence_band": "Interval pouzdanosti",
        "forecast.detail_table": "Detalji prognoze",
        "forecast.col_forecast": "Prognoza",
        "forecast.col_low": "Niže (≈10. percentil)",
        "forecast.col_high": "Više (≈90. percentil)",
        "forecast.download_btn": "⬇️ Preuzmi prognozu kao CSV",
        "forecast.model_used_linear_insufficient": "Linearni trend (nedovoljno istorije za sezonalnost)",
        "forecast.model_used_holt_winters": "Holt-Winters (trend + sezonalnost)",
        "forecast.model_used_fallback": "Linearni trend (rezervni model)",
        "forecast.model_used_manual": "Linearni trend (ručni odabir)",
        "metric.revenue": "Prihod",
        "metric.ebitda": "EBITDA",
        "metric.gross_profit": "Bruto dobit",

        # --- Scenario Planning --------------------------------------------------
        "scenario.title": "Testiraj plan prije nego što to uradi tržište",
        "scenario.subtitle": "Prilagodi pretpostavke o cijeni, obimu, troškovima i operativnim troškovima "
                              "da vidiš projektovani uticaj na prihod, bruto dobit i EBITDA-u u odnosu na "
                              "trenutnu filtriranu osnovu.",
        "scenario.drivers_header": "Pokretači scenarija",
        "scenario.price_change": "Promjena cijene (%)",
        "scenario.volume_change": "Promjena obima (%)",
        "scenario.cogs_change": "Promjena jediničnog troška, COGS (%)",
        "scenario.cogs_help": "Promjena troška po jedinici, npr. zbog inflacije ulaznih troškova ili "
                               "pregovora sa dobavljačem.",
        "scenario.opex_change": "Promjena operativnih troškova (%)",
        "scenario.opex_help": "Promjena proizvodnih/operativnih režijskih troškova, nezavisno od obima.",
        "scenario.baseline_vs_scenario": "Osnova naspram scenarija",
        "scenario.baseline_label": "Osnova (trenutni filteri)",
        "scenario.scenario_label": "Scenarij",
        "scenario.ebitda_bridge": "EBITDA most: osnova → scenarij",
        "scenario.bridge_baseline_ebitda": "Osnovna EBITDA",
        "scenario.bridge_price_effect": "Efekat cijene",
        "scenario.bridge_volume_effect": "Efekat obima (neto)",
        "scenario.bridge_cogs_effect": "Efekat troška (COGS)",
        "scenario.bridge_opex_effect": "Efekat operativnih troškova",
        "scenario.bridge_scenario_ebitda": "EBITDA scenarija",
        "scenario.sensitivity_header": "Osjetljivost pokretača (ilustrativno ±10%, nezavisno od klizača iznad)",
        "scenario.sensitivity_caption": "Rangira koja poluga najviše pomjera EBITDA-u, uz sve ostalo nepromijenjeno.",
        "scenario.driver_price": "Cijena ±10%",
        "scenario.driver_volume": "Obim ±10%",
        "scenario.driver_cogs": "Stopa COGS-a ±10%",
        "scenario.driver_opex": "Operativni troškovi ±10%",
        "scenario.favorable": "Povoljno",
        "scenario.unfavorable": "Nepovoljno",
        "scenario.ebitda_impact_axis": "Uticaj na EBITDA-u ($)",
        "scenario.summary_text": "Uz trenutne postavke klizača, scenarij mijenja EBITDA-u za **{delta}** "
                                  "({pct:+.1f}%) u odnosu na osnovu, pomjerajući EBITDA maržu sa **{m0}** "
                                  "na **{m1}**.",

        # --- Variance Analysis ---------------------------------------------------
        "variance.title": "Stvarno naspram očekivanog -- i zašto",
        "variance.subtitle": "Uporedi filtrirani period sa prethodnim periodom ili istim periodom prošle "
                              "godine, uz potpuni most prihoda i detalje odstupanja po segmentu.",
        "variance.compare_label": "Uporedi trenutni period sa",
        "variance.compare_prior": "Prethodni period (iste dužine)",
        "variance.compare_yoy": "Isti period prošle godine",
        "variance.no_comp_data": "Nema dostupnih podataka za uporedni period za odabrane filtere/period.",
        "variance.period_caption": "Trenutno: {c_start} – {c_end}  ·  Poređenje: {p_start} – {p_end}",
        "variance.bridge_title": "Most odstupanja prihoda po regiji",
        "variance.bridge_start_label": "Prethodni/uporedni prihod",
        "variance.bridge_end_label": "Trenutni prihod",
        "variance.heatmap_title": "Toplotna mapa odstupanja: % promjene prihoda po regiji × proizvodu",
        "variance.detail_table": "Detalji odstupanja po regiji i proizvodu",
        "variance.col_current": "Trenutno",
        "variance.col_comparison": "Poređenje",
        "variance.col_dollar_variance": "Odstupanje ($)",
        "variance.col_pct_variance": "Odstupanje (%)",

        # --- AI Insights -------------------------------------------------------
        "ai.title": "Automatsko tumačenje brojki",
        "ai.subtitle": "Statistički uvidi se generišu automatski pri svakom učitavanju stranice -- nije "
                        "potreban API ključ. Poveži Anthropic API ključ ispod da otključaš pitanja i "
                        "odgovore u slobodnoj formi.",
        "ai.cards_header": "Kartice uvida",
        "ai.cards_caption": "Generisano na osnovu trendova, izuzetaka i korelacija u filtriranom skupu podataka.",
        "ai.tab_all": "Sve",
        "ai.cat_growth": "Rast",
        "ai.cat_risk": "Rizik",
        "ai.cat_efficiency": "Efikasnost",
        "ai.cat_recommendation": "Preporuka",
        "ai.no_insights_in_cat": "Nema uvida u ovoj kategoriji za trenutne filtere.",
        "ai.ask_header": "Postavi pitanje o ovim podacima",
        "ai.secret_key_success": "Koristi se Anthropic API ključ podešen u tajnama (secrets) ove aplikacije.",
        "ai.no_key_warning": "Nije pronađen Anthropic API ključ u tajnama. Zalijepi ključ ispod da ga "
                              "koristiš samo za ovu sesiju (ne čuva se niti šalje nigdje osim direktno na "
                              "Anthropic API), ili dodaj `ANTHROPIC_API_KEY` u Streamlit tajne za trajan pristup.",
        "ai.session_key_expander": "Dodaj API ključ za sesiju",
        "ai.session_key_input_label": "Anthropic API ključ",
        "ai.session_key_success": "Ključ je postavljen za ovu sesiju. Postavi svoje pitanje ispod.",
        "ai.question_label": "Tvoje pitanje",
        "ai.question_placeholder": "npr. Koju regiju treba prioritizovati za poboljšanje marže?",
        "ai.ask_button": "Pitaj",
        "ai.analyzing_spinner": "Analiziram filtrirane podatke...",
        "ai.api_error": "Nije moguće dobiti odgovor sa Anthropic API-ja: {error}",
        "ai.need_key_info": "Dodaj API ključ iznad da omogućiš pitanja uživo.",
        "ai.what_data_expander": "Koje podatke AI vidi?",
        "ai.what_data_caption": "Šalje se samo agregirani tekstualni sažetak trenutno filtriranih podataka "
                                 "(KPI-jevi i prihod po regiji/proizvodu) -- nikada sirovi podaci na nivou reda.",
        "ai.answer_tag": "🧠 AI odgovor",

        # --- Auto-generated executive commentary --------------------------------
        "commentary.no_data": "Nema dovoljno podataka u odabranim filterima za generisanje komentara.",
        "commentary.revenue_change": "Prihod je {verb} za **{pct:.1f}%** u odnosu na prethodni period na "
                                      "**{revenue}**, sa EBITDA maržom od **{margin}** ({delta:+.1f} p.p.).",
        "commentary.verb_grew": "porastao",
        "commentary.verb_declined": "opao",
        "commentary.revenue_total_only": "Prihod za period iznosio je **{revenue}**.",
        "commentary.revenue_total_with_margin": "Prihod za period iznosio je **{revenue}**, sa EBITDA "
                                                 "maržom od **{margin}**.",
        "commentary.region_lead_trail": "**{top}** je predvodila sve regije sa {top_rev} prihoda, dok je "
                                         "**{bottom}** zaostajala sa {bottom_rev}.",
        "commentary.product_margin": "**{top}** ima najjaču bruto maržu od **{top_pct:.1f}%**, dok "
                                      "**{bottom}** ima najnižu od {bottom_pct:.1f}%.",
        "commentary.low_on_time": "⚠️ Isporuka na vrijeme je u prosjeku iznosila **{pct:.1f}%**, ispod "
                                   "ciljanog nivoa usluge od 85% — rizik za zadržavanje kupaca ako se nastavi.",
        "commentary.high_return": "⚠️ Stopa povrata je povišena na **{pct:.1f}%**, vrijedi razmotriti "
                                   "kontrolu kvaliteta.",
        "commentary.low_turns": "Zalihe se obrću **{turns:.1f}x** godišnje — sporiji obrt vezuje obrtni "
                                 "kapital ({wc} prosječnih zaliha na stanju).",

        # --- Auto-generated insight cards ---------------------------------------
        "insight.few_records_tag": "Podaci",
        "insight.few_records_text": "Proširi filtere za bogatije uvide — odabrano je premalo zapisa.",
        "insight.growth_driver_tag": "Pokretač rasta",
        "insight.growth_driver_text": "<b>{product} u regiji {region}</b> je pojedinačno najveća "
                                       "kombinacija prihoda sa {revenue} ({share:.1f}% ukupnog prihoda). "
                                       "Razmotri prioritizaciju kapaciteta i marketinških ulaganja ovdje.",
        "insight.momentum_tag": "Zamah",
        "insight.momentum_text": "Prihod je ubrzao <b>{pct:.1f}%</b> u odnosu na prethodni mjesec u "
                                  "{month}, najjače nedavno očitanje u nizu.",
        "insight.op_risk_tag": "Operativni rizik",
        "insight.op_risk_text": "Zastoj mašina pokazuje negativnu korelaciju ({corr:.2f}) sa isporukom na "
                                 "vrijeme — skokovi zastoja vjerovatno doprinose propuštenim rokovima isporuke.",
        "insight.quality_risk_tag": "Rizik kvaliteta",
        "insight.quality_risk_text": "<b>{product}</b> ima stopu povrata od {pct:.1f}%, znatno iznad "
                                      "ukupnog prosjeka od {avg:.1f}% — označi za pregled kvaliteta.",
        "insight.working_capital_tag": "Obrtni kapital",
        "insight.working_capital_text": "<b>{region}</b> ima najviši prosječni nivo zaliha ({level:,.0f} "
                                         "jedinica) — razmotri politiku sigurnosnih zaliha radi mogućeg "
                                         "oslobađanja obrtnog kapitala.",
        "insight.labor_prod_tag": "Produktivnost rada",
        "insight.labor_prod_text": "<b>{region}</b> ostvaruje najviše prodanih jedinica po radnom satu "
                                    "({value:.2f}), referentna vrijednost za ostale regije.",
        "insight.cx_tag": "Iskustvo kupaca",
        "insight.cx_text": "Prosječno zadovoljstvo kupaca je {value:.1f}/5 — kombinuj ovo sa gornjim "
                            "nalazima o kvalitetu i isporuci za prioritizaciju plana oporavka usluge.",
        "insight.next_step_tag": "Sljedeći korak",
        "insight.next_step_text": "Koristi stranicu Planiranje scenarija da testiraš plan poboljšanja "
                                   "marže (promjene cijene, troškova ili strukture) naspram ovdje "
                                   "identifikovanih trendova.",
    },
}
