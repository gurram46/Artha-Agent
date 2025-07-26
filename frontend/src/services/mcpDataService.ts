/**
 * Enhanced Financial Data Service - Fetches real financial data from backend API
 * This service connects to the Artha AI backend for live financial data
 */

interface MCPAsset {
  netWorthAttribute: string;
  value: {
    currencyCode: string;
    units: string;
  };
}

interface MCPLiability {
  netWorthAttribute: string;
  value: {
    currencyCode: string;
    units: string;
  };
}

interface MCPNetWorthResponse {
  netWorthResponse: {
    assetValues: MCPAsset[];
    liabilityValues: MCPLiability[];
    totalNetWorthValue?: {
      currencyCode: string;
      units: string;
    };
  };
}

interface MCPCreditReport {
  creditReports: Array<{
    creditReportData: {
      score?: {
        bureauScore?: string;
      };
      creditAccount?: {
        creditAccountSummary?: {
          totalOutstandingBalance?: {
            outstandingBalanceAll?: string;
          };
        };
      };
    };
  }>;
}

interface MCPEPFDetails {
  epfDetails: {
    balance?: {
      currencyCode: string;
      units: string;
    };
  };
}

interface BackendFinancialData {
  status: string;
  data: {
    net_worth: MCPNetWorthResponse;
    credit_report: MCPCreditReport;
    epf_details: MCPEPFDetails;
  };
  summary: {
    total_net_worth_formatted: string;
    total_assets: number;
    total_liabilities: number;
    credit_score: string;
  };
}

class MCPDataService {
  private static instance: MCPDataService;
  private backendUrl: string;
  private cachedData: BackendFinancialData | null = null;
  private lastFetch: number = 0;
  private cacheDuration: number = 30000; // 30 seconds cache
  private isDemoMode: boolean = false;

  private constructor() {
    // Default to localhost backend, can be configured via environment
    this.backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8003';
  }

  setDemoMode(enabled: boolean): void {
    this.isDemoMode = enabled;
    // Clear cache when switching modes
    this.cachedData = null;
    this.lastFetch = 0;
  }

  static getInstance(): MCPDataService {
    if (!MCPDataService.instance) {
      MCPDataService.instance = new MCPDataService();
    }
    return MCPDataService.instance;
  }

  async loadMCPData(): Promise<{
    success: boolean;
    data?: {
      net_worth: MCPNetWorthResponse;
      credit_report: MCPCreditReport;
      epf_details: MCPEPFDetails;
    };
    error?: string;
    authRequired?: boolean;
  }> {
    try {
      console.log(this.isDemoMode 
        ? '🎭 Fetching demo financial data...'
        : '🔄 Fetching real-time financial data from Fi Money MCP...');

      // Check cache first
      const now = Date.now();
      if (this.cachedData && (now - this.lastFetch) < this.cacheDuration) {
        console.log('✅ Using cached financial data');
        return {
          success: true,
          data: this.cachedData.data
        };
      }

      // Fetch from Fi Money MCP via backend (with demo mode support)
      const url = this.isDemoMode 
        ? `${this.backendUrl}/financial-data?demo=true`
        : `${this.backendUrl}/financial-data`;
        
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(15000) // 15 second timeout for real API
      });

      if (!response.ok) {
        throw new Error(`Fi Money MCP API error: ${response.status} ${response.statusText}`);
      }

      const backendData: BackendFinancialData = await response.json();

      // Handle authentication required
      if (backendData.status === 'unauthenticated') {
        console.warn('🔐 Fi Money authentication required');
        return {
          success: false,
          error: backendData.message || 'Authentication required',
          authRequired: true
        };
      }

      if (backendData.status !== 'success') {
        throw new Error(backendData.message || 'Fi Money MCP server error');
      }

      // Cache the successful response
      this.cachedData = backendData;
      this.lastFetch = now;

      console.log(this.isDemoMode 
        ? '✅ Successfully loaded demo data'
        : '✅ Successfully fetched real-time data from Fi Money MCP');
      console.log(`📊 Data source: ${this.isDemoMode ? 'Demo Data' : backendData.summary?.data_source || 'Fi Money MCP'}`);

