"""
Page 3: Goal-Based Financial Planner.
Performs deterministic mathematical planning: inflation-adjusted target corpus,
future value of existing assets, required monthly SIP (annuity due), real return,
systematic de-risking glide paths, and multi-scenario sensitivity matrices.
"""

import streamlit as st
import pandas as pd
from core.client import get_all_clients, FinancialGoal, save_custom_client
from core.financial_calc import calculate_goal_projection
from core.risk_engine import assess_client_risk
from ui.components import plot_asset_allocation_donut, plot_glide_path_chart, plot_sensitivity_heatmap

def render_goal_planner_page():
    st.title("🎯 Goal-Based Financial Planner")
    st.markdown(
        "Deterministic compounding calculations for inflation-adjusted target corpus, required monthly SIP, "
        "asset allocation, and systematic glide paths. No hallucinations — powered strictly by mathematical formulas."
    )

    clients = get_all_clients()
    client_keys = list(clients.keys())
    default_key = st.session_state.get("active_client_key", client_keys[0])
    idx = client_keys.index(default_key) if default_key in client_keys else 0
    selected_client_id = st.selectbox(
        "Select Client Profile:",
        client_keys,
        index=idx,
        format_func=lambda k: clients[k].name
    )
    st.session_state["active_client_key"] = selected_client_id
    client = clients[selected_client_id]
    risk_res = assess_client_risk(client)

    # Goal Selection or Creation
    existing_goals = client.financial_goals
    goal_names = [g.name for g in existing_goals]
    
    st.markdown("---")
    col_sel, col_new = st.columns([3, 1])
    with col_sel:
        selected_goal_name = st.selectbox("Select Financial Goal to Plan:", goal_names if goal_names else ["No goals"])
    with col_new:
        st.write("")
        st.write("")
        create_new = st.checkbox("➕ Add New Goal")

    if create_new:
        with st.form("new_goal_form"):
            st.subheader("Create New Financial Goal")
            n_name = st.text_input("Goal Name", value="Retirement Wealth")
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                n_cost = st.number_input("Target Cost in Today's Money (₹)", min_value=10000.0, value=2500000.0, step=50000.0)
                n_years = st.number_input("Years to Goal Deadline", min_value=0.5, max_value=40.0, value=10.0, step=0.5)
                n_alloc = st.number_input("Existing Savings Allocated (₹)", min_value=0.0, value=200000.0, step=25000.0)
            with g_col2:
                n_inf = st.number_input("Assumed Annual Inflation (e.g. 0.06 for 6%)", min_value=0.01, max_value=0.20, value=0.06, step=0.005, format="%.3f")
                n_ret = st.number_input("Assumed Annual Investment Return (e.g. 0.12 for 12%)", min_value=0.01, max_value=0.20, value=0.12, step=0.005, format="%.3f")
                n_prio = st.selectbox("Priority", ["High", "Medium", "Low"])
            
            submit_goal = st.form_submit_button("Save Goal to Client Profile")
            if submit_goal:
                new_g = FinancialGoal(
                    goal_id=f"g_custom_{len(existing_goals)+1}",
                    name=n_name,
                    target_corpus=n_cost,
                    years_remaining=n_years,
                    existing_allocated=n_alloc,
                    inflation_rate=n_inf,
                    expected_return=n_ret,
                    priority=n_prio
                )
                client.financial_goals.append(new_g)
                save_custom_client(client)
                st.success(f"Goal '{n_name}' added to {client.name}!")
                st.rerun()

    if not existing_goals and not create_new:
        st.warning("Please add a financial goal using the checkbox above to begin planning.")
        return

    # Find active goal
    active_goal = next((g for g in existing_goals if g.name == selected_goal_name), existing_goals[0] if existing_goals else None)
    if not active_goal:
        return

    # Interactive Adjustments Sidebar/Controls
    st.subheader(f"Planning Analysis: {active_goal.name}")
    
    with st.expander("⚙️ Fine-Tune Goal Parameters & Assumptions", expanded=False):
        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            adj_cost = st.number_input("Current Cost (₹)", value=float(active_goal.target_corpus), step=50000.0)
            adj_years = st.number_input("Years Remaining", value=float(active_goal.years_remaining), step=0.5)
        with c_p2:
            adj_alloc = st.number_input("Existing Earmarked (₹)", value=float(active_goal.existing_allocated), step=25000.0)
            adj_inf = st.number_input("Inflation Rate", value=float(active_goal.inflation_rate), step=0.005, format="%.3f")
        with c_p3:
            adj_ret = st.number_input("Expected Return", value=float(active_goal.expected_return), step=0.005, format="%.3f")
            
        active_goal.target_corpus = adj_cost
        active_goal.years_remaining = adj_years
        active_goal.existing_allocated = adj_alloc
        active_goal.inflation_rate = adj_inf
        active_goal.expected_return = adj_ret

    # Calculate deterministic projection
    proj = calculate_goal_projection(active_goal, max_equity_cap=risk_res.max_equity_allocation_pct)

    # Display KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Future Target Corpus", f"₹{proj['future_corpus']:,.0f}", f"Inflation: {proj['inflation_rate_pct']}%")
    with k2:
        st.metric("Existing Asset FV", f"₹{proj['existing_fv']:,.0f}", f"Current: ₹{proj['existing_allocated']:,.0f}")
    with k3:
        st.metric("Funding Shortfall", f"₹{proj['funding_shortfall']:,.0f}", "To be accumulated via SIP")
    with k4:
        st.metric(
            label="Required Monthly SIP",
            value=f"₹{proj['monthly_sip']:,.0f} / mo",
            delta=f"Real Return: {proj['real_return_pct']}% p.a."
        )

    st.markdown("---")

    # Visualizations Row
    col_chart_left, col_chart_right = st.columns([1, 1])

    with col_chart_left:
        st.plotly_chart(
            plot_asset_allocation_donut(proj["asset_allocation"], title=f"Recommended Baseline Allocation ({risk_res.final_recommended_tier})"),
            use_container_width=True
        )

    with col_chart_right:
        st.plotly_chart(
            plot_glide_path_chart(proj["glide_path"]),
            use_container_width=True
        )

    # Sensitivity Analysis Section
    st.subheader("📊 Scenario Sensitivity Matrix")
    st.markdown("Examines how required monthly SIP shifts if equity returns fluctuate by ±2% or inflation shifts by ±1%:")
    
    st.plotly_chart(
        plot_sensitivity_heatmap(proj["sensitivity_matrix"]),
        use_container_width=True
    )

    st.caption(f"📢 **SEBI Compliance Disclosure**: {proj['disclaimer']}")

