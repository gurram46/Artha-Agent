'use client';

import { useState, useEffect } from 'react';
import AIInsightCard from './AIInsightCard';
import MoneyTruthCard from './MoneyTruthCard';
import LiveInsightsCard from './LiveInsightsCard';

interface Props {
  financialData: any;
}

export default function Dashboard({ financialData }: Props) {
  const [portfolioHealth, setPortfolioHealth] = useState<any>(null);
  const [moneyLeaks, setMoneyLeaks] = useState<any>(null);
  const [riskAssessment, setRiskAssessment] = useState<any>(null);
  const [isLoadingHealth, setIsLoadingHealth] = useState(false);
  const [isLoadingLeaks, setIsLoadingLeaks] = useState(false);
  const [isLoadingRisk, setIsLoadingRisk] = useState(false);

  // Individual streaming fetch functions for each card
  const [hiddenTruths, setHiddenTruths] = useState<any>(null);
  const [futureProjection, setFutureProjection] = useState<any>(null);
  const [goalReality, setGoalReality] = useState<any>(null);
  const [moneyPersonality, setMoneyPersonality] = useState<any>(null);
  const [isLoadingHidden, setIsLoadingHidden] = useState(false);
  const [isLoadingFuture, setIsLoadingFuture] = useState(false);
  const [isLoadingGoals, setIsLoadingGoals] = useState(false);
  const [isLoadingPersonality, setIsLoadingPersonality] = useState(false);

  const fetchHiddenTruths = async () => {
    if (!financialData) return;
    setIsLoadingHidden(true);
    try {
      const response = await fetch('http://localhost:8003/api/hidden-truths', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      setHiddenTruths(data.insights);
    } catch (error) {
      console.error('Failed to fetch hidden truths:', error);
    } finally {
      setIsLoadingHidden(false);
    }
  };

  const fetchFutureProjection = async () => {
    if (!financialData) return;
    setIsLoadingFuture(true);
    try {
      const response = await fetch('http://localhost:8003/api/future-projection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      setFutureProjection(data.insights);
    } catch (error) {
      console.error('Failed to fetch future projection:', error);
    } finally {
      setIsLoadingFuture(false);
    }
  };

  const fetchGoalReality = async () => {
    if (!financialData) return;
    setIsLoadingGoals(true);
    try {
      const response = await fetch('http://localhost:8003/api/goal-reality', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      setGoalReality(data.insights);
    } catch (error) {
      console.error('Failed to fetch goal reality:', error);
    } finally {
      setIsLoadingGoals(false);
    }
  };

  const fetchMoneyPersonality = async () => {
    if (!financialData) return;
    setIsLoadingPersonality(true);
    try {
      const response = await fetch('http://localhost:8003/api/money-personality', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      setMoneyPersonality(data.insights);
    } catch (error) {
      console.error('Failed to fetch money personality:', error);
    } finally {
      setIsLoadingPersonality(false);
    }
  };

  // Fetch Portfolio Health
  const fetchPortfolioHealth = async () => {
    if (!financialData) return;
    
    setIsLoadingHealth(true);
    try {
      const response = await fetch('http://localhost:8003/api/portfolio-health', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const data = await response.json();
      setPortfolioHealth(data.portfolio_health);
    } catch (error) {
      console.error('Failed to fetch portfolio health:', error);
    } finally {
      setIsLoadingHealth(false);
    }
  };

  // Fetch Money Leaks
  const fetchMoneyLeaks = async () => {
    if (!financialData) return;
    
    setIsLoadingLeaks(true);
    try {
      const response = await fetch('http://localhost:8003/api/money-leaks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const data = await response.json();
      setMoneyLeaks(data.money_leaks);
    } catch (error) {
      console.error('Failed to fetch money leaks:', error);
    } finally {
      setIsLoadingLeaks(false);
    }
  };

  // Fetch Risk Assessment
  const fetchRiskAssessment = async () => {
    if (!financialData) return;
    
    setIsLoadingRisk(true);
    try {
      const response = await fetch('http://localhost:8003/api/risk-assessment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const data = await response.json();
      setRiskAssessment(data.risk_assessment);
    } catch (error) {
      console.error('Failed to fetch risk assessment:', error);
    } finally {
      setIsLoadingRisk(false);
    }
  };

  useEffect(() => {
    if (financialData) {
      // Start all analyses in parallel - each updates independently 
      fetchHiddenTruths();
      fetchPortfolioHealth();
      fetchMoneyLeaks();
      fetchRiskAssessment();
      // Stagger these to avoid overwhelming the API
      setTimeout(() => fetchFutureProjection(), 100);
      setTimeout(() => fetchGoalReality(), 200);
      setTimeout(() => fetchMoneyPersonality(), 300);
    }
  }, [financialData]);

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

      {/* Money Truth Engine - Hidden Insights */}
      <MoneyTruthCard
        title="💡 Hidden Money Truths"
        subtitle="Shocking discoveries about your finances"
        insights={hiddenTruths}
        isLoading={isLoadingHidden}
        onRefresh={fetchHiddenTruths}
        type="hidden_truths"
      />

      {/* Two Column Layout for AI Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Portfolio Health */}
        <AIInsightCard
          title="🏥 Portfolio Health Check"
          subtitle="AI diagnosis of your investments"
          insights={portfolioHealth}
          isLoading={isLoadingHealth}
          onRefresh={fetchPortfolioHealth}
          type="portfolio_health"
        />

        {/* Money Leaks Detection */}
        <AIInsightCard
          title="🔍 Money Leak Detection"
          subtitle="Where you're losing money secretly"
          insights={moneyLeaks}
          isLoading={isLoadingLeaks}
          onRefresh={fetchMoneyLeaks}
          type="money_leaks"
        />
      </div>

      {/* Risk Assessment */}
      <AIInsightCard
        title="⚠️ Risk Assessment"
        subtitle="AI-powered risk analysis and protection gaps"
        insights={riskAssessment}
        isLoading={isLoadingRisk}
        onRefresh={fetchRiskAssessment}
        type="risk_assessment"
      />

      {/* Live AI Insights */}
      <LiveInsightsCard />

      {/* Future Wealth Projection */}
      <MoneyTruthCard
        title="🔮 Future Wealth Projection"
        subtitle="AI predicts your financial future"
        insights={futureProjection}
        isLoading={isLoadingFuture}
        onRefresh={fetchFutureProjection}
        type="future_projection"
      />

      {/* Goal Reality Check */}
      <MoneyTruthCard
        title="🎯 Life Goal Reality Check"
        subtitle="Can you achieve your dreams?"
        insights={goalReality}
        isLoading={isLoadingGoals}
        onRefresh={fetchGoalReality}
        type="goal_reality"
      />

      {/* Money Personality Analysis */}
      <MoneyTruthCard
        title="🧠 Money Personality Analysis"
        subtitle="What your behavior reveals about your wealth"
        insights={moneyPersonality}
        isLoading={isLoadingPersonality}
        onRefresh={fetchMoneyPersonality}
        type="personality"
      />

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