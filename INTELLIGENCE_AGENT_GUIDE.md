# Discount Product Intelligence Agent - Complete Guide

## 🎯 **System Overview**

A comprehensive AI-powered system for detecting, verifying, and extracting discounted products from Indian e-commerce platforms.

### **Key Features**

✅ **Dual Monitoring System**
- Telegram channel monitoring (30+ channels)
- Official deal page scraping (Amazon, Flipkart, Myntra)

✅ **Historical Price Tracking**
- Detects genuine vs fake discounts
- Identifies sudden price drops
- Tracks 90-day price history
- Alerts on historical lows

✅ **Advanced Deal Scoring (0-100)**
- Discount authenticity (25 points)
- Discount percentage (20 points)
- Product popularity (15 points)
- Deal urgency (15 points)
- Price competitiveness (15 points)
- Seller trust (10 points)

✅ **Stock & Offers Intelligence**
- Real-time stock availability
- Coupon extraction
- Bank offer detection
- Exchange offer tracking
- No-cost EMI detection
- Final effective price calculation

✅ **Duplicate Detection**
- URL normalization
- Title similarity matching
- Cross-platform deduplication
- Multi-source aggregation

✅ **Smart Categorization**
- 9 main categories
- AI-powered classification
- Subcategory detection

---

## 📁 **File Structure**

### **Core Modules**

```
├── intelligence_agent.py           # Main orchestrator
├── telegram_listener.py            # Telegram monitoring
├── official_deal_monitor.py        # Official deal page scraper
├── product_scraper.py              # Site-specific scrapers
├── price_history_tracker.py        # Historical price tracking
├── deal_scorer.py                  # Deal scoring system (0-100)
├── duplicate_detector.py           # Duplicate detection
├── scraper_enhancements.py         # Stock & offers extraction
├── smart_categorizer.py            # Product categorization
├── nlp_discount_parser.py          # NLP message parsing
├── url_expander.py                 # URL expansion
├── llm_verifier.py                 # LLM-based verification
├── supabase_database.py            # Database interface
└── enhanced_database_schema.sql    # Database schema
```

### **Database Tables**

- `deals` - Main deals table (enhanced)
- `price_history` - Historical price data
- `deal_sources` - Multi-source tracking
- `product_urls` - URL mapping for deduplication
- `intelligence_stats` - Daily statistics

---

## 🚀 **Quick Start**

### **1. Install Dependencies**

```bash
pip install telethon requests beautifulsoup4 selenium webdriver-manager openai supabase
```

### **2. Configure Environment**

```bash
# Telegram API
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"

# OpenAI API (for AI categorization)
export OPENAI_API_KEY="your_openai_key"

# Supabase
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"
```

### **3. Setup Database**

**Important**: The system uses your **existing Supabase database** (the same one configured for Telegram).

Just run the enhanced schema to add new tables:

```bash
# Option 1: Via Supabase SQL Editor (Recommended)
# - Go to your Supabase Dashboard
# - Navigate to SQL Editor
# - Copy & paste contents of enhanced_database_schema.sql
# - Click Run

# Option 2: Via psql command line
psql -h db.your-project.supabase.co -U postgres -d postgres -f enhanced_database_schema.sql
```

**Note**: Your Supabase URL and key are already configured from the Telegram setup.

### **4. Run the Intelligence Agent**

#### **Demo Mode** (Test with sample data)

```bash
python intelligence_agent.py
```

#### **Monitor Official Deal Pages**

```python
from intelligence_agent import DiscountIntelligenceAgent

agent = DiscountIntelligenceAgent()

# Monitor all platforms
deals = agent.monitor_official_deal_pages()

# Monitor specific platforms
deals = agent.monitor_official_deal_pages(platforms=['amazon', 'flipkart'])

# Get top deals
top_deals = agent.get_top_deals(deals, limit=10, min_score=75)

# Export to JSON
agent.export_deals_json(top_deals, 'top_deals.json')

# Generate report
print(agent.generate_report())
```

#### **Monitor Telegram Channels**

```bash
python telegram_listener.py
```

