// Sample data loader that transforms the MCP sample responses into our application format

export const loadSampleData = () => {
  // This is the actual sample data from @Artha-Agent/mcp-docs/sample_responses/fetch_net_worth.json
  const sampleMCPData = {
    "netWorthResponse": {
      "assetValues": [
        {
          "netWorthAttribute": "ASSET_TYPE_MUTUAL_FUND",
          "value": {
            "currencyCode": "INR",
            "units": "84613"
          }
        },
        {
          "netWorthAttribute": "ASSET_TYPE_EPF",
          "value": {
            "currencyCode": "INR",
            "units": "211111"
          }
        },
        {
          "netWorthAttribute": "ASSET_TYPE_INDIAN_SECURITIES",
          "value": {
            "currencyCode": "INR",
            "units": "200642"
          }
        },
        {
          "netWorthAttribute": "ASSET_TYPE_SAVINGS_ACCOUNTS",
          "value": {
            "currencyCode": "INR",
            "units": "436355"
          }
        }
      ],
      "liabilityValues": [
        {
          "netWorthAttribute": "LIABILITY_TYPE_OTHER_LOAN",
          "value": {
            "currencyCode": "INR",
            "units": "42000"
          }
        },
        {
          "netWorthAttribute": "LIABILITY_TYPE_HOME_LOAN",
          "value": {
            "currencyCode": "INR",
            "units": "17000"
          }
        },
        {
          "netWorthAttribute": "LIABILITY_TYPE_VEHICLE_LOAN",
          "value": {
            "currencyCode": "INR",
            "units": "5000"
          }
        }
      ],
      "totalNetWorthValue": {
        "currencyCode": "INR",
        "units": "868721"
      }
    },
    "mfSchemeAnalytics": {
      "schemeAnalytics": [
        {
          "schemeDetail": {
            "amc": "CANARA_ROBECO",
            "nameData": {
              "longName": "Canara Robeco Gilt Fund"
            },
            "planType": "DIRECT",
            "investmentType": "OPEN",
            "optionType": "GROWTH",
            "nav": {
              "currencyCode": "INR",
              "units": "73",
              "nanos": 450300000
            },
            "assetClass": "DEBT",
            "isinNumber": "INF760K01FC4",
            "categoryName": "GOVERNMENT_BOND",
            "fundhouseDefinedRiskLevel": "MODERATE_RISK"
          },
          "enrichedAnalytics": {
            "analytics": {
              "schemeDetails": {
                "currentValue": {
                  "currencyCode": "INR",
                  "units": "54141",
                  "nanos": 968504017
                },
                "investedValue": {
                  "currencyCode": "INR",
                  "units": "6655",
                  "nanos": 460000000
                },
                "XIRR": 129.91475375746282,
                "absoluteReturns": {
                  "currencyCode": "INR",
                  "units": "47486",
                  "nanos": 508504017
                },
                "unrealisedReturns": {
                  "currencyCode": "INR",
                  "units": "47486",
                  "nanos": 508504017
                },
                "navValue": {
                  "currencyCode": "INR",
                  "units": "81",
                  "nanos": 414200000
                },
                "units": 665.0187375668689
              }
            }
          }
        },
        {
          "schemeDetail": {
            "amc": "ICICI_PRUDENTIAL",
            "nameData": {
              "longName": "ICICI Prudential Nifty 50 Index Fund"
            },
            "planType": "DIRECT",
            "investmentType": "OPEN",
            "optionType": "GROWTH",
            "nav": {
              "currencyCode": "INR",
              "units": "232",
              "nanos": 380500000
            },
            "assetClass": "EQUITY",
            "isinNumber": "INF109K012M7",
            "categoryName": "INDEX_FUNDS",
            "fundhouseDefinedRiskLevel": "VERY_HIGH_RISK"
          },
          "enrichedAnalytics": {
            "analytics": {
              "schemeDetails": {
                "currentValue": {
                  "currencyCode": "INR",
                  "units": "20147",
                  "nanos": 9681617
                },
                "investedValue": {
                  "currencyCode": "INR",
                  "units": "20054",
                  "nanos": 50755620
                },
                "XIRR": 23.278395563728317,
                "absoluteReturns": {
                  "currencyCode": "INR",
                  "units": "92",
                  "nanos": 958925997
                },
                "unrealisedReturns": {
                  "currencyCode": "INR",
                  "units": "92",
                  "nanos": 958925997
                },
                "navValue": {
                  "currencyCode": "INR",
                  "units": "266",
                  "nanos": 415900000
                },
                "units": 75.62239972020237
              }
            }
          }
        },
        {
          "schemeDetail": {
            "amc": "ICICI_PRUDENTIAL",
            "nameData": {
              "longName": "ICICI Prudential Balanced Advantage Fund"
            },
            "planType": "DIRECT",
            "investmentType": "OPEN",
            "optionType": "GROWTH",
            "nav": {
              "currencyCode": "INR",
              "units": "71",
              "nanos": 650000000
            },
            "assetClass": "HYBRID",
            "isinNumber": "INF109K012B0",
            "categoryName": "DYNAMIC_ASSET_ALLOCATION",
            "fundhouseDefinedRiskLevel": "HIGH_RISK"
          },
          "enrichedAnalytics": {
            "analytics": {
              "schemeDetails": {
                "currentValue": {
                  "currencyCode": "INR",
                  "units": "1438",
                  "nanos": 678832201
                },
                "investedValue": {
                  "currencyCode": "INR",
                  "units": "5272"
                },
                "XIRR": -17.430194898264094,
                "absoluteReturns": {
                  "currencyCode": "INR",
                  "units": "-3833",
                  "nanos": -321167799
                },
                "unrealisedReturns": {
                  "currencyCode": "INR",
                  "units": "-3833",
                  "nanos": -321167799
                },
                "navValue": {
                  "currencyCode": "INR",
                  "units": "12",
                  "nanos": 231100000
                },
                "units": 117.6246480039755
              }
            }
          }
        },
        {
          "schemeDetail": {
            "amc": "UTI",
            "nameData": {
              "longName": "UTI Overnight Fund"
            },
            "planType": "DIRECT",
            "investmentType": "OPEN",
            "optionType": "GROWTH",
            "nav": {
              "currencyCode": "INR",
              "units": "3279",
              "nanos": 785700000
            },
            "assetClass": "CASH",
            "isinNumber": "INF789FB1S71",
            "categoryName": "OVERNIGHT",
            "fundhouseDefinedRiskLevel": "LOW_RISK"
          },
          "enrichedAnalytics": {
            "analytics": {
              "schemeDetails": {
                "currentValue": {
                  "currencyCode": "INR",
                  "units": "123",
                  "nanos": 100000000
                },
                "investedValue": {
                  "currencyCode": "INR",
                  "units": "29235",
                  "nanos": 68000000
                },
                "XIRR": -82.3806209069403,
                "absoluteReturns": {
                  "currencyCode": "INR",
                  "units": "-29111",
                  "nanos": -968000000
                },
                "unrealisedReturns": {
                  "currencyCode": "INR",
                  "units": "-29111",
                  "nanos": -968000000
                },
                "navValue": {
                  "currencyCode": "INR",
                  "units": "12",
                  "nanos": 310000000
                },
                "units": 10
              }
            }
          }
        }
      ]
    },
    "accountDetailsBulkResponse": {
      "accountDetailsMap": {
        "144a3179-a516-48c6-9ed9-73e2f2721c05": {
          "accountDetails": {
            "fipId": "HDFC-FIP",
            "maskedAccountNumber": "XXXXXX8697",
            "accInstrumentType": "ACC_INSTRUMENT_TYPE_DEPOSIT",
            "ifscCode": "EPIFI000012",
            "accountType": {
              "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_SAVINGS"
            },
            "fipMeta": {
              "name": "HDFC Bank",
              "displayName": "HDFC",
              "bank": "HDFC"
            }
          },
          "depositSummary": {
            "accountId": "144a3179-a516-48c6-9ed9-73e2f2721c05",
            "currentBalance": {
              "currencyCode": "INR",
              "units": "106775"
            },
            "balanceDate": "2025-07-08T12:30:14Z",
            "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_SAVINGS",
            "branch": "Test",
            "ifscCode": "EPIFI000012",
            "micrCode": "EPIFI1234",
            "openingDate": "2024-07-07T00:00:00Z",
            "depositAccountStatus": "DEPOSIT_ACCOUNT_STATUS_ACTIVE"
          }
        },
        "241d639b-bc89-4654-9679-f4205b005765": {
          "accountDetails": {
            "fipId": "IDFCFirstBank-FIP",
            "maskedAccountNumber": "XXXXXX8081",
            "accInstrumentType": "ACC_INSTRUMENT_TYPE_DEPOSIT",
            "ifscCode": "EPIFI000012",
            "accountType": {
              "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_SAVINGS"
            },
            "fipMeta": {
              "name": "IDFC Bank",
              "displayName": "IDFC",
              "bank": "IDFC"
            }
          },
          "depositSummary": {
            "accountId": "241d639b-bc89-4654-9679-f4205b005765",
            "currentBalance": {
              "currencyCode": "INR",
              "units": "102735"
            },
            "balanceDate": "2025-07-08T12:30:15Z",
            "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_SAVINGS",
            "branch": "Test",
            "ifscCode": "EPIFI000012",
            "micrCode": "EPIFI1234",
            "openingDate": "2025-05-27T00:00:00Z",
            "depositAccountStatus": "DEPOSIT_ACCOUNT_STATUS_ACTIVE"
          }
        },
        "298184ef-bb92-40cd-afbf-3481d96bdf9e": {
          "accountDetails": {
            "fipId": "HDFC-FIP",
            "maskedAccountNumber": "XXXXXX3139",
            "accInstrumentType": "ACC_INSTRUMENT_TYPE_DEPOSIT",
            "ifscCode": "EPIFI000012",
            "accountType": {
              "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_CURRENT"
            },
            "fipMeta": {
              "name": "HDFC Bank",
              "displayName": "HDFC",
              "bank": "HDFC"
            }
          },
          "depositSummary": {
            "accountId": "298184ef-bb92-40cd-afbf-3481d96bdf9e",
            "currentBalance": {
              "currencyCode": "INR",
              "units": "102464"
            },
            "balanceDate": "2025-07-08T12:30:15Z",
            "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_CURRENT",
            "branch": "Test",
            "ifscCode": "EPIFI000012",
            "micrCode": "EPIFI1234",
            "openingDate": "2024-07-07T00:00:00Z",
            "depositAccountStatus": "DEPOSIT_ACCOUNT_STATUS_ACTIVE"
          }
        },
        "322ef727-c9e1-4347-9077-a8914466ef84": {
          "accountDetails": {
            "fipId": "HDFC-FIP",
            "maskedAccountNumber": "XXXXXX6831",
            "accInstrumentType": "ACC_INSTRUMENT_TYPE_DEPOSIT",
            "ifscCode": "EPIFI000012",
            "accountType": {
              "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_SAVINGS"
            },
            "fipMeta": {
              "name": "HDFC Bank",
              "displayName": "HDFC",
              "bank": "HDFC"
            }
          },
          "depositSummary": {
            "accountId": "322ef727-c9e1-4347-9077-a8914466ef84",
            "currentBalance": {
              "currencyCode": "INR",
              "units": "10726"
            },
            "balanceDate": "2025-07-08T12:30:15Z",
            "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_SAVINGS",
            "branch": "Test",
            "ifscCode": "EPIFI000012",
            "micrCode": "EPIFI1234",
            "openingDate": "2024-07-07T00:00:00Z",
            "depositAccountStatus": "DEPOSIT_ACCOUNT_STATUS_ACTIVE"
          }
        },
        "51ee017b-7eaf-478d-97b2-913e6d4de272": {
          "accountDetails": {
            "fipId": "IDFCFirstBank-FIP",
            "maskedAccountNumber": "XXXXXX6108",
            "accInstrumentType": "ACC_INSTRUMENT_TYPE_DEPOSIT",
            "ifscCode": "EPIFI000012",
            "accountType": {
              "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_CURRENT"
            },
            "fipMeta": {
              "name": "IDFC Bank",
              "displayName": "IDFC",
              "bank": "IDFC"
            }
          },
          "depositSummary": {
            "accountId": "51ee017b-7eaf-478d-97b2-913e6d4de272",
            "currentBalance": {
              "currencyCode": "INR",
              "units": "101669"
            },
            "balanceDate": "2025-07-08T12:30:15Z",
            "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_CURRENT",
            "branch": "Test",
            "ifscCode": "EPIFI000012",
            "micrCode": "EPIFI1234",
            "openingDate": "2025-05-27T00:00:00Z",
            "depositAccountStatus": "DEPOSIT_ACCOUNT_STATUS_ACTIVE"
          }
        },
        "be5e2d35-6daf-41ba-a161-95805f3b59c7": {
          "accountDetails": {
            "fipId": "IDFCFirstBank-FIP",
            "maskedAccountNumber": "XXXXXX8859",
            "accInstrumentType": "ACC_INSTRUMENT_TYPE_DEPOSIT",
            "ifscCode": "EPIFI000012",
            "accountType": {
              "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_SAVINGS"
            },
            "fipMeta": {
              "name": "IDFC Bank",
              "displayName": "IDFC",
              "bank": "IDFC"
            }
          },
          "depositSummary": {
            "accountId": "be5e2d35-6daf-41ba-a161-95805f3b59c7",
            "currentBalance": {
              "currencyCode": "INR",
              "units": "8518"
            },
            "balanceDate": "2025-07-08T12:30:14Z",
            "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_SAVINGS",
            "branch": "Test",
            "ifscCode": "EPIFI000012",
            "micrCode": "EPIFI1234",
            "openingDate": "2025-05-27T00:00:00Z",
            "depositAccountStatus": "DEPOSIT_ACCOUNT_STATUS_ACTIVE"
          }
        }
      }
    }
  };

  return transformMCPDataToPortfolio(sampleMCPData);
};

