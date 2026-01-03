# 🗄️ Database Setup Guide - Using Existing Supabase

## ✅ **Good News!**

The Intelligence Agent uses your **existing Supabase database** - the same one you've already configured for the Telegram listener. No need for a separate database!

---

## 📋 **Prerequisites**

You should already have:
- ✅ Supabase project created
- ✅ `SUPABASE_URL` configured
- ✅ `SUPABASE_KEY` configured
- ✅ `deals` table exists (from Telegram setup)

If you can run `python telegram_listener.py` successfully, you're all set!

---

## 🚀 **Setup Steps**

### **Step 1: Verify Connection**

Test your existing Supabase connection:

```bash
python -c "from supabase_database import get_supabase_client; client = get_supabase_client(); print('✅ Supabase connected!')"
```

### **Step 2: Run Enhanced Schema**

Add the new tables and columns to your existing database:

#### **Option A: Via Supabase Dashboard (Recommended)**

1. Go to your Supabase Dashboard: https://app.supabase.com
2. Select your project
3. Click **SQL Editor** (left sidebar)
4. Click **New Query**
5. Copy the entire contents of `enhanced_database_schema.sql`
6. Paste into the editor
7. Click **Run** or press `Ctrl+Enter`

#### **Option B: Via Command Line**

```bash
# Replace with your actual Supabase connection details
psql -h db.sspufleiikzsazouzkot.supabase.co -U postgres -d postgres -f enhanced_database_schema.sql
```

---

## 📊 **What Gets Added**

### **New Tables (4)**
- `price_history` - Historical price tracking
- `deal_sources` - Multi-source tracking
- `product_urls` - URL normalization
- `intelligence_stats` - Daily statistics

### **Enhanced Tables**
- `deals` - Adds 30+ new columns:
  - Stock fields
  - Score fields
  - Offer fields
  - Price breakdown
  - Intelligence metadata

### **New Views (5)**
- `v_top_deals`
- `v_historical_low_deals`
- `v_high_value_deals`
- `v_price_history_summary`
- `v_daily_stats`

### **Functions (2)**
- `update_product_url_mapping()`
- `update_daily_stats()`

---

## ✅ **Verify Setup**

After running the schema, verify everything is set up:

```sql
-- Check new tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('price_history', 'deal_sources', 'product_urls', 'intelligence_stats');

-- Check views exist
SELECT table_name FROM information_schema.views 
WHERE table_schema = 'public' 
AND table_name LIKE 'v_%';

-- Check new columns in deals table
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'deals' 
AND column_name IN ('deal_score', 'stock_status', 'final_effective_price');
```

---

## 🔧 **Connection Details**

All modules automatically use the same Supabase connection:

```python
# From supabase_database.py (already configured)
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://sspufleiikzsazouzkot.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your-key')
```

New modules (`price_history_tracker.py`, `intelligence_agent.py`, etc.) all use this same connection via:

```python
from supabase_database import get_supabase_client

client = get_supabase_client()
```

---

## 🎯 **Quick Test**

After setup, test the new features:

```python
from price_history_tracker import PriceHistoryTracker

tracker = PriceHistoryTracker()

# Record a test price
tracker.record_price(
    product_url='https://www.amazon.in/test',
    price=1000.0,
    mrp=1500.0,
    metadata={'title': 'Test Product'}
)

# Get insights
insights = tracker.get_price_insights(
    product_url='https://www.amazon.in/test',
    current_price=1000.0,
    claimed_mrp=1500.0
)

print("✅ Price tracking working!" if insights else "❌ Issue with setup")
```

---

## 🐛 **Troubleshooting**

### **Error: "relation does not exist"**
- Run the `enhanced_database_schema.sql` script
- Check you're connected to the correct database

### **Error: "permission denied"**
- Verify your RLS policies allow the operations
- The schema includes policies - make sure they were created

### **Error: "column does not exist"**
- The schema updates the `deals` table with new columns
- Make sure all ALTER TABLE statements ran successfully

### **Connection Issues**
```bash
# Test connection
python -c "from supabase_database import get_supabase_client; print(get_supabase_client())"
```

---

## 📝 **Notes**

- ✅ **No separate database needed** - uses your existing Supabase
- ✅ **No data loss** - only adds new tables/columns
- ✅ **Backward compatible** - existing Telegram listener continues to work
- ✅ **Row Level Security** - all new tables have RLS enabled
- ✅ **Indexes created** - for optimal query performance

---

## 🎉 **That's It!**

Your database is now ready for the Intelligence Agent. All modules will automatically use your existing Supabase connection.

**Next Steps:**
```bash
# Run the intelligence agent demo
python intelligence_agent.py

# Or monitor official deal pages
python official_deal_monitor.py
```

---

**Version**: 2.0  
**Database**: Supabase (existing connection)  
**Status**: ✅ Ready to use
