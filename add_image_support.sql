-- Add Product Image Support to Database
-- =======================================
-- Run this in your Supabase SQL editor to add image columns
-- Note: Images will be stored in Supabase Storage, URLs stored in these columns

-- Step 1: Create storage bucket for images (run this first in Supabase Dashboard)
-- Go to Storage > Create new bucket > Name: "product-images" > Public: Yes

-- Step 2: Add image columns to deals table
ALTER TABLE deals 
ADD COLUMN IF NOT EXISTS product_image_url TEXT,
ADD COLUMN IF NOT EXISTS additional_images TEXT[],
ADD COLUMN IF NOT EXISTS image_scraped_at TIMESTAMP;

-- Add index for faster image queries
CREATE INDEX IF NOT EXISTS idx_deals_has_image 
ON deals(product_image_url) 
WHERE product_image_url IS NOT NULL;

-- Add column comments for documentation
COMMENT ON COLUMN deals.product_image_url IS 'Main product image URL from official site';
COMMENT ON COLUMN deals.additional_images IS 'Array of additional product image URLs (up to 5)';
COMMENT ON COLUMN deals.image_scraped_at IS 'Timestamp when images were extracted';

-- Update the best_deals view to include images
DROP VIEW IF EXISTS best_deals;
CREATE OR REPLACE VIEW best_deals AS
SELECT 
    title,
    verified_mrp,
    verified_price,
    verified_discount,
    link,
    rating,
    product_image_url,
    additional_images,
    timestamp
FROM deals
WHERE verified_discount IS NOT NULL
  AND verified_discount > 0
ORDER BY verified_discount DESC, rating DESC NULLS LAST;

-- Create view for deals with images
CREATE OR REPLACE VIEW deals_with_images AS
SELECT 
    title,
    verified_mrp,
    verified_price,
    verified_discount,
    link,
    rating,
    product_image_url,
    additional_images,
    image_scraped_at,
    timestamp
FROM deals
WHERE product_image_url IS NOT NULL
ORDER BY timestamp DESC;

-- Verify the schema
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'deals'
ORDER BY ordinal_position;
