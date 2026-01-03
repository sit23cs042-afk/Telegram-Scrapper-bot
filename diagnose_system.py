"""
System Diagnostics for URL Scraping Issues
==========================================
Run this to diagnose why URLs are showing "Not found"
"""

import sys
import requests
from urllib.parse import urlparse

print("🔍 SYSTEM DIAGNOSTICS")
print("=" * 70)

# Test 1: Check Python version
print("\n1️⃣ Python Version:")
print(f"   {sys.version}")

# Test 2: Check required packages
print("\n2️⃣ Required Packages:")
packages = {
    'requests': None,
    'beautifulsoup4': 'bs4',
    'selenium': None,
    'telethon': None,
    'supabase': None
}

for pkg, import_name in packages.items():
    try:
        if import_name:
            __import__(import_name)
        else:
            __import__(pkg)
        print(f"   ✅ {pkg}")
    except ImportError:
        print(f"   ❌ {pkg} - NOT INSTALLED")

# Test 3: Check internet connectivity
print("\n3️⃣ Internet Connectivity:")
test_urls = [
    'https://www.google.com',
    'https://www.amazon.in',
    'https://www.flipkart.com',
    'https://amzn.to'
]

for url in test_urls:
    try:
        response = requests.get(url, timeout=5, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        print(f"   ✅ {urlparse(url).netloc} - {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"   ⏱️ {urlparse(url).netloc} - TIMEOUT")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ {urlparse(url).netloc} - CONNECTION FAILED")
    except Exception as e:
        print(f"   ⚠️ {urlparse(url).netloc} - {str(e)[:50]}")

# Test 4: Check Selenium/ChromeDriver
print("\n4️⃣ Selenium & ChromeDriver:")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    print("   ✅ Selenium installed")
    
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get('https://www.google.com')
        print(f"   ✅ ChromeDriver working - Version detected")
        driver.quit()
    except Exception as e:
        print(f"   ❌ ChromeDriver error: {str(e)[:80]}")
        
except ImportError:
    print("   ❌ Selenium not installed")

# Test 5: Check URL Expander
print("\n5️⃣ URL Expander Test:")
from url_expander import URLExpander

expander = URLExpander()
test_short_urls = [
    'https://amzn.to/test',  # Will fail but tests connectivity
    'https://www.amazon.in/dp/B0CX23V2ZK'  # Direct URL
]

for url in test_short_urls:
    try:
        expanded = expander.expand_url(url)
        if expanded and expanded != url:
            print(f"   ✅ {url[:30]}... → {expanded[:50]}...")
        elif expanded:
            print(f"   ℹ️  {url[:30]}... → No redirect (direct URL)")
        else:
            print(f"   ⚠️ {url[:30]}... → Failed to expand")
    except Exception as e:
        print(f"   ❌ {url[:30]}... → Error: {str(e)[:50]}")

# Test 6: Check Firewall/Proxy
print("\n6️⃣ Network Configuration:")
try:
    import os
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    if http_proxy or https_proxy:
        print(f"   ⚠️ Proxy detected:")
        if http_proxy:
            print(f"      HTTP: {http_proxy}")
        if https_proxy:
            print(f"      HTTPS: {https_proxy}")
    else:
        print("   ✅ No proxy configured (direct connection)")
except Exception as e:
    print(f"   ⚠️ Error checking proxy: {e}")

# Test 7: Test Product Scraper
print("\n7️⃣ Product Scraper Test:")
try:
    from product_scraper import ProductScraperFactory
    
    scraper = ProductScraperFactory()
    test_url = 'https://www.amazon.in/dp/B0CX23V2ZK'
    
    print(f"   Testing: {test_url}")
    result = scraper.scrape_product(test_url)
    
    if result.get('success'):
        print(f"   ✅ Scraper working")
        print(f"      Title extracted: {'Yes' if result.get('title') else 'No'}")
        print(f"      Price extracted: {'Yes' if result.get('offer_price') else 'No'}")
    else:
        print(f"   ❌ Scraper failed: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"   ❌ Scraper error: {str(e)[:80]}")

print("\n" + "=" * 70)
print("\n📋 DIAGNOSIS SUMMARY:")
print("\nIf you see ❌ or ⚠️ above, that's likely causing the 'Not found' error.")
print("\nCommon fixes:")
print("  • Install missing packages: pip install -r requirements.txt")
print("  • Check firewall/antivirus blocking Python/Chrome")
print("  • Verify internet connection to Amazon/Flipkart domains")
print("  • Try running as Administrator (for ChromeDriver)")
print("  • Check if workplace/network blocks e-commerce sites")
print("\n" + "=" * 70)
