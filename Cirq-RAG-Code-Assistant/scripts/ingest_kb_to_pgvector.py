"""
Idempotent ingestion of the curated knowledge base into Postgres + pgvector.

Reads every ``data/knowledge_base/curated_*_examples.jsonl`` file, turns each
row into an embedded knowledge-base entry, and upserts it into
``cirq_rag.rag_knowledge_base`` (see ``scripts/sql/001_init_pgvector.sql``).

Deduplication:
    For each row the script computes ``sha256(content)``. If the DB already
    has a row with the same ``doc_id``, the same ``content_hash`` AND the same
    embedding ``model_id`` as the currently-configured embedding model, the
    row is skipped - no Bedrock call, no write. This keeps re-runs cheap.

Usage:
    export CIRQ_RAG_DB_URL=postgresql://user:pass@host:5432/db
    python scripts/ingest_kb_to_pgvector.py
    python scripts/ingest_kb_to_pgvector.py --limit 10   # smoke run
    python scripts/ingest_kb_to_pgvector.py --dry-run    # no writes, no embeds
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# Make ``src`` importable without requiring an editable install.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT))

try:
    import psycopg
    from pgvector.psycopg import register_vector
except ImportError as exc:
    raise SystemExit(
        "psycopg and pgvector are required. "
        "Install with: pip install 'psycopg[binary]' pgvector"
    ) from exc

from src.cirq_rag_code_assistant.config import get_config  # noqa: E402
from src.cirq_rag_code_assistant.config.logging import get_logger  # noqa: E402
from src.rag.embeddings import EmbeddingModel  # noqa: E402


logger = get_logger(__name__)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_text_for_embedding(entry: Dict[str, Any]) -> str:
    """Mirror the text assembly used by KnowledgeBase.index_entries."""
    parts: List[str] = []
    if entry.get("task"):
        parts.append(entry["task"])
    topics = entry.get("topics") or []
    if topics:
        parts.append("Topics: " + ", ".join(topics))
    constraints = entry.get("constraints") or []
    if constraints:
        parts.append("Constraints: " + "; ".join(constraints))
    if entry.get("description"):
        parts.append(entry["description"])
    if entry.get("code"):
        parts.append(entry["code"])
    return "\n\n".join(parts)


def _derive_source(jsonl_path: Path, entry: Dict[str, Any]) -> str:
    """Derive a stable 'source' label (designer / optimizer / validator / ...)."""
    name = jsonl_path.stem  # e.g. curated_designer_examples
    if name.startswith("curated_") and name.endswith("_examples"):
        return name[len("curated_"): -len("_examples")]
    return entry.get("framework", "unknown").lower()


def _iter_entries(kb_dir: Path) -> Iterable[Tuple[Path, Dict[str, Any]]]:
    for jsonl_file in sorted(kb_dir.glob("curated_*_examples.jsonl")):
        with jsonl_file.open("r", encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as exc:
                    logger.warning("Skipping %s:%d - invalid JSON (%s)", jsonl_file, lineno, exc)
                    continue
                yield jsonl_file, entry


def _existing_doc(
    conn: "psycopg.Connection", schema: str, table: str, doc_id: str
) -> Optional[Tuple[str, str]]:
    """Return (content_hash, model_id) for an existing doc_id, or None."""
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT content_hash, model_id FROM {schema}.{table} WHERE doc_id = %s",
            (doc_id,),
        )
        row = cur.fetchone()
    if row is None:
        return None
    return row[0], row[1]


def _upsert(
    conn: "psycopg.Connection",
    schema: str,
    table: str,
    *,
    source: str,
    doc_id: str,
    content: str,
    content_hash: str,
    metadata: Dict[str, Any],
    embedding,
    model_id: str,
) -> None:
    sql = (
        f"INSERT INTO {schema}.{table} "
        "(source, doc_id, content, content_hash, metadata, embedding, model_id) "
        "VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s) "
        "ON CONFLICT (doc_id) DO UPDATE SET "
        "source = EXCLUDED.source, "
        "content = EXCLUDED.content, "
        "content_hash = EXCLUDED.content_hash, "
        "metadata = EXCLUDED.metadata, "
        "embedding = EXCLUDED.embedding, "
        "model_id = EXCLUDED.model_id, "
        "updated_at = now()"
    )
    with conn.cursor() as cur:
        cur.execute(
            sql,
            (
                source,
                doc_id,
                content,
                content_hash,
                json.dumps(metadata),
                embedding,
                model_id,
            ),
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--kb-dir",
        default=None,
        help="Knowledge base directory (defaults to rag.knowledge_base.path in config.json)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only the first N new/changed entries across all files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not call Bedrock and do not write to the database.",
    )
    args = parser.parse_args()

    cfg = get_config()

    pg_cfg = cfg.get("rag", {}).get("vector_store", {}).get("pgvector", {}) or {}
    schema = pg_cfg.get("schema", "cirq_rag")
    table = pg_cfg.get("table", "rag_knowledge_base")
    dsn_env = pg_cfg.get("dsn_env", "CIRQ_RAG_DB_URL")
    dsn = os.getenv(dsn_env)
    if not dsn:
        logger.error("Env var %s is not set. Export it to a libpq DSN and retry.", dsn_env)
        return 2

    kb_dir = Path(
        args.kb_dir
        or cfg.get("rag", {}).get("knowledge_base", {}).get("path", "data/knowledge_base")
    )
    if not kb_dir.is_absolute():
        kb_dir = _PROJECT_ROOT / kb_dir
    if not kb_dir.exists():
        logger.error("Knowledge base directory not found: %s", kb_dir)
        return 2

    embedder = EmbeddingModel()
    model_id = (
        cfg.get("aws", {}).get("embeddings", {}).get("model_id")
        or cfg.get("models", {}).get("embedding", {}).get("model_name")
        or "unknown"
    )
    logger.info("Using embedding model_id=%s (provider=%s)", model_id, embedder.provider)

    if args.dry_run:
        logger.warning("Dry run: no Bedrock calls, no DB writes.")

    conn: Optional["psycopg.Connection"] = None
    if not args.dry_run:
        conn = psycopg.connect(dsn, autocommit=True)
        register_vector(conn)

    stats = {"seen": 0, "skipped_unchanged": 0, "upserted": 0, "errors": 0}

    try:
        for jsonl_file, entry in _iter_entries(kb_dir):
            stats["seen"] += 1
            doc_id = entry.get("id")
            if not doc_id:
                logger.warning("Skipping entry in %s without 'id'", jsonl_file.name)
                stats["errors"] += 1
                continue

            content = _build_text_for_embedding(entry)
            if not content.strip():
                logger.warning("Skipping %s (empty content after assembly)", doc_id)
                stats["errors"] += 1
                continue

            content_hash = _sha256(content)

            if conn is not None:
                existing = _existing_doc(conn, schema, table, doc_id)
                if existing is not None and existing == (content_hash, model_id):
                    stats["skipped_unchanged"] += 1
                    continue

            if args.limit is not None and stats["upserted"] >= args.limit:
                logger.info("Limit of %d reached, stopping.", args.limit)
                break

            metadata: Dict[str, Any] = {
                "framework": entry.get("framework", "Cirq"),
                "difficulty": entry.get("difficulty"),
                "topics": entry.get("topics", []),
                "source_file": jsonl_file.name,
                "content_hash": content_hash,
            }
            # Preserve any original metadata block if present.
            if isinstance(entry.get("metadata"), dict):
                metadata.update(entry["metadata"])

            source = _derive_source(jsonl_file, entry)

            if args.dry_run:
                stats["upserted"] += 1
                logger.info("DRY-RUN would embed+upsert %s (source=%s)", doc_id, source)
                continue

            try:
                embedding_arr = embedder.encode([content])
                embedding = embedding_arr[0]
                assert conn is not None
                _upsert(
                    conn,
                    schema,
                    table,
                    source=source,
                    doc_id=doc_id,
                    content=content,
                    content_hash=content_hash,
                    metadata=metadata,
                    embedding=embedding,
                    model_id=model_id,
                )
                stats["upserted"] += 1
                logger.info("Upserted %s (source=%s)", doc_id, source)
            except Exception as exc:
                stats["errors"] += 1
                logger.exception("Failed to ingest %s: %s", doc_id, exc)

            if args.limit is not None and stats["upserted"] >= args.limit:
                logger.info("Limit of %d reached, stopping.", args.limit)
                break
    finally:
        if conn is not None:
            conn.close()

    logger.info(
        "Ingestion complete: seen=%d upserted=%d skipped_unchanged=%d errors=%d",
        stats["seen"],
        stats["upserted"],
        stats["skipped_unchanged"],
        stats["errors"],
    )
    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
