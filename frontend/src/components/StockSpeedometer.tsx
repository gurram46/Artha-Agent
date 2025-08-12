'use client';

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

interface StockRecommendation {
  score: number;
  sentiment: string;
  strengths: string[];
  weaknesses: string[];
  considerations: string[];
  confidence: number;
  lastUpdated: string;
  analysis?: {
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
  userProfile?: any;
  onAnalysisStart?: () => void;
  onProfileSetup?: () => void;
}

interface LogMessage {
  type: 'log' | 'error' | 'result';
  content: string | any;
  timestamp: number;
}

const getSentimentConfig = (sentiment: string) => {
  const configs: Record<string, any> = {
    'strong buy': {
      label: 'Strong Buy',
      color: '#10b981',
      bgColor: 'from-emerald-500 to-green-600',
      textColor: 'text-emerald-700',
      icon: '🚀',
      range: [80, 100]
    },
    'buy': {
      label: 'Buy',
      color: '#22c55e', 
      bgColor: 'from-green-400 to-green-600',
      textColor: 'text-green-700',
      icon: '📈',
      range: [60, 79]
    },
    'hold': {
      label: 'Hold',
      color: '#f59e0b',
      bgColor: 'from-yellow-400 to-orange-500',
      textColor: 'text-yellow-700',
      icon: '⚖️',
      range: [40, 59]
    },
    'sell': {
      label: 'Sell',
      color: '#f97316',
      bgColor: 'from-orange-500 to-red-500',
      textColor: 'text-orange-700',
      icon: '📉',
      range: [20, 39]
    },
    'strong sell': {
      label: 'Strong Sell',
      color: '#ef4444',
      bgColor: 'from-red-500 to-red-700', 
      textColor: 'text-red-700',
      icon: '🔻',
      range: [0, 19]
    }
  };
  
  return configs[sentiment.toLowerCase()] || configs['hold'];
};

export default function StockSpeedometer({ 
  recommendation, 
  loading = false, 
  symbol, 
  userProfile, 
  onAnalysisStart, 
  onProfileSetup 
}: StockSpeedometerProps) {
  const [logs, setLogs] = useState<LogMessage[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [animatedScore, setAnimatedScore] = useState(0);
  const [currentRecommendation, setCurrentRecommendation] = useState<StockRecommendation | null>(recommendation);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [progress, setProgress] = useState(0);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (recommendation) {
      setCurrentRecommendation(recommendation);
      const timer = setTimeout(() => {
        setAnimatedScore(recommendation.score);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [recommendation]);

  // Remove auto-scroll to prevent interrupting user reading
  // Users can manually scroll if needed

  // Start real-time analysis with actual backend streaming
  const startAnalysis = async () => {
    if (!userProfile) return;
    
    setIsAnalyzing(true);
    setLogs([]);
    setProgress(0);
    setCurrentStep('Initializing AI Analysis...');

    try {
      const response = await fetch('http://localhost:8000/api/stocks/recommendation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          symbol, 
          userProfile,
          stockData: { currentPrice: 0, sector: 'Unknown' } // Will be filled by backend
        })
      });

      if (!response.body) throw new Error('No response stream');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim().startsWith('data: ')) {
            try {
              const jsonStr = line.replace(/^data:\s*/, '').trim();
              if (jsonStr && jsonStr !== '') {
                console.log('Parsing JSON:', jsonStr); // Debug log
                const data = JSON.parse(jsonStr);
                
                if (data.type === 'log') {
                  setLogs(prev => [...prev, {
                    type: 'log',
                    content: data.content,
                    timestamp: Date.now()
                  }]);
                  setCurrentStep(data.content);
                  setProgress(prev => Math.min(prev + 8, 90));
                } else if (data.type === 'result') {
                  console.log('Received result:', data.content); // Debug log
                  setCurrentRecommendation(data.content);
                  setProgress(100);
                  setCurrentStep('Analysis Complete!');
                  setIsAnalyzing(false);
                  // Animate the score
                  setTimeout(() => {
                    setAnimatedScore(data.content.score || 50);
                  }, 500);
                }
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
              console.error('Problematic line:', line);
              console.error('Extracted JSON string:', line.replace(/^data:\s*/, '').trim());
            }
          }
        }
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      setLogs(prev => [...prev, {
        type: 'error',
        content: 'Analysis failed. Please try again.',
        timestamp: Date.now()
      }]);
      setIsAnalyzing(false);
    }

    if (onAnalysisStart) onAnalysisStart();
  };

