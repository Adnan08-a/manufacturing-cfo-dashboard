"""AI Insights -- automated insight cards and natural-language Q&A over the filtered data."""
import streamlit as st

from utils.styling import inject_page_theme, page_header, section_title, insight_card
from utils.app_state import render_sidebar_and_load
from utils.insights import generate_insight_cards, build_data_summary, ask_claude
from utils.i18n import t

inject_page_theme()

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    t("nav.ai_insights"),
    t("ai.title"),
    t("ai.subtitle"),
)

# ----------------------------------------------------------------------------
section_title(t("ai.cards_header"), "💡")
st.caption(t("ai.cards_caption"))

cards = generate_insight_cards(df)

category_labels = {
    "growth": ("📈", t("ai.cat_growth")), "risk": ("⚠️", t("ai.cat_risk")),
    "efficiency": ("⚙️", t("ai.cat_efficiency")), "recommendation": ("✅", t("ai.cat_recommendation")),
}
tab_names = [t("ai.tab_all")] + [f"{icon} {label}" for icon, label in category_labels.values()]
tabs = st.tabs(tab_names)

with tabs[0]:
    for c in cards:
        icon, label = category_labels[c["category"]]
        insight_card(c["category"], f"{icon} {label}", c["text"])

for tab, (cat_key, (icon, label)) in zip(tabs[1:], category_labels.items()):
    with tab:
        filtered = [c for c in cards if c["category"] == cat_key]
        if not filtered:
            st.caption(t("ai.no_insights_in_cat"))
        for c in filtered:
            insight_card(c["category"], f"{icon} {label}", c["text"])

# ----------------------------------------------------------------------------
st.markdown("---")
section_title(t("ai.ask_header"), "💬")

secret_key = None
try:
    if "ANTHROPIC_API_KEY" in st.secrets:
        secret_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    pass

if secret_key:
    api_key = secret_key
    st.success(t("ai.secret_key_success"), icon="🔑")
else:
    st.warning(t("ai.no_key_warning"), icon="🔑")
    with st.expander(t("ai.session_key_expander"), expanded=True):
        st.text_input(t("ai.session_key_input_label"), type="password", key="anthropic_api_key_input")
    api_key = st.session_state.get("anthropic_api_key_input") or None
    if api_key:
        st.success(t("ai.session_key_success"))

question = st.text_input(
    t("ai.question_label"),
    placeholder=t("ai.question_placeholder"),
    key="ai_question",
)
ask = st.button(t("ai.ask_button"), type="primary", disabled=not api_key)

if ask and api_key:
    with st.spinner(t("ai.analyzing_spinner")):
        try:
            summary = build_data_summary(df)
            answer = ask_claude(question, summary, api_key)
            st.markdown(
                f'<div class="insight-card recommendation"><div class="insight-tag">{t("ai.answer_tag")}</div>'
                f'<div>{answer}</div></div>',
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(t("ai.api_error", error=e))
elif ask and not api_key:
    st.info(t("ai.need_key_info"))

with st.expander(t("ai.what_data_expander")):
    st.caption(t("ai.what_data_caption"))
    st.code(build_data_summary(df), language="text")
