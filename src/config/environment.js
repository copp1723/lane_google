class EnvironmentConfig {
  static getApiBaseUrl() {
    // Check if we're in development or production
    const isDev = import.meta.env.DEV;
    const envApiUrl = import.meta.env.VITE_API_BASE_URL;
    
    if (envApiUrl) {
      return envApiUrl;
    }
    
    // Default to localhost in development, otherwise use relative path
    return isDev ? 'http://localhost:5000' : '/api';
  }
  
  static getAppEnv() {
    return import.meta.env.MODE || 'development';
  }
  
  static isProduction() {
    return this.getAppEnv() === 'production';
  }
  
  static isDevelopment() {
    return this.getAppEnv() === 'development';
  }
}

export default EnvironmentConfig;