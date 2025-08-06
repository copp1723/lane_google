// Polyfill for process.env to prevent errors in Vite
// This creates a global process object with env if it doesn't exist

if (typeof process === 'undefined') {
  window.process = {
    env: {
      NODE_ENV: import.meta.env.MODE,
      // Map common environment variables to Vite equivalents
      OPENROUTER_API_KEY: import.meta.env.VITE_OPENROUTER_API_KEY || '',
      OPENROUTER_BASE_URL: import.meta.env.VITE_OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
      SITE_URL: import.meta.env.VITE_SITE_URL || 'http://localhost:3000',
      SITE_NAME: import.meta.env.VITE_SITE_NAME || 'Lane MCP',
      API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
      // Add any other legacy process.env variables that might be referenced
    }
  };
}

// Also create a global process if it doesn't exist (for compatibility)
if (typeof global !== 'undefined' && typeof global.process === 'undefined') {
  global.process = window.process;
}

// Export for use if needed
export const processPolyfill = window.process;