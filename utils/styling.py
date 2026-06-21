"""
styling.py
----------
Visual identity for the dashboard: a deep-navy-to-blue gradient "command
center" theme with glassmorphic KPI cards, a signature gradient-text number
treatment, and a matching Plotly template so every chart inherits the same
palette without per-chart boilerplate.
"""
from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------
COLORS = {
    "bg_deep": "#070F22",
    "bg_panel": "#0E1C36",
    "bg_panel_alt": "#122548",
    "navy": "#10243F",
    "royal": "#1B3B6F",
    "blue": "#2563EB",
    "blue_bright": "#3B82F6",
    "sky": "#60A5FA",
    "sky_light": "#93C5FD",
    "cyan": "#22D3EE",
    "ink": "#E7EEF8",
    "ink_dim": "#9FB3CC",
    "border": "rgba(96, 165, 250, 0.18)",
    "amber": "#F59E0B",
    "green": "#22C55E",
    "red": "#F87171",
    "violet": "#A78BFA",
}

CATEGORICAL_SEQUENCE = ["#3B82F6", "#22D3EE", "#A78BFA", "#F59E0B", "#22C55E", "#F87171"]
SEQUENTIAL_BLUES = ["#0E1C36", "#11335E", "#1B3B6F", "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD"]
DIVERGING_RG = ["#F87171", "#F3A6A6", "#1E2D45", "#86C9A9", "#22C55E"]

PLOTLY_TEMPLATE_NAME = "cfo_blue"


# ----------------------------------------------------------------------------
# Page bootstrap
# ----------------------------------------------------------------------------
def configure_page(page_title: str, page_icon: str = "📊") -> None:
    """Must be the first Streamlit call on every page."""
    st.set_page_config(
        page_title=f"{page_title} | Manufacturing CFO Cockpit",
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _register_plotly_template()
    _inject_css()


def _register_plotly_template() -> None:
    template = go.layout.Template()
    template.layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", color=COLORS["ink"], size=13),
        title=dict(font=dict(family="Sora, Inter, sans-serif", size=18, color=COLORS["ink"])),
        colorway=CATEGORICAL_SEQUENCE,
        xaxis=dict(
            gridcolor="rgba(96,165,250,0.10)",
            zerolinecolor="rgba(96,165,250,0.18)",
            linecolor="rgba(96,165,250,0.18)",
            tickfont=dict(color=COLORS["ink_dim"]),
            title=dict(font=dict(color=COLORS["ink_dim"])),
        ),
        yaxis=dict(
            gridcolor="rgba(96,165,250,0.10)",
            zerolinecolor="rgba(96,165,250,0.18)",
            linecolor="rgba(96,165,250,0.18)",
            tickfont=dict(color=COLORS["ink_dim"]),
            title=dict(font=dict(color=COLORS["ink_dim"])),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["ink_dim"]),
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        hoverlabel=dict(
            bgcolor=COLORS["bg_panel_alt"],
            bordercolor=COLORS["border"],
            font=dict(family="Inter, sans-serif", color=COLORS["ink"]),
        ),
        colorscale=dict(sequential=SEQUENTIAL_BLUES, diverging=DIVERGING_RG),
    )
    pio.templates[PLOTLY_TEMPLATE_NAME] = template
    pio.templates.default = PLOTLY_TEMPLATE_NAME


