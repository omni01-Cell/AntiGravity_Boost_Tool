-- DB.sql
-- Fichier d'initialisation complet de la base de données AntiGravity (SLM-V3)
-- À exécuter dans l'éditeur SQL de Supabase.

-- 1. Activation de l'extension vectorielle (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Création de la table principale des fragments de connaissance
CREATE TABLE IF NOT EXISTS public.knowledge_chunks (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  source text NOT NULL,
  chapter text,
  content text NOT NULL,
  embedding vector(768),                            -- Embeddings via Gemini
  variance double precision[],                      -- Incerpitude dimensionnelle (Fisher)
  category text DEFAULT 'THEORY'::text,             -- THEORY | SKILL | RULE
  importance_score double precision DEFAULT 0.5,   -- Score par feedback LoopRAG
  access_count integer DEFAULT 0,
  energy double precision DEFAULT 1.0,              -- Dynamique de Langevin (0.1 à 1.5)
  is_flagged boolean DEFAULT false,                 -- Défini par le classificateur de cohérence
  last_accessed_at timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT knowledge_chunks_pkey PRIMARY KEY (id)
);

-- 3. Index de performance pour la recherche sémantique (HNSW)
-- Note: Requis pour les recherches sur de grands volumes de données.
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding_cosine 
ON public.knowledge_chunks USING hnsw (embedding vector_cosine_ops);

-- 4. Fonction de Recherche Riemannian Fisher (SLM-V3)
-- Cette fonction est le coeur du moteur de recherche pondéré par l'énergie.
CREATE OR REPLACE FUNCTION public.search_knowledge_fisher(
  query_embedding vector(768),
  match_count int,
  similarity_threshold float
)
RETURNS TABLE (
  id uuid,
  content text,
  source text,
  energy float,
  importance_score float,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    k.id,
    k.content,
    k.source,
    k.energy::float4,
    k.importance_score::float4,
    -- Similarité pondérée Fisher : (Cosinus Similarity) * (Energy / (1 + Mean Variance))
    ( (1 - (k.embedding <=> query_embedding)) * (k.energy / (1 + COALESCE((SELECT avg(v) FROM unnest(k.variance) v), 0))) )::float4 AS similarity
  FROM knowledge_chunks k
  WHERE (1 - (k.embedding <=> query_embedding)) > similarity_threshold
    AND k.is_flagged = false
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;

-- 5. Fonction de mise à jour Langevin (Entropie mémorielle)
-- Gère la dégradation naturelle et les sursauts stochastiques de l'énergie.
CREATE OR REPLACE FUNCTION public.langevin_energy_update(
  dt float,
  noise_amplitude float,
  storage_cost float
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE public.knowledge_chunks
  SET energy = GREATEST(0.1, LEAST(1.5, 
    energy - storage_cost * dt + noise_amplitude * (random() - 0.5)
  ))
  WHERE is_flagged = false;
END;
$$;
