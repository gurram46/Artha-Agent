'use client';

import React, { useState, useEffect } from 'react';
import { UnifiedButton } from './ui/UnifiedButton';
import { Card } from './ui/card';
import MCPDataService from '../services/mcpDataService';

interface FiMoneyAuthProps {
  onAuthSuccess: () => void;
  onAuthError: (error: string) => void;
}

const FiMoneyAuth: React.FC<FiMoneyAuthProps> = ({ onAuthSuccess, onAuthError }) => {
  const [isConnecting, setIsConnecting] = useState(false);
  const [showPasscodeInput, setShowPasscodeInput] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [passcode, setPasscode] = useState('');
  // Removed timeout functionality as requested
  const [authError, setAuthError] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessionInfo, setSessionInfo] = useState<any>(null);

  const mcpService = MCPDataService.getInstance();

  useEffect(() => {
    checkAuthStatus();
  }, []);

  // Removed timeout useEffect as requested

  const checkAuthStatus = async () => {
    try {
      const status = await mcpService.checkAuthenticationStatus();
      setIsAuthenticated(status.authenticated);
      setSessionInfo(status);
      
      if (status.authenticated) {
        onAuthSuccess();
      }
    } catch (error) {
      console.error('Auth status check failed:', error);
    }
  };

  const handleConnectToFiMoney = async () => {
    console.log('🧹 Clearing previous Fi Money session before new authentication...');
    
    // Preserve user signup data while clearing Fi Money session data
    const existingUserData = localStorage.getItem('userData');
    console.log('💾 Preserving user signup data:', existingUserData ? 'Found' : 'None');
    
    // Logout from any existing Fi Money session
    try {
      await mcpService.logout();
      console.log('✅ Previous Fi Money session cleared');
    } catch (logoutError) {
      console.log('⚠️ No previous session to clear or logout failed:', logoutError);
    }
    
    // Clear only Fi Money related session data, preserve user profile
    sessionStorage.removeItem('demoMode');
    // Note: We're NOT clearing localStorage to preserve user signup data
    
    setShowPasscodeInput(true);
    setAuthError('');
    setPasscode('');
  };

  const handleAuthenticate = async () => {
    if (!phoneNumber.trim()) {
      setAuthError('Please enter your phone number');
      return;
    }

    if (!passcode.trim()) {
      setAuthError('Please enter the passcode from Fi Money app');
      return;
    }

    setIsConnecting(true);
    setAuthError('');

    try {
      const result = await mcpService.authenticateWithFiMoney(phoneNumber, passcode);
      
      if (result.success && result.authenticated) {
        setIsAuthenticated(true);
        setShowPasscodeInput(false);
        onAuthSuccess();
      } else {
        setAuthError(result.message || 'Authentication failed');
        onAuthError(result.message || 'Authentication failed');
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Authentication error';
      setAuthError(errorMsg);
      onAuthError(errorMsg);
    }

    setIsConnecting(false);
  };

  const handleLogout = async () => {
    try {
      console.log('🚪 Starting Fi Money logout process (preserving user profile)...');
      
      // Preserve user signup data
      const existingUserData = localStorage.getItem('userData');
      console.log('💾 Preserving user signup data during logout:', existingUserData ? 'Found' : 'None');
      
      // Logout from Fi Money backend session
      await mcpService.logout();
      console.log('✅ Fi Money backend session cleared');
      
      // Clear demo mode
      mcpService.setDemoMode(false);
      
      // Clear only Fi Money related session data, preserve user profile
      console.log('🧹 Clearing Fi Money session data (preserving user profile)...');
      sessionStorage.removeItem('demoMode');
      // Note: We're NOT clearing localStorage to preserve user signup data
      
      // Reset only Fi Money authentication state
      setIsAuthenticated(false);
      setSessionInfo(null);
      setShowPasscodeInput(false);
      setPhoneNumber('');
      setPasscode('');
      setAuthError('');
      
      console.log('✅ Fi Money logout successful - user profile preserved');
      
      // Notify parent component about logout
      if (onAuthError) {
        onAuthError('User logged out');
      }
      
    } catch (error) {
      console.error('❌ Logout failed:', error);
      
      // Even if logout fails, clear Fi Money data but preserve user profile
      console.log('🧹 Clearing Fi Money data despite logout error (preserving user profile)...');
      sessionStorage.removeItem('demoMode');
      setIsAuthenticated(false);
      setSessionInfo(null);
      setShowPasscodeInput(false);
      setPhoneNumber('');
      setPasscode('');
      setAuthError('');
    }
  };

  // Removed handleNewPasscode function as timeout is removed

  if (isAuthenticated) {
    return (
      <Card className="p-6 bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <div>
              <h3 className="text-lg font-semibold text-green-800">
                🔗 Connected to Fi Money
              </h3>
              <p className="text-sm text-green-600">
                Real-time financial data active
                {sessionInfo?.expiresInMinutes && (
                  <span className="ml-2">
                    • Session expires in {Math.round(sessionInfo.expiresInMinutes)} minutes
                  </span>
                )}
              </p>
            </div>
          </div>
          <UnifiedButton
            onClick={handleLogout}
            variant="secondary"
            size="sm"
            className="text-gray-600 hover:text-gray-800"
          >
            Disconnect
          </UnifiedButton>
        </div>
      </Card>
    );
  }

  if (showPasscodeInput) {
    return (
      <Card className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <div className="space-y-4">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">
              🔐 Connect to Fi Money
            </h3>
            <p className="text-sm text-blue-600 mb-4">
              Enter your Fi Money registered phone number and passcode
            </p>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="Enter your Fi Money phone number"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white placeholder-gray-500"
                disabled={isConnecting}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Passcode
              </label>
              <input
                type="text"
                value={passcode}
                onChange={(e) => setPasscode(e.target.value)}
                placeholder="Enter passcode from Fi Money app"
                className="w-full px-3 py-2 border border-gray-300 bg-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                disabled={isConnecting}
                maxLength={6}
              />
            </div>
          </div>

          {authError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{authError}</p>
            </div>
          )}

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <p className="text-xs text-yellow-800 mb-2">
              📱 <strong>Get Passcode:</strong> Open Fi Money app → Net Worth Dashboard → Talk to AI → Get Passcode
            </p>
            <p className="text-xs text-yellow-700">
              💡 <strong>Tip:</strong> Copy the passcode from Fi Money app and paste it here for quick entry.
            </p>
          </div>

          <div className="flex space-x-3">
            <UnifiedButton
              onClick={handleAuthenticate}
              disabled={isConnecting || !phoneNumber.trim() || !passcode.trim()}
              variant="primary"
              className="flex-1"
              isLoading={isConnecting}
            >
              {isConnecting ? 'Connecting...' : 'Connect to Fi Money'}
            </UnifiedButton>
            
            <UnifiedButton
              onClick={() => setShowPasscodeInput(false)}
              variant="secondary"
              disabled={isConnecting}
            >
              Cancel
            </UnifiedButton>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6 bg-gradient-to-r from-gray-50 to-blue-50 border-gray-200">
      <div className="text-center space-y-4">
        <div className="w-16 h-16 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
          <span className="text-2xl">🏦</span>
        </div>
        
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Connect to Fi Money
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Get real-time access to your complete financial portfolio from Fi Money
          </p>
        </div>

        <div className="bg-[rgb(24,25,27)] border border-[rgba(204,166,149,0.2)] rounded-lg p-6">
          <h4 className="font-medium text-blue-800 mb-2">What you'll get:</h4>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Real-time net worth and asset allocation</li>
            <li>• Live mutual fund and stock holdings</li>
            <li>• Current bank balances and transactions</li>
            <li>• Credit score and loan details</li>
            <li>• EPF balance and contribution history</li>
          </ul>
        </div>

        <UnifiedButton
          onClick={handleConnectToFiMoney}
          variant="primary"
          size="lg"
          className="w-full"
        >
          🔗 Connect to Fi Money
        </UnifiedButton>

        <p className="text-xs text-gray-500">
          Secure connection • Data never stored • Session-based authentication
        </p>
      </div>
    </Card>
  );
};

export default FiMoneyAuth;