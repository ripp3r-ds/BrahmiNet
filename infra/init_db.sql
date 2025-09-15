
-- Init DB schema for BrahmiNet (template-first)

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-----------------------------
-- memes (templates) table
-----------------------------
CREATE TABLE IF NOT EXISTS memes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Source & canonical template
  source text,                   -- 'tenor', 'giphy', 'user_upload', etc.
  source_id text,                -- id from provider (optional)
  url text,                      -- original discovery URL (optional)
  url_hash text,                 -- md5(url) computed by trigger
  template_r2_url text,          -- canonical stored image on R2 / object storage
  template_url text,             -- canonical template original url (if different)

  -- Deduplication & template identity
  template_phash text,           -- perceptual hash of template image (hex)
  template_sample_count int DEFAULT 0, -- how many variants discovered for this template

  -- Content & metadata
  title text,
  caption text,
  tags text[],                   -- tags / keywords from Tenor / provider
  content_type text,
  file_size int,
  width int,
  height int,

  -- Variant-extracted text (aggregate)
  extracted_text text,           -- aggregated / representative text
  text_hash text,                -- md5(extracted_text) computed by trigger

  -- Film / context fields (Scholar enrichment)
  film_name text,
  film_year int,
  director text,
  main_cast text[],              -- array of cast names
  dialogue text,                 -- canonical dialogue if identified

  -- Emotional / semantic context
  emotions jsonb,                -- {"angry":0.8, "sad":0.2}

  -- Embeddings & provenance
  text_embedding vector(1536),   -- change dimension to match your model
  image_embedding vector(1536),  -- optional: visual embedding (if computed)
  embedding_model text,
  embedding_dim int,
  embedding_created_at timestamptz,

  -- Generic metadata & lifecycle
  metadata jsonb,                -- raw scholar output, evidence links, other data
  status text DEFAULT 'discovered', -- 'discovered','processed','enriched','indexed'
  is_template boolean DEFAULT true,

  discovered_at timestamptz DEFAULT now(),
  created_at timestamptz DEFAULT now()
);

-- Uniqueness & quick exact-dedupe
CREATE UNIQUE INDEX IF NOT EXISTS uq_memes_source_sourceid ON memes (source, source_id) WHERE source IS NOT NULL AND source_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_memes_url_hash ON memes (url_hash) WHERE url_hash IS NOT NULL;

-- Indexes for search, filtering, and metadata
CREATE INDEX IF NOT EXISTS idx_memes_template_phash ON memes (template_phash);
CREATE INDEX IF NOT EXISTS idx_memes_film ON memes (film_name, film_year);
CREATE INDEX IF NOT EXISTS idx_memes_tags_gin ON memes USING gin (tags);
CREATE INDEX IF NOT EXISTS idx_memes_metadata_gin ON memes USING gin (metadata);
CREATE INDEX IF NOT EXISTS idx_memes_emotions_gin ON memes USING gin (emotions);

-- Vector index for text_embedding (pgvector ivfflat)
CREATE INDEX IF NOT EXISTS idx_memes_text_embedding_ivf ON memes USING ivfflat (text_embedding vector_cosine_ops) WITH (lists = 100);

-----------------------------
-- meme_variants table
-----------------------------
CREATE TABLE IF NOT EXISTS meme_variants (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id uuid NOT NULL REFERENCES memes(id) ON DELETE CASCADE,
  source text,               -- 'tenor', 'giphy', 'user_upload'
  source_id text,
  original_url text,         -- original discovery URL for the variant
  overlay_text text,         -- OCR / extracted overlay text
  text_hash text,            -- md5(overlay_text)
  ocr_confidence numeric,    -- confidence from OCR
  variant_metadata jsonb,    -- any provider-specific metadata
  status text DEFAULT 'variant_discovered',
  discovered_at timestamptz DEFAULT now(),
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_variant_template_id ON meme_variants (template_id);
CREATE INDEX IF NOT EXISTS idx_variant_text_hash ON meme_variants (text_hash);
CREATE UNIQUE INDEX IF NOT EXISTS uq_variant_template_texthash ON meme_variants (template_id, text_hash) WHERE text_hash IS NOT NULL;

-----------------------------
-- Trigger: auto-fill url_hash and text_hash
-----------------------------
CREATE OR REPLACE FUNCTION brhn_set_hashes()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.url IS NOT NULL AND (NEW.url_hash IS NULL OR NEW.url_hash = '') THEN
    NEW.url_hash := md5(NEW.url);
  END IF;

  IF NEW.extracted_text IS NOT NULL AND (NEW.text_hash IS NULL OR NEW.text_hash = '') THEN
    NEW.text_hash := md5(NEW.extracted_text);
  END IF;

  -- For variants table: if overlay_text present and text_hash empty, compute it
  IF TG_TABLE_NAME = 'meme_variants' THEN
    IF NEW.overlay_text IS NOT NULL AND (NEW.text_hash IS NULL OR NEW.text_hash = '') THEN
      NEW.text_hash := md5(NEW.overlay_text);
    END IF;
  END IF;

  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_memes_set_hashes ON memes;
CREATE TRIGGER trg_memes_set_hashes
BEFORE INSERT OR UPDATE ON memes
FOR EACH ROW EXECUTE FUNCTION brhn_set_hashes();

DROP TRIGGER IF EXISTS trg_variant_set_hashes ON meme_variants;
CREATE TRIGGER trg_variant_set_hashes
BEFORE INSERT OR UPDATE ON meme_variants
FOR EACH ROW EXECUTE FUNCTION brhn_set_hashes();


-- A view that returns template rows with example variant overlay_texts
CREATE OR REPLACE VIEW vw_templates_with_samples AS
SELECT
  m.id AS template_id,
  m.template_r2_url,
  m.title,
  m.film_name,
  m.template_sample_count,
  json_agg(mv.overlay_text) FILTER (WHERE mv.overlay_text IS NOT NULL) AS sample_overlay_texts
FROM memes m
LEFT JOIN meme_variants mv ON mv.template_id = m.id
WHERE m.is_template = true
GROUP BY m.id;
