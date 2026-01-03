"""
Create database tables using raw SQL queries
This uses Supabase's PostgREST API to execute raw SQL
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Individual table creation queries
tables = {
    'amazon_deals': """
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
    """,
    'flipkart_deals': """
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
    """,
    'myntra_deals': """
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
    """,
    'ajio_deals': """
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
    """,
    'meesho_deals': """
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
    """,
    'tata_cliq_deals': """
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
    """,
    'reliance_digital_deals': """
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
    """
}

print("\n" + "="*70)
print("  DATABASE SETUP - Manual Instructions")
print("="*70)
print("\nTo create the required tables, please:")
print("\n1. Go to: https://supabase.com/dashboard/project/sspufleiikzsazouzkot")
print("2. Click on 'SQL Editor' in the left sidebar")
print("3. Click 'New Query' button")
print("4. Copy and paste the SQL from: daily_deals_schema.sql")
print("5. Click 'RUN' (or press Ctrl+Enter)")
print("\nAlternatively, copy this SQL and run it:\n")
print("="*70)

for table_name, sql in tables.items():
    print(f"\n-- {table_name.upper()} --")
    print(sql.strip())

print("\n" + "="*70)
print("\n✓ After running the SQL, test with:")
print("  python daily_deals_main.py --test-db")
print("\n" + "="*70 + "\n")
