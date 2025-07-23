'use client';

import { useState, useEffect } from 'react';
import Dashboard from '@/components/Dashboard';
import ChatInterface from '@/components/ChatInterface';
import FinancialOverview from '@/components/FinancialOverview';
import MoneyTruthEngine from '@/components/MoneyTruthEngine';
import HydrationProvider from '@/components/HydrationProvider';

export default function Home() {
  const [financialData, setFinancialData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('portfolio');

  useEffect(() => {
    fetchFinancialData();
  }, []);

  const fetchFinancialData = async () => {
    try {
      console.log('🔄 Loading real financial data from MCP docs...');
      
      // Load real MCP data from docs directory
      const { loadMCPData } = await import('../services/mcpDataService');
      const mcpService = (await import('../services/mcpDataService')).default.getInstance();
      
      const result = await mcpService.loadMCPData();
      
      if (result.success && result.data) {
        console.log('✅ Real MCP data loaded successfully:', result.data);
        const transformedData = mcpService.transformToPortfolioFormat(result.data);
        setFinancialData(transformedData);
        return;
      } else {
        throw new Error(result.error || 'Failed to load MCP data');
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
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center space-y-8 max-w-md">
          <div className="relative">
            <div className="w-20 h-20 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
            <div className="absolute inset-0 w-20 h-20 border-4 border-transparent border-r-slate-300 rounded-full animate-spin mx-auto" style={{animationDirection: 'reverse', animationDuration: '3s'}}></div>
          </div>
          <div className="space-y-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-slate-700 rounded-xl flex items-center justify-center mx-auto shadow-lg">
              <svg className="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-slate-900">Artha Wealth Intelligence</h2>
            <p className="text-slate-600 text-lg">Loading real financial data from MCP...</p>
            <div className="flex items-center justify-center space-x-2 text-sm text-slate-500">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
              <span>Processing Fi MCP response data</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const navigationItems = [
    { id: 'portfolio', label: 'Portfolio', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
    { id: 'analytics', label: 'Analytics', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
    { id: 'advisory', label: 'Advisory', icon: 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
    { id: 'insights', label: 'Insights', icon: 'M13 10V3L4 14h7v7l9-11h-7z' }
  ];

  return (
    <HydrationProvider>
      <div className="min-h-screen bg-slate-50">
        {/* Enhanced Header with Glassmorphism */}
        <header className="bg-white/80 backdrop-blur-xl border-b border-slate-200/50 shadow-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6">
            <div className="flex items-center justify-between h-18">
              <div className="flex items-center space-x-12">
                {/* Enhanced Brand */}
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-600 via-slate-700 to-slate-900 rounded-xl flex items-center justify-center shadow-lg">
                      <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                      </svg>
                    </div>
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white animate-pulse"></div>
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-900 via-blue-800 to-slate-700 bg-clip-text text-transparent">Artha</h1>
                    <p className="text-xs text-slate-600 font-medium tracking-wide">WEALTH INTELLIGENCE</p>
                  </div>
                </div>
                
                {/* Enhanced Navigation */}
                <nav className="hidden lg:flex items-center space-x-2">
                  {navigationItems.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setActiveTab(item.id)}
                      className={`relative flex items-center space-x-2 px-5 py-3 text-sm font-medium rounded-xl transition-all duration-300 group ${
                        activeTab === item.id
                          ? 'text-blue-700 bg-blue-50 shadow-md border border-blue-200'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50/80'
                      }`}
                    >
                      <svg className={`w-4 h-4 transition-transform duration-300 ${
                        activeTab === item.id ? 'scale-110' : 'group-hover:scale-105'
                      }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                      </svg>
                      <span>{item.label}</span>
                      {activeTab === item.id && (
                        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-blue-600 rounded-full"></div>
                      )}
                    </button>
                  ))}
                </nav>
              </div>
              
              <div className="flex items-center space-x-6">
                {/* Enhanced Status Indicators */}
                <div className="hidden md:flex items-center space-x-4">
                  <div className="flex items-center space-x-3 px-4 py-2 bg-emerald-50 rounded-xl border border-emerald-200">
                    <div className="relative">
                      <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                      <div className="absolute inset-0 w-2 h-2 bg-emerald-500 rounded-full animate-ping opacity-30"></div>
                    </div>
                    <span className="text-sm font-semibold text-emerald-700">Live Markets</span>
                  </div>
                  <div className="flex items-center space-x-3 px-4 py-2 bg-blue-50 rounded-xl border border-blue-200">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-sm font-semibold text-blue-700">Real-time Data</span>
                  </div>
                </div>
                
                {/* Enhanced User Menu */}
                <div className="flex items-center space-x-3">
                  <button className="p-3 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-all duration-200 hover:scale-105">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                  </button>
                  <div className="relative">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-slate-700 rounded-xl flex items-center justify-center shadow-lg border-2 border-white">
                      <span className="text-sm font-bold text-white">VS</span>
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full border-2 border-white flex items-center justify-center">
                      <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Mobile Navigation */}
        <div className="lg:hidden bg-white border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-6">
            <div className="grid grid-cols-4 gap-1 py-3">
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex flex-col items-center space-y-1 py-2 text-xs font-medium rounded-lg transition-colors ${
                    activeTab === item.id
                      ? 'text-slate-900 bg-slate-100'
                      : 'text-slate-600'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                  </svg>
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Enhanced Main Content with Welcome Section */}
        <main className="max-w-7xl mx-auto px-6">
          {/* Welcome Hero Section */}
          {activeTab === 'portfolio' && (
            <div className="py-8 mb-8">
              <div className="bg-gradient-to-r from-blue-600 via-slate-700 to-slate-900 rounded-3xl p-8 text-white relative overflow-hidden">
                <div className="absolute inset-0 bg-black/20"></div>
                <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-32 translate-x-32"></div>
                <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-24 -translate-x-24"></div>
                <div className="relative z-10">
                  <div className="flex items-center justify-between">
                    <div className="space-y-4">
                      <div className="flex items-center space-x-3">
                        <div className="px-3 py-1 bg-white/20 rounded-full text-sm font-medium backdrop-blur-sm">
                          ✨ Welcome back
                        </div>
                        <div className="px-3 py-1 bg-emerald-500/30 rounded-full text-sm font-medium backdrop-blur-sm">
                          Portfolio Active
                        </div>
                      </div>
                      <h1 className="text-4xl font-bold leading-tight">
                        Your Financial
                        <br />
                        <span className="text-blue-200">Dashboard</span>
                      </h1>
                      <p className="text-xl text-blue-100 max-w-md">
                        Track, analyze, and optimize your wealth with AI-powered insights
                      </p>
                    </div>
                    <div className="hidden lg:block">
                      <div className="text-right space-y-2">
                        <p className="text-sm text-blue-200 font-medium">Total Portfolio Value</p>
                        <p className="text-3xl font-bold">{financialData?.summary?.total_net_worth_formatted || '₹0'}</p>
                        <div className="flex items-center justify-end space-x-2">
                          <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                          <span className="text-sm text-emerald-200">Live tracking</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div className="pb-8">
            {activeTab === 'portfolio' && <Dashboard financialData={financialData} />}
            {activeTab === 'analytics' && <FinancialOverview financialData={financialData} />}
            {activeTab === 'advisory' && <ChatInterface />}
            {activeTab === 'insights' && <MoneyTruthEngine financialData={financialData} />}
          </div>
        </main>
      </div>
    </HydrationProvider>
  );
}
