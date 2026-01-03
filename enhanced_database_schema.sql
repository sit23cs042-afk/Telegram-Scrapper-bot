-- ============================================================================
-- Enhanced Database Schema for Discount Product Intelligence Agent
-- ============================================================================
-- Run this on your EXISTING Supabase database (same one used for Telegram)
-- This adds new tables and enhances the existing 'deals' table
--
-- Adds support for:
-- - Historical price tracking
-- - Stock availability
-- - Coupon/bank offers
-- - Deal scoring (0-100)
-- - Final effective price
-- - Duplicate detection
--
-- NOTE: Uses the same Supabase connection as telegram_listener.py
-- ============================================================================

-- Price History Table
CREATE TABLE IF NOT EXISTS price_history (
    id BIGSERIAL PRIMARY KEY,
    product_url TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    mrp DECIMAL(10, 2),
    observed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for price history
CREATE INDEX IF NOT EXISTS idx_price_history_url ON price_history(product_url);
CREATE INDEX IF NOT EXISTS idx_price_history_observed ON price_history(observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_price_history_url_observed ON price_history(product_url, observed_at DESC);

-- Enable Row Level Security
ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;

-- Policy for price history
DROP POLICY IF EXISTS "Allow all operations on price_history" ON price_history;
CREATE POLICY "Allow all operations on price_history" ON price_history
    FOR ALL USING (true) WITH CHECK (true);


-- ============================================================================
-- Enhanced Deals Table (Update existing table)
-- ============================================================================

-- Add new columns to existing deals table
ALTER TABLE deals ADD COLUMN IF NOT EXISTS stock_status TEXT DEFAULT 'unknown';
ALTER TABLE deals ADD COLUMN IF NOT EXISTS in_stock BOOLEAN DEFAULT TRUE;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS stock_message TEXT;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

ALTER TABLE deals ADD COLUMN IF NOT EXISTS deal_score DECIMAL(5, 2);
ALTER TABLE deals ADD COLUMN IF NOT EXISTS deal_grade TEXT;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS recommendation TEXT;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS score_breakdown JSONB;

ALTER TABLE deals ADD COLUMN IF NOT EXISTS offers JSONB;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS has_coupon BOOLEAN DEFAULT FALSE;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS has_bank_offer BOOLEAN DEFAULT FALSE;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS has_exchange BOOLEAN DEFAULT FALSE;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS no_cost_emi BOOLEAN DEFAULT FALSE;

ALTER TABLE deals ADD COLUMN IF NOT EXISTS final_effective_price DECIMAL(10, 2);
ALTER TABLE deals ADD COLUMN IF NOT EXISTS total_savings DECIMAL(10, 2);
ALTER TABLE deals ADD COLUMN IF NOT EXISTS price_breakdown JSONB;

ALTER TABLE deals ADD COLUMN IF NOT EXISTS price_insights JSONB;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS is_historical_low BOOLEAN DEFAULT FALSE;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS is_fake_discount BOOLEAN DEFAULT FALSE;

ALTER TABLE deals ADD COLUMN IF NOT EXISTS deal_type TEXT;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS seller_type TEXT;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS source TEXT;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS is_high_value BOOLEAN DEFAULT FALSE;

-- Seller Details (extracted from official website)
ALTER TABLE deals ADD COLUMN IF NOT EXISTS seller_name TEXT;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS seller_rating DECIMAL(3, 2);
ALTER TABLE deals ADD COLUMN IF NOT EXISTS is_fulfilled_by_platform BOOLEAN DEFAULT FALSE;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS seller_info JSONB;

ALTER TABLE deals ADD COLUMN IF NOT EXISTS processed_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS intelligence_version TEXT;


-- ============================================================================
-- Deal Sources Tracking (for duplicate detection)
-- ============================================================================

CREATE TABLE IF NOT EXISTS deal_sources (
    id BIGSERIAL PRIMARY KEY,
    deal_id BIGINT REFERENCES deals(id) ON DELETE CASCADE,
    source_name TEXT NOT NULL,
    source_url TEXT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_deal_sources_deal_id ON deal_sources(deal_id);
CREATE INDEX IF NOT EXISTS idx_deal_sources_source_name ON deal_sources(source_name);

ALTER TABLE deal_sources ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all operations on deal_sources" ON deal_sources;
CREATE POLICY "Allow all operations on deal_sources" ON deal_sources
    FOR ALL USING (true) WITH CHECK (true);


-- ============================================================================
-- Product URL Mapping (for duplicate detection)
-- ============================================================================

CREATE TABLE IF NOT EXISTS product_urls (
    id BIGSERIAL PRIMARY KEY,
    normalized_url TEXT NOT NULL UNIQUE,
    original_urls TEXT[] DEFAULT '{}',
    product_id TEXT,
    platform TEXT,
    first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_product_urls_normalized ON product_urls(normalized_url);
CREATE INDEX IF NOT EXISTS idx_product_urls_platform ON product_urls(platform);

ALTER TABLE product_urls ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all operations on product_urls" ON product_urls;
CREATE POLICY "Allow all operations on product_urls" ON product_urls
    FOR ALL USING (true) WITH CHECK (true);


-- ============================================================================
-- Intelligence Statistics
-- ============================================================================

CREATE TABLE IF NOT EXISTS intelligence_stats (
    id BIGSERIAL PRIMARY KEY,
    stat_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_deals_processed INT DEFAULT 0,
    duplicates_removed INT DEFAULT 0,
    high_value_deals INT DEFAULT 0,
    deals_saved INT DEFAULT 0,
    errors INT DEFAULT 0,
    avg_deal_score DECIMAL(5, 2),
    top_category TEXT,
    top_store TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(stat_date)
);

CREATE INDEX IF NOT EXISTS idx_intelligence_stats_date ON intelligence_stats(stat_date DESC);

ALTER TABLE intelligence_stats ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all operations on intelligence_stats" ON intelligence_stats;
CREATE POLICY "Allow all operations on intelligence_stats" ON intelligence_stats
    FOR ALL USING (true) WITH CHECK (true);


-- ============================================================================
-- Views for Analytics
-- ============================================================================

-- Top Deals by Score
CREATE OR REPLACE VIEW v_top_deals AS
SELECT 
    id,
    title,
    CASE 
        WHEN link LIKE '%amazon.%' THEN 'Amazon'
        WHEN link LIKE '%flipkart.%' THEN 'Flipkart'
        WHEN link LIKE '%myntra.%' THEN 'Myntra'
        WHEN link LIKE '%ajio.%' THEN 'Ajio'
        WHEN link LIKE '%snapdeal.%' THEN 'Snapdeal'
        ELSE 'Other'
    END as store,
    category,
    deal_score,
    deal_grade,
    recommendation,
    final_effective_price,
    total_savings,
    stock_status,
    is_high_value,
    COALESCE(detected_at, created_at) as detected_at,
    link as url
FROM deals
WHERE deal_score IS NOT NULL
ORDER BY deal_score DESC
LIMIT 100;

-- Historical Low Deals
CREATE OR REPLACE VIEW v_historical_low_deals AS
SELECT 
    id,
    title,
    CASE 
        WHEN link LIKE '%amazon.%' THEN 'Amazon'
        WHEN link LIKE '%flipkart.%' THEN 'Flipkart'
        WHEN link LIKE '%myntra.%' THEN 'Myntra'
        WHEN link LIKE '%ajio.%' THEN 'Ajio'
        WHEN link LIKE '%snapdeal.%' THEN 'Snapdeal'
        ELSE 'Other'
    END as store,
    category,
    final_effective_price,
    deal_score,
    COALESCE(detected_at, created_at) as detected_at,
    link as url
FROM deals
WHERE is_historical_low = TRUE
ORDER BY COALESCE(detected_at, created_at) DESC;

-- High-Value Deals
CREATE OR REPLACE VIEW v_high_value_deals AS
SELECT 
    id,
    title,
    CASE 
        WHEN link LIKE '%amazon.%' THEN 'Amazon'
        WHEN link LIKE '%flipkart.%' THEN 'Flipkart'
        WHEN link LIKE '%myntra.%' THEN 'Myntra'
        WHEN link LIKE '%ajio.%' THEN 'Ajio'
        WHEN link LIKE '%snapdeal.%' THEN 'Snapdeal'
        ELSE 'Other'
    END as store,
    category,
    deal_score,
    deal_grade,
    final_effective_price,
    total_savings,
    stock_status,
    COALESCE(detected_at, created_at) as detected_at,
    link as url
FROM deals
WHERE is_high_value = TRUE
ORDER BY deal_score DESC;

-- Price History Summary
CREATE OR REPLACE VIEW v_price_history_summary AS
SELECT 
    product_url,
    COUNT(*) as observation_count,
    MIN(price) as lowest_price,
    MAX(price) as highest_price,
    AVG(price) as average_price,
    MAX(observed_at) as last_observed
FROM price_history
GROUP BY product_url;

-- Daily Stats
CREATE OR REPLACE VIEW v_daily_stats AS
SELECT 
    stat_date,
    total_deals_processed,
    duplicates_removed,
    high_value_deals,
    deals_saved,
    avg_deal_score,
    top_category,
    top_store
FROM intelligence_stats
ORDER BY stat_date DESC;


-- ============================================================================
-- Functions for Common Operations
-- ============================================================================

-- Function to update product URL mapping
CREATE OR REPLACE FUNCTION update_product_url_mapping(
    p_normalized_url TEXT,
    p_original_url TEXT,
    p_platform TEXT,
    p_product_id TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO product_urls (normalized_url, original_urls, platform, product_id)
    VALUES (p_normalized_url, ARRAY[p_original_url], p_platform, p_product_id)
    ON CONFLICT (normalized_url) 
    DO UPDATE SET
        original_urls = array_append(
            COALESCE(product_urls.original_urls, '{}'), 
            p_original_url
        ),
        last_seen_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to update daily stats
CREATE OR REPLACE FUNCTION update_daily_stats()
RETURNS VOID AS $$
BEGIN
    INSERT INTO intelligence_stats (
        stat_date,
        total_deals_processed,
        high_value_deals,
        deals_saved,
        avg_deal_score,
        top_category,
        top_store
    )
    VALUES (
        CURRENT_DATE,
        (SELECT COUNT(*) FROM deals WHERE DATE(COALESCE(detected_at, created_at)) = CURRENT_DATE),
        (SELECT COUNT(*) FROM deals WHERE DATE(COALESCE(detected_at, created_at)) = CURRENT_DATE AND is_high_value = TRUE),
        (SELECT COUNT(*) FROM deals WHERE DATE(processed_at) = CURRENT_DATE),
        (SELECT AVG(deal_score) FROM deals WHERE DATE(COALESCE(detected_at, created_at)) = CURRENT_DATE AND deal_score IS NOT NULL),
        (SELECT category FROM deals WHERE DATE(COALESCE(detected_at, created_at)) = CURRENT_DATE GROUP BY category ORDER BY COUNT(*) DESC LIMIT 1),
        (SELECT 
            CASE 
                WHEN link LIKE '%amazon.%' THEN 'Amazon'
                WHEN link LIKE '%flipkart.%' THEN 'Flipkart'
                WHEN link LIKE '%myntra.%' THEN 'Myntra'
                ELSE 'Other'
            END
         FROM deals 
         WHERE DATE(COALESCE(detected_at, created_at)) = CURRENT_DATE 
         GROUP BY link 
         ORDER BY COUNT(*) DESC 
         LIMIT 1)
    )
    ON CONFLICT (stat_date)
    DO UPDATE SET
        total_deals_processed = EXCLUDED.total_deals_processed,
        high_value_deals = EXCLUDED.high_value_deals,
        deals_saved = EXCLUDED.deals_saved,
        avg_deal_score = EXCLUDED.avg_deal_score,
        top_category = EXCLUDED.top_category,
        top_store = EXCLUDED.top_store,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- Sample Queries
-- ============================================================================

-- Get top 10 deals by score
-- SELECT * FROM v_top_deals LIMIT 10;

-- Get all historical low deals
-- SELECT * FROM v_historical_low_deals;

-- Get price history for a product
-- SELECT * FROM price_history WHERE product_url = 'your_url' ORDER BY observed_at DESC;

-- Get deals with bank offers
-- SELECT title, store, final_effective_price, offers FROM deals WHERE has_bank_offer = TRUE;

-- Get in-stock high-value deals
-- SELECT * FROM deals WHERE is_high_value = TRUE AND in_stock = TRUE ORDER BY deal_score DESC;

-- Get today's statistics
-- SELECT * FROM v_daily_stats WHERE stat_date = CURRENT_DATE;
