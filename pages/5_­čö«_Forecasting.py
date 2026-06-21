"""Forecasting -- statistical projections of revenue and profitability."""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.styling import configure_page, page_header, kpi_grid, section_title, COLORS
from utils.app_state import render_sidebar_and_load
from utils.formatting import format_currency, format_pct
from utils.forecasting import monthly_series, forecast_holt_winters, forecast_linear

configure_page("Forecasting", "🔮")

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    "Forecasting",
    "Where performance is headed",
    "Statistical forecasts of revenue and EBITDA, built on the filtered history. "
    "Use the controls below to change the horizon and forecasting method.",
)

st.info(
    "Forecasts use **filtered, unfiltered-by-date history** (the full dataset for the selected "
    "regions/products) so the model has as much history as possible -- the date filter sets "
    "the *forecast horizon*, not the training window.",
    icon="ℹ️",
)

# Use full date history for the selected region/product filters (ignore date filter for training)
df_hist = df_full[df_full["Region"].isin(regions) & df_full["Product"].isin(products)]

c1, c2, c3 = st.columns(3)
with c1:
    metric = st.selectbox("Metric to forecast", ["Revenue", "EBITDA", "Gross Profit"], key="fc_metric")
with c2:
    horizon = st.slider("Forecast horizon (months)", 1, 12, 6, key="fc_horizon")
with c3:
    method = st.radio("Model", ["Auto (Holt-Winters)", "Linear trend"], key="fc_method")

series = monthly_series(df_hist, metric)

if len(series) < 3:
    st.warning("Not enough monthly history in the current filters to build a forecast.")
    st.stop()

if method.startswith("Auto"):
    forecast_df, model_used = forecast_holt_winters(series, horizon)
else:
    forecast_df, model_used = forecast_linear(series, horizon), "Linear trend (manual selection)"

st.caption(f"Model used: **{model_used}** · trained on {len(series)} months of history.")

# ----------------------------------------------------------------------------
last_actual = series.iloc[-1]
forecast_total = forecast_df["forecast"].sum()
forecast_avg = forecast_df["forecast"].mean()
implied_growth = (forecast_avg - series.tail(min(3, len(series))).mean()) / series.tail(min(3, len(series))).mean() * 100 \
    if series.tail(min(3, len(series))).mean() else 0

kpi_grid([
    {"label": f"Last actual {metric}", "value": format_currency(last_actual)},
    {"label": f"Forecast total ({horizon}mo)", "value": format_currency(forecast_total)},
    {"label": "Forecast monthly avg", "value": format_currency(forecast_avg)},
    {"label": "Implied trend vs. recent avg", "value": format_pct(implied_growth, signed=True)},
])

# ----------------------------------------------------------------------------
section_title(f"{metric} forecast", "🔮")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=series.index, y=series.values, name="Actual", mode="lines+markers",
    line=dict(color=COLORS["sky_light"], width=3), marker=dict(size=6),
))
fig.add_trace(go.Scatter(
    x=forecast_df.index, y=forecast_df["forecast"], name="Forecast", mode="lines+markers",
    line=dict(color=COLORS["cyan"], width=3, dash="dash"), marker=dict(size=6),
))
fig.add_trace(go.Scatter(
    x=list(forecast_df.index) + list(forecast_df.index[::-1]),
    y=list(forecast_df["upper"]) + list(forecast_df["lower"][::-1]),
    fill="toself", fillcolor="rgba(34,211,238,0.12)",
    line=dict(color="rgba(0,0,0,0)"), name="Confidence band", hoverinfo="skip",
))
fig.update_layout(height=440, yaxis_title=f"{metric} ($)", legend=dict(orientation="h", y=1.05))
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title("Forecast detail", "📋")
table = forecast_df.copy()
table.index = table.index.strftime("%b %Y")
table = table.rename(columns={"forecast": "Forecast", "lower": "Low (≈10th pct)", "upper": "High (≈90th pct)"})
table = table.map(lambda v: format_currency(v))
st.dataframe(table, width="stretch")

csv = forecast_df.reset_index().rename(columns={"index": "Month"}).to_csv(index=False)
st.download_button("⬇️ Download forecast as CSV", csv, file_name=f"{metric.lower()}_forecast.csv", mime="text/csv")
