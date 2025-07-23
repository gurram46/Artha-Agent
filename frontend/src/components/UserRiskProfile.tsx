'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface RiskProfile {
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
  investmentHorizon: 'short' | 'medium' | 'long';
  investmentGoal: 'growth' | 'income' | 'balanced';
  monthlyInvestment: number;
}

interface UserRiskProfileProps {
  onProfileUpdate: (profile: RiskProfile) => void;
  initialProfile?: RiskProfile;
}

const riskOptions = [
  {
    id: 'conservative',
    label: 'Conservative',
    description: 'Low risk, stable returns',
    icon: '🛡️',
    color: 'from-green-400 to-green-600',
    textColor: 'text-green-700',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
  },
  {
    id: 'moderate',
    label: 'Moderate',
    description: 'Balanced risk-return',
    icon: '⚖️',
    color: 'from-blue-400 to-blue-600',
    textColor: 'text-blue-700',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
  },
  {
    id: 'aggressive',
    label: 'Aggressive',
    description: 'High risk, high returns',
    icon: '🚀',
    color: 'from-red-400 to-red-600',
    textColor: 'text-red-700',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
  },
];

const horizonOptions = [
  {
    id: 'short',
    label: 'Short-term',
    description: '< 2 years',
    icon: '⚡',
    duration: '< 2 years',
  },
  {
    id: 'medium',
    label: 'Medium-term',
    description: '2-5 years',
    icon: '📈',
    duration: '2-5 years',
  },
  {
    id: 'long',
    label: 'Long-term',
    description: '5+ years',
    icon: '🎯',
    duration: '5+ years',
  },
];

const goalOptions = [
  {
    id: 'growth',
    label: 'Capital Growth',
    description: 'Focus on appreciation',
    icon: '📊',
  },
  {
    id: 'income',
    label: 'Regular Income',
    description: 'Focus on dividends',
    icon: '💰',
  },
  {
    id: 'balanced',
    label: 'Balanced',
    description: 'Growth + Income',
    icon: '🎯',
  },
];

