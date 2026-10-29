# Test Report: Zeckathon PS-04 Advisory Co-pilot

**Date**: 28-Oct-2026  
**Evaluation Scope**: Unit tests, financial formula proofs, SEBI suitability guardrails, empirical backtesting, and RAG retrieval citations.  
**Execution Environment**: Python 3.14.2 on Windows 11 (AMD64)  
**Overall Status**: **19 PASSED | 0 FAILED**

---

## 1. Automated Test Suite Execution Summary

Executed via `python run_tests.py`:

| Test Suite / Area | Tests Executed | Passed | Failed | Status |
|---|---|---|---|---|
| **Financial Calculations Engine** | 7 | 7 | 0 | `PASSED` |
| **Risk Profiling & Conflict Resolution** | 4 | 4 | 0 | `PASSED` |
| **Data Loader & Universe Integrity** | 3 | 3 | 0 | `PASSED` |
| **Suitability & Guardrails Engine** | 3 | 3 | 0 | `PASSED` |
| **RAG Document Retrieval & Citations** | 2 | 2 | 0 | `PASSED` |
| **TOTAL** | **19** | **19** | **0** | **100% SUCCESS** |

---

## 2. Detailed Test Item Breakdown

### A. Financial Calculations (`tests/test_financial_calc.py`)
1. **Inflation-Adjusted Target Corpus**: Verified mathematical formula $C_{future} = C_{today} \times (1 + r_{inf})^t$. ₹10,00,000 at 6% over 10 years evaluated to exact ₹17,90,847.70. `[PASS]`
2. **Future Value of Lump Sum**: Verified $FV = PV \times (1 + r)^t$. ₹5,00,000 at 12% over 5 years evaluated to exact ₹8,81,170.84. `[PASS]`
3. **Fisher Real Rate of Return**: Verified $(1 + r_{nominal}) / (1 + r_{inflation}) - 1$. 12% nominal and 6% inflation yielded exact 5.66% real return. `[PASS]`
4. **Monthly SIP Annuity Due Formula**: Verified beginning-of-period compounding factor. Shortfall of ₹10,00,000 over 10 years at 12% yielded correct annuity-due monthly SIP. `[PASS]`
5. **SIP Zero-Return Edge Case**: Verified handling of $r = 0.0$. Shortfall of ₹1,20,000 over 1 year yielded exact ₹10,000.00/month without division by zero. `[PASS]`
6. **SIP Zero-Shortfall Edge Case**: Verified that fully funded or negative shortfall returns SIP = ₹0.00. `[PASS]`
7. **Systematic De-risking Glide Path**: Verified 11-step yearly trajectory transitioning equity systematically from 75% down to 0% at maturity, shifting capital into liquid/cash preservation. `[PASS]`

### B. Risk Engine & Persona Evaluation (`tests/test_risk_engine.py`)
1. **Fresh Graduate (Age 23)**: Evaluated high savings surplus and 15-year horizon against moderate psychological tolerance. Correctly allocated 55% maximum equity without excessive risk damping. `[PASS]`
2. **Retiree Senior Citizen Cap (Age 68)**: Enforced senior citizen decumulation rule capping equity strictly to $\le 30\%$ (assigned 25%) regardless of aggressive requests. `[PASS]`
3. **Aggressive Trader (Age 29)**: Successfully detected severe conflict between high emotional risk appetite (score 10/10) and weak financial capacity (debt burden, derivative losses, low liquidity). Capped equity to capacity limit. `[PASS]`
4. **Doctor (Age 38)**: Successfully detected capacity-exceeds-tolerance conflict (High capacity vs Conservative tolerance). Flagged under-investment inflation risk and recommended stepped STP. `[PASS]`

### C. Data Loader & Data Integrity (`tests/test_data_loader.py`)
1. **AMFI Universe**: Verified 14,419 schemes loaded from `Mutual Fund NAVAll.txt` with clean categorization into Direct Plan (4,347 schemes) and Growth Options. `[PASS]`
2. **Historical Time Series**: Verified empirical daily NAV series parsing for Altiva SIF and Infinity SIF across 97 and 77 daily observations. `[PASS]`
3. **Data Coverage Summary**: Verified transparent reporting of local time-series coverage without fabricating fake observations. `[PASS]`

### D. Suitability Guardrails (`tests/test_suitability.py`)
1. **SEBI IA Reg 15 Return Guarantee Prohibition**: Blocked 20% return expectation and requests for guaranteed returns with `CRITICAL_BLOCKER` severity. `[PASS]`
2. **Senior Citizen Over-Allocation Guardrail**: Blocked 80% equity recommendation for an age 68 retiree. `[PASS]`
3. **Regular Plan Commission Conflict**: Detected non-direct schemes and blocked distributor commission conflicts under SEBI RIA fiduciary rules. `[PASS]`

### E. RAG Document Retrieval & Citations (`tests/test_rag.py`)
1. **Semantic Vector Search**: Queried ChromaDB vector index; retrieved top excerpts from `dsp-factsheet_september-2026_final.pdf` with verified Page 5 citation. `[PASS]`
2. **Grounded QA Engine Structure**: Verified that answers retain source filenames, page citations, and fallback seamlessly to Diagnostic Mode when offline. `[PASS]`

---

## 3. Verified Factual Findings & Known Data Limitations

1. **Backtesting Period Reality**:
   - The two historical time-series Excel files provided (`NAV_2021-11-01_to_2026-10-28.xlsx` and `(1).xlsx`) contain daily NAVs starting in June/July 2026 through October 2026 (~77 common sessions).
   - The application reports verified empirical metrics on available data and displays an explicit historical coverage warning rather than fabricating fake 10-year observations.
2. **Mutual Fund Universe**:
   - Contains all 14,419 AMFI schemes. Expense ratios and AUM are fully verified for schemes covered in official factsheets; other schemes are labeled "Not Disclosed in Local Dataset" rather than showing false zeros.
3. **LLM Synthesis & Diagnostic Mode**:
   - Tested Groq LLM integration. When network is sandboxed or keys are missing, the system automatically runs in **Offline Diagnostic Retrieval Mode**, surfacing exact passages and page numbers.

