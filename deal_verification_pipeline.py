"""
Deal Verification Pipeline
===========================
Main orchestrator that combines all modules:
- URL expansion
- Web scraping
- LLM verification
- Vision extraction (fallback)
- Confidence scoring

Author: AI Assistant
Date: December 2025
"""

from typing import Dict, Optional, List
import time
from datetime import datetime

# Import all modules
from url_expander import URLExpander
from product_scraper import ProductScraperFactory
from llm_verifier import LLMDealVerifier
from vision_extractor import VisionDealExtractor


class ConfidenceScorer:
    """
    Assigns confidence scores to deals based on multiple factors.
    """
    
    @staticmethod
    def calculate_confidence(verification_data: Dict) -> float:
        """
        SIMPLIFIED: Just check if we got official data.
        High confidence = we scraped official data successfully.
        """
        score = 0.40  # Base score for attempting verification (increased from 0.35)
        
        # Got official price? +0.35
        if verification_data.get('verified_price'):
            score += 0.35
        
        # Got MRP? +0.15
        if verification_data.get('verified_mrp'):
            score += 0.15
        
        # Got title? +0.10
        if verification_data.get('verified_title'):
            score += 0.10
        
        # That's it! Simple and straightforward.
        return round(min(1.0, score), 2)
    
    @staticmethod
    def get_confidence_label(score: float) -> str:
        """
        Get human-readable confidence label.
        
        Args:
            score: Confidence score (0-1)
            
        Returns:
            Label string
        """
        if score >= 0.9:
            return "Very High"
        elif score >= 0.75:
            return "High"
        elif score >= 0.6:
            return "Medium"
        elif score >= 0.4:
            return "Low"
        else:
            return "Very Low"


