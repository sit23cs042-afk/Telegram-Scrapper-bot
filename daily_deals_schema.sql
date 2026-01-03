-- Daily Deals Database Schema for Supabase
-- Run this SQL in your Supabase SQL Editor to create the required tables

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
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_amazon_prices CHECK (discounted_price >= 0 AND original_price >= discounted_price)
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
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_flipkart_prices CHECK (discounted_price >= 0 AND original_price >= discounted_price)
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
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_myntra_prices CHECK (discounted_price >= 0 AND original_price >= discounted_price)
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
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_ajio_prices CHECK (discounted_price >= 0 AND original_price >= discounted_price)
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
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_meesho_prices CHECK (discounted_price >= 0 AND original_price >= discounted_price)
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
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_tata_cliq_prices CHECK (discounted_price >= 0 AND original_price >= discounted_price)
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
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_reliance_digital_prices CHECK (discounted_price >= 0 AND original_price >= discounted_price)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_amazon_collected_at ON amazon_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_amazon_category ON amazon_deals(category);
CREATE INDEX IF NOT EXISTS idx_amazon_discount ON amazon_deals(discount_percentage DESC);

CREATE INDEX IF NOT EXISTS idx_flipkart_collected_at ON flipkart_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_flipkart_category ON flipkart_deals(category);
CREATE INDEX IF NOT EXISTS idx_flipkart_discount ON flipkart_deals(discount_percentage DESC);

CREATE INDEX IF NOT EXISTS idx_myntra_collected_at ON myntra_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_myntra_category ON myntra_deals(category);
CREATE INDEX IF NOT EXISTS idx_myntra_discount ON myntra_deals(discount_percentage DESC);

CREATE INDEX IF NOT EXISTS idx_ajio_collected_at ON ajio_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_ajio_category ON ajio_deals(category);
CREATE INDEX IF NOT EXISTS idx_ajio_discount ON ajio_deals(discount_percentage DESC);

CREATE INDEX IF NOT EXISTS idx_meesho_collected_at ON meesho_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_meesho_category ON meesho_deals(category);
CREATE INDEX IF NOT EXISTS idx_meesho_discount ON meesho_deals(discount_percentage DESC);

CREATE INDEX IF NOT EXISTS idx_tata_cliq_collected_at ON tata_cliq_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_tata_cliq_category ON tata_cliq_deals(category);
CREATE INDEX IF NOT EXISTS idx_tata_cliq_discount ON tata_cliq_deals(discount_percentage DESC);

CREATE INDEX IF NOT EXISTS idx_reliance_digital_collected_at ON reliance_digital_deals(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_reliance_digital_category ON reliance_digital_deals(category);
CREATE INDEX IF NOT EXISTS idx_reliance_digital_discount ON reliance_digital_deals(discount_percentage DESC);

-- Enable Row Level Security (RLS) if needed
-- Uncomment if you want to enable RLS
-- ALTER TABLE amazon_deals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE flipkart_deals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE myntra_deals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ajio_deals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE meesho_deals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE tata_cliq_deals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE reliance_digital_deals ENABLE ROW LEVEL SECURITY;
