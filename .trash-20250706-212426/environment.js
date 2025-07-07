// Environment Configuration
// Centralized environment variable management

class EnvironmentConfig {
  // Get API base URL from environment
  static getApiBaseUrl() {
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';
  }
  
  // Get current environment
  static getEnvironment() {
    return import.meta.env.MODE || 'development';
  }
  
  // Check if running in production
  static isProduction() {
    return this.getEnvironment() === 'production';
  }
  
  // Check if running in development
  static isDevelopment() {
    return this.getEnvironment() === 'development';
  }
  
  // Get WebSocket URL
  static getWebSocketUrl() {
    const apiUrl = this.getApiBaseUrl();
    return apiUrl.replace('http://', 'ws://').replace('https://', 'wss://');
  }
  
  // Get complete environment configuration
  static getConfig() {
    return {
      apiBaseUrl: this.getApiBaseUrl(),
      environment: this.getEnvironment(),
      isProduction: this.isProduction(),
      isDevelopment: this.isDevelopment(),
      webSocketUrl: this.getWebSocketUrl(),
    };
  }
}

export default EnvironmentConfig;