const transformMCPDataToPortfolio = (mcpData: any) => {
  if (!mcpData) return null;
  
  try {
    const netWorthResponse = mcpData.netWorthResponse;
    const mfAnalytics = mcpData.mfSchemeAnalytics?.schemeAnalytics || [];
    const accountDetails = mcpData.accountDetailsBulkResponse?.accountDetailsMap || {};
    
    // Calculate totals from real MCP data
    const totalNetWorth = netWorthResponse?.totalNetWorthValue ? 
      parseFloat(netWorthResponse.totalNetWorthValue.units) + 
      (netWorthResponse.totalNetWorthValue.nanos || 0) / 1000000000 : 0;
    
    // Extract asset values from real data
    const assetValues = netWorthResponse?.assetValues || [];
    const liabilityValues = netWorthResponse?.liabilityValues || [];
    
    let liquidFunds = 0;
    let mutualFundsValue = 0;
    let epfValue = 0;
    let stocksValue = 0;
    let totalLiabilities = 0;
    
    assetValues.forEach((asset: any) => {
      const value = parseFloat(asset.value.units || '0') + (asset.value.nanos || 0) / 1000000000;
      switch (asset.netWorthAttribute) {
        case 'ASSET_TYPE_SAVINGS_ACCOUNTS':
          liquidFunds += value;
          break;
        case 'ASSET_TYPE_MUTUAL_FUND':
          mutualFundsValue += value;
          break;
        case 'ASSET_TYPE_EPF':
          epfValue += value;
          break;
        case 'ASSET_TYPE_INDIAN_SECURITIES':
        case 'ASSET_TYPE_US_SECURITIES':
          stocksValue += value;
          break;
      }
    });

    liabilityValues.forEach((liability: any) => {
      const value = parseFloat(liability.value.units || '0') + (liability.value.nanos || 0) / 1000000000;
      totalLiabilities += value;
    });
    
    // Process mutual fund schemes
    const mutualFundSchemes = mfAnalytics
      .filter((scheme: any) => scheme.enrichedAnalytics?.analytics?.schemeDetails)
      .map((scheme: any) => {
        const schemeDetail = scheme.schemeDetail;
        const analytics = scheme.enrichedAnalytics?.analytics?.schemeDetails;
        
        return {
          name: schemeDetail?.nameData?.longName || 'Unknown Fund',
          amc: schemeDetail?.amc?.replace(/_/g, ' ') || 'Unknown AMC',
          isin: schemeDetail?.isinNumber,
          category: schemeDetail?.categoryName,
          riskLevel: schemeDetail?.fundhouseDefinedRiskLevel,
          assetClass: schemeDetail?.assetClass,
          nav: parseFloat(schemeDetail?.nav?.units || '0') + (schemeDetail?.nav?.nanos || 0) / 1000000000,
          currentValue: analytics ? parseFloat(analytics.currentValue?.units || '0') + (analytics.currentValue?.nanos || 0) / 1000000000 : 0,
          investedValue: analytics ? parseFloat(analytics.investedValue?.units || '0') + (analytics.investedValue?.nanos || 0) / 1000000000 : 0,
          xirr: analytics?.XIRR || 0,
          units: analytics?.units || 0,
          absoluteReturns: analytics ? parseFloat(analytics.absoluteReturns?.units || '0') + (analytics.absoluteReturns?.nanos || 0) / 1000000000 : 0
        };
      });
    
    // Process bank accounts
    const bankAccounts = Object.values(accountDetails)
      .filter((account: any) => account.depositSummary)
      .map((account: any) => ({
        bank: account.accountDetails?.fipMeta?.displayName || 'Unknown Bank',
        accountNumber: account.accountDetails?.maskedAccountNumber,
        accountType: account.accountDetails?.accountType?.depositAccountType,
        ifsc: account.accountDetails?.ifscCode,
        balance: account.depositSummary ? 
          parseFloat(account.depositSummary.currentBalance?.units || '0') + 
          (account.depositSummary.currentBalance?.nanos || 0) / 1000000000 : 0,
        balanceDate: account.depositSummary?.balanceDate
      }));
    
    return {
      summary: {
        total_net_worth: Math.round(totalNetWorth),
        total_net_worth_formatted: formatCurrency(totalNetWorth),
        liquid_funds: Math.round(liquidFunds),
        liquid_funds_formatted: formatCurrency(liquidFunds),
        mutual_funds_value: Math.round(mutualFundsValue),
        mutual_funds_formatted: formatCurrency(mutualFundsValue),
        epf_value: Math.round(epfValue),
        epf_formatted: formatCurrency(epfValue),
        stocks_value: Math.round(stocksValue),
        stocks_formatted: formatCurrency(stocksValue),
        total_liabilities: Math.round(totalLiabilities),
        total_liabilities_formatted: formatCurrency(totalLiabilities)
      },
      data: {
        mutual_fund_schemes: mutualFundSchemes,
        bank_accounts: bankAccounts,
        asset_allocation: [
          { name: 'Mutual Funds', value: mutualFundsValue, percentage: totalNetWorth > 0 ? (mutualFundsValue / totalNetWorth) * 100 : 0 },
          { name: 'Stocks', value: stocksValue, percentage: totalNetWorth > 0 ? (stocksValue / totalNetWorth) * 100 : 0 },
          { name: 'EPF', value: epfValue, percentage: totalNetWorth > 0 ? (epfValue / totalNetWorth) * 100 : 0 },
          { name: 'Liquid Funds', value: liquidFunds, percentage: totalNetWorth > 0 ? (liquidFunds / totalNetWorth) * 100 : 0 }
        ].filter(item => item.value > 0),
        performance_metrics: {
          total_invested: mutualFundSchemes.reduce((sum: number, scheme: any) => sum + scheme.investedValue, 0),
          total_current: mutualFundSchemes.reduce((sum: number, scheme: any) => sum + scheme.currentValue, 0),
          total_returns: mutualFundSchemes.reduce((sum: number, scheme: any) => sum + scheme.absoluteReturns, 0),
          avg_xirr: mutualFundSchemes.length > 0 ? 
            mutualFundSchemes.reduce((sum: number, scheme: any) => sum + scheme.xirr, 0) / mutualFundSchemes.length : 0
        }
      }
    };
  } catch (error) {
    console.error('Error transforming MCP data:', error);
    return null;
  }
};

const formatCurrency = (amount: number): string => {
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(1)}Cr`;
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`;
  return `₹${amount.toFixed(0)}`;
};