# Category-wise Organization & Auto-Expiry System

## 📋 Overview

This system adds two major features to your discount bot:

1. **Category-wise Product Organization** - Products are automatically classified into categories (electronics, fashion, home, beauty, books, grocery, sports, etc.)
2. **Automatic Offer Expiry** - Products are automatically removed from the database when their offers expire

## 🗂️ Product Categories

Products are automatically categorized based on their titles into:

- **Electronics** - Phones, laptops, earbuds, smartwatches, TVs, etc.
- **Fashion** - Clothing, shoes, accessories, ethnic wear, etc.
- **Home** - Furniture, decor, kitchenware, appliances, etc.
- **Beauty** - Cosmetics, skincare, makeup, perfumes, etc.
- **Books** - Books, magazines, stationery, etc.
- **Grocery** - Food items, beverages, snacks, etc.
- **Sports** - Fitness equipment, sports gear, etc.
- **Other** - Products that don't fit other categories

## 🚀 Setup Instructions

### Step 1: Run Database Migration

Run the SQL migration script in your Supabase SQL Editor:

```bash
# The script is located at: add_category_and_expiry.sql
```

Go to your Supabase dashboard:
1. Navigate to **SQL Editor**
2. Open the file `add_category_and_expiry.sql`
3. Click **Run** to execute the migration

This will:
- Add `category` column to the deals table
- Add `offer_end_date` column to the deals table
- Create indexes for better query performance
- Create views for active deals and category statistics
- Create a cleanup function for expired deals

### Step 2: Enable Automatic Cleanup (Optional)

For automatic daily cleanup of expired deals, enable the `pg_cron` extension:

1. Go to **Database > Extensions** in Supabase
2. Search for **pg_cron**
3. Click **Enable**
4. Run this in SQL Editor:

```sql
SELECT cron.schedule(
    'cleanup-expired-deals',  -- Job name
    '0 2 * * *',              -- Run daily at 2 AM
    $$SELECT cleanup_expired_deals()$$
);
```

## 📁 New Files Created

### 1. `add_category_and_expiry.sql`
SQL migration script to add category and expiry fields to your database.

### 2. `view_deals_by_category.py`
Interactive viewer for browsing deals by category.

**Features:**
- View all categories with deal counts
- Browse deals by specific category
- View all active deals (excludes expired)
- Manual cleanup of expired deals

**Usage:**
```bash
python view_deals_by_category.py
```

### 3. `cleanup_expired_deals.py`
Automated cleanup script for removing expired deals.

**Usage:**
```bash
python cleanup_expired_deals.py
```

**Schedule on Windows (Task Scheduler):**
```
Task: Daily Cleanup
Trigger: Daily at 2:00 AM
Action: python C:\path\to\cleanup_expired_deals.py
Start in: C:\path\to\project
```

**Schedule on Linux (cron):**
```bash
0 2 * * * cd /path/to/project && python cleanup_expired_deals.py >> cleanup.log 2>&1
```

## 🔧 Updated Files

### `supabase_database.py`
**New Functions:**

```python
# Get deals by category (active only)
get_deals_by_category_supabase(category, limit=10)

# Get all categories with counts
get_all_categories()

# Remove expired deals
cleanup_expired_deals()

# Get all active deals
get_active_deals(limit=50)
```

**Automatic Features:**
- Products are automatically categorized based on their titles
- Default offer expiry is set to 7 days from creation
- Category is saved with every new deal

## 📊 Usage Examples

### View Deals by Category

```python
from supabase_database import init_database, get_deals_by_category_supabase

# Initialize
init_database()

# Get electronics deals
electronics = get_deals_by_category_supabase('electronics', limit=20)

for deal in electronics:
    print(f"{deal['title']} - ₹{deal['verified_price']}")
```

### Get Category Statistics

```python
from supabase_database import init_database, get_all_categories

# Initialize
init_database()

# Get all categories
categories = get_all_categories()

for cat_info in categories:
    print(f"{cat_info['category']}: {cat_info['count']} deals")
```

### Cleanup Expired Deals

```python
from supabase_database import init_database, cleanup_expired_deals

# Initialize
init_database()

# Cleanup
deleted_count = cleanup_expired_deals()
print(f"Removed {deleted_count} expired deals")
```

### Get Only Active Deals

```python
from supabase_database import init_database, get_active_deals

# Initialize
init_database()

# Get active deals (non-expired)
active = get_active_deals(limit=50)

print(f"Found {len(active)} active deals")
```

