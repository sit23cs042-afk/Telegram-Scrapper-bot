# 🤖 Discount Product Intelligence Agent

> AI-powered system for detecting, verifying, and scoring discounted products from Indian e-commerce platforms.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ **Features**

### **🎯 Dual Monitoring System**
- 📱 **Telegram Integration**: Monitors 30+ deal channels in real-time
- 🌐 **Official Deal Pages**: Direct scraping from Amazon, Flipkart, Myntra

### **📊 Advanced Intelligence**
- 📈 **Historical Price Tracking**: 90-day price history with fake discount detection
- 🏆 **Deal Scoring (0-100)**: Multi-factor scoring for deal quality
- 🔍 **Duplicate Detection**: Smart deduplication across sources
- 📦 **Stock Availability**: Real-time stock status monitoring
- 💰 **Final Price Calculator**: Includes coupons, bank offers, and all discounts

### **🤖 AI-Powered**
- 🧠 **Smart Categorization**: Automatic product classification (9 categories)
- ✅ **Deal Verification**: LLM-based authenticity checking
- 🎨 **Vision Extraction**: OCR fallback for image-based deals

---

## 🚀 **Quick Start**

### **1. Installation**

```bash
# Clone the repository
git clone <your-repo>
cd <your-folder>

# Install dependencies
pip install -r requirements.txt
```

### **2. Configuration**

Create a `.env` file or set environment variables:

```bash
# Telegram API (get from https://my.telegram.org)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# OpenAI API (for AI features)
OPENAI_API_KEY=your_openai_key

# Supabase Database (already configured from Telegram setup)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

**Note**: If your Telegram listener is working, Supabase is already configured!

### **3. Setup Database**

**Uses your existing Supabase database** (same as Telegram setup).

```bash
# Run via Supabase SQL Editor (Recommended)
# 1. Go to Supabase Dashboard → SQL Editor
# 2. Copy contents of enhanced_database_schema.sql
# 3. Paste and Run

# Or via command line:
psql -h db.your-project.supabase.co -U postgres -f enhanced_database_schema.sql
```

### **4. Run the System**

#### **Option 1: Demo Mode (Test with sample data)**

```bash
python intelligence_agent.py
```

#### **Option 2: Monitor Official Deal Pages**

```python
from intelligence_agent import DiscountIntelligenceAgent

agent = DiscountIntelligenceAgent()

# Monitor all platforms
deals = agent.monitor_official_deal_pages()

# Get top deals (score >= 75)
top_deals = agent.get_top_deals(deals, limit=10, min_score=75)

# Export to JSON
agent.export_deals_json(top_deals, 'top_deals.json')

# Generate report
print(agent.generate_report())
```

#### **Option 3: Monitor Telegram Channels**

```bash
python telegram_listener.py
```

---

## 📁 **Project Structure**

```
├── intelligence_agent.py           # 🎯 Main orchestrator
├── telegram_listener.py            # 📱 Telegram monitoring
├── official_deal_monitor.py        # 🌐 Official deal scraper
├── product_scraper.py              # 🔧 Site-specific scrapers
├── price_history_tracker.py        # 📈 Historical price tracking
├── deal_scorer.py                  # 🏆 Deal scoring (0-100)
├── duplicate_detector.py           # 🔍 Duplicate detection
├── scraper_enhancements.py         # 💎 Stock & offers extraction
├── smart_categorizer.py            # 🤖 AI categorization
├── nlp_discount_parser.py          # 📝 NLP message parsing
├── enhanced_database_schema.sql    # 💾 Database schema
└── INTELLIGENCE_AGENT_GUIDE.md     # 📚 Complete documentation
```

---

## 📊 **Deal Scoring System (0-100)**

| Component              | Weight | Description                          |
|------------------------|--------|--------------------------------------|
| Discount Authenticity  | 25%    | Historical price validation          |
| Discount Percentage    | 20%    | Actual discount amount               |
| Product Popularity     | 15%    | Ratings & review count               |
| Deal Urgency           | 15%    | Flash/limited time deals             |
| Price Competitiveness  | 15%    | Historical lows, price drops         |
| Seller Trust           | 10%    | Official/verified sellers            |

### **Score Grades**
- **90-100 (A+)**: 🔥 Excellent Deal! Highly Recommended
- **85-89 (A)**: ✅ Great Deal! Worth Buying
- **75-84 (B)**: 👍 Good Deal! Consider It
- **65-74 (C)**: ⚠️ Average Deal
- **Below 65**: ❌ Poor Deal

---

## 🎯 **Supported Platforms**

### **Official Deal Pages**
- ✅ Amazon India (Today's Deals, Lightning Deals)
- ✅ Flipkart (Offers Store, Deal of the Day)
- ✅ Myntra (Offers, Deals of the Day)

### **Product Scrapers**
- ✅ Amazon, Flipkart, Myntra, Ajio, Meesho, Shopsy
- ✅ Tata Cliq, Reliance Digital, Croma, Vijay Sales

### **Telegram Channels**
- ✅ 30+ monitored channels

---

## 💡 **Usage Examples**

### **Example 1: Process a Deal**

```python
from intelligence_agent import DiscountIntelligenceAgent

