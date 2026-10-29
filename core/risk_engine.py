"""
Transparent, Configurable Risk Profiling Engine.
Separates Risk Capacity (Financial Ability) from Risk Tolerance (Psychological Willingness).
Defines explicit, deterministic rules for resolving conflicts between the two.
Compliant with SEBI RIA Guidelines.
"""

from typing import Dict, Any, List, Tuple
from core.client import ClientProfile

class RiskAssessmentResult:
    def __init__(
        self,
        capacity_score: float, # 0 to 100
        capacity_tier: str,   # Low, Moderate, High, Very High
        tolerance_score: float, # 0 to 100
        tolerance_tier: str,  # Conservative, Moderate, Aggressive
        final_recommended_tier: str, # Conservative, Moderately Conservative, Moderate, Moderately Aggressive, Aggressive
        max_equity_allocation_pct: float,
        conflict_detected: bool,
        conflict_type: str,
        conflict_reasoning: str,
        capacity_breakdown: Dict[str, Any],
        tolerance_breakdown: Dict[str, Any],
        recommended_actions: List[str]
    ):
        self.capacity_score = capacity_score
        self.capacity_tier = capacity_tier
        self.tolerance_score = tolerance_score
        self.tolerance_tier = tolerance_tier
        self.final_recommended_tier = final_recommended_tier
        self.max_equity_allocation_pct = max_equity_allocation_pct
        self.conflict_detected = conflict_detected
        self.conflict_type = conflict_type
        self.conflict_reasoning = conflict_reasoning
        self.capacity_breakdown = capacity_breakdown
        self.tolerance_breakdown = tolerance_breakdown
        self.recommended_actions = recommended_actions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capacity_score": round(self.capacity_score, 1),
            "capacity_tier": self.capacity_tier,
            "tolerance_score": round(self.tolerance_score, 1),
            "tolerance_tier": self.tolerance_tier,
            "final_recommended_tier": self.final_recommended_tier,
            "max_equity_allocation_pct": round(self.max_equity_allocation_pct, 1),
            "conflict_detected": self.conflict_detected,
            "conflict_type": self.conflict_type,
            "conflict_reasoning": self.conflict_reasoning,
            "capacity_breakdown": self.capacity_breakdown,
            "tolerance_breakdown": self.tolerance_breakdown,
            "recommended_actions": self.recommended_actions
        }

