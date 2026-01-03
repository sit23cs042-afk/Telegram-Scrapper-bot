-- Add seller detail columns to deals table
-- Run this in Supabase SQL Editor

ALTER TABLE deals ADD COLUMN IF NOT EXISTS seller_name TEXT;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS seller_rating DECIMAL(3, 2);
ALTER TABLE deals ADD COLUMN IF NOT EXISTS is_fulfilled_by_platform BOOLEAN DEFAULT FALSE;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS seller_info JSONB;

-- Update existing records to mark Flipkart/Amazon as platform fulfilled
UPDATE deals 
SET is_fulfilled_by_platform = TRUE,
    seller_name = CASE 
        WHEN link LIKE '%amazon.%' THEN 'Amazon'
        WHEN link LIKE '%flipkart.%' THEN 'Flipkart'
        WHEN link LIKE '%myntra.%' THEN 'Myntra'
        ELSE NULL
    END
WHERE seller_name IS NULL 
  AND (link LIKE '%amazon.%' OR link LIKE '%flipkart.%' OR link LIKE '%myntra.%');
