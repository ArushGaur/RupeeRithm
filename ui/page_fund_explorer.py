"""
Page 4: Mutual Fund Universe & Fund Explorer.
Enables searching and filtering across 14,419 AMFI schemes,
verifies Direct Plan and Growth options, ranks schemes with explainable criteria,
and displays verified factsheet disclosures and empirical NAV charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from core.fund_analysis import filter_funds, rank_funds, enrich_fund_with_factsheet
from core.data_loader import load_historical_nav_series, load_amfi_nav_all

def render_fund_explorer_page():
    st.title("🔎 AMFI Mutual Fund Universe & Research Explorer")
    st.markdown(
        "Screen and analyze the live AMFI universe (14,419 schemes). Enforces SEBI RIA fiduciary rules: "
        "filters for **Direct Plans** (zero commission) and **Growth Options** (tax compounding) with explainable ranking."
    )

    amfi_df = load_amfi_nav_all()
    hist_series = load_historical_nav_series()

    # Search and Filter Controls
    col_s1, col_s2, col_s3, col_s4 = st.columns([2, 1, 1, 1])
    with col_s1:
        query = st.text_input("🔍 Search Scheme Name / AMC / Keyword:", placeholder="e.g. Nifty 50, Flexi Cap, Liquid, DSP, Mirae...")
    with col_s2:
        asset_classes = ["All", "Equity", "Debt", "Hybrid", "Passive / Index", "Solution Oriented"]
        selected_asset = st.selectbox("Asset Class", asset_classes)
    with col_s3:
        direct_toggle = st.checkbox("Direct Plans Only", value=True, help="Mandatory for SEBI Registered Investment Advisers")
    with col_s4:
        growth_toggle = st.checkbox("Growth Options Only", value=True, help="Optimized for long-term compounding")

    filtered_funds = filter_funds(
        search_query=query,
        broad_asset_class=selected_asset,
        direct_only=direct_toggle,
        growth_only=growth_toggle,
        limit=100
    )

    st.markdown(f"**Found {len(filtered_funds)} schemes** matching current filters (Displaying top 100):")

    if filtered_funds.empty:
        st.warning("No schemes match the specified filters. Try loosening search terms.")
        return

    # Rank filtered schemes
    ranked_df = rank_funds(filtered_funds)

    display_cols = ["scheme_name", "category", "plan", "option", "nav", "composite_score", "ter_direct_pct", "aum_cr", "benchmark"]
    st.dataframe(
        ranked_df[display_cols].rename(columns={
            "scheme_name": "Scheme Name",
            "category": "SEBI Category",
            "plan": "Plan",
            "option": "Option",
            "nav": "Latest NAV (₹)",
            "composite_score": "Score (0-100)",
            "ter_direct_pct": "Direct TER %",
            "aum_cr": "AUM",
            "benchmark": "Benchmark"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # Scheme Deep-Dive Section
    st.subheader("🔬 Scheme Due Diligence & Verified Factsheet Disclosures")
    scheme_options = ranked_df["scheme_name"].tolist()
    selected_scheme_name = st.selectbox("Select Scheme for In-Depth Fiduciary Review:", scheme_options)

    fund_row = ranked_df[ranked_df["scheme_name"] == selected_scheme_name].iloc[0]
    enrichment = enrich_fund_with_factsheet(selected_scheme_name)

    c_d1, c_d2, c_d3, c_d4 = st.columns(4)
    with c_d1:
        st.metric("Latest NAV", f"₹{fund_row['nav']}" if pd.notna(fund_row['nav']) else "N/A", fund_row["plan"])
    with c_d2:
        st.metric("Direct TER", f"{enrichment['ter_direct_pct']}%" if enrichment['ter_direct_pct'] else "Not Disclosed", "Annual Expense Ratio")
    with c_d3:
        st.metric("AUM", f"₹{enrichment['aum_cr']:,.0f} Cr" if enrichment['aum_cr'] else "Not Disclosed", "Fund Corpus Size")
    with c_d4:
        st.metric("Risk-o-Meter", enrichment["risk_o_meter"], "SEBI Risk Label")

    st.markdown("#### 💡 Fiduciary Selection Rationale")
    st.info(f"**Selection Scoring Analysis**: {fund_row['selection_rationale']}")

    st.markdown("#### 📄 Document Source Reference")
    st.caption(f"**Verified Factsheet / Master Source**: `{fund_row['source_doc']}`")

    # If this scheme matches an empirical daily historical series, display its NAV chart
    matched_hist_key = None
    for k in hist_series.keys():
        if "altiva" in selected_scheme_name.lower() and "altiva" in k.lower():
            matched_hist_key = k
            break
        elif "infinity" in selected_scheme_name.lower() and "infinity" in k.lower():
            matched_hist_key = k
            break

    if matched_hist_key:
        st.markdown(f"#### 📈 Historical Daily NAV Chart ({matched_hist_key})")
        h_df = hist_series[matched_hist_key]
        fig_nav = px.line(h_df, x="Date", y="Net Asset Value", title=f"Empirical Daily NAV Series: {matched_hist_key}")
        fig_nav.update_layout(height=300, margin=dict(t=30, b=30, l=40, r=20))
        st.plotly_chart(fig_nav, use_container_width=True)
    else:
        st.markdown("""
        <div style="background-color: #F8FAFC; border: 1px dashed #CBD5E1; padding: 12px; border-radius: 6px; font-size: 13px; color: #64748B;">
            ℹ️ Daily empirical time-series observations in local files are currently available for Altiva SIF and Infinity SIF. 
            For this scheme, latest NAV is loaded from AMFI live snapshot. Full multi-year daily NAV history can be imported via the data pipeline.
        </div>
        """, unsafe_allow_html=True)

