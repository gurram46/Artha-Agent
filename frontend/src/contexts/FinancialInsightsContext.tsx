'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

interface FinancialInsightsState {
  portfolioHealth: any;
  riskAssessment: any;
  tripPlanning: any;
  isLoadingHealth: boolean;
  isLoadingRisk: boolean;
  isLoadingTrip: boolean;
  lastUpdated: Record<string, string>;
}

interface FinancialInsightsContextType extends FinancialInsightsState {
  setPortfolioHealth: (data: any) => void;
  setRiskAssessment: (data: any) => void;
  setTripPlanning: (data: any) => void;
  setIsLoadingHealth: (loading: boolean) => void;
  setIsLoadingRisk: (loading: boolean) => void;
  setIsLoadingTrip: (loading: boolean) => void;
  fetchPortfolioHealth: () => Promise<void>;
  fetchRiskAssessment: () => Promise<void>;
  fetchTripPlanning: () => Promise<void>;
  isDataStale: (key: string) => boolean;
  clearAllData: () => void;
}

const FinancialInsightsContext = createContext<FinancialInsightsContextType | undefined>(undefined);

// Cache duration: 5 minutes
const CACHE_DURATION = 5 * 60 * 1000;

const getInitialState = (): FinancialInsightsState => {
  if (typeof window === 'undefined') {
    return {
      portfolioHealth: null,
      riskAssessment: null,
      tripPlanning: null,
      isLoadingHealth: false,
      isLoadingRisk: false,
      isLoadingTrip: false,
      lastUpdated: {}
    };
  }

  try {
    return {
      portfolioHealth: JSON.parse(localStorage.getItem('financial_portfolioHealth') || 'null'),
      riskAssessment: JSON.parse(localStorage.getItem('financial_riskAssessment') || 'null'),
      tripPlanning: JSON.parse(localStorage.getItem('financial_tripPlanning') || 'null'),
      isLoadingHealth: false,
      isLoadingRisk: false,
      isLoadingTrip: false,
      lastUpdated: JSON.parse(localStorage.getItem('financial_lastUpdated') || '{}')
    };
  } catch {
    return {
      portfolioHealth: null,
      riskAssessment: null,
      tripPlanning: null,
      isLoadingHealth: false,
      isLoadingRisk: false,
      isLoadingTrip: false,
      lastUpdated: {}
    };
  }
};