---

## 📊 **Usage Examples**

### **Process Single Deal**

```python
from intelligence_agent import DiscountIntelligenceAgent

agent = DiscountIntelligenceAgent()

deal_data = {
    'title': 'iPhone 15 Pro 256GB',
    'price': 119900,
    'mrp': 139900,
    'url': 'https://www.amazon.in/dp/B0CHX1W1XY',
    'store': 'Amazon',
    'rating': 4.5,
    'review_count': 5000,
    'deal_type': 'Lightning Deal',
    'seller_type': 'official',
    'stock_status': 'low_stock'
}

processed_deal = agent.process_deal(deal_data)

print(f"Score: {processed_deal['score']}/100")
print(f"Grade: {processed_deal['grade']}")
print(f"Category: {processed_deal['category']}")
print(f"Recommendation: {processed_deal['recommendation']}")
```

### **Track Price History**

```python
from price_history_tracker import PriceHistoryTracker

tracker = PriceHistoryTracker()

# Record price
tracker.record_price(
    product_url='https://www.amazon.in/dp/B0CHX1W1XY',
    price=119900,
    mrp=139900,
    metadata={'title': 'iPhone 15 Pro', 'store': 'Amazon'}
)

# Get insights
insights = tracker.get_price_insights(
    product_url='https://www.amazon.in/dp/B0CHX1W1XY',
    current_price=119900,
    claimed_mrp=139900
)

print(f"Historical Low: {insights['is_historical_low']}")
print(f"Fake Discount: {insights['is_fake_discount']}")
print(f"Price Drop (7d): {insights['price_drop_7d']}%")
print(f"Trend: {insights['trend_30d']}")
```

### **Detect Duplicates**

```python
from duplicate_detector import DuplicateDetector

detector = DuplicateDetector()

deals = [
    {'title': 'iPhone 15 Pro', 'url': 'https://amazon.in/dp/ABC', 'price': 119900},
    {'title': 'Apple iPhone 15 Pro', 'url': 'https://amazon.in/dp/ABC?ref=xyz', 'price': 119900}
]

# Find duplicates
duplicate_groups = detector.find_duplicates(deals)

# Deduplicate
unique_deals = detector.deduplicate(deals, strategy='best')
```

### **Score Deals**

```python
from deal_scorer import DealScorer

scorer = DealScorer()

deal = {
    'discount_percent': 40,
    'price': 35999,
    'mrp': 59999,
    'rating': 4.3,
    'review_count': 3500,
    'deal_type': 'Festival Sale',
    'seller_type': 'verified',
    'stock_status': 'in_stock',
    'price_insights': {
        'has_history': True,
        'is_historical_low': True,
        'is_fake_discount': False,
        'price_drop_7d': 15.5,
        'trend_30d': 'falling'
    }
}

score_data = scorer.score_deal(deal)

print(f"Total Score: {score_data['total_score']}/100")
print(f"Grade: {score_data['grade']}")
print(f"Recommendation: {score_data['recommendation']}")
print(f"Breakdown: {score_data['breakdown']}")
```

---

## 🎯 **Product Categories**

The system automatically classifies products into:

1. **Electronics** - Phones, laptops, gadgets
2. **Fashion** - Clothing, footwear, accessories
3. **Home** - Furniture, appliances, kitchenware
4. **Beauty** - Cosmetics, skincare, personal care
5. **Baby** - Baby products, toys
6. **Books** - Books, education
7. **Grocery** - Food, daily essentials
8. **Sports** - Sports equipment, fitness
9. **Other** - Miscellaneous

---

## 📈 **Deal Scoring Criteria**

### **Score Breakdown (0-100)**

| Component              | Weight | Description                          |
|------------------------|--------|--------------------------------------|
| Discount Authenticity  | 25 pts | Historical price validation          |
| Discount Percentage    | 20 pts | Actual discount amount               |
| Product Popularity     | 15 pts | Ratings & reviews                    |
| Deal Urgency           | 15 pts | Flash/limited time                   |
| Price Competitiveness  | 15 pts | Historical low, price drops          |
| Seller Trust           | 10 pts | Official/verified seller             |

