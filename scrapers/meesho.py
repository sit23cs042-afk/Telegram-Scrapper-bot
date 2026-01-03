"""
Meesho Daily Deals Scraper
Uses browser automation to bypass anti-bot measures
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


class MeeshoScraper:
    """Scraper for Meesho daily deals"""
    
    BASE_URL = "https://www.meesho.com"
    
    def __init__(self):
        self.website_name = "Meesho"
    
    def scrape_deals(self, max_deals: int = 50) -> List[Dict]:
        """
        Scrape deals from Meesho using browser automation
        
        Args:
            max_deals: Maximum number of deals to scrape
            
        Returns:
            List of deal dictionaries
        """
        logger.info(f"🔍 Starting {self.website_name} scraper with browser automation...")
        deals = []
        
        # Category URLs to scrape
        category_urls = [
            "https://www.meesho.com/mens-shirts/pl/4ep",
            "https://www.meesho.com/womens-kurtis/pl/p8s",
            "https://www.meesho.com/s/p/trending"
        ]
        
        try:
            with BrowserHelper() as browser:
                for category_url in category_urls:
                    if len(deals) >= max_deals:
                        break
                    
                    # Respect rate limiting
                    rate_limiter.wait()
                    
                    logger.info(f"Fetching {category_url}...")
                    
                    # Fetch page with browser and scroll to load lazy content
                    html_content = browser.fetch_page_with_scroll(category_url, scroll_count=3)
                    
                    if not html_content:
                        logger.warning(f"Failed to fetch {category_url}")
                        continue
                    
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Find product containers or links
                    deal_containers = soup.find_all('a', href=re.compile(r'/p/'))
                    
                    logger.info(f"Found {len(deal_containers)} products")
                    
                    for container in deal_containers:
                        if len(deals) >= max_deals:
                            break
                        deal = self._extract_deal_from_link(container)
                        if deal:
                            deals.append(deal)
            
            logger.info(f"✓ Scraped {len(deals)} deals from {self.website_name}")
            
        except Exception as e:
            logger.error(f"Error scraping {self.website_name}: {e}")
        
        return deals
    
    def _extract_deal_from_link(self, link_elem) -> Optional[Dict]:
        """Extract deal information from a product link"""
        try:
            # Product URL
            product_url = urljoin(self.BASE_URL, link_elem.get('href', ''))
            if not product_url or not validate_url(product_url):
                return None
            
            # Find parent container
            container = link_elem.find_parent(['div', 'article'])
            if not container:
                container = link_elem
            
            # Product name from img alt or text
            img = container.find('img')
            name_elem = container.find(['p', 'span', 'h2', 'h3'])
            
            product_name = None
            if img and img.get('alt'):
                product_name = clean_text(img['alt'])
            elif name_elem:
                product_name = clean_text(name_elem.get_text())
            
            if not product_name:
                return None
            
            # Image URL
            image_url = img.get('src') or img.get('data-src') if img else None
            
            # Prices
            price_elems = container.find_all(['span', 'p'], class_=re.compile(r'price|Price'))
            
            discounted_price = None
            original_price = None
            
            for elem in price_elems:
                price_text = elem.get_text()
                price = extract_price(price_text)
                if price:
                    if not discounted_price:
                        discounted_price = price
                    elif not original_price and price > discounted_price:
                        original_price = price
            
            # Calculate discount
            discount_percentage = calculate_discount_percentage(original_price, discounted_price)
            
            deal = {
                'product_name': product_name,
                'category': 'Fashion',
                'brand': 'Unknown',
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
            name_elem = container.find(['p', 'span'], class_=re.compile(r'Name|Title'))
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
            price_elem = container.find(['span', 'p'], class_=re.compile(r'Price|price'))
            original_price_elem = container.find(['span', 'p'], class_=re.compile(r'OriginalPrice|strike'))
            
            discounted_price = extract_price(price_elem.get_text()) if price_elem else None
            original_price = extract_price(original_price_elem.get_text()) if original_price_elem else None
            
            # Extract discount percentage
            discount_elem = container.find(['span', 'p'], class_=re.compile(r'Discount|discount'))
            if discount_elem:
                discount_text = discount_elem.get_text()
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match and not original_price and discounted_price:
                    discount_pct = int(discount_match.group(1))
                    original_price = discounted_price / (1 - discount_pct / 100)
            
            # Calculate discount
            discount_percentage = calculate_discount_percentage(original_price, discounted_price)
            
            # Brand
            brand = self._extract_brand_from_name(product_name)
            
            # Category
            category = 'Fashion & Home'
            
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
        
        words = product_name.split()
        return words[0] if words else 'Unknown'


def scrape_meesho_deals(max_deals: int = 50) -> List[Dict]:
    """
    Main function to scrape Meesho deals
    
    Args:
        max_deals: Maximum number of deals to scrape
        
    Returns:
        List of deal dictionaries
    """
    scraper = MeeshoScraper()
    return scraper.scrape_deals(max_deals)


if __name__ == "__main__":
    # Test the scraper
    deals = scrape_meesho_deals(max_deals=10)
    print(f"\nScraped {len(deals)} deals:")
    for i, deal in enumerate(deals[:5], 1):
        print(f"\n{i}. {deal['product_name'][:60]}")
        print(f"   Price: ₹{deal.get('discounted_price', 'N/A')}")