      return {
        success: true,
        data: backendData.data
      };

    } catch (error) {
      console.error('❌ Failed to fetch real-time data from Fi Money MCP:', error);
      
      // NO FALLBACKS - Production ready
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to connect to Fi Money MCP server',
        authRequired: error instanceof Error && (error.message.includes('authentication') || error.message.includes('expired'))
      };
    }
  }

  // Fi Money Web Authentication Methods
  async initiateWebAuthentication(): Promise<{
    success: boolean;
    loginRequired?: boolean;
    loginUrl?: string;
    sessionId?: string;
    message: string;
  }> {
    try {
      console.log('🌐 Initiating Fi Money web authentication...');
      
      const response = await fetch(`${this.backendUrl}/api/fi-auth/initiate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(10000)
      });

      if (!response.ok) {
        throw new Error(`Authentication initiation failed: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.status === 'login_required') {
        console.log('🔗 Fi Money login URL received');
        return {
          success: true,
          loginRequired: true,
          loginUrl: result.login_url,
          sessionId: result.session_id,
          message: result.message
        };
      } else if (result.status === 'already_authenticated') {
        console.log('✅ Already authenticated with Fi Money');
        return {
          success: true,
          loginRequired: false,
          message: result.message
        };
      } else {
        console.error('❌ Fi Money authentication initiation failed');
        return {
          success: false,
          message: result.message || 'Authentication initiation failed'
        };
      }
      
    } catch (error) {
      console.error('❌ Fi Money authentication initiation error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Authentication initiation error'
      };
    }
  }

  async checkAuthenticationStatus(): Promise<{
    authenticated: boolean;
    expiresInMinutes?: number;
    message?: string;
  }> {
    try {
      const response = await fetch(`${this.backendUrl}/api/fi-auth/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(5000)
      });

      if (!response.ok) {
        throw new Error(`Status check failed: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.status === 'success') {
        const authStatus = result.auth_status;
        return {
          authenticated: authStatus.authenticated || false,
          expiresInMinutes: authStatus.expires_in_minutes,
          message: authStatus.message
        };
      } else {
        return {
          authenticated: false,
          message: result.message
        };
      }
      
    } catch (error) {
      console.error('❌ Auth status check error:', error);
      return {
        authenticated: false,
        message: 'Status check failed'
      };
    }
  }

  async logout(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.backendUrl}/api/fi-auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(5000)
      });

      const result = await response.json();
      
      // Clear cache regardless of response
      this.cachedData = null;
      this.lastFetch = 0;
      
      return {
        success: result.status === 'success',
        message: result.message
      };
      
    } catch (error) {
      console.error('❌ Logout error:', error);
      return {
        success: false,
        message: 'Logout failed'
      };
    }
  }

  // New method to get additional portfolio insights from backend
  async getPortfolioInsights(): Promise<{
    success: boolean;
    insights?: any;
    error?: string;
  }> {
    try {
      const response = await fetch(`${this.backendUrl}/api/portfolio-health`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(8000)
      });

      if (!response.ok) {
        throw new Error(`Portfolio insights API error: ${response.status}`);
      }

      const data = await response.json();
      return {
        success: true,
        insights: data.portfolio_health
      };

    } catch (error) {
      console.warn('Portfolio insights not available:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Portfolio insights unavailable'
      };
    }
  }

  // New method to get risk assessment from backend
  async getRiskAssessment(): Promise<{
    success: boolean;
    assessment?: any;
    error?: string;
  }> {
    try {
      const response = await fetch(`${this.backendUrl}/api/risk-assessment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(8000)
      });

      if (!response.ok) {
        throw new Error(`Risk assessment API error: ${response.status}`);
      }

      const data = await response.json();
      return {
        success: true,
        assessment: data.risk_assessment
      };

    } catch (error) {
      console.warn('Risk assessment not available:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Risk assessment unavailable'
      };
    }
  }

  transformToPortfolioFormat(mcpData: {
    net_worth: MCPNetWorthResponse;
    credit_report: MCPCreditReport;
    epf_details: MCPEPFDetails;
  }) {
    try {
      const { net_worth, credit_report, epf_details } = mcpData;
      const assets = net_worth.netWorthResponse.assetValues || [];
      const liabilities = net_worth.netWorthResponse.liabilityValues || [];

      // Calculate totals from real MCP data
      let totalAssets = 0;
      let totalLiabilities = 0;

      const assetBreakdown: { [key: string]: number } = {};

      // Process assets
      assets.forEach(asset => {
        const value = parseInt(asset.value.units) || 0;
        totalAssets += value;
        
        // Map asset types to readable names
        const assetTypeMap: { [key: string]: string } = {
          'ASSET_TYPE_MUTUAL_FUND': 'Mutual Funds',
          'ASSET_TYPE_EPF': 'EPF',
          'ASSET_TYPE_INDIAN_SECURITIES': 'Securities',
          'ASSET_TYPE_SAVINGS_ACCOUNTS': 'Savings Accounts',
          'ASSET_TYPE_FIXED_DEPOSIT': 'Fixed Deposits'
        };

        const displayName = assetTypeMap[asset.netWorthAttribute] || asset.netWorthAttribute;
        assetBreakdown[displayName] = value;
      });

      // Process liabilities
      liabilities.forEach(liability => {
        const value = parseInt(liability.value.units) || 0;
        totalLiabilities += value;
      });

      const totalNetWorth = totalAssets - totalLiabilities;

      // Get credit score from real data
      let creditScore = 'N/A';
      if (credit_report.creditReports && credit_report.creditReports.length > 0) {
        const creditData = credit_report.creditReports[0].creditReportData;
        creditScore = creditData?.score?.bureauScore || 'N/A';
      }

      // Create asset allocation array
      const assetAllocation = Object.entries(assetBreakdown)
        .filter(([_, value]) => value > 0)
        .map(([name, value]) => ({
          name,
          value,
          percentage: totalAssets > 0 ? (value / totalAssets * 100) : 0,
          category: this.getCategoryForAssetType(name)
        }));

      // Get individual asset values
      const mutualFunds = assetBreakdown['Mutual Funds'] || 0;
      const savingsAccounts = assetBreakdown['Savings Accounts'] || 0;
      const epfBalance = assetBreakdown['EPF'] || 0;
      const securities = assetBreakdown['Securities'] || 0;
      const fixedDeposits = assetBreakdown['Fixed Deposits'] || 0;

      return {
        summary: {
          total_net_worth: totalNetWorth,
          total_net_worth_formatted: this.formatCurrency(totalNetWorth),
          mutual_funds: mutualFunds,
          mutual_funds_formatted: this.formatCurrency(mutualFunds),
          liquid_funds: savingsAccounts + fixedDeposits,
          liquid_funds_formatted: this.formatCurrency(savingsAccounts + fixedDeposits),
          epf: epfBalance,
          epf_formatted: this.formatCurrency(epfBalance),
          credit_score: creditScore,
          total_assets: totalAssets,
          total_liabilities: totalLiabilities
        },
        data: {
          asset_allocation: assetAllocation,
          mutual_fund_schemes: [], // Would need additional data for individual schemes
          bank_accounts: [
            {
              account_type: "Savings Accounts",
              balance: savingsAccounts,
              bank_name: "Combined Accounts"
            }
          ],
          performance_metrics: {
            total_invested: totalAssets * 0.85, // Estimate
            total_current: totalAssets,
            total_gains: totalAssets * 0.15, // Estimate
            total_gains_percentage: 15, // Estimate
            avg_xirr: 0,
            best_performer: "N/A",
            worst_performer: "N/A"
          }
        },
        metadata: {
          last_updated: new Date().toISOString(),
          data_source: "Fi MCP Real Data from mcp-docs",
          accuracy: "Real MCP response data structure",
          total_assets_inr: totalAssets,
          total_liabilities_inr: totalLiabilities,
          net_worth_inr: totalNetWorth
        }
      };

    } catch (error) {
      console.error('Error transforming MCP data:', error);
      throw new Error('Failed to transform MCP data to portfolio format');
    }
  }

  private formatCurrency(amount: number): string {
    if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)}Cr`;
    if (amount >= 100000) return `₹${(amount / 100000).toFixed(2)}L`;
    if (amount >= 1000) return `₹${(amount / 1000).toFixed(2)}K`;
    return `₹${amount}`;
  }

  private getCategoryForAssetType(assetType: string): string {
    const categoryMap: { [key: string]: string } = {
      'Mutual Funds': 'equity',
      'EPF': 'retirement',
      'Securities': 'equity',
      'Savings Accounts': 'liquid',
      'Fixed Deposits': 'debt'
    };
    return categoryMap[assetType] || 'others';
  }
}

export default MCPDataService;