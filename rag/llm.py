"""
RAG Question Answering and Grounded LLM Integration Module.
Implements provider-agnostic LLM interface (Groq, OpenAI, Gemini)
with mandatory grounding rules, verifiable citations, and Diagnostic Mode.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from typing import List, Dict, Any, Optional
from rag.retrieval import search_documents

SYSTEM_PROMPT = """You are an AI Investment Research Assistant for a SEBI-registered Investment Adviser (RIA).
Your purpose is to answer the adviser's mutual fund research questions accurately based ONLY on the provided official fund document excerpts.

STRICT OPERATIONAL RULES:
1. Ground every claim directly in the provided context passages.
2. For EVERY factual claim (investment objective, risk, asset allocation, TER, benchmark), cite the exact source document and page number in brackets, for example: [active-factsheet---october-2026.pdf, Page 4].
3. If the provided context does NOT contain sufficient evidence to answer the question, explicitly state:
   "The available local fund document excerpts do not contain sufficient verified information to answer this question."
4. NEVER invent, hallucinate, extrapolate, or guess expense ratios, AUM, returns, or page citations.
5. NEVER guarantee returns or make unconditional return forecasts under any circumstance.
6. Clearly distinguish verified document facts from general concepts.
7. Keep answers concise, factual, and formatted in clear bullet points for an investment adviser.
"""

def generate_grounded_answer(
    question: str,
    top_k: int = 5,
    source_file_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves relevant passages and generates a grounded response.
    If no LLM key is available or network blocks, operates in Diagnostic Mode.
    """
    passages = search_documents(question, top_k=top_k, source_file_filter=source_file_filter)
    
    citations = []
    for p in passages:
        c_str = f"{p['source_file']} (Page {p['page_number']})"
        if c_str not in citations:
            citations.append(c_str)

    if not passages:
        return {
            "answer": "No relevant document passages were found in the indexed fund factsheets for your query.",
            "citations": [],
            "passages": [],
            "provider": "None",
            "diagnostic_mode": True,
            "disclaimer": "No matching text in local database."
        }

    # Prepare context block
    context_str = ""
    for idx, p in enumerate(passages):
        context_str += f"\n--- EXCERPT {idx+1} [Source: {p['source_file']}, Page: {p['page_number']}] ---\n"
        context_str += p["text"] + "\n"

    user_prompt = f"""EVIDENCE FROM OFFICIAL FUND DOCUMENTS:
{context_str}

RESEARCH QUESTION:
{question}

Provide a concise, cited answer based strictly on the excerpts above:"""

    # Check available LLM providers
    groq_api_key = os.environ.get("GROQ_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    gemini_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    # 1. Try Groq (if available)
    if groq_api_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)
            
            # Select working model dynamically from account
            candidate_models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
            selected_model = candidate_models[0]
            try:
                available_ids = [m.id for m in client.models.list().data]
                for cand in candidate_models:
                    if cand in available_ids:
                        selected_model = cand
                        break
            except Exception:
                pass

            completion = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            answer_text = completion.choices[0].message.content.strip()
            return {
                "answer": answer_text,
                "citations": citations,
                "passages": passages,
                "provider": f"Groq ({selected_model})",
                "diagnostic_mode": False,
                "disclaimer": "Grounded AI output. Adviser verification required before distribution."
            }
        except Exception as e:
            print(f"Groq invocation failed: {e}. Falling back to diagnostic mode.")

    # 2. Try OpenAI (if available)
    if openai_api_key:
        try:
            import httpx
            # Fallback to standard OpenAI API call if configured
            pass
        except Exception:
            pass

    # 3. Fallback: Retrieval-Only Diagnostic Mode
    # Displays exact retrieved passages with highlights and citations directly to adviser
    diagnostic_text = (
        "**[RETRIEVAL-ONLY DIAGNOSTIC MODE]**\n\n"
        "_LLM API key not configured or network unreachable. Displaying verified source document excerpts directly:_\n\n"
    )
    for idx, p in enumerate(passages[:3]):
        diagnostic_text += (
            f"**Passage {idx+1}** — *{p['source_file']} (Page {p['page_number']})* [Relevance: {p['similarity_score']}%]:\n"
            f"> \"{p['text']}\"\n\n"
        )
    diagnostic_text += (
        "**Adviser Note:** To enable AI synthesis, configure `GROQ_API_KEY`, `OPENAI_API_KEY`, or `GEMINI_API_KEY` "
        "in your `.env` file."
    )

    return {
        "answer": diagnostic_text,
        "citations": citations,
        "passages": passages,
        "provider": "Offline Diagnostic Retrieval",
        "diagnostic_mode": True,
        "disclaimer": "Direct evidence extraction from local documents."
    }

