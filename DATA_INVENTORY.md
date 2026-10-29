# Data Inventory: Zeckathon PS-04 Financial Advisory Datasets

This document catalogs all datasets and documents identified in the local `data/` directory, analyzing their structure, content, date ranges, and mapping them to application capabilities.

---

## 1. Structured Financial Datasets

| File Name | Format | Rows / Size | Key Columns / Content | Date Range / Coverage | Intended Application Use |
|---|---|---|---|---|---|
| `Mutual Fund NAVAll.txt` | Semicolon-delimited TXT | 14,419 scheme rows, 1.49 MB | `Scheme Code`, `ISIN Div Payout/ ISIN Growth`, `ISIN Div Reinvestment`, `Scheme Name`, `Plan`, `Option`, `Net Asset Value`, `Date` | Snapshot as of 27-Oct-2026 | **Core Fund Universe**: AMFI universe containing 57 fund houses, 104 SEBI categories. Used for searching, categorizing, filtering Direct vs Regular plans, Growth vs IDCW options, and current NAV pricing. |
| `latest-nav.xlsx` | Excel (`latestNAV_Reports`) | 178 rows, 15.7 KB | `SIF Code`, `SIF NAV Name`, `Plan`, `Option`, `ISIN`, `Net Asset Value`, `Date` | Snapshot as of 28-Oct-2026 | **Specialized SIF NAVs**: Specialised Investment Fund quotes and plan details. |
| `cdmdf_nav_latest.xlsx` | Excel (`NAV Latest`) | 3 rows, 6.6 KB | `Scheme NAV Name`, `ISIN Div Payout/ISIN Growth`, `ISIN Div Reinvestment`, `NAV Asset Value`, `NAV Date` | Snapshot as of 28-Oct-2026 | Corporate Debt Market Development Fund (CDMDF Class A1, A2, B) valuation data. |
| `NAV_2021-11-01_to_2026-10-28.xlsx` | Excel (`Historical NAV Data`) | 97 daily NAV rows, 9.4 KB | `Net Asset Value`, `Repurchase Price`, `Sale Price`, `Date`, `Plan`, `Option` (Altiva Equity Ex-Top 100 Long-Short Fund Direct Growth) | 10-Jun-2026 to 28-Oct-2026 | **Empirical Time Series**: Real daily NAV series for volatility, return, and drawdown calculations. (Covers ~4.5 months; see Limitations). |
| `NAV_2021-11-01_to_2026-10-28 (1).xlsx` | Excel (`Historical NAV Data`) | 77 daily NAV rows, 8.8 KB | `Net Asset Value`, `Repurchase Price`, `Sale Price`, `Date`, `Plan`, `Option` (Infinity Hybrid Long-Short Fund Direct Growth) | 08-Jul-2026 to 28-Oct-2026 | **Empirical Time Series**: Real daily NAV series for hybrid allocation comparison and backtesting. |

---

## 2. Macroeconomic & Inflation Datasets (RBI DBIE)

| File Name | Format | Rows / Size | Key Content | Coverage Period | Intended Application Use |
|---|---|---|---|---|---|
| `Consumer Price Index for Industrial Workers - By Group ( Annual Average ).xlsx` | Excel (`Report 1`) | 42 data rows, 10.6 KB | Base CPI series (2016=100 and 1982/2001 base years). General Index, Food, Fuel & Light, Housing, Clothing, Misc. | 1990s through 2025-26 | **Historical Inflation Estimation**: Base for default inflation rates in long-term goals (education, retirement). Historical CAGR is 5.5%–7.2%. |
| `Consumer Price Index for Agricultural Labourer - By Group (Year-End).xlsx` | Excel | 20 data rows, 9.3 KB | Base CPI-1986-87 and Base CPI-2019=100 General Index and food basket. | Through 2025-26 | Macroeconomic comparison and rural/semi-urban cost-of-living benchmarking. |
| `Consumer Price Index for Rural Labourer - By Group (Annual Average).xlsx` | Excel | 10 data rows, 7.4 KB | Rural Labourer annual price index series. | 1995-96 to 2024-25 | Macroeconomic inflation reference. |

---

## 3. Official Regulatory & Fund Disclosure PDFs (RAG Knowledge Base)

