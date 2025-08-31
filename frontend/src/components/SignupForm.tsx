'use client';

import React, { useState } from 'react';
import { Card } from './ui/card';
import { UnifiedButton } from './ui/UnifiedButton';

interface SignupFormProps {
  onSignupSuccess: (userData: UserData) => void;
  onClose: () => void;
  onSwitchToLogin?: () => void;
  authMode?: 'login' | 'signup'; // Add this prop
  onLoginSuccess?: (userData: UserData) => void; // Add this prop
}

interface UserData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  phone: string;
  dateOfBirth: string;
  occupation: string;
  annualIncome: string;
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
  investmentGoals: string[];
}

export default function SignupForm({
  onSignupSuccess,
  onClose,
  onSwitchToLogin,
  authMode = 'signup', // Default to signup
  onLoginSuccess
}: SignupFormProps) {
  // Near the top of the component, add:
  const isLoginMode = authMode === 'login';
  const formTitle = isLoginMode ? 'Sign In to Your Account' : 'Create Your Account';
  const submitButtonText = isLoginMode ? 'Sign In' : 'Create Account';
  const [formData, setFormData] = useState<UserData>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    phone: '',
    dateOfBirth: '',
    occupation: '',
    annualIncome: '',
    riskTolerance: 'moderate',
    investmentGoals: []
  });

  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const investmentGoalOptions = [
    'Wealth Building',
    'Retirement Planning',
    'Emergency Fund',
    'Tax Saving',
    'Child Education',
    'Home Purchase',
    'Travel Fund',
    'Business Investment'
  ];

  const handleInputChange = (field: keyof UserData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleGoalToggle = (goal: string) => {
    setFormData(prev => ({
      ...prev,
      investmentGoals: prev.investmentGoals.includes(goal)
        ? prev.investmentGoals.filter(g => g !== goal)
        : [...prev.investmentGoals, goal]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🚀 Form submission started');
    console.log('📝 Form data:', formData);
    setIsSubmitting(true);

    try {
      if (isLoginMode) {
        // Handle login
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
          ...result.user,
          // CRITICAL: DO NOT SET isAuthenticated to true here
          tokens: result.tokens
        };

        // Save to localStorage for immediate access
        localStorage.setItem('userData', JSON.stringify(userData));
        console.log('💾 Saved authenticated user data to localStorage');
        
        setIsSubmitting(false);
        console.log('🎯 About to call onLoginSuccess with authenticated user:', userData);
        if (onLoginSuccess) {
          onLoginSuccess(userData);
        }
      } else {
        // Handle signup (existing logic)
        // Transform data to match backend expected structure
        const backendData = {
          personalInfo: {
            fullName: `${formData.firstName} ${formData.lastName}`,
            email: formData.email,
            phoneNumber: formData.phone,
            dateOfBirth: formData.dateOfBirth,
            occupation: formData.occupation
          },
          professionalInfo: {
            occupation: formData.occupation,
            annualIncome: formData.annualIncome
          },
          investmentPreferences: {
            riskTolerance: formData.riskTolerance,
            investmentGoals: formData.investmentGoals
          }
        };

        // Register user with proper authentication
        const response = await fetch('http://localhost:8000/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
            full_name: `${formData.firstName} ${formData.lastName}`,
            phone: formData.phone,
            date_of_birth: formData.dateOfBirth
          }),
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error('Backend error:', errorText);
          
          // Parse backend error for better user feedback
          try {
            const errorData = JSON.parse(errorText);
            if (errorData.detail && (errorData.detail.includes('already exists') || errorData.detail.includes('User with this email already exists'))) {
              throw new Error('USER_EXISTS');
            }
          } catch (parseError) {
            // If parsing fails, continue with generic error
            console.log('Failed to parse error response:', parseError);
          }
          
          throw new Error('Failed to save user data');
        }

        const result = await response.json();
        console.log('✅ User registered successfully:', result);

        // Save authentication tokens
        if (result.tokens) {
          localStorage.setItem('access_token', result.tokens.access_token);
          localStorage.setItem('refresh_token', result.tokens.refresh_token);
          console.log('🔐 Authentication tokens saved');
        }

        // Prepare user data for frontend (combine form data with backend response)
        const userData = {
          ...formData,
          id: result.user?.id,
          email: result.user?.email || formData.email,
          // CRITICAL: DO NOT SET isAuthenticated to true here
          tokens: result.tokens
        };

        // Save to localStorage for immediate access
        localStorage.setItem('userData', JSON.stringify(userData));
        console.log('💾 Saved authenticated user data to localStorage');
        
        setIsSubmitting(false);
        console.log('🎯 About to call onSignupSuccess with authenticated user:', userData);
        onSignupSuccess(userData);
      }
    } catch (error) {
      console.error('Error during authentication:', error);
      setIsSubmitting(false);
      
      if (isLoginMode) {
        alert('Invalid email or password. Please try again.');
        return;
      }
      
      // Handle specific error cases for signup
      if (error.message === 'USER_EXISTS') {
        if (onSwitchToLogin) {
          const shouldSwitchToLogin = confirm('An account with this email already exists. Would you like to sign in instead?');
          if (shouldSwitchToLogin) {
            onSwitchToLogin();
            return;
          }
        } else {
          alert('An account with this email already exists. Please use a different email address or try logging in.');
        }
        return;
      }
      
      // Check if it's a validation error from backend
      if (error.message === 'Failed to save user data') {
        // Show validation error to user instead of proceeding
        alert('Please check your input data. Make sure your email address is valid.');
        return;
      }
      
      // Only fallback to localStorage for network errors, not validation errors
      console.log('🌐 Network error - falling back to localStorage');
      localStorage.setItem('userData', JSON.stringify(formData));
      console.log('🎯 About to call onSignupSuccess (fallback) with:', formData);
      onSignupSuccess(formData);
    }
  };

  const nextStep = () => {
    if (currentStep < 3) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const isStepValid = () => {
    switch (currentStep) {
      case 1:
        return formData.firstName && formData.lastName && formData.email && isValidEmail(formData.email) && formData.phone;
      case 2:
        return formData.dateOfBirth && formData.occupation && formData.annualIncome;
      case 3:
        return formData.riskTolerance && formData.investmentGoals.length > 0;
      default:
        return false;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl bg-[rgb(24,25,27)] border border-[rgba(34,197,94,0.2)] max-h-[90vh] overflow-y-auto">
        <div className="p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-white">{formTitle}</h2>
              {!isLoginMode && <p className="text-gray-400 mt-1">Step {currentStep} of 3</p>}
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

          {/* Progress Bar - Only show for signup */}
          {!isLoginMode && (
            <div className="mb-8">
              <div className="flex items-center space-x-4">
                {[1, 2, 3].map((step) => (
                  <div key={step} className="flex items-center flex-1">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                      step <= currentStep 
                        ? 'bg-[rgb(34,197,94)] text-white' 
                        : 'bg-gray-600 text-gray-400'
                    }`}>
                      {step}
                    </div>
                    {step < 3 && (
                      <div className={`flex-1 h-1 mx-2 ${
                        step < currentStep ? 'bg-[rgb(34,197,94)]' : 'bg-gray-600'
                      }`} />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Login Form - Simplified */}
            {isLoginMode && (
              <div className="space-y-6">
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

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(34,197,94,0.2)] rounded-xl text-white focus:outline-none focus:border-[rgb(34,197,94)] transition-colors"
                    placeholder="Enter your password"
                    required
                  />
                </div>
              </div>
            )}

            {/* Step 1: Personal Information */}
            {!isLoginMode && currentStep === 1 && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-white mb-4">Personal Information</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">First Name</label>
                    <input
                      type="text"
                      value={formData.firstName}
                      onChange={(e) => handleInputChange('firstName', e.target.value)}
                      className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(34,197,94,0.2)] rounded-xl text-white focus:outline-none focus:border-[rgb(34,197,94)] transition-colors"
                      placeholder="Enter your first name"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Last Name</label>
                    <input
                      type="text"
                      value={formData.lastName}
                      onChange={(e) => handleInputChange('lastName', e.target.value)}
                      className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(34,197,94,0.2)] rounded-xl text-white focus:outline-none focus:border-[rgb(34,197,94)] transition-colors"
                      placeholder="Enter your last name"
                      required
                    />
                  </div>
                </div>

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

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(34,197,94,0.2)] rounded-xl text-white focus:outline-none focus:border-[rgb(34,197,94)] transition-colors"
                    placeholder="Enter your password (min 12 characters)"
                    minLength={12}
                    required
                  />
                  <p className="text-gray-400 text-xs mt-1">Password must be at least 12 characters with uppercase, lowercase, number, and special character</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Phone Number</label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(34,197,94,0.2)] rounded-xl text-white focus:outline-none focus:border-[rgb(34,197,94)] transition-colors"
                    placeholder="Enter your phone number"
                    required
                  />
                </div>
              </div>
            )}

            {/* Step 2: Professional Information */}
            {!isLoginMode && currentStep === 2 && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-white mb-4">Professional Information</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Date of Birth</label>
                  <input
                    type="date"
                    value={formData.dateOfBirth}
                    onChange={(e) => handleInputChange('dateOfBirth', e.target.value)}
                    className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(34,197,94,0.2)] rounded-xl text-white focus:outline-none focus:border-[rgb(34,197,94)] transition-colors"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Occupation</label>
                  <input
                    type="text"
                    value={formData.occupation}
                    onChange={(e) => handleInputChange('occupation', e.target.value)}
                    className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(34,197,94,0.2)] rounded-xl text-white focus:outline-none focus:border-[rgb(34,197,94)] transition-colors"
                    placeholder="Enter your occupation"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Annual Income</label>
                  <select
                    value={formData.annualIncome}
                    onChange={(e) => handleInputChange('annualIncome', e.target.value)}
                    className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(34,197,94,0.2)] rounded-xl text-white focus:outline-none focus:border-[rgb(34,197,94)] transition-colors"
                    required
                  >
                    <option value="">Select your annual income</option>
                    <option value="0-3L">₹0 - ₹3 Lakhs</option>
                    <option value="3-5L">₹3 - ₹5 Lakhs</option>
                    <option value="5-10L">₹5 - ₹10 Lakhs</option>
                    <option value="10-20L">₹10 - ₹20 Lakhs</option>
                    <option value="20-50L">₹20 - ₹50 Lakhs</option>
                    <option value="50L+">₹50 Lakhs+</option>
                  </select>
                </div>
              </div>
            )}

            {/* Step 3: Investment Preferences */}
            {!isLoginMode && currentStep === 3 && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-white mb-4">Investment Preferences</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-4">Risk Tolerance</label>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                      { value: 'conservative', label: 'Conservative', desc: 'Low risk, stable returns' },
                      { value: 'moderate', label: 'Moderate', desc: 'Balanced risk and returns' },
                      { value: 'aggressive', label: 'Aggressive', desc: 'High risk, high returns' }
                    ].map((option) => (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => handleInputChange('riskTolerance', option.value as any)}
                        className={`p-4 rounded-xl border text-left transition-all ${
                          formData.riskTolerance === option.value
                            ? 'border-[rgb(34,197,94)] bg-[rgba(34,197,94,0.1)]'
                            : 'border-[rgba(34,197,94,0.2)] bg-[rgb(30,31,33)]'
                        }`}
                      >
                        <div className="font-semibold text-white">{option.label}</div>
                        <div className="text-sm text-gray-400 mt-1">{option.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-4">Investment Goals (Select multiple)</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {investmentGoalOptions.map((goal) => (
                      <button
                        key={goal}
                        type="button"
                        onClick={() => handleGoalToggle(goal)}
                        className={`p-3 rounded-xl border text-sm transition-all ${
                          formData.investmentGoals.includes(goal)
                            ? 'border-[rgb(34,197,94)] bg-[rgba(34,197,94,0.1)] text-white'
                            : 'border-[rgba(34,197,94,0.2)] bg-[rgb(30,31,33)] text-gray-300'
                        }`}
                      >
                        {goal}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between mt-8">
              {isLoginMode ? (
                // Login mode - only submit button
                <div className="w-full flex justify-end">
                  <UnifiedButton
                    type="submit"
                    disabled={!formData.email || !formData.password || isSubmitting}
                    className="px-8 py-3"
                  >
                    {isSubmitting ? 'Signing In...' : submitButtonText}
                  </UnifiedButton>
                </div>
              ) : (
                // Signup mode - step navigation
                <>
                  <button
                    type="button"
                    onClick={prevStep}
                    disabled={currentStep === 1}
                    className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                      currentStep === 1
                        ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                        : 'bg-[rgb(30,31,33)] text-white hover:bg-[rgb(40,41,43)] border border-[rgba(34,197,94,0.2)]'
                    }`}
                  >
                    Previous
                  </button>

                  {currentStep < 3 ? (
                    <button
                      type="button"
                      onClick={nextStep}
                      disabled={!isStepValid()}
                      className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                        isStepValid()
                          ? 'bg-[rgb(34,197,94)] text-white hover:bg-[rgb(22,163,74)]'
                          : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      Next
                    </button>
                  ) : (
                    <UnifiedButton
                      type="submit"
                      disabled={!isStepValid() || isSubmitting}
                      className="px-8 py-3"
                    >
                      {isSubmitting ? 'Creating Account...' : submitButtonText}
                    </UnifiedButton>
                  )}
                </>
              )}
            </div>
          </form>

          {/* Switch to Login */}
          {onSwitchToLogin && (
            <div className="mt-6 text-center">
              <p className="text-gray-400">
                Already have an account?{' '}
                <button
                  onClick={onSwitchToLogin}
                  className="text-[rgb(34,197,94)] hover:text-[rgb(22,163,74)] font-semibold transition-colors"
                >
                  Sign In
                </button>
              </p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}