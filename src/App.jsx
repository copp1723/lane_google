import React, { useState, useEffect, useCallback, lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import { 
  Bot, MessageCircle, DollarSign, TrendingUp, 
  Target, Activity, Sparkles, ChevronRight, 
  Plus, Search, Bell, User, ArrowUp, ArrowDown,
  Calendar, Clock, AlertCircle, CheckCircle,
  PieChart, BarChart3, Zap, Shield, LogOut,
  Menu, X, Settings, HelpCircle, CreditCard,
  Package, Users, Eye, FileText, Download
} from 'lucide-react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import ProtectedRoute from './components/auth/ProtectedRoute'

// Lazy load components
const DashboardView = lazy(() => import('./components/views/DashboardView'))
const CampaignsView = lazy(() => import('./components/views/CampaignsView'))
const ChatView = lazy(() => import('./components/views/ChatView'))
const SettingsView = lazy(() => import('./components/views/SettingsView'))
const LoginPage = lazy(() => import('./components/auth/LoginPage'))
const RegisterPage = lazy(() => import('./components/auth/RegisterPage'))

// Loading component
const LoadingSpinner = () => (
  <div className="flex items-center justify-center h-64">
    <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
  </div>
)

// AI Assistant Widget Component
const AIAssistantWidget = ({ onExpand }) => {
  const [query, setQuery] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  
  const suggestions = [
    "How's my budget pacing today?",
    "Optimize my top campaigns",
    "Show me underperforming keywords",
    "Create a new campaign strategy"
  ]

  return (
    <div className="ai-assistant-widget">
      <div className="ai-header">
        <div className="ai-avatar">
          <Bot size={24} className="text-white" />
          <div className="ai-status-indicator"></div>
        </div>
        <div className="ai-title">
          <h3>AI Assistant</h3>
          <span className="text-xs text-green-500 flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            Online & Ready
          </span>
        </div>
        <button onClick={onExpand} className="expand-btn">
          <MessageCircle size={20} />
        </button>
      </div>

      <div className="ai-input-container">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask me anything about your campaigns..."
          className="ai-input"
          onFocus={() => setIsTyping(true)}
          onBlur={() => setIsTyping(false)}
        />
        <button className="ai-send-btn">
          <Sparkles size={18} />
        </button>
      </div>

      {!isTyping && (
        <div className="ai-suggestions">
          <p className="text-xs text-gray-500 mb-2">Quick actions:</p>
          <div className="suggestion-pills">
            {suggestions.map((suggestion, idx) => (
              <button key={idx} className="suggestion-pill">
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Budget Tracking Card Component
const BudgetTrackingCard = ({ dealer }) => {
  const budgetData = {
    allocated: 50000,
    spent: 32450,
    remaining: 17550,
    pace: 64.9,
    projection: 48750,
    campaigns: 12,
    performanceChange: 12.5
  }

  const paceColor = budgetData.pace > 80 ? '#ef4444' : budgetData.pace > 60 ? '#f59e0b' : '#10b981'

  return (
    <div className="budget-card">
      <div className="budget-header">
        <div className="budget-title">
          <DollarSign size={20} className="text-blue-600" />
          <h3>Budget Tracking</h3>
        </div>
        <div className="budget-period">
          <Calendar size={14} />
          <span>Jan 2025</span>
        </div>
      </div>

      <div className="budget-metrics">
        <div className="metric-primary">
          <span className="metric-label">Total Budget</span>
          <span className="metric-value">${(budgetData.allocated / 1000).toFixed(1)}K</span>
        </div>
        
        <div className="budget-progress">
          <div className="progress-header">
            <span className="text-sm text-gray-600">Spent</span>
            <span className="text-sm font-semibold">${(budgetData.spent / 1000).toFixed(1)}K</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ 
                width: `${budgetData.pace}%`,
                background: paceColor
              }}
            ></div>
          </div>
          <div className="progress-footer">
            <span className="text-xs text-gray-500">{budgetData.pace}% of budget</span>
            <span className="text-xs text-gray-500">${(budgetData.remaining / 1000).toFixed(1)}K remaining</span>
          </div>
        </div>

        <div className="budget-stats">
          <div className="stat-item">
            <TrendingUp size={16} className="text-green-500" />
            <div>
              <p className="stat-value">+{budgetData.performanceChange}%</p>
              <p className="stat-label">vs last month</p>
            </div>
          </div>
          <div className="stat-item">
            <Target size={16} className="text-blue-500" />
            <div>
              <p className="stat-value">{budgetData.campaigns}</p>
              <p className="stat-label">Active campaigns</p>
            </div>
          </div>
          <div className="stat-item">
            <Activity size={16} className="text-purple-500" />
            <div>
              <p className="stat-value">${(budgetData.projection / 1000).toFixed(1)}K</p>
              <p className="stat-label">Month projection</p>
            </div>
          </div>
        </div>
      </div>

      <div className="budget-actions">
        <button className="action-btn primary">
          <Eye size={14} />
          View Details
        </button>
        <button className="action-btn secondary">
          <Settings size={14} />
          Adjust Budget
        </button>
      </div>
    </div>
  )
}

// Performance Insight Card
const PerformanceInsightCard = ({ type, data }) => {
  const insights = {
    opportunity: {
      icon: Sparkles,
      color: 'blue',
      title: 'Optimization Opportunity',
      message: 'Your "Brand" campaign could save $2,300/month with bid adjustments',
      action: 'Apply Now'
    },
    alert: {
      icon: AlertCircle,
      color: 'amber',
      title: 'Budget Alert',
      message: 'Campaign "Holiday Sale" is pacing 23% over budget',
      action: 'Review'
    },
    success: {
      icon: CheckCircle,
      color: 'green',
      title: 'Performance Win',
      message: 'ROAS improved by 35% after recent optimizations',
      action: 'See Details'
    }
  }

  const insight = insights[type] || insights.opportunity
  const IconComponent = insight.icon

  return (
    <div className={`insight-card ${insight.color}`}>
      <div className="insight-icon">
        <IconComponent size={20} />
      </div>
      <div className="insight-content">
        <h4>{insight.title}</h4>
        <p>{insight.message}</p>
        <button className="insight-action">
          {insight.action}
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  )
}

// Main App Content
const AppContent = () => {
  const { user, logout } = useAuth()
  const [activeView, setActiveView] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [notifications] = useState(3)
  const [showAIChat, setShowAIChat] = useState(false)

  // Quick stats for header
  const quickStats = {
    spend: { value: '$12.4K', change: '+8%', trend: 'up' },
    conversions: { value: '487', change: '+23%', trend: 'up' },
    roas: { value: '4.2x', change: '+0.3', trend: 'up' },
    ctr: { value: '3.8%', change: '-0.2%', trend: 'down' }
  }

  return (
    <div className="app-container modern">
      {/* Sidebar Navigation */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="logo">
            <Zap size={24} className="text-blue-600" />
            <span>Lane AI</span>
          </div>
          <button 
            className="sidebar-toggle desktop-hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section">
            <span className="nav-label">Main</span>
            <button 
              className={`nav-item ${activeView === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveView('dashboard')}
            >
              <BarChart3 size={18} />
              <span>Dashboard</span>
            </button>
            <button 
              className={`nav-item ${activeView === 'budget' ? 'active' : ''}`}
              onClick={() => setActiveView('budget')}
            >
              <DollarSign size={18} />
              <span>Budget Tracking</span>
              <span className="nav-badge">New</span>
            </button>
            <button 
              className={`nav-item ${activeView === 'campaigns' ? 'active' : ''}`}
              onClick={() => setActiveView('campaigns')}
            >
              <Target size={18} />
              <span>Campaigns</span>
            </button>
            <button 
              className={`nav-item ${activeView === 'insights' ? 'active' : ''}`}
              onClick={() => setActiveView('insights')}
            >
              <TrendingUp size={18} />
              <span>Insights</span>
            </button>
          </div>

          <div className="nav-section">
            <span className="nav-label">Tools</span>
            <button className="nav-item">
              <Package size={18} />
              <span>Inventory</span>
            </button>
            <button className="nav-item">
              <Users size={18} />
              <span>Customers</span>
            </button>
            <button className="nav-item">
              <FileText size={18} />
              <span>Reports</span>
            </button>
          </div>
        </nav>

        <div className="sidebar-footer">
          <button className="nav-item">
            <Settings size={18} />
            <span>Settings</span>
          </button>
          <button className="nav-item">
            <HelpCircle size={18} />
            <span>Help</span>
          </button>
          <button onClick={logout} className="nav-item logout">
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Top Header */}
        <header className="top-header">
          <div className="header-left">
            <button 
              className="menu-toggle mobile-only"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={24} />
            </button>
            
            <div className="search-bar">
              <Search size={18} />
              <input type="text" placeholder="Search campaigns, keywords, or ask AI..." />
              <kbd>⌘K</kbd>
            </div>
          </div>

          <div className="header-right">
            <div className="quick-stats">
              {Object.entries(quickStats).map(([key, stat]) => (
                <div key={key} className="stat-chip">
                  <span className="stat-label">{key.toUpperCase()}</span>
                  <span className="stat-value">{stat.value}</span>
                  <span className={`stat-change ${stat.trend}`}>
                    {stat.trend === 'up' ? <ArrowUp size={12} /> : <ArrowDown size={12} />}
                    {stat.change}
                  </span>
                </div>
              ))}
            </div>

            <button className="header-btn notifications">
              <Bell size={20} />
              {notifications > 0 && <span className="badge">{notifications}</span>}
            </button>

            <div className="user-menu">
              <button className="user-btn">
                <div className="user-avatar">
                  <User size={16} />
                </div>
                <span>{user?.first_name || 'User'}</span>
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="page-content">
          {/* AI Assistant Central Widget */}
          <div className="ai-central-container">
            <AIAssistantWidget onExpand={() => setShowAIChat(true)} />
          </div>

          {/* Welcome Section */}
          <div className="welcome-section">
            <h1>Good morning, {user?.first_name || 'there'}! 👋</h1>
            <p>Your AI assistant has identified 3 optimization opportunities worth $4,200 in savings.</p>
          </div>

          {/* Main Grid Layout */}
          <div className="dashboard-grid">
            {/* Budget Tracking Section */}
            <div className="grid-section budget-section">
              <div className="section-header">
                <h2>Budget & Pacing</h2>
                <button className="section-action">
                  <Plus size={16} />
                  Add Budget
                </button>
              </div>
              <div className="budget-cards">
                <BudgetTrackingCard dealer="Main Account" />
                <BudgetTrackingCard dealer="Secondary" />
              </div>
            </div>

            {/* Performance Insights */}
            <div className="grid-section insights-section">
              <div className="section-header">
                <h2>AI Insights</h2>
                <button className="section-action">View All</button>
              </div>
              <div className="insights-list">
                <PerformanceInsightCard type="opportunity" />
                <PerformanceInsightCard type="alert" />
                <PerformanceInsightCard type="success" />
              </div>
            </div>

            {/* Campaign Performance */}
            <div className="grid-section performance-section">
              <div className="section-header">
                <h2>Campaign Performance</h2>
                <div className="time-selector">
                  <button className="time-btn active">Today</button>
                  <button className="time-btn">Week</button>
                  <button className="time-btn">Month</button>
                </div>
              </div>
              
              <div className="performance-chart">
                <div className="chart-placeholder">
                  <BarChart3 size={32} className="text-gray-300" />
                  <p>Performance visualization here</p>
                </div>
              </div>

              <div className="top-campaigns">
                <h3>Top Performers</h3>
                <div className="campaign-list">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="campaign-item">
                      <div className="campaign-info">
                        <span className="campaign-name">Campaign {i}</span>
                        <span className="campaign-metric">4.{i}x ROAS</span>
                      </div>
                      <div className="campaign-bar">
                        <div className="bar-fill" style={{ width: `${90 - i * 10}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid-section actions-section">
              <div className="section-header">
                <h2>Quick Actions</h2>
              </div>
              <div className="action-buttons">
                <button className="action-card">
                  <Plus size={20} />
                  <span>New Campaign</span>
                </button>
                <button className="action-card">
                  <CreditCard size={20} />
                  <span>Adjust Budget</span>
                </button>
                <button className="action-card">
                  <Download size={20} />
                  <span>Export Report</span>
                </button>
                <button className="action-card">
                  <Shield size={20} />
                  <span>Audit Check</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* AI Chat Modal */}
      {showAIChat && (
        <div className="ai-chat-modal">
          <div className="ai-chat-container">
            <div className="ai-chat-header">
              <Bot size={24} />
              <h3>AI Assistant</h3>
              <button onClick={() => setShowAIChat(false)}>
                <X size={20} />
              </button>
            </div>
            <Suspense fallback={<LoadingSpinner />}>
              <ChatView />
            </Suspense>
          </div>
        </div>
      )}
    </div>
  )
}

// Main App Component
const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Suspense fallback={<LoadingSpinner />}><LoginPage /></Suspense>} />
          <Route path="/register" element={<Suspense fallback={<LoadingSpinner />}><RegisterPage /></Suspense>} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppContent />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App