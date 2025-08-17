'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Smartphone, WifiOff, Lightbulb, Brain, Shield, Copy, Zap, Database, Clock } from 'lucide-react';
import FiMoneyWebAuth from './FiMoneyWebAuth';
import ReactMarkdown from 'react-markdown';

interface LocalLLMInsightsProps {
  className?: string;
}

interface CompressedData {
  nw: string;
  assets: Record<string, string>;
  debt?: string;
  credit?: string;
  investments: Array<{ v: string; r?: string }>;
  risk: string;
  liquidity: string;
  insights: string[];
}

interface MetricCardProps {
  title: string;
  value: string;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
}

const MetricCard = ({ title, value, subtitle, icon, color }: MetricCardProps) => (
  <div className="bg-[rgb(24,25,27)] border border-[rgba(34,197,94,0.2)] rounded-3xl p-6 group hover:border-[rgba(34,197,94,0.5)] transition-all duration-300 shadow-xl hover:shadow-2xl">
    <div className="flex items-center justify-between mb-4">
      <div>
        <p className="text-sm font-semibold text-gray-300 mb-1">{title}</p>
        <p className="text-xs text-gray-400 font-medium">{subtitle}</p>
      </div>
      <div className={`w-12 h-12 ${color} rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110`}>
        {icon}
      </div>
    </div>
    <div className="space-y-3">
      <h3 className="text-3xl font-bold text-white tracking-tight">{value}</h3>
    </div>
  </div>
);

