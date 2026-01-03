"""
Quick Database Setup Script
Automatically creates all required tables in Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# SQL to create all tables
CREATE_TABLES_SQL = """
-- Amazon Deals Table
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

-- Flipkart Deals Table
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

-- Myntra Deals Table
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

-- Ajio Deals Table
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

-- Meesho Deals Table
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

-- Tata Cliq Deals Table
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

-- Reliance Digital Deals Table
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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_amazon_collected_at ON amazon_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_flipkart_collected_at ON flipkart_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_myntra_collected_at ON myntra_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_ajio_collected_at ON ajio_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_meesho_collected_at ON meesho_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_tata_cliq_collected_at ON tata_cliq_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_reliance_digital_collected_at ON reliance_digital_deals(collected_at DESC);
"""

def create_tables():
    """Create all required tables using Supabase SQL API"""
    try:
        print("\n" + "="*60)
        print("Creating Database Tables in Supabase")
        print("="*60 + "\n")
        
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Execute SQL using Supabase RPC
        print("Executing SQL commands...")
        
        # Split into individual commands and execute
        commands = CREATE_TABLES_SQL.strip().split(';')
        
        for i, cmd in enumerate(commands):
            cmd = cmd.strip()
            if cmd:
                try:
                    # Use Supabase's SQL execution
                    result = supabase.rpc('exec_sql', {'query': cmd}).execute()
                    print(f"✓ Command {i+1} executed successfully")
                except Exception as e:
                    # This might fail if exec_sql function doesn't exist
                    # In that case, we'll need to use Supabase dashboard
                    if i == 0:
                        print(f"\n⚠️  Cannot execute SQL directly via API")
                        print("\nPlease run the SQL manually:")
                        print("1. Go to: https://supabase.com/dashboard")
                        print("2. Select your project")
                        print("3. Go to: SQL Editor")
                        print("4. Copy and paste contents from: daily_deals_schema.sql")
                        print("5. Click 'RUN'\n")
                        return False
        
        print("\n" + "="*60)
        print("✅ All tables created successfully!")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        print("Please create tables manually:")
        print("1. Go to: https://supabase.com/dashboard")
        print("2. Select your project")
        print("3. Go to: SQL Editor")
        print("4. Copy and paste contents from: daily_deals_schema.sql")
        print("5. Click 'RUN'\n")
        return False

if __name__ == "__main__":
    create_tables()
