'use client';

import { useState, useEffect } from 'react';
import MCPDataService from '@/services/mcpDataService';
import UnifiedCard, { CardHeader, CardContent } from '@/components/ui/UnifiedCard';
import UnifiedButton from '@/components/ui/UnifiedButton';
import StatCard from '@/components/ui/StatCard';
import { designSystem } from '@/styles/designSystem';

interface AnalyticsData {
  netWorth: number;
  netWorthFormatted: string;
  totalAssets: number;
  totalLiabilities: number;
  assetAllocation: Array<{
    name: string;
    value: number;
    percentage: number;
    color: string;
  }>;
  creditScore: string;
  creditHealth: string;
  mutualFundCount: number;
  avgXIRR: number;
  bestPerformer: string;
  worstPerformer: string;
  totalInvested: number;
  totalCurrent: number;
  totalReturns: number;
  epfBalance: number;
}

const EnhancedAnalytics = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const mcpService = MCPDataService.getInstance();
      const result = await mcpService.loadMCPData();

      if (result.success && result.data) {
        const transformedData = mcpService.transformToPortfolioFormat(result.data);
        
        // Process the raw MCP data for analytics
        const netWorthData = result.data.net_worth?.netWorthResponse;
        const creditReportData = result.data.credit_report?.creditReports?.[0]?.creditReportData;
        const mfSchemeAnalytics = netWorthData?.mfSchemeAnalytics?.schemeAnalytics || [];

        // Calculate asset allocation with colors
        const assetAllocation = (netWorthData?.assetValues || []).map((asset: any, index: number) => {
          const colors = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444'];
          const value = parseInt(asset.value.units) || 0;
          const total = transformedData.summary.total_assets;
          const percentage = total > 0 ? (value / total) * 100 : 0;
          
          return {
            name: asset.netWorthAttribute.replace('ASSET_TYPE_', '').replace(/_/g, ' '),
            value,
            percentage,
            color: colors[index % colors.length]
          };
        });

        // Calculate mutual fund performance
        const validFunds = mfSchemeAnalytics.filter((fund: any) => 
          fund.enrichedAnalytics?.analytics?.schemeDetails?.XIRR !== undefined
        );
        
        const avgXIRR = validFunds.length > 0 
          ? validFunds.reduce((sum: number, fund: any) => 
              sum + (fund.enrichedAnalytics.analytics.schemeDetails.XIRR || 0), 0) / validFunds.length
          : 0;

        // Find best and worst performers
        const sortedFunds = [...validFunds].sort((a: any, b: any) => 
          b.enrichedAnalytics.analytics.schemeDetails.XIRR - a.enrichedAnalytics.analytics.schemeDetails.XIRR
        );
        
        const bestPerformer = sortedFunds[0]?.schemeDetail?.nameData?.longName || 'N/A';
        const worstPerformer = sortedFunds[sortedFunds.length - 1]?.schemeDetail?.nameData?.longName || 'N/A';

        // Calculate totals
        const totalInvested = mfSchemeAnalytics.reduce((sum: number, fund: any) => 
          sum + (parseFloat(fund.enrichedAnalytics?.analytics?.schemeDetails?.investedValue?.units || '0')), 0);
        
        const totalCurrent = mfSchemeAnalytics.reduce((sum: number, fund: any) => 
          sum + (parseFloat(fund.enrichedAnalytics?.analytics?.schemeDetails?.currentValue?.units || '0')), 0);

        const totalReturns = totalCurrent - totalInvested;

        // Credit score and health
        const creditScore = creditReportData?.score?.bureauScore || 'N/A';
        const creditHealth = creditScore !== 'N/A' ? 
          (parseInt(creditScore) >= 750 ? 'Excellent' : 
           parseInt(creditScore) >= 650 ? 'Good' : 'Fair') : 'Unknown';

        setAnalyticsData({
          netWorth: transformedData.summary.total_net_worth,
          netWorthFormatted: transformedData.summary.total_net_worth_formatted,
          totalAssets: transformedData.summary.total_assets,
          totalLiabilities: transformedData.summary.total_liabilities,
          assetAllocation,
          creditScore,
          creditHealth,
          mutualFundCount: mfSchemeAnalytics.length,
          avgXIRR,
          bestPerformer,
          worstPerformer,
          totalInvested,
          totalCurrent,
          totalReturns,
          epfBalance: transformedData.summary.epf
        });

      } else {
        setError('Failed to load analytics data');
      }
    } catch (err) {
      console.error('Error loading analytics:', err);
      setError('Error loading financial analytics');
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (amount: number): string => {
    if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)}Cr`;
    if (amount >= 100000) return `₹${(amount / 100000).toFixed(2)}L`;
    if (amount >= 1000) return `₹${(amount / 1000).toFixed(2)}K`;
    return `₹${amount}`;
  };

  const LoadingCard = () => (
    <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6 animate-pulse">
      <div className="h-4 bg-[rgba(0,184,153,0.2)] rounded mb-4"></div>
      <div className="h-8 bg-[rgba(0,184,153,0.2)] rounded mb-2"></div>
      <div className="h-4 bg-[rgba(0,184,153,0.2)] rounded w-3/4"></div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-white tracking-tight">Financial Analytics</h2>
            <p className="text-gray-300 text-lg mt-2">Loading comprehensive portfolio analysis...</p>
          </div>
          <div className="w-20 h-8 bg-[rgba(0,184,153,0.2)] rounded-xl animate-pulse"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => <LoadingCard key={i} />)}
        </div>
      </div>
    );
  }

  if (error || !analyticsData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="bg-[rgb(24,25,27)] border border-[rgba(239,68,68,0.3)] rounded-2xl p-8 text-center max-w-md">
          <div className="w-16 h-16 bg-[rgba(239,68,68,0.1)] rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <p className="text-red-400 mb-6 text-lg font-medium">{error || 'No analytics data available'}</p>
          <UnifiedButton 
            onClick={loadAnalyticsData}
            variant="primary"
            className="w-full"
          >
            Retry Analytics
          </UnifiedButton>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Enhanced Header */}
      <div className="bg-gradient-to-r from-[rgb(24,25,27)] to-[rgb(28,29,31)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-14 h-14 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white tracking-tight">Financial Analytics</h2>
              <p className="text-gray-300 text-lg mt-1">Comprehensive analysis of your portfolio performance</p>
            </div>
          </div>
          <UnifiedButton
            onClick={loadAnalyticsData}
            variant="primary"
            size="md"
            className="flex items-center space-x-2 shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Refresh Data</span>
          </UnifiedButton>
        </div>
      </div>

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Net Worth Card */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6 shadow-xl hover:shadow-2xl hover:border-[rgba(0,184,153,0.4)] transition-all duration-300">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-sm font-semibold text-white mb-1">Net Worth</p>
              <p className="text-xs text-gray-300 font-medium">Total Assets vs Liabilities</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
              </svg>
            </div>
          </div>
          <div className="space-y-4">
            <h3 className="text-3xl font-bold text-white tracking-tight">{analyticsData.netWorthFormatted}</h3>
            <div className="space-y-2">
              <p className="text-sm text-gray-300">
                Assets: <span className="font-semibold text-[rgb(0,184,153)]">{formatCurrency(analyticsData.totalAssets)}</span>
              </p>
              <p className="text-sm text-gray-300">
                Liabilities: <span className="font-semibold text-red-400">{formatCurrency(analyticsData.totalLiabilities)}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Portfolio Returns Card */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6 shadow-xl hover:shadow-2xl hover:border-[rgba(0,184,153,0.4)] transition-all duration-300">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-sm font-semibold text-white mb-1">Portfolio Returns</p>
              <p className="text-xs text-gray-300 font-medium">Average XIRR across {analyticsData.mutualFundCount} funds</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
          <div className="space-y-4">
            <h3 className="text-3xl font-bold text-white tracking-tight">
              {analyticsData.avgXIRR > 0 ? '+' : ''}{analyticsData.avgXIRR.toFixed(1)}%
            </h3>
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
              analyticsData.avgXIRR > 0 
                ? 'bg-[rgba(0,184,153,0.1)] text-[rgb(0,184,153)] border border-[rgba(0,184,153,0.2)]' 
                : analyticsData.avgXIRR < 0
                ? 'bg-[rgba(239,68,68,0.1)] text-red-400 border border-[rgba(239,68,68,0.2)]'
                : 'bg-[rgba(156,163,175,0.1)] text-gray-400 border border-[rgba(156,163,175,0.2)]'
            }`}>
              {analyticsData.avgXIRR > 0 ? 'Positive Returns' : analyticsData.avgXIRR < 0 ? 'Negative Returns' : 'Neutral'}
            </div>
          </div>
        </div>

        {/* Credit Health Card */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6 shadow-xl hover:shadow-2xl hover:border-[rgba(0,184,153,0.4)] transition-all duration-300">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-sm font-semibold text-white mb-1">Credit Health</p>
              <p className="text-xs text-gray-300 font-medium">Current Credit Score Status</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div className="space-y-4">
            <h3 className="text-3xl font-bold text-white tracking-tight">{analyticsData.creditScore}</h3>
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
              analyticsData.creditHealth === 'Excellent' 
                ? 'bg-[rgba(0,184,153,0.1)] text-[rgb(0,184,153)] border border-[rgba(0,184,153,0.2)]' 
                : analyticsData.creditHealth === 'Good'
                ? 'bg-[rgba(245,158,11,0.1)] text-yellow-400 border border-[rgba(245,158,11,0.2)]'
                : 'bg-[rgba(239,68,68,0.1)] text-red-400 border border-[rgba(239,68,68,0.2)]'
            }`}>
              {analyticsData.creditHealth}
            </div>
          </div>
        </div>
      </div>

      {/* Asset Allocation Analysis */}
      <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6 shadow-xl hover:shadow-2xl hover:border-[rgba(0,184,153,0.4)] transition-all duration-300">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
            </svg>
          </div>
          <div>
            <h3 className="text-xl font-bold text-white mb-1">Asset Allocation</h3>
            <p className="text-sm text-gray-300">Portfolio distribution across asset classes</p>
          </div>
        </div>
        <div className="space-y-5">
          {analyticsData.assetAllocation.map((asset, index) => (
            <div key={index} className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-4 h-4 rounded-full shadow-sm" 
                    style={{ backgroundColor: asset.color }}
                  ></div>
                  <span className="font-semibold text-white text-sm">{asset.name}</span>
                </div>
                <div className="text-right">
                  <span className="font-bold text-white">{formatCurrency(asset.value)}</span>
                  <span className="text-gray-300 ml-2 text-sm">({asset.percentage.toFixed(1)}%)</span>
                </div>
              </div>
              <div className="w-full bg-[rgba(0,184,153,0.1)] rounded-full h-3 overflow-hidden">
                <div 
                  className="h-3 rounded-full transition-all duration-700 ease-out shadow-sm"
                  style={{ 
                    width: `${asset.percentage}%`,
                    backgroundColor: asset.color 
                  }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Performance Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Investment Performance */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6 shadow-xl hover:shadow-2xl hover:border-[rgba(0,184,153,0.4)] transition-all duration-300">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-bold text-white mb-1">Investment Performance</h3>
              <p className="text-sm text-gray-300">Portfolio growth metrics</p>
            </div>
          </div>
          <div className="space-y-5">
            <div className="flex justify-between items-center p-3 bg-[rgba(0,184,153,0.05)] rounded-xl">
              <span className="text-gray-300 font-medium">Total Invested</span>
              <span className="font-bold text-white">{formatCurrency(analyticsData.totalInvested)}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-[rgba(0,184,153,0.05)] rounded-xl">
              <span className="text-gray-300 font-medium">Current Value</span>
              <span className="font-bold text-white">{formatCurrency(analyticsData.totalCurrent)}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-[rgba(0,184,153,0.05)] rounded-xl">
              <span className="text-gray-300 font-medium">Total Returns</span>
              <span className={`font-bold ${
                analyticsData.totalReturns >= 0 ? 'text-[rgb(0,184,153)]' : 'text-red-400'
              }`}>
                {analyticsData.totalReturns >= 0 ? '+' : ''}{formatCurrency(analyticsData.totalReturns)}
              </span>
            </div>
            <div className="border-t border-[rgba(0,184,153,0.2)] pt-4">
              <div className="flex justify-between items-center p-3 bg-[rgba(0,184,153,0.1)] rounded-xl">
                <span className="text-white font-semibold">Return Percentage</span>
                <span className={`font-bold text-lg ${
                  analyticsData.totalReturns >= 0 ? 'text-[rgb(0,184,153)]' : 'text-red-400'
                }`}>
                  {analyticsData.totalReturns >= 0 ? '+' : ''}{
                    analyticsData.totalInvested > 0 
                      ? ((analyticsData.totalReturns / analyticsData.totalInvested) * 100).toFixed(2)
                      : '0.00'
                  }%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Fund Performance & EPF */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6 shadow-xl hover:shadow-2xl hover:border-[rgba(0,184,153,0.4)] transition-all duration-300">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-bold text-white mb-1">Fund Analysis</h3>
              <p className="text-sm text-gray-300">Top performers & retirement funds</p>
            </div>
          </div>
          <div className="space-y-5">
            <div className="p-4 bg-[rgba(0,184,153,0.05)] rounded-xl">
              <p className="text-sm text-gray-300 font-medium mb-2">🏆 Best Performer</p>
              <p className="font-bold text-[rgb(0,184,153)] text-sm leading-relaxed">
                {analyticsData.bestPerformer}
              </p>
            </div>
            <div className="p-4 bg-[rgba(239,68,68,0.05)] rounded-xl">
              <p className="text-sm text-gray-300 font-medium mb-2">⚠️ Needs Attention</p>
              <p className="font-bold text-red-400 text-sm leading-relaxed">
                {analyticsData.worstPerformer}
              </p>
            </div>
            <div className="border-t border-[rgba(0,184,153,0.2)] pt-4">
              <div className="p-4 bg-[rgba(0,184,153,0.1)] rounded-xl">
                <p className="text-sm text-white font-semibold mb-2">💼 EPF Balance</p>
                <p className="font-bold text-[rgb(0,184,153)] text-lg">
                  {formatCurrency(analyticsData.epfBalance)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Data Source Indicator */}
      <div className="flex items-center justify-center space-x-3 py-6">
        <div className="flex items-center space-x-2 bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-full px-4 py-2">
          <div className="w-2 h-2 bg-[rgb(0,184,153)] rounded-full animate-pulse"></div>
          <span className="text-sm font-semibold text-white">Live data from Artha AI</span>
          <div className="w-2 h-2 bg-[rgb(0,184,153)] rounded-full animate-pulse"></div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedAnalytics;