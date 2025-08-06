/**
 * Centralized API Configuration
 * This file defines all API endpoints for the Lane Google frontend
 * Supports both v1 (new standardized) and legacy endpoints
 */

import { API_BASE_URL } from './environment';

/**
 * API Version Prefixes
 */
export const API_VERSIONS = {
  V1: '/api',  // Backend doesn't use v1 prefix
  LEGACY: '/api'
};

/**
 * Standardized V1 API Endpoints
 * All new features should use these endpoints
 */
export const API_V1_ENDPOINTS = {
  // Health Check
  HEALTH: `${API_BASE_URL}${API_VERSIONS.V1}/health`,
  
  // Authentication (using /api/auth for compatibility)
  AUTH: {
    LOGIN: `${API_BASE_URL}/api/auth/login`,
    REGISTER: `${API_BASE_URL}/api/auth/register`,
    REFRESH: `${API_BASE_URL}/api/auth/refresh`,
    PROFILE: `${API_BASE_URL}/api/auth/me`,
    LOGOUT: `${API_BASE_URL}/api/auth/logout`
  },
  
  // AI Agent
  AI: {
    CHAT: `${API_BASE_URL}${API_VERSIONS.V1}/ai/chat`,
    STREAM: `${API_BASE_URL}${API_VERSIONS.V1}/ai/stream`,
    HEALTH: `${API_BASE_URL}${API_VERSIONS.V1}/ai/health`,
    GENERATE_CAMPAIGN: `${API_BASE_URL}${API_VERSIONS.V1}/ai/generate-campaign`
  },
  
  // Campaign Management
  CAMPAIGNS: {
    LIST: `${API_BASE_URL}${API_VERSIONS.V1}/campaigns`,
    CREATE: `${API_BASE_URL}${API_VERSIONS.V1}/campaigns`,
    DETAILS: (campaignId) => `${API_BASE_URL}${API_VERSIONS.V1}/campaigns/${campaignId}`,
    UPDATE: (campaignId) => `${API_BASE_URL}${API_VERSIONS.V1}/campaigns/${campaignId}`,
    DELETE: (campaignId) => `${API_BASE_URL}${API_VERSIONS.V1}/campaigns/${campaignId}`,
    STATUS: (campaignId) => `${API_BASE_URL}${API_VERSIONS.V1}/campaigns/${campaignId}/status`
  },
  
  // Google Ads Integration
  GOOGLE_ADS: {
    ACCOUNTS: `${API_BASE_URL}${API_VERSIONS.V1}/google-ads/accounts`,
    CAMPAIGNS: `${API_BASE_URL}${API_VERSIONS.V1}/google-ads/campaigns`,
    CAMPAIGN_BY_ACCOUNT: (accountId) => `${API_BASE_URL}${API_VERSIONS.V1}/google-ads/accounts/${accountId}/campaigns`,
    CAMPAIGN_STATUS: (campaignId) => `${API_BASE_URL}${API_VERSIONS.V1}/google-ads/campaigns/${campaignId}/status`
  },
  
  // Keyword Research
  KEYWORDS: {
    RESEARCH: `${API_BASE_URL}${API_VERSIONS.V1}/keywords/research`,
    SUGGESTIONS: `${API_BASE_URL}${API_VERSIONS.V1}/keywords/suggestions`,
    ANALYTICS: `${API_BASE_URL}${API_VERSIONS.V1}/keywords/analytics`,
    COMPREHENSIVE_ANALYSIS: `${API_BASE_URL}${API_VERSIONS.V1}/keywords/analytics/comprehensive`,
    QUICK_INSIGHTS: `${API_BASE_URL}${API_VERSIONS.V1}/keywords/analytics/quick-insights`
  },
  
  // Budget Pacing
  BUDGET: {
    SUMMARY: (customerId) => `${API_BASE_URL}${API_VERSIONS.V1}/budget/summary/${customerId}`,
    PAUSE_CAMPAIGN: `${API_BASE_URL}${API_VERSIONS.V1}/budget/pause-campaign`,
    RESUME_CAMPAIGN: `${API_BASE_URL}${API_VERSIONS.V1}/budget/resume-campaign`,
    CONTROL_CAMPAIGN: `${API_BASE_URL}${API_VERSIONS.V1}/budget/control-campaign`
  },
  
  // Campaign Orchestration
  ORCHESTRATOR: {
    WORKFLOWS: `${API_BASE_URL}${API_VERSIONS.V1}/orchestrator/workflows`,
    CREATE_WORKFLOW: `${API_BASE_URL}${API_VERSIONS.V1}/orchestrator/campaigns/create-workflow`,
    WORKFLOW_STATUS: (workflowId) => `${API_BASE_URL}${API_VERSIONS.V1}/orchestrator/workflows/${workflowId}`
  },
  
  // Campaign Analytics
  CAMPAIGN_ANALYTICS: {
    PERFORMANCE_ANALYSIS: `${API_BASE_URL}${API_VERSIONS.V1}/campaign-analytics/performance-analysis`,
    BUDGET_OPTIMIZATION: `${API_BASE_URL}${API_VERSIONS.V1}/campaign-analytics/budget-optimization`,
    ANOMALY_DETECTION: `${API_BASE_URL}${API_VERSIONS.V1}/campaign-analytics/anomaly-detection`,
    TESTING_RECOMMENDATIONS: `${API_BASE_URL}${API_VERSIONS.V1}/campaign-analytics/testing-recommendations`,
    REAL_TIME_METRICS: `${API_BASE_URL}${API_VERSIONS.V1}/campaign-analytics/real-time-metrics`,
    OPPORTUNITY_SCAN: `${API_BASE_URL}${API_VERSIONS.V1}/campaign-analytics/opportunity-scan`
  },
  
  // User Management
  USERS: {
    LIST: `${API_BASE_URL}${API_VERSIONS.V1}/users`,
    PROFILE: `${API_BASE_URL}${API_VERSIONS.V1}/users/profile`,
    UPDATE: (userId) => `${API_BASE_URL}${API_VERSIONS.V1}/users/${userId}`,
    DELETE: (userId) => `${API_BASE_URL}${API_VERSIONS.V1}/users/${userId}`
  }
};

