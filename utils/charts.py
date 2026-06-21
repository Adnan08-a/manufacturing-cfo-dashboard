"""
charts.py
---------
Reusable Plotly chart builders. All functions return a `go.Figure` /
`px` figure ready for `st.plotly_chart(fig, width="stretch")`.
The active Plotly template (registered in styling.py) supplies fonts,
colors, and backgrounds, so these builders focus on data shape only.
"""
from __future__ import annotations

from typing import Optional, Sequence

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.styling import COLORS, CATEGORICAL_SEQUENCE, SEQUENTIAL_BLUES


# ----------------------------------------------------------------------------
# Trend / line charts
# ----------------------------------------------------------------------------
def trend_line(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    title: str = "",
    y_title: Optional[str] = None,
    height: int = 380,
) -> go.Figure:
    fig = px.line(
        df, x=x, y=y, color=color, markers=True, title=title,
        color_discrete_sequence=CATEGORICAL_SEQUENCE,
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=6))
    fig.update_layout(height=height, yaxis_title=y_title or y, xaxis_title="")
    return fig


def dual_metric_trend(
    df: pd.DataFrame, x: str, y1: str, y2: str,
    y1_title: str, y2_title: str, title: str = "", height: int = 380,
) -> go.Figure:
    """Two metrics on primary/secondary y-axes (e.g. Revenue vs Margin %)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y1], name=y1_title, mode="lines+markers",
        line=dict(color=COLORS["blue_bright"], width=3), marker=dict(size=6),
    ))
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y2], name=y2_title, mode="lines+markers", yaxis="y2",
        line=dict(color=COLORS["cyan"], width=3, dash="dot"), marker=dict(size=6),
    ))
    fig.update_layout(
        title=title, height=height,
        yaxis=dict(title=y1_title),
        yaxis2=dict(title=y2_title, overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


# ----------------------------------------------------------------------------
# Bar / comparison charts
# ----------------------------------------------------------------------------
def bar_compare(
    df: pd.DataFrame, x: str, y: str, color: Optional[str] = None,
    title: str = "", orientation: str = "v", height: int = 380,
    text_auto: bool = False,
) -> go.Figure:
    fig = px.bar(
        df, x=x if orientation == "v" else y, y=y if orientation == "v" else x,
        color=color, orientation=orientation, title=title,
        color_discrete_sequence=CATEGORICAL_SEQUENCE,
        text_auto=".2s" if text_auto else False,
    )
    fig.update_layout(height=height, xaxis_title="", yaxis_title="")
    return fig


def donut(df: pd.DataFrame, names: str, values: str, title: str = "", height: int = 360) -> go.Figure:
    fig = px.pie(
        df, names=names, values=values, hole=0.55, title=title,
        color_discrete_sequence=CATEGORICAL_SEQUENCE,
    )
    fig.update_traces(textinfo="percent+label", textfont=dict(color=COLORS["ink"]))
    fig.update_layout(height=height, showlegend=False)
    return fig


# ----------------------------------------------------------------------------
# Waterfall / bridge charts
# ----------------------------------------------------------------------------
def waterfall(
    labels: Sequence[str],
    values: Sequence[float],
    measures: Sequence[str],
    title: str = "",
    height: int = 420,
    value_format: str = "$,.0f",
) -> go.Figure:
    """Generic waterfall. `measures` items are 'absolute', 'relative', or 'total'."""
    fig = go.Figure(go.Waterfall(
        x=labels,
        y=values,
        measure=measures,
        connector=dict(line=dict(color="rgba(147,197,253,0.35)", width=1)),
        increasing=dict(marker=dict(color=COLORS["green"])),
        decreasing=dict(marker=dict(color=COLORS["red"])),
        totals=dict(marker=dict(color=COLORS["blue_bright"])),
        texttemplate="%{y:" + value_format + "}",
        textposition="outside",
    ))
    fig.update_layout(title=title, height=height, showlegend=False)
    return fig


# ----------------------------------------------------------------------------
# Heatmaps
# ----------------------------------------------------------------------------
def heatmap(
    pivot_df: pd.DataFrame, title: str = "", height: int = 420,
    colorscale: Optional[list] = None, value_suffix: str = "",
) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns.astype(str),
        y=pivot_df.index.astype(str),
        colorscale=colorscale or SEQUENTIAL_BLUES,
        texttemplate="%{z:.1f}" + value_suffix,
        textfont=dict(size=11, color=COLORS["ink"]),
        colorbar=dict(outlinewidth=0),
    ))
    fig.update_layout(title=title, height=height, xaxis_title="", yaxis_title="")
    return fig


def diverging_heatmap(pivot_df: pd.DataFrame, title: str = "", height: int = 420) -> go.Figure:
    from utils.styling import DIVERGING_RG
    zmax = max(abs(pivot_df.values.min()), abs(pivot_df.values.max())) or 1
    fig = go.Figure(go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns.astype(str),
        y=pivot_df.index.astype(str),
        colorscale=DIVERGING_RG,
        zmid=0, zmin=-zmax, zmax=zmax,
        texttemplate="%{z:+.1f}%",
        textfont=dict(size=11, color=COLORS["ink"]),
        colorbar=dict(outlinewidth=0),
    ))
    fig.update_layout(title=title, height=height, xaxis_title="", yaxis_title="")
    return fig


# ----------------------------------------------------------------------------
# Driver tree / decomposition
# ----------------------------------------------------------------------------
def driver_treemap(
    df: pd.DataFrame, path: list, values: str, color: Optional[str] = None,
    title: str = "", height: int = 460,
) -> go.Figure:
    fig = px.treemap(
        df, path=path, values=values, color=color,
        color_continuous_scale=SEQUENTIAL_BLUES,
        title=title,
    )
    fig.update_traces(
        textfont=dict(color="white", size=13),
        marker=dict(line=dict(color=COLORS["bg_deep"], width=2)),
    )
    fig.update_layout(height=height, margin=dict(t=50, l=4, r=4, b=4))
    return fig


# ----------------------------------------------------------------------------
# Gauges
# ----------------------------------------------------------------------------
def gauge(value: float, title: str, max_value: float = 100, target: Optional[float] = None,
          suffix: str = "%", height: int = 240) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix=suffix, font=dict(color=COLORS["ink"], size=26)),
        title=dict(text=title, font=dict(color=COLORS["ink_dim"], size=13)),
        gauge=dict(
            axis=dict(range=[0, max_value], tickcolor=COLORS["ink_dim"]),
            bar=dict(color=COLORS["blue_bright"]),
            bgcolor="rgba(255,255,255,0.04)",
            borderwidth=0,
            steps=[
                dict(range=[0, max_value * 0.5], color="rgba(248,113,113,0.18)"),
                dict(range=[max_value * 0.5, max_value * 0.8], color="rgba(245,158,11,0.18)"),
                dict(range=[max_value * 0.8, max_value], color="rgba(34,197,94,0.18)"),
            ],
            threshold=dict(
                line=dict(color=COLORS["amber"], width=3),
                thickness=0.8,
                value=target if target is not None else max_value,
            ),
        ),
    ))
    fig.update_layout(height=height, margin=dict(l=20, r=20, t=40, b=10))
    return fig


# ----------------------------------------------------------------------------
# Scatter / correlation
# ----------------------------------------------------------------------------
def scatter_corr(
    df: pd.DataFrame, x: str, y: str, color: Optional[str] = None,
    size: Optional[str] = None, title: str = "", height: int = 400,
    trendline: bool = False,
) -> go.Figure:
    fig = px.scatter(
        df, x=x, y=y, color=color, size=size, title=title,
        color_discrete_sequence=CATEGORICAL_SEQUENCE,
        trendline="ols" if trendline else None,
        opacity=0.75,
    )
    fig.update_layout(height=height)
    return fig


def correlation_heatmap(df: pd.DataFrame, columns: list, title: str = "", height: int = 460) -> go.Figure:
    corr = df[columns].corr()
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.columns,
        colorscale=[[0, COLORS["red"]], [0.5, "#1E2D45"], [1, COLORS["green"]]],
        zmid=0, zmin=-1, zmax=1,
        texttemplate="%{z:.2f}",
        textfont=dict(size=11, color=COLORS["ink"]),
        colorbar=dict(outlinewidth=0),
    ))
    fig.update_layout(title=title, height=height)
    return fig


# ----------------------------------------------------------------------------
# Distribution
# ----------------------------------------------------------------------------
def box_distribution(df: pd.DataFrame, x: str, y: str, title: str = "", height: int = 380) -> go.Figure:
    fig = px.box(
        df, x=x, y=y, title=title, color=x,
        color_discrete_sequence=CATEGORICAL_SEQUENCE,
    )
    fig.update_layout(height=height, showlegend=False, xaxis_title="", yaxis_title=y)
    return fig
