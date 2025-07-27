'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface InvestmentRecommendationCardProps {
  financialData: any;
}

export default function InvestmentRecommendationCard({ financialData }: InvestmentRecommendationCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [brokerPlan, setBrokerPlan] = useState<any>(null);
  const [selectedBroker, setSelectedBroker] = useState('groww');
  const [formData, setFormData] = useState({
    investmentAmount: 50000,
    riskTolerance: 'moderate',
    investmentGoal: 'wealth_creation',
    timeHorizon: 'long_term',
    monthlyInvestment: 5000
  });

  const handleGetRecommendation = async () => {
    setIsAnalyzing(true);
    try {
      const response = await fetch('http://localhost:8003/api/investment-recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        // Get personalized recommendation based on form data
        const chatResponse = await fetch('http://localhost:8003/api/investment-recommendations/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: `Create investment plan for ₹${formData.investmentAmount.toLocaleString()} with ${formData.riskTolerance} risk tolerance, ${formData.investmentGoal} goal, ${formData.timeHorizon} horizon, ₹${formData.monthlyInvestment.toLocaleString()} monthly SIP. Provide specific mutual funds, stocks, and platform recommendations.`,
            mode: 'research'
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
      console.error('Investment analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const openInvestmentPlatform = (platform: string) => {
    const platforms = {
      angel_one: 'https://web.angelone.in',
      zerodha: 'https://zerodha.com',
      groww: 'https://groww.in',
      paytm_money: 'https://www.paytmmoney.com'
    };
    window.open(platforms[platform as keyof typeof platforms] || platforms.angel_one, '_blank');
  };

  const generateBrokerPlan = async () => {
    if (!recommendation?.personalized_plan) return;
    
    try {
      const response = await fetch('/api/investment-recommendations/broker-plan', {
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
      const response = await fetch('/api/investment-recommendations/execute', {
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
            <h3 className="text-xl font-bold text-white mb-1">📈 Investment Preferences</h3>
            <p className="text-sm text-gray-300">Tell us about your investment goals</p>
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
                Analyzing with AI...
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
            <h3 className="text-xl font-bold text-white mb-1">🎯 Your Investment Plan</h3>
            <p className="text-sm text-gray-300">AI-powered recommendations using real Fi Money data</p>
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

          {/* Enhanced Invest Now Feature */}
          {recommendation?.investment_analysis?.invest_now_urls && (
            <div className="bg-gradient-to-br from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.05)] border border-[rgba(0,184,153,0.3)] rounded-2xl p-6 mb-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-full flex items-center justify-center">
                  <span className="text-2xl">🚀</span>
                </div>
                <div>
                  <h4 className="text-white font-bold text-xl">Invest Now</h4>
                  <p className="text-gray-300 text-sm">Execute your investment plan immediately</p>
                </div>
              </div>
              
              {/* Broker Selection Grid */}
              <div className="mb-6">
                <h5 className="text-white font-semibold text-lg mb-4">Choose Your Broker</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[
                    { id: 'angel_one', name: 'Angel One', emoji: '📈', desc: 'API Integration & Real-time Data', color: 'from-orange-500 to-orange-600', features: ['Live Prices', 'Basket Orders', 'Research'] },
                    { id: 'zerodha', name: 'Zerodha Kite', emoji: '🔷', desc: 'Advanced Trading Platform', color: 'from-blue-500 to-blue-600', features: ['Low Brokerage', 'Kite Platform', 'Education'] },
                    { id: 'groww', name: 'Groww', emoji: '🌱', desc: 'Beginner-Friendly', color: 'from-green-500 to-green-600', features: ['Simple UI', 'Zero AMC', 'Goal Based'] },
                    { id: 'upstox', name: 'Upstox', emoji: '⚡', desc: 'Professional Tools', color: 'from-purple-500 to-purple-600', features: ['Pro Platform', 'Research', 'Charts'] },
                    { id: 'paytm_money', name: 'Paytm Money', emoji: '💰', desc: 'Digital-First Experience', color: 'from-indigo-500 to-indigo-600', features: ['Zero Delivery', 'Digital KYC', 'UPI'] },
                    { id: 'iifl', name: 'IIFL Securities', emoji: '🏛️', desc: 'Full-Service Broker', color: 'from-gray-500 to-gray-600', features: ['Advisory', 'Research', 'Wealth Mgmt'] }
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

              {/* Investment Summary Preview */}
              {recommendation?.investment_analysis?.actionable_investments && (
                <div className="bg-[rgba(255,255,255,0.05)] rounded-xl p-4 mb-6">
                  <h5 className="text-white font-semibold text-sm mb-3">📊 Investment Summary</h5>
                  <div className="space-y-2">
                    {recommendation.investment_analysis.actionable_investments.slice(0, 3).map((investment: any, index: number) => (
                      <div key={index} className="flex justify-between items-center text-sm">
                        <span className="text-gray-300">{investment.name}</span>
                        <span className="text-[rgb(0,184,153)] font-semibold">₹{investment.amount?.toLocaleString()}</span>
                      </div>
                    ))}
                    {recommendation.investment_analysis.actionable_investments.length > 3 && (
                      <div className="text-gray-400 text-xs">
                        +{recommendation.investment_analysis.actionable_investments.length - 3} more investments
                      </div>
                    )}
                  </div>
                </div>
              )}

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
                    <h5 className="text-white font-semibold">Ready to Invest</h5>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                      <div className="text-[rgb(0,184,153)] font-bold text-lg">{brokerPlan.execution_plan?.broker || 'Selected Broker'}</div>
                      <div className="text-gray-400 text-xs">Broker</div>
                    </div>
                    <div>
                      <div className="text-[rgb(0,184,153)] font-bold text-lg">{brokerPlan.execution_plan?.total_investments || '0'}</div>
                      <div className="text-gray-400 text-xs">Investments</div>
                    </div>
                    <div>
                      <div className="text-[rgb(0,184,153)] font-bold text-lg">
                        {brokerPlan.execution_plan?.real_time_data ? '🟢 Live' : '🟡 Static'}
                      </div>
                      <div className="text-gray-400 text-xs">Data</div>
                    </div>
                    <div>
                      <div className="text-[rgb(0,184,153)] font-bold text-lg">
                        ₹{Math.round(brokerPlan.investment_summary?.reduce((sum: number, inv: string) => {
                          const match = inv.match(/₹([0-9,]+)/);
                          return sum + (match ? parseInt(match[1].replace(/,/g, '')) : 0);
                        }, 0) || 0).toLocaleString()}
                      </div>
                      <div className="text-gray-400 text-xs">Total Amount</div>
                    </div>
                  </div>
                  {brokerPlan.investment_summary && brokerPlan.investment_summary.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-[rgba(255,255,255,0.1)]">
                      <h6 className="text-white text-sm mb-2">Investment Details:</h6>
                      <div className="space-y-1">
                        {brokerPlan.investment_summary.map((investment: string, index: number) => (
                          <div key={index} className="text-gray-300 text-xs flex items-center gap-2">
                            <span className="w-2 h-2 bg-[rgb(0,184,153)] rounded-full"></span>
                            {investment}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Investment Platform Buttons */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
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
              onClick={() => openInvestmentPlatform('paytm_money')}
              className="bg-gradient-to-r from-purple-600 to-purple-700 text-white px-4 py-3 rounded-xl hover:from-purple-700 hover:to-purple-800 transition-all text-sm font-medium"
            >
              💰 Paytm Money
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl group hover:border-[rgba(0,184,153,0.5)] transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-2xl flex items-center justify-center shadow-lg">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Investment Recommendations</h3>
            <p className="text-sm text-gray-300">AI-powered investment strategy</p>
          </div>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <svg className={`w-6 h-6 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-[rgb(0,184,153)]">🤖</p>
            <p className="text-xs text-gray-300 font-medium">AI Analysis</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-[rgb(0,184,153)]">📊</p>
            <p className="text-xs text-gray-300 font-medium">Real Data</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-[rgb(0,184,153)]">🚀</p>
            <p className="text-xs text-gray-300 font-medium">Direct Invest</p>
          </div>
        </div>

        {isExpanded && (
          <div className="space-y-4 border-t border-[rgba(0,184,153,0.2)] pt-4">
            <div className="bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-4">
              <h4 className="text-sm font-bold text-white mb-2">🎯 What You'll Get:</h4>
              <ul className="text-sm text-gray-300 space-y-1">
                <li>• Personalized investment strategies based on your Fi Money data</li>
                <li>• Specific mutual fund and stock recommendations</li>
                <li>• Risk-appropriate portfolio allocation</li>
                <li>• Direct links to invest on Angel One, Zerodha, Groww</li>
                <li>• Tax-efficient investment planning</li>
              </ul>
            </div>

            <button
              onClick={() => setShowForm(true)}
              className="w-full bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white px-6 py-4 rounded-xl hover:from-[rgb(0,164,133)] hover:to-[rgb(0,144,113)] transition-all font-medium flex items-center justify-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              Get Personalized Investment Plan
            </button>
          </div>
        )}
      </div>
    </div>
  );
}