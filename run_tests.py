"""
Automated Test Runner for Zeckathon PS-04 Advisory Co-pilot.
Executes all unit and integration tests across financial calculations,
risk profiling, data loading, suitability guardrails, and RAG retrieval.
"""

import sys
import traceback

def run_all_tests():
    passed = 0
    failed = 0
    test_results = []

    print("=" * 70)
    print("ZECKATHON PS-04: EXECUTING AUTOMATED TEST SUITE")
    print("=" * 70)

    # 1. Financial Calculations
    from tests.test_financial_calc import (
        test_inflation_adjusted_corpus,
        test_future_value_lump_sum,
        test_real_return_fisher,
        test_monthly_sip_annuity_due,
        test_monthly_sip_zero_return_edge_case,
        test_monthly_sip_zero_shortfall_edge_case,
        test_glide_path_derisking
    )
    fin_tests = [
        ("Inflation-Adjusted Target Corpus", test_inflation_adjusted_corpus),
        ("Future Value of Lump Sum", test_future_value_lump_sum),
        ("Fisher Real Rate of Return", test_real_return_fisher),
        ("Monthly SIP Annuity Due Formula", test_monthly_sip_annuity_due),
        ("SIP Zero-Return Edge Case", test_monthly_sip_zero_return_edge_case),
        ("SIP Zero-Shortfall Edge Case", test_monthly_sip_zero_shortfall_edge_case),
        ("Systematic De-risking Glide Path", test_glide_path_derisking)
    ]
    for name, fn in fin_tests:
        try:
            fn()
            passed += 1
            print(f" [PASS] Financial Calculations :: {name}")
            test_results.append((name, "PASS", ""))
        except Exception as e:
            failed += 1
            err = traceback.format_exc()
            print(f" [FAIL] Financial Calculations :: {name} -> {e}")
            test_results.append((name, "FAIL", err))

    # 2. Risk Profiling & Engine
    from tests.test_risk_engine import (
        test_fresh_graduate_risk_profile,
        test_retiree_senior_citizen_cap,
        test_aggressive_trader_conflict_detection,
        test_doctor_capacity_exceeds_tolerance_conflict
    )
    risk_tests = [
        ("Fresh Graduate Risk Profile & Capacity", test_fresh_graduate_risk_profile),
        ("Retiree Senior Citizen Equity Cap (<=30%)", test_retiree_senior_citizen_cap),
        ("Aggressive Trader Capacity vs Tolerance Conflict", test_aggressive_trader_conflict_detection),
        ("Doctor Capacity Exceeds Tolerance Conflict", test_doctor_capacity_exceeds_tolerance_conflict)
    ]
    for name, fn in risk_tests:
        try:
            fn()
            passed += 1
            print(f" [PASS] Risk Engine :: {name}")
            test_results.append((name, "PASS", ""))
        except Exception as e:
            failed += 1
            err = traceback.format_exc()
            print(f" [FAIL] Risk Engine :: {name} -> {e}")
            test_results.append((name, "FAIL", err))

    # 3. Data Loader & Coverage
    from tests.test_data_loader import (
        test_load_amfi_nav_all,
        test_load_historical_nav_series,
        test_data_coverage_summary
    )
    data_tests = [
        ("AMFI 14,419 Universe & Direct/Growth Parsing", test_load_amfi_nav_all),
        ("Historical Daily NAV Series Parsing", test_load_historical_nav_series),
        ("Data Coverage & Limitation Summary", test_data_coverage_summary)
    ]
    for name, fn in data_tests:
        try:
            fn()
            passed += 1
            print(f" [PASS] Data Loader :: {name}")
            test_results.append((name, "PASS", ""))
        except Exception as e:
            failed += 1
            err = traceback.format_exc()
            print(f" [FAIL] Data Loader :: {name} -> {e}")
            test_results.append((name, "FAIL", err))

    # 4. Suitability Guardrails
    from tests.test_suitability import (
        test_unrealistic_return_guarantee_blocked,
        test_senior_citizen_high_equity_blocked,
        test_regular_plan_commission_conflict_blocked
    )
    suit_tests = [
        ("Block Unrealistic Return Guarantees (SEBI IA Reg 15)", test_unrealistic_return_guarantee_blocked),
        ("Block Senior Citizen Over-Allocation to Equity", test_senior_citizen_high_equity_blocked),
        ("Block Regular Plan Commission Conflicts", test_regular_plan_commission_conflict_blocked)
    ]
    for name, fn in suit_tests:
        try:
            fn()
            passed += 1
            print(f" [PASS] Suitability Guardrails :: {name}")
            test_results.append((name, "PASS", ""))
        except Exception as e:
            failed += 1
            err = traceback.format_exc()
            print(f" [FAIL] Suitability Guardrails :: {name} -> {e}")
            test_results.append((name, "FAIL", err))

    # 5. RAG Retrieval & Citations
    from tests.test_rag import (
        test_document_retrieval_citations,
        test_grounded_answer_structure
    )
    rag_tests = [
        ("RAG Chroma Vector Retrieval & Page Citations", test_document_retrieval_citations),
        ("Grounded QA Engine Structure & Fallback", test_grounded_answer_structure)
    ]
    for name, fn in rag_tests:
        try:
            fn()
            passed += 1
            print(f" [PASS] RAG Assistant :: {name}")
            test_results.append((name, "PASS", ""))
        except Exception as e:
            failed += 1
            err = traceback.format_exc()
            print(f" [FAIL] RAG Assistant :: {name} -> {e}")
            test_results.append((name, "FAIL", err))

    print("=" * 70)
    print(f"TEST EXECUTION SUMMARY: {passed} PASSED | {failed} FAILED | TOTAL: {passed + failed}")
    print("=" * 70)

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()

