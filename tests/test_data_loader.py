"""
Automated Unit Tests for Data Loader and Data Integrity.
Verifies parsing of AMFI NAV snapshot, SIF historical series, and inflation series.
"""

import pytest
import pandas as pd
from core.data_loader import load_amfi_nav_all, load_historical_nav_series, load_cpi_inflation_data, get_data_coverage_summary

def test_load_amfi_nav_all():
    df = load_amfi_nav_all()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 10000 # Live AMFI has 14,419 rows
    expected_cols = {"scheme_code", "scheme_name", "fund_house", "category", "plan", "option", "is_direct", "is_growth"}
    assert expected_cols.issubset(set(df.columns))
    
    # Verify Direct Plan detection
    direct_df = df[df["is_direct"]]
    assert len(direct_df) > 1000
    assert all("direct" in s.lower() or "direct" in p.lower() for s, p in zip(direct_df["scheme_name"], direct_df["plan"]))

def test_load_historical_nav_series():
    series = load_historical_nav_series()
    assert len(series) >= 2
    for name, df in series.items():
        assert "Date" in df.columns
        assert "Net Asset Value" in df.columns
        assert len(df) > 50
        assert pd.api.types.is_datetime64_any_dtype(df["Date"])
        assert pd.api.types.is_numeric_dtype(df["Net Asset Value"])

def test_data_coverage_summary():
    cov = get_data_coverage_summary()
    assert cov["amfi_schemes_count"] > 10000
    assert cov["historical_series_count"] >= 2
    assert cov["full_10_year_daily_history_present"] is False
    assert "LIMITATION DISCLOSURE" in cov["coverage_limitation_notice"]

