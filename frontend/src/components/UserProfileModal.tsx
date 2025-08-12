'use client';

import React, { useState } from 'react';
import { Card } from './ui/card';
import { UnifiedButton } from './ui/UnifiedButton';
import CacheManagement from './CacheManagement';

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

interface UserProfileModalProps {
  userData: UserData;
  onClose: () => void;
  onEdit: () => void;
  onLogout: () => void;
  onClearProfile?: () => void;
}

export default function UserProfileModal({ userData, onClose, onEdit, onLogout, onClearProfile }: UserProfileModalProps) {
  const [showCacheManagement, setShowCacheManagement] = useState(false);

  const getRiskToleranceColor = (risk: string) => {
    switch (risk) {
      case 'conservative': return 'text-blue-400';
      case 'moderate': return 'text-yellow-400';
      case 'aggressive': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getRiskToleranceIcon = (risk: string) => {
    switch (risk) {
      case 'conservative': return '🛡️';
      case 'moderate': return '⚖️';
      case 'aggressive': return '🚀';
      default: return '📊';
    }
  };

  const calculateAge = (dateOfBirth: string) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl bg-[rgb(24,25,27)] border border-[rgba(34,197,94,0.2)] max-h-[90vh] overflow-y-auto">
        <div className="p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-[rgb(34,197,94)] to-[rgb(22,163,74)] rounded-2xl flex items-center justify-center shadow-lg">
                <span className="text-xl font-bold text-white">
                  {userData.firstName.charAt(0)}{userData.lastName.charAt(0)}
                </span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">
                  {userData.firstName} {userData.lastName}
                </h2>
                <p className="text-[rgb(0,184,153)] font-semibold">Premium Member</p>
              </div>
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

          {/* Profile Information */}
          <div className="space-y-6">
            {/* Personal Information */}
            <div className="bg-[rgb(30,31,33)] rounded-2xl p-6 border border-[rgba(0,184,153,0.1)]">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                <span>👤</span>
                <span>Personal Information</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Email</label>
                  <p className="text-white">{userData.email}</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Phone</label>
                  <p className="text-white">{userData.phone}</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Date of Birth</label>
                  <p className="text-white">
                    {new Date(userData.dateOfBirth).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })} ({calculateAge(userData.dateOfBirth)} years old)
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Occupation</label>
                  <p className="text-white">{userData.occupation}</p>
                </div>
              </div>
            </div>

            {/* Financial Information */}
            <div className="bg-[rgb(30,31,33)] rounded-2xl p-6 border border-[rgba(0,184,153,0.1)]">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                <span>💰</span>
                <span>Financial Profile</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Annual Income</label>
                  <p className="text-white">{userData.annualIncome}</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Risk Tolerance</label>
                  <div className="flex items-center space-x-2">
                    <span>{getRiskToleranceIcon(userData.riskTolerance)}</span>
                    <p className={`font-semibold capitalize ${getRiskToleranceColor(userData.riskTolerance)}`}>
                      {userData.riskTolerance}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Investment Goals */}
            <div className="bg-[rgb(30,31,33)] rounded-2xl p-6 border border-[rgba(0,184,153,0.1)]">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                <span>🎯</span>
                <span>Investment Goals</span>
              </h3>
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {userData.investmentGoals.map((goal, index) => (
                  <div
                    key={index}
                    className="bg-[rgba(34,197,94,0.1)] border border-[rgba(34,197,94,0.2)] rounded-xl p-3 text-center"
                  >
                    <p className="text-sm text-[rgb(34,197,94)] font-medium">{goal}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Account Stats */}
            <div className="bg-[rgb(30,31,33)] rounded-2xl p-6 border border-[rgba(0,184,153,0.1)]">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                <span>📊</span>
                <span>Account Statistics</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-[rgb(0,184,153)]">Premium</p>
                  <p className="text-sm text-gray-400">Membership</p>
                </div>
                
                <div className="text-center">
                  <p className="text-2xl font-bold text-[rgb(0,184,153)]">
                    {new Date().toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                  </p>
                  <p className="text-sm text-gray-400">Member Since</p>
                </div>
                
                <div className="text-center">
                  <p className="text-2xl font-bold text-[rgb(0,184,153)]">Active</p>
                  <p className="text-sm text-gray-400">Status</p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 mt-8">
            <UnifiedButton
              onClick={onEdit}
              className="flex-1 bg-[rgb(0,184,153)] hover:bg-[rgb(0,164,133)]"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit Profile
            </UnifiedButton>
            
            <button
              onClick={() => setShowCacheManagement(true)}
              className="flex-1 px-6 py-3 bg-[rgba(0,184,153,0.1)] hover:bg-[rgba(0,184,153,0.2)] border border-[rgba(0,184,153,0.3)] text-[rgb(0,184,153)] font-semibold rounded-xl transition-all flex items-center justify-center"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.79 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.79 4 8 4s8-1.79 8-4M4 7c0-2.21 3.79-4 8-4s8 1.79 8 4" />
              </svg>
              Cache Settings
            </button>
            
            {onClearProfile && (
              <button
                onClick={onClearProfile}
                className="flex-1 px-6 py-3 bg-[rgba(255,165,0,0.1)] hover:bg-[rgba(255,165,0,0.2)] border border-[rgba(255,165,0,0.3)] text-orange-400 font-semibold rounded-xl transition-all flex items-center justify-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Clear Profile
              </button>
            )}
            
            <button
              onClick={onLogout}
              className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-xl transition-all flex items-center justify-center"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button>
          </div>
        </div>
      </Card>
      
      {/* Cache Management Modal */}
      {showCacheManagement && (
        <CacheManagement
          userEmail={userData.email}
          onClose={() => setShowCacheManagement(false)}
        />
      )}
    </div>
  );
}