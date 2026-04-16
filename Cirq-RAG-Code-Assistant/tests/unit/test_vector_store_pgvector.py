"""Unit tests for the pgvector VectorStore backend.

These tests stub psycopg and pgvector so no real database is needed. They
verify the SQL shape the backend emits (not the actual query semantics - that
lives in the integration test).
"""

from __future__ import annotations

import sys
import types
from typing import Any, List, Tuple
from unittest.mock import MagicMock

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Fake psycopg / pgvector implementation installed on sys.modules so
# `import psycopg` inside the module under test resolves to these stubs.
# ---------------------------------------------------------------------------


class FakeCursor:
    def __init__(self, conn: "FakeConnection") -> None:
        self.conn = conn
        self._rows: List[Tuple[Any, ...]] = []

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *_exc: Any) -> None:
        return None

    def execute(self, sql: str, params: Any = None) -> None:
        self.conn.executed.append((sql, params))
        # Simulate preflight checks so _init_pgvector does not blow up.
        normalized = " ".join(sql.split()).lower()
        if "from pg_extension where extname = 'vector'" in normalized:
            self._rows = [("vector",)]
        elif "information_schema.tables" in normalized:
            self._rows = [(1,)]
        elif "select count(*)" in normalized:
            self._rows = [(42,)]
        else:
            # Return whatever the test pre-loaded via conn.result_queue, else [].
            if self.conn.result_queue:
                self._rows = self.conn.result_queue.pop(0)
            else:
                self._rows = []

    def fetchone(self) -> Any:
        return self._rows[0] if self._rows else None

    def fetchall(self) -> List[Tuple[Any, ...]]:
        return list(self._rows)


class FakeConnection:
    def __init__(self) -> None:
        self.executed: List[Tuple[str, Any]] = []
        self.result_queue: List[List[Tuple[Any, ...]]] = []
        self.autocommit = True

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)

    def close(self) -> None:
        # Tests reuse the connection across assertions; close is a no-op.
        return None


def _install_fakes(monkeypatch: pytest.MonkeyPatch, conn: FakeConnection) -> None:
    psycopg_stub = types.ModuleType("psycopg")
    psycopg_stub.connect = MagicMock(return_value=conn)  # type: ignore[attr-defined]
    psycopg_stub.Connection = FakeConnection  # type: ignore[attr-defined]

    pgvector_stub = types.ModuleType("pgvector")
    pgvector_psycopg_stub = types.ModuleType("pgvector.psycopg")
    pgvector_psycopg_stub.register_vector = MagicMock()  # type: ignore[attr-defined]
    pgvector_stub.psycopg = pgvector_psycopg_stub  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "psycopg", psycopg_stub)
    monkeypatch.setitem(sys.modules, "pgvector", pgvector_stub)
    monkeypatch.setitem(sys.modules, "pgvector.psycopg", pgvector_psycopg_stub)

    # Make sure a fresh import of vector_store picks up the stubs and the
    # PGVECTOR_AVAILABLE flag flips to True.
    sys.modules.pop("src.rag.vector_store", None)


@pytest.fixture
def vector_store_module(monkeypatch: pytest.MonkeyPatch):
    conn = FakeConnection()
    _install_fakes(monkeypatch, conn)
    monkeypatch.setenv("CIRQ_RAG_DB_URL", "postgresql://u:p@localhost/x")

    import importlib

    import src.rag.vector_store as vs_module  # noqa: WPS433 - runtime import

    importlib.reload(vs_module)
    return vs_module, conn


def _make_store(vector_store_module) -> Any:
    vs_module, _conn = vector_store_module
    return vs_module.VectorStore(embedding_dim=1024, vector_db_type="pgvector")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_init_performs_preflight_checks(vector_store_module) -> None:
    vs_module, conn = vector_store_module
    vs_module.VectorStore(embedding_dim=1024, vector_db_type="pgvector")

    joined = " ".join(sql for sql, _ in conn.executed).lower()
    assert "pg_extension" in joined
    assert "information_schema.tables" in joined


def test_init_raises_without_dsn(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CIRQ_RAG_DB_URL", raising=False)

    conn = FakeConnection()
    _install_fakes(monkeypatch, conn)
    import importlib

    import src.rag.vector_store as vs_module

    importlib.reload(vs_module)

    with pytest.raises(RuntimeError, match="CIRQ_RAG_DB_URL"):
        vs_module.VectorStore(embedding_dim=1024, vector_db_type="pgvector")


def test_add_requires_contents(vector_store_module) -> None:
    store = _make_store(vector_store_module)
    embeddings = np.random.rand(1, 1024).astype(np.float32)

    with pytest.raises(ValueError, match="contents"):
        store.add(embeddings=embeddings, ids=["a"], metadatas=[{}])


def test_add_emits_upsert_with_all_columns(vector_store_module) -> None:
    store = _make_store(vector_store_module)
    _, conn = vector_store_module

    before = len(conn.executed)
    store.add(
        embeddings=np.random.rand(2, 1024).astype(np.float32),
        ids=["doc-1", "doc-2"],
        metadatas=[{"source": "designer"}, {"source": "optimizer"}],
        contents=["first", "second"],
    )

    upserts = [e for e in conn.executed[before:] if "INSERT INTO" in e[0]]
    assert len(upserts) == 2
    sql = upserts[0][0]
    assert "ON CONFLICT (doc_id) DO UPDATE" in sql
    assert "embedding" in sql and "content" in sql and "metadata" in sql


def test_search_emits_cosine_ordering(vector_store_module) -> None:
    store = _make_store(vector_store_module)
    _, conn = vector_store_module

    conn.result_queue.append([("doc-1", "hello", {"source": "designer"}, 0.9, 0.1)])

    results = store.search(np.random.rand(1, 1024).astype(np.float32), k=3)

    assert len(results) == 1
    assert results[0][0]["id"] == "doc-1"
    assert results[0][0]["content"] == "hello"

    search_sql = next(e[0] for e in conn.executed if "ORDER BY embedding <=>" in e[0])
    assert "LIMIT %s" in search_sql


def test_save_and_load_are_noops(vector_store_module) -> None:
    store = _make_store(vector_store_module)
    _, conn = vector_store_module

    before = len(conn.executed)

    store.save("/tmp/ignored")
    store.load("/tmp/ignored")

    assert len(conn.executed) == before


def test_size_queries_count_star(vector_store_module) -> None:
    store = _make_store(vector_store_module)
    _, conn = vector_store_module

    assert store.size() == 42
    assert any("SELECT count(*)" in sql for sql, _ in conn.executed)
