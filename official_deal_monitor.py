"""
Official Deal Page Monitor
===========================
Directly scrapes official e-commerce deal pages:
- Today's Deals
- Lightning Deals
- Sale & Offer Zones
- Festival & Bank Offer pages
- Category-specific deal pages

Author: AI Assistant
Date: December 2025
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
import random

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available. Install with: pip install selenium webdriver-manager")


class BaseDealPageMonitor:
    """Base class for deal page monitors."""
    
    def __init__(self, use_selenium: bool = False):
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.driver = None
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Setup session with headers."""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def _get_selenium_driver(self):
        """Initialize Selenium WebDriver."""
        if not self.driver:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            options.add_argument(f'user-agent={self.session.headers["User-Agent"]}')
            
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
        return self.driver
    
    def fetch_page(self, url: str, wait_time: int = 3) -> Optional[str]:
        """Fetch page content."""
        try:
            if self.use_selenium:
                driver = self._get_selenium_driver()
                driver.get(url)
                time.sleep(wait_time)
                return driver.page_source
            else:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def extract_deals(self, html: str) -> List[Dict]:
        """Extract deals from HTML. To be implemented by subclasses."""
        raise NotImplementedError
    
    def cleanup(self):
        """Cleanup resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None


class AmazonDealMonitor(BaseDealPageMonitor):
    """Monitor Amazon India deal pages."""
    
    DEAL_PAGES = [
        'https://www.amazon.in/gp/goldbox',  # Today's Deals
        'https://www.amazon.in/deals',  # All Deals
    ]
    
    CATEGORY_DEAL_PAGES = {
        'electronics': 'https://www.amazon.in/gp/goldbox?deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-electronics%2522%257D',
        'fashion': 'https://www.amazon.in/gp/goldbox?deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-fashion%2522%257D',
        'home': 'https://www.amazon.in/gp/goldbox?deals-widget=%257B%2522version%2522%253A1%252C%2522viewIndex%2522%253A0%252C%2522presetId%2522%253A%2522deals-collection-home%2522%257D',
    }
    
    def extract_deals(self, html: str) -> List[Dict]:
        """Extract deals from Amazon deal pages."""
        deals = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all deal cards
        deal_cards = soup.find_all('div', {'data-deal-id': True})
        
        for card in deal_cards[:50]:  # Limit to 50 deals per page
            try:
                deal = self._extract_deal_from_card(card, soup)
                if deal:
                    deals.append(deal)
            except Exception as e:
                print(f"⚠️  Error extracting deal: {e}")
                continue
        
        return deals
    
    def _extract_deal_from_card(self, card, soup) -> Optional[Dict]:
        """Extract individual deal from card."""
        deal = {}
        
        # Product link
        link_tag = card.find('a', href=True)
        if link_tag:
            deal['url'] = urljoin('https://www.amazon.in', link_tag['href'])
        else:
            return None
        
        # Title
        title_tag = card.find('div', {'id': lambda x: x and 'dealTitle' in x})
        if title_tag:
            deal['title'] = title_tag.get_text(strip=True)
        
        # Price
        price_tag = card.find('span', class_=lambda x: x and 'dealPrice' in str(x).lower())
        if price_tag:
            deal['price'] = price_tag.get_text(strip=True)
        
        # MRP
        mrp_tag = card.find('span', class_=lambda x: x and 'listPrice' in str(x).lower())
        if mrp_tag:
            deal['mrp'] = mrp_tag.get_text(strip=True)
        
        # Discount percentage
        discount_tag = card.find('span', class_=lambda x: x and 'savingsPercentage' in str(x).lower())
        if discount_tag:
            deal['discount'] = discount_tag.get_text(strip=True)
        
        # Deal type
        badge_tag = card.find('span', class_=lambda x: x and 'badge' in str(x).lower())
        if badge_tag:
            deal['deal_type'] = badge_tag.get_text(strip=True)
        else:
            deal['deal_type'] = 'Regular Deal'
        
        # Metadata
        deal['store'] = 'Amazon'
        deal['detected_at'] = datetime.now().isoformat()
        deal['source'] = 'official_deal_page'
        
        return deal if deal.get('url') else None
    
    def monitor_all_pages(self, category: Optional[str] = None) -> List[Dict]:
        """Monitor all Amazon deal pages."""
        all_deals = []
        
        if category and category in self.CATEGORY_DEAL_PAGES:
            pages = [self.CATEGORY_DEAL_PAGES[category]]
        else:
            pages = self.DEAL_PAGES
        
        for page_url in pages:
            print(f"📡 Monitoring: {page_url}")
            html = self.fetch_page(page_url)
            if html:
                deals = self.extract_deals(html)
                all_deals.extend(deals)
                print(f"✅ Found {len(deals)} deals")
            time.sleep(random.uniform(2, 4))  # Respectful scraping
        
        return all_deals


class FlipkartDealMonitor(BaseDealPageMonitor):
    """Monitor Flipkart deal pages."""
    
    DEAL_PAGES = [
        'https://www.flipkart.com/offers-list/content?screen=dynamic&pk=themeViews%3DDealMania~widgetType%3DdealCard~contentType%3Dneo&wid=1.dealCard.OMU',
        'https://www.flipkart.com/offers-store',
    ]
    
    def extract_deals(self, html: str) -> List[Dict]:
        """Extract deals from Flipkart deal pages."""
        deals = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Flipkart uses dynamic content - need Selenium
        if not self.use_selenium:
            print("⚠️  Flipkart requires Selenium. Use use_selenium=True")
            return deals
        
        # Find product cards
        product_cards = soup.find_all('div', class_=lambda x: x and any(c in str(x).lower() for c in ['product', 'card', 'deal']))
        
        for card in product_cards[:50]:
            try:
                deal = self._extract_deal_from_card(card)
                if deal:
                    deals.append(deal)
            except Exception as e:
                continue
        
        return deals
    
    def _extract_deal_from_card(self, card) -> Optional[Dict]:
        """Extract individual deal from Flipkart card."""
        deal = {}
        
        # Link
        link_tag = card.find('a', href=True)
        if link_tag:
            deal['url'] = urljoin('https://www.flipkart.com', link_tag['href'])
        else:
            return None
        
        # Title
        title_tag = card.find(['div', 'a'], class_=lambda x: x and 'title' in str(x).lower())
        if title_tag:
            deal['title'] = title_tag.get_text(strip=True)
        
        # Price
        price_tag = card.find('div', class_=lambda x: x and 'price' in str(x).lower())
        if price_tag:
            deal['price'] = price_tag.get_text(strip=True)
        
        # Discount
        discount_tag = card.find('div', class_=lambda x: x and 'discount' in str(x).lower())
        if discount_tag:
            deal['discount'] = discount_tag.get_text(strip=True)
        
        deal['store'] = 'Flipkart'
        deal['detected_at'] = datetime.now().isoformat()
        deal['source'] = 'official_deal_page'
        deal['deal_type'] = 'Deal of the Day'
        
        return deal if deal.get('url') else None
    
    def monitor_all_pages(self) -> List[Dict]:
        """Monitor all Flipkart deal pages."""
        all_deals = []
        
        for page_url in self.DEAL_PAGES:
            print(f"📡 Monitoring: {page_url}")
            html = self.fetch_page(page_url)
            if html:
                deals = self.extract_deals(html)
                all_deals.extend(deals)
                print(f"✅ Found {len(deals)} deals")
            time.sleep(random.uniform(2, 4))
        
        return all_deals


class MyntraDealMonitor(BaseDealPageMonitor):
    """Monitor Myntra deal pages."""
    
    DEAL_PAGES = [
        'https://www.myntra.com/shop/offers',
        'https://www.myntra.com/shop/deals-of-the-day',
    ]
    
    def extract_deals(self, html: str) -> List[Dict]:
        """Extract deals from Myntra pages."""
        deals = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Myntra uses dynamic content
        product_cards = soup.find_all('li', class_='product-base')
        
        for card in product_cards[:50]:
            try:
                deal = self._extract_deal_from_card(card)
                if deal:
                    deals.append(deal)
            except Exception as e:
                continue
        
        return deals
    
    def _extract_deal_from_card(self, card) -> Optional[Dict]:
        """Extract deal from Myntra card."""
        deal = {}
        
        # Link
        link_tag = card.find('a', href=True)
        if link_tag:
            deal['url'] = urljoin('https://www.myntra.com', link_tag['href'])
        else:
            return None
        
        # Title
        title_tag = card.find('h4', class_='product-product')
        if title_tag:
            deal['title'] = title_tag.get_text(strip=True)
        
        # Price
        price_tag = card.find('span', class_='product-discountedPrice')
        if price_tag:
            deal['price'] = price_tag.get_text(strip=True)
        
        # MRP
        mrp_tag = card.find('span', class_='product-strike')
        if mrp_tag:
            deal['mrp'] = mrp_tag.get_text(strip=True)
        
        # Discount
        discount_tag = card.find('span', class_='product-discountPercentage')
        if discount_tag:
            deal['discount'] = discount_tag.get_text(strip=True)
        
        deal['store'] = 'Myntra'
        deal['detected_at'] = datetime.now().isoformat()
        deal['source'] = 'official_deal_page'
        
        return deal if deal.get('url') else None
    
    def monitor_all_pages(self) -> List[Dict]:
        """Monitor all Myntra deal pages."""
        all_deals = []
        
        for page_url in self.DEAL_PAGES:
            print(f"📡 Monitoring: {page_url}")
            html = self.fetch_page(page_url)
            if html:
                deals = self.extract_deals(html)
                all_deals.extend(deals)
                print(f"✅ Found {len(deals)} deals")
            time.sleep(random.uniform(2, 4))
        
        return all_deals


class OfficialDealMonitorOrchestrator:
    """Orchestrates monitoring across all e-commerce platforms."""
    
    def __init__(self, use_selenium: bool = False):
        self.monitors = {
            'amazon': AmazonDealMonitor(use_selenium=use_selenium),
            'flipkart': FlipkartDealMonitor(use_selenium=True),  # Flipkart requires Selenium
            'myntra': MyntraDealMonitor(use_selenium=use_selenium),
        }
    
    def monitor_all_platforms(self, platforms: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """
        Monitor deal pages across all platforms.
        
        Args:
            platforms: List of platforms to monitor. If None, monitors all.
        
        Returns:
            Dictionary with platform names as keys and deals as values
        """
        if platforms is None:
            platforms = list(self.monitors.keys())
        
        results = {}
        
        for platform in platforms:
            if platform not in self.monitors:
                print(f"⚠️  Unknown platform: {platform}")
                continue
            
            print(f"\n{'='*60}")
            print(f"🔍 Monitoring {platform.upper()} Deal Pages")
            print(f"{'='*60}")
            
            try:
                monitor = self.monitors[platform]
                deals = monitor.monitor_all_pages()
                results[platform] = deals
                print(f"✅ {platform.upper()}: Found {len(deals)} deals\n")
            except Exception as e:
                print(f"❌ Error monitoring {platform}: {e}\n")
                results[platform] = []
        
        return results
    
    def get_all_deals(self) -> List[Dict]:
        """Get all deals from all platforms as a flat list."""
        results = self.monitor_all_platforms()
        all_deals = []
        for platform, deals in results.items():
            all_deals.extend(deals)
        return all_deals
    
    def cleanup(self):
        """Cleanup all monitors."""
        for monitor in self.monitors.values():
            monitor.cleanup()


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    print("🚀 Official Deal Page Monitor - Test Mode\n")
    
    # Initialize orchestrator
    orchestrator = OfficialDealMonitorOrchestrator(use_selenium=False)
    
    try:
        # Monitor Amazon only for testing (faster without Selenium)
        print("Testing Amazon Deal Monitor...\n")
        results = orchestrator.monitor_all_platforms(platforms=['amazon'])
        
        # Display results
        for platform, deals in results.items():
            print(f"\n📊 {platform.upper()} Results:")
            print(f"Total deals found: {len(deals)}")
            
            if deals:
                print("\nSample deals:")
                for deal in deals[:3]:
                    print(f"\n  • {deal.get('title', 'N/A')}")
                    print(f"    Price: {deal.get('price', 'N/A')} (was {deal.get('mrp', 'N/A')})")
                    print(f"    Discount: {deal.get('discount', 'N/A')}")
                    print(f"    URL: {deal.get('url', 'N/A')[:80]}...")
    
    finally:
        orchestrator.cleanup()
        print("\n✅ Test completed!")
