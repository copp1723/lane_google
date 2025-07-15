import React, { useState, useEffect } from 'react'
import { BarChart3, Users, MessageCircle, TrendingUp, Settings, Zap, DollarSign, AlertTriangle, Workflow, FolderOpen, Target } from 'lucide-react'
import EnhancedChatInterface from './components/chat/EnhancedChatInterface'
import EnterpriseAIChat from './components/chat/EnterpriseAIChat'
import CampaignDashboard from './components/campaigns/CampaignDashboard'
import EnhancedCampaignDashboard from './components/campaigns/EnhancedCampaignDashboard'
import ApprovalWorkflow from './components/workflows/ApprovalWorkflow'
import KeywordResearch from './components/keywords/KeywordResearch'
import EnhancedKeywordResearch from './components/keywords/EnhancedKeywordResearch'
import { API_ENDPOINTS, DEFAULTS, getAuthHeaders } from './config/environment'

const App = () => {
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('Dashboard')
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(null)
  const [dashboardData, setDashboardData] = useState({
    analytics: null,
    budgetPacing: null,
    performance: null,
    monitoring: null
  })

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const customerId = DEFAULTS.CUSTOMER_ID
      
      // Get authentication headers
      const authHeaders = getAuthHeaders()
      const requestOptions = {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders
        }
      }
      
      // Fetch data from all dashboard APIs
      const [analyticsRes, budgetRes, performanceRes, monitoringRes] = await Promise.all([
        fetch(API_ENDPOINTS.ANALYTICS_DASHBOARD(customerId), requestOptions),
        fetch(API_ENDPOINTS.BUDGET_PACING(customerId), requestOptions),
        fetch(API_ENDPOINTS.PERFORMANCE_SUMMARY(customerId), requestOptions),
        fetch(API_ENDPOINTS.MONITORING_STATUS(customerId), requestOptions)
      ])

      const analytics = await analyticsRes.json()
      const budgetPacing = await budgetRes.json()
      const performance = await performanceRes.json()
      const monitoring = await monitoringRes.json()

      setDashboardData({
        analytics: analytics.data,
        budgetPacing: budgetPacing.data,
        performance: performance.data,
        monitoring: monitoring.data
      })

      // Use budget pacing campaigns for the main display
      if (budgetPacing.success && budgetPacing.data.campaigns) {
        setCampaigns(budgetPacing.data.campaigns.map(camp => ({
          id: camp.id,
          name: camp.name,
          status: camp.status === 'healthy' ? 'Active' : camp.status === 'warning' ? 'Warning' : 'Critical',
          impressions: `${(Math.random() * 3 + 1).toFixed(1)}M`,
          clicks: `${Math.floor(Math.random() * 100 + 50)}K`,
          conversions: `${(Math.random() * 5 + 2).toFixed(1)}K`
        })))
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      // Fallback to demo data if backend is not available
      setCampaigns([
        { id: 1, name: 'Summer Sale 2024', status: 'Active', impressions: '2.4M', clicks: '124K', conversions: '5.2K' },
        { id: 2, name: 'Holiday Promotion', status: 'Warning', impressions: '1.8M', clicks: '98K', conversions: '3.7K' },
        { id: 3, name: 'Product Launch', status: 'Active', impressions: '3.1M', clicks: '156K', conversions: '6.8K' }
      ])
    } finally {
      setLoading(false)
    }
  }

  const navItems = [
    { icon: BarChart3, label: 'Dashboard' },
    { icon: Zap, label: 'Campaigns' },
    { icon: FolderOpen, label: 'Campaign Management' },
    { icon: Settings, label: 'AI Campaign Intelligence' },
    { icon: Workflow, label: 'Workflows' },
    { icon: Target, label: 'Keyword Research' },
    { icon: Users, label: 'Accounts' },
    { icon: MessageCircle, label: 'AI Chat' },
    { icon: TrendingUp, label: 'Analytics' },
    { icon: DollarSign, label: 'Budget Pacing' },
    { icon: TrendingUp, label: 'Performance' },
    { icon: AlertTriangle, label: 'Monitoring' }
  ]

  const getDisplayData = () => {
    const data = dashboardData.analytics
    if (!data) return { impressions: '2.4M', clicks: '124K', conversions: '5.2K' }
    
    return {
      impressions: `${(data.overview.impressions / 1000000).toFixed(1)}M`,
      clicks: `${Math.floor(data.overview.clicks / 1000)}K`,
      conversions: `${(data.overview.conversions / 1000).toFixed(1)}K`
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #e0e7ff 0%, #f1f5f9 50%, #fdf2f8 100%)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Floating Orbs */}
      <div style={{
        position: 'fixed',
        top: '10%',
        left: '10%',
        width: '300px',
        height: '300px',
        background: 'radial-gradient(circle, rgba(99,102,241,0.3), rgba(139,92,246,0.3))',
        borderRadius: '50%',
        filter: 'blur(80px)',
        animation: 'float 8s ease-in-out infinite',
        zIndex: 1
      }} />
      <div style={{
        position: 'fixed',
        bottom: '10%',
        right: '10%',
        width: '400px',
        height: '400px',
        background: 'radial-gradient(circle, rgba(34,197,94,0.2), rgba(59,130,246,0.2))',
        borderRadius: '50%',
        filter: 'blur(100px)',
        animation: 'float 12s ease-in-out infinite reverse',
        zIndex: 1
      }} />
      <div style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        width: '250px',
        height: '250px',
        background: 'radial-gradient(circle, rgba(168,85,247,0.25), rgba(236,72,153,0.25))',
        borderRadius: '50%',
        filter: 'blur(60px)',
        animation: 'float 10s ease-in-out infinite',
        transform: 'translate(-50%, -50%)',
        zIndex: 1
      }} />

      {/* Main Content */}
      <div style={{ position: 'relative', zIndex: 10 }}>
        {/* Header */}
        <header style={{
          background: 'rgba(255, 255, 255, 0.4)',
          backdropFilter: 'blur(30px)',
          WebkitBackdropFilter: 'blur(30px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
          padding: '1rem 2rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                borderRadius: '12px',
                padding: '8px',
                color: 'white'
              }}>
                <Zap size={24} />
              </div>
              <h1 style={{
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontSize: '1.5rem',
                fontWeight: 'bold',
                margin: 0
              }}>
                Lane MCP
              </h1>
            </div>
            <div style={{
              background: 'rgba(16, 185, 129, 0.2)',
              borderRadius: '20px',
              padding: '6px 12px',
              color: '#10b981',
              fontSize: '0.875rem',
              fontWeight: '600'
            }}>
              System Online
            </div>
          </div>
        </header>

        {/* Navigation */}
        <nav style={{
          background: 'rgba(255, 255, 255, 0.3)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderRadius: '25px',
          margin: '1rem 2rem',
          padding: '12px',
          display: 'flex',
          gap: '8px'
        }}>
          {navItems.map((item, index) => (
            <button
              key={index}
              onClick={() => setActiveTab(item.label)}
              style={{
                background: activeTab === item.label ? 'rgba(255, 255, 255, 0.95)' : 'rgba(255, 255, 255, 0.1)',
                color: activeTab === item.label ? '#1f2937' : '#374151',
                border: 'none',
                borderRadius: '18px',
                padding: '12px 20px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '0.875rem',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                backdropFilter: activeTab === item.label ? 'blur(10px)' : 'none',
                transform: activeTab === item.label ? 'scale(1.05)' : 'scale(1)'
              }}
            >
              <item.icon size={16} />
              {item.label}
            </button>
          ))}
        </nav>

        {/* Main Content */}
        <main style={{ padding: '0 2rem 2rem' }}>
          {activeTab === 'AI Chat' && <EnterpriseAIChat />}
          
          {activeTab === 'Dashboard' && (
            <>
              {/* Stats Cards */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '1.5rem',
                marginBottom: '2rem'
              }}>
                {(() => {
                  const displayData = getDisplayData()
                  return [
                    { title: 'Impressions', value: displayData.impressions, change: '+12%', icon: BarChart3 },
                    { title: 'Clicks', value: displayData.clicks, change: '+8%', icon: TrendingUp },
                    { title: 'Conversions', value: displayData.conversions, change: '+15%', icon: Users }
                  ]
                })().map((stat, index) => (
                  <div
                    key={index}
                    style={{
                      background: 'rgba(255, 255, 255, 0.6)',
                      backdropFilter: 'blur(15px)',
                      WebkitBackdropFilter: 'blur(15px)',
                      border: '1px solid rgba(255, 255, 255, 0.5)',
                      borderRadius: '20px',
                      padding: '2rem',
                      transition: 'all 0.4s cubic-bezier(0.23, 1, 0.320, 1)',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.transform = 'translateY(-8px) scale(1.02)'
                      e.target.style.boxShadow = '0 20px 60px rgba(31, 38, 135, 0.4)'
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.transform = 'translateY(0) scale(1)'
                      e.target.style.boxShadow = 'none'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                      <h3 style={{ color: '#1f2937', fontSize: '0.875rem', fontWeight: '600', margin: 0 }}>
                        {stat.title}
                      </h3>
                      <stat.icon size={20} style={{ color: '#667eea' }} />
                    </div>
                    <div style={{ fontSize: '2rem', fontWeight: '700', color: '#111827', marginBottom: '0.5rem' }}>
                      {stat.value}
                    </div>
                    <div style={{ color: '#10b981', fontSize: '0.875rem', fontWeight: '600' }}>
                      {stat.change} from last period
                    </div>
                  </div>
                ))}
              </div>

              {/* Campaigns Table */}
              <div style={{
                background: 'rgba(255, 255, 255, 0.25)',
                backdropFilter: 'blur(25px)',
                WebkitBackdropFilter: 'blur(25px)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '20px',
                overflow: 'hidden'
              }}>
                <div style={{ padding: '1.5rem 2rem', borderBottom: '1px solid rgba(255, 255, 255, 0.2)' }}>
                  <h2 style={{ color: '#111827', fontSize: '1.25rem', fontWeight: '700', margin: 0 }}>
                    Active Campaigns
                  </h2>
                </div>
                <div style={{ padding: '1rem' }}>
                  {loading ? (
                    <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>
                      Loading campaigns...
                    </div>
                  ) : (
                    <div style={{ display: 'grid', gap: '1rem' }}>
                      {campaigns.map((campaign) => (
                        <div
                          key={campaign.id}
                          style={{
                            background: 'rgba(255, 255, 255, 0.4)',
                            backdropFilter: 'blur(10px)',
                            WebkitBackdropFilter: 'blur(10px)',
                            borderRadius: '16px',
                            padding: '1.5rem',
                            display: 'grid',
                            gridTemplateColumns: '1fr auto auto auto auto',
                            gap: '1rem',
                            alignItems: 'center'
                          }}
                        >
                          <div>
                            <h3 style={{ color: '#111827', fontWeight: '600', margin: '0 0 0.25rem 0' }}>
                              {campaign.name}
                            </h3>
                            <span style={{
                              background: campaign.status === 'Active' ? '#10b981' : '#f59e0b',
                              color: 'white',
                              padding: '2px 8px',
                              borderRadius: '12px',
                              fontSize: '0.75rem',
                              fontWeight: '600'
                            }}>
                              {campaign.status}
                            </span>
                          </div>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ color: '#111827', fontWeight: '600' }}>{campaign.impressions}</div>
                            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Impressions</div>
                          </div>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ color: '#111827', fontWeight: '600' }}>{campaign.clicks}</div>
                            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Clicks</div>
                          </div>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ color: '#111827', fontWeight: '600' }}>{campaign.conversions}</div>
                            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Conversions</div>
                          </div>
                          <button style={{
                            background: 'linear-gradient(135deg, #667eea, #764ba2)',
                            color: 'white',
                            border: 'none',
                            borderRadius: '12px',
                            padding: '8px 16px',
                            fontSize: '0.875rem',
                            fontWeight: '600',
                            cursor: 'pointer'
                          }}>
                            View Details
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {activeTab === 'Campaigns' && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.6)',
              backdropFilter: 'blur(15px)',
              WebkitBackdropFilter: 'blur(15px)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
              borderRadius: '20px',
              padding: '2rem'
            }}>
              <h2 style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700', margin: '0 0 1.5rem 0' }}>
                Campaign Creation
              </h2>
              <div style={{ display: 'grid', gap: '1rem' }}>
                <button
                  onClick={() => setActiveTab('AI Chat')}
                  style={{
                    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    padding: '12px 24px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    width: 'fit-content'
                  }}
                >
                  Start Campaign Brief with AI
                </button>
                <button
                  onClick={() => setActiveTab('Campaign Management')}
                  style={{
                    background: 'linear-gradient(135deg, #10b981, #059669)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    padding: '12px 24px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    width: 'fit-content'
                  }}
                >
                  View Campaign Dashboard
                </button>
                <div style={{ color: '#6b7280', fontSize: '1rem' }}>
                  Use AI Chat to generate campaign briefs, then manage created campaigns in the Campaign Management dashboard.
                </div>
              </div>
            </div>
          )}

          {activeTab === 'Campaign Management' && <CampaignDashboard />}

          {activeTab === 'AI Campaign Intelligence' && <EnhancedCampaignDashboard />}

          {activeTab === 'Keyword Research' && <EnhancedKeywordResearch />}

          {activeTab === 'Workflows' && (
            selectedWorkflowId ? (
              <ApprovalWorkflow
                workflowId={selectedWorkflowId}
                onClose={() => setSelectedWorkflowId(null)}
              />
            ) : (
              <div style={{
                background: 'rgba(255, 255, 255, 0.6)',
                backdropFilter: 'blur(15px)',
                WebkitBackdropFilter: 'blur(15px)',
                border: '1px solid rgba(255, 255, 255, 0.5)',
                borderRadius: '20px',
                padding: '2rem'
              }}>
                <h2 style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700', margin: '0 0 1.5rem 0' }}>
                  Campaign Approval Workflows
                </h2>
                <div style={{ display: 'grid', gap: '1rem' }}>
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.4)',
                    padding: '1.5rem',
                    borderRadius: '16px',
                    border: '1px solid rgba(255, 255, 255, 0.3)'
                  }}>
                    <h3 style={{ color: '#111827', fontWeight: '600', margin: '0 0 1rem 0' }}>
                      Active Workflows
                    </h3>
                    <div style={{ display: 'grid', gap: '0.75rem' }}>
                      {[
                        { id: 'wf_001', campaign: 'Fitness Equipment Q1 2024', phase: 'review', status: 'in_progress' },
                        { id: 'wf_002', campaign: 'Holiday Tech Sale', phase: 'creation', status: 'in_progress' },
                        { id: 'wf_003', campaign: 'Spring Fashion Launch', phase: 'planning', status: 'completed' }
                      ].map((workflow) => (
                        <div
                          key={workflow.id}
                          onClick={() => setSelectedWorkflowId(workflow.id)}
                          style={{
                            background: 'rgba(255, 255, 255, 0.5)',
                            padding: '1rem',
                            borderRadius: '12px',
                            border: '1px solid rgba(255, 255, 255, 0.3)',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                          }}
                          onMouseEnter={(e) => {
                            e.target.style.transform = 'translateY(-2px)'
                            e.target.style.background = 'rgba(255, 255, 255, 0.7)'
                          }}
                          onMouseLeave={(e) => {
                            e.target.style.transform = 'translateY(0)'
                            e.target.style.background = 'rgba(255, 255, 255, 0.5)'
                          }}
                        >
                          <div>
                            <div style={{ color: '#111827', fontWeight: '600', marginBottom: '0.25rem' }}>
                              {workflow.campaign}
                            </div>
                            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                              ID: {workflow.id} • Phase: {workflow.phase}
                            </div>
                          </div>
                          <div style={{
                            background: workflow.status === 'in_progress' ? '#f59e0b' : '#10b981',
                            color: 'white',
                            padding: '4px 8px',
                            borderRadius: '8px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'capitalize'
                          }}>
                            {workflow.status.replace('_', ' ')}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.4)',
                    padding: '1.5rem',
                    borderRadius: '16px',
                    border: '1px solid rgba(255, 255, 255, 0.3)'
                  }}>
                    <h3 style={{ color: '#111827', fontWeight: '600', margin: '0 0 1rem 0' }}>
                      Workflow Actions
                    </h3>
                    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                      <button style={{
                        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '12px',
                        padding: '12px 24px',
                        fontSize: '1rem',
                        fontWeight: '600',
                        cursor: 'pointer'
                      }}>
                        Create New Workflow
                      </button>
                      <button style={{
                        background: 'linear-gradient(135deg, #10b981, #059669)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '12px',
                        padding: '12px 24px',
                        fontSize: '1rem',
                        fontWeight: '600',
                        cursor: 'pointer'
                      }}>
                        View All Workflows
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )
          )}

          {activeTab === 'Accounts' && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.6)',
              backdropFilter: 'blur(15px)',
              WebkitBackdropFilter: 'blur(15px)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
              borderRadius: '20px',
              padding: '2rem'
            }}>
              <h2 style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700', margin: '0 0 1.5rem 0' }}>
                Account Overview
              </h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                <div style={{
                  background: 'rgba(255, 255, 255, 0.4)',
                  padding: '1.5rem',
                  borderRadius: '16px',
                  border: '1px solid rgba(255, 255, 255, 0.3)'
                }}>
                  <h3 style={{ color: '#111827', fontWeight: '600', margin: '0 0 1rem 0' }}>Connected Accounts</h3>
                  <div style={{ color: '#6b7280' }}>Demo Customer Account</div>
                  <div style={{ color: '#10b981', fontSize: '0.875rem', marginTop: '0.5rem' }}>✓ Active</div>
                </div>
                <div style={{
                  background: 'rgba(255, 255, 255, 0.4)',
                  padding: '1.5rem',
                  borderRadius: '16px',
                  border: '1px solid rgba(255, 255, 255, 0.3)'
                }}>
                  <h3 style={{ color: '#111827', fontWeight: '600', margin: '0 0 1rem 0' }}>Account Health</h3>
                  <div style={{ color: '#10b981', fontWeight: '600' }}>Excellent</div>
                  <div style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '0.5rem' }}>All systems operational</div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'Analytics' && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.6)',
              backdropFilter: 'blur(15px)',
              WebkitBackdropFilter: 'blur(15px)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
              borderRadius: '20px',
              padding: '2rem'
            }}>
              <h2 style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700', margin: '0 0 1.5rem 0' }}>
                Advanced Analytics
              </h2>
              {dashboardData.analytics ? (
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.4)',
                    padding: '1.5rem',
                    borderRadius: '16px',
                    border: '1px solid rgba(255, 255, 255, 0.3)'
                  }}>
                    <h3 style={{ color: '#111827', fontWeight: '600', margin: '0 0 1rem 0' }}>Performance Overview</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Total Impressions</div>
                        <div style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700' }}>
                          {dashboardData.analytics?.overview?.impressions?.toLocaleString?.() || '0'}
                        </div>
                      </div>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Total Clicks</div>
                        <div style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700' }}>
                          {dashboardData.analytics?.overview?.clicks?.toLocaleString?.() || '0'}
                        </div>
                      </div>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Total Conversions</div>
                        <div style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700' }}>
                          {dashboardData.analytics?.overview?.conversions?.toLocaleString?.() || '0'}
                        </div>
                      </div>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Total Spend</div>
                        <div style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700' }}>
                          ${dashboardData.analytics?.overview?.spend?.toLocaleString?.() || '0'}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>
                  Loading analytics data...
                </div>
              )}
            </div>
          )}

          {activeTab === 'Budget Pacing' && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.6)',
              backdropFilter: 'blur(15px)',
              WebkitBackdropFilter: 'blur(15px)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
              borderRadius: '20px',
              padding: '2rem'
            }}>
              <h2 style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700', margin: '0 0 1.5rem 0' }}>
                Budget Pacing Control
              </h2>
              {dashboardData.budgetPacing ? (
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.4)',
                    padding: '1.5rem',
                    borderRadius: '16px',
                    border: '1px solid rgba(255, 255, 255, 0.3)'
                  }}>
                    <h3 style={{ color: '#111827', fontWeight: '600', margin: '0 0 1rem 0' }}>Budget Summary</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Total Budget</div>
                        <div style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700' }}>
                          ${dashboardData.budgetPacing?.total_budget?.toLocaleString?.() || '0'}
                        </div>
                      </div>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Spent Today</div>
                        <div style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700' }}>
                          ${dashboardData.budgetPacing?.spent_today?.toLocaleString?.() || '0'}
                        </div>
                      </div>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Remaining</div>
                        <div style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700' }}>
                          ${dashboardData.budgetPacing?.remaining_budget?.toLocaleString?.() || '0'}
                        </div>
                      </div>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Pace Status</div>
                        <div style={{
                          color: dashboardData.budgetPacing.pace_status === 'on_track' ? '#10b981' : '#f59e0b',
                          fontSize: '1.5rem',
                          fontWeight: '700'
                        }}>
                          {dashboardData.budgetPacing.pace_status.replace('_', ' ').toUpperCase()}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>
                  Loading budget pacing data...
                </div>
              )}
            </div>
          )}

          {activeTab === 'Performance' && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.6)',
              backdropFilter: 'blur(15px)',
              WebkitBackdropFilter: 'blur(15px)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
              borderRadius: '20px',
              padding: '2rem'
            }}>
              <h2 style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700', margin: '0 0 1.5rem 0' }}>
                Performance Optimization
              </h2>
              {dashboardData.performance ? (
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.4)',
                    padding: '1.5rem',
                    borderRadius: '16px',
                    border: '1px solid rgba(255, 255, 255, 0.3)'
                  }}>
                    <h3 style={{ color: '#111827', fontWeight: '600', margin: '0 0 1rem 0' }}>Key Metrics</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Average CPC</div>
                        <div style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700' }}>
                          ${dashboardData.performance.avg_cpc.toFixed(2)}
                        </div>
                      </div>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>CTR</div>
                        <div style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700' }}>
                          {(dashboardData.performance.avg_ctr * 100).toFixed(2)}%
                        </div>
                      </div>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Conversion Rate</div>
                        <div style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700' }}>
                          {(dashboardData.performance.conversion_rate * 100).toFixed(2)}%
                        </div>
                      </div>
                      <div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>Quality Score</div>
                        <div style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700' }}>
                          {dashboardData.performance.avg_quality_score.toFixed(1)}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>
                  Loading performance data...
                </div>
              )}
            </div>
          )}

          {activeTab === 'Monitoring' && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.6)',
              backdropFilter: 'blur(15px)',
              WebkitBackdropFilter: 'blur(15px)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
              borderRadius: '20px',
              padding: '2rem'
            }}>
              <h2 style={{ color: '#111827', fontSize: '1.5rem', fontWeight: '700', margin: '0 0 1.5rem 0' }}>
                System Monitoring
              </h2>
              {dashboardData.monitoring ? (
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.4)',
                    padding: '1.5rem',
                    borderRadius: '16px',
                    border: '1px solid rgba(255, 255, 255, 0.3)'
                  }}>
                    <h3 style={{ color: '#111827', fontWeight: '600', margin: '0 0 1rem 0' }}>System Status</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
                      {dashboardData.monitoring.services.map((service, index) => (
                        <div key={index} style={{
                          background: 'rgba(255, 255, 255, 0.3)',
                          padding: '1rem',
                          borderRadius: '12px',
                          border: '1px solid rgba(255, 255, 255, 0.2)'
                        }}>
                          <div style={{ color: '#111827', fontWeight: '600', marginBottom: '0.5rem' }}>
                            {service.name}
                          </div>
                          <div style={{
                            color: service.status === 'healthy' ? '#10b981' : '#ef4444',
                            fontSize: '0.875rem',
                            fontWeight: '600'
                          }}>
                            {service.status.toUpperCase()}
                          </div>
                          <div style={{ color: '#6b7280', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                            Last updated: {service.last_updated}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>
                  Loading monitoring data...
                </div>
              )}
            </div>
          )}
        </main>
      </div>

      <style>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0px) translateX(0px);
          }
          25% {
            transform: translateY(-20px) translateX(10px);
          }
          50% {
            transform: translateY(-10px) translateX(-10px);
          }
          75% {
            transform: translateY(15px) translateX(5px);
          }
        }
        
        body {
          margin: 0;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        }
      `}</style>
    </div>
  )
}

export default App