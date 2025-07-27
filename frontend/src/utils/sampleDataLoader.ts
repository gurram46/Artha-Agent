/**
 * Comprehensive Sample Data Loader - Provides extensive hardcoded mock financial data
 * This utility serves comprehensive financial data for demonstration purposes
 */

export interface SampleFinancialData {
  portfolio: {
    summary: {
      total_net_worth: number;
      total_net_worth_formatted: string;
      mutual_funds: number;
      mutual_funds_formatted: string;
      liquid_funds: number;
      liquid_funds_formatted: string;
      epf: number;
      epf_formatted: string;
      credit_score: string;
      total_assets: number;
      total_liabilities: number;
    };
    data: {
      asset_allocation: Array<{
        name: string;
        value: number;
        percentage: number;
        category: string;
      }>;
      mutual_fund_schemes: Array<{
        scheme_name: string;
        current_value: number;
        invested_amount: number;
        gains: number;
        gains_percentage: number;
        last_nav: number;
        units: number;
        category: string;
      }>;
      bank_accounts: Array<{
        account_type: string;
        balance: number;
        bank_name: string;
      }>;
      performance_metrics: {
        total_invested: number;
        total_current: number;
        total_gains: number;
        total_gains_percentage: number;
        avg_xirr: number;
        best_performer: string;
        worst_performer: string;
      };
    };
    metadata: {
      last_updated: string;
      data_source: string;
      accuracy: string;
      total_assets_inr: number;
      total_liabilities_inr: number;
      net_worth_inr: number;
    };
  };
  bank_transactions: {
    transactions: Array<{
      transactionId: string;
      accountNumber: string;
      accountType: string;
      transactionDate: string;
      amount: {
        currencyCode: string;
        units: string;
      };
      description: string;
      category: string;
      merchantName: string;
      transactionType: string;
      status: string;
    }>;
    summary: {
      total_spent_this_month: number;
      total_transactions: number;
      most_frequent_category: string;
    };
  };
  mutual_fund_transactions: Array<{
    transactionId: string;
    folioNumber: string;
    schemeName: string;
    transactionType: string;
    transactionDate: string;
    amount: number;
    units: number;
    nav: number;
    status: string;
  }>;
  stock_transactions: Array<{
    transactionId: string;
    symbol: string;
    companyName: string;
    transactionType: string;
    transactionDate: string;
    quantity: number;
    price: number;
    totalAmount: number;
    status: string;
  }>;
  insights: {
    spending_insights: Array<{
      category: string;
      percentage: number;
      amount: number;
      trend: string;
    }>;
    investment_insights: Array<{
      scheme_name: string;
      performance: string;
      recommendation: string;
    }>;
    portfolio_health: {
      score: number;
      status: string;
      recommendations: string[];
    };
  };
}

