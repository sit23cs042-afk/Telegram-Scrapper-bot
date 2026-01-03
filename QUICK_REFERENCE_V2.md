# 🚀 QUICK REFERENCE - Intelligence Agent Commands

## 📦 Installation
```bash
pip install -r requirements.txt
```

## ⚙️ Environment Setup
```bash
# Windows PowerShell
$env:TELEGRAM_API_ID="your_id"
$env:TELEGRAM_API_HASH="your_hash"
$env:OPENAI_API_KEY="your_key"

# Linux/Mac
export TELEGRAM_API_ID="your_id"
export TELEGRAM_API_HASH="your_hash"
export OPENAI_API_KEY="your_key"

# Supabase (already configured from Telegram setup)
# SUPABASE_URL and SUPABASE_KEY are already in your environment or code
```

## 🗄️ Database Setup
**Uses existing Supabase** (same as Telegram setup)

### Quick Check
```bash
python check_database.py
```

### Setup (if needed)
```bash
# Via Supabase SQL Editor (Recommended):
# 1. Dashboard → SQL Editor
# 2. Copy & paste enhanced_database_schema.sql
# 3. Click Run

# Verify setup
python check_database.py
```

---

## 🎯 CORE COMMANDS

### 1. Run Intelligence Agent (Demo)
```bash
python intelligence_agent.py
```

### 2. Monitor Official Deal Pages
```python
from intelligence_agent import DiscountIntelligenceAgent

agent = DiscountIntelligenceAgent()

# All platforms
deals = agent.monitor_official_deal_pages()

# Specific platforms
deals = agent.monitor_official_deal_pages(['amazon', 'flipkart'])

# Get top deals
top = agent.get_top_deals(deals, limit=10, min_score=75)

# Export
agent.export_deals_json(top, 'deals.json')

# Report
print(agent.generate_report())
```

### 3. Monitor Telegram
```bash
python telegram_listener.py
```

### 4. Test Official Monitor
```bash
python official_deal_monitor.py
```

---

## 💡 CODE SNIPPETS

### Process Single Deal
```python
from intelligence_agent import DiscountIntelligenceAgent

agent = DiscountIntelligenceAgent()

deal = {
    'title': 'Product Name',
    'price': 10000,
    'mrp': 15000,
    'url': 'https://example.com/product',
    'store': 'Amazon',
    'rating': 4.5,
    'review_count': 1000
}

result = agent.process_deal(deal)
print(f"Score: {result['score']}/100")
```

### Track Price History
```python
from price_history_tracker import PriceHistoryTracker

tracker = PriceHistoryTracker()

# Record price
tracker.record_price('url', 10000, 15000, {'title': 'Product'})

# Get insights
insights = tracker.get_price_insights('url', 10000, 15000)
print(insights)
```

### Score Deal
```python
from deal_scorer import DealScorer

scorer = DealScorer()
score_data = scorer.score_deal(deal, price_insights)
print(f"Score: {score_data['total_score']}/100")
```

### Detect Duplicates
```python
from duplicate_detector import DuplicateDetector

detector = DuplicateDetector()
unique = detector.deduplicate(deals, strategy='best')
```

---

## 🗄️ DATABASE QUERIES

### Top Deals
```sql
SELECT * FROM v_top_deals LIMIT 10;
```

### Historical Lows
```sql
SELECT * FROM v_historical_low_deals;
```

### High-Value In-Stock
```sql
SELECT * FROM deals 
WHERE is_high_value = TRUE AND in_stock = TRUE 
ORDER BY deal_score DESC;
```

### Bank Offers
```sql
SELECT title, final_effective_price, offers 
FROM deals 
WHERE has_bank_offer = TRUE;
```

### Price History
```sql
SELECT * FROM price_history 
WHERE product_url = 'url' 
ORDER BY observed_at DESC;
```

### Today's Stats
```sql
SELECT * FROM v_daily_stats 
WHERE stat_date = CURRENT_DATE;
```

### Update Daily Stats
```sql
SELECT update_daily_stats();
```

---

## 📊 SCORING BREAKDOWN

| Component            | Weight | Range  |
|---------------------|--------|--------|
| Discount Authenticity| 25%    | 0-25   |
| Discount Percentage  | 20%    | 0-20   |
| Product Popularity   | 15%    | 0-15   |
| Deal Urgency         | 15%    | 0-15   |
| Price Competitiveness| 15%    | 0-15   |
| Seller Trust         | 10%    | 0-10   |
| **TOTAL**            | **100%**| **0-100** |

---

## 🎯 SCORE GRADES

- **90-100 (A+)**: 🔥 Excellent Deal
- **85-89 (A)**: ✅ Great Deal
- **75-84 (B)**: 👍 Good Deal
- **65-74 (C)**: ⚠️ Average Deal
- **<65**: ❌ Poor Deal

---

## 🌐 SUPPORTED PLATFORMS

### Official Monitors
- Amazon India
- Flipkart
- Myntra

### Scrapers
- Amazon, Flipkart, Myntra
- Ajio, Meesho, Shopsy
- Tata Cliq, Reliance Digital

---

## 🔧 TESTING

### Test Individual Modules
```bash
python price_history_tracker.py
python deal_scorer.py
python duplicate_detector.py
python scraper_enhancements.py
```

---

## 📁 KEY FILES

| File                          | Purpose                    |
|-------------------------------|----------------------------|
| intelligence_agent.py         | Main orchestrator          |
| official_deal_monitor.py      | Deal page scraper          |
| price_history_tracker.py      | Price tracking             |
| deal_scorer.py                | Scoring system             |
| duplicate_detector.py         | Deduplication              |
| scraper_enhancements.py       | Stock & offers             |
| telegram_listener.py          | Telegram monitoring        |
| enhanced_database_schema.sql  | Database schema            |

---

## 🐛 TROUBLESHOOTING

### Bot Detection
```python
monitor = AmazonDealMonitor(use_selenium=True)
```

### Missing Packages
```bash
pip install selenium webdriver-manager
```

### Database Issues
- Check credentials in .env
- Verify RLS policies
- Run schema: `psql ... -f enhanced_database_schema.sql`

---

## 📊 OUTPUT FORMAT

```json
{
  "title": "Product",
  "score": 87.5,
  "grade": "A",
  "category": "electronics",
  "final_effective_price": 9500,
  "total_savings": 5500,
  "recommendation": "✅ Great Deal!",
  "stock_status": "low_stock",
  "in_stock": true,
  "offers": {
    "coupons": ["SAVE10"],
    "bank_offers": ["₹500 off on HDFC"]
  }
}
```

---

## ⏰ RECOMMENDED SCHEDULE

- **Official Monitor**: Every 2-4 hours
- **Telegram**: Continuous (real-time)
- **Stats Update**: Daily at midnight

---

## 📞 QUICK HELP

```bash
# View help
python intelligence_agent.py --help

# Check status
python -c "from intelligence_agent import DiscountIntelligenceAgent; print('✅ OK')"

# Test database
python -c "from supabase_database import get_supabase_client; print('✅ DB OK')"
```

---

**Version**: 2.0  
**Status**: ✅ Production Ready
