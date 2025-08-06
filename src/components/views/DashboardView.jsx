import React, { useState, useEffect } from 'react'
import { 
  TrendingUp, DollarSign, Target, Users, 
  BarChart3, Activity, Eye, Clock,
  ChevronUp, ChevronDown, RefreshCw,
  AlertCircle, CheckCircle, XCircle
} from 'lucide-react'

const DashboardView = ({ viewMode }) => {
  const [metrics, setMetrics] = useState({
    impressions: 2456789,
    clicks: 124567,
    conversions: 5234,
    spend: 45678.90,
    ctr: 5.07,
    conversionRate: 4.2,
    cpc: 0.37,
    roas: 3.24
  })
  
  const [isLoading, setIsLoading] = useState(false)
  const [selectedPeriod, setSelectedPeriod] = useState('7d')
  
  // Mock campaign data
  const campaigns = [
    { id: 1, name: 'Summer Sale 2024', status: 'active', spend: 12345, conversions: 234, roas: 3.5 },
    { id: 2, name: 'Brand Awareness', status: 'active', spend: 8976, conversions: 156, roas: 2.8 },
    { id: 3, name: 'Product Launch', status: 'paused', spend: 5432, conversions: 89, roas: 2.1 },
    { id: 4, name: 'Holiday Campaign', status: 'active', spend: 18765, conversions: 456, roas: 4.2 }
  ]

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
    return num.toFixed(0)
  }

  const formatCurrency = (num) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(num)
  }

  const refreshData = () => {
    setIsLoading(true)
    setTimeout(() => {
      // Simulate data refresh
      setMetrics(prev => ({
        ...prev,
        impressions: prev.impressions + Math.floor(Math.random() * 1000),
        clicks: prev.clicks + Math.floor(Math.random() * 100)
      }))
      setIsLoading(false)
    }, 1000)
  }

  // Metric cards data
  const metricCards = [
    {
      id: 'impressions',
      label: 'Impressions',
      value: formatNumber(metrics.impressions),
      change: '+12.5%',
      trend: 'up',
      icon: Eye,
      color: 'var(--primary)'
    },
    {
      id: 'clicks',
      label: 'Clicks',
      value: formatNumber(metrics.clicks),
      change: '+8.3%',
      trend: 'up',
      icon: Target,
      color: 'var(--secondary)'
    },
    {
      id: 'conversions',
      label: 'Conversions',
      value: formatNumber(metrics.conversions),
      change: '+15.2%',
      trend: 'up',
      icon: CheckCircle,
      color: 'var(--accent)'
    },
    {
      id: 'spend',
      label: 'Total Spend',
      value: formatCurrency(metrics.spend),
      change: '+5.1%',
      trend: 'up',
      icon: DollarSign,
      color: 'var(--warning)'
    }
  ]

  // Advanced metrics for professional/expert view
  const advancedMetrics = [
    { label: 'CTR', value: `${metrics.ctr}%`, change: '+0.3%' },
    { label: 'Conv. Rate', value: `${metrics.conversionRate}%`, change: '+0.5%' },
    { label: 'Avg. CPC', value: `$${metrics.cpc}`, change: '-0.02' },
    { label: 'ROAS', value: `${metrics.roas}x`, change: '+0.4' }
  ]

  return (
    <div className="dashboard-view">
      {/* Header */}
      <div className="view-header">
        <div className="view-title-section">
          <h1 className="view-title">Dashboard</h1>
          <p className="view-subtitle">Monitor your Google Ads performance</p>
        </div>
        
        <div className="view-actions">
          <select 
            className="period-selector"
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
          >
            <option value="1d">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          
          <button 
            className="refresh-button"
            onClick={refreshData}
            disabled={isLoading}
          >
            <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Main Metrics Grid */}
      <div className="metrics-grid">
        {metricCards.map(metric => (
          <div key={metric.id} className="metric-card">
            <div className="metric-header">
              <div 
                className="metric-icon"
                style={{ backgroundColor: `${metric.color}15`, color: metric.color }}
              >
                <metric.icon size={20} />
              </div>
              <div className={`metric-change ${metric.trend}`}>
                {metric.trend === 'up' ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                {metric.change}
              </div>
            </div>
            <div className="metric-value">{metric.value}</div>
            <div className="metric-label">{metric.label}</div>
          </div>
        ))}
      </div>

      {/* Advanced Metrics - Show in Professional and Expert modes */}
      {viewMode !== 'simple' && (
        <div className="advanced-metrics">
          <h3 className="section-title">Performance Metrics</h3>
          <div className="advanced-metrics-grid">
            {advancedMetrics.map((metric, index) => (
              <div key={index} className="advanced-metric">
                <div className="advanced-metric-label">{metric.label}</div>
                <div className="advanced-metric-value">{metric.value}</div>
                <div className="advanced-metric-change">{metric.change}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Campaign Performance Table */}
      <div className="campaigns-section">
        <div className="section-header">
          <h3 className="section-title">Campaign Performance</h3>
          <button className="link-button">View all campaigns</button>
        </div>
        
        <div className="campaigns-table">
          <table>
            <thead>
              <tr>
                <th>Campaign</th>
                <th>Status</th>
                <th>Spend</th>
                <th>Conversions</th>
                <th>ROAS</th>
                {viewMode === 'expert' && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {campaigns.map(campaign => (
                <tr key={campaign.id}>
                  <td className="campaign-name">{campaign.name}</td>
                  <td>
                    <span className={`status-badge ${campaign.status}`}>
                      {campaign.status === 'active' ? <CheckCircle size={14} /> : <XCircle size={14} />}
                      {campaign.status}
                    </span>
                  </td>
                  <td>{formatCurrency(campaign.spend)}</td>
                  <td>{campaign.conversions}</td>
                  <td className="roas-value">{campaign.roas}x</td>
                  {viewMode === 'expert' && (
                    <td>
                      <button className="action-button">Edit</button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Expert Mode - Additional Analytics */}
      {viewMode === 'expert' && (
        <div className="expert-analytics">
          <h3 className="section-title">Advanced Analytics</h3>
          <div className="analytics-grid">
            <div className="analytics-card">
              <h4>Conversion Path Analysis</h4>
              <p>Average touchpoints: 3.2</p>
              <p>Time to conversion: 2.5 days</p>
            </div>
            <div className="analytics-card">
              <h4>Budget Utilization</h4>
              <p>Daily budget: $500</p>
              <p>Utilization: 87%</p>
            </div>
            <div className="analytics-card">
              <h4>Quality Score</h4>
              <p>Average: 7.8/10</p>
              <p>Improvement areas: 3</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardView