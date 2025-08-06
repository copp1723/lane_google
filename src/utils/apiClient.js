/**
 * API Client Utility
 * Provides consistent error handling, authentication, and request management
 */

import { API_CONFIG } from '../config/api';
import { getAuthHeaders } from '../config/environment';

/**
 * Custom error class for API errors
 */
export class APIError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Sleep utility for retry delays
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Main API client class
 */
class ApiClient {
  constructor(config = {}) {
    this.config = {
      ...API_CONFIG,
      ...config
    };
    this.activeRequests = new Map();
  }

  /**
   * Make an API request with automatic retries and error handling
   * @param {string} url - The URL to request
   * @param {object} options - Fetch options
   * @returns {Promise<any>} The response data
   */
  async request(url, options = {}) {
    const {
      retries = this.config.retries,
      retryDelay = this.config.retryDelay,
      timeout = this.config.timeout,
      ...fetchOptions
    } = options;

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    // Merge headers
    const headers = {
      ...this.config.headers,
      ...getAuthHeaders(),
      ...fetchOptions.headers
    };

    // Create request key for deduplication
    const requestKey = `${fetchOptions.method || 'GET'}-${url}`;
    
    // Check if there's an active request for the same endpoint
    if (this.activeRequests.has(requestKey) && fetchOptions.method === 'GET') {
      return this.activeRequests.get(requestKey);
    }

    // Create the request promise
    const requestPromise = this._performRequest(url, {
      ...fetchOptions,
      headers,
      signal: controller.signal
    }, retries, retryDelay, timeoutId);

    // Store active request
    if (fetchOptions.method === 'GET') {
      this.activeRequests.set(requestKey, requestPromise);
      requestPromise.finally(() => {
        this.activeRequests.delete(requestKey);
      });
    }

    return requestPromise;
  }

  /**
   * Perform the actual request with retry logic
   * @private
   */
  async _performRequest(url, fetchOptions, retriesLeft, retryDelay, timeoutId) {
    try {
      const response = await fetch(url, fetchOptions);
      clearTimeout(timeoutId);

      // Handle non-200 responses
      if (!response.ok) {
        const errorData = await this._parseErrorResponse(response);
        throw new APIError(
          errorData.message || `Request failed with status ${response.status}`,
          response.status,
          errorData
        );
      }

      // Parse successful response
      const data = await this._parseResponse(response);
      return data;

    } catch (error) {
      clearTimeout(timeoutId);

      // Don't retry on client errors (4xx) or abort errors
      if (error.status >= 400 && error.status < 500) {
        throw error;
      }

      if (error.name === 'AbortError') {
        throw new APIError('Request timeout', 408);
      }

      // Retry if we have attempts left
      if (retriesLeft > 0) {
        console.log(`Retrying request to ${url}. Attempts left: ${retriesLeft}`);
        await sleep(retryDelay);
        return this._performRequest(
          url, 
          fetchOptions, 
          retriesLeft - 1, 
          retryDelay * 2, // Exponential backoff
          setTimeout(() => {}, fetchOptions.timeout || this.config.timeout)
        );
      }

      // No retries left
      throw error;
    }
  }

  /**
   * Parse response based on content type
   * @private
   */
  async _parseResponse(response) {
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    }
    
    return response.text();
  }

  /**
   * Parse error response
   * @private
   */
  async _parseErrorResponse(response) {
    try {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      return { message: await response.text() };
    } catch {
      return { message: 'An error occurred' };
    }
  }

  /**
   * Convenience methods for common HTTP verbs
   */
  get(url, options = {}) {
    return this.request(url, { ...options, method: 'GET' });
  }

  post(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  put(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  patch(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }

  delete(url, options = {}) {
    return this.request(url, { ...options, method: 'DELETE' });
  }

  /**
   * Upload files with multipart/form-data
   */
  upload(url, formData, options = {}) {
    const headers = { ...options.headers };
    // Don't set Content-Type for FormData, let browser set it with boundary
    delete headers['Content-Type'];
    
    return this.request(url, {
      ...options,
      method: 'POST',
      body: formData,
      headers
    });
  }

  /**
   * Stream response for Server-Sent Events
   */
  async stream(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.config.headers,
        ...getAuthHeaders(),
        ...options.headers,
        'Accept': 'text/event-stream'
      }
    });

    if (!response.ok) {
      const errorData = await this._parseErrorResponse(response);
      throw new APIError(
        errorData.message || `Stream request failed with status ${response.status}`,
        response.status,
        errorData
      );
    }

    return response;
  }
}

// Create and export a default instance
export const apiClient = new ApiClient();

// Export convenience functions
export const api = {
  get: (url, options) => apiClient.get(url, options),
  post: (url, data, options) => apiClient.post(url, data, options),
  put: (url, data, options) => apiClient.put(url, data, options),
  patch: (url, data, options) => apiClient.patch(url, data, options),
  delete: (url, options) => apiClient.delete(url, options),
  upload: (url, formData, options) => apiClient.upload(url, formData, options),
  stream: (url, options) => apiClient.stream(url, options)
};

// Export for custom instances
export default ApiClient;