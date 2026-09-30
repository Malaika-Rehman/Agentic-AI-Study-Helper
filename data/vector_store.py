"""
Local vector store layer for Agentic AI Study Helper.

This version intentionally does NOT use ChromaDB's default embedding
function because Chroma's default embedding model can trigger a large
ONNX model download on every new laptop.

Instead, this file creates deterministic lightweight local embeddings
using Python's built-in hashlib module.

Advantages:
- No HuggingFace download
- No ONNX model download
- Works offline
- Same behavior across laptops
- ChromaDB is still used for persistent vector storage
"""

import os
import re
import math
import hashlib

import chromadb
from chromadb.config import Settings


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

CHROMA_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "chroma_db"
    )
)


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

# Keep this at 384 so the vector size is fixed and compact.
EMBEDDING_DIMENSION = 384


# ---------------------------------------------------------------------
# Chroma client
# ---------------------------------------------------------------------

def _client():
    """
    Create the persistent ChromaDB client.

    No embedding model is configured here.
    """

    os.makedirs(CHROMA_PATH, exist_ok=True)

    return chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(
            anonymized_telemetry=False
        )
    )


# ---------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------

def _collection(client, user_email: str):
    """
    Each user gets a separate ChromaDB collection.
    """

    safe_name = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        user_email
    )

    return client.get_or_create_collection(
        name=f"user_{safe_name}",
        metadata={
            "hnsw:space": "cosine"
        },
        embedding_function=None,
    )


# ---------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------

def _chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> list[str]:
    """
    Split document text into overlapping chunks.
    """

    if not text:
        return []

    text = str(text).strip()

    if not text:
        return []

    words = text.split()

    if not words:
        return []

    chunks = []

    start = 0
    step = max(1, chunk_size - overlap)

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words)
        )

        chunk = " ".join(
            words[start:end]
        ).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start += step

    return chunks


