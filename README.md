# AI Investment Adviser Co-pilot (Zeckathon PS-04)
### *"A Co-pilot That Lets One Adviser Serve 1,000 Clients Safely"*

A SEBI-registered Investment Adviser (RIA) co-pilot prototype that automates client profiling, goal-based mutual fund plan construction, and factsheet research with grounded citations, while keeping the human adviser in control of every client-facing recommendation.

---

## 1. System Architecture & Features

```
Zeckathon/
├── app.py                     # Main Streamlit Application with Multi-Page Navigation
├── run_tests.py               # Unified Automated Test Suite Runner (19 Tests)
├── config.py                  # System Configuration & Path Constants
├── core/
│   ├── client.py              # Client Profile Data Models & 6 Test Personas
│   ├── risk_engine.py         # Dual Risk Engine: Capacity vs Tolerance Conflict Resolution
│   ├── financial_calc.py      # Deterministic Calculations: Target Corpus, SIP, Glidepath, Sensitivity
│   ├── data_loader.py         # AMFI NAV Master (14,419 funds), SIF Loader, RBI CPI Series
│   ├── fund_analysis.py       # Direct/Growth Filtering, Explainable Ranking, Factsheet Metrics
│   ├── backtesting.py         # Multi-Asset Empirical Backtester, Drawdown, Sharpe, Limitations
│   ├── suitability.py         # Deterministic SEBI Guardrails & Fiduciary Rules Engine
│   └── approval.py            # Adviser Approval Workflow & Tamper-Evident Audit Trail
├── rag/
│   ├── ingestion.py           # PyMuPDF Page-by-Page PDF Chunker & Metadata Extractor
│   ├── retrieval.py           # ChromaDB Semantic Vector Index & Passage Search
│   └── llm.py                 # Grounded LLM Research Engine (Groq/Agnostic) + Diagnostic Mode
├── ui/
│   ├── components.py          # Institutional Visualizations (Plotly Donut, Glidepath, Curve, Heatmap)
│   ├── page_dashboard.py      # Page 1: Operational Overview & Pending Queue
│   ├── page_clients.py        # Page 2: Client Intake & Dual Risk Profiling
│   ├── page_goal_planner.py   # Page 3: Goal-Based Compounding Planner & Sensitivity
│   ├── page_fund_explorer.py  # Page 4: AMFI Mutual Fund Universe & Verified Disclosures
│   ├── page_ai_assistant.py   # Page 5: RAG Document Research with Page Citations
│   ├── page_backtest.py       # Page 6: Portfolio Backtesting & Historical Analysis
│   └── page_adviser_review.py # Page 7: Fiduciary Review, Guardrails & Sign-Off
├── data/                      # 12 Factsheet PDFs, 4 Spreadsheets, AMFI Master
├── tests/                     # Modular Pytest Unit Tests
├── DATA_INVENTORY.md          # Comprehensive Data Catalog
├── TEST_REPORT.md             # Test Execution Log & Validation Proofs
├── .env.example               # Environment Variables Template
└── .gitignore                 # Secrets & Local Runtime File Protection
```

---

## 2. Key Deliverables Implemented

| ID | Core Capability | Implementation Details |
|---|---|---|
| **01** | **Dual Risk Profiling Engine** | Separates **Financial Risk Capacity** (mathematical ability based on savings rate, liquidity runway, liabilities, dependants, horizon) from **Behavioral Risk Tolerance** (psychological willingness). Transparent rules resolve conflicts (capacity serves as safety ceiling). |
| **02** | **Deterministic Goal Planner** | Inflation-adjusted corpus compounding ($C_{future} = C_{today} \times (1+r_{inf})^t$), annuity-due monthly SIP formula with payment timing, real return (Fisher equation), and systematic de-risking glide paths to maturity. |
| **03** | **Fund Screening & Empirical Backtest** | Screens 14,419 AMFI schemes. Filters for Direct Plans (mandatory for RIAs) and Growth options. Empirical daily backtest on available series with CAGR, volatility, drawdown, and transparent data coverage warnings. |
| **04** | **Grounded RAG Assistant** | Ingests official PDF factsheets (DSP, Mirae Asset, Axis, ABSL). Generates answers citing exact source document and page number. Automatically falls back to **Diagnostic Mode** when API keys are absent. |
| **05** | **Fiduciary Suitability Guardrails** | Deterministic Python rules block unrealistic return expectations (SEBI Reg 15), enforce senior citizen equity caps ($\le 30\%$), flag emergency fund deficiencies, and detect Regular Plan commission conflicts. |
| **06** | **Human-in-the-Loop Sign-off** | All plans enter a "Pending Review" state. Advisers review calculations, fund rationale, and guardrail warnings before approving, rejecting, or requesting changes with an immutable JSON audit log. |

---

## 3. The Six Problem Statement Test Personas

1. **Fresh Graduate (Bengaluru, Age 23)**: ₹55k take-home, no dependants. Goal: Emergency fund (₹1.5 Lakh) then wealth creation. High capacity, moderate tolerance.
2. **Young Couple (Pune, Age 31)**: Dual income ₹1.6L/mo, home-loan EMI ₹40k, 1 child. Goal: Higher education (₹35 Lakh in 15 years).
3. **Small Business Owner (Surat, Age 44)**: Irregular income, high cash holdings (₹30L in savings/current account). Goal: Retirement at 58.
4. **Doctor (Patna, Age 38)**: High income (₹3.5L/mo), under-invested in FDs, risk-averse. **Conflict Flagged**: High capacity vs Conservative tolerance. Recommended stepped STP.
5. **Retiree (Chennai, Age 68)**: ₹80 Lakh lump sum corpus, pension ₹35k/mo. **Guardrail Enforced**: Senior citizen equity capped at 25% for capital preservation & SWP.
6. **Aggressive Trader (Mumbai, Age 29)**: Recent ₹6L F&O losses, wants "high returns fast / guaranteed 20%+". **Guardrail Enforced**: Zero guarantee mandate triggered, equity capped to financial capacity.

---

## 4. Installation & Startup Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.14 on Windows)
- Git

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
# Or install core packages directly:
pip install streamlit plotly pymupdf chromadb openpyxl pandas numpy pydantic groq
```

### Step 2: Configure Environment (Optional for Groq LLM)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional: If `GROQ_API_KEY` is not provided, the research assistant runs in **Offline Diagnostic Retrieval Mode**, displaying exact retrieved excerpts and verified citations directly.)*

### Step 3: Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Step 4: Run the Automated Test Suite
```bash
python run_tests.py
```
Expected output: **19 PASSED | 0 FAILED**.

---

## 5. Compliance & Data Integrity Disclosures

1. **Backtesting Period Coverage**: The local historical daily NAV files (`NAV_2021-11-01_to_2026-10-28.xlsx` and `(1).xlsx`) contain ~77 trading sessions (June to October 2026). The application reports empirical metrics over available observations and explicitly discloses this limitation rather than fabricating synthetic 10-year market data.
2. **Factsheet Metrics**: Schemes covered in local PDFs (DSP, Mirae Asset, Axis, ABSL) display verified TER, AUM, and manager tenure. For other schemes in the AMFI snapshot, unverified metrics are labeled "Not Disclosed in Local Dataset" rather than showing false zeros.
3. **Fiduciary Principle**: Automated suitability checks do not substitute for human adviser approval. Unapproved plans are strictly barred from distribution to clients.

