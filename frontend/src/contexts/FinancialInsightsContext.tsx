'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

interface FinancialInsightsState {
  hiddenTruths: any;
  futureProjection: any;
  goalReality: any;
  moneyPersonality: any;
  portfolioHealth: any;
  moneyLeaks: any;
  riskAssessment: any;
  isLoadingHidden: boolean;
  isLoadingFuture: boolean;
  isLoadingGoals: boolean;
  isLoadingPersonality: boolean;
  isLoadingHealth: boolean;
  isLoadingLeaks: boolean;
  isLoadingRisk: boolean;
  lastUpdated: Record<string, string>;
}

interface FinancialInsightsContextType extends FinancialInsightsState {
  setHiddenTruths: (data: any) => void;
  setFutureProjection: (data: any) => void;
  setGoalReality: (data: any) => void;
  setMoneyPersonality: (data: any) => void;
  setPortfolioHealth: (data: any) => void;
  setMoneyLeaks: (data: any) => void;
  setRiskAssessment: (data: any) => void;
  setIsLoadingHidden: (loading: boolean) => void;
  setIsLoadingFuture: (loading: boolean) => void;
  setIsLoadingGoals: (loading: boolean) => void;
  setIsLoadingPersonality: (loading: boolean) => void;
  setIsLoadingHealth: (loading: boolean) => void;
  setIsLoadingLeaks: (loading: boolean) => void;
  setIsLoadingRisk: (loading: boolean) => void;
  fetchHiddenTruths: () => Promise<void>;
  fetchFutureProjection: () => Promise<void>;
  fetchGoalReality: () => Promise<void>;
  fetchMoneyPersonality: () => Promise<void>;
  fetchPortfolioHealth: () => Promise<void>;
  fetchMoneyLeaks: () => Promise<void>;
  fetchRiskAssessment: () => Promise<void>;
  isDataStale: (key: string) => boolean;
  clearAllData: () => void;
}

const FinancialInsightsContext = createContext<FinancialInsightsContextType | undefined>(undefined);

// Cache duration: 5 minutes
const CACHE_DURATION = 5 * 60 * 1000;

