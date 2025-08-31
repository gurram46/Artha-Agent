'use client';

import React, { useState, useEffect } from 'react';
import { designSystem } from '@/styles/designSystem';
import UnifiedButton from '@/components/ui/UnifiedButton';
import StatCard from '@/components/ui/StatCard';
import { formatCurrency, formatDate } from '@/utils/formatters';

interface FinancialStats {
  totalNetWorth: number;
  totalNetWorthFormatted: string;
  totalAssets: number;
  totalLiabilities: number;
  growthRate: number;
  mutualFunds: number;
  mutualFundsFormatted: string;
  liquidFunds: number;
  liquidFundsFormatted: string;
  creditScore: string;
  epf: number;
  epfFormatted: string;
  portfolioHealth: string;
  riskScore: string;
}

const EnhancedFinancialStats = ({ financialData }: { financialData: any }) => {
  const [stats, setStats] = useState<FinancialStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  // Transform financial data to stats format
  const transformFinancialData = (data: any): FinancialStats => {
    if (!data?.summary) {
      return {
        totalNetWorth: 0,
        totalNetWorthFormatted: '₹0',
        totalAssets: 0,
        totalLiabilities: 0,
        growthRate: 0,
        mutualFunds: 0,
        mutualFundsFormatted: '₹0',
        liquidFunds: 0,
        liquidFundsFormatted: '₹0',
        creditScore: 'N/A',
        epf: 0,
        epfFormatted: '₹0',
        portfolioHealth: 'Loading',
        riskScore: 'Medium'
      };
    }

    return {
      totalNetWorth: data.summary.total_net_worth || 0,
      totalNetWorthFormatted: data.summary.total_net_worth_formatted || '₹0',
      totalAssets: data.summary.total_assets || 0,
      totalLiabilities: data.summary.total_liabilities || 0,
      growthRate: data.summary.growth_rate || 0,
      mutualFunds: data.summary.mutual_funds || 0,
      mutualFundsFormatted: data.summary.mutual_funds_formatted || '₹0',
      liquidFunds: data.summary.liquid_funds || 0,
      liquidFundsFormatted: data.summary.liquid_funds_formatted || '₹0',
      creditScore: data.summary.credit_score || 'N/A',
      epf: data.summary.epf || 0,
      epfFormatted: data.summary.epf_formatted || '₹0',
      portfolioHealth: data.summary.portfolio_health || 'Loading',
      riskScore: data.summary.risk_score || 'Medium'
    };
  };

  // Format growth rate with sign
  const formatGrowthRate = (rate: number): string => {
    if (rate > 0) return `+${rate.toFixed(2)}%`;
    if (rate < 0) return `${rate.toFixed(2)}%`;
    return '0.00%';
  };

  // Determine trend direction
  const getTrendDirection = (rate: number): 'up' | 'down' | 'neutral' => {
    if (rate > 0) return 'up';
    if (rate < 0) return 'down';
    return 'neutral';
  };

  // Load financial stats
  const loadFinancialStats = async () => {
    setIsLoading(true);
    
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 800));
      
      if (financialData) {
        const transformedStats = transformFinancialData(financialData);
        setStats(transformedStats);
        setLastUpdated(formatDate(new Date()));
      }
    } catch (error) {
      console.error('Failed to load financial stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Initialize stats on mount and when financialData changes
  useEffect(() => {
    loadFinancialStats();
  }, [financialData]);

  return (
    <div className="space-y-6">
      {/* Header with refresh */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={designSystem.typography.heading.large}>Financial Overview</h2>
          <p className={designSystem.typography.body.small}>
            Last updated: {lastUpdated || 'Loading...'}
          </p>
        </div>
        <UnifiedButton
          onClick={loadFinancialStats}
          disabled={isLoading}
          isLoading={isLoading}
          variant="primary"
          size="sm"
          className="flex items-center space-x-2"
        >
          <svg 
            className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>{isLoading ? 'Updating...' : 'Refresh'}</span>
        </UnifiedButton>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Net Worth"
          value={stats?.totalNetWorthFormatted || '₹0'}
          subtitle="Total portfolio value"
          icon={
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
            </svg>
          }
          trend={{
            value: stats ? formatGrowthRate(stats.growthRate) : '0%',
            type: stats ? (getTrendDirection(stats.growthRate) === 'up' ? 'positive' : getTrendDirection(stats.growthRate) === 'down' ? 'negative' : 'neutral') : 'neutral'
          }}
        />

        <StatCard
          title="Mutual Funds"
          value={stats?.mutualFundsFormatted || '₹0'}
          subtitle="Investment corpus"
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          }
          trend={{
            value: "+12.5%",
            type: "positive"
          }}
        />

        <StatCard
          title="Liquid Funds"
          value={stats?.liquidFundsFormatted || '₹0'}
          subtitle="Available cash & deposits"
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          }
          trend={{
            value: "Stable",
            type: "neutral"
          }}
        />

        <StatCard
          title="Credit Score"
          value={stats?.creditScore || 'N/A'}
          subtitle="Credit health"
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          trend={{
            value: stats?.creditScore ? 'Excellent' : 'Loading',
            type: stats?.creditScore && parseInt(stats.creditScore) > 750 ? 'positive' : 'neutral'
          }}
        />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="EPF Balance"
          value={stats?.epfFormatted || '₹0'}
          subtitle="Retirement savings"
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          }
        />

        <StatCard
          title="Portfolio Health"
          value={stats?.portfolioHealth || 'Good'}
          subtitle="AI assessment"
          icon={
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
            </svg>
          }
        />

        <StatCard
          title="Risk Level"
          value={stats?.riskScore || 'Medium'}
          subtitle="Investment risk"
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          }
        />
      </div>

      {/* Live Data Indicator */}
      <div className={`flex items-center justify-center space-x-2 ${designSystem.typography.body.small}`}>
        <div className="bg-[rgb(24,25,27)] border border-[rgba(204,166,149,0.2)] rounded-lg p-6">
          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
          <span>Live data from backend API</span>
        </div>
      </div>
    </div>
  );
};

export default EnhancedFinancialStats;