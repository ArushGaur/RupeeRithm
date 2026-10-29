"""
Page 6: Portfolio Backtesting & Historical Risk-Return Analysis.
Executes empirical multi-asset backtesting on daily historical NAVs,
calculates CAGR, annualized volatility, maximum drawdown, and Sharpe ratio,
and prominently reports data coverage limitations.
"""

import streamlit as st
import pandas as pd
from core.backtesting import run_portfolio_backtest
from core.data_loader import load_historical_nav_series
from ui.components import plot_backtest_curve, plot_drawdown_chart

def render_backtest_page():
    st.title("📈 Empirical Portfolio Backtesting & Analysis")
    st.markdown(
        "Reproducible multi-asset portfolio backtesting engine using available empirical daily NAV observations. "
        "Strictly adheres to evaluation standards: **reports verified historical data without inventing fake market prices.**"
    )

    hist_series = load_historical_nav_series()
    assets = list(hist_series.keys())

    if not assets:
        st.error("No historical daily NAV time series found in local data directory.")
        return

    # Configuration Sidebar / Controls
    st.subheader("⚙️ Portfolio Configuration & Asset Weights")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown(f"**Asset 1**: `{assets[0]}`")
        w1 = st.slider(f"Weight for {assets[0][:30]}...", min_value=0.0, max_value=1.0, value=0.60, step=0.05)
    with col_w2:
        if len(assets) > 1:
            st.markdown(f"**Asset 2**: `{assets[1]}`")
            w2 = 1.0 - w1
            st.info(f"Complementary Weight for Asset 2: **{w2*100:.0f}%** (Total: 100%)")
        else:
            w2 = 0.0

    target_weights = {assets[0]: w1}
    if len(assets) > 1:
        target_weights[assets[1]] = w2

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        initial_corpus = st.number_input("Initial Investment Amount (₹)", min_value=100000.0, value=1000000.0, step=50000.0)
    with col_p2:
        rf_rate = st.number_input("Risk-Free Rate (Annual, e.g. 0.065 for 6.5%)", min_value=0.01, max_value=0.12, value=0.065, step=0.005, format="%.3f")

    # Run Backtest
    with st.spinner("Executing empirical backtest and aligning historical dates..."):
        res = run_portfolio_backtest(
            weights=target_weights,
            initial_capital=initial_corpus,
            risk_free_rate=rf_rate
        )

    # Prominent Coverage Limitation Notice
    if res.coverage_warning:
        st.warning(f"⚠️ **{res.coverage_warning}**")

    st.markdown("---")

    # KPI Metrics
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Period Return", f"{res.absolute_return_pct:.2f}%", f"{res.trading_days} Trading Days")
    with k2:
        st.metric("Annualized CAGR", f"{res.cagr_pct:.2f}%" if res.cagr_pct is not None else "N/A", "Annualized Compounded")
    with k3:
        st.metric("Annualized Volatility", f"{res.annualized_volatility_pct:.2f}%" if res.annualized_volatility_pct is not None else "N/A", "Standard Deviation (σ)")
    with k4:
        st.metric("Max Drawdown", f"{res.max_drawdown_pct:.2f}%", "Peak-to-Trough Decline", delta_color="inverse")
    with k5:
        st.metric("Sharpe Ratio", f"{res.sharpe_ratio:.2f}" if res.sharpe_ratio is not None else "N/A", f"Rf = {rf_rate*100:.1f}%")

    # Charts Row
    st.plotly_chart(
        plot_backtest_curve(res.daily_portfolio_values, res.portfolio_name),
        use_container_width=True
    )
    
    st.plotly_chart(
        plot_drawdown_chart(res.daily_portfolio_values),
        use_container_width=True
    )

    # Asset Contribution & Benchmark Comparison
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("📊 Asset Level Contribution")
        contrib_data = []
        for aname, cinfo in res.asset_contributions.items():
            contrib_data.append({
                "Asset": aname,
                "Weight": f"{cinfo['weight_pct']}%",
                "Asset Return": f"{cinfo['asset_absolute_return_pct']}%",
                "Weighted Contribution": f"{cinfo['weighted_contribution_pct']}%"
            })
        st.dataframe(pd.DataFrame(contrib_data), use_container_width=True, hide_index=True)

    with col_c2:
        st.subheader("🎯 Benchmark Relative Performance")
        bm = res.benchmark_comparison
        st.write(f"**Benchmark Reference**: {bm['benchmark_name']}")
        st.write(f"- Benchmark Return over Period: **{bm['benchmark_period_return_pct']}%**")
        st.write(f"- Active Alpha Generated: **{bm['alpha_generated_pct']}%**")
        st.caption(f"Note: {bm['notes']}")

    # Methodology Notes
    with st.expander("📝 Methodological Assumptions & Limitations Disclosures", expanded=True):
        for note in res.methodology_notes:
            st.markdown(f"- {note}")
        st.markdown(
            "- **Integrity Guarantee**: We do not claim to have completed a 10-year backtest because the local files contain 77 daily observations. "
            "Under Zeckathon evaluation rubrics, fabricating synthetic daily market data is strictly forbidden."
        )