export default function LocalLLMInsights({ className = '' }: LocalLLMInsightsProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [compressedData, setCompressedData] = useState<CompressedData | null>(null);
  const [prompt, setPrompt] = useState('');
  const [metadata, setMetadata] = useState<any>(null);
  const [error, setError] = useState('');
  const [userQuery, setUserQuery] = useState('Give me financial insights');
  const [showLocalPrompt, setShowLocalPrompt] = useState(false);
  const [localLLMInsights, setLocalLLMInsights] = useState<string>('');
  const [isLLMAvailable, setIsLLMAvailable] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication status and demo mode on component mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      const demoMode = sessionStorage.getItem('demoMode') === 'true';
      setIsDemoMode(demoMode);
      
      // If in demo mode, consider as authenticated
      if (demoMode) {
        setIsAuthenticated(true);
      } else {
        // Check if user is authenticated with real Fi Money account
        try {
          const MCPDataService = (await import('../services/mcpDataService')).default;
          const mcpService = MCPDataService.getInstance();
          const status = await mcpService.checkAuthenticationStatus();
          setIsAuthenticated(status.authenticated);
        } catch (error) {
          console.error('Error checking auth status:', error);
          setIsAuthenticated(false);
        }
      }
    };

    checkAuthStatus();
    
    // Listen for storage changes (if user switches between demo/real mode)
    const handleStorageChange = () => {
      checkAuthStatus();
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const handleGetLocalInsights = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      // Check if we're in demo mode by checking session storage
      const demoMode = sessionStorage.getItem('demoMode') === 'true';
      setIsDemoMode(demoMode);
      
      const response = await fetch('http://localhost:8000/api/local-llm/prepare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: userQuery,
          demo_mode: demoMode 
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setCompressedData(data.compressed_data);
        setPrompt(data.prompt);
        setMetadata(data.metadata);
        
        // Check if local LLM provided insights
        if (data.local_llm && data.local_llm.available) {
          setLocalLLMInsights(data.local_llm.insights);
          setIsLLMAvailable(true);
        } else {
          setIsLLMAvailable(false);
          if (data.local_llm && data.local_llm.message) {
            setError(data.local_llm.message);
          }
        }
        setShowLocalPrompt(true);
      } else {
        setError(data.message || 'Failed to prepare data');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleAuthError = (error: string) => {
    setError(error);
  };

  // Show authentication UI if not authenticated
  if (!isAuthenticated) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="bg-[rgb(24,25,27)] border border-[rgba(34,197,94,0.2)] rounded-3xl shadow-xl p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Local LLM Insights</h1>
              <p className="text-gray-600 font-medium mt-1">
                Connect your data source to start analyzing with local AI
              </p>
            </div>
          </div>
        </div>
        
        <FiMoneyWebAuth 
          onAuthSuccess={handleAuthSuccess}
          onAuthError={handleAuthError}
        />
        
        {error && (
          <div className="bg-[rgb(24,25,27)] border border-[rgba(34,197,94,0.2)] rounded-3xl shadow-xl p-4 bg-[rgba(220,53,69,0.05)] border border-[rgba(220,53,69,0.3)]">
            <div className="flex items-center gap-2">
              <WifiOff className="w-5 h-5 text-red-600" />
              <p className="text-sm font-medium text-red-700">{error}</p>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Header Section */}
      <div className="bg-[rgb(24,25,27)] border border-[rgba(34,197,94,0.2)] rounded-3xl shadow-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Local LLM Insights</h1>
              <p className="text-gray-600 font-medium mt-1">
                Process your financial data locally with complete privacy
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-[#cca695]/10 text-[#cca695] rounded-full border border-[#cca695]/20">
            <Shield className="w-4 h-4" />
            <span className="text-sm font-semibold">100% Private</span>
          </div>
        </div>

        {/* Query Input */}
        <div className="space-y-3">
          <label className="text-sm font-semibold text-gray-700">
            What would you like to know about your portfolio?
          </label>
          <div className="flex gap-3">
            <input
              type="text"
              value={userQuery}
              onChange={(e) => setUserQuery(e.target.value)}
              placeholder="E.g., What's my risk profile? How's my portfolio allocation?"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl bg-white focus:ring-2 focus:ring-purple-500 focus:border-transparent font-medium"
            />
            <button
              onClick={handleGetLocalInsights}
              disabled={isLoading}
              className="btn-primary flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 disabled:opacity-50 font-semibold"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                  Processing...
                </>
              ) : (
                <>
                  <Lightbulb className="w-4 h-4" />
                  Get Insights
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Benefits Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          title="Privacy First"
          value="100%"
          subtitle="Data stays on device"
          icon={<Shield className="w-5 h-5 text-white" />}
          color="bg-gradient-to-br from-[#cca695] to-[#b8956a]"
        />
        <MetricCard
          title="Ultra Fast"
          value="< 2s"
          subtitle="Local processing"
          icon={<Zap className="w-5 h-5 text-white" />}
          color="bg-gradient-to-br from-blue-500 to-blue-600"
        />
        <MetricCard
          title="Compressed"
          value="< 2K"
          subtitle="Token efficient"
          icon={<Database className="w-5 h-5 text-white" />}
          color="bg-gradient-to-br from-purple-500 to-purple-600"
        />
        <MetricCard
          title="Mobile Ready"
          value="Works"
          subtitle="Any device"
          icon={<Smartphone className="w-5 h-5 text-white" />}
          color="bg-gradient-to-br from-orange-500 to-orange-600"
        />
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl shadow-xl p-4 bg-[rgba(220,53,69,0.05)] border border-[rgba(220,53,69,0.3)]">
          <div className="flex items-center gap-2">
            <WifiOff className="w-5 h-5 text-red-600" />
            <p className="text-sm font-medium text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Local LLM Insights Display */}
      {localLLMInsights && (
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl shadow-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">AI Analysis</h3>
                <p className="text-sm font-medium text-gray-700">Generated locally by Gemma 3N E2B</p>
              </div>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-purple-100 text-purple-700 rounded-full border border-purple-200">
              <Clock className="w-4 h-4" />
              <span className="text-xs font-semibold">Real-time</span>
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
            <div className="prose prose-gray max-w-none text-white leading-relaxed">
              <ReactMarkdown 
                components={{
                  h2: ({node, ...props}) => <h2 className="text-xl font-bold text-white mt-6 mb-3 border-b border-gray-200 pb-2" {...props} />,
                  h3: ({node, ...props}) => <h3 className="text-lg font-semibold text-gray-800 mt-4 mb-2" {...props} />,
                  p: ({node, ...props}) => <p className="text-gray-700 mb-3 leading-relaxed" {...props} />,
                  ul: ({node, ...props}) => <ul className="list-disc list-inside space-y-1 mb-3 text-gray-700" {...props} />,
                  li: ({node, ...props}) => <li className="text-gray-700" {...props} />,
                  strong: ({node, ...props}) => <strong className="font-semibold text-white" {...props} />,
                  code: ({node, ...props}) => <code className="bg-gray-200 px-1 py-0.5 rounded text-sm font-mono" {...props} />
                }}
              >
                {localLLMInsights}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      )}

      {/* Compressed Data Display */}
      {compressedData && (
        <div className="space-y-6">
          {/* Financial Snapshot Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <MetricCard
              title="Net Worth"
              value={`₹${compressedData.nw}`}
              subtitle="Total portfolio value"
              icon={<Brain className="w-5 h-5 text-white" />}
              color="bg-gradient-to-br from-green-500 to-green-600"
            />
            {compressedData.debt && (
              <MetricCard
                title="Total Debt"
                value={`₹${compressedData.debt}`}
                subtitle="Outstanding liabilities"
                icon={<WifiOff className="w-5 h-5 text-white" />}
                color="bg-gradient-to-br from-red-500 to-red-600"
              />
            )}
            {compressedData.credit && (
              <MetricCard
                title="Credit Score"
                value={compressedData.credit}
                subtitle="Financial health"
                icon={<Shield className="w-5 h-5 text-white" />}
                color="bg-gradient-to-br from-blue-500 to-blue-600"
              />
            )}
            <MetricCard
              title="Risk Level"
              value={compressedData.risk}
              subtitle="Portfolio risk"
              icon={<Zap className="w-5 h-5 text-white" />}
              color="bg-gradient-to-br from-purple-500 to-purple-600"
            />
          </div>

          {/* Assets and Investments */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Assets Breakdown */}
            {Object.keys(compressedData.assets).length > 0 && (
              <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl shadow-xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-white">Asset Allocation</h3>
                  <span className="text-sm text-gray-500">Breakdown by type</span>
                </div>
                <div className="space-y-3">
                  {Object.entries(compressedData.assets).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
                      <span className="font-medium text-gray-700">{key}</span>
                      <span className="font-semibold text-white">₹{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Top Investments */}
            {compressedData.investments.length > 0 && (
              <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl shadow-xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-white">Top Holdings</h3>
                  <span className="text-sm text-gray-500">{compressedData.investments.length} investments</span>
                </div>
                <div className="space-y-3">
                  {compressedData.investments.map((inv, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
                      <span className="font-medium text-white">₹{inv.v}</span>
                      {inv.r && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-700">
                          {inv.r}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Metadata and Controls */}
          <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl shadow-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Compression Analytics</h3>
              {metadata && (
                <div className="flex gap-4 text-sm text-gray-600">
                  <span>~{metadata.estimated_tokens} tokens</span>
                  <span>{metadata.compression_ratio}x compressed</span>
                  <span>{metadata.data_points} data points</span>
                </div>
              )}
            </div>
            
            {/* Show Prompt Button */}
            <div className="space-y-4">
              <button
                onClick={() => setShowLocalPrompt(!showLocalPrompt)}
                className="btn-secondary w-full flex items-center justify-center gap-2 py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium"
              >
                <Copy className="w-4 h-4" />
                {showLocalPrompt ? 'Hide' : 'Show'} LLM Prompt
              </button>
              
              {showLocalPrompt && (
                <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-xs">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-400">LLM Prompt ({prompt.length} chars)</span>
                    <button
                      onClick={() => copyToClipboard(prompt)}
                      className="text-blue-400 hover:text-blue-300 font-medium"
                    >
                      Copy
                    </button>
                  </div>
                  <pre className="whitespace-pre-wrap">{prompt}</pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* LLM Status */}
      {!isLoading && !isLLMAvailable && (
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl shadow-xl p-4 bg-[rgba(255,193,7,0.05)] border border-[rgba(255,193,7,0.3)]">
          <div className="flex items-center gap-3">
            <WifiOff className="w-5 h-5 text-yellow-600" />
            <div>
              <p className="text-sm font-medium text-yellow-800">Local LLM Unavailable</p>
              <p className="text-xs text-yellow-700 mt-1">
                Make sure LM Studio is running on port 1234 for AI insights
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Info Note */}
      <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl shadow-xl p-4 bg-[rgba(0,184,153,0.05)] border border-[rgba(0,184,153,0.3)]">
        <div className="flex items-start gap-3">
          <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-800">Privacy Guaranteed</p>
            <p className="text-xs text-blue-700 mt-1">
              Your financial data is compressed and processed locally. No data is sent to external servers.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}