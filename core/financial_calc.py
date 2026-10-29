"""
Deterministic Financial Calculations Engine.
Provides mathematically exact, tested functions for:
1. Inflation-adjusted target corpus
2. Future value of existing investments
3. Monthly SIP requirement (annuity due)
4. Funding shortfall calculation
5. Asset allocation & illustrative glide path
6. Real vs Nominal returns (Fisher equation)
7. Sensitivity matrix analysis
"""

from typing import Dict, Any, List
import math
from core.client import FinancialGoal

def calculate_inflation_adjusted_corpus(current_cost: float, inflation_rate: float, years: float) -> float:
    """
    Computes inflation-adjusted future target corpus:
    C_future = C_today * (1 + inflation_rate)^years
    """
    if current_cost <= 0 or years <= 0:
        return max(0.0, float(current_cost))
    if inflation_rate <= -1.0:
        return 0.0
    return float(current_cost * math.pow(1.0 + inflation_rate, years))

def calculate_future_value_lump_sum(present_value: float, annual_return: float, years: float) -> float:
    """
    Computes compound future value of existing lump sum investments:
    FV = PV * (1 + annual_return)^years
    """
    if present_value <= 0 or years <= 0:
        return max(0.0, float(present_value))
    if annual_return <= -1.0:
        return 0.0
    return float(present_value * math.pow(1.0 + annual_return, years))

def calculate_real_return(nominal_return: float, inflation_rate: float) -> float:
    """
    Computes real return using Fisher equation:
    r_real = (1 + r_nominal) / (1 + r_inflation) - 1
    """
    if inflation_rate <= -1.0:
        return 0.0
    return float((1.0 + nominal_return) / (1.0 + inflation_rate) - 1.0)

def calculate_monthly_sip(
    funding_shortfall: float,
    annual_return: float,
    years: float,
    timing: str = "beginning" # standard SIP is paid at beginning of each month (annuity due)
) -> float:
    """
    Calculates monthly SIP required to accumulate funding_shortfall over 'years' at 'annual_return'.
    
    Formula for Annuity Due (payments at beginning of month):
        monthly_rate i = (1 + annual_return)^(1/12) - 1
        n = years * 12
        FV = SIP * [((1 + i)^n - 1) / i] * (1 + i)
        => SIP = FV / { [((1 + i)^n - 1) / i] * (1 + i) }
        
    Handles edge cases:
        - shortfall <= 0 => SIP = 0
        - annual_return == 0 => SIP = FV / n
        - years <= 0 => SIP = FV
    """
    if funding_shortfall <= 0:
        return 0.0
    
    months = int(round(years * 12))
    if months <= 0:
        return float(funding_shortfall)
    
    if abs(annual_return) < 1e-7:
        # Zero interest edge case
        return float(funding_shortfall / months)
    
    # Effective monthly rate using compound compounding (standard in wealth advisory)
    # Alternatively nominal i = annual_return / 12
    monthly_rate = math.pow(1.0 + annual_return, 1.0 / 12.0) - 1.0
    
    if timing == "beginning":
        # Annuity Due
        factor = ((math.pow(1.0 + monthly_rate, months) - 1.0) / monthly_rate) * (1.0 + monthly_rate)
    else:
        # Ordinary Annuity
        factor = (math.pow(1.0 + monthly_rate, months) - 1.0) / monthly_rate
        
    if factor <= 0:
        return float(funding_shortfall / months)
    
    return float(funding_shortfall / factor)

def generate_glide_path(
    initial_equity_pct: float,
    initial_debt_pct: float,
    initial_liquid_pct: float,
    total_years: float,
    current_year: int = 0
) -> List[Dict[str, Any]]:
    """
    Generates a yearly asset allocation glide path from Year 0 to Goal Maturity.
    Rule: As the deadline nears (< 5 years, < 3 years, < 1 year), equity is systematically
    transitioned into debt and liquid/overnight funds to lock in accumulated capital.
    """
    total_y = max(1, int(math.ceil(total_years)))
    glide_steps = []
    
    for yr in range(total_y + 1):
        years_left = total_y - yr
        
        if years_left > 7:
            # Accumulation phase
            eq = initial_equity_pct
            db = initial_debt_pct
            lq = initial_liquid_pct
        elif years_left > 4:
            # Mild de-risking
            eq = min(initial_equity_pct * 0.8, 50.0)
            db = 100.0 - eq - 10.0
            lq = 10.0
        elif years_left > 2:
            # Significant de-risking
            eq = min(initial_equity_pct * 0.4, 30.0)
            db = 100.0 - eq - 15.0
            lq = 15.0
        elif years_left > 0:
            # Capital preservation phase
            eq = min(initial_equity_pct * 0.15, 10.0)
            db = 100.0 - eq - 30.0
            lq = 30.0
        else:
            # At maturity: 100% Cash / Liquid / Arbitrage
            eq = 0.0
            db = 20.0
            lq = 80.0
            
        glide_steps.append({
            "year": yr,
            "years_remaining": years_left,
            "equity_pct": round(eq, 1),
            "debt_pct": round(db, 1),
            "liquid_pct": round(lq, 1),
            "phase": "Accumulation" if years_left > 5 else ("Consolidation" if years_left > 2 else "Preservation")
        })
    return glide_steps

