"""
Page 5: RAG-Powered AI Investment Research Assistant.
Queries the local Chroma vector database of official fund factsheets and SIDs,
generates concise answers grounded strictly in retrieved passages,
and attaches page-level citations with zero hallucination.
"""

import streamlit as st
from rag.llm import generate_grounded_answer
from rag.retrieval import search_documents

def render_ai_assistant_page():
    st.title("🤖 RAG Fund Research Assistant")
    st.markdown(
        "Ask factual questions about mutual fund objectives, asset allocations, risk-o-meters, and expenses. "
        "Every claim is grounded in official factsheets in `data/` and cited by page number."
    )

    sample_queries = [
        "What is the investment objective and benchmark of DSP Large Cap / Top 100 Equity Fund?",
        "What are the risk factors and asset allocation of Axis Nifty 500 Index Fund?",
        "What does the Mirae Asset Factsheet disclose about Midcap and Small Cap Funds?",
        "What does the factsheet say about expense ratios and tracking errors of passive funds?"
    ]

    # Initialize session state for RAG query and results
    if "rag_query" not in st.session_state:
        st.session_state["rag_query"] = sample_queries[0]
    if "rag_last_result" not in st.session_state:
        st.session_state["rag_last_result"] = None
    if "rag_trigger_search" not in st.session_state:
        st.session_state["rag_trigger_search"] = False

    def select_prompt(text: str):
        st.session_state["rag_query"] = text
        st.session_state["rag_trigger_search"] = True

    # Suggested Prompts
    st.markdown("##### 💡 Suggested Research Questions (Click to run):")
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        st.button(f"🔍 {sample_queries[0]}", on_click=select_prompt, args=(sample_queries[0],), use_container_width=True)
        st.button(f"🔍 {sample_queries[1]}", on_click=select_prompt, args=(sample_queries[1],), use_container_width=True)
    with col_q2:
        st.button(f"🔍 {sample_queries[2]}", on_click=select_prompt, args=(sample_queries[2],), use_container_width=True)
        st.button(f"🔍 {sample_queries[3]}", on_click=select_prompt, args=(sample_queries[3],), use_container_width=True)

    st.markdown("---")

    # Query Input Box (State-bound)
    query_input = st.text_input(
        "Enter Fund Research Question:",
        key="rag_query",
        placeholder="e.g. What is the investment strategy of Axis Multi Factor FoF?"
    )

    col_opt1, col_opt2 = st.columns([1, 1])
    with col_opt1:
        doc_filter = st.selectbox(
            "Filter by Source Document:",
            ["All", "dsp-factsheet_september-2026_final.pdf", "active-factsheet---october-2026.pdf", "passive-factsheet---september-2026.pdf", "Presentation_Axis_Nifty_500_Index_Fund_September_26_pdf_4238ba84e6.pdf", "Presentation_Axis_Multi_Factor_Passive_Fo_F_Final_September_26_70833a0948.pdf", "ABSL Factsheet_Aug 2026.pdf"]
        )
    with col_opt2:
        top_k = st.slider("Passages to Retrieve (Top K):", min_value=2, max_value=8, value=4)

    search_clicked = st.button("🚀 Search Fund Documents & Generate Answer", type="primary", use_container_width=True)

    # Determine if search should execute
    should_run_search = search_clicked or st.session_state.get("rag_trigger_search", False)
    # Reset trigger
    st.session_state["rag_trigger_search"] = False

    if should_run_search:
        clean_query = st.session_state["rag_query"].strip()
        if not clean_query:
            st.warning("Please enter a question or select one of the suggested prompts above.")
        else:
            with st.spinner("Retrieving factsheet passages and verifying evidence..."):
                result = generate_grounded_answer(
                    question=clean_query,
                    top_k=top_k,
                    source_file_filter=None if doc_filter == "All" else doc_filter
                )
                st.session_state["rag_last_result"] = result

    # Display Active Result
    res = st.session_state.get("rag_last_result")
    if res:
        # Provider Badge
        p_badge = "🟢 " + res["provider"] if not res.get("diagnostic_mode") else "🔵 " + res["provider"]
        st.markdown(f"**Research Engine Status**: `{p_badge}`")

        # Answer Presentation
        st.markdown("### 📝 Grounded Research Summary")
        st.markdown(res["answer"])

        # Citations Section
        st.markdown("---")
        st.subheader("📚 Verified Source Citations")
        if res.get("citations"):
            for c in res["citations"]:
                st.markdown(f"- 📄 `{c}`")
        else:
            st.caption("No direct citations found.")

        # Retrieved Passages Expander
        with st.expander("🔍 View Raw Retrieved Context Passages (Evidence Audit)", expanded=False):
            for idx, p in enumerate(res.get("passages", [])):
                st.markdown(f"**Passage {idx+1}** — *{p['source_file']} (Page {p['page_number']})* [Relevance Score: {p['similarity_score']}%]")
                st.markdown(f"> \"{p['text']}\"")
                st.markdown("---")

        st.caption(f"🛡️ **Fiduciary Grounding Notice**: {res.get('disclaimer', '')}")
