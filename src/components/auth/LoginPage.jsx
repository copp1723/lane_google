import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Lock, Loader2, AlertCircle, Zap } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, loading, error, clearError } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    clearError();
    
    const result = await login(formData.email, formData.password);
    if (result.success) {
      navigate('/');
    }
  };

  const handleDemoLogin = async () => {
    // Pre-fill with demo credentials
    setFormData({
      email: 'demo@lane-mcp.com',
      password: 'demo123456',
    });
    
    // Auto-submit after a brief delay
    setTimeout(async () => {
      const result = await login('demo@lane-mcp.com', 'demo123456');
      if (result.success) {
        navigate('/');
      }
    }, 300);
  };

  return (
    <div className="min-h-screen flex" style={{ background: 'var(--bg-gradient-main)' }}>
        {/* Left Panel - Login Form */}
        <div className="flex-1 flex items-center justify-center px-8 py-12">
          <div className="w-full max-w-md">
            {/* Logo */}
            <div className="flex items-center gap-2 mb-8">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: 'var(--secondary-500)' }}>
                <Zap className="text-white" size={24} />
              </div>
              <h1 className="text-2xl font-semibold" style={{ color: 'var(--primary-800)' }}>Lane MCP</h1>
            </div>

            {/* Form Header */}
            <div className="mb-8">
              <h2 className="text-3xl font-semibold mb-2" style={{ color: 'var(--primary-800)' }}>Welcome back</h2>
              <p style={{ color: 'var(--primary-600)' }}>Sign in to your account to continue</p>
            </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 rounded-lg flex items-start gap-3" style={{
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              color: 'var(--accent-red)'
            }}>
              <AlertCircle style={{ color: 'var(--accent-red)' }} className="mt-0.5" size={20} />
              <p className="text-sm" style={{ color: 'var(--accent-red)' }}>{error}</p>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2" style={{ color: 'var(--primary-700)' }}>
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3" style={{ color: 'var(--primary-400)' }} size={20} />
                <input
                  type="email"
                  id="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full pl-10 pr-4 py-3 rounded-lg transition-all"
                  style={{
                    border: '1px solid var(--glass-border)',
                    backgroundColor: 'var(--glass-bg-strong)',
                    color: 'var(--primary-800)'
                  }}
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-2" style={{ color: 'var(--primary-700)' }}>
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3" style={{ color: 'var(--primary-400)' }} size={20} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-10 pr-12 py-3 rounded-lg transition-all"
                  style={{
                    border: '1px solid var(--glass-border)',
                    backgroundColor: 'var(--glass-bg-strong)',
                    color: 'var(--primary-800)'
                  }}
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 hover:opacity-80 transition-opacity"
                  style={{ color: 'var(--primary-500)' }}
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" />
                <span className="text-sm" style={{ color: 'var(--primary-600)' }}>Remember me</span>
              </label>
              <Link
                to="/forgot-password"
                className="text-sm hover:opacity-80 transition-opacity"
                style={{ color: 'var(--secondary-600)' }}
              >
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              style={{
                backgroundColor: 'var(--secondary-500)',
                color: 'white'
              }}
              onMouseEnter={(e) => e.target.style.backgroundColor = 'var(--secondary-600)'}
              onMouseLeave={(e) => e.target.style.backgroundColor = 'var(--secondary-500)'}
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t" style={{ borderColor: 'var(--glass-border)' }}></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4" style={{
                backgroundColor: 'var(--bg-secondary)',
                color: 'var(--primary-500)'
              }}>Or continue with</span>
            </div>
          </div>

          {/* Demo Login */}
          <button
            onClick={handleDemoLogin}
            className="w-full py-3 rounded-lg transition-all flex items-center justify-center gap-2"
            style={{
              backgroundColor: 'var(--glass-bg-strong)',
              color: 'var(--primary-700)',
              border: '1px solid var(--glass-border)'
            }}
            onMouseEnter={(e) => e.target.style.backgroundColor = 'var(--primary-50)'}
            onMouseLeave={(e) => e.target.style.backgroundColor = 'var(--glass-bg-strong)'}
          >
            <Zap size={20} />
            Try Demo Account
          </button>

          {/* Sign Up Link */}
          <p className="mt-8 text-center text-sm" style={{ color: 'var(--primary-600)' }}>
            Don't have an account?{' '}
            <Link
              to="/register"
              className="font-medium hover:opacity-80 transition-opacity"
              style={{ color: 'var(--secondary-600)' }}
            >
              Sign up for free
            </Link>
          </p>
        </div>
      </div>

      {/* Right Panel - Features */}
      <div className="hidden lg:flex lg:flex-1 items-center justify-center px-8" style={{ background: 'var(--bg-gradient-accent)' }}>
        <div className="max-w-md" style={{ color: 'var(--primary-800)' }}>
          <h2 className="text-4xl font-semibold mb-6">
            AI-Powered Google Ads Management
          </h2>
          <ul className="space-y-4">
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: 'var(--secondary-500)' }}>
                <span className="text-xs text-white">✓</span>
              </div>
              <p>Create and optimize campaigns with natural language</p>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: 'var(--secondary-500)' }}>
                <span className="text-xs text-white">✓</span>
              </div>
              <p>Real-time budget monitoring and pacing alerts</p>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: 'var(--secondary-500)' }}>
                <span className="text-xs text-white">✓</span>
              </div>
              <p>Advanced analytics and performance insights</p>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: 'var(--secondary-500)' }}>
                <span className="text-xs text-white">✓</span>
              </div>
              <p>Automated keyword research and optimization</p>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;