/**
 * Legacy API Endpoints
 * These are maintained for backward compatibility with dashboard components
 * Eventually these should be migrated to v1 endpoints
 */
export const LEGACY_ENDPOINTS = {
  // Analytics Dashboard
  ANALYTICS: {
    DASHBOARD: (customerId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/analytics/dashboard/${customerId}`,
    INSIGHTS: (customerId, timeRange) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/analytics/insights/${customerId}?time_range=${timeRange}`,
    BENCHMARKS: `${API_BASE_URL}${API_VERSIONS.LEGACY}/analytics/benchmarks`,
    REPORT_TEMPLATES: `${API_BASE_URL}${API_VERSIONS.LEGACY}/analytics/reports/templates`,
    GENERATE_REPORT: `${API_BASE_URL}${API_VERSIONS.LEGACY}/analytics/reports/generate`
  },
  
  // Performance Optimization
  PERFORMANCE: {
    SUMMARY: (customerId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/performance/summary/${customerId}`,
    ANALYZE: (customerId, campaignId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/performance/analyze/${customerId}/${campaignId}`,
    RECOMMENDATIONS: (customerId, campaignId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/performance/recommendations/${customerId}/${campaignId}`,
    OPTIMIZE: (customerId, campaignId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/performance/optimize/${customerId}/${campaignId}`,
    AUTO_OPTIMIZE: (customerId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/performance/auto-optimize/${customerId}`,
    APPLY_OPTIMIZATION: `${API_BASE_URL}${API_VERSIONS.LEGACY}/performance/apply-optimization`
  },
  
  // Real-Time Monitoring
  MONITORING: {
    STATUS: (customerId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/monitoring/status/${customerId}`,
    ISSUES: (customerId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/monitoring/issues/${customerId}`,
    DASHBOARD: (customerId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/monitoring/dashboard/${customerId}`,
    RULES: `${API_BASE_URL}${API_VERSIONS.LEGACY}/monitoring/rules`,
    START: (customerId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/monitoring/start/${customerId}`,
    STOP: `${API_BASE_URL}${API_VERSIONS.LEGACY}/monitoring/stop`,
    RESOLVE_ISSUE: (issueId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/monitoring/issues/${issueId}/resolve`,
    IGNORE_ISSUE: (issueId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/monitoring/issues/${issueId}/ignore`,
    TOGGLE_RULE: (ruleId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/monitoring/rules/${ruleId}/toggle`,
    TEST_ALERT: `${API_BASE_URL}${API_VERSIONS.LEGACY}/monitoring/alerts/test`
  },
  
  // Budget Pacing (Legacy)
  BUDGET_PACING: {
    SUMMARY: (customerId) => `${API_BASE_URL}${API_VERSIONS.LEGACY}/budget-pacing/summary/${customerId}`,
    PAUSE_CAMPAIGN: `${API_BASE_URL}${API_VERSIONS.LEGACY}/budget-pacing/pause-campaign`,
    RESUME_CAMPAIGN: `${API_BASE_URL}${API_VERSIONS.LEGACY}/budget-pacing/resume-campaign`,
    CONTROL_CAMPAIGN: `${API_BASE_URL}${API_VERSIONS.LEGACY}/budget-pacing/control-campaign`
  }
};

/**
 * Helper function to get the appropriate endpoint based on feature flags
 * @param {string} feature - The feature/endpoint name
 * @param {boolean} useLegacy - Whether to use legacy endpoint
 * @returns {string|function} The endpoint URL or function
 */
export const getEndpoint = (feature, useLegacy = false) => {
  if (useLegacy) {
    return LEGACY_ENDPOINTS[feature];
  }
  return API_V1_ENDPOINTS[feature];
};

/**
 * API client configuration defaults
 */
export const API_CONFIG = {
  timeout: 30000, // 30 seconds
  retries: 3,
  retryDelay: 1000, // 1 second
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Client-Version': '1.0.0'
  }
};

/**
 * Export all endpoints for convenience
 */
export const API_ENDPOINTS = {
  ...API_V1_ENDPOINTS,
  LEGACY: LEGACY_ENDPOINTS
};

export default API_ENDPOINTS;