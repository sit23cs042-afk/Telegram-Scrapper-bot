"""
URL Expander Module
===================
Expands shortened URLs (amzn.to, fkrt.it, etc.) to get the real product page URLs.

Author: AI Assistant
Date: December 2025
"""

import requests
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict
import time
import re


class URLExpander:
    """
    Handles URL expansion for shortened e-commerce links.
    """
    
    def __init__(self, timeout: int = 20, max_retries: int = 3):
        """
        Initialize URL expander.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def expand_url(self, short_url: str) -> Dict[str, Optional[str]]:
        """
        Expand a shortened URL to get the final destination.
        
        Args:
            short_url: The shortened URL to expand
            
        Returns:
            Dict containing:
                - expanded_url: The final expanded URL
                - domain: The domain of the expanded URL
                - error: Error message if expansion failed
        """
        if not short_url or not short_url.startswith(('http://', 'https://')):
            # Try adding https:// if missing
            if short_url and not short_url.startswith(('http://', 'https://')):
                short_url = f'https://{short_url}'
            else:
                return {
                    'expanded_url': None,
                    'domain': None,
                    'error': 'Invalid URL format'
                }
        
        for attempt in range(self.max_retries):
            try:
                # Make HEAD request first (faster)
                response = self.session.head(
                    short_url,
                    allow_redirects=True,
                    timeout=self.timeout
                )
                
                expanded_url = response.url
                
                # Parse the domain
                parsed = urlparse(expanded_url)
                domain = parsed.netloc.lower()
                
                # Check if it's an affiliate redirect page - need to extract and expand again
                if any(redirect_domain in domain for redirect_domain in ['linkredirect.in', 'indiafreestuff.in', 'indfs.in', 'redirect']):
                    # Try to extract the actual product URL from query parameters
                    query_params = parse_qs(parsed.query)
                    # Look for common redirect parameter names
                    for param in ['dl', 'url', 'redirect', 'target', 'link', 'destination', 'to']:
                        if param in query_params:
                            actual_url = query_params[param][0]
                            # URL might be encoded, try decoding
                            if '%' in actual_url:
                                from urllib.parse import unquote
                                actual_url = unquote(actual_url)
                            # Recursively expand the extracted URL (but limit depth to avoid infinite loops)
                            if attempt == 0:  # Only do second expansion on first attempt
                                result = self.expand_url(actual_url)
                                if result['expanded_url']:
                                    return result
                
                # If no query param found, try making a GET request to follow HTML meta redirects
                if any(redirect_domain in domain for redirect_domain in ['linkredirect.in', 'indiafreestuff.in', 'indfs.in']) and attempt == 0:
                    try:
                        response = self.session.get(short_url, allow_redirects=True, timeout=self.timeout)
                        final_url = response.url
                        if final_url != expanded_url:
                            # We got redirected further
                            expanded_url = final_url
                            domain = urlparse(final_url).netloc.lower()
                        
                        # Still on redirect domain? Try parsing HTML for meta refresh or links
                        if any(redirect_domain in domain for redirect_domain in ['indiafreestuff.in', 'indfs.in']):
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # Method 0: Check for tdldz-specific data attributes or hidden fields
                            # These pages often have the target URL in data attributes
                            for elem in soup.find_all(attrs={'data-url': True}):
                                target_url = elem.get('data-url')
                                if target_url and any(store in target_url.lower() for store in ['amazon', 'flipkart', 'myntra', 'ajio', 'meesho']):
                                    result = self.expand_url(target_url)
                                    if result['expanded_url']:
                                        return result
                            
                            # Method 0b: Look for form actions or buttons with URLs
                            for form in soup.find_all('form', action=True):
                                action_url = form.get('action')
                                if action_url and any(store in action_url.lower() for store in ['amazon', 'flipkart', 'myntra', 'ajio', 'meesho']):
                                    result = self.expand_url(action_url)
                                    if result['expanded_url']:
                                        return result
                            
                            # Method 1: Look for meta refresh
                            meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile(r'refresh', re.IGNORECASE)})
                            if meta_refresh and meta_refresh.get('content'):
                                content = meta_refresh['content']
                                url_match = re.search(r'url=([^\"\\s]+)', content, re.IGNORECASE)
                                if url_match:
                                    extracted_url = url_match.group(1)
                                    result = self.expand_url(extracted_url)
                                    if result['expanded_url']:
                                        return result
                            
                            # Method 2: Look for JavaScript redirects (window.location, etc.)
                            scripts = soup.find_all('script')
                            for script in scripts:
                                script_text = script.string or ''
                                # Look for URL patterns in JavaScript - expanded patterns
                                url_patterns = [
                                    r'window\.location\.href\s*=\s*["\']([^"\']+)["\']',
                                    r'window\.location\s*=\s*["\']([^"\']+)["\']',
                                    r'location\.href\s*=\s*["\']([^"\']+)["\']',
                                    r'location\.replace\s*\(\s*["\']([^"\']+)["\']',
                                    r'href\s*:\s*["\']([^"\']+)["\']',
                                    r'url\s*:\s*["\']([^"\']+)["\']',
                                    r'["\']https?://[^"\']*(?:amazon|flipkart|myntra|ajio|meesho)[^"\']*["\']',
                                ]
                                for pattern in url_patterns:
                                    matches = re.findall(pattern, script_text, re.IGNORECASE)
                                    for url in matches:
                                        # Clean up the URL if it has quotes
                                        url = url.strip('"\'')
                                        if any(store in url.lower() for store in ['amazon', 'flipkart', 'myntra', 'ajio', 'meesho']):
                                            result = self.expand_url(url)
                                            if result['expanded_url']:
                                                return result
                            
                            # Method 3: Look for \"Go to deal\" or deal links in HTML
                            for link in soup.find_all('a', href=True):
                                href = link['href']
                                link_text = link.get_text().lower()
                                # Check if it's a deal link (by href or link text)
                                if (any(store in href.lower() for store in ['amazon', 'flipkart', 'myntra', 'ajio', 'meesho']) or
                                    any(keyword in link_text for keyword in ['deal', 'buy', 'shop', 'get', 'click', 'visit'])):
                                    # Skip internal links
                                    if not any(internal in href.lower() for internal in ['indiafreestuff', 'indfs.in', 'login', 'register', 'about', 'contact', 'privacy']):
                                        result = self.expand_url(href)
                                        if result['expanded_url']:
                                            return result
                    except Exception as e:
                        pass  # Continue with current expanded_url
                
                # Last resort for stubborn redirect pages - use Selenium
                if any(redirect_domain in domain for redirect_domain in ['indiafreestuff.in', 'indfs.in']) and '/tdldz/' in expanded_url:
                    # Try Selenium expansion
                    selenium_result = self._expand_with_selenium(expanded_url)
                    if selenium_result and selenium_result.get('expanded_url'):
                        expanded_url = selenium_result['expanded_url']
                        domain = selenium_result['domain']
                    else:
                        # Selenium failed or not available - return error
                        return {
                            'expanded_url': None,
                            'domain': domain,
                            'error': 'Could not extract product URL from redirect page (requires JavaScript)'
                        }
                
                # Check if URL is a category/search page (not a product page)
                is_invalid = False
                error_msg = None
                
                # Myntra category/search patterns
                if 'myntra.com' in domain:
                    # Valid product pages have specific patterns
                    if not any(pattern in expanded_url for pattern in ['/buy/', '/-/', '/p/']):
                        # Check if it's a category page
                        if any(pattern in expanded_url for pattern in ['?', 'rf=', 'sort=', 'filter', '/shop/', 'category']):
                            is_invalid = True
                            error_msg = 'Myntra category/search page detected (not a single product)'
                
                # Amazon category/search patterns
                if 'amazon' in domain:
                    if '/s?' in expanded_url or '/s/' in expanded_url:
                        is_invalid = True
                        error_msg = 'Amazon search results page (not a single product)'
                
                # Flipkart category/search/collection patterns
                if 'flipkart.com' in domain:
                    if any(pattern in expanded_url for pattern in ['/search?', 'q=', '/category/', '/~cs-', '/pr?', 'collection']):
                        is_invalid = True
                        error_msg = 'Flipkart search/category page (not a single product)'
                    # Also check for category URLs ending in /pr
                    if expanded_url.rstrip('/').endswith('/pr'):
                        is_invalid = True
                        error_msg = 'Flipkart category page (not a single product)'
                
                # Shopsy (Flipkart's budget platform) search/category patterns
                if 'shopsy.in' in domain:
                    # Collection/category pages have /pr? or ~cs- patterns
                    if '/pr?' in expanded_url or '~cs-' in expanded_url:
                        # Check if it's actually a collection (has collection-tab-name)
                        if 'collection-tab-name' in expanded_url or 'pageCriteria' in expanded_url:
                            is_invalid = True
                            error_msg = 'Shopsy collection/category page (not a single product)'
                    if any(pattern in expanded_url for pattern in ['/search?', 'q=', '/category/']):
                        is_invalid = True
                        error_msg = 'Shopsy search/category page (not a single product)'
                
                if is_invalid:
                    return {
                        'expanded_url': None,
                        'domain': domain,
                        'error': error_msg
                    }
                
                # Clean Amazon URLs (remove tracking parameters)
                if 'amazon' in domain:
                    expanded_url = self._clean_amazon_url(expanded_url)
                
                # Clean Flipkart URLs
                elif 'flipkart' in domain:
                    expanded_url = self._clean_flipkart_url(expanded_url)
                
                return {
                    'expanded_url': expanded_url,
                    'domain': domain,
                    'error': None
                }
                
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                return {
                    'expanded_url': None,
                    'domain': None,
                    'error': 'Request timeout'
                }
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                return {
                    'expanded_url': None,
                    'domain': None,
                    'error': f'Request failed: {str(e)}'
                }
        
        return {
            'expanded_url': None,
            'domain': None,
            'error': 'Max retries exceeded'
        }
    
    def _clean_amazon_url(self, url: str) -> str:
        """
        Clean Amazon URL by removing tracking parameters and keeping only essential parts.
        
        Args:
            url: Amazon product URL
            
        Returns:
            Cleaned URL
        """
        try:
            parsed = urlparse(url)
            
            # Extract product ID (ASIN)
            path_parts = parsed.path.split('/')
            if '/dp/' in parsed.path:
                dp_index = path_parts.index('dp')
                if dp_index + 1 < len(path_parts):
                    asin = path_parts[dp_index + 1]
                    return f"https://{parsed.netloc}/dp/{asin}"
            
            elif '/gp/product/' in parsed.path:
                gp_index = path_parts.index('product')
                if gp_index + 1 < len(path_parts):
                    asin = path_parts[gp_index + 1]
                    return f"https://{parsed.netloc}/dp/{asin}"
            
            # If we can't clean it, return original
            return url
            
        except Exception:
            return url
    
    def _clean_flipkart_url(self, url: str) -> str:
        """
        Clean Flipkart URL by removing tracking parameters.
        
        Args:
            url: Flipkart product URL
            
        Returns:
            Cleaned URL
        """
        try:
            parsed = urlparse(url)
            
            # Remove tracking parameters
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            # Keep only pid parameter if present
            if parsed.query:
                params = parse_qs(parsed.query)
                if 'pid' in params:
                    clean_url += f"?pid={params['pid'][0]}"
            
            return clean_url
            
        except Exception:
            return url
    
    def is_shortened_url(self, url: str) -> bool:
        """
        Check if a URL is a known shortened URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is shortened, False otherwise
        """
        shortened_domains = [
            'amzn.to',
            'amzn-to.co',    # Amazon affiliate shortener
            'amzn.in',
            'fkrt.it',
            'fkrt.co',
            'fkrt.cc',
            'bit.ly',
            'bitli.in',
            'tinyurl.com',
            'goo.gl',
            'ow.ly',
            't.co',
            'rb.gy',
            'cutt.ly',
            's.click.aliexpress.com',
            'dl.flipkart.com',
            'indfs.in',      # India Free Stuff shortener
            'msho.in',       # Meesho shortener
            'myntr.it',      # Myntra shortener
            'myntr.in',      # Myntra shortener
            'ajiio.in',      # Ajio shortener
            'ajiio.co',      # Ajio shortener alternate
            'extp.in',       # External shortener
        ]
        
        try:
            parsed = urlparse(url if url.startswith('http') else f'https://{url}')
            domain = parsed.netloc.lower()
            return any(short_domain in domain for short_domain in shortened_domains)
        except Exception:
            return False
    
    def get_domain(self, url: str) -> Optional[str]:
        """
        Extract domain from URL.
        
        Args:
            url: URL to parse
            
        Returns:
            Domain name or None
        """
        try:
            parsed = urlparse(url if url.startswith('http') else f'https://{url}')
            return parsed.netloc.lower()
        except Exception:
            return None
    
    def _expand_with_selenium(self, url: str) -> Optional[Dict]:
        """
        Use Selenium to expand URLs that require JavaScript execution.
        This is a fallback for redirect pages like indiafreestuff.in/tdldz/
        
        Args:
            url: URL to expand with Selenium
            
        Returns:
            Dict with expanded_url, domain, error or None if Selenium not available
        """
        print(f"   ⚙️  Attempting Selenium expansion for: {url}")
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = None
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.set_page_load_timeout(15)
                
                driver.get(url)
                
                # Wait for potential redirects (max 10 seconds)
                time.sleep(5)  # Give JavaScript time to execute and redirect
                
                final_url = driver.current_url
                parsed = urlparse(final_url)
                domain = parsed.netloc.lower()
                
                print(f"   ✅ Selenium navigated to: {final_url}")
                
                # Check if we actually got redirected to a product page
                if any(store in domain for store in ['amazon', 'flipkart', 'myntra', 'ajio', 'meesho', 'shopsy']):
                    print(f"   ✅ Successfully expanded to product page: {domain}")
                    return {
                        'expanded_url': final_url,
                        'domain': domain,
                        'error': None
                    }
                else:
                    print(f"   ⚠️  Selenium did not reach a product page (still on: {domain})")
                    return None
                    
                return None
                
            finally:
                if driver:
                    driver.quit()
                    
        except ImportError:
            # Selenium not available
            print(f"   ⚠️  Selenium not available (install selenium and webdriver-manager)")
            return None
        except Exception as e:
            # Selenium expansion failed
            print(f"   ⚠️  Selenium expansion failed: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    expander = URLExpander()
    
    # Test URLs
    test_urls = [
        'https://amzn.to/3XYZ123',
        'https://fkrt.it/ABC123',
        'https://www.amazon.in/dp/B0ABCD1234'
    ]
    
    print("Testing URL Expander")
    print("=" * 80)
    
    for url in test_urls:
        print(f"\nOriginal: {url}")
        result = expander.expand_url(url)
        
        if result['error']:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Expanded: {result['expanded_url']}")
            print(f"   Domain: {result['domain']}")
