import 'dart:convert';
import 'dart:io';
import 'package:flutter/services.dart';
import '../models/net_worth.dart';
import '../models/credit_report.dart';
import '../models/epf_details.dart';
import '../models/mf_transactions.dart';
import 'fi_money_api_service.dart';

class FiMoneyMockService {
  static const String _basePath = 'assets/sample_data';
  
  static final FiMoneyMockService _instance = FiMoneyMockService._internal();
  factory FiMoneyMockService() => _instance;
  FiMoneyMockService._internal();

  /// Load sample data files and copy them to assets if they don't exist
  Future<void> _initializeSampleData() async {
    try {
      // Check if sample data exists in assets, if not, we'll use the provided sample data
      await rootBundle.loadString('$_basePath/fetch_net_worth.json');
    } catch (e) {
      // Sample data not found in assets, we'll use hardcoded sample data
      print('Sample data not found in assets, using hardcoded data');
    }
  }

  /// Fetches net worth data from sample JSON
  Future<ApiResponse<FullNetWorthData>> fetchNetWorth() async {
    try {
      await Future.delayed(Duration(milliseconds: 500)); // Simulate network delay
      
      String jsonString;
      try {
        jsonString = await rootBundle.loadString('$_basePath/fetch_net_worth.json');
      } catch (e) {
        // If assets not found, use hardcoded sample data
        jsonString = _getSampleNetWorthData();
      }
      
      final jsonData = jsonDecode(jsonString);
      final netWorthData = FullNetWorthData.fromJson(jsonData);
      return ApiResponse.success(netWorthData);
    } catch (e) {
      return ApiResponse.error('Failed to load net worth data: $e', 500);
    }
  }

  /// Fetches credit report data from sample JSON
  Future<ApiResponse<CreditReportResponse>> fetchCreditReport() async {
    try {
      await Future.delayed(Duration(milliseconds: 300)); // Simulate network delay
      
      String jsonString;
      try {
        jsonString = await rootBundle.loadString('$_basePath/fetch_credit_report.json');
      } catch (e) {
        jsonString = _getSampleCreditReportData();
      }
      
      final jsonData = jsonDecode(jsonString);
      final creditReportData = CreditReportResponse.fromJson(jsonData);
      return ApiResponse.success(creditReportData);
    } catch (e) {
      return ApiResponse.error('Failed to load credit report: $e', 500);
    }
  }

  /// Fetches EPF details from sample JSON
  Future<ApiResponse<EpfDetailsResponse>> fetchEpfDetails() async {
    try {
      await Future.delayed(Duration(milliseconds: 400)); // Simulate network delay
      
      String jsonString;
      try {
        jsonString = await rootBundle.loadString('$_basePath/fetch_epf_details.json');
      } catch (e) {
        jsonString = _getSampleEpfDetailsData();
      }
      
      final jsonData = jsonDecode(jsonString);
      final epfDetailsData = EpfDetailsResponse.fromJson(jsonData);
      return ApiResponse.success(epfDetailsData);
    } catch (e) {
      return ApiResponse.error('Failed to load EPF details: $e', 500);
    }
  }

  /// Fetches mutual fund transactions from sample JSON
  Future<ApiResponse<MfTransactionsResponse>> fetchMfTransactions() async {
    try {
      await Future.delayed(Duration(milliseconds: 600)); // Simulate network delay
      
      String jsonString;
      try {
        jsonString = await rootBundle.loadString('$_basePath/fetch_mf_transactions.json');
      } catch (e) {
        jsonString = _getSampleMfTransactionsData();
      }
      
      final jsonData = jsonDecode(jsonString);
      final mfTransactionsData = MfTransactionsResponse.fromJson(jsonData);
      return ApiResponse.success(mfTransactionsData);
    } catch (e) {
      return ApiResponse.error('Failed to load MF transactions: $e', 500);
    }
  }

  /// Fetches all financial data in parallel
  Future<AllFinancialDataResponse> fetchAllFinancialData() async {
    final List<Future> futures = [
      fetchNetWorth(),
      fetchCreditReport(),
      fetchEpfDetails(),
      fetchMfTransactions(),
    ];

    final results = await Future.wait(futures);

    return AllFinancialDataResponse(
      netWorth: results[0] as ApiResponse<FullNetWorthData>,
      creditReport: results[1] as ApiResponse<CreditReportResponse>,
      epfDetails: results[2] as ApiResponse<EpfDetailsResponse>,
      mfTransactions: results[3] as ApiResponse<MfTransactionsResponse>,
    );
  }

  // Exact sample data from fetch_net_worth.json
  String _getSampleNetWorthData() {
    return '''{
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
          "divReinvOptionType": "REINVESTMENT_ONY",
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
            "longName": "ICICI Prudential Nifty 50 Index Fund"
          },
          "planType": "DIRECT",
          "investmentType": "OPEN",
          "optionType": "GROWTH",
          "divReinvOptionType": "REINVESTMENT_ONY",
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
                "units": "6923",
                "nanos": 570000000
              },
              "investedValue": {
                "currencyCode": "INR"
              },
              "XIRR": 0,
              "absoluteReturns": {
                "currencyCode": "INR"
              },
              "unrealisedReturns": {
                "currencyCode": "INR"
              },
              "navValue": {
                "currencyCode": "INR",
                "units": "185",
                "nanos": 643100000
              },
              "units": 37.29505702070263
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
                "units": "1746",
                "nanos": 414478218
              },
              "investedValue": {
                "currencyCode": "INR"
              },
              "XIRR": 0,
              "absoluteReturns": {
                "currencyCode": "INR"
              },
              "unrealisedReturns": {
                "currencyCode": "INR"
              },
              "navValue": {
                "currencyCode": "INR",
                "units": "21",
                "nanos": 84100000
              },
              "units": 82.83087626304456
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
                "units": "51",
                "nanos": 610077158
              },
              "investedValue": {
                "currencyCode": "INR"
              },
              "XIRR": 0,
              "absoluteReturns": {
                "currencyCode": "INR"
              },
              "unrealisedReturns": {
                "currencyCode": "INR"
              },
              "navValue": {
                "currencyCode": "INR",
                "units": "61",
                "nanos": 925900000
              },
              "units": 0.8334166666666667
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
                "units": "28",
                "nanos": 170566775
              },
              "investedValue": {
                "currencyCode": "INR"
              },
              "XIRR": 0,
              "absoluteReturns": {
                "currencyCode": "INR"
              },
              "unrealisedReturns": {
                "currencyCode": "INR"
              },
              "navValue": {
                "currencyCode": "INR",
                "units": "33",
                "nanos": 801300000
              },
              "units": 0.8334166666666667
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
                "units": "13",
                "nanos": 64973033
              },
              "investedValue": {
                "currencyCode": "INR"
              },
              "XIRR": 0,
              "absoluteReturns": {
                "currencyCode": "INR"
              },
              "unrealisedReturns": {
                "currencyCode": "INR"
              },
              "navValue": {
                "currencyCode": "INR",
                "units": "15",
                "nanos": 676400000
              },
              "units": 0.8334166666666667
            }
          }
        }
      }
    ]
  },
  "accountDetailsBulkResponse": {
    "accountDetailsMap": {
      "102dc53c-0398-40b3-8134-9c198d780dcf": {
        "accountDetails": {
          "fipId": "IDFCFirstBank-FIP",
          "maskedAccountNumber": "XXXXXX0439",
          "accInstrumentType": "ACC_INSTRUMENT_TYPE_RECURRING_DEPOSIT",
          "accountType": {
            "recurringDepositAccountType": "RECURRING_DEPOSIT_ACCOUNT_TYPE_RECURRING"
          },
          "fipMeta": {
            "name": "IDFC Bank",
            "displayName": "IDFC",
            "bank": "IDFC"
          }
        }
      },
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
      "47313386-570c-4cd2-9db6-ee2716bd8b65": {
        "accountDetails": {
          "fipId": "ICICI-FIP",
          "maskedAccountNumber": "XXXXXX0443",
          "accInstrumentType": "ACC_INSTRUMENT_TYPE_DEPOSIT",
          "accountType": {
            "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_SAVINGS"
          },
          "fipMeta": {
            "name": "ICICI Bank",
            "displayName": "ICICI",
            "bank": "ICICI"
          }
        }
      },
      "487bc140-b6b3-4bb6-aaab-457eeb7dab71": {
        "accountDetails": {
          "fipId": "fip@nsdl",
          "maskedAccountNumber": "XXXXXX6066",
          "accInstrumentType": "ACC_INSTRUMENT_TYPE_ETF",
          "accountType": {
            "etfAccountType": "ETF_ACCOUNT_TYPE_DEFAULT_TYPE"
          },
          "fipMeta": {
            "name": "National Securities Depository Limited",
            "displayName": "NSDL"
          }
        },
        "etfSummary": {
          "accountId": "487bc140-b6b3-4bb6-aaab-457eeb7dab71",
          "currentValue": {
            "currencyCode": "INR",
            "units": "24913",
            "nanos": 600000000
          },
          "holdingsInfo": [
            {
              "isin": "INF204KB14I2",
              "units": 115,
              "nav": {
                "currencyCode": "INR",
                "units": "216",
                "nanos": 640000000
              },
              "lastNavDate": "2023-10-06T00:00:00Z",
              "isinDescription": "NIP ETF NIFTY50 BEES"
            },
            {
              "isin": "INF204KB14I3",
              "units": 215,
              "nav": {
                "currencyCode": "INR",
                "units": "400",
                "nanos": 640000000
              },
              "lastNavDate": "2023-10-08T00:00:00Z",
              "isinDescription": "NIP ETF NIFTY30 BEES"
            }
          ]
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
      "53e9ae4e-46c8-48b5-9051-a5ff01da2411": {
        "accountDetails": {
          "fipId": "HDFC-FIP",
          "maskedAccountNumber": "XXXXXX0641",
          "accInstrumentType": "ACC_INSTRUMENT_TYPE_RECURRING_DEPOSIT",
          "accountType": {
            "recurringDepositAccountType": "RECURRING_DEPOSIT_ACCOUNT_TYPE_RECURRING"
          },
          "fipMeta": {
            "name": "HDFC Bank",
            "displayName": "HDFC",
            "bank": "HDFC"
          }
        }
      },
      "66d1faa8-563b-4af5-b738-85f46198faff": {
        "accountDetails": {
          "fipId": "IDFCFirstBank-FIP",
          "maskedAccountNumber": "XXXXXX7612",
          "accInstrumentType": "ACC_INSTRUMENT_TYPE_RECURRING_DEPOSIT",
          "accountType": {
            "recurringDepositAccountType": "RECURRING_DEPOSIT_ACCOUNT_TYPE_RECURRING"
          },
          "fipMeta": {
            "name": "IDFC Bank",
            "displayName": "IDFC",
            "bank": "IDFC"
          }
        }
      },
      "a07eb7b4-5dc3-4da3-8855-2a53b2d83d79": {
        "accountDetails": {
          "fipId": "fip@nsdl",
          "maskedAccountNumber": "XXXXXX4874",
          "accInstrumentType": "ACC_INSTRUMENT_TYPE_EQUITIES",
          "accountType": {
            "equityAccountType": "EQUITY_ACCOUNT_TYPE_DEFAULT_TYPE"
          },
          "fipMeta": {
            "name": "National Securities Depository Limited",
            "displayName": "NSDL"
          }
        },
        "equitySummary": {
          "accountId": "a07eb7b4-5dc3-4da3-8855-2a53b2d83d79",
          "currentValue": {
            "currencyCode": "INR",
            "units": "12000"
          },
          "holdingsInfo": [
            {
              "isin": "INE043B01028",
              "issuerName": "VINTRON INFORMATICS LIMITED",
              "type": "EQUITY_HOLDING_TYPE_DEMAT",
              "units": 12,
              "lastTradedPrice": {
                "currencyCode": "INR",
                "units": "5",
                "nanos": 850000000
              },
              "isinDescription": "VINTRON INFORM-EQ1/-"
            },
            {
              "isin": "INE916P01025",
              "issuerName": "TRIVENI-EQ FV 1",
              "type": "EQUITY_HOLDING_TYPE_DEMAT",
              "units": 24,
              "lastTradedPrice": {
                "currencyCode": "INR",
                "units": "13"
              },
              "isinDescription": "TRIVENI-EQ FV 1"
            },
            {
              "isin": "INE040A01034",
              "issuerName": "HDFC BANK LIMITED",
              "type": "EQUITY_HOLDING_TYPE_DEMAT",
              "units": 12,
              "lastTradedPrice": {
                "currencyCode": "INR",
                "units": "1625"
              },
              "isinDescription": "HDFC BANK-EQ1/-"
            }
          ]
        }
      },
      "a5552841-d50f-4e3f-81bc-847eb8d53323": {
        "accountDetails": {
          "fipId": "fip@nsdl",
          "maskedAccountNumber": "XXXXXX1331",
          "accInstrumentType": "ACC_INSTRUMENT_TYPE_EQUITIES",
          "accountType": {
            "equityAccountType": "EQUITY_ACCOUNT_TYPE_DEFAULT_TYPE"
          },
          "fipMeta": {
            "name": "National Securities Depository Limited",
            "displayName": "NSDL"
          }
        },
        "equitySummary": {
          "accountId": "a5552841-d50f-4e3f-81bc-847eb8d53323",
          "currentValue": {
            "currencyCode": "INR",
            "units": "12000"
          },
          "holdingsInfo": [
            {
              "isin": "INE043B01028",
              "issuerName": "VINTRON INFORMATICS LIMITED",
              "type": "EQUITY_HOLDING_TYPE_DEMAT",
              "units": 12,
              "lastTradedPrice": {
                "currencyCode": "INR",
                "units": "5",
                "nanos": 850000000
              },
              "isinDescription": "VINTRON INFORM-EQ1/-"
            },
            {
              "isin": "INE916P01025",
              "issuerName": "TRIVENI-EQ FV 1",
              "type": "EQUITY_HOLDING_TYPE_DEMAT",
              "units": 24,
              "lastTradedPrice": {
                "currencyCode": "INR",
                "units": "13"
              },
              "isinDescription": "TRIVENI-EQ FV 1"
            },
            {
              "isin": "INE040A01034",
              "issuerName": "HDFC BANK LIMITED",
              "type": "EQUITY_HOLDING_TYPE_DEMAT",
              "units": 12,
              "lastTradedPrice": {
                "currencyCode": "INR",
                "units": "1625"
              },
              "isinDescription": "HDFC BANK-EQ1/-"
            }
          ]
        }
      },
      "b4ab0cb2-5a84-44f3-8e99-da8fb6a93753": {
        "accountDetails": {
          "fipId": "fip@nsdl",
          "maskedAccountNumber": "XXXXXX1864",
          "accInstrumentType": "ACC_INSTRUMENT_TYPE_REIT",
          "accountType": {
            "reitAccountType": "REIT_ACCOUNT_TYPE_DEFAULT_TYPE"
          },
          "fipMeta": {
            "name": "National Securities Depository Limited",
            "displayName": "NSDL"
          }
        },
        "reitSummary": {
          "accountId": "b4ab0cb2-5a84-44f3-8e99-da8fb6a93753",
          "currentValue": {
            "currencyCode": "INR",
            "units": "24913",
            "nanos": 600000000
          },
          "holdingsInfo": [
            {
              "isin": "INE0FDU25010",
              "totalNumberUnits": 115,
              "isinDescription": "BROOKFIELD INDIA REAL ESTATE TRUST",
              "nominee": "NOMINEE_TYPE_REGISTERED",
              "lastClosingRate": {
                "currencyCode": "INR",
                "units": "14",
                "nanos": 550000000
              }
            },
            {
              "isin": "INE0CCU25019",
              "totalNumberUnits": 215,
              "isinDescription": "MINDSPACE BUSINESS PARKS REIT ",
              "nominee": "NOMINEE_TYPE_REGISTERED",
              "lastClosingRate": {
                "currencyCode": "INR",
                "units": "14",
                "nanos": 550000000
              }
            }
          ]
        }
      },
      "b9377d21-932a-439c-8aa1-a9fa96231217": {
        "accountDetails": {
          "fipId": "fip@nsdl",
          "maskedAccountNumber": "XXXXXX8185",
          "accInstrumentType": "ACC_INSTRUMENT_TYPE_INVIT",
          "accountType": {
            "invitAccountType": "INVIT_ACCOUNT_TYPE_DEFAULT_TYPE"
          },
          "fipMeta": {
            "name": "National Securities Depository Limited",
            "displayName": "NSDL"
          }
        },
        "invitSummary": {
          "accountId": "b9377d21-932a-439c-8aa1-a9fa96231217",
          "currentValue": {
            "currencyCode": "INR",
            "units": "24913",
            "nanos": 600000000
          },
          "holdingsInfo": [
            {
              "isin": "INE0GGX23010",
              "totalNumberUnits": 115,
              "isinDescription": "POWERGRID INFRASTRUCTURE INVESTMENT TRUST"
            },
            {
              "isin": "INE0BWS23018",
              "totalNumberUnits": 215,
              "isinDescription": "Data Infrastructure Trust"
            }
          ]
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
      },
      "c46479bd-0bcb-4617-b660-04caa49c4907": {
        "accountDetails": {
          "fipId": "ICICI-FIP",
          "maskedAccountNumber": "XXXXXX9775",
          "accInstrumentType": "ACC_INSTRUMENT_TYPE_DEPOSIT",
          "accountType": {
            "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_CURRENT"
          },
          "fipMeta": {
            "name": "ICICI Bank",
            "displayName": "ICICI",
            "bank": "ICICI"
          }
        }
      },
      "d034b210-b527-4e2e-a871-2e06db5b2cc8": {
        "accountDetails": {
          "fipId": "ICICI-FIP",
          "maskedAccountNumber": "XXXXXX1799",
          "accInstrumentType": "ACC_INSTRUMENT_TYPE_DEPOSIT",
          "accountType": {
            "depositAccountType": "DEPOSIT_ACCOUNT_TYPE_SAVINGS"
          },
          "fipMeta": {
            "name": "ICICI Bank",
            "displayName": "ICICI",
            "bank": "ICICI"
          }
        }
      },
      "d051bf68-fa34-4222-af9b-b8a39b0a8a68": {
        "accountDetails": {
          "fipId": "ICICI-FIP",
          "maskedAccountNumber": "XXXXXX2470",
          "accInstrumentType": "ACC_INSTRUMENT_TYPE_RECURRING_DEPOSIT",
          "accountType": {
            "recurringDepositAccountType": "RECURRING_DEPOSIT_ACCOUNT_TYPE_RECURRING"
          },
          "fipMeta": {
            "name": "ICICI Bank",
            "displayName": "ICICI",
            "bank": "ICICI"
          }
        }
      }
    }
  }
}''';
  }

  // Exact sample data from fetch_credit_report.json
  String _getSampleCreditReportData() {
    return '''{
  "creditReports": [
    {
      "creditReportData": {
        "userMessage": {
          "userMessageText": "Normal Response"
        },
        "creditProfileHeader": {
          "reportDate": "20210620",
          "reportTime": "023304"
        },
        "currentApplication": {
          "currentApplicationDetails": {
            "enquiryReason": "6",
            "amountFinanced": "0",
            "durationOfAgreement": "0",
            "currentApplicantDetails": {
              "dateOfBirthApplicant": "19910202"
            }
          }
        },
        "creditAccount": {
          "creditAccountSummary": {
            "account": {
              "creditAccountTotal": "6",
              "creditAccountActive": "6",
              "creditAccountDefault": "0",
              "creditAccountClosed": "0",
              "cadSuitFiledCurrentBalance": "0"
            },
            "totalOutstandingBalance": {
              "outstandingBalanceSecured": "44000",
              "outstandingBalanceSecuredPercentage": "59",
              "outstandingBalanceUnSecured": "31000",
              "outstandingBalanceUnSecuredPercentage": "41",
              "outstandingBalanceAll": "75000"
            }
          },
          "creditAccountDetails": [
            {
              "subscriberName": "HDFC Bank",
              "portfolioType": "I",
              "accountType": "01",
              "openDate": "20060110",
              "highestCreditOrOriginalLoanAmount": "50000",
              "accountStatus": "83",
              "paymentRating": "5",
              "paymentHistoryProfile": "00??????????????????????????????????",
              "currentBalance": "5000",
              "amountPastDue": "1000",
              "dateReported": "20201228",
              "occupationCode": "S",
              "rateOfInterest": "11.5",
              "repaymentTenure": "0",
              "dateOfAddition": "20201028",
              "currencyCode": "INR",
              "accountHolderTypeCode": "1"
            },
            {
              "subscriberName": "ICICI Bank",
              "portfolioType": "I",
              "accountType": "03",
              "openDate": "20060122",
              "highestCreditOrOriginalLoanAmount": "110000",
              "accountStatus": "11",
              "paymentRating": "0",
              "paymentHistoryProfile": "44??????????????????????????????????",
              "currentBalance": "17000",
              "amountPastDue": "13000",
              "dateReported": "20201228",
              "occupationCode": "S",
              "rateOfInterest": "8.24",
              "repaymentTenure": "0",
              "dateOfAddition": "20201028",
              "currencyCode": "INR",
              "accountHolderTypeCode": "1"
            },
            {
              "subscriberName": "Aditya Brila Finance Limited",
              "portfolioType": "I",
              "accountType": "53",
              "openDate": "20060119",
              "highestCreditOrOriginalLoanAmount": "95000",
              "accountStatus": "78",
              "paymentRating": "2",
              "paymentHistoryProfile": "33??????????????????????????????????",
              "currentBalance": "14000",
              "amountPastDue": "10000",
              "dateReported": "20201228",
              "occupationCode": "N",
              "rateOfInterest": "14",
              "repaymentTenure": "0",
              "dateOfAddition": "20201028",
              "currencyCode": "INR",
              "accountHolderTypeCode": "1"
            },
            {
              "subscriberName": "Bajaj Finance",
              "portfolioType": "I",
              "accountType": "04",
              "openDate": "20060113",
              "highestCreditOrOriginalLoanAmount": "65000",
              "accountStatus": "11",
              "paymentRating": "0",
              "paymentHistoryProfile": "11??????????????????????????????????",
              "currentBalance": "8000",
              "amountPastDue": "0",
              "dateReported": "20201228",
              "occupationCode": "N",
              "repaymentTenure": "0",
              "dateOfAddition": "20201028",
              "currencyCode": "INR",
              "accountHolderTypeCode": "1"
            },
            {
              "subscriberName": "Epifi Capital",
              "portfolioType": "R",
              "accountType": "10",
              "openDate": "20060116",
              "creditLimitAmount": "500000",
              "highestCreditOrOriginalLoanAmount": "80000",
              "accountStatus": "82",
              "paymentRating": "4",
              "paymentHistoryProfile": "22??????????????????????????????????",
              "currentBalance": "11000",
              "amountPastDue": "7000",
              "dateReported": "20201228",
              "occupationCode": "N",
              "repaymentTenure": "0",
              "dateOfAddition": "20201028",
              "currencyCode": "INR",
              "accountHolderTypeCode": "1"
            },
            {
              "subscriberName": "Mannapuram Finance",
              "portfolioType": "I",
              "accountType": "06",
              "openDate": "20060125",
              "highestCreditOrOriginalLoanAmount": "125000",
              "accountStatus": "71",
              "paymentRating": "1",
              "paymentHistoryProfile": "55??????????????????????????????????",
              "currentBalance": "20000",
              "amountPastDue": "16000",
              "dateReported": "20201228",
              "occupationCode": "N",
              "repaymentTenure": "0",
              "dateOfAddition": "20201028",
              "currencyCode": "INR",
              "accountHolderTypeCode": "1"
            }
          ]
        },
        "matchResult": {
          "exactMatch": "Y"
        },
        "totalCapsSummary": {
          "totalCapsLast7Days": "0",
          "totalCapsLast30Days": "0",
          "totalCapsLast90Days": "0",
          "totalCapsLast180Days": "0"
        },
        "nonCreditCaps": {
          "nonCreditCapsSummary": {
            "nonCreditCapsLast7Days": "4",
            "nonCreditCapsLast30Days": "4",
            "nonCreditCapsLast90Days": "4",
            "nonCreditCapsLast180Days": "4"
          },
          "capsApplicationDetailsArray": [
            {
              "SubscriberName": "Bajaj finance",
              "FinancePurpose": "10",
              "capsApplicantDetails": {},
              "capsOtherDetails": {},
              "capsApplicantAddressDetails": {},
              "capsApplicantAdditionalAddressDetails": {}
            },
            {
              "SubscriberName": "Muthoot finance",
              "FinancePurpose": "2",
              "capsApplicantDetails": {},
              "capsOtherDetails": {},
              "capsApplicantAddressDetails": {},
              "capsApplicantAdditionalAddressDetails": {}
            },
            {
              "SubscriberName": "HDFC",
              "FinancePurpose": "8",
              "capsApplicantDetails": {},
              "capsOtherDetails": {},
              "capsApplicantAddressDetails": {},
              "capsApplicantAdditionalAddressDetails": {}
            },
            {
              "SubscriberName": "SBI",
              "FinancePurpose": "1",
              "capsApplicantDetails": {},
              "capsOtherDetails": {},
              "capsApplicantAddressDetails": {},
              "capsApplicantAdditionalAddressDetails": {}
            }
          ]
        },
        "score": {
          "bureauScore": "746",
          "bureauScoreConfidenceLevel": "H"
        },
        "segment": {},
        "caps": {
          "capsSummary": {
            "capsLast7Days": "4",
            "capsLast30Days": "4",
            "capsLast90Days": "4",
            "capsLast180Days": "4"
          },
          "capsApplicationDetailsArray": [
            {
              "SubscriberName": "Bajaj finance",
              "DateOfRequest": "20250625",
              "EnquiryReason": "10",
              "FinancePurpose": "10"
            },
            {
              "SubscriberName": "Muthoot finance",
              "DateOfRequest": "20250625",
              "EnquiryReason": "2",
              "FinancePurpose": "2"
            },
            {
              "SubscriberName": "HDFC",
              "DateOfRequest": "20250625",
              "EnquiryReason": "8",
              "FinancePurpose": "8"
            },
            {
              "SubscriberName": "SBI",
              "DateOfRequest": "20250625",
              "EnquiryReason": "1",
              "FinancePurpose": "1"
            }
          ]
        }
      },
      "vendor": "EXPERIAN"
    }
  ]
}''';
  }

  // Exact sample data from fetch_epf_details.json
  String _getSampleEpfDetailsData() {
    return '''{
  "uanAccounts": [
    {
      "phoneNumber": {},
      "rawDetails": {
        "est_details": [
          {
            "est_name": "KARZA TECHNOLOGIES PRIVATE LIMITED",
            "member_id": "MHBANXXXXXXXXXXXXXXXXX",
            "office": "(RO)BANDRA(MUMBAI-I)",
            "doj_epf": "24-03-2021",
            "doe_epf": "02-01-2022",
            "doe_eps": "02-01-2022",
            "pf_balance": {
              "net_balance": "200000",
              "employee_share": {
                "credit": "100000",
                "balance": "100000"
              },
              "employer_share": {
                "credit": "100000",
                "balance": "100000"
              }
            }
          },
          {
            "est_name": "TSS CONSULTANCY PRIVATE LIMITED",
            "member_id": "MHBAN*****************",
            "office": "(RO)BANDRA(MUMBAI-I)",
            "doj_epf": "07-08-2018",
            "doe_epf": "02-01-2022",
            "doe_eps": "02-01-2022",
            "pf_balance": {
              "net_balance": "11111",
              "employee_share": {
                "credit": "5000"
              },
              "employer_share": {
                "credit": "5000"
              }
            }
          }
        ],
        "overall_pf_balance": {
          "pension_balance": "1000000",
          "current_pf_balance": "211111",
          "employee_share_total": {
            "credit": "1111",
            "balance": "11111"
          }
        }
      }
    }
  ]
}''';
  }

