"""
Page 2: Client Intake & Dual-Engine Risk Profiling.
Allows selecting one of the 6 standard problem statement personas or creating a custom client.
Calculates and presents Risk Capacity and Risk Tolerance separately,
detects conflicts, shows calculation breakdowns, and allows adding and editing
Problem Statement Context and illustrative assumptions for any client.
"""

import streamlit as st
import time
import re
from core.client import get_all_clients, save_custom_client, ClientProfile, FinancialGoal
from core.risk_engine import assess_client_risk
from core.financial_calc import calculate_goal_projection
from core.approval import AdvisoryPlan, add_or_update_plan
from core.suitability import evaluate_plan_suitability

def render_clients_page():
    st.title("👤 Client Intake & Dual-Engine Risk Profiling")
    st.markdown(
        "Separates **Financial Risk Capacity** (mathematical ability to endure loss) from **Behavioral Risk Tolerance** "
        "(psychological willingness to bear volatility), resolving conflicts under SEBI fiduciary standards."
    )

    clients = get_all_clients()
    persona_keys = list(clients.keys())

    # Session state management for selected client
    if "active_client_key" not in st.session_state or st.session_state["active_client_key"] not in persona_keys:
        st.session_state["active_client_key"] = persona_keys[0]

    current_idx = persona_keys.index(st.session_state["active_client_key"])

    # Persona Selector or Custom Intake
    st.sidebar.markdown("---")
    st.sidebar.subheader("Select Persona / Client")
    selected_key = st.sidebar.selectbox(
        "Choose a Test Persona or Custom Client:",
        persona_keys,
        index=current_idx,
        format_func=lambda k: clients[k].name,
        key="client_selector_widget"
    )
    st.session_state["active_client_key"] = selected_key
    current_client = clients[selected_key]

    # Flash success message if client just created/updated
    if "profile_created_success" in st.session_state:
        st.success(st.session_state.pop("profile_created_success"))

    tab1, tab2 = st.tabs(["📋 Active Profile & Risk Evaluation", "✍️ Create New Client / Edit Profile"])

    with tab1:
        st.subheader(f"Profile: {current_client.name}")
        
        # Problem Statement Context Display
        if current_client.persona_notes:
            st.info(f"📌 **Problem Statement Context**: {current_client.persona_notes}")
        else:
            st.caption("📌 *No Problem Statement Context configured yet for this client.*")

        # Quick in-place editor for Problem Statement Context
        with st.expander("✏️ Quick Edit: Problem Statement Context for this Client"):
            with st.form(f"quick_edit_context_{current_client.id}"):
                quick_notes = st.text_area(
                    "Problem Statement Context / Scenario Notes:",
                    value=current_client.persona_notes or "",
                    help="Describe the client's financial situation, background, constraints, or case study goals.",
                    height=90
                )
                save_quick_btn = st.form_submit_button("💾 Save Problem Statement Context")
                if save_quick_btn:
                    current_client.persona_notes = quick_notes.strip() if quick_notes.strip() else None
                    save_custom_client(current_client)
                    st.session_state["profile_created_success"] = f"Problem Statement Context for '{current_client.name}' updated!"
                    st.rerun()

        if current_client.assumptions_made:
            with st.expander("🔍 View Illustrative Assumptions & Methodology Notes", expanded=False):
                for asm in current_client.assumptions_made:
                    st.markdown(f"- *{asm}*")

        # Top client metrics cards
        col1, col2, col3, col4 = st.columns(4)
        surplus = max(0.0, current_client.monthly_income - current_client.monthly_expenses)
        with col1:
            st.metric("Age / City", f"{current_client.age} yrs", current_client.city)
        with col2:
            st.metric("Monthly Surplus", f"₹{surplus:,.0f}", f"Income: ₹{current_client.monthly_income:,.0f}")
        with col3:
            st.metric("Net Savings", f"₹{current_client.existing_savings:,.0f}", f"Debt: ₹{current_client.existing_liabilities:,.0f}")
        with col4:
            st.metric("Horizon & Buffer", f"{current_client.investment_horizon_years:.0f} yrs", f"{current_client.emergency_fund_months:.1f} mos buffer")

        st.markdown("---")

        # Risk Engine Execution
        risk_result = assess_client_risk(current_client)

        st.subheader("⚖️ Dual Risk Engine Assessment")
        rc_col, rt_col, rf_col = st.columns(3)

        with rc_col:
            st.markdown("#### 1. Financial Risk Capacity")
            st.metric(
                label="Capacity Score (Ability to take loss)",
                value=f"{risk_result.capacity_score:.1f} / 100",
                delta=f"Tier: {risk_result.capacity_tier}"
            )
            with st.expander("Capacity Breakdown"):
                cb = risk_result.capacity_breakdown
                st.write(f"- **Savings Rate Score**: {cb['savings_rate_score']}/25 ({cb['savings_rate_pct']}%)")
                st.write(f"- **Emergency Buffer Score**: {cb['liquidity_score']}/20 ({cb['emergency_months']} months)")
                st.write(f"- **Debt Burden Score**: {cb['debt_burden_score']}/20 (Debt/Assets: {cb['debt_to_assets']})")
                st.write(f"- **Time Horizon Score**: {cb['horizon_score']}/20 ({cb['horizon_years']} years)")
                st.write(f"- **Stability & Family Score**: {cb['stability_and_dependants_score']}/15")

        with rt_col:
            st.markdown("#### 2. Behavioral Risk Tolerance")
            st.metric(
                label="Tolerance Score (Psychological willingness)",
                value=f"{risk_result.tolerance_score:.1f} / 100",
                delta=f"Tier: {risk_result.tolerance_tier}"
            )
            with st.expander("Tolerance Breakdown"):
                tb = risk_result.tolerance_breakdown
                st.write(f"- **Behavioral Questionnaire Score**: {tb['raw_behavioral_score']} / 10")
                st.write(f"- **Psychological Tier**: {tb['tier']}")
                st.write(f"- **Self-reported Label**: {tb['stated_label']}")

        with rf_col:
            st.markdown("#### 3. SEBI Fiduciary Recommendation")
            st.metric(
                label="Final Recommended Risk Tier",
                value=risk_result.final_recommended_tier,
                delta=f"Max Equity Cap: {risk_result.max_equity_allocation_pct:.0f}%"
            )
            st.write(f"**Equity Ceiling**: {risk_result.max_equity_allocation_pct:.1f}%")
            st.write(f"**Debt/Liquid Floor**: {100.0 - risk_result.max_equity_allocation_pct:.1f}%")

        # Conflict Banner
        if risk_result.conflict_detected:
            st.warning(f"⚠️ **FIDUCIARY CONFLICT DETECTED**: {risk_result.conflict_type}")
            st.markdown(f"> **Reasoning**: {risk_result.conflict_reasoning}")
            st.markdown("**Required Adviser Next Steps:**")
            for act in risk_result.recommended_actions:
                st.markdown(f"- 📌 {act}")
        else:
            st.success("✅ **Capacity & Tolerance Aligned**: Client's financial capacity comfortably matches psychological risk tolerance.")

        st.markdown("---")
        st.subheader("🎯 Earmarked Financial Goals")
        if current_client.financial_goals:
            for g in current_client.financial_goals:
                g_c1, g_c2, g_c3, g_c4 = st.columns(4)
                with g_c1:
                    st.write(f"**Goal**: {g.name}")
                with g_c2:
                    st.write(f"**Target Cost (Today)**: ₹{g.target_corpus:,.0f}")
                with g_c3:
                    st.write(f"**Deadline**: {g.years_remaining:.1f} years")
                with g_c4:
                    st.write(f"**Assumed Return / Inf**: {g.expected_return*100:.1f}% / {g.inflation_rate*100:.1f}%")
        else:
            st.caption("No specific goals mapped yet for this client. Create one in the Goal Planner page.")

    with tab2:
        action_mode = st.radio(
            "Select Profile Action:",
            ["➕ Create Brand New Client Profile", f"✏️ Edit Currently Selected Profile ({current_client.name})"],
            horizontal=True
        )

        if "Create Brand New" in action_mode:
            st.subheader("➕ Intake Form: Register a New Client")
            st.markdown("Enter the new client's financial details below to create an auditable profile and automated initial plan:")

            with st.form("new_client_intake_form"):
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    new_name = st.text_input("Client Full Name *", placeholder="e.g. Ramesh Kulkarni")
                    new_age = st.number_input("Age", min_value=18, max_value=95, value=35)
                    new_city = st.text_input("City", value="Mumbai")
                    new_income = st.number_input("Monthly Take-Home Income (₹)", min_value=0.0, value=125000.0, step=5000.0)
                    new_expenses = st.number_input("Monthly Living Expenses (₹)", min_value=0.0, value=65000.0, step=5000.0)
                    new_savings = st.number_input("Existing Financial Assets / Savings (₹)", min_value=0.0, value=750000.0, step=50000.0)
                with col_n2:
                    new_debt = st.number_input("Existing Liabilities / Loans (₹)", min_value=0.0, value=0.0, step=25000.0)
                    new_deps = st.number_input("Number of Dependants", min_value=0, max_value=10, value=1)
                    new_stability = st.selectbox("Income Stability", ["Stable", "Fluctuating", "Fixed Pension", "High Volatility"], index=0)
                    new_emg = st.number_input("Emergency Buffer (Months of Expenses in Cash)", min_value=0.0, max_value=48.0, value=4.0, step=0.5)
                    new_horizon = st.number_input("Overall Investment Horizon (Years)", min_value=1.0, max_value=40.0, value=15.0, step=1.0)
                    new_major = st.number_input("Anticipated Outflows in Next 1-2 Years (₹)", min_value=0.0, value=0.0, step=25000.0)

                # Problem Statement Context Field for New Profile
                new_persona_notes = st.text_area(
                    "Problem Statement Context / Case Study Notes:",
                    placeholder="e.g. Age 35; IT professional; ₹1.25L take-home; 1 infant child; needs long-term wealth creation and emergency buffer.",
                    help="Describe the scenario, test persona situation, or case study goals from the problem statement.",
                    height=80
                )

                st.markdown("#### Behavioral Risk Questionnaire")
                new_score = st.slider(
                    "Risk Tolerance Scale (1 = Extremely Conservative / FD Only, 5 = Moderate, 10 = High Volatility / Aggressive)",
                    min_value=1,
                    max_value=10,
                    value=6
                )

                st.markdown("#### Primary Financial Goal Setup")
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    g_name = st.text_input("Goal Name", value="Long-Term Wealth & Retirement")
                    g_cost = st.number_input("Target Corpus in Today's Money (₹)", min_value=10000.0, value=3000000.0, step=50000.0)
                    g_years = st.number_input("Years to Goal Deadline", min_value=1.0, max_value=40.0, value=12.0, step=1.0)
                with col_g2:
                    g_alloc = st.number_input("Existing Savings Earmarked (₹)", min_value=0.0, value=150000.0, step=25000.0)
                    g_inf = st.number_input("Assumed Annual Inflation (e.g. 0.06 for 6%)", min_value=0.01, max_value=0.20, value=0.06, step=0.005, format="%.3f")
                    g_ret = st.number_input("Assumed Expected Return (e.g. 0.12 for 12%)", min_value=0.01, max_value=0.20, value=0.12, step=0.005, format="%.3f")

                submit_new = st.form_submit_button("🚀 Create & Register New Client Profile", type="primary")

                if submit_new:
                    if not new_name.strip():
                        st.error("Please enter a valid Client Full Name.")
                    else:
                        # Generate clean unique identifier
                        clean_slug = re.sub(r'[^a-zA-Z0-9]', '_', new_name.strip().lower())
                        new_id = f"client_{clean_slug}_{int(time.time())}"

                        tol_label = "Conservative" if new_score <= 3 else ("Moderate" if new_score <= 6 else "Aggressive")

                        goal_obj = FinancialGoal(
                            goal_id=f"goal_{int(time.time())}",
                            name=g_name,
                            target_corpus=g_cost,
                            years_remaining=g_years,
                            existing_allocated=g_alloc,
                            inflation_rate=g_inf,
                            expected_return=g_ret,
                            priority="High"
                        )

                        notes_val = new_persona_notes.strip() if new_persona_notes.strip() else None

                        new_client_obj = ClientProfile(
                            id=new_id,
                            name=new_name.strip(),
                            age=int(new_age),
                            city=new_city.strip(),
                            monthly_income=float(new_income),
                            monthly_expenses=float(new_expenses),
                            existing_savings=float(new_savings),
                            existing_liabilities=float(new_debt),
                            number_of_dependants=int(new_deps),
                            income_stability=new_stability,
                            emergency_fund_months=float(new_emg),
                            investment_horizon_years=float(new_horizon),
                            financial_goals=[goal_obj],
                            behavioral_risk_score=int(new_score),
                            risk_tolerance_label=tol_label,
                            expected_major_expenses=float(new_major),
                            is_persona=False,
                            persona_notes=notes_val,
                            assumptions_made=[
                                f"Monthly living expenses configured at ₹{new_expenses:,.0f}.",
                                f"Goal {g_name} projected at {g_inf*100:.1f}% inflation and {g_ret*100:.1f}% expected return."
                            ]
                        )

                        # Persist to disk
                        save_custom_client(new_client_obj)

                        # Automatically compute initial goal projection and register plan in Pending Review state
                        risk_eval = assess_client_risk(new_client_obj)
                        proj = calculate_goal_projection(goal_obj, max_equity_cap=risk_eval.max_equity_allocation_pct)
                        
                        # Generate recommended Direct Growth mix matching allocation
                        eq_pct = proj["asset_allocation"]["equity_pct"]
                        db_pct = proj["asset_allocation"]["debt_pct"]
                        lq_pct = proj["asset_allocation"]["liquid_pct"]

                        recommended_schemes = []
                        if eq_pct > 0:
                            recommended_schemes.append({"scheme_name": "Axis Nifty 500 Index Fund - Direct - Growth", "allocation_pct": round(eq_pct * 0.6, 1)})
                            recommended_schemes.append({"scheme_name": "Mirae Asset Large Cap Fund - Direct - Growth", "allocation_pct": round(eq_pct * 0.4, 1)})
                        if db_pct > 0:
                            recommended_schemes.append({"scheme_name": "DSP Short Term Fund - Direct - Growth", "allocation_pct": round(db_pct, 1)})
                        if lq_pct > 0:
                            recommended_schemes.append({"scheme_name": "DSP Liquid Fund - Direct - Growth", "allocation_pct": round(lq_pct, 1)})

                        suit_rep = evaluate_plan_suitability(
                            client=new_client_obj,
                            goal=goal_obj,
                            proposed_equity_pct=eq_pct,
                            proposed_debt_pct=db_pct,
                            proposed_schemes=recommended_schemes
                        )

                        new_plan = AdvisoryPlan(
                            plan_id=f"PLAN-{int(time.time()) % 10000:04d}",
                            client_id=new_id,
                            client_name=new_name.strip(),
                            goal_name=g_name,
                            target_corpus=proj["future_corpus"],
                            years_remaining=g_years,
                            required_monthly_sip=proj["monthly_sip"],
                            asset_allocation=proj["asset_allocation"],
                            recommended_schemes=recommended_schemes,
                            suitability_verdict=suit_rep.overall_verdict,
                            suitability_warnings_count=len(suit_rep.warnings),
                            status="Pending Review"
                        )
                        add_or_update_plan(new_plan)

                        # Update session state to select this new client immediately
                        st.session_state["active_client_key"] = new_id
                        st.session_state["profile_created_success"] = f"🎉 Client Profile for '{new_name.strip()}' successfully created and added to Adviser Queue!"
                        st.rerun()

        else:
            st.subheader(f"✏️ Edit Profile: {current_client.name}")
            with st.form("edit_client_form"):
                e_name = st.text_input("Client Full Name", value=current_client.name)
                col_ea, col_eb = st.columns(2)
                with col_ea:
                    e_age = st.number_input("Age", min_value=18, max_value=100, value=current_client.age)
                    e_city = st.text_input("City", value=current_client.city)
                    e_income = st.number_input("Monthly Income (₹)", min_value=0.0, value=float(current_client.monthly_income), step=5000.0)
                    e_expenses = st.number_input("Monthly Expenses (₹)", min_value=0.0, value=float(current_client.monthly_expenses), step=5000.0)
                    e_savings = st.number_input("Existing Savings (₹)", min_value=0.0, value=float(current_client.existing_savings), step=50000.0)
                with col_eb:
                    e_debt = st.number_input("Existing Liabilities (₹)", min_value=0.0, value=float(current_client.existing_liabilities), step=25000.0)
                    e_deps = st.number_input("Dependants", min_value=0, max_value=10, value=current_client.number_of_dependants)
                    stability_list = ["Stable", "Fluctuating", "Fixed Pension", "High Volatility"]
                    e_stab_idx = stability_list.index(current_client.income_stability) if current_client.income_stability in stability_list else 0
                    e_stability = st.selectbox("Income Stability", stability_list, index=e_stab_idx)
                    e_emg = st.number_input("Emergency Buffer (Months)", min_value=0.0, max_value=60.0, value=float(current_client.emergency_fund_months), step=0.5)
                    e_horizon = st.number_input("Horizon (Years)", min_value=1.0, max_value=50.0, value=float(current_client.investment_horizon_years), step=1.0)

                # Problem Statement Context Field for Existing Profile
                e_persona_notes = st.text_area(
                    "Problem Statement Context / Scenario Notes:",
                    value=current_client.persona_notes or "",
                    help="Edit the problem statement context or case scenario for this client.",
                    height=90
                )

                e_score = st.slider("Risk Tolerance (1-10)", min_value=1, max_value=10, value=current_client.behavioral_risk_score)
                e_major = st.number_input("Anticipated Outflow (₹)", min_value=0.0, value=float(current_client.expected_major_expenses), step=25000.0)

                submitted_edit = st.form_submit_button("💾 Save Profile Changes")
                if submitted_edit:
                    tol_lbl = "Conservative" if e_score <= 3 else ("Moderate" if e_score <= 6 else "Aggressive")
                    notes_edit_val = e_persona_notes.strip() if e_persona_notes.strip() else None

                    updated_client = ClientProfile(
                        id=current_client.id,
                        name=e_name,
                        age=int(e_age),
                        city=e_city,
                        monthly_income=float(e_income),
                        monthly_expenses=float(e_expenses),
                        existing_savings=float(e_savings),
                        existing_liabilities=float(e_debt),
                        number_of_dependants=int(e_deps),
                        income_stability=e_stability,
                        emergency_fund_months=float(e_emg),
                        investment_horizon_years=float(e_horizon),
                        financial_goals=current_client.financial_goals,
                        behavioral_risk_score=int(e_score),
                        risk_tolerance_label=tol_lbl,
                        expected_major_expenses=float(e_major),
                        is_persona=current_client.is_persona,
                        persona_notes=notes_edit_val,
                        assumptions_made=current_client.assumptions_made
                    )
                    save_custom_client(updated_client)
                    st.session_state["profile_created_success"] = f"Profile & Problem Statement Context for '{e_name}' updated successfully!"
                    st.rerun()
