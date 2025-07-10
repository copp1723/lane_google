import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  Settings, 
  TrendingUp, 
  DollarSign, 
  Users, 
  Eye,
  Plus,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';

const CampaignDashboard = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [workflows, setWorkflows] = useState([]);

  useEffect(() => {
    fetchCampaigns();
    fetchWorkflows();
  }, []);

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      
      // Try to fetch real campaign data from Google Ads API and workflows
      const [campaignsResponse, workflowsResponse] = await Promise.all([
        fetch('/api/google-ads/campaigns'),
        fetch('/api/orchestrator/workflows')
      ]);
      
      let campaignData = [];
      let workflowData = [];
      
      // Get campaigns data
      if (campaignsResponse.ok) {
        const campaignsResult = await campaignsResponse.json();
        if (campaignsResult.success) {
          campaignData = campaignsResult.data.campaigns || [];
        }
      }
      
      // Get workflows data
      if (workflowsResponse.ok) {
        const workflowsResult = await workflowsResponse.json();
        if (workflowsResult.success) {
          workflowData = workflowsResult.data.workflows || [];
        }
      }
      
      // Merge campaign and workflow data
      const enrichedCampaigns = campaignData.map(campaign => {
        const workflow = workflowData.find(w => w.campaign_id === campaign.id);
        return {
          id: campaign.id,
          name: campaign.name,
          status: campaign.status,
          channel_type: campaign.advertising_channel_type || 'SEARCH',
          budget_amount: campaign.budget_amount_micros ? campaign.budget_amount_micros / 1000000 : 0,
          performance: {
            impressions: campaign.metrics?.impressions || 0,
            clicks: campaign.metrics?.clicks || 0,
            cost: campaign.metrics?.cost_micros ? campaign.metrics.cost_micros / 1000000 : 0,
            conversions: campaign.metrics?.conversions || 0
          },
          workflow_status: workflow ? workflow.current_phase : 'none',
          workflow_id: workflow ? workflow.workflow_id : null,
          workflow_progress: workflow ? workflow.progress : 0,
          created_at: campaign.created_at || new Date().toISOString()
        };
      });
      
      if (enrichedCampaigns.length > 0) {
        setCampaigns(enrichedCampaigns);
        setError(null);
      } else {
        throw new Error('No campaigns found');
      }
      
    } catch (err) {
      console.error('Error fetching campaigns:', err);
      setError(err.message);
      
      // Fallback to demo data
      setCampaigns([
        {
          id: 'camp_001',
          name: 'Fitness Equipment Q1 2024',
          status: 'ENABLED',
          channel_type: 'SEARCH',
          budget_amount: 5000,
          performance: {
            impressions: 45230,
            clicks: 2156,
            cost: 3420.50,
            conversions: 89
          },
          workflow_status: 'completed',
          workflow_id: 'wf_001',
          workflow_progress: 100,
          created_at: '2024-01-15T10:30:00Z'
        },
        {
          id: 'camp_002',
          name: 'Holiday Sale Campaign',
          status: 'PAUSED',
          channel_type: 'DISPLAY',
          budget_amount: 3000,
          performance: {
            impressions: 125600,
            clicks: 1834,
            cost: 2145.75,
            conversions: 34
          },
          workflow_status: 'in_progress',
          workflow_id: 'wf_002',
          workflow_progress: 65,
          created_at: '2024-01-10T14:20:00Z'
        },
        {
          id: 'camp_003',
          name: 'Brand Awareness Drive',
          status: 'ENABLED',
          channel_type: 'VIDEO',
          budget_amount: 8000,
          performance: {
            impressions: 89450,
            clicks: 3422,
            cost: 4567.25,
            conversions: 156
          },
          workflow_status: 'review_required',
          workflow_id: 'wf_003',
          workflow_progress: 85,
          created_at: '2024-01-05T09:15:00Z'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkflows = async () => {
    try {
      const response = await fetch('/api/orchestrator/workflows');
      if (response.ok) {
        const data = await response.json();
        setWorkflows(data.workflows || []);
      }
    } catch (err) {
      console.error('Error fetching workflows:', err);
    }
  };

  const toggleCampaignStatus = async (campaignId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'ENABLED' ? 'PAUSED' : 'ENABLED';
      
      const response = await fetch(`/api/google-ads/campaigns/${campaignId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      
      if (!response.ok) throw new Error('Failed to update campaign status');
      
      const result = await response.json();
      if (result.success) {
        // Update local state
        setCampaigns(prev => prev.map(camp =>
          camp.id === campaignId ? { ...camp, status: newStatus } : camp
        ));
        setError(null);
      } else {
        throw new Error(result.error || 'Failed to update status');
      }
    } catch (err) {
      console.error('Error updating campaign status:', err);
      setError('Failed to update campaign status');
      
      // Still update UI optimistically for demo
      setCampaigns(prev => prev.map(camp =>
        camp.id === campaignId ? { ...camp, status: currentStatus === 'ENABLED' ? 'PAUSED' : 'ENABLED' } : camp
      ));
    }
  };

  const createNewCampaign = async () => {
    try {
      // Create a new campaign workflow
      const response = await fetch('/api/orchestrator/campaigns/create-workflow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          campaign_brief: {
            name: 'New Campaign',
            type: 'search',
            business_goals: ['Generate leads'],
            target_audience: 'General audience',
            budget: 1000
          }
        })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          // Refresh campaigns list
          fetchCampaigns();
          alert(`New campaign workflow created: ${result.data.workflow_id}`);
        } else {
          throw new Error(result.error || 'Failed to create workflow');
        }
      } else {
        throw new Error('Failed to create campaign workflow');
      }
    } catch (err) {
      console.error('Error creating campaign:', err);
      // Fallback to showing integration message
      alert('Campaign creation will integrate with AI chat interface for brief generation. Use AI Chat tab to start.');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ENABLED': return '#10b981';
      case 'PAUSED': return '#f59e0b';
      case 'REMOVED': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getWorkflowStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#10b981';
      case 'in_progress': return '#f59e0b';
      case 'review_required': return '#8b5cf6';
      case 'failed': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getWorkflowIcon = (status) => {
    switch (status) {
      case 'completed': return CheckCircle;
      case 'in_progress': return Clock;
      case 'review_required': return AlertCircle;
      case 'failed': return AlertCircle;
      default: return Clock;
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const calculateCTR = (clicks, impressions) => {
    return impressions > 0 ? ((clicks / impressions) * 100).toFixed(2) : '0.00';
  };

  const calculateCPC = (cost, clicks) => {
    return clicks > 0 ? (cost / clicks).toFixed(2) : '0.00';
  };

  if (loading) {
    return (
      <div style={{
        background: 'rgba(255, 255, 255, 0.6)',
        backdropFilter: 'blur(15px)',
        WebkitBackdropFilter: 'blur(15px)',
        border: '1px solid rgba(255, 255, 255, 0.5)',
        borderRadius: '20px',
        padding: '2rem',
        textAlign: 'center'
      }}>
        <RefreshCw size={48} style={{ color: '#6366f1', animation: 'spin 1s linear infinite' }} />
        <h2 style={{ color: '#111827', marginTop: '1rem' }}>Loading Campaigns...</h2>
        <style>
          {`
            @keyframes spin {
              from { transform: rotate(0deg); }
              to { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    );
  }

  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.6)',
      backdropFilter: 'blur(15px)',
      WebkitBackdropFilter: 'blur(15px)',
      border: '1px solid rgba(255, 255, 255, 0.5)',
      borderRadius: '20px',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '1.5rem 2rem',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h2 style={{
            color: '#111827',
            fontSize: '1.5rem',
            fontWeight: '700',
            margin: '0 0 0.5rem 0'
          }}>
            Campaign Management
          </h2>
          <p style={{
            color: '#6b7280',
            fontSize: '0.875rem',
            margin: 0
          }}>
            Monitor and manage your Google Ads campaigns
          </p>
        </div>
        
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={fetchCampaigns}
            style={{
              background: 'rgba(255, 255, 255, 0.8)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
              borderRadius: '8px',
              padding: '8px 12px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              color: '#374151',
              fontSize: '0.875rem'
            }}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
          
          <button
            onClick={createNewCampaign}
            style={{
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '8px 16px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.875rem',
              fontWeight: '600'
            }}
          >
            <Plus size={16} />
            Create Campaign
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          borderBottom: '1px solid rgba(239, 68, 68, 0.2)',
          padding: '12px 24px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <AlertCircle size={16} color="#dc2626" />
          <span style={{ color: '#dc2626', fontSize: '0.875rem' }}>
            {error}
          </span>
        </div>
      )}

      {/* Campaigns List */}
      <div style={{ padding: '1rem' }}>
        {campaigns.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '3rem',
            color: '#6b7280'
          }}>
            <Settings size={48} style={{ color: '#d1d5db', marginBottom: '1rem' }} />
            <h3 style={{ margin: '0 0 0.5rem 0' }}>No Campaigns Found</h3>
            <p style={{ margin: 0 }}>Create your first campaign to get started</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {campaigns.map((campaign) => {
              const WorkflowIcon = getWorkflowIcon(campaign.workflow_status);
              
              return (
                <div
                  key={campaign.id}
                  style={{
                    background: 'rgba(255, 255, 255, 0.4)',
                    backdropFilter: 'blur(10px)',
                    WebkitBackdropFilter: 'blur(10px)',
                    borderRadius: '16px',
                    padding: '1.5rem',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 8px 25px rgba(0,0,0,0.1)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = 'none';
                  }}
                  onClick={() => setSelectedCampaign(selectedCampaign === campaign.id ? null : campaign.id)}
                >
                  {/* Campaign Header */}
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '1rem'
                  }}>
                    <div style={{ flex: 1 }}>
                      <h3 style={{
                        color: '#111827',
                        fontWeight: '600',
                        margin: '0 0 0.5rem 0',
                        fontSize: '1.125rem'
                      }}>
                        {campaign.name}
                      </h3>
                      
                      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                        <span style={{
                          background: getStatusColor(campaign.status),
                          color: 'white',
                          padding: '2px 8px',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                          fontWeight: '600'
                        }}>
                          {campaign.status}
                        </span>
                        
                        <span style={{
                          background: 'rgba(99, 102, 241, 0.1)',
                          color: '#6366f1',
                          padding: '2px 8px',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                          fontWeight: '600'
                        }}>
                          {campaign.channel_type}
                        </span>
                        
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <WorkflowIcon 
                            size={14} 
                            color={getWorkflowStatusColor(campaign.workflow_status)} 
                          />
                          <span style={{
                            color: getWorkflowStatusColor(campaign.workflow_status),
                            fontSize: '0.75rem',
                            fontWeight: '600'
                          }}>
                            {campaign.workflow_status.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleCampaignStatus(campaign.id, campaign.status);
                        }}
                        style={{
                          background: campaign.status === 'ENABLED' ? 
                            'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                          color: campaign.status === 'ENABLED' ? '#dc2626' : '#10b981',
                          border: `1px solid ${campaign.status === 'ENABLED' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
                          borderRadius: '6px',
                          padding: '6px 8px',
                          cursor: 'pointer',
                          fontSize: '0.75rem'
                        }}
                      >
                        {campaign.status === 'ENABLED' ? <Pause size={12} /> : <Play size={12} />}
                      </button>
                      
                      <button
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          background: 'rgba(99, 102, 241, 0.1)',
                          color: '#6366f1',
                          border: '1px solid rgba(99, 102, 241, 0.3)',
                          borderRadius: '6px',
                          padding: '6px 8px',
                          cursor: 'pointer'
                        }}
                      >
                        <Settings size={12} />
                      </button>
                    </div>
                  </div>

                  {/* Performance Metrics */}
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                        Budget
                      </div>
                      <div style={{ color: '#111827', fontWeight: '600' }}>
                        {formatCurrency(campaign.budget_amount)}
                      </div>
                    </div>
                    
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                        Impressions
                      </div>
                      <div style={{ color: '#111827', fontWeight: '600' }}>
                        {formatNumber(campaign.performance.impressions)}
                      </div>
                    </div>
                    
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                        Clicks
                      </div>
                      <div style={{ color: '#111827', fontWeight: '600' }}>
                        {formatNumber(campaign.performance.clicks)}
                      </div>
                    </div>
                    
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                        CTR
                      </div>
                      <div style={{ color: '#111827', fontWeight: '600' }}>
                        {calculateCTR(campaign.performance.clicks, campaign.performance.impressions)}%
                      </div>
                    </div>
                    
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                        Cost
                      </div>
                      <div style={{ color: '#111827', fontWeight: '600' }}>
                        {formatCurrency(campaign.performance.cost)}
                      </div>
                    </div>
                    
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                        Conversions
                      </div>
                      <div style={{ color: '#111827', fontWeight: '600' }}>
                        {formatNumber(campaign.performance.conversions)}
                      </div>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {selectedCampaign === campaign.id && (
                    <div style={{
                      borderTop: '1px solid rgba(255, 255, 255, 0.3)',
                      paddingTop: '1rem',
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                      gap: '1rem'
                    }}>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                          Average CPC
                        </div>
                        <div style={{ color: '#111827', fontWeight: '600' }}>
                          ${calculateCPC(campaign.performance.cost, campaign.performance.clicks)}
                        </div>
                      </div>
                      
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                          Conversion Rate
                        </div>
                        <div style={{ color: '#111827', fontWeight: '600' }}>
                          {calculateCTR(campaign.performance.conversions, campaign.performance.clicks)}%
                        </div>
                      </div>
                      
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                          Created
                        </div>
                        <div style={{ color: '#111827', fontWeight: '600' }}>
                          {new Date(campaign.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <button style={{
                          background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '6px 12px',
                          cursor: 'pointer',
                          fontSize: '0.75rem',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}>
                          <Eye size={12} />
                          View Details
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default CampaignDashboard;