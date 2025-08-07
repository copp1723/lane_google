import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Lock, User, Building, Phone, Loader2, AlertCircle, Zap } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, loading, error, clearError } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    company: '',
    phone: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});

  const validateForm = () => {
    const errors = {};
    
    if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      errors.email = 'Please enter a valid email address';
    }
    
    if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters long';
    }
    
    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }
    
    if (!formData.first_name.trim()) {
      errors.first_name = 'First name is required';
    }
    
    if (!formData.last_name.trim()) {
      errors.last_name = 'Last name is required';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    clearError();
    
    if (!validateForm()) {
      return;
    }
    
    const { confirmPassword, ...userData } = formData;
    const result = await register(userData);
    
    if (result.success) {
      navigate('/');
    }
  };

  const handleInputChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors({ ...validationErrors, [field]: undefined });
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Features */}
      <div className="hidden lg:flex lg:flex-1 bg-gradient-to-br from-blue-500 to-blue-600 items-center justify-center px-8">
        <div className="max-w-md text-white">
          <h2 className="text-4xl font-bold mb-6">
            Start Your 14-Day Free Trial
          </h2>
          <ul className="space-y-4">
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs">✓</span>
              </div>
              <p>No credit card required</p>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs">✓</span>
              </div>
              <p>Full access to all features</p>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs">✓</span>
              </div>
              <p>Connect your Google Ads account</p>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-xs">✓</span>
              </div>
              <p>24/7 support and onboarding</p>
            </li>
          </ul>
          
          <div className="mt-12 p-6 bg-white/10 rounded-lg backdrop-blur">
            <p className="text-sm mb-2">"Lane MCP transformed how we manage our Google Ads. The AI suggestions alone saved us 20+ hours per week."</p>
            <p className="text-sm font-medium">- Sarah Chen, Marketing Director</p>
          </div>
        </div>
      </div>

      {/* Right Panel - Register Form */}
      <div className="flex-1 flex items-center justify-center px-8 py-12">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="flex items-center gap-2 mb-8">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <Zap className="text-white" size={24} />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Lane MCP</h1>
          </div>

          {/* Form Header */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Create your account</h2>
            <p className="text-gray-600">Get started with your free trial</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="text-red-500 mt-0.5" size={20} />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Register Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name Fields */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">
                  First name
                </label>
                <input
                  type="text"
                  id="first_name"
                  value={formData.first_name}
                  onChange={(e) => handleInputChange('first_name', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    validationErrors.first_name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  required
                />
                {validationErrors.first_name && (
                  <p className="mt-1 text-xs text-red-600">{validationErrors.first_name}</p>
                )}
              </div>
              
              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Last name
                </label>
                <input
                  type="text"
                  id="last_name"
                  value={formData.last_name}
                  onChange={(e) => handleInputChange('last_name', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    validationErrors.last_name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  required
                />
                {validationErrors.last_name && (
                  <p className="mt-1 text-xs text-red-600">{validationErrors.last_name}</p>
                )}
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 text-gray-400" size={20} />
                <input
                  type="email"
                  id="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    validationErrors.email ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="you@example.com"
                  required
                />
              </div>
              {validationErrors.email && (
                <p className="mt-1 text-xs text-red-600">{validationErrors.email}</p>
              )}
            </div>

            {/* Company */}
            <div>
              <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-1">
                Company (optional)
              </label>
              <div className="relative">
                <Building className="absolute left-3 top-2.5 text-gray-400" size={20} />
                <input
                  type="text"
                  id="company"
                  value={formData.company}
                  onChange={(e) => handleInputChange('company', e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Your company name"
                />
              </div>
            </div>

            {/* Phone */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                Phone (optional)
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-2.5 text-gray-400" size={20} />
                <input
                  type="tel"
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 text-gray-400" size={20} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  className={`w-full pl-10 pr-12 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    validationErrors.password ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="At least 8 characters"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
              {validationErrors.password && (
                <p className="mt-1 text-xs text-red-600">{validationErrors.password}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Confirm password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-2.5 text-gray-400" size={20} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                  className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    validationErrors.confirmPassword ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Confirm your password"
                  required
                />
              </div>
              {validationErrors.confirmPassword && (
                <p className="mt-1 text-xs text-red-600">{validationErrors.confirmPassword}</p>
              )}
            </div>

            {/* Terms */}
            <div className="flex items-start">
              <input
                type="checkbox"
                id="terms"
                className="mt-1 mr-2"
                required
              />
              <label htmlFor="terms" className="text-sm text-gray-600">
                I agree to the{' '}
                <Link to="/terms" className="text-blue-600 hover:text-blue-700">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link to="/privacy" className="text-blue-600 hover:text-blue-700">
                  Privacy Policy
                </Link>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Creating account...
                </>
              ) : (
                'Create account'
              )}
            </button>
          </form>

          {/* Sign In Link */}
          <p className="mt-6 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;