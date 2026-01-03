# Daily Deals Scraper - Setup & Usage Guide

## 🎯 Overview

This module automatically collects daily deals from 7 major Indian e-commerce websites and stores them in Supabase. It integrates seamlessly with your existing Telegram listener project.

### Supported Websites
- **Amazon India** - Gold Box Deals
- **Flipkart** - Deal of the Day
- **Myntra** - Fashion Deals
- **Ajio** - Fashion & Lifestyle
- **Meesho** - Budget Deals
- **Tata Cliq** - Electronics & Fashion
- **Reliance Digital** - Electronics & Appliances

---

## 📁 Project Structure

```
New folder (2)/
├── scrapers/               # Website-specific scrapers
│   ├── __init__.py
│   ├── amazon.py
│   ├── flipkart.py
│   ├── myntra.py
│   ├── ajio.py
│   ├── meesho.py
│   ├── tata_cliq.py
│   └── reliance_digital.py
├── database/               # Database client
│   ├── __init__.py
│   └── supabase_client.py
├── scheduler/              # Job scheduling
│   ├── __init__.py
│   └── daily_deals_job.py
├── utils/                  # Helper utilities
│   ├── __init__.py
│   └── helpers.py
├── daily_deals_main.py     # Main entry point
├── daily_deals_schema.sql  # Database schema
├── .env.example            # Environment template
└── requirements.txt        # Dependencies
```

---

## 🚀 Quick Start

### 1. Database Setup

Run the SQL schema in your Supabase SQL Editor:

```sql
-- Navigate to Supabase Dashboard > SQL Editor
-- Copy and run the contents of daily_deals_schema.sql
```

This creates 7 tables:
- `amazon_deals`
- `flipkart_deals`
- `myntra_deals`
- `ajio_deals`
- `meesho_deals`
- `tata_cliq_deals`
- `reliance_digital_deals`

### 2. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# Optional
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0
MAX_DEALS_PER_SITE=50
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `APScheduler` - Task scheduling
- `pytz` - Timezone support
- `urllib3` - HTTP utilities

---

## 📋 Usage

### Run All Scrapers Once

```bash
python daily_deals_main.py --run-once
```

### Run a Specific Scraper

```bash
python daily_deals_main.py --scraper flipkart
```

Available scrapers: `amazon`, `flipkart`, `myntra`, `ajio`, `meesho`, `tata_cliq`, `reliance_digital`

### Start Scheduled Jobs

Run daily at 9:00 AM IST (configurable):

```bash
python daily_deals_main.py --schedule
```

### Show Database Statistics

```bash
python daily_deals_main.py --stats
```

### Test Database Connection

```bash
python daily_deals_main.py --test-db
```

---

## ⚙️ Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SUPABASE_URL` | *Required* | Your Supabase project URL |
| `SUPABASE_KEY` | *Required* | Your Supabase anon key |
| `SCHEDULE_HOUR` | `9` | Hour to run scraper (0-23) |
| `SCHEDULE_MINUTE` | `0` | Minute to run scraper (0-59) |
| `MAX_DEALS_PER_SITE` | `50` | Max deals per website |
| `RUN_NOW` | `false` | Run immediately on start |

### Scheduling Examples

**Run at 6:00 AM:**
```env
SCHEDULE_HOUR=6
SCHEDULE_MINUTE=0
```

**Run at 2:30 PM:**
```env
SCHEDULE_HOUR=14
SCHEDULE_MINUTE=30
```

---

## 🔍 How It Works

### 1. Scraping Process

Each scraper:
- Uses `requests` + `BeautifulSoup` for static pages
- Implements random user-agent rotation
- Adds delays between requests (1-3 seconds)
- Retries failed requests automatically
- Extracts: name, price, discount, URL, image, brand, category

### 2. Data Storage

- **Upsert Logic**: Uses `product_url` as unique key
- **Update vs Insert**: Existing deals are updated with new prices
- **No Duplicates**: Same product URL won't create duplicate entries

### 3. Anti-Blocking Measures

✅ Random user-agent rotation  
✅ Request delays (1-3 seconds)  
✅ Retry logic with exponential backoff  
✅ Session management with connection pooling  

---

## 📊 Database Schema

Each table has the following structure:

