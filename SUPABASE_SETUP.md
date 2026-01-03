# Supabase Setup Guide

## 1. Create Supabase Account & Project

1. Go to https://supabase.com
2. Sign up / Log in
3. Click "New Project"
4. Fill in details:
   - Name: discount-deals
   - Database Password: (create strong password)
   - Region: (choose closest to you)
5. Wait for project to be created (~2 minutes)

## 2. Create Database Table

1. In Supabase Dashboard, go to **Table Editor**
2. Click **New Table**
3. Table name: `deals`
4. Add columns:

```sql
CREATE TABLE deals (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    store TEXT,
    mrp TEXT,
    discount_price TEXT,
    discount_percent TEXT,
    link TEXT NOT NULL,
    category TEXT,
    channel TEXT,
    message_id BIGINT,
    message_date TIMESTAMPTZ,
    timestamp TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(link, message_id)
);

-- Create indexes for faster queries
CREATE INDEX idx_store ON deals(store);
CREATE INDEX idx_category ON deals(category);
CREATE INDEX idx_created_at ON deals(created_at DESC);
```

Or use the SQL Editor:
- Go to **SQL Editor** → **New Query**
- Paste the SQL above
- Click **Run**

## 3. Get API Credentials

1. Go to **Settings** → **API**
2. Copy:
   - **Project URL** (e.g., https://xxxxx.supabase.co)
   - **anon public** key

## 4. Configure Python Project

### Install Supabase Python SDK:
```bash
pip install supabase
```

### Set Environment Variables:

**Windows (PowerShell):**
```powershell
$env:SUPABASE_URL="https://your-project.supabase.co"
$env:SUPABASE_KEY="your-anon-key-here"
```

**Or edit telegram_listener.py:**
Update the import at the top:
```python
# Change from:
from database import save_to_database, init_database

# To:
from supabase_database import save_to_database, init_database
```

**Or edit supabase_database.py directly:**
```python
SUPABASE_URL = 'https://your-project.supabase.co'
SUPABASE_KEY = 'your-anon-key-here'
```

## 5. Test Connection

```bash
python supabase_database.py
```

## 6. Update Telegram Listener

The telegram_listener.py will automatically use Supabase if you:
1. Rename imports or
2. Rename `supabase_database.py` to `database.py` (replace old file)

## 7. Run Bot

```bash
python telegram_listener.py
```

## 8. View Data in Supabase

- Go to Supabase Dashboard → **Table Editor**
- Select `deals` table
- See all collected deals in real-time!

## Benefits of Supabase:

✅ Cloud-hosted (access from anywhere)
✅ Real-time subscriptions
✅ Built-in authentication
✅ Automatic backups
✅ REST API included
✅ PostgreSQL (more powerful than SQLite)
✅ Free tier: 500MB database, 2GB bandwidth

---

**Need help?** Check the Supabase docs: https://supabase.com/docs
