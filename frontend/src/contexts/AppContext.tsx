'use client';

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
// import { sessionService } from '../services/sessionService';

// Types
export interface UserData {
  id: string;
  email: string;
  name: string;
  firstName?: string;
  lastName?: string;
  preferences?: {
    theme?: 'light' | 'dark';
    currency?: string;
    notifications?: boolean;
  };
}

export interface FinancialData {
  [key: string]: any;
}

export interface CacheStatus {
  [key: string]: any;
}

export interface AppState {
  user: UserData | null;
  userData: any; // For compatibility with existing code
  isLoggedIn: boolean; // For compatibility with existing code
  isAuthenticated: boolean;
  authToken: string | null;
  demoMode: boolean;
  loading: boolean;
  error: string | null;
  isCheckingAuth: boolean;
  financialData: FinancialData | null;
  cacheStatus: CacheStatus | null;
  authError: string;
  activeTab: string;
  showSignupForm: boolean;
  showLoginForm: boolean;
  showUserProfile: boolean;
  authMode: 'login' | 'signup';
}

type AppAction =
  | { type: 'SET_USER'; payload: UserData }
  | { type: 'SET_USER_DATA'; payload: any } // For compatibility with existing code
  | { type: 'SET_LOGGED_IN'; payload: boolean } // For compatibility with existing code
  | { type: 'SET_AUTH_TOKEN'; payload: string }
  | { type: 'SET_DEMO_MODE'; payload: boolean }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_CHECKING_AUTH'; payload: boolean }
  | { type: 'SET_AUTHENTICATED'; payload: boolean }
  | { type: 'SET_FINANCIAL_DATA'; payload: FinancialData | null }
  | { type: 'SET_CACHE_STATUS'; payload: CacheStatus | null }
  | { type: 'SET_AUTH_ERROR'; payload: string }
  | { type: 'SET_ACTIVE_TAB'; payload: string }
  | { type: 'SET_SHOW_SIGNUP_FORM'; payload: boolean }
  | { type: 'SET_SHOW_LOGIN_FORM'; payload: boolean }
  | { type: 'SET_SHOW_USER_PROFILE'; payload: boolean }
  | { type: 'SET_AUTH_MODE'; payload: 'login' | 'signup' }
  | { type: 'CLEAR_ALL_DATA' }
  | { type: 'CLEAR_USER_PROFILE' }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' };

// Initial state
const initialState: AppState = {
  user: null,
  userData: null,
  isLoggedIn: false,
  isAuthenticated: false,
  authToken: null,
  demoMode: false,
  loading: false,
  error: null,
  isCheckingAuth: false,
  financialData: null,
  cacheStatus: null,
  authError: '',
  activeTab: 'portfolio',
  showSignupForm: false,
  showLoginForm: false,
  showUserProfile: false,
  authMode: 'signup',
};

// Reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        loading: false,
      };
    case 'SET_USER_DATA':
      return {
        ...state,
        userData: action.payload,
        loading: false,
      };
    case 'SET_LOGGED_IN':
      return {
        ...state,
        isLoggedIn: action.payload,
      };
    case 'SET_AUTH_TOKEN':
      return {
        ...state,
        authToken: action.payload,
        // Don't automatically set isAuthenticated - let Fi Money auth flow control this
      };
    case 'SET_DEMO_MODE':
      return {
        ...state,
        demoMode: action.payload,
      };
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        loading: false,
      };
    case 'SET_CHECKING_AUTH':
      return {
        ...state,
        isCheckingAuth: action.payload,
      };
    case 'SET_AUTHENTICATED':
      return {
        ...state,
        isAuthenticated: action.payload,
      };
    case 'SET_FINANCIAL_DATA':
      return {
        ...state,
        financialData: action.payload,
      };
    case 'SET_CACHE_STATUS':
      return {
        ...state,
        cacheStatus: action.payload,
      };
    case 'SET_AUTH_ERROR':
      return {
        ...state,
        authError: action.payload,
      };
    case 'SET_ACTIVE_TAB':
      return {
        ...state,
        activeTab: action.payload,
      };
    case 'SET_SHOW_SIGNUP_FORM':
      return {
        ...state,
        showSignupForm: action.payload,
      };
    case 'SET_SHOW_LOGIN_FORM':
      return {
        ...state,
        showLoginForm: action.payload,
      };
    case 'SET_SHOW_USER_PROFILE':
      return {
        ...state,
        showUserProfile: action.payload,
      };
    case 'SET_AUTH_MODE':
      return {
        ...state,
        authMode: action.payload,
      };
    case 'CLEAR_ALL_DATA':
      return {
        ...initialState,
        demoMode: state.demoMode, // Preserve demo mode setting
      };
    case 'CLEAR_USER_PROFILE':
      return {
        ...state,
        user: null,
        userData: null,
        isLoggedIn: false,
      };
    case 'LOGOUT':
      return {
        ...initialState,
        demoMode: state.demoMode, // Preserve demo mode setting
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    default:
      return state;
  }
}

