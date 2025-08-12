import React from 'react';
import Image from 'next/image';

interface ArthaLogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export const ArthaLogo: React.FC<ArthaLogoProps> = ({ 
  className = '', 
  size = 'md' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6', 
    lg: 'w-7 h-7',
    xl: 'w-8 h-8'
  };

  return (
    <Image
      src="/artha-logo.svg"
      alt="Artha AI Logo"
      width={24}
      height={24}
      className={`${sizeClasses[size]} ${className}`}
      style={{
        filter: className.includes('text-white') ? 'brightness(0) invert(1)' : 'brightness(0) saturate(100%) invert(48%) sepia(79%) saturate(2476%) hue-rotate(86deg) brightness(118%) contrast(119%)'
      }}
    />
  );
};