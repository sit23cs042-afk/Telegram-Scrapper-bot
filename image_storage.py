"""
Image Storage Module
====================
Downloads product images and uploads them to Supabase Storage.

Author: AI Assistant
Date: December 2025
"""

import os
import requests
import hashlib
from typing import Dict, Optional, List
from io import BytesIO
from PIL import Image
from supabase import create_client, Client
import mimetypes


# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://sspufleiikzsazouzkot.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNzcHVmbGVpaWt6c2F6b3V6a290Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU1MjkzNTEsImV4cCI6MjA4MTEwNTM1MX0.Uzh8O4Tn6buf2mhcA4w1JQeCZA-dcpzhm7AovwL4c4E')

# Storage bucket name
STORAGE_BUCKET = 'product-images'

# Initialize Supabase client
supabase: Client = None


def init_storage():
    """Initialize Supabase storage connection and create bucket if needed."""
    global supabase
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Try to create bucket (will fail silently if already exists)
        try:
            supabase.storage.create_bucket(STORAGE_BUCKET, options={'public': True})
            print(f"✅ Created storage bucket: {STORAGE_BUCKET}")
        except Exception:
            # Bucket already exists, that's fine
            pass
            
        print(f"✅ Connected to Supabase Storage")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize Supabase Storage: {e}")
        return False


def download_image(url: str, timeout: int = 10) -> Optional[bytes]:
    """
    Download image from URL.
    
    Args:
        url: Image URL
        timeout: Request timeout in seconds
        
    Returns:
        Image bytes or None if failed
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': url.split('/')[0] + '//' + url.split('/')[2]
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Check if content type is image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            print(f"⚠️  URL is not an image: {content_type}")
            return None
        
        # Read image data
        image_data = response.content
        
        # Validate it's a real image by trying to open it
        try:
            img = Image.open(BytesIO(image_data))
            img.verify()  # Verify it's a valid image
            return image_data
        except Exception as e:
            print(f"⚠️  Invalid image data: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to download image from {url}: {e}")
        return None


def optimize_image(image_data: bytes, max_size: int = 1024) -> Optional[bytes]:
    """
    Optimize image by resizing and compressing.
    
    Args:
        image_data: Original image bytes
        max_size: Maximum width/height in pixels
        
    Returns:
        Optimized image bytes or None if failed
    """
    try:
        img = Image.open(BytesIO(image_data))
        
        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save as JPEG with compression
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        print(f"⚠️  Failed to optimize image: {e}")
        return image_data  # Return original if optimization fails


def upload_to_storage(image_data: bytes, filename: str) -> Optional[str]:
    """
    Upload image to Supabase Storage.
    
    Args:
        image_data: Image bytes
        filename: Filename for storage
        
    Returns:
        Public URL of uploaded image or None if failed
    """
    global supabase
    
    if supabase is None:
        print("❌ Supabase storage not initialized")
        return None
    
    try:
        # Upload to storage
        supabase.storage.from_(STORAGE_BUCKET).upload(
            filename,
            image_data,
            file_options={'content-type': 'image/jpeg'}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(filename)
        
        return public_url
        
    except Exception as e:
        # If file exists, try to get its URL
        if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
            try:
                public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(filename)
                return public_url
            except:
                pass
        
        print(f"❌ Failed to upload to storage: {e}")
        return None


def generate_filename(url: str, product_title: str = None) -> str:
    """
    Generate unique filename for image.
    
    Args:
        url: Original image URL
        product_title: Optional product title for better naming
        
    Returns:
        Unique filename
    """
    # Create hash from URL for uniqueness
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    
    # Clean product title if provided
    if product_title:
        # Take first 30 chars, remove special characters
        clean_title = ''.join(c for c in product_title[:30] if c.isalnum() or c in ' -_')
        clean_title = clean_title.replace(' ', '_').lower()
        filename = f"{clean_title}_{url_hash}.jpg"
    else:
        filename = f"product_{url_hash}.jpg"
    
    return filename


def store_product_images(image_urls: Dict[str, any], product_title: str = None) -> Dict[str, any]:
    """
    Download and store product images.
    
    Args:
        image_urls: Dict with 'main_image' and 'additional_images' URLs
        product_title: Product title for better filenames
        
    Returns:
        Dict with stored image URLs from Supabase Storage
    """
    result = {
        'main_image': None,
        'additional_images': []
    }
    
    # Process main image
    main_url = image_urls.get('main_image')
    if main_url:
        print(f"📥 Downloading main image...")
        image_data = download_image(main_url)
        
        if image_data:
            # Optimize image
            optimized = optimize_image(image_data)
            
            # Generate filename and upload
            filename = generate_filename(main_url, product_title)
            stored_url = upload_to_storage(optimized, filename)
            
            if stored_url:
                result['main_image'] = stored_url
                print(f"✅ Main image stored: {filename}")
            else:
                # Fallback to original URL if upload fails
                result['main_image'] = main_url
                print(f"⚠️  Using original URL as fallback")
    
    # Process additional images
    additional_urls = image_urls.get('additional_images', [])
    for idx, url in enumerate(additional_urls[:5]):  # Max 5 additional
        print(f"📥 Downloading additional image {idx + 1}/{len(additional_urls[:5])}...")
        image_data = download_image(url)
        
        if image_data:
            # Optimize image
            optimized = optimize_image(image_data)
            
            # Generate filename with index
            filename = generate_filename(url, f"{product_title}_img{idx + 1}" if product_title else None)
            stored_url = upload_to_storage(optimized, filename)
            
            if stored_url:
                result['additional_images'].append(stored_url)
                print(f"✅ Additional image {idx + 1} stored")
            else:
                # Fallback to original URL
                result['additional_images'].append(url)
                print(f"⚠️  Using original URL as fallback for image {idx + 1}")
    
    return result


def delete_image(filename: str) -> bool:
    """
    Delete image from Supabase Storage.
    
    Args:
        filename: Filename to delete
        
    Returns:
        True if deleted successfully
    """
    global supabase
    
    if supabase is None:
        return False
    
    try:
        supabase.storage.from_(STORAGE_BUCKET).remove([filename])
        return True
    except Exception as e:
        print(f"❌ Failed to delete image: {e}")
        return False