### **Score Grades**

- **90-100**: A+ (Excellent Deal)
- **85-89**: A (Great Deal)
- **75-84**: B (Good Deal)
- **65-74**: C (Average Deal)
- **Below 65**: D/F (Poor Deal)

---

## 🔍 **Supported Platforms**

### **Official Deal Pages**
- Amazon India (Today's Deals, Lightning Deals)
- Flipkart (Offers Store, Deal of the Day)
- Myntra (Offers, Deals of the Day)

### **Telegram Channels** (30+ channels)
- TrickXpert, DealBlast, Quality_Loots, etc.

### **Product Scrapers**
- Amazon, Flipkart, Myntra, Ajio, Meesho, Shopsy, Tata Cliq, Reliance Digital

---

## 💾 **Database Queries**

### **Get Top Deals**

```sql
SELECT * FROM v_top_deals LIMIT 10;
```

### **Get Historical Low Deals**

```sql
SELECT * FROM v_historical_low_deals;
```

### **Get High-Value Deals (Score >= 75)**

```sql
SELECT * FROM deals 
WHERE is_high_value = TRUE 
AND in_stock = TRUE 
ORDER BY deal_score DESC;
```

### **Get Deals with Bank Offers**

```sql
SELECT title, store, final_effective_price, offers 
FROM deals 
WHERE has_bank_offer = TRUE;
```

### **Get Price History**

```sql
SELECT * FROM price_history 
WHERE product_url = 'your_url' 
ORDER BY observed_at DESC;
```

### **Get Today's Statistics**

```sql
SELECT * FROM v_daily_stats WHERE stat_date = CURRENT_DATE;
```

---

## 🔧 **Advanced Features**

### **Stock Availability Detection**

Automatically detects:
- In stock / Out of stock
- Low stock warnings
- Stock level indicators

### **Coupon & Offer Extraction**

Extracts:
- Coupon codes
- Bank offers (HDFC, ICICI, SBI, etc.)
- Exchange offers
- No-cost EMI availability

### **Final Effective Price**

Calculates:
- Base price
- Coupon discount
- Bank offer discount
- Final effective price
- Total savings

---

## 📱 **Output Formats**

### **JSON Export**

```json
{
  "deals": [
    {
      "title": "iPhone 15 Pro 256GB",
      "score": 87.5,
      "grade": "A",
      "category": "electronics",
      "final_effective_price": 114900,
      "total_savings": 25000,
      "recommendation": "✅ Great Deal! Worth Buying",
      "stock_status": "low_stock",
      "offers": {
        "coupons": ["SAVE10"],
        "bank_offers": ["₹5000 instant discount on HDFC cards"]
      }
    }
  ],
  "count": 1,
  "generated_at": "2025-12-30T10:00:00"
}
```

---

## 🎓 **Best Practices**

1. **Run Official Monitor** every 2-4 hours
2. **Keep Telegram Listener** running continuously
3. **Update daily stats** with `SELECT update_daily_stats();`
4. **Monitor high-value deals** (score >= 75)
5. **Check historical lows** for best prices
6. **Verify stock availability** before buying
7. **Calculate final effective price** with all offers

---

## 🐛 **Troubleshooting**

### **Bot Detection on Amazon**
- Use Selenium with `use_selenium=True`
- Add random delays between requests
- Rotate user agents

### **Missing Dependencies**
```bash
pip install -r requirements.txt
```

### **Database Connection Issues**
- Check Supabase credentials
- Verify RLS policies
- Test connection with `psql`

---

## 📞 **Support**

For issues or questions:
1. Check the error logs
2. Review the ARCHITECTURE.md file
3. Test individual modules separately

---

## 🎉 **Success Metrics**

The system tracks:
- Total deals processed
- Duplicates removed
- High-value deals found
- Average deal score
- Top categories
- Top stores

Generate reports with:
```python
print(agent.generate_report())
```

---

**Version**: 2.0  
**Last Updated**: December 2025  
**Status**: Production Ready ✅
