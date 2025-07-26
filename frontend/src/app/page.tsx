'use client';

import { useState, useEffect } from 'react';
import Dashboard from '@/components/Dashboard';
import ChatInterface from '@/components/ChatInterface';
import FinancialOverview from '@/components/FinancialOverview';
import MoneyTruthEngine from '@/components/MoneyTruthEngine';
import HydrationProvider from '@/components/HydrationProvider';
import EnhancedFinancialStats from '@/components/EnhancedFinancialStats';
import EnhancedAnalytics from '@/components/EnhancedAnalytics';
import LocalLLMInsights from '@/components/LocalLLMInsights';
import UnifiedCard from '@/components/ui/UnifiedCard';
import UnifiedButton from '@/components/ui/UnifiedButton';
import FiMoneyWebAuth from '@/components/FiMoneyWebAuth';
import { designSystem } from '@/styles/designSystem';
import MCPDataService from '@/services/mcpDataService';

export default function Home() {
  const [financialData, setFinancialData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('portfolio');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authError, setAuthError] = useState('');
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  const mcpService = MCPDataService.getInstance();

  useEffect(() => {
    checkAuthenticationAndFetchData();
  }, []);

  const checkAuthenticationAndFetchData = async () => {
    setIsCheckingAuth(true);
    try {
      // Check if already authenticated with Fi Money
      const authStatus = await mcpService.checkAuthenticationStatus();
      
      if (authStatus.authenticated) {
        console.log('✅ Already authenticated with Fi Money MCP');
        setIsAuthenticated(true);
        await fetchFinancialData();
      } else {
        console.log('🔐 Fi Money authentication required');
        setIsAuthenticated(false);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsAuthenticated(false);
      setIsLoading(false);
    }
    setIsCheckingAuth(false);
  };

  const fetchFinancialData = async () => {
    try {
      console.log('🔄 Loading real-time financial data from Fi Money MCP...');
      setIsLoading(true);
      
      const result = await mcpService.loadMCPData();
      
      if (result.success && result.data) {
        console.log('✅ Real-time financial data loaded successfully from Fi Money');
        const transformedData = mcpService.transformToPortfolioFormat(result.data);
        setFinancialData(transformedData);
        setAuthError('');
      } else if (result.authRequired) {
        console.log('🔐 Fi Money authentication required');
        setIsAuthenticated(false);
        setAuthError(result.error || 'Please authenticate with Fi Money');
      } else {
        throw new Error(result.error || 'Failed to load financial data from Fi Money');
      }
      
    } catch (error) {
      console.error('💥 Error loading financial data from Fi Money:', error);
      setFinancialData(null);
      if (error instanceof Error && (error.message.includes('authentication') || error.message.includes('expired'))) {
        setIsAuthenticated(false);
        setAuthError('Session expired. Please authenticate again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleAuthSuccess = async () => {
    console.log('✅ Fi Money authentication successful');
    setIsAuthenticated(true);
    setAuthError('');
    await fetchFinancialData();
  };

  const handleAuthError = (error: string) => {
    console.error('❌ Fi Money authentication failed:', error);
    setAuthError(error);
    setIsAuthenticated(false);
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

  // Show authentication screen if not authenticated
  if (!isAuthenticated) {
    return (
      <HydrationProvider>
        <div className="min-h-screen bg-[rgb(0,26,30)]">
          {/* Fi Money Auth Header */}
          <header className="bg-[rgba(26,26,26,0.95)] backdrop-blur-xl border-b border-[rgba(0,184,153,0.2)] sticky top-0 z-50 shadow-2xl">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-20">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-2xl flex items-center justify-center shadow-xl">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                  <div>
                    <h1 className="text-2xl font-black text-white tracking-tight">Artha AI</h1>
                    <p className="text-xs text-[rgb(0,184,153)] font-semibold">AI Financial Intelligence</p>
                  </div>
                </div>
              </div>
            </div>
          </header>

          {/* Fi Money Authentication Content */}
          <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-black text-white mb-6">
                Connect to Fi Money for Real-Time Financial Intelligence
              </h2>
              <p className="text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
                Get AI-powered insights on your complete financial portfolio with live data from Fi Money's MCP server
              </p>
            </div>

            {authError && (
              <div className="mb-8 max-w-md mx-auto">
                <div className="bg-[rgba(220,53,69,0.1)] border border-[rgba(220,53,69,0.3)] rounded-2xl p-4">
                  <p className="text-sm text-red-400">{authError}</p>
                </div>
              </div>
            )}

            <div className="max-w-md mx-auto">
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

  const navigationItems = [
    { id: 'portfolio', label: 'Portfolio', icon: 'M4 7v10c0 2.21 3.79 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.79 4 8 4s8-1.79 8-4M4 7c0-2.21 3.79-4 8-4s8 1.79 8 4' },
    { id: 'analytics', label: 'Analytics', icon: 'M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z' },
    { id: 'advisory', label: 'AI Chat', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' },
    { id: 'insights', label: 'Agents', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
    { id: 'local-ai', label: 'Local AI', icon: 'M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18' }
  ];

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
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                  <div>
                    <h1 className="text-2xl font-black text-white tracking-tight">Artha</h1>
                    <p className="text-xs text-[rgb(0,184,153)] font-semibold">AI Financial Intelligence</p>
                  </div>
                </div>
                
                {/* Fi Money Navigation */}
                <nav className="hidden md:flex items-center bg-[rgba(30,30,30,0.8)] rounded-2xl p-2 backdrop-blur-sm border border-[rgba(70,68,68,0.3)]">
                  {navigationItems.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setActiveTab(item.id)}
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
              
              {/* Fi Money User Section */}
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.3)] rounded-2xl flex items-center justify-center shadow-lg">
                    <span className="text-sm font-bold text-[rgb(0,184,153)]">VS</span>
                  </div>
                  <div className="hidden md:block">
                    <p className="text-sm font-bold text-white">Visvanth Sai</p>
                    <p className="text-xs text-[rgb(0,184,153)]">Premium Member</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Fi Money Mobile Navigation */}
        <div className="md:hidden bg-[rgba(26,26,26,0.95)] backdrop-blur-xl border-b border-[rgba(0,184,153,0.2)]">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex space-x-1 py-3">
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
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
          </div>
        </div>

        {/* Fi Money Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Fi Money Portfolio Header */}
          {activeTab === 'portfolio' && financialData && (
            <div className="mb-10">
              <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-8 shadow-2xl">
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-4xl font-black text-white tracking-tight mb-2">Fi Money Portfolio</h1>
                    <p className="text-gray-300 text-lg font-medium">Real-time financial intelligence powered by Fi Money MCP</p>
                    <div className="flex items-center mt-4 space-x-2">
                      <div className="w-3 h-3 bg-[rgb(0,184,153)] rounded-full animate-pulse"></div>
                      <span className="text-sm text-[rgb(0,184,153)] font-bold">Live Fi Money Data</span>
                      <span className="text-sm text-gray-400">• No Sample Data • Production Ready</span>
                    </div>
                  </div>
                  <div className="text-right bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.3)] backdrop-blur-sm rounded-2xl p-6">
                    <p className="text-sm text-gray-300 font-semibold mb-1">Total Net Worth</p>
                    <p className="text-3xl font-black text-white tracking-tight">{financialData?.summary?.total_net_worth_formatted || '₹0'}</p>
                    <div className="flex items-center justify-end mt-3 space-x-2">
                      <svg className="w-4 h-4 text-[rgb(0,184,153)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-xs text-[rgb(0,184,153)] font-bold">Fi Money MCP</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Show Fi Money Auth in header for logged in users */}
          <div className="mb-6">
            <FiMoneyWebAuth
              onAuthSuccess={handleAuthSuccess}
              onAuthError={handleAuthError}
            />
          </div>
          
          {/* Premium Content Sections */}
          <div className="space-y-8">
            {activeTab === 'portfolio' && <Dashboard financialData={financialData} />}
            {activeTab === 'analytics' && <EnhancedAnalytics />}
            {activeTab === 'advisory' && <ChatInterface />}
            {activeTab === 'insights' && <MoneyTruthEngine financialData={financialData} />}
            {activeTab === 'local-ai' && <LocalLLMInsights />}
          </div>
        </main>
      </div>
    </HydrationProvider>
  );
}
