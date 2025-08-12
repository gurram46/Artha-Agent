// Fi Money Design System for Artha AI

export const designSystem = {
  // Artha AI Color Palette - #cca695 and Black Theme
  colors: {
    // Primary Background Colors
    primary: {
      darkest: '#000000',                 // Main background
      dark: '#1a1a1a',                   // Card/surface background
      darker: '#2a2a2a',                 // Secondary surface
      elevated: '#333333',               // Elevated surface
      overlay: 'rgba(0, 0, 0, 0.95)',    // Dark overlay
      transparent: 'rgba(0, 0, 0, 0)',   // Transparent
      blur: 'rgba(26, 26, 26, 0.95)'     // Backdrop blur background
    },
    
    // Text Colors
    text: {
      primary: '#ffffff',       // Primary white text
      secondary: '#e5e7eb',     // Secondary gray text
      tertiary: '#d1d5db',      // Tertiary lighter gray
      muted: '#9ca3af',         // Muted gray text
      placeholder: '#6b7280'    // Placeholder text
    },
    
    // Artha AI Accent Colors - #cca695 Theme
    accent: {
      green: '#cca695',                   // Artha AI signature color
      greenHover: '#b8956a',              // Color hover state
      greenLight: 'rgba(204, 166, 149, 0.1)', // Light background
      greenBorder: 'rgba(204, 166, 149, 0.2)', // Border
      greenBorderHover: 'rgba(204, 166, 149, 0.5)' // Border hover
    },
    
    // Status Colors
    success: '#cca695',
    successLight: 'rgba(204, 166, 149, 0.1)',
    warning: '#f59e0b',
    warningLight: 'rgba(245, 158, 11, 0.1)',
    error: '#ef4444',
    errorLight: 'rgba(239, 68, 68, 0.1)',
    info: '#cca695'
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

  // Artha AI Component Styles - New Color Scheme
  components: {
    // Card Component - #cca695 Theme
    card: {
      base: 'bg-[#1a1a1a] border border-[rgba(204,166,149,0.2)] rounded-3xl shadow-xl hover:shadow-2xl hover:border-[rgba(204,166,149,0.5)] transition-all duration-300',
      elevated: 'bg-[#2a2a2a] border border-[rgba(204,166,149,0.3)] rounded-3xl shadow-2xl hover:shadow-[0_25px_50px_-12px_rgba(0,0,0,0.8)] transition-all duration-300',
      padding: 'p-6',
      header: 'pb-4 border-b border-[rgba(204,166,149,0.2)]',
      content: 'space-y-4'
    },
    
    // Button Component - #cca695 Theme
    button: {
      base: 'inline-flex items-center justify-center font-semibold transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#000000] rounded-2xl shadow-lg',
      sizes: {
        sm: 'px-4 py-2 text-sm',
        md: 'px-6 py-3 text-sm',
        lg: 'px-8 py-4 text-base'
      },
      variants: {
        primary: 'bg-gradient-to-r from-[#cca695] to-[#b8956a] hover:from-[#b8956a] hover:to-[#a6845e] text-white focus:ring-[#cca695] shadow-lg hover:shadow-xl transform hover:scale-105',
    secondary: 'bg-[#2a2a2a] hover:bg-[#333333] text-white focus:ring-[rgba(204,166,149,0.5)] border border-[rgba(204,166,149,0.2)] hover:border-[rgba(204,166,149,0.5)]',
    ghost: 'bg-transparent hover:bg-[rgba(204,166,149,0.1)] text-gray-300 hover:text-white border border-[rgba(204,166,149,0.2)] hover:border-[rgba(204,166,149,0.5)]',
        danger: 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white focus:ring-red-500'
      }
    },
    
    // Input Component - #cca695 Theme
    input: {
      base: 'w-full px-4 py-3 bg-[#2a2a2a] border border-[rgba(204,166,149,0.2)] rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#cca695] focus:border-[#cca695] transition-all duration-300',
    textarea: 'w-full px-4 py-3 bg-[#2a2a2a] border border-[rgba(204,166,149,0.2)] rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#cca695] focus:border-[#cca695] transition-all duration-300 resize-none'
    },
    
    // Badge Component - #cca695 Theme
    badge: {
      base: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border',
      variants: {
        primary: 'bg-[rgba(204,166,149,0.1)] text-[#cca695] border-[rgba(204,166,149,0.2)]',
    success: 'bg-[rgba(204,166,149,0.1)] text-[#cca695] border-[rgba(204,166,149,0.2)]',
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