export class SampleDataLoader {
  /**
   * Load comprehensive hardcoded portfolio data
   */
  static loadPortfolioData(): SampleFinancialData['portfolio'] {
    return {
      summary: {
        total_net_worth: 2150000,
        total_net_worth_formatted: "₹21.50L",
        mutual_funds: 950000,
        mutual_funds_formatted: "₹9.50L",
        liquid_funds: 385000,
        liquid_funds_formatted: "₹3.85L",
        epf: 465000,
        epf_formatted: "₹4.65L",
        credit_score: "768",
        total_assets: 2225000,
        total_liabilities: 75000
      },
      data: {
        asset_allocation: [
          { name: "Mutual Funds", value: 950000, percentage: 42.7, category: "equity" },
          { name: "EPF", value: 465000, percentage: 20.9, category: "retirement" },
          { name: "Savings Account", value: 285000, percentage: 12.8, category: "liquid" },
          { name: "Stocks", value: 220000, percentage: 9.9, category: "equity" },
          { name: "Fixed Deposits", value: 205000, percentage: 9.2, category: "debt" },
          { name: "Emergency Fund", value: 100000, percentage: 4.5, category: "liquid" }
        ],
        mutual_fund_schemes: [
          {
            scheme_name: "ICICI Prudential Bluechip Fund Direct Growth",
            current_value: 225420,
            invested_amount: 180000,
            gains: 45420,
            gains_percentage: 25.23,
            last_nav: 68.24,
            units: 3302.5,
            category: "Large Cap"
          },
          {
            scheme_name: "Axis Midcap Fund Direct Growth",
            current_value: 189680,
            invested_amount: 150000,
            gains: 39680,
            gains_percentage: 26.45,
            last_nav: 74.87,
            units: 2533.2,
            category: "Mid Cap"
          },
          {
            scheme_name: "Mirae Asset Large Cap Fund Direct Growth",
            current_value: 198750,
            invested_amount: 165000,
            gains: 33750,
            gains_percentage: 20.45,
            last_nav: 82.81,
            units: 2400.0,
            category: "Large Cap"
          },
          {
            scheme_name: "Parag Parikh Flexi Cap Fund Direct Growth",
            current_value: 218420,
            invested_amount: 200000,
            gains: 18420,
            gains_percentage: 9.21,
            last_nav: 52.18,
            units: 4186.8,
            category: "Flexi Cap"
          },
          {
            scheme_name: "HDFC Index Fund Nifty 50 Direct Plan Growth",
            current_value: 117730,
            invested_amount: 100000,
            gains: 17730,
            gains_percentage: 17.73,
            last_nav: 156.31,
            units: 753.4,
            category: "Index"
          }
        ],
        bank_accounts: [
          { account_type: "Savings Account", balance: 285000, bank_name: "HDFC Bank" },
          { account_type: "Salary Account", balance: 125000, bank_name: "SBI Bank" },
          { account_type: "Fixed Deposit", balance: 205000, bank_name: "ICICI Bank" }
        ],
        performance_metrics: {
          total_invested: 795000,
          total_current: 950000,
          total_gains: 155000,
          total_gains_percentage: 19.50,
          avg_xirr: 16.8,
          best_performer: "Axis Midcap Fund Direct Growth",
          worst_performer: "Parag Parikh Flexi Cap Fund Direct Growth"
        }
      },
      metadata: {
        last_updated: new Date().toISOString(),
        data_source: "Comprehensive Hardcoded Mock Data v3.0",
        accuracy: "Full mock dataset for comprehensive testing",
        total_assets_inr: 2225000,
        total_liabilities_inr: 75000,
        net_worth_inr: 2150000
      }
    };
  }

