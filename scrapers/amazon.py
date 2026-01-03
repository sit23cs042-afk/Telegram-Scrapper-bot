"""
Amazon India Daily Deals Scraper
Scrapes deals from Amazon India's deals page
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


class AmazonScraper:
    """Scraper for Amazon India daily deals"""
    
    BASE_URL = "https://www.amazon.in"
    DEALS_URL = "https://www.amazon.in/s?k=deals&rh=p_n_pct-off-with-tax%3A2665400031"  # Updated to search page
    
    def __init__(self):
        self.website_name = "Amazon India"
    
    def scrape_deals(self, max_deals: int = 50) -> List[Dict]:
        """
        Scrape daily deals from Amazon India search with discount filter
        
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
            
            # Find search results - this is the working selector
            deal_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
            
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
        """Extract deal information from a search result container"""
        try:
            # Product name - h2 inside search results
            name_elem = container.find('h2', class_=re.compile(r'a-size'))
            product_name = clean_text(name_elem.get_text()) if name_elem else None
            
            if not product_name:
                return None
            
            # Product URL - link from h2
            link_elem = container.find('a', href=re.compile(r'/dp/|/gp/'))
            product_url = urljoin(self.BASE_URL, link_elem['href']) if link_elem else None
            
            if not product_url or not validate_url(product_url):
                return None
            
            # Image URL
            img_elem = container.find('img', {'class': 's-image'})
            image_url = img_elem.get('src') if img_elem else None
            
            # Discounted price - look for a-price-whole
            price_whole = container.find('span', class_='a-price-whole')
            price_fraction = container.find('span', class_='a-price-fraction')
            
            discounted_price = None
            if price_whole:
                price_text = price_whole.get_text().replace(',', '') + (price_fraction.get_text() if price_fraction else '')
                discounted_price = extract_price(price_text)
            
            # Original price - look for a-text-price
            original_price_elem = container.find('span', class_='a-price a-text-price')
            original_price = None
            if original_price_elem:
                price_text = original_price_elem.get_text()
                original_price = extract_price(price_text)
            
            # Calculate discount
            discount_percentage = calculate_discount_percentage(original_price, discounted_price)
            
            # Category - extract from breadcrumb or set default
            category = 'Electronics'
            
            # Brand - try to extract from title
            brand = self._extract_brand_from_name(product_name)
            
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
        
        # Common brand patterns
        common_brands = [
            'Samsung', 'Apple', 'OnePlus', 'Xiaomi', 'Realme', 'Vivo', 'Oppo',
            'Sony', 'LG', 'Boat', 'Noise', 'Fire-Boltt', 'Amazon Basics',
            'Redmi', 'Mi', 'Poco', 'Motorola', 'Nokia', 'Google', 'Nothing'
        ]
        
        for brand in common_brands:
            if brand.lower() in product_name.lower():
                return brand
        
        # Return first word as brand
        words = product_name.split()
        return words[0] if words else 'Unknown'


def scrape_amazon_deals(max_deals: int = 50) -> List[Dict]:
    """
    Main function to scrape Amazon India deals
    
    Args:
        max_deals: Maximum number of deals to scrape
        
    Returns:
        List of deal dictionaries
    """
    scraper = AmazonScraper()
    return scraper.scrape_deals(max_deals)


if __name__ == "__main__":
    # Test the scraper
    deals = scrape_amazon_deals(max_deals=10)
    print(f"\nScraped {len(deals)} deals:")
    for i, deal in enumerate(deals[:5], 1):
        print(f"\n{i}. {deal['product_name'][:60]}")
        print(f"   Price: ₹{deal.get('discounted_price', 'N/A')}")
        print(f"   Discount: {deal.get('discount_percentage', 'N/A')}%")
