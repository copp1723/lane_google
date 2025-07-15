/**
 * Environment Configuration
 * Centralized configuration for API endpoints and environment variables
 */

const getEnvironmentConfig = () => {
  // Check if we're in development or production
  const isDevelopment = import.meta.env.DEV || process.env.NODE_ENV === 'development'
  
  // Get API base URL from environment variables or use defaults
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
                      process.env.REACT_APP_API_BASE_URL || 
                      (isDevelopment ? 'http://localhost:5000' : window.location.origin)
  
  return {
    // API Configuration
    API_BASE_URL,
    API_ENDPOINTS: {
      // Authentication
      LOGIN: `${API_BASE_URL}/api/auth/login`,
      REGISTER: `${API_BASE_URL}/api/auth/register`,
      REFRESH_TOKEN: `${API_BASE_URL}/api/auth/refresh`,
      
      // Dashboard APIs
      ANALYTICS_DASHBOARD: (customerId) => `${API_BASE_URL}/api/analytics/dashboard/${customerId}`,
      BUDGET_PACING: (customerId) => `${API_BASE_URL}/api/budget-pacing/summary/${customerId}`,
      PERFORMANCE_SUMMARY: (customerId) => `${API_BASE_URL}/api/performance/summary/${customerId}`,
      MONITORING_STATUS: (customerId) => `${API_BASE_URL}/api/monitoring/status/${customerId}`,
      
      // Campaign Management
      CAMPAIGNS: `${API_BASE_URL}/api/campaigns`,
      CAMPAIGN_DETAILS: (campaignId) => `${API_BASE_URL}/api/campaigns/${campaignId}`,
      CREATE_CAMPAIGN: `${API_BASE_URL}/api/campaigns/create`,
      
      // AI Agent
      AI_CHAT: `${API_BASE_URL}/api/ai/chat`,
      AI_GENERATE_CAMPAIGN: `${API_BASE_URL}/api/ai/generate-campaign`,
      
      // Google Ads
      GOOGLE_ADS_ACCOUNTS: `${API_BASE_URL}/api/google-ads/accounts`,
      GOOGLE_ADS_CAMPAIGNS: (accountId) => `${API_BASE_URL}/api/google-ads/accounts/${accountId}/campaigns`,
      
      // User Management
      USERS: `${API_BASE_URL}/api/users`,
      USER_PROFILE: `${API_BASE_URL}/api/users/profile`,
      
      // Optimization Actions
      APPLY_OPTIMIZATION: `${API_BASE_URL}/api/performance/apply-optimization`,
      CONTROL_CAMPAIGN: `${API_BASE_URL}/api/budget-pacing/control-campaign`,
      RESOLVE_ISSUE: `${API_BASE_URL}/api/monitoring/resolve-issue`
    },
    
    // Application Configuration
    APP_NAME: 'Lane MCP',
    APP_VERSION: '1.0.0',
    
    // Feature Flags
    FEATURES: {
      AI_CHAT_ENABLED: true,
      REAL_TIME_MONITORING: true,
      AUTO_OPTIMIZATION: true,
      WORKFLOW_APPROVAL: true
    },
    
    // Default Values
    DEFAULTS: {
      CUSTOMER_ID: 'demo-customer',
      PAGINATION_SIZE: 20,
      REFRESH_INTERVAL: 30000, // 30 seconds
      TOKEN_REFRESH_THRESHOLD: 300000 // 5 minutes
    },
    
    // Environment Info
    ENVIRONMENT: {
      IS_DEVELOPMENT: isDevelopment,
      IS_PRODUCTION: !isDevelopment,
      BUILD_TIME: new Date().toISOString()
    }
  }
}

// Export the configuration
export const config = getEnvironmentConfig()

// Export individual pieces for convenience
export const { API_BASE_URL, API_ENDPOINTS, DEFAULTS, FEATURES } = config

// Utility function to get API endpoint with error handling
export const getApiEndpoint = (endpointKey, ...params) => {
  try {
    const endpoint = API_ENDPOINTS[endpointKey]
    if (typeof endpoint === 'function') {
      return endpoint(...params)
    }
    return endpoint
  } catch (error) {
    console.error(`Error getting API endpoint for ${endpointKey}:`, error)
    return `${API_BASE_URL}/api/error`
  }
}

// HTTP client configuration
export const httpConfig = {
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false
}

// Authentication helper
export const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

export default config
