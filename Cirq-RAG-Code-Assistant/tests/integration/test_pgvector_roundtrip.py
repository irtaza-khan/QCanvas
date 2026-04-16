"""Opt-in integration test for the pgvector VectorStore backend.

Skipped unless ``CIRQ_RAG_DB_URL`` is set in the environment and points at a
Postgres instance that already has the pgvector extension installed and the
``cirq_rag.rag_knowledge_base`` table created (see
``scripts/sql/001_init_pgvector.sql``).

Run with::

    export CIRQ_RAG_DB_URL=postgresql://user:pass@host:5432/db
    pytest tests/integration/test_pgvector_roundtrip.py -v
"""

from __future__ import annotations

import os
import uuid

import numpy as np
import pytest


pytestmark = pytest.mark.skipif(
    not os.getenv("CIRQ_RAG_DB_URL"),
    reason="Set CIRQ_RAG_DB_URL to run the pgvector integration test.",
)


def _rand_unit_vector(dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(dim).astype(np.float32)
    vec /= np.linalg.norm(vec) or 1.0
    return vec


def test_add_search_get_roundtrip() -> None:
    from src.rag.vector_store import VectorStore

    dim = 1024
    store = VectorStore(embedding_dim=dim, vector_db_type="pgvector")

    # Use a unique prefix so this test is safe to run against a live DB.
    prefix = f"it-{uuid.uuid4().hex[:8]}-"
    ids = [prefix + str(i) for i in range(3)]
    contents = ["first example", "second example", "third example"]
    metadatas = [
        {"source": "test", "topic": "a", "content_hash": "h1"},
        {"source": "test", "topic": "b", "content_hash": "h2"},
        {"source": "test", "topic": "c", "content_hash": "h3"},
    ]
    vectors = np.stack([_rand_unit_vector(dim, seed=i) for i in range(3)])

    try:
        store.add(
            embeddings=vectors,
            ids=ids,
            metadatas=metadatas,
            contents=contents,
        )

        fetched = store.get_by_id(ids[0])
        assert fetched is not None
        assert fetched["content"] == contents[0]
        assert fetched["metadata"].get("topic") == "a"

        # Querying with vectors[1] should rank ids[1] first.
        results = store.search(vectors[1].reshape(1, -1), k=3, filter_dict={"source": "test"})
        assert results, "expected at least one query result"
        top_ids = [r["id"] for r in results[0]]
        assert ids[1] in top_ids
        assert top_ids[0] == ids[1]
    finally:
        # Best-effort cleanup so the table does not accumulate test rows.
        import psycopg

        with psycopg.connect(os.environ["CIRQ_RAG_DB_URL"], autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM cirq_rag.rag_knowledge_base WHERE doc_id = ANY(%s)",
                    (ids,),
                )