  /**
   * Load comprehensive hardcoded bank transaction data
   */
  static loadBankTransactions(): SampleFinancialData['bank_transactions'] {
    return {
      transactions: [
        {
          transactionId: "BNK001",
          accountNumber: "****8847",
          accountType: "SAVINGS",
          transactionDate: "2025-01-15T14:30:00Z",
          amount: { currencyCode: "INR", units: "85000" },
          description: "SALARY CREDIT - COMPANY ABC",
          category: "SALARY",
          merchantName: "ABC Technologies",
          transactionType: "CREDIT",
          status: "COMPLETED"
        },
        {
          transactionId: "BNK002",
          accountNumber: "****8847",
          accountType: "SAVINGS",
          transactionDate: "2025-01-14T10:45:00Z",
          amount: { currencyCode: "INR", units: "15000" },
          description: "SIP MUTUAL FUND",
          category: "INVESTMENT",
          merchantName: "ICICI Prudential AMC",
          transactionType: "DEBIT",
          status: "COMPLETED"
        },
        {
          transactionId: "BNK003",
          accountNumber: "****8847",
          accountType: "SAVINGS",
          transactionDate: "2025-01-13T18:20:00Z",
          amount: { currencyCode: "INR", units: "3500" },
          description: "DMart GROCERY SHOPPING",
          category: "GROCERY",
          merchantName: "DMart",
          transactionType: "DEBIT",
          status: "COMPLETED"
        },
        {
          transactionId: "BNK004",
          accountNumber: "****8847",
          accountType: "SAVINGS",
          transactionDate: "2025-01-12T16:15:00Z",
          amount: { currencyCode: "INR", units: "2800" },
          description: "SWIGGY FOOD ORDER",
          category: "FOOD_DELIVERY",
          merchantName: "Swiggy",
          transactionType: "DEBIT",
          status: "COMPLETED"
        },
        {
          transactionId: "BNK005",
          accountNumber: "****8847",
          accountType: "SAVINGS",
          transactionDate: "2025-01-11T09:30:00Z",
          amount: { currencyCode: "INR", units: "1850" },
          description: "ELECTRICITY BILL BESCOM",
          category: "UTILITIES",
          merchantName: "BESCOM",
          transactionType: "DEBIT",
          status: "COMPLETED"
        },
        {
          transactionId: "BNK006",
          accountNumber: "****8847",
          accountType: "SAVINGS",
          transactionDate: "2025-01-10T12:45:00Z",
          amount: { currencyCode: "INR", units: "4200" },
          description: "PETROL PUMP PAYMENT",
          category: "FUEL",
          merchantName: "Indian Oil",
          transactionType: "DEBIT",
          status: "COMPLETED"
        },
        {
          transactionId: "BNK007",
          accountNumber: "****8847",
          accountType: "SAVINGS",
          transactionDate: "2025-01-09T20:15:00Z",
          amount: { currencyCode: "INR", units: "12500" },
          description: "AMAZON SHOPPING",
          category: "SHOPPING",
          merchantName: "Amazon",
          transactionType: "DEBIT",
          status: "COMPLETED"
        },
        {
          transactionId: "BNK008",
          accountNumber: "****8847",
          accountType: "SAVINGS",
          transactionDate: "2025-01-08T15:30:00Z",
          amount: { currencyCode: "INR", units: "950" },
          description: "UBER RIDE",
          category: "TRANSPORTATION",
          merchantName: "Uber",
          transactionType: "DEBIT",
          status: "COMPLETED"
        }
      ],
      summary: {
        total_spent_this_month: 55850,
        total_transactions: 48,
        most_frequent_category: "FOOD_DELIVERY"
      }
    };
  }

  /**
   * Load hardcoded mutual fund transaction data
   */
  static loadMutualFundTransactions(): SampleFinancialData['mutual_fund_transactions'] {
    return [
      {
        transactionId: "MF001",
        folioNumber: "12345678",
        schemeName: "ICICI Prudential Bluechip Fund Direct Growth",
        transactionType: "PURCHASE",
        transactionDate: "2025-01-14T10:30:00Z",
        amount: 5000,
        units: 73.24,
        nav: 68.24,
        status: "CONFIRMED"
      },
      {
        transactionId: "MF002",
        folioNumber: "87654321",
        schemeName: "Axis Midcap Fund Direct Growth",
        transactionType: "PURCHASE",
        transactionDate: "2025-01-14T10:30:00Z",
        amount: 5000,
        units: 66.78,
        nav: 74.87,
        status: "CONFIRMED"
      },
      {
        transactionId: "MF003",
        folioNumber: "11223344",
        schemeName: "Mirae Asset Large Cap Fund Direct Growth",
        transactionType: "PURCHASE",
        transactionDate: "2025-01-14T10:30:00Z",
        amount: 5000,
        units: 60.37,
        nav: 82.81,
        status: "CONFIRMED"
      },
      {
        transactionId: "MF004",
        folioNumber: "55667788",
        schemeName: "HDFC Index Fund Nifty 50 Direct Plan Growth",
        transactionDate: "2024-12-14T10:30:00Z",
        transactionType: "REDEMPTION",
        amount: 15000,
        units: 95.94,
        nav: 156.31,
        status: "CONFIRMED"
      }
    ];
  }

