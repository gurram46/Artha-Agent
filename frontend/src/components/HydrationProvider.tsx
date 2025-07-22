'use client';

import { useEffect, useState } from 'react';

interface HydrationProviderProps {
  children: React.ReactNode;
}

export default function HydrationProvider({ children }: HydrationProviderProps) {
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    // This ensures the component has mounted on the client side
    setIsHydrated(true);
  }, []);

  // During SSR or before hydration, render with suppressHydrationWarning
  if (!isHydrated) {
    return (
      <div suppressHydrationWarning>
        {children}
      </div>
    );
  }

  // After hydration, render normally
  return <>{children}</>;
}