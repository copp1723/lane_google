import React, { useState } from 'react'
import { 
  Plus, Search, Filter, MoreVertical, 
  Play, Pause, Trash2, Edit, Copy,
  TrendingUp, AlertTriangle, CheckCircle,
  Calendar, DollarSign, Target, BarChart3
} from 'lucide-react'

const CampaignsView = ({ viewMode }) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [selectedCampaigns, setSelectedCampaigns] = useState([])
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Mock campaigns data
  const [campaigns] = useState([
    {
      id: 1,
      name: 'Summer Sale 2024',
      status: 'active',
      type: 'Search',
      budget: 500,
      spent: 423.45,
      impressions: 45678,
      clicks: 2345,
      conversions: 156,
      ctr: 5.13,
      cpc: 0.18,
      startDate: '2024-06-01',
      endDate: '2024-08-31',
      performance: 'good'
    },
    {
      id: 2,
      name: 'Brand Awareness Campaign',
      status: 'active',
      type: 'Display',
      budget: 1000,
      spent: 876.32,
      impressions: 123456,
      clicks: 3456,
      conversions: 234,
      ctr: 2.8,
      cpc: 0.25,
      startDate: '2024-01-01',
      endDate: '2024-12-31',
      performance: 'excellent'
    },
    {
      id: 3,
      name: 'Holiday Special',
      status: 'paused',
      type: 'Shopping',
      budget: 2000,
      spent: 1543.21,
      impressions: 87654,
      clicks: 4321,
      conversions: 321,
      ctr: 4.93,
      cpc: 0.36,
      startDate: '2024-11-01',
      endDate: '2024-12-31',
      performance: 'warning'
    },
    {
      id: 4,
      name: 'Product Launch',
      status: 'draft',
      type: 'Video',
      budget: 750,
      spent: 0,
      impressions: 0,
      clicks: 0,
      conversions: 0,
      ctr: 0,
      cpc: 0,
      startDate: '2024-08-01',
      endDate: '2024-09-30',
      performance: 'none'
    }
  ])

  const filteredCampaigns = campaigns.filter(campaign => {
    const matchesSearch = campaign.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = filterStatus === 'all' || campaign.status === filterStatus
    return matchesSearch && matchesStatus
  })

  const getPerformanceIcon = (performance) => {
    switch (performance) {
      case 'excellent':
        return <TrendingUp size={16} className="text-green" />
      case 'good':
        return <CheckCircle size={16} className="text-blue" />
      case 'warning':
        return <AlertTriangle size={16} className="text-yellow" />
      default:
        return null
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'status-active'
      case 'paused':
        return 'status-paused'
      case 'draft':
        return 'status-draft'
      default:
        return ''
    }
  }

  const handleBulkAction = (action) => {
    console.log(`Performing ${action} on campaigns:`, selectedCampaigns)
    // Implement bulk actions
    setSelectedCampaigns([])
  }

  return (
    <div className="campaigns-view">
      {/* Header */}
      <div className="view-header">
        <div className="view-title-section">
          <h1 className="view-title">Campaigns</h1>
          <p className="view-subtitle">Manage and optimize your ad campaigns</p>
        </div>
        
        <button 
          className="primary-button"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus size={20} />
          Create Campaign
        </button>
      </div>

      {/* Filters and Search */}
      <div className="campaigns-controls">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search campaigns..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-controls">
          <select
            className="filter-select"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="draft">Draft</option>
          </select>

          {viewMode !== 'simple' && (
            <button className="filter-button">
              <Filter size={16} />
              More Filters
            </button>
          )}
        </div>

        {selectedCampaigns.length > 0 && (
          <div className="bulk-actions">
            <span>{selectedCampaigns.length} selected</span>
            <button onClick={() => handleBulkAction('pause')}>Pause</button>
            <button onClick={() => handleBulkAction('activate')}>Activate</button>
            <button onClick={() => handleBulkAction('delete')}>Delete</button>
          </div>
        )}
      </div>

      {/* Campaign Cards/Table based on view mode */}
      {viewMode === 'simple' ? (
        // Simple View - Card Layout
        <div className="campaigns-grid">
          {filteredCampaigns.map(campaign => (
            <div key={campaign.id} className="campaign-card">
              <div className="campaign-card-header">
                <h3>{campaign.name}</h3>
                <button className="icon-button">
                  <MoreVertical size={16} />
                </button>
              </div>
              
              <div className={`campaign-status ${getStatusColor(campaign.status)}`}>
                {campaign.status === 'active' && <Play size={14} />}
                {campaign.status === 'paused' && <Pause size={14} />}
                {campaign.status}
              </div>

              <div className="campaign-metrics">
                <div className="metric">
                  <span className="metric-label">Budget</span>
                  <span className="metric-value">${campaign.budget}/day</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Spent</span>
                  <span className="metric-value">${campaign.spent.toFixed(2)}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Conversions</span>
                  <span className="metric-value">{campaign.conversions}</span>
                </div>
              </div>

              <div className="campaign-actions">
                <button className="action-button">View Details</button>
                <button className="action-button">Edit</button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        // Professional/Expert View - Table Layout
        <div className="campaigns-table-container">
          <table className="campaigns-table">
            <thead>
              <tr>
                {viewMode === 'expert' && (
                  <th>
                    <input
                      type="checkbox"
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedCampaigns(campaigns.map(c => c.id))
                        } else {
                          setSelectedCampaigns([])
                        }
                      }}
                    />
                  </th>
                )}
                <th>Campaign</th>
                <th>Status</th>
                <th>Type</th>
                <th>Budget</th>
                <th>Spent</th>
                <th>Impressions</th>
                <th>Clicks</th>
                <th>CTR</th>
                {viewMode === 'expert' && (
                  <>
                    <th>CPC</th>
                    <th>Conversions</th>
                    <th>Performance</th>
                  </>
                )}
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredCampaigns.map(campaign => (
                <tr key={campaign.id}>
                  {viewMode === 'expert' && (
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedCampaigns.includes(campaign.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedCampaigns([...selectedCampaigns, campaign.id])
                          } else {
                            setSelectedCampaigns(selectedCampaigns.filter(id => id !== campaign.id))
                          }
                        }}
                      />
                    </td>
                  )}
                  <td className="campaign-name-cell">
                    <div className="campaign-name">
                      {campaign.name}
                      <span className="campaign-dates">
                        {campaign.startDate} - {campaign.endDate}
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className={`status-badge ${getStatusColor(campaign.status)}`}>
                      {campaign.status}
                    </span>
                  </td>
                  <td>{campaign.type}</td>
                  <td>${campaign.budget}/day</td>
                  <td>${campaign.spent.toFixed(2)}</td>
                  <td>{campaign.impressions.toLocaleString()}</td>
                  <td>{campaign.clicks.toLocaleString()}</td>
                  <td>{campaign.ctr.toFixed(2)}%</td>
                  {viewMode === 'expert' && (
                    <>
                      <td>${campaign.cpc.toFixed(2)}</td>
                      <td>{campaign.conversions}</td>
                      <td>
                        <div className="performance-indicator">
                          {getPerformanceIcon(campaign.performance)}
                        </div>
                      </td>
                    </>
                  )}
                  <td>
                    <div className="table-actions">
                      <button className="icon-button" title="Edit">
                        <Edit size={16} />
                      </button>
                      <button className="icon-button" title="Duplicate">
                        <Copy size={16} />
                      </button>
                      {viewMode === 'expert' && (
                        <button className="icon-button" title="Delete">
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Expert Mode - Campaign Insights */}
      {viewMode === 'expert' && (
        <div className="campaign-insights">
          <h3 className="section-title">Campaign Insights</h3>
          <div className="insights-grid">
            <div className="insight-card">
              <BarChart3 size={24} className="insight-icon" />
              <h4>Performance Trends</h4>
              <p>3 campaigns showing improvement</p>
              <p>1 campaign needs attention</p>
            </div>
            <div className="insight-card">
              <DollarSign size={24} className="insight-icon" />
              <h4>Budget Optimization</h4>
              <p>$234 daily budget unused</p>
              <p>Reallocate to top performers</p>
            </div>
            <div className="insight-card">
              <Target size={24} className="insight-icon" />
              <h4>Targeting Opportunities</h4>
              <p>5 new keywords suggested</p>
              <p>2 negative keywords recommended</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CampaignsView