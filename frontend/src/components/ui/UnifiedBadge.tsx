'use client';

import { ReactNode } from 'react';
import { badgeClasses, cn } from '@/styles/designSystem';

interface UnifiedBadgeProps {
  children: ReactNode;
  variant?: 'blue' | 'green' | 'yellow' | 'red' | 'gray';
  className?: string;
}

export const UnifiedBadge = ({ 
  children, 
  variant = 'blue', 
  className = '' 
}: UnifiedBadgeProps) => {
  return (
    <span className={cn(badgeClasses(variant), className)}>
      {children}
    </span>
  );
};

export default UnifiedBadge;