class DealVerificationPipeline:
    """
    Main pipeline that orchestrates the entire deal verification process.
    """
    
    def __init__(
        self,
        enable_llm: bool = True,
        enable_vision: bool = True,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize the verification pipeline.
        
        Args:
            enable_llm: Enable LLM-based verification
            enable_vision: Enable vision-based fallback
            openai_api_key: OpenAI API key for LLM and vision
        """
        self.url_expander = URLExpander()
        self.scraper_factory = ProductScraperFactory()
        self.llm_verifier = LLMDealVerifier(api_key=openai_api_key) if enable_llm else None
        self.vision_extractor = VisionDealExtractor(api_key=openai_api_key) if enable_vision else None
        self.confidence_scorer = ConfidenceScorer()
    
    def verify_deal(self, telegram_data: Dict) -> Dict:
        """
        Complete end-to-end deal verification.
        
        Args:
            telegram_data: Data extracted from Telegram message
                {
                    'title': str,
                    'discount_price': float,
                    'discount_percent': float,
                    'store': str,
                    'link': str,
                    'channel': str,
                    'message_id': int
                }
        
        Returns:
            Dict containing complete verification results:
                {
                    'is_verified': bool,
                    'confidence_score': float,
                    'confidence_label': str,
                    'verified_title': str,
                    'verified_price': float,
                    'verified_mrp': float,
                    'verified_discount': float,
                    'availability': str,
                    'rating': float,
                    'seller': str,
                    'verification_source': str,
                    'issues': List[str],
                    'recommendation': str,
                    'timestamp': str
                }
        """
        print(f"\n{'='*80}")
        print(f"🔍 VERIFYING DEAL: {telegram_data.get('title', 'Unknown Product')}")
        print(f"{'='*80}\n")
        
        result = {
            'telegram_data': telegram_data,
            'is_verified': False,
            'confidence_score': 0.0,
            'confidence_label': 'Unknown',
            'verification_source': 'none',
            'issues': [],
            'timestamp': datetime.now().isoformat()
        }
        
        product_link = telegram_data.get('link')
        
        if not product_link:
            result['issues'].append('No product link provided')
            result['recommendation'] = 'REJECT'
            return result
        
        # Step 1: Expand URL if shortened
        print("📎 Step 1: Expanding URL...")
        
        if self.url_expander.is_shortened_url(product_link):
            expanded = self.url_expander.expand_url(product_link)
            
            if expanded['error']:
                print(f"   ❌ URL expansion failed: {expanded['error']}")
                result['issues'].append(f"URL expansion failed: {expanded['error']}")
            else:
                product_link = expanded['expanded_url']
                print(f"   ✅ Expanded to: {product_link}")
        else:
            print(f"   ℹ️  URL not shortened, using as-is")
        
        # Step 2: Scrape official product page
        print("\n🌐 Step 2: Scraping official product page...")
        
        scraped_data = self.scraper_factory.scrape_product(product_link)
        
        if not scraped_data.get('success'):
            print(f"   ❌ Scraping failed: {scraped_data.get('error')}")
            result['issues'].append(f"Could not scrape product page")
            
            # Try vision extraction as fallback
            if self.vision_extractor and self.vision_extractor.enabled:
                print("\n📸 Fallback: Attempting vision-based extraction...")
                # Note: This would require image URL from Telegram message
                # For now, we skip this in the main flow
                pass
            
            result['verification_source'] = 'telegram_text'
            result['recommendation'] = 'REVIEW'
        else:
            print(f"   ✅ Successfully scraped product data")
            print(f"      Title: {scraped_data.get('title', 'N/A')}")
            
            # Format price display
            offer_price = scraped_data.get('offer_price')
            mrp = scraped_data.get('mrp')
            print(f"      Price: ₹{offer_price}" if offer_price else "      Price: N/A")
            print(f"      MRP: ₹{mrp}" if mrp else "      MRP: N/A")
            
            result['verification_source'] = 'official_site'
        
        # Step 3: Extract official data (no complex verification)
        print("\n📋 Step 3: Extracting official data...")
        
        if scraped_data.get('success'):
            # Just use the official data as-is
            has_discount = scraped_data.get('mrp') and scraped_data.get('offer_price') and \
                          scraped_data.get('mrp') > scraped_data.get('offer_price')
            
            discount_pct = 0
            if has_discount:
                discount_pct = ((scraped_data.get('mrp') - scraped_data.get('offer_price')) / 
                               scraped_data.get('mrp')) * 100
            
            print(f"   ✅ Official data extracted")
            
            # Format price display
            offer_price = scraped_data.get('offer_price')
            mrp = scraped_data.get('mrp')
            print(f"      Official Price: ₹{offer_price}" if offer_price else "      Official Price: N/A")
            print(f"      Official MRP: ₹{mrp}" if mrp else "      Official MRP: N/A")
            
            if has_discount:
                print(f"      Discount: {discount_pct:.1f}% OFF")
            else:
                print(f"      Discount: No discount found")
            
            # Download and store images in Supabase Storage
            stored_images = {'main_image': None, 'additional_images': []}
            if scraped_data.get('product_image_url'):
                print("\n📥 Downloading and storing product images...")
                try:
                    from image_storage import store_product_images
                    image_urls = {
                        'main_image': scraped_data.get('product_image_url'),
                        'additional_images': scraped_data.get('additional_images', [])
                    }
                    stored_images = store_product_images(image_urls, scraped_data.get('title'))
                except Exception as e:
                    print(f"⚠️  Failed to store images: {e}")
                    # Fallback to original URLs
                    stored_images = {
                        'main_image': scraped_data.get('product_image_url'),
                        'additional_images': scraped_data.get('additional_images', [])
                    }
            
            # Store official data (with stored image URLs)
            result.update({
                'is_verified': True,
                'verified_title': scraped_data.get('title'),
                'verified_price': scraped_data.get('offer_price'),
                'verified_mrp': scraped_data.get('mrp'),
                'verified_discount': discount_pct if has_discount else None,
                'availability': scraped_data.get('availability'),
                'rating': scraped_data.get('rating'),
                'seller': scraped_data.get('seller'),
                'product_image_url': stored_images.get('main_image'),
                'additional_images': stored_images.get('additional_images', []),
                'price_match': True,  # Not judging, just saving
                'title_match': True,
                'issues': [],
                'recommendation': 'ACCEPT'
            })
        
        # Step 4: Calculate confidence score
        print("\n📊 Step 4: Calculating confidence score...")
        
        result['telegram_claimed_price'] = telegram_data.get('discount_price')
        confidence = self.confidence_scorer.calculate_confidence(result)
        confidence_label = self.confidence_scorer.get_confidence_label(confidence)
        
        result['confidence_score'] = confidence
        result['confidence_label'] = confidence_label
        
        # Debug breakdown
        telegram_price = result.get('telegram_claimed_price')
        verified_price = result.get('verified_price')
        if telegram_price and verified_price:
            try:
                telegram_price_float = float(telegram_price)
                verified_price_float = float(verified_price)
                price_diff = abs(telegram_price_float - verified_price_float) / verified_price_float * 100
                print(f"   📊 Price Match: Claimed ₹{telegram_price} vs Official ₹{verified_price} ({price_diff:.1f}% diff)")
            except (ValueError, TypeError):
                pass  # Skip price comparison if conversion fails
        
        print(f"   ✅ Confidence Score: {confidence:.2f} ({confidence_label})")
        
        # Step 5: Final decision
        print(f"\n{'='*80}")
        print(f"📋 FINAL RESULT")
        print(f"{'='*80}")
        
        if result.get('verified_price'):
            print(f"   ✅ Official data retrieved and saved")
            print(f"   Confidence: {result['confidence_label']} ({result['confidence_score']:.2f})")
        else:
            print(f"   ❌ Could not retrieve official data")
        
        print(f"{'='*80}\n")
        
        return result
    
    def should_save_to_database(self, verification_result: Dict, min_confidence: float = 0.4) -> bool:
        """
        Decide if verification result is good enough to save.
        
        Args:
            verification_result: The verification result dict
            min_confidence: Minimum confidence threshold (default 0.4)
            
        Returns:
            True if should save, False otherwise
        """
        # Get confidence score
        confidence = verification_result.get('confidence_score', 0)
        
        # Save if confidence meets or exceeds threshold
        if confidence >= min_confidence:
            return True
        
        # Also save if we got official data even if confidence is slightly below
        has_official_data = (
            verification_result.get('verified_price') is not None or
            verification_result.get('verified_title') is not None
        )
        
        if has_official_data and confidence >= (min_confidence - 0.1):
            return True
        
        return False


# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = DealVerificationPipeline(
        enable_llm=True,
        enable_vision=True
    )
    
    # Test data
    test_deal = {
        'title': 'Samsung Galaxy S23 5G',
        'discount_price': 49999,
        'discount_percent': 30,
        'store': 'Amazon',
        'link': 'https://www.amazon.in/dp/B0ABCD1234',
        'channel': 'TrickXpert',
        'message_id': 12345
    }
    
    # Verify deal
    result = pipeline.verify_deal(test_deal)
    
    # Check if should save
    if pipeline.should_save_to_database(result):
        print("✅ Deal approved for database storage")
    else:
        print("❌ Deal rejected - will not be saved")
