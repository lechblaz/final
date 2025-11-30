-- Migration 002: Add merchant details and stores table
-- Phase 2: Merchant Normalization

-- Add new columns to transactions table for detailed merchant info
ALTER TABLE transactions
    ADD COLUMN store_identifier VARCHAR(100),
    ADD COLUMN location_extracted VARCHAR(255),
    ADD COLUMN raw_merchant_text TEXT,
    ADD COLUMN store_id UUID;

-- Create stores table for precise location data
CREATE TABLE stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    store_identifier VARCHAR(100) NOT NULL,
    store_name VARCHAR(255),
    address TEXT,
    city VARCHAR(255),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Poland',
    latitude NUMERIC(10, 8),
    longitude NUMERIC(11, 8),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(merchant_id, store_identifier)
);

-- Add foreign key from transactions to stores
ALTER TABLE transactions
    ADD CONSTRAINT fk_transactions_store
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE SET NULL;

-- Create indexes for performance
CREATE INDEX idx_stores_merchant ON stores(merchant_id);
CREATE INDEX idx_stores_identifier ON stores(store_identifier);
CREATE INDEX idx_stores_city ON stores(city);
CREATE INDEX idx_transactions_store ON transactions(store_id);
CREATE INDEX idx_transactions_merchant_name ON transactions(normalized_merchant_name);
CREATE INDEX idx_transactions_location ON transactions(location_extracted);

-- Create trigger to update stores.updated_at
CREATE OR REPLACE FUNCTION update_stores_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_stores_updated_at
    BEFORE UPDATE ON stores
    FOR EACH ROW
    EXECUTE FUNCTION update_stores_updated_at();

-- Populate raw_merchant_text from existing title data
UPDATE transactions
SET raw_merchant_text = title
WHERE raw_merchant_text IS NULL;
