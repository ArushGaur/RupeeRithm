"""
Automated Unit Tests for Risk Profiling and Conflict Resolution Engine.
Verifies separation of capacity vs tolerance, conflict detection, and senior citizen rules.
"""

import pytest
from core.client import SAMPLE_PERSONAS
from core.risk_engine import assess_client_risk, calculate_risk_capacity, calculate_risk_tolerance

def test_fresh_graduate_risk_profile():
    # Fresh graduate: age 23, 55k income, 25k expenses, no debt, 15 yr horizon
    p = SAMPLE_PERSONAS["fresh_graduate"]
    res = assess_client_risk(p)
    assert res.capacity_tier in ["Moderate", "High"]
    assert res.tolerance_tier == "Moderate"
    # Fresh graduate is generally well-aligned or has high capacity
    assert res.max_equity_allocation_pct >= 50.0

def test_retiree_senior_citizen_cap():
    # Retiree: age 68, lump sum corpus, low risk tolerance
    p = SAMPLE_PERSONAS["retiree"]
    res = assess_client_risk(p)
    assert p.age == 68
    # Senior citizen rule must strictly cap equity <= 25% or 30%
    assert res.max_equity_allocation_pct <= 30.0
    assert res.final_recommended_tier in ["Conservative", "Moderately Conservative"]

def test_aggressive_trader_conflict_detection():
    # Aggressive trader: low buffer, personal loan, wants high returns fast (score 10)
    p = SAMPLE_PERSONAS["aggressive_trader"]
    res = assess_client_risk(p)
    # Must flag conflict: tolerance exceeds capacity!
    assert res.conflict_detected is True
    assert "Tolerance Exceeds Capacity" in res.conflict_type
    # Equity must be capped to capacity limit
    assert res.max_equity_allocation_pct <= 50.0

def test_doctor_capacity_exceeds_tolerance_conflict():
    # Doctor: high income, zero debt, 60L savings, but risk averse (score 3)
    p = SAMPLE_PERSONAS["doctor"]
    res = assess_client_risk(p)
    assert res.conflict_detected is True
    assert "Capacity Exceeds Tolerance" in res.conflict_type
    assert res.capacity_tier in ["High", "Very High"]
    assert res.tolerance_tier == "Conservative"

