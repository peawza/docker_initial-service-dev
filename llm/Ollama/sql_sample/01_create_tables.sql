-- =========================================
-- Enable pgvector extension
-- =========================================
CREATE EXTENSION IF NOT EXISTS vector;

-- =========================================
-- Drop tables (for re-run testing)
-- =========================================
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS rag_documents;

-- =========================================
-- Create documents table
-- =========================================
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding vector(8),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================================
-- Create rag_documents table
-- =========================================
CREATE TABLE rag_documents (
    id BIGSERIAL PRIMARY KEY,
    source_type VARCHAR(50),
    source_id VARCHAR(100),
    content TEXT,
    embedding vector(8),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================================
-- Create Vector Index
-- =========================================
CREATE INDEX idx_documents_embedding
ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10);

CREATE INDEX idx_rag_embedding
ON rag_documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10);

-- =========================================
-- Analyze tables
-- =========================================
ANALYZE documents;
ANALYZE rag_documents;
