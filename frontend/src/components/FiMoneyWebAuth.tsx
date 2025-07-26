'use client';

import React, { useState, useEffect, useRef } from 'react';
import { UnifiedButton } from './ui/UnifiedButton';
import { Card } from './ui/card';
import MCPDataService from '../services/mcpDataService';

interface FiMoneyWebAuthProps {
  onAuthSuccess: () => void;
  onAuthError: (error: string) => void;
}

const FiMoneyWebAuth: React.FC<FiMoneyWebAuthProps> = ({ onAuthSuccess, onAuthError }) => {
  const [authState, setAuthState] = useState<'initial' | 'initiating' | 'waiting' | 'polling' | 'success' | 'error' | 'demo'>('initial');
  const [loginUrl, setLoginUrl] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [authError, setAuthError] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessionInfo, setSessionInfo] = useState<any>(null);
  const [pollingCount, setPollingCount] = useState(0);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const maxPollingCount = 60; // 5 minutes of polling (5s intervals)
  
  const pollingInterval = useRef<NodeJS.Timeout | null>(null);
  const authWindow = useRef<Window | null>(null);

  const mcpService = MCPDataService.getInstance();

  useEffect(() => {
    checkInitialAuthStatus();
    return () => {
      stopPolling();
      closeAuthWindow();
    };
  }, []);

  const checkInitialAuthStatus = async () => {
    try {
      const status = await mcpService.checkAuthenticationStatus();
      setIsAuthenticated(status.authenticated);
      setSessionInfo(status);
      
      if (status.authenticated) {
        setAuthState('success');
        onAuthSuccess();
      }
    } catch (error) {
      console.error('Initial auth status check failed:', error);
    }
  };

  const stopPolling = () => {
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
      pollingInterval.current = null;
    }
  };

  const closeAuthWindow = () => {
    if (authWindow.current) {
      authWindow.current.close();
      authWindow.current = null;
    }
  };

  const startAuthentication = async () => {
    setAuthState('initiating');
    setAuthError('');
    
    try {
      const result = await mcpService.initiateWebAuthentication();
      
      if (result.success) {
        if (result.loginRequired && result.loginUrl) {
          setLoginUrl(result.loginUrl);
          setSessionId(result.sessionId || '');
          setAuthState('waiting');
          
          // Open authentication window
          const width = 500;
          const height = 700;
          const left = (window.screen.width / 2) - (width / 2);
          const top = (window.screen.height / 2) - (height / 2);
          
          authWindow.current = window.open(
            result.loginUrl,
            'fiMoneyAuth',
            `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
          );
          
          if (authWindow.current) {
            // Start polling for authentication completion
            startPolling();
          } else {
            setAuthError('Failed to open authentication window. Please check popup blocker settings.');
            setAuthState('error');
          }
        } else {
          // Already authenticated
          setIsAuthenticated(true);
          setAuthState('success');
          onAuthSuccess();
        }
      } else {
        setAuthError(result.message);
        setAuthState('error');
        onAuthError(result.message);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Authentication initiation failed';
      setAuthError(errorMsg);
      setAuthState('error');
      onAuthError(errorMsg);
    }
  };

  const startPolling = () => {
    setAuthState('polling');
    setPollingCount(0);
    
    pollingInterval.current = setInterval(async () => {
      try {
        const status = await mcpService.checkAuthenticationStatus();
        setPollingCount(prev => prev + 1);
        
        if (status.authenticated) {
          // Authentication successful!
          setIsAuthenticated(true);
          setSessionInfo(status);
          setAuthState('success');
          stopPolling();
          closeAuthWindow();
          onAuthSuccess();
        } else if (pollingCount >= maxPollingCount) {
          // Timeout after 5 minutes
          setAuthError('Authentication timeout. Please try again.');
          setAuthState('error');
          stopPolling();
          closeAuthWindow();
          onAuthError('Authentication timeout');
        }
      } catch (error) {
        console.error('Polling error:', error);
        if (pollingCount >= maxPollingCount) {
          setAuthError('Authentication check failed. Please try again.');
          setAuthState('error');
          stopPolling();
          closeAuthWindow();
        }
      }
    }, 5000); // Poll every 5 seconds
  };

  const handleManualCheck = async () => {
    try {
      setAuthState('polling');
      const status = await mcpService.checkAuthenticationStatus();
      
      if (status.authenticated) {
        setIsAuthenticated(true);
        setSessionInfo(status);
        setAuthState('success');
        stopPolling();
        closeAuthWindow();
        onAuthSuccess();
      } else {
        setAuthError('Authentication not yet complete. Please complete the process in the Fi Money window.');
        setAuthState('waiting');
      }
    } catch (error) {
      setAuthError('Failed to check authentication status');
      setAuthState('error');
    }
  };

  const handleLogout = async () => {
    try {
      await mcpService.logout();
      mcpService.setDemoMode(false);
      sessionStorage.removeItem('demoMode');
      setIsAuthenticated(false);
      setIsDemoMode(false);
      setSessionInfo(null);
      setAuthState('initial');
      setLoginUrl('');
      setSessionId('');
      setAuthError('');
      stopPolling();
      closeAuthWindow();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const handleRetry = () => {
    setAuthState('initial');
    setAuthError('');
    setLoginUrl('');
    setSessionId('');
    setPollingCount(0);
    setIsDemoMode(false);
    stopPolling();
    closeAuthWindow();
  };

  const startDemoMode = async () => {
    setAuthState('demo');
    setIsDemoMode(true);
    setAuthError('');
    
    try {
      // Enable demo mode in the data service
      mcpService.setDemoMode(true);
      
      // Store demo mode in session storage
      sessionStorage.setItem('demoMode', 'true');
      
      // Mark as authenticated in demo mode
      setIsAuthenticated(true);
      setSessionInfo({ 
        authenticated: true, 
        isDemo: true,
        message: 'Using demo data'
      });
      
      setAuthState('success');
      onAuthSuccess();
    } catch (error) {
      setAuthError('Failed to start demo mode');
      setAuthState('error');
      onAuthError('Failed to start demo mode');
    }
  };

  if (authState === 'success' && isAuthenticated) {
    return (
      <Card className="p-6 bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 ${isDemoMode ? 'bg-yellow-500' : 'bg-green-500'} rounded-full animate-pulse`}></div>
            <div>
              <h3 className="text-lg font-semibold text-green-800">
                {isDemoMode ? '🎭 Demo Mode Active' : '🌐 Connected to Fi Money'}
              </h3>
              <p className="text-sm text-green-600">
                {isDemoMode ? 'Using sample financial data' : 'Real-time financial data active'}
                {!isDemoMode && sessionInfo?.expiresInMinutes && (
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

  if (authState === 'waiting' || authState === 'polling') {
    return (
      <Card className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <div className="space-y-4">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">
              🌐 Authenticating with Fi Money
            </h3>
            <p className="text-sm text-blue-600 mb-4">
              {authState === 'waiting' 
                ? 'Please complete authentication in the Fi Money window'
                : `Checking authentication status... (${pollingCount}/${maxPollingCount})`
              }
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-3"></div>
              <span className="text-sm font-medium text-blue-800">Authentication in progress</span>
            </div>
            <ol className="text-xs text-blue-700 space-y-1">
              <li>1. ✅ Fi Money authentication window opened</li>
              <li>2. 🔄 Complete authentication in Fi Money app</li>
              <li>3. ⏳ System will automatically detect completion</li>
            </ol>
          </div>

          {authState === 'waiting' && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-xs text-yellow-800">
                📱 <strong>Steps:</strong> Complete authentication in the Fi Money window that opened. 
                This system will automatically detect when you're authenticated.
              </p>
            </div>
          )}

          <div className="flex space-x-3">
            <UnifiedButton
              onClick={handleManualCheck}
              variant="primary"
              className="flex-1"
              disabled={authState === 'polling'}
            >
              {authState === 'polling' ? 'Checking...' : 'Check Authentication'}
            </UnifiedButton>
            
            <UnifiedButton
              onClick={handleRetry}
              variant="secondary"
            >
              Cancel
            </UnifiedButton>
          </div>
        </div>
      </Card>
    );
  }

  if (authState === 'error') {
    return (
      <Card className="p-6 bg-gradient-to-r from-red-50 to-orange-50 border-red-200">
        <div className="space-y-4">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-red-800 mb-2">
              ❌ Authentication Error
            </h3>
          </div>

          {authError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{authError}</p>
            </div>
          )}

          <div className="flex space-x-3">
            <UnifiedButton
              onClick={handleRetry}
              variant="primary"
              className="flex-1"
            >
              Try Again
            </UnifiedButton>
          </div>
        </div>
      </Card>
    );
  }

  // Initial state
  return (
    <Card className="p-6 bg-gradient-to-r from-gray-50 to-blue-50 border-gray-200">
      <div className="text-center space-y-4">
        <div className="w-16 h-16 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
          <span className="text-2xl">🌐</span>
        </div>
        
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Connect to Fi Money
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Secure web-based authentication with your Fi Money account
          </p>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left">
          <h4 className="font-medium text-blue-800 mb-2">What you'll get:</h4>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Real-time net worth and asset allocation</li>
            <li>• Live mutual fund and stock holdings</li>
            <li>• Current bank balances and transactions</li>
            <li>• Credit score and loan details</li>
            <li>• EPF balance and contribution history</li>
          </ul>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-left">
          <h4 className="font-medium text-green-800 mb-2">How it works:</h4>
          <ol className="text-sm text-green-700 space-y-1">
            <li>1. Click "Connect to Fi Money" below</li>
            <li>2. Fi Money authentication window will open</li>
            <li>3. Complete authentication in Fi Money app</li>
            <li>4. System automatically detects completion</li>
            <li>5. Access your real-time financial data!</li>
          </ol>
        </div>

        <div className="space-y-3">
          <UnifiedButton
            onClick={startAuthentication}
            variant="primary"
            size="lg"
            className="w-full"
            isLoading={authState === 'initiating'}
          >
            {authState === 'initiating' ? 'Connecting...' : '🌐 Connect to Fi Money'}
          </UnifiedButton>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gray-50 text-gray-500">OR</span>
            </div>
          </div>

          <UnifiedButton
            onClick={startDemoMode}
            variant="secondary"
            size="lg"
            className="w-full border-2 border-dashed border-gray-300 hover:border-gray-400"
          >
            🎭 Try Demo Mode
          </UnifiedButton>
        </div>

        <p className="text-xs text-gray-500">
          Demo mode uses sample data • No authentication required • Perfect for exploring
        </p>
      </div>
    </Card>
  );
};

export default FiMoneyWebAuth;