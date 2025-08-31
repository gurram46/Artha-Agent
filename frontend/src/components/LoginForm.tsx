'use client';

import React, { useState } from 'react';
import { Card } from './ui/card';
import { UnifiedButton } from './ui/UnifiedButton';

interface LoginFormProps {
  onLoginSuccess: (userData: any) => void;
  onClose: () => void;
  onSwitchToSignup: () => void;
}

export default function LoginForm({ onLoginSuccess, onClose, onSwitchToSignup }: LoginFormProps) {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🔐 Login submission started');
    console.log('📝 Login data:', { email: formData.email, password: '[HIDDEN]' });
    setIsSubmitting(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Login error:', errorText);
        
        // Parse backend error for better user feedback
        try {
          const errorData = JSON.parse(errorText);
          if (errorData.detail) {
            throw new Error(errorData.detail);
          }
        } catch (parseError) {
          console.log('Failed to parse error response:', parseError);
        }
        
        throw new Error('Invalid email or password');
      }

      const result = await response.json();
      console.log('✅ User logged in successfully:', result);

      // Save authentication tokens
      if (result.tokens) {
        localStorage.setItem('access_token', result.tokens.access_token);
        localStorage.setItem('refresh_token', result.tokens.refresh_token);
        console.log('🔐 Authentication tokens saved');
      }

      // Prepare user data for frontend
      const userData = {
        id: result.user?.id,
        firstName: result.user?.full_name?.split(' ')[0] || '',
        lastName: result.user?.full_name?.split(' ').slice(1).join(' ') || '',
        email: result.user?.email || formData.email,
        phone: '', // Will be filled from user profile if needed
        dateOfBirth: '',
        occupation: '',
        annualIncome: '',
        riskTolerance: 'moderate',
        investmentGoals: [],
        isAuthenticated: false, // User needs Fi Money authentication after login
        tokens: result.tokens
      };

      // Save to localStorage for immediate access
      localStorage.setItem('userData', JSON.stringify(userData));
      console.log('💾 Saved authenticated user data to localStorage');
      
      setIsSubmitting(false);
      console.log('🎯 About to call onLoginSuccess with authenticated user:', userData);
      onLoginSuccess(userData);
    } catch (error) {
      console.error('Error during login:', error);
      setIsSubmitting(false);
      
      // Show user-friendly error message
      alert(error.message || 'Login failed. Please check your credentials and try again.');
    }
  };

  const isFormValid = () => {
    return formData.email && isValidEmail(formData.email) && formData.password;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md bg-[rgb(24,25,27)] border border-[rgba(34,197,94,0.2)]">
        <div className="p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-white">Welcome Back</h2>
              <p className="text-gray-400 mt-1">Sign in to your account</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className={`w-full px-4 py-3 bg-[rgb(30,31,33)] border rounded-xl text-white focus:outline-none transition-colors ${
                  formData.email && !isValidEmail(formData.email)
                    ? 'border-red-500 focus:border-red-500'
                    : 'border-[rgba(34,197,94,0.2)] focus:border-[rgb(34,197,94)]'
                }`}
                placeholder="Enter your email address"
                required
              />
              {formData.email && !isValidEmail(formData.email) && (
                <p className="text-red-400 text-sm mt-1">Please enter a valid email address</p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(34,197,94,0.2)] rounded-xl text-white focus:outline-none focus:border-[rgb(34,197,94)] transition-colors pr-12"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                >
                  {showPassword ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <UnifiedButton
              type="submit"
              disabled={!isFormValid() || isSubmitting}
              className="w-full py-3"
            >
              {isSubmitting ? 'Signing In...' : 'Sign In'}
            </UnifiedButton>
          </form>

          {/* Switch to Signup */}
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Don't have an account?{' '}
              <button
                onClick={onSwitchToSignup}
                className="text-[rgb(34,197,94)] hover:text-[rgb(22,163,74)] font-semibold transition-colors"
              >
                Create Account
              </button>
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}