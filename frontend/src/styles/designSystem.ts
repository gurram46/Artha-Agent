// Fi Money Design System for Artha AI

export const designSystem = {
  // Dark Theme Color Palette - Artha AI
  colors: {
    // Primary Dark Background Colors
    primary: {
      darkest: 'rgb(0, 26, 30)',         // Main background
      dark: 'rgb(24, 25, 27)',           // Card/surface background
      darker: 'rgb(30, 32, 34)',         // Secondary surface
      elevated: 'rgb(34, 36, 38)',       // Elevated surface
      overlay: 'rgba(0, 26, 30, 0.95)',  // Dark overlay
      transparent: 'rgba(0, 0, 0, 0)',   // Transparent
      blur: 'rgba(26, 26, 26, 0.95)'     // Backdrop blur background
    },
    
    // Text Colors for Dark Theme
    text: {
      primary: '#ffffff',       // Primary white text
      secondary: '#e5e7eb',     // Secondary gray text
      tertiary: '#d1d5db',      // Tertiary lighter gray
      muted: '#9ca3af',         // Muted gray text
      placeholder: '#6b7280'    // Placeholder text
    },
    
    // Fi Money Accent Colors
    accent: {
      green: 'rgb(0, 184, 153)',         // Fi Money signature green
      greenHover: 'rgb(0, 164, 133)',    // Green hover state
      greenLight: 'rgba(0, 184, 153, 0.1)', // Light green background
      greenBorder: 'rgba(0, 184, 153, 0.2)', // Green border
      greenBorderHover: 'rgba(0, 184, 153, 0.5)' // Green border hover
    },
    
    // Status Colors for Dark Theme
    success: 'rgb(0, 184, 153)',
    successLight: 'rgba(0, 184, 153, 0.1)',
    warning: '#f59e0b',
    warningLight: 'rgba(245, 158, 11, 0.1)',
    error: '#ef4444',
    errorLight: 'rgba(239, 68, 68, 0.1)',
    info: 'rgb(0, 184, 153)'
  },

  // Typography (Fi Money Style)
  typography: {
    fontFamily: {
      primary: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
      mono: 'JetBrains Mono, Menlo, monospace'
    },
    
    fontSize: {
      xs: '0.75rem',      // 12px
      sm: '0.875rem',     // 14px
      base: '1rem',       // 16px
      lg: '1.125rem',     // 18px
      xl: '1.25rem',      // 20px
      '2xl': '1.5rem',    // 24px
      '3xl': '1.875rem',  // 30px
      '4xl': '2.25rem',   // 36px
      '5xl': '3rem'       // 48px
    },
    
    fontWeight: {
      light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      black: '900'
    },
    
    // Dark Theme Heading styles
    heading: {
      xlarge: 'text-4xl font-black text-white tracking-tight',
      large: 'text-3xl font-bold text-white tracking-tight',
      medium: 'text-2xl font-bold text-white tracking-tight',
      small: 'text-xl font-semibold text-white tracking-tight',
      xsmall: 'text-lg font-semibold text-white'
    },
    
    // Dark Theme Body text styles
    body: {
      large: 'text-lg text-gray-300 font-medium',
      default: 'text-base text-gray-300 font-medium',
      small: 'text-sm text-gray-400 font-medium',
      xsmall: 'text-xs text-gray-400 font-medium'
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

  // Dark Theme Component Styles
  components: {
    // Card Component - Consistent Dark Style
    card: {
      base: 'bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl shadow-xl hover:shadow-2xl hover:border-[rgba(0,184,153,0.5)] transition-all duration-300',
      elevated: 'bg-[rgb(30,32,34)] border border-[rgba(0,184,153,0.3)] rounded-3xl shadow-2xl hover:shadow-[0_25px_50px_-12px_rgba(0,0,0,0.8)] transition-all duration-300',
      padding: 'p-6',
      header: 'pb-4 border-b border-[rgba(0,184,153,0.2)]',
      content: 'space-y-4'
    },
    
    // Button Component - Dark Theme
    button: {
      base: 'inline-flex items-center justify-center font-semibold transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[rgb(0,26,30)] rounded-2xl shadow-lg',
      sizes: {
        sm: 'px-4 py-2 text-sm',
        md: 'px-6 py-3 text-sm',
        lg: 'px-8 py-4 text-base'
      },
      variants: {
        primary: 'bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] hover:from-[rgb(0,164,133)] hover:to-[rgb(0,144,113)] text-white focus:ring-[rgb(0,184,153)] shadow-lg hover:shadow-xl transform hover:scale-105',
        secondary: 'bg-[rgb(30,32,34)] hover:bg-[rgb(34,36,38)] text-white focus:ring-[rgba(0,184,153,0.5)] border border-[rgba(0,184,153,0.2)] hover:border-[rgba(0,184,153,0.5)]',
        ghost: 'bg-transparent hover:bg-[rgba(0,184,153,0.1)] text-gray-300 hover:text-white border border-[rgba(0,184,153,0.2)] hover:border-[rgba(0,184,153,0.5)]',
        danger: 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white focus:ring-red-500'
      }
    },
    
    // Input Component - Dark Theme
    input: {
      base: 'w-full px-4 py-3 bg-[rgb(30,32,34)] border border-[rgba(0,184,153,0.2)] rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[rgb(0,184,153)] focus:border-[rgb(0,184,153)] transition-all duration-300',
      textarea: 'w-full px-4 py-3 bg-[rgb(30,32,34)] border border-[rgba(0,184,153,0.2)] rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[rgb(0,184,153)] focus:border-[rgb(0,184,153)] transition-all duration-300 resize-none'
    },
    
    // Badge Component - Dark Theme
    badge: {
      base: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border',
      variants: {
        primary: 'bg-[rgba(0,184,153,0.1)] text-[rgb(0,184,153)] border-[rgba(0,184,153,0.2)]',
        success: 'bg-[rgba(0,184,153,0.1)] text-[rgb(0,184,153)] border-[rgba(0,184,153,0.2)]',
        warning: 'bg-[rgba(245,158,11,0.1)] text-yellow-400 border-[rgba(245,158,11,0.2)]',
        error: 'bg-[rgba(239,68,68,0.1)] text-red-400 border-[rgba(239,68,68,0.2)]',
        neutral: 'bg-[rgba(156,163,175,0.1)] text-gray-400 border-[rgba(156,163,175,0.2)]'
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