def calculate_risk_capacity(client: ClientProfile) -> Tuple[float, str, Dict[str, Any]]:
    """
    Evaluates financial ability to endure loss based on:
    1. Net Monthly Savings Rate (Savings / Income): 25 pts
    2. Emergency Liquidity Coverage (months of expenses in cash): 20 pts
    3. Debt-to-Asset / Liability Burden: 20 pts
    4. Investment Horizon: 20 pts
    5. Dependant Load & Income Stability: 15 pts
    Total: 100 points
    """
    pts_savings = 0.0
    pts_liquidity = 0.0
    pts_debt = 0.0
    pts_horizon = 0.0
    pts_stability = 0.0

    # 1. Savings Rate (Monthly Income - Monthly Expenses) / Monthly Income
    monthly_surplus = max(0.0, client.monthly_income - client.monthly_expenses)
    savings_rate = monthly_surplus / client.monthly_income if client.monthly_income > 0 else 0.0
    if savings_rate >= 0.50:
        pts_savings = 25.0
    elif savings_rate >= 0.35:
        pts_savings = 20.0
    elif savings_rate >= 0.20:
        pts_savings = 15.0
    elif savings_rate >= 0.10:
        pts_savings = 10.0
    else:
        pts_savings = 3.0

    # 2. Emergency Fund Runway
    if client.emergency_fund_months >= 6.0:
        pts_liquidity = 20.0
    elif client.emergency_fund_months >= 3.0:
        pts_liquidity = 14.0
    elif client.emergency_fund_months >= 1.0:
        pts_liquidity = 7.0
    else:
        pts_liquidity = 2.0

    # 3. Debt to Assets / Liabilities
    total_assets = max(1.0, client.existing_savings)
    debt_ratio = client.existing_liabilities / total_assets
    if client.existing_liabilities == 0:
        pts_debt = 20.0
    elif debt_ratio <= 0.3:
        pts_debt = 16.0
    elif debt_ratio <= 0.7:
        pts_debt = 10.0
    elif debt_ratio <= 1.5:
        pts_debt = 5.0
    else:
        pts_debt = 0.0

    # 4. Investment Horizon (years)
    if client.investment_horizon_years >= 12:
        pts_horizon = 20.0
    elif client.investment_horizon_years >= 7:
        pts_horizon = 15.0
    elif client.investment_horizon_years >= 4:
        pts_horizon = 10.0
    elif client.investment_horizon_years >= 2:
        pts_horizon = 5.0
    else:
        pts_horizon = 2.0

    # 5. Stability & Dependants
    # Age factor: retirees have lower capacity to replace capital from future human earnings
    age_penalty = 0.0
    if client.age >= 65:
        age_penalty = 6.0
    elif client.age >= 55:
        age_penalty = 3.0

    stability_bonus = 0.0
    if client.income_stability == "Stable":
        stability_bonus = 10.0
    elif client.income_stability == "Fixed Pension":
        stability_bonus = 8.0
    elif client.income_stability == "Fluctuating":
        stability_bonus = 5.0
    else: # High Volatility
        stability_bonus = 1.0

    dep_score = max(0.0, 5.0 - (client.number_of_dependants * 1.5))
    pts_stability = max(0.0, stability_bonus + dep_score - age_penalty)

    total_capacity = min(100.0, pts_savings + pts_liquidity + pts_debt + pts_horizon + pts_stability)

    if total_capacity >= 75.0:
        tier = "High"
    elif total_capacity >= 55.0:
        tier = "Moderate"
    elif total_capacity >= 35.0:
        tier = "Low"
    else:
        tier = "Very Low"

    breakdown = {
        "savings_rate_score": round(pts_savings, 1),
        "savings_rate_pct": round(savings_rate * 100, 1),
        "liquidity_score": round(pts_liquidity, 1),
        "emergency_months": client.emergency_fund_months,
        "debt_burden_score": round(pts_debt, 1),
        "debt_to_assets": round(debt_ratio, 2),
        "horizon_score": round(pts_horizon, 1),
        "horizon_years": client.investment_horizon_years,
        "stability_and_dependants_score": round(pts_stability, 1),
        "total_capacity_score": round(total_capacity, 1),
        "tier": tier
    }
    return total_capacity, tier, breakdown

def calculate_risk_tolerance(client: ClientProfile) -> Tuple[float, str, Dict[str, Any]]:
    """
    Evaluates psychological willingness to bear volatility based on questionnaire score (1-10).
    Scale: 0 to 100
    """
    score = (client.behavioral_risk_score / 10.0) * 100.0
    if score >= 70.0:
        tier = "Aggressive"
    elif score >= 40.0:
        tier = "Moderate"
    else:
        tier = "Conservative"

    breakdown = {
        "raw_behavioral_score": client.behavioral_risk_score,
        "tolerance_percentage": round(score, 1),
        "tier": tier,
        "stated_label": client.risk_tolerance_label
    }
    return score, tier, breakdown