  const sentimentConfig = currentRecommendation ? getSentimentConfig(currentRecommendation.sentiment) : getSentimentConfig('hold');
  
  // Investment Recommendation Visualization
  const InvestmentRecommendationCard = () => (
    <div className="relative">
      <motion.div 
        className={`relative bg-gradient-to-br ${sentimentConfig.bgColor} rounded-3xl p-8 text-white shadow-2xl overflow-hidden`}
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.6, type: "spring", bounce: 0.1 }}
      >
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
        <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
        
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <motion.div 
                className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm"
                initial={{ rotate: -180, scale: 0 }}
                animate={{ rotate: 0, scale: 1 }}
                transition={{ delay: 0.3, duration: 0.8, type: "spring", bounce: 0.3 }}
              >
                <span className="text-3xl">{sentimentConfig.icon}</span>
              </motion.div>
              <div>
                <motion.div 
                  className="text-4xl font-bold"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5, duration: 0.5 }}
                >
                  {Math.round(animatedScore)}
                </motion.div>
                <motion.div 
                  className="text-white/80 text-sm"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.7, duration: 0.5 }}
                >
                  Investment Score
                </motion.div>
              </div>
            </div>
            
            <motion.div 
              className="bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 border border-white/30"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.9, duration: 0.4 }}
            >
              <div className="text-sm font-medium text-center">
                <div className="text-lg font-bold">{currentRecommendation?.confidence}%</div>
                <div className="text-xs text-white/80">Confidence</div>
              </div>
            </motion.div>
          </div>

          <motion.div 
            className="mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.1, duration: 0.5 }}
          >
            <h3 className="text-2xl font-bold mb-2">
              {sentimentConfig.label} Recommendation
            </h3>
            <p className="text-white/90 leading-relaxed">
              Based on comprehensive AI analysis, this stock shows {sentimentConfig.label.toLowerCase()} potential 
              with a confidence level of {currentRecommendation?.confidence}% for your investment profile.
            </p>
          </motion.div>

          <motion.div 
            className="space-y-3"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.3, duration: 0.5 }}
          >
            <div className="flex justify-between text-sm text-white/80">
              <span>Risk Level</span>
              <span>{Math.round(animatedScore)}% Match</span>
            </div>
            <div className="w-full bg-white/20 rounded-full h-3 overflow-hidden">
              <motion.div
                className="h-full bg-white/40 rounded-full backdrop-blur-sm"
                initial={{ width: 0 }}
                animate={{ width: `${animatedScore}%` }}
                transition={{ delay: 1.5, duration: 1.5, ease: "easeOut" }}
              />
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );

  // Premium Modern Initial State
  if (!currentRecommendation && !isAnalyzing) {
    return (
      <motion.div 
        className="relative overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Gradient Background with Animated Orbs */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 rounded-3xl"></div>
        <div className="absolute top-0 left-0 w-72 h-72 bg-blue-500/20 rounded-full -translate-x-36 -translate-y-36 animate-pulse"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full translate-x-48 translate-y-48 animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-gradient-to-r from-blue-400/10 to-purple-400/10 rounded-full -translate-x-32 -translate-y-32 animate-spin" style={{ animationDuration: '20s' }}></div>

        <div className="relative z-10 p-12">
          {/* Premium Header */}
          <div className="text-center mb-12">
            <motion.div
              className="inline-flex items-center space-x-3 mb-6"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <div className="w-16 h-16 bg-gradient-to-r from-blue-400 to-purple-500 rounded-2xl flex items-center justify-center shadow-2xl">
                <span className="text-3xl">🧠</span>
              </div>
              <div className="text-left">
                <h1 className="text-4xl font-bold text-white bg-gradient-to-r from-blue-200 to-purple-200 bg-clip-text text-transparent">
                  AI Investment Analysis
                </h1>
                <p className="text-blue-200 text-lg font-medium">Powered by Advanced Machine Learning</p>
              </div>
            </motion.div>

            <motion.p 
              className="text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
            >
              Get personalized investment recommendations based on real-time market analysis, 
              fundamental research, and your risk profile using cutting-edge AI technology.
            </motion.p>
          </div>

          {/* Feature Grid */}
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
          >
            {[
              { icon: '📊', title: 'Real-time Analysis', desc: 'Live market data processing' },
              { icon: '🎯', title: 'Personalized Insights', desc: 'Tailored to your risk profile' },
              { icon: '⚡', title: 'AI-Powered Research', desc: 'Advanced machine learning models' }
            ].map((feature, index) => (
              <motion.div
                key={index}
                className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 + index * 0.1, duration: 0.5 }}
                whileHover={{ scale: 1.02, y: -2 }}
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-white font-bold text-lg mb-2">{feature.title}</h3>
                <p className="text-slate-300 text-sm">{feature.desc}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* Action Button */}
          <motion.div 
            className="text-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1.1, duration: 0.5 }}
          >
            {userProfile ? (
              <motion.button
                onClick={startAnalysis}
                className="group relative inline-flex items-center justify-center px-12 py-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl text-white font-bold text-xl shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 overflow-hidden"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="relative flex items-center space-x-4">
                  <span className="text-3xl">🚀</span>
                  <div className="text-left">
                    <div>Start AI Analysis</div>
                    <div className="text-sm text-blue-200 font-normal">Analyze {symbol} stock</div>
                  </div>
                </div>
                
                {/* Animated particles */}
                <div className="absolute inset-0 overflow-hidden rounded-2xl">
                  {[...Array(3)].map((_, i) => (
                    <div
                      key={i}
                      className="absolute w-2 h-2 bg-white/30 rounded-full animate-ping"
                      style={{
                        left: `${20 + i * 30}%`,
                        top: `${30 + i * 10}%`,
                        animationDelay: `${i * 0.5}s`,
                        animationDuration: '2s'
                      }}
                    ></div>
                  ))}
                </div>
              </motion.button>
            ) : (
              <motion.button
                onClick={onProfileSetup}
                className="group relative inline-flex items-center justify-center px-12 py-6 bg-gradient-to-r from-amber-500 to-orange-600 rounded-2xl text-white font-bold text-xl shadow-2xl hover:shadow-amber-500/25 transition-all duration-300"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="relative flex items-center space-x-4">
                  <span className="text-3xl">⚙️</span>
                  <div className="text-left">
                    <div>Setup Profile First</div>
                    <div className="text-sm text-amber-200 font-normal">Configure your investment preferences</div>
                  </div>
                </div>
              </motion.button>
            )}
          </motion.div>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="space-y-6">
      {isAnalyzing ? (
        <motion.div 
          className="relative overflow-hidden rounded-3xl"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          {/* Premium Analysis Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900"></div>
          <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
          
          {/* Animated Background Effects */}
          <div className="absolute top-0 left-0 w-full h-full overflow-hidden">
            <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/10 rounded-full animate-pulse"></div>
            <div className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-purple-500/10 rounded-full animate-pulse" style={{animationDelay: '1s'}}></div>
            <div className="absolute top-1/2 left-1/2 w-32 h-32 bg-cyan-400/10 rounded-full animate-ping" style={{animationDelay: '2s'}}></div>
          </div>

          <div className="relative z-10 p-8">
            {/* Header with Progress */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-6">
                <motion.div 
                  className="flex items-center space-x-4"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-400 to-purple-500 rounded-2xl flex items-center justify-center shadow-2xl">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    >
                      🧠
                    </motion.div>
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold text-white bg-gradient-to-r from-blue-200 to-purple-200 bg-clip-text text-transparent">
                      AI Analysis Active
                    </h2>
                    <p className="text-blue-200 text-lg">Analyzing {symbol} with advanced ML models</p>
                  </div>
                </motion.div>

                <motion.div 
                  className="flex items-center space-x-4"
                  initial={{ x: 20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  <div className="text-right">
                    <div className="text-3xl font-bold text-white">{Math.round(progress)}%</div>
                    <div className="text-sm text-blue-200">Complete</div>
                  </div>
                  <div className="w-20 h-20 relative">
                    <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="45" stroke="rgba(255,255,255,0.1)" strokeWidth="8" fill="none"/>
                      <motion.circle 
                        cx="50" cy="50" r="45" 
                        stroke="url(#progressGradient)" 
                        strokeWidth="8" 
                        fill="none"
                        strokeLinecap="round"
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: progress / 100 }}
                        transition={{ duration: 0.5 }}
                        style={{
                          strokeDasharray: "283",
                          strokeDashoffset: 283 - (283 * progress) / 100
                        }}
                      />
                      <defs>
                        <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#3B82F6" />
                          <stop offset="100%" stopColor="#8B5CF6" />
                        </linearGradient>
                      </defs>
                    </svg>
                  </div>
                </motion.div>
              </div>

              {/* Current Step Display */}
              <motion.div 
                className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20"
                initial={{ y: 10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.4 }}
              >
                <div className="flex items-center space-x-3">
                  <motion.div
                    className="w-3 h-3 bg-gradient-to-r from-green-400 to-blue-500 rounded-full"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  />
                  <span className="text-white font-medium text-lg">{currentStep}</span>
                </div>
              </motion.div>
            </div>

            {/* Premium Real-time Logs Terminal */}
            <motion.div 
              className="relative"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              {/* Terminal Header */}
              <div className="bg-slate-800/80 backdrop-blur-sm rounded-t-2xl p-4 border border-slate-600/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex space-x-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    </div>
                    <span className="text-slate-300 font-mono text-sm">artha-ai-research-terminal</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <motion.div
                      className="w-2 h-2 bg-green-400 rounded-full"
                      animate={{ opacity: [1, 0.3, 1] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    />
                    <span className="text-green-400 text-sm font-mono">LIVE</span>
                  </div>
                </div>
              </div>

              {/* Terminal Body */}
              <div className="bg-slate-900/90 backdrop-blur-sm rounded-b-2xl border-x border-b border-slate-600/50 overflow-hidden">
                <div className="h-80 overflow-y-auto p-6 space-y-2">
                  {logs.length === 0 ? (
                    <motion.div 
                      className="flex items-center space-x-3 text-slate-400"
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      <span className="font-mono">$</span>
                      <span>Connecting to AI analysis systems...</span>
                      <motion.span
                        animate={{ opacity: [0, 1, 0] }}
                        transition={{ duration: 1, repeat: Infinity }}
                      >
                        ▋
                      </motion.span>
                    </motion.div>
                  ) : (
                    logs.map((log, index) => (
                      <div
                        key={index}
                        className="flex items-start space-x-3"
                      >
                        <span className="text-blue-400 font-mono text-xs flex-shrink-0 mt-1">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                        <div className="flex-1">
                          <div
                            className={`font-mono text-sm leading-relaxed ${
                              log.type === 'error' 
                                ? 'text-red-300' 
                                : 'text-green-300'
                            }`}
                          >
                            {log.content}
                            {index === logs.length - 1 && (
                              <motion.span
                                className="inline-block w-2 h-4 bg-green-400 ml-1"
                                animate={{ opacity: [0, 1, 0] }}
                                transition={{ duration: 1, repeat: Infinity }}
                              />
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </motion.div>

            {/* Real-time Status Info */}
            {logs.length > 0 && (
              <motion.div 
                className="mt-6 bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20"
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.6 }}
              >
                <div className="flex items-center justify-between text-white">
                  <div className="flex items-center space-x-3">
                    <motion.div
                      className="w-3 h-3 bg-green-400 rounded-full"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    />
                    <span className="font-medium">Analysis Progress</span>
                  </div>
                  <div className="text-sm text-slate-300">
                    {logs.length} research steps completed
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>
      ) : currentRecommendation ? (
        <div className="space-y-8">
          <InvestmentRecommendationCard />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Strengths */}
            <motion.div 
              className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-2xl p-6 border border-emerald-100 shadow-sm"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center">
                  <span className="text-white text-lg">✓</span>
                </div>
                <h3 className="text-xl font-bold text-emerald-800">Strengths</h3>
              </div>
              <div className="space-y-3">
                {currentRecommendation.strengths.length > 0 ? (
                  currentRecommendation.strengths.map((strength, index) => (
                    <motion.div 
                      key={index} 
                      className="flex items-start space-x-3 p-3 bg-white/60 rounded-xl border border-emerald-100/50"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 + index * 0.1 }}
                    >
                      <div className="w-6 h-6 bg-emerald-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-white text-xs">+</span>
                      </div>
                      <div className="text-emerald-800 text-sm leading-relaxed prose prose-sm prose-emerald max-w-none">
                        <ReactMarkdown 
                          components={{
                            p: ({children}) => <span>{children}</span>,
                            strong: ({children}) => <strong className="font-bold text-emerald-900">{children}</strong>
                          }}
                        >
                          {strength}
                        </ReactMarkdown>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <p className="text-emerald-600 text-sm italic">No specific strengths identified</p>
                )}
              </div>
            </motion.div>

            {/* Concerns */}
            <motion.div 
              className="bg-gradient-to-br from-red-50 to-rose-50 rounded-2xl p-6 border border-red-100 shadow-sm"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-red-500 rounded-xl flex items-center justify-center">
                  <span className="text-white text-lg">!</span>
                </div>
                <h3 className="text-xl font-bold text-red-800">Concerns</h3>
              </div>
              <div className="space-y-3">
                {currentRecommendation.weaknesses.length > 0 ? (
                  currentRecommendation.weaknesses.map((weakness, index) => (
                    <motion.div 
                      key={index} 
                      className="flex items-start space-x-3 p-3 bg-white/60 rounded-xl border border-red-100/50"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 + index * 0.1 }}
                    >
                      <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-white text-xs">-</span>
                      </div>
                      <div className="text-red-800 text-sm leading-relaxed prose prose-sm prose-red max-w-none">
                        <ReactMarkdown 
                          components={{
                            p: ({children}) => <span>{children}</span>,
                            strong: ({children}) => <strong className="font-bold text-red-900">{children}</strong>
                          }}
                        >
                          {weakness}
                        </ReactMarkdown>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <p className="text-red-600 text-sm italic">No major concerns identified</p>
                )}
              </div>
            </motion.div>
          </div>

          {/* Key Considerations */}
          {currentRecommendation.considerations.length > 0 && (
            <motion.div 
              className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-2xl p-6 border border-amber-100 shadow-sm"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-amber-500 rounded-xl flex items-center justify-center">
                  <span className="text-white text-lg">💡</span>
                </div>
                <h3 className="text-xl font-bold text-amber-800">Key Considerations</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {currentRecommendation.considerations.map((consideration, index) => (
                  <motion.div 
                    key={index} 
                    className="flex items-start space-x-3 p-3 bg-white/60 rounded-xl border border-amber-100/50"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7 + index * 0.1 }}
                  >
                    <div className="w-6 h-6 bg-amber-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-white text-xs">i</span>
                    </div>
                    <div className="text-amber-800 text-sm leading-relaxed prose prose-sm prose-amber max-w-none">
                      <ReactMarkdown 
                        components={{
                          p: ({children}) => <span>{children}</span>,
                          strong: ({children}) => <strong className="font-bold text-amber-900">{children}</strong>
                        }}
                      >
                        {consideration}
                      </ReactMarkdown>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      ) : null}
    </div>
  );
}