| File Name | AMC / Entity | Pages | Document Type & Key Content |
|---|---|---|---|
| `ABSL Factsheet_Aug 2026.pdf` | Aditya Birla Sun Life Mutual Fund | 255 | Comprehensive monthly factsheet: fund performance, portfolio holdings, expense ratios, risk-o-meter, fund managers, AUM. |
| `Empower for the month of October 2026.pdf` | Aditya Birla Sun Life Mutual Fund | 347 | Factsheet & portfolio disclosure for equity, debt, and hybrid schemes. |
| `active-factsheet---august-2026.pdf` | Mirae Asset Mutual Fund | 90 | Active equity & hybrid funds: Large Cap, Mid Cap, Great Consumer, Healthcare, Banking. Investment objectives, top 10 holdings, risk ratios. |
| `active-factsheet---october-2026.pdf` | Mirae Asset Mutual Fund | 126 | Updated active fund factsheet: Small Cap Fund, Mid Cap, Large Cap, ELSS, Flexi Cap. |
| `passive-factsheet---august-2026.pdf` | Mirae Asset Mutual Fund | 140 | ETFs and Index Funds: Nifty 50 ETF, Nifty Next 50 ETF, ESG, Factor ETFs. Tracking error, expense ratios, portfolio composition. |
| `passive-factsheet---september-2026.pdf` | Mirae Asset Mutual Fund | 142 | Passive funds & ETFs factsheet September 2026. Tracking error & TER disclosures. |
| `dsp-factsheet-april-2026.pdf` | DSP Mutual Fund | 167 | DSP schemes: Flexi Cap, Top 100, Small Cap, Healthcare, Overnight, Liquid, Gilt. |
| `dsp-factsheet-may-2026.pdf` | DSP Mutual Fund | 169 | DSP May 2026 factsheet. Performance versus benchmarks (NIFTY 50 TRI, S&P BSE 500 TRI). |
| `dsp-factsheet-august-2026.pdf` | DSP Mutual Fund | 180 | DSP August 2026 factsheet: detailed portfolio disclosures, exit loads, turnover ratios. |
| `dsp-factsheet_september-2026_final.pdf` | DSP Mutual Fund | 181 | DSP September 2026 factsheet: updated holdings, Sharpe ratio, standard deviation, beta. |
| `Presentation_Axis_Multi_Factor_Passive_Fo_F_Final_September_26_70833a0948.pdf` | Axis Mutual Fund | 47 | Scheme Information Document / Presentation: Axis Multi Factor Passive FoF. Factor investing principles, risk metrics, asset allocation. |
| `Presentation_Axis_Nifty_500_Index_Fund_September_26_pdf_4238ba84e6.pdf` | Axis Mutual Fund | 17 | Product presentation: Axis Nifty 500 Index Fund. Risk-o-meter, asset allocation, investment strategy, benchmark comparison. |

---

## 4. Data Coverage, Gaps, and Methodological Notes

1. **Backtesting Horizon**:
   - The two historical time-series Excel files provided (`NAV_2021-11-01_to_2026-10-28.xlsx` and `(1).xlsx`) contain daily NAVs starting in June/July 2026 through October 2026 (~96 daily observations). Despite the workbook header mentioning 2021, the actual scheme records start in mid-2026.
   - **Compliance with prompt instructions**: The backtesting engine is designed to execute against available empirical NAV series, calculate annualized metrics, and display explicit data-coverage warnings. The application does *not* fabricate fake 10-year daily historical NAVs.
2. **Current Fund Universe**:
   - `Mutual Fund NAVAll.txt` provides the complete live AMFI snapshot with 14,419 schemes. It contains scheme code, category, Direct vs Regular plan, Growth vs IDCW option, current NAV, and NAV date.
3. **Fund Metrics (AUM, TER, Sharpe, Beta, Tracking Error)**:
   - For schemes covered in the official PDF factsheets, exact figures are retrieved and cited via RAG.
   - For other schemes where factsheets are not loaded locally, fields without verified data will explicitly display "Not Disclosed in Local Dataset" rather than fictitious numbers or deceptive zeroes.
4. **Inflation Reference**:
   - RBI DBIE CPI series confirm average long-term headline CPI inflation in India between 5.0% and 6.5%. The Goal Planner utilizes 6.0% as a standard baseline, editable by the adviser.

