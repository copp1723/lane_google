// Environment configuration for Lane MCP
class EnvironmentConfig {
  static getApiBaseUrl() {
    // Return a dummy URL to prevent connection errors during UI testing
    // Change this back to http://localhost:5000 when your backend is running
    return 'https://api.example.com';
  }

  static isDevelopment() {
    return import.meta.env.MODE === 'development';
  }

  static isProduction() {
    return import.meta.env.MODE === 'production';
  }
}

export default EnvironmentConfig;
