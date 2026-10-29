"""
Automated Unit Tests for RAG Document Ingestion, Retrieval, and Citations.
Verifies that retrieved chunks retain valid filenames, page numbers, and non-empty text.
"""

import pytest
from rag.retrieval import search_documents
from rag.llm import generate_grounded_answer

def test_document_retrieval_citations():
    results = search_documents("DSP Large Cap benchmark objective", top_k=3)
    assert len(results) > 0
    for r in results:
        assert "source_file" in r
        assert "page_number" in r
        assert r["page_number"] >= 1
        assert len(r["text"].strip()) > 30
        assert r["source_file"].endswith(".pdf")
        assert "Page" in r["citation"]

def test_grounded_answer_structure():
    res = generate_grounded_answer("What is the investment objective of DSP Top 100 or Large Cap Fund?")
    assert "answer" in res
    assert "citations" in res
    assert "diagnostic_mode" in res
    assert len(res["citations"]) > 0
    assert any("Page" in c for c in res["citations"])

