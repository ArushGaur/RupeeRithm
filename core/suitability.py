"""
Deterministic Python Suitability Guardrails Engine.
Enforces SEBI-aligned financial advisory safety rules without relying on LLM prompts.
Generates structured, explainable warnings detailing:
1. Issue detected
2. Relevant client / portfolio data
3. Specific rule triggered
4. Why the issue matters
5. Required action or adviser review
"""

from typing import List, Dict, Any, Optional
from core.client import ClientProfile, FinancialGoal
from core.risk_engine import assess_client_risk, RiskAssessmentResult

class SuitabilityWarning:
    def __init__(
        self,
        severity: str, # "CRITICAL_BLOCKER", "HIGH_RISK", "MODERATE_WARNING", "INFORMATIONAL"
        rule_name: str,
        issue_detected: str,
        relevant_data: Dict[str, Any],
        why_it_matters: str,
        required_review_action: str
    ):
        self.severity = severity
        self.rule_name = rule_name
        self.issue_detected = issue_detected
        self.relevant_data = relevant_data
        self.why_it_matters = why_it_matters
        self.required_review_action = required_review_action

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "rule_name": self.rule_name,
            "issue_detected": self.issue_detected,
            "relevant_data": self.relevant_data,
            "why_it_matters": self.why_it_matters,
            "required_review_action": self.required_review_action
        }

class SuitabilityEvaluationReport:
    def __init__(
        self,
        client_id: str,
        passed_automated_checks: bool,
        overall_verdict: str, # "PASSED", "WARNINGS_REQUIRE_ADVISER_ATTENTION", "FAILED_CRITICAL_GUARDRAIL"
        warnings: List[SuitabilityWarning],
        risk_result: RiskAssessmentResult,
        disclaimer: str
    ):
        self.client_id = client_id
        self.passed_automated_checks = passed_automated_checks
        self.overall_verdict = overall_verdict
        self.warnings = warnings
        self.risk_result = risk_result
        self.disclaimer = disclaimer

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "passed_automated_checks": self.passed_automated_checks,
            "overall_verdict": self.overall_verdict,
            "warnings_count": len(self.warnings),
            "warnings": [w.to_dict() for w in self.warnings],
            "risk_assessment": self.risk_result.to_dict(),
            "disclaimer": self.disclaimer
        }

