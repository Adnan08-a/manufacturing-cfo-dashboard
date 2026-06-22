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
from utils.i18n import t


def render_sidebar_and_load() -> Tuple[pd.DataFrame, pd.DataFrame, tuple, list, list]:
    """Renders the sidebar (data source + filters) and returns:
    (df_full, df_filtered, date_range, regions, products)
    """
    with st.sidebar:
        st.markdown(f"## {t('sidebar.brand_title')}")
        st.caption(t("sidebar.brand_caption"))
        st.markdown("---")

        with st.expander(t("sidebar.data_source"), expanded=False):
            uploaded = st.file_uploader(
                t("sidebar.upload_label"),
                type=["xlsx", "csv"],
                key="data_uploader",
                help=t("sidebar.upload_help"),
            )
            st.caption(t("sidebar.upload_caption"))

    try:
        df = load_data(uploaded)
    except Exception as e:
        st.sidebar.error(t("sidebar.load_error", error=e))
        st.stop()

    with st.sidebar:
        st.markdown(f"### {t('sidebar.filters')}")

        min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
        default_range = st.session_state.get("flt_date_range", (min_date, max_date))
        date_range = st.date_input(
            t("sidebar.date_range"),
            value=default_range,
            min_value=min_date,
            max_value=max_date,
            key="flt_date_range",
        )
        if not (isinstance(date_range, (tuple, list)) and len(date_range) == 2):
            date_range = (min_date, max_date)

        all_regions = sorted(df["Region"].unique())
        regions = st.multiselect(
            t("sidebar.region"), all_regions,
            default=st.session_state.get("flt_regions", all_regions),
            key="flt_regions",
        )

        all_products = sorted(df["Product"].unique())
        products = st.multiselect(
            t("sidebar.product"), all_products,
            default=st.session_state.get("flt_products", all_products),
            key="flt_products",
        )

        if st.button(t("sidebar.reset_filters"), width="stretch"):
            for k in ("flt_date_range", "flt_regions", "flt_products"):
                st.session_state.pop(k, None)
            st.rerun()

        st.markdown("---")
        st.caption(t(
            "sidebar.dataset_caption",
            n=f"{len(df):,}",
            start=f"{df['Date'].min():%b %Y}",
            end=f"{df['Date'].max():%b %Y}",
        ))

    regions_eff = regions if regions else all_regions
    products_eff = products if products else all_products

    df_filtered = filter_data(df, date_range, regions_eff, products_eff)

    if df_filtered.empty:
        st.warning(t("sidebar.no_data_warning"))
        st.stop()

    return df, df_filtered, date_range, regions_eff, products_eff
