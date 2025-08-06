import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Eye, EyeOff, Zap, Mail, Lock, Loader2, AlertCircle, CheckCircle, Sparkles } from 'lucide-react';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const { login, isAuthenticated, DEV_MODE } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // AUTO-LOGIN IN DEV MODE
  useEffect(() => {
    if (DEV_MODE) {
      console.log('🔐 DEV MODE: Auto-logging in...');
      setTimeout(() => {
        navigate('/', { replace: true });
      }, 100);
      return;
    }
  }, [DEV_MODE, navigate]);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.email || !formData.password) {
      setError('Please fill in all fields');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const result = await login(formData.email, formData.password);
      
      if (result.success) {
        setSuccess('Login successful! Redirecting...');
        const from = location.state?.from?.pathname || '/';
        setTimeout(() => {
          navigate(from, { replace: true });
        }, 1000);
      } else {
        setError(result.error || 'Login failed. Please try again.');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Quick login for demo
  const handleDemoLogin = () => {
    setFormData({
      email: 'admin@lane-ai.com',
      password: 'LaneAI2025!'
    });
  };

  // DEV MODE: Skip login entirely
  const handleDevModeLogin = () => {
    navigate('/', { replace: true });
  };

  // Show dev mode message
  if (DEV_MODE) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem'
      }}>
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: '20px',
          padding: '3rem',
          textAlign: 'center',
          maxWidth: '400px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
        }}>
          <Sparkles size={48} style={{ color: '#667eea', marginBottom: '1rem' }} />
          <h2 style={{ marginBottom: '1rem', color: '#1a202c' }}>Dev Mode Active</h2>
          <p style={{ marginBottom: '2rem', color: '#4a5568' }}>
            Authentication is bypassed. Click below to enter the app.
          </p>
          <button
            onClick={handleDevModeLogin}
            style={{
              width: '100%',
              padding: '1rem',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'transform 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.transform = 'scale(1.02)'}
            onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
          >
            Enter Dashboard →
          </button>
          <p style={{ 
            marginTop: '1rem', 
            fontSize: '0.75rem', 
            color: '#718096' 
          }}>
            Logged in as: admin@lane-ai.com
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '900px',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        background: 'rgba(255, 255, 255, 0.95)',
        borderRadius: '20px',
        overflow: 'hidden',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
      }}>
        {/* Left Panel - Branding */}
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          padding: '3rem',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          color: 'white'
        }}>
          <div style={{ marginBottom: '2rem' }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px',
              marginBottom: '2rem'
            }}>
              <Zap size={40} />
              <h1 style={{ 
                fontSize: '2rem', 
                fontWeight: '700',
                margin: 0
              }}>
                Lane AI
              </h1>
            </div>
            <h2 style={{ 
              fontSize: '1.5rem', 
              fontWeight: '600',
              marginBottom: '1rem'
            }}>
              Welcome Back
            </h2>
            <p style={{ 
              fontSize: '1rem',
              opacity: 0.9,
              lineHeight: '1.6'
            }}>
              Your AI-powered Google Ads management platform with intelligent budget tracking and campaign optimization.
            </p>
          </div>
          
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '12px',
            padding: '1.5rem',
            backdropFilter: 'blur(10px)'
          }}>
            <h3 style={{ 
              fontSize: '1rem', 
              fontWeight: '600',
              marginBottom: '1rem'
            }}>
              Platform Features
            </h3>
            <ul style={{ 
              listStyle: 'none', 
              padding: 0,
              margin: 0,
              fontSize: '0.875rem',
              lineHeight: '2'
            }}>
              <li>✨ AI-Powered Campaign Assistant</li>
              <li>💰 Real-time Budget Tracking</li>
              <li>📊 Advanced Analytics Dashboard</li>
              <li>🎯 Performance Optimization</li>
              <li>🔔 Smart Alert System</li>
            </ul>
          </div>
        </div>

        {/* Right Panel - Login Form */}
        <div style={{ padding: '3rem' }}>
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{ 
              fontSize: '1.75rem', 
              fontWeight: '700',
              marginBottom: '0.5rem',
              color: '#1a202c'
            }}>
              Sign In
            </h2>
            <p style={{ 
              color: '#718096',
              fontSize: '0.875rem'
            }}>
              Enter your credentials to access your dashboard
            </p>
          </div>

          {error && (
            <div style={{
              background: '#fed7d7',
              border: '1px solid #fc8181',
              borderRadius: '8px',
              padding: '0.75rem',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: '#742a2a',
              fontSize: '0.875rem'
            }}>
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          {success && (
            <div style={{
              background: '#c6f6d5',
              border: '1px solid #68d391',
              borderRadius: '8px',
              padding: '0.75rem',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: '#22543d',
              fontSize: '0.875rem'
            }}>
              <CheckCircle size={16} />
              {success}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: '500',
                color: '#4a5568'
              }}>
                Email Address
              </label>
              <div style={{
                position: 'relative'
              }}>
                <Mail size={18} style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#a0aec0'
                }} />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="admin@example.com"
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem 0.75rem 0.75rem 2.5rem',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '0.875rem',
                    outline: 'none',
                    transition: 'border-color 0.2s'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
                />
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontSize: '0.875rem',
                fontWeight: '500',
                color: '#4a5568'
              }}>
                Password
              </label>
              <div style={{
                position: 'relative'
              }}>
                <Lock size={18} style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#a0aec0'
                }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="••••••••"
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem 3rem 0.75rem 2.5rem',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '0.875rem',
                    outline: 'none',
                    transition: 'border-color 0.2s'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'transparent',
                    border: 'none',
                    color: '#a0aec0',
                    cursor: 'pointer',
                    padding: '4px'
                  }}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1.5rem'
            }}>
              <label style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '0.875rem',
                color: '#4a5568',
                cursor: 'pointer'
              }}>
                <input type="checkbox" />
                Remember me
              </label>
              <a href="#" style={{
                fontSize: '0.875rem',
                color: '#667eea',
                textDecoration: 'none',
                fontWeight: '500'
              }}>
                Forgot password?
              </a>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              style={{
                width: '100%',
                padding: '0.75rem',
                background: isLoading ? '#a0aec0' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'transform 0.2s'
              }}
              onMouseEnter={(e) => !isLoading && (e.target.style.transform = 'scale(1.02)')}
              onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
            >
              {isLoading ? (
                <>
                  <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>

            <button
              type="button"
              onClick={handleDemoLogin}
              style={{
                width: '100%',
                marginTop: '1rem',
                padding: '0.75rem',
                background: 'transparent',
                color: '#667eea',
                border: '1px solid #667eea',
                borderRadius: '8px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = '#667eea';
                e.target.style.color = 'white';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'transparent';
                e.target.style.color = '#667eea';
              }}
            >
              Use Demo Credentials
            </button>
          </form>

          <div style={{
            marginTop: '2rem',
            paddingTop: '2rem',
            borderTop: '1px solid #e2e8f0',
            textAlign: 'center'
          }}>
            <p style={{
              fontSize: '0.875rem',
              color: '#718096'
            }}>
              Don't have an account? {' '}
              <Link to="/register" style={{
                color: '#667eea',
                textDecoration: 'none',
                fontWeight: '500'
              }}>
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>

      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default LoginPage;