export default function UserRiskProfile({ onProfileUpdate, initialProfile }: UserRiskProfileProps) {
  const [profile, setProfile] = useState<RiskProfile>(
    initialProfile || {
      riskTolerance: 'moderate',
      investmentHorizon: 'medium',
      investmentGoal: 'balanced',
      monthlyInvestment: 10000,
    }
  );

  const [isExpanded, setIsExpanded] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);

  // Use ref to store the latest callback
  const onProfileUpdateRef = useRef(onProfileUpdate);
  onProfileUpdateRef.current = onProfileUpdate;

  useEffect(() => {
    if (!hasLoaded) {
      const savedProfile = localStorage.getItem('userRiskProfile');
      if (savedProfile) {
        const parsed = JSON.parse(savedProfile);
        setProfile(parsed);
        onProfileUpdateRef.current(parsed);
      }
      setHasLoaded(true);
    }
  }, [hasLoaded]);

  const updateProfile = (updates: Partial<RiskProfile>) => {
    const newProfile = { ...profile, ...updates };
    setProfile(newProfile);
    setHasChanges(true);
  };

  const saveProfile = () => {
    localStorage.setItem('userRiskProfile', JSON.stringify(profile));
    onProfileUpdateRef.current(profile);
    setHasChanges(false);
    setIsExpanded(false);
  };

  const getCurrentRiskOption = () => riskOptions.find(opt => opt.id === profile.riskTolerance);
  const currentRisk = getCurrentRiskOption();

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div 
        className="px-6 py-4 border-b border-slate-200 cursor-pointer hover:bg-slate-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`w-12 h-12 rounded-2xl ${currentRisk?.bgColor} ${currentRisk?.borderColor} border-2 flex items-center justify-center`}>
              <span className="text-2xl">{currentRisk?.icon}</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900">Investment Profile</h3>
              <p className="text-sm text-slate-600">
                {currentRisk?.label} • {horizonOptions.find(h => h.id === profile.investmentHorizon)?.duration} • 
                {goalOptions.find(g => g.id === profile.investmentGoal)?.label}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            {hasChanges && (
              <motion.button
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                onClick={(e) => {
                  e.stopPropagation();
                  saveProfile();
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                Save Changes
              </motion.button>
            )}
            <motion.div
              animate={{ rotate: isExpanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="p-6 space-y-8">
              {/* Risk Tolerance */}
              <div>
                <h4 className="text-lg font-semibold text-slate-900 mb-4">Risk Tolerance</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {riskOptions.map((option) => (
                    <motion.div
                      key={option.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => updateProfile({ riskTolerance: option.id as any })}
                      className={`
                        relative p-4 rounded-xl border-2 cursor-pointer transition-all duration-200
                        ${profile.riskTolerance === option.id 
                          ? `${option.borderColor} ${option.bgColor} ring-2 ring-offset-2 ring-blue-500` 
                          : 'border-slate-200 hover:border-slate-300'
                        }
                      `}
                    >
                      <div className="text-center">
                        <div className="text-3xl mb-2">{option.icon}</div>
                        <h5 className={`font-semibold mb-1 ${profile.riskTolerance === option.id ? option.textColor : 'text-slate-900'}`}>
                          {option.label}
                        </h5>
                        <p className="text-sm text-slate-600">{option.description}</p>
                      </div>
                      {profile.riskTolerance === option.id && (
                        <motion.div
                          layoutId="risk-selected"
                          className="absolute -top-2 -right-2 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center"
                        >
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Investment Horizon */}
              <div>
                <h4 className="text-lg font-semibold text-slate-900 mb-4">Investment Horizon</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {horizonOptions.map((option) => (
                    <motion.div
                      key={option.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => updateProfile({ investmentHorizon: option.id as any })}
                      className={`
                        relative p-4 rounded-xl border-2 cursor-pointer transition-all duration-200
                        ${profile.investmentHorizon === option.id 
                          ? 'border-blue-500 bg-blue-50 ring-2 ring-offset-2 ring-blue-500' 
                          : 'border-slate-200 hover:border-slate-300'
                        }
                      `}
                    >
                      <div className="text-center">
                        <div className="text-3xl mb-2">{option.icon}</div>
                        <h5 className={`font-semibold mb-1 ${profile.investmentHorizon === option.id ? 'text-blue-700' : 'text-slate-900'}`}>
                          {option.label}
                        </h5>
                        <p className="text-sm text-slate-600">{option.duration}</p>
                      </div>
                      {profile.investmentHorizon === option.id && (
                        <motion.div
                          layoutId="horizon-selected"
                          className="absolute -top-2 -right-2 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center"
                        >
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Investment Goal */}
              <div>
                <h4 className="text-lg font-semibold text-slate-900 mb-4">Investment Goal</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {goalOptions.map((option) => (
                    <motion.div
                      key={option.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => updateProfile({ investmentGoal: option.id as any })}
                      className={`
                        relative p-4 rounded-xl border-2 cursor-pointer transition-all duration-200
                        ${profile.investmentGoal === option.id 
                          ? 'border-blue-500 bg-blue-50 ring-2 ring-offset-2 ring-blue-500' 
                          : 'border-slate-200 hover:border-slate-300'
                        }
                      `}
                    >
                      <div className="text-center">
                        <div className="text-3xl mb-2">{option.icon}</div>
                        <h5 className={`font-semibold mb-1 ${profile.investmentGoal === option.id ? 'text-blue-700' : 'text-slate-900'}`}>
                          {option.label}
                        </h5>
                        <p className="text-sm text-slate-600">{option.description}</p>
                      </div>
                      {profile.investmentGoal === option.id && (
                        <motion.div
                          layoutId="goal-selected"
                          className="absolute -top-2 -right-2 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center"
                        >
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Monthly Investment */}
              <div>
                <h4 className="text-lg font-semibold text-slate-900 mb-4">Monthly Investment Budget</h4>
                <div className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <span className="text-sm font-medium text-slate-700 min-w-0">₹1,000</span>
                    <div className="flex-1">
                      <input
                        type="range"
                        min="1000"
                        max="100000"
                        step="1000"
                        value={profile.monthlyInvestment}
                        onChange={(e) => updateProfile({ monthlyInvestment: parseInt(e.target.value) })}
                        className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer slider"
                      />
                    </div>
                    <span className="text-sm font-medium text-slate-700 min-w-0">₹1,00,000</span>
                  </div>
                  <div className="text-center">
                    <span className="text-2xl font-bold text-blue-600">
                      ₹{profile.monthlyInvestment.toLocaleString('en-IN')}
                    </span>
                    <span className="text-sm text-slate-600 ml-2">per month</span>
                  </div>
                </div>
              </div>

              {/* Save Button */}
              <div className="flex justify-end pt-4 border-t border-slate-200">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={saveProfile}
                  disabled={!hasChanges}
                  className={`
                    px-6 py-3 rounded-lg font-medium transition-all duration-200
                    ${hasChanges 
                      ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg' 
                      : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                    }
                  `}
                >
                  {hasChanges ? 'Save Profile' : 'Profile Saved'}
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3b82f6;
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .slider::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3b82f6;
          cursor: pointer;
          border: none;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
      `}</style>
    </div>
  );
}