const getInitialState = (): FinancialInsightsState => {
  if (typeof window === 'undefined') {
    return {
      hiddenTruths: null,
      futureProjection: null,
      goalReality: null,
      moneyPersonality: null,
      portfolioHealth: null,
      moneyLeaks: null,
      riskAssessment: null,
      isLoadingHidden: false,
      isLoadingFuture: false,
      isLoadingGoals: false,
      isLoadingPersonality: false,
      isLoadingHealth: false,
      isLoadingLeaks: false,
      isLoadingRisk: false,
      lastUpdated: {}
    };
  }

  try {
    return {
      hiddenTruths: JSON.parse(localStorage.getItem('financial_hiddenTruths') || 'null'),
      futureProjection: JSON.parse(localStorage.getItem('financial_futureProjection') || 'null'),
      goalReality: JSON.parse(localStorage.getItem('financial_goalReality') || 'null'),
      moneyPersonality: JSON.parse(localStorage.getItem('financial_moneyPersonality') || 'null'),
      portfolioHealth: JSON.parse(localStorage.getItem('financial_portfolioHealth') || 'null'),
      moneyLeaks: JSON.parse(localStorage.getItem('financial_moneyLeaks') || 'null'),
      riskAssessment: JSON.parse(localStorage.getItem('financial_riskAssessment') || 'null'),
      isLoadingHidden: false,
      isLoadingFuture: false,
      isLoadingGoals: false,
      isLoadingPersonality: false,
      isLoadingHealth: false,
      isLoadingLeaks: false,
      isLoadingRisk: false,
      lastUpdated: JSON.parse(localStorage.getItem('financial_lastUpdated') || '{}')
    };
  } catch {
    return {
      hiddenTruths: null,
      futureProjection: null,
      goalReality: null,
      moneyPersonality: null,
      portfolioHealth: null,
      moneyLeaks: null,
      riskAssessment: null,
      isLoadingHidden: false,
      isLoadingFuture: false,
      isLoadingGoals: false,
      isLoadingPersonality: false,
      isLoadingHealth: false,
      isLoadingLeaks: false,
      isLoadingRisk: false,
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

  // Reusable streaming fetch function
  const fetchWithStreaming = useCallback(async (
    endpoint: string,
    fallbackEndpoint: string,
    currentData: any,
    setData: (data: any) => void,
    setLoading: (loading: boolean) => void,
    initialMessage: string,
    dataKey: string
  ) => {
    // Check if data is fresh (less than 5 minutes old)
    const lastUpdate = state.lastUpdated[dataKey];
    if (lastUpdate && currentData && typeof currentData === 'object' && 
        Object.keys(currentData).some(key => key.includes('ai_') || key.includes('_analysis'))) {
      const timeSinceUpdate = Date.now() - new Date(lastUpdate).getTime();
      if (timeSinceUpdate < CACHE_DURATION) {
        console.log(`Using cached data for ${dataKey}`);
        return; // Use cached data
      }
    }

    setLoading(true);
    setData(initialMessage);

    try {
      // Use fetch-based streaming for better reliability
      const response = await fetch(`http://localhost:8003${endpoint}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      if (!reader) {
        throw new Error('No response body reader available');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              switch (data.type) {
                case 'status':
                  setData(data.message);
                  break;
                case 'content':
                  setData(data.content);
                  break;
                case 'complete':
                  const responseKey = endpoint.includes('hidden-truths') ? 'ai_insights' :
                                      endpoint.includes('future-projection') ? 'ai_projection' :
                                      endpoint.includes('goal-reality') ? 'goal_analysis' :
                                      endpoint.includes('money-personality') ? 'personality_analysis' : 'ai_insights';
                  const finalData = { [responseKey]: data.content };
                  setData(finalData);
                  
                  // Update timestamp
                  setState(prev => ({
                    ...prev,
                    lastUpdated: {
                      ...prev.lastUpdated,
                      [dataKey]: new Date().toISOString()
                    }
                  }));
                  
                  setLoading(false);
                  return;
                case 'error':
                  console.error('Stream Error:', data.message);
                  setLoading(false);
                  return;
              }
            } catch (e) {
              console.error('Error parsing stream data:', e);
            }
          }
        }
      }

    } catch (error) {
      console.error(`Failed to fetch ${endpoint}:`, error);
      // Fallback to regular fetch if streaming fails
      try {
        const fallbackResponse = await fetch(`http://localhost:8003${fallbackEndpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        const fallbackData = await fallbackResponse.json();
        setData(fallbackData.insights);
        
        setState(prev => ({
          ...prev,
          lastUpdated: {
            ...prev.lastUpdated,
            [dataKey]: new Date().toISOString()
          }
        }));
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
        setData({ ai_insights: 'Unable to load insights. Please refresh to try again.' });
      }
      setLoading(false);
    }
  }, [state.lastUpdated]);

  // Individual setter functions
  const setHiddenTruths = useCallback((data: any) => {
    setState(prev => ({ ...prev, hiddenTruths: data }));
  }, []);

  const setFutureProjection = useCallback((data: any) => {
    setState(prev => ({ ...prev, futureProjection: data }));
  }, []);

  const setGoalReality = useCallback((data: any) => {
    setState(prev => ({ ...prev, goalReality: data }));
  }, []);

  const setMoneyPersonality = useCallback((data: any) => {
    setState(prev => ({ ...prev, moneyPersonality: data }));
  }, []);

  const setPortfolioHealth = useCallback((data: any) => {
    setState(prev => ({ ...prev, portfolioHealth: data }));
  }, []);

  const setMoneyLeaks = useCallback((data: any) => {
    setState(prev => ({ ...prev, moneyLeaks: data }));
  }, []);

  const setRiskAssessment = useCallback((data: any) => {
    setState(prev => ({ ...prev, riskAssessment: data }));
  }, []);

  // Loading state setters
  const setIsLoadingHidden = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoadingHidden: loading }));
  }, []);

  const setIsLoadingFuture = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoadingFuture: loading }));
  }, []);

  const setIsLoadingGoals = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoadingGoals: loading }));
  }, []);

  const setIsLoadingPersonality = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoadingPersonality: loading }));
  }, []);

  const setIsLoadingHealth = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoadingHealth: loading }));
  }, []);

  const setIsLoadingLeaks = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoadingLeaks: loading }));
  }, []);

  const setIsLoadingRisk = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoadingRisk: loading }));
  }, []);

  // Fetch functions
  const fetchHiddenTruths = useCallback(async () => {
    await fetchWithStreaming(
      '/api/stream/hidden-truths',
      '/api/hidden-truths',
      state.hiddenTruths,
      setHiddenTruths,
      setIsLoadingHidden,
      '🔍 Analyzing your financial data...',
      'hiddenTruths'
    );
  }, [fetchWithStreaming, state.hiddenTruths]);

  const fetchFutureProjection = useCallback(async () => {
    await fetchWithStreaming(
      '/api/stream/future-projection',
      '/api/future-projection',
      state.futureProjection,
      setFutureProjection,
      setIsLoadingFuture,
      '🔮 Projecting your financial future...',
      'futureProjection'
    );
  }, [fetchWithStreaming, state.futureProjection]);

  const fetchGoalReality = useCallback(async () => {
    await fetchWithStreaming(
      '/api/stream/goal-reality',
      '/api/goal-reality',
      state.goalReality,
      setGoalReality,
      setIsLoadingGoals,
      '🎯 Analyzing your life goals...',
      'goalReality'
    );
  }, [fetchWithStreaming, state.goalReality]);

  const fetchMoneyPersonality = useCallback(async () => {
    await fetchWithStreaming(
      '/api/stream/money-personality',
      '/api/money-personality',
      state.moneyPersonality,
      setMoneyPersonality,
      setIsLoadingPersonality,
      '🧠 Analyzing your money personality...',
      'moneyPersonality'
    );
  }, [fetchWithStreaming, state.moneyPersonality]);

  // Regular fetch functions for non-streaming endpoints
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

  const fetchMoneyLeaks = useCallback(async () => {
    const lastUpdate = state.lastUpdated['moneyLeaks'];
    if (lastUpdate && state.moneyLeaks) {
      const timeSinceUpdate = Date.now() - new Date(lastUpdate).getTime();
      if (timeSinceUpdate < CACHE_DURATION) {
        return; // Use cached data
      }
    }

    setIsLoadingLeaks(true);
    try {
      const response = await fetch('http://localhost:8003/api/money-leaks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      setMoneyLeaks(data.money_leaks);
      
      setState(prev => ({
        ...prev,
        lastUpdated: {
          ...prev.lastUpdated,
          moneyLeaks: new Date().toISOString()
        }
      }));
    } catch (error) {
      console.error('Failed to fetch money leaks:', error);
    } finally {
      setIsLoadingLeaks(false);
    }
  }, [state.moneyLeaks, state.lastUpdated]);

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
      hiddenTruths: null,
      futureProjection: null,
      goalReality: null,
      moneyPersonality: null,
      portfolioHealth: null,
      moneyLeaks: null,
      riskAssessment: null,
      isLoadingHidden: false,
      isLoadingFuture: false,
      isLoadingGoals: false,
      isLoadingPersonality: false,
      isLoadingHealth: false,
      isLoadingLeaks: false,
      isLoadingRisk: false,
      lastUpdated: {}
    });
  }, []);

  const value: FinancialInsightsContextType = {
    ...state,
    setHiddenTruths,
    setFutureProjection,
    setGoalReality,
    setMoneyPersonality,
    setPortfolioHealth,
    setMoneyLeaks,
    setRiskAssessment,
    setIsLoadingHidden,
    setIsLoadingFuture,
    setIsLoadingGoals,
    setIsLoadingPersonality,
    setIsLoadingHealth,
    setIsLoadingLeaks,
    setIsLoadingRisk,
    fetchHiddenTruths,
    fetchFutureProjection,
    fetchGoalReality,
    fetchMoneyPersonality,
    fetchPortfolioHealth,
    fetchMoneyLeaks,
    fetchRiskAssessment,
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