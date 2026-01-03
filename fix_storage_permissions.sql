-- Fix Supabase Storage Permissions for Image Uploads
-- =====================================================
-- Run this in Supabase SQL Editor to allow image uploads

-- Enable public access to product-images bucket for uploads
INSERT INTO storage.buckets (id, name, public)
VALUES ('product-images', 'product-images', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- Create policy to allow anyone to upload images
CREATE POLICY "Allow public uploads"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'product-images');

-- Create policy to allow anyone to read images
CREATE POLICY "Allow public reads"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'product-images');

-- Create policy to allow updates
CREATE POLICY "Allow public updates"
ON storage.objects FOR UPDATE
TO public
USING (bucket_id = 'product-images');

-- Create policy to allow deletes (optional, for cleanup)
CREATE POLICY "Allow public deletes"
ON storage.objects FOR DELETE
TO public
USING (bucket_id = 'product-images');

-- Verify bucket is public
SELECT id, name, public FROM storage.buckets WHERE id = 'product-images';
