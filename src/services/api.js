/**
 * API Client Service
 * Centralized API client for all backend endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:5000';

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('authToken');
    this.refreshTokenTimeout = null;
  }

  // Helper method to make requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    // Add auth token if available
    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, config);
      
      // Handle non-JSON responses
      const contentType = response.headers.get('content-type');
      let data;
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        throw new ApiError(
          data.error || data.message || 'Request failed',
          response.status,
          data
        );
      }

      return data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(error.message, 0, null);
    }
  }

  // Set auth token
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('authToken', token);
      this.scheduleTokenRefresh();
    } else {
      localStorage.removeItem('authToken');
      this.cancelTokenRefresh();
    }
  }

  // Schedule token refresh
  scheduleTokenRefresh() {
    // Refresh token 5 minutes before expiry (assuming 1hr tokens)
    this.cancelTokenRefresh();
    this.refreshTokenTimeout = setTimeout(() => {
      this.auth.refreshToken();
    }, 55 * 60 * 1000); // 55 minutes
  }

  cancelTokenRefresh() {
    if (this.refreshTokenTimeout) {
      clearTimeout(this.refreshTokenTimeout);
      this.refreshTokenTimeout = null;
    }
  }

  // ======================
  // Authentication APIs
  // ======================
  auth = {
    register: async (userData) => {
      const response = await this.request('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
      });
      if (response.token) {
        this.setToken(response.token);
      }
      return response;
    },

    login: async (email, password) => {
      const response = await this.request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      if (response.token) {
        this.setToken(response.token);
      }
      return response;
    },

    logout: async () => {
      try {
        await this.request('/auth/logout', { method: 'POST' });
      } finally {
        this.setToken(null);
      }
    },

    refreshToken: async () => {
      try {
        const response = await this.request('/auth/refresh', { method: 'POST' });
        if (response.token) {
          this.setToken(response.token);
        }
        return response;
      } catch (error) {
        this.setToken(null);
        throw error;
      }
    },

    getProfile: async () => {
      return this.request('/auth/profile');
    },

    updateProfile: async (updates) => {
      return this.request('/auth/profile', {
        method: 'PUT',
        body: JSON.stringify(updates),
      });
    },

    changePassword: async (currentPassword, newPassword) => {
      return this.request('/auth/change-password', {
        method: 'POST',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });
    },

    verifyToken: async (token) => {
      return this.request('/auth/verify-token', {
        method: 'POST',
        body: JSON.stringify({ token }),
      });
    },
  };

  // ======================
  // AI Agent APIs
  // ======================
  ai = {
    chat: async (message, conversationId = null, context = {}) => {
      return this.request('/ai/chat', {
        method: 'POST',
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          user_id: 'current-user', // Will be replaced by auth
          context,
        }),
      });
    },

    generateBrief: async (conversationId) => {
      return this.request(`/ai/conversations/${conversationId}/brief`, {
        method: 'POST',
      });
    },

    createCampaign: async (conversationId) => {
      return this.request(`/ai/conversations/${conversationId}/create-campaign`, {
        method: 'POST',
      });
    },

    getConversation: async (conversationId) => {
      return this.request(`/ai/conversations/${conversationId}`);
    },

    listConversations: async (userId) => {
      return this.request('/ai/conversations' + (userId ? `?user_id=${userId}` : ''));
    },

    // Streaming chat for real-time responses
    streamChat: async function* (message, conversationId = null, context = {}) {
      const response = await fetch(`${this.baseURL}/ai/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`,
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          user_id: 'current-user',
          context,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new ApiError('Stream failed', response.status);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              yield data;
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    },
  };

  // ======================
  // Campaign APIs
  // ======================
  campaigns = {
    list: async (customerId = 'demo-customer') => {
      return this.request(`/google-ads/campaigns?customer_id=${customerId}`);
    },

    get: async (campaignId, customerId = 'demo-customer') => {
      return this.request(`/google-ads/campaigns/${campaignId}?customer_id=${customerId}`);
    },

    create: async (campaignData) => {
      return this.request('/orchestrator/campaigns/create-workflow', {
        method: 'POST',
        body: JSON.stringify(campaignData),
      });
    },

    update: async (campaignId, updates) => {
      return this.request(`/google-ads/campaigns/${campaignId}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
      });
    },

    updateStatus: async (campaignId, status) => {
      return this.request(`/google-ads/campaigns/${campaignId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status }),
      });
    },

    delete: async (campaignId) => {
      return this.request(`/google-ads/campaigns/${campaignId}`, {
        method: 'DELETE',
      });
    },

    getMetrics: async (campaignId, dateRange) => {
      const params = new URLSearchParams(dateRange).toString();
      return this.request(`/campaign-analytics/metrics/${campaignId}?${params}`);
    },
  };

  // ======================
  // Dashboard & Analytics APIs
  // ======================
  analytics = {
    getDashboard: async (customerId = 'demo-customer') => {
      return this.request(`/analytics/dashboard/${customerId}`);
    },

    getBudgetPacing: async (customerId = 'demo-customer') => {
      return this.request(`/budget-pacing/summary/${customerId}`);
    },

    getPerformanceOptimization: async (customerId = 'demo-customer') => {
      return this.request(`/performance/optimization/${customerId}`);
    },

    getRealTimeMonitoring: async (customerId = 'demo-customer') => {
      return this.request(`/monitoring/real-time/${customerId}`);
    },

    getKeywordAnalytics: async (customerId = 'demo-customer') => {
      return this.request(`/keyword-analytics/performance/${customerId}`);
    },

    getCampaignAnalytics: async (campaignId) => {
      return this.request(`/campaign-analytics/campaign/${campaignId}`);
    },
  };

  // ======================
  // Budget & Pacing APIs
  // ======================
  budget = {
    getSummary: async (customerId = 'demo-customer') => {
      return this.request(`/budget/summary/${customerId}`);
    },

    getAlerts: async (customerId = 'demo-customer') => {
      return this.request(`/budget/alerts/${customerId}`);
    },

    updateBudget: async (campaignId, budget) => {
      return this.request(`/budget/campaigns/${campaignId}`, {
        method: 'PUT',
        body: JSON.stringify({ budget }),
      });
    },

    getProjections: async (customerId = 'demo-customer') => {
      return this.request(`/budget/projections/${customerId}`);
    },
  };

  // ======================
  // Keyword Research APIs
  // ======================
  keywords = {
    research: async (query, options = {}) => {
      return this.request('/keywords/research', {
        method: 'POST',
        body: JSON.stringify({ query, ...options }),
      });
    },

    analyze: async (keywords) => {
      return this.request('/keywords/analyze', {
        method: 'POST',
        body: JSON.stringify({ keywords }),
      });
    },

    getSuggestions: async (seedKeywords) => {
      return this.request('/keywords/suggestions', {
        method: 'POST',
        body: JSON.stringify({ seed_keywords: seedKeywords }),
      });
    },

    getPerformance: async (customerId = 'demo-customer') => {
      return this.request(`/keyword-analytics/performance/${customerId}`);
    },
  };

  // ======================
  // Workflow & Orchestration APIs
  // ======================
  workflows = {
    list: async () => {
      return this.request('/orchestrator/workflows');
    },

    get: async (workflowId) => {
      return this.request(`/orchestrator/workflows/${workflowId}`);
    },

    create: async (workflowData) => {
      return this.request('/orchestrator/workflows', {
        method: 'POST',
        body: JSON.stringify(workflowData),
      });
    },

    updatePhase: async (workflowId, phase, status) => {
      return this.request(`/orchestrator/workflows/${workflowId}/phase`, {
        method: 'PUT',
        body: JSON.stringify({ phase, status }),
      });
    },

    approve: async (workflowId, phase) => {
      return this.request(`/orchestrator/workflows/${workflowId}/approve`, {
        method: 'POST',
        body: JSON.stringify({ phase }),
      });
    },
  };

  // ======================
  // Health & System APIs
  // ======================
  system = {
    health: async () => {
      return this.request('/health');
    },

    aiHealth: async () => {
      return this.request('/ai/health');
    },

    systemStatus: async () => {
      return this.request('/health/status');
    },
  };
}

// Create singleton instance
const apiClient = new ApiClient();

// Export both the class and instance
export { ApiClient, apiClient as default };