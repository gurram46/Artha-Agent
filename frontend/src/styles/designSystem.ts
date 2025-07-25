// Unified Design System for Artha Wealth Intelligence

export const designSystem = {
  // Color Palette
  colors: {
    // Primary Brand Colors
    primary: {
      50: '#f0f9ff',
      100: '#e0f2fe', 
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
      900: '#0c4a6e'
    },
    
    // Secondary Colors
    secondary: {
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      500: '#64748b',
      600: '#475569',
      700: '#334155',
      900: '#0f172a'
    },
    
    // Accent Colors
    accent: {
      emerald: '#10b981',
      purple: '#8b5cf6',
      orange: '#f59e0b',
      red: '#ef4444'
    },
    
    // Status Colors
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#0ea5e9'
  },

  // Typography
  typography: {
    fontFamily: {
      primary: 'Inter, system-ui, sans-serif',
      mono: 'JetBrains Mono, monospace'
    },
    
    fontSize: {
      xs: '0.75rem',      // 12px
      sm: '0.875rem',     // 14px
      base: '1rem',       // 16px
      lg: '1.125rem',     // 18px
      xl: '1.25rem',      // 20px
      '2xl': '1.5rem',    // 24px
      '3xl': '1.875rem',  // 30px
      '4xl': '2.25rem'    // 36px
    },
    
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700'
    },
    
    // Heading styles
    heading: {
      xlarge: 'text-3xl font-bold text-slate-900',
      large: 'text-2xl font-bold text-slate-900',
      medium: 'text-xl font-bold text-slate-900',
      small: 'text-lg font-semibold text-slate-900'
    },
    
    // Body text styles
    body: {
      large: 'text-lg text-slate-600',
      default: 'text-base text-slate-600',
      small: 'text-sm text-slate-600'
    }
  },

  // Spacing Scale
  spacing: {
    xs: '0.5rem',     // 8px
    sm: '0.75rem',    // 12px
    md: '1rem',       // 16px
    lg: '1.5rem',     // 24px
    xl: '2rem',       // 32px
    '2xl': '3rem',    // 48px
    '3xl': '4rem'     // 64px
  },

  // Border Radius
  borderRadius: {
    sm: '0.5rem',     // 8px
    md: '0.75rem',    // 12px
    lg: '1rem',       // 16px
    xl: '1.5rem',     // 24px
    full: '9999px'
  },

  // Shadows
  shadows: {
    sm: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)'
  },

  // Component Styles
  components: {
    // Card Component
    card: {
      base: 'bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300',
      padding: 'p-6',
      header: 'pb-4 border-b border-slate-100'
    },
    
    // Button Component
    button: {
      base: 'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2',
      sizes: {
        sm: 'px-3 py-2 text-sm rounded-lg',
        md: 'px-4 py-2.5 text-sm rounded-lg',
        lg: 'px-6 py-3 text-base rounded-xl'
      },
      variants: {
        primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500',
        secondary: 'bg-slate-100 hover:bg-slate-200 text-slate-700 focus:ring-slate-500',
        success: 'bg-emerald-600 hover:bg-emerald-700 text-white focus:ring-emerald-500',
        warning: 'bg-orange-600 hover:bg-orange-700 text-white focus:ring-orange-500',
        danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500'
      }
    },
    
    // Input Component
    input: {
      base: 'w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors'
    },
    
    // Badge Component
    badge: {
      base: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
      variants: {
        blue: 'bg-blue-100 text-blue-800',
        green: 'bg-emerald-100 text-emerald-800',
        yellow: 'bg-orange-100 text-orange-800',
        red: 'bg-red-100 text-red-800',
        gray: 'bg-slate-100 text-slate-800'
      }
    }
  },

  // Layout
  layout: {
    container: 'max-w-7xl mx-auto px-6',
    section: 'py-8',
    grid: {
      cols1: 'grid grid-cols-1 gap-6',
      cols2: 'grid grid-cols-1 md:grid-cols-2 gap-6',
      cols3: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6',
      cols4: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'
    }
  },

  // Animations
  animations: {
    fadeIn: 'animate-fade-in',
    slideUp: 'animate-slide-up',
    bounce: 'animate-bounce',
    pulse: 'animate-pulse',
    spin: 'animate-spin'
  }
};

// Helper function to combine classes
export const cn = (...classes: (string | undefined | false)[]): string => {
  return classes.filter(Boolean).join(' ');
};

// Component class generators
export const cardClasses = (variant?: 'elevated' | 'flat') => {
  const base = designSystem.components.card.base;
  if (variant === 'elevated') {
    return `${base} shadow-lg hover:shadow-xl`;
  }
  return base;
};

export const buttonClasses = (
  variant: keyof typeof designSystem.components.button.variants = 'primary',
  size: keyof typeof designSystem.components.button.sizes = 'md'
) => {
  return cn(
    designSystem.components.button.base,
    designSystem.components.button.sizes[size],
    designSystem.components.button.variants[variant]
  );
};

export const badgeClasses = (
  variant: keyof typeof designSystem.components.badge.variants = 'blue'
) => {
  return cn(
    designSystem.components.badge.base,
    designSystem.components.badge.variants[variant]
  );
};