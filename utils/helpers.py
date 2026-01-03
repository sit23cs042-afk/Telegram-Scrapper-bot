"""
Utility helpers for web scraping with anti-blocking measures
"""

import random
import time
import logging
from typing import Optional, List
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
]


def get_random_user_agent() -> str:
    """Get a random user agent from the list"""
    return random.choice(USER_AGENTS)


def get_session_with_retries(retries: int = 3, backoff_factor: float = 0.3) -> requests.Session:
    """
    Create a requests session with retry logic
    
    Args:
        retries: Number of retry attempts
        backoff_factor: Backoff factor for retries
        
    Returns:
        Configured requests session
    """
    session = requests.Session()
    
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def fetch_page(url: str, timeout: int = 10, use_session: bool = True) -> Optional[requests.Response]:
    """
    Fetch a webpage with anti-blocking measures
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        use_session: Whether to use session with retries
        
    Returns:
        Response object if successful, None otherwise
    """
    try:
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Add random delay to avoid rate limiting
        time.sleep(random.uniform(1.0, 3.0))
        
        if use_session:
            session = get_session_with_retries()
            response = session.get(url, headers=headers, timeout=timeout)
        else:
            response = requests.get(url, headers=headers, timeout=timeout)
        
        response.raise_for_status()
        logger.info(f"✓ Successfully fetched: {url[:80]}...")
        return response
        
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Error fetching {url}: {e}")
        return None


def extract_price(price_text: str) -> Optional[float]:
    """
    Extract numeric price from text
    
    Args:
        price_text: Text containing price (e.g., "₹1,299", "Rs. 999")
        
    Returns:
        Float price value or None
    """
    if not price_text:
        return None
    
    try:
        # Remove common currency symbols and text
        price_text = price_text.replace('₹', '').replace('Rs.', '').replace('Rs', '')
        price_text = price_text.replace(',', '').replace(' ', '').strip()
        
        # Extract first number found
        import re
        match = re.search(r'\d+\.?\d*', price_text)
        if match:
            return float(match.group())
        
        return None
    except (ValueError, AttributeError):
        return None


def calculate_discount_percentage(original: float, discounted: float) -> Optional[float]:
    """
    Calculate discount percentage
    
    Args:
        original: Original price
        discounted: Discounted price
        
    Returns:
        Discount percentage or None
    """
    if not original or not discounted or original <= 0:
        return None
    
    try:
        discount = ((original - discounted) / original) * 100
        return round(discount, 2)
    except (ValueError, ZeroDivisionError):
        return None


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep basic punctuation
    import re
    text = re.sub(r'[^\w\s\-.,()%&]', '', text)
    
    return text.strip()


def validate_url(url: str) -> bool:
    """
    Validate if a URL is well-formed
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def format_deal_data(data: dict) -> dict:
    """
    Format and validate deal data before database insertion
    
    Args:
        data: Raw deal data
        
    Returns:
        Formatted deal data
    """
    return {
        'product_name': clean_text(data.get('product_name', ''))[:500],
        'category': clean_text(data.get('category', 'General'))[:100],
        'brand': clean_text(data.get('brand', 'Unknown'))[:100],
        'original_price': data.get('original_price'),
        'discounted_price': data.get('discounted_price'),
        'discount_percentage': data.get('discount_percentage'),
        'product_url': data.get('product_url', '')[:1000],
        'image_url': data.get('image_url', '')[:1000],
        'website_name': data.get('website_name', '')[:50],
        'deal_type': data.get('deal_type', 'Daily Deal')[:50],
    }


def batch_items(items: List, batch_size: int = 10) -> List[List]:
    """
    Split items into batches
    
    Args:
        items: List of items
        batch_size: Size of each batch
        
    Returns:
        List of batches
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, calls_per_minute: int = 10):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call = 0
    
    def wait(self):
        """Wait if necessary to respect rate limit"""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            time.sleep(sleep_time)
        self.last_call = time.time()


# Global rate limiter instance
rate_limiter = RateLimiter(calls_per_minute=20)
