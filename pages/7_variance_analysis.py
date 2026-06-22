"""Variance Analysis -- actual vs. prior-period (or prior-year) performance bridges."""
import pandas as pd
import streamlit as st

from utils.styling import inject_page_theme, page_header, kpi_grid, section_title
from utils.app_state import render_sidebar_and_load
from utils.data_loader import get_prior_period, get_year_ago_period
from utils.kpis import compute_kpis, pct_change
from utils.formatting import format_currency, format_pct
from utils.charts import waterfall, diverging_heatmap
from utils.i18n import t

inject_page_theme()

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    t("nav.variance_analysis"),
    t("variance.title"),
    t("variance.subtitle"),
)

compare_display = {"prior": t("variance.compare_prior"), "yoy": t("variance.compare_yoy")}
comparison = st.radio(
    t("variance.compare_label"), ["prior", "yoy"],
    format_func=lambda v: compare_display[v],
    horizontal=True, key="var_comparison",
)

if comparison == "prior":
    df_comp = get_prior_period(df_full, date_range)
else:
    df_comp = get_year_ago_period(df_full, date_range)

df_comp = df_comp[df_comp["Region"].isin(regions) & df_comp["Product"].isin(products)]

if df_comp.empty:
    st.warning(t("variance.no_comp_data"))
    st.stop()

k_curr = compute_kpis(df)
k_comp = compute_kpis(df_comp)

# ----------------------------------------------------------------------------
def _delta_card(label, curr, comp, is_pct=False):
    chg = pct_change(curr, comp)
    val = format_pct(curr) if is_pct else format_currency(curr)
    return {
        "label": label, "value": val,
        "delta": f"{chg:+.1f}%" if chg is not None else None,
        "delta_sign": "positive" if (chg or 0) >= 0 else "negative",
    }


kpi_grid([
    _delta_card(t("kpi.revenue"), k_curr["revenue"], k_comp["revenue"]),
    _delta_card(t("kpi.gross_profit"), k_curr["gross_profit"], k_comp["gross_profit"]),
    _delta_card(t("kpi.ebitda"), k_curr["ebitda"], k_comp["ebitda"]),
    _delta_card(t("kpi.net_profit"), k_curr["net_profit"], k_comp["net_profit"]),
])

st.caption(t(
    "variance.period_caption",
    c_start=f"{pd.Timestamp(date_range[0]):%b %d, %Y}", c_end=f"{pd.Timestamp(date_range[1]):%b %d, %Y}",
    p_start=f"{df_comp['Date'].min():%b %d, %Y}", p_end=f"{df_comp['Date'].max():%b %d, %Y}",
))

# ----------------------------------------------------------------------------
section_title(t("variance.bridge_title"), "🌉")
rev_curr_region = df.groupby("Region")["Revenue"].sum()
rev_comp_region = df_comp.groupby("Region")["Revenue"].sum()
all_regions_seen = sorted(set(rev_curr_region.index) | set(rev_comp_region.index))

labels = [t("variance.bridge_start_label")]
values = [rev_comp_region.sum()]
measures = ["absolute"]
for r in all_regions_seen:
    diff = rev_curr_region.get(r, 0) - rev_comp_region.get(r, 0)
    labels.append(r)
    values.append(diff)
    measures.append("relative")
labels.append(t("variance.bridge_end_label"))
values.append(rev_curr_region.sum())
measures.append("total")

st.plotly_chart(waterfall(labels, values, measures, height=440), width="stretch",
                 config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title(t("variance.heatmap_title"), "🔥")
curr_pivot = df.pivot_table(index="Region", columns="Product", values="Revenue", aggfunc="sum", fill_value=0)
comp_pivot = df_comp.pivot_table(index="Region", columns="Product", values="Revenue", aggfunc="sum", fill_value=0)
comp_pivot = comp_pivot.reindex(index=curr_pivot.index, columns=curr_pivot.columns, fill_value=0)
pct_pivot = ((curr_pivot - comp_pivot) / comp_pivot.replace(0, pd.NA) * 100).fillna(0).round(1)
st.plotly_chart(diverging_heatmap(pct_pivot), width="stretch", config={"displayModeBar": False})

# ----------------------------------------------------------------------------
section_title(t("variance.detail_table"), "📋")
detail_curr = df.groupby(["Region", "Product"])["Revenue"].sum().rename("Current")
detail_comp = df_comp.groupby(["Region", "Product"])["Revenue"].sum().rename("Comparison")
detail = pd.concat([detail_curr, detail_comp], axis=1).fillna(0).reset_index()
detail["$ Variance"] = detail["Current"] - detail["Comparison"]
detail["% Variance"] = (detail["$ Variance"] / detail["Comparison"].replace(0, pd.NA) * 100).fillna(0).round(1)
detail = detail.sort_values("$ Variance", ascending=False)

display_detail = detail.copy()
for col in ["Current", "Comparison", "$ Variance"]:
    display_detail[col] = display_detail[col].apply(format_currency)
display_detail["% Variance"] = display_detail["% Variance"].astype(str) + "%"
display_detail.columns = [t("sidebar.region"), t("sidebar.product"), t("variance.col_current"),
                           t("variance.col_comparison"), t("variance.col_dollar_variance"),
                           t("variance.col_pct_variance")]

styled = display_detail.style.map(
    lambda v: "color:#22C55E" if isinstance(v, str) and v.startswith(("+", "$")) and not v.startswith("-")
    else ("color:#F87171" if isinstance(v, str) and v.startswith("-") else ""),
    subset=[t("variance.col_dollar_variance"), t("variance.col_pct_variance")],
)
st.dataframe(styled, width="stretch", hide_index=True)
