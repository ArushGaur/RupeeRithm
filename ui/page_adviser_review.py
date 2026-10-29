"""
Page 7: Fiduciary Adviser Review & Human-in-the-Loop Sign-Off.
Displays proposed investment plan, client risk profile, calculation assumptions,
suitability guardrail evaluation, and enables the registered adviser to
Approve, Reject, or Request Changes with full audit log persistence.
"""

import streamlit as st
import pandas as pd
from core.approval import get_all_plans, update_plan_status, get_audit_trail
from core.client import get_all_clients
from core.suitability import evaluate_plan_suitability

def render_adviser_review_page():
    st.title("⚖️ Fiduciary Review & Human-in-the-Loop Approval")
    st.markdown(
        "**SEBI Regulatory Guardrail**: Every client recommendation must enter a pending-review state. "
        "Automated suitability checks assist the adviser, but **only an explicit human adviser decision can approve a plan.**"
    )

    plans = get_all_plans()
    clients = get_all_clients()

    if not plans:
        st.info("No plans currently exist in the database.")
        return

    plan_options = [f"{p.plan_id} — {p.client_name} ({p.goal_name}) [{p.status}]" for p in plans]
    selected_idx = st.selectbox("Select Plan to Review:", range(len(plans)), format_func=lambda i: plan_options[i])
    plan = plans[selected_idx]
    client = clients.get(plan.client_id)

    # Current Status Banner
    status_colors = {
        "Pending Review": "#F59E0B",
        "Approved": "#10B981",
        "Rejected": "#EF4444",
        "Changes Requested": "#8B5CF6"
    }
    st.markdown(f"""
    <div style="background-color: {status_colors.get(plan.status, '#F59E0B')}; color: white; padding: 12px 18px; border-radius: 8px; font-weight: 600; font-size: 16px; margin-bottom: 20px;">
        STATUS: {plan.status.upper()} — Plan ID: {plan.plan_id}
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.subheader("📋 Proposed Plan Specifications")
        st.write(f"**Client**: {plan.client_name}")
        st.write(f"**Goal**: {plan.goal_name}")
        st.write(f"**Target Corpus**: ₹{plan.target_corpus:,.0f} | **Time Horizon**: {plan.years_remaining:.1f} years")
        st.write(f"**Required Monthly SIP**: ₹{plan.required_monthly_sip:,.0f}/month")
        
        st.markdown("#### Proposed Asset Allocation")
        st.write(f"- Equity: **{plan.asset_allocation.get('equity_pct', 0)}%**")
        st.write(f"- Debt: **{plan.asset_allocation.get('debt_pct', 0)}%**")
        st.write(f"- Liquid/Cash: **{plan.asset_allocation.get('liquid_pct', 0)}%**")

        st.markdown("#### Shortlisted Direct Mutual Funds")
        st.dataframe(pd.DataFrame(plan.recommended_schemes), use_container_width=True, hide_index=True)

    with col_r:
        st.subheader("🛡️ Automated Suitability Check Engine")
        
        # Run live suitability check if client profile is available
        if client:
            # find corresponding goal
            goal_obj = next((g for g in client.financial_goals if g.name == plan.goal_name), None)
            if not goal_obj and client.financial_goals:
                goal_obj = client.financial_goals[0]
                
            if goal_obj:
                s_report = evaluate_plan_suitability(
                    client=client,
                    goal=goal_obj,
                    proposed_equity_pct=float(plan.asset_allocation.get("equity_pct", 0)),
                    proposed_debt_pct=float(plan.asset_allocation.get("debt_pct", 0)),
                    proposed_schemes=plan.recommended_schemes,
                    user_prompt_flags=["high returns fast"] if "trader" in plan.client_id else None
                )

                if s_report.warnings:
                    for w in s_report.warnings:
                        badge_color = "#EF4444" if w.severity == "CRITICAL_BLOCKER" else ("#F97316" if w.severity == "HIGH_RISK" else "#EAB308")
                        st.markdown(f"""
                        <div style="border-left: 4px solid {badge_color}; background-color: #FFF7ED; padding: 10px; margin-bottom: 12px; border-radius: 4px;">
                            <span style="background-color: {badge_color}; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: bold;">{w.severity}</span>
                            <strong style="color: #9A3412; font-size: 13px;"> {w.rule_name}</strong><br>
                            <span style="font-size: 12px; color: #1E293B;"><strong>Issue:</strong> {w.issue_detected}</span><br>
                            <span style="font-size: 11px; color: #475569;"><strong>Why it matters:</strong> {w.why_it_matters}</span><br>
                            <span style="font-size: 11px; color: #047857;"><strong>Action:</strong> {w.required_review_action}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ All deterministic suitability checks passed. Zero guardrail violations detected.")
                    
                st.caption(f"ℹ️ {s_report.disclaimer}")

    st.markdown("---")

    # Human Adviser Action Station
    st.subheader("✍️ Registered Adviser Decision & Audit Sign-Off")
    
    with st.form(f"adviser_decision_form_{plan.plan_id}"):
        st.markdown("Select fiduciary action:")
        action_choice = st.radio(
            "Fiduciary Action:",
            ["Approve", "Request Changes", "Reject"],
            horizontal=True
        )
        adv_name = st.text_input("Adviser Name / SEBI Reg. No.:", value="Adviser Rahul Sharma (SEBI Reg: INA000084920)")
        adv_notes = st.text_area(
            "Clinical Advisory Rationale & Client-Specific Notes:",
            value=plan.adviser_notes if plan.adviser_notes else "Verified client risk capacity, cash flow surplus, and goal horizon. Approved for implementation."
        )

        submit_decision = st.form_submit_button("🔒 Submit Fiduciary Sign-Off & Commit to Audit Trail", type="primary")

        if submit_decision:
            updated = update_plan_status(
                plan_id=plan.plan_id,
                action=action_choice,
                adviser_name=adv_name,
                adviser_notes=adv_notes
            )
            st.success(f"Plan {plan.plan_id} marked as '{updated.status}' by {adv_name}! Event logged to immutable audit file.")
            st.rerun()

    # Audit Trail History for this plan
    st.markdown("---")
    st.subheader(f"📜 Audit Trail for Plan {plan.plan_id}")
    all_events = get_audit_trail()
    plan_events = [e for e in all_events if e.get("plan_id") == plan.plan_id]
    if plan_events:
        for ev in reversed(plan_events):
            st.markdown(f"- **{ev['timestamp']}** — `{ev['event_type']}`: Status changed from `{ev['old_status']}` to `{ev['new_status']}` by **{ev['adviser_name']}**. *Notes: {ev['adviser_notes']}*")
    else:
        st.caption("No prior decisions recorded for this plan.")