agent = DiscountIntelligenceAgent()

deal = {
    'title': 'iPhone 15 Pro 256GB',
    'price': 119900,
    'mrp': 139900,
    'url': 'https://www.amazon.in/dp/B0CHX1W1XY',
    'store': 'Amazon',
    'rating': 4.5,
    'review_count': 5000,
    'deal_type': 'Lightning Deal',
    'seller_type': 'official'
}

result = agent.process_deal(deal)

print(f"Score: {result['score']}/100")
print(f"Grade: {result['grade']}")
print(f"Category: {result['category']}")
print(f"Recommendation: {result['recommendation']}")
```

**Output:**
```
Score: 87.5/100
Grade: A
Category: electronics
Recommendation: ✅ Great Deal! Worth Buying
```

### **Example 2: Track Price History**

```python
from price_history_tracker import PriceHistoryTracker

tracker = PriceHistoryTracker()

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

### **Example 3: Monitor Deal Pages**

```bash
python official_deal_monitor.py
```

---

## 📊 **Database Queries**

### **Get Top 10 Deals**
```sql
SELECT * FROM v_top_deals LIMIT 10;
```

### **Get Historical Low Deals**
```sql
SELECT * FROM v_historical_low_deals;
```

### **Get High-Value In-Stock Deals**
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

---

## 📱 **Output Format (JSON)**

```json
{
  "title": "iPhone 15 Pro 256GB",
  "score": 87.5,
  "grade": "A",
  "category": "electronics",
  "sub_category": "smartphones",
  "final_effective_price": 114900,
  "total_savings": 25000,
  "recommendation": "✅ Great Deal! Worth Buying",
  "stock_status": "low_stock",
  "in_stock": true,
  "offers": {
    "coupons": ["SAVE10"],
    "bank_offers": ["₹5000 instant discount on HDFC cards"],
    "no_cost_emi": true
  },
  "price_insights": {
    "is_historical_low": true,
    "is_fake_discount": false,
    "price_drop_7d": 8.5,
    "trend_30d": "falling"
  },
  "score_breakdown": {
    "discount_authenticity": 25.0,
    "discount_percentage": 14.0,
    "product_popularity": 14.5,
    "deal_urgency": 10.0,
    "price_competitiveness": 15.0,
    "seller_trust": 10.0
  }
}
```

---

## 🎓 **Key Capabilities**

### **✅ What It Does**
- Monitors 30+ Telegram channels + official deal pages
- Tracks 90-day price history
- Detects fake discounts using historical data
- Scores deals on 0-100 scale with 6 factors
- Extracts stock availability, coupons, bank offers
- Calculates final effective price
- Removes duplicates across sources
- Categorizes products automatically
- Saves everything to database

### **🎯 What Makes It Intelligent**
- Historical price comparison (not just claimed discounts)
- Multi-factor deal scoring
- Fake discount detection
- Cross-platform deduplication
- Real-time stock monitoring
- Complete offer extraction
- AI-powered categorization

---

## 📚 **Documentation**

- **[INTELLIGENCE_AGENT_GUIDE.md](INTELLIGENCE_AGENT_GUIDE.md)** - Complete usage guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[DEAL_VERIFICATION_SUMMARY.md](DEAL_VERIFICATION_SUMMARY.md)** - Verification pipeline

---

## 🐛 **Troubleshooting**

### **Bot Detection on Amazon**
```python
# Use Selenium
monitor = AmazonDealMonitor(use_selenium=True)
```

### **Missing Dependencies**
```bash
pip install -r requirements.txt
```

### **Database Connection Issues**
- Verify Supabase credentials
- Check RLS policies
- Run enhanced schema

---

## 🎉 **System Statistics**

The agent tracks:
- ✅ Total deals processed
- ✅ Duplicates removed
- ✅ High-value deals (score >= 75)
- ✅ Average deal score
- ✅ Top categories
- ✅ Top stores

Generate report:
```python
print(agent.generate_report())
```

---

## 🔧 **Configuration**

### **Monitoring Schedule**
- Official pages: Every 2-4 hours
- Telegram: Real-time continuous

### **Score Thresholds**
- High-value: >= 75
- Recommended: >= 65
- Acceptable: >= 55

### **Price History**
- Tracking period: 90 days
- Fake discount tolerance: 20%

---

## 📞 **Support**

For issues:
1. Check error logs
2. Review documentation
3. Test modules individually

---

## 📄 **License**

MIT License - See LICENSE file

---

## 🎯 **Version**

**v2.0** - Production Ready ✅

**Features:**
- ✅ Dual monitoring (Telegram + Official)
- ✅ Historical price tracking
- ✅ Deal scoring (0-100)
- ✅ Stock & offers intelligence
- ✅ Duplicate detection
- ✅ Complete automation

---

**Built with ❤️ for the Indian e-commerce ecosystem**
