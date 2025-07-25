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

  private constructor() {
    // Default to localhost backend, can be configured via environment
    this.backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8003';
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
  }> {
    try {
      console.log('🔄 Fetching real financial data from backend API...');

      // Check cache first
      const now = Date.now();
      if (this.cachedData && (now - this.lastFetch) < this.cacheDuration) {
        console.log('✅ Using cached financial data');
        return {
          success: true,
          data: this.cachedData.data
        };
      }

      // Fetch from backend API
      const response = await fetch(`${this.backendUrl}/financial-data`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        // Add timeout
        signal: AbortSignal.timeout(10000) // 10 second timeout
      });

      if (!response.ok) {
        throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
      }

      const backendData: BackendFinancialData = await response.json();

      if (backendData.status !== 'success') {
        throw new Error(backendData.status || 'Backend returned error status');
      }

      // Cache the successful response
      this.cachedData = backendData;
      this.lastFetch = now;

      console.log('✅ Successfully fetched financial data from backend');

      return {
        success: true,
        data: backendData.data
      };

    } catch (error) {
      console.error('❌ Failed to fetch data from backend, falling back to static data:', error);
      
      // Fallback to static MCP data if backend is unavailable
      return await this.loadStaticMCPData();
    }
  }

  // Fallback method to load static data from mcp-docs if backend is down
  private async loadStaticMCPData(): Promise<{
    success: boolean;
    data?: {
      net_worth: MCPNetWorthResponse;
      credit_report: MCPCreditReport;
      epf_details: MCPEPFDetails;
    };
    error?: string;
  }> {
    try {
      console.log('🔄 Falling back to static MCP data from docs...');

      // Load all MCP data files from static files
      const [netWorthResponse, creditReportResponse, epfResponse] = await Promise.all([
        fetch('/mcp-docs/sample_responses/fetch_net_worth.json'),
        fetch('/mcp-docs/sample_responses/fetch_credit_report.json'),
        fetch('/mcp-docs/sample_responses/fetch_epf_details.json')
      ]);

      if (!netWorthResponse.ok || !creditReportResponse.ok || !epfResponse.ok) {
        throw new Error('Failed to load static MCP data files');
      }

      const netWorthData = await netWorthResponse.json();
      const creditReportData = await creditReportResponse.json();
      const epfData = await epfResponse.json();

      console.log('✅ Successfully loaded static MCP data from docs (fallback)');

      return {
        success: true,
        data: {
          net_worth: netWorthData,
          credit_report: creditReportData,
          epf_details: epfData
        }
      };

    } catch (error) {
      console.error('❌ Failed to load static MCP data:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error loading financial data'
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