def calculate_goal_projection(goal: FinancialGoal, max_equity_cap: float = 75.0) -> Dict[str, Any]:
    """
    Comprehensive goal evaluation:
    Calculates future corpus, existing FV, shortfall, required SIP, baseline allocation,
    glide path, and sensitivity matrix.
    """
    future_corpus = calculate_inflation_adjusted_corpus(goal.target_corpus, goal.inflation_rate, goal.years_remaining)
    existing_fv = calculate_future_value_lump_sum(goal.existing_allocated, goal.expected_return, goal.years_remaining)
    shortfall = max(0.0, future_corpus - existing_fv)
    monthly_sip = calculate_monthly_sip(shortfall, goal.expected_return, goal.years_remaining)
    real_ret = calculate_real_return(goal.expected_return, goal.inflation_rate)
    
    # Asset Allocation baseline based on years remaining and max_equity_cap
    if goal.years_remaining >= 10:
        target_equity = min(75.0, max_equity_cap)
        target_debt = max(15.0, 95.0 - target_equity)
        target_liquid = 5.0
    elif goal.years_remaining >= 5:
        target_equity = min(60.0, max_equity_cap)
        target_debt = max(25.0, 90.0 - target_equity)
        target_liquid = 10.0
    elif goal.years_remaining >= 3:
        target_equity = min(35.0, max_equity_cap)
        target_debt = 50.0
        target_liquid = 15.0
    else:
        target_equity = min(15.0, max_equity_cap)
        target_debt = 50.0
        target_liquid = 35.0

    glide_path = generate_glide_path(target_equity, target_debt, target_liquid, goal.years_remaining)

    # Sensitivity Matrix: variation in SIP with +/- 2% return and +/- 1% inflation
    sensitivity = []
    base_ret = goal.expected_return
    base_inf = goal.inflation_rate
    
    for r_delta in [-0.02, 0.0, 0.02]:
        for inf_delta in [-0.01, 0.0, 0.01]:
            test_r = max(0.01, base_ret + r_delta)
            test_inf = max(0.01, base_inf + inf_delta)
            test_corpus = calculate_inflation_adjusted_corpus(goal.target_corpus, test_inf, goal.years_remaining)
            test_fv = calculate_future_value_lump_sum(goal.existing_allocated, test_r, goal.years_remaining)
            test_shortfall = max(0.0, test_corpus - test_fv)
            test_sip = calculate_monthly_sip(test_shortfall, test_r, goal.years_remaining)
            
            sensitivity.append({
                "expected_return_pct": round(test_r * 100, 1),
                "inflation_rate_pct": round(test_inf * 100, 1),
                "target_corpus": round(test_corpus, 0),
                "monthly_sip": round(test_sip, 0),
                "difference_from_base": round(test_sip - monthly_sip, 0)
            })

    return {
        "goal_id": goal.goal_id,
        "goal_name": goal.name,
        "current_cost": goal.target_corpus,
        "years_remaining": goal.years_remaining,
        "inflation_rate_pct": round(goal.inflation_rate * 100, 2),
        "expected_return_pct": round(goal.expected_return * 100, 2),
        "real_return_pct": round(real_ret * 100, 2),
        "future_corpus": round(future_corpus, 2),
        "existing_allocated": goal.existing_allocated,
        "existing_fv": round(existing_fv, 2),
        "funding_shortfall": round(shortfall, 2),
        "monthly_sip": round(monthly_sip, 2),
        "asset_allocation": {
            "equity_pct": round(target_equity, 1),
            "debt_pct": round(target_debt, 1),
            "liquid_pct": round(target_liquid, 1)
        },
        "glide_path": glide_path,
        "sensitivity_matrix": sensitivity,
        "disclaimer": (
            "DISCLOSURE: Investment returns are assumptions for financial planning purposes "
            "and are neither guaranteed nor assured by SEBI or the Adviser. Mutual fund investments "
            "are subject to market risks."
        )
    }

