-- Migration: Enhance Campaign Model for PostgreSQL
-- Description: Add new fields for enhanced campaign management and analytics
-- Version: 003
-- Created: 2024-07-05

-- Add new columns to existing campaigns table
ALTER TABLE campaigns 
    ADD COLUMN IF NOT EXISTS account_id UUID,
    ADD COLUMN IF NOT EXISTS google_ads_campaign_id VARCHAR(20),
    ADD COLUMN IF NOT EXISTS budget_amount DECIMAL(10,2),
    ADD COLUMN IF NOT EXISTS daily_budget DECIMAL(10,2),
    ADD COLUMN IF NOT EXISTS budget_delivery_method VARCHAR(20) DEFAULT 'standard',
    ADD COLUMN IF NOT EXISTS bidding_strategy VARCHAR(50),
    ADD COLUMN IF NOT EXISTS target_cpa DECIMAL(10,2),
    ADD COLUMN IF NOT EXISTS target_roas DECIMAL(5,2),
    ADD COLUMN IF NOT EXISTS start_date DATE,
    ADD COLUMN IF NOT EXISTS end_date DATE,
    ADD COLUMN IF NOT EXISTS tracking_template VARCHAR(500),
    ADD COLUMN IF NOT EXISTS final_url_suffix VARCHAR(200),
    ADD COLUMN IF NOT EXISTS geo_targeting JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS language_targeting JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS device_targeting JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS schedule_targeting JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS negative_keywords JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS conversion_tracking JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS labels JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS notes TEXT,
    ADD COLUMN IF NOT EXISTS approval_status VARCHAR(20) DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS approval_notes TEXT,
    ADD COLUMN IF NOT EXISTS approved_by UUID,
    ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS last_sync_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS sync_errors JSONB;

-- Update existing status values if needed
UPDATE campaigns SET status = 'draft' WHERE status IS NULL;

-- Add foreign key constraints
ALTER TABLE campaigns
    ADD CONSTRAINT fk_campaigns_account 
        FOREIGN KEY (account_id) 
        REFERENCES accounts(id) 
        ON DELETE CASCADE,
    ADD CONSTRAINT fk_campaigns_approved_by 
        FOREIGN KEY (approved_by) 
        REFERENCES users(id) 
        ON DELETE SET NULL;

-- Add check constraints
ALTER TABLE campaigns
    ADD CONSTRAINT check_budget_amount CHECK (budget_amount >= 0),
    ADD CONSTRAINT check_daily_budget CHECK (daily_budget >= 0),
    ADD CONSTRAINT check_target_cpa CHECK (target_cpa >= 0),
    ADD CONSTRAINT check_target_roas CHECK (target_roas >= 0);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_campaigns_account_id ON campaigns(account_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_google_ads_campaign_id ON campaigns(google_ads_campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_approval_status ON campaigns(approval_status);
CREATE INDEX IF NOT EXISTS idx_campaigns_approved_by ON campaigns(approved_by);
CREATE INDEX IF NOT EXISTS idx_campaigns_start_date ON campaigns(start_date);
CREATE INDEX IF NOT EXISTS idx_campaigns_end_date ON campaigns(end_date);
CREATE INDEX IF NOT EXISTS idx_campaigns_geo_targeting ON campaigns USING GIN(geo_targeting);
CREATE INDEX IF NOT EXISTS idx_campaigns_labels ON campaigns USING GIN(labels);

-- Add comments
COMMENT ON COLUMN campaigns.account_id IS 'Associated account for multi-tenant support';
COMMENT ON COLUMN campaigns.google_ads_campaign_id IS 'Google Ads campaign ID for synchronization';
COMMENT ON COLUMN campaigns.geo_targeting IS 'Geographic targeting settings as JSON array';
COMMENT ON COLUMN campaigns.conversion_tracking IS 'Conversion tracking configuration';