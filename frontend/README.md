# Artha AI Frontend

A modern React-based frontend application for personal finance management, built with Next.js and TypeScript. Provides an intuitive interface for portfolio tracking, investment recommendations, and financial insights.

## Overview

The Artha AI frontend delivers a comprehensive dashboard for personal finance management with real-time data visualization, AI-powered investment recommendations, and seamless integration with the backend API. Built with modern web technologies for optimal performance and user experience.

## Features

### Core Functionality
- **Portfolio Dashboard**: Real-time net worth tracking and asset allocation visualization
- **Investment Recommendations**: AI-powered mutual fund and stock suggestions with interactive forms
- **Credit Monitoring**: Credit score tracking with detailed analysis and improvement tips
- **Demo Mode**: Toggle between real and demo data for testing and demonstrations
- **Responsive Design**: Mobile-first approach with optimized layouts for all devices
- **Interactive Charts**: Dynamic data visualization using Recharts library

### User Interface
- **Modern Design**: Clean, professional interface with smooth animations
- **Dark/Light Mode**: Automatic theme switching based on system preferences
- **Real-time Updates**: Live data updates without page refresh
- **Progressive Web App**: Installable on mobile devices with offline capabilities
- **Accessibility**: WCAG compliant with keyboard navigation and screen reader support

## Technology Stack

- **Next.js 15**: React framework with app router and server-side rendering
- **TypeScript**: Type-safe development with enhanced IDE support
- **Tailwind CSS**: Utility-first CSS framework for rapid styling
- **Recharts**: Powerful charting library for financial data visualization
- **Framer Motion**: Smooth animations and transitions
- **Redux Toolkit**: Predictable state management with modern patterns
- **Heroicons**: Beautiful SVG icon library
- **Headless UI**: Unstyled, accessible UI components

## Installation

### Prerequisites
- Node.js 18 or higher
- npm, yarn, or pnpm package manager
- Backend API running (see backend README)

### Setup Steps

1. **Clone the repository**:
```bash
git clone <repository-url>
cd Artha-Agent/frontend
```

2. **Install dependencies**:
```bash
npm install
# or
yarn install
# or
pnpm install
```

3. **Environment configuration**:
Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEMO_MODE=false
NEXT_PUBLIC_APP_ENV=development
```

4. **Start the development server**:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

The application will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── app/                        # Next.js app router
│   │   ├── globals.css            # Global styles
│   │   ├── layout.tsx             # Root layout component
│   │   ├── page.tsx               # Home page
│   │   └── loading.tsx            # Loading component
│   ├── components/                 # React components
│   │   ├── Dashboard.tsx          # Main dashboard
│   │   ├── PortfolioOverview.tsx  # Portfolio summary
│   │   ├── InvestmentRecommendationCard.tsx # Investment recommendations
│   │   ├── CreditAnalysis.tsx     # Credit score analysis
│   │   ├── NetWorthChart.tsx      # Net worth visualization
│   │   └── ui/                    # Reusable UI components
│   ├── contexts/                   # React contexts
│   │   ├── FinancialInsightsContext.tsx # Financial data context
│   │   └── ThemeContext.tsx       # Theme management
│   ├── services/                   # API services
│   │   ├── mcpDataService.ts      # MCP data service
│   │   ├── investmentService.ts   # Investment API calls
│   │   └── creditService.ts       # Credit analysis service
│   ├── types/                      # TypeScript type definitions
│   │   ├── financial.ts           # Financial data types
│   │   └── investment.ts          # Investment types
│   ├── utils/                      # Utility functions
│   │   ├── formatters.ts          # Data formatting
│   │   └── calculations.ts        # Financial calculations
│   └── styles/                     # Additional styles
├── public/                         # Static assets
│   ├── icons/                     # App icons
│   ├── images/                    # Images and graphics
│   └── mcp-docs/                  # MCP documentation and sample data
├── package.json                    # Dependencies and scripts
├── tailwind.config.js             # Tailwind configuration
├── next.config.ts                 # Next.js configuration
└── tsconfig.json                  # TypeScript configuration
```

## Key Components

### Dashboard
The main dashboard component that orchestrates all financial data display:

```typescript
// components/Dashboard.tsx
export default function Dashboard() {
  const { financialData, loading } = useFinancialInsights();
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <PortfolioOverview data={financialData} />
      <InvestmentRecommendationCard />
      <CreditAnalysis />
    </div>
  );
}
```

### Investment Recommendations
Interactive component for getting AI-powered investment advice:

```typescript
// components/InvestmentRecommendationCard.tsx
export default function InvestmentRecommendationCard() {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const getRecommendations = async (formData) => {
    setLoading(true);
    try {
      const response = await investmentService.getRecommendations(formData);
      setRecommendations(response.data);
    } finally {
      setLoading(false);
    }
  };
  
  // Component JSX...
}
```

### Portfolio Visualization
Charts and graphs for portfolio data visualization:

```typescript
// components/NetWorthChart.tsx
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts';

export default function NetWorthChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis dataKey="date" />
        <YAxis />
        <Line type="monotone" dataKey="netWorth" stroke="#3B82F6" />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

## State Management

### Context API
Financial data is managed through React Context:

```typescript
// contexts/FinancialInsightsContext.tsx
export const FinancialInsightsProvider = ({ children }) => {
  const [financialData, setFinancialData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const refreshData = async () => {
    setLoading(true);
    try {
      const data = await mcpDataService.getFinancialInsights();
      setFinancialData(data);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <FinancialInsightsContext.Provider value={{ 
      financialData, 
      loading, 
      refreshData 
    }}>
      {children}
    </FinancialInsightsContext.Provider>
  );
};
```

### Redux Store (for complex state)
For application-wide state that needs persistence:

```typescript
// store/slices/portfolioSlice.ts
import { createSlice } from '@reduxjs/toolkit';

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState: {
    data: null,
    lastUpdated: null,
    preferences: {}
  },
  reducers: {
    updatePortfolio: (state, action) => {
      state.data = action.payload;
      state.lastUpdated = new Date().toISOString();
    }
  }
});
```

## API Integration

### Service Layer
Centralized API calls through service modules:

```typescript
// services/investmentService.ts
class InvestmentService {
  private baseURL = process.env.NEXT_PUBLIC_API_URL;
  
  async getRecommendations(params: InvestmentParams) {
    const response = await fetch(`${this.baseURL}/api/ai-investment-recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    
    if (!response.ok) {
      throw new Error('Failed to get recommendations');
    }
    
    return response.json();
  }
  
  async getChatResponse(query: string) {
    const response = await fetch(`${this.baseURL}/api/ai-investment-recommendations/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, mode: 'comprehensive' })
    });
    
    return response.json();
  }
}

export const investmentService = new InvestmentService();
```

## Styling and Theming

### Tailwind CSS Configuration
Customized Tailwind configuration for brand colors and utilities:

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a'
        },
        financial: {
          success: '#10b981',
          warning: '#f59e0b',
          danger: '#ef4444'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    }
  }
};
```

### Component Styling
Consistent styling patterns using Tailwind classes:

```typescript
// Standardized card component
const Card = ({ children, className = '' }) => (
  <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
    {children}
  </div>
);
```

## Build and Deployment

### Development
```bash
npm run dev          # Start development server
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

### Production Build
```bash
npm run build        # Build for production
npm run start        # Start production server
npm run export       # Export static files
```

### Environment-specific Builds
```bash
# Development
npm run build:dev

# Staging
npm run build:staging

# Production
npm run build:prod
```

### Deployment Options

#### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

#### Netlify
```bash
# Build command
npm run build

# Publish directory
out/
```

#### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Performance Optimization

### Code Splitting
Automatic code splitting with Next.js dynamic imports:

```typescript
import dynamic from 'next/dynamic';

const InvestmentChart = dynamic(() => import('./InvestmentChart'), {
  loading: () => <div>Loading chart...</div>,
  ssr: false
});
```

### Image Optimization
Using Next.js Image component for optimal loading:

```typescript
import Image from 'next/image';

<Image
  src="/images/portfolio-hero.jpg"
  alt="Portfolio Dashboard"
  width={800}
  height={400}
  priority
/>
```

### Bundle Analysis
Analyze bundle size:

```bash
npm run analyze
```

## Testing

### Unit Tests
```bash
npm run test         # Run Jest tests
npm run test:watch   # Watch mode
npm run test:coverage # Coverage report
```

### Integration Tests
```bash
npm run test:integration
```

### E2E Tests
```bash
npm run test:e2e     # Playwright tests
```

## Accessibility

- **WCAG 2.1 AA compliant**
- **Keyboard navigation support**
- **Screen reader optimized**
- **High contrast mode**
- **Focus management**

### Testing Accessibility
```bash
npm run test:a11y    # Accessibility tests
npm run lighthouse   # Lighthouse audit
```

## Security

- **Content Security Policy (CSP)**
- **XSS protection**
- **CSRF token handling**
- **Secure cookie management**
- **Input sanitization**

## Browser Support

- **Chrome 80+**
- **Firefox 74+**
- **Safari 13+**
- **Edge 80+**
- **Mobile browsers**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow coding standards
4. Add tests for new features
5. Submit a pull request

### Code Standards
- **ESLint configuration**
- **Prettier formatting**
- **TypeScript strict mode**
- **Component documentation**
- **Accessibility guidelines**

## Troubleshooting

### Common Issues

1. **Module not found**: Clear node_modules and reinstall
2. **Build errors**: Check TypeScript errors and fix types
3. **API connection**: Verify backend URL in environment variables
4. **Styling issues**: Clear Next.js cache with `rm -rf .next`

### Debug Mode
Enable debug logging:
```env
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_LOG_LEVEL=debug
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review browser console for errors