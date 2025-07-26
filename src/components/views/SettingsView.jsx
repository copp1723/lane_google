import React, { useState } from 'react'
import { 
  User, Key, Bell, Shield, Palette, 
  Globe, CreditCard, Users, Link,
  Save, ChevronRight, Check, X,
  AlertCircle, HelpCircle, ExternalLink
} from 'lucide-react'

const SettingsView = ({ viewMode }) => {
  const [activeSection, setActiveSection] = useState('account')
  const [hasChanges, setHasChanges] = useState(false)
  const [settings, setSettings] = useState({
    account: {
      name: 'John Doe',
      email: 'john.doe@example.com',
      company: 'Acme Corp',
      timezone: 'America/New_York'
    },
    notifications: {
      emailAlerts: true,
      budgetAlerts: true,
      performanceReports: 'weekly',
      campaignUpdates: true,
      criticalAlerts: true
    },
    integrations: {
      googleAds: {
        connected: true,
        accountId: '123-456-7890',
        lastSync: '2024-01-15 10:30 AM'
      },
      analytics: {
        connected: false,
        accountId: ''
      },
      slack: {
        connected: false,
        webhook: ''
      }
    },
    billing: {
      plan: 'Professional',
      nextBilling: '2024-02-01',
      amount: 299,
      paymentMethod: '**** 4242'
    },
    preferences: {
      theme: 'light',
      language: 'en',
      dateFormat: 'MM/DD/YYYY',
      currency: 'USD',
      defaultView: 'simple'
    }
  })

  const settingSections = [
    { id: 'account', label: 'Account', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'integrations', label: 'Integrations', icon: Link },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'preferences', label: 'Preferences', icon: Palette },
    { id: 'billing', label: 'Billing', icon: CreditCard },
    { id: 'team', label: 'Team', icon: Users }
  ]

  const handleInputChange = (section, field, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }))
    setHasChanges(true)
  }

  const saveSettings = () => {
    // Implement save logic
    console.log('Saving settings:', settings)
    setHasChanges(false)
  }

  const renderAccountSection = () => (
    <div className="settings-section">
      <h3 className="section-title">Account Information</h3>
      <div className="settings-form">
        <div className="form-group">
          <label>Full Name</label>
          <input
            type="text"
            value={settings.account.name}
            onChange={(e) => handleInputChange('account', 'name', e.target.value)}
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label>Email Address</label>
          <input
            type="email"
            value={settings.account.email}
            onChange={(e) => handleInputChange('account', 'email', e.target.value)}
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label>Company Name</label>
          <input
            type="text"
            value={settings.account.company}
            onChange={(e) => handleInputChange('account', 'company', e.target.value)}
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label>Timezone</label>
          <select
            value={settings.account.timezone}
            onChange={(e) => handleInputChange('account', 'timezone', e.target.value)}
            className="form-select"
          >
            <option value="America/New_York">Eastern Time (ET)</option>
            <option value="America/Chicago">Central Time (CT)</option>
            <option value="America/Denver">Mountain Time (MT)</option>
            <option value="America/Los_Angeles">Pacific Time (PT)</option>
          </select>
        </div>
      </div>
    </div>
  )

  const renderNotificationsSection = () => (
    <div className="settings-section">
      <h3 className="section-title">Notification Preferences</h3>
      <div className="settings-list">
        <div className="setting-item">
          <div className="setting-info">
            <h4>Email Alerts</h4>
            <p>Receive email notifications for important updates</p>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={settings.notifications.emailAlerts}
              onChange={(e) => handleInputChange('notifications', 'emailAlerts', e.target.checked)}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        <div className="setting-item">
          <div className="setting-info">
            <h4>Budget Alerts</h4>
            <p>Get notified when campaigns approach budget limits</p>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={settings.notifications.budgetAlerts}
              onChange={(e) => handleInputChange('notifications', 'budgetAlerts', e.target.checked)}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        <div className="setting-item">
          <div className="setting-info">
            <h4>Performance Reports</h4>
            <p>Receive regular performance summaries</p>
          </div>
          <select
            value={settings.notifications.performanceReports}
            onChange={(e) => handleInputChange('notifications', 'performanceReports', e.target.value)}
            className="form-select small"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="never">Never</option>
          </select>
        </div>
      </div>
    </div>
  )

  const renderIntegrationsSection = () => (
    <div className="settings-section">
      <h3 className="section-title">Connected Services</h3>
      <div className="integrations-list">
        <div className="integration-item">
          <div className="integration-header">
            <div className="integration-info">
              <div className="integration-logo" style={{ background: 'linear-gradient(135deg, #4285f4, #34a853)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '16px', fontWeight: 'bold' }}>G</div>
              <div>
                <h4>Google Ads</h4>
                <p className="integration-status connected">
                  <Check size={14} /> Connected
                </p>
              </div>
            </div>
            <button className="secondary-button small">
              Manage
            </button>
          </div>
          {viewMode !== 'simple' && (
            <div className="integration-details">
              <p>Account ID: {settings.integrations.googleAds.accountId}</p>
              <p>Last sync: {settings.integrations.googleAds.lastSync}</p>
            </div>
          )}
        </div>

        <div className="integration-item">
          <div className="integration-header">
            <div className="integration-info">
              <div className="integration-logo" style={{ background: 'linear-gradient(135deg, #f9ab00, #e37400)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '16px', fontWeight: 'bold' }}>A</div>
              <div>
                <h4>Google Analytics</h4>
                <p className="integration-status disconnected">
                  <X size={14} /> Not Connected
                </p>
              </div>
            </div>
            <button className="primary-button small">
              Connect
            </button>
          </div>
        </div>

        {viewMode === 'expert' && (
          <div className="integration-item">
            <div className="integration-header">
              <div className="integration-info">
                <div className="integration-logo" style={{ background: 'linear-gradient(135deg, #611f69, #4a154b)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '16px', fontWeight: 'bold' }}>S</div>
                <div>
                  <h4>Slack</h4>
                  <p className="integration-status disconnected">
                    <X size={14} /> Not Connected
                  </p>
                </div>
              </div>
              <button className="primary-button small">
                Connect
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )

  const renderBillingSection = () => (
    <div className="settings-section">
      <h3 className="section-title">Billing & Subscription</h3>
      <div className="billing-overview">
        <div className="billing-card">
          <h4>Current Plan</h4>
          <div className="plan-info">
            <span className="plan-name">{settings.billing.plan}</span>
            <span className="plan-price">${settings.billing.amount}/month</span>
          </div>
          <p>Next billing date: {settings.billing.nextBilling}</p>
          <button className="link-button">
            Change Plan <ChevronRight size={16} />
          </button>
        </div>
        
        <div className="billing-card">
          <h4>Payment Method</h4>
          <div className="payment-method">
            <CreditCard size={20} />
            <span>{settings.billing.paymentMethod}</span>
          </div>
          <button className="link-button">
            Update Payment Method <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {viewMode === 'expert' && (
        <div className="billing-history">
          <h4>Recent Invoices</h4>
          <table className="invoices-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Jan 1, 2024</td>
                <td>$299.00</td>
                <td><span className="status-badge paid">Paid</span></td>
                <td><button className="link-button">Download</button></td>
              </tr>
              <tr>
                <td>Dec 1, 2023</td>
                <td>$299.00</td>
                <td><span className="status-badge paid">Paid</span></td>
                <td><button className="link-button">Download</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  )

  const renderContent = () => {
    switch (activeSection) {
      case 'account':
        return renderAccountSection()
      case 'notifications':
        return renderNotificationsSection()
      case 'integrations':
        return renderIntegrationsSection()
      case 'billing':
        return renderBillingSection()
      case 'security':
        return (
          <div className="settings-section">
            <h3 className="section-title">Security Settings</h3>
            <div className="security-options">
              <button className="security-action">
                <Key size={20} />
                <span>Change Password</span>
                <ChevronRight size={16} />
              </button>
              <button className="security-action">
                <Shield size={20} />
                <span>Enable Two-Factor Authentication</span>
                <ChevronRight size={16} />
              </button>
              {viewMode === 'expert' && (
                <button className="security-action">
                  <Globe size={20} />
                  <span>API Keys</span>
                  <ChevronRight size={16} />
                </button>
              )}
            </div>
          </div>
        )
      case 'preferences':
        return (
          <div className="settings-section">
            <h3 className="section-title">Preferences</h3>
            <div className="settings-form">
              <div className="form-group">
                <label>Default View Mode</label>
                <select
                  value={settings.preferences.defaultView}
                  onChange={(e) => handleInputChange('preferences', 'defaultView', e.target.value)}
                  className="form-select"
                >
                  <option value="simple">Simple</option>
                  <option value="professional">Professional</option>
                  <option value="expert">Expert</option>
                </select>
              </div>
              <div className="form-group">
                <label>Language</label>
                <select
                  value={settings.preferences.language}
                  onChange={(e) => handleInputChange('preferences', 'language', e.target.value)}
                  className="form-select"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                </select>
              </div>
              <div className="form-group">
                <label>Currency</label>
                <select
                  value={settings.preferences.currency}
                  onChange={(e) => handleInputChange('preferences', 'currency', e.target.value)}
                  className="form-select"
                >
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                </select>
              </div>
            </div>
          </div>
        )
      case 'team':
        return (
          <div className="settings-section">
            <h3 className="section-title">Team Members</h3>
            <p className="section-description">
              Manage team access and permissions
            </p>
            <button className="primary-button">
              <Users size={20} />
              Invite Team Member
            </button>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="settings-view">
      <div className="settings-container">
        {/* Sidebar Navigation */}
        <aside className="settings-sidebar">
          <nav className="settings-nav">
            {settingSections.map(section => (
              <button
                key={section.id}
                className={`settings-nav-item ${activeSection === section.id ? 'active' : ''}`}
                onClick={() => setActiveSection(section.id)}
              >
                <section.icon size={18} />
                <span>{section.label}</span>
                <ChevronRight size={16} className="nav-arrow" />
              </button>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="settings-content">
          {renderContent()}

          {/* Save Bar */}
          {hasChanges && (
            <div className="save-bar">
              <div className="save-bar-content">
                <div className="save-bar-message">
                  <AlertCircle size={16} />
                  <span>You have unsaved changes</span>
                </div>
                <div className="save-bar-actions">
                  <button 
                    className="secondary-button"
                    onClick={() => {
                      // Reset changes
                      setHasChanges(false)
                    }}
                  >
                    Cancel
                  </button>
                  <button 
                    className="primary-button"
                    onClick={saveSettings}
                  >
                    <Save size={16} />
                    Save Changes
                  </button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default SettingsView