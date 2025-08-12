'use client';

import { ReactNode } from 'react';
import UnifiedCard from './UnifiedCard';
import { cn } from '@/styles/designSystem';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  trend?: {
    value: string;
    type: 'positive' | 'negative' | 'neutral';
  };
  className?: string;
  onClick?: () => void;
}

export const StatCard = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  className = '',
  onClick
}: StatCardProps) => {
  const getTrendClasses = (type: 'positive' | 'negative' | 'neutral') => {
    switch (type) {
      case 'positive':
        return 'bg-[rgba(34,197,94,0.1)] text-[rgb(34,197,94)] border-[rgba(34,197,94,0.2)]';
      case 'negative':
        return 'bg-[rgba(220,53,69,0.1)] text-red-400 border-[rgba(220,53,69,0.2)]';
      default:
        return 'bg-[rgba(70,68,68,0.3)] text-gray-300 border-[rgba(70,68,68,0.5)]';
    }
  };

  const getTrendIcon = (type: 'positive' | 'negative' | 'neutral') => {
    switch (type) {
      case 'positive':
        return (
          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        );
      case 'negative':
        return (
          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <UnifiedCard 
      className={cn('group hover:shadow-lg transition-all duration-300', onClick && 'cursor-pointer', className)}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {icon && (
            <div className="w-10 h-10 bg-[rgba(34,197,94,0.1)] rounded-lg flex items-center justify-center text-[rgb(34,197,94)] group-hover:bg-[rgba(34,197,94,0.2)] transition-colors">
              {icon}
            </div>
          )}
          <div>
            <p className="text-sm font-medium text-gray-300">{title}</p>
            {subtitle && (
              <p className="text-xs text-gray-400">{subtitle}</p>
            )}
          </div>
        </div>
        
        {trend && (
          <span className={cn(
            'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border',
            getTrendClasses(trend.type)
          )}>
            {getTrendIcon(trend.type)}
            {trend.value}
          </span>
        )}
      </div>
      
      <div className="space-y-1">
        <p className="text-2xl font-bold text-white group-hover:text-[rgb(34,197,94)] transition-colors">
          {value}
        </p>
      </div>
    </UnifiedCard>
  );
};

export default StatCard;