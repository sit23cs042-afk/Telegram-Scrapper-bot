-- Database Schema Migration - CLEAN RESTART
-- ==========================================
-- This script clears all data and sets up only the 6 required fields
-- Run this in your Supabase SQL editor
-- 
-- WARNING: This will DELETE ALL existing data in the deals table!
-- 
-- Required fields:
-- 1. title (product name)
-- 2. verified_mrp (original MRP)
-- 3. verified_price (discounted price)
-- 4. verified_discount (discount percent)
-- 5. link (e-commerce link)
-- 6. rating (product rating)

-- Step 1: Drop all old views and functions
DROP VIEW IF EXISTS verified_deals CASCADE;
DROP VIEW IF EXISTS high_confidence_deals CASCADE;
DROP VIEW IF EXISTS discounted_deals CASCADE;
DROP FUNCTION IF EXISTS get_deal_statistics() CASCADE;
DROP FUNCTION IF EXISTS cleanup_low_confidence_deals(INTEGER) CASCADE;

-- Step 2: Drop all old unnecessary columns
ALTER TABLE deals 
DROP COLUMN IF EXISTS is_verified CASCADE,
DROP COLUMN IF EXISTS confidence_score CASCADE,
DROP COLUMN IF EXISTS verification_source CASCADE,
DROP COLUMN IF EXISTS availability CASCADE,
DROP COLUMN IF EXISTS seller CASCADE,
DROP COLUMN IF EXISTS store CASCADE,
DROP COLUMN IF EXISTS discount_price CASCADE,
DROP COLUMN IF EXISTS category CASCADE,
DROP COLUMN IF EXISTS channel CASCADE,
DROP COLUMN IF EXISTS message_id CASCADE,
DROP COLUMN IF EXISTS message_date CASCADE;

-- Step 3: Delete all existing rows
DELETE FROM deals;

-- Step 4: Ensure required columns exist with proper constraints
-- Drop and recreate to ensure clean schema
ALTER TABLE deals DROP COLUMN IF EXISTS title CASCADE;
ALTER TABLE deals DROP COLUMN IF EXISTS link CASCADE;
ALTER TABLE deals DROP COLUMN IF EXISTS verified_mrp CASCADE;
ALTER TABLE deals DROP COLUMN IF EXISTS verified_price CASCADE;
ALTER TABLE deals DROP COLUMN IF EXISTS verified_discount CASCADE;
ALTER TABLE deals DROP COLUMN IF EXISTS rating CASCADE;
ALTER TABLE deals DROP COLUMN IF EXISTS timestamp CASCADE;

-- Add columns with proper constraints
ALTER TABLE deals
ADD COLUMN title VARCHAR(500) NOT NULL,  -- Increased from 200 to 500 to prevent truncation
ADD COLUMN verified_mrp NUMERIC(10, 2),
ADD COLUMN verified_price NUMERIC(10, 2) NOT NULL,
ADD COLUMN verified_discount NUMERIC(5, 2),
ADD COLUMN link TEXT NOT NULL,
ADD COLUMN rating NUMERIC(2, 1),
ADD COLUMN timestamp TIMESTAMP DEFAULT NOW();

-- Add unique constraint on link (prevents same URL twice)
ALTER TABLE deals ADD CONSTRAINT deals_link_unique UNIQUE (link);

-- Step 5: Drop old indexes
DROP INDEX IF EXISTS idx_deals_is_verified;
DROP INDEX IF EXISTS idx_deals_confidence_score;
DROP INDEX IF EXISTS idx_deals_verification_source;

-- Step 6: Create new indexes for performance
CREATE INDEX IF NOT EXISTS idx_deals_verified_price ON deals(verified_price);
CREATE INDEX IF NOT EXISTS idx_deals_verified_discount ON deals(verified_discount);
CREATE INDEX IF NOT EXISTS idx_deals_rating ON deals(rating);
CREATE INDEX IF NOT EXISTS idx_deals_timestamp ON deals(timestamp DESC);

-- Step 7: Add column comments
COMMENT ON COLUMN deals.title IS 'Product name';
COMMENT ON COLUMN deals.verified_mrp IS 'Original MRP from official site';
COMMENT ON COLUMN deals.verified_price IS 'Discounted price from official site';
COMMENT ON COLUMN deals.verified_discount IS 'Discount percentage';
COMMENT ON COLUMN deals.link IS 'E-commerce product link';
COMMENT ON COLUMN deals.rating IS 'Product rating from official site';

-- Step 8: Create a simple view for best deals
CREATE OR REPLACE VIEW best_deals AS
SELECT 
    title,
    verified_mrp,
    verified_price,
    verified_discount,
    link,
    rating,
    timestamp
FROM deals
WHERE verified_discount IS NOT NULL
  AND verified_discount > 0
ORDER BY verified_discount DESC, rating DESC NULLS LAST;

-- Verify the clean schema
-- Run this to check your table structure:
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'deals'
-- ORDER BY ordinal_position;

COMMIT;
