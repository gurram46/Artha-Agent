'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

interface InvestmentForm {
  investmentAmount: number;
  investmentGoal: string;
  timeHorizon: string;
  riskTolerance: string;
  investmentExperience: string;
  monthlyInvestment: number;
  preferredAssets: string[];
}

interface InvestmentRecommendation {
  strategies: any[];
  recommended_strategy: any;
  execution_plan: any;
  risk_assessment: any;
  angel_one_links: any;
}

interface InvestmentRecommendationAgentProps {
  onClose?: () => void;
}

export default function InvestmentRecommendationAgent({ onClose }: InvestmentRecommendationAgentProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [formData, setFormData] = useState<InvestmentForm>({
    investmentAmount: 50000,
    investmentGoal: '',
    timeHorizon: '',
    riskTolerance: '',
    investmentExperience: '',
    monthlyInvestment: 5000,
    preferredAssets: []
  });
  const [recommendation, setRecommendation] = useState<InvestmentRecommendation | null>(null);
  const [financialData, setFinancialData] = useState<any>(null);

  // Detect demo mode
  useEffect(() => {
    const demoMode = sessionStorage.getItem('demoMode') === 'true';
    setIsDemoMode(demoMode);
  }, []);

  const investmentGoals = [
    { id: 'wealth_creation', label: '💰 Wealth Creation', desc: 'Long-term wealth building' },
    { id: 'retirement', label: '🏖️ Retirement Planning', desc: 'Secure your future' },
    { id: 'child_education', label: '🎓 Child Education', desc: 'Fund education expenses' },
    { id: 'home_purchase', label: '🏠 Home Purchase', desc: 'Save for dream home' },
    { id: 'emergency_fund', label: '🛡️ Emergency Fund', desc: 'Financial safety net' },
    { id: 'tax_saving', label: '🏛️ Tax Saving', desc: 'Reduce tax liability' }
  ];

  const timeHorizons = [
    { id: '1_year', label: '1 Year', desc: 'Short-term goals' },
    { id: '1_3_years', label: '1-3 Years', desc: 'Medium-term planning' },
    { id: '3_5_years', label: '3-5 Years', desc: 'Medium to long-term' },
    { id: '5_10_years', label: '5-10 Years', desc: 'Long-term wealth' },
    { id: '10_plus_years', label: '10+ Years', desc: 'Ultra long-term' }
  ];

  const riskProfiles = [
    { id: 'conservative', label: '🛡️ Conservative', desc: 'Minimal risk, stable returns', allocation: 'Debt 70%, Equity 30%' },
    { id: 'moderate', label: '⚖️ Moderate', desc: 'Balanced risk-return', allocation: 'Debt 40%, Equity 60%' },
    { id: 'aggressive', label: '🚀 Aggressive', desc: 'High risk, high returns', allocation: 'Debt 20%, Equity 80%' }
  ];

  const experienceLevels = [
    { id: 'beginner', label: '🌱 Beginner', desc: 'New to investing' },
    { id: 'intermediate', label: '📈 Intermediate', desc: 'Some experience' },
    { id: 'advanced', label: '🎯 Advanced', desc: 'Experienced investor' }
  ];

  const assetTypes = [
    { id: 'mutual_funds', label: '📊 Mutual Funds', desc: 'Diversified portfolios' },
    { id: 'stocks', label: '📈 Direct Stocks', desc: 'Individual companies' },
    { id: 'etfs', label: '🏪 ETFs', desc: 'Exchange traded funds' },
    { id: 'bonds', label: '🏛️ Bonds/Debt', desc: 'Fixed income securities' },
    { id: 'gold', label: '🥇 Gold ETF', desc: 'Precious metals' },
    { id: 'elss', label: '💸 ELSS', desc: 'Tax-saving funds' }
  ];

  const handleAssetToggle = (assetId: string) => {
    setFormData(prev => ({
      ...prev,
      preferredAssets: prev.preferredAssets.includes(assetId)
        ? prev.preferredAssets.filter(id => id !== assetId)
        : [...prev.preferredAssets, assetId]
    }));
  };

  const analyzeInvestment = async () => {
    setIsAnalyzing(true);
    try {
      // First get the investment recommendation using Fi Money data (real or demo)
      const response = await fetch(`http://localhost:8003/api/investment-recommendations?demo=${isDemoMode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        setFinancialData(data.investment_recommendations.user_data);
        
        // Now send user preferences to get personalized recommendation
        const personalizedResponse = await fetch('http://localhost:8003/api/investment-recommendations/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: `Create personalized investment plan:
            - Investment Amount: ₹${formData.investmentAmount.toLocaleString()}
            - Monthly SIP: ₹${formData.monthlyInvestment.toLocaleString()}
            - Goal: ${formData.investmentGoal}
            - Time Horizon: ${formData.timeHorizon}
            - Risk Tolerance: ${formData.riskTolerance}
            - Experience: ${formData.investmentExperience}
            - Preferred Assets: ${formData.preferredAssets.join(', ')}
            
            Provide specific product recommendations with current NAV/prices and Angel Broking investment links.`,
            mode: 'research',
            demo_mode: isDemoMode
          })
        });

        const personalizedData = await personalizedResponse.json();
        
        if (personalizedData.status === 'success') {
          // Parse the response to create structured recommendation
          setRecommendation({
            strategies: [data.investment_recommendations],
            recommended_strategy: {
              name: `${formData.riskTolerance} Investment Strategy`,
              allocation: formData.preferredAssets,
              amount: formData.investmentAmount,
              sip_amount: formData.monthlyInvestment
            },
            execution_plan: personalizedData.response,
            risk_assessment: data.investment_recommendations.key_insights,
            angel_one_links: {
              mutual_funds: "https://web.angelone.in/mutualfunds",
              stocks: "https://web.angelone.in/",
              sip: "https://web.angelone.in/mutualfunds/sip"
            }
          });
          setCurrentStep(6); // Show results
        }
      }
    } catch (error) {
      console.error('Investment analysis failed:', error);
      alert('Failed to analyze investment. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const openAngelBroking = (investmentType: string) => {
    const links = {
      mutual_funds: "https://web.angelone.in/mutualfunds",
      stocks: "https://web.angelone.in/",
      sip: "https://web.angelone.in/mutualfunds/sip",
      elss: "https://web.angelone.in/mutualfunds/tax-saver"
    };
    
    window.open(links[investmentType as keyof typeof links] || links.mutual_funds, '_blank');
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-xl font-bold text-gray-900 mb-2">💰 Investment Amount</h3>
              <p className="text-gray-600">How much would you like to invest?</p>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Lump Sum Investment</label>
                <input
                  type="number"
                  value={formData.investmentAmount}
                  onChange={(e) => setFormData(prev => ({ ...prev, investmentAmount: Number(e.target.value) }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                  placeholder="50000"
                />
                <p className="text-sm text-gray-500 mt-1">Minimum: ₹10,000</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Monthly SIP Amount</label>
                <input
                  type="number"
                  value={formData.monthlyInvestment}
                  onChange={(e) => setFormData(prev => ({ ...prev, monthlyInvestment: Number(e.target.value) }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                  placeholder="5000"
                />
                <p className="text-sm text-gray-500 mt-1">Minimum: ₹1,000</p>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-xl font-bold text-gray-900 mb-2">🎯 Investment Goal</h3>
              <p className="text-gray-600">What's your primary investment objective?</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {investmentGoals.map((goal) => (
                <button
                  key={goal.id}
                  onClick={() => setFormData(prev => ({ ...prev, investmentGoal: goal.id }))}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    formData.investmentGoal === goal.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-lg font-medium">{goal.label}</div>
                  <div className="text-sm text-gray-600">{goal.desc}</div>
                </button>
              ))}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-xl font-bold text-gray-900 mb-2">⏰ Time Horizon</h3>
              <p className="text-gray-600">When do you need the money?</p>
            </div>
            
            <div className="space-y-3">
              {timeHorizons.map((horizon) => (
                <button
                  key={horizon.id}
                  onClick={() => setFormData(prev => ({ ...prev, timeHorizon: horizon.id }))}
                  className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                    formData.timeHorizon === horizon.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">{horizon.label}</div>
                      <div className="text-sm text-gray-600">{horizon.desc}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-xl font-bold text-gray-900 mb-2">⚖️ Risk Tolerance</h3>
              <p className="text-gray-600">How comfortable are you with market volatility?</p>
            </div>
            
            <div className="space-y-4">
              {riskProfiles.map((risk) => (
                <button
                  key={risk.id}
                  onClick={() => setFormData(prev => ({ ...prev, riskTolerance: risk.id }))}
                  className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                    formData.riskTolerance === risk.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">{risk.label}</div>
                      <div className="text-sm text-gray-600">{risk.desc}</div>
                    </div>
                    <div className="text-sm text-blue-600 font-medium">{risk.allocation}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-xl font-bold text-gray-900 mb-2">📚 Investment Experience</h3>
              <p className="text-gray-600">What's your investment experience level?</p>
            </div>
            
            <div className="space-y-3">
              {experienceLevels.map((level) => (
                <button
                  key={level.id}
                  onClick={() => setFormData(prev => ({ ...prev, investmentExperience: level.id }))}
                  className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                    formData.investmentExperience === level.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium">{level.label}</div>
                  <div className="text-sm text-gray-600">{level.desc}</div>
                </button>
              ))}
            </div>

            <div className="mt-8">
              <h4 className="font-medium text-gray-900 mb-4">🎯 Preferred Investment Types (Select Multiple)</h4>
              <div className="grid grid-cols-2 gap-3">
                {assetTypes.map((asset) => (
                  <button
                    key={asset.id}
                    onClick={() => handleAssetToggle(asset.id)}
                    className={`p-3 rounded-lg border-2 transition-all text-left ${
                      formData.preferredAssets.includes(asset.id)
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-sm font-medium">{asset.label}</div>
                    <div className="text-xs text-gray-600">{asset.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        );

      case 6:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-xl font-bold text-gray-900 mb-2">📈 Your Investment Plan</h3>
              <p className="text-gray-600">Personalized recommendations based on your profile</p>
            </div>

            {recommendation && (
              <div className="space-y-6">
                {/* Investment Summary */}
                <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
                  <h4 className="font-bold text-lg mb-4">💰 Investment Summary</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Lump Sum</p>
                      <p className="font-bold text-xl">₹{formData.investmentAmount.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Monthly SIP</p>
                      <p className="font-bold text-xl">₹{formData.monthlyInvestment.toLocaleString()}</p>
                    </div>
                  </div>
                </div>

                {/* AI Recommendations */}
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h4 className="font-bold text-lg mb-4">🤖 AI Investment Recommendations</h4>
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{recommendation.execution_plan}</ReactMarkdown>
                  </div>
                </div>

                {/* Direct Investment Buttons */}
                <div className="bg-orange-50 rounded-lg p-6">
                  <h4 className="font-bold text-lg mb-4">🚀 Invest Now via Angel Broking</h4>
                  <p className="text-sm text-gray-600 mb-4">Click to open Angel Broking and start investing immediately</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button
                      onClick={() => openAngelBroking('mutual_funds')}
                      className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-medium"
                    >
                      📊 Invest in Mutual Funds
                    </button>
                    
                    <button
                      onClick={() => openAngelBroking('sip')}
                      className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-4 rounded-lg hover:from-green-700 hover:to-green-800 transition-all font-medium"
                    >
                      💰 Start SIP
                    </button>
                    
                    <button
                      onClick={() => openAngelBroking('stocks')}
                      className="bg-gradient-to-r from-purple-600 to-purple-700 text-white px-6 py-4 rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all font-medium"
                    >
                      📈 Buy Stocks
                    </button>
                    
                    <button
                      onClick={() => openAngelBroking('elss')}
                      className="bg-gradient-to-r from-orange-600 to-orange-700 text-white px-6 py-4 rounded-lg hover:from-orange-700 hover:to-orange-800 transition-all font-medium"
                    >
                      🏛️ Tax Saving (ELSS)
                    </button>
                  </div>
                </div>

                {/* Financial Context */}
                {financialData && (
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h4 className="font-bold text-lg mb-4">📊 Your Financial Profile (Fi Money Data)</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Total Net Worth</p>
                        <p className="font-bold">₹{financialData.total_net_worth?.toLocaleString() || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Investment Capacity</p>
                        <p className="font-bold">₹{financialData.investment_metrics?.recommended_investment_amount?.toLocaleString() || 'N/A'}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1: return formData.investmentAmount >= 10000 && formData.monthlyInvestment >= 1000;
      case 2: return formData.investmentGoal !== '';
      case 3: return formData.timeHorizon !== '';
      case 4: return formData.riskTolerance !== '';
      case 5: return formData.investmentExperience !== '' && formData.preferredAssets.length > 0;
      default: return false;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white p-6 rounded-t-2xl">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">📈 Investment Recommendation Agent</h2>
              <p className="text-green-100 mt-1">
                Step {currentStep} of 5 • Powered by Fi Money + Sandeep-Artha AI
              </p>
            </div>
            <button 
              onClick={onClose}
              className="text-white hover:text-gray-200 text-3xl font-bold transition-colors"
            >
              ×
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="bg-gray-200 h-2">
          <div 
            className="bg-gradient-to-r from-green-600 to-blue-600 h-2 transition-all duration-300"
            style={{ width: `${(currentStep / 5) * 100}%` }}
          />
        </div>

        {/* Content */}
        <div className="p-6">
          {isAnalyzing ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">🔍 Analyzing Your Investment Profile</h3>
              <p className="text-gray-600">Using real Fi Money data + AI investment system...</p>
              <div className="mt-4 space-y-2 text-sm text-gray-500">
                <p>• Fetching your financial data from Fi Money MCP</p>
                <p>• Running multi-agent investment analysis</p>
                <p>• Generating personalized recommendations</p>
                <p>• Preparing Angel Broking integration</p>
              </div>
            </div>
          ) : (
            <>
              {renderStep()}
              
              {/* Navigation */}
              <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
                <button
                  onClick={() => setCurrentStep(prev => prev - 1)}
                  disabled={currentStep === 1}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  ← Previous
                </button>
                
                {currentStep < 5 ? (
                  <button
                    onClick={() => setCurrentStep(prev => prev + 1)}
                    disabled={!canProceed()}
                    className="px-6 py-2 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg hover:from-green-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    Next →
                  </button>
                ) : (
                  <button
                    onClick={analyzeInvestment}
                    disabled={!canProceed()}
                    className="px-8 py-2 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg hover:from-green-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
                  >
                    🚀 Get Investment Plan
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}