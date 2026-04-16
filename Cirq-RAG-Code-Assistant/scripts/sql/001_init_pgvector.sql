-- Cirq-RAG-Code-Assistant: pgvector knowledge base schema.
--
-- Idempotent migration. Apply once per database. Safe to re-run.
--
-- Usage:
--   psql "$CIRQ_RAG_DB_URL" -f scripts/sql/001_init_pgvector.sql
--
-- Notes:
--   * On Amazon RDS / Aurora Postgres, the pgvector extension is available
--     on Postgres 15.5+ and 16.x. The CREATE EXTENSION call requires the
--     rds_superuser role (or local superuser on self-hosted Postgres).
--   * The embedding dimension (1024) must match aws.embeddings.embedding_dimension
--     in config/config.json. If that value changes, this migration needs to be
--     updated and the table re-populated.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE SCHEMA IF NOT EXISTS cirq_rag;

CREATE TABLE IF NOT EXISTS cirq_rag.rag_knowledge_base (
    id             BIGSERIAL   PRIMARY KEY,
    source         TEXT        NOT NULL,
    doc_id         TEXT        NOT NULL UNIQUE,
    content        TEXT        NOT NULL,
    content_hash   TEXT        NOT NULL,
    metadata       JSONB       NOT NULL DEFAULT '{}'::jsonb,
    embedding      vector(1024) NOT NULL,
    model_id       TEXT        NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Approximate nearest-neighbour index using cosine distance. HNSW gives
-- low-latency queries for the expected dataset size (2,500 rows at target).
CREATE INDEX IF NOT EXISTS rag_kb_embedding_hnsw
    ON cirq_rag.rag_knowledge_base
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Support cheap metadata filters alongside vector search.
CREATE INDEX IF NOT EXISTS rag_kb_source_idx
    ON cirq_rag.rag_knowledge_base (source);

CREATE INDEX IF NOT EXISTS rag_kb_metadata_gin
    ON cirq_rag.rag_knowledge_base
    USING gin (metadata);

-- Keep updated_at honest without relying on every caller remembering to set it.
CREATE OR REPLACE FUNCTION cirq_rag.set_updated_at()
RETURNS trigger AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS rag_kb_set_updated_at
    ON cirq_rag.rag_knowledge_base;

CREATE TRIGGER rag_kb_set_updated_at
    BEFORE UPDATE ON cirq_rag.rag_knowledge_base
    FOR EACH ROW EXECUTE FUNCTION cirq_rag.set_updated_at();
