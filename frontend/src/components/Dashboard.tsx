'use client';

import { useState, useEffect } from 'react';
import LiveInsightsCard from './LiveInsightsCard';

interface Props {
  financialData: any;
}

export default function Dashboard({ financialData }: Props) {

  if (!financialData?.data) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500">No financial data available</div>
      </div>
    );
  }

  // Use portfolio summary from the new API structure
  const summary = financialData.summary || {};
  const totalNetWorth = summary.total_net_worth || 0;
  const liquidFunds = summary.liquid_funds || 0;
  const totalDebt = summary.total_debt || 0;
  const netWorthData = financialData.data?.net_worth?.netWorthResponse;

  return (
    <div className="space-y-6">
      {/* Header with Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Net Worth"
          value={summary.total_net_worth_formatted || `₹${formatNumber(totalNetWorth)}`}
          subtitle="Total Portfolio Value"
          icon="💰"
          gradient="from-blue-600 to-blue-700"
        />
        <MetricCard
          title="Liquid Assets"
          value={summary.liquid_funds_formatted || `₹${formatNumber(liquidFunds)}`}
          subtitle="Available for Investment"
          icon="💧"
          gradient="from-green-600 to-green-700"
        />
        <MetricCard
          title="Total Debt"
          value={summary.total_debt_formatted || `₹${formatNumber(totalDebt)}`}
          subtitle="Outstanding Liabilities"
          icon="📊"
          gradient="from-red-600 to-red-700"
        />
      </div>

      {/* Main AI Chat Interface */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-100 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">💬 AI Financial Assistant</h2>
            <p className="text-gray-600">Ask anything about your portfolio, investments, or financial planning</p>
          </div>
          <div className="text-right text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>AI Ready</span>
            </div>
          </div>
        </div>
        <LiveInsightsCard />
      </div>

      {/* Portfolio Analytics Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Portfolio Performance */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">📈 Performance</h3>
            <span className="text-green-600 text-sm font-medium bg-green-50 px-2 py-1 rounded-full">+5.2%</span>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Today's Gain</span>
              <span className="text-green-600 font-medium">+₹{formatNumber(Math.abs(totalNetWorth * 0.002))}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Monthly Return</span>
              <span className="text-green-600 font-medium">+{((Math.random() * 5) + 2).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-green-600 h-2 rounded-full" style={{width: '68%'}}></div>
            </div>
            <p className="text-xs text-gray-500">68% of target achieved</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full text-left p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors">
              <div className="text-blue-700 font-medium">💰 Add Investment</div>
              <div className="text-blue-600 text-sm">Invest in MF or Stocks</div>
            </button>
            <button className="w-full text-left p-3 bg-green-50 hover:bg-green-100 rounded-lg transition-colors">
              <div className="text-green-700 font-medium">📊 Rebalance Portfolio</div>
              <div className="text-green-600 text-sm">Optimize allocation</div>
            </button>
            <button className="w-full text-left p-3 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors">
              <div className="text-purple-700 font-medium">🎯 Set Goals</div>
              <div className="text-purple-600 text-sm">Plan financial targets</div>
            </button>
          </div>
        </div>

        {/* AI Insights Summary */}
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-100 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🔮 AI Insights</h3>
          <div className="space-y-3">
            <div className="bg-white bg-opacity-70 rounded-lg p-3">
              <div className="text-purple-700 font-medium text-sm">💡 Top Recommendation</div>
              <div className="text-purple-600 text-xs mt-1">Reallocate UTI Overnight Fund for ₹29K+ potential recovery</div>
            </div>
            <div className="bg-white bg-opacity-70 rounded-lg p-3">
              <div className="text-purple-700 font-medium text-sm">⚠️ Risk Alert</div>
              <div className="text-purple-600 text-xs mt-1">Clear loan defaults to save ₹11K annually</div>
            </div>
            <button className="w-full mt-3 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors">
              View Full Analysis →
            </button>
          </div>
        </div>
      </div>

      {/* Portfolio Breakdown - Real Mutual Funds */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">📈 Mutual Fund Portfolio</h2>
          <p className="text-sm text-gray-600 mt-1">Your mutual fund investments from Fi Money</p>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {summary.mutual_funds && summary.mutual_funds.length > 0 ? (
              summary.mutual_funds.map((fund: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{fund.name}</h3>
                    <div className="flex items-center space-x-4 mt-1">
                      <p className="text-sm text-gray-600">{fund.amc}</p>
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                        {fund.asset_class}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        fund.risk_level.includes('HIGH') ? 'bg-red-100 text-red-800' : 
                        fund.risk_level.includes('MODERATE') ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {fund.risk_level.replace(/_/g, ' ')}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900 text-lg">₹{formatNumber(fund.current_value)}</p>
                    <p className={`text-sm font-medium ${
                      fund.xirr > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {fund.xirr > 0 ? '+' : ''}{fund.xirr.toFixed(1)}% XIRR
                    </p>
                    <p className="text-xs text-gray-500">
                      Invested: ₹{formatNumber(fund.invested_value)}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No mutual fund data available</p>
                <p className="text-sm">Connect your mutual fund accounts in Fi Money app</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bank Accounts */}
      {summary.bank_accounts && summary.bank_accounts.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">🏦 Bank Accounts</h2>
            <p className="text-sm text-gray-600 mt-1">Your connected bank accounts</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {summary.bank_accounts.map((account: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border">
                  <div>
                    <h3 className="font-medium text-gray-900">{account.bank}</h3>
                    <p className="text-sm text-gray-600">{account.masked_number}</p>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full mt-1 inline-block">
                      {account.account_type.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900 text-lg">₹{formatNumber(account.balance)}</p>
                    <p className="text-sm text-gray-500">Available Balance</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string;
  subtitle: string;
  icon: string;
  gradient: string;
}

function MetricCard({ title, value, subtitle, icon, gradient }: MetricCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 relative overflow-hidden">
      <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${gradient} opacity-10 rounded-full -mr-8 -mt-8`}></div>
      <div className="flex items-center relative z-10">
        <div className="text-3xl mr-4">{icon}</div>
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
          <p className="text-sm text-gray-500">{subtitle}</p>
        </div>
      </div>
    </div>
  );
}

function formatNumber(num: string | number): string {
  const value = typeof num === 'string' ? parseFloat(num) : num;
  if (value >= 10000000) return (value / 10000000).toFixed(1) + 'Cr';
  if (value >= 100000) return (value / 100000).toFixed(1) + 'L';
  if (value >= 1000) return (value / 1000).toFixed(1) + 'K';
  return value.toFixed(0);
}