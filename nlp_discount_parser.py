"""
NLP Discount Parser Module
===========================
Parses unstructured e-commerce discount messages from Telegram channels
and extracts structured product information.

Author: AI Assistant
Date: December 2025
"""

import re
from datetime import datetime, timezone
from typing import Dict, Optional, List
import unicodedata


class DiscountMessageParser:
    """
    Main parser class for extracting structured data from discount messages.
    """
    
    # Store detection patterns
    STORE_PATTERNS = {
        'Amazon': r'(?i)\b(amazon|amzn\.to|amazon\.in)\b',
        'Flipkart': r'(?i)\b(flipkart|fkrt\.it|flipkart\.com)\b',
        'Myntra': r'(?i)\b(myntra|myntra\.com)\b',
        'Ajio': r'(?i)\b(ajio|ajio\.com)\b',
        'Meesho': r'(?i)\b(meesho|meesho\.com)\b',
        'Nykaa': r'(?i)\b(nykaa|nykaa\.com)\b',
        'Snapdeal': r'(?i)\b(snapdeal|snapdeal\.com)\b',
    }
    
    # Category keywords mapping
    CATEGORY_KEYWORDS = {
        'electronics': [
            'phone', 'mobile', 'smartphone', 'laptop', 'tablet', 'computer',
            'earbuds', 'headphone', 'speaker', 'smartwatch', 'watch', 'tv',
            'television', 'camera', 'airdopes', 'earphone', 'charger', 'powerbank',
            'keyboard', 'mouse', 'monitor', 'processor', 'gpu', 'ram'
        ],
        'fashion': [
            'shirt', 'tshirt', 't-shirt', 'jeans', 'dress', 'saree', 'kurta',
            'shoes', 'sneakers', 'sandal', 'footwear', 'clothing', 'apparel',
            'jacket', 'hoodie', 'trouser', 'skirt', 'ethnic', 'western',
            'blazer', 'suit', 'lehenga', 'kurti', 'pant', 'shorts'
        ],
        'home': [
            'furniture', 'sofa', 'bed', 'mattress', 'chair', 'table',
            'decor', 'curtain', 'cushion', 'lamp', 'kitchenware', 'utensil',
            'appliance', 'mixer', 'grinder', 'cooker', 'oven', 'refrigerator',
            'flask', 'bottle', 'cooktop', 'water purifier', 'purifier', 'ro',
            'heater', 'geyser', 'fan', 'cooler', 'iron', 'vacuum', 'kettle'
        ],
        'beauty': [
            'cosmetics', 'makeup', 'lipstick', 'foundation', 'skincare',
            'cream', 'lotion', 'perfume', 'shampoo', 'conditioner', 'serum',
            'facewash', 'sunscreen', 'moisturizer', 'kajal', 'eyeliner'
        ],
        'books': [
            'book', 'novel', 'magazine', 'journal', 'notebook', 'diary',
            'stationery', 'pen', 'pencil'
        ],
        'grocery': [
            'grocery', 'food', 'snack', 'beverage', 'oil', 'rice', 'dal',
            'flour', 'sugar', 'tea', 'coffee', 'biscuit', 'chocolate'
        ],
        'sports': [
            'sports', 'fitness', 'gym', 'yoga', 'exercise', 'dumbbell',
            'treadmill', 'cycle', 'bicycle', 'cricket', 'football', 'badminton'
        ]
    }
    
    def __init__(self):
        """Initialize the parser."""
        pass
    
    def clean_text(self, raw_text: str) -> str:
        """
        Clean and normalize raw text by removing emojis and extra whitespace.
        
        Args:
            raw_text (str): Raw input text with potential emojis and formatting
            
        Returns:
            str: Cleaned text
        """
        if not raw_text:
            return ""
        
        # Remove emojis using unicode categories
        text = ''.join(
            char for char in raw_text 
            if unicodedata.category(char) not in ['So', 'Cn']
        )
        
        # Remove extra whitespaces and normalize
        text = ' '.join(text.split())
        
        # Remove common decorative characters
        text = re.sub(r'[•·●◆◇★☆▪▫]', '', text)
        
        return text.strip()
    
    def extract_store(self, text: str) -> str:
        """
        Detect e-commerce store from text using pattern matching.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Store name or "Other"
        """
        text_lower = text.lower()
        
        for store, pattern in self.STORE_PATTERNS.items():
            if re.search(pattern, text_lower):
                return store
        
        return "Other"
    
    def extract_prices(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract MRP, discount price, and discount percentage from text with improved accuracy.
        
        Args:
            text (str): Input text containing price information
            
        Returns:
            dict: Dictionary with 'mrp', 'discount_price', 'discount_percent'
        """
        result = {
            'mrp': None,
            'discount_price': None,
            'discount_percent': None
        }
        
        # Normalize text
        text = text.replace(',', '')  # Remove commas from numbers
        
        # Extract percentage FIRST (most reliable)
        percent_pattern = r'(\d+)\s*%\s*(?:off|discount|Off)?'
        percent_match = re.search(percent_pattern, text, re.IGNORECASE)
        if percent_match:
            pct = int(percent_match.group(1))
            # Validate percentage (1-99%)
            if 1 <= pct <= 99:
                result['discount_percent'] = str(pct)
        
        # Priority 1: Look for explicit discount price patterns (most specific)
        discount_patterns = [
            r'(?:at|@|for|just|only)\s+(?:Rs\.?\s*|₹\s*)(\d{2,6})\b',  # "at Rs.664"
            r'(?:starting\s+from|starts\s+at)\s+(?:Rs\.?\s*|₹\s*)(\d{2,6})\b',  # "starting from Rs.664"
            r'(?:price|deal|offer)\s*:?\s*(?:Rs\.?\s*|₹\s*)(\d{2,6})\b',  # "price: Rs.664"
            r'(?:now|today)\s+(?:Rs\.?\s*|₹\s*)(\d{2,6})\b',  # "now Rs.664"
        ]
        
        for pattern in discount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price = int(match.group(1))
                # Validate price range (₹10 to ₹500,000)
                if 10 <= price <= 500000:
                    result['discount_price'] = str(price)
                    break
        
        # Priority 2: Look for explicit MRP patterns
        mrp_patterns = [
            r'(?:MRP|M\.R\.P\.?|mrp)\s*:?\s*(?:Rs\.?\s*|₹\s*)(\d{2,6})\b',  # "MRP: Rs.1299"
            r'(?:original\s+price|was|worth)\s+(?:Rs\.?\s*|₹\s*)(\d{2,6})\b',  # "was Rs.1999"
        ]
        
        for pattern in mrp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price = int(match.group(1))
                # Validate price range
                if 10 <= price <= 500000:
                    result['mrp'] = str(price)
                    break
        
        # Priority 3: If no explicit patterns, find all prices with currency symbols
        if not result['discount_price']:
            # Only match prices with clear currency indicators
            currency_price_pattern = r'(?:Rs\.?\s*|₹\s*)(\d{2,6})\b'
            price_matches = re.findall(currency_price_pattern, text, re.IGNORECASE)
            
            if price_matches:
                valid_prices = []
                for p in price_matches:
                    price_val = int(p)
                    # Filter valid price range and avoid phone numbers (10-digit)
                    if 10 <= price_val <= 500000 and len(p) <= 6:
                        valid_prices.append(price_val)
                
                # Remove duplicates and sort
                valid_prices = sorted(set(valid_prices))
                
                if len(valid_prices) == 1:
                    result['discount_price'] = str(valid_prices[0])
                elif len(valid_prices) >= 2:
                    # Smallest is discount, largest is MRP
                    result['discount_price'] = str(valid_prices[0])
                    # Only set MRP if it's significantly higher than discount (at least 10% more)
                    if valid_prices[-1] > valid_prices[0] * 1.1:
                        result['mrp'] = str(valid_prices[-1])
        
        # Validate and clean up results
        if result['mrp'] and result['discount_price']:
            mrp_val = int(result['mrp'])
            disc_val = int(result['discount_price'])
            
            # If MRP <= discount price, clear MRP
            if mrp_val <= disc_val:
                result['mrp'] = None
            # If discount price > MRP, swap them
            elif disc_val > mrp_val:
                result['mrp'], result['discount_price'] = result['discount_price'], result['mrp']
        
        # Calculate missing percentage if we have both valid prices
        if result['mrp'] and result['discount_price'] and not result['discount_percent']:
            try:
                mrp_val = float(result['mrp'])
                disc_val = float(result['discount_price'])
                if mrp_val > disc_val:
                    percent = ((mrp_val - disc_val) / mrp_val) * 100
                    result['discount_percent'] = str(int(round(percent)))
            except (ValueError, ZeroDivisionError):
                pass
        
        # Calculate missing MRP if we have discount price and valid percentage
        if not result['mrp'] and result['discount_price'] and result['discount_percent']:
            try:
                disc_val = float(result['discount_price'])
                percent = float(result['discount_percent'])
                # Only calculate if percentage is reasonable (10-90%)
                if 10 <= percent <= 90:
                    mrp_val = disc_val / (1 - percent / 100)
                    # Only set if result is reasonable
                    if mrp_val <= 500000:
                        result['mrp'] = str(int(round(mrp_val)))
            except (ValueError, ZeroDivisionError):
                pass
        
        return result
    
    def extract_link(self, text: str) -> Optional[str]:
        """
        Extract product URL from text.
        
        Args:
            text (str): Input text
            
        Returns:
            str or None: Extracted URL or None if not found
        """
        # Pattern for URLs (including shortened URLs)
        url_patterns = [
            r'https?://[^\s]+',  # Standard URLs
            r'(?:amzn\.to|fkrt\.it|myntra\.com|ajio\.com)/[^\s]+',  # Shortened URLs
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                url = match.group(0)
                # Clean trailing punctuation
                url = re.sub(r'[,\.;:!?\)]+$', '', url)
                return url
        
        return None
    
    def extract_title(self, text: str) -> str:
        """
        Extract product title from text - handles real-world Telegram discount messages.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Extracted product title
        """
        # Return early if message is URL-only
        if re.match(r'^https?://', text.strip()):
            return "Product"
        
        # Clean text
        cleaned = text
        cleaned = re.sub(r'\*+', '', cleaned)  # Remove markdown
        cleaned = re.sub(r'_+', '', cleaned)
        cleaned = re.sub(r'[🔥😍❤️‍🔥💥⚡️✨🎉🎁👇⭐️💯🛒📦🎯✅]', '', cleaned)  # Remove emojis
        
        # Remove markdown links [text](url)
        cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)
        
        # Split into lines
        lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
        
        # Find the first line that looks like a product description
        product_line = None
        
        for line in lines:
            # Skip URLs
            if line.startswith('http'):
                continue
            
            # Skip action prompts
            if re.match(r'^(buy now|click|link|join|subscribe|available only|don\'t miss)', line, re.IGNORECASE):
                continue
            
            # Skip "Get X" lines (usually service promotions, not products)
            if re.match(r'^get\s+\d+', line, re.IGNORECASE):
                continue
            
            # Skip pure instructions/descriptions in Hindi
            if any(word in line.lower() for word in ['lelo', 'krne', 'hoga', 'krdena', 'auto-charged']):
                continue
            
            # Skip lines that are just "Good Rating" or similar
            if re.match(r'^(good\s+rating|rating|review)s?$', line, re.IGNORECASE):
                continue
            
            # This looks like a product line - take it
            if len(line) > 10:
                product_line = line
                break
        
        if not product_line:
            return "Product"
        
        # Extract the FIRST product mention from multi-product lines
        # Pattern: "Store Loot/Deal : Product at/starts at Price"
        # Example: "AJIO Loot : Levi's Jeans Starts at 650."
        
        title = product_line
        
        # Remove store + discount phrases at start (e.g., "AJIO Loot :", "Myntra Loot : Flat 80% Off On")
        title = re.sub(r'^.*?(loot|deal|offer|sale)\s*:\s*(flat\s+\d+%\s+off\s+on\s+)?', '', title, flags=re.IGNORECASE)
        
        # Remove percentage patterns at start (e.g., "⚡58% Off - ", "67% discount")
        title = re.sub(r'^⚡?\d+%?\s+off\s*[-:]?\s*', '', title, flags=re.IGNORECASE)
        
        # Remove "[Many Options]" and similar brackets
        title = re.sub(r'\[many options\]', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\[[^\]]{1,30}\]', '', title)  # Remove short bracketed text
        
        # Remove "Upto X% Off On" at the start
        title = re.sub(r'^upto\s+\d+%\s+off\s+on\s+', '', title, flags=re.IGNORECASE)
        
        # If multi-line had multiple products, we already took first line
        # But if single line has "Product1 : Link\nProduct2 : Link", we've handled it
        
        # Extract up to price mention (keep "at Price" in title as it's meaningful)
        # But stop before the next product/section starts
        
        # Find where the first product description ends
        # Usually before: next colon, "Men's :", "Women's :", "Boy's :", etc.
        match = re.search(r'((?:men\'?s?|women\'?s?|boy\'?s?|girl\'?s?|kid\'?s?)\s*:)', title, re.IGNORECASE)
        if match:
            # Take everything before the gender-specific section
            title = title[:match.start()].strip()
        
        # Remove "upto X% off" mid-sentence
        title = re.sub(r'\s+upto\s+\d+%?\s+off\b', '', title, flags=re.IGNORECASE)
        
        # Remove "starting from" phrases
        title = re.sub(r'\s+starting\s+from\b.*$', '', title, flags=re.IGNORECASE)
        
        # Remove "Apply X% Off Coupon" and similar patterns
        title = re.sub(r'\s*apply\s+₹?\d+%?\s+off\s+coupon.*$', '', title, flags=re.IGNORECASE)
        
        # Remove @ store mentions (e.g., "@ flipkart")
        title = re.sub(r'\s*@\s*\w+.*$', '', title, flags=re.IGNORECASE)
        
        # Remove price patterns from title (e.g., "at ₹2699", "at Rs.664")
        title = re.sub(r'\s+at\s+(?:₹|rs\.?)\s*\d+', '', title, flags=re.IGNORECASE)
        
        # Remove trailing period
        title = re.sub(r'\s*\.\s*$', '', title)
        
        # Remove "free trial" and everything after
        title = re.sub(r'\bfree trial\b.*', '', title, flags=re.IGNORECASE)
        
        # Remove URLs that might have slipped through
        title = re.sub(r'https?://[^\s]+', '', title)
        
        # Clean whitespace
        title = ' '.join(title.split())
        title = title.strip(' :-.,;!?*_#')
        
        # Validation
        if len(title) < 5:
            return "Product"
        
        # Check for generic/invalid titles (expanded list)
        generic_words = [
            'product', 'item', 'deal', 'offer', 'sale', 'buy', 'good rating', 'buy now',
            'big bold sale', 'biggest sale', 'all branded product', 'many options',
            'hot deal', 'best deal', 'super sale', 'mega sale', 'flash sale',
            'special offer', 'limited offer', 'exclusive deal', 'top deal',
            'amazing deal', 'great offer', 'best offer', 'discount', 'coupon',
            'shopping', 'online shopping', 'shop now', 'order now',
            'clothing starts', 'products', 'items', 'options available',
            'deals starts', 'offer starts', 'sale starts', 'new arrival',
            'new arrivals', 'latest deals', 'trending', 'best price',
            'lowest price', 'special price', 'exclusive', 'limited time'
        ]
        if title.lower() in generic_words:
            return "Product"
        
        # Check if title is too short and meaningless
        if len(title.split()) <= 1 and title.lower() not in ['jeans', 'shirt', 'watch', 'phone', 'laptop']:
            return "Product"
        
        # Check if title is just generic words (e.g., "Options Available", "Great Deal")
        generic_patterns = [
            r'^(options?|deals?|offers?|sales?|items?|products?)\s+(available|here|now)$',
            r'^(shop|buy|order|get|grab)\s+(now|here|today)$',
            r'^(hot|best|top|super|mega|flash)\s+(deal|offer|sale)s?$',
            r'^\d+\s*%?\s*(off|discount)$',
        ]
        for pattern in generic_patterns:
            if re.match(pattern, title, re.IGNORECASE):
                return "Product"
        
        # Check if title contains too many promotional keywords (indicates it's not a product name)
        promo_keywords = ['big bold', 'biggest', 'don\'t miss', 'scroll down', 'all loots', 'branded product', 'only at', 'price', 'options', 'available']
        promo_count = sum(1 for keyword in promo_keywords if keyword in title.lower())
        if promo_count >= 2:  # If 2+ promotional keywords, it's generic
            return "Product"
        
        # Check if it's just a number + words (like "172 Good Rating")
        if re.match(r'^\d+\s+\w+(\s+\w+)?$', title) and not any(word in title.lower() for word in ['pack', 'shirt', 'jeans', 'pcs', 'pieces']):
            return "Product"
        
        # Check if title starts with generic words
        if re.match(r'^(all|many|various|multiple|different)\s+(options?|items?|products?)', title, re.IGNORECASE):
            return "Product"
        
        # Limit length
        if len(title) > 80:
            title = title[:80].rsplit(' ', 1)[0].strip()
        
        return title
    
    def categorize_product(self, text: str) -> str:
        """
        Classify product into a category based on keywords.
        
        Args:
            text (str): Input text (title or full message)
            
        Returns:
            str: Category name
        """
        text_lower = text.lower()
        
        # Score each category
        category_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return "other"
    
    def parse_discount_message(self, raw_text: str) -> Dict:
        """
        Main parsing function that orchestrates all extraction steps.
        
        Args:
            raw_text (str): Raw discount message text
            
        Returns:
            dict: Structured product information
        """
        # Initialize result dictionary (removed mrp and discount_percent)
        result = {
            "title": "",
            "store": "",
            "discount_price": "",
            "link": "",
            "category": "",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Handle empty input
        if not raw_text or not raw_text.strip():
            return result
        
        # Clean the text
        cleaned_text = self.clean_text(raw_text)
        
        # Extract store
        result["store"] = self.extract_store(cleaned_text)
        
        # Extract only discount price (no MRP or discount_percent)
        prices = self.extract_prices(cleaned_text)
        result["discount_price"] = prices.get("discount_price") or ""
        
        # Extract link
        link = self.extract_link(raw_text)  # Use raw text for better URL detection
        result["link"] = link or ""
        
        # Extract title
        result["title"] = self.extract_title(cleaned_text)
        
        # Categorize product
        result["category"] = self.categorize_product(cleaned_text)
        
        return result


# Convenience function for direct use
def parse_discount_message(raw_text: str) -> Dict:
    """
    Parse a discount message and return structured data.
    
    Args:
        raw_text (str): Raw discount message text
        
    Returns:
        dict: Structured product information
    """
    parser = DiscountMessageParser()
    return parser.parse_discount_message(raw_text)


# ============================================================================
# TEST CASES
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("NLP DISCOUNT PARSER - TEST CASES")
    print("=" * 80)
    print()
    
    # Initialize parser
    parser = DiscountMessageParser()
    
    # Test cases
    test_messages = [
        # Test 1: Amazon deal with emoji
        """🔥 Amazon Deal: Boat Airdopes 441 at ₹999 (MRP ₹2999) – 67% Off. Buy Now: https://amzn.to/xxxx""",
        
        # Test 2: Flipkart deal with different formatting
        """Flipkart Offer!! Redmi A3 now at just Rs. 6499 (Original Price: Rs 7999). Link: https://fkrt.it/xxxxx""",
        
        # Test 3: Myntra fashion deal
        """🛍️ MYNTRA SALE: Nike Air Max Shoes - Was Rs.8999, Now Only Rs.4499 (50% OFF) 
        https://myntra.com/deal123""",
        
        # Test 4: Multiple emojis and complex formatting
        """⚡🔥💥 Amazon Lightning Deal! 
        Samsung Galaxy M14 5G 
        MRP: ₹14,999 
        Deal Price: ₹9,999 
        Discount: 33% 
        🔗 https://amzn.to/samsung-m14""",
        
        # Test 5: Minimal information
        """Ajio: Denim Jeans for Rs.799. Limited stock! https://ajio.com/jeans""",
        
        # Test 6: No link
        """Flipkart: HP Laptop at Rs.35999 (was Rs.45999)""",
        
        # Test 7: Beauty product
        """Nykaa Deal! Lakme Foundation only ₹350 (MRP ₹699) - 50% off""",
        
        # Test 8: Electronics with detailed specs
        """🎧 Boat Rockerz 450 Bluetooth Headphones at just ₹1299 on Amazon (Original: ₹2990)
        Grab now: https://amzn.to/rockerz450"""
    ]
    
    # Run tests
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST CASE {i}")
        print(f"{'─' * 80}")
        print(f"RAW MESSAGE:\n{message}")
        print(f"\n{'·' * 80}")
        
        result = parser.parse_discount_message(message)
        
        print("PARSED OUTPUT:")
        for key, value in result.items():
            if key != 'timestamp':  # Skip timestamp for cleaner output
                print(f"  {key:18s}: {value}")
        
        print()
    
    print("=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)
