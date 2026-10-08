-- ============================================================================
-- CannaGenetics — Initial Relational Schema (PostgreSQL 15+)
-- v0.1 · Living document · The jurisdictions table is the legal firewall.
-- Requires extensions: pg_trgm, citext (CREATE EXTENSION IF NOT EXISTS ...).
-- ============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- Jurisdictions — THE LEGAL FIREWALL.
-- No row here may be modified by automation; changes require human merge.
-- drives_allowed: which product forms may be rendered/linked for a visitor
-- declaring residence in this jurisdiction.
-- ---------------------------------------------------------------------------
CREATE TABLE jurisdictions (
    id              BIGSERIAL PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,          -- ISO-3166-ish: 'US-CA', 'NL', 'DE'
    name            TEXT NOT NULL,
    country         TEXT NOT NULL,
    region          TEXT,                          -- state/province, nullable
    is_active       BOOLEAN NOT NULL DEFAULT FALSE,  -- only reviewed rows activate
    seeds_allowed   BOOLEAN NOT NULL DEFAULT FALSE,
    clones_allowed  BOOLEAN NOT NULL DEFAULT FALSE,
    min_age         SMALLINT NOT NULL DEFAULT 18,
    notes           TEXT,                          -- legal basis summary w/ source
    legal_source_url TEXT,
    reviewed_by     TEXT,
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Breeders — the people/houses that created cultivars.
-- ---------------------------------------------------------------------------
CREATE TABLE breeders (
    id              BIGSERIAL PRIMARY KEY,
    slug            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    country         TEXT,
    website_url     TEXT,
    founded_year    SMALLINT,
    reputation_note TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Cultivars — the genetic catalog core.
-- ---------------------------------------------------------------------------
CREATE TABLE cultivars (
    id              BIGSERIAL PRIMARY KEY,
    slug            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    aliases         TEXT[] NOT NULL DEFAULT '{}',   -- 'GG4' -> 'Gorilla Glue #4'
    breeder_id      BIGINT REFERENCES breeders(id) ON DELETE SET NULL,
    type            TEXT NOT NULL CHECK (type IN
                    ('photoperiod','autoflower','feminized','regular','cbd_rich')),
    thc_min         NUMERIC(4,1) CHECK (thc_min BETWEEN 0 AND 40),
    thc_max         NUMERIC(4,1) CHECK (thc_max BETWEEN 0 AND 40),
    cbd_min         NUMERIC(4,1) CHECK (cbd_min BETWEEN 0 AND 40),
    cbd_max         NUMERIC(4,1) CHECK (cbd_max BETWEEN 0 AND 40),
    chemotype_source TEXT CHECK (chemotype_source IN
                    ('lab_tested','breeder_claimed','community_reported','unknown')),
    flowering_days_min SMALLINT,
    flowering_days_max SMALLINT,
    yield_class     TEXT CHECK (yield_class IN ('low','medium','high','very_high')),
    difficulty      TEXT CHECK (difficulty IN ('easy','moderate','hard')),
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_cultivars_name_trgm ON cultivars USING gin (name gin_trgm_ops);
CREATE INDEX idx_cultivars_breeder  ON cultivars (breeder_id);

-- ---------------------------------------------------------------------------
-- Terpenes — normalized profile per cultivar (top 3–5 per record).
-- ---------------------------------------------------------------------------
CREATE TABLE terpenes (
    id    BIGSERIAL PRIMARY KEY,
    name  TEXT NOT NULL UNIQUE          -- 'myrcene', 'limonene', ...
);

CREATE TABLE cultivar_terpenes (
    cultivar_id BIGINT NOT NULL REFERENCES cultivars(id) ON DELETE CASCADE,
    terpene_id  BIGINT NOT NULL REFERENCES terpenes(id)  ON DELETE CASCADE,
    rank        SMALLINT NOT NULL CHECK (rank BETWEEN 1 AND 5),
    source_url  TEXT NOT NULL,          -- every profile claim is sourced
    PRIMARY KEY (cultivar_id, terpene_id)
);

-- ---------------------------------------------------------------------------
-- Lineage — directed parent->child edges with verification status.
-- claimed   : what the breeder marketing says
-- verified  : corroborated by independent/community documentation
-- disputed  : active contradiction — shown, flagged, not resolved
-- ---------------------------------------------------------------------------
CREATE TABLE lineage_edges (
    id           BIGSERIAL PRIMARY KEY,
    parent_id    BIGINT NOT NULL REFERENCES cultivars(id) ON DELETE CASCADE,
    child_id     BIGINT NOT NULL REFERENCES cultivars(id) ON DELETE CASCADE,
    status       TEXT NOT NULL DEFAULT 'claimed'
                 CHECK (status IN ('claimed','verified','disputed')),
    source_url   TEXT NOT NULL,         -- breeder page, forum thread, lab doc...
    note         TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (parent_id <> child_id),
    UNIQUE (parent_id, child_id, source_url)
);

-- ---------------------------------------------------------------------------
-- Suppliers — see SUPPLIERS.md for required fields and gates.
-- ---------------------------------------------------------------------------
CREATE TABLE suppliers (
    id              BIGSERIAL PRIMARY KEY,
    slug            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    website_url     TEXT NOT NULL,
    hq_jurisdiction_id BIGINT REFERENCES jurisdictions(id),
    product_types   TEXT[] NOT NULL DEFAULT '{}'
                    CHECK (product_types <@ ARRAY['seeds','clones']::text[]),
    seed_types      TEXT[] NOT NULL DEFAULT '{}',
    payment_methods TEXT[] NOT NULL DEFAULT '{}',
    tos_posture     JSONB NOT NULL DEFAULT '{}'::jsonb,
    reputation_score NUMERIC(2,1) CHECK (reputation_score BETWEEN 0 AND 5),
    founded_year    SMALLINT,
    affiliate_status TEXT NOT NULL DEFAULT 'none'
                    CHECK (affiliate_status IN ('none','applied','active','rejected')),
    source_urls     TEXT[] NOT NULL DEFAULT '{}',
    is_active       BOOLEAN NOT NULL DEFAULT FALSE,
    first_seen      TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_verified   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Which jurisdictions a supplier states it ships to (source-linked).
CREATE TABLE supplier_ships_to (
    supplier_id     BIGINT NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
    jurisdiction_id BIGINT NOT NULL REFERENCES jurisdictions(id) ON DELETE CASCADE,
    source_url      TEXT NOT NULL,
    PRIMARY KEY (supplier_id, jurisdiction_id)
);

-- Which breeders a supplier carries.
CREATE TABLE supplier_breeders (
    supplier_id BIGINT NOT NULL REFERENCES suppliers(id)   ON DELETE CASCADE,
    breeder_id  BIGINT NOT NULL REFERENCES breeders(id)    ON DELETE CASCADE,
    source_url  TEXT NOT NULL,
    PRIMARY KEY (supplier_id, breeder_id)
);

-- ---------------------------------------------------------------------------
-- Listings — one supplier's offer of one cultivar.
-- HARD RULE: no source_url + timestamps -> no listing. Ever.
-- ---------------------------------------------------------------------------
CREATE TABLE listings (
    id             BIGSERIAL PRIMARY KEY,
    cultivar_id    BIGINT NOT NULL REFERENCES cultivars(id)  ON DELETE CASCADE,
    supplier_id    BIGINT NOT NULL REFERENCES suppliers(id)  ON DELETE CASCADE,
    product_form   TEXT NOT NULL CHECK (product_form IN ('seed','clone')),
    pack_size      TEXT,                 -- '3 pack', '10 seeds', 'clone (teen)'
    price_native   NUMERIC(12,2) NOT NULL,
    currency       CHAR(3) NOT NULL,     -- ISO 4217
    price_normalized NUMERIC(12,2),      -- USD-normalized, FX source noted
    fx_source_url  TEXT,
    in_stock       BOOLEAN,
    source_url     TEXT NOT NULL,        -- the listing page this came from
    first_seen     TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_verified  TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_dead        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (cultivar_id, supplier_id, pack_size, source_url)
);

CREATE INDEX idx_listings_cultivar ON listings (cultivar_id, in_stock, is_dead);
CREATE INDEX idx_listings_supplier ON listings (supplier_id, is_dead);

-- ---------------------------------------------------------------------------
-- Review queue — where dark-factory detections land for human curation.
-- Machines refresh; humans admit. This preserves the trust contract.
-- ---------------------------------------------------------------------------
CREATE TABLE review_queue (
    id           BIGSERIAL PRIMARY KEY,
    job          TEXT NOT NULL,           -- 'new-drop-detection' | 'tos-reaudit' | ...
    payload      JSONB NOT NULL,          -- detected candidate record w/ source
    status       TEXT NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending','approved','rejected','expired')),
    reviewer     TEXT,
    reviewed_at  TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Users & alerts (Phase 2) — declared jurisdiction is mandatory.
-- ---------------------------------------------------------------------------
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    email           CITEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    declared_jurisdiction_id BIGINT NOT NULL REFERENCES jurisdictions(id),
    age_verified_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE alerts (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind        TEXT NOT NULL CHECK (kind IN
                ('new_cultivar','restock','price_drop','new_supplier','drop')),
    target      JSONB NOT NULL,           -- cultivar_id / breeder_id / price spec
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Audit log — every automated mutation lands here. Dark-factory telemetry
-- and the success-metric staleness targets read from this table.
-- ---------------------------------------------------------------------------
CREATE TABLE audit_log (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job         TEXT NOT NULL,
    entity      TEXT NOT NULL,            -- 'listings', 'suppliers', ...
    entity_id   BIGINT,
    action      TEXT NOT NULL,            -- 'refresh','mark_dead','flag'...
    before      JSONB,
    after       JSONB,
    ran_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMIT;
