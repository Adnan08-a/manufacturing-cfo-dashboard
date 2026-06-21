"""Scenario Planning -- stress-test price, volume, and cost assumptions against EBITDA."""
import pandas as pd
import streamlit as st

from utils.styling import configure_page, page_header, kpi_grid, section_title
from utils.app_state import render_sidebar_and_load
from utils.kpis import compute_kpis
from utils.formatting import format_currency, format_pct
from utils.charts import waterfall

import plotly.graph_objects as go
from utils.styling import COLORS

configure_page("Scenario Planning", "🎯")

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    "Scenario Planning",
    "Stress-test the plan before the market does",
    "Adjust price, volume, cost, and opex assumptions to see the projected impact on "
    "Revenue, Gross Profit, and EBITDA versus the current filtered baseline.",
)

k0 = compute_kpis(df)
R0, C0 = k0["revenue"], k0["cost"]
M0 = df["Manufacturing Cost"].sum()
U0 = df["Units Sold"].sum()
P0 = R0 / U0 if U0 else 0
GP0, EBITDA0 = k0["gross_profit"], k0["ebitda"]

st.markdown("##### Scenario drivers")
s1, s2, s3, s4 = st.columns(4)
with s1:
    price_chg = st.slider("Price change (%)", -20, 20, 0, key="sc_price")
with s2:
    volume_chg = st.slider("Volume change (%)", -30, 30, 0, key="sc_volume")
with s3:
    cogs_chg = st.slider("Unit COGS rate change (%)", -20, 20, 0, key="sc_cogs",
                          help="Change in cost per unit, e.g. from input cost inflation or supplier negotiation.")
with s4:
    opex_chg = st.slider("Operating expense change (%)", -20, 20, 0, key="sc_opex",
                          help="Change in manufacturing/operating overhead, independent of volume.")

# --- Scenario math (sequential decomposition for a clean bridge) -----------
U1 = U0 * (1 + volume_chg / 100)
P1 = P0 * (1 + price_chg / 100)

R_after_vol = P0 * U1
effect_volume_rev = R_after_vol - R0
R1 = P1 * U1
effect_price = R1 - R_after_vol

C_after_vol = C0 * (1 + volume_chg / 100)
effect_volume_cogs = C_after_vol - C0
C1 = C_after_vol * (1 + cogs_chg / 100)
effect_cogs_rate = C1 - C_after_vol

M1 = M0 * (1 + opex_chg / 100)
effect_opex = M1 - M0

net_volume_effect = effect_volume_rev - effect_volume_cogs

GP1 = R1 - C1
EBITDA1 = GP1 - M1

k1 = {
    "revenue": R1, "cost": C1, "gross_profit": GP1, "ebitda": EBITDA1,
    "gross_margin": (GP1 / R1 * 100) if R1 else 0,
    "ebitda_margin": (EBITDA1 / R1 * 100) if R1 else 0,
}

# ----------------------------------------------------------------------------
section_title("Baseline vs. scenario", "⚖️")
b1, b2 = st.columns(2)
with b1:
    st.markdown("**Baseline (current filters)**")
    kpi_grid([
        {"label": "Revenue", "value": format_currency(R0)},
        {"label": "Gross Profit", "value": format_currency(GP0)},
        {"label": "EBITDA", "value": format_currency(EBITDA0)},
        {"label": "EBITDA Margin", "value": format_pct(k0["ebitda_margin"])},
    ])
with b2:
    st.markdown("**Scenario**")
    rev_delta = (R1 - R0) / R0 * 100 if R0 else 0
    gp_delta = (GP1 - GP0) / GP0 * 100 if GP0 else 0
    eb_delta = (EBITDA1 - EBITDA0) / EBITDA0 * 100 if EBITDA0 else 0
    margin_delta = k1["ebitda_margin"] - k0["ebitda_margin"]
    kpi_grid([
        {"label": "Revenue", "value": format_currency(R1), "delta": f"{rev_delta:+.1f}%",
         "delta_sign": "positive" if rev_delta >= 0 else "negative"},
        {"label": "Gross Profit", "value": format_currency(GP1), "delta": f"{gp_delta:+.1f}%",
         "delta_sign": "positive" if gp_delta >= 0 else "negative"},
        {"label": "EBITDA", "value": format_currency(EBITDA1), "delta": f"{eb_delta:+.1f}%",
         "delta_sign": "positive" if eb_delta >= 0 else "negative"},
        {"label": "EBITDA Margin", "value": format_pct(k1["ebitda_margin"]), "delta": f"{margin_delta:+.1f} pts",
         "delta_sign": "positive" if margin_delta >= 0 else "negative"},
    ])

# ----------------------------------------------------------------------------
section_title("EBITDA bridge: baseline → scenario", "🌉")
labels = ["Baseline EBITDA", "Price effect", "Volume effect (net)", "COGS rate effect", "Opex effect", "Scenario EBITDA"]
values = [EBITDA0, effect_price, net_volume_effect, -effect_cogs_rate, -effect_opex, EBITDA1]
measures = ["absolute", "relative", "relative", "relative", "relative", "total"]
st.plotly_chart(waterfall(labels, values, measures, height=440), width="stretch",
                 config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title("Driver sensitivity (illustrative ±10%, independent of sliders above)", "🎢")
st.caption("Ranks which lever moves EBITDA the most, holding all else at baseline.")


def _ebitda_at(price_pct=0, vol_pct=0, cogs_pct=0, opex_pct=0):
    u = U0 * (1 + vol_pct / 100)
    p = P0 * (1 + price_pct / 100)
    r = p * u
    c = C0 * (1 + vol_pct / 100) * (1 + cogs_pct / 100)
    m = M0 * (1 + opex_pct / 100)
    return (r - c) - m


drivers = {
    "Price ±10%": (_ebitda_at(price_pct=-10), _ebitda_at(price_pct=10)),
    "Volume ±10%": (_ebitda_at(vol_pct=-10), _ebitda_at(vol_pct=10)),
    "COGS rate ±10%": (_ebitda_at(cogs_pct=10), _ebitda_at(cogs_pct=-10)),
    "Opex ±10%": (_ebitda_at(opex_pct=10), _ebitda_at(opex_pct=-10)),
}

tornado_rows = []
for name, (low, high) in drivers.items():
    tornado_rows.append({"Driver": name, "Low": low - EBITDA0, "High": high - EBITDA0})
tornado_df = pd.DataFrame(tornado_rows)
tornado_df["range"] = (tornado_df["High"] - tornado_df["Low"]).abs()
tornado_df = tornado_df.sort_values("range")

fig = go.Figure()
fig.add_trace(go.Bar(
    y=tornado_df["Driver"], x=tornado_df["High"], orientation="h",
    name="Favorable", marker_color=COLORS["green"],
))
fig.add_trace(go.Bar(
    y=tornado_df["Driver"], x=tornado_df["Low"], orientation="h",
    name="Unfavorable", marker_color=COLORS["red"],
))
fig.update_layout(
    barmode="overlay", height=320, xaxis_title="EBITDA impact ($)",
    legend=dict(orientation="h", y=1.1),
)
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

st.markdown(
    f"At the current slider settings, the scenario shifts EBITDA by "
    f"**{format_currency(EBITDA1 - EBITDA0)}** ({eb_delta:+.1f}%) versus baseline, moving the "
    f"EBITDA margin from **{format_pct(k0['ebitda_margin'])}** to **{format_pct(k1['ebitda_margin'])}**."
)
