# Daily Deals Module - Quick Reference

## 🚀 Quick Commands

```bash
# Test database connection
python daily_deals_main.py --test-db

# Run all scrapers once
python daily_deals_main.py --run-once

# Run single scraper
python daily_deals_main.py --scraper amazon

# Start scheduled jobs (daily at 9 AM)
python daily_deals_main.py --schedule

# View statistics
python daily_deals_main.py --stats
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `daily_deals_main.py` | Main entry point |
| `daily_deals_schema.sql` | Database schema |
| `.env` | Configuration (create from `.env.example`) |
| `DAILY_DEALS_README.md` | Full documentation |

## ⚙️ Environment Variables

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0
MAX_DEALS_PER_SITE=50
```

## 🗄️ Database Tables

- `amazon_deals`
- `flipkart_deals`
- `myntra_deals`
- `ajio_deals`
- `meesho_deals`
- `tata_cliq_deals`
- `reliance_digital_deals`

## 🔧 Module Structure

```
scrapers/          → Website scrapers
database/          → Supabase client
scheduler/         → APScheduler jobs
utils/             → Helper functions
```

## ✨ Features

✅ 7 major e-commerce sites  
✅ Automatic price updates (upsert)  
✅ No duplicate entries  
✅ Daily scheduling  
✅ Anti-blocking measures  
✅ Modular & extensible  

## 📊 Sample Query

```sql
-- Get top 10 deals by discount
SELECT product_name, brand, discounted_price, discount_percentage
FROM amazon_deals
ORDER BY discount_percentage DESC
LIMIT 10;
```

## 🐛 Common Issues

**No deals found**: Website structure changed, check logs  
**DB connection error**: Verify SUPABASE_URL and SUPABASE_KEY  
**Import errors**: Run `pip install -r requirements.txt`  

## 📖 Full Docs

See [DAILY_DEALS_README.md](DAILY_DEALS_README.md) for complete documentation.
