'use client';

import { useState, useEffect } from 'react';
import MoneyTruthCard from './MoneyTruthCard';
import AIInsightCard from './AIInsightCard';
import { useFinancialInsights } from '../contexts/FinancialInsightsContext';

interface Props {
  financialData: any;
}

export default function MoneyTruthEngine({ financialData }: Props) {
  // Use global financial insights context
  const {
    hiddenTruths,
    futureProjection,
    goalReality,
    moneyPersonality,
    portfolioHealth,
    moneyLeaks,
    riskAssessment,
    isLoadingHidden,
    isLoadingFuture,
    isLoadingGoals,
    isLoadingPersonality,
    isLoadingHealth,
    isLoadingLeaks,
    isLoadingRisk,
    fetchHiddenTruths,
    fetchFutureProjection,
    fetchGoalReality,
    fetchMoneyPersonality,
    fetchPortfolioHealth,
    fetchMoneyLeaks,
    fetchRiskAssessment,
    clearAllData
  } = useFinancialInsights();

  // Run all analyses when component loads
  const runCompleteAnalysis = async () => {
    if (!financialData) return;
    
    // Run all analyses in parallel using the global context
    await Promise.all([
      fetchHiddenTruths(),
      fetchFutureProjection(),
      fetchGoalReality(),
      fetchMoneyPersonality(),
      fetchPortfolioHealth(),
      fetchMoneyLeaks(),
      fetchRiskAssessment()
    ]);
  };

  useEffect(() => {
    if (financialData) {
      // Only run analysis if we don't have fresh data
      const hasCompleteData = hiddenTruths && futureProjection && goalReality && moneyPersonality && portfolioHealth && moneyLeaks && riskAssessment;
      if (!hasCompleteData) {
        runCompleteAnalysis();
      }
    }
  }, [financialData]);

  // Check if any analysis is currently loading
  const isLoading = isLoadingHidden || isLoadingFuture || isLoadingGoals || isLoadingPersonality || isLoadingHealth || isLoadingLeaks || isLoadingRisk;
  
  // Check if we have complete results
  const hasCompleteResults = hiddenTruths && futureProjection && goalReality && moneyPersonality && portfolioHealth && moneyLeaks && riskAssessment;

  if (!financialData?.data) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500">No financial data available</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-red-600 via-red-700 to-orange-600 rounded-2xl p-8 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-white opacity-10 rounded-full -mr-16 -mt-16"></div>
        <div className="absolute bottom-0 left-0 w-24 h-24 bg-white opacity-10 rounded-full -ml-12 -mb-12"></div>
        <div className="relative z-10">
          <div className="flex items-center space-x-3 mb-4">
            <div className="text-4xl">🔍</div>
            <div>
              <h1 className="text-3xl font-bold">Money Truth Engine</h1>
              <p className="text-red-100 mt-2">AI-powered analysis revealing hidden financial insights</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            <div className="text-center">
              <div className="text-2xl font-bold">100%</div>
              <div className="text-red-100 text-sm">AI-Driven Analysis</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">5</div>
              <div className="text-red-100 text-sm">Killer Features</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">Real-Time</div>
              <div className="text-red-100 text-sm">Live Insights</div>
            </div>
          </div>
          <div className="mt-6 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-red-100 text-sm">
                Last updated: {new Date().toLocaleString()}
              </span>
            </div>
            <button
              onClick={runCompleteAnalysis}
              disabled={isLoading}
              className="bg-white text-red-600 px-6 py-2 rounded-lg font-medium hover:bg-red-50 disabled:opacity-50 transition-colors"
            >
              {isLoading ? '🔄 Analyzing...' : '🚀 Run Complete Analysis'}
            </button>
          </div>
        </div>
      </div>

      {/* Analysis Progress */}
      {isLoading && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Money Truth Engine Running...
            </h3>
            <div className="space-y-4">
              <div className="relative">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-red-600 h-2 rounded-full animate-pulse" style={{width: '100%'}}></div>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4 text-sm">
                <div className="text-center p-3 bg-red-50 rounded-lg border border-red-100">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-red-300 border-t-red-600 mx-auto mb-2"></div>
                  <div className="font-medium text-red-800">Hidden Truths</div>
                  <div className="text-red-600 text-xs">Detecting patterns...</div>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg border border-purple-100">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-purple-300 border-t-purple-600 mx-auto mb-2" style={{animationDelay: '0.2s'}}></div>
                  <div className="font-medium text-purple-800">Future Wealth</div>
                  <div className="text-purple-600 text-xs">Projecting scenarios...</div>
                </div>
                <div className="text-center p-3 bg-blue-50 rounded-lg border border-blue-100">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-300 border-t-blue-600 mx-auto mb-2" style={{animationDelay: '0.4s'}}></div>
                  <div className="font-medium text-blue-800">Portfolio Health</div>
                  <div className="text-blue-600 text-xs">Diagnosing issues...</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg border border-green-100">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-green-300 border-t-green-600 mx-auto mb-2" style={{animationDelay: '0.6s'}}></div>
                  <div className="font-medium text-green-800">Goal Reality</div>
                  <div className="text-green-600 text-xs">Simulating outcomes...</div>
                </div>
                <div className="text-center p-3 bg-indigo-50 rounded-lg border border-indigo-100">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-indigo-300 border-t-indigo-600 mx-auto mb-2" style={{animationDelay: '0.8s'}}></div>
                  <div className="font-medium text-indigo-800">Personality</div>
                  <div className="text-indigo-600 text-xs">Analyzing behavior...</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Insights Grid */}
      {completeInsights && !isLoading && (
        <div className="space-y-8">
          {/* Hidden Money Truths - Priority #1 */}
          <MoneyTruthCard
            title="🚨 Hidden Money Truths"
            subtitle="Shocking discoveries that will change how you see your finances"
            insights={completeInsights.hidden_truths}
            isLoading={false}
            onRefresh={fetchCompleteInsights}
            type="hidden_truths"
          />

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Future Wealth Projection */}
            <MoneyTruthCard
              title="🔮 Future Wealth Projection"
              subtitle="AI predicts your financial future based on current patterns"
              insights={completeInsights.future_projection}
              isLoading={false}
              onRefresh={fetchCompleteInsights}
              type="future_projection"
            />

            {/* Portfolio Health Check */}
            <MoneyTruthCard
              title="🏥 Portfolio Health Diagnosis"
              subtitle="Comprehensive AI analysis of your investment health"
              insights={completeInsights.portfolio_health}
              isLoading={false}
              onRefresh={fetchCompleteInsights}
              type="portfolio_health"
            />
          </div>

          {/* Goal Reality Check - Full Width */}
          <MoneyTruthCard
            title="🎯 Life Goal Reality Check"
            subtitle="Can you actually achieve your dreams? AI simulation reveals the truth"
            insights={completeInsights.goal_reality}
            isLoading={false}
            onRefresh={fetchCompleteInsights}
            type="goal_reality"
          />

          {/* Money Personality Analysis */}
          <MoneyTruthCard
            title="🧠 Money Personality Deep Dive"
            subtitle="What your financial behavior reveals about your wealth potential"
            insights={completeInsights.personality}
            isLoading={false}
            onRefresh={fetchCompleteInsights}
            type="personality"
          />

          {/* Unified Summary */}
          {completeInsights.unified_summary && (
            <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-black rounded-2xl p-8 text-white">
              <div className="flex items-center space-x-3 mb-6">
                <div className="text-4xl">🎯</div>
                <div>
                  <h2 className="text-2xl font-bold">AI Summary & Action Plan</h2>
                  <p className="text-gray-300 mt-1">Your complete financial roadmap</p>
                </div>
              </div>
              <div className="space-y-4">
                {typeof completeInsights.unified_summary === 'string' ? (
                  <p className="text-gray-100 leading-relaxed text-lg">
                    {completeInsights.unified_summary}
                  </p>
                ) : (
                  <div className="space-y-4">
                    {completeInsights.unified_summary.unified_summary && (
                      <p className="text-gray-100 leading-relaxed text-lg">
                        {completeInsights.unified_summary.unified_summary}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Individual Analysis Cards */}
      <div className="space-y-8 mt-12">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Detailed Analysis</h2>
          <p className="text-gray-600">Dive deeper into each aspect of your financial profile</p>
        </div>

        {/* Hidden Money Truths */}
        <MoneyTruthCard
          title="💡 Hidden Money Truths"
          subtitle="Shocking discoveries about your finances"
          insights={hiddenTruths}
          isLoading={isLoadingHidden}
          onRefresh={fetchHiddenTruths}
          type="hidden_truths"
        />

        {/* Two Column Layout for Health & Leaks */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AIInsightCard
            title="🏥 Portfolio Health Check"
            subtitle="AI diagnosis of your investments"
            insights={portfolioHealth}
            isLoading={isLoadingHealth}
            onRefresh={fetchPortfolioHealth}
            type="portfolio_health"
          />
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

        {/* Future Wealth & Goals */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <MoneyTruthCard
            title="🔮 Future Wealth Projection"
            subtitle="AI predicts your financial future"
            insights={futureProjection}
            isLoading={isLoadingFuture}
            onRefresh={fetchFutureProjection}
            type="future_projection"
          />
          <MoneyTruthCard
            title="🎯 Life Goal Reality Check"
            subtitle="Can you achieve your dreams?"
            insights={goalReality}
            isLoading={isLoadingGoals}
            onRefresh={fetchGoalReality}
            type="goal_reality"
          />
        </div>

        {/* Money Personality Analysis */}
        <MoneyTruthCard
          title="🧠 Money Personality Analysis"
          subtitle="What your behavior reveals about your wealth"
          insights={moneyPersonality}
          isLoading={isLoadingPersonality}
          onRefresh={fetchMoneyPersonality}
          type="personality"
        />
      </div>

      {/* Empty State */}
      {!completeInsights && !isLoading && (
        <div className="text-center py-16">
          <div className="text-6xl mb-6">🔍</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Ready to Uncover Your Money Truths?
          </h2>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            Our AI will analyze your complete financial data and reveal shocking insights
            about your money that you've never seen before.
          </p>
          <button
            onClick={fetchCompleteInsights}
            className="bg-red-600 text-white px-8 py-3 rounded-xl font-medium hover:bg-red-700 transition-colors text-lg"
          >
            🚀 Start AI Analysis
          </button>
        </div>
      )}
    </div>
  );
}