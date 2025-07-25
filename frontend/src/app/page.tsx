'use client';

import { useState, useEffect } from 'react';
import Dashboard from '@/components/Dashboard';
import ChatInterface from '@/components/ChatInterface';
import FinancialOverview from '@/components/FinancialOverview';
import MoneyTruthEngine from '@/components/MoneyTruthEngine';
import HydrationProvider from '@/components/HydrationProvider';
import EnhancedFinancialStats from '@/components/EnhancedFinancialStats';
import EnhancedAnalytics from '@/components/EnhancedAnalytics';
import UnifiedCard from '@/components/ui/UnifiedCard';
import UnifiedButton from '@/components/ui/UnifiedButton';
import { designSystem } from '@/styles/designSystem';

export default function Home() {
  const [financialData, setFinancialData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('portfolio');

  useEffect(() => {
    fetchFinancialData();
  }, []);

  const fetchFinancialData = async () => {
    try {
      console.log('🔄 Loading financial data from backend API...');
      
      // Use the enhanced MCP service that connects to backend
      const mcpService = (await import('../services/mcpDataService')).default.getInstance();
      
      const result = await mcpService.loadMCPData();
      
      if (result.success && result.data) {
        console.log('✅ Financial data loaded successfully from backend');
        const transformedData = mcpService.transformToPortfolioFormat(result.data);
        setFinancialData(transformedData);
        return;
      } else {
        throw new Error(result.error || 'Failed to load financial data');
      }
      
    } catch (error) {
      console.error('💥 Error loading financial data:', error);
      setFinancialData(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Transformation handled by MCPDataService

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Artha</h2>
            <p className="text-gray-600">Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  const navigationItems = [
    { id: 'portfolio', label: 'Portfolio', icon: 'M4 7v10c0 2.21 3.79 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.79 4 8 4s8-1.79 8-4M4 7c0-2.21 3.79-4 8-4s8 1.79 8 4' },
    { id: 'analytics', label: 'Analytics', icon: 'M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z' },
    { id: 'advisory', label: 'AI Chat', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' },
    { id: 'insights', label: 'Insights', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' }
  ];

  return (
    <HydrationProvider>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/30">
        {/* Modern Premium Header */}
        <header className="bg-white/80 backdrop-blur-xl border-b border-gray-200/50 sticky top-0 z-50 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-18">
              {/* Premium Brand */}
              <div className="flex items-center space-x-8">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Artha</h1>
                    <p className="text-xs text-gray-500 font-medium">AI Financial Intelligence</p>
                  </div>
                </div>
                
                {/* Modern Navigation */}
                <nav className="hidden md:flex items-center bg-gray-100/80 rounded-2xl p-1 backdrop-blur-sm">
                  {navigationItems.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setActiveTab(item.id)}
                      className={`flex items-center space-x-2 px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-300 ${
                        activeTab === item.id
                          ? 'bg-white text-blue-600 shadow-md transform scale-105'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
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
              
              {/* Premium User Section */}
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center shadow-sm">
                    <span className="text-sm font-semibold text-gray-700">VS</span>
                  </div>
                  <div className="hidden md:block">
                    <p className="text-sm font-semibold text-gray-900">Visvanth Sai</p>
                    <p className="text-xs text-gray-500">Premium Member</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Modern Mobile Navigation */}
        <div className="md:hidden bg-white/90 backdrop-blur-xl border-b border-gray-200/50">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex space-x-1 py-3">
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex-1 flex flex-col items-center py-3 text-xs font-semibold rounded-xl transition-all duration-300 ${
                    activeTab === item.id
                      ? 'text-blue-600 bg-blue-50 shadow-sm transform scale-105'
                      : 'text-gray-600 hover:bg-gray-50'
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

        {/* Modern Premium Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Premium Portfolio Header */}
          {activeTab === 'portfolio' && financialData && (
            <div className="mb-10">
              <div className="bg-gradient-to-r from-white/80 to-blue-50/50 backdrop-blur-sm rounded-3xl p-8 border border-gray-200/50 shadow-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-4xl font-bold text-gray-900 tracking-tight mb-2">Portfolio Overview</h1>
                    <p className="text-gray-600 text-lg font-medium">Track your investments and performance with AI-powered insights</p>
                  </div>
                  <div className="text-right bg-white/60 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/30">
                    <p className="text-sm text-gray-500 font-semibold mb-1">Total Portfolio Value</p>
                    <p className="text-3xl font-bold text-gray-900 tracking-tight">{financialData?.summary?.total_net_worth_formatted || '₹0'}</p>
                    <div className="flex items-center justify-end mt-2 space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-xs text-green-600 font-semibold">Live Data</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Premium Content Sections */}
          <div className="space-y-8">
            {activeTab === 'portfolio' && <Dashboard financialData={financialData} />}
            {activeTab === 'analytics' && <EnhancedAnalytics />}
            {activeTab === 'advisory' && <ChatInterface />}
            {activeTab === 'insights' && <MoneyTruthEngine financialData={financialData} />}
          </div>
        </main>
      </div>
    </HydrationProvider>
  );
}
