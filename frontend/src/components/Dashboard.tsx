'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface DashboardProps {
  financialData: any;
}

export default function Dashboard({ financialData }: DashboardProps) {

  // Process real Fi MCP data
  const processFinancialData = (data: any) => {
    if (!data?.data) {
      return {
        netWorth: '₹0',
        liquidFunds: '₹0',
        investments: '₹0',
        debt: '₹0',
        creditScore: 'N/A',
        assets: [],
        liabilities: [],
        mutualFunds: [],
        bankAccounts: [],
        monthlyChange: 0,
        yearlyReturn: 0
      };
    }

    const mcpData = data.data;
    const netWorthData = mcpData.net_worth;
    
    // Process net worth
    const totalNetWorth = netWorthData?.netWorthResponse?.totalNetWorthValue?.units || '0';
    const netWorthFormatted = `₹${(parseFloat(totalNetWorth) / 100000).toFixed(1)}L`;

    // Process assets
    const assets = netWorthData?.netWorthResponse?.assetValues || [];
    let liquidFunds = 0;
    let investments = 0;
    
    const processedAssets = assets.map((asset: any) => {
      const amount = parseFloat(asset.value?.units || '0');
      const type = asset.netWorthAttribute;
      
      if (type.includes('SAVINGS_ACCOUNTS')) {
        liquidFunds += amount;
      } else if (type.includes('MUTUAL_FUND') || type.includes('SECURITIES')) {
        investments += amount;
      }
      
      return {
        type: type.replace('ASSET_TYPE_', '').replace('_', ' '),
        amount: amount,
        formatted: `₹${(amount / 100000).toFixed(1)}L`
      };
    });

    // Process liabilities
    const liabilities = netWorthData?.netWorthResponse?.liabilityValues || [];
    let totalDebt = 0;
    
    const processedLiabilities = liabilities.map((liability: any) => {
      const amount = parseFloat(liability.value?.units || '0');
      totalDebt += amount;
      
      return {
        type: liability.netWorthAttribute.replace('LIABILITY_TYPE_', '').replace('_', ' '),
        amount: amount,
        formatted: `₹${(amount / 1000).toFixed(0)}K`
      };
    });

    // Process mutual funds
    const mutualFunds = netWorthData?.mfSchemeAnalytics?.schemeAnalytics?.slice(0, 5) || [];
    const processedMutualFunds = mutualFunds.map((fund: any) => {
      const currentValue = parseFloat(fund.enrichedAnalytics?.analytics?.schemeDetails?.currentValue?.units || '0');
      const investedValue = parseFloat(fund.enrichedAnalytics?.analytics?.schemeDetails?.investedValue?.units || '0');
      const xirr = fund.enrichedAnalytics?.analytics?.schemeDetails?.XIRR || 0;
      
      return {
        name: fund.schemeDetail?.nameData?.longName || 'Unknown Fund',
        currentValue: currentValue,
        investedValue: investedValue,
        xirr: xirr,
        returns: currentValue - investedValue,
        riskLevel: fund.schemeDetail?.fundhouseDefinedRiskLevel || 'UNKNOWN',
        assetClass: fund.schemeDetail?.assetClass || 'UNKNOWN'
      };
    });

    // Calculate average returns
    const avgReturns = mutualFunds.length > 0 
      ? mutualFunds.reduce((sum: number, fund: any) => sum + (fund.enrichedAnalytics?.analytics?.schemeDetails?.XIRR || 0), 0) / mutualFunds.length
      : 0;

    // Process bank accounts
    const accountsMap = netWorthData?.accountDetailsBulkResponse?.accountDetailsMap || {};
    const bankAccounts = Object.values(accountsMap)
      .filter((account: any) => account.depositSummary?.currentBalance)
      .map((account: any) => ({
        bank: account.accountDetails?.fipMeta?.displayName || 'Unknown Bank',
        balance: parseFloat(account.depositSummary?.currentBalance?.units || '0'),
        type: account.depositSummary?.depositAccountType?.replace('DEPOSIT_ACCOUNT_TYPE_', '') || 'UNKNOWN'
      }));

    // Get credit score
    const creditScore = mcpData.credit_report?.creditReports?.[0]?.creditReportData?.score?.bureauScore || 'N/A';

    return {
      netWorth: netWorthFormatted,
      netWorthRaw: parseFloat(totalNetWorth),
      liquidFunds: `₹${(liquidFunds / 100000).toFixed(1)}L`,
      liquidFundsRaw: liquidFunds,
      investments: `₹${(investments / 100000).toFixed(1)}L`,
      investmentsRaw: investments,
      debt: `₹${(totalDebt / 1000).toFixed(0)}K`,
      debtRaw: totalDebt,
      creditScore: creditScore,
      assets: processedAssets,
      liabilities: processedLiabilities,
      mutualFunds: processedMutualFunds,
      bankAccounts: bankAccounts,
      monthlyChange: 2.4, // Mock for now
      yearlyReturn: avgReturns
    };
  };

  const data = processFinancialData(financialData);

  return (
    <div className="space-y-6">
      {/* Professional Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-white border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-600 font-medium">Net Worth</p>
                <p className="text-2xl font-semibold text-gray-900 mt-1">{data.netWorth}</p>
              </div>
              <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="flex items-center text-sm">
              <span className="text-green-600 font-medium">↑ {data.monthlyChange}%</span>
              <span className="text-gray-500 ml-2">vs last month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-600 font-medium">Investments</p>
                <p className="text-2xl font-semibold text-gray-900 mt-1">{data.investments}</p>
              </div>
              <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
            <div className="flex items-center text-sm">
              <span className="text-green-600 font-medium">↑ {data.yearlyReturn.toFixed(1)}%</span>
              <span className="text-gray-500 ml-2">avg XIRR</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-600 font-medium">Liquid Funds</p>
                <p className="text-2xl font-semibold text-gray-900 mt-1">{data.liquidFunds}</p>
              </div>
              <div className="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
            <div className="flex items-center text-sm">
              <span className="text-gray-600">{data.bankAccounts.length} accounts</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-600 font-medium">Credit Score</p>
                <p className="text-2xl font-semibold text-gray-900 mt-1">{data.creditScore}</p>
              </div>
              <div className="w-12 h-12 bg-orange-50 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
            <div className="flex items-center text-sm">
              <span className={`font-medium ${parseInt(data.creditScore) >= 750 ? 'text-green-600' : 'text-orange-600'}`}>
                {parseInt(data.creditScore) >= 750 ? 'Excellent' : 'Good'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Asset Allocation Chart */}
      <Card className="bg-white border border-gray-200 shadow-sm">
        <CardHeader className="border-b border-gray-200">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold text-gray-900">Asset Allocation</CardTitle>
            <span className="text-sm text-gray-500">Updated just now</span>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex-1">
              <div className="relative h-4 bg-gray-100 rounded-full overflow-hidden">
                <div 
                  className="absolute h-full bg-blue-600 transition-all duration-500"
                  style={{ width: `${(data.liquidFundsRaw / data.netWorthRaw) * 100}%` }}
                />
                <div 
                  className="absolute h-full bg-green-600 transition-all duration-500"
                  style={{ 
                    left: `${(data.liquidFundsRaw / data.netWorthRaw) * 100}%`,
                    width: `${(data.investmentsRaw / data.netWorthRaw) * 100}%` 
                  }}
                />
              </div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-blue-600 rounded"></div>
              <div>
                <p className="text-sm text-gray-600">Liquid Funds</p>
                <p className="font-semibold text-gray-900">{data.liquidFunds}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-600 rounded"></div>
              <div>
                <p className="text-sm text-gray-600">Investments</p>
                <p className="font-semibold text-gray-900">{data.investments}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mutual Funds Performance */}
        <Card className="bg-white border border-gray-200 shadow-sm">
          <CardHeader className="border-b border-gray-200">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-gray-900">Mutual Funds</CardTitle>
              <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">View All</button>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-gray-200">
              {data.mutualFunds.slice(0, 3).map((fund: any, index: number) => (
                <div key={index} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 pr-4">
                      <p className="text-sm font-medium text-gray-900 line-clamp-1">{fund.name}</p>
                      <p className="text-xs text-gray-500 mt-1">{fund.assetClass} • {fund.riskLevel.replace('_', ' ')}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">₹{(fund.currentValue / 1000).toFixed(1)}K</p>
                      <p className={`text-xs font-medium mt-1 ${fund.xirr > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {fund.xirr > 0 ? '+' : ''}{fund.xirr.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Returns</span>
                      <span className={fund.returns > 0 ? 'text-green-600' : 'text-red-600'}>
                        {fund.returns > 0 ? '+' : ''}₹{Math.abs(fund.returns / 1000).toFixed(1)}K
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        className={`h-1.5 rounded-full ${fund.returns > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ width: `${Math.min(Math.abs(fund.returns) / fund.investedValue * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Bank Accounts */}
        <Card className="bg-white border border-gray-200 shadow-sm">
          <CardHeader className="border-b border-gray-200">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-gray-900">Bank Accounts</CardTitle>
              <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">Add Account</button>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-gray-200">
              {data.bankAccounts.map((account, index) => (
                <div key={index} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{account.bank}</p>
                      <p className="text-xs text-gray-500 mt-1">{account.type}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">₹{(account.balance / 1000).toFixed(0)}K</p>
                      <p className="text-xs text-gray-500">₹{account.balance.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Investment Analysis', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', color: 'blue' },
          { label: 'Tax Planning', icon: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z', color: 'green' },
          { label: 'Goal Tracker', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4', color: 'purple' },
          { label: 'Reports', icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', color: 'orange' }
        ].map((action, index) => (
          <button key={index} className="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-all group">
            <div className={`w-10 h-10 bg-${action.color}-50 rounded-lg flex items-center justify-center mb-3 group-hover:bg-${action.color}-100 transition-colors`}>
              <svg className={`w-5 h-5 text-${action.color}-600`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={action.icon} />
              </svg>
            </div>
            <p className="text-sm font-medium text-gray-900">{action.label}</p>
          </button>
        ))}
      </div>
    </div>
  );
}