def _inject_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, sans-serif;
        }}

        .stApp {{
            background:
                radial-gradient(1200px 600px at 10% -10%, rgba(37,99,235,0.18), transparent 60%),
                radial-gradient(1000px 500px at 110% 10%, rgba(34,211,238,0.10), transparent 55%),
                linear-gradient(180deg, {COLORS['bg_deep']} 0%, #081227 55%, {COLORS['bg_deep']} 100%);
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(195deg, #0A1730 0%, {COLORS['bg_panel']} 100%);
            border-right: 1px solid {COLORS['border']};
        }}
        section[data-testid="stSidebar"] * {{
            color: {COLORS['ink']} !important;
        }}

        h1, h2, h3 {{
            font-family: 'Sora', 'Inter', sans-serif !important;
            color: {COLORS['ink']} !important;
            letter-spacing: -0.01em;
        }}
        p, li, span, label, .stMarkdown {{
            color: {COLORS['ink_dim']};
        }}

        /* ---- Gradient header banner (signature element) ---- */
        .cfo-header {{
            position: relative;
            border-radius: 18px;
            padding: 28px 32px;
            margin-bottom: 22px;
            overflow: hidden;
            background: linear-gradient(120deg, #0B2447 0%, #15356B 35%, #2563EB 80%, #22D3EE 130%);
            background-size: 220% 220%;
            animation: cfoGradientShift 14s ease infinite;
            border: 1px solid rgba(147, 197, 253, 0.25);
            box-shadow: 0 20px 60px -25px rgba(37, 99, 235, 0.65);
        }}
        @keyframes cfoGradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        .cfo-header .eyebrow {{
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.72rem;
            font-weight: 600;
            color: #BFDBFE;
            margin-bottom: 6px;
        }}
        .cfo-header h1 {{
            font-size: 2.0rem;
            margin: 0 0 6px 0;
            color: #FFFFFF !important;
        }}
        .cfo-header .subtitle {{
            color: #DCEAFE;
            font-size: 0.95rem;
            margin: 0;
            max-width: 760px;
        }}

        /* ---- KPI cards ---- */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 14px;
            margin-bottom: 22px;
        }}
        .kpi-card {{
            background: linear-gradient(160deg, rgba(27,59,111,0.55) 0%, rgba(14,28,54,0.75) 100%);
            border: 1px solid {COLORS['border']};
            border-radius: 16px;
            padding: 18px 20px;
            backdrop-filter: blur(6px);
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(147, 197, 253, 0.45);
        }}
        .kpi-card .kpi-label {{
            font-size: 0.76rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {COLORS['ink_dim']};
            margin-bottom: 8px;
        }}
        .kpi-card .kpi-value {{
            font-family: 'Sora', sans-serif;
            font-weight: 700;
            font-size: 1.65rem;
            line-height: 1.1;
            background: linear-gradient(90deg, #93C5FD 0%, #FFFFFF 45%, #67E8F9 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 6px;
        }}
        .kpi-card .kpi-delta {{
            font-size: 0.80rem;
            font-weight: 600;
        }}
        .kpi-delta.positive {{ color: {COLORS['green']}; }}
        .kpi-delta.negative {{ color: {COLORS['red']}; }}
        .kpi-delta.neutral {{ color: {COLORS['ink_dim']}; }}

        /* ---- Section titles ---- */
        .section-title {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: 'Sora', sans-serif;
            font-weight: 600;
            font-size: 1.05rem;
            color: {COLORS['ink']};
            margin: 6px 0 12px 0;
            padding-bottom: 8px;
            border-bottom: 1px solid {COLORS['border']};
        }}

        /* ---- Insight / commentary cards ---- */
        .insight-card {{
            background: rgba(14,28,54,0.6);
            border-left: 3px solid {COLORS['sky']};
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 10px;
            font-size: 0.92rem;
            color: {COLORS['ink']};
        }}
        .insight-card.risk {{ border-left-color: {COLORS['red']}; }}
        .insight-card.growth {{ border-left-color: {COLORS['green']}; }}
        .insight-card.efficiency {{ border-left-color: {COLORS['amber']}; }}
        .insight-card.recommendation {{ border-left-color: {COLORS['violet']}; }}
        .insight-tag {{
            display: inline-block;
            font-size: 0.66rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 2px 8px;
            border-radius: 999px;
            margin-bottom: 6px;
            background: rgba(96,165,250,0.15);
            color: {COLORS['sky_light']};
        }}

        /* ---- Misc ---- */
        div[data-testid="stMetric"] {{
            background: rgba(14,28,54,0.55);
            border: 1px solid {COLORS['border']};
            border-radius: 14px;
            padding: 12px 16px;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(14,28,54,0.5);
            border-radius: 10px 10px 0 0;
            color: {COLORS['ink_dim']};
        }}
        .stTabs [aria-selected="true"] {{
            background-color: rgba(37,99,235,0.25) !important;
            color: {COLORS['ink']} !important;
        }}
        footer {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# Reusable UI components
# ----------------------------------------------------------------------------
def page_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="cfo-header">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p class="subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str, icon: str = "") -> None:
    st.markdown(f'<div class="section-title">{icon} {text}</div>', unsafe_allow_html=True)


def kpi_grid(cards: list[dict]) -> None:
    """Render a responsive grid of KPI cards.

    Each card dict: {"label": str, "value": str, "delta": str|None,
                      "delta_sign": "positive"|"negative"|"neutral"}
    """
    html = ['<div class="kpi-grid">']
    for c in cards:
        delta_html = ""
        if c.get("delta"):
            sign_class = c.get("delta_sign", "neutral")
            delta_html = f'<div class="kpi-delta {sign_class}">{c["delta"]}</div>'
        html.append(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{c['label']}</div>
                <div class="kpi-value">{c['value']}</div>
                {delta_html}
            </div>
            """
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def insight_card(category: str, tag: str, text: str) -> None:
    """category in {growth, risk, efficiency, recommendation}"""
    st.markdown(
        f"""
        <div class="insight-card {category}">
            <div class="insight-tag">{tag}</div>
            <div>{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
