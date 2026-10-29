"""
Document Retrieval Module.
Performs semantic vector search over persisted ChromaDB index,
filters by document type if requested, and formats retrieved passages
with verified source filenames, page citations, and relevance distances.
"""

from typing import List, Dict, Any, Optional
import os
import chromadb
from rag.ingestion import CHROMA_PERSIST_DIR, COLLECTION_NAME, get_embedding_function, build_or_get_vector_store

_CLIENT: Optional[chromadb.PersistentClient] = None
_COLLECTION: Optional[chromadb.Collection] = None

def get_collection() -> chromadb.Collection:
    """Gets or initializes the cached Chroma collection."""
    global _CLIENT, _COLLECTION
    if _COLLECTION is not None:
        return _COLLECTION

    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    _CLIENT = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    ef = get_embedding_function()
    
    try:
        _COLLECTION = _CLIENT.get_collection(name=COLLECTION_NAME, embedding_function=ef)
    except Exception:
        # If collection does not exist, build it
        _COLLECTION = build_or_get_vector_store()
        
    return _COLLECTION

def search_documents(
    query: str,
    top_k: int = 5,
    source_file_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves top_k relevant passages from the indexed fund documents.
    Attaches page numbers, source filenames, and clean text snippets.
    """
    collection = get_collection()
    if collection.count() == 0:
        return []

    where_filter = None
    if source_file_filter and source_file_filter != "All":
        where_filter = {"source_file": source_file_filter}

    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter
        )
    except Exception as e:
        print(f"Error querying ChromaDB: {e}")
        return []

    formatted = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else []
        ids = results["ids"][0] if "ids" in results and results["ids"] else []
        distances = results["distances"][0] if "distances" in results and results["distances"] else []

        for i in range(len(docs)):
            meta = metas[i] if i < len(metas) else {}
            dist = distances[i] if i < len(distances) else 1.0
            # Convert cosine distance to pseudo-similarity percentage
            sim_score = max(0.0, min(100.0, (1.0 - (dist / 2.0)) * 100.0))

            formatted.append({
                "chunk_id": ids[i] if i < len(ids) else f"chunk_{i}",
                "text": docs[i],
                "source_file": meta.get("source_file", "Unknown Document"),
                "page_number": meta.get("page_number", 1),
                "total_pages": meta.get("total_pages", 1),
                "doc_type": meta.get("doc_type", "Factsheet"),
                "similarity_score": round(sim_score, 1),
                "citation": f"{meta.get('source_file', 'Document')}, Page {meta.get('page_number', 1)}"
            })

    return formatted

