"""
Reliance Digital Daily Deals Scraper
Scrapes deals from Reliance Digital's deals page
"""

import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

from utils.helpers import (
    fetch_page,
    extract_price,
    calculate_discount_percentage,
    clean_text,
    validate_url,
    format_deal_data,
    rate_limiter
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RelianceDigitalScraper:
    """Scraper for Reliance Digital daily deals"""
    
    BASE_URL = "https://www.reliancedigital.in"
    DEALS_URL = "https://www.reliancedigital.in/deals-and-offers/"
    
    def __init__(self):
        self.website_name = "Reliance Digital"
    
    def scrape_deals(self, max_deals: int = 50) -> List[Dict]:
        """
        Scrape daily deals from Reliance Digital
        
        Args:
            max_deals: Maximum number of deals to scrape
            
        Returns:
            List of deal dictionaries
        """
        logger.info(f"🔍 Starting {self.website_name} scraper...")
        deals = []
        
        try:
            # Respect rate limiting
            rate_limiter.wait()
            
            # Fetch deals page
            response = fetch_page(self.DEALS_URL, timeout=15)
            if not response:
                logger.error(f"Failed to fetch {self.website_name} deals page")
                return deals
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product containers
            deal_containers = soup.find_all('div', class_=re.compile(r'product|item'))
            
            if not deal_containers:
                # Alternative selector
                deal_containers = soup.find_all('li', class_=re.compile(r'product'))
            
            logger.info(f"Found {len(deal_containers)} deal containers")
            
            for container in deal_containers[:max_deals]:
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
            name_elem = container.find(['h3', 'h4', 'a'], class_=re.compile(r'product|title|name'))
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
            brand_elem = container.find(['span', 'div'], class_=re.compile(r'brand'))
            brand = clean_text(brand_elem.get_text()) if brand_elem else self._extract_brand_from_name(product_name)
            
            # Prices
            price_elem = container.find(['span', 'div'], class_=re.compile(r'price|offer'))
            original_price_elem = container.find(['span', 'del'], class_=re.compile(r'old|original|mrp'))
            
            discounted_price = extract_price(price_elem.get_text()) if price_elem else None
            original_price = extract_price(original_price_elem.get_text()) if original_price_elem else None
            
            # Extract discount percentage
            discount_elem = container.find(['span', 'div'], class_=re.compile(r'discount|save'))
            if discount_elem:
                discount_text = discount_elem.get_text()
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match and not original_price and discounted_price:
                    discount_pct = int(discount_match.group(1))
                    original_price = discounted_price / (1 - discount_pct / 100)
            
            # Calculate discount
            discount_percentage = calculate_discount_percentage(original_price, discounted_price)
            
            # Category
            category = 'Electronics & Appliances'
            
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
                'deal_type': 'Deal & Offer'
            }
            
            return format_deal_data(deal)
            
        except Exception as e:
            logger.debug(f"Error extracting deal: {e}")
            return None
    
    def _extract_brand_from_name(self, product_name: str) -> str:
        """Try to extract brand from product name"""
        if not product_name:
            return 'Unknown'
        
        electronics_brands = [
            'Samsung', 'LG', 'Sony', 'Apple', 'OnePlus', 'Xiaomi', 'Realme',
            'Vivo', 'Oppo', 'Boat', 'JBL', 'Philips', 'Panasonic', 'Whirlpool',
            'Godrej', 'Haier', 'Voltas', 'Blue Star', 'Dell', 'HP', 'Lenovo'
        ]
        
        for brand in electronics_brands:
            if brand.lower() in product_name.lower():
                return brand
        
        words = product_name.split()
        return words[0] if words else 'Unknown'


def scrape_reliance_digital_deals(max_deals: int = 50) -> List[Dict]:
    """
    Main function to scrape Reliance Digital deals
    
    Args:
        max_deals: Maximum number of deals to scrape
        
    Returns:
        List of deal dictionaries
    """
    scraper = RelianceDigitalScraper()
    return scraper.scrape_deals(max_deals)


if __name__ == "__main__":
    # Test the scraper
    deals = scrape_reliance_digital_deals(max_deals=10)
    print(f"\nScraped {len(deals)} deals:")
    for i, deal in enumerate(deals[:5], 1):
        print(f"\n{i}. {deal['product_name'][:60]}")
        print(f"   Brand: {deal['brand']}")
        print(f"   Price: ₹{deal.get('discounted_price', 'N/A')}")
