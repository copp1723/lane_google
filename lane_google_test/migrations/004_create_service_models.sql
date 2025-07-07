-- Migration: Create Service Models
-- Description: Add tables for budget pacing, analytics, and approval workflow
-- Version: 004
-- Created: 2024-07-05

-- Create budget_alerts table
CREATE TABLE budget_alerts (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    campaign_id VARCHAR(36) NOT NULL,
    account_id VARCHAR(36) NOT NULL,
    
    -- Alert details
    alert_type VARCHAR(50) NOT NULL, -- 'budget_pace', 'budget_exhausted', 'overspend', etc.
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    
    -- Metrics
    current_spend DECIMAL(10,2),
    budget_amount DECIMAL(10,2),
    pace_percentage DECIMAL(5,2),
    recommended_action VARCHAR(200),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'dismissed')),
    resolved_at DATETIME,
    resolved_by VARCHAR(36),
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Create analytics_snapshots table
CREATE TABLE analytics_snapshots (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    campaign_id VARCHAR(36) NOT NULL,
    account_id VARCHAR(36) NOT NULL,
    
    -- Time period
    snapshot_date DATE NOT NULL,
    period_type VARCHAR(20) DEFAULT 'daily' CHECK (period_type IN ('hourly', 'daily', 'weekly', 'monthly')),
    
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    UNIQUE(campaign_id, snapshot_date, period_type)
);

-- Create approval_requests table
CREATE TABLE approval_requests (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    
    -- Request details
    request_type VARCHAR(50) NOT NULL, -- 'campaign_launch', 'budget_change', 'bid_change', etc.
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    
    -- Related entities
    campaign_id VARCHAR(36),
    account_id VARCHAR(36) NOT NULL,
    requester_id VARCHAR(36) NOT NULL,
    
    -- Request data
    request_data TEXT NOT NULL, -- JSON string with change details
    current_data TEXT, -- JSON string with current state
    
    -- Approval workflow
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'expired')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    approved_by VARCHAR(36),
    approved_at DATETIME,
    rejection_reason TEXT,
    
    -- Auto-approval settings
    auto_approved BOOLEAN DEFAULT FALSE,
    auto_approval_reason VARCHAR(200),
    
    -- Expiration
    expires_at DATETIME,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
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

CREATE INDEX idx_approval_requests_campaign_id ON approval_requests(campaign_id);
CREATE INDEX idx_approval_requests_account_id ON approval_requests(account_id);
CREATE INDEX idx_approval_requests_requester_id ON approval_requests(requester_id);
CREATE INDEX idx_approval_requests_status ON approval_requests(status);
CREATE INDEX idx_approval_requests_priority ON approval_requests(priority);
CREATE INDEX idx_approval_requests_created_at ON approval_requests(created_at);

-- Create triggers for updated_at
CREATE TRIGGER budget_alerts_updated_at 
    AFTER UPDATE ON budget_alerts
    BEGIN
        UPDATE budget_alerts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER analytics_snapshots_updated_at 
    AFTER UPDATE ON analytics_snapshots
    BEGIN
        UPDATE analytics_snapshots SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER approval_requests_updated_at 
    AFTER UPDATE ON approval_requests
    BEGIN
        UPDATE approval_requests SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;