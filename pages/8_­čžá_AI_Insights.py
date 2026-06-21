"""AI Insights -- automated insight cards and natural-language Q&A over the filtered data."""
import streamlit as st

from utils.styling import configure_page, page_header, section_title, insight_card
from utils.app_state import render_sidebar_and_load
from utils.insights import generate_insight_cards, build_data_summary, ask_claude

configure_page("AI Insights", "🧠")

df_full, df, date_range, regions, products = render_sidebar_and_load()

page_header(
    "AI Insights",
    "Automated read on the numbers",
    "Statistical insight generation runs automatically on every page load -- no API key "
    "required. Connect an Anthropic API key below to unlock free-form Q&A on top.",
)

# ----------------------------------------------------------------------------
section_title("Insight cards", "💡")
st.caption("Generated from trends, outliers, and correlations in the filtered dataset.")

cards = generate_insight_cards(df)

category_labels = {
    "growth": ("📈", "Growth"), "risk": ("⚠️", "Risk"),
    "efficiency": ("⚙️", "Efficiency"), "recommendation": ("✅", "Recommendation"),
}
tab_names = ["All"] + [f"{icon} {label}" for icon, label in category_labels.values()]
tabs = st.tabs(tab_names)

with tabs[0]:
    for c in cards:
        icon, label = category_labels[c["category"]]
        insight_card(c["category"], f"{icon} {label}", c["text"])

for tab, (cat_key, (icon, label)) in zip(tabs[1:], category_labels.items()):
    with tab:
        filtered = [c for c in cards if c["category"] == cat_key]
        if not filtered:
            st.caption("No insights in this category for the current filters.")
        for c in filtered:
            insight_card(c["category"], f"{icon} {label}", c["text"])

# ----------------------------------------------------------------------------
st.markdown("---")
section_title("Ask a question about this data", "💬")

# ----------------------------------------------------------------------------
st.markdown("---")
section_title("Ask a question about this data", "💬")

secret_key = None
try:
    if "ANTHROPIC_API_KEY" in st.secrets:
        secret_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    pass

if secret_key:
    api_key = secret_key
    st.success("Using the Anthropic API key configured in this app's secrets.", icon="🔑")
else:
    st.warning(
        "No Anthropic API key detected in secrets. Paste a key below to use it for this "
        "session only (it is not stored or sent anywhere except directly to the Anthropic "
        "API), or add `ANTHROPIC_API_KEY` to your Streamlit secrets for persistent access.",
        icon="🔑",
    )
    with st.expander("Add a session API key", expanded=True):
        st.text_input("Anthropic API key", type="password", key="anthropic_api_key_input")
    api_key = st.session_state.get("anthropic_api_key_input") or None
    if api_key:
        st.success("Key set for this session. Ask your question below.")

question = st.text_input(
    "Your question",
    placeholder="e.g. Which region should we prioritize for margin improvement?",
    key="ai_question",
)
ask = st.button("Ask", type="primary", disabled=not api_key)

if ask and api_key:
    with st.spinner("Analyzing the filtered data..."):
        try:
            summary = build_data_summary(df)
            answer = ask_claude(question, summary, api_key)
            st.markdown(
                f'<div class="insight-card recommendation"><div class="insight-tag">🧠 AI answer</div>'
                f'<div>{answer}</div></div>',
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"Couldn't get an answer from the Anthropic API: {e}")
elif ask and not api_key:
    st.info("Add an API key above to enable live Q&A.")

with st.expander("What data does the AI see?"):
    st.caption(
        "Only an aggregated text summary of the currently filtered data (KPIs and revenue "
        "by region/product) is sent -- never the raw row-level dataset."
    )
    st.code(build_data_summary(df), language="text")
