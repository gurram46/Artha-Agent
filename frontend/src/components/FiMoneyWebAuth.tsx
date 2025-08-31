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
  const [retryCount, setRetryCount] = useState(0);

  const maxPollingCount = 300; // 15 minutes of polling (3s intervals)
  
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
      // Clear any existing fallback mode on component mount
      mcpService.clearFallbackMode();
      console.log('🧹 Cleared any existing fallback mode on component mount');
      
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
    
    // Add retry logic
    let retryCount = 0;
    const maxRetries = 2;
    
    while (retryCount <= maxRetries) {
      try {
        // Preserve user signup data while clearing Fi Money session data
        console.log('🧹 Clearing previous Fi Money session before new authentication...');
        
        // Preserve user signup data
        const existingUserData = localStorage.getItem('userData');
        console.log('💾 Preserving user signup data:', existingUserData ? 'Found' : 'None');
        
        // Clear cached session to force fresh authentication with phone number and passcode
        try {
          console.log('🧹 Clearing cached Fi Money session to force fresh login...');
          await mcpService.clearCachedSession();
          console.log('✅ Cached Fi Money session cleared - fresh login required');
        } catch (clearError) {
          console.log('⚠️ Failed to clear cached session:', clearError);
        }
        
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
              // Monitor window for loading issues
              const windowCheckInterval = setInterval(() => {
                if (authWindow.current && authWindow.current.closed) {
                  clearInterval(windowCheckInterval);
                  if (authState === 'waiting') {
                    console.log('⚠️ Authentication window was closed by user');
                    setAuthError('Authentication was cancelled. Please try again if you want to connect to Fi Money.');
                    setAuthState('error');
                    stopPolling();
                  }
                }
              }, 1000);
              
              // Start polling for authentication completion
              startPolling();
              
              // Set a timeout to detect if credentials don't load
              setTimeout(async () => {
                if (authState === 'waiting' && authWindow.current && !authWindow.current.closed) {
                  console.log('⚠️ Authentication window may have loading issues - testing connectivity');
                  try {
                    // Test connectivity to help diagnose the issue
                    const connectivityTest = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8002'}/api/fi-auth/test-connectivity`);
                    const testResult = await connectivityTest.json();
                    
                    if (!testResult.server_reachable) {
                      console.log('❌ Fi Money server connectivity issue detected');
                      setAuthError(`Fi Money service connectivity issue: ${testResult.message}. Please check your internet connection and try again.`);
                      setAuthState('error');
                      closeAuthWindow();
                      stopPolling();
                    }
                  } catch (testError) {
                    console.log('⚠️ Could not test connectivity:', testError);
                  }
                }
              }, 10000); // Check after 10 seconds
            } else {
              setAuthError('Failed to open authentication window. Please check popup blocker settings and ensure popups are allowed for this site.');
              setAuthState('error');
            }
          } else {
            // Already authenticated
            setIsAuthenticated(true);
            setAuthState('success');
            onAuthSuccess();
          }
          // Success - break out of retry loop
          break;
        } else {
          // Check if fallback mode was enabled
          if (result.fallbackEnabled) {
            console.log('🔄 Fallback mode enabled, switching to demo mode');
            setAuthError('');
            await startDemoMode();
            break;
          } else if (retryCount < maxRetries) {
            // Retry on failure
            retryCount++;
            console.log(`⚠️ Authentication attempt ${retryCount} failed, retrying in 2 seconds...`);
            await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds before retry
            continue;
          } else {
            // Max retries reached
            const errorMsg = result.message || 'Authentication initiation failed. This may be due to network connectivity issues or Fi Money server timeout. Please try again in a few minutes.';
            setAuthError(errorMsg);
            setAuthState('error');
            onAuthError(errorMsg);
            break;
          }
        }
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Authentication initiation failed';
        
        // Retry on timeout errors
        if (errorMsg.includes('timeout') && retryCount < maxRetries) {
          retryCount++;
          console.log(`⚠️ Timeout error on attempt ${retryCount}, retrying in 3 seconds...`);
          await new Promise(resolve => setTimeout(resolve, 3000)); // Wait 3 seconds before retry
          continue;
        } else {
          // Don't retry or max retries reached
          const enhancedErrorMsg = `Authentication failed: ${errorMsg}. Please check your network connection and try again.`;
          setAuthError(enhancedErrorMsg);
          setAuthState('error');
          onAuthError(errorMsg);
          break;
        }
      }
    }
  };

  const startPolling = () => {
    setAuthState('polling');
    setPollingCount(0);
    
    let currentPollingCount = 0;
    
    pollingInterval.current = setInterval(async () => {
      try {
        // Increment and check polling count
        currentPollingCount += 1;
        setPollingCount(currentPollingCount);
        
        console.log(`🔄 Polling attempt ${currentPollingCount}/${maxPollingCount}`);
        
        if (currentPollingCount > maxPollingCount) {
          // Timeout after maximum attempts
          console.log('⏰ Authentication polling timeout after 15 minutes');
          setAuthError('Authentication timeout after 15 minutes. Please try again or check if you completed the authentication in the browser.');
          setAuthState('error');
          stopPolling();
          closeAuthWindow();
          onAuthError('Authentication timeout after 15 minutes');
          return;
        }
        
        // Always try completion endpoint first, then status if that fails
        let status;
        try {
          console.log('🔄 Checking authentication completion...');
          status = await mcpService.completeAuthentication();
        } catch (completionError) {
          console.log('⚠️ Completion check failed, trying status check...');
          status = await mcpService.checkAuthenticationStatus();
        }
        
        console.log('📊 Auth status result:', status);
        
        if (status.authenticated) {
          // Authentication successful!
          console.log('🎉 Fi Money authentication confirmed - calling onAuthSuccess');
          setIsAuthenticated(true);
          setSessionInfo(status);
          setAuthState('success');
          stopPolling();
          closeAuthWindow();
          setAuthError(''); // Clear any previous errors
          
          // Call onAuthSuccess to trigger parent component updates
          onAuthSuccess();
        } else if (status.message?.includes('expired')) {
          console.log('⚠️ Session expired');
          setAuthError('Session expired. Please try again.');
          setAuthState('error');
          stopPolling();
          closeAuthWindow();
          onAuthError('Session expired');
        } else if (status.message?.includes('timeout')) {
          console.log('⚠️ Authentication timeout');
          setAuthError('Authentication check timed out. Please try again.');
          setAuthState('error');
          stopPolling();
          closeAuthWindow();
          onAuthError('Authentication timeout');
        } else if (status.message?.includes('error') || status.message?.includes('failed')) {
          console.log('❌ Authentication failed:', status.message);
          setAuthError(`Authentication failed: ${status.message}`);
          setAuthState('error');
          stopPolling();
          closeAuthWindow();
          onAuthError(status.message);
        } else {
          console.log('⏳ Authentication still pending...');
        }
      } catch (error) {
        console.error('❌ Polling error:', error);
        const errorMsg = error instanceof Error ? error.message : 'Authentication check failed';
        
        // Provide specific guidance based on error type
        let userFriendlyError = errorMsg;
        if (errorMsg.includes('Network Error') || errorMsg.includes('fetch')) {
          userFriendlyError = 'Network connection issue. Please check your internet connection and try again.';
        } else if (errorMsg.includes('timeout')) {
          userFriendlyError = 'Connection timeout. The Fi Money service may be temporarily unavailable. Please try again in a few minutes.';
        } else if (errorMsg.includes('500') || errorMsg.includes('Internal Server Error')) {
          userFriendlyError = 'Fi Money service is temporarily unavailable. Please try again later.';
        } else if (errorMsg.includes('404')) {
          userFriendlyError = 'Authentication service not found. Please contact support if this persists.';
        }
        
        // Only fail after multiple consecutive errors or timeout
        if (currentPollingCount >= maxPollingCount) {
          console.log('❌ Max polling attempts reached with errors');
          setAuthError(`Authentication check failed: ${userFriendlyError}`);
          setAuthState('error');
          stopPolling();
          closeAuthWindow();
          onAuthError(userFriendlyError);
        } else {
          console.log(`⚠️ Polling error on attempt ${currentPollingCount}, continuing...`);
        }
      }
    }, 3000); // Poll every 3 seconds
  };

  const handleManualCheck = async () => {
    try {
      console.log('🔄 Manual authentication check requested');
      setAuthState('polling');
      setAuthError('');
      
      // Try completion endpoint first for most accurate check
      let status;
      try {
        console.log('🔄 Manual check: Trying completion endpoint...');
        status = await mcpService.completeAuthentication();
      } catch (completionError) {
        console.log('⚠️ Manual check: Completion failed, trying status check...');
        status = await mcpService.checkAuthenticationStatus();
      }
      
      console.log('📊 Manual check result:', status);
      
      if (status.authenticated) {
        console.log('🎉 Manual auth check successful - calling onAuthSuccess');
        setIsAuthenticated(true);
        setSessionInfo(status);
        setAuthState('success');
        stopPolling();
        closeAuthWindow();
        onAuthSuccess();
      } else {
        console.log('⏳ Authentication not yet complete');
        setAuthError('Authentication not yet complete. Please complete the process in the Fi Money window.');
        setAuthState('waiting');
      }
    } catch (error) {
      console.error('❌ Manual check failed:', error);
      setAuthError('Failed to check authentication status');
      setAuthState('error');
    }
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
      setIsDemoMode(false);
      setSessionInfo(null);
      setAuthState('initial');
      setLoginUrl('');
      setSessionId('');
      setAuthError('');
      setPollingCount(0);
      
      // Stop any ongoing processes
      stopPolling();
      closeAuthWindow();
      
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
      setIsDemoMode(false);
      setSessionInfo(null);
      setAuthState('initial');
      setLoginUrl('');
      setSessionId('');
      setAuthError('');
      setPollingCount(0);
      stopPolling();
      closeAuthWindow();
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
      console.log('🎉 Demo mode activated - calling onAuthSuccess');
      onAuthSuccess();
    } catch (error) {
      setAuthError('Failed to start demo mode');
      setAuthState('error');
      onAuthError('Failed to start demo mode');
    }
  };



  if (authState === 'success' && isAuthenticated) {
    return (
      <Card className="p-6 bg-[rgba(204,166,149,0.1)] border border-[rgba(204,166,149,0.3)] bg-black">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 ${isDemoMode ? 'bg-yellow-400' : 'bg-[#cca695]'} rounded-full animate-pulse`}></div>
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
      <Card className="p-6 bg-[rgba(204,166,149,0.1)] border border-[rgba(204,166,149,0.2)] bg-black">
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

          <div className="bg-[rgba(204,166,149,0.1)] border border-[rgba(204,166,149,0.2)] rounded-lg p-4">
            <div className="flex items-center mb-3">
              <div className="w-4 h-4 border-2 border-[#cca695] border-t-transparent rounded-full animate-spin mr-3"></div>
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
    const isConnectivityIssue = authError?.includes('connectivity') || authError?.includes('Network') || authError?.includes('timeout');
    const isPopupIssue = authError?.includes('popup') || authError?.includes('window');
    const isServiceIssue = authError?.includes('unavailable') || authError?.includes('500');
    
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
              <p className="text-sm text-red-400 mb-3">{authError}</p>
              
              {/* Troubleshooting guidance based on error type */}
              <div className="text-xs text-gray-300">
                <p className="font-medium text-yellow-400 mb-2">💡 Troubleshooting steps:</p>
                <ul className="space-y-1 list-disc list-inside">
                  {isPopupIssue && (
                    <>
                      <li>Allow popups for this website in your browser settings</li>
                      <li>Disable popup blockers temporarily</li>
                      <li>Try using a different browser (Chrome, Firefox, Safari)</li>
                    </>
                  )}
                  {isConnectivityIssue && (
                    <>
                      <li>Check your internet connection</li>
                      <li>Try refreshing the page and attempting again</li>
                      <li>Disable VPN if you're using one</li>
                      <li>Wait a few minutes and try again</li>
                    </>
                  )}
                  {isServiceIssue && (
                    <>
                      <li>Fi Money service may be temporarily down</li>
                      <li>Try again in a few minutes</li>
                      <li>Consider using Demo Mode to explore features</li>
                    </>
                  )}
                  {!isPopupIssue && !isConnectivityIssue && !isServiceIssue && (
                    <>
                      <li>Refresh the page and try again</li>
                      <li>Clear your browser cache and cookies</li>
                      <li>Try using an incognito/private browsing window</li>
                      <li>Ensure you have a stable internet connection</li>
                    </>
                  )}
                </ul>
              </div>
            </div>
          )}

          <div className="flex space-x-3">
            <UnifiedButton
              onClick={handleRetry}
              variant="primary"
              className="flex-1"
            >
              🔄 Try Again
            </UnifiedButton>
            
            {(isConnectivityIssue || isServiceIssue) && (
              <UnifiedButton
                onClick={startDemoMode}
                variant="secondary"
                className="flex-1"
              >
                🎭 Use Demo Mode
              </UnifiedButton>
            )}
          </div>
          
          <div className="text-center">
            <p className="text-xs text-gray-400">
              Still having issues? Try refreshing the page or contact support.
            </p>
          </div>
        </div>
      </Card>
    );
  }

  // Initial state
  return (
    <Card className="p-6 bg-black border border-[rgba(204,166,149,0.2)]">
      <div className="text-center space-y-4">
        <div className="w-16 h-16 mx-auto bg-[rgba(204,166,149,0.1)] border border-[rgba(204,166,149,0.2)] rounded-full flex items-center justify-center">
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

        <div className="bg-[rgba(204,166,149,0.1)] border border-[rgba(204,166,149,0.2)] rounded-lg p-4 text-left">
          <h4 className="font-medium text-white mb-2">What you'll get:</h4>
          <ul className="text-sm text-gray-300 space-y-1">
            <li>• Real-time net worth and asset allocation</li>
            <li>• Live mutual fund and stock holdings</li>
            <li>• Current bank balances and transactions</li>
            <li>• Credit score and loan details</li>
            <li>• EPF balance and contribution history</li>
          </ul>
        </div>

        <div className="bg-[rgba(204,166,149,0.1)] border border-[rgba(204,166,149,0.2)] rounded-lg p-4 text-left">
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
            disabled={authState === 'initiating'}
          >
            {authState === 'initiating' ? (
              <div className="flex items-center justify-center">
                <span>Connecting to Fi Money...</span>
                <span className="ml-2 animate-spin">⏳</span>
              </div>
            ) : '🌐 Connect to Fi Money'}
          </UnifiedButton>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[rgba(204,166,149,0.2)]"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-black text-gray-400">OR</span>
            </div>
          </div>

          <UnifiedButton
            onClick={startDemoMode}
            variant="secondary"
            size="lg"
            className="w-full border-2 border-dashed border-[rgba(204,166,149,0.2)] hover:border-[rgba(204,166,149,0.5)]"
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