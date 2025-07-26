import React, { useState, useEffect, useCallback, lazy, Suspense } from 'react'
import { 
  BarChart3, MessageCircle, Zap, Settings, Search, 
  ChevronRight, Command, X, Loader2, Home, 
  TrendingUp, DollarSign, Target, Users, 
  Shield, Bell, HelpCircle, Menu, ChevronDown,
  Layers, Eye, Code
} from 'lucide-react'

// Lazy load components for performance
const DashboardView = lazy(() => import('./components/views/DashboardView'))
const CampaignsView = lazy(() => import('./components/views/CampaignsView'))
const ChatView = lazy(() => import('./components/views/ChatView'))
const SettingsView = lazy(() => import('./components/views/SettingsView'))

// View mode options
const VIEW_MODES = {
  SIMPLE: 'simple',
  PROFESSIONAL: 'professional',
  EXPERT: 'expert'
}

// Loading component
const LoadingSpinner = () => (
  <div className="flex items-center justify-center h-64">
    <Loader2 className="animate-spin text-primary" size={32} />
  </div>
)

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-content">
            <Shield size={48} className="text-red-500" />
            <h2>Something went wrong</h2>
            <p>{this.state.error?.message || 'An unexpected error occurred'}</p>
            <button onClick={() => this.setState({ hasError: false, error: null })}>
              Try again
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// AI Command Palette Component
const CommandPalette = ({ isOpen, onClose, onExecuteCommand }) => {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  
  const commands = [
    { id: 'create-campaign', label: 'Create new campaign', icon: Zap, action: 'navigate:campaigns:create' },
    { id: 'view-analytics', label: 'View performance analytics', icon: TrendingUp, action: 'navigate:dashboard:analytics' },
    { id: 'budget-report', label: 'Generate budget report', icon: DollarSign, action: 'command:report:budget' },
    { id: 'optimize-keywords', label: 'Optimize keywords', icon: Target, action: 'command:optimize:keywords' },
    { id: 'chat-ai', label: 'Ask AI assistant', icon: MessageCircle, action: 'navigate:chat' },
  ]

  useEffect(() => {
    if (query) {
      const filtered = commands.filter(cmd => 
        cmd.label.toLowerCase().includes(query.toLowerCase())
      )
      setSuggestions(filtered)
    } else {
      setSuggestions(commands.slice(0, 5))
    }
  }, [query])

  if (!isOpen) return null

  return (
    <div className="command-palette-overlay" onClick={onClose}>
      <div className="command-palette" onClick={e => e.stopPropagation()}>
        <div className="command-header">
          <Command size={20} />
          <input
            type="text"
            placeholder="Type a command or search..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            className="command-input"
          />
          <button onClick={onClose} className="command-close">
            <X size={20} />
          </button>
        </div>
        <div className="command-suggestions">
          {suggestions.map(cmd => (
            <button
              key={cmd.id}
              className="command-item"
              onClick={() => {
                onExecuteCommand(cmd.action)
                onClose()
              }}
            >
              <cmd.icon size={16} />
              <span>{cmd.label}</span>
              <ChevronRight size={16} className="ml-auto" />
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

// Main App Component
const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [viewMode, setViewMode] = useState(VIEW_MODES.SIMPLE)
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [notifications, setNotifications] = useState(3)

  // Navigation items - consolidated to 4 main tabs
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'campaigns', label: 'Campaigns', icon: Zap },
    { id: 'chat', label: 'AI Assistant', icon: MessageCircle },
    { id: 'settings', label: 'Settings', icon: Settings }
  ]

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Cmd/Ctrl + K for command palette
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsCommandPaletteOpen(true)
      }
      // Escape to close
      if (e.key === 'Escape') {
        setIsCommandPaletteOpen(false)
        setIsMobileMenuOpen(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Execute command from palette
  const executeCommand = useCallback((action) => {
    const [type, ...params] = action.split(':')
    
    switch (type) {
      case 'navigate':
        setActiveTab(params[0])
        break
      case 'command':
        // Handle specific commands
        console.log('Executing command:', params.join(':'))
        break
      default:
        break
    }
  }, [])

  // Render the active view based on selected tab
  const renderActiveView = () => {
    const viewProps = { viewMode, setViewMode }
    
    return (
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          {activeTab === 'dashboard' && <DashboardView {...viewProps} />}
          {activeTab === 'campaigns' && <CampaignsView {...viewProps} />}
          {activeTab === 'chat' && <ChatView {...viewProps} />}
          {activeTab === 'settings' && <SettingsView {...viewProps} />}
        </Suspense>
      </ErrorBoundary>
    )
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <button 
              className="mobile-menu-toggle"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              aria-label="Toggle menu"
            >
              <Menu size={24} />
            </button>
            <div className="brand">
              <div className="brand-icon">
                <Zap size={24} />
              </div>
              <h1 className="brand-name">Lane MCP</h1>
            </div>
          </div>

          <div className="header-center">
            <button 
              className="command-button"
              onClick={() => setIsCommandPaletteOpen(true)}
              aria-label="Open command palette"
            >
              <Search size={16} />
              <span>Search or type a command</span>
              <kbd>⌘K</kbd>
            </button>
          </div>

          <div className="header-right">
            <button className="icon-button" aria-label="View mode">
              <Layers size={20} />
            </button>
            <button className="icon-button notification-button" aria-label="Notifications">
              <Bell size={20} />
              {notifications > 0 && (
                <span className="notification-badge">{notifications}</span>
              )}
            </button>
            <button className="icon-button" aria-label="Help">
              <HelpCircle size={20} />
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className={`app-nav ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
        <div className="nav-content">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                setActiveTab(item.id)
                setIsMobileMenuOpen(false)
              }}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              aria-current={activeTab === item.id ? 'page' : undefined}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
            </button>
          ))}

          {/* View Mode Selector */}
          <div className="view-mode-selector">
            <button className="view-mode-trigger">
              {viewMode === VIEW_MODES.SIMPLE && <Eye size={16} />}
              {viewMode === VIEW_MODES.PROFESSIONAL && <Layers size={16} />}
              {viewMode === VIEW_MODES.EXPERT && <Code size={16} />}
              <span>{viewMode.charAt(0).toUpperCase() + viewMode.slice(1)} View</span>
              <ChevronDown size={16} />
            </button>
            <div className="view-mode-dropdown">
              {Object.values(VIEW_MODES).map(mode => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  className={`view-mode-option ${viewMode === mode ? 'active' : ''}`}
                >
                  {mode === VIEW_MODES.SIMPLE && <Eye size={16} />}
                  {mode === VIEW_MODES.PROFESSIONAL && <Layers size={16} />}
                  {mode === VIEW_MODES.EXPERT && <Code size={16} />}
                  <span>{mode.charAt(0).toUpperCase() + mode.slice(1)} View</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="app-main">
        <div className="main-content">
          {renderActiveView()}
        </div>
      </main>

      {/* Command Palette */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onExecuteCommand={executeCommand}
      />
    </div>
  )
}

export default App