  // Exact sample data from fetch_mf_transactions.json
  String _getSampleMfTransactionsData() {
    return '''{
  "transactions": [
    {
      "isinNumber": "INF760K01FC4",
      "folioId": "55557777",
      "externalOrderType": "BUY",
      "transactionDate": "2022-12-31T18:30:00Z",
      "purchasePrice": {
        "currencyCode": "INR",
        "units": "66",
        "nanos": 554600000
      },
      "transactionAmount": {
        "currencyCode": "INR",
        "units": "6655",
        "nanos": 460000000
      },
      "transactionUnits": 100,
      "transactionMode": "N",
      "schemeName": "Canara Robeco Gilt Fund - Regular Plan"
    },
    {
      "isinNumber": "INF789FB1S71",
      "folioId": "7777711111",
      "externalOrderType": "BUY",
      "transactionDate": "2022-05-14T18:30:00Z",
      "purchasePrice": {
        "currencyCode": "INR",
        "units": "2923",
        "nanos": 506800000
      },
      "transactionAmount": {
        "currencyCode": "INR",
        "units": "29235",
        "nanos": 68000000
      },
      "transactionUnits": 10,
      "transactionMode": "N",
      "schemeName": "UTI Overnight - Direct Plan"
    },
    {
      "isinNumber": "INF109K012B0",
      "folioId": "222221111",
      "externalOrderType": "BUY",
      "transactionDate": "2022-05-10T18:30:00Z",
      "purchasePrice": {
        "currencyCode": "INR",
        "units": "52",
        "nanos": 720000000
      },
      "transactionAmount": {
        "currencyCode": "INR",
        "units": "2636"
      },
      "transactionUnits": 50,
      "transactionMode": "N",
      "schemeName": "ICICI Prudential Balanced Advantage - Direct Plan"
    },
    {
      "isinNumber": "INF109K012M7",
      "folioId": "1234567",
      "externalOrderType": "BUY",
      "transactionDate": "2022-03-08T18:30:00Z",
      "purchasePrice": {
        "currencyCode": "INR",
        "units": "165",
        "nanos": 718700000
      },
      "transactionAmount": {
        "currencyCode": "INR",
        "units": "10027"
      },
      "transactionUnits": 60.5063,
      "transactionMode": "N",
      "schemeName": "ICICI Prudential Nifty 50 Index Fund - Direct Plan Growth "
    }
  ]
}''';
  }
}