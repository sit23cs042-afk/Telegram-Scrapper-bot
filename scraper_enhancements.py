"""
Product Scraper Enhancements
=============================
Enhances existing scrapers with:
- Stock availability detection
- Coupon/Bank offer extraction
- Final effective price calculation
- Enhanced metadata

Author: AI Assistant
Date: December 2025
"""

from typing import Dict, Optional, List
from bs4 import BeautifulSoup
import re


class StockAvailabilityDetector:
    """Detect stock availability from product pages."""
    
    @staticmethod
    def detect_amazon(soup: BeautifulSoup, html: str) -> Dict:
        """Detect stock status on Amazon."""
        status = {
            'in_stock': True,
            'stock_level': 'unknown',  # 'high', 'medium', 'low', 'out', 'unknown'
            'stock_message': None
        }
        
        # Check availability div
        avail_elem = soup.find('div', {'id': 'availability'})
        if avail_elem:
            avail_text = avail_elem.get_text().lower()
            
            # Out of stock indicators
            if any(x in avail_text for x in ['out of stock', 'unavailable', 'currently unavailable']):
                status['in_stock'] = False
                status['stock_level'] = 'out'
                status['stock_message'] = avail_elem.get_text().strip()
            
            # Low stock indicators
            elif any(x in avail_text for x in ['only', 'left in stock', 'limited stock']):
                status['in_stock'] = True
                status['stock_level'] = 'low'
                status['stock_message'] = avail_elem.get_text().strip()
                
                # Extract number if available
                match = re.search(r'only\s+(\d+)\s+left', avail_text)
                if match:
                    count = int(match.group(1))
                    if count <= 2:
                        status['stock_level'] = 'very_low'
            
            # In stock
            elif any(x in avail_text for x in ['in stock', 'available']):
                status['in_stock'] = True
                status['stock_level'] = 'high'
                status['stock_message'] = avail_elem.get_text().strip()
        
        # Check for "Currently unavailable" message
        if 'Currently unavailable' in html or 'currently unavailable' in html:
            status['in_stock'] = False
            status['stock_level'] = 'out'
        
        return status
    
    @staticmethod
    def detect_flipkart(soup: BeautifulSoup) -> Dict:
        """Detect stock status on Flipkart."""
        status = {
            'in_stock': True,
            'stock_level': 'unknown',
            'stock_message': None
        }
        
        # Check for out of stock button
        button = soup.find('button', string=re.compile('Sold Out|Out of Stock', re.I))
        if button:
            status['in_stock'] = False
            status['stock_level'] = 'out'
            status['stock_message'] = 'Sold Out'
            return status
        
        # Check availability div
        for div in soup.find_all('div'):
            text = div.get_text().lower()
            if 'out of stock' in text or 'sold out' in text:
                status['in_stock'] = False
                status['stock_level'] = 'out'
                status['stock_message'] = div.get_text().strip()
            elif 'hurry, only' in text or 'few left' in text:
                status['stock_level'] = 'low'
                status['stock_message'] = div.get_text().strip()
        
        return status
    
    @staticmethod
    def detect_myntra(soup: BeautifulSoup) -> Dict:
        """Detect stock status on Myntra."""
        status = {
            'in_stock': True,
            'stock_level': 'unknown',
            'stock_message': None
        }
        
        # Myntra shows "SOLD OUT" badge
        sold_out = soup.find(string=re.compile('SOLD OUT|Out of Stock', re.I))
        if sold_out:
            status['in_stock'] = False
            status['stock_level'] = 'out'
            status['stock_message'] = 'Sold Out'
        
        return status
    
    @staticmethod
    def detect_generic(soup: BeautifulSoup, html: str) -> Dict:
        """Generic stock detection for unknown sites."""
        status = {
            'in_stock': True,
            'stock_level': 'unknown',
            'stock_message': None
        }
        
        text_lower = html.lower()
        
        # Out of stock patterns
        out_patterns = ['out of stock', 'sold out', 'unavailable', 'not available']
        if any(pattern in text_lower for pattern in out_patterns):
            status['in_stock'] = False
            status['stock_level'] = 'out'
        
        # Low stock patterns
        low_patterns = ['limited stock', 'low stock', 'hurry', 'few left', 'only.*left']
        if any(re.search(pattern, text_lower) for pattern in low_patterns):
            status['stock_level'] = 'low'
        
        return status


class CouponOfferExtractor:
    """Extract coupon and bank offer details."""
    
    @staticmethod
    def extract_amazon(soup: BeautifulSoup) -> Dict:
        """Extract coupons and offers from Amazon."""
        offers = {
            'coupons': [],
            'bank_offers': [],
            'exchange_offers': [],
            'no_cost_emi': False
        }
        
        # Extract coupons
        coupon_elem = soup.find('span', {'id': 'couponBadge'})
        if not coupon_elem:
            coupon_elem = soup.find('label', {'id': 'couponLabel'})
        if coupon_elem:
            coupon_text = coupon_elem.get_text().strip()
            if coupon_text:
                offers['coupons'].append(coupon_text)
        
        # Extract bank offers
        promo_section = soup.find('div', {'id': 'promoPriceBlockMessage_feature_div'})
        if promo_section:
            for li in promo_section.find_all('li'):
                offer_text = li.get_text().strip()
                if offer_text:
                    if 'bank' in offer_text.lower() or 'card' in offer_text.lower():
                        offers['bank_offers'].append(offer_text)
        
        # Alternative: Look for offer messages
        for span in soup.find_all('span', class_=re.compile('.*promo.*|.*offer.*', re.I)):
            text = span.get_text().strip()
            if text and len(text) > 10:
                if 'bank' in text.lower() or 'card' in text.lower():
                    if text not in offers['bank_offers']:
                        offers['bank_offers'].append(text)
        
        # Exchange offer
        exchange_elem = soup.find(string=re.compile('exchange', re.I))
        if exchange_elem:
            parent = exchange_elem.find_parent()
            if parent:
                exchange_text = parent.get_text().strip()
                if exchange_text:
                    offers['exchange_offers'].append(exchange_text)
        
        # No cost EMI
        if 'no cost emi' in soup.get_text().lower():
            offers['no_cost_emi'] = True
        
        return offers
    
    @staticmethod
    def extract_flipkart(soup: BeautifulSoup) -> Dict:
        """Extract coupons and offers from Flipkart."""
        offers = {
            'coupons': [],
            'bank_offers': [],
            'exchange_offers': [],
            'no_cost_emi': False
        }
        
        # Bank offers section
        for div in soup.find_all('div', class_=re.compile('.*offer.*|.*promo.*', re.I)):
            text = div.get_text().strip()
            if 'bank' in text.lower() or 'card' in text.lower():
                if text and len(text) > 10 and text not in offers['bank_offers']:
                    offers['bank_offers'].append(text)
        
        # Exchange offer
        if 'exchange offer' in soup.get_text().lower():
            for elem in soup.find_all(string=re.compile('exchange', re.I)):
                parent = elem.find_parent()
                if parent:
                    text = parent.get_text().strip()
                    if text and 'exchange' in text.lower():
                        offers['exchange_offers'].append(text)
                        break
        
        # No cost EMI
        if 'no cost emi' in soup.get_text().lower():
            offers['no_cost_emi'] = True
        
        return offers
    
    @staticmethod
    def extract_generic(soup: BeautifulSoup) -> Dict:
        """Generic offer extraction."""
        offers = {
            'coupons': [],
            'bank_offers': [],
            'exchange_offers': [],
            'no_cost_emi': False
        }
        
        page_text = soup.get_text().lower()
        
        # Look for bank offers
        for elem in soup.find_all(string=re.compile('bank.*offer|card.*offer|cashback', re.I)):
            parent = elem.find_parent()
            if parent:
                text = parent.get_text().strip()
                if text and len(text) > 10:
                    offers['bank_offers'].append(text)
        
        # No cost EMI
        if 'no cost emi' in page_text:
            offers['no_cost_emi'] = True
        
        return offers


class FinalPriceCalculator:
    """Calculate final effective price after all offers."""
    
    @staticmethod
    def calculate(base_price: float, offers: Dict, additional_discount: Optional[float] = None) -> Dict:
        """
        Calculate final effective price.
        
        Args:
            base_price: Current selling price
            offers: Dict with coupons, bank_offers, etc.
            additional_discount: Additional discount amount/percentage
        
        Returns:
            Dict with price breakdown
        """
        breakdown = {
            'base_price': base_price,
            'coupon_discount': 0,
            'bank_discount': 0,
            'additional_discount': additional_discount or 0,
            'total_discount': 0,
            'final_price': base_price,
            'savings': 0
        }
        
        # Extract coupon discount
        for coupon in offers.get('coupons', []):
            discount = FinalPriceCalculator._extract_discount_amount(coupon, base_price)
            if discount > 0:
                breakdown['coupon_discount'] += discount
        
        # Extract bank offer discount
        for bank_offer in offers.get('bank_offers', []):
            discount = FinalPriceCalculator._extract_discount_amount(bank_offer, base_price)
            if discount > 0:
                breakdown['bank_discount'] += discount
        
        # Calculate total
        breakdown['total_discount'] = (
            breakdown['coupon_discount'] + 
            breakdown['bank_discount'] + 
            breakdown['additional_discount']
        )
        
        breakdown['final_price'] = max(0, base_price - breakdown['total_discount'])
        breakdown['savings'] = breakdown['total_discount']
        
        return breakdown
    
    @staticmethod
    def _extract_discount_amount(offer_text: str, base_price: float) -> float:
        """Extract discount amount from offer text."""
        # Look for percentage discount (e.g., "10% off")
        pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', offer_text)
        if pct_match:
            percentage = float(pct_match.group(1))
            return (base_price * percentage) / 100
        
        # Look for flat discount (e.g., "₹500 off")
        flat_match = re.search(r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)', offer_text)
        if flat_match:
            amount_str = flat_match.group(1).replace(',', '')
            return float(amount_str)
        
        # Look for "Flat 500" pattern
        flat_match2 = re.search(r'flat\s+(\d+)', offer_text, re.I)
        if flat_match2:
            return float(flat_match2.group(1))
        
        return 0


class ProductScraperEnhancer:
    """Main class to enhance scraped product data."""
    
    def __init__(self):
        self.stock_detector = StockAvailabilityDetector()
        self.offer_extractor = CouponOfferExtractor()
        self.price_calculator = FinalPriceCalculator()
    
    def enhance(self, scraped_data: Dict, soup: BeautifulSoup, html: str, url: str) -> Dict:
        """
        Enhance scraped product data with additional information.
        
        Args:
            scraped_data: Original scraped data
            soup: BeautifulSoup object
            html: Raw HTML
            url: Product URL
        
        Returns:
            Enhanced data dictionary
        """
        # Detect platform
        platform = self._detect_platform(url)
        
        # Detect stock availability
        stock_status = self._detect_stock(platform, soup, html)
        scraped_data['stock_status'] = stock_status['stock_level']
        scraped_data['in_stock'] = stock_status['in_stock']
        scraped_data['stock_message'] = stock_status['stock_message']
        
        # Extract offers
        offers = self._extract_offers(platform, soup)
        scraped_data['offers'] = offers
        scraped_data['has_coupon'] = len(offers['coupons']) > 0
        scraped_data['has_bank_offer'] = len(offers['bank_offers']) > 0
        scraped_data['has_exchange'] = len(offers['exchange_offers']) > 0
        scraped_data['no_cost_emi'] = offers['no_cost_emi']
        
        # Calculate final effective price
        base_price = scraped_data.get('offer_price') or scraped_data.get('price')
        if base_price:
            price_breakdown = self.price_calculator.calculate(base_price, offers)
            scraped_data['price_breakdown'] = price_breakdown
            scraped_data['final_effective_price'] = price_breakdown['final_price']
            scraped_data['total_savings'] = price_breakdown['savings']
        
        return scraped_data
    
    def _detect_platform(self, url: str) -> str:
        """Detect e-commerce platform from URL."""
        url_lower = url.lower()
        if 'amazon' in url_lower:
            return 'amazon'
        elif 'flipkart' in url_lower:
            return 'flipkart'
        elif 'myntra' in url_lower:
            return 'myntra'
        elif 'ajio' in url_lower:
            return 'ajio'
        elif 'meesho' in url_lower:
            return 'meesho'
        else:
            return 'generic'
    
    def _detect_stock(self, platform: str, soup: BeautifulSoup, html: str) -> Dict:
        """Detect stock availability based on platform."""
        if platform == 'amazon':
            return self.stock_detector.detect_amazon(soup, html)
        elif platform == 'flipkart':
            return self.stock_detector.detect_flipkart(soup)
        elif platform == 'myntra':
            return self.stock_detector.detect_myntra(soup)
        else:
            return self.stock_detector.detect_generic(soup, html)
    
    def _extract_offers(self, platform: str, soup: BeautifulSoup) -> Dict:
        """Extract offers based on platform."""
        if platform == 'amazon':
            return self.offer_extractor.extract_amazon(soup)
        elif platform == 'flipkart':
            return self.offer_extractor.extract_flipkart(soup)
        else:
            return self.offer_extractor.extract_generic(soup)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    print("🧪 Product Scraper Enhancements - Test Mode\n")
    
    enhancer = ProductScraperEnhancer()
    
    # Test price calculation
    test_offers = {
        'coupons': ['Apply coupon SAVE10 for 10% off'],
        'bank_offers': ['Get ₹500 instant discount on HDFC cards'],
        'exchange_offers': [],
        'no_cost_emi': True
    }
    
    breakdown = enhancer.price_calculator.calculate(10000, test_offers)
    
    print("💰 Price Breakdown:")
    print(f"  Base Price: ₹{breakdown['base_price']}")
    print(f"  Coupon Discount: ₹{breakdown['coupon_discount']}")
    print(f"  Bank Discount: ₹{breakdown['bank_discount']}")
    print(f"  Total Discount: ₹{breakdown['total_discount']}")
    print(f"  Final Price: ₹{breakdown['final_price']}")
    print(f"  Total Savings: ₹{breakdown['savings']}")
    
    print("\n✅ Test completed!")
