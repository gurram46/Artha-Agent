import 'currency.dart';

class NetWorthResponse {
  final Currency totalNetWorthValue;
  final List<AssetValue> assetValues;
  final List<LiabilityValue> liabilityValues;

  NetWorthResponse({
    required this.totalNetWorthValue,
    required this.assetValues,
    required this.liabilityValues,
  });

  factory NetWorthResponse.fromJson(Map<String, dynamic> json) {
    return NetWorthResponse(
      totalNetWorthValue: Currency.fromJson(json['totalNetWorthValue'] ?? {}),
      assetValues: (json['assetValues'] as List<dynamic>?)
          ?.map((e) => AssetValue.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
      liabilityValues: (json['liabilityValues'] as List<dynamic>?)
          ?.map((e) => LiabilityValue.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'totalNetWorthValue': totalNetWorthValue.toJson(),
      'assetValues': assetValues.map((e) => e.toJson()).toList(),
      'liabilityValues': liabilityValues.map((e) => e.toJson()).toList(),
    };
  }

  double get totalAssets => assetValues.fold(0, (sum, asset) => sum + asset.value.value);
  double get totalLiabilities => liabilityValues.fold(0, (sum, liability) => sum + liability.value.value);
}

class AssetValue {
  final String netWorthAttribute;
  final Currency value;

  AssetValue({
    required this.netWorthAttribute,
    required this.value,
  });

  factory AssetValue.fromJson(Map<String, dynamic> json) {
    return AssetValue(
      netWorthAttribute: json['netWorthAttribute'] ?? '',
      value: Currency.fromJson(json['value'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'netWorthAttribute': netWorthAttribute,
      'value': value.toJson(),
    };
  }

  String get displayName {
    switch (netWorthAttribute) {
      case 'ASSET_TYPE_MUTUAL_FUND':
        return 'Mutual Funds';
      case 'ASSET_TYPE_EPF':
        return 'EPF';
      case 'ASSET_TYPE_INDIAN_SECURITIES':
        return 'Indian Stocks';
      case 'ASSET_TYPE_SAVINGS_ACCOUNTS':
        return 'Savings Accounts';
      case 'ASSET_TYPE_US_SECURITIES':
        return 'US Stocks';
      default:
        return netWorthAttribute;
    }
  }
}

class LiabilityValue {
  final String netWorthAttribute;
  final Currency value;

  LiabilityValue({
    required this.netWorthAttribute,
    required this.value,
  });

  factory LiabilityValue.fromJson(Map<String, dynamic> json) {
    return LiabilityValue(
      netWorthAttribute: json['netWorthAttribute'] ?? '',
      value: Currency.fromJson(json['value'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'netWorthAttribute': netWorthAttribute,
      'value': value.toJson(),
    };
  }

  String get displayName {
    switch (netWorthAttribute) {
      case 'LIABILITY_TYPE_HOME_LOAN':
        return 'Home Loan';
      case 'LIABILITY_TYPE_VEHICLE_LOAN':
        return 'Vehicle Loan';
      case 'LIABILITY_TYPE_OTHER_LOAN':
        return 'Other Loans';
      case 'LIABILITY_TYPE_CREDIT_CARD':
        return 'Credit Card';
      default:
        return netWorthAttribute;
    }
  }
}

class MutualFundSchemeAnalytics {
  final SchemeDetail schemeDetail;
  final EnrichedAnalytics enrichedAnalytics;

  MutualFundSchemeAnalytics({
    required this.schemeDetail,
    required this.enrichedAnalytics,
  });

  factory MutualFundSchemeAnalytics.fromJson(Map<String, dynamic> json) {
    return MutualFundSchemeAnalytics(
      schemeDetail: SchemeDetail.fromJson(json['schemeDetail'] ?? {}),
      enrichedAnalytics: EnrichedAnalytics.fromJson(json['enrichedAnalytics'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'schemeDetail': schemeDetail.toJson(),
      'enrichedAnalytics': enrichedAnalytics.toJson(),
    };
  }
}

class SchemeDetail {
  final String amc;
  final NameData nameData;
  final String planType;
  final String investmentType;
  final String optionType;
  final Currency nav;
  final String assetClass;
  final String isinNumber;
  final String categoryName;
  final String fundhouseDefinedRiskLevel;

  SchemeDetail({
    required this.amc,
    required this.nameData,
    required this.planType,
    required this.investmentType,
    required this.optionType,
    required this.nav,
    required this.assetClass,
    required this.isinNumber,
    required this.categoryName,
    required this.fundhouseDefinedRiskLevel,
  });

  factory SchemeDetail.fromJson(Map<String, dynamic> json) {
    return SchemeDetail(
      amc: json['amc'] ?? '',
      nameData: NameData.fromJson(json['nameData'] ?? {}),
      planType: json['planType'] ?? '',
      investmentType: json['investmentType'] ?? '',
      optionType: json['optionType'] ?? '',
      nav: Currency.fromJson(json['nav'] ?? {}),
      assetClass: json['assetClass'] ?? '',
      isinNumber: json['isinNumber'] ?? '',
      categoryName: json['categoryName'] ?? '',
      fundhouseDefinedRiskLevel: json['fundhouseDefinedRiskLevel'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'amc': amc,
      'nameData': nameData.toJson(),
      'planType': planType,
      'investmentType': investmentType,
      'optionType': optionType,
      'nav': nav.toJson(),
      'assetClass': assetClass,
      'isinNumber': isinNumber,
      'categoryName': categoryName,
      'fundhouseDefinedRiskLevel': fundhouseDefinedRiskLevel,
    };
  }

  String get riskLevel {
    switch (fundhouseDefinedRiskLevel) {
      case 'LOW_RISK':
        return 'Low Risk';
      case 'MODERATE_RISK':
        return 'Moderate Risk';
      case 'HIGH_RISK':
        return 'High Risk';
      case 'VERY_HIGH_RISK':
        return 'Very High Risk';
      default:
        return fundhouseDefinedRiskLevel;
    }
  }
}

class NameData {
  final String longName;

  NameData({
    required this.longName,
  });

  factory NameData.fromJson(Map<String, dynamic> json) {
    return NameData(
      longName: json['longName'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'longName': longName,
    };
  }
}

class EnrichedAnalytics {
  final Analytics analytics;

  EnrichedAnalytics({
    required this.analytics,
  });

  factory EnrichedAnalytics.fromJson(Map<String, dynamic> json) {
    return EnrichedAnalytics(
      analytics: Analytics.fromJson(json['analytics'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'analytics': analytics.toJson(),
    };
  }
}

class Analytics {
  final SchemeDetails schemeDetails;

  Analytics({
    required this.schemeDetails,
  });

  factory Analytics.fromJson(Map<String, dynamic> json) {
    return Analytics(
      schemeDetails: SchemeDetails.fromJson(json['schemeDetails'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'schemeDetails': schemeDetails.toJson(),
    };
  }
}

class SchemeDetails {
  final Currency currentValue;
  final Currency investedValue;
  final double xirr;
  final Currency absoluteReturns;
  final Currency unrealisedReturns;
  final Currency navValue;
  final double units;

  SchemeDetails({
    required this.currentValue,
    required this.investedValue,
    required this.xirr,
    required this.absoluteReturns,
    required this.unrealisedReturns,
    required this.navValue,
    required this.units,
  });

  factory SchemeDetails.fromJson(Map<String, dynamic> json) {
    return SchemeDetails(
      currentValue: Currency.fromJson(json['currentValue'] ?? {}),
      investedValue: Currency.fromJson(json['investedValue'] ?? {}),
      xirr: (json['XIRR'] as num?)?.toDouble() ?? 0.0,
      absoluteReturns: Currency.fromJson(json['absoluteReturns'] ?? {}),
      unrealisedReturns: Currency.fromJson(json['unrealisedReturns'] ?? {}),
      navValue: Currency.fromJson(json['navValue'] ?? {}),
      units: (json['units'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'currentValue': currentValue.toJson(),
      'investedValue': investedValue.toJson(),
      'XIRR': xirr,
      'absoluteReturns': absoluteReturns.toJson(),
      'unrealisedReturns': unrealisedReturns.toJson(),
      'navValue': navValue.toJson(),
      'units': units,
    };
  }

  double get returnsPercentage {
    if (investedValue.value == 0) return 0.0;
    return (absoluteReturns.value / investedValue.value) * 100;
  }

  bool get isProfitable => absoluteReturns.value > 0;
}

class FullNetWorthData {
  final NetWorthResponse netWorthResponse;
  final List<MutualFundSchemeAnalytics> mfSchemeAnalytics;
  final AccountDetailsBulkResponse accountDetailsBulkResponse;

  FullNetWorthData({
    required this.netWorthResponse,
    required this.mfSchemeAnalytics,
    required this.accountDetailsBulkResponse,
  });

  factory FullNetWorthData.fromJson(Map<String, dynamic> json) {
    return FullNetWorthData(
      netWorthResponse: NetWorthResponse.fromJson(json['netWorthResponse'] ?? {}),
      mfSchemeAnalytics: (json['mfSchemeAnalytics']?['schemeAnalytics'] as List<dynamic>?)
          ?.map((e) => MutualFundSchemeAnalytics.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
      accountDetailsBulkResponse: AccountDetailsBulkResponse.fromJson(
        json['accountDetailsBulkResponse'] ?? {}
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'netWorthResponse': netWorthResponse.toJson(),
      'mfSchemeAnalytics': {
        'schemeAnalytics': mfSchemeAnalytics.map((e) => e.toJson()).toList(),
      },
      'accountDetailsBulkResponse': accountDetailsBulkResponse.toJson(),
    };
  }
}

class AccountDetailsBulkResponse {
  final Map<String, AccountDetail> accountDetailsMap;

  AccountDetailsBulkResponse({
    required this.accountDetailsMap,
  });

  factory AccountDetailsBulkResponse.fromJson(Map<String, dynamic> json) {
    final Map<String, AccountDetail> accountsMap = {};
    final accountDetailsMap = json['accountDetailsMap'] as Map<String, dynamic>?;
    
    if (accountDetailsMap != null) {
      accountDetailsMap.forEach((key, value) {
        accountsMap[key] = AccountDetail.fromJson(value as Map<String, dynamic>);
      });
    }
    
    return AccountDetailsBulkResponse(
      accountDetailsMap: accountsMap,
    );
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> accountDetailsMap = {};
    accountDetailsMap.forEach((key, value) {
      accountDetailsMap[key] = value.toJson();
    });
    return {
      'accountDetailsMap': accountDetailsMap,
    };
  }

  List<AccountDetail> get savingsAccounts => accountDetailsMap.values
      .where((account) => account.accountDetails.accountType?.depositAccountType == 'DEPOSIT_ACCOUNT_TYPE_SAVINGS')
      .toList();

  List<AccountDetail> get currentAccounts => accountDetailsMap.values
      .where((account) => account.accountDetails.accountType?.depositAccountType == 'DEPOSIT_ACCOUNT_TYPE_CURRENT')
      .toList();
}

class AccountDetail {
  final AccountDetails accountDetails;
  final DepositSummary? depositSummary;
  final EquitySummary? equitySummary;

  AccountDetail({
    required this.accountDetails,
    this.depositSummary,
    this.equitySummary,
  });

  factory AccountDetail.fromJson(Map<String, dynamic> json) {
    return AccountDetail(
      accountDetails: AccountDetails.fromJson(json['accountDetails'] ?? {}),
      depositSummary: json['depositSummary'] != null 
          ? DepositSummary.fromJson(json['depositSummary'] as Map<String, dynamic>)
          : null,
      equitySummary: json['equitySummary'] != null
          ? EquitySummary.fromJson(json['equitySummary'] as Map<String, dynamic>)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'accountDetails': accountDetails.toJson(),
      'depositSummary': depositSummary?.toJson(),
      'equitySummary': equitySummary?.toJson(),
    };
  }
}

class AccountDetails {
  final String fipId;
  final String maskedAccountNumber;
  final String accInstrumentType;
  final String? ifscCode;
  final AccountType? accountType;
  final FipMeta fipMeta;

  AccountDetails({
    required this.fipId,
    required this.maskedAccountNumber,
    required this.accInstrumentType,
    this.ifscCode,
    this.accountType,
    required this.fipMeta,
  });

  factory AccountDetails.fromJson(Map<String, dynamic> json) {
    return AccountDetails(
      fipId: json['fipId'] ?? '',
      maskedAccountNumber: json['maskedAccountNumber'] ?? '',
      accInstrumentType: json['accInstrumentType'] ?? '',
      ifscCode: json['ifscCode'],
      accountType: json['accountType'] != null
          ? AccountType.fromJson(json['accountType'] as Map<String, dynamic>)
          : null,
      fipMeta: FipMeta.fromJson(json['fipMeta'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'fipId': fipId,
      'maskedAccountNumber': maskedAccountNumber,
      'accInstrumentType': accInstrumentType,
      'ifscCode': ifscCode,
      'accountType': accountType?.toJson(),
      'fipMeta': fipMeta.toJson(),
    };
  }
}

class AccountType {
  final String? depositAccountType;
  final String? recurringDepositAccountType;
  final String? equityAccountType;

  AccountType({
    this.depositAccountType,
    this.recurringDepositAccountType,
    this.equityAccountType,
  });

  factory AccountType.fromJson(Map<String, dynamic> json) {
    return AccountType(
      depositAccountType: json['depositAccountType'],
      recurringDepositAccountType: json['recurringDepositAccountType'],
      equityAccountType: json['equityAccountType'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'depositAccountType': depositAccountType,
      'recurringDepositAccountType': recurringDepositAccountType,
      'equityAccountType': equityAccountType,
    };
  }
}

class FipMeta {
  final String name;
  final String displayName;
  final String? bank;

  FipMeta({
    required this.name,
    required this.displayName,
    this.bank,
  });

  factory FipMeta.fromJson(Map<String, dynamic> json) {
    return FipMeta(
      name: json['name'] ?? '',
      displayName: json['displayName'] ?? '',
      bank: json['bank'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'displayName': displayName,
      'bank': bank,
    };
  }
}

class DepositSummary {
  final String accountId;
  final Currency currentBalance;
  final DateTime balanceDate;
  final String depositAccountType;
  final String branch;
  final String ifscCode;
  final DateTime openingDate;
  final String depositAccountStatus;

  DepositSummary({
    required this.accountId,
    required this.currentBalance,
    required this.balanceDate,
    required this.depositAccountType,
    required this.branch,
    required this.ifscCode,
    required this.openingDate,
    required this.depositAccountStatus,
  });

  factory DepositSummary.fromJson(Map<String, dynamic> json) {
    return DepositSummary(
      accountId: json['accountId'] ?? '',
      currentBalance: Currency.fromJson(json['currentBalance'] ?? {}),
      balanceDate: DateTime.parse(json['balanceDate'] ?? DateTime.now().toIso8601String()),
      depositAccountType: json['depositAccountType'] ?? '',
      branch: json['branch'] ?? '',
      ifscCode: json['ifscCode'] ?? '',
      openingDate: DateTime.parse(json['openingDate'] ?? DateTime.now().toIso8601String()),
      depositAccountStatus: json['depositAccountStatus'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'accountId': accountId,
      'currentBalance': currentBalance.toJson(),
      'balanceDate': balanceDate.toIso8601String(),
      'depositAccountType': depositAccountType,
      'branch': branch,
      'ifscCode': ifscCode,
      'openingDate': openingDate.toIso8601String(),
      'depositAccountStatus': depositAccountStatus,
    };
  }
}

class EquitySummary {
  final String accountId;
  final Currency currentValue;
  final List<HoldingInfo> holdingsInfo;

  EquitySummary({
    required this.accountId,
    required this.currentValue,
    required this.holdingsInfo,
  });

  factory EquitySummary.fromJson(Map<String, dynamic> json) {
    return EquitySummary(
      accountId: json['accountId'] ?? '',
      currentValue: Currency.fromJson(json['currentValue'] ?? {}),
      holdingsInfo: (json['holdingsInfo'] as List<dynamic>?)
          ?.map((e) => HoldingInfo.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'accountId': accountId,
      'currentValue': currentValue.toJson(),
      'holdingsInfo': holdingsInfo.map((e) => e.toJson()).toList(),
    };
  }
}

class HoldingInfo {
  final String isin;
  final String issuerName;
  final String type;
  final double units;
  final Currency lastTradedPrice;
  final String isinDescription;

  HoldingInfo({
    required this.isin,
    required this.issuerName,
    required this.type,
    required this.units,
    required this.lastTradedPrice,
    required this.isinDescription,
  });

  factory HoldingInfo.fromJson(Map<String, dynamic> json) {
    return HoldingInfo(
      isin: json['isin'] ?? '',
      issuerName: json['issuerName'] ?? '',
      type: json['type'] ?? '',
      units: (json['units'] as num?)?.toDouble() ?? 0.0,
      lastTradedPrice: Currency.fromJson(json['lastTradedPrice'] ?? {}),
      isinDescription: json['isinDescription'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'isin': isin,
      'issuerName': issuerName,
      'type': type,
      'units': units,
      'lastTradedPrice': lastTradedPrice.toJson(),
      'isinDescription': isinDescription,
    };
  }

  double get currentValue => units * lastTradedPrice.value;
}