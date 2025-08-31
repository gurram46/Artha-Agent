'use client';

import { useEffect, useState } from 'react';
import Dashboard from '@/components/Dashboard';
import ChatInterface from '@/components/ChatInterface';
import FinancialOverview from '@/components/FinancialOverview';
import HydrationProvider from '@/components/HydrationProvider';
import EnhancedFinancialStats from '@/components/EnhancedFinancialStats';
import EnhancedLandingPage from '@/components/EnhancedLandingPage';
import UnifiedCard from '@/components/ui/UnifiedCard';
import UnifiedButton from '@/components/ui/UnifiedButton';
import FiMoneyWebAuth from '@/components/FiMoneyWebAuth';
import SignupForm from '@/components/SignupForm';
import UserProfileModal from '@/components/UserProfileModal';

import { designSystem } from '@/styles/designSystem';
import { AppProvider, useAppContext, useAuth, useFinancialData, useUI } from '@/contexts/AppContext';
import MCPDataService from '@/services/mcpDataService';
import { ArthaLogo } from '@/components/ui/ArthaLogo';

// Helper function to get user initials from full_name
const getInitials = (userData: any): string => {
  if (userData?.full_name) {
    const nameParts = userData.full_name.split(' ');
    if (nameParts.length >= 2) {
      return `${nameParts[0].charAt(0)}${nameParts[1].charAt(0)}`;
    } else {
      return nameParts[0].charAt(0);
    }
  }
  return 'U';
};

// Helper function to get user's first name from full_name
const getFirstName = (userData: any): string => {
  if (userData?.full_name) {
    return userData.full_name.split(' ')[0];
  }
  return 'User';
};

// Helper function to get user's full name
const getFullName = (userData: any): string => {
  return userData?.full_name || 'User';
};

