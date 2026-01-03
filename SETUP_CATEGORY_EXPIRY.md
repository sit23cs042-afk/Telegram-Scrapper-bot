# Quick Setup Guide - Category & Expiry Features

## ⚡ Quick Start (5 minutes)

### Step 1: Run Database Migration
1. Open your Supabase dashboard: https://app.supabase.com
2. Go to **SQL Editor**
3. Open and run: `add_category_and_expiry.sql`

### Step 2: Test the System
```bash
# Activate your virtual environment
.\.venv\Scripts\Activate.ps1

# View deals by category
python view_deals_by_category.py
```

## ✅ What's New

### 1. Automatic Categorization
Products are now automatically sorted into:
- Electronics (phones, laptops, etc.)
- Fashion (clothing, shoes, etc.)
- Home (furniture, appliances, etc.)
- Beauty (cosmetics, skincare, etc.)
- Books, Grocery, Sports, Other

### 2. Auto-Expiry
- Offers automatically expire after **7 days** (configurable)
- Expired deals are hidden from searches
- Run cleanup manually or schedule it

## 🎯 Key Features

### Browse by Category
```bash
python view_deals_by_category.py
```
Options:
1. View all categories
2. View deals by category
3. View all active deals
4. Cleanup expired deals

### Manual Cleanup
```bash
python cleanup_expired_deals.py
```

### Schedule Automatic Cleanup (Optional)

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task → "Daily Cleanup"
3. Trigger: Daily at 2:00 AM
4. Action: `python C:\path\to\cleanup_expired_deals.py`

**Linux (cron):**
```bash
crontab -e
# Add this line:
0 2 * * * cd /path/to/project && python cleanup_expired_deals.py >> cleanup.log 2>&1
```

## 📊 Usage in Code

### Get Deals by Category
```python
from supabase_database import init_database, get_deals_by_category_supabase

init_database()
electronics = get_deals_by_category_supabase('electronics', limit=20)
```

### Get All Categories
```python
from supabase_database import get_all_categories

categories = get_all_categories()
# Returns: [{'category': 'electronics', 'count': 45}, ...]
```

### Cleanup Expired Deals
```python
from supabase_database import cleanup_expired_deals

deleted = cleanup_expired_deals()
print(f"Removed {deleted} expired deals")
```

## 🗃️ Database Views

### Active Deals (Excludes Expired)
```sql
SELECT * FROM active_deals;
```

### Best Deals by Category
```sql
SELECT * FROM best_deals_by_category;
```

### Category Statistics
```sql
SELECT * FROM category_statistics;
```

## 🔧 Customize Expiry Time

Default: 7 days. To change:

Edit `supabase_database.py`, line ~90:
```python
# Change from 7 to your desired days
offer_end_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
```

## 📝 Files Modified/Created

**New Files:**
- `add_category_and_expiry.sql` - Database migration
- `view_deals_by_category.py` - Category viewer
- `cleanup_expired_deals.py` - Cleanup script
- `CATEGORY_EXPIRY_README.md` - Full documentation

**Modified Files:**
- `supabase_database.py` - Added category & expiry functions

## 🧪 Test Everything

1. **View categories:**
   ```bash
   python view_deals_by_category.py
   ```

2. **Check database:**
   Go to Supabase → Table Editor → deals
   - You should see `category` and `offer_end_date` columns

3. **Test cleanup:**
   ```bash
   python cleanup_expired_deals.py
   ```

## 🆘 Troubleshooting

### "PARSER_AVAILABLE is False"
```bash
pip install -r requirements.txt
```

### Categories Not Showing
- Run the SQL migration first
- Restart your bot to pick up changes

### Cleanup Not Working
- Check Supabase connection
- Verify `offer_end_date` column exists

## 📞 Need Help?

See `CATEGORY_EXPIRY_README.md` for detailed documentation.

---

**Done! Your bot now has category organization and auto-expiry. 🎉**