```sql
CREATE TABLE website_deals (
    id BIGSERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    original_price DECIMAL(10, 2),
    discounted_price DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2),
    product_url TEXT NOT NULL UNIQUE,
    image_url TEXT,
    website_name VARCHAR(50),
    deal_type VARCHAR(50),
    collected_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

### Query Examples

**Get top deals by discount:**
```sql
SELECT * FROM amazon_deals 
ORDER BY discount_percentage DESC 
LIMIT 10;
```

**Get deals by category:**
```sql
SELECT * FROM flipkart_deals 
WHERE category = 'Electronics' 
ORDER BY discounted_price ASC;
```

**Get recent deals:**
```sql
SELECT * FROM myntra_deals 
WHERE collected_at >= NOW() - INTERVAL '24 hours'
ORDER BY collected_at DESC;
```

---

## 🔧 Integration with Existing Project

The daily deals module is **completely isolated** and won't interfere with your Telegram listener:

### Separate Tables
- Telegram deals → `deals` table (existing)
- E-commerce deals → `amazon_deals`, `flipkart_deals`, etc. (new)

### Separate Processes
- Your Telegram listener continues running independently
- Daily deals scheduler runs as a separate process
- No shared state or dependencies

### Integration Options

**Option 1: Run Both Simultaneously**
```bash
# Terminal 1: Telegram listener
python telegram_listener.py

# Terminal 2: Daily deals (scheduled)
python daily_deals_main.py --schedule
```

**Option 2: Unified View (Optional)**
Create a view combining all deals:
```sql
CREATE VIEW all_deals AS
SELECT 'Amazon' as source, * FROM amazon_deals
UNION ALL
SELECT 'Flipkart' as source, * FROM flipkart_deals
UNION ALL
SELECT 'Telegram' as source, * FROM deals;
```

---

## 🐛 Troubleshooting

### Scrapers Return 0 Deals

**Cause**: Website structure changed or blocking detected

**Solutions**:
1. Check if website is accessible
2. Increase delay between requests
3. Update CSS selectors in scraper code
4. Use Playwright/Selenium for JavaScript-heavy sites

### Database Connection Errors

```bash
# Test connection
python daily_deals_main.py --test-db
```

Check:
- `SUPABASE_URL` is correct
- `SUPABASE_KEY` has proper permissions
- Internet connection is stable

### Scheduler Not Running

Verify timezone:
```python
# In scheduler/daily_deals_job.py
# Default: 'Asia/Kolkata'
```

Check logs for errors:
```bash
python daily_deals_main.py --schedule
# Watch for error messages
```

---

## 🔐 Security Best Practices

1. **Never commit `.env` file**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables in production**
   ```bash
   export SUPABASE_URL="https://..."
   export SUPABASE_KEY="..."
   ```

3. **Limit scraping frequency**
   - Respect website robots.txt
   - Don't scrape more than once per day
   - Use rate limiting

---

## 📈 Performance Tips

### Optimize Scraping Speed

1. **Reduce delays for testing:**
   ```python
   # In utils/helpers.py
   time.sleep(random.uniform(0.5, 1.0))  # Instead of 1-3 seconds
   ```

2. **Limit deals per site:**
   ```env
   MAX_DEALS_PER_SITE=20
   ```

3. **Run scrapers in parallel (advanced):**
   ```python
   # Modify scheduler to use threading
   from concurrent.futures import ThreadPoolExecutor
   ```

### Database Optimization

1. **Clean old deals regularly:**
   ```python
   db.delete_old_deals('amazon', days_old=30)
   ```

2. **Use indexes (already created in schema)**

3. **Monitor table sizes:**
   ```sql
   SELECT pg_size_pretty(pg_total_relation_size('amazon_deals'));
   ```

---

## 🎨 Customization

### Add a New Website

1. Create scraper in `scrapers/new_site.py`:
```python
from utils.helpers import fetch_page, extract_price, format_deal_data

class NewSiteScraper:
    BASE_URL = "https://newsite.com"
    
    def scrape_deals(self, max_deals=50):
        # Implement scraping logic
        pass
```

2. Register in `scrapers/__init__.py`:
```python
from .new_site import scrape_new_site_deals
```

3. Add to scheduler in `scheduler/daily_deals_job.py`:
```python
self.scrapers['new_site'] = scrape_new_site_deals
```

4. Create database table:
```sql
CREATE TABLE new_site_deals (
    -- Same schema as other tables
);
```

### Change Scraping Schedule

Multiple times per day:
```python
# In scheduler/daily_deals_job.py
# Run every 6 hours
self.scheduler.add_job(
    self.run_all_scrapers,
    'interval',
    hours=6
)
```

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review scraper logs for errors
3. Verify website accessibility
4. Test database connection

---

## 📝 License

This module integrates with your existing Telegram listener project. Use according to your project's license and respect website Terms of Service.

---

## ✅ Checklist

- [ ] Database tables created in Supabase
- [ ] `.env` file configured with credentials
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database connection tested (`--test-db`)
- [ ] Test run completed successfully (`--run-once`)
- [ ] Scheduler configured and running (`--schedule`)

**You're all set! 🎉**
