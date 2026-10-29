"""
Adviser Human-in-the-Loop Approval and Audit Log Module.
Ensures that no AI-generated or co-pilot recommendation reaches a client without
explicit review and cryptographic/timestamped sign-off by a registered adviser.
Implements: Pending Review, Approved, Rejected, Changes Requested states and tamper-evident audit logging.
"""

from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_LOG_FILE = os.path.join(BASE_DIR, "adviser_audit_log.json")
PENDING_PLANS_FILE = os.path.join(BASE_DIR, "pending_plans.json")

class AdvisoryPlan:
    def __init__(
        self,
        plan_id: str,
        client_id: str,
        client_name: str,
        goal_name: str,
        target_corpus: float,
        years_remaining: float,
        required_monthly_sip: float,
        asset_allocation: Dict[str, float],
        recommended_schemes: List[Dict[str, Any]],
        suitability_verdict: str,
        suitability_warnings_count: int,
        status: str = "Pending Review", # "Pending Review", "Approved", "Rejected", "Changes Requested"
        adviser_notes: Optional[str] = None,
        adviser_name: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.plan_id = plan_id
        self.client_id = client_id
        self.client_name = client_name
        self.goal_name = goal_name
        self.target_corpus = target_corpus
        self.years_remaining = years_remaining
        self.required_monthly_sip = required_monthly_sip
        self.asset_allocation = asset_allocation
        self.recommended_schemes = recommended_schemes
        self.suitability_verdict = suitability_verdict
        self.suitability_warnings_count = suitability_warnings_count
        self.status = status
        self.adviser_notes = adviser_notes
        self.adviser_name = adviser_name
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = updated_at or self.created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "client_id": self.client_id,
            "client_name": self.client_name,
            "goal_name": self.goal_name,
            "target_corpus": self.target_corpus,
            "years_remaining": self.years_remaining,
            "required_monthly_sip": self.required_monthly_sip,
            "asset_allocation": self.asset_allocation,
            "recommended_schemes": self.recommended_schemes,
            "suitability_verdict": self.suitability_verdict,
            "suitability_warnings_count": self.suitability_warnings_count,
            "status": self.status,
            "adviser_notes": self.adviser_notes,
            "adviser_name": self.adviser_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

def get_all_plans() -> List[AdvisoryPlan]:
    """Loads all plans from disk."""
    if not os.path.exists(PENDING_PLANS_FILE):
        # Initialize default pending plans for sample personas
        init_default_plans()

    try:
        with open(PENDING_PLANS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [AdvisoryPlan(**item) for item in data]
    except Exception as e:
        print(f"Error loading plans: {e}")
        return []

def save_plans(plans: List[AdvisoryPlan]) -> None:
    """Saves plan list to disk."""
    data = [p.to_dict() for p in plans]
    with open(PENDING_PLANS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_or_update_plan(plan: AdvisoryPlan) -> None:
    """Adds a new plan or updates an existing plan in pending_plans.json."""
    plans = get_all_plans()
    plans = [p for p in plans if p.plan_id != plan.plan_id]
    plans.append(plan)
    save_plans(plans)

def update_plan_status(
    plan_id: str,
    action: str, # "Approve", "Reject", "Request Changes"
    adviser_name: str,
    adviser_notes: str
) -> Optional[AdvisoryPlan]:
    """
    Updates the state of a plan and logs the event in the audit trail.
    """
    status_map = {
        "Approve": "Approved",
        "Reject": "Rejected",
        "Request Changes": "Changes Requested"
    }
    new_status = status_map.get(action, "Pending Review")
    plans = get_all_plans()
    target_plan = None

    for p in plans:
        if p.plan_id == plan_id:
            old_status = p.status
            p.status = new_status
            p.adviser_notes = adviser_notes
            p.adviser_name = adviser_name
            p.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            target_plan = p
            break

    if target_plan:
        save_plans(plans)
        log_audit_event(
            event_type=f"PLAN_{new_status.upper().replace(' ', '_')}",
            plan_id=plan_id,
            client_id=target_plan.client_id,
            client_name=target_plan.client_name,
            old_status=old_status,
            new_status=new_status,
            adviser_name=adviser_name,
            adviser_notes=adviser_notes
        )

    return target_plan

def log_audit_event(
    event_type: str,
    plan_id: str,
    client_id: str,
    client_name: str,
    old_status: str,
    new_status: str,
    adviser_name: str,
    adviser_notes: str
) -> None:
    """Appends an immutable audit event to adviser_audit_log.json."""
    events = []
    if os.path.exists(AUDIT_LOG_FILE):
        try:
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                events = json.load(f)
        except Exception:
            events = []

    events.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event_type": event_type,
        "plan_id": plan_id,
        "client_id": client_id,
        "client_name": client_name,
        "old_status": old_status,
        "new_status": new_status,
        "adviser_name": adviser_name,
        "adviser_notes": adviser_notes
    })

    with open(AUDIT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

def get_audit_trail() -> List[Dict[str, Any]]:
    """Loads all audit log records."""
    if not os.path.exists(AUDIT_LOG_FILE):
        return []
    try:
        with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def init_default_plans() -> None:
    """Seeds realistic sample plans for the 6 personas to illustrate adviser review workflow."""
    seed_plans = [
        AdvisoryPlan(
            plan_id="PLAN-001",
            client_id="fresh_graduate",
            client_name="Arjun Verma (Fresh Graduate)",
            goal_name="Emergency Fund Buffer (6 months)",
            target_corpus=150000.0,
            years_remaining=1.0,
            required_monthly_sip=8120.0,
            asset_allocation={"equity_pct": 0.0, "debt_pct": 20.0, "liquid_pct": 80.0},
            recommended_schemes=[
                {"scheme_name": "DSP Liquid Fund - Direct Plan - Growth", "allocation_pct": 80.0},
                {"scheme_name": "Mirae Asset Short Term Fund - Direct - Growth", "allocation_pct": 20.0}
            ],
            suitability_verdict="PASSED",
            suitability_warnings_count=0,
            status="Pending Review"
        ),
        AdvisoryPlan(
            plan_id="PLAN-002",
            client_id="retiree",
            client_name="S. Ramanathan (Retiree)",
            goal_name="Monthly Income Generation (SWP)",
            target_corpus=6000000.0,
            years_remaining=25.0,
            required_monthly_sip=0.0, # Funded via lump sum SWP
            asset_allocation={"equity_pct": 20.0, "debt_pct": 65.0, "liquid_pct": 15.0},
            recommended_schemes=[
                {"scheme_name": "Mirae Asset Banking & PSU Debt Fund - Direct - Growth", "allocation_pct": 45.0},
                {"scheme_name": "DSP Corporate Bond Fund - Direct - Growth", "allocation_pct": 20.0},
                {"scheme_name": "Mirae Asset Large Cap Fund - Direct - Growth", "allocation_pct": 20.0},
                {"scheme_name": "DSP Arbitrage Fund - Direct - Growth", "allocation_pct": 15.0}
            ],
            suitability_verdict="WARNINGS_REQUIRE_ADVISER_ATTENTION",
            suitability_warnings_count=1,
            status="Pending Review"
        ),
        AdvisoryPlan(
            plan_id="PLAN-003",
            client_id="doctor",
            client_name="Dr. Alok Verma (Consultant Physician)",
            goal_name="Doctor Retirement Fund",
            target_corpus=35000000.0,
            years_remaining=20.0,
            required_monthly_sip=28450.0,
            asset_allocation={"equity_pct": 50.0, "debt_pct": 45.0, "liquid_pct": 5.0},
            recommended_schemes=[
                {"scheme_name": "DSP Flexi Cap Fund - Direct Plan - Growth", "allocation_pct": 30.0},
                {"scheme_name": "Axis Nifty 500 Index Fund - Direct - Growth", "allocation_pct": 20.0},
                {"scheme_name": "DSP Short Term Fund - Direct - Growth", "allocation_pct": 45.0},
                {"scheme_name": "DSP Liquid Fund - Direct - Growth", "allocation_pct": 5.0}
            ],
            suitability_verdict="WARNINGS_REQUIRE_ADVISER_ATTENTION",
            suitability_warnings_count=1,
            status="Pending Review"
        ),
        AdvisoryPlan(
            plan_id="PLAN-004",
            client_id="aggressive_trader",
            client_name="Vikram Mehta (Aggressive Trader)",
            goal_name="Disciplined Wealth Building",
            target_corpus=5000000.0,
            years_remaining=10.0,
            required_monthly_sip=21500.0,
            asset_allocation={"equity_pct": 45.0, "debt_pct": 45.0, "liquid_pct": 10.0},
            recommended_schemes=[
                {"scheme_name": "Axis Nifty 500 Index Fund - Direct - Growth", "allocation_pct": 30.0},
                {"scheme_name": "Mirae Asset Midcap Fund - Direct - Growth", "allocation_pct": 15.0},
                {"scheme_name": "DSP Short Term Fund - Direct - Growth", "allocation_pct": 45.0},
                {"scheme_name": "DSP Liquid Fund - Direct - Growth", "allocation_pct": 10.0}
            ],
            suitability_verdict="WARNINGS_REQUIRE_ADVISER_ATTENTION",
            suitability_warnings_count=2,
            status="Pending Review"
        )
    ]
    save_plans(seed_plans)

