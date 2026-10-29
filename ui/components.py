"""
UI Design Components and Interactive Plotly Visualizations.
Adheres to institutional wealth management dashboard standards.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List

# Institutional Color Palette
COLORS = {
    "primary": "#1E3A8A",      # Navy Blue
    "secondary": "#0D9488",    # Teal
    "accent": "#F59E0B",       # Amber
    "equity": "#2563EB",       # Royal Blue
    "debt": "#10B981",         # Emerald Green
    "liquid": "#6366F1",       # Indigo
    "danger": "#EF4444",       # Crimson
    "warning": "#F59E0B",      # Amber
    "success": "#10B981",      # Emerald
    "bg_light": "#F8FAFC",     # Off-white Slate
    "card_border": "#E2E8F0"   # Light grey border
}

def plot_asset_allocation_donut(allocation: Dict[str, float], title: str = "Target Asset Allocation") -> go.Figure:
    """Renders a modern donut chart for portfolio asset allocation."""
    labels = ["Equity", "Debt", "Liquid / Cash"]
    values = [
        allocation.get("equity_pct", 0.0),
        allocation.get("debt_pct", 0.0),
        allocation.get("liquid_pct", 0.0)
    ]
    color_map = [COLORS["equity"], COLORS["debt"], COLORS["liquid"]]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=color_map, line=dict(color="#FFFFFF", width=2)),
        textinfo="label+percent",
        textfont=dict(size=13, family="Inter, sans-serif"),
        hoverinfo="label+value+percent"
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#0F172A", family="Inter")),
        margin=dict(t=40, b=20, l=20, r=20),
        height=280,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

def plot_glide_path_chart(glide_path: List[Dict[str, Any]]) -> go.Figure:
    """Renders a stacked area chart depicting the glide path to goal maturity."""
    df = pd.DataFrame(glide_path)
    if df.empty:
        return go.Figure()

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["year"],
        y=df["equity_pct"],
        mode="lines",
        name="Equity %",
        line=dict(width=0.5, color=COLORS["equity"]),
        stackgroup="one",
        fillcolor="rgba(37, 99, 235, 0.7)"
    ))
    
    fig.add_trace(go.Scatter(
        x=df["year"],
        y=df["debt_pct"],
        mode="lines",
        name="Debt %",
        line=dict(width=0.5, color=COLORS["debt"]),
        stackgroup="one",
        fillcolor="rgba(16, 185, 129, 0.7)"
    ))
    
    fig.add_trace(go.Scatter(
        x=df["year"],
        y=df["liquid_pct"],
        mode="lines",
        name="Liquid %",
        line=dict(width=0.5, color=COLORS["liquid"]),
        stackgroup="one",
        fillcolor="rgba(99, 102, 241, 0.7)"
    ))

    fig.update_layout(
        title=dict(text="Systematic Asset Allocation Glide Path (De-risking to Maturity)", font=dict(size=15)),
        xaxis=dict(title="Years Elapsed", dtick=1),
        yaxis=dict(title="Allocation %", range=[0, 100]),
        height=320,
        margin=dict(t=40, b=40, l=40, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_backtest_curve(daily_df: pd.DataFrame, portfolio_name: str) -> go.Figure:
    """Renders the historical empirical portfolio equity curve."""
    if daily_df.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_df["Date"],
        y=daily_df["Portfolio_Value"],
        mode="lines",
        name=portfolio_name,
        line=dict(color=COLORS["primary"], width=2.5),
        hovertemplate="Date: %{x|%d-%b-%Y}<br>Portfolio Value: ₹%{y:,.0f}<extra></extra>"
    ))

    fig.update_layout(
        title="Empirical Portfolio Value Evolution (Base ₹10,00,000)",
        xaxis=dict(title="Date", showgrid=True),
        yaxis=dict(title="Portfolio Value (INR)", tickprefix="₹", showgrid=True),
        height=320,
        margin=dict(t=40, b=40, l=50, r=20)
    )
    return fig

def plot_drawdown_chart(daily_df: pd.DataFrame) -> go.Figure:
    """Renders underwater drawdown chart."""
    if daily_df.empty or "Drawdown_Pct" not in daily_df.columns:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_df["Date"],
        y=daily_df["Drawdown_Pct"],
        mode="lines",
        name="Drawdown %",
        line=dict(color=COLORS["danger"], width=1.5),
        fill="tozeroy",
        fillcolor="rgba(239, 68, 68, 0.25)",
        hovertemplate="Date: %{x|%d-%b-%Y}<br>Drawdown: %{y:.2f}%<extra></extra>"
    ))

    fig.update_layout(
        title="Portfolio Underwater Drawdown Profile",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Drawdown (%)", ticksuffix="%"),
        height=220,
        margin=dict(t=35, b=30, l=50, r=20)
    )
    return fig

def plot_sensitivity_heatmap(sensitivity_records: List[Dict[str, Any]]) -> go.Figure:
    """Renders a sensitivity matrix heatmap for required SIP vs Return & Inflation."""
    df = pd.DataFrame(sensitivity_records)
    if df.empty:
        return go.Figure()

    pivot = df.pivot(index="inflation_rate_pct", columns="expected_return_pct", values="monthly_sip")
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"{c}% Return" for c in pivot.columns],
        y=[f"{r}% Inflation" for r in pivot.index],
        colorscale="Blues_r",
        text=pivot.values,
        texttemplate="₹%{text:,.0f}",
        textfont={"size": 11},
        hoverongaps=False
    ))

    fig.update_layout(
        title="SIP Sensitivity Matrix: Monthly SIP (₹) under Varying Scenarios",
        xaxis=dict(title="Assumed Annual Investment Return"),
        yaxis=dict(title="Assumed Annual Inflation"),
        height=280,
        margin=dict(t=40, b=40, l=60, r=20)
    )
    return fig

