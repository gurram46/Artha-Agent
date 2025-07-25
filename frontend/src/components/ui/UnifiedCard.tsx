'use client';

import { ReactNode } from 'react';
import { cardClasses, cn } from '@/styles/designSystem';

interface UnifiedCardProps {
  children: ReactNode;
  className?: string;
  variant?: 'elevated' | 'flat';
  padding?: boolean;
  hover?: boolean;
  onClick?: () => void;
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export const UnifiedCard = ({ 
  children, 
  className = '', 
  variant = 'flat',
  padding = true,
  hover = true,
  onClick
}: UnifiedCardProps) => {
  return (
    <div 
      className={cn(
        cardClasses(variant),
        padding && 'p-6',
        hover && 'hover:shadow-md',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className = '' }: CardHeaderProps) => {
  return (
    <div className={cn('pb-4 border-b border-slate-100', className)}>
      {children}
    </div>
  );
};

export const CardContent = ({ children, className = '' }: CardContentProps) => {
  return (
    <div className={cn('pt-4', className)}>
      {children}
    </div>
  );
};

export default UnifiedCard;