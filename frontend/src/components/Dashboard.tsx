'use client';

import { useState, useEffect, useMemo, memo, useCallback } from 'react';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, AreaChart, Area, RadialBarChart, RadialBar, ComposedChart, Scatter, ScatterChart } from 'recharts';
import StocksList from './StocksList';
import UserRiskProfile from './UserRiskProfile';

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

const AssetAllocationChart = memo(({ data }: { data: any[] }) => {
  const COLORS = ['rgb(0, 184, 153)', 'rgb(0, 164, 133)', 'rgb(59, 130, 246)', 'rgb(139, 92, 246)', 'rgb(245, 158, 11)'];
  
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-xl p-3 shadow-xl">
          <p className="font-semibold text-white">{item.name}</p>
          <p className="text-sm font-medium text-gray-300">₹{(item.value / 100000).toFixed(1)}L ({item.percentage.toFixed(1)}%)</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white mb-1">Asset Allocation</h3>
        <p className="text-sm font-medium text-gray-300">Portfolio distribution by asset class</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`allocation-cell-${entry.name || index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        <div className="space-y-3">
          {data.map((item, index) => (
            <div key={`allocation-item-${item.name || index}`} className="flex items-center justify-between p-3 hover:bg-[rgba(0,184,153,0.05)] rounded-lg transition-colors">
              <div className="flex items-center space-x-3">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <span className="font-semibold text-white">{item.name}</span>
              </div>
              <div className="text-right">
                <p className="font-semibold text-white">{item.percentage.toFixed(1)}%</p>
                <p className="text-sm font-medium text-gray-300">₹{(item.value / 100000).toFixed(1)}L</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});

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
      <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-8 text-center shadow-xl">
        <div className="space-y-4">
          <div className="w-12 h-12 bg-[rgba(220,53,69,0.1)] border border-[rgba(220,53,69,0.3)] rounded-lg flex items-center justify-center mx-auto">
            <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">No Data Available</h3>
            <p className="font-medium text-gray-300 mt-1">Unable to load financial data</p>
          </div>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-[rgb(0,184,153)] hover:bg-[rgb(0,164,133)] text-white font-bold py-3 px-6 rounded-xl transition-all duration-300 shadow-lg"
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
  const assetAllocation = useMemo(() => data.asset_allocation || [], [data.asset_allocation]);
  const performanceMetrics = useMemo(() => data.performance_metrics || {}, [data.performance_metrics]);

  const calculatePortfolioGrowth = () => {
    if (performanceMetrics.total_invested > 0) {
      return ((performanceMetrics.total_current - performanceMetrics.total_invested) / performanceMetrics.total_invested * 100).toFixed(1);
    }
    return '0.0';
  };

  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          title="Net Worth"
          value={summary.total_net_worth_formatted || '₹0'}
          change={performanceMetrics.total_returns > 0 ? `+${calculatePortfolioGrowth()}%` : undefined}
          changeType={performanceMetrics.total_returns > 0 ? 'positive' : 'neutral'}
          subtitle="Total portfolio value"
          icon="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
        <MetricCard
          title="Mutual Funds"
          value={summary.mutual_funds_formatted || '₹0'}
          change={performanceMetrics.avg_xirr > 0 ? `${performanceMetrics.avg_xirr.toFixed(1)}% XIRR` : undefined}
          changeType={performanceMetrics.avg_xirr > 0 ? 'positive' : 'neutral'}
          subtitle="Investment portfolio"
          icon="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
        <MetricCard
          title="Liquid Assets"
          value={summary.liquid_funds_formatted || '₹0'}
          subtitle="Available funds"
          icon="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
        />
        <MetricCard
          title="EPF"
          value={summary.epf_formatted || '₹0'}
          subtitle="Provident fund"
          icon="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
        />
      </div>

      {/* User Investment Profile */}
      <UserRiskProfile onProfileUpdate={handleProfileUpdate} />

      {/* Stock Market Overview */}
      <StocksList />

      {/* Charts Grid */}
      {assetAllocation.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <AssetAllocationChart data={assetAllocation} />
          {schemes.length > 0 && <PerformanceChart schemes={schemes} />}
        </div>
      )}

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
                {schemes.map((scheme, index) => (
                  <tr key={scheme.isin || index} className="hover:bg-[rgba(0,184,153,0.05)]">
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

      {/* Bank Accounts */}
      {bankAccounts.length > 0 && (
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl overflow-hidden shadow-xl">
          <div className="px-6 py-4 border-b border-[rgba(0,184,153,0.2)]">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">Bank Accounts</h3>
                <p className="text-sm font-medium text-gray-300">{bankAccounts.length} connected accounts</p>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {bankAccounts.map((account, index) => (
                <div key={index} className="p-4 border border-[rgba(0,184,153,0.2)] rounded-xl bg-[rgba(0,184,153,0.05)] hover:bg-[rgba(0,184,153,0.1)] transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-white">{account.bank}</h4>
                    <span className="text-xs bg-[rgba(0,184,153,0.1)] font-medium text-[rgb(0,184,153)] px-2 py-1 rounded border border-[rgba(0,184,153,0.2)]">
                      {account.accountType?.replace(/_/g, ' ') || 'Account'}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-gray-300 mb-2">{account.accountNumber}</p>
                  <p className="text-lg font-semibold text-white">₹{formatNumber(account.balance)}</p>
                  {account.balanceDate && (
                    <p className="text-xs font-medium text-gray-400 mt-1">
                      Updated: {new Date(account.balanceDate).toLocaleDateString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}