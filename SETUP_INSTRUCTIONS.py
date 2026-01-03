"""
AUTOMATED DATABASE SETUP COMPLETE - FINAL INSTRUCTIONS
======================================================

✅ CONNECTION SUCCESSFUL
Your Supabase credentials are configured and working!
- URL: https://sspufleiikzsazouzkot.supabase.co
- Connection: ✓ VERIFIED

⚠️  ONE MANUAL STEP REQUIRED
The 7 tables need to be created in Supabase. This takes 30 seconds:

QUICK SETUP (30 seconds):
1. Open this link: https://supabase.com/dashboard/project/sspufleiikzsazouzkot/sql/new

2. Paste THIS SQL (copy from below):

```sql
-- Create all 7 tables at once
CREATE TABLE IF NOT EXISTS amazon_deals (
    id BIGSERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    original_price DECIMAL(10, 2),
    discounted_price DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2),
    product_url TEXT NOT NULL UNIQUE,
    image_url TEXT,
    website_name VARCHAR(50) DEFAULT 'Amazon India',
    deal_type VARCHAR(50),
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS flipkart_deals (
    id BIGSERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    original_price DECIMAL(10, 2),
    discounted_price DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2),
    product_url TEXT NOT NULL UNIQUE,
    image_url TEXT,
    website_name VARCHAR(50) DEFAULT 'Flipkart',
    deal_type VARCHAR(50),
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS myntra_deals (
    id BIGSERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    original_price DECIMAL(10, 2),
    discounted_price DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2),
    product_url TEXT NOT NULL UNIQUE,
    image_url TEXT,
    website_name VARCHAR(50) DEFAULT 'Myntra',
    deal_type VARCHAR(50),
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ajio_deals (
    id BIGSERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    original_price DECIMAL(10, 2),
    discounted_price DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2),
    product_url TEXT NOT NULL UNIQUE,
    image_url TEXT,
    website_name VARCHAR(50) DEFAULT 'Ajio',
    deal_type VARCHAR(50),
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS meesho_deals (
    id BIGSERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    original_price DECIMAL(10, 2),
    discounted_price DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2),
    product_url TEXT NOT NULL UNIQUE,
    image_url TEXT,
    website_name VARCHAR(50) DEFAULT 'Meesho',
    deal_type VARCHAR(50),
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tata_cliq_deals (
    id BIGSERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    original_price DECIMAL(10, 2),
    discounted_price DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2),
    product_url TEXT NOT NULL UNIQUE,
    image_url TEXT,
    website_name VARCHAR(50) DEFAULT 'Tata Cliq',
    deal_type VARCHAR(50),
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reliance_digital_deals (
    id BIGSERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    original_price DECIMAL(10, 2),
    discounted_price DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2),
    product_url TEXT NOT NULL UNIQUE,
    image_url TEXT,
    website_name VARCHAR(50) DEFAULT 'Reliance Digital',
    deal_type VARCHAR(50),
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_amazon_collected_at ON amazon_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_flipkart_collected_at ON flipkart_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_myntra_collected_at ON myntra_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_ajio_collected_at ON ajio_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_meesho_collected_at ON meesho_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_tata_cliq_collected_at ON tata_cliq_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_reliance_digital_collected_at ON reliance_digital_deals(collected_at DESC);
```

3. Click "RUN" button (or press Ctrl+Enter)

4. Verify by running:
   python test_db_tables.py

THEN TEST THE SCRAPER:
Once tables are created, test with:
   python daily_deals_main.py --run-once

That's it! 🎉
"""

print(__doc__)
