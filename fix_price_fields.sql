-- Fix price field overflow errors
-- Increase precision from NUMERIC(5,2) to NUMERIC(10,2) to handle higher prices
-- This allows prices up to 99,999,999.99 instead of 999.99

ALTER TABLE amazon_deals 
    ALTER COLUMN original_price TYPE NUMERIC(10,2),
    ALTER COLUMN discounted_price TYPE NUMERIC(10,2);

ALTER TABLE flipkart_deals 
    ALTER COLUMN original_price TYPE NUMERIC(10,2),
    ALTER COLUMN discounted_price TYPE NUMERIC(10,2);

ALTER TABLE myntra_deals 
    ALTER COLUMN original_price TYPE NUMERIC(10,2),
    ALTER COLUMN discounted_price TYPE NUMERIC(10,2);

ALTER TABLE ajio_deals 
    ALTER COLUMN original_price TYPE NUMERIC(10,2),
    ALTER COLUMN discounted_price TYPE NUMERIC(10,2);

ALTER TABLE meesho_deals 
    ALTER COLUMN original_price TYPE NUMERIC(10,2),
    ALTER COLUMN discounted_price TYPE NUMERIC(10,2);

ALTER TABLE tata_cliq_deals 
    ALTER COLUMN original_price TYPE NUMERIC(10,2),
    ALTER COLUMN discounted_price TYPE NUMERIC(10,2);

ALTER TABLE reliance_digital_deals 
    ALTER COLUMN original_price TYPE NUMERIC(10,2),
    ALTER COLUMN discounted_price TYPE NUMERIC(10,2);
