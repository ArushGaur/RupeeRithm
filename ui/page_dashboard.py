"""
Page 1: Executive Dashboard.
Displays high-level operational overview: client count, plans pending review,
suitability alerts, and recent audit activity.
"""

import streamlit as st
import pandas as pd
from core.client import get_all_clients
from core.approval import get_all_plans, get_audit_trail
from core.data_loader import load_amfi_nav_all

def render_dashboard_page():
    st.title("🏛️ Adviser Operational Dashboard")
    st.markdown(
        "**SEBI Registered Investment Adviser Co-pilot** — *Scaling 1 Adviser to 1,000 Clients with Automated Intelligence & Fiduciary Guardrails.*"
    )
    
    clients = get_all_clients()
    plans = get_all_plans()
    audit_events = get_audit_trail()
    amfi_df = load_amfi_nav_all()

    pending_plans = [p for p in plans if p.status == "Pending Review"]
    approved_plans = [p for p in plans if p.status == "Approved"]
    changes_plans = [p for p in plans if p.status == "Changes Requested"]
    total_warnings = sum(p.suitability_warnings_count for p in plans)

    # Top KPI Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Active Client Personas", value=len(clients), delta="6 Standard Test Personas")
    with c2:
        st.metric(label="Plans Pending Review", value=len(pending_plans), delta=f"{len(approved_plans)} Approved", delta_color="normal")
    with c3:
        st.metric(label="Suitability Warnings", value=total_warnings, delta="Requires Fiduciary Check", delta_color="inverse")
    with c4:
        st.metric(label="AMFI Universe Coverage", value=f"{len(amfi_df):,}", delta="Live Snapshot (27-Oct-2026)")

    st.markdown("---")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📋 Priority Plans Awaiting Fiduciary Review")
        if pending_plans:
            plan_data = []
            for p in pending_plans:
                plan_data.append({
                    "Plan ID": p.plan_id,
                    "Client": p.client_name,
                    "Goal": p.goal_name,
                    "Target Corpus": f"₹{p.target_corpus:,.0f}",
                    "Required SIP": f"₹{p.required_monthly_sip:,.0f}/mo",
                    "Suitability Verdict": p.suitability_verdict,
                    "Warnings": p.suitability_warnings_count,
                    "Status": p.status
                })
            df_pending = pd.DataFrame(plan_data)
            st.dataframe(df_pending, use_container_width=True, hide_index=True)
            st.info("💡 Navigate to **Page 7: Adviser Review** to approve, reject, or mandate changes for these plans.")
        else:
            st.success("🎉 All client plans have been reviewed! No pending items in queue.")

        st.subheader("👥 Active Client Personas in Memory")
        persona_rows = []
        for cid, c in clients.items():
            monthly_surplus = max(0.0, c.monthly_income - c.monthly_expenses)
            persona_rows.append({
                "Persona / Client": c.name,
                "Age": c.age,
                "City": c.city,
                "Monthly Income": f"₹{c.monthly_income:,.0f}",
                "Surplus": f"₹{monthly_surplus:,.0f}",
                "Horizon": f"{c.investment_horizon_years:.0f} yrs",
                "Stated Tolerance": c.risk_tolerance_label,
                "Dependants": c.number_of_dependants
            })
        st.dataframe(pd.DataFrame(persona_rows), use_container_width=True, hide_index=True)

    with col_right:
        st.subheader("🛡️ Fiduciary Compliance & System Status")
        st.markdown("""
        <div style="background-color: #F1F5F9; padding: 14px; border-radius: 8px; border-left: 4px solid #1E3A8A; margin-bottom: 15px;">
            <p style="margin: 0; font-size: 13px; font-weight: 600; color: #1E293B;">SEBI RIA Compliance Active</p>
            <p style="margin: 4px 0 0 0; font-size: 12px; color: #475569;">
                Deterministic rules enforce: Direct Plan mandatory filter, return guarantee ban, senior citizen equity caps, and audit trail persistence.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📜 Recent Audit Activity Log")
        if audit_events:
            recent = audit_events[-5:]
            recent.reverse()
            for ev in recent:
                ts = ev.get("timestamp", "")
                etype = ev.get("event_type", "")
                client_n = ev.get("client_name", "")
                adv = ev.get("adviser_name", "Adviser")
                notes = ev.get("adviser_notes", "")
                
                badge_color = "#10B981" if "APPROVED" in etype else ("#EF4444" if "REJECTED" in etype else "#F59E0B")
                st.markdown(f"""
                <div style="border-bottom: 1px solid #E2E8F0; padding: 6px 0; font-size: 12px;">
                    <span style="background-color: {badge_color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">{etype}</span>
                    <strong>{client_n}</strong> by <em>{adv}</em> <span style="color: #64748B;">({ts})</span><br>
                    <span style="color: #334155;">{notes}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No audit events logged yet. Approvals or rejections will be recorded here.")

        st.markdown("#### ⚡ Quick Actions")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("➕ Profile Client", use_container_width=True):
                st.session_state["nav_page"] = "Client Profiles"
                st.rerun()
        with col_b2:
            if st.button("🔍 Explore Funds", use_container_width=True):
                st.session_state["nav_page"] = "Fund Explorer"
                st.rerun()

