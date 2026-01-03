"""
Browser automation helper for JavaScript-heavy websites
Uses Playwright to render pages and extract data
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)


class BrowserHelper:
    """Helper class for browser automation"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        
    def __enter__(self):
        """Context manager entry"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True,
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
        )
        # Stealth mode - hide automation
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def fetch_page(self, url: str, wait_for: str = 'load', timeout: int = 30000) -> Optional[str]:
        """
        Fetch page content with JavaScript rendering
        
        Args:
            url: URL to fetch
            wait_for: Wait condition ('networkidle', 'domcontentloaded', 'load')
            timeout: Timeout in milliseconds
            
        Returns:
            HTML content or None if failed
        """
        try:
            page = self.context.new_page()
            
            # Navigate to page with load wait (more lenient than networkidle)
            page.goto(url, wait_until=wait_for, timeout=timeout)
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Get page content
            content = page.content()
            
            page.close()
            return content
            
        except PlaywrightTimeout:
            logger.error(f"Timeout fetching {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def fetch_page_with_scroll(self, url: str, scroll_count: int = 3, timeout: int = 30000) -> Optional[str]:
        """
        Fetch page and scroll to load lazy content
        
        Args:
            url: URL to fetch
            scroll_count: Number of times to scroll
            timeout: Timeout in milliseconds
            
        Returns:
            HTML content or None if failed
        """
        try:
            page = self.context.new_page()
            
            # Navigate to page with load wait (more lenient)
            page.goto(url, wait_until='load', timeout=timeout)
            
            # Wait for page to settle
            time.sleep(3)
            
            # Scroll to load lazy content
            for i in range(scroll_count):
                page.evaluate('window.scrollBy(0, window.innerHeight)')
                time.sleep(2)
            
            # Scroll back to top
            page.evaluate('window.scrollTo(0, 0)')
            time.sleep(1)
            
            # Get page content
            content = page.content()
            
            page.close()
            return content
            
        except Exception as e:
            logger.error(f"Error fetching {url} with scroll: {e}")
            return None


def fetch_with_browser(url: str, wait_for: str = 'networkidle', scroll: bool = False) -> Optional[str]:
    """
    Convenience function to fetch a single page with browser
    
    Args:
        url: URL to fetch
        wait_for: Wait condition
        scroll: Whether to scroll for lazy loading
        
    Returns:
        HTML content or None
    """
    with BrowserHelper() as browser:
        if scroll:
            return browser.fetch_page_with_scroll(url)
        else:
            return browser.fetch_page(url, wait_for=wait_for)
