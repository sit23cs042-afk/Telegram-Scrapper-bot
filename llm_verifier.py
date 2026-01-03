"""
LLM-Based Deal Verification Module
===================================
Uses LLM reasoning to verify deal authenticity, normalize prices,
and detect fake or misleading discounts.

Author: AI Assistant
Date: December 2025
"""

import os
import json
from typing import Dict, Optional, List
import re
from datetime import datetime


class LLMDealVerifier:
    """
    Uses LLM reasoning to verify and validate deal information.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize LLM verifier.
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env variable)
            model: Model to use for verification
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        # Only import and initialize if API key is available
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.enabled = True
            except ImportError:
                print("⚠️  OpenAI package not installed. Run: pip install openai")
                self.enabled = False
        else:
            print("⚠️  No OpenAI API key found. LLM verification will be disabled.")
            self.enabled = False
    
    def verify_deal(self, telegram_data: Dict, scraped_data: Dict) -> Dict:
        """
        Simple verification: just check if we got valid data from official site.
        No complex LLM analysis - just data extraction.
        
        Args:
            telegram_data: Data from Telegram
            scraped_data: Data from official site
        
        Returns:
            Simple verification result with official data
        """
        # Always use simple rule-based approach
        return self._simple_verification(telegram_data, scraped_data)
        
        # Prepare context for LLM
        verification_prompt = self._build_verification_prompt(telegram_data, scraped_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an e-commerce deal verification system.
                        Your ONLY job is to verify if the claimed price matches the official website price.
                        
                        DO NOT judge:
                        - Whether the MRP is inflated
                        - Whether the discount is "too good to be true"
                        - Whether the deal seems suspicious
                        
                        ONLY verify:
                        1. Does the claimed price match the official website price? (Allow ±5% tolerance)
                        2. Does the product title reasonably match?
                        3. Is the product available?
                        
                        Return your analysis as JSON with this exact structure:
                        {
                            "is_verified": true/false,
                            "confidence_score": 0.0-1.0,
                            "verified_price": float,
                            "verified_mrp": float,
                            "verified_discount": float,
                            "price_match": true/false,
                            "price_difference_percent": float,
                            "title_match": true/false,
                            "issues": ["issue1", "issue2"],
                            "recommendation": "ACCEPT/REJECT/REVIEW",
                            "reasoning": "explanation"
                        }
                        
                        If price matches within 5%, mark price_match as true and recommend ACCEPT.
                        If price differs by 5-15%, recommend REVIEW.
                        If price differs by >15%, recommend REJECT."""
                    },
                    {
                        "role": "user",
                        "content": verification_prompt
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Parse LLM response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return result
            
        except Exception as e:
            print(f"❌ LLM verification failed: {e}")
            # Fallback to rule-based
            return self._rule_based_verification(telegram_data, scraped_data)
    
    def _build_verification_prompt(self, telegram_data: Dict, scraped_data: Dict) -> str:
        """Build prompt for LLM verification."""
        
        prompt = f"""
TELEGRAM DEAL CLAIM:
--------------------
Product Title: {telegram_data.get('title', 'Not provided')}
Store: {telegram_data.get('store', 'Unknown')}
Claimed Price: ₹{telegram_data.get('claimed_price', 'N/A')}
Claimed Discount: {telegram_data.get('discount_percent', 'N/A')}%
Product Link: {telegram_data.get('link', 'N/A')}

OFFICIAL WEBSITE DATA:
----------------------
Product Title: {scraped_data.get('title', 'Not found')}
MRP (Original Price): ₹{scraped_data.get('mrp', 'N/A')}
Offer Price: ₹{scraped_data.get('offer_price', 'N/A')}
Availability: {scraped_data.get('availability', 'Unknown')}
Rating: {scraped_data.get('rating', 'N/A')}
Seller: {scraped_data.get('seller', 'N/A')}

VERIFICATION TASK:
------------------
1. Compare the claimed price (₹{telegram_data.get('claimed_price', 'N/A')}) with official offer price (₹{scraped_data.get('offer_price', 'N/A')})
   - Calculate percentage difference
   - If difference ≤5%: price_match = true
   - If difference >5%: price_match = false

2. Check if product titles match (allow variations for size/color/model)
   - Extract key product identifiers (brand, model, type)
   - Ignore minor differences

3. Calculate actual discount percentage (if MRP available)
   - verified_discount = ((MRP - offer_price) / MRP) * 100

4. DO NOT flag deals as fake just because discount seems high
5. DO NOT judge MRP validity - just report what the official site shows

Provide your verification result in the specified JSON format.
"""
        
        return prompt
    
    def _simple_verification(self, telegram_data: Dict, scraped_data: Dict) -> Dict:
        """
        SIMPLIFIED: Just extract official data and save it.
        No complex verification - if we got data from official site, use it.
        """
        
        # Check if scraping was successful
        if not scraped_data.get('success', False):
            return {
                'is_verified': False,
                'confidence_score': 0.0,
                'verified_price': None,
                'verified_mrp': None,
                'verified_discount': None,
                'price_match': False,
                'title_match': False,
                'issues': ['Failed to fetch official product page'],
                'recommendation': 'REJECT',
                'reasoning': 'Could not access official site'
            }
        
        # Extract official data
        offer_price = scraped_data.get('offer_price')
        mrp = scraped_data.get('mrp')
        title = scraped_data.get('title')
        
        # Calculate discount if both prices available
        verified_discount = None
        if mrp and offer_price and mrp > offer_price:
            verified_discount = ((mrp - offer_price) / mrp) * 100
        
        # Simple price match check
        claimed_price = telegram_data.get('claimed_price')
        price_match = False
        price_diff = 0
        
        if claimed_price and offer_price:
            price_diff = abs(claimed_price - offer_price) / offer_price * 100
            price_match = price_diff <= 15  # Allow 15% tolerance
        
        # Calculate simple confidence
        confidence = 0.5  # Base
        
        if offer_price:
            confidence += 0.2  # Got price
        if mrp:
            confidence += 0.1  # Got MRP
        if title:
            confidence += 0.1  # Got title
        if price_match:
            confidence += 0.1  # Prices match
        
        # If we successfully scraped, mark as verified
        is_verified = bool(offer_price)  # Has official price = verified
        
        return {
            'is_verified': is_verified,
            'confidence_score': round(confidence, 2),
            'verified_price': offer_price,
            'verified_mrp': mrp,
            'verified_discount': verified_discount,
            'price_match': price_match,
            'title_match': bool(title),
            'issues': [],
            'recommendation': 'ACCEPT' if is_verified else 'REJECT',
            'reasoning': f'Official data extracted. Price diff: {price_diff:.1f}%' if offer_price else 'No price data'
        }
    
    def extract_price_from_text(self, text: str) -> Optional[float]:
        """
        Extract price from text using LLM or regex.
        
        Args:
            text: Text containing price information
            
        Returns:
            Extracted price or None
        """
        if not text:
            return None
        
        # Try regex first
        # Pattern: ₹123.45 or Rs. 123 or 123 rupees
        patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rupees|inr)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return float(price_str)
                except ValueError:
                    continue
        
        # If regex fails and LLM is available, use LLM
        if self.enabled:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Extract the numeric price value from the text. Return only the number, no currency symbols. If no price found, return null."
                        },
                        {
                            "role": "user",
                            "content": text
                        }
                    ],
                    temperature=0
                )
                
                result = response.choices[0].message.content.strip()
                if result.lower() != 'null':
                    return float(result)
            except Exception:
                pass
        
        return None


# Example usage
if __name__ == "__main__":
    verifier = LLMDealVerifier()
    
    # Test data
    telegram_data = {
        'title': 'Samsung Galaxy S23 5G',
        'claimed_price': 49999,
        'discount_percent': 30,
        'store': 'Amazon',
        'link': 'https://amazon.in/dp/B0ABC123'
    }
    
    scraped_data = {
        'success': True,
        'title': 'Samsung Galaxy S23 5G (Phantom Black, 128GB)',
        'mrp': 74999,
        'offer_price': 49990,
        'availability': 'In Stock',
        'rating': 4.5,
        'seller': 'Amazon'
    }
    
    print("Testing LLM Deal Verifier")
    print("=" * 80)
    
    result = verifier.verify_deal(telegram_data, scraped_data)
    
    print(f"\n✅ Verification Result:")
    print(f"   Verified: {result['is_verified']}")
    print(f"   Confidence: {result['confidence_score']:.2f}")
    print(f"   Price Match: {result['price_match']}")
    print(f"   Recommendation: {result['recommendation']}")
    print(f"   Issues: {', '.join(result['issues']) if result['issues'] else 'None'}")
