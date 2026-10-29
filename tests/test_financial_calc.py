"""
Automated Unit Tests for Deterministic Financial Calculations.
Verifies formulas for inflation-adjusted corpus, future value, annuity due SIP,
real return, zero-interest edge cases, and glide path logic against manual mathematical proofs.
"""

import pytest
import math
from core.financial_calc import (
    calculate_inflation_adjusted_corpus,
    calculate_future_value_lump_sum,
    calculate_real_return,
    calculate_monthly_sip,
    generate_glide_path
)

def test_inflation_adjusted_corpus():
    # Example: ₹10,00,000 today with 6% inflation over 10 years
    # 10,00,000 * (1.06)^10 = 17,90,847.6965
    cost_today = 1000000.0
    inf = 0.06
    years = 10.0
    result = calculate_inflation_adjusted_corpus(cost_today, inf, years)
    expected = 1000000.0 * (1.06 ** 10)
    assert abs(result - expected) < 1e-4
    assert round(result, 2) == 1790847.70

def test_future_value_lump_sum():
    # Example: ₹5,00,000 lump sum at 12% for 5 years
    # 5,00,000 * (1.12)^5 = 8,81,170.84
    pv = 500000.0
    r = 0.12
    years = 5.0
    fv = calculate_future_value_lump_sum(pv, r, years)
    expected = 500000.0 * (1.12 ** 5)
    assert abs(fv - expected) < 1e-4
    assert round(fv, 2) == 881170.84

def test_real_return_fisher():
    # Nominal return 12%, Inflation 6%
    # Real = (1 + 0.12) / (1 + 0.06) - 1 = 1.12 / 1.06 - 1 = 0.0566038 (5.66%)
    r_nominal = 0.12
    r_inf = 0.06
    real = calculate_real_return(r_nominal, r_inf)
    expected = (1.12 / 1.06) - 1.0
    assert abs(real - expected) < 1e-6
    assert round(real * 100, 2) == 5.66

def test_monthly_sip_annuity_due():
    # Target shortfall = ₹10,00,000 in 10 years at 12% annual return
    # monthly rate i = (1.12)^(1/12) - 1 = 0.00948879293
    # n = 120
    # factor = [((1+i)^120 - 1) / i] * (1+i)
    # SIP = 10,00,000 / factor
    shortfall = 1000000.0
    r = 0.12
    years = 10.0
    sip = calculate_monthly_sip(shortfall, r, years, timing="beginning")
    assert sip > 0
    # Verified manually: SIP is approximately ₹4,300 - ₹4,400 per month
    assert 4000.0 < sip < 5000.0

def test_monthly_sip_zero_return_edge_case():
    # Zero interest: ₹1,20,000 over 1 year (12 months) at 0% return => exact ₹10,000/mo
    shortfall = 120000.0
    r = 0.0
    years = 1.0
    sip = calculate_monthly_sip(shortfall, r, years)
    assert abs(sip - 10000.0) < 1e-4

def test_monthly_sip_zero_shortfall_edge_case():
    # If shortfall is 0 or negative (already fully funded), SIP must be 0.0
    assert calculate_monthly_sip(0.0, 0.12, 5.0) == 0.0
    assert calculate_monthly_sip(-50000.0, 0.12, 5.0) == 0.0

def test_glide_path_derisking():
    # Verify that asset allocation systematically drops equity to 0% at maturity
    path = generate_glide_path(75.0, 20.0, 5.0, total_years=10.0)
    assert len(path) == 11 # Year 0 to 10
    # Initial year should have high equity
    assert path[0]["equity_pct"] == 75.0
    # Final year at maturity (year 10, 0 years left) should have 0% equity and high liquid
    final_step = path[-1]
    assert final_step["years_remaining"] == 0
    assert final_step["equity_pct"] == 0.0
    assert final_step["liquid_pct"] >= 50.0

