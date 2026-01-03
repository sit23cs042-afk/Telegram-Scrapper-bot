# System Configuration & Troubleshooting Guide

## "Not Found" Error - Common Causes

### 1. **Product Delisted (404 Error)**
**Symptoms:** "404 Client Error: Not Found"  
**Cause:** Amazon/Flipkart removed the product  
**Fix:** Use fresh URLs from recent Telegram messages

### 2. **Bot Protection**
**Symptoms:** "Amazon bot protection detected", CAPTCHA pages  
**Cause:** Amazon/Flipkart blocking automated access  
**Current Solution:** System automatically switches to Selenium  
**Additional Fix:** 
- Clear browser cache
- Run as Administrator
- Try different network

### 3. **Network/Firewall Blocking**
**Symptoms:** Connection timeout, connection refused  
**Cause:** Corporate firewall, antivirus, VPN issues  
**Fix:**
- Disable VPN temporarily
- Check antivirus settings
- Allow Python/Chrome through firewall
- Test URLs in browser first

### 4. **Shortened URL Expiration**
**Symptoms:** Short URLs (amzn.to, fkrt.cc) not expanding  
**Cause:** URL expired or tracking link broken  
**Fix:** Get fresh link from Telegram

### 5. **Geographic Restrictions**
**Symptoms:** Works on one system but not another  
**Cause:** IP-based blocking, regional restrictions  
**Fix:** 
- Ensure both systems in same region (India)
- Check IP address isn't flagged
- Use VPN set to India

## Quick Diagnostics

Run on the problematic system:
```bash
python diagnose_system.py
```

Test specific URLs:
```bash
python test_url_scraping.py
```

## For Different Systems

### Setup Checklist:
- [ ] Python 3.8+ installed
- [ ] All packages installed: `pip install -r requirements.txt`
- [ ] Chrome browser installed (for Selenium)
- [ ] Internet access to amazon.in, flipkart.com
- [ ] Firewall allows Python/Chrome
- [ ] No VPN issues

### Environment Variables:
Ensure these are set in `.env`:
```
SUPABASE_URL=https://sspufleiikzsazouzkot.supabase.co
SUPABASE_KEY=your-key-here
TELEGRAM_API_ID=your-id
TELEGRAM_API_HASH=your-hash
TELEGRAM_PHONE=your-phone
```

## Testing Steps

1. **Test Internet Connectivity:**
   ```bash
   python -c "import requests; print(requests.get('https://www.amazon.in').status_code)"
   ```

2. **Test URL Expansion:**
   ```bash
   python -c "from url_expander import URLExpander; e = URLExpander(); print(e.expand_url('https://www.amazon.in/dp/B0CZNT188T'))"
   ```

3. **Test Product Scraper:**
   ```bash
   python -c "from product_scraper import ProductScraperFactory; s = ProductScraperFactory(); print(s.scrape_product('https://www.amazon.in/dp/B0CZNT188T')['success'])"
   ```

## Common Solutions

### Solution 1: Reinstall Dependencies
```bash
pip install --upgrade --force-reinstall -r requirements.txt
```

### Solution 2: Clear Chrome Cache
```bash
# ChromeDriver caches data
rd /s /q "%USERPROFILE%\.wdm"  # Windows
```

### Solution 3: Run as Administrator
Right-click PowerShell → "Run as Administrator"
```bash
python telegram_listener.py
```

### Solution 4: Use Valid Test URLs
Replace test URLs with these fresh ones:
- Amazon: https://www.amazon.in/dp/B0CZNT188T
- Flipkart: https://www.flipkart.com/spotwalk-sw-mexico-black-running-sports-sneakers-shoes-men/p/itm8fc450c47893b
- Myntra: https://www.myntra.com/sweatshirts/mast+%26+harbour/mast--harbour-mock-collar-sweatshirt/23102794/buy

## Error Messages Reference

| Error | Meaning | Fix |
|-------|---------|-----|
| 404 Not Found | Product delisted | Use fresh URL |
| 403 Forbidden | Bot protection | Selenium will retry |
| Connection timeout | Network issue | Check firewall/internet |
| ChromeDriver error | Selenium issue | Run as Admin, reinstall chrome |
| ImportError | Package missing | pip install package-name |

## Still Not Working?

1. **Compare working vs non-working system:**
   ```bash
   python diagnose_system.py > diagnosis_working.txt
   python diagnose_system.py > diagnosis_broken.txt
   # Compare the two files
   ```

2. **Test with minimal script:**
   ```python
   import requests
   url = "https://www.amazon.in/dp/B0CZNT188T"
   r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
   print(f"Status: {r.status_code}")
   print(f"Content length: {len(r.text)}")
   ```

3. **Check logs:**
   Look for specific error messages in terminal output

Need more help? Share the output of `python diagnose_system.py`