export function FinancialInsightsProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<FinancialInsightsState>(getInitialState);

  // Persist to localStorage whenever state changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      Object.entries(state).forEach(([key, value]) => {
        if (key.startsWith('isLoading')) return; // Don't persist loading states
        localStorage.setItem(`financial_${key}`, JSON.stringify(value));
      });
    }
  }, [state]);


  // Individual setter functions
  const setPortfolioHealth = useCallback((data: any) => {
    setState(prev => ({ ...prev, portfolioHealth: data }));
  }, []);

  const setRiskAssessment = useCallback((data: any) => {
    setState(prev => ({ ...prev, riskAssessment: data }));
  }, []);

  const setTripPlanning = useCallback((data: any) => {
    setState(prev => ({ ...prev, tripPlanning: data }));
  }, []);

  // Loading state setters
  const setIsLoadingHealth = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoadingHealth: loading }));
  }, []);

  const setIsLoadingRisk = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoadingRisk: loading }));
  }, []);

  const setIsLoadingTrip = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoadingTrip: loading }));
  }, []);

  // Fetch functions for core agents
  const fetchPortfolioHealth = useCallback(async () => {
    const lastUpdate = state.lastUpdated['portfolioHealth'];
    if (lastUpdate && state.portfolioHealth) {
      const timeSinceUpdate = Date.now() - new Date(lastUpdate).getTime();
      if (timeSinceUpdate < CACHE_DURATION) {
        return; // Use cached data
      }
    }

    setIsLoadingHealth(true);
    try {
      const response = await fetch('http://localhost:8003/api/portfolio-health', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      setPortfolioHealth(data.portfolio_health);
      
      setState(prev => ({
        ...prev,
        lastUpdated: {
          ...prev.lastUpdated,
          portfolioHealth: new Date().toISOString()
        }
      }));
    } catch (error) {
      console.error('Failed to fetch portfolio health:', error);
    } finally {
      setIsLoadingHealth(false);
    }
  }, [state.portfolioHealth, state.lastUpdated]);


  const fetchRiskAssessment = useCallback(async () => {
    const lastUpdate = state.lastUpdated['riskAssessment'];
    if (lastUpdate && state.riskAssessment) {
      const timeSinceUpdate = Date.now() - new Date(lastUpdate).getTime();
      if (timeSinceUpdate < CACHE_DURATION) {
        return; // Use cached data
      }
    }

    setIsLoadingRisk(true);
    try {
      const response = await fetch('http://localhost:8003/api/risk-assessment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      setRiskAssessment(data.risk_assessment);
      
      setState(prev => ({
        ...prev,
        lastUpdated: {
          ...prev.lastUpdated,
          riskAssessment: new Date().toISOString()
        }
      }));
    } catch (error) {
      console.error('Failed to fetch risk assessment:', error);
    } finally {
      setIsLoadingRisk(false);
    }
  }, [state.riskAssessment, state.lastUpdated]);

  const fetchTripPlanning = useCallback(async () => {
    const lastUpdate = state.lastUpdated['tripPlanning'];
    if (lastUpdate && state.tripPlanning) {
      const timeSinceUpdate = Date.now() - new Date(lastUpdate).getTime();
      if (timeSinceUpdate < CACHE_DURATION) {
        return; // Use cached data
      }
    }

    setIsLoadingTrip(true);
    try {
      const response = await fetch('http://localhost:8003/api/trip-planning', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      setTripPlanning(data.trip_planning);
      
      setState(prev => ({
        ...prev,
        lastUpdated: {
          ...prev.lastUpdated,
          tripPlanning: new Date().toISOString()
        }
      }));
    } catch (error) {
      console.error('Failed to fetch trip planning:', error);
    } finally {
      setIsLoadingTrip(false);
    }
  }, [state.tripPlanning, state.lastUpdated]);

  const isDataStale = useCallback((key: string) => {
    const lastUpdate = state.lastUpdated[key];
    if (!lastUpdate) return true;
    const timeSinceUpdate = Date.now() - new Date(lastUpdate).getTime();
    return timeSinceUpdate > CACHE_DURATION;
  }, [state.lastUpdated]);

  const clearAllData = useCallback(() => {
    if (typeof window !== 'undefined') {
      // Clear localStorage
      Object.keys(localStorage).forEach(key => {
        if (key.startsWith('financial_')) {
          localStorage.removeItem(key);
        }
      });
    }

    // Reset state
    setState({
      portfolioHealth: null,
      riskAssessment: null,
      tripPlanning: null,
      isLoadingHealth: false,
      isLoadingRisk: false,
      isLoadingTrip: false,
      lastUpdated: {}
    });
  }, []);

  const value: FinancialInsightsContextType = {
    ...state,
    setPortfolioHealth,
    setRiskAssessment,
    setTripPlanning,
    setIsLoadingHealth,
    setIsLoadingRisk,
    setIsLoadingTrip,
    fetchPortfolioHealth,
    fetchRiskAssessment,
    fetchTripPlanning,
    isDataStale,
    clearAllData
  };

  return (
    <FinancialInsightsContext.Provider value={value}>
      {children}
    </FinancialInsightsContext.Provider>
  );
}

export function useFinancialInsights() {
  const context = useContext(FinancialInsightsContext);
  if (context === undefined) {
    throw new Error('useFinancialInsights must be used within a FinancialInsightsProvider');
  }
  return context;
}