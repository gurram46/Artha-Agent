'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion } from 'framer-motion';

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
    color: 'from-[#cca695] to-[#b8956a]',
    textColor: 'text-[#cca695]',
    bgColor: 'bg-[#cca695]/10',
    borderColor: 'border-[#cca695]/20',
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
    icon: 'Lightning',
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
    icon: 'Target',
    duration: '5+ years',
  },
];

const goalOptions = [
  {
    id: 'growth',
    label: 'Capital Growth',
    description: 'Focus on appreciation',
    icon: 'Chart',
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
    icon: 'Target',
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
    <div className="bg-[rgb(24,25,27)] rounded-xl border border-[rgba(34,197,94,0.2)] shadow-lg">
      {/* Always Visible Header */}
      <div className="px-4 py-3 border-b border-[rgba(34,197,94,0.2)]">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-[rgb(34,197,94)] to-[rgb(22,163,74)] rounded-lg flex items-center justify-center">
              <span className="text-lg">⚖️</span>
            </div>
            <div>
              <h3 className="text-md font-semibold text-white">Investment Profile</h3>
              <p className="text-xs text-gray-400">
                {currentRisk?.label} • {horizonOptions.find(h => h.id === profile.investmentHorizon)?.duration} • 
                {goalOptions.find(g => g.id === profile.investmentGoal)?.label}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {hasChanges && (
              <motion.button
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                onClick={saveProfile}
                className="px-3 py-1 bg-[rgb(34,197,94)] text-white rounded-md text-xs font-medium hover:bg-[rgb(22,163,74)] transition-colors"
              >
                Save
              </motion.button>
            )}
          </div>
        </div>
      </div>

      {/* Always Expanded Content */}
      <div className="p-4 space-y-5">
              {/* Compact Risk Tolerance */}
              <div>
                <h4 className="text-md font-semibold text-white mb-3">Risk Tolerance</h4>
                <div className="grid grid-cols-3 gap-2">
                  {riskOptions.map((option) => (
                    <motion.div
                      key={option.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => updateProfile({ riskTolerance: option.id as any })}
                      className={`
                        relative p-3 rounded-lg border cursor-pointer transition-all duration-200
                        ${profile.riskTolerance === option.id 
                          ? 'border-[rgb(34,197,94)] bg-[rgba(34,197,94,0.1)]' 
                          : 'border-gray-600 hover:border-gray-500'
                        }
                      `}
                    >
                      <div className="text-center">
                        <div className="text-xl mb-1">{option.icon}</div>
                        <h5 className={`text-xs font-medium mb-1 ${profile.riskTolerance === option.id ? 'text-[rgb(34,197,94)]' : 'text-white'}`}>
                          {option.label}
                        </h5>
                        <p className="text-xs text-gray-500">{option.description}</p>
                      </div>
                      {profile.riskTolerance === option.id && (
                        <motion.div
                          layoutId="risk-selected"
                          className="absolute -top-1 -right-1 w-4 h-4 bg-[rgb(34,197,94)] rounded-full flex items-center justify-center"
                        >
                          <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Compact Investment Horizon */}
              <div>
                <h4 className="text-md font-semibold text-white mb-3">Investment Horizon</h4>
                <div className="grid grid-cols-3 gap-2">
                  {horizonOptions.map((option) => (
                    <motion.div
                      key={option.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => updateProfile({ investmentHorizon: option.id as any })}
                      className={`
                        relative p-3 rounded-lg border cursor-pointer transition-all duration-200
                        ${profile.investmentHorizon === option.id 
                          ? 'border-[rgb(34,197,94)] bg-[rgba(34,197,94,0.1)]' 
                          : 'border-gray-600 hover:border-gray-500'
                        }
                      `}
                    >
                      <div className="text-center">
                        <div className="text-xl mb-1">{option.icon}</div>
                        <h5 className={`text-xs font-medium mb-1 ${profile.investmentHorizon === option.id ? 'text-[rgb(34,197,94)]' : 'text-white'}`}>
                          {option.label}
                        </h5>
                        <p className="text-xs text-gray-500">{option.duration}</p>
                      </div>
                      {profile.investmentHorizon === option.id && (
                        <motion.div
                          layoutId="horizon-selected"
                          className="absolute -top-1 -right-1 w-4 h-4 bg-[rgb(34,197,94)] rounded-full flex items-center justify-center"
                        >
                          <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Compact Investment Goal */}
              <div>
                <h4 className="text-md font-semibold text-white mb-3">Investment Goal</h4>
                <div className="grid grid-cols-3 gap-2">
                  {goalOptions.map((option) => (
                    <motion.div
                      key={option.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => updateProfile({ investmentGoal: option.id as any })}
                      className={`
                        relative p-3 rounded-lg border cursor-pointer transition-all duration-200
                        ${profile.investmentGoal === option.id 
                          ? 'border-[rgb(34,197,94)] bg-[rgba(34,197,94,0.1)]' 
                          : 'border-gray-600 hover:border-gray-500'
                        }
                      `}
                    >
                      <div className="text-center">
                        <div className="text-xl mb-1">{option.icon}</div>
                        <h5 className={`text-xs font-medium mb-1 ${profile.investmentGoal === option.id ? 'text-[rgb(34,197,94)]' : 'text-white'}`}>
                          {option.label}
                        </h5>
                        <p className="text-xs text-gray-500">{option.description}</p>
                      </div>
                      {profile.investmentGoal === option.id && (
                        <motion.div
                          layoutId="goal-selected"
                          className="absolute -top-1 -right-1 w-4 h-4 bg-[rgb(34,197,94)] rounded-full flex items-center justify-center"
                        >
                          <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Compact Monthly Investment */}
              <div>
                <h4 className="text-md font-semibold text-white mb-3">Monthly Budget</h4>
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <span className="text-xs text-gray-400">₹1K</span>
                    <div className="flex-1">
                      <input
                        type="range"
                        min="1000"
                        max="100000"
                        step="1000"
                        value={profile.monthlyInvestment}
                        onChange={(e) => updateProfile({ monthlyInvestment: parseInt(e.target.value) })}
                        className="w-full h-2 bg-[rgba(34,197,94,0.2)] rounded-lg appearance-none cursor-pointer"
                        style={{
                          WebkitAppearance: 'none',
                          MozAppearance: 'none',
                        }}
                      />
                    </div>
                    <span className="text-xs text-gray-400">₹1L</span>
                  </div>
                  <div className="text-center">
                    <span className="text-lg font-bold text-[rgb(34,197,94)]">
                      ₹{profile.monthlyInvestment.toLocaleString('en-IN')}
                    </span>
                    <span className="text-xs text-gray-400 ml-1">per month</span>
                  </div>
                </div>
              </div>

              {/* Compact Save Button */}
              <div className="flex justify-end pt-3 border-t border-gray-700">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={saveProfile}
                  disabled={!hasChanges}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                    ${hasChanges 
                      ? 'bg-[rgb(34,197,94)] text-white hover:bg-[rgb(22,163,74)]' 
                      : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    }
                  `}
                >
                  {hasChanges ? 'Save' : 'Saved'}
                </motion.button>
              </div>
      </div>

    </div>
  );
}