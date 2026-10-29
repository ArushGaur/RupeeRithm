"""
Client Profile and Persona Management Module.
Compliant with SEBI Investment Adviser Regulations regarding Client Profiling.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import json
import os

class FinancialGoal(BaseModel):
    goal_id: str
    name: str
    target_corpus: float = Field(..., description="Target cost in today's money (INR)")
    years_remaining: float = Field(..., description="Years until goal deadline")
    existing_allocated: float = Field(0.0, description="Existing savings earmarked for this goal (INR)")
    inflation_rate: float = Field(0.06, description="Annual inflation assumption (e.g. 0.06 for 6%)")
    expected_return: float = Field(0.12, description="Assumed nominal investment return (e.g. 0.12 for 12%)")
    priority: str = Field("High", description="High / Medium / Low")

class ClientProfile(BaseModel):
    id: str
    name: str
    age: int
    city: str
    monthly_income: float
    monthly_expenses: float
    existing_savings: float
    existing_liabilities: float
    number_of_dependants: int
    income_stability: str = Field("Stable", description="Stable / Fluctuating / Fixed Pension / High Volatility")
    emergency_fund_months: float = Field(0.0, description="Months of expenses covered in liquid savings")
    investment_horizon_years: float = Field(..., description="Overall investment time horizon in years")
    financial_goals: List[FinancialGoal] = []
    
    # Behavioral Risk Tolerance (psychological questionnaire)
    # Scale 1-10: 1-3 Conservative, 4-6 Moderate, 7-10 Aggressive
    behavioral_risk_score: int = Field(5, ge=1, le=10)
    risk_tolerance_label: str = Field("Moderate", description="Conservative / Moderate / Aggressive")
    expected_major_expenses: float = Field(0.0, description="Anticipated major expense in next 1-2 years")
    is_persona: bool = False
    persona_notes: Optional[str] = None
    assumptions_made: List[str] = []

# The Six Standard Test Personas from Problem Statement PS-04
SAMPLE_PERSONAS: Dict[str, ClientProfile] = {
    "fresh_graduate": ClientProfile(
        id="fresh_graduate",
        name="Arjun Verma (Fresh Graduate)",
        age=23,
        city="Bengaluru",
        monthly_income=55000.0,
        monthly_expenses=25000.0,
        existing_savings=50000.0,
        existing_liabilities=0.0,
        number_of_dependants=0,
        income_stability="Stable",
        emergency_fund_months=2.0,
        investment_horizon_years=15.0,
        behavioral_risk_score=6,
        risk_tolerance_label="Moderate",
        expected_major_expenses=0.0,
        is_persona=True,
        persona_notes="Age 23; ₹55k/month take-home; no dependants. Goal: Emergency fund, then long-term wealth.",
        assumptions_made=[
            "Monthly expenses assumed at ₹25k/month living in Bengaluru.",
            "Initial savings assumed at ₹50,000 in bank savings account.",
            "Initial emergency fund is 2 months (₹50k); needs building to 6 months (₹1.5 Lakh)."
        ],
        financial_goals=[
            FinancialGoal(
                goal_id="g1_emg",
                name="Emergency Fund Buffer (6 months)",
                target_corpus=150000.0,
                years_remaining=1.0,
                existing_allocated=50000.0,
                inflation_rate=0.05,
                expected_return=0.065, # Liquid / Arbitrage fund
                priority="High"
            ),
            FinancialGoal(
                goal_id="g1_wealth",
                name="Long-term Wealth Creation",
                target_corpus=2500000.0,
                years_remaining=10.0,
                existing_allocated=0.0,
                inflation_rate=0.06,
                expected_return=0.12, # Equity Diversified
                priority="Medium"
            )
        ]
    ),
    "young_couple": ClientProfile(
        id="young_couple",
        name="Rohit & Neha (Young Couple)",
        age=31,
        city="Pune",
        monthly_income=160000.0,
        monthly_expenses=90000.0, # including ₹40k home-loan EMI
        existing_savings=500000.0,
        existing_liabilities=3500000.0, # Home loan outstanding
        number_of_dependants=1, # 1 infant child
        income_stability="Stable",
        emergency_fund_months=3.0,
        investment_horizon_years=15.0,
        behavioral_risk_score=7,
        risk_tolerance_label="Aggressive",
        expected_major_expenses=100000.0,
        is_persona=True,
        persona_notes="Age 31; Dual income; home-loan EMI; 1 dependant child. Goal: Child's higher education in 15 years.",
        assumptions_made=[
            "Dual income combined take-home assumed at ₹1,60,000/month.",
            "Home loan EMI assumed at ₹40,000/month (total expenses ₹90,000/month).",
            "Child higher education target estimated at ₹35,000,000 in today's fees."
        ],
        financial_goals=[
            FinancialGoal(
                goal_id="g2_edu",
                name="Child's Higher Education",
                target_corpus=3500000.0,
                years_remaining=15.0,
                existing_allocated=300000.0,
                inflation_rate=0.08, # Higher education inflation is typically 8-10%
                expected_return=0.12,
                priority="High"
            )
        ]
    ),
    "business_owner": ClientProfile(
        id="business_owner",
        name="Kishore Shah (Small Business Owner)",
        age=44,
        city="Surat",
        monthly_income=250000.0, # Average across cyclical business
        monthly_expenses=120000.0,
        existing_savings=4500000.0, # High cash holdings ₹30L in savings/current accounts
        existing_liabilities=1000000.0, # Working capital credit line
        number_of_dependants=3, # Spouse, 2 teenage school children
        income_stability="Fluctuating",
        emergency_fund_months=12.0, # Needs 12-month buffer due to irregular cash flows
        investment_horizon_years=14.0,
        behavioral_risk_score=5,
        risk_tolerance_label="Moderate",
        expected_major_expenses=500000.0,
        is_persona=True,
        persona_notes="Age 44; Irregular income; high cash holdings. Goal: Retirement at age 58.",
        assumptions_made=[
            "Average monthly net business drawings assumed at ₹2,50,000 with seasonal swings.",
            "₹30 Lakh currently idling in low-yield bank savings/current accounts.",
            "Retirement target age 58 (14 years remaining)."
        ],
        financial_goals=[
            FinancialGoal(
                goal_id="g3_retire",
                name="Retirement Corpus at Age 58",
                target_corpus=25000000.0,
                years_remaining=14.0,
                existing_allocated=2000000.0,
                inflation_rate=0.06,
                expected_return=0.11,
                priority="High"
            )
        ]
    ),
    "doctor": ClientProfile(
        id="doctor",
        name="Dr. Alok Verma (Consultant Physician)",
        age=38,
        city="Patna",
        monthly_income=350000.0,
        monthly_expenses=100000.0,
        existing_savings=6000000.0, # Under-invested: ₹50L sitting in bank fixed deposits
        existing_liabilities=0.0,
        number_of_dependants=3, # Spouse and 2 elderly dependent parents
        income_stability="Stable",
        emergency_fund_months=10.0,
        investment_horizon_years=20.0,
        behavioral_risk_score=3,
        risk_tolerance_label="Conservative", # Self-reported risk-averse
        expected_major_expenses=1500000.0,
        is_persona=True,
        persona_notes="Age 38; High income; under-invested; risk-averse. Goal: Retirement + parents' medical corpus.",
        assumptions_made=[
            "Stable monthly net consultation & hospital income of ₹3,50,000.",
            "Under-invested: ₹50 Lakh idling in 6.5% bank FDs earning negative real return after 30% tax bracket.",
            "Flag: Capacity is Very High, but stated Tolerance is Conservative. Requires conflict resolution."
        ],
        financial_goals=[
            FinancialGoal(
                goal_id="g4_parents_med",
                name="Parents' Medical Emergency Reserve",
                target_corpus=3000000.0,
                years_remaining=3.0,
                existing_allocated=1500000.0,
                inflation_rate=0.09, # Healthcare inflation in India ~9-12%
                expected_return=0.075, # Conservative Hybrid / Arbitrage / Short Debt
                priority="High"
            ),
            FinancialGoal(
                goal_id="g4_retire",
                name="Doctor Retirement Fund",
                target_corpus=35000000.0,
                years_remaining=20.0,
                existing_allocated=2000000.0,
                inflation_rate=0.06,
                expected_return=0.10,
                priority="Medium"
            )
        ]
    ),
    "retiree": ClientProfile(
        id="retiree",
        name="S. Ramanathan (Retired Central Govt PSU)",
        age=68,
        city="Chennai",
        monthly_income=35000.0, # Guaranteed monthly pension
        monthly_expenses=55000.0, # Monthly shortfall of ₹20k needed from corpus
        existing_savings=8000000.0, # ₹80 Lakh lump sum retirement corpus
        existing_liabilities=0.0,
        number_of_dependants=1, # Spouse (age 65)
        income_stability="Fixed Pension",
        emergency_fund_months=12.0,
        investment_horizon_years=25.0, # Life expectancy to age 93
        behavioral_risk_score=2,
        risk_tolerance_label="Conservative",
        expected_major_expenses=300000.0,
        is_persona=True,
        persona_notes="Age 68; ₹80 lakh corpus; pension ₹35k/mo. Goal: Monthly income for 25 years. Capital preservation essential.",
        assumptions_made=[
            "Retirement corpus is ₹80,00,000.",
            "Monthly living expenditure ₹55,000 with ₹35,000 indexed pension (net deficit ₹20,000/month).",
            "Guardrail: Must reject high-equity or small-cap allocations; focus on SWP from Conservative Debt / Arbitrage / Hybrid."
        ],
        financial_goals=[
            FinancialGoal(
                goal_id="g5_swp",
                name="Monthly Income Generation (SWP)",
                target_corpus=6000000.0,
                years_remaining=25.0,
                existing_allocated=6000000.0,
                inflation_rate=0.06,
                expected_return=0.075, # Conservative Debt / Multi-Asset / SWP
                priority="High"
            ),
            FinancialGoal(
                goal_id="g5_contingency",
                name="Senior Citizen Health Contingency",
                target_corpus=2000000.0,
                years_remaining=5.0,
                existing_allocated=2000000.0,
                inflation_rate=0.08,
                expected_return=0.07,
                priority="High"
            )
        ]
    ),
    "aggressive_trader": ClientProfile(
        id="aggressive_trader",
        name="Vikram Mehta (F&O Trader / Software Engineer)",
        age=29,
        city="Mumbai",
        monthly_income=110000.0,
        monthly_expenses=60000.0,
        existing_savings=200000.0,
        existing_liabilities=300000.0, # Personal loan taken to fund trading margins
        number_of_dependants=0,
        income_stability="High Volatility",
        emergency_fund_months=1.0,
        investment_horizon_years=5.0,
        behavioral_risk_score=10,
        risk_tolerance_label="Aggressive", # Seeks "high returns fast"
        expected_major_expenses=0.0,
        is_persona=True,
        persona_notes="Age 29; recent ₹6 Lakh F&O losses; wants 'high returns fast' (demands 20%+ guaranteed). Co-pilot must handle suitability.",
        assumptions_made=[
            "Monthly salary ₹1,10,000, but has suffered ₹6 Lakh derivative losses over past 12 months.",
            "₹3 Lakh personal loan outstanding.",
            "Guardrail trigger: Disallow guaranteed-return claims; resolve aggressive tolerance vs weak financial capacity."
        ],
        financial_goals=[
            FinancialGoal(
                goal_id="g6_rehab",
                name="Debt Elimination & Emergency Cushion",
                target_corpus=500000.0,
                years_remaining=2.0,
                existing_allocated=100000.0,
                inflation_rate=0.06,
                expected_return=0.07,
                priority="High"
            ),
            FinancialGoal(
                goal_id="g6_wealth",
                name="Disciplined Wealth Building",
                target_corpus=5000000.0,
                years_remaining=10.0,
                existing_allocated=100000.0,
                inflation_rate=0.06,
                expected_return=0.12, # Diversified Direct Mutual Funds (No F&O)
                priority="Medium"
            )
        ]
    )
}

CUSTOM_CLIENTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "clients_custom.json")

def get_all_clients() -> Dict[str, ClientProfile]:
    """Returns all preloaded personas and any persisted custom clients."""
    clients = dict(SAMPLE_PERSONAS)
    if os.path.exists(CUSTOM_CLIENTS_FILE):
        try:
            with open(CUSTOM_CLIENTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    c = ClientProfile(**item)
                    clients[c.id] = c
        except Exception:
            pass
    return clients

def save_custom_client(client: ClientProfile) -> None:
    """Persists a custom client profile to disk."""
    existing = []
    if os.path.exists(CUSTOM_CLIENTS_FILE):
        try:
            with open(CUSTOM_CLIENTS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []
    # Replace or append
    existing = [x for x in existing if x.get("id") != client.id]
    existing.append(client.model_dump())
    with open(CUSTOM_CLIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

