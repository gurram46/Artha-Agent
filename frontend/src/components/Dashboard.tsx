'use client';

import { useState, useEffect, useMemo, memo, useCallback } from 'react';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, AreaChart, Area, RadialBarChart, RadialBar, ComposedChart, Scatter, ScatterChart } from 'recharts';
import StocksList from './StocksList';
import UserRiskProfile from './UserRiskProfile';
import InvestmentRecommendationCard from './InvestmentRecommendationCard';
import CreditCardTransactions from './CreditCardTransactions';

interface Props {
  financialData: any;
}

interface MetricCardProps {
  title: string;
  value: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  subtitle: string;
  icon: string;
}

const MetricCard = ({ title, value, change, changeType, subtitle, icon }: MetricCardProps) => (
  <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 group hover:border-[rgba(0,184,153,0.5)] transition-all duration-300 shadow-xl hover:shadow-2xl">
    <div className="flex items-center justify-between mb-4">
      <div>
        <p className="text-sm font-semibold text-gray-300 mb-1">{title}</p>
        <p className="text-xs text-gray-400 font-medium">{subtitle}</p>
      </div>
      <div className="w-12 h-12 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon} />
        </svg>
      </div>
    </div>
    <div className="space-y-3">
      <h3 className="text-3xl font-bold text-white tracking-tight">{value}</h3>
      {change && changeType && (
        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
          changeType === 'positive' 
            ? 'bg-[rgba(0,184,153,0.1)] text-[rgb(0,184,153)] border border-[rgba(0,184,153,0.2)]' 
            : changeType === 'negative'
            ? 'bg-[rgba(220,53,69,0.1)] text-red-400 border border-[rgba(220,53,69,0.2)]'
            : 'bg-[rgba(70,68,68,0.3)] text-gray-300 border border-[rgba(70,68,68,0.5)]'
        }`}>
          {changeType === 'positive' && (
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          )}
          {changeType === 'negative' && (
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          )}
          {change}
        </div>
      )}
    </div>
  </div>
);

const PerformanceChart = memo(({ schemes }: { schemes: any[] }) => {
  // Generate performance data based on schemes
  const performanceData = schemes.slice(0, 6).map((scheme, index) => ({
    name: scheme.name.substring(0, 15) + '...',
    returns: scheme.xirr || 0,
    invested: scheme.investedValue / 100000,
    current: scheme.currentValue / 100000,
  }));

  return (
    <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white">Fund Performance</h3>
          <p className="text-sm font-medium text-gray-300">XIRR vs Investment Amount</p>
        </div>
      </div>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 184, 153, 0.1)" />
            <XAxis 
              dataKey="name" 
              stroke="#9ca3af" 
              fontSize={12}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis stroke="#9ca3af" fontSize={12} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgb(24, 25, 27)', 
                border: '1px solid rgba(0, 184, 153, 0.2)',
                borderRadius: '12px',
                fontSize: '12px',
                color: 'white'
              }}
              formatter={(value: any, name: string) => [
                name === 'returns' ? `${value.toFixed(1)}%` : `₹${value.toFixed(1)}L`,
                name === 'returns' ? 'XIRR' : name === 'invested' ? 'Invested' : 'Current Value'
              ]}
            />
            <Bar dataKey="invested" fill="rgba(0, 184, 153, 0.3)" name="invested" />
            <Bar dataKey="current" fill="rgb(0, 184, 153)" name="current" />
            <Line type="monotone" dataKey="returns" stroke="rgb(0, 164, 133)" strokeWidth={3} name="returns" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
});

const RiskReturnScatter = memo(({ schemes }: { schemes: any[] }) => {
  const scatterData = schemes.map((scheme, index) => ({
    x: Math.abs(scheme.xirr) || 0, // Returns
    y: scheme.riskLevel === 'VERY_HIGH_RISK' ? 5 : 
       scheme.riskLevel === 'HIGH_RISK' ? 4 :
       scheme.riskLevel === 'MODERATE_RISK' ? 3 :
       scheme.riskLevel === 'LOW_RISK' ? 2 : 1, // Risk Score
    name: scheme.name.substring(0, 20),
    value: scheme.currentValue / 100000,
    category: scheme.assetClass
  }));

  return (
    <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white">Risk vs Return Analysis</h3>
          <p className="text-sm font-medium text-gray-300">Portfolio risk-return mapping</p>
        </div>
      </div>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 184, 153, 0.1)" />
            <XAxis 
              type="number" 
              dataKey="x" 
              name="Returns" 
              unit="%" 
              stroke="#9ca3af"
              fontSize={12}
            />
            <YAxis 
              type="number" 
              dataKey="y" 
              name="Risk" 
              stroke="#9ca3af"
              fontSize={12}
              domain={[0, 6]}
              tickFormatter={(value) => {
                const labels = ['', 'Very Low', 'Low', 'Moderate', 'High', 'Very High'];
                return labels[value] || '';
              }}
            />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{ 
                backgroundColor: 'rgb(24, 25, 27)', 
                border: '1px solid rgba(0, 184, 153, 0.2)',
                borderRadius: '12px',
                fontSize: '12px',
                color: 'white'
              }}
              formatter={(value: any, name: string) => [
                name === 'x' ? `${value.toFixed(1)}%` : 
                name === 'y' ? (['', 'Very Low', 'Low', 'Moderate', 'High', 'Very High'][value] || value) :
                `₹${value.toFixed(1)}L`,
                name === 'x' ? 'Returns (XIRR)' : 
                name === 'y' ? 'Risk Level' : 'Current Value'
              ]}
              labelFormatter={(label, payload) => payload[0]?.payload?.name || ''}
            />
            <Scatter data={scatterData} fill="rgb(0, 184, 153)" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
});

const MutualFundBreakdown = memo(({ schemes }: { schemes: any[] }) => {
  const categoryData = schemes.reduce((acc: any, scheme) => {
    const category = scheme.category || 'OTHERS';
    if (!acc[category]) {
      acc[category] = { 
        name: category.replace(/_/g, ' '), 
        value: 0, 
        count: 0,
        totalReturns: 0,
        avgXIRR: 0
      };
    }
    acc[category].value += scheme.currentValue;
    acc[category].count += 1;
    acc[category].totalReturns += scheme.absoluteReturns;
    acc[category].avgXIRR += scheme.xirr;
    return acc;
  }, {});

  const chartData = Object.values(categoryData).map((cat: any) => ({
    ...cat,
    avgXIRR: cat.avgXIRR / cat.count,
    value: cat.value / 100000
  }));

  return (
    <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white">Category Breakdown</h3>
          <p className="text-sm font-medium text-gray-300">Mutual fund allocation by category</p>
        </div>
      </div>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 184, 153, 0.1)" />
            <XAxis type="number" stroke="#9ca3af" fontSize={12} />
            <YAxis 
              type="category" 
              dataKey="name" 
              stroke="#9ca3af" 
              fontSize={10}
              width={100}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgb(24, 25, 27)', 
                border: '1px solid rgba(0, 184, 153, 0.2)',
                borderRadius: '12px',
                fontSize: '12px',
                color: 'white'
              }}
              formatter={(value: any, name: string) => [
                name === 'value' ? `₹${value.toFixed(1)}L` : 
                name === 'avgXIRR' ? `${value.toFixed(1)}%` : value,
                name === 'value' ? 'Investment Value' : 
                name === 'avgXIRR' ? 'Average XIRR' : 'Fund Count'
              ]}
            />
            <Bar dataKey="value" fill="rgb(0, 184, 153)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
});

const formatNumber = (num: number): string => {
  if (num >= 10000000) return `${(num / 10000000).toFixed(1)}Cr`;
  if (num >= 100000) return `${(num / 100000).toFixed(1)}L`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
};

export default function Dashboard({ financialData }: Props) {
  const [userProfile, setUserProfile] = useState(null);

  const handleProfileUpdate = useCallback((profile: any) => {
    setUserProfile(profile);
    console.log('User profile updated:', profile);
  }, []);

  if (!financialData) {
    return (
      <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-xl p-6 text-center shadow-lg">
        <div className="space-y-3">
          <div className="w-8 h-8 bg-[rgba(220,53,69,0.1)] rounded-lg flex items-center justify-center mx-auto">
            <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div>
            <h3 className="text-md font-semibold text-white">No Data Available</h3>
            <p className="text-sm text-gray-400">Unable to load financial data</p>
          </div>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-[rgb(0,184,153)] hover:bg-[rgb(0,164,133)] text-white font-medium py-2 px-4 rounded-lg transition-all text-sm"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const summary = useMemo(() => financialData.summary || {}, [financialData.summary]);
  const data = useMemo(() => financialData.data || {}, [financialData.data]);
  const schemes = useMemo(() => data.mutual_fund_schemes || [], [data.mutual_fund_schemes]);
  const bankAccounts = useMemo(() => data.bank_accounts || [], [data.bank_accounts]);
  const performanceMetrics = useMemo(() => data.performance_metrics || {}, [data.performance_metrics]);

  const calculatePortfolioGrowth = () => {
    if (performanceMetrics.total_invested > 0) {
      return ((performanceMetrics.total_current - performanceMetrics.total_invested) / performanceMetrics.total_invested * 100).toFixed(1);
    }
    return '0.0';
  };

  return (
    <div className="space-y-5">
      {/* Top Metrics Row with Bank Accounts First */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        {/* Bank Accounts - Top Priority */}
        {bankAccounts.length > 0 && (
          <MetricCard
            title="Bank Accounts"
            value={`₹${formatNumber(bankAccounts.reduce((total: number, account: any) => total + account.balance, 0))}`}
            subtitle={`${bankAccounts.length} connected accounts`}
            icon="M12 2C13.1 2 14 2.9 14 4V8C14 9.1 13.1 10 12 10H4C2.9 10 2 9.1 2 8V4C2 2.9 2.9 2 4 2H12M12 12C13.1 12 14 12.9 14 14V18C14 19.1 13.1 20 12 20H4C2.9 20 2 19.1 2 18V14C2 12.9 2.9 12 4 12H12M20 2C21.1 2 22 2.9 22 4V8C22 9.1 21.1 10 20 10H16C15.4 10 15 9.6 15 9S15.4 8 16 8H20V4H16C15.4 4 15 3.6 15 3S15.4 2 16 2H20M20 12C21.1 12 22 12.9 22 14V18C22 19.1 21.1 20 20 20H16C15.4 20 15 19.6 15 19S15.4 18 16 18H20V14H16C15.4 14 15 13.6 15 13S15.4 12 16 12H20Z"
          />
        )}
        <MetricCard
          title="Net Worth"
          value={summary.total_net_worth_formatted || '₹0'}
          change={performanceMetrics.total_returns > 0 ? `+${calculatePortfolioGrowth()}%` : undefined}
          changeType={performanceMetrics.total_returns > 0 ? 'positive' : 'neutral'}
          subtitle="Total value"
          icon="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
        <MetricCard
          title="Mutual Funds"
          value={summary.mutual_funds_formatted || '₹0'}
          change={performanceMetrics.avg_xirr > 0 ? `${performanceMetrics.avg_xirr.toFixed(1)}% XIRR` : undefined}
          changeType={performanceMetrics.avg_xirr > 0 ? 'positive' : 'neutral'}
          subtitle="Investments"
          icon="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
        <MetricCard
          title="Liquid Assets"
          value={summary.liquid_funds_formatted || '₹0'}
          subtitle="Available"
          icon="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
        />
        <MetricCard
          title="EPF"
          value={summary.epf_formatted || '₹0'}
          subtitle="Provident"
          icon="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
        />
      </div>

      {/* Side by Side Investment Components */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Investment Profile */}
        <UserRiskProfile onProfileUpdate={handleProfileUpdate} />
        
        {/* AI Investment Recommendations */}
        <InvestmentRecommendationCard financialData={financialData} />
      </div>

      {/* Stock Market Overview */}
      <StocksList />

      {/* Credit Card Transactions */}
      <CreditCardTransactions financialData={financialData} />

      {schemes.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <RiskReturnScatter schemes={schemes} />
          <MutualFundBreakdown schemes={schemes} />
        </div>
      )}

      {/* Detailed Holdings Table */}
      {schemes.length > 0 && (
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl overflow-hidden shadow-xl">
          <div className="px-6 py-4 border-b border-[rgba(0,184,153,0.2)]">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">Mutual Fund Holdings</h3>
                <p className="text-sm font-medium text-gray-300">Detailed breakdown of {schemes.length} schemes</p>
              </div>
              <div className="text-right text-sm font-medium text-gray-300">
                <p>Total: {summary.mutual_funds_formatted}</p>
                <p>Avg XIRR: {performanceMetrics.avg_xirr ? performanceMetrics.avg_xirr.toFixed(1) : '0'}%</p>
              </div>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[rgba(0,184,153,0.05)]">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">Fund Name</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">Current Value</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">Invested</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">Returns</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">XIRR</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">Units</th>
                </tr>
              </thead>
              <tbody className="bg-[rgb(24,25,27)] divide-y divide-[rgba(0,184,153,0.1)]">
                {schemes.map((scheme: any, index: number) => (
                  <tr key={scheme.isin || index} className="hover:bg-[rgba(0,184,153,0.05)] border-b border-[rgba(0,184,153,0.1)]">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-semibold text-white max-w-xs truncate">
                          {scheme.name}
                        </div>
                        <div className="text-sm font-medium text-gray-300">{scheme.amc}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[rgba(0,184,153,0.1)] text-[rgb(0,184,153)] border border-[rgba(0,184,153,0.2)]">
                        {scheme.category?.replace(/_/g, ' ') || 'Other'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-white font-semibold">
                      ₹{formatNumber(scheme.currentValue)}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-white">
                      ₹{formatNumber(scheme.investedValue)}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className={scheme.absoluteReturns >= 0 ? 'text-[rgb(0,184,153)]' : 'text-red-400'}>
                        {scheme.absoluteReturns >= 0 ? '+' : ''}₹{formatNumber(Math.abs(scheme.absoluteReturns))}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className={scheme.xirr >= 0 ? 'text-[rgb(0,184,153)]' : 'text-red-400'}>
                        {scheme.xirr >= 0 ? '+' : ''}{scheme.xirr.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-white">
                      {scheme.units.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
}