# ---------------------------------------------------------------------
# Local embedding
# ---------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """
    Convert text into normalized tokens.
    """

    if not text:
        return []

    text = text.lower()

    return re.findall(
        r"[a-zA-Z0-9_]+",
        text
    )


def _hash_index(value: str) -> int:
    """
    Convert a token into a deterministic vector position.
    """

    digest = hashlib.sha256(
        value.encode("utf-8")
    ).digest()

    number = int.from_bytes(
        digest[:8],
        byteorder="little",
        signed=False
    )

    return number % EMBEDDING_DIMENSION


def _hash_sign(value: str) -> float:
    """
    Give each hashed feature a deterministic +1 / -1 sign.
    """

    digest = hashlib.sha256(
        ("sign:" + value).encode("utf-8")
    ).digest()

    number = int.from_bytes(
        digest[:8],
        byteorder="little",
        signed=False
    )

    return 1.0 if number % 2 == 0 else -1.0


def _embed_text(text: str) -> list[float]:
    """
    Generate a deterministic lightweight local vector.

    Uses word and word-pair hashing.

    No external model or internet connection is required.
    """

    vector = [
        0.0
        for _ in range(EMBEDDING_DIMENSION)
    ]

    tokens = _tokenize(text)

    if not tokens:
        return vector

    # ---------------------------------------------------------------
    # Word features
    # ---------------------------------------------------------------

    for token in tokens:

        index = _hash_index(
            "word:" + token
        )

        vector[index] += _hash_sign(
            "word:" + token
        )

    # ---------------------------------------------------------------
    # Bigram features
    # ---------------------------------------------------------------

    for i in range(len(tokens) - 1):

        bigram = (
            tokens[i]
            + "_"
            + tokens[i + 1]
        )

        index = _hash_index(
            "bigram:" + bigram
        )

        vector[index] += (
            0.5
            * _hash_sign(
                "bigram:" + bigram
            )
        )

    # ---------------------------------------------------------------
    # Normalize vector
    # ---------------------------------------------------------------

    magnitude = math.sqrt(
        sum(value * value for value in vector)
    )

    if magnitude > 0:

        vector = [
            value / magnitude
            for value in vector
        ]

    return vector


def _embed_documents(
    documents: list[str]
) -> list[list[float]]:
    """
    Generate embeddings for multiple documents.
    """

    return [
        _embed_text(document)
        for document in documents
    ]


# ---------------------------------------------------------------------
# Store document
# ---------------------------------------------------------------------

def store_document(
    user_email: str,
    doc_id: int,
    text: str
):
    """
    Chunk and store a document in ChromaDB.

    Existing chunks for the same document are removed first.
    """

    try:

        print(
            f"[ChromaDB] Starting indexing for document {doc_id}..."
        )

        client = _client()

        collection = _collection(
            client,
            user_email
        )

        # -------------------------------------------------------------
        # Remove previous chunks
        # -------------------------------------------------------------

        try:

            existing = collection.get(
                where={
                    "doc_id": doc_id
                }
            )

            existing_ids = existing.get(
                "ids",
                []
            )

            if existing_ids:

                collection.delete(
                    ids=existing_ids
                )

                print(
                    f"[ChromaDB] Removed "
                    f"{len(existing_ids)} old chunks."
                )

        except Exception as e:

            print(
                f"[ChromaDB] Could not remove old chunks: {e}"
            )

        # -------------------------------------------------------------
        # Create chunks
        # -------------------------------------------------------------

        chunks = _chunk_text(text)

        if not chunks:

            print(
                "[ChromaDB] No text chunks found."
            )

            return False

        print(
            f"[ChromaDB] Created {len(chunks)} chunks."
        )

        # -------------------------------------------------------------
        # IDs
        # -------------------------------------------------------------

        ids = [
            f"doc{doc_id}_chunk{i}"
            for i in range(len(chunks))
        ]

        # -------------------------------------------------------------
        # Metadata
        # -------------------------------------------------------------

        metadatas = [
            {
                "doc_id": int(doc_id),
                "chunk_index": int(i)
            }
            for i in range(len(chunks))
        ]

        # -------------------------------------------------------------
        # Local embeddings
        # -------------------------------------------------------------

        print(
            "[ChromaDB] Creating local embeddings..."
        )

        embeddings = _embed_documents(
            chunks
        )

        print(
            "[ChromaDB] Local embeddings created."
        )

        # -------------------------------------------------------------
        # Store in batches
        # -------------------------------------------------------------

        batch_size = 50

        for i in range(
            0,
            len(chunks),
            batch_size
        ):

            end = min(
                i + batch_size,
                len(chunks)
            )

            collection.add(
                documents=chunks[i:end],
                embeddings=embeddings[i:end],
                ids=ids[i:end],
                metadatas=metadatas[i:end],
            )

            print(
                f"[ChromaDB] Indexed "
                f"{end}/{len(chunks)} chunks."
            )

        print(
            f"[ChromaDB] Document {doc_id} indexed successfully."
        )

        return True

    except Exception as e:

        print(
            f"[ChromaDB] store_document error: {e}"
        )

        return False


# ---------------------------------------------------------------------
# Retrieve chunks
# ---------------------------------------------------------------------

def retrieve_chunks(
    user_email: str,
    doc_id: int,
    query: str,
    n_results: int = 5
) -> str:
    """
    Find the most relevant chunks for a question.
    """

    try:

        client = _client()

        collection = _collection(
            client,
            user_email
        )

        # -------------------------------------------------------------
        # Get chunks belonging to this document
        # -------------------------------------------------------------

        matching = collection.get(
            where={
                "doc_id": int(doc_id)
            }
        )

        matching_ids = matching.get(
            "ids",
            []
        )

        if not matching_ids:
            return ""

        result_count = min(
            n_results,
            len(matching_ids)
        )

        # -------------------------------------------------------------
        # Create query embedding locally
        # -------------------------------------------------------------

        query_embedding = _embed_text(
            query
        )

        # -------------------------------------------------------------
        # Chroma vector search
        # -------------------------------------------------------------

        results = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=result_count,
            where={
                "doc_id": int(doc_id)
            }
        )

        documents = results.get(
            "documents",
            [[]]
        )

        if not documents:
            return ""

        chunks = documents[0]

        if not chunks:
            return ""

        return "\n\n".join(
            chunks
        )

    except Exception as e:

        print(
            f"[ChromaDB] retrieve_chunks error: {e}"
        )

        return ""


# ---------------------------------------------------------------------
# Delete document
# ---------------------------------------------------------------------

def delete_document(
    user_email: str,
    doc_id: int
):
    """
    Delete all ChromaDB chunks belonging to a document.
    """

    try:

        client = _client()

        collection = _collection(
            client,
            user_email
        )

        existing = collection.get(
            where={
                "doc_id": int(doc_id)
            }
        )

        ids = existing.get(
            "ids",
            []
        )

        if ids:

            collection.delete(
                ids=ids
            )

            print(
                f"[ChromaDB] Deleted "
                f"{len(ids)} chunks for document {doc_id}."
            )

        return True

    except Exception as e:

        print(
            f"[ChromaDB] delete_document error: {e}"
        )

        return False