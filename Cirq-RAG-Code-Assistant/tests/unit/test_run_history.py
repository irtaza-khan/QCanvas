"""Unit tests for the run-history storage backends."""

from __future__ import annotations

from datetime import datetime

import pytest

from src.run_history import (
    InMemoryRunHistory,
    RedisRunHistory,
    build_run_history_store,
)


def _make_run(run_id: str, *, created_at: datetime, prompt: str = "hello") -> dict:
    return {
        "run_id": run_id,
        "created_at": created_at.isoformat(),
        "prompt": prompt,
        "status": "completed",
        "agents": [{"name": "designer", "status": "success"}],
    }


# ---------------------------------------------------------------------------
# InMemoryRunHistory
# ---------------------------------------------------------------------------


def test_in_memory_put_get_roundtrip() -> None:
    store = InMemoryRunHistory(max_entries=5)
    run = _make_run("abc", created_at=datetime(2026, 4, 17))

    store.put("abc", run)

    assert store.get("abc") == run
    assert store.get("missing") is None


def test_in_memory_list_is_reverse_chronological() -> None:
    store = InMemoryRunHistory(max_entries=5)
    store.put("a", _make_run("a", created_at=datetime(2026, 1, 1)))
    store.put("b", _make_run("b", created_at=datetime(2026, 3, 1)))
    store.put("c", _make_run("c", created_at=datetime(2026, 2, 1)))

    listed = store.list(limit=10)

    assert [r["run_id"] for r in listed] == ["b", "c", "a"]


def test_in_memory_evicts_oldest_when_capped() -> None:
    store = InMemoryRunHistory(max_entries=2)
    store.put("a", _make_run("a", created_at=datetime(2026, 1, 1)))
    store.put("b", _make_run("b", created_at=datetime(2026, 2, 1)))
    store.put("c", _make_run("c", created_at=datetime(2026, 3, 1)))

    assert store.get("a") is None
    assert store.get("b") is not None
    assert store.get("c") is not None


# ---------------------------------------------------------------------------
# RedisRunHistory (using fakeredis)
# ---------------------------------------------------------------------------


fakeredis = pytest.importorskip("fakeredis")


def _redis_store() -> RedisRunHistory:
    # fakeredis.FakeRedis is a drop-in replacement for redis.Redis.
    return RedisRunHistory(
        url="redis://localhost:6379/0",
        ttl_seconds=3600,
        client=fakeredis.FakeStrictRedis(decode_responses=True),
    )


def test_redis_put_get_roundtrip() -> None:
    store = _redis_store()
    run = _make_run("abc", created_at=datetime(2026, 4, 17))

    store.put("abc", run)

    assert store.get("abc") == run
    assert store.get("missing") is None


def test_redis_list_reverse_chronological() -> None:
    store = _redis_store()
    store.put("a", _make_run("a", created_at=datetime(2026, 1, 1)))
    store.put("b", _make_run("b", created_at=datetime(2026, 3, 1)))
    store.put("c", _make_run("c", created_at=datetime(2026, 2, 1)))

    listed = store.list(limit=10)

    assert [r["run_id"] for r in listed] == ["b", "c", "a"]


def test_redis_list_limit_is_honoured() -> None:
    store = _redis_store()
    for i in range(5):
        store.put(str(i), _make_run(str(i), created_at=datetime(2026, 1, i + 1)))

    listed = store.list(limit=2)

    assert len(listed) == 2


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def test_builder_defaults_to_memory_without_redis_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CIRQ_RAG_REDIS_URL", raising=False)
    monkeypatch.delenv("CIRQ_RAG_RUN_HISTORY_BACKEND", raising=False)

    store = build_run_history_store()

    assert isinstance(store, InMemoryRunHistory)


def test_builder_raises_when_redis_backend_missing_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CIRQ_RAG_RUN_HISTORY_BACKEND", "redis")
    monkeypatch.delenv("CIRQ_RAG_REDIS_URL", raising=False)

    with pytest.raises(RuntimeError, match="CIRQ_RAG_REDIS_URL"):
        build_run_history_store()
