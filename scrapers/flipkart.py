"""
Flipkart Daily Deals Scraper
Scrapes deals from Flipkart's deals page
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


class FlipkartScraper:
    """Scraper for Flipkart daily deals"""
    
    BASE_URL = "https://www.flipkart.com"
    DEALS_URL = "https://www.flipkart.com/search?q=mobile&sort=popularity"  # More reliable search page
    
    def __init__(self):
        self.website_name = "Flipkart"
    
    def scrape_deals(self, max_deals: int = 50) -> List[Dict]:
        """
        Scrape daily deals from Flipkart search results
        
        Args:
            max_deals: Maximum number of deals to scrape
            
        Returns:
            List of deal dictionaries
        """
        logger.info(f"🔍 Starting {self.website_name} scraper...")
        deals = []
        
        # Try multiple search queries to get variety
        search_queries = [
            'https://www.flipkart.com/search?q=mobile&sort=popularity',
            'https://www.flipkart.com/search?q=laptop&sort=popularity',
            'https://www.flipkart.com/search?q=electronics&sort=popularity'
        ]
        
        for search_url in search_queries:
            try:
                # Respect rate limiting
                rate_limiter.wait()
                
                # Fetch search page
                response = fetch_page(search_url, timeout=15)
                if not response:
                    logger.warning(f"Failed to fetch {search_url}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find product links - most reliable selector
                product_links = soup.find_all('a', href=re.compile(r'/p/'))
                
                logger.info(f"Found {len(product_links)} products in search results")
                
                for link in product_links:
                    if len(deals) >= max_deals:
                        break
                        
                    deal = self._extract_deal_from_link(link)
                    if deal:
                        deals.append(deal)
                
                if len(deals) >= max_deals:
                    break
                
            except Exception as e:
                logger.error(f"Error scraping {search_url}: {e}")
                continue
        
        logger.info(f"✓ Scraped {len(deals)} deals from {self.website_name}")
        return deals
    
    def _extract_deal_from_link(self, link_elem) -> Optional[Dict]:
        """Extract deal information from a product link element"""
        try:
            # Product URL
            product_url = urljoin(self.BASE_URL, link_elem.get('href', ''))
            if not product_url or not validate_url(product_url):
                return None
            
            # Product name - from title attribute or text
            product_name = link_elem.get('title') or clean_text(link_elem.get_text())
            if not product_name:
                return None
            
            # Find parent container for more info
            container = link_elem.find_parent('div', class_=re.compile(r'_1AtVbE|slAVV4|CGtC98'))
            if not container:
                container = link_elem
            
            # Image URL
            img_elem = container.find('img')
            image_url = None
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
            
            # Prices - Flipkart uses specific classes
            price_elem = container.find('div', class_=re.compile(r'_30jeq3|_1_WHN1'))
            original_price_elem = container.find('div', class_=re.compile(r'_3I9_wc|_2_R_DZ'))
            
            discounted_price = extract_price(price_elem.get_text()) if price_elem else None
            original_price = extract_price(original_price_elem.get_text()) if original_price_elem else None
            
            # Calculate discount
            discount_percentage = calculate_discount_percentage(original_price, discounted_price)
            
            # Category - default for now
            category = 'Electronics'
            
            # Brand
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
            logger.debug(f"Error extracting deal from link: {e}")
            return None
    
    def _extract_deal_from_container(self, container) -> Optional[Dict]:
        """Extract deal information from a container element"""
        try:
            # Product name
            name_elem = container.find(['div', 'a'], class_=re.compile(r'_4rR01T|s1Q9rs|_2WkVRV'))
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
            link_elem = container if container.name == 'a' else container.find('a', href=True)
            product_url = None
            if link_elem and link_elem.get('href'):
                product_url = urljoin(self.BASE_URL, link_elem['href'])
            
            if not product_url or not validate_url(product_url):
                return None
            
            # Image URL
            img_elem = container.find('img', src=True)
            image_url = img_elem['src'] if img_elem else None
            
            # Prices
            price_elem = container.find(['div'], class_=re.compile(r'_30jeq3|_3I9_wc'))
            original_price_elem = container.find(['div'], class_=re.compile(r'_3Ay6sb|_2_R_DZ'))
            
            discounted_price = extract_price(price_elem.get_text()) if price_elem else None
            original_price = extract_price(original_price_elem.get_text()) if original_price_elem else None
            
            # Extract discount percentage
            discount_elem = container.find(['div', 'span'], class_=re.compile(r'_3Ay6sb|_3xFx9B'))
            if discount_elem:
                discount_text = discount_elem.get_text()
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match and not original_price and discounted_price:
                    discount_pct = int(discount_match.group(1))
                    original_price = discounted_price / (1 - discount_pct / 100)
            
            # Calculate discount
            discount_percentage = calculate_discount_percentage(original_price, discounted_price)
            
            # Category
            category_elem = container.find(['div', 'span'], class_=re.compile(r'_3LWZlK|_2WkVRV'))
            category = clean_text(category_elem.get_text()) if category_elem else 'General'
            
            # Brand
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
                'deal_type': 'Deal of the Day'
            }
            
            return format_deal_data(deal)
            
        except Exception as e:
            logger.debug(f"Error extracting deal: {e}")
            return None
    
    def _extract_brand_from_name(self, product_name: str) -> str:
        """Try to extract brand from product name"""
        if not product_name:
            return 'Unknown'
        
        common_brands = [
            'Samsung', 'Apple', 'OnePlus', 'Xiaomi', 'Realme', 'Vivo', 'Oppo',
            'Sony', 'LG', 'Boat', 'Noise', 'Fire-Boltt', 'Redmi', 'Mi', 'Poco',
            'Motorola', 'Nokia', 'Google', 'Nothing', 'Puma', 'Adidas', 'Nike',
            'Levi', 'H&M', 'Zara', 'UCB', 'Allen Solly', 'Peter England'
        ]
        
        for brand in common_brands:
            if brand.lower() in product_name.lower():
                return brand
        
        words = product_name.split()
        return words[0] if words else 'Unknown'


def scrape_flipkart_deals(max_deals: int = 50) -> List[Dict]:
    """
    Main function to scrape Flipkart deals
    
    Args:
        max_deals: Maximum number of deals to scrape
        
    Returns:
        List of deal dictionaries
    """
    scraper = FlipkartScraper()
    return scraper.scrape_deals(max_deals)


if __name__ == "__main__":
    # Test the scraper
    deals = scrape_flipkart_deals(max_deals=10)
    print(f"\nScraped {len(deals)} deals:")
    for i, deal in enumerate(deals[:5], 1):
        print(f"\n{i}. {deal['product_name'][:60]}")
        print(f"   Price: ₹{deal.get('discounted_price', 'N/A')}")
        print(f"   Discount: {deal.get('discount_percentage', 'N/A')}%")