def assess_client_risk(client: ClientProfile) -> RiskAssessmentResult:
    """
    Transparent SEBI RIA rule engine for resolving conflicts between Capacity and Tolerance.
    Golden Rule: Risk Capacity forms the safety ceiling; Risk Tolerance guides behavioral comfort.
    The co-pilot ALWAYS caps equity allocation to the lower of Capacity and Tolerance.
    """
    cap_score, cap_tier, cap_breakdown = calculate_risk_capacity(client)
    tol_score, tol_tier, tol_breakdown = calculate_risk_tolerance(client)

    conflict_detected = False
    conflict_type = "None"
    conflict_reasoning = ""
    actions = []

    # Map tiers to ordinal ranks: 1=Low/Conservative, 2=Moderate, 3=High/Aggressive
    cap_rank = {"Very Low": 1, "Low": 1, "Moderate": 2, "High": 3}[cap_tier]
    tol_rank = {"Conservative": 1, "Moderate": 2, "Aggressive": 3}[tol_tier]

    if tol_rank > cap_rank:
        # Case A: High Tolerance, Low/Moderate Capacity (e.g. Aggressive Trader or young indebted couple)
        conflict_detected = True
        conflict_type = "Tolerance Exceeds Capacity (Overconfidence / High Risk of Ruin)"
        conflict_reasoning = (
            f"Client expresses {tol_tier} risk tolerance, but objective financial capacity is only {cap_tier} "
            f"(Capacity Score: {cap_score:.1f}/100 vs Tolerance Score: {tol_score:.1f}/100). "
            f"In accordance with SEBI fiduciary standards, risk capacity must serve as the ceiling. "
            f"Adviser must prevent overexposure to volatile equity/derivatives that could cause permanent capital loss."
        )
        actions.append("Cap equity allocation to capacity limit.")
        actions.append("Counsel client on the difference between emotional risk appetite and financial buffer.")
        actions.append("Mandate 6-month emergency reserve before increasing discretionary risk.")
        
        final_tier = "Moderate" if cap_tier == "Moderate" else "Conservative"
        max_equity = 45.0 if cap_tier == "Moderate" else 25.0

    elif cap_rank > tol_rank:
        # Case B: Capacity Exceeds Tolerance (e.g. Dr. Alok Verma, Patna - high income, ₹50L cash, but risk-averse)
        conflict_detected = True
        conflict_type = "Capacity Exceeds Tolerance (Under-invested / Inflation Risk)"
        conflict_reasoning = (
            f"Client has {cap_tier} financial capacity (Score: {cap_score:.1f}/100), but self-reports "
            f"{tol_tier} risk tolerance (Score: {tol_score:.1f}/100). "
            f"While the client's strong cash flow and zero debt can comfortably absorb market drawdowns, "
            f"their behavioral aversion to volatility poses severe long-term inflation risk if kept in cash/FDs."
        )
        if tol_tier == "Conservative":
            actions.append("Do NOT force an immediate high-equity portfolio, as panic selling during a correction is likely.")
            actions.append("Recommend a stepped Systematic Transfer Plan (STP) or Conservative Hybrid Fund.")
            actions.append("Demonstrate historical post-tax real return comparisons between FDs and conservative hybrid funds.")
            final_tier = "Moderately Conservative"
            max_equity = 35.0
        else: # Moderate tolerance with High capacity (e.g. young professional with long horizon)
            actions.append("Proceed with balanced allocation suited for moderate tolerance (55% equity max).")
            actions.append("Educate client on gradual equity exposure via systematic SIP.")
            final_tier = "Moderate"
            max_equity = 55.0

    else:
        # Aligned
        conflict_detected = False
        conflict_type = "Aligned"
        conflict_reasoning = (
            f"Risk capacity ({cap_tier}) and psychological tolerance ({tol_tier}) are well-aligned. "
            f"Portfolio asset allocation can proceed without conflict damping."
        )
        if cap_tier == "High":
            final_tier = "Aggressive"
            max_equity = 75.0
        elif cap_tier == "Moderate":
            final_tier = "Moderate"
            max_equity = 55.0
        else:
            final_tier = "Conservative"
            max_equity = 25.0
        actions.append("Proceed with standard goal-based asset allocation matching client profile.")

    # Specific override for senior citizens / retirees (e.g. S. Ramanathan, Age 68)
    if client.age >= 65 and max_equity > 30.0:
        max_equity = 25.0
        conflict_detected = True
        conflict_type = "Senior Citizen Capital Preservation Rule"
        conflict_reasoning += (
            f" [Senior Citizen Override]: Client is {client.age} years old in post-retirement phase. "
            f"SEBI suitability rules require prioritizing regular income generation and capital preservation over capital appreciation."
        )
        actions.append("Prioritize debt, arbitrage, and systematic withdrawal plan (SWP) for pension supplement.")

    return RiskAssessmentResult(
        capacity_score=cap_score,
        capacity_tier=cap_tier,
        tolerance_score=tol_score,
        tolerance_tier=tol_tier,
        final_recommended_tier=final_tier,
        max_equity_allocation_pct=max_equity,
        conflict_detected=conflict_detected,
        conflict_type=conflict_type,
        conflict_reasoning=conflict_reasoning,
        capacity_breakdown=cap_breakdown,
        tolerance_breakdown=tol_breakdown,
        recommended_actions=actions
    )

