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
      <Card className="p-6 bg-gradient-to-r from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.1)] border border-[rgba(0,184,153,0.3)] bg-black">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 ${isDemoMode ? 'bg-yellow-400' : 'bg-[rgb(0,184,153)]'} rounded-full animate-pulse`}></div>
            <div>
              <h3 className="text-lg font-semibold text-white">
                {isDemoMode ? '🎭 Demo Mode Active' : '🌐 Connected to Fi Money'}
              </h3>
              <p className="text-sm text-gray-300">
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
            className="text-gray-300 hover:text-white"
          >
            Disconnect
          </UnifiedButton>
        </div>
      </Card>
    );
  }

  if (authState === 'waiting' || authState === 'polling') {
    return (
      <Card className="p-6 bg-gradient-to-r from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.1)] border border-[rgba(0,184,153,0.2)] bg-black">
        <div className="space-y-4">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-white mb-2">
              🌐 Authenticating with Fi Money
            </h3>
            <p className="text-sm text-gray-300 mb-4">
              {authState === 'waiting' 
                ? 'Please complete authentication in the Fi Money window'
                : `Checking authentication status... (${pollingCount}/${maxPollingCount})`
              }
            </p>
          </div>

          <div className="bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-lg p-4">
            <div className="flex items-center mb-3">
              <div className="w-4 h-4 border-2 border-[rgb(0,184,153)] border-t-transparent rounded-full animate-spin mr-3"></div>
              <span className="text-sm font-medium text-white">Authentication in progress</span>
            </div>
            <ol className="text-xs text-gray-300 space-y-1">
              <li>1. ✅ Fi Money authentication window opened</li>
              <li>2. 🔄 Complete authentication in Fi Money app</li>
              <li>3. ⏳ System will automatically detect completion</li>
            </ol>
          </div>

          {authState === 'waiting' && (
            <div className="bg-[rgba(245,158,11,0.1)] border border-[rgba(245,158,11,0.2)] rounded-lg p-3">
              <p className="text-xs text-yellow-400">
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
      <Card className="p-6 bg-gradient-to-r from-[rgba(239,68,68,0.1)] to-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)] bg-black">
        <div className="space-y-4">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-white mb-2">
              ❌ Authentication Error
            </h3>
          </div>

          {authError && (
            <div className="p-3 bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)] rounded-lg">
              <p className="text-sm text-red-400">{authError}</p>
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
    <Card className="p-6 bg-black border border-[rgba(0,184,153,0.2)]">
      <div className="text-center space-y-4">
        <div className="w-16 h-16 mx-auto bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-full flex items-center justify-center">
          <span className="text-2xl">🌐</span>
        </div>
        
        <div>
          <h3 className="text-lg font-semibold text-white mb-2">
            Connect to Fi Money
          </h3>
          <p className="text-sm text-gray-300 mb-4">
            Secure web-based authentication with your Fi Money account
          </p>
        </div>

        <div className="bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-lg p-4 text-left">
          <h4 className="font-medium text-white mb-2">What you'll get:</h4>
          <ul className="text-sm text-gray-300 space-y-1">
            <li>• Real-time net worth and asset allocation</li>
            <li>• Live mutual fund and stock holdings</li>
            <li>• Current bank balances and transactions</li>
            <li>• Credit score and loan details</li>
            <li>• EPF balance and contribution history</li>
          </ul>
        </div>

        <div className="bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-lg p-4 text-left">
          <h4 className="font-medium text-white mb-2">How it works:</h4>
          <ol className="text-sm text-gray-300 space-y-1">
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
              <div className="w-full border-t border-[rgba(0,184,153,0.2)]"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-black text-gray-400">OR</span>
            </div>
          </div>

          <UnifiedButton
            onClick={startDemoMode}
            variant="secondary"
            size="lg"
            className="w-full border-2 border-dashed border-[rgba(0,184,153,0.2)] hover:border-[rgba(0,184,153,0.5)]"
          >
            🎭 Try Demo Mode
          </UnifiedButton>
        </div>

        <p className="text-xs text-gray-400">
          Demo mode uses sample data • No authentication required • Perfect for exploring
        </p>
      </div>
    </Card>
  );
};

export default FiMoneyWebAuth;