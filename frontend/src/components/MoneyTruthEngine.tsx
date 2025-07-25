'use client';

import { useState, useEffect } from 'react';
import MoneyTruthCard from './MoneyTruthCard';
import UnifiedCard from '@/components/ui/UnifiedCard';
import UnifiedButton from '@/components/ui/UnifiedButton';
import { useFinancialInsights } from '../contexts/FinancialInsightsContext';
import { designSystem } from '@/styles/designSystem';

interface Props {
  financialData: any;
}

export default function MoneyTruthEngine({ financialData }: Props) {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'focused'>('grid');
  
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

  const agents = [
    {
      id: 'hidden_truths',
      icon: '🚨',
      title: 'Hidden Money Truths',
      subtitle: 'Shocking discoveries hidden in your data',
      description: 'Uncover shocking financial discoveries that will make you say "I had NO IDEA!" Our AI detective reveals surprising money patterns, hidden inefficiencies, and eye-opening comparisons.',
      features: ['Surprising money patterns', 'Hidden waste & inefficiencies', 'Eye-opening peer comparisons', 'Shocking trajectory implications'],
      gradient: 'from-red-500 to-pink-500',
      bgGradient: 'from-red-50 to-pink-50',
      borderColor: 'border-red-200',
      fetchFunction: fetchHiddenTruths,
      isLoading: isLoadingHidden,
      data: hiddenTruths,
      type: 'hidden_truths' as const
    },
    {
      id: 'future_projection',
      icon: '🔮',
      title: 'Future Wealth Projection',
      subtitle: 'AI predicts your financial future',
      description: 'Our AI crystal ball analyzes your current patterns to predict your financial future with 3 detailed scenarios: best case, realistic, and worst case projections.',
      features: ['5, 10, 20 year projections', 'Best/realistic/worst scenarios', 'Growth acceleration strategies', 'Timeline milestones'],
      gradient: 'from-purple-500 to-indigo-500',
      bgGradient: 'from-purple-50 to-indigo-50',
      borderColor: 'border-purple-200',
      fetchFunction: fetchFutureProjection,
      isLoading: isLoadingFuture,
      data: futureProjection,
      type: 'future_projection' as const
    },
    {
      id: 'portfolio_health',
      icon: '🏥',
      title: 'Portfolio Health Check',
      subtitle: 'Medical-style investment diagnosis',
      description: 'Get a comprehensive health checkup for your investments with our AI doctor. Receive a health score, critical issue detection, and a detailed treatment plan.',
      features: ['Health score 0-100', 'Critical issues detection', 'Specific treatment plan', 'Recovery recommendations'],
      gradient: 'from-emerald-500 to-teal-500',
      bgGradient: 'from-emerald-50 to-teal-50',
      borderColor: 'border-emerald-200',
      fetchFunction: fetchPortfolioHealth,
      isLoading: isLoadingHealth,
      data: portfolioHealth,
      type: 'portfolio_health' as const
    },
    {
      id: 'goal_reality',
      icon: '🎯',
      title: 'Goal Reality Check',
      subtitle: 'Brutal honesty about your dreams',
      description: 'Our AI provides brutal honesty about whether your financial goals are actually achievable. Get realistic timelines, required savings, and alternative strategies.',
      features: ['Realistic goal analysis', 'Required monthly savings', 'Alternative strategies', 'Achievement probability'],
      gradient: 'from-green-500 to-emerald-500',
      bgGradient: 'from-green-50 to-emerald-50',
      borderColor: 'border-green-200',
      fetchFunction: fetchGoalReality,
      isLoading: isLoadingGoals,
      data: goalReality,
      type: 'goal_reality' as const
    },
    {
      id: 'money_personality',
      icon: '🧠',
      title: 'Money Personality',
      subtitle: 'Deep psychological money analysis',
      description: 'Discover your financial DNA with deep psychological analysis of your money behavior patterns, wealth potential, and growth limitations.',
      features: ['Money archetype analysis', 'Behavioral pattern insights', 'Growth limitation detection', 'Wealth potential assessment'],
      gradient: 'from-blue-500 to-cyan-500',
      bgGradient: 'from-blue-50 to-cyan-50',
      borderColor: 'border-blue-200',
      fetchFunction: fetchMoneyPersonality,
      isLoading: isLoadingPersonality,
      data: moneyPersonality,
      type: 'personality' as const
    },
    {
      id: 'money_leaks',
      icon: '🔍',
      title: 'Money Leak Detection',
      subtitle: 'Find where you\'re secretly losing money',
      description: 'Our AI detective does forensic work to find exactly where you\'re secretly losing money and provides immediate fixes to plug those leaks.',
      features: ['Hidden money drains', 'Quantified monthly losses', 'Immediate leak fixes', 'Prevention strategies'],
      gradient: 'from-yellow-500 to-orange-500',
      bgGradient: 'from-yellow-50 to-orange-50',
      borderColor: 'border-yellow-200',
      fetchFunction: fetchMoneyLeaks,
      isLoading: isLoadingLeaks,
      data: moneyLeaks,
      type: 'money_leaks' as const
    },
    {
      id: 'risk_assessment',
      icon: '⚠️',
      title: 'Risk Assessment',
      subtitle: 'Comprehensive threat analysis',
      description: 'Get a comprehensive analysis of financial threats and protection gaps in your wealth with detailed mitigation strategies and insurance recommendations.',
      features: ['Critical risk identification', 'Protection gap analysis', 'Mitigation strategies', 'Insurance recommendations'],
      gradient: 'from-red-500 to-rose-500',
      bgGradient: 'from-red-50 to-rose-50',
      borderColor: 'border-red-200',
      fetchFunction: fetchRiskAssessment,
      isLoading: isLoadingRisk,
      data: riskAssessment,
      type: 'risk_assessment' as const
    }
  ];

  const handleAgentClick = (agentId: string) => {
    const agent = agents.find(a => a.id === agentId);
    if (agent) {
      setSelectedAgent(agentId);
      setViewMode('focused');
      agent.fetchFunction();
    }
  };

  const handleBackToGrid = () => {
    setViewMode('grid');
    setSelectedAgent(null);
  };

  const selectedAgentData = selectedAgent ? agents.find(a => a.id === selectedAgent) : null;

  if (!financialData?.data) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <UnifiedCard className="text-center max-w-md">
          <div className="text-6xl mb-6">📊</div>
          <h2 className={`${designSystem.typography.heading.large} mb-4`}>No Financial Data Available</h2>
          <p className={designSystem.typography.body.default}>Please connect your financial accounts to access Money Truth Engine</p>
        </UnifiedCard>
      </div>
    );
  }

  // Focused view for selected agent
  if (viewMode === 'focused' && selectedAgentData) {
    return (
      <div className="min-h-screen bg-slate-50">
        {/* Header with back button */}
        <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-sm border-b border-slate-200">
          <div className={`${designSystem.layout.container} py-4`}>
            <div className="flex items-center space-x-4">
              <UnifiedButton
                onClick={handleBackToGrid}
                variant="secondary"
                size="sm"
                className="flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span>Back to All Agents</span>
              </UnifiedButton>
              <div className="flex items-center space-x-3">
                <div className={`text-3xl`}>{selectedAgentData.icon}</div>
                <div>
                  <h1 className={designSystem.typography.heading.large}>{selectedAgentData.title}</h1>
                  <p className={designSystem.typography.body.default}>{selectedAgentData.subtitle}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className={`${designSystem.layout.container} ${designSystem.layout.section}`}>
          <MoneyTruthCard
            title={`${selectedAgentData.icon} ${selectedAgentData.title}`}
            subtitle={selectedAgentData.subtitle}
            insights={selectedAgentData.data}
            isLoading={selectedAgentData.isLoading}
            onRefresh={selectedAgentData.fetchFunction}
            type={selectedAgentData.type}
          />
        </div>
      </div>
    );
  }

  // Grid view
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className={`relative ${designSystem.layout.container} py-20`}>
          <div className="text-center text-white">
            <div className="flex items-center justify-center space-x-4 mb-6">
              <div className="text-6xl">🔍</div>
              <div>
                <h1 className="text-5xl font-bold mb-2">Money Truth Engine</h1>
                <p className="text-xl text-blue-100">AI-powered analysis revealing hidden financial insights</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold mb-2">7</div>
                <div className="text-blue-100">Specialized AI Agents</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold mb-2">100%</div>
                <div className="text-blue-100">AI-Driven Analysis</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold mb-2">Real-Time</div>
                <div className="text-blue-100">Live Insights</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Agents Grid */}
      <div className={`${designSystem.layout.container} ${designSystem.layout.section}`}>
        <div className="text-center mb-12">
          <h2 className={`${designSystem.typography.heading.xlarge} mb-4`}>Choose Your AI Financial Detective</h2>
          <p className={`${designSystem.typography.body.large} max-w-3xl mx-auto`}>
            Each specialized AI agent analyzes different aspects of your financial life. 
            Click on any agent to get deep insights tailored to your specific situation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {agents.map((agent) => (
            <UnifiedCard
              key={agent.id}
              className={`group relative hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer overflow-hidden ${agent.borderColor} border-2`}
              onClick={() => handleAgentClick(agent.id)}
              hover={false}
            >
              {/* Gradient overlay */}
              <div className={`absolute inset-0 bg-gradient-to-br ${agent.bgGradient} opacity-50`}></div>
              
              {/* Content */}
              <div className="relative">
                {/* Icon and title */}
                <div className="text-center mb-6">
                  <div className="text-5xl mb-4 transform group-hover:scale-110 transition-transform duration-300">
                    {agent.icon}
                  </div>
                  <h3 className={`${designSystem.typography.heading.medium} mb-2`}>{agent.title}</h3>
                  <p className={`${designSystem.typography.body.small} mb-4`}>{agent.subtitle}</p>
                </div>

                {/* Description */}
                <p className={`${designSystem.typography.body.small} mb-6 leading-relaxed`}>
                  {agent.description}
                </p>

                {/* Features */}
                <div className="mb-6">
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
                    What you'll discover:
                  </h4>
                  <ul className="space-y-2">
                    {agent.features.map((feature, idx) => (
                      <li key={idx} className="text-xs text-slate-600 flex items-start">
                        <span className="w-1.5 h-1.5 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mr-2 mt-1.5 flex-shrink-0"></span>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Action button */}
                <UnifiedButton
                  className={`w-full bg-gradient-to-r ${agent.gradient} hover:shadow-lg transition-all duration-300 transform group-hover:scale-105`}
                  disabled={agent.isLoading}
                  isLoading={agent.isLoading}
                  variant="primary"
                >
                  {!agent.isLoading && (
                    <span>🚀 Analyze with {agent.title}</span>
                  )}
                </UnifiedButton>

                {/* Status indicator */}
                <div className="flex items-center justify-center mt-4 space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    agent.isLoading ? 'bg-yellow-500 animate-pulse' : 
                    agent.data ? 'bg-green-500' : 'bg-slate-300'
                  }`}></div>
                  <span className="text-xs text-slate-500">
                    {agent.isLoading ? 'Analyzing' : agent.data ? 'Complete' : 'Ready'}
                  </span>
                </div>
              </div>
            </UnifiedCard>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="mt-16 text-center">
          <UnifiedCard className="max-w-2xl mx-auto">
            <h3 className={`${designSystem.typography.heading.large} mb-4`}>Quick Actions</h3>
            <div className="flex flex-wrap justify-center gap-4">
              <UnifiedButton
                onClick={() => agents.forEach(agent => agent.fetchFunction())}
                variant="primary"
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:shadow-lg"
              >
                🚀 Run All Agents
              </UnifiedButton>
              <UnifiedButton
                onClick={clearAllData}
                variant="secondary"
                className="bg-gradient-to-r from-slate-600 to-slate-700 text-white hover:shadow-lg"
              >
                🔄 Clear All Data
              </UnifiedButton>
            </div>
          </UnifiedCard>
        </div>
      </div>
    </div>
  );
}