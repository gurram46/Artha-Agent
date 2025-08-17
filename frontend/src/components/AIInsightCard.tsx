'use client';

import { useState } from 'react';

interface AIInsightCardProps {
  title: string;
  subtitle: string;
  insights: any;
  isLoading: boolean;
  onRefresh: () => void;
  type: 'portfolio_health' | 'money_leaks' | 'risk_assessment';
}

export default function AIInsightCard({ 
  title, 
  subtitle, 
  insights, 
  isLoading, 
  onRefresh, 
  type 
}: AIInsightCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const renderInsightContent = () => {
    if (isLoading) {
      return (
        <div className="space-y-4">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="animate-spin rounded-full h-8 w-8 border-3 border-gray-200 border-t-blue-600"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
              </div>
            </div>
            <div className="flex-1">
              <div className="text-sm text-gray-600 font-medium">
                AI agents are analyzing...
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {type === 'portfolio_health' && 'Running technical analysis on your investments'}
                {type === 'money_leaks' && 'Scanning for hidden fees and inefficiencies'}
                {type === 'risk_assessment' && 'Evaluating risks and protection gaps'}
              </div>
            </div>
          </div>
          
          {/* Loading skeleton */}
          <div className="space-y-3 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      );
    }

    if (!insights) {
      return (
        <div className="text-center py-8">
          <div className="text-gray-400 mb-3">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <p className="text-gray-500 text-sm">No insights available</p>
          <button 
            onClick={onRefresh}
            className="mt-3 text-blue-600 text-sm font-medium hover:text-blue-700"
          >
            Generate AI insights
          </button>
        </div>
      );
    }

    // Handle insights - always treat as text content
    const parsedInsights = {
      content: typeof insights === 'string' ? insights : 
               insights?.content || 
               insights?.ai_insights ||
               insights?.technical_analysis ||
               insights?.money_leaks ||
               insights?.portfolio_risk_assessment ||
               JSON.stringify(insights, null, 2)
    };

    return (
      <div className="space-y-4">
        {/* Main insight content */}
        <div className="prose prose-sm max-w-none">
          {typeof parsedInsights === 'string' ? (
            <p className="text-gray-700 leading-relaxed">{parsedInsights}</p>
          ) : (
            <div className="space-y-3">
              {parsedInsights.content && (
                <p className="text-gray-700 leading-relaxed">
                  {parsedInsights.content}
                </p>
              )}
              
              {/* Portfolio Health specific rendering */}
              {type === 'portfolio_health' && parsedInsights.technical_analysis && (
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm text-blue-800">{parsedInsights.technical_analysis}</p>
                </div>
              )}
              
              {/* Money Leaks specific rendering */}
              {type === 'money_leaks' && parsedInsights.money_leaks && (
                <div className="bg-red-50 p-3 rounded-lg">
                  <p className="text-sm text-red-800">{parsedInsights.money_leaks}</p>
                </div>
              )}
              
              {/* Risk Assessment specific rendering */}
              {type === 'risk_assessment' && parsedInsights.portfolio_risk_assessment && (
                <div className="bg-yellow-50 p-3 rounded-lg">
                  <p className="text-sm text-yellow-800">{parsedInsights.portfolio_risk_assessment}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Action indicators */}
        {parsedInsights.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-red-700">Analysis temporarily unavailable</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
            <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div className={`w-2 h-2 rounded-full ${
                isLoading ? 'bg-yellow-500 animate-pulse' : 
                insights ? 'bg-[#cca695]' : 'bg-gray-400'
              }`}></div>
              <span className="text-xs text-gray-500">
                {isLoading ? 'Analyzing' : insights ? 'Ready' : 'Idle'}
              </span>
            </div>
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-1.5 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 disabled:opacity-50"
            >
              <svg className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <div className="p-6">
        {renderInsightContent()}
        
        {/* Show expand/collapse if content is long */}
        {insights && typeof insights === 'string' && insights.length > 500 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-3 text-sm text-blue-600 font-medium hover:text-blue-700"
          >
            {isExpanded ? 'Show less' : 'Show more'}
          </button>
        )}
      </div>
    </div>
  );
}