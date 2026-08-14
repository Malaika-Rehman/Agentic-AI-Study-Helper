"""
ChromaDB vector store layer.
Stores document chunks as embeddings for semantic RAG search.
DB folder: chroma_db/ (auto-created in project root)
"""
import os
import re
import chromadb
from chromadb.config import Settings

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")


def _client():
    return chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False)
    )


def _collection(client, user_email: str):
    """Each user gets their own collection."""
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", user_email)
    return client.get_or_create_collection(
        name=f"user_{safe_name}",
        metadata={"hnsw:space": "cosine"}
    )


# ─────────────────────────────────────────────
# CHUNK TEXT
# ─────────────────────────────────────────────
def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for better RAG retrieval."""
    words  = text.split()
    chunks = []
    start  = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


# ─────────────────────────────────────────────
# STORE DOCUMENT CHUNKS
# ─────────────────────────────────────────────
def store_document(user_email: str, doc_id: int, text: str):
    """
    Chunk the document text and store in ChromaDB.
    Uses doc_id as namespace so chunks from different docs don't mix.
    """
    try:
        client     = _client()
        collection = _collection(client, user_email)

        # Remove old chunks for this doc_id if re-uploading
        try:
            existing = collection.get(where={"doc_id": doc_id})
            if existing["ids"]:
                collection.delete(ids=existing["ids"])
        except Exception:
            pass

        chunks = _chunk_text(text)
        if not chunks:
            return

        ids        = [f"doc{doc_id}_chunk{i}" for i in range(len(chunks))]
        metadatas  = [{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]

        # Store in batches of 50
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            collection.add(
                documents=metadatas[i:i+batch_size],
                ids=ids[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
            )
            # Add actual text as documents
            collection.update(
                ids=ids[i:i+batch_size],
                documents=chunks[i:i+batch_size],
            )
    except Exception as e:
        print(f"[ChromaDB] store_document error: {e}")


# ─────────────────────────────────────────────
# RETRIEVE RELEVANT CHUNKS
# ─────────────────────────────────────────────
def retrieve_chunks(user_email: str, doc_id: int, query: str, n_results: int = 5) -> str:
    """
    Find the most semantically relevant chunks for a query.
    Returns them joined as a single context string.
    """
    try:
        client     = _client()
        collection = _collection(client, user_email)

        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count()),
            where={"doc_id": doc_id},
        )

        chunks = results.get("documents", [[]])[0]
        if not chunks:
            return ""
        return "\n\n".join(chunks)

    except Exception as e:
        print(f"[ChromaDB] retrieve_chunks error: {e}")
        return ""


# ─────────────────────────────────────────────
# DELETE USER'S DOCUMENT CHUNKS
# ─────────────────────────────────────────────
def delete_document(user_email: str, doc_id: int):
    try:
        client     = _client()
        collection = _collection(client, user_email)
        existing   = collection.get(where={"doc_id": doc_id})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception as e:
        print(f"[ChromaDB] delete_document error: {e}")
