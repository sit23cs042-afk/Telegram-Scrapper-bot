# 💡 Database Connection - How It Works

## 🎯 **TL;DR**

**All modules use your existing Supabase database** - the same one configured for Telegram. No separate database setup needed!

---

## 🔌 **Connection Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                Your Supabase Database                   │
│            (Already configured for Telegram)            │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        │  supabase_database.py   │
        │  (Central connection)   │
        │                         │
        └────────────┬────────────┘
                     │
        ┌────────────┴─────────────┐
        │                          │
   ┌────▼────┐              ┌──────▼──────┐
   │ Telegram│              │Intelligence │
   │ Listener│              │   Agent     │
   └────┬────┘              └──────┬──────┘
        │                          │
        ├──────────────┬───────────┤
        │              │           │
   ┌────▼────┐   ┌────▼────┐ ┌───▼────┐
   │  Price  │   │  Deal   │ │ Dupli  │
   │ Tracker │   │ Scorer  │ │  cate  │
   └─────────┘   └─────────┘ └────────┘
```

All modules connect through `supabase_database.py` using `get_supabase_client()`

---

## 📝 **Current Configuration**

### **From your `supabase_database.py`:**

```python
# Supabase configuration (already set up)
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://sspufleiikzsazouzkot.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGc...')  # Your key

# Connection function
def get_supabase_client():
    global supabase
    if supabase is None:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase
```

---

## 🔧 **How New Modules Connect**

### **Example 1: Price History Tracker**

```python
# price_history_tracker.py
from supabase_database import get_supabase_client

class PriceHistoryTracker:
    def __init__(self):
        # Uses your existing Supabase connection
        self.client = get_supabase_client()
    
    def record_price(self, url, price, mrp):
        # Saves to YOUR Supabase database
        self.client.table('price_history').insert({...}).execute()
```

### **Example 2: Intelligence Agent**

```python
# intelligence_agent.py
from supabase_database import save_to_database

def process_deal(deal):
    # Uses your existing save function
    save_to_database(deal)  # Saves to YOUR database
```

---

## 🗄️ **Database Structure**

### **Existing (From Telegram Setup)**
```
deals                    ← Main table (already exists)
├─ id
├─ title
├─ price
├─ store
└─ ... (existing columns)
```

### **New (After running schema)**
```
deals                    ← Enhanced with new columns
├─ ... (existing columns)
├─ deal_score           ← NEW
├─ stock_status         ← NEW
├─ final_effective_price ← NEW
└─ ... (30+ new columns)

price_history           ← NEW table
deal_sources            ← NEW table
product_urls            ← NEW table
intelligence_stats      ← NEW table
```

---

## ✅ **Verification**

### **Check 1: Test Existing Connection**

```python
# This should work if Telegram is configured
from supabase_database import get_supabase_client

client = get_supabase_client()
print("✅ Connected to:", client.url)
```

### **Check 2: Verify Database Setup**

```bash
# Run the checker script
python check_database.py
```

Output should show:
```
✅ Connected to Supabase
✅ price_history table exists
✅ deal_sources table exists
✅ product_urls table exists
✅ intelligence_stats table exists
✅ deals table has new columns
```

---

## 🛠️ **Setup Steps (One Time)**

### **Step 1: Verify Existing Connection**
```bash
python -c "from supabase_database import get_supabase_client; print(get_supabase_client().url)"
```

Expected output: `https://sspufleiikzsazouzkot.supabase.co`

### **Step 2: Add New Tables**
1. Open Supabase Dashboard
2. Go to SQL Editor
3. Copy `enhanced_database_schema.sql`
4. Paste and Run

### **Step 3: Verify Setup**
```bash
python check_database.py
```

---

## 🎯 **What Gets Shared**

### **Shared Resources**
- ✅ Supabase connection
- ✅ Database instance
- ✅ `deals` table (enhanced)
- ✅ Authentication credentials
- ✅ RLS policies

### **Independent Resources**
- ✅ New tables (price_history, etc.)
- ✅ New views
- ✅ New functions
- ✅ New indexes

---

## 💰 **Supabase Usage**

### **Current Usage (Telegram Only)**
- Stores deal records in `deals` table
- ~500 MB database size (estimated)

### **After Enhancement**
- Same `deals` table + new columns
- New tables for price history
- Estimated increase: +200 MB
- Still well within free tier (500 MB limit)

### **Free Tier Limits**
- ✅ 500 MB database storage
- ✅ 50,000 monthly active users
- ✅ 500 MB egress
- ✅ Unlimited API requests

**You'll stay within free tier with normal usage**

---

## 🔐 **Security (RLS)**

All new tables have Row Level Security enabled:

```sql
-- Applied automatically in schema
ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all operations on price_history" 
ON price_history FOR ALL USING (true) WITH CHECK (true);
```

You can adjust policies in Supabase Dashboard → Authentication → Policies

---

## 🐛 **Common Issues**

### **"Table does not exist"**
**Solution**: Run `enhanced_database_schema.sql` in Supabase SQL Editor

### **"Column does not exist"**
**Solution**: The schema adds new columns to `deals` table. Re-run the schema.

### **"Permission denied"**
**Solution**: Check RLS policies in Supabase Dashboard

### **Connection timeout**
**Solution**: Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct

---

## 📊 **Testing the Connection**

### **Complete Test**

```python
# test_connection.py
from supabase_database import get_supabase_client
from price_history_tracker import PriceHistoryTracker

# Test 1: Basic connection
client = get_supabase_client()
print(f"✅ Connected to: {client.url}")

# Test 2: Check tables
tables = ['deals', 'price_history', 'deal_sources', 'product_urls']
for table in tables:
    try:
        result = client.table(table).select('*').limit(1).execute()
        print(f"✅ Table '{table}' accessible")
    except Exception as e:
        print(f"❌ Table '{table}' error: {e}")

# Test 3: Price tracking
tracker = PriceHistoryTracker()
tracker.record_price(
    'https://test.com',
    1000.0,
    1500.0,
    {'test': True}
)
print("✅ Price tracking works")

print("\n🎉 All tests passed!")
```

---

## 📚 **Summary**

1. **Single Database**: Everything uses your existing Supabase
2. **Single Connection**: All modules use `supabase_database.py`
3. **No Duplication**: Same credentials, same instance
4. **Enhanced Schema**: Only adds new tables/columns
5. **Backward Compatible**: Telegram listener still works
6. **Easy Verification**: Run `python check_database.py`

---

**Questions?**
- Check [DATABASE_SETUP.md](DATABASE_SETUP.md) for detailed setup
- Run `python check_database.py` to verify
- Review `enhanced_database_schema.sql` to see what's added

**Status**: ✅ Ready to use with your existing Supabase!
