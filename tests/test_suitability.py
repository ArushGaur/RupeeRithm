"""
Automated Unit Tests for Fiduciary Suitability Guardrails.
Verifies blocking of unrealistic return guarantees, senior citizen misallocations,
horizon mismatches, and Regular Plan commission conflicts.
"""

import pytest
from core.client import SAMPLE_PERSONAS, FinancialGoal
from core.suitability import evaluate_plan_suitability

def test_unrealistic_return_guarantee_blocked():
    # If a plan or client assumes >= 15% guaranteed returns, must trigger CRITICAL_BLOCKER
    p = SAMPLE_PERSONAS["aggressive_trader"]
    goal = FinancialGoal(
        goal_id="g_test_unrealistic",
        name="Get Rich Fast",
        target_corpus=1000000.0,
        years_remaining=2.0,
        inflation_rate=0.06,
        expected_return=0.20 # 20% unrealistic return!
    )
    report = evaluate_plan_suitability(
        client=p,
        goal=goal,
        proposed_equity_pct=75.0,
        proposed_debt_pct=25.0,
        user_prompt_flags=["guarantee me 20%"]
    )
    assert report.passed_automated_checks is False
    assert report.overall_verdict == "FAILED_CRITICAL_GUARDRAIL"
    blockers = [w for w in report.warnings if w.severity == "CRITICAL_BLOCKER"]
    assert len(blockers) >= 1
    assert any("Return Assumption" in w.rule_name or "Guarantee" in w.rule_name for w in blockers)

def test_senior_citizen_high_equity_blocked():
    # Age 68 retiree asked for 80% equity exposure
    retiree = SAMPLE_PERSONAS["retiree"]
    goal = retiree.financial_goals[0]
    report = evaluate_plan_suitability(
        client=retiree,
        goal=goal,
        proposed_equity_pct=80.0, # Excessive equity for senior citizen!
        proposed_debt_pct=20.0
    )
    assert report.passed_automated_checks is False
    assert report.overall_verdict == "FAILED_CRITICAL_GUARDRAIL"
    senior_warnings = [w for w in report.warnings if "Senior Citizen" in w.rule_name]
    assert len(senior_warnings) == 1

def test_regular_plan_commission_conflict_blocked():
    # Attempting to recommend a Regular Plan where distributor commissions exist
    fresh = SAMPLE_PERSONAS["fresh_graduate"]
    goal = fresh.financial_goals[0]
    bad_schemes = [
        {"scheme_name": "ABC Bluechip Fund - Regular Plan - Growth", "plan": "Regular Plan", "is_direct": False}
    ]
    report = evaluate_plan_suitability(
        client=fresh,
        goal=goal,
        proposed_equity_pct=20.0,
        proposed_debt_pct=80.0,
        proposed_schemes=bad_schemes
    )
    assert report.passed_automated_checks is False
    commission_warnings = [w for w in report.warnings if "Conflict of Interest" in w.rule_name]
    assert len(commission_warnings) == 1