  /**
   * Load hardcoded stock transaction data
   */
  static loadStockTransactions(): SampleFinancialData['stock_transactions'] {
    return [
      {
        transactionId: "STK001",
        symbol: "RELIANCE",
        companyName: "Reliance Industries Limited",
        transactionType: "BUY",
        transactionDate: "2025-01-12T09:15:00Z",
        quantity: 10,
        price: 2850.50,
        totalAmount: 28505,
        status: "CONFIRMED"
      },
      {
        transactionId: "STK002",
        symbol: "TCS",
        companyName: "Tata Consultancy Services",
        transactionType: "BUY",
        transactionDate: "2025-01-08T14:20:00Z",
        quantity: 5,
        price: 4125.75,
        totalAmount: 20628.75,
        status: "CONFIRMED"
      },
      {
        transactionId: "STK003",
        symbol: "INFY",
        companyName: "Infosys Limited",
        transactionType: "BUY",
        transactionDate: "2024-12-20T11:45:00Z",
        quantity: 15,
        price: 1820.25,
        totalAmount: 27303.75,
        status: "CONFIRMED"
      },
      {
        transactionId: "STK004",
        symbol: "HDFC",
        companyName: "HDFC Bank Limited",
        transactionType: "SELL",
        transactionDate: "2024-12-15T15:30:00Z",
        quantity: 8,
        price: 1685.90,
        totalAmount: 13487.20,
        status: "CONFIRMED"
      }
    ];
  }

  /**
   * Load comprehensive hardcoded insights data
   */
  static loadInsights(): SampleFinancialData['insights'] {
    return {
      spending_insights: [
        { category: "Investment", percentage: 26.9, amount: 15000, trend: "increasing" },
        { category: "Shopping", percentage: 22.4, amount: 12500, trend: "stable" },
        { category: "Grocery", percentage: 15.7, amount: 8750, trend: "decreasing" },
        { category: "Food Delivery", percentage: 12.6, amount: 7050, trend: "increasing" },
        { category: "Fuel", percentage: 7.5, amount: 4200, trend: "stable" },
        { category: "Utilities", percentage: 6.6, amount: 3700, trend: "stable" },
        { category: "Transportation", percentage: 4.3, amount: 2400, trend: "increasing" },
        { category: "Entertainment", percentage: 4.0, amount: 2250, trend: "stable" }
      ],
      investment_insights: [
        {
          scheme_name: "Axis Midcap Fund Direct Growth",
          performance: "excellent",
          recommendation: "Continue SIP and consider increasing allocation"
        },
        {
          scheme_name: "ICICI Prudential Bluechip Fund Direct Growth",
          performance: "very good",
          recommendation: "Maintain current SIP amount"
        },
        {
          scheme_name: "Mirae Asset Large Cap Fund Direct Growth",
          performance: "good",
          recommendation: "Good for stable returns, continue"
        },
        {
          scheme_name: "HDFC Index Fund Nifty 50 Direct Plan Growth",
          performance: "good",
          recommendation: "Excellent for diversification, maintain"
        },
        {
          scheme_name: "Parag Parikh Flexi Cap Fund Direct Growth",
          performance: "average",
          recommendation: "Monitor closely, consider alternatives"
        }
      ],
      portfolio_health: {
        score: 78,
        status: "Good",
        recommendations: [
          "Increase emergency fund to 6 months of expenses",
          "Consider adding international diversification",
          "Review and rebalance portfolio quarterly",
          "Optimize tax-saving investments",
          "Monitor high-performing midcap exposure"
        ]
      }
    };
  }

  /**
   * Load comprehensive hardcoded financial data
   */
  static loadAllData(): SampleFinancialData {
    return {
      portfolio: this.loadPortfolioData(),
      bank_transactions: this.loadBankTransactions(),
      mutual_fund_transactions: this.loadMutualFundTransactions(),
      stock_transactions: this.loadStockTransactions(),
      insights: this.loadInsights()
    };
  }
}

// Legacy compatibility - keep original function for backward compatibility
export const loadSampleData = () => {
  const data = SampleDataLoader.loadAllData();
  return {
    summary: data.portfolio.summary,
    data: {
      asset_allocation: data.portfolio.data.asset_allocation,
      mutual_fund_schemes: data.portfolio.data.mutual_fund_schemes,
      bank_accounts: data.portfolio.data.bank_accounts,
      performance_metrics: data.portfolio.data.performance_metrics
    },
    metadata: data.portfolio.metadata
  };
};

const formatCurrency = (amount: number): string => {
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(1)}Cr`;
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`;
  return `₹${amount.toFixed(0)}`;
};