def evaluate_plan_suitability(
    client: ClientProfile,
    goal: FinancialGoal,
    proposed_equity_pct: float,
    proposed_debt_pct: float,
    proposed_schemes: Optional[List[Dict[str, Any]]] = None,
    user_prompt_flags: Optional[List[str]] = None
) -> SuitabilityEvaluationReport:
    """
    Evaluates a proposed goal recommendation against the client profile and SEBI suitability principles.
    """
    warnings: List[SuitabilityWarning] = []
    risk_res = assess_client_risk(client)

    # RULE 1: Return Guarantee Prohibition (SEBI IA Regulations, 2013)
    # Never promise or model unrealistic or guaranteed returns
    if goal.expected_return >= 0.15:
        warnings.append(SuitabilityWarning(
            severity="CRITICAL_BLOCKER",
            rule_name="SEBI Reg 15(1) - Unrealistic Return Assumption Rule",
            issue_detected=f"Assumed nominal return is {goal.expected_return*100:.1f}%, which exceeds safe advisory threshold (14.0%).",
            relevant_data={"assumed_return_pct": goal.expected_return * 100, "safe_threshold_pct": 14.0},
            why_it_matters="Long-term diversified mutual fund compounding above 12-14% CAGR in INR is historically aggressive and cannot be assured. Using inflated return assumptions causes clients to under-save.",
            required_review_action="Reduce expected return assumption to 10.0% - 12.0% and recompute required monthly SIP."
        ))

    if user_prompt_flags:
        for fl in user_prompt_flags:
            if "guarantee" in fl.lower() or "assured" in fl.lower() or "high returns fast" in fl.lower():
                warnings.append(SuitabilityWarning(
                    severity="CRITICAL_BLOCKER",
                    rule_name="Zero Guarantee Mandate",
                    issue_detected=f"Client expressed expectation: '{fl}'. Guaranteed or assured returns are illegal for SEBI RIAs.",
                    relevant_data={"client_expectation": fl},
                    why_it_matters="Mutual fund investments are subject to market risks. Promising guaranteed returns violates SEBI code of conduct.",
                    required_review_action="Issue formal written disclosure clarifying all returns are market-linked with potential capital drawdown."
                ))

    # RULE 2: Senior Citizen Decumulation Capital Preservation
    if client.age >= 65 and proposed_equity_pct > 30.0:
        warnings.append(SuitabilityWarning(
            severity="CRITICAL_BLOCKER",
            rule_name="Senior Citizen Capital Preservation Guardrail",
            issue_detected=f"Client age is {client.age} (retiree), but proposed equity allocation is {proposed_equity_pct:.1f}% (cap is 30.0%).",
            relevant_data={"client_age": client.age, "proposed_equity_pct": proposed_equity_pct, "maximum_allowed_pct": 30.0},
            why_it_matters="Retirees in post-retirement drawdown phase lack future human capital earnings to recover from prolonged market drawdowns. Capital preservation and predictable SWP income must take priority.",
            required_review_action="Rebalance proposed mix: cap equity to <= 25%, allocate remainder to Short/Corporate Debt and Arbitrage."
        ))

    # RULE 3: Risk Capacity Ceiling Violation
    if proposed_equity_pct > risk_res.max_equity_allocation_pct:
        warnings.append(SuitabilityWarning(
            severity="HIGH_RISK",
            rule_name="Risk Capacity Ceiling Constraint",
            issue_detected=f"Proposed equity exposure ({proposed_equity_pct:.1f}%) exceeds client risk capacity limit ({risk_res.max_equity_allocation_pct:.1f}%).",
            relevant_data={
                "proposed_equity": proposed_equity_pct,
                "capacity_ceiling": risk_res.max_equity_allocation_pct,
                "capacity_tier": risk_res.capacity_tier
            },
            why_it_matters="Risk capacity represents actual financial solvency and debt burden. Even if client tolerance is high, exceeding capacity risks financial distress during market downturns.",
            required_review_action="Align portfolio equity weight strictly with capacity limit."
        ))

    # RULE 4: Investment Horizon vs Asset Class Mismatch
    if goal.years_remaining < 3.0 and proposed_equity_pct > 20.0:
        warnings.append(SuitabilityWarning(
            severity="HIGH_RISK",
            rule_name="Short Horizon Equity Misallocation Rule",
            issue_detected=f"Goal deadline is only {goal.years_remaining:.1f} years away, but portfolio has {proposed_equity_pct:.1f}% equity.",
            relevant_data={"years_remaining": goal.years_remaining, "proposed_equity_pct": proposed_equity_pct},
            why_it_matters="Equity markets exhibit high rolling return volatility over 1 to 3 year windows. A 20-30% market correction right before goal deadline can severely impair the goal.",
            required_review_action="Shift allocation to liquid, arbitrage, or ultra-short duration debt funds."
        ))

    # RULE 5: Emergency Liquidity Buffer Deficit
    min_months_required = 6.0 if client.income_stability in ["Fluctuating", "High Volatility"] else 3.0
    if client.emergency_fund_months < min_months_required:
        warnings.append(SuitabilityWarning(
            severity="MODERATE_WARNING",
            rule_name="Emergency Liquidity Adequacy Rule",
            issue_detected=f"Client maintains only {client.emergency_fund_months:.1f} months of expenses in liquid savings (minimum recommended: {min_months_required:.1f} months).",
            relevant_data={"current_months": client.emergency_fund_months, "recommended_months": min_months_required},
            why_it_matters="Inadequate liquid reserves force clients to prematurely liquidate long-term equity mutual funds at distressed prices during personal financial shocks.",
            required_review_action="Allocate initial monthly SIPs towards building a 6-month liquid emergency fund before locking into long-term equity."
        ))

    # RULE 6: Regular Plan / Conflict of Interest Detection
    if proposed_schemes:
        has_regular = False
        regular_names = []
        for s in proposed_schemes:
            if not s.get("is_direct", True) or "regular" in str(s.get("plan", "")).lower():
                has_regular = True
                regular_names.append(s.get("scheme_name", "Unknown"))
        if has_regular:
            warnings.append(SuitabilityWarning(
                severity="CRITICAL_BLOCKER",
                rule_name="SEBI RIA Fiduciary Conflict of Interest Guardrail",
                issue_detected=f"Proposed portfolio contains Regular Plan schemes: {', '.join(regular_names)}.",
                relevant_data={"non_direct_schemes": regular_names},
                why_it_matters="SEBI Investment Advisers Regulations prohibit RIAs from receiving commissions or recommending Regular Plans where Direct Plans exist.",
                required_review_action="Substitute all Regular Plans with Direct Plans (Direct Growth)."
            ))

    # Overall Verdict
    critical_count = sum(1 for w in warnings if w.severity == "CRITICAL_BLOCKER")
    high_count = sum(1 for w in warnings if w.severity == "HIGH_RISK")
    
    if critical_count > 0:
        passed = False
        verdict = "FAILED_CRITICAL_GUARDRAIL"
    elif high_count > 0 or len(warnings) > 0:
        passed = True # Can be presented to adviser, but adviser attention required
        verdict = "WARNINGS_REQUIRE_ADVISER_ATTENTION"
    else:
        passed = True
        verdict = "PASSED"

    disclaimer = (
        "SUITABILITY NOTICE: Automated suitability rules provide decision-support for the registered adviser. "
        "Automated clearance does NOT substitute professional adviser fiduciary sign-off. "
        "SEBI RIA Regulations require an authorized adviser to approve every recommendation before distribution."
    )

    return SuitabilityEvaluationReport(
        client_id=client.id,
        passed_automated_checks=passed,
        overall_verdict=verdict,
        warnings=warnings,
        risk_result=risk_res,
        disclaimer=disclaimer
    )

