import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_V1_ENDPOINTS } from '../config/api';

const AuthContext = createContext({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// TEMPORARY: Dev mode bypass
const DEV_MODE = false; // Set to false in production
const DEV_USER = {
  id: 1,
  email: 'admin@lane-ai.com',
  first_name: 'Admin',
  last_name: 'User',
  role: 'admin'
};

export const AuthProvider = ({ children }) => {
  // TEMPORARY: Auto-login in dev mode
  const [user, setUser] = useState(DEV_MODE ? DEV_USER : null);
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState(DEV_MODE ? 'dev-token' : localStorage.getItem('auth_token'));

  useEffect(() => {
    // Skip API calls in dev mode
    if (DEV_MODE) {
      setLoading(false);
      return;
    }

    if (token) {
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch(API_V1_ENDPOINTS.AUTH.PROFILE, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user profile');
      }

      const result = await response.json();
      if (result.success && result.data) {
        setUser(result.data);
      } else {
        throw new Error('Invalid profile response');
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      // Clear invalid token
      localStorage.removeItem('auth_token');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    // TEMPORARY: Bypass login in dev mode
    if (DEV_MODE) {
      console.log('🔐 Dev Mode: Bypassing authentication');
      setUser(DEV_USER);
      setToken('dev-token');
      localStorage.setItem('auth_token', 'dev-token');
      return { success: true };
    }

    try {
      const response = await fetch(API_V1_ENDPOINTS.AUTH.LOGIN, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || 'Login failed');
      }

      if (result.success && result.data) {
        const { token: newToken, user: userData } = result.data;
        
        // Store token
        localStorage.setItem('auth_token', newToken);
        setToken(newToken);
        
        // Store user
        setUser(userData);
        
        return { success: true };
      } else {
        throw new Error(result.message || 'Invalid login response');
      }
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.message || 'Failed to login' 
      };
    }
  };

  const register = async (userData) => {
    // TEMPORARY: Bypass registration in dev mode
    if (DEV_MODE) {
      console.log('🔐 Dev Mode: Bypassing registration');
      setUser(DEV_USER);
      setToken('dev-token');
      localStorage.setItem('auth_token', 'dev-token');
      return { success: true };
    }

    try {
      const response = await fetch(API_V1_ENDPOINTS.AUTH.REGISTER, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || 'Registration failed');
      }

      if (result.success && result.data) {
        const { token: newToken, user: newUser } = result.data;
        
        // Store token
        localStorage.setItem('auth_token', newToken);
        setToken(newToken);
        
        // Store user
        setUser(newUser);
        
        return { success: true };
      } else {
        throw new Error(result.message || 'Invalid registration response');
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.message || 'Failed to register' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(DEV_MODE ? null : null); // Clear user even in dev mode
    
    // Redirect to login if not in dev mode
    if (!DEV_MODE) {
      window.location.href = '/login';
    }
  };

  const updateProfile = async (updates) => {
    // TEMPORARY: Mock update in dev mode
    if (DEV_MODE) {
      setUser({ ...user, ...updates });
      return { success: true };
    }

    try {
      const response = await fetch(API_V1_ENDPOINTS.AUTH.PROFILE, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || 'Failed to update profile');
      }

      if (result.success && result.data) {
        setUser(result.data);
        return { success: true };
      } else {
        throw new Error(result.message || 'Invalid update response');
      }
    } catch (error) {
      console.error('Profile update error:', error);
      return { 
        success: false, 
        error: error.message || 'Failed to update profile' 
      };
    }
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateProfile,
    isAuthenticated: DEV_MODE ? true : !!user,
    isAdmin: user?.role === 'admin',
    DEV_MODE // Expose dev mode flag
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;