-- Personal Finance Manager Database Schema
-- Flat tag system with multi-user support

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USER MANAGEMENT (Multi-user ready)
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);

-- Create default user for MVP (single-user mode)
INSERT INTO users (email, password_hash, full_name)
VALUES ('default@finance.local', 'no_auth_in_mvp', 'Default User');

-- ============================================
-- IMPORT TRACKING
-- ============================================

CREATE TABLE import_batches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(500) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    account_number VARCHAR(50),
    account_type VARCHAR(100),
    currency VARCHAR(3) DEFAULT 'PLN',
    period_start DATE,
    period_end DATE,
    raw_content TEXT,
    transactions_imported INTEGER DEFAULT 0,
    duplicates_skipped INTEGER DEFAULT 0,
    import_status VARCHAR(50) DEFAULT 'processing',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, file_hash)
);

CREATE INDEX idx_import_batches_user ON import_batches(user_id);
CREATE INDEX idx_import_batches_status ON import_batches(import_status);
CREATE INDEX idx_import_batches_created ON import_batches(created_at DESC);

-- ============================================
-- MERCHANTS (Normalized merchant database)
-- ============================================

CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    normalized_name VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    logo_url VARCHAR(500),
    website VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_merchants_normalized ON merchants(normalized_name);

-- Merchant patterns for matching raw transaction titles
CREATE TABLE merchant_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    pattern VARCHAR(500) NOT NULL,
    pattern_type VARCHAR(50) DEFAULT 'substring',
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_merchant_patterns_merchant ON merchant_patterns(merchant_id);
CREATE INDEX idx_merchant_patterns_priority ON merchant_patterns(priority DESC);

-- ============================================
-- TRANSACTIONS (Core financial data)
-- ============================================

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    import_batch_id UUID REFERENCES import_batches(id) ON DELETE SET NULL,

    -- Transaction identity (for duplicate detection)
    transaction_hash VARCHAR(64) UNIQUE NOT NULL,

    -- Core transaction data
    booking_date DATE NOT NULL,
    transaction_date DATE NOT NULL,
    operation_type VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    sender_recipient VARCHAR(500),
    account_number VARCHAR(50),
    amount NUMERIC(15, 2) NOT NULL,
    balance_after NUMERIC(15, 2),
    currency VARCHAR(3) DEFAULT 'PLN',

    -- Enrichment fields
    merchant_id UUID REFERENCES merchants(id) ON DELETE SET NULL,
    normalized_merchant_name VARCHAR(255),
    merchant_confidence NUMERIC(3, 2),

    -- Metadata
    notes TEXT,
    is_hidden BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_transactions_booking_date ON transactions(booking_date DESC);
CREATE INDEX idx_transactions_merchant ON transactions(merchant_id);
CREATE INDEX idx_transactions_amount ON transactions(amount);
CREATE INDEX idx_transactions_user_date ON transactions(user_id, booking_date DESC);
CREATE INDEX idx_transactions_hash ON transactions(transaction_hash);

-- ============================================
-- FLAT TAGGING SYSTEM (Core feature)
-- ============================================

CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    color VARCHAR(7),
    icon VARCHAR(50),
    description TEXT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, name)
);

CREATE INDEX idx_tags_user ON tags(user_id);
CREATE INDEX idx_tags_usage ON tags(usage_count DESC);
CREATE INDEX idx_tags_name ON tags(name);

-- Tag synonyms/aliases (for NLP-based detection)
CREATE TABLE tag_synonyms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    canonical_tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    synonym VARCHAR(100) NOT NULL,
    source VARCHAR(50) DEFAULT 'manual',
    confidence NUMERIC(3, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, synonym)
);

CREATE INDEX idx_tag_synonyms_canonical ON tag_synonyms(canonical_tag_id);
CREATE INDEX idx_tag_synonyms_user ON tag_synonyms(user_id);
CREATE INDEX idx_tag_synonyms_active ON tag_synonyms(is_active) WHERE is_active = TRUE;

-- Transaction-Tag many-to-many relationship
CREATE TABLE transaction_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    source VARCHAR(50) DEFAULT 'manual',
    confidence NUMERIC(3, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(transaction_id, tag_id)
);

CREATE INDEX idx_transaction_tags_transaction ON transaction_tags(transaction_id);
CREATE INDEX idx_transaction_tags_tag ON transaction_tags(tag_id);
CREATE INDEX idx_transaction_tags_source ON transaction_tags(source);

-- ============================================
-- AUTO-TAGGING RULES
-- ============================================

CREATE TABLE tagging_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Rule conditions (JSON for flexibility)
    conditions JSONB NOT NULL,

    -- Tags to apply
    tag_ids UUID[] NOT NULL,

    -- Rule metadata
    priority INTEGER DEFAULT 0,
    confidence NUMERIC(3, 2) DEFAULT 0.90,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tagging_rules_user ON tagging_rules(user_id);
CREATE INDEX idx_tagging_rules_active ON tagging_rules(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_tagging_rules_priority ON tagging_rules(priority DESC);

-- Rule application history (audit trail)
CREATE TABLE tagging_rule_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_id UUID NOT NULL REFERENCES tagging_rules(id) ON DELETE CASCADE,
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_rule_applications_transaction ON tagging_rule_applications(transaction_id);
CREATE INDEX idx_rule_applications_rule ON tagging_rule_applications(rule_id);

-- ============================================
-- MERCHANT DEFAULT TAGS (Common taxonomy)
-- ============================================

CREATE TABLE merchant_default_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    tag_name VARCHAR(100) NOT NULL,
    confidence NUMERIC(3, 2) DEFAULT 0.85,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(merchant_id, tag_name)
);

CREATE INDEX idx_merchant_default_tags_merchant ON merchant_default_tags(merchant_id);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Update tag usage count
CREATE OR REPLACE FUNCTION update_tag_usage_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE tags SET usage_count = usage_count + 1 WHERE id = NEW.tag_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE tags SET usage_count = usage_count - 1 WHERE id = OLD.tag_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_tag_usage
AFTER INSERT OR DELETE ON transaction_tags
FOR EACH ROW EXECUTE FUNCTION update_tag_usage_count();

-- Update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_merchants_updated_at BEFORE UPDATE ON merchants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tags_updated_at BEFORE UPDATE ON tags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tagging_rules_updated_at BEFORE UPDATE ON tagging_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================

COMMENT ON TABLE transactions IS 'Core transaction data from bank statements';
COMMENT ON TABLE tags IS 'Flat tag system - no hierarchies, meaning emerges from combinations';
COMMENT ON TABLE transaction_tags IS 'Many-to-many: transactions can have multiple tags';
COMMENT ON TABLE tag_synonyms IS 'NLP-detected synonyms for tag consolidation';
COMMENT ON TABLE merchant_patterns IS 'Patterns for normalizing raw merchant names';
COMMENT ON TABLE tagging_rules IS 'User-defined auto-tagging rules with JSONB conditions';

COMMENT ON COLUMN transactions.transaction_hash IS 'SHA256 hash for duplicate detection';
COMMENT ON COLUMN transactions.normalized_merchant_name IS 'Clean merchant name extracted from title';
COMMENT ON COLUMN transaction_tags.source IS 'manual, auto_rule, auto_merchant, auto_nlp';
COMMENT ON COLUMN tag_synonyms.confidence IS 'NLP similarity score 0.00-1.00';
COMMENT ON COLUMN merchant_patterns.pattern_type IS 'substring, regex, exact';
