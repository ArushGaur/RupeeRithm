"""
Mutual Fund Analysis and Ranking Module.
Enables searching, filtering, metric calculation, and explainable scoring
over the live AMFI universe (14,419 schemes) and verified factsheet metrics.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from core.data_loader import load_amfi_nav_all

# Curated factsheet verified metrics extracted from the local factsheet PDFs
# for benchmark comparisons and fund details
VERIFIED_FACTSHEET_DATA: Dict[str, Dict[str, Any]] = {
    "DSP Flexi Cap Fund": {
        "amc": "DSP Mutual Fund",
        "benchmark": "NIFTY 500 TRI",
        "ter_direct": 0.72,
        "ter_regular": 1.68,
        "aum_cr": 14250.0,
        "risk_o_meter": "Very High",
        "manager": "Atul Bhole / Abhishek Singhal",
        "turnover_pct": 28.5,
        "source_doc": "dsp-factsheet_september-2026_final.pdf"
    },
    "DSP Top 100 Equity Fund": {
        "amc": "DSP Mutual Fund",
        "benchmark": "NIFTY 100 TRI",
        "ter_direct": 1.05,
        "ter_regular": 1.95,
        "aum_cr": 3890.0,
        "risk_o_meter": "Very High",
        "manager": "Gaurav Khandelwal",
        "turnover_pct": 34.0,
        "source_doc": "dsp-factsheet_september-2026_final.pdf"
    },
    "Mirae Asset Large Cap Fund": {
        "amc": "Mirae Asset Mutual Fund",
        "benchmark": "NIFTY 100 TRI",
        "ter_direct": 0.54,
        "ter_regular": 1.55,
        "aum_cr": 37210.0,
        "risk_o_meter": "Very High",
        "manager": "Gaurav Misra / Gaurav Khandelwal",
        "turnover_pct": 42.1,
        "source_doc": "active-factsheet---october-2026.pdf"
    },
    "Mirae Asset Midcap Fund": {
        "amc": "Mirae Asset Mutual Fund",
        "benchmark": "NIFTY Midcap 150 TRI",
        "ter_direct": 0.62,
        "ter_regular": 1.72,
        "aum_cr": 16540.0,
        "risk_o_meter": "Very High",
        "manager": "Ankit Jain",
        "turnover_pct": 55.0,
        "source_doc": "active-factsheet---august-2026.pdf"
    },
    "Mirae Asset Nifty 50 ETF": {
        "amc": "Mirae Asset Mutual Fund",
        "benchmark": "NIFTY 50 TRI",
        "ter_direct": 0.05,
        "ter_regular": 0.05,
        "aum_cr": 4120.0,
        "risk_o_meter": "Very High",
        "manager": "Ekta Gala",
        "tracking_error_pct": 0.04,
        "source_doc": "passive-factsheet---september-2026.pdf"
    },
    "Axis Nifty 500 Index Fund": {
        "amc": "Axis Mutual Fund",
        "benchmark": "NIFTY 500 TRI",
        "ter_direct": 0.20,
        "ter_regular": 0.85,
        "aum_cr": 980.0,
        "risk_o_meter": "Very High",
        "manager": "Karthik Kumar",
        "tracking_error_pct": 0.08,
        "source_doc": "Presentation_Axis_Nifty_500_Index_Fund_September_26_pdf_4238ba84e6.pdf"
    },
    "Axis Multi Factor Passive FoF": {
        "amc": "Axis Mutual Fund",
        "benchmark": "NIFTY 500 TRI",
        "ter_direct": 0.25,
        "ter_regular": 1.00,
        "aum_cr": 450.0,
        "risk_o_meter": "Very High",
        "manager": "Karthik Kumar",
        "source_doc": "Presentation_Axis_Multi_Factor_Passive_Fo_F_Final_September_26_70833a0948.pdf"
    },
    "Aditya Birla Sun Life Frontline Equity Fund": {
        "amc": "Aditya Birla Sun Life Mutual Fund",
        "benchmark": "NIFTY 100 TRI",
        "ter_direct": 0.98,
        "ter_regular": 1.68,
        "aum_cr": 26800.0,
        "risk_o_meter": "Very High",
        "manager": "Mahesh Patil",
        "turnover_pct": 31.0,
        "source_doc": "ABSL Factsheet_Aug 2026.pdf"
    }
}

def filter_funds(
    search_query: str = "",
    broad_asset_class: Optional[str] = None,
    category: Optional[str] = None,
    fund_house: Optional[str] = None,
    direct_only: bool = True,
    growth_only: bool = True,
    limit: int = 200
) -> pd.DataFrame:
    """
    Filters the 14,419 AMFI universe by search text, asset class, plan, and option.
    """
    df = load_amfi_nav_all()
    filtered = df

    if direct_only:
        filtered = filtered[filtered["is_direct"]]
    if growth_only:
        filtered = filtered[filtered["is_growth"]]
    if broad_asset_class and broad_asset_class != "All":
        filtered = filtered[filtered["broad_asset_class"] == broad_asset_class]
    if category and category != "All":
        filtered = filtered[filtered["category"].str.contains(category, case=False, na=False)]
    if fund_house and fund_house != "All":
        filtered = filtered[filtered["fund_house"].str.contains(fund_house, case=False, na=False)]
    if search_query:
        q = search_query.strip().lower()
        filtered = filtered[filtered["scheme_name"].str.lower().str.contains(q, na=False)]

    return filtered.head(limit).reset_index(drop=True)

def enrich_fund_with_factsheet(scheme_name: str) -> Dict[str, Any]:
    """
    Enriches an AMFI scheme with verified metrics from official factsheet PDFs
    if a verified match exists, or clearly flags metrics as 'Not Disclosed in Local Dataset'.
    """
    matched = None
    for k, v in VERIFIED_FACTSHEET_DATA.items():
        if k.lower() in scheme_name.lower():
            matched = v
            matched["matched_name"] = k
            break
            
    if matched:
        return {
            "has_verified_factsheet": True,
            "ter_direct_pct": matched.get("ter_direct"),
            "ter_regular_pct": matched.get("ter_regular"),
            "aum_cr": matched.get("aum_cr"),
            "benchmark": matched.get("benchmark"),
            "manager": matched.get("manager"),
            "turnover_pct": matched.get("turnover_pct"),
            "tracking_error_pct": matched.get("tracking_error_pct"),
            "risk_o_meter": matched.get("risk_o_meter"),
            "source_doc": matched.get("source_doc")
        }
    else:
        return {
            "has_verified_factsheet": False,
            "ter_direct_pct": None,
            "ter_regular_pct": None,
            "aum_cr": None,
            "benchmark": "Benchmark not in local factsheet",
            "manager": "Not Disclosed in Local Dataset",
            "turnover_pct": None,
            "tracking_error_pct": None,
            "risk_o_meter": "Refer Scheme SID",
            "source_doc": "AMFI Live NAV Snapshot (27-Oct-2026)"
        }

def calculate_time_series_metrics(nav_series: pd.Series, dates: pd.Series) -> Dict[str, Any]:
    """
    Calculates empirical financial metrics from a daily NAV series:
    - Period Start, End, and Total Calendar Days
    - Absolute Return
    - Annualized Return (CAGR) if period >= 30 days
    - Annualized Volatility (daily std * sqrt(250))
    - Maximum Drawdown (peak-to-trough decline)
    """
    if len(nav_series) < 2:
        return {
            "days": len(nav_series),
            "absolute_return_pct": 0.0,
            "cagr_pct": 0.0,
            "annualized_volatility_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "warning": "Insufficient observations (< 2 days)"
        }

    valid_mask = pd.notna(nav_series) & pd.notna(dates)
    clean_nav = nav_series[valid_mask].astype(float).values
    clean_dates = pd.to_datetime(dates[valid_mask]).values

    if len(clean_nav) < 2:
        return {"warning": "No valid non-null records"}

    start_nav = clean_nav[0]
    end_nav = clean_nav[-1]
    start_dt = pd.Timestamp(clean_dates[0])
    end_dt = pd.Timestamp(clean_dates[-1])
    days = (end_dt - start_dt).days

    abs_return = ((end_nav - start_nav) / start_nav) * 100.0

    # CAGR calculation: only meaningful if period > 30 days
    if days >= 30 and start_nav > 0 and end_nav > 0:
        years = days / 365.25
        cagr = (math_pow := (end_nav / start_nav) ** (1.0 / years) - 1.0) * 100.0
    else:
        cagr = np.nan

    # Daily returns & Annualized Volatility
    daily_returns = np.diff(clean_nav) / clean_nav[:-1]
    if len(daily_returns) > 5:
        daily_std = np.std(daily_returns, ddof=1)
        annualized_vol = daily_std * np.sqrt(250.0) * 100.0
    else:
        annualized_vol = np.nan

    # Maximum Drawdown
    cum_max = np.maximum.accumulate(clean_nav)
    drawdowns = (clean_nav - cum_max) / cum_max
    max_dd = np.min(drawdowns) * 100.0 if len(drawdowns) > 0 else 0.0

    return {
        "start_date": start_dt.strftime("%Y-%m-%d"),
        "end_date": end_dt.strftime("%Y-%m-%d"),
        "calendar_days": days,
        "trading_days": len(clean_nav),
        "start_nav": round(start_nav, 4),
        "end_nav": round(end_nav, 4),
        "absolute_return_pct": round(abs_return, 2),
        "cagr_pct": round(cagr, 2) if not np.isnan(cagr) else None,
        "annualized_volatility_pct": round(annualized_vol, 2) if not np.isnan(annualized_vol) else None,
        "max_drawdown_pct": round(max_dd, 2)
    }

def rank_funds(
    funds_df: pd.DataFrame,
    cost_weight: float = 0.35,
    structure_weight: float = 0.35, # Direct + Growth bonus
    size_weight: float = 0.30
) -> pd.DataFrame:
    """
    Explainable Fund Ranking Engine:
    Ranks funds using transparent criteria (Direct plan compliance, growth option, low TER if known, size)
    Generates a human-readable suitability reasoning text for every fund.
    """
    results = []
    for _, row in funds_df.iterrows():
        name = row["scheme_name"]
        is_direct = bool(row["is_direct"])
        is_growth = bool(row["is_growth"])
        f_info = enrich_fund_with_factsheet(name)

        score = 0.0
        reasons = []

        # 1. Direct Plan: Mandatory for SEBI RIA fiduciary duty (saves 0.5% - 1.2% p.a. commission)
        if is_direct:
            score += 35.0
            reasons.append("Direct Plan: Eliminates distributor trail commissions.")
        else:
            reasons.append("WARNING: Regular Plan includes embedded distributor commissions. Inadmissible for RIA.")

        # 2. Growth Option: Tax efficient wealth compounding (avoids immediate IDCW dividend taxation at slab rate)
        if is_growth:
            score += 25.0
            reasons.append("Growth Option: Optimized for tax-efficient long term compounding.")
        else:
            reasons.append("IDCW Option: Dividend payouts trigger tax at marginal income tax slab.")

        # 3. Cost / TER (if known from factsheets)
        ter = f_info.get("ter_direct_pct")
        if ter is not None:
            if ter <= 0.25:
                score += 30.0
                reasons.append(f"Ultra-low TER ({ter}%): Exceptional cost efficiency.")
            elif ter <= 0.75:
                score += 20.0
                reasons.append(f"Competitive TER ({ter}%): Favorable expense ratio.")
            else:
                score += 10.0
                reasons.append(f"Moderate TER ({ter}%).")
        else:
            # Baseline neutral score if factsheet not in local subset
            score += 15.0
            reasons.append("TER not disclosed in local factsheet subset.")

        # 4. AUM Size
        aum = f_info.get("aum_cr")
        if aum is not None:
            if aum >= 5000.0:
                score += 10.0
                reasons.append(f"Large AUM (₹{aum:,.0f} Cr): Deep liquidity and institutional backing.")
            elif aum >= 500.0:
                score += 7.0
                reasons.append(f"Established AUM (₹{aum:,.0f} Cr).")
            else:
                score += 3.0
                reasons.append(f"Small AUM (₹{aum:,.0f} Cr): Monitor tracking error and liquidity.")

        results.append({
            "scheme_code": row["scheme_code"],
            "scheme_name": name,
            "category": row["category"],
            "broad_asset_class": row["broad_asset_class"],
            "plan": row["plan"],
            "option": row["option"],
            "nav": row["nav"],
            "composite_score": round(score, 1),
            "selection_rationale": " | ".join(reasons),
            "ter_direct_pct": ter if ter is not None else "N/A",
            "aum_cr": f"₹{aum:,.0f} Cr" if aum is not None else "N/A",
            "benchmark": f_info.get("benchmark", "N/A"),
            "source_doc": f_info.get("source_doc")
        })

    res_df = pd.DataFrame(results)
    if not res_df.empty:
        res_df = res_df.sort_values("composite_score", ascending=False).reset_index(drop=True)
    return res_df

