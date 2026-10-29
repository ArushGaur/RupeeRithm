"""
Zeckathon Problem Statement 04: AI Investment Adviser Co-pilot.
"A Co-pilot That Lets One Adviser Serve 1,000 Clients Safely."
Main Streamlit Application Entrypoint.
"""

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="AI Investment Adviser Co-pilot | Zeckathon PS-04",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom institutional styling
st.markdown("""
<style>
    /* Main container and font styles */
    .main {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Metrics card styling */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 700;
        color: #1E3A8A;
    }
    
    /* Sidebar branding */
    .sidebar-header {
        padding: 12px 0;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 16px;
    }
    
    /* Table headers */
    th {
        background-color: #F1F5F9 !important;
        color: #1E293B !important;
        font-weight: 600 !important;
    }
    
    /* Card containers */
    .stCard {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        padding: 16px;
        background-color: #FFFFFF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Import individual page views
from ui.page_dashboard import render_dashboard_page
from ui.page_clients import render_clients_page
from ui.page_goal_planner import render_goal_planner_page
from ui.page_fund_explorer import render_fund_explorer_page
from ui.page_ai_assistant import render_ai_assistant_page
from ui.page_backtest import render_backtest_page
from ui.page_adviser_review import render_adviser_review_page

def main():
    # Sidebar Branding
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h2 style="margin: 0; color: #1E3A8A; font-size: 20px;">🏛️ RIA Co-pilot</h2>
        <span style="font-size: 11px; color: #64748B; font-weight: 600; letter-spacing: 0.5px;">ZECKATHON PS-04 • SERVE 1,000 SAFELY</span>
    </div>
    """, unsafe_allow_html=True)

    # Navigation menu
    PAGES = {
        "Executive Dashboard": render_dashboard_page,
        "Client Profiles": render_clients_page,
        "Goal Planner": render_goal_planner_page,
        "Fund Explorer": render_fund_explorer_page,
        "AI Research Assistant": render_ai_assistant_page,
        "Portfolio Analysis": render_backtest_page,
        "Adviser Review": render_adviser_review_page
    }

    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = "Executive Dashboard"

    # Radio selection for navigation
    selected_page = st.sidebar.radio(
        "Navigation",
        list(PAGES.keys()),
        index=list(PAGES.keys()).index(st.session_state["nav_page"]) if st.session_state["nav_page"] in PAGES else 0
    )
    st.session_state["nav_page"] = selected_page

    # Sidebar Fiduciary Status Badge
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; padding: 10px; border-radius: 6px; font-size: 11px;">
        <strong style="color: #1E40AF;">SEBI RIA Guardrails Active</strong><br>
        <span style="color: #3B82F6;">• Direct Plans Only</span><br>
        <span style="color: #3B82F6;">• Zero Return Guarantees</span><br>
        <span style="color: #3B82F6;">• Senior Citizen Equity Cap</span><br>
        <span style="color: #3B82F6;">• Human-in-the-Loop Sign-off</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.caption("Prototype Version 1.0.0 • Local Offline Cache")

    # Render selected view
    page_func = PAGES[selected_page]
    page_func()

if __name__ == "__main__":
    main()

