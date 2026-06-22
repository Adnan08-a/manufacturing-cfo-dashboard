"""Forecasting -- statistical projections of revenue and profitability."""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.styling import inject_page_theme, page_header, kpi_grid, section_title, COLORS
from utils.app_state import render_sidebar_and_load
from utils.formatting import format_currency, format_pct
from utils.forecasting import monthly_series, forecast_holt_winters, forecast_linear
from utils.i18n import t

inject_page_theme()

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    t("nav.forecasting"),
    t("forecast.title"),
    t("forecast.subtitle"),
)

st.info(t("forecast.info"), icon="ℹ️")

# Use full date history for the selected region/product filters (ignore date filter for training)
df_hist = df_full[df_full["Region"].isin(regions) & df_full["Product"].isin(products)]

metric_options = ["Revenue", "EBITDA", "Gross Profit"]
metric_labels = {"Revenue": t("metric.revenue"), "EBITDA": t("metric.ebitda"), "Gross Profit": t("metric.gross_profit")}

c1, c2, c3 = st.columns(3)
with c1:
    metric = st.selectbox(
        t("forecast.metric_label"), metric_options,
        format_func=lambda v: metric_labels[v], key="fc_metric",
    )
with c2:
    horizon = st.slider(t("forecast.horizon_label"), 1, 12, 6, key="fc_horizon")
with c3:
    method_display = {"auto": t("forecast.model_auto"), "linear": t("forecast.model_linear")}
    method = st.radio(
        t("forecast.model_label"), ["auto", "linear"],
        format_func=lambda v: method_display[v],
        key="fc_method",
    )

metric_label = metric_labels[metric]
series = monthly_series(df_hist, metric)

if len(series) < 3:
    st.warning(t("forecast.no_history_warning"))
    st.stop()

if method == "auto":
    forecast_df, model_used = forecast_holt_winters(series, horizon)
else:
    forecast_df, model_used = forecast_linear(series, horizon), t("forecast.model_used_manual")

st.caption(t("forecast.model_used_caption", model=model_used, n=len(series)))

# ----------------------------------------------------------------------------
last_actual = series.iloc[-1]
forecast_total = forecast_df["forecast"].sum()
forecast_avg = forecast_df["forecast"].mean()
implied_growth = (forecast_avg - series.tail(min(3, len(series))).mean()) / series.tail(min(3, len(series))).mean() * 100 \
    if series.tail(min(3, len(series))).mean() else 0

kpi_grid([
    {"label": t("forecast.kpi_last_actual", metric=metric_label), "value": format_currency(last_actual)},
    {"label": t("forecast.kpi_total", horizon=horizon), "value": format_currency(forecast_total)},
    {"label": t("forecast.kpi_monthly_avg"), "value": format_currency(forecast_avg)},
    {"label": t("forecast.kpi_implied_trend"), "value": format_pct(implied_growth, signed=True)},
])

# ----------------------------------------------------------------------------
section_title(t("forecast.chart_title", metric=metric_label), "🔮")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=series.index, y=series.values, name=t("forecast.actual_label"), mode="lines+markers",
    line=dict(color=COLORS["sky_light"], width=3), marker=dict(size=6),
))
fig.add_trace(go.Scatter(
    x=forecast_df.index, y=forecast_df["forecast"], name=t("forecast.forecast_label"), mode="lines+markers",
    line=dict(color=COLORS["cyan"], width=3, dash="dash"), marker=dict(size=6),
))
fig.add_trace(go.Scatter(
    x=list(forecast_df.index) + list(forecast_df.index[::-1]),
    y=list(forecast_df["upper"]) + list(forecast_df["lower"][::-1]),
    fill="toself", fillcolor="rgba(34,211,238,0.12)",
    line=dict(color="rgba(0,0,0,0)"), name=t("forecast.confidence_band"), hoverinfo="skip",
))
fig.update_layout(height=440, yaxis_title=f"{metric_label} ($)", legend=dict(orientation="h", y=1.05))
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title(t("forecast.detail_table"), "📋")
table = forecast_df.copy()
table.index = table.index.strftime("%b %Y")
table = table.rename(columns={
    "forecast": t("forecast.col_forecast"),
    "lower": t("forecast.col_low"),
    "upper": t("forecast.col_high"),
})
table = table.map(lambda v: format_currency(v))
st.dataframe(table, width="stretch")

csv = forecast_df.reset_index().rename(columns={"index": "Month"}).to_csv(index=False)
st.download_button(
    t("forecast.download_btn"), csv,
    file_name=f"{metric.lower().replace(' ', '_')}_forecast.csv", mime="text/csv",
)
