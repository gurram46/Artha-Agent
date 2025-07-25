'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface MoneyTruthCardProps {
  title: string;
  subtitle: string;
  insights: any;
  isLoading: boolean;
  onRefresh: () => void;
  type: 'hidden_truths' | 'future_projection' | 'goal_reality' | 'personality' | 'portfolio_health' | 'money_leaks' | 'risk_assessment';
}

export default function MoneyTruthCard({ 
  title, 
  subtitle, 
  insights, 
  isLoading, 
  onRefresh, 
  type 
}: MoneyTruthCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getCardStyle = () => {
    switch (type) {
      case 'hidden_truths':
        return {
          border: 'border-red-200',
          bg: 'bg-gradient-to-br from-red-50 to-orange-50',
          header: 'bg-red-50 border-red-100'
        };
      case 'future_projection':
        return {
          border: 'border-purple-200',
          bg: 'bg-gradient-to-br from-purple-50 to-indigo-50',
          header: 'bg-purple-50 border-purple-100'
        };
      case 'goal_reality':
        return {
          border: 'border-green-200',
          bg: 'bg-gradient-to-br from-green-50 to-emerald-50',
          header: 'bg-green-50 border-green-100'
        };
      case 'personality':
        return {
          border: 'border-blue-200',
          bg: 'bg-gradient-to-br from-blue-50 to-cyan-50',
          header: 'bg-blue-50 border-blue-100'
        };
      case 'portfolio_health':
        return {
          border: 'border-emerald-200',
          bg: 'bg-gradient-to-br from-emerald-50 to-green-50',
          header: 'bg-emerald-50 border-emerald-100'
        };
      case 'money_leaks':
        return {
          border: 'border-yellow-200',
          bg: 'bg-gradient-to-br from-yellow-50 to-amber-50',
          header: 'bg-yellow-50 border-yellow-100'
        };
      case 'risk_assessment':
        return {
          border: 'border-red-200',
          bg: 'bg-gradient-to-br from-red-50 to-pink-50',
          header: 'bg-red-50 border-red-100'
        };
      default:
        return {
          border: 'border-gray-200',
          bg: 'bg-white',
          header: 'bg-gray-50 border-gray-100'
        };
    }
  };

  const cardStyle = getCardStyle();

  const renderLoadingState = () => {
    const loadingMessages = {
      hidden_truths: 'Uncovering hidden financial patterns...',
      future_projection: 'Calculating future wealth trajectories...',
      goal_reality: 'Analyzing life goal feasibility...',
      personality: 'Evaluating money behavior patterns...',
      portfolio_health: 'Diagnosing investment health...',
      money_leaks: 'Detecting money drains and leaks...',
      risk_assessment: 'Analyzing financial risks and threats...'
    };

    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <div className="animate-spin rounded-full h-10 w-10 border-3 border-gray-200 border-t-red-500"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            </div>
          </div>
          <div className="flex-1">
            <div className="text-base text-gray-700 font-medium">
              AI Money Truth Engine at work...
            </div>
            <div className="text-sm text-gray-500 mt-1">
              {loadingMessages[type]}
            </div>
          </div>
        </div>
        
        {/* Animated thinking indicators */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <div className="animate-pulse w-2 h-2 bg-red-400 rounded-full"></div>
            <div className="text-sm text-gray-600">Analyzing transaction patterns...</div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="animate-pulse w-2 h-2 bg-orange-400 rounded-full" style={{animationDelay: '0.2s'}}></div>
            <div className="text-sm text-gray-600">Detecting financial inefficiencies...</div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="animate-pulse w-2 h-2 bg-yellow-400 rounded-full" style={{animationDelay: '0.4s'}}></div>
            <div className="text-sm text-gray-600">Calculating impact projections...</div>
          </div>
        </div>
        
        {/* Loading skeleton */}
        <div className="space-y-4 animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-4/5"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  };

  const renderMarkdownContent = (text: string) => {
    if (!text) return null;
    
    return (
      <div className="prose prose-sm max-w-none">
        <ReactMarkdown
          components={{
            h1: ({children}) => <h1 className="text-2xl font-bold text-gray-900 mb-4">{children}</h1>,
            h2: ({children}) => <h2 className="text-xl font-bold text-gray-900 mb-3">{children}</h2>,
            h3: ({children}) => <h3 className="text-lg font-bold text-gray-900 mb-3">{children}</h3>,
            p: ({children}) => <p className="text-gray-700 leading-relaxed mb-3">{children}</p>,
            ul: ({children}) => <ul className="space-y-2 mb-4">{children}</ul>,
            li: ({children}) => (
              <li className="flex items-start space-x-3 p-3 bg-white rounded-lg border border-gray-100">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                <div className="text-gray-800 leading-relaxed">{children}</div>
              </li>
            ),
            strong: ({children}) => (
              <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 mb-3 inline-block w-full">
                <span className="font-bold text-gray-900">{children}</span>
              </div>
            ),
            blockquote: ({children}) => (
              <div className="p-4 bg-green-50 rounded-lg border border-green-200 mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-green-600 font-bold">💡 Insight:</span>
                  <div className="text-green-800 font-medium">{children}</div>
                </div>
              </div>
            )
          }}
        >
          {text}
        </ReactMarkdown>
      </div>
    );
  };

  const renderInsightContent = () => {
    if (isLoading) {
      return renderLoadingState();
    }

    if (!insights) {
      return (
        <div className="text-center py-8">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
            </svg>
          </div>
          <p className="text-gray-600 text-lg font-medium mb-2">Ready to reveal the truth?</p>
          <p className="text-gray-500 text-sm mb-4">Click to uncover hidden insights about your money</p>
          <button 
            onClick={onRefresh}
            className="bg-red-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors"
          >
            🔍 Discover Money Truths
          </button>
        </div>
      );
    }

    // Handle insights - always extract readable content
    const parsedInsights = {
      ai_insights: typeof insights === 'string' ? insights :
                   insights?.ai_insights ||
                   insights?.ai_projection ||
                   insights?.goal_analysis ||
                   insights?.personality_analysis ||
                   insights?.content ||
                   JSON.stringify(insights, null, 2)
    };

    return (
      <div className="space-y-6">
        {/* Main insight content with beautiful markdown rendering */}
        <div className="max-w-none">
          {parsedInsights.ai_insights && (
            <div className="space-y-4">
              {renderMarkdownContent(parsedInsights.ai_insights)}
            </div>
          )}

          {/* Type-specific content rendering */}
          {type === 'hidden_truths' && renderHiddenTruthsContent(parsedInsights)}
          {type === 'future_projection' && renderFutureProjectionContent(parsedInsights)}
          {type === 'goal_reality' && renderGoalRealityContent(parsedInsights)}
          {type === 'personality' && renderPersonalityContent(parsedInsights)}
        </div>

        {/* Status indicators - only show when analysis is complete */}
        {parsedInsights.ai_insights && typeof parsedInsights.ai_insights === 'string' && parsedInsights.ai_insights.length > 50 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-3 bg-white rounded-lg border">
              <div className="text-2xl font-bold text-red-600">🚨</div>
              <div className="text-xs text-gray-600 mt-1">High Impact</div>
            </div>
            <div className="text-center p-3 bg-white rounded-lg border">
              <div className="text-2xl font-bold text-orange-600">💡</div>
              <div className="text-xs text-gray-600 mt-1">Eye Opening</div>
            </div>
            <div className="text-center p-3 bg-white rounded-lg border">
              <div className="text-2xl font-bold text-green-600">✅</div>
              <div className="text-xs text-gray-600 mt-1">Actionable</div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderHiddenTruthsContent = (insights: any) => {
    return (
      <div className="space-y-4">
        {insights.bleeding_investments && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <h4 className="font-semibold text-red-800 mb-2">🩸 Bleeding Investments</h4>
            <p className="text-red-700 text-sm">{insights.bleeding_investments}</p>
          </div>
        )}
        {insights.dead_money && (
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h4 className="font-semibold text-yellow-800 mb-2">💀 Dead Money</h4>
            <p className="text-yellow-700 text-sm">{insights.dead_money}</p>
          </div>
        )}
      </div>
    );
  };

  const renderFutureProjectionContent = (insights: any) => {
    return (
      <div className="space-y-4">
        {insights.ai_projection && (
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <h4 className="font-semibold text-purple-800 mb-2">🔮 AI Projection</h4>
            <p className="text-purple-700 text-sm">{insights.ai_projection}</p>
          </div>
        )}
      </div>
    );
  };

  const renderGoalRealityContent = (insights: any) => {
    return (
      <div className="space-y-4">
        {insights.goal_analysis && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <h4 className="font-semibold text-green-800 mb-2">🎯 Goal Analysis</h4>
            <p className="text-green-700 text-sm">{insights.goal_analysis}</p>
          </div>
        )}
      </div>
    );
  };

  const renderPersonalityContent = (insights: any) => {
    return (
      <div className="space-y-4">
        {insights.personality_analysis && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-semibold text-blue-800 mb-2">🧠 Personality Analysis</h4>
            <p className="text-blue-700 text-sm">{insights.personality_analysis}</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`rounded-xl shadow-lg border ${cardStyle.border} ${cardStyle.bg}`}>
      <div className={`px-6 py-4 border-b ${cardStyle.header}`}>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{title}</h2>
            <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-1">
              <div className={`w-2 h-2 rounded-full ${
                isLoading ? 'bg-yellow-500 animate-pulse' : 
                insights ? 'bg-green-500' : 'bg-gray-400'
              }`}></div>
              <span className="text-xs text-gray-500 font-medium">
                {isLoading ? 'Analyzing' : insights ? 'Complete' : 'Ready'}
              </span>
            </div>
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-2 text-gray-600 hover:text-gray-800 rounded-lg hover:bg-white/50 disabled:opacity-50 transition-colors"
            >
              <svg className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <div className="p-6">
        {renderInsightContent()}
      </div>
    </div>
  );
}