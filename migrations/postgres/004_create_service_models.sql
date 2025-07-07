-- Migration: Create Service Models for PostgreSQL
-- Description: Add tables for budget pacing, analytics, and approval workflow
-- Version: 004
-- Created: 2024-07-05

-- Create custom types
CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE alert_status AS ENUM ('active', 'resolved', 'dismissed');
CREATE TYPE period_type AS ENUM ('hourly', 'daily', 'weekly', 'monthly');
CREATE TYPE approval_status AS ENUM ('pending', 'approved', 'rejected', 'expired');
CREATE TYPE priority_level AS ENUM ('low', 'medium', 'high', 'urgent');

-- Create budget_alerts table
CREATE TABLE budget_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL,
    account_id UUID NOT NULL,
    
    -- Alert details
    alert_type VARCHAR(50) NOT NULL,
    severity alert_severity DEFAULT 'medium',
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    
    -- Metrics
    current_spend DECIMAL(10,2),
    budget_amount DECIMAL(10,2),
    pace_percentage DECIMAL(5,2),
    recommended_action VARCHAR(200),
    
    -- Status
    status alert_status DEFAULT 'active',
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_budget_alerts_campaign
        FOREIGN KEY (campaign_id) 
        REFERENCES campaigns(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_budget_alerts_resolved_by
        FOREIGN KEY (resolved_by) 
        REFERENCES users(id) 
        ON DELETE SET NULL
);

-- Create analytics_snapshots table
CREATE TABLE analytics_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL,
    account_id UUID NOT NULL,
    
    -- Time period
    snapshot_date DATE NOT NULL,
    period_type period_type DEFAULT 'daily',
    
    -- Core metrics
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    cost DECIMAL(10,2) DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    conversion_value DECIMAL(10,2) DEFAULT 0,
    
    -- Calculated metrics
    ctr DECIMAL(5,4),
    cpc DECIMAL(10,2),
    cpm DECIMAL(10,2),
    conversion_rate DECIMAL(5,4),
    cost_per_conversion DECIMAL(10,2),
    roas DECIMAL(5,2),
    
    -- Additional data
    search_impression_share DECIMAL(5,4),
    search_budget_lost_impression_share DECIMAL(5,4),
    search_rank_lost_impression_share DECIMAL(5,4),
    quality_score DECIMAL(3,1),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_analytics_snapshots_campaign
        FOREIGN KEY (campaign_id) 
        REFERENCES campaigns(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT unique_analytics_snapshot
        UNIQUE(campaign_id, snapshot_date, period_type)
);

-- Create approval_requests table
CREATE TABLE approval_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Request details
    request_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    
    -- Related entities
    campaign_id UUID,
    account_id UUID NOT NULL,
    requester_id UUID NOT NULL,
    
    -- Request data
    request_data JSONB NOT NULL,
    current_data JSONB,
    
    -- Approval workflow
    status approval_status DEFAULT 'pending',
    priority priority_level DEFAULT 'medium',
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    
    -- Auto-approval settings
    auto_approved BOOLEAN DEFAULT FALSE,
    auto_approval_reason VARCHAR(200),
    
    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_approval_requests_campaign
        FOREIGN KEY (campaign_id) 
        REFERENCES campaigns(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_approval_requests_requester
        FOREIGN KEY (requester_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_approval_requests_approved_by
        FOREIGN KEY (approved_by) 
        REFERENCES users(id) 
        ON DELETE SET NULL
);

-- Create indexes for performance
CREATE INDEX idx_budget_alerts_campaign_id ON budget_alerts(campaign_id);
CREATE INDEX idx_budget_alerts_account_id ON budget_alerts(account_id);
CREATE INDEX idx_budget_alerts_status ON budget_alerts(status);
CREATE INDEX idx_budget_alerts_severity ON budget_alerts(severity);
CREATE INDEX idx_budget_alerts_created_at ON budget_alerts(created_at);

CREATE INDEX idx_analytics_snapshots_campaign_id ON analytics_snapshots(campaign_id);
CREATE INDEX idx_analytics_snapshots_account_id ON analytics_snapshots(account_id);
CREATE INDEX idx_analytics_snapshots_snapshot_date ON analytics_snapshots(snapshot_date);
CREATE INDEX idx_analytics_snapshots_period_type ON analytics_snapshots(period_type);
CREATE INDEX idx_analytics_snapshots_date_campaign ON analytics_snapshots(snapshot_date, campaign_id);

CREATE INDEX idx_approval_requests_campaign_id ON approval_requests(campaign_id);
CREATE INDEX idx_approval_requests_account_id ON approval_requests(account_id);
CREATE INDEX idx_approval_requests_requester_id ON approval_requests(requester_id);
CREATE INDEX idx_approval_requests_status ON approval_requests(status);
CREATE INDEX idx_approval_requests_priority ON approval_requests(priority);
CREATE INDEX idx_approval_requests_created_at ON approval_requests(created_at);
CREATE INDEX idx_approval_requests_expires_at ON approval_requests(expires_at);

-- Create triggers for updated_at
CREATE TRIGGER update_budget_alerts_updated_at BEFORE UPDATE ON budget_alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analytics_snapshots_updated_at BEFORE UPDATE ON analytics_snapshots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_approval_requests_updated_at BEFORE UPDATE ON approval_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE budget_alerts IS 'Budget pacing alerts for campaigns';
COMMENT ON TABLE analytics_snapshots IS 'Historical performance metrics for campaigns';
COMMENT ON TABLE approval_requests IS 'Workflow for approving campaign changes';
COMMENT ON COLUMN analytics_snapshots.roas IS 'Return on Ad Spend (conversion_value / cost)';
COMMENT ON COLUMN approval_requests.request_data IS 'JSON data for the requested changes';
COMMENT ON COLUMN approval_requests.current_data IS 'JSON data for the current state before changes';