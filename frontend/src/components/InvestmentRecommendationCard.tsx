'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

interface InvestmentRecommendationCardProps {
  financialData: any;
}

export default function InvestmentRecommendationCard({ financialData }: InvestmentRecommendationCardProps) {
  const [showForm, setShowForm] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [brokerPlan, setBrokerPlan] = useState<any>(null);
  const [selectedBroker, setSelectedBroker] = useState('groww');
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [formData, setFormData] = useState({
    investmentAmount: 50000,
    riskTolerance: 'moderate',
    investmentGoal: 'wealth_creation',
    timeHorizon: 'long_term',
    monthlyInvestment: 5000
  });

  // Detect demo mode
  useEffect(() => {
    const demoMode = sessionStorage.getItem('demoMode') === 'true';
    setIsDemoMode(demoMode);
  }, []);

  const handleGetRecommendation = async () => {
    setIsAnalyzing(true);
    try {
      // Call AI Investment System API endpoint
      const response = await fetch(`http://localhost:8003/api/ai-investment-recommendations?demo=${isDemoMode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          investment_amount: formData.investmentAmount,
          risk_tolerance: formData.riskTolerance,
          investment_goal: formData.investmentGoal,
          time_horizon: formData.timeHorizon,
          monthly_investment: formData.monthlyInvestment
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        // Get personalized recommendation using AI chat system
        const chatResponse = await fetch('http://localhost:8003/api/ai-investment-recommendations/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: `Create investment plan for ₹${formData.investmentAmount.toLocaleString()} with ${formData.riskTolerance} risk tolerance, ${formData.investmentGoal} goal, ${formData.timeHorizon} horizon, ₹${formData.monthlyInvestment.toLocaleString()} monthly SIP. Use our multi-agent AI analysis to provide specific Indian stocks, mutual funds, and platform recommendations.`,
            mode: 'comprehensive'
          })
        });

        const chatData = await chatResponse.json();
        if (chatData.status === 'success') {
          setRecommendation({
            analysis: data.investment_recommendations,
            personalized_plan: chatData.response
          });
          setShowForm(false);
        }
      }
    } catch (error) {
      console.error('AI Investment analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const openInvestmentPlatform = (platform: string) => {
    const platforms = {
      angel_one: 'https://trade.angelone.in/',
      zerodha: 'https://kite.zerodha.com/',
      groww: 'https://groww.in/',
      upstox: 'https://upstox.com/',
      iifl: 'https://www.iiflsecurities.com/',
      paytm_money: 'https://www.paytmmoney.com'
    };
    window.open(platforms[platform as keyof typeof platforms] || platforms.angel_one, '_blank');
  };

  const generateBrokerPlan = async () => {
    if (!recommendation?.personalized_plan) return;
    
    try {
      const response = await fetch('/api/ai-investment-recommendations/broker-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recommendation_text: recommendation.personalized_plan,
          preferred_broker: selectedBroker
        }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        setBrokerPlan(data.broker_plan);
      } else {
        console.error('Failed to generate broker plan:', data);
      }
    } catch (error) {
      console.error('Error generating broker plan:', error);
    }
  };

  const executeInvestments = async () => {
    if (!brokerPlan) return;
    
    try {
      const response = await fetch('/api/ai-investment-recommendations/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          broker_plan: brokerPlan.execution_plan
        }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        // Investment platforms opened in browser
        alert('Investment platforms opened! Please complete your investments in the opened tabs.');
      } else {
        console.error('Failed to execute investments:', data);
      }
    } catch (error) {
      console.error('Error executing investments:', error);
    }
  };

  if (showForm) {
    return (
      <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold text-white mb-1">📈 Investment Agent</h3>
            <p className="text-sm text-gray-300">Multi-Agent AI System</p>
          </div>
          <button
            onClick={() => setShowForm(false)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-6">
          {/* Investment Amount */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Lump Sum Investment</label>
              <input
                type="number"
                value={formData.investmentAmount}
                onChange={(e) => setFormData({...formData, investmentAmount: Number(e.target.value)})}
                className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(0,184,153,0.2)] rounded-xl text-white focus:ring-2 focus:ring-[rgb(0,184,153)] focus:border-transparent"
                placeholder="50000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Monthly SIP</label>
              <input
                type="number"
                value={formData.monthlyInvestment}
                onChange={(e) => setFormData({...formData, monthlyInvestment: Number(e.target.value)})}
                className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(0,184,153,0.2)] rounded-xl text-white focus:ring-2 focus:ring-[rgb(0,184,153)] focus:border-transparent"
                placeholder="5000"
              />
            </div>
          </div>

          {/* Risk Tolerance */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">Risk Tolerance</label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'conservative', label: '🛡️ Conservative', desc: 'Low risk' },
                { value: 'moderate', label: '⚖️ Moderate', desc: 'Balanced' },
                { value: 'aggressive', label: '🚀 Aggressive', desc: 'High growth' }
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => setFormData({...formData, riskTolerance: option.value})}
                  className={`p-3 rounded-xl border-2 transition-all text-left ${
                    formData.riskTolerance === option.value
                      ? 'border-[rgb(0,184,153)] bg-[rgba(0,184,153,0.1)]'
                      : 'border-[rgba(0,184,153,0.2)] hover:border-[rgba(0,184,153,0.4)]'
                  }`}
                >
                  <div className="text-sm font-medium text-white">{option.label}</div>
                  <div className="text-xs text-gray-400">{option.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Investment Goal */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Investment Goal</label>
              <select
                value={formData.investmentGoal}
                onChange={(e) => setFormData({...formData, investmentGoal: e.target.value})}
                className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(0,184,153,0.2)] rounded-xl text-white focus:ring-2 focus:ring-[rgb(0,184,153)] focus:border-transparent"
              >
                <option value="wealth_creation">💰 Wealth Creation</option>
                <option value="retirement">🏖️ Retirement</option>
                <option value="education">🎓 Education</option>
                <option value="home_purchase">🏠 Home Purchase</option>
                <option value="tax_saving">🏛️ Tax Saving</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Time Horizon</label>
              <select
                value={formData.timeHorizon}
                onChange={(e) => setFormData({...formData, timeHorizon: e.target.value})}
                className="w-full px-4 py-3 bg-[rgb(30,31,33)] border border-[rgba(0,184,153,0.2)] rounded-xl text-white focus:ring-2 focus:ring-[rgb(0,184,153)] focus:border-transparent"
              >
                <option value="short_term">📅 1-3 Years</option>
                <option value="medium_term">📆 3-7 Years</option>
                <option value="long_term">🗓️ 7+ Years</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleGetRecommendation}
            disabled={isAnalyzing}
            className="w-full bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white px-6 py-4 rounded-xl hover:from-[rgb(0,164,133)] hover:to-[rgb(0,144,113)] transition-all disabled:opacity-50 font-medium flex items-center justify-center"
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-3"></div>
                AI Analyzing...
              </>
            ) : (
              '🤖 Get AI Investment Plan'
            )}
          </button>
        </div>
      </div>
    );
  }

  if (recommendation) {
    return (
      <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold text-white mb-1">🎯 AI Investment Plan</h3>
            <p className="text-sm text-gray-300">Multi-Agent AI Analysis Complete</p>
          </div>
          <button
            onClick={() => {
              setRecommendation(null);
              setShowForm(true);
            }}
            className="text-gray-400 hover:text-white transition-colors text-sm"
          >
            📝 Modify
          </button>
        </div>

        <div className="space-y-6">
          {/* Investment Summary */}
          <div className="bg-gradient-to-r from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.1)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-300">Lump Sum</p>
                <p className="text-lg font-bold text-white">₹{formData.investmentAmount.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-300">Monthly SIP</p>
                <p className="text-lg font-bold text-white">₹{formData.monthlyInvestment.toLocaleString()}</p>
              </div>
            </div>
          </div>

          {/* AI Recommendations */}
          <div className="max-h-64 overflow-y-auto">
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p className="text-gray-300 mb-2 last:mb-0">{children}</p>,
                  strong: ({ children }) => <strong className="text-white font-bold">{children}</strong>,
                  ul: ({ children }) => <ul className="text-gray-300 list-disc pl-4 mb-2">{children}</ul>,
                  li: ({ children }) => <li className="text-gray-300 mb-1">{children}</li>,
                  h3: ({ children }) => <h3 className="text-white font-bold text-base mb-2">{children}</h3>,
                  h4: ({ children }) => <h4 className="text-white font-bold text-sm mb-1">{children}</h4>,
                }}
              >
                {recommendation.personalized_plan}
              </ReactMarkdown>
            </div>
          </div>

          {/* Multi-Broker Integration */}
          <div className="bg-gradient-to-br from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.05)] border border-[rgba(0,184,153,0.3)] rounded-2xl p-6 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-full flex items-center justify-center">
                <span className="text-2xl">🚀</span>
              </div>
              <div>
                <h4 className="text-white font-bold text-xl">Invest Now</h4>
                <p className="text-gray-300 text-sm">Execute via 6 major Indian brokers</p>
              </div>
            </div>
            
            {/* Broker Selection Grid */}
            <div className="mb-6">
              <h5 className="text-white font-semibold text-lg mb-4">Choose Your Broker</h5>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { id: 'angel_one', name: 'Angel One', emoji: '📈', desc: 'Zero brokerage delivery', color: 'from-orange-500 to-orange-600', features: ['Zero Delivery', 'Real-time Data', 'Research'] },
                  { id: 'zerodha', name: 'Zerodha Kite', emoji: '🔷', desc: 'Advanced trading platform', color: 'from-blue-500 to-blue-600', features: ['Kite Platform', 'Low Brokerage', 'Education'] },
                  { id: 'groww', name: 'Groww', emoji: '🌱', desc: 'Beginner-friendly', color: 'from-green-500 to-green-600', features: ['Simple UI', 'Zero AMC', 'Goal Based'] },
                  { id: 'upstox', name: 'Upstox', emoji: '⚡', desc: 'Professional tools', color: 'from-purple-500 to-purple-600', features: ['Pro Platform', 'Research', 'Charts'] },
                  { id: 'iifl', name: 'IIFL Securities', emoji: '🏛️', desc: 'Full-service broker', color: 'from-indigo-500 to-indigo-600', features: ['Advisory', 'Research', 'Wealth Mgmt'] },
                  { id: 'paytm_money', name: 'Paytm Money', emoji: '💰', desc: 'Digital-first experience', color: 'from-gray-500 to-gray-600', features: ['Zero Delivery', 'Digital KYC', 'UPI'] }
                ].map((broker) => (
                  <div
                    key={broker.id}
                    onClick={() => setSelectedBroker(broker.id)}
                    className={`relative p-4 rounded-xl border-2 cursor-pointer transition-all hover:scale-105 ${
                      selectedBroker === broker.id
                        ? 'border-[rgb(0,184,153)] bg-[rgba(0,184,153,0.1)] shadow-lg shadow-[rgba(0,184,153,0.3)]'
                        : 'border-[rgba(255,255,255,0.1)] hover:border-[rgba(0,184,153,0.5)] bg-[rgba(255,255,255,0.02)]'
                    }`}
                  >
                    {selectedBroker === broker.id && (
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-[rgb(0,184,153)] rounded-full flex items-center justify-center">
                        <span className="text-white text-xs">✓</span>
                      </div>
                    )}
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`w-10 h-10 bg-gradient-to-r ${broker.color} rounded-lg flex items-center justify-center`}>
                        <span className="text-xl">{broker.emoji}</span>
                      </div>
                      <div>
                        <h6 className="text-white font-semibold text-sm">{broker.name}</h6>
                        <p className="text-gray-400 text-xs">{broker.desc}</p>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {broker.features.map((feature, idx) => (
                        <span key={idx} className="px-2 py-1 bg-[rgba(255,255,255,0.1)] rounded-full text-xs text-gray-300">
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={generateBrokerPlan}
                disabled={!selectedBroker}
                className="flex-1 bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white px-6 py-4 rounded-xl hover:from-[rgb(0,164,133)] hover:to-[rgb(0,144,113)] transition-all font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <span>📋</span>
                Generate Investment URLs
              </button>
              {brokerPlan && (
                <button
                  onClick={executeInvestments}
                  className="flex-1 bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-4 rounded-xl hover:from-green-700 hover:to-green-800 transition-all font-semibold text-sm flex items-center justify-center gap-2 shadow-lg"
                >
                  <span>🚀</span>
                  Execute Now
                </button>
              )}
            </div>

            {/* Enhanced Broker Plan Details */}
            {brokerPlan && (
              <div className="mt-6 p-4 bg-[rgba(0,0,0,0.3)] rounded-xl border border-[rgba(255,255,255,0.1)]">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-lg">✅</span>
                  <h5 className="text-white font-semibold">Investment Ready</h5>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                  <div>
                    <div className="text-[rgb(0,184,153)] font-bold text-lg">{brokerPlan.execution_plan?.broker || selectedBroker}</div>
                    <div className="text-gray-400 text-xs">Selected Broker</div>
                  </div>
                  <div>
                    <div className="text-[rgb(0,184,153)] font-bold text-lg">{brokerPlan.execution_plan?.total_investments || '6+'}</div>
                    <div className="text-gray-400 text-xs">Investments</div>
                  </div>
                  <div>
                    <div className="text-[rgb(0,184,153)] font-bold text-lg">
                      {brokerPlan.execution_plan?.real_time_data ? '🟢 Live' : '🟡 Static'}
                    </div>
                    <div className="text-gray-400 text-xs">Market Data</div>
                  </div>
                  <div>
                    <div className="text-[rgb(0,184,153)] font-bold text-lg">
                      ₹{formData.investmentAmount.toLocaleString()}
                    </div>
                    <div className="text-gray-400 text-xs">Total Amount</div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Investment Platform Buttons */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            <button
              onClick={() => openInvestmentPlatform('angel_one')}
              className="bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white px-4 py-3 rounded-xl hover:from-[rgb(0,164,133)] hover:to-[rgb(0,144,113)] transition-all text-sm font-medium"
            >
              📈 Angel One
            </button>
            <button
              onClick={() => openInvestmentPlatform('zerodha')}
              className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-3 rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all text-sm font-medium"
            >
              🔷 Zerodha
            </button>
            <button
              onClick={() => openInvestmentPlatform('groww')}
              className="bg-gradient-to-r from-green-600 to-green-700 text-white px-4 py-3 rounded-xl hover:from-green-700 hover:to-green-800 transition-all text-sm font-medium"
            >
              🌱 Groww
            </button>
            <button
              onClick={() => openInvestmentPlatform('upstox')}
              className="bg-gradient-to-r from-purple-600 to-purple-700 text-white px-4 py-3 rounded-xl hover:from-purple-700 hover:to-purple-800 transition-all text-sm font-medium"
            >
              ⚡ Upstox
            </button>
            <button
              onClick={() => openInvestmentPlatform('iifl')}
              className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white px-4 py-3 rounded-xl hover:from-indigo-700 hover:to-indigo-800 transition-all text-sm font-medium"
            >
              🏛️ IIFL
            </button>
            <button
              onClick={() => openInvestmentPlatform('paytm_money')}
              className="bg-gradient-to-r from-gray-600 to-gray-700 text-white px-4 py-3 rounded-xl hover:from-gray-700 hover:to-gray-800 transition-all text-sm font-medium"
            >
              💰 Paytm Money
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-xl p-4 shadow-lg group hover:border-[rgba(0,184,153,0.5)] transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-lg flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div>
            <h3 className="text-md font-semibold text-white">Investment Recommendations</h3>
            <p className="text-xs text-gray-400">Multi-Agent AI System</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-xl font-bold text-[rgb(0,184,153)]">🤖</p>
            <p className="text-xs text-gray-300 font-medium">4-Agent AI</p>
          </div>
          <div className="text-center">
            <p className="text-xl font-bold text-[rgb(0,184,153)]">📊</p>
            <p className="text-xs text-gray-300 font-medium">Real Data</p>
          </div>
          <div className="text-center">
            <p className="text-xl font-bold text-[rgb(0,184,153)]">🚀</p>
            <p className="text-xs text-gray-300 font-medium">6 Brokers</p>
          </div>
        </div>

        <div className="space-y-4 border-t border-[rgba(0,184,153,0.2)] pt-4">
          <div className="bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-xl p-3">
            <h4 className="text-xs font-bold text-white mb-2">🎯 AI Features:</h4>
            <ul className="text-xs text-gray-300 space-y-1">
              <li>• Multi-agent analysis (Data, Trading, Execution, Risk)</li>
              <li>• Specific Indian stocks, ETFs, and mutual fund recommendations</li>
              <li>• Risk-appropriate portfolio allocation with tax optimization</li>
              <li>• Direct links to 6 major brokers (Angel One, Zerodha, Groww)</li>
              <li>• Real-time market data integration via Angel One API</li>
            </ul>
          </div>

          <button
            onClick={() => setShowForm(true)}
            className="w-full bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white px-4 py-3 rounded-lg hover:from-[rgb(0,164,133)] hover:to-[rgb(0,144,113)] transition-all text-sm font-medium flex items-center justify-center"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            Get AI Investment Plan
          </button>
        </div>
      </div>
    </div>
  );
}