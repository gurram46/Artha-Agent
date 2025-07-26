'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface MoneyTruthCardProps {
  title: string;
  subtitle: string;
  insights: any;
  isLoading: boolean;
  onRefresh: () => void;
  type: 'hidden_truths' | 'future_projection' | 'goal_reality' | 'personality' | 'portfolio_health' | 'money_leaks' | 'risk_assessment' | 'trip_planning';
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
    // Fi Money unified dark design for all card types
    return {
      border: 'border-[rgba(0,184,153,0.2)]',
      bg: 'bg-[rgb(24,25,27)]',
      header: 'bg-[rgba(0,184,153,0.05)] border-[rgba(0,184,153,0.2)]'
    };
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
      risk_assessment: 'Analyzing financial risks and threats...',
      trip_planning: 'Planning budget-smart travel options...'
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
      <div className="prose prose-invert max-w-none">
        <ReactMarkdown
          components={{
            h1: ({children}) => <h1 className="text-3xl font-black text-white mb-6">{children}</h1>,
            h2: ({children}) => <h2 className="text-2xl font-bold text-white mb-4">{children}</h2>,
            h3: ({children}) => <h3 className="text-xl font-semibold text-white mb-4">{children}</h3>,
            p: ({children}) => <p className="text-gray-300 leading-relaxed mb-4">{children}</p>,
            ul: ({children}) => <ul className="space-y-3 mb-6">{children}</ul>,
            li: ({children}) => (
              <li className="flex items-start space-x-3 p-4 bg-[rgba(0,184,153,0.05)] rounded-xl border border-[rgba(0,184,153,0.1)]">
                <div className="w-2 h-2 bg-[rgb(0,184,153)] rounded-full mt-2 flex-shrink-0"></div>
                <div className="text-gray-300 leading-relaxed">{children}</div>
              </li>
            ),
            strong: ({children}) => (
              <div className="p-4 bg-[rgba(0,184,153,0.1)] rounded-xl border border-[rgba(0,184,153,0.2)] mb-4 inline-block w-full">
                <span className="font-bold text-white">{children}</span>
              </div>
            ),
            blockquote: ({children}) => (
              <div className="p-4 bg-[rgba(0,184,153,0.1)] rounded-xl border border-[rgba(0,184,153,0.2)] mb-4">
                <div className="flex items-center space-x-2">
                  <span className="text-[rgb(0,184,153)] font-bold">💡 Insight:</span>
                  <div className="text-gray-300 font-medium">{children}</div>
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
        <div className="text-center py-12">
          <div className="text-gray-500 mb-6">
            <svg className="w-20 h-20 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
            </svg>
          </div>
          <p className="text-white text-xl font-bold mb-3">Ready to reveal the truth?</p>
          <p className="text-gray-400 text-sm mb-6">Click to uncover hidden insights about your money</p>
          <button 
            onClick={onRefresh}
            className="bg-[rgb(0,184,153)] hover:bg-[rgb(0,164,133)] text-white px-8 py-3 rounded-xl font-bold transition-all duration-300 shadow-lg transform hover:scale-105"
          >
            🔍 Discover Money Truths
          </button>
        </div>
      );
    }

    // Simple, unified content extraction - extract readable text from any format
    const extractContent = (data: any): string => {
      if (typeof data === 'string') {
        return data;
      }
      
      if (typeof data === 'object' && data !== null) {
        // Try to find any text content in the object
        const textFields = [
          data.ai_insights,
          data.ai_projection, 
          data.goal_analysis,
          data.personality_analysis,
          data.technical_analysis,
          data.portfolio_risk_assessment,
          data.content,
          data.overall_diagnosis,
          data.analysis,
          data.insights
        ];
        
        for (const field of textFields) {
          if (typeof field === 'string' && field.trim().length > 0) {
            return field;
          }
        }
        
        // If no text fields found, try to extract from structured portfolio/risk data
        if (data.health_score !== undefined || data.critical_issues || data.prescription) {
          // For portfolio health, build a readable summary
          let summary = '';
          if (data.overall_diagnosis) summary += `${data.overall_diagnosis}\n\n`;
          if (data.health_score !== undefined) summary += `**Health Score: ${data.health_score}/100**\n\n`;
          if (data.critical_issues && data.critical_issues.length > 0) {
            summary += '**Critical Issues:**\n';
            data.critical_issues.forEach((issue: any, i: number) => {
              summary += `${i + 1}. ${issue.problem} (${issue.severity})\n   Treatment: ${issue.treatment}\n\n`;
            });
          }
          if (data.prescription && data.prescription.length > 0) {
            summary += '**Prescription:**\n';
            data.prescription.forEach((item: string, i: number) => {
              summary += `${i + 1}. ${item}\n`;
            });
          }
          return summary;
        }
      }
      
      return '';
    };

    const content = extractContent(insights);

    // If no content extracted, show a message
    if (!content) {
      return (
        <div className="text-center py-10">
          <div className="text-gray-400 mb-6 text-lg">
            📊 Analysis completed but no readable content available
          </div>
          <button 
            onClick={onRefresh}
            className="bg-[rgb(0,184,153)] hover:bg-[rgb(0,164,133)] text-white px-6 py-3 rounded-xl font-bold transition-all duration-300 shadow-lg"
          >
            🔄 Retry Analysis
          </button>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Simple markdown rendering of extracted content */}
        <div className="max-w-none">
          {renderMarkdownContent(content)}
        </div>
      </div>
    );
  };


  return (
    <div className={`rounded-3xl shadow-2xl border ${cardStyle.border} ${cardStyle.bg}`}>
      <div className={`px-8 py-6 border-b ${cardStyle.header}`}>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-black text-white">{title}</h2>
            <p className="text-sm text-gray-300 mt-2">{subtitle}</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                isLoading ? 'bg-yellow-500 animate-pulse' : 
                insights ? 'bg-[rgb(0,184,153)]' : 'bg-gray-500'
              }`}></div>
              <span className="text-sm text-gray-400 font-medium">
                {isLoading ? 'Analyzing' : insights ? 'Complete' : 'Ready'}
              </span>
            </div>
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-3 text-gray-400 hover:text-[rgb(0,184,153)] rounded-xl hover:bg-[rgba(0,184,153,0.1)] disabled:opacity-50 transition-all duration-300"
            >
              <svg className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <div className="p-8">
        {renderInsightContent()}
      </div>
    </div>
  );
}