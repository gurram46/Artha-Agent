'use client';

import { useState, useEffect } from 'react';
import MCPDataService from '@/services/mcpDataService';
import StatCard from '@/components/ui/StatCard';
import UnifiedButton from '@/components/ui/UnifiedButton';
import { designSystem } from '@/styles/designSystem';

interface FinancialStats {
  totalNetWorth: number;
  totalNetWorthFormatted: string;
  mutualFunds: number;
  mutualFundsFormatted: string;
  liquidFunds: number;
  liquidFundsFormatted: string;
  epf: number;
  epfFormatted: string;
  creditScore: string;
  totalAssets: number;
  totalLiabilities: number;
  growthRate: number;
  riskScore: string;
  portfolioHealth: string;
}


const EnhancedFinancialStats = () => {
  const [stats, setStats] = useState<FinancialStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  useEffect(() => {
    loadFinancialStats();
  }, []);

  const loadFinancialStats = async () => {
    try {
      setIsLoading(true);
      const mcpService = MCPDataService.getInstance();
      const result = await mcpService.loadMCPData();

      if (result.success && result.data) {
        const transformedData = mcpService.transformToPortfolioFormat(result.data);
        
        // Get additional insights
        const [portfolioInsights, riskAssessment] = await Promise.all([
          mcpService.getPortfolioInsights(),
          mcpService.getRiskAssessment()
        ]);

        // Calculate growth rate (example: based on performance metrics)
        const growthRate = transformedData.data.performance_metrics.total_gains_percentage || 0;
        const riskScore = riskAssessment.success ? riskAssessment.assessment?.risk_level || 'Medium' : 'N/A';
        const portfolioHealth = portfolioInsights.success ? portfolioInsights.insights?.health_score || 'Good' : 'N/A';

        setStats({
          totalNetWorth: transformedData.summary.total_net_worth,
          totalNetWorthFormatted: transformedData.summary.total_net_worth_formatted,
          mutualFunds: transformedData.summary.mutual_funds,
          mutualFundsFormatted: transformedData.summary.mutual_funds_formatted,
          liquidFunds: transformedData.summary.liquid_funds,
          liquidFundsFormatted: transformedData.summary.liquid_funds_formatted,
          epf: transformedData.summary.epf,
          epfFormatted: transformedData.summary.epf_formatted,
          creditScore: transformedData.summary.credit_score,
          totalAssets: transformedData.summary.total_assets,
          totalLiabilities: transformedData.summary.total_liabilities,
          growthRate,
          riskScore,
          portfolioHealth
        });

        setLastUpdated(new Date().toLocaleTimeString());
      }
    } catch (error) {
      console.error('Failed to load financial stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getTrendDirection = (value: number): 'up' | 'down' | 'neutral' => {
    if (value > 5) return 'up';
    if (value < -2) return 'down';
    return 'neutral';
  };

  const formatGrowthRate = (rate: number): string => {
    return `${rate > 0 ? '+' : ''}${rate.toFixed(1)}%`;
  };

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
        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
        <span>Live data from backend API</span>
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
      </div>
    </div>
  );
};

export default EnhancedFinancialStats;