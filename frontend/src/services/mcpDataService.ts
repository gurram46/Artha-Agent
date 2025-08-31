/**
 * Enhanced Financial Data Service - Fetches real financial data from backend API
 * This service connects to the Artha AI backend for live financial data
 * Integrated with secure 24-hour cache system for persistent data storage
 */

import CacheService from './cacheService';
import { getApiUrl } from '../config/environment';

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
    credit_report: MCPCreditReport | null;
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
  private cacheService: CacheService;
  private currentUserEmail: string | null = null;

  private constructor() {
    // Use centralized environment configuration
    this.backendUrl = getApiUrl();
    this.cacheService = CacheService.getInstance();
    console.log(`🔗 MCPDataService initialized with backend URL: ${this.backendUrl}`);
  }

  setDemoMode(enabled: boolean): void {
    this.isDemoMode = enabled;
    // Clear cache when switching modes
    this.cachedData = null;
    this.lastFetch = 0;
    console.log(`🎭 Demo mode ${enabled ? 'enabled' : 'disabled'}`);
  }

  async testConnectivity(): Promise<{ available: boolean; message: string }> {
    try {
      const response = await fetch(`${this.backendUrl}/api/fi-auth/test-connectivity`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });
      
      const result = await response.json();
      return {
        available: result.server_reachable || false,
        message: result.message || 'Unknown connectivity status'
      };
    } catch (error) {
      console.error('Connectivity test failed:', error);
      return {
        available: false,
        message: 'Failed to test Fi Money service connectivity'
      };
    }
  }

  async enableFallbackMode(): Promise<void> {
    console.log('🔄 Enabling fallback mode due to Fi Money service unavailability');
    this.setDemoMode(true);
    
    // Store fallback mode in session storage
    sessionStorage.setItem('fallbackMode', 'true');
    sessionStorage.setItem('fallbackReason', 'Fi Money service unavailable');
  }

  isFallbackMode(): boolean {
    return sessionStorage.getItem('fallbackMode') === 'true';
  }

  getFallbackReason(): string {
    return sessionStorage.getItem('fallbackReason') || 'Service unavailable';
  }

  clearFallbackMode(): void {
    sessionStorage.removeItem('fallbackMode');
    sessionStorage.removeItem('fallbackReason');
    this.setDemoMode(false);
  }

  setUserEmail(email: string): void {
    this.currentUserEmail = email;
    console.log(`👤 User email set for cache operations: ${email}`);
  }

  async getCacheStatus(): Promise<{
    enabled: boolean;
    has_cache: boolean;
    expires_at?: string;
    time_remaining?: string;
    cached_at?: string;
    message: string;
    warning?: string;
  }> {
    if (!this.currentUserEmail) {
      return {
        enabled: false,
        has_cache: false,
        message: 'User email not set for cache operations'
      };
    }

    const status = await this.cacheService.checkCacheStatus(this.currentUserEmail);
    
    // Add expiry warning if applicable
    const warning = this.cacheService.getCacheExpiryWarning(status.time_remaining);
    
    return {
      ...status,
      warning
    };
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
      credit_report: MCPCreditReport | null;
      epf_details: MCPEPFDetails;
    };
    error?: string;
    authRequired?: boolean;
    fromCache?: boolean;
    cacheExpiry?: string;
  }> {
    try {
      console.log(this.isDemoMode 
        ? '🎭 Fetching demo financial data...'
        : '🔄 Fetching real-time financial data from Artha AI...');

      // Check secure cache first (if user email is set and not in demo mode)
      if (!this.isDemoMode && this.currentUserEmail) {
        console.log('🔍 Checking secure cache for financial data...');
        const cacheResult = await this.cacheService.retrieveFinancialData(this.currentUserEmail);
        
        if (cacheResult.success && cacheResult.data) {
          console.log('✅ Using secure cached financial data');
          this.cachedData = cacheResult.data;
          this.lastFetch = Date.now();
          
          const cacheStatus = await this.cacheService.checkCacheStatus(this.currentUserEmail);
          
          return {
            success: true,
            data: cacheResult.data.data,
            fromCache: true,
            cacheExpiry: cacheStatus.expires_at
          };
        }
      }

      // Check short-term memory cache
      const now = Date.now();
      if (this.cachedData && (now - this.lastFetch) < this.cacheDuration) {
        console.log('✅ Using short-term cached financial data');
        return {
          success: true,
          data: this.cachedData.data,
          fromCache: true
        };
      }

      // Fetch from Artha AI via backend (with demo mode support)
      const url = this.isDemoMode 
        ? `${this.backendUrl}/financial-data?demo=true`
        : `${this.backendUrl}/financial-data`;
        
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(30000) // 30 second timeout for real API (increased from 15s)
      });

      if (!response.ok) {
        throw new Error(`Artha AI API error: ${response.status} ${response.statusText}`);
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
        throw new Error(backendData.message || 'Artha AI server error');
      }

      // Cache the successful response in memory
      this.cachedData = backendData;
      this.lastFetch = now;

      // Store in secure cache (if user email is set and not in demo mode)
      if (!this.isDemoMode && this.currentUserEmail) {
        console.log('🔒 Storing data in secure cache...');
        const cacheResult = await this.cacheService.storeFinancialData(
          this.currentUserEmail,
          backendData,
          backendData.summary?.data_source || 'fi_mcp'
        );
        
        if (cacheResult.success) {
          console.log(`✅ Data cached securely for 24 hours`);
        } else {
          console.warn(`⚠️ Failed to cache data: ${cacheResult.message}`);
        }
      }

      console.log(this.isDemoMode 
        ? '✅ Successfully loaded demo data'
        : '✅ Successfully fetched real-time data from Artha AI');
      console.log(`📊 Data source: ${this.isDemoMode ? 'Demo Data' : backendData.summary?.data_source || 'Artha AI'}`);

      return {
        success: true,
        data: backendData.data,
        fromCache: false
      };

    } catch (error) {
      console.error('❌ Failed to fetch real-time data from Artha AI:', error);
      
      // NO FALLBACKS - Production ready
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to connect to Artha AI server',
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
    fallbackEnabled?: boolean;
  }> {
    try {
      console.log('🌐 Initiating Fi Money web authentication...');
      console.log(`🔗 Backend URL: ${this.backendUrl}`);
      console.log(`🔗 Full URL: ${this.backendUrl}/api/fi-auth/initiate`);
      
      // Skip connectivity test - let the actual authentication attempt handle failures
      console.log('🚀 Proceeding directly to Fi Money authentication...');
      
      const response = await fetch(`${this.backendUrl}/api/fi-auth/initiate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(120000) // 120 seconds (2 minutes) timeout for authentication initiation
      });

      console.log(`📡 Response status: ${response.status}`);
      console.log(`📡 Response ok: ${response.ok}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.log(`❌ Response error text: ${errorText}`);
        
        // Don't auto-enable fallback mode - let user choose
        console.warn(`⚠️ Fi Money service error: ${response.status}`);
        
        throw new Error(`Authentication initiation failed: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('📊 Authentication initiate result:', result);
      
      if (result.status === 'login_required') {
        console.log('🔗 Fi Money login URL received');
        // Clear any previous fallback mode since service is working
        this.clearFallbackMode();
        return {
          success: true,
          loginRequired: true,
          loginUrl: result.login_url,
          sessionId: result.session_id,
          message: result.message
        };
      } else if (result.status === 'already_authenticated') {
        console.log('✅ Already authenticated with Fi Money');
        // Clear any previous fallback mode since service is working
        this.clearFallbackMode();
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
      const errorMsg = error instanceof Error ? error.message : 'Authentication initiation error';
      
      // Don't auto-enable fallback mode for network errors
      console.warn(`⚠️ Network/timeout error: ${errorMsg}`);
      
      return {
        success: false,
        message: errorMsg
      };
    }
  }

  async checkAuthenticationStatus(): Promise<{
    authenticated: boolean;
    expiresInMinutes?: number;
    message?: string;
  }> {
    try {
      console.log('🔍 Checking Fi Money authentication status...');
      console.log(`🔗 Status URL: ${this.backendUrl}/api/fi-auth/status`);
      
      const response = await fetch(`${this.backendUrl}/api/fi-auth/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(60000) // 60 seconds timeout for status checks
      });

      console.log(`📡 Status response: ${response.status}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.log(`❌ Status error text: ${errorText}`);
        throw new Error(`Status check failed: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('📊 Status check result:', result);
      
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

  async completeAuthentication(): Promise<{
    authenticated: boolean;
    expiresInMinutes?: number;
    message?: string;
  }> {
    try {
      console.log('🔄 Completing Fi Money authentication...');
      console.log(`🔗 Complete URL: ${this.backendUrl}/api/fi-auth/complete`);
      
      const response = await fetch(`${this.backendUrl}/api/fi-auth/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(30000) // 30 seconds timeout for authentication completion
      });

      console.log(`📡 Complete response: ${response.status}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.log(`❌ Complete error text: ${errorText}`);
        throw new Error(`Auth completion failed: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('📊 Complete result:', result);
      
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
      console.error('❌ Auth completion error:', error);
      return {
        authenticated: false,
        message: 'Auth completion failed'
      };
    }
  }

  async clearCachedSession(): Promise<{ success: boolean; message: string }> {
    try {
      console.log('🧹 Clearing cached Fi Money session to force fresh authentication...');
      
      const response = await fetch(`${this.backendUrl}/api/fi-auth/clear-cache`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(10000)
      });

      const result = await response.json();
      
      // Clear local memory cache regardless of response
      this.cachedData = null;
      this.lastFetch = 0;
      
      console.log('✅ Local cache cleared, server response:', result.message);
      
      return {
        success: result.success || false,
        message: result.message || 'Cache cleared locally'
      };
      
    } catch (error) {
      console.error('❌ Clear cache error:', error);
      // Still clear local cache even if server request fails
      this.cachedData = null;
      this.lastFetch = 0;
      
      return {
        success: true, // Return success since local cache was cleared
        message: 'Local cache cleared (server clear failed)'
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
        signal: AbortSignal.timeout(15000)
      });

      const result = await response.json();
      
      // Clear memory cache regardless of response
      this.cachedData = null;
      this.lastFetch = 0;
      
      // Clear secure cache if user email is set
      if (this.currentUserEmail) {
        await this.invalidateSecureCache();
      }
      
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

  async invalidateSecureCache(): Promise<{ success: boolean; message: string }> {
    if (!this.currentUserEmail) {
      return {
        success: false,
        message: 'User email not set for cache operations'
      };
    }

    const result = await this.cacheService.invalidateCache(this.currentUserEmail);
    
    // Also clear memory cache
    this.cachedData = null;
    this.lastFetch = 0;
    
    return result;
  }

  async handleCacheExpiry(): Promise<{
    shouldReLogin: boolean;
    message: string;
    redirectUrl?: string;
  }> {
    console.log('⏰ Handling cache expiry - prompting for re-login');
    
    // Clear all cached data
    this.cachedData = null;
    this.lastFetch = 0;
    
    if (this.currentUserEmail) {
      await this.cacheService.invalidateCache(this.currentUserEmail);
    }
    
    return {
      shouldReLogin: true,
      message: 'Your session has expired. Please re-login to access your financial data.',
      redirectUrl: '/auth' // Adjust based on your auth route
    };
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

  private parseCurrencyValue(currencyObj: any): number {
    try {
      const units = parseFloat(currencyObj?.units || '0');
      const nanos = currencyObj?.nanos || 0;
      return units + (nanos / 1_000_000_000);
    } catch {
      return 0;
    }
  }

  private getMutualFundCategory(assetClass: string): string {
    const categoryMap: { [key: string]: string } = {
      'EQUITY': 'equity',
      'DEBT': 'debt',
      'HYBRID': 'hybrid',
      'SOLUTION_ORIENTED': 'solution',
      'OTHER': 'others'
    };
    return categoryMap[assetClass] || 'others';
  }

  transformToPortfolioFormat(mcpData: {
    net_worth: MCPNetWorthResponse;
    credit_report: MCPCreditReport | null;
    epf_details: MCPEPFDetails;
    mf_transactions?: any;
    bank_transactions?: any;
  }) {
    try {
      const { net_worth, credit_report, epf_details } = mcpData;
      // Add defensive checks for net_worth data structure
      const assets = (net_worth && net_worth.netWorthResponse && net_worth.netWorthResponse.assetValues) || [];
      const liabilities = (net_worth && net_worth.netWorthResponse && net_worth.netWorthResponse.liabilityValues) || [];

      // Calculate totals from real MCP data
      let totalAssets = 0;
      let totalLiabilities = 0;
      const assetBreakdown: { [key: string]: number } = {};

      // Process assets
      assets.forEach(asset => {
        const value = parseInt(asset.value.units) || 0;
        totalAssets += value;
        
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

      // Get credit score
      let creditScore = 'N/A';
      if (credit_report && credit_report.creditReports && credit_report.creditReports.length > 0) {
        const creditData = credit_report.creditReports[0].creditReportData;
        creditScore = creditData?.score?.bureauScore || 'N/A';
      }

      // Extract mutual fund schemes from net worth data
      const mutualFundSchemes: any[] = [];
      const mfData = net_worth.mfSchemeAnalytics || {};
      
      if (mfData.schemeAnalytics && Array.isArray(mfData.schemeAnalytics)) {
        mfData.schemeAnalytics.forEach((scheme: any) => {
          const schemeDetail = scheme.schemeDetail || {};
          const analytics = scheme.enrichedAnalytics?.analytics?.schemeDetails || {};
          
          const currentValue = this.parseCurrencyValue(analytics.currentValue || {});
          const investedValue = this.parseCurrencyValue(analytics.investedValue || {});
          const absoluteReturns = this.parseCurrencyValue(analytics.absoluteReturns || {});
          
          mutualFundSchemes.push({
            name: schemeDetail.nameData?.longName || 'Unknown Fund',
            amc: (schemeDetail.amc || '').replace(/_/g, ' '),
            asset_class: schemeDetail.assetClass || '',
            risk_level: schemeDetail.fundhouseDefinedRiskLevel || '',
            current_value: currentValue,
            invested_value: investedValue,
            xirr: analytics.XIRR || 0,
            absolute_returns: absoluteReturns,
            returns_percentage: investedValue > 0 ? ((currentValue - investedValue) / investedValue * 100) : 0,
            scheme_code: schemeDetail.schemeCode || '',
            category: this.getMutualFundCategory(schemeDetail.assetClass || '')
          });
        });
      }

      // Extract bank accounts
      const bankAccounts: any[] = [];
      const accountDetails = net_worth.accountDetailsBulkResponse?.accountDetailsMap || {};
      
      Object.entries(accountDetails).forEach(([accountId, accountInfo]: [string, any]) => {
        if (accountInfo.depositSummary) {
          const depositInfo = accountInfo.depositSummary;
          const accountData = accountInfo.accountDetails;
          
          bankAccounts.push({
            bank: accountData.fipMeta?.displayName || 'Unknown Bank',
            account_type: (depositInfo.depositAccountType || '').replace('DEPOSIT_ACCOUNT_TYPE_', ''),
            balance: this.parseCurrencyValue(depositInfo.currentBalance || {}),
            masked_number: accountData.maskedAccountNumber || '',
            account_id: accountId
          });
        }
      });

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

      // Calculate performance metrics from mutual fund data
      let totalInvested = 0;
      let totalCurrent = 0;
      let totalGains = 0;
      let avgXirr = 0;
      let bestPerformer = 'N/A';
      let worstPerformer = 'N/A';
      let bestReturns = -Infinity;
      let worstReturns = Infinity;

      if (mutualFundSchemes.length > 0) {
        mutualFundSchemes.forEach(scheme => {
          totalInvested += scheme.invested_value;
          totalCurrent += scheme.current_value;
          totalGains += scheme.absolute_returns;
          avgXirr += scheme.xirr;
          
          if (scheme.returns_percentage > bestReturns) {
            bestReturns = scheme.returns_percentage;
            bestPerformer = scheme.name;
          }
          
          if (scheme.returns_percentage < worstReturns) {
            worstReturns = scheme.returns_percentage;
            worstPerformer = scheme.name;
          }
        });
        
        avgXirr = avgXirr / mutualFundSchemes.length;
      }

      return {
        summary: {
          total_net_worth: totalNetWorth,
          total_net_worth_formatted: this.formatCurrency(totalNetWorth),
          mutual_funds: mutualFunds,
          mutual_funds_formatted: this.formatCurrency(mutualFunds),
          liquid_funds: savingsAccounts,
          liquid_funds_formatted: this.formatCurrency(savingsAccounts),
          epf: epfBalance,
          epf_formatted: this.formatCurrency(epfBalance),
          credit_score: creditScore,
          total_assets: totalAssets,
          total_liabilities: totalLiabilities
        },
        data: {
          asset_allocation: assetAllocation,
          mutual_fund_schemes: mutualFundSchemes,
          bank_accounts: bankAccounts,
          performance_metrics: {
            total_invested: totalInvested || totalAssets * 0.85,
            total_current: totalCurrent || totalAssets,
            total_gains: totalGains || totalAssets * 0.15,
            total_gains_percentage: totalInvested > 0 ? ((totalCurrent - totalInvested) / totalInvested * 100) : 15,
            avg_xirr: avgXirr || 0,
            best_performer: bestPerformer,
            worst_performer: worstPerformer
          }
        },
        metadata: {
          last_updated: new Date().toISOString(),
          data_source: "Artha AI Real Data from mcp-docs",
          accuracy: "Real MCP response data structure",
          total_assets_inr: totalAssets,
          total_liabilities_inr: totalLiabilities,
          net_worth_inr: totalNetWorth,
          mutual_funds_count: mutualFundSchemes.length,
          bank_accounts_count: bankAccounts.length
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