## 🗄️ Database Schema

### New Fields in `deals` Table

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `category` | VARCHAR(50) | Product category | 'other' |
| `offer_end_date` | TIMESTAMP | When offer expires | +7 days |

### Database Views

#### `active_deals`
Shows only deals that haven't expired:
```sql
SELECT * FROM active_deals;
```

#### `best_deals_by_category`
Shows best active deals organized by category:
```sql
SELECT * FROM best_deals_by_category;
```

#### `category_statistics`
Shows statistics for each category:
```sql
SELECT * FROM category_statistics;
```

## ⚙️ Configuration

### Customize Offer Expiry Duration

By default, offers expire after 7 days. To customize:

```python
from datetime import datetime, timedelta

# Custom expiry (e.g., 3 days)
custom_expiry = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")

deal_data = {
    'verified_title': 'Product Name',
    'verified_price': 999,
    'link': 'https://...',
    'offer_end_date': custom_expiry  # Override default
}

save_to_database(deal_data)
```

### Customize Categories

To modify category keywords, edit `nlp_discount_parser.py`:

```python
CATEGORY_KEYWORDS = {
    'electronics': [
        'phone', 'mobile', 'laptop', 'tablet', 'computer',
        # Add more keywords...
    ],
    'fashion': [
        'shirt', 'tshirt', 'jeans', 'dress', 'shoes',
        # Add more keywords...
    ],
    # Add new categories...
}
```

## 🔍 Query Examples

### Get Active Deals in a Category

```sql
-- Using view
SELECT * FROM active_deals 
WHERE category = 'electronics' 
ORDER BY verified_discount DESC 
LIMIT 10;
```

### Get Category Statistics

```sql
SELECT * FROM category_statistics 
ORDER BY total_deals DESC;
```

### Find Expiring Soon (next 24 hours)

```sql
SELECT title, category, offer_end_date 
FROM deals 
WHERE offer_end_date BETWEEN NOW() AND NOW() + INTERVAL '24 hours'
ORDER BY offer_end_date;
```

### Get Best Deals by Category

```sql
SELECT category, title, verified_discount, verified_price 
FROM active_deals 
WHERE verified_discount > 50 
ORDER BY category, verified_discount DESC;
```

## 🧪 Testing

Test the category system:

```bash
# View deals by category interactively
python view_deals_by_category.py

# Test cleanup function
python cleanup_expired_deals.py

# Check database directly
# (Run in Supabase SQL Editor)
SELECT category, COUNT(*) as count 
FROM active_deals 
GROUP BY category 
ORDER BY count DESC;
```

## 📝 Important Notes

1. **Default Expiry**: All new deals automatically expire after 7 days unless specified otherwise
2. **Active Queries**: Use `get_active_deals()` instead of `get_recent_deals()` to exclude expired offers
3. **Manual Cleanup**: Run `cleanup_expired_deals()` manually or schedule it
4. **Category Detection**: Categories are auto-detected based on product title keywords
5. **NULL Expiry**: If `offer_end_date` is NULL, the deal never expires

## 🆘 Troubleshooting

### Categories Not Showing

```python
# Check if PARSER_AVAILABLE is True
from supabase_database import PARSER_AVAILABLE
print(f"Parser available: {PARSER_AVAILABLE}")

# If False, install dependencies:
pip install -r requirements.txt
```

### Expired Deals Not Removed

```python
# Manually run cleanup
from supabase_database import cleanup_expired_deals
count = cleanup_expired_deals()
print(f"Removed {count} deals")
```

### Wrong Category Assigned

Edit `nlp_discount_parser.py` and add more keywords to the category:

```python
CATEGORY_KEYWORDS = {
    'electronics': [
        'phone', 'mobile', 'laptop',
        'your_new_keyword',  # Add here
    ]
}
```

## 📚 API Reference

### Functions in `supabase_database.py`

```python
# Get deals by category (active only)
get_deals_by_category_supabase(category: str, limit: int = 10) -> List[Dict]

# Get all categories with counts
get_all_categories() -> List[Dict]

# Remove expired deals
cleanup_expired_deals() -> int

# Get all active deals
get_active_deals(limit: int = 50) -> List[Dict]
```

## ✅ Summary

Your discount bot now:
- ✅ Automatically categorizes products
- ✅ Removes expired offers automatically
- ✅ Provides category-wise browsing
- ✅ Shows only active deals by default
- ✅ Includes statistics and reporting views

Enjoy your organized and self-cleaning deal database! 🎉
