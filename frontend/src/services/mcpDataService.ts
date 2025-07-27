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
  message?: string;
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
    data_source?: string;
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
    // Use environment variable or production backend URL with explicit checks
    const envBackendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
    const envApiUrl = process.env.NEXT_PUBLIC_API_URL;
    
    // Log for debugging
    console.log('Environment variables check:', { envBackendUrl, envApiUrl });
    
    // Ensure we never use placeholder URLs
    let backendUrl = envBackendUrl || envApiUrl || 'https://artha-agent.onrender.com';
    
    // Safety check for placeholder URLs and localhost
    if (backendUrl.includes('your-backend-url') || backendUrl.includes('placeholder') || backendUrl.includes('localhost')) {
      backendUrl = 'https://artha-agent.onrender.com';
      console.warn('⚠️ Detected placeholder/localhost URL, using production fallback:', backendUrl);
    }
    
    this.backendUrl = backendUrl;
    console.log('✅ MCPDataService initialized with backend URL:', this.backendUrl);
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
      console.log('🎭 Loading MCP data from local files...');

      // Check cache first
      const now = Date.now();
      if (this.cachedData && (now - this.lastFetch) < this.cacheDuration) {
        console.log('✅ Using cached financial data');
        return {
          success: true,
          data: this.cachedData.data
        };
      }

      // Load data from local MCP files
      const netWorthResponse = await fetch('/mcp-docs/fetch_net_worth.json');
      const creditReportResponse = await fetch('/mcp-docs/fetch_credit_report.json');
      const epfDetailsResponse = await fetch('/mcp-docs/fetch_epf_details.json');

      if (!netWorthResponse.ok || !creditReportResponse.ok || !epfDetailsResponse.ok) {
        throw new Error('Failed to load MCP data files');
      }

      const netWorthData = await netWorthResponse.json();
      const creditReportData = await creditReportResponse.json();
      const epfDetailsData = await epfDetailsResponse.json();

      // Transform to expected format
      const mcpData = {
        net_worth: netWorthData,
        credit_report: creditReportData,
        epf_details: {
          epfDetails: {
            balance: {
              currencyCode: "INR",
              units: epfDetailsData.uanAccounts[0]?.rawDetails?.overall_pf_balance?.current_pf_balance || "211111"
            }
          }
        }
      };

      // Create mock backend response for caching
      this.cachedData = {
        status: 'success',
        message: 'Data loaded from local MCP files',
        data: mcpData,
        summary: {
          total_net_worth_formatted: this.formatCurrency(parseInt(netWorthData.netWorthResponse.totalNetWorthValue.units)),
          total_assets: this.calculateTotalAssets(netWorthData.netWorthResponse.assetValues),
          total_liabilities: this.calculateTotalLiabilities(netWorthData.netWorthResponse.liabilityValues),
          credit_score: creditReportData.creditReports[0]?.creditReportData?.score?.bureauScore || '746',
          data_source: 'Local MCP Files'
        }
      };
      
      this.lastFetch = now;

      console.log('✅ Successfully loaded MCP data from local files');
      console.log('📊 Data source: Local MCP Files');

      return {
        success: true,
        data: mcpData
      };

    } catch (error) {
      console.error('❌ Failed to load MCP data from local files:', error);
      
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to load local MCP data files',
        authRequired: false
      };
    }
  }

  private calculateTotalAssets(assetValues: MCPAsset[]): number {
    return assetValues.reduce((total, asset) => total + parseInt(asset.value.units), 0);
  }

  private calculateTotalLiabilities(liabilityValues: MCPLiability[]): number {
    return liabilityValues.reduce((total, liability) => total + parseInt(liability.value.units), 0);
  }

  // Local MCP Authentication Methods (simplified for local data)
  async initiateWebAuthentication(): Promise<{
    success: boolean;
    loginRequired?: boolean;
    loginUrl?: string;
    sessionId?: string;
    message: string;
  }> {
    console.log('🎭 Mock authentication - using local MCP data');
    
    // Simulate successful authentication since we're using local data
    return {
      success: true,
      loginRequired: false,
      message: 'Local MCP data - no authentication required'
    };
  }

  async checkAuthenticationStatus(): Promise<{
    authenticated: boolean;
    expiresInMinutes?: number;
    message?: string;
    isDemo?: boolean;
  }> {
    // Always authenticated since we're using local data
    return {
      authenticated: true,
      isDemo: true,
      message: 'Using local MCP data files'
    };
  }

  async logout(): Promise<{ success: boolean; message: string }> {
    // Clear cache
    this.cachedData = null;
    this.lastFetch = 0;
    
    return {
      success: true,
      message: 'Logged out from local MCP data'
    };
  }

  // Local portfolio insights (using MCP data)
  async getPortfolioInsights(): Promise<{
    success: boolean;
    insights?: any;
    error?: string;
  }> {
    try {
      const mcpResult = await this.loadMCPData();
      if (!mcpResult.success || !mcpResult.data) {
        throw new Error('MCP data not available');
      }

      // Generate insights from local MCP data
      const insights = this.generatePortfolioInsights(mcpResult.data);
      
      return {
        success: true,
        insights
      };

    } catch (error) {
      console.warn('Portfolio insights not available:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Portfolio insights unavailable'
      };
    }
  }

  // Local risk assessment (using MCP data)
  async getRiskAssessment(): Promise<{
    success: boolean;
    assessment?: any;
    error?: string;
  }> {
    try {
      const mcpResult = await this.loadMCPData();
      if (!mcpResult.success || !mcpResult.data) {
        throw new Error('MCP data not available');
      }

      // Generate risk assessment from local MCP data
      const assessment = this.generateRiskAssessment(mcpResult.data);
      
      return {
        success: true,
        assessment
      };

    } catch (error) {
      console.warn('Risk assessment not available:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Risk assessment unavailable'
      };
    }
  }

  private generatePortfolioInsights(mcpData: any) {
    const netWorth = mcpData.net_worth.netWorthResponse;
    const totalAssets = this.calculateTotalAssets(netWorth.assetValues);
    const totalLiabilities = this.calculateTotalLiabilities(netWorth.liabilityValues);
    
    return {
      portfolio_health: {
        overall_score: 75,
        health_status: 'Good',
        key_insights: [
          `Total net worth: ${this.formatCurrency(totalAssets - totalLiabilities)}`,
          `Asset allocation looks balanced across multiple asset classes`,
          `Credit score of ${mcpData.credit_report.creditReports[0]?.creditReportData?.score?.bureauScore || '746'} is good`,
          `EPF balance: ${this.formatCurrency(parseInt(mcpData.epf_details.epfDetails.balance.units))}`
        ],
        recommendations: [
          'Consider increasing emergency fund to 6 months of expenses',
          'Review mutual fund allocation for better tax efficiency',
          'Monitor credit utilization ratio'
        ]
      }
    };
  }

  private generateRiskAssessment(mcpData: any) {
    const creditScore = parseInt(mcpData.credit_report.creditReports[0]?.creditReportData?.score?.bureauScore || '746');
    const outstandingBalance = parseInt(mcpData.credit_report.creditReports[0]?.creditReportData?.creditAccount?.creditAccountSummary?.totalOutstandingBalance?.outstandingBalanceAll || '75000');
    
    return {
      risk_assessment: {
        overall_risk_level: creditScore > 750 ? 'Low' : creditScore > 650 ? 'Moderate' : 'High',
        credit_risk: creditScore > 750 ? 'Low' : 'Moderate',
        liquidity_risk: 'Low',
        market_risk: 'Moderate',
        concentration_risk: 'Low',
        key_risks: [
          `Outstanding debt: ${this.formatCurrency(outstandingBalance)}`,
          'Equity exposure in mutual funds carries market risk',
          'Multiple bank accounts provide good liquidity'
        ],
        mitigation_strategies: [
          'Maintain emergency fund in liquid assets',
          'Diversify across asset classes',
          'Monitor and pay down high-interest debt'
        ]
      }
    };
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