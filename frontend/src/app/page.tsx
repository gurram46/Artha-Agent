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
import MCPDataService from '@/services/mcpDataService';

export default function Home() {
  const [financialData, setFinancialData] = useState(null);
  const [activeTab, setActiveTab] = useState('portfolio');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authError, setAuthError] = useState('');
  const [isDemoMode, setIsDemoMode] = useState(false);

  const mcpService = MCPDataService.getInstance();

  useEffect(() => {
    // Check if demo mode is already enabled
    const demoMode = sessionStorage.getItem('demoMode') === 'true';
    if (demoMode) {
      setIsDemoMode(true);
      setIsAuthenticated(true);
      loadFinancialDataImmediately();
    }
  }, []);

  const loadFinancialDataImmediately = async () => {
    try {
      console.log('🎭 Loading MCP data from local files...');
      
      // Set demo mode
      mcpService.setDemoMode(true);
      
      // Load data immediately
      const result = await mcpService.loadMCPData();
      
      if (result.success && result.data) {
        console.log('✅ Local MCP data loaded successfully');
        const transformedData = mcpService.transformToPortfolioFormat(result.data);
        setFinancialData(transformedData);
        setAuthError('');
      } else {
        console.warn('⚠️ Failed to load local MCP data');
        setAuthError('Unable to load financial data');
      }
      
    } catch (error) {
      console.error('❌ Error loading local MCP data:', error);
      setAuthError('Error loading financial data');
    }
  };

  const handleAuthSuccess = async () => {
    console.log('✅ Authentication successful');
    setIsAuthenticated(true);
    setAuthError('');
    
    // Check if demo mode was enabled
    const demoMode = sessionStorage.getItem('demoMode') === 'true';
    setIsDemoMode(demoMode);
    
    await loadFinancialDataImmediately();
  };

  const handleAuthError = (error: string) => {
    console.error('❌ Authentication failed:', error);
    setAuthError(error);
    setIsAuthenticated(false);
  };


  // No loading screens - go straight to the app

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
                    <p className="text-xs text-[rgb(0,184,153)] font-semibold">
                      Local MCP Data • AI Financial Intelligence
                    </p>
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

        {/* Compact Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          {/* Compact Portfolio Header */}
          {activeTab === 'portfolio' && financialData && (
            <div className="mb-6">
              <div className="bg-gradient-to-r from-[rgb(24,25,27)] to-[rgb(28,29,31)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-5 shadow-xl">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-xl flex items-center justify-center shadow-lg">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    </div>
                    <div>
                      <h1 className="text-xl font-bold text-white tracking-tight">
                        MCP Portfolio
                      </h1>
                      <div className="flex items-center mt-1 space-x-2">
                        <div className="w-2 h-2 rounded-full bg-[rgb(0,184,153)] animate-pulse"></div>
                        <span className="text-xs font-medium text-[rgb(0,184,153)]">
                          Local MCP Data
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-400 font-medium">Total Value</p>
                    <p className="text-2xl font-bold text-white">{financialData?.summary?.total_net_worth_formatted || '₹0'}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* No authentication needed - using local MCP data */}
          
          {/* Compact Content Sections */}
          <div className="space-y-5">
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
