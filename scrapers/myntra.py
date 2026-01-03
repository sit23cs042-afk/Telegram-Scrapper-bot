"""
Myntra Daily Deals Scraper
Uses browser automation to handle JavaScript content
"""

import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

from utils.helpers import (
    extract_price,
    calculate_discount_percentage,
    clean_text,
    validate_url,
    format_deal_data,
    rate_limiter
)
from utils.browser_helper import BrowserHelper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MyntraScraper:
    """Scraper for Myntra daily deals"""
    
    BASE_URL = "https://www.myntra.com"
    
    def __init__(self):
        self.website_name = "Myntra"
    
    def scrape_deals(self, max_deals: int = 50) -> List[Dict]:
        """
        Scrape deals from Myntra using browser automation
        
        Args:
            max_deals: Maximum number of deals to scrape
            
        Returns:
            List of deal dictionaries
        """
        logger.info(f"🔍 Starting {self.website_name} scraper with browser automation...")
        deals = []
        
        # Category URLs to scrape
        category_urls = [
            "https://www.myntra.com/men-tshirts?plaEnabled=false",
            "https://www.myntra.com/women-kurtas?plaEnabled=false",
            "https://www.myntra.com/shoes?plaEnabled=false"
        ]
        
        try:
            with BrowserHelper() as browser:
                for category_url in category_urls:
                    if len(deals) >= max_deals:
                        break
                    
                    # Respect rate limiting
                    rate_limiter.wait()
                    
                    logger.info(f"Fetching {category_url}...")
                    
                    # Fetch page with browser
                    html_content = browser.fetch_page_with_scroll(category_url, scroll_count=2)
                    
                    if not html_content:
                        logger.warning(f"Failed to fetch {category_url}")
                        continue
                    
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Find product containers
                    deal_containers = soup.find_all('li', class_=re.compile(r'product-base'))
                    
                    logger.info(f"Found {len(deal_containers)} products")
                    
                    for container in deal_containers:
                        if len(deals) >= max_deals:
                            break
                        deal = self._extract_deal_from_container(container)
                        if deal:
                            deals.append(deal)
            
            logger.info(f"✓ Scraped {len(deals)} deals from {self.website_name}")
            
        except Exception as e:
            logger.error(f"Error scraping {self.website_name}: {e}")
        
        return deals
    
    def _extract_deal_from_container(self, container) -> Optional[Dict]:
        """Extract deal information from a container element"""
        try:
            # Product name
            name_elem = container.find(['h3', 'h4'], class_=re.compile(r'product-product|product-brand'))
            if not name_elem:
                name_elem = container.find('img', alt=True)
            
            product_name = None
            if name_elem:
                if name_elem.name == 'img':
                    product_name = name_elem.get('alt')
                else:
                    product_name = clean_text(name_elem.get_text())
            
            if not product_name:
                return None
            
            # Product URL
            link_elem = container.find('a', href=True)
            product_url = None
            if link_elem:
                product_url = urljoin(self.BASE_URL, link_elem['href'])
            
            if not product_url or not validate_url(product_url):
                return None
            
            # Image URL
            img_elem = container.find('img', src=True)
            image_url = img_elem['src'] if img_elem else None
            
            # Brand
            brand_elem = container.find(['h3'], class_=re.compile(r'product-brand'))
            brand = clean_text(brand_elem.get_text()) if brand_elem else self._extract_brand_from_name(product_name)
            
            # Prices
            price_elem = container.find(['span', 'div'], class_=re.compile(r'product-discountedPrice'))
            original_price_elem = container.find(['span', 'div'], class_=re.compile(r'product-strike'))
            
            discounted_price = extract_price(price_elem.get_text()) if price_elem else None
            original_price = extract_price(original_price_elem.get_text()) if original_price_elem else None
            
            # Extract discount percentage
            discount_elem = container.find(['span', 'div'], class_=re.compile(r'product-discountPercentage'))
            if discount_elem:
                discount_text = discount_elem.get_text()
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match and not original_price and discounted_price:
                    discount_pct = int(discount_match.group(1))
                    original_price = discounted_price / (1 - discount_pct / 100)
            
            # Calculate discount
            discount_percentage = calculate_discount_percentage(original_price, discounted_price)
            
            # Category (Myntra is primarily fashion)
            category = 'Fashion & Apparel'
            
            deal = {
                'product_name': product_name,
                'category': category,
                'brand': brand,
                'original_price': original_price,
                'discounted_price': discounted_price,
                'discount_percentage': discount_percentage,
                'product_url': product_url,
                'image_url': image_url,
                'website_name': self.website_name,
                'deal_type': 'Daily Deal'
            }
            
            return format_deal_data(deal)
            
        except Exception as e:
            logger.debug(f"Error extracting deal: {e}")
            return None
    
    def _extract_brand_from_name(self, product_name: str) -> str:
        """Try to extract brand from product name"""
        if not product_name:
            return 'Unknown'
        
        fashion_brands = [
            'Puma', 'Adidas', 'Nike', 'Reebok', 'Levis', 'H&M', 'Zara',
            'UCB', 'Allen Solly', 'Peter England', 'Van Heusen', 'Louis Philippe',
            'Roadster', 'HERE&NOW', 'Mast & Harbour', 'Wrogn', 'Flying Machine'
        ]
        
        for brand in fashion_brands:
            if brand.lower() in product_name.lower():
                return brand
        
        words = product_name.split()
        return words[0] if words else 'Unknown'


def scrape_myntra_deals(max_deals: int = 50) -> List[Dict]:
    """
    Main function to scrape Myntra deals
    
    Args:
        max_deals: Maximum number of deals to scrape
        
    Returns:
        List of deal dictionaries
    """
    scraper = MyntraScraper()
    return scraper.scrape_deals(max_deals)


if __name__ == "__main__":
    # Test the scraper
    deals = scrape_myntra_deals(max_deals=10)
    print(f"\nScraped {len(deals)} deals:")
    for i, deal in enumerate(deals[:5], 1):
        print(f"\n{i}. {deal['product_name'][:60]}")
        print(f"   Brand: {deal['brand']}")
        print(f"   Price: ₹{deal.get('discounted_price', 'N/A')}")
        print(f"   Discount: {deal.get('discount_percentage', 'N/A')}%")
