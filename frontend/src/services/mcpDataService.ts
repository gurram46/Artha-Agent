/**
 * MCP Data Service - Loads real financial data from MCP docs
 * This service reads actual Fi MCP response data from the mcp-docs directory
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

class MCPDataService {
  private static instance: MCPDataService;
  private netWorthData: MCPNetWorthResponse | null = null;
  private creditReportData: MCPCreditReport | null = null;
  private epfData: MCPEPFDetails | null = null;

  private constructor() {}

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
      console.log('🔄 Loading real MCP financial data from docs...');

      // Load all MCP data files
      const [netWorthResponse, creditReportResponse, epfResponse] = await Promise.all([
        fetch('/mcp-docs/sample_responses/fetch_net_worth.json'),
        fetch('/mcp-docs/sample_responses/fetch_credit_report.json'),
        fetch('/mcp-docs/sample_responses/fetch_epf_details.json')
      ]);

      if (!netWorthResponse.ok) {
        throw new Error(`Failed to load net worth data: ${netWorthResponse.status}`);
      }
      if (!creditReportResponse.ok) {
        throw new Error(`Failed to load credit report: ${creditReportResponse.status}`);
      }
      if (!epfResponse.ok) {
        throw new Error(`Failed to load EPF data: ${epfResponse.status}`);
      }

      this.netWorthData = await netWorthResponse.json();
      this.creditReportData = await creditReportResponse.json();
      this.epfData = await epfResponse.json();

      console.log('✅ Successfully loaded real MCP data from docs');

      return {
        success: true,
        data: {
          net_worth: this.netWorthData,
          credit_report: this.creditReportData,
          epf_details: this.epfData
        }
      };

    } catch (error) {
      console.error('❌ Failed to load MCP data:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error loading MCP data'
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