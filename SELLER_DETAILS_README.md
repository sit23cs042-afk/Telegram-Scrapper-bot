# Seller Details Extraction

## Overview
Enhanced the Discount Product Intelligence Agent to automatically extract detailed seller information from official e-commerce websites.

## What's New

### 🔍 **Seller Information Extracted**

#### Amazon
- **Seller Name**: Cloudtail India, Appario Retail, Amazon, etc.
- **Seller Type**:
  - "Amazon Direct" - sold directly by Amazon
  - "Fulfilled by Amazon" - third-party seller with Amazon fulfillment
  - "Third-party seller" - independent seller
- **Seller Rating**: If available on product page
- **Seller Profile Link**: For additional research

#### Flipkart  
- **Seller Name**: Flipkart, RetailNet, other sellers
- **Seller Type**:
  - "Flipkart Direct/Assured" - sold/fulfilled by Flipkart
  - "Third-party seller" - independent seller
- **Flipkart Assured**: Automatically detected
- **Seller Rating**: If available

#### Other Platforms
- Myntra, Ajio, Meesho, Shopsy - basic seller detection

---

## Database Schema

### New Columns Added to `deals` Table

```sql
-- Seller details columns
seller_name                  TEXT                  -- Seller name (e.g., "Cloudtail India")
seller_rating                DECIMAL(3, 2)         -- Seller rating (0-5.0)
is_fulfilled_by_platform     BOOLEAN               -- TRUE for Amazon/Flipkart fulfillment
seller_info                  JSONB                 -- Full seller details (see below)
```

### Seller Info JSON Structure

```json
{
  "name": "Cloudtail India",
  "platform": "Amazon",
  "type": "Fulfilled by Amazon",
  "profile_link": "/gp/help/seller/at-a-glance.html...",
  "fulfillment": "Amazon",
  "assured": true
}
```

---

## Setup Instructions

### 1. Update Database Schema

Run the SQL file in Supabase Dashboard → SQL Editor:

```bash
# File: add_seller_columns.sql
```

**Contents:**
```sql
ALTER TABLE deals ADD COLUMN IF NOT EXISTS seller_name TEXT;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS seller_rating DECIMAL(3, 2);
ALTER TABLE deals ADD COLUMN IF NOT EXISTS is_fulfilled_by_platform BOOLEAN DEFAULT FALSE;
ALTER TABLE deals ADD COLUMN IF NOT EXISTS seller_info JSONB;
```

### 2. Verify Setup

```bash
python test_seller_extraction.py
```

---

## How It Works

### 1. **Telegram Monitoring**
When you run `telegram_listener.py`:
- Monitors configured Telegram channels for product links
- Extracts product URLs from messages
- Scrapes official product pages

### 2. **Seller Extraction Process**

#### For Amazon:
```python
# Extraction sources (in priority order):
1. #sellerProfileTriggerId anchor tag
2. #tabular-buybox div
3. #merchant-info div  
4. "Sold by" text patterns
5. "Ships from and sold by" patterns

# Fulfillment detection:
- Checks for "Fulfilled by Amazon" text
- Checks for "Ships from and sold by Amazon"
```

#### For Flipkart:
```python
# Extraction sources:
1. #sellerName div
2. "Sold by" text patterns
3. Default to "Flipkart" for direct sales

# Assured detection:
- Looks for "Flipkart Assured" badge/text
- Checks "F-assured" markers
```

### 3. **Data Storage**
All seller details automatically saved to Supabase:
```python
from supabase_database import save_to_database

deal_data = {
    'verified_title': 'Product Name',
    'verified_price': 5999,
    'link': 'https://amazon.in/...',
    'seller_name': 'Cloudtail India',
    'seller_rating': 4.5,
    'is_fulfilled_by_platform': True,
    'seller_info': {...}
}

save_to_database(deal_data)
```

---

## Usage Examples

### Example 1: View Deals with Seller Info

```python
from supabase_database import get_supabase_client

client = get_supabase_client()
result = client.table('deals')\
    .select('title, verified_price, seller_name, is_fulfilled_by_platform, seller_info')\
    .order('id', desc=True)\
    .limit(10)\
    .execute()

for deal in result.data:
    print(f"📦 {deal['title']}")
    print(f"   💰 ₹{deal['verified_price']}")
    print(f"   👤 Seller: {deal['seller_name']}")
    if deal['is_fulfilled_by_platform']:
        print(f"   ✅ Platform Fulfilled")
    print()
```

### Example 2: Filter by Seller Type

```python
# Get only platform-fulfilled deals (more reliable)
result = client.table('deals')\
    .select('*')\
    .eq('is_fulfilled_by_platform', True)\
    .order('verified_discount', desc=True)\
    .limit(20)\
    .execute()
```

### Example 3: Enhanced View Script

Update `view_deals.py` to show seller info:
```python
# In display function, add:
if deal.get('seller_name'):
    print(f"   👤 Seller: {deal['seller_name']}")
    if deal.get('is_fulfilled_by_platform'):
        print(f"   ✅ {platform} Fulfilled")
```

---

## Query Examples

### Top Deals from Trusted Sellers

```sql
-- Platform-fulfilled deals (Amazon/Flipkart direct)
SELECT 
    title,
    verified_price,
    verified_discount,
    seller_name,
    is_fulfilled_by_platform
FROM deals
WHERE is_fulfilled_by_platform = TRUE
ORDER BY verified_discount DESC
LIMIT 20;
```

### Deals by Specific Seller

```sql
-- All deals from a specific seller
SELECT *
FROM deals
WHERE seller_name = 'Cloudtail India'
ORDER BY detected_at DESC;
```

### Seller Performance Analysis

```sql
-- Count deals by seller
SELECT 
    seller_name,
    COUNT(*) as deal_count,
    AVG(verified_discount) as avg_discount,
    AVG(seller_rating) as avg_rating
FROM deals
WHERE seller_name IS NOT NULL
GROUP BY seller_name
ORDER BY deal_count DESC
LIMIT 20;
```

---

## API Integration

### Get Seller Info via API

```python
from product_scraper import ProductScraperFactory

scraper = ProductScraperFactory()
result = scraper.scrape_product('https://www.amazon.in/dp/PRODUCT_ID')

print(f"Seller: {result['seller_name']}")
print(f"Rating: {result['seller_rating']}")
print(f"Platform Fulfilled: {result['is_fulfilled_by_platform']}")
print(f"Full Info: {result['seller_info']}")
```

---

## Benefits

### 🎯 **For Users**
- **Trust Signal**: Know if product is sold by Amazon/Flipkart directly
- **Quality Assurance**: Platform fulfillment = better service
- **Seller Research**: Identify reliable third-party sellers
- **Avoid Fakes**: Platform sellers less likely to sell counterfeits

### 📊 **For Analytics**
- Track which sellers offer best deals
- Identify patterns in pricing by seller type
- Filter by trusted sellers only
- Analyze seller rating correlation with deal quality

### 🚀 **For Intelligence**
- Enhanced deal scoring based on seller reputation
- Prioritize platform-fulfilled deals
- Better duplicate detection using seller info
- Seller-specific price history tracking

---

## Future Enhancements

- [ ] Seller reputation scoring
- [ ] Historical seller performance tracking
- [ ] Seller-specific deal alerts
- [ ] Cross-platform seller matching
- [ ] Seller fraud detection
- [ ] Seller contact information extraction

---

## Troubleshooting

### Issue: Seller not detected

**Solution:**
- Amazon/Flipkart frequently change HTML structure
- Check scraper selectors in `product_scraper.py`
- Enable debug mode to see extraction attempts

### Issue: Wrong seller extracted

**Solution:**
- Verify product URL is valid
- Check for bot protection (Selenium fallback activates)
- Review `seller_info` JSON for all detected data

### Issue: Database column missing

**Solution:**
```bash
# Rerun the SQL migration
cat add_seller_columns.sql
# Copy and paste into Supabase SQL Editor
```

---

## Files Modified

1. **product_scraper.py** - Enhanced seller extraction for Amazon & Flipkart
2. **supabase_database.py** - Added seller fields to save function
3. **enhanced_database_schema.sql** - Added seller columns to schema
4. **add_seller_columns.sql** - Migration script for existing databases

## Files Created

1. **test_seller_extraction.py** - Test & demo script
2. **SELLER_DETAILS_README.md** - This documentation

---

## Summary

✅ **Automatic seller extraction** from official product pages  
✅ **Platform fulfillment detection** (Amazon/Flipkart)  
✅ **Seller ratings** when available  
✅ **Rich seller metadata** in JSONB format  
✅ **Backward compatible** with existing code  
✅ **Ready for analytics** and filtering  

**Your Telegram bot now captures complete seller information for every product automatically!** 🎉
