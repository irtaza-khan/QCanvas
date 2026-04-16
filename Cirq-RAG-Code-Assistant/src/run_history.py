"""Run history storage backends for the Cirq-RAG server.

The original implementation kept the last 50 runs in a module-level dict.
That breaks as soon as more than one server replica is running behind a load
balancer, and loses data on every container restart.

This module factors that out behind a small interface with two production-
ready implementations:

* ``InMemoryRunHistory``  - zero-dependency fallback for local development
  and unit tests.
* ``RedisRunHistory``     - persists runs in Redis with a per-run TTL and a
  ZSET index so ``list()`` is cheap even when the backing store is shared
  across replicas.
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional


class RunHistoryStore(ABC):
    """Minimal interface every run-history backend must implement."""

    @abstractmethod
    def put(self, run_id: str, run: Dict[str, Any]) -> None:  # pragma: no cover - interface
        ...

    @abstractmethod
    def get(self, run_id: str) -> Optional[Dict[str, Any]]:  # pragma: no cover - interface
        ...

    @abstractmethod
    def list(self, limit: int = 50) -> List[Dict[str, Any]]:  # pragma: no cover - interface
        ...


def _parse_created_at(run: Dict[str, Any]) -> float:
    raw = run.get("created_at")
    if isinstance(raw, datetime):
        return raw.timestamp()
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return 0.0
    return 0.0


class InMemoryRunHistory(RunHistoryStore):
    """Bounded in-memory LRU. Intended for dev and tests only."""

    def __init__(self, max_entries: int = 50) -> None:
        self._entries: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
        self._max = max_entries

    def put(self, run_id: str, run: Dict[str, Any]) -> None:
        self._entries[run_id] = run
        self._entries.move_to_end(run_id)
        while len(self._entries) > self._max:
            self._entries.popitem(last=False)

    def get(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._entries.get(run_id)

    def list(self, limit: int = 50) -> List[Dict[str, Any]]:
        runs = list(self._entries.values())
        runs.sort(key=_parse_created_at, reverse=True)
        return runs[:limit]


class RedisRunHistory(RunHistoryStore):
    """Run history backed by Redis.

    Storage layout:
    * ``cirq_rag:run:{run_id}``      - JSON payload, expires after ``ttl_seconds``.
    * ``cirq_rag:runs:index``        - sorted set, score = created_at unix ts,
                                       member = run_id. Used for fast ``list()``.
    """

    KEY_PREFIX = "cirq_rag:run:"
    INDEX_KEY = "cirq_rag:runs:index"

    def __init__(self, url: str, ttl_seconds: int = 86_400, client: Any = None) -> None:
        if client is None:
            # Local import keeps the dev-only fakeredis workflow simple and
            # means modules that never touch Redis do not pay an import cost.
            import redis

            client = redis.Redis.from_url(url, decode_responses=True)
        self._r = client
        self._ttl = int(ttl_seconds)

    def put(self, run_id: str, run: Dict[str, Any]) -> None:
        payload = json.dumps(run, default=_json_default)
        key = self.KEY_PREFIX + run_id
        score = _parse_created_at(run)

        pipe = self._r.pipeline()
        pipe.set(key, payload, ex=self._ttl)
        pipe.zadd(self.INDEX_KEY, {run_id: score})
        # Trim the index opportunistically so it doesn't grow forever; keep
        # the last 1000 entries (the `list()` API caps at 50 by default).
        pipe.zremrangebyrank(self.INDEX_KEY, 0, -1001)
        pipe.execute()

    def get(self, run_id: str) -> Optional[Dict[str, Any]]:
        raw = self._r.get(self.KEY_PREFIX + run_id)
        if raw is None:
            # If the payload expired but the index still references it, clean up.
            self._r.zrem(self.INDEX_KEY, run_id)
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def list(self, limit: int = 50) -> List[Dict[str, Any]]:
        ids = self._r.zrevrange(self.INDEX_KEY, 0, max(0, limit - 1))
        if not ids:
            return []
        pipe = self._r.pipeline()
        for run_id in ids:
            pipe.get(self.KEY_PREFIX + run_id)
        results = pipe.execute()

        runs: List[Dict[str, Any]] = []
        stale_ids: List[str] = []
        for run_id, raw in zip(ids, results):
            if raw is None:
                stale_ids.append(run_id)
                continue
            try:
                runs.append(json.loads(raw))
            except json.JSONDecodeError:
                stale_ids.append(run_id)
        if stale_ids:
            self._r.zrem(self.INDEX_KEY, *stale_ids)
        return runs


def _json_default(value: Any) -> Any:
    """Fallback JSON serializer for datetime and other non-JSON types."""
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def build_run_history_store(
    backend: Optional[str] = None,
    redis_url: Optional[str] = None,
    ttl_seconds: Optional[int] = None,
    max_entries: int = 50,
) -> RunHistoryStore:
    """Build a ``RunHistoryStore`` from config/env.

    Precedence:
    1. Explicit ``backend`` argument.
    2. ``CIRQ_RAG_RUN_HISTORY_BACKEND`` env var.
    3. Auto-detect Redis if ``CIRQ_RAG_REDIS_URL`` is set, otherwise memory.
    """
    backend = (backend or os.getenv("CIRQ_RAG_RUN_HISTORY_BACKEND") or "").strip().lower()
    url = redis_url or os.getenv("CIRQ_RAG_REDIS_URL")
    ttl = int(ttl_seconds or os.getenv("CIRQ_RAG_RUN_HISTORY_TTL_SECONDS") or 86_400)

    if backend == "redis" or (backend == "" and url):
        if not url:
            raise RuntimeError(
                "Redis run-history backend selected but CIRQ_RAG_REDIS_URL is not set."
            )
        return RedisRunHistory(url=url, ttl_seconds=ttl)
    return InMemoryRunHistory(max_entries=max_entries)
