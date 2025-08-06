// Temporary auth bypass for development
// Add this to your AuthContext or use directly

export const DEV_CREDENTIALS = {
  email: 'admin@lane-ai.com',
  password: 'LaneAI2025!',
  bypass: true
};

// Quick login function for development
export const devLogin = () => {
  // Set a fake token
  localStorage.setItem('auth_token', 'dev-token-12345');
  localStorage.setItem('user', JSON.stringify({
    id: 1,
    email: DEV_CREDENTIALS.email,
    first_name: 'Admin',
    last_name: 'User',
    role: 'admin'
  }));
  
  // Reload to dashboard
  window.location.href = '/';
};

// Add this to your login component temporarily:
// <button onClick={devLogin}>Dev Login (Bypass)</button>