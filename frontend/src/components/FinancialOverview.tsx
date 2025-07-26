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
    if (score >= 750) return 'text-green-600';
    if (score >= 650) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 750) return 'Excellent';
    if (score >= 650) return 'Good';
    return 'Poor';
  };

  return (
    <div className="space-y-6">
      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] shadow-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-300 font-medium">Total Portfolio Value</p>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-2xl font-semibold text-white">₹{(overviewData.totalCurrent / 100000).toFixed(1)}L</p>
            <div className="mt-2 flex items-center">
              <span className={`text-sm font-medium ${overviewData.totalReturns >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {overviewData.totalReturns >= 0 ? '+' : ''}₹{Math.abs(overviewData.totalReturns / 1000).toFixed(0)}K
              </span>
              <span className="text-gray-400 text-sm ml-2">
                ({overviewData.totalReturns >= 0 ? '+' : ''}{((overviewData.totalReturns / overviewData.totalInvested) * 100).toFixed(1)}%)
              </span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] shadow-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-300 font-medium">Average XIRR</p>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <p className="text-2xl font-semibold text-white">{overviewData.avgXIRR.toFixed(1)}%</p>
            <div className="mt-2">
              <span className="text-sm text-gray-400">Across {overviewData.fundCount} funds</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] shadow-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-300 font-medium">Credit Score</p>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p className={`text-2xl font-semibold ${getScoreColor(parseInt(overviewData.creditScore || '0'))}`}>
              {overviewData.creditScore || 'N/A'}
            </p>
            <div className="mt-2">
              <span className={`text-sm font-medium ${getScoreColor(parseInt(overviewData.creditScore || '0'))}`}>
                {overviewData.creditScore ? getScoreLabel(parseInt(overviewData.creditScore)) : 'Not Available'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Asset Allocation */}
      <Card className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] shadow-xl">
        <CardHeader className="border-b border-[rgba(0,184,153,0.2)]">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold text-white">Asset Allocation</CardTitle>
            <span className="text-sm text-gray-300">Total: ₹{(overviewData.totalAssets / 100000).toFixed(1)}L</span>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-4">
            {overviewData.assetAllocation.map((asset: any, index: number) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${
                      asset.type.includes('MUTUAL FUND') ? 'bg-blue-600' :
                      asset.type.includes('SAVINGS') ? 'bg-green-600' :
                      asset.type.includes('SECURITIES') ? 'bg-purple-600' :
                      'bg-orange-600'
                    }`}></div>
                    <span className="text-sm font-medium text-gray-300">{asset.type}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-semibold text-white">{asset.formatted}</span>
                    <span className="text-xs text-gray-400 ml-2">{asset.percentage.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="w-full bg-[rgba(0,184,153,0.1)] rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-500 ${
                      asset.type.includes('MUTUAL FUND') ? 'bg-blue-600' :
                      asset.type.includes('SAVINGS') ? 'bg-green-600' :
                      asset.type.includes('SECURITIES') ? 'bg-purple-600' :
                      'bg-orange-600'
                    }`}
                    style={{ width: `${asset.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Performing Funds */}
        <Card className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] shadow-xl">
          <CardHeader className="border-b border-[rgba(0,184,153,0.2)]">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-white">Top Performers</CardTitle>
              <span className="text-xs bg-[rgba(0,184,153,0.1)] text-[rgb(0,184,153)] px-2 py-1 rounded-full font-medium border border-[rgba(0,184,153,0.2)]">
                By XIRR
              </span>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-[rgba(0,184,153,0.1)]">
              {overviewData.topPerformers.map((fund, index) => (
                <div key={index} className="p-4 hover:bg-[rgba(0,184,153,0.05)] transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 pr-4">
                      <p className="text-sm font-medium text-white line-clamp-1">
                        {fund.schemeDetail?.nameData?.longName}
                      </p>
                      <div className="flex items-center space-x-3 mt-2">
                        <span className="text-xs bg-[rgba(0,184,153,0.1)] text-[rgb(0,184,153)] px-2 py-1 rounded border border-[rgba(0,184,153,0.2)]">
                          {fund.schemeDetail?.assetClass}
                        </span>
                        <span className="text-xs bg-[rgba(0,184,153,0.1)] text-[rgb(0,184,153)] px-2 py-1 rounded border border-[rgba(0,184,153,0.2)]">
                          {fund.schemeDetail?.fundhouseDefinedRiskLevel?.replace(/_/g, ' ')}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-white">
                        ₹{(fund.enrichedAnalytics.analytics.schemeDetails.currentValue.units / 100000).toFixed(1)}L
                      </p>
                      <p className="text-sm font-medium text-green-600 mt-1">
                        +{fund.enrichedAnalytics.analytics.schemeDetails.XIRR.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Credit Summary */}
        <Card className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] shadow-xl">
          <CardHeader className="border-b border-[rgba(0,184,153,0.2)]">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-white">Credit Overview</CardTitle>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                parseInt(overviewData.creditScore || '0') >= 750 ? 'bg-green-100 text-green-700' :
                parseInt(overviewData.creditScore || '0') >= 650 ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-700'
              }`}>
                Score: {overviewData.creditScore || 'N/A'}
              </span>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-300">Total Outstanding</span>
                  <span className="text-sm font-semibold text-white">
                    ₹{parseInt(overviewData.totalOutstanding?.outstandingBalanceAll || 0).toLocaleString()}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-3">
                  <div className="bg-[rgba(0,184,153,0.05)] rounded-lg p-3 border border-[rgba(0,184,153,0.1)]">
                    <p className="text-xs text-gray-400">Secured</p>
                    <p className="text-sm font-medium text-white">
                      ₹{parseInt(overviewData.totalOutstanding?.outstandingBalanceSecured || 0).toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-[rgba(0,184,153,0.05)] rounded-lg p-3 border border-[rgba(0,184,153,0.1)]">
                    <p className="text-xs text-gray-400">Unsecured</p>
                    <p className="text-sm font-medium text-white">
                      ₹{parseInt(overviewData.totalOutstanding?.outstandingBalanceUnSecured || 0).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              {overviewData.epfBalance && (
                <div className="pt-4 border-t border-[rgba(0,184,153,0.2)]">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-sm text-gray-300">EPF Balance</p>
                      <p className="text-xs text-gray-400 mt-1">Retirement Fund</p>
                    </div>
                    <p className="text-lg font-semibold text-white">
                      ₹{parseInt(overviewData.epfBalance).toLocaleString()}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Underperforming Funds Alert */}
      {overviewData.underPerformers.length > 0 && (
        <Card className="bg-[rgb(24,25,27)] border border-[rgba(220,53,69,0.3)] shadow-xl">
          <CardHeader className="border-b border-[rgba(220,53,69,0.3)]">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-red-400">
                Funds Needing Attention
              </CardTitle>
              <span className="text-xs bg-[rgba(220,53,69,0.1)] text-red-400 px-2 py-1 rounded-full font-medium border border-[rgba(220,53,69,0.2)]">
                {overviewData.underPerformers.length} funds with negative returns
              </span>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-3">
              {overviewData.underPerformers.slice(0, 3).map((fund, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-[rgba(220,53,69,0.05)] rounded-lg border border-[rgba(220,53,69,0.2)]">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-white line-clamp-1">
                      {fund.schemeDetail?.nameData?.longName}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      {fund.schemeDetail?.assetClass} • Current: ₹{(fund.enrichedAnalytics.analytics.schemeDetails.currentValue.units / 1000).toFixed(0)}K
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-red-400">
                      {fund.enrichedAnalytics.analytics.schemeDetails.XIRR.toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-400">XIRR</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}