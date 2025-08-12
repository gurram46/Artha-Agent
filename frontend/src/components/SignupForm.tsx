'use client';

import React, { useState } from 'react';
import { Card } from './ui/card';
import { UnifiedButton } from './ui/UnifiedButton';

interface SignupFormProps {
  onSignupSuccess: (userData: UserData) => void;
  onClose: () => void;
}

interface UserData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  occupation: string;
  annualIncome: string;
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
  investmentGoals: string[];
}

export default function SignupForm({ onSignupSuccess, onClose }: SignupFormProps) {
  const [formData, setFormData] = useState<UserData>({
    firstName: '',
    lastName: '',
    email: '',
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

      // Save user data to backend
      const response = await fetch('http://localhost:8000/api/user/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_data: backendData
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error:', errorText);
        throw new Error('Failed to save user data');
      }

      const result = await response.json();
      console.log('✅ User data saved successfully:', result);

      // Also save to localStorage for immediate access (keep original format for frontend)
      localStorage.setItem('userData', JSON.stringify(formData));
      console.log('💾 Saved to localStorage in SignupForm');
      
      setIsSubmitting(false);
      console.log('🎯 About to call onSignupSuccess with:', formData);
      onSignupSuccess(formData);
    } catch (error) {
      console.error('Error saving user data:', error);
      setIsSubmitting(false);
      
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
              <h2 className="text-2xl font-bold text-white">Create Your Account</h2>
              <p className="text-gray-400 mt-1">Step {currentStep} of 3</p>
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

          {/* Progress Bar */}
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

          <form onSubmit={handleSubmit}>
            {/* Step 1: Personal Information */}
            {currentStep === 1 && (
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
            {currentStep === 2 && (
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
            {currentStep === 3 && (
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
                  {isSubmitting ? 'Creating Account...' : 'Create Account'}
                </UnifiedButton>
              )}
            </div>
          </form>
        </div>
      </Card>
    </div>
  );
}