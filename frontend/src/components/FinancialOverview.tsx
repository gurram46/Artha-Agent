'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface FinancialOverviewProps {
  financialData: any;
}

export default function FinancialOverview({ financialData }: FinancialOverviewProps) {
  
  // Process financial data for detailed overview
  const processOverviewData = (data: any) => {
    if (!data?.data) return null;

    const mcpData = data.data;
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

  const overviewData = processOverviewData(financialData);

  if (!overviewData) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-gray-500">Loading financial overview...</p>
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
        <Card className="bg-white border border-gray-200 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-600 font-medium">Total Portfolio Value</p>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-2xl font-semibold text-gray-900">₹{(overviewData.totalCurrent / 100000).toFixed(1)}L</p>
            <div className="mt-2 flex items-center">
              <span className={`text-sm font-medium ${overviewData.totalReturns >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {overviewData.totalReturns >= 0 ? '+' : ''}₹{Math.abs(overviewData.totalReturns / 1000).toFixed(0)}K
              </span>
              <span className="text-gray-500 text-sm ml-2">
                ({overviewData.totalReturns >= 0 ? '+' : ''}{((overviewData.totalReturns / overviewData.totalInvested) * 100).toFixed(1)}%)
              </span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border border-gray-200 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-600 font-medium">Average XIRR</p>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <p className="text-2xl font-semibold text-gray-900">{overviewData.avgXIRR.toFixed(1)}%</p>
            <div className="mt-2">
              <span className="text-sm text-gray-500">Across {overviewData.fundCount} funds</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border border-gray-200 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-600 font-medium">Credit Score</p>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p className={`text-2xl font-semibold ${getScoreColor(parseInt(overviewData.creditScore))}`}>
              {overviewData.creditScore}
            </p>
            <div className="mt-2">
              <span className={`text-sm font-medium ${getScoreColor(parseInt(overviewData.creditScore))}`}>
                {getScoreLabel(parseInt(overviewData.creditScore))}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Asset Allocation */}
      <Card className="bg-white border border-gray-200 shadow-sm">
        <CardHeader className="border-b border-gray-200">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold text-gray-900">Asset Allocation</CardTitle>
            <span className="text-sm text-gray-500">Total: ₹{(overviewData.totalAssets / 100000).toFixed(1)}L</span>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-4">
            {overviewData.assetAllocation.map((asset, index) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${
                      asset.type.includes('MUTUAL FUND') ? 'bg-blue-600' :
                      asset.type.includes('SAVINGS') ? 'bg-green-600' :
                      asset.type.includes('SECURITIES') ? 'bg-purple-600' :
                      'bg-orange-600'
                    }`}></div>
                    <span className="text-sm font-medium text-gray-700">{asset.type}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-semibold text-gray-900">{asset.formatted}</span>
                    <span className="text-xs text-gray-500 ml-2">{asset.percentage.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
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
        <Card className="bg-white border border-gray-200 shadow-sm">
          <CardHeader className="border-b border-gray-200">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-gray-900">Top Performers</CardTitle>
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
                By XIRR
              </span>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-gray-200">
              {overviewData.topPerformers.map((fund, index) => (
                <div key={index} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 pr-4">
                      <p className="text-sm font-medium text-gray-900 line-clamp-1">
                        {fund.schemeDetail?.nameData?.longName}
                      </p>
                      <div className="flex items-center space-x-3 mt-2">
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                          {fund.schemeDetail?.assetClass}
                        </span>
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                          {fund.schemeDetail?.fundhouseDefinedRiskLevel?.replace(/_/g, ' ')}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">
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
        <Card className="bg-white border border-gray-200 shadow-sm">
          <CardHeader className="border-b border-gray-200">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-gray-900">Credit Overview</CardTitle>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                parseInt(overviewData.creditScore) >= 750 ? 'bg-green-100 text-green-700' :
                parseInt(overviewData.creditScore) >= 650 ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-700'
              }`}>
                Score: {overviewData.creditScore}
              </span>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Total Outstanding</span>
                  <span className="text-sm font-semibold text-gray-900">
                    ₹{parseInt(overviewData.totalOutstanding?.outstandingBalanceAll || 0).toLocaleString()}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-3">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-500">Secured</p>
                    <p className="text-sm font-medium text-gray-900">
                      ₹{parseInt(overviewData.totalOutstanding?.outstandingBalanceSecured || 0).toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-500">Unsecured</p>
                    <p className="text-sm font-medium text-gray-900">
                      ₹{parseInt(overviewData.totalOutstanding?.outstandingBalanceUnSecured || 0).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              {overviewData.epfBalance && (
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-sm text-gray-600">EPF Balance</p>
                      <p className="text-xs text-gray-500 mt-1">Retirement Fund</p>
                    </div>
                    <p className="text-lg font-semibold text-gray-900">
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
        <Card className="bg-red-50 border border-red-200">
          <CardHeader className="border-b border-red-200">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-red-900">
                Funds Needing Attention
              </CardTitle>
              <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full font-medium">
                {overviewData.underPerformers.length} funds with negative returns
              </span>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-3">
              {overviewData.underPerformers.slice(0, 3).map((fund, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg border border-red-100">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 line-clamp-1">
                      {fund.schemeDetail?.nameData?.longName}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {fund.schemeDetail?.assetClass} • Current: ₹{(fund.enrichedAnalytics.analytics.schemeDetails.currentValue.units / 1000).toFixed(0)}K
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-red-600">
                      {fund.enrichedAnalytics.analytics.schemeDetails.XIRR.toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-500">XIRR</p>
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