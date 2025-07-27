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
    <UnifiedCard className="animate-pulse">
      <div className="h-4 bg-slate-200 rounded mb-4"></div>
      <div className="h-8 bg-slate-200 rounded mb-2"></div>
      <div className="h-4 bg-slate-200 rounded w-3/4"></div>
    </UnifiedCard>
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className={designSystem.typography.heading.large}>Financial Analytics</h2>
          <div className="w-20 h-8 bg-slate-200 rounded animate-pulse"></div>
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
        <UnifiedCard className="text-center max-w-md">
          <p className="text-red-500 mb-4">{error || 'No analytics data available'}</p>
          <UnifiedButton 
            onClick={loadAnalyticsData}
            variant="primary"
          >
            Retry
          </UnifiedButton>
        </UnifiedCard>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={designSystem.typography.heading.large}>Financial Analytics</h2>
          <p className={designSystem.typography.body.small}>Comprehensive analysis of your portfolio</p>
        </div>
        <UnifiedButton
          onClick={loadAnalyticsData}
          variant="primary"
          size="sm"
          className="flex items-center space-x-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Refresh</span>
        </UnifiedButton>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <UnifiedCard className="p-6 bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] shadow-xl hover:shadow-2xl transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-1">Net Worth</p>
              <p className="text-xs text-gray-500 font-medium">Assets vs Liabilities</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
              </svg>
            </div>
          </div>
          <div className="space-y-3">
            <h3 className="text-3xl font-bold text-gray-900 tracking-tight">{analyticsData.netWorthFormatted}</h3>
            <p className="text-sm text-gray-600">
              Assets: <span className="font-semibold text-green-600">{formatCurrency(analyticsData.totalAssets)}</span> | 
              Liabilities: <span className="font-semibold text-red-600">{formatCurrency(analyticsData.totalLiabilities)}</span>
            </p>
          </div>
        </UnifiedCard>

        <UnifiedCard className="p-6 bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] shadow-xl hover:shadow-2xl transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-1">Portfolio Returns</p>
              <p className="text-xs text-gray-500 font-medium">Avg XIRR across {analyticsData.mutualFundCount} funds</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
          <div className="space-y-3">
            <h3 className="text-3xl font-bold text-gray-900 tracking-tight">
              {analyticsData.avgXIRR > 0 ? '+' : ''}{analyticsData.avgXIRR.toFixed(1)}%
            </h3>
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
              analyticsData.avgXIRR > 0 
                ? 'bg-green-100 text-green-700' 
                : analyticsData.avgXIRR < 0
                ? 'bg-red-100 text-red-700'
                : 'bg-[rgba(156,163,175,0.1)] text-gray-400'
            }`}>
              {analyticsData.avgXIRR > 0 ? 'Positive' : analyticsData.avgXIRR < 0 ? 'Negative' : 'Neutral'}
            </div>
          </div>
        </UnifiedCard>

        <UnifiedCard className="p-6 bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] shadow-xl hover:shadow-2xl transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-1">Credit Health</p>
              <p className="text-xs text-gray-500 font-medium">{analyticsData.creditHealth}</p>
            </div>
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
          <div className="space-y-3">
            <h3 className="text-3xl font-bold text-gray-900 tracking-tight">{analyticsData.creditScore}</h3>
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
              analyticsData.creditHealth === 'Excellent' 
                ? 'bg-green-100 text-green-700' 
                : analyticsData.creditHealth === 'Good'
                ? 'bg-yellow-100 text-yellow-700'
                : 'bg-red-100 text-red-700'
            }`}>
              {analyticsData.creditHealth}
            </div>
          </div>
        </UnifiedCard>
      </div>

      {/* Asset Allocation Chart */}
      <UnifiedCard className="p-6 bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] shadow-xl">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">Asset Allocation</h3>
          <p className="text-sm text-gray-600">Portfolio distribution by asset class</p>
        </div>
        <div className="space-y-4">
          {analyticsData.assetAllocation.map((asset, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: asset.color }}
                  ></div>
                  <span className="font-medium text-gray-900">{asset.name}</span>
                </div>
                <div className="text-right">
                  <span className="font-semibold text-gray-900">{formatCurrency(asset.value)}</span>
                  <span className="text-gray-500 ml-2">({asset.percentage.toFixed(1)}%)</span>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="h-2 rounded-full transition-all duration-500"
                  style={{ 
                    width: `${asset.percentage}%`,
                    backgroundColor: asset.color 
                  }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </UnifiedCard>

      {/* Compact Performance Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <UnifiedCard className="p-6 bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] shadow-xl">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">Investment Performance</h3>
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Total Invested</span>
              <span className="font-semibold text-gray-900">{formatCurrency(analyticsData.totalInvested)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Current Value</span>
              <span className="font-semibold text-gray-900">{formatCurrency(analyticsData.totalCurrent)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Total Returns</span>
              <span className={`font-semibold ${
                analyticsData.totalReturns >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {analyticsData.totalReturns >= 0 ? '+' : ''}{formatCurrency(analyticsData.totalReturns)}
              </span>
            </div>
            <div className="border-t border-gray-200 pt-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-medium">Return Percentage</span>
                <span className={`font-semibold ${
                  analyticsData.totalReturns >= 0 ? 'text-green-600' : 'text-red-600'
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
        </UnifiedCard>

        <UnifiedCard className="p-6 bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] shadow-xl">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">Top & Bottom Performers</h3>
          </div>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600 font-medium mb-2">Best Performer</p>
              <p className="font-semibold text-green-600 text-sm">
                {analyticsData.bestPerformer}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 font-medium mb-2">Needs Attention</p>
              <p className="font-semibold text-red-600 text-sm">
                {analyticsData.worstPerformer}
              </p>
            </div>
            <div className="border-t border-gray-200 pt-4">
              <p className="text-sm text-gray-600 font-medium mb-2">EPF Balance</p>
              <p className="font-semibold text-blue-600">
                {formatCurrency(analyticsData.epfBalance)}
              </p>
            </div>
          </div>
        </UnifiedCard>
      </div>

      {/* Data Source Indicator */}
      <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
        <span className="font-medium">Live data from Artha AI backend</span>
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
      </div>
    </div>
  );
};

export default EnhancedAnalytics;