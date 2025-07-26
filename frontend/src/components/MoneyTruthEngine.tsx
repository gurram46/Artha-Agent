'use client';

import { useState, useEffect } from 'react';
import MoneyTruthCard from './MoneyTruthCard';
import TripPlanningChatbot from './TripPlanningChatbot';
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
  const [showTripChatbot, setShowTripChatbot] = useState(false);
  
  // Use global financial insights context
  const {
    portfolioHealth,
    riskAssessment,
    tripPlanning,
    isLoadingHealth,
    isLoadingRisk,
    isLoadingTrip,
    fetchPortfolioHealth,
    fetchRiskAssessment,
    fetchTripPlanning,
    clearAllData
  } = useFinancialInsights();

  const agents = [
    {
      id: 'portfolio_health',
      icon: '🏥',
      title: 'Portfolio Health Check',
      subtitle: 'Comprehensive investment analysis',
      description: 'Get a thorough health checkup for your investments with AI-powered analysis. Receive detailed insights, performance metrics, and optimization recommendations.',
      features: ['Performance analysis', 'Asset allocation review', 'Diversification assessment', 'Optimization recommendations'],
      gradient: 'from-emerald-500 to-teal-500',
      bgGradient: 'from-emerald-50 to-teal-50',
      borderColor: 'border-emerald-200',
      fetchFunction: fetchPortfolioHealth,
      isLoading: isLoadingHealth,
      data: portfolioHealth,
      type: 'portfolio_health' as const
    },
    {
      id: 'risk_assessment',
      icon: '⚠️',
      title: 'Risk Assessment',
      subtitle: 'Financial risk analysis',
      description: 'Comprehensive analysis of financial risks in your portfolio with detailed mitigation strategies and protection recommendations.',
      features: ['Risk identification', 'Protection analysis', 'Mitigation strategies', 'Insurance recommendations'],
      gradient: 'from-red-500 to-rose-500',
      bgGradient: 'from-red-50 to-rose-50',
      borderColor: 'border-red-200',
      fetchFunction: fetchRiskAssessment,
      isLoading: isLoadingRisk,
      data: riskAssessment,
      type: 'risk_assessment' as const
    },
    {
      id: 'trip_planning',
      icon: '🧳',
      title: 'Smart Trip Planner',
      subtitle: 'Interactive AI travel chatbot',
      description: 'Chat with your personal AI travel advisor who knows your finances! Get real-time trip recommendations, budget analysis, and personalized itineraries through interactive conversation.',
      features: ['Interactive chat planning', 'Real-time recommendations', 'Budget-aware suggestions', 'Personalized itineraries'],
      gradient: 'from-blue-500 to-cyan-500',
      bgGradient: 'from-blue-50 to-cyan-50',
      borderColor: 'border-blue-200',
      fetchFunction: fetchTripPlanning,
      isLoading: isLoadingTrip,
      data: tripPlanning,
      type: 'trip_planning' as const
    }
  ];

  const handleAgentClick = (agentId: string) => {
    const agent = agents.find(a => a.id === agentId);
    if (agent) {
      if (agentId === 'trip_planning') {
        // Open chatbot for trip planning
        setShowTripChatbot(true);
      } else {
        // Regular agent card view
        setSelectedAgent(agentId);
        setViewMode('focused');
        agent.fetchFunction();
      }
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
      <div className="min-h-screen bg-[rgb(0,26,30)]">
        {/* Header with back button */}
        <div className="sticky top-0 z-10 bg-[rgba(0,26,30,0.95)] backdrop-blur-sm border-b border-[rgba(0,184,153,0.2)]">
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
    <div className="min-h-screen bg-[rgb(0,26,30)]">
      {/* Fi Money Hero Section */}
      <div className="relative overflow-hidden bg-[rgb(11,17,17)]">
        <div className="absolute inset-0 bg-[rgba(0,184,153,0.05)]"></div>
        <div className={`relative ${designSystem.layout.container} py-20`}>
          <div className="text-center text-white">
            <div className="flex items-center justify-center space-x-6 mb-8">
              <div className="text-7xl">🤖</div>
              <div>
                <h1 className="text-6xl font-black mb-3 text-white">Money Truth Engine</h1>
                <p className="text-2xl text-[rgb(0,184,153)]">AI-powered analysis revealing hidden financial insights</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16 max-w-5xl mx-auto">
              <div className="text-center bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6">
                <div className="text-4xl font-black mb-3 text-[rgb(0,184,153)]">3</div>
                <div className="text-gray-300 font-semibold">Core AI Agents</div>
              </div>
              <div className="text-center bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6">
                <div className="text-4xl font-black mb-3 text-[rgb(0,184,153)]">100%</div>
                <div className="text-gray-300 font-semibold">AI-Driven Analysis</div>
              </div>
              <div className="text-center bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6">
                <div className="text-4xl font-black mb-3 text-[rgb(0,184,153)]">Real-Time</div>
                <div className="text-gray-300 font-semibold">Live Insights</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Fi Money Agents Grid */}
      <div className={`${designSystem.layout.container} ${designSystem.layout.section}`}>
        <div className="text-center mb-16">
          <h2 className="text-4xl font-black text-white mb-6">Choose Your AI Financial Detective</h2>
          <p className="text-xl text-gray-300 max-w-4xl mx-auto leading-relaxed">
            Each specialized AI agent analyzes different aspects of your financial life. 
            Click on any agent to get deep insights tailored to your specific situation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="group relative bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] hover:border-[rgba(0,184,153,0.5)] rounded-3xl p-8 cursor-pointer transition-all duration-300 transform hover:-translate-y-2 hover:shadow-2xl"
              onClick={() => handleAgentClick(agent.id)}
            >
              {/* Fi Money Gradient overlay */}
              <div className="absolute inset-0 bg-[rgba(0,184,153,0.02)] rounded-3xl"></div>
              
              {/* Content */}
              <div className="relative">
                {/* Icon and title */}
                <div className="text-center mb-8">
                  <div className="text-6xl mb-6 transform group-hover:scale-110 transition-transform duration-300">
                    {agent.icon}
                  </div>
                  <h3 className="text-2xl font-black text-white mb-3">{agent.title}</h3>
                  <p className="text-lg text-gray-300 mb-6">{agent.subtitle}</p>
                </div>

                {/* Description */}
                <p className="text-gray-400 mb-8 leading-relaxed text-center">
                  {agent.description}
                </p>

                {/* Features */}
                <div className="mb-8">
                  <h4 className="text-sm font-bold text-[rgb(0,184,153)] uppercase tracking-wide mb-4">
                    What you'll discover:
                  </h4>
                  <ul className="space-y-3">
                    {agent.features.map((feature, idx) => (
                      <li key={idx} className="text-sm text-gray-300 flex items-start">
                        <span className="w-2 h-2 bg-[rgb(0,184,153)] rounded-full mr-3 mt-2 flex-shrink-0"></span>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Action button */}
                <button
                  className="w-full bg-[rgb(0,184,153)] hover:bg-[rgb(0,164,133)] text-white font-bold py-4 px-6 rounded-2xl transition-all duration-300 transform group-hover:scale-105 shadow-lg disabled:opacity-50"
                  disabled={agent.isLoading}
                >
                  {agent.isLoading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Analyzing...</span>
                    </div>
                  ) : (
                    <span>{agent.id === 'trip_planning' ? '💬 Chat with ' : '🚀 Analyze with '}{agent.title}</span>
                  )}
                </button>

                {/* Status indicator */}
                <div className="flex items-center justify-center mt-6 space-x-2">
                  <div className={`w-3 h-3 rounded-full ${
                    agent.isLoading ? 'bg-yellow-500 animate-pulse' : 
                    agent.data ? 'bg-[rgb(0,184,153)]' : 'bg-gray-500'
                  }`}></div>
                  <span className="text-sm text-gray-400 font-medium">
                    {agent.isLoading ? 'Analyzing' : agent.data ? 'Complete' : 'Ready'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Fi Money Quick Actions */}
        <div className="mt-20 text-center">
          <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-8 max-w-3xl mx-auto">
            <h3 className="text-3xl font-black text-white mb-6">Quick Actions</h3>
            <div className="flex flex-wrap justify-center gap-6">
              <button
                onClick={() => agents.forEach(agent => agent.fetchFunction())}
                className="bg-[rgb(0,184,153)] hover:bg-[rgb(0,164,133)] text-white font-bold py-4 px-8 rounded-2xl transition-all duration-300 shadow-lg transform hover:scale-105"
              >
                🚀 Run All Agents
              </button>
              <button
                onClick={clearAllData}
                className="bg-[rgb(70,68,68)] hover:bg-[rgb(90,88,88)] text-white font-bold py-4 px-8 rounded-2xl transition-all duration-300 shadow-lg transform hover:scale-105"
              >
                🔄 Clear All Data
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Trip Planning Chatbot */}
      {showTripChatbot && (
        <TripPlanningChatbot 
          onClose={() => setShowTripChatbot(false)}
        />
      )}
    </div>
  );
}