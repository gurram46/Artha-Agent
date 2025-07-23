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
  <div className="group bg-white/95 backdrop-blur-sm rounded-3xl border border-slate-200/60 p-6 shadow-lg hover:shadow-xl transition-all duration-500 hover:scale-[1.02] hover:border-blue-300/50 relative overflow-hidden">
    <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
    <div className="relative z-10 flex items-start justify-between">
      <div className="flex-1">
        <div className="flex items-center space-x-4 mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-slate-100 rounded-2xl flex items-center justify-center shadow-md group-hover:shadow-lg transition-shadow duration-300">
            <svg className="w-6 h-6 text-blue-600 group-hover:scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon} />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-700 tracking-wide">{title}</p>
            <p className="text-xs text-slate-500 font-medium">{subtitle}</p>
          </div>
        </div>
        <div className="space-y-3">
          <h3 className="text-3xl font-bold text-slate-900 group-hover:text-blue-900 transition-colors duration-300">{value}</h3>
          {change && changeType && (
            <div className="flex items-center space-x-2">
              <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold shadow-sm ${
                changeType === 'positive' 
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' 
                  : changeType === 'negative'
                  ? 'bg-red-100 text-red-800 border border-red-200'
                  : 'bg-slate-100 text-slate-800 border border-slate-200'
              }`}>
                {changeType === 'positive' && (
                  <svg className="w-3.5 h-3.5 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                {changeType === 'negative' && (
                  <svg className="w-3.5 h-3.5 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                {change}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  </div>
);

const AssetAllocationChart = memo(({ data }: { data: any[] }) => {
  const COLORS = ['#334155', '#475569', '#64748b', '#94a3b8', '#cbd5e1'];
  
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-lg">
          <p className="font-medium text-slate-900">{item.name}</p>
          <p className="text-sm text-slate-600">Value: ₹{(item.value / 100000).toFixed(1)}L</p>
          <p className="text-sm text-slate-600">Allocation: {item.percentage.toFixed(1)}%</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white/95 backdrop-blur-sm rounded-3xl border border-slate-200/60 p-8 shadow-lg hover:shadow-xl transition-all duration-500">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h3 className="text-xl font-bold text-slate-900 mb-1">Asset Allocation</h3>
          <p className="text-sm text-slate-600 font-medium">Portfolio distribution by asset class</p>
        </div>
        <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-slate-100 rounded-xl flex items-center justify-center">
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
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
        
        <div className="space-y-5">
          {data.map((item, index) => (
            <div key={`allocation-item-${item.name || index}`} className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50/80 transition-colors duration-200">
              <div className="flex items-center space-x-4">
                <div 
                  className="w-4 h-4 rounded-full shadow-sm" 
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <span className="text-sm font-semibold text-slate-700">{item.name}</span>
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-slate-900">{item.percentage.toFixed(1)}%</p>
                <p className="text-xs text-slate-600 font-medium">₹{(item.value / 100000).toFixed(1)}L</p>
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
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Fund Performance</h3>
          <p className="text-sm text-slate-600">XIRR vs Investment Amount</p>
        </div>
      </div>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis 
              dataKey="name" 
              stroke="#64748b" 
              fontSize={12}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis stroke="#64748b" fontSize={12} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '12px'
              }}
              formatter={(value: any, name: string) => [
                name === 'returns' ? `${value.toFixed(1)}%` : `₹${value.toFixed(1)}L`,
                name === 'returns' ? 'XIRR' : name === 'invested' ? 'Invested' : 'Current Value'
              ]}
            />
            <Bar dataKey="invested" fill="#94a3b8" name="invested" />
            <Bar dataKey="current" fill="#475569" name="current" />
            <Line type="monotone" dataKey="returns" stroke="#334155" strokeWidth={3} name="returns" />
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
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Risk vs Return Analysis</h3>
          <p className="text-sm text-slate-600">Portfolio risk-return mapping</p>
        </div>
      </div>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis 
              type="number" 
              dataKey="x" 
              name="Returns" 
              unit="%" 
              stroke="#64748b"
              fontSize={12}
            />
            <YAxis 
              type="number" 
              dataKey="y" 
              name="Risk" 
              stroke="#64748b"
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
                backgroundColor: 'white', 
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '12px'
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
            <Scatter data={scatterData} fill="#334155" />
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
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Category Breakdown</h3>
          <p className="text-sm text-slate-600">Mutual fund allocation by category</p>
        </div>
      </div>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis type="number" stroke="#64748b" fontSize={12} />
            <YAxis 
              type="category" 
              dataKey="name" 
              stroke="#64748b" 
              fontSize={10}
              width={100}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '12px'
              }}
              formatter={(value: any, name: string) => [
                name === 'value' ? `₹${value.toFixed(1)}L` : 
                name === 'avgXIRR' ? `${value.toFixed(1)}%` : value,
                name === 'value' ? 'Investment Value' : 
                name === 'avgXIRR' ? 'Average XIRR' : 'Fund Count'
              ]}
            />
            <Bar dataKey="value" fill="#475569" />
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
      <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm">
        <div className="space-y-4">
          <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-slate-900">Failed to Load Financial Data</h3>
          <p className="text-red-600">Unable to load real MCP data from mcp-docs directory</p>
          <div className="text-xs text-slate-500 space-y-1">
            <p>Expected data sources:</p>
            <p>• /mcp-docs/sample_responses/fetch_net_worth.json</p>
            <p>• /mcp-docs/sample_responses/fetch_credit_report.json</p>
            <p>• /mcp-docs/sample_responses/fetch_epf_details.json</p>
          </div>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry Loading
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
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">Mutual Fund Holdings</h3>
                <p className="text-sm text-slate-600">Detailed breakdown of {schemes.length} schemes</p>
              </div>
              <div className="text-right text-sm text-slate-600">
                <p>Total: {summary.mutual_funds_formatted}</p>
                <p>Avg XIRR: {performanceMetrics.avg_xirr ? performanceMetrics.avg_xirr.toFixed(1) : '0'}%</p>
              </div>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Fund Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Current Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Invested</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Returns</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">XIRR</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Units</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {schemes.map((scheme, index) => (
                  <tr key={scheme.isin || index} className="hover:bg-slate-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-slate-900 max-w-xs truncate">
                          {scheme.name}
                        </div>
                        <div className="text-sm text-slate-500">{scheme.amc}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                        {scheme.category?.replace(/_/g, ' ') || 'Other'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-900 font-medium">
                      ₹{formatNumber(scheme.currentValue)}
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-900">
                      ₹{formatNumber(scheme.investedValue)}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className={scheme.absoluteReturns >= 0 ? 'text-emerald-600' : 'text-red-600'}>
                        {scheme.absoluteReturns >= 0 ? '+' : ''}₹{formatNumber(Math.abs(scheme.absoluteReturns))}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className={scheme.xirr >= 0 ? 'text-emerald-600' : 'text-red-600'}>
                        {scheme.xirr >= 0 ? '+' : ''}{scheme.xirr.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-900">
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
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">Bank Accounts</h3>
                <p className="text-sm text-slate-600">{bankAccounts.length} connected accounts</p>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {bankAccounts.map((account, index) => (
                <div key={index} className="p-4 border border-slate-200 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-slate-900">{account.bank}</h4>
                    <span className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded">
                      {account.accountType?.replace(/_/g, ' ') || 'Account'}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 mb-2">{account.accountNumber}</p>
                  <p className="text-lg font-semibold text-slate-900">₹{formatNumber(account.balance)}</p>
                  {account.balanceDate && (
                    <p className="text-xs text-slate-500 mt-1">
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