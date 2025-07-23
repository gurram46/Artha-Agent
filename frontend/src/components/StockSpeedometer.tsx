'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface StockRecommendation {
  score: number; // 0-100
  sentiment: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell';
  strengths: string[];
  weaknesses: string[];
  considerations: string[];
  confidence: number; // 0-100
  lastUpdated: string;
  analysis: {
    technical: number;
    fundamental: number;
    market: number;
    risk: number;
  };
}

interface StockSpeedometerProps {
  recommendation: StockRecommendation | null;
  loading?: boolean;
  symbol: string;
}

const getSentimentConfig = (sentiment: string) => {
  const configs = {
    strong_buy: {
      label: 'Strong Buy',
      color: '#10b981',
      bgColor: 'from-emerald-400 to-emerald-600',
      textColor: 'text-emerald-700',
      icon: '🚀',
    },
    buy: {
      label: 'Buy',
      color: '#22c55e',
      bgColor: 'from-green-400 to-green-600',
      textColor: 'text-green-700',
      icon: '📈',
    },
    hold: {
      label: 'Hold',
      color: '#f59e0b',
      bgColor: 'from-yellow-400 to-yellow-600',
      textColor: 'text-yellow-700',
      icon: '⚖️',
    },
    sell: {
      label: 'Sell',
      color: '#ef4444',
      bgColor: 'from-red-400 to-red-600',
      textColor: 'text-red-700',
      icon: '📉',
    },
    strong_sell: {
      label: 'Strong Sell',
      color: '#dc2626',
      bgColor: 'from-red-500 to-red-700',
      textColor: 'text-red-800',
      icon: '⚠️',
    },
  };
  return configs[sentiment] || configs.hold;
};

const Speedometer = ({ score, sentiment, confidence }: { score: number; sentiment: string; confidence: number }) => {
  const [animatedScore, setAnimatedScore] = useState(0);
  const sentimentConfig = getSentimentConfig(sentiment);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedScore(score);
    }, 500);
    return () => clearTimeout(timer);
  }, [score]);

  // Calculate needle rotation (0-180 degrees)
  const needleRotation = (animatedScore / 100) * 180;
  
  // Generate arc segments
  const generateArcSegments = () => {
    const segments = [];
    const colors = ['#dc2626', '#ef4444', '#f59e0b', '#22c55e', '#10b981'];
    
    for (let i = 0; i < 5; i++) {
      const startAngle = i * 36 - 90;
      const endAngle = (i + 1) * 36 - 90;
      const isActive = score > i * 20;
      
      segments.push(
        <motion.path
          key={i}
          d={`M 150 150 L ${150 + 100 * Math.cos((startAngle * Math.PI) / 180)} ${150 + 100 * Math.sin((startAngle * Math.PI) / 180)} A 100 100 0 0 1 ${150 + 100 * Math.cos((endAngle * Math.PI) / 180)} ${150 + 100 * Math.sin((endAngle * Math.PI) / 180)} Z`}
          fill={isActive ? colors[i] : '#e2e8f0'}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: i * 0.1, duration: 0.3 }}
        />
      );
    }
    return segments;
  };

  return (
    <div className="relative">
      <svg width="300" height="200" viewBox="0 0 300 200" className="overflow-visible">
        {/* Background Arc */}
        <path
          d="M 50 150 A 100 100 0 0 1 250 150"
          fill="none"
          stroke="#e2e8f0"
          strokeWidth="20"
          strokeLinecap="round"
        />
        
        {/* Colored Segments */}
        {generateArcSegments()}
        
        {/* Score Markers */}
        {[0, 20, 40, 60, 80, 100].map((value, i) => {
          const angle = (value / 100) * 180 - 90;
          const x1 = 150 + 85 * Math.cos((angle * Math.PI) / 180);
          const y1 = 150 + 85 * Math.sin((angle * Math.PI) / 180);
          const x2 = 150 + 95 * Math.cos((angle * Math.PI) / 180);
          const y2 = 150 + 95 * Math.sin((angle * Math.PI) / 180);
          
          return (
            <g key={i}>
              <line
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke="#64748b"
                strokeWidth="2"
              />
              <text
                x={150 + 110 * Math.cos((angle * Math.PI) / 180)}
                y={150 + 110 * Math.sin((angle * Math.PI) / 180)}
                textAnchor="middle"
                alignmentBaseline="middle"
                className="text-xs font-medium fill-slate-600"
              >
                {value}
              </text>
            </g>
          );
        })}
        
        {/* Needle */}
        <motion.g
          animate={{ rotate: needleRotation }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
          style={{ transformOrigin: '150px 150px' }}
        >
          <line
            x1="150"
            y1="150"
            x2="60"
            y2="150"
            stroke={sentimentConfig.color}
            strokeWidth="4"
            strokeLinecap="round"
          />
          <circle
            cx="150"
            cy="150"
            r="8"
            fill={sentimentConfig.color}
          />
        </motion.g>
        
        {/* Center Circle */}
        <circle
          cx="150"
          cy="150"
          r="12"
          fill="white"
          stroke="#e2e8f0"
          strokeWidth="2"
        />
      </svg>
      
      {/* Score Display */}
      <div className="absolute inset-0 flex flex-col items-center justify-end pb-8">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 1, duration: 0.5 }}
          className="text-center"
        >
          <div className="text-4xl font-bold text-slate-900">
            {Math.round(animatedScore)}
          </div>
          <div className="text-sm text-slate-600">out of 100</div>
        </motion.div>
      </div>
      
      {/* Confidence Indicator */}
      <div className="absolute top-2 right-2">
        <div className="flex items-center space-x-1 bg-white/90 backdrop-blur-sm rounded-full px-3 py-1 border border-slate-200">
          <div className="w-2 h-2 rounded-full bg-blue-500"></div>
          <span className="text-xs font-medium text-slate-700">{confidence}% confidence</span>
        </div>
      </div>
    </div>
  );
};

export default function StockSpeedometer({ recommendation, loading, symbol }: StockSpeedometerProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'analysis' | 'details'>('overview');

  if (loading) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
        <div className="text-center space-y-4">
          <div className="relative">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              className="w-16 h-16 mx-auto"
            >
              <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full"></div>
            </motion.div>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl">🤖</span>
            </div>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-900">AI Analysis in Progress</h3>
            <p className="text-sm text-slate-600">Researching {symbol} across multiple sources...</p>
          </div>
          <div className="space-y-2 text-xs text-slate-500">
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
              <span>Analyzing technical indicators</span>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse delay-75"></div>
              <span>Evaluating fundamental metrics</span>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-yellow-600 rounded-full animate-pulse delay-150"></div>
              <span>Researching market sentiment</span>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse delay-225"></div>
              <span>Assessing risk factors</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto">
            <span className="text-2xl">📊</span>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-900">No Analysis Available</h3>
            <p className="text-sm text-slate-600">Click "Get AI Recommendation" to analyze this stock</p>
          </div>
        </div>
      </div>
    );
  }

  const sentimentConfig = getSentimentConfig(recommendation.sentiment);

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${sentimentConfig.bgColor} flex items-center justify-center shadow-lg`}>
              <span className="text-2xl">{sentimentConfig.icon}</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900">AI Recommendation</h3>
              <div className="flex items-center space-x-2">
                <span className={`text-sm font-medium ${sentimentConfig.textColor}`}>
                  {sentimentConfig.label}
                </span>
                <span className="text-xs text-slate-500">
                  Updated {new Date(recommendation.lastUpdated).toLocaleTimeString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-6 py-2 border-b border-slate-200">
        <div className="flex space-x-1">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'analysis', label: 'Analysis', icon: '🔍' },
            { id: 'details', label: 'Details', icon: '📋' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`
                flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                ${activeTab === tab.id 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }
              `}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.2 }}
          className="p-6"
        >
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Speedometer */}
              <div className="flex justify-center">
                <Speedometer 
                  score={recommendation.score} 
                  sentiment={recommendation.sentiment}
                  confidence={recommendation.confidence}
                />
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-50 rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600">{recommendation.analysis.technical}</div>
                  <div className="text-xs text-slate-600">Technical</div>
                </div>
                <div className="bg-slate-50 rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-green-600">{recommendation.analysis.fundamental}</div>
                  <div className="text-xs text-slate-600">Fundamental</div>
                </div>
                <div className="bg-slate-50 rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-yellow-600">{recommendation.analysis.market}</div>
                  <div className="text-xs text-slate-600">Market</div>
                </div>
                <div className="bg-slate-50 rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-red-600">{recommendation.analysis.risk}</div>
                  <div className="text-xs text-slate-600">Risk</div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'analysis' && (
            <div className="space-y-6">
              {/* Strengths */}
              <div>
                <h4 className="font-semibold text-slate-900 mb-3 flex items-center">
                  <span className="text-green-600 mr-2">✅</span>
                  Strengths
                </h4>
                <div className="space-y-2">
                  {recommendation.strengths.map((strength, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg border border-green-200"
                    >
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                      <p className="text-sm text-green-800">{strength}</p>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Weaknesses */}
              <div>
                <h4 className="font-semibold text-slate-900 mb-3 flex items-center">
                  <span className="text-red-600 mr-2">⚠️</span>
                  Weaknesses
                </h4>
                <div className="space-y-2">
                  {recommendation.weaknesses.map((weakness, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg border border-red-200"
                    >
                      <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                      <p className="text-sm text-red-800">{weakness}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'details' && (
            <div className="space-y-6">
              {/* Considerations */}
              <div>
                <h4 className="font-semibold text-slate-900 mb-3 flex items-center">
                  <span className="text-blue-600 mr-2">💡</span>
                  Key Considerations
                </h4>
                <div className="space-y-2">
                  {recommendation.considerations.map((consideration, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-200"
                    >
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                      <p className="text-sm text-blue-800">{consideration}</p>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Confidence & Methodology */}
              <div className="bg-slate-50 rounded-xl p-4">
                <h4 className="font-semibold text-slate-900 mb-3">Analysis Methodology</h4>
                <div className="space-y-3 text-sm text-slate-600">
                  <div className="flex justify-between">
                    <span>AI Confidence Level:</span>
                    <span className="font-medium">{recommendation.confidence}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Data Sources:</span>
                    <span className="font-medium">Google Search, Financial APIs</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Analysis Type:</span>
                    <span className="font-medium">Multi-Agent AI Research</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Last Updated:</span>
                    <span className="font-medium">
                      {new Date(recommendation.lastUpdated).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}