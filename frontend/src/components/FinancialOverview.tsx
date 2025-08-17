'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface FinancialOverviewProps {
  financialData: any;
}

export default function FinancialOverview({ financialData }: FinancialOverviewProps) {
  
  // Process financial data for detailed overview
  const processOverviewData = (data: any) => {
    if (!data?.summary && !data?.data) return null;

    // Handle both old format (from static files) and new format (from backend)
    const mcpData = data.data || data;
    const netWorthData = mcpData.net_worth;
    const creditData = mcpData.credit_report;
    const epfData = mcpData.epf_details;

    // Calculate asset allocation
    const assets = netWorthData?.netWorthResponse?.assetValues || [];
    const totalAssets = assets.reduce((sum: number, asset: any) => sum + parseFloat(asset.value?.units || '0'), 0);
    
    const assetAllocation = assets.map((asset: any) => {
      const amount = parseFloat(asset.value?.units || '0');
      const percentage = totalAssets > 0 ? (amount / totalAssets) * 100 : 0;
      return {
        type: asset.netWorthAttribute.replace('ASSET_TYPE_', '').replace(/_/g, ' '),
        amount: amount,
        percentage: percentage,
        formatted: `₹${(amount / 100000).toFixed(1)}L`
      };
    });

    // Process mutual fund analytics
    const mfAnalytics = netWorthData?.mfSchemeAnalytics?.schemeAnalytics || [];
    const topPerformers = mfAnalytics
      .filter((fund: any) => fund.enrichedAnalytics?.analytics?.schemeDetails?.XIRR)
      .sort((a: any, b: any) => b.enrichedAnalytics.analytics.schemeDetails.XIRR - a.enrichedAnalytics.analytics.schemeDetails.XIRR)
      .slice(0, 5);

    const underPerformers = mfAnalytics
      .filter((fund: any) => fund.enrichedAnalytics?.analytics?.schemeDetails?.XIRR < 0)
      .sort((a: any, b: any) => a.enrichedAnalytics.analytics.schemeDetails.XIRR - b.enrichedAnalytics.analytics.schemeDetails.XIRR);

    // Calculate portfolio metrics
    const totalInvested = mfAnalytics.reduce((sum: number, fund: any) => 
      sum + parseFloat(fund.enrichedAnalytics?.analytics?.schemeDetails?.investedValue?.units || '0'), 0);
    const totalCurrent = mfAnalytics.reduce((sum: number, fund: any) => 
      sum + parseFloat(fund.enrichedAnalytics?.analytics?.schemeDetails?.currentValue?.units || '0'), 0);
    const totalReturns = totalCurrent - totalInvested;
    const avgXIRR = mfAnalytics.length > 0 
      ? mfAnalytics.reduce((sum: number, fund: any) => sum + (fund.enrichedAnalytics?.analytics?.schemeDetails?.XIRR || 0), 0) / mfAnalytics.length
      : 0;

    // Credit insights
    const creditScore = creditData?.creditReports?.[0]?.creditReportData?.score?.bureauScore;
    const creditAccounts = creditData?.creditReports?.[0]?.creditReportData?.creditAccount?.creditAccountDetails || [];
    const totalOutstanding = creditData?.creditReports?.[0]?.creditReportData?.creditAccount?.creditAccountSummary?.totalOutstandingBalance;

    // Liabilities
    const liabilities = netWorthData?.netWorthResponse?.liabilityValues || [];
    const totalLiabilities = liabilities.reduce((sum: number, liability: any) => 
      sum + parseFloat(liability.value?.units || '0'), 0);

    return {
      netWorth: parseFloat(netWorthData?.netWorthResponse?.totalNetWorthValue?.units || '0'),
      assetAllocation,
      topPerformers,
      underPerformers,
      creditScore,
      creditAccounts: creditAccounts.slice(0, 5),
      totalOutstanding,
      epfBalance: epfData?.uanAccounts?.[0]?.rawDetails?.overall_pf_balance?.current_pf_balance,
      totalAssets,
      totalLiabilities,
      totalInvested,
      totalCurrent,
      totalReturns,
      avgXIRR,
      fundCount: mfAnalytics.length
    };
  };

  // Add loading state and better error handling
  const [isLoading, setIsLoading] = useState(true);
  const [overviewData, setOverviewData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadOverviewData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        if (!financialData) {
          // If no data passed, fetch directly from backend
          const mcpService = (await import('../services/mcpDataService')).default.getInstance();
          const result = await mcpService.loadMCPData();
          
          if (result.success && result.data) {
            const processed = processOverviewData(result);
            setOverviewData(processed);
          } else {
            setError('Failed to load financial data');
          }
        } else {
          // Use passed data
          const processed = processOverviewData(financialData);
          setOverviewData(processed);
        }
      } catch (err) {
        console.error('Error loading overview data:', err);
        setError('Error loading financial overview');
      } finally {
        setIsLoading(false);
      }
    };

    loadOverviewData();
  }, [financialData]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500">Loading financial analytics...</p>
        </div>
      </div>
    );
  }

  if (error || !overviewData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-red-500 mb-2">{error || 'No financial data available'}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 750) return 'text-[#cca695]';
    if (score >= 650) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 750) return 'Excellent';
    if (score >= 650) return 'Good';
    return 'Poor';
  };

  return (
    <div className="space-y-8">
      {/* Main Financial Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Net Worth */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(204,166,149,0.2)] rounded-3xl p-6 shadow-xl hover:border-[rgba(204,166,149,0.5)] transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-semibold text-gray-300 mb-1">Net Worth</p>
              <p className="text-xs text-gray-400 font-medium">Assets vs Liabilities</p>
            </div>
            <div className="w-12 h-12 bg-[#cca695] rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <h3 className="text-3xl font-bold text-white tracking-tight mb-2">₹{(overviewData.netWorth / 100000).toFixed(2)}L</h3>
          <p className="text-sm text-gray-300">
            Assets: ₹{(overviewData.totalAssets / 100000).toFixed(2)}L | Liabilities: ₹{(overviewData.totalLiabilities / 1000).toFixed(0)}K
          </p>
        </div>

        {/* Portfolio Returns */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(204,166,149,0.2)] rounded-3xl p-6 shadow-xl hover:border-[rgba(204,166,149,0.5)] transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-semibold text-gray-300 mb-1">Portfolio Returns</p>
              <p className="text-xs text-gray-400 font-medium">Avg XIRR across {overviewData.fundCount} funds</p>
            </div>
            <div className="w-12 h-12 bg-[#cca695] rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
          <h3 className="text-3xl font-bold text-white tracking-tight mb-2">{overviewData.avgXIRR.toFixed(1)}%</h3>
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
            overviewData.avgXIRR > 12 
              ? 'bg-[rgba(204,166,149,0.1)] text-[#cca695] border border-[rgba(204,166,149,0.2)]' 
              : overviewData.avgXIRR > 8
              ? 'bg-[rgba(245,158,11,0.1)] text-yellow-400 border border-[rgba(245,158,11,0.2)]'
              : 'bg-[rgba(220,53,69,0.1)] text-red-400 border border-[rgba(220,53,69,0.2)]'
          }`}>
            {overviewData.avgXIRR > 12 ? 'Excellent' : overviewData.avgXIRR > 8 ? 'Good' : 'Neutral'}
          </div>
        </div>

        {/* Credit Health */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(204,166,149,0.2)] rounded-3xl p-6 shadow-xl hover:border-[rgba(204,166,149,0.5)] transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-semibold text-gray-300 mb-1">Credit Health</p>
              <p className="text-xs text-gray-400 font-medium">
                {overviewData.creditScore ? getScoreLabel(parseInt(overviewData.creditScore)) : 'Not Available'}
              </p>
            </div>
            <div className="w-12 h-12 bg-[#cca695] rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
          <h3 className={`text-3xl font-bold tracking-tight mb-2 ${getScoreColor(parseInt(overviewData.creditScore || '0'))}`}>
            {overviewData.creditScore || 'N/A'}
          </h3>
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
            parseInt(overviewData.creditScore || '0') >= 750 
              ? 'bg-[rgba(204,166,149,0.1)] text-[#cca695] border border-[rgba(204,166,149,0.2)]' 
              : parseInt(overviewData.creditScore || '0') >= 650
              ? 'bg-[rgba(245,158,11,0.1)] text-yellow-400 border border-[rgba(245,158,11,0.2)]'
              : 'bg-[rgba(220,53,69,0.1)] text-red-400 border border-[rgba(220,53,69,0.2)]'
          }`}>
            {overviewData.creditScore ? getScoreLabel(parseInt(overviewData.creditScore)) : 'Unknown'}
          </div>
        </div>

        {/* EPF Balance */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(204,166,149,0.2)] rounded-3xl p-6 shadow-xl hover:border-[rgba(204,166,149,0.5)] transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-semibold text-gray-300 mb-1">EPF Balance</p>
              <p className="text-xs text-gray-400 font-medium">Employee Provident Fund</p>
            </div>
            <div className="w-12 h-12 bg-[#cca695] rounded-2xl flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </div>
          <h3 className="text-3xl font-bold text-white tracking-tight mb-2">
            ₹{overviewData.epfBalance ? (parseInt(overviewData.epfBalance) / 100000).toFixed(2) : '0'}L
          </h3>
          <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-[rgba(204,166,149,0.1)] text-[#cca695] border border-[rgba(204,166,149,0.2)]">
            Active
          </div>
        </div>
      </div>

      {/* Asset Allocation */}
      <div className="bg-[rgb(24,25,27)] border border-[rgba(204,166,149,0.2)] rounded-3xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold text-white mb-1">Asset Allocation</h3>
            <p className="text-sm text-gray-300">Portfolio distribution by asset class</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {overviewData.assetAllocation.map((asset: any, index: number) => (
            <div key={index} className="bg-[rgba(204,166,149,0.05)] border border-[rgba(204,166,149,0.1)] rounded-2xl p-4">
              <div className="flex items-center justify-between mb-3">
                <div className={`w-4 h-4 rounded-full ${
                  asset.type.includes('MUTUAL FUND') ? 'bg-blue-500' :
                  asset.type.includes('SAVINGS') ? 'bg-[#cca695]' :
                  asset.type.includes('SECURITIES') ? 'bg-purple-500' :
                  'bg-orange-500'
                }`}></div>
                <span className="text-lg font-bold text-white">{asset.percentage.toFixed(1)}%</span>
              </div>
              <h4 className="text-sm font-semibold text-white mb-1">{asset.type}</h4>
              <p className="text-lg font-bold text-[#cca695]">{asset.formatted}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Investment Performance */}
      <div className="bg-[rgb(24,25,27)] border border-[rgba(204,166,149,0.2)] rounded-3xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold text-white mb-1">Investment Performance</h3>
            <p className="text-sm text-gray-300">Mutual funds and equity returns</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <p className="text-sm text-gray-400 mb-2">Total Invested</p>
            <p className="text-2xl font-bold text-white">₹{(overviewData.totalInvested / 100000).toFixed(1)}L</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-400 mb-2">Current Value</p>
            <p className="text-2xl font-bold text-white">₹{(overviewData.totalCurrent / 100000).toFixed(1)}L</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-400 mb-2">Total Returns</p>
            <p className={`text-2xl font-bold ${overviewData.totalReturns >= 0 ? 'text-[#cca695]' : 'text-red-400'}`}>
              {overviewData.totalReturns >= 0 ? '+' : ''}₹{(overviewData.totalReturns / 100000).toFixed(1)}L
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-400 mb-2">Return Percentage</p>
            <p className={`text-2xl font-bold ${overviewData.totalReturns >= 0 ? 'text-[#cca695]' : 'text-red-400'}`}>
              {overviewData.totalReturns >= 0 ? '+' : ''}{overviewData.totalInvested > 0 ? ((overviewData.totalReturns / overviewData.totalInvested) * 100).toFixed(2) : '0.00'}%
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top & Bottom Performers */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(204,166,149,0.2)] rounded-3xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-bold text-white mb-1">Top & Bottom Performers</h3>
              <p className="text-sm text-gray-300">Best and worst performing funds</p>
            </div>
          </div>
          
          <div className="space-y-6">
            {/* Best Performer */}
            <div>
              <h4 className="text-sm font-semibold text-[#cca695] mb-3">Best Performer</h4>
              {overviewData.topPerformers.length > 0 ? (
                <div className="bg-[rgba(204,166,149,0.05)] border border-[rgba(204,166,149,0.1)] rounded-xl p-4">
                  <p className="text-sm font-medium text-white line-clamp-2 mb-2">
                    {overviewData.topPerformers[0].schemeDetail?.nameData?.longName}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs bg-[rgba(204,166,149,0.1)] text-[#cca695] px-2 py-1 rounded border border-[rgba(204,166,149,0.2)]">
                      {overviewData.topPerformers[0].schemeDetail?.assetClass}
                    </span>
                    <span className="text-lg font-bold text-[#cca695]">
                      +{overviewData.topPerformers[0].enrichedAnalytics.analytics.schemeDetails.XIRR.toFixed(1)}%
                    </span>
                  </div>
                </div>
              ) : (
                <div className="bg-[rgba(70,68,68,0.3)] border border-[rgba(70,68,68,0.5)] rounded-xl p-4">
                  <p className="text-center text-gray-400">N/A</p>
                </div>
              )}
            </div>

            {/* Needs Attention */}
            <div>
              <h4 className="text-sm font-semibold text-red-400 mb-3">Needs Attention</h4>
              {overviewData.underPerformers.length > 0 ? (
                <div className="bg-[rgba(220,53,69,0.05)] border border-[rgba(220,53,69,0.2)] rounded-xl p-4">
                  <p className="text-sm font-medium text-white line-clamp-2 mb-2">
                    {overviewData.underPerformers[0].schemeDetail?.nameData?.longName}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs bg-[rgba(220,53,69,0.1)] text-red-400 px-2 py-1 rounded border border-[rgba(220,53,69,0.2)]">
                      {overviewData.underPerformers[0].schemeDetail?.assetClass}
                    </span>
                    <span className="text-lg font-bold text-red-400">
                      {overviewData.underPerformers[0].enrichedAnalytics.analytics.schemeDetails.XIRR.toFixed(1)}%
                    </span>
                  </div>
                </div>
              ) : (
                <div className="bg-[rgba(70,68,68,0.3)] border border-[rgba(70,68,68,0.5)] rounded-xl p-4">
                  <p className="text-center text-gray-400">N/A</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Additional EPF Details */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(204,166,149,0.2)] rounded-3xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-bold text-white mb-1">EPF Balance</h3>
              <p className="text-sm text-gray-300">Employee Provident Fund details</p>
            </div>
          </div>
          
          <div className="text-center">
            <p className="text-4xl font-bold text-[#cca695] mb-4">
              ₹{overviewData.epfBalance ? (parseInt(overviewData.epfBalance) / 100000).toFixed(2) : '0'}L
            </p>
            <div className="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-[rgba(204,166,149,0.1)] text-[#cca695] border border-[rgba(204,166,149,0.2)]">
              Active Contribution
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}