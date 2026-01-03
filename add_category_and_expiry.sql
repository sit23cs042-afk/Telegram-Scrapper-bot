-- Add Category and Offer Expiry Fields Migration
-- ================================================
-- This script adds category classification and automatic offer expiry
-- Run this in your Supabase SQL editor

-- Step 1: Add new columns to deals table
ALTER TABLE deals 
ADD COLUMN IF NOT EXISTS category VARCHAR(50),
ADD COLUMN IF NOT EXISTS offer_end_date TIMESTAMP;

-- Step 2: Create index for category-based queries
CREATE INDEX IF NOT EXISTS idx_deals_category ON deals(category);
CREATE INDEX IF NOT EXISTS idx_deals_offer_end_date ON deals(offer_end_date);

-- Step 3: Add column comments
COMMENT ON COLUMN deals.category IS 'Product category (electronics, fashion, home, grocery, health, sports, toys, books, other)';
COMMENT ON COLUMN deals.offer_end_date IS 'Date when the offer expires - product will be automatically removed after this date';

-- Step 4: Create view for active deals only (not expired)
CREATE OR REPLACE VIEW active_deals AS
SELECT 
    id,
    title,
    verified_mrp,
    verified_price,
    verified_discount,
    link,
    rating,
    category,
    offer_end_date,
    product_image_url,
    additional_images,
    timestamp
FROM deals
WHERE offer_end_date IS NULL OR offer_end_date > NOW()
ORDER BY timestamp DESC;

-- Step 5: Create view for best deals by category
CREATE OR REPLACE VIEW best_deals_by_category AS
SELECT 
    category,
    title,
    verified_mrp,
    verified_price,
    verified_discount,
    link,
    rating,
    offer_end_date,
    product_image_url,
    timestamp
FROM deals
WHERE (offer_end_date IS NULL OR offer_end_date > NOW())
  AND verified_discount IS NOT NULL
  AND verified_discount > 0
ORDER BY category, verified_discount DESC, rating DESC NULLS LAST;

-- Step 6: Create function to cleanup expired deals
CREATE OR REPLACE FUNCTION cleanup_expired_deals()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete deals where offer_end_date has passed
    DELETE FROM deals
    WHERE offer_end_date IS NOT NULL 
      AND offer_end_date < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Step 7: Create scheduled job to run cleanup daily
-- (Note: You need to enable pg_cron extension in Supabase first)
-- Go to Database > Extensions and enable "pg_cron"
-- Then run this:
/*
SELECT cron.schedule(
    'cleanup-expired-deals',  -- Job name
    '0 2 * * *',              -- Run daily at 2 AM
    $$SELECT cleanup_expired_deals()$$
);
*/

-- Step 8: Get category statistics
CREATE OR REPLACE VIEW category_statistics AS
SELECT 
    category,
    COUNT(*) as total_deals,
    COUNT(CASE WHEN offer_end_date IS NULL OR offer_end_date > NOW() THEN 1 END) as active_deals,
    COUNT(CASE WHEN offer_end_date IS NOT NULL AND offer_end_date <= NOW() THEN 1 END) as expired_deals,
    AVG(verified_discount) as avg_discount,
    MAX(verified_discount) as max_discount,
    AVG(rating) as avg_rating
FROM deals
GROUP BY category
ORDER BY total_deals DESC;

-- Step 9: Test the cleanup function manually
-- SELECT cleanup_expired_deals();

-- Step 10: View active deals by category
-- SELECT category, COUNT(*) as count
-- FROM active_deals
-- GROUP BY category
-- ORDER BY count DESC;

-- ✅ Migration complete!
-- Your database now supports:
-- 1. Category-wise product organization
-- 2. Automatic removal of expired offers
-- 3. Views for active deals and category statistics
-- 4. Scheduled cleanup job (needs pg_cron extension)