// Context
const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
} | null>(null);

// Provider component
export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Load persisted state on mount - but don't automatically set authentication states
  useEffect(() => {
    const loadPersistedState = async () => {
      try {
        console.log('🔄 AppContext: Loading persisted state...');
        console.log('🔍 Current state before loading:', { 
          isLoggedIn: state.isLoggedIn, 
          userData: !!state.userData, 
          loading: state.loading 
        });
        
        // Check if we have userData in localStorage
        const userData = localStorage.getItem('userData');
        const hasUserData = !!userData;
        
        // Load user data from localStorage and set isLoggedIn if userData exists
        if (hasUserData) {
          console.log('🔄 AppContext: Loading userData from localStorage...');
          const parsedUserData = JSON.parse(userData);
          
          // Always update state with localStorage data to ensure sync
          dispatch({ type: 'SET_USER_DATA', payload: parsedUserData });
          dispatch({ type: 'SET_LOGGED_IN', payload: true });
          
          console.log('🔄 AppContext: Loaded userData from localStorage and set isLoggedIn to true');
          console.log('🔄 AppContext: User name from localStorage:', parsedUserData.full_name);
        } else {
          console.log('🔄 AppContext: No userData found in localStorage');
          // Ensure logged out state if no userData
          dispatch({ type: 'SET_LOGGED_IN', payload: false });
          dispatch({ type: 'SET_USER_DATA', payload: null });
        }

        // Load auth token from localStorage but don't set authentication state
        const authToken = localStorage.getItem('authToken');
        if (authToken) {
          dispatch({ type: 'SET_AUTH_TOKEN', payload: authToken });
          console.log('🔄 AppContext: Auth token loaded but authentication state not set automatically');
        }

        // Ensure loading is false after initialization
        dispatch({ type: 'SET_LOADING', payload: false });
      } catch (error) {
        console.error('Error loading persisted state:', error);
        dispatch({ type: 'SET_ERROR', payload: 'Failed to load saved data' });
      }
    };

    loadPersistedState();
  }, []); // Only run once on mount

  // Persist state changes
  useEffect(() => {
    try {
      // Save demo mode to sessionStorage (non-sensitive)
      sessionStorage.setItem('demoMode', JSON.stringify(state.demoMode));
    } catch (error) {
      console.error('Error saving demo mode:', error);
    }
  }, [state.demoMode]);

  useEffect(() => {
    try {
      if (state.userData) {
        localStorage.setItem('userData', JSON.stringify(state.userData));
      } else if (!state.isLoggedIn) {
        localStorage.removeItem('userData');
      }
    } catch (error) {
      console.error('Error saving user data:', error);
    }
  }, [state.userData, state.isLoggedIn]);

  useEffect(() => {
    try {
      if (state.authToken) {
        localStorage.setItem('authToken', state.authToken);
      } else {
        localStorage.removeItem('authToken');
      }
    } catch (error) {
      console.error('Error saving auth token:', error);
    }
  }, [state.authToken]);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

// Hook to use the context
export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}

// Auth hook
export function useAuth() {
  const { state } = useAppContext();
  return {
    isAuthenticated: state.isAuthenticated,
    isCheckingAuth: state.isCheckingAuth,
    isDemoMode: state.demoMode,
    userData: state.userData,
    isLoggedIn: state.isLoggedIn,
    authError: state.authError,
  };
}

// Financial Data hook
export function useFinancialData() {
  const { state } = useAppContext();
  return {
    financialData: state.financialData,
    isLoading: state.loading,
    cacheStatus: state.cacheStatus,
  };
}

// UI hook
export function useUI() {
  const { state } = useAppContext();
  return {
    activeTab: state.activeTab,
    showSignupForm: state.showSignupForm,
    showLoginForm: state.showLoginForm,
    showUserProfile: state.showUserProfile,
    authMode: state.authMode,
  };
}