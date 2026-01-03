"""
OCR & Vision-Based Deal Extraction Module
==========================================
Fallback module for extracting deal information from images when:
- Product page is inaccessible
- Data is in image format (screenshots, promotional banners)
- Text-based scraping fails

Uses OCR and vision AI to extract product details from images.

Author: AI Assistant
Date: December 2025
"""

import os
import base64
from typing import Dict, Optional, List
from io import BytesIO
import requests
from PIL import Image


class VisionDealExtractor:
    """
    Extracts deal information from images using OCR and vision AI.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize vision extractor.
        
        Args:
            api_key: OpenAI API key for GPT-4 Vision
            model: Vision model to use (gpt-4-vision-preview or gpt-4o)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.enabled = True
            except ImportError:
                print("⚠️  OpenAI package not installed. Run: pip install openai")
                self.enabled = False
        else:
            print("⚠️  No OpenAI API key found. Vision extraction will be disabled.")
            self.enabled = False
    
    def extract_from_image_url(self, image_url: str) -> Dict:
        """
        Extract deal information from an image URL.
        
        Args:
            image_url: URL of the product/deal image
            
        Returns:
            Dict containing extracted information:
                {
                    'success': bool,
                    'title': str,
                    'price': float,
                    'mrp': float,
                    'discount': float,
                    'store': str,
                    'brand': str,
                    'features': List[str],
                    'confidence': float,
                    'raw_text': str
                }
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Vision AI not enabled (no API key)',
                'method': 'vision_extraction'
            }
        
        try:
            # Create prompt for vision model
            prompt = """Analyze this product/deal image and extract the following information:

1. Product Title/Name
2. Current Price (offer price)
3. Original Price (MRP) if shown
4. Discount percentage if shown
5. Store/Platform name
6. Brand name
7. Key features or specifications visible
8. Any promotional text or urgency indicators (limited time, stock, etc.)

Return the information as JSON with this structure:
{
    "title": "product name",
    "price": numeric_value,
    "mrp": numeric_value,
    "discount": numeric_percentage,
    "store": "store name",
    "brand": "brand name",
    "features": ["feature1", "feature2"],
    "promotional_text": "any urgency/promo text",
    "confidence": 0.0-1.0
}

If any field is not visible, set it to null. Be accurate with prices - extract exact numbers."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse response
            import json
            result_text = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = result_text
            if '```json' in result_text:
                json_match = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                json_match = result_text.split('```')[1].strip()
            
            result = json.loads(json_match)
            result['success'] = True
            result['method'] = 'vision_extraction'
            result['raw_response'] = result_text
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Vision extraction failed: {str(e)}',
                'method': 'vision_extraction'
            }
    
    def extract_from_image_file(self, image_path: str) -> Dict:
        """
        Extract deal information from a local image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict containing extracted information
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Vision AI not enabled (no API key)',
                'method': 'vision_extraction'
            }
        
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Determine image format
            image_ext = os.path.splitext(image_path)[1].lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }.get(image_ext, 'image/jpeg')
            
            # Create data URL
            image_url = f"data:{mime_type};base64,{image_data}"
            
            # Use the same extraction logic
            return self.extract_from_image_url(image_url)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to read image file: {str(e)}',
                'method': 'vision_extraction'
            }
    
    def extract_from_screenshot(self, screenshot_url: str, context: str = "") -> Dict:
        """
        Extract deal information from a product page screenshot.
        
        Args:
            screenshot_url: URL or path to screenshot
            context: Additional context about what to look for
            
        Returns:
            Dict containing extracted information
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'Vision AI not enabled',
                'method': 'screenshot_extraction'
            }
        
        try:
            prompt = f"""This is a screenshot of an e-commerce product page. Extract the following:

1. Product title/name (usually prominently displayed)
2. Current selling price (offer price, discounted price)
3. Original price (MRP, crossed out price)
4. Discount percentage if shown
5. Availability status (In Stock, Out of Stock)
6. Product rating if visible
7. Seller name if shown
8. Key product features or specifications

{f'Additional context: {context}' if context else ''}

Return as JSON:
{{
    "title": "product name",
    "offer_price": numeric_value,
    "mrp": numeric_value,
    "discount_percent": numeric_value,
    "availability": "status",
    "rating": numeric_value,
    "seller": "seller name",
    "features": ["feature1", "feature2"],
    "confidence": 0.0-1.0
}}

Be precise with prices. Look carefully for crossed-out/strikethrough prices as MRP."""

            # Determine if it's a URL or file path
            if screenshot_url.startswith('http'):
                image_reference = screenshot_url
            else:
                # Local file - encode it
                with open(screenshot_url, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                image_reference = f"data:image/jpeg;base64,{image_data}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_reference}}
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            import json
            result_text = response.choices[0].message.content
            
            # Extract JSON
            if '```json' in result_text:
                json_match = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                json_match = result_text.split('```')[1].strip()
            else:
                json_match = result_text
            
            result = json.loads(json_match)
            result['success'] = True
            result['method'] = 'screenshot_extraction'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Screenshot extraction failed: {str(e)}',
                'method': 'screenshot_extraction'
            }


class OCRExtractor:
    """
    Fallback OCR-based text extraction (using pytesseract or similar).
    Less accurate than vision AI but doesn't require API calls.
    """
    
    def __init__(self):
        """Initialize OCR extractor."""
        try:
            import pytesseract
            self.enabled = True
        except ImportError:
            print("⚠️  pytesseract not installed. OCR extraction disabled.")
            print("   Install with: pip install pytesseract")
            self.enabled = False
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        if not self.enabled:
            return ""
        
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
            
        except Exception as e:
            print(f"❌ OCR extraction failed: {e}")
            return ""
    
    def extract_prices_from_text(self, text: str) -> Dict:
        """
        Extract price information from OCR text using regex.
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dict with extracted prices
        """
        import re
        
        # Price patterns
        price_pattern = r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)'
        prices = []
        
        matches = re.findall(price_pattern, text)
        for match in matches:
            try:
                price = float(match.replace(',', ''))
                prices.append(price)
            except ValueError:
                continue
        
        # Heuristic: usually offer price is smaller, MRP is larger
        prices.sort()
        
        result = {}
        if len(prices) >= 2:
            result['offer_price'] = prices[0]
            result['mrp'] = prices[-1]
        elif len(prices) == 1:
            result['offer_price'] = prices[0]
        
        return result


# Example usage
if __name__ == "__main__":
    # Test vision extraction
    vision_extractor = VisionDealExtractor()
    
    if vision_extractor.enabled:
        print("Vision Extractor is enabled")
        print("=" * 80)
        print("\nTo test, provide an image URL or file path")
    else:
        print("⚠️  Vision Extractor is not enabled")
        print("Set OPENAI_API_KEY environment variable to enable")
    
    # Test OCR extraction
    ocr_extractor = OCRExtractor()
    
    if ocr_extractor.enabled:
        print("\n\nOCR Extractor is enabled")
        print("=" * 80)
    else:
        print("\n⚠️  OCR Extractor is not enabled")
        print("Install pytesseract to enable")
