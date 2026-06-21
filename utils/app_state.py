"""
app_state.py
------------
Shared "load data + render global filters" routine called at the top of
every page so the Date / Region / Product filters and the optional dataset
upload stay consistent (and persist via st.session_state) as the user
navigates between pages.
"""
from __future__ import annotations

from typing import Tuple

import pandas as pd
import streamlit as st

from utils.data_loader import load_data, filter_data


def render_sidebar_and_load() -> Tuple[pd.DataFrame, pd.DataFrame, tuple, list, list]:
    """Renders the sidebar (data source + filters) and returns:
    (df_full, df_filtered, date_range, regions, products)
    """
    with st.sidebar:
        st.markdown("## 🏭 CFO Cockpit")
        st.caption("Manufacturing performance & planning")
        st.markdown("---")

        with st.expander("📁 Data source", expanded=False):
            uploaded = st.file_uploader(
                "Upload your own dataset",
                type=["xlsx", "csv"],
                key="data_uploader",
                help="Same schema as the bundled sample. Leave empty to use the sample dataset.",
            )
            st.caption("Columns expected: Date, Region, Product, Revenue, Cost, Profit, "
                       "Units Sold, Customer Satisfaction, Manufacturing Cost, Labor Hours, "
                       "Machine Downtime, Inventory Levels, Order Lead Time, Return Rate, "
                       "On-Time Delivery.")

    try:
        df = load_data(uploaded)
    except Exception as e:
        st.sidebar.error(f"Could not load dataset: {e}")
        st.stop()

    with st.sidebar:
        st.markdown("### 🔎 Filters")

        min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
        default_range = st.session_state.get("flt_date_range", (min_date, max_date))
        date_range = st.date_input(
            "Date range",
            value=default_range,
            min_value=min_date,
            max_value=max_date,
            key="flt_date_range",
        )
        if not (isinstance(date_range, (tuple, list)) and len(date_range) == 2):
            date_range = (min_date, max_date)

        all_regions = sorted(df["Region"].unique())
        regions = st.multiselect(
            "Region", all_regions,
            default=st.session_state.get("flt_regions", all_regions),
            key="flt_regions",
        )

        all_products = sorted(df["Product"].unique())
        products = st.multiselect(
            "Product", all_products,
            default=st.session_state.get("flt_products", all_products),
            key="flt_products",
        )

        if st.button("↺ Reset filters", width="stretch"):
            for k in ("flt_date_range", "flt_regions", "flt_products"):
                st.session_state.pop(k, None)
            st.rerun()

        st.markdown("---")
        st.caption(f"Dataset: {len(df):,} records · "
                   f"{df['Date'].min():%b %Y} – {df['Date'].max():%b %Y}")

    regions_eff = regions if regions else all_regions
    products_eff = products if products else all_products

    df_filtered = filter_data(df, date_range, regions_eff, products_eff)

    if df_filtered.empty:
        st.warning("No data matches the current filters. Adjust the filters in the sidebar.")
        st.stop()

    return df, df_filtered, date_range, regions_eff, products_eff