// Main component wrapped with Context Provider
function HomeContent() {
  const { state, dispatch } = useAppContext();
  const { 
    isAuthenticated, 
    isCheckingAuth, 
    isDemoMode, 
    userData, 
    isLoggedIn, 
    authError 
  } = useAuth();
  
  const { 
    financialData, 
    isLoading, 
    cacheStatus 
  } = useFinancialData();
  
  const { 
    activeTab, 
    showSignupForm, 
    showUserProfile 
  } = useUI();

  const mcpService = MCPDataService.getInstance();

  // Force landing page on fresh visits - track if user has visited in this session
  const [hasVisited, setHasVisited] = useState(true);
  
  // Fresh start detection - check if this is a completely new session (client-side only)
  const [isFreshStart, setIsFreshStart] = useState(false);

  // Force landing page logic for fresh visits
  useEffect(() => {
    const visitFlag = sessionStorage.getItem('hasVisited');
    if (!visitFlag) {
      console.log('🆕 First time visit in this session - ensuring landing page shows');
      // First time visit in this session - ensure landing page shows
      sessionStorage.setItem('hasVisited', 'true');
      setHasVisited(false);
      // Clear any stale auth states
      dispatch({ type: 'SET_AUTHENTICATED', payload: false });
      dispatch({ type: 'SET_LOGGED_IN', payload: false });
      dispatch({ type: 'SET_DEMO_MODE', payload: false });
    }
  }, [dispatch]);
  
  useEffect(() => {
    // Only run on client-side to avoid SSR issues
    if (typeof window !== 'undefined') {
      const freshStart = !localStorage.getItem('userData') && 
                        !sessionStorage.getItem('demoMode') && 
                        !sessionStorage.getItem('isAuthenticated');
      setIsFreshStart(freshStart);
    }
  }, []);

  // Clear session storage on fresh loads to ensure clean state
  useEffect(() => {
    const isFirstLoad = sessionStorage.getItem('isFirstLoad') !== 'true';
    if (isFirstLoad) {
      console.log('🧹 Fresh load detected - clearing session storage for clean state');
      // Clear all session storage on first load to ensure clean state
      sessionStorage.clear();
      // Don't clear localStorage as it contains user profile data
      sessionStorage.setItem('isFirstLoad', 'true');
    }
  }, []);

  useEffect(() => {
    checkAuthenticationAndFetchData();
  }, []);

  // Comprehensive debug logging to track authentication state flow
  useEffect(() => {
    console.log('=== AUTH STATE DEBUG ===');
    console.log('isLoggedIn:', isLoggedIn);
    console.log('isAuthenticated:', isAuthenticated);
    console.log('isDemoMode:', isDemoMode);
    console.log('isCheckingAuth:', isCheckingAuth);
    console.log('userData exists:', !!userData);
    console.log('userData:', userData);
    console.log('sessionStorage demoMode:', sessionStorage.getItem('demoMode'));
    console.log('sessionStorage isAuthenticated:', sessionStorage.getItem('isAuthenticated'));
    console.log('sessionStorage hasVisited:', sessionStorage.getItem('hasVisited'));
    console.log('localStorage userData:', localStorage.getItem('userData'));
    console.log('hasVisited state:', hasVisited);
    console.log('========================');
  }, [isLoggedIn, isAuthenticated, isDemoMode, isCheckingAuth, userData, hasVisited]);

  useEffect(() => {
    if (userData?.email && isAuthenticated && !isDemoMode) {
      checkCacheStatus();
    }
  }, [userData, isAuthenticated, isDemoMode]);

  // Handle demo mode activation
  useEffect(() => {
    if (isDemoMode && isAuthenticated && !financialData) {
      console.log('🎭 Demo mode activated - loading demo data...');
      fetchFinancialData();
    }
  }, [isDemoMode, isAuthenticated, financialData]);

  // Ensure state consistency - if userData exists but isLoggedIn is false, fix it
  // Add a small delay to prevent rapid state changes during initialization
  useEffect(() => {
    if (userData && !isLoggedIn && !isDemoMode && !isCheckingAuth) {
      const timeoutId = setTimeout(() => {
        console.log('🔧 State consistency fix: userData exists but isLoggedIn is false, setting isLoggedIn to true');
        dispatch({ type: 'SET_LOGGED_IN', payload: true });
      }, 50); // Small delay to ensure stable state
      
      return () => clearTimeout(timeoutId);
    }
  }, [userData, isLoggedIn, isDemoMode, isCheckingAuth]);

  const checkAuthenticationAndFetchData = async () => {
    dispatch({ type: 'SET_CHECKING_AUTH', payload: true });
    try {
      // Check if demo mode is enabled first
      const demoMode = sessionStorage.getItem('demoMode') === 'true';
      if (demoMode) {
        console.log('🎭 Demo mode detected');
        dispatch({ type: 'SET_DEMO_MODE', payload: true });
        mcpService.setDemoMode(true);
        dispatch({ type: 'SET_AUTHENTICATED', payload: true });
        await fetchFinancialData();
        return;
      }

      // Check if already authenticated with Fi Money
      const authStatus = await mcpService.checkAuthenticationStatus();
      
      if (authStatus.authenticated) {
        console.log('✅ Already authenticated with Fi Money MCP');
        dispatch({ type: 'SET_AUTHENTICATED', payload: true });
        dispatch({ type: 'SET_DEMO_MODE', payload: authStatus.isDemo || false });
        await fetchFinancialData();
      } else {
        console.log('🔐 Fi Money authentication required');
        dispatch({ type: 'SET_AUTHENTICATED', payload: false });
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      dispatch({ type: 'SET_AUTHENTICATED', payload: false });
      dispatch({ type: 'SET_LOADING', payload: false });
    }
    dispatch({ type: 'SET_CHECKING_AUTH', payload: false });
  };

  const fetchFinancialData = async () => {
    try {
      console.log('🔄 Loading real-time financial data from Fi Money MCP...');
      console.log('🔍 fetchFinancialData - Current auth state before fetch:', isAuthenticated);
      dispatch({ type: 'SET_LOADING', payload: true });
      
      const result = await mcpService.loadMCPData();
      console.log('📊 MCP Data result:', { success: result.success, hasData: !!result.data, authRequired: result.authRequired });
      
      if (result.success && result.data) {
        console.log('✅ Real-time financial data loaded successfully from Fi Money');
        const transformedData = mcpService.transformToPortfolioFormat(result.data);
        dispatch({ type: 'SET_FINANCIAL_DATA', payload: transformedData });
        dispatch({ type: 'SET_AUTH_ERROR', payload: '' });
        // Ensure authentication state remains true after successful data fetch
        console.log('🔄 Ensuring authentication state remains true after data fetch');
        dispatch({ type: 'SET_AUTHENTICATED', payload: true });
      } else if (result.authRequired) {
        console.log('🔐 Fi Money authentication required - setting auth to false');
        dispatch({ type: 'SET_AUTHENTICATED', payload: false });
        dispatch({ type: 'SET_AUTH_ERROR', payload: result.error || 'Please authenticate with Fi Money' });
      } else {
        console.log('❌ Data fetch failed but not auth error:', result.error);
        throw new Error(result.error || 'Failed to load financial data from Fi Money');
      }
      
    } catch (error) {
      console.error('💥 Error loading financial data from Fi Money:', error);
      dispatch({ type: 'SET_FINANCIAL_DATA', payload: null });
      // Only set authentication to false if it's specifically an auth error
      // Don't reset auth state for other types of errors
      if (error instanceof Error && (error.message.includes('authentication') || error.message.includes('expired'))) {
        console.log('🔐 Authentication error detected, resetting auth state');
        dispatch({ type: 'SET_AUTHENTICATED', payload: false });
        dispatch({ type: 'SET_AUTH_ERROR', payload: 'Session expired. Please authenticate again.' });
      } else {
        console.log('⚠️ Non-authentication error, keeping auth state');
        dispatch({ type: 'SET_AUTH_ERROR', payload: 'Failed to load data. Please try again.' });
      }
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
      console.log('🔍 fetchFinancialData completed - Final auth state:', isAuthenticated);
    }
  };

  const checkCacheStatus = async () => {
    if (userData?.email && !isDemoMode) {
      try {
        const status = await mcpService.getCacheStatus();
        dispatch({ type: 'SET_CACHE_STATUS', payload: status });
      } catch (error) {
        console.error('Failed to check cache status:', error);
        dispatch({ type: 'SET_CACHE_STATUS', payload: null });
      }
    }
  };

  const clearAllUserData = async () => {
    console.log('🧹 Clearing all previous user data before new authentication...');
    
    try {
      // Clear any existing secure cache (for any previous user)
      const existingUserData = localStorage.getItem('userData');
      if (existingUserData) {
        const parsedData = JSON.parse(existingUserData);
        if (parsedData?.email) {
          console.log('🗑️ Clearing secure cache for previous user:', parsedData.email);
          mcpService.setUserEmail(parsedData.email);
          await mcpService.invalidateSecureCache();
        }
      }
      
      // Logout from any existing Fi Money session
      console.log('🔐 Logging out from any existing Fi Money session...');
      await mcpService.logout();
      
      // Clear all frontend storage
      console.log('🧹 Clearing all frontend storage...');
      localStorage.clear();
      sessionStorage.clear();
      
      // Reset all state variables
      dispatch({ type: 'CLEAR_ALL_DATA' });
      
      console.log('✅ All previous user data cleared successfully');
    } catch (error) {
      console.error('⚠️ Error clearing previous user data:', error);
      // Continue with authentication even if cleanup fails
    }
  };

  const clearProfile = () => {
    // Only clear user profile data, keep Fi Money authentication
    localStorage.removeItem('userData');
    dispatch({ type: 'CLEAR_USER_PROFILE' });
  };

  const handleAuthSuccess = async () => {
    console.log('✅ Fi Money authentication successful - starting redirect process');
    console.log('🔍 Initial state - isAuthenticated:', isAuthenticated, 'isLoggedIn:', isLoggedIn, 'isLoading:', isLoading);
    
    try {
      // Clear any existing errors first
      dispatch({ type: 'SET_AUTH_ERROR', payload: '' });
      
      // Set authentication state IMMEDIATELY when authentication succeeds
      console.log('🔄 Setting authentication state to true IMMEDIATELY after successful auth...');
      dispatch({ type: 'SET_AUTHENTICATED', payload: true });
      
      dispatch({ type: 'SET_LOADING', payload: true });
      console.log('🔄 Set isLoading to true');
      
      // Check if demo mode was enabled
      const demoMode = sessionStorage.getItem('demoMode') === 'true';
      dispatch({ type: 'SET_DEMO_MODE', payload: demoMode });
      console.log('🎭 Demo mode:', demoMode);
      
      // Set user email for cache operations (if user is logged in)
      if (userData?.email) {
        console.log('👤 Setting user email for cache operations:', userData.email);
        mcpService.setUserEmail(userData.email);
        await checkCacheStatus();
      } else {
        console.log('🔄 Guest user - proceeding without cache operations');
      }
      
      // Now fetch financial data with authentication already set
      console.log('🔄 Fetching financial data after authentication state is set...');
      const result = await mcpService.loadMCPData();
      console.log('📊 MCP Data result:', { success: result.success, hasData: !!result.data, authRequired: result.authRequired });
      
      if (result.success && result.data) {
        console.log('✅ Real-time financial data loaded successfully from Fi Money');
        const transformedData = mcpService.transformToPortfolioFormat(result.data);
        dispatch({ type: 'SET_FINANCIAL_DATA', payload: transformedData });
        dispatch({ type: 'SET_AUTH_ERROR', payload: '' });
        console.log('🎉 Authentication and data loading completed successfully');
      } else if (result.authRequired) {
        console.log('⚠️ Authentication verification failed - data fetch requires re-auth');
        dispatch({ type: 'SET_AUTHENTICATED', payload: false });
        dispatch({ type: 'SET_AUTH_ERROR', payload: 'Authentication verification failed. Please try again.' });
      } else {
        console.log('⚠️ Data fetch failed but authentication state remains true');
        dispatch({ type: 'SET_AUTH_ERROR', payload: 'Authentication successful, but data loading failed. Please refresh to try again.' });
      }
      
    } catch (error) {
      console.error('❌ Error in handleAuthSuccess:', error);
      dispatch({ type: 'SET_AUTH_ERROR', payload: 'Failed to complete authentication. Please try again.' });
      // Only reset auth state if it's specifically an auth-related error
      if (error instanceof Error && (error.message.includes('authentication') || error.message.includes('unauthorized'))) {
        dispatch({ type: 'SET_AUTHENTICATED', payload: false });
        console.log('❌ Reset authentication state due to auth error');
      } else {
        console.log('⚠️ Keeping authentication state true despite data error');
      }
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
      console.log('🔄 Set isLoading to false - Auth flow completed');
    }
  };

  const handleAuthError = (error: string) => {
    console.error('❌ Fi Money authentication failed:', error);
    dispatch({ type: 'SET_AUTH_ERROR', payload: error });
    dispatch({ type: 'SET_AUTHENTICATED', payload: false });
    
    // Don't automatically enable demo mode on auth errors
    // Let user choose what to do next
    console.log('⚠️ Authentication error - user can choose to retry or try demo mode');
  };

  const handleSignupSuccess = async (newUserData: any) => {
    try {
      console.log('🎯 handleSignupSuccess called with authenticated user:', newUserData);
      console.log('🔍 Current state before signup success:', { isLoggedIn, userData, isAuthenticated });
      
      // Save new user data to localStorage for persistence FIRST
      localStorage.setItem('userData', JSON.stringify(newUserData));
      console.log('💾 Saved authenticated user to localStorage:', JSON.stringify(newUserData));
      
      // Set hasVisited to true to prevent landing page from showing
      sessionStorage.setItem('hasVisited', 'true');
      setHasVisited(true);
      
      // Dispatch state updates in the correct order
      console.log('🔄 Dispatching state updates...');
      dispatch({ type: 'SET_USER_DATA', payload: newUserData });
      dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: false });
      
      // Set both logged in AND authenticated since user is now properly registered
      dispatch({ type: 'SET_LOGGED_IN', payload: true });
      dispatch({ type: 'SET_AUTHENTICATED', payload: true }); // User is now authenticated
      dispatch({ type: 'SET_FINANCIAL_DATA', payload: null });
      dispatch({ type: 'SET_AUTH_ERROR', payload: '' });
      
      console.log('✅ User registered and authenticated successfully! Proceeding to dashboard...');
      
      // Since user is now authenticated, fetch financial data
      await fetchFinancialData();
      
    } catch (error) {
      console.error('⚠️ Error during signup success handling:', error);
      // Continue with signup even if cleanup fails
      localStorage.setItem('userData', JSON.stringify(newUserData));
      // Set hasVisited to true to prevent landing page from showing
      sessionStorage.setItem('hasVisited', 'true');
      setHasVisited(true);
      dispatch({ type: 'SET_USER_DATA', payload: newUserData });
      dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: false });
      dispatch({ type: 'SET_AUTHENTICATED', payload: false });
      dispatch({ type: 'SET_FINANCIAL_DATA', payload: null });
      dispatch({ type: 'SET_AUTH_ERROR', payload: '' });
      dispatch({ type: 'SET_LOGGED_IN', payload: true });
    }
  };

  const handleLoginSuccess = async (userData: any) => {
    try {
      console.log('🎯 handleLoginSuccess called with user:', userData);
      console.log('🔍 Current state before login success:', { isLoggedIn, isAuthenticated });
      
      // Save user data to localStorage for persistence
      localStorage.setItem('userData', JSON.stringify(userData));
      console.log('💾 Saved logged in user to localStorage:', JSON.stringify(userData));
      
      // Set hasVisited to true to prevent landing page from showing
      sessionStorage.setItem('hasVisited', 'true');
      setHasVisited(true);
      
      // Dispatch state updates
      console.log('🔄 Dispatching login state updates...');
      dispatch({ type: 'SET_USER_DATA', payload: userData });
      dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: false });
      dispatch({ type: 'SET_LOGGED_IN', payload: true });
      
      // Important: Do NOT set authenticated to true here
      // User needs to authenticate with Fi Money first
      dispatch({ type: 'SET_AUTHENTICATED', payload: false });
      dispatch({ type: 'SET_FINANCIAL_DATA', payload: null });
      dispatch({ type: 'SET_AUTH_ERROR', payload: '' });
      
      console.log('✅ User logged in successfully! Redirecting to Fi Money authentication...');
      
    } catch (error) {
      console.error('⚠️ Error during login success handling:', error);
      // Continue with login even if there are errors
      localStorage.setItem('userData', JSON.stringify(userData));
      // Set hasVisited to true to prevent landing page from showing
      sessionStorage.setItem('hasVisited', 'true');
      setHasVisited(true);
      dispatch({ type: 'SET_USER_DATA', payload: userData });
      dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: false });
      dispatch({ type: 'SET_LOGGED_IN', payload: true });
      dispatch({ type: 'SET_AUTHENTICATED', payload: false });
      dispatch({ type: 'SET_FINANCIAL_DATA', payload: null });
      dispatch({ type: 'SET_AUTH_ERROR', payload: '' });
    }
  };

  const handleProfileClick = () => {
    if (isLoggedIn && userData) {
      dispatch({ type: 'SET_SHOW_USER_PROFILE', payload: true });
    } else {
      dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: true });
    }
  };

  const handleLogout = async () => {
    try {
      console.log('🚪 Starting complete logout process (returning to landing page)...');
      
      // Clear secure cache before logout
      if (userData?.email) {
        console.log('🗑️ Clearing secure cache for user:', userData.email);
        await mcpService.invalidateSecureCache();
      }
      
      // Logout from Fi Money backend session
      console.log('🔐 Logging out from Fi Money session...');
      await mcpService.logout();
      
      // Clear demo mode
      mcpService.setDemoMode(false);
      sessionStorage.removeItem('demoMode');
      
      // Complete logout - clear all user data and return to landing page
      console.log('🧹 Clearing all user data and returning to landing page...');
      
      // Clear user profile data from localStorage
      localStorage.removeItem('userData');
      
      // Reset all state to initial values
      dispatch({ type: 'SET_AUTHENTICATED', payload: false });
      dispatch({ type: 'SET_LOGGED_IN', payload: false });
      dispatch({ type: 'SET_USER_DATA', payload: null });
      dispatch({ type: 'SET_FINANCIAL_DATA', payload: null });
      dispatch({ type: 'SET_SHOW_USER_PROFILE', payload: false });
      dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: false });
      dispatch({ type: 'SET_CACHE_STATUS', payload: null });
      dispatch({ type: 'SET_DEMO_MODE', payload: false });
      dispatch({ type: 'SET_AUTH_ERROR', payload: '' });
      
      console.log('✅ Complete logout successful - returning to landing page');
      
    } catch (error) {
      console.error('❌ Error during logout:', error);
      // Force complete logout even if backend logout fails
      sessionStorage.removeItem('demoMode');
      localStorage.removeItem('userData');
      dispatch({ type: 'SET_AUTHENTICATED', payload: false });
      dispatch({ type: 'SET_LOGGED_IN', payload: false });
      dispatch({ type: 'SET_USER_DATA', payload: null });
      dispatch({ type: 'SET_FINANCIAL_DATA', payload: null });
      dispatch({ type: 'SET_SHOW_USER_PROFILE', payload: false });
      dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: false });
      dispatch({ type: 'SET_CACHE_STATUS', payload: null });
      dispatch({ type: 'SET_DEMO_MODE', payload: false });
      dispatch({ type: 'SET_AUTH_ERROR', payload: '' });
    }
  };

  // Force reset to landing page function
  const forceResetToLandingPage = () => {
    console.log('🔄 Force resetting to landing page...');
    
    // Clear all storage
    sessionStorage.clear();
    localStorage.clear();
    
    // Clear MCP service state
    mcpService.setDemoMode(false);
    
    // Reset all state to initial values
    dispatch({ type: 'SET_AUTHENTICATED', payload: false });
    dispatch({ type: 'SET_LOGGED_IN', payload: false });
    dispatch({ type: 'SET_USER_DATA', payload: null });
    dispatch({ type: 'SET_FINANCIAL_DATA', payload: null });
    dispatch({ type: 'SET_SHOW_USER_PROFILE', payload: false });
    dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: false });
    dispatch({ type: 'SET_CACHE_STATUS', payload: null });
    dispatch({ type: 'SET_DEMO_MODE', payload: false });
    dispatch({ type: 'SET_AUTH_ERROR', payload: '' });
    dispatch({ type: 'SET_ACTIVE_TAB', payload: 'portfolio' });
    dispatch({ type: 'SET_LOADING', payload: false });
    dispatch({ type: 'SET_CHECKING_AUTH', payload: false });
    
    // Force page reload to clear any cached state
    setTimeout(() => {
      window.location.reload();
    }, 100);
    
    console.log('✅ Force reset complete - reloading page to show landing page');
  };

  const handleEditProfile = () => {
    dispatch({ type: 'SET_SHOW_USER_PROFILE', payload: false });
    dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: true });
  };

  // Transformation handled by MCPDataService

  if (isCheckingAuth || isLoading) {
    return (
      <div className="min-h-screen bg-[rgb(0,26,30)] flex items-center justify-center">
        <div className="text-center space-y-6">
          <div className="w-12 h-12 border-4 border-[rgba(0,184,153,0.3)] border-t-[rgb(0,184,153)] rounded-full animate-spin mx-auto"></div>
          <div>
            <h2 className="text-2xl font-black text-white">Artha AI</h2>
            <p className="text-gray-300 mt-2">
              {isCheckingAuth ? 'Checking Fi Money connection...' : 'Loading real-time financial data...'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Show landing page only if user is not logged in AND not authenticated with Fi Money AND not in demo mode
  // Also ensure we're not in the middle of checking auth to prevent flickering
  // More explicit and robust landing page condition
  const shouldShowLandingPage = (
    !hasVisited || // First visit in session
    isFreshStart || // Fresh start detection
    (!isLoggedIn && !isAuthenticated && !isDemoMode && !isCheckingAuth && !userData) || // Standard condition - check userData state
    (!localStorage.getItem('userData') && !sessionStorage.getItem('demoMode')) // No stored data
  );

  console.log('🔍 Conditional rendering check - isLoggedIn:', isLoggedIn, 'isAuthenticated:', isAuthenticated, 'isDemoMode:', isDemoMode, 'userData:', !!userData, 'isLoading:', isLoading, 'isCheckingAuth:', isCheckingAuth);
  console.log('🔍 showSignupForm:', showSignupForm, 'showUserProfile:', showUserProfile);
  console.log('🔍 isFreshStart:', isFreshStart, 'hasVisited:', hasVisited);
  console.log('🎯 DECISION POINT 1: shouldShowLandingPage:', shouldShowLandingPage);
  
  // Prevent flickering by ensuring we're not in the middle of auth checks
  // Updated condition to be more explicit and robust
  if (shouldShowLandingPage) {
    console.log('📄 ✅ SHOWING LANDING PAGE - user can choose demo mode or create profile');
    return (
      <HydrationProvider>
        <div className="min-h-screen bg-[rgb(0,26,30)]">
          {/* Modern Landing Page Header */}
          <header className="bg-[rgba(0,26,30,0.95)] backdrop-blur-2xl border-b border-[rgba(0,184,153,0.3)] sticky top-0 z-50 shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-r from-[rgba(0,184,153,0.05)] to-transparent"></div>
            <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-20">
                <div className="flex items-center space-x-4 group">
                  <div className="group-hover:translate-x-1 transition-transform duration-300">
                    <h1 className="text-2xl font-black bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent tracking-tight">
                      Artha AI
                    </h1>
                    <p className="text-xs text-[rgb(0,184,153)] font-semibold tracking-wide">
                      AI Financial Intelligence
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => {
                      console.log('🎭 Activating demo mode from header...');
                      sessionStorage.setItem('demoMode', 'true');
                      dispatch({ type: 'SET_DEMO_MODE', payload: true });
                      dispatch({ type: 'SET_AUTHENTICATED', payload: true });
                      mcpService.setDemoMode(true);
                    }}
                    className="group relative px-6 py-3 bg-transparent border-2 border-[rgb(0,184,153)] text-[rgb(0,184,153)] font-semibold rounded-xl overflow-hidden transition-all duration-300 hover:bg-[rgba(0,184,153,0.1)] hover:border-[rgb(0,204,173)] hover:text-[rgb(0,204,173)] hover:shadow-lg hover:shadow-[rgba(0,184,153,0.2)]"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[rgba(0,184,153,0.1)] to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
                    <span className="relative flex items-center">
                      <span className="mr-2 text-lg">🎭</span>
                      Try Demo
                    </span>
                  </button>
                  <button
                    onClick={() => dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: true })}
                    className="group relative px-6 py-3 bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white font-semibold rounded-xl overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-[rgba(0,184,153,0.3)] hover:scale-105"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-[rgb(0,164,133)] to-[rgb(0,144,113)] opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                    <span className="relative flex items-center">
                      <span className="mr-2 text-lg">👤</span>
                      Create Profile
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </header>

          {/* Enhanced Interactive Landing Page */}
          <EnhancedLandingPage />
          

        </div>

        {/* Signup Form Modal */}
        {showSignupForm && (
          <SignupForm
            onSignupSuccess={handleSignupSuccess}
            onLoginSuccess={handleLoginSuccess}
            onClose={() => dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: false })}
            authMode={state.authMode}
          />
        )}
      </HydrationProvider>
    );
  }

  // Show Fi Money authentication screen if user is logged in but not authenticated with Fi Money
  console.log('🔍 Checking Fi Money auth condition - isLoggedIn:', isLoggedIn, '!isAuthenticated:', !isAuthenticated, '!isDemoMode:', !isDemoMode, '!isCheckingAuth:', !isCheckingAuth);
  console.log('🎯 DECISION POINT 2: Fi Money auth condition (isLoggedIn && !isAuthenticated && !isDemoMode && !isCheckingAuth):', (isLoggedIn && !isAuthenticated && !isDemoMode && !isCheckingAuth));
  if (isLoggedIn && !isAuthenticated && !isDemoMode && !isCheckingAuth) {
    console.log('🔐 ✅ SHOWING FI MONEY AUTH SCREEN - logged in user needs Fi Money authentication');
    console.log('🔐 Auth screen state - isAuthenticated:', isAuthenticated, 'isLoggedIn:', isLoggedIn, 'isLoading:', isLoading, 'financialData:', !!financialData);
    return (
      <HydrationProvider>
        <div className="min-h-screen bg-[rgb(0,26,30)]">
          {/* Fi Money Auth Header */}
          <header className="bg-[rgba(26,26,26,0.95)] backdrop-blur-xl border-b border-[rgba(0,184,153,0.2)] sticky top-0 z-50 shadow-2xl">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-20">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-2xl flex items-center justify-center shadow-xl">
                    <ArthaLogo className="text-white" size="md" src="/ArthaAi.svg" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-black text-white tracking-tight">Artha AI</h1>
                    <p className="text-xs text-[rgb(0,184,153)] font-semibold">AI Financial Intelligence</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.3)] rounded-xl flex items-center justify-center">
                      <span className="text-sm font-bold text-[rgb(0,184,153)]">
                        {userData ? getInitials(userData) : 'U'}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-bold text-white">
                        {userData ? getFullName(userData) : 'User'}
                      </p>
                      <p className="text-xs text-[rgb(0,184,153)]">Premium Member</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </header>

          {/* Fi Money Authentication Content */}
          <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-black text-white mb-6">
                Welcome {getFirstName(userData)}! Connect to Fi Money
              </h2>
              <p className="text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
                Connect your Fi Money account to get real-time financial data and AI-powered insights on your complete portfolio
              </p>
            </div>

            {authError && (
              <div className="mb-8 max-w-md mx-auto">
                <div className="bg-[rgba(220,53,69,0.1)] border border-[rgba(220,53,69,0.3)] rounded-2xl p-4">
                  <p className="text-sm text-red-400">{authError}</p>
                </div>
              </div>
            )}

            <div className="mx-auto">
              <FiMoneyWebAuth
                onAuthSuccess={handleAuthSuccess}
                onAuthError={handleAuthError}
              />
            </div>
          </main>
        </div>
      </HydrationProvider>
    );
  }

  // At this point, either:
  // 1. User is authenticated with Fi Money (with or without login) - show dashboard
  // 2. User is in demo mode - show dashboard
  // 3. Any other combination that should show dashboard
  console.log('🎯 DECISION POINT 3: Dashboard condition - reached final fallback');
  console.log('🏠 ✅ SHOWING DASHBOARD - Final check: isAuthenticated:', isAuthenticated, 'isLoggedIn:', isLoggedIn, 'isDemoMode:', isDemoMode);

  const navigationItems = [
    { id: 'portfolio', label: 'Portfolio', icon: 'M4 7v10c0 2.21 3.79 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.79 4 8 4s8-1.79 8-4M4 7c0-2.21 3.79-4 8-4s8 1.79 8 4' },
    { id: 'advisory', label: 'AI Chat', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' }
  ];

  console.log('🚨 CRITICAL DEBUG - Why are we showing dashboard instead of landing page?');
  console.log('🔍 Current state values:');
  console.log('  - isLoggedIn:', isLoggedIn);
  console.log('  - isAuthenticated:', isAuthenticated);
  console.log('  - isDemoMode:', isDemoMode);
  console.log('  - userData:', !!userData);
  console.log('  - isLoading:', isLoading);
  console.log('  - isCheckingAuth:', isCheckingAuth);
  console.log('🎯 Landing page condition (!isLoggedIn && !isAuthenticated && !isDemoMode):', (!isLoggedIn && !isAuthenticated && !isDemoMode));
  console.log('🎯 Fi Money auth condition (isLoggedIn && !isAuthenticated && !isDemoMode):', (isLoggedIn && !isAuthenticated && !isDemoMode));
  console.log('🏠 Rendering main dashboard - this should NOT happen if landing page should show');
  console.log('✅ All conditions passed - showing dashboard');

  return (
    <HydrationProvider>
      <div className="min-h-screen bg-[rgb(0,26,30)]">
        {/* Fi Money Header */}
        <header className="bg-[rgba(26,26,26,0.95)] backdrop-blur-xl border-b border-[rgba(0,184,153,0.2)] sticky top-0 z-50 shadow-2xl">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-20">
              {/* Fi Money Brand */}
              <div className="flex items-center space-x-8">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-2xl flex items-center justify-center shadow-xl">
                    <ArthaLogo className="text-white" size="md" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-black text-white tracking-tight">Artha</h1>
                    <p className="text-xs text-[rgb(0,184,153)] font-semibold">
                      {isDemoMode ? 'Demo Mode • AI Financial Intelligence' : 'AI Financial Intelligence'}
                    </p>
                  </div>
                </div>
                
                {/* Fi Money Navigation */}
                <nav className="hidden md:flex items-center bg-[rgba(30,30,30,0.8)] rounded-2xl p-2 backdrop-blur-sm border border-[rgba(70,68,68,0.3)]">
                  {navigationItems.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => dispatch({ type: 'SET_ACTIVE_TAB', payload: item.id })}
                      className={`flex items-center space-x-2 px-5 py-3 text-sm font-semibold rounded-xl transition-all duration-300 ${
                        activeTab === item.id
                          ? 'bg-[rgb(0,184,153)] text-white shadow-lg transform scale-105'
                          : 'text-gray-300 hover:text-white hover:bg-[rgba(0,184,153,0.1)]'
                      }`}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                      </svg>
                      <span>{item.label}</span>
                    </button>
                  ))}
                </nav>
              </div>
              
              {/* User Actions */}
              <div className="flex items-center space-x-4">
                {/* Reset to Landing Page Button */}
                <button
                  onClick={forceResetToLandingPage}
                  className="group relative px-4 py-2 bg-transparent border border-[rgba(0,184,153,0.5)] text-[rgb(0,184,153)] font-medium rounded-lg overflow-hidden transition-all duration-300 hover:bg-[rgba(0,184,153,0.1)] hover:border-[rgb(0,204,173)] hover:text-[rgb(0,204,173)] text-sm"
                  title="Return to Landing Page"
                >
                  <span className="relative flex items-center">
                    <span className="mr-2">🏠</span>
                    Home
                  </span>
                </button>
                
                {/* Cache Status Indicator */}
                {!isDemoMode && cacheStatus && (
                  <div className="hidden lg:flex items-center space-x-2 bg-[rgba(30,30,30,0.8)] rounded-xl px-3 py-2 border border-[rgba(70,68,68,0.3)]">
                    <div className={`w-2 h-2 rounded-full ${
                      cacheStatus.isExpired ? 'bg-red-400' : 
                      cacheStatus.hasCache ? 'bg-[#cca695]' : 'bg-gray-400'
                    } animate-pulse`}></div>
                    <div className="text-xs">
                      <p className="text-gray-300 font-medium">
                        {cacheStatus.hasCache ? 'Cached Data' : 'No Cache'}
                      </p>
                      {cacheStatus.timeRemaining && !cacheStatus.isExpired && (
                        <p className="text-[#cca695]">
                          {cacheStatus.timeRemaining} left
                        </p>
                      )}
                      {cacheStatus.isExpired && (
                        <p className="text-red-400">Expired</p>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Authentication Section */}
              <div className="flex items-center space-x-3">
                {/* Demo Mode Toggle */}
                {!isLoggedIn && (
                  <button
                    onClick={() => {
                      console.log('🎭 Activating demo mode from dashboard header...');
                      sessionStorage.setItem('demoMode', 'true');
                      dispatch({ type: 'SET_DEMO_MODE', payload: true });
                      dispatch({ type: 'SET_AUTHENTICATED', payload: true });
                      mcpService.setDemoMode(true);
                    }}
                    className="px-4 py-2 bg-[rgba(255,165,0,0.1)] hover:bg-[rgba(255,165,0,0.2)] border border-[rgba(255,165,0,0.3)] text-orange-400 font-semibold rounded-xl transition-all flex items-center space-x-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <span className="hidden sm:inline">Try Demo</span>
                  </button>
                )}

                {/* Login Button */}
                {!isLoggedIn && !isDemoMode && (
                  <button
                    onClick={() => dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: true })}
                    className="px-4 py-2 bg-[rgb(0,184,153)] hover:bg-[rgb(0,164,133)] text-white font-semibold rounded-xl transition-all flex items-center space-x-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    <span className="hidden sm:inline">Login</span>
                  </button>
                )}

                {/* User Profile Section */}
                {(isLoggedIn || isDemoMode) && (
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={handleProfileClick}
                      className="flex items-center space-x-3 hover:bg-[rgba(0,184,153,0.1)] rounded-2xl p-2 transition-all duration-300"
                    >
                      <div className="w-10 h-10 bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.3)] rounded-xl flex items-center justify-center shadow-lg">
                        <span className="text-sm font-bold text-[rgb(0,184,153)]">
                          {isLoggedIn && userData 
                            ? getInitials(userData)
                            : isDemoMode ? 'DM' : 'GU'
                          }
                        </span>
                      </div>
                      <div className="hidden lg:block">
                        <p className="text-sm font-bold text-white">
                          {isLoggedIn && userData 
                            ? getFullName(userData)
                            : isDemoMode ? 'Demo Mode' : 'Guest User'
                          }
                        </p>
                        <p className="text-xs text-[rgb(0,184,153)]">
                          {isLoggedIn ? 'Premium Member' : isDemoMode ? 'Demo User' : 'Click to Sign Up'}
                        </p>
                      </div>
                    </button>

                    {/* Logout Button */}
                    <button
                      onClick={handleLogout}
                      className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-xl transition-all flex items-center space-x-2"
                      title="Logout"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      <span className="hidden sm:inline">Logout</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Fi Money Mobile Navigation */}
        <div className="md:hidden bg-[rgba(26,26,26,0.95)] backdrop-blur-xl border-b border-[rgba(0,184,153,0.2)]">
          <div className="max-w-7xl mx-auto px-4">
            {/* Main Navigation */}
            <div className="flex space-x-1 py-3">
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => dispatch({ type: 'SET_ACTIVE_TAB', payload: item.id })}
                  className={`flex-1 flex flex-col items-center py-3 text-xs font-semibold rounded-xl transition-all duration-300 ${
                    activeTab === item.id
                      ? 'text-white bg-[rgb(0,184,153)] shadow-lg transform scale-105'
                      : 'text-gray-300 hover:bg-[rgba(0,184,153,0.1)] hover:text-white'
                  }`}
                >
                  <svg className="w-5 h-5 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                  </svg>
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
            
            {/* Mobile Authentication Section */}
            <div className="flex items-center justify-between py-2 border-t border-[rgba(0,184,153,0.1)]">
              <div className="flex items-center space-x-2">
                {(isLoggedIn || isDemoMode) && (
                  <button
                    onClick={handleProfileClick}
                    className="flex items-center space-x-2 hover:bg-[rgba(0,184,153,0.1)] rounded-xl p-2 transition-all"
                  >
                    <div className="w-8 h-8 bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.3)] rounded-lg flex items-center justify-center">
                      <span className="text-xs font-bold text-[rgb(0,184,153)]">
                        {isLoggedIn && userData 
                          ? getInitials(userData)
                          : isDemoMode ? 'DM' : 'GU'
                        }
                      </span>
                    </div>
                    <span className="text-sm text-white">
                      {isLoggedIn && userData 
                        ? getFirstName(userData)
                        : isDemoMode ? 'Demo' : 'Guest'
                      }
                    </span>
                  </button>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                {!isLoggedIn && !isDemoMode && (
                  <>
                    <button
                      onClick={() => {
                        console.log(' Activating demo mode from mobile...');
                        sessionStorage.setItem('demoMode', 'true');
                        dispatch({ type: 'SET_DEMO_MODE', payload: true });
                        dispatch({ type: 'SET_AUTHENTICATED', payload: true });
                        mcpService.setDemoMode(true);
                      }}
                      className="px-3 py-1 bg-[rgba(255,165,0,0.1)] border border-[rgba(255,165,0,0.3)] text-orange-400 text-xs font-semibold rounded-lg"
                    >
                      Demo
                    </button>
                    <button
                      onClick={() => dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: true })}
                      className="px-3 py-1 bg-[rgb(0,184,153)] text-white text-xs font-semibold rounded-lg"
                    >
                      Login
                    </button>
                  </>
                )}
                
                {(isLoggedIn || isDemoMode) && (
                  <button
                    onClick={handleLogout}
                    className="px-3 py-1 bg-red-600 text-white text-xs font-semibold rounded-lg"
                  >
                    Logout
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Compact Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          {/* Compact Portfolio Header */}
          {activeTab === 'portfolio' && financialData && (
            <div className="mb-6">
              <div className="bg-gradient-to-r from-[rgb(24,25,27)] to-[rgb(28,29,31)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-5 shadow-xl">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-xl flex items-center justify-center shadow-lg">
                      <ArthaLogo className="text-white" size="md" />
                    </div>
                    <div>
                      <h1 className="text-xl font-bold text-white tracking-tight">
                        {isDemoMode ? 'Demo Portfolio' : 'My Portfolio'}
                      </h1>
                      <div className="flex items-center mt-1 space-x-2">
                        <div className={`w-2 h-2 rounded-full ${
                          isDemoMode ? 'bg-yellow-400' : 
                          (financialData?.fromCache ? 'bg-blue-400' : 'bg-[rgb(0,184,153)]')
                        } animate-pulse`}></div>
                        <span className={`text-xs font-medium ${
                          isDemoMode ? 'text-yellow-400' : 
                          (financialData?.fromCache ? 'text-blue-400' : 'text-[rgb(0,184,153)]')
                        }`}>
                          {isDemoMode ? 'Demo Mode' : 
                           (financialData?.fromCache ? 'Cached Data' : 'Live Data')}
                        </span>
                        {financialData?.fromCache && financialData?.cacheExpiry && (
                          <span className="text-xs text-gray-400">
                            • Expires {new Date(financialData.cacheExpiry).toLocaleTimeString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    {!isDemoMode && (
                      <button
                        onClick={async () => {
                          dispatch({ type: 'SET_LOADING', payload: true });
                          try {
                            // Invalidate cache and reload fresh data
                            if (userData?.email) {
                              await mcpService.invalidateSecureCache();
                              await checkCacheStatus();
                            }
                            await fetchFinancialData();
                          } catch (error) {
                            console.error('Failed to refresh data:', error);
                          } finally {
                            dispatch({ type: 'SET_LOADING', payload: false });
                          }
                        }}
                        className="p-2 bg-[rgba(0,184,153,0.1)] hover:bg-[rgba(0,184,153,0.2)] rounded-xl transition-colors"
                        title="Refresh Data"
                      >
                        <svg className="w-4 h-4 text-[rgb(0,184,153)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                      </button>
                    )}
                    <div className="text-right">
                      <p className="text-xs text-gray-400 font-medium">Total Value</p>
                      <p className="text-2xl font-bold text-white">{financialData?.summary?.total_net_worth_formatted || '₹0'}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Compact Auth Status - Only show if logged in but not authenticated */}
          {!isDemoMode && isLoggedIn && !isAuthenticated && (
            <div className="mb-4">
              <FiMoneyWebAuth
                onAuthSuccess={handleAuthSuccess}
                onAuthError={handleAuthError}
              />
            </div>
          )}
          
          {/* Compact Content Sections */}
          <div className="space-y-5">
            {activeTab === 'portfolio' && <Dashboard financialData={financialData} />}
            {activeTab === 'advisory' && <ChatInterface />}
          </div>
        </main>

        {/* Signup Form Modal */}
        {showSignupForm && (
          <SignupForm
            onSignupSuccess={handleSignupSuccess}
            onLoginSuccess={handleLoginSuccess}
            onClose={() => dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: false })}
            authMode={state.authMode}
          />
        )}

        {/* User Profile Modal */}
        {showUserProfile && userData && (
          <UserProfileModal
            userData={userData}
            onClose={() => dispatch({ type: 'SET_SHOW_USER_PROFILE', payload: false })}
            onEdit={handleEditProfile}
            onLogout={handleLogout}
            onClearProfile={clearProfile}
          />
        )}
      </div>
    </HydrationProvider>
  );
}

// Main component with Context Provider wrapper
export default function Home() {
  return (
    <AppProvider>
      <HomeContent />
    </AppProvider>
  );
}
