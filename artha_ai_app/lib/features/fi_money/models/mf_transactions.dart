import 'dart:math' as math;
import 'currency.dart';

class MfTransactionsResponse {
  final List<MfTransaction> transactions;

  MfTransactionsResponse({
    required this.transactions,
  });

  factory MfTransactionsResponse.fromJson(Map<String, dynamic> json) {
    return MfTransactionsResponse(
      transactions: (json['transactions'] as List<dynamic>?)
          ?.map((e) => MfTransaction.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'transactions': transactions.map((e) => e.toJson()).toList(),
    };
  }

  /// Groups transactions by scheme (ISIN)
  Map<String, List<MfTransaction>> get transactionsByScheme {
    final Map<String, List<MfTransaction>> grouped = {};
    for (final transaction in transactions) {
      if (!grouped.containsKey(transaction.isinNumber)) {
        grouped[transaction.isinNumber] = [];
      }
      grouped[transaction.isinNumber]!.add(transaction);
    }
    return grouped;
  }

  /// Gets transactions for a specific scheme
  List<MfTransaction> getTransactionsForScheme(String isinNumber) {
    return transactions.where((t) => t.isinNumber == isinNumber).toList();
  }

  /// Gets all unique schemes
  List<String> get uniqueSchemes {
    return transactions.map((t) => t.isinNumber).toSet().toList();
  }

  /// Gets total invested amount across all schemes
  double get totalInvestedAmount {
    return transactions
        .where((t) => t.isBuy)
        .fold(0.0, (sum, t) => sum + t.transactionAmount.value);
  }

  /// Gets total redeemed amount across all schemes
  double get totalRedeemedAmount {
    return transactions
        .where((t) => t.isSell)
        .fold(0.0, (sum, t) => sum + t.transactionAmount.value);
  }

  /// Gets net invested amount (invested - redeemed)
  double get netInvestedAmount {
    return totalInvestedAmount - totalRedeemedAmount;
  }

  /// Gets most recent transaction date
  DateTime? get lastTransactionDate {
    if (transactions.isEmpty) return null;
    return transactions
        .map((t) => t.transactionDate)
        .reduce((a, b) => a.isAfter(b) ? a : b);
  }

  /// Gets oldest transaction date
  DateTime? get firstTransactionDate {
    if (transactions.isEmpty) return null;
    return transactions
        .map((t) => t.transactionDate)
        .reduce((a, b) => a.isBefore(b) ? a : b);
  }

  /// Gets transaction count by type
  Map<String, int> get transactionCountByType {
    final Map<String, int> counts = {};
    for (final transaction in transactions) {
      counts[transaction.externalOrderType] = 
          (counts[transaction.externalOrderType] ?? 0) + 1;
    }
    return counts;
  }

  /// Gets transactions within a date range
  List<MfTransaction> getTransactionsInDateRange(DateTime startDate, DateTime endDate) {
    return transactions
        .where((t) => t.transactionDate.isAfter(startDate) && 
                     t.transactionDate.isBefore(endDate))
        .toList();
  }

  /// Gets transactions for the last N days
  List<MfTransaction> getRecentTransactions(int days) {
    final cutoffDate = DateTime.now().subtract(Duration(days: days));
    return transactions
        .where((t) => t.transactionDate.isAfter(cutoffDate))
        .toList();
  }
}

class MfTransaction {
  final String isinNumber;
  final String folioId;
  final String externalOrderType;
  final DateTime transactionDate;
  final Currency purchasePrice;
  final Currency transactionAmount;
  final double transactionUnits;
  final String transactionMode;
  final String schemeName;
  final double? stampDuty;

  MfTransaction({
    required this.isinNumber,
    required this.folioId,
    required this.externalOrderType,
    required this.transactionDate,
    required this.purchasePrice,
    required this.transactionAmount,
    required this.transactionUnits,
    required this.transactionMode,
    required this.schemeName,
    this.stampDuty,
  });

  factory MfTransaction.fromJson(Map<String, dynamic> json) {
    return MfTransaction(
      isinNumber: json['isinNumber'] ?? '',
      folioId: json['folioId'] ?? '',
      externalOrderType: json['externalOrderType'] ?? '',
      transactionDate: DateTime.parse(json['transactionDate'] ?? DateTime.now().toIso8601String()),
      purchasePrice: Currency.fromJson(json['purchasePrice'] ?? {}),
      transactionAmount: Currency.fromJson(json['transactionAmount'] ?? {}),
      transactionUnits: (json['transactionUnits'] as num?)?.toDouble() ?? 0.0,
      transactionMode: json['transactionMode'] ?? '',
      schemeName: json['schemeName'] ?? '',
      stampDuty: (json['stampDuty'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'isinNumber': isinNumber,
      'folioId': folioId,
      'externalOrderType': externalOrderType,
      'transactionDate': transactionDate.toIso8601String(),
      'purchasePrice': purchasePrice.toJson(),
      'transactionAmount': transactionAmount.toJson(),
      'transactionUnits': transactionUnits,
      'transactionMode': transactionMode,
      'schemeName': schemeName,
      'stampDuty': stampDuty,
    };
  }

  /// Whether this is a buy transaction
  bool get isBuy => externalOrderType.toUpperCase() == 'BUY';

  /// Whether this is a sell transaction
  bool get isSell => externalOrderType.toUpperCase() == 'SELL';

  /// Whether this is a SIP transaction
  bool get isSip => transactionMode.toUpperCase() == 'SIP';

  /// Whether this is a dividend transaction
  bool get isDividend => externalOrderType.toUpperCase() == 'DIVIDEND';

  /// Transaction type display name
  String get transactionTypeName {
    switch (externalOrderType.toUpperCase()) {
      case 'BUY':
        return isSip ? 'SIP' : 'Purchase';
      case 'SELL':
        return 'Redemption';
      case 'DIVIDEND':
        return 'Dividend';
      default:
        return externalOrderType;
    }
  }

  /// Formatted transaction date
  String get formattedDate {
    return '${transactionDate.day.toString().padLeft(2, '0')}/${transactionDate.month.toString().padLeft(2, '0')}/${transactionDate.year}';
  }

  /// Formatted transaction amount
  String get formattedAmount {
    return transactionAmount.formattedCompact;
  }

  /// Formatted NAV (purchase price)
  String get formattedNav {
    return '₹${purchasePrice.value.toStringAsFixed(2)}';
  }

  /// Formatted units
  String get formattedUnits {
    return transactionUnits.toStringAsFixed(3);
  }

  /// Short scheme name (first 3 words)
  String get shortSchemeName {
    final words = schemeName.split(' ');
    if (words.length <= 3) return schemeName;
    return '${words.take(3).join(' ')}...';
  }

  /// Get the cash flow value for XIRR calculation
  /// Negative for purchases, positive for redemptions
  double get cashFlow {
    return isBuy ? -transactionAmount.value : transactionAmount.value;
  }
}

/// Utility class for calculating XIRR and other portfolio metrics
class PortfolioCalculator {
  /// Calculates XIRR for a list of transactions
  /// Returns null if calculation fails
  static double? calculateXirr(List<MfTransaction> transactions, double currentValue) {
    if (transactions.isEmpty) return null;

    // Prepare cash flows with dates
    final List<XirrCashFlow> cashFlows = [];
    
    // Add all transactions
    for (final transaction in transactions) {
      cashFlows.add(XirrCashFlow(
        date: transaction.transactionDate,
        amount: transaction.cashFlow,
      ));
    }

    // Add current value as final cash flow
    cashFlows.add(XirrCashFlow(
      date: DateTime.now(),
      amount: currentValue,
    ));

    // Sort by date
    cashFlows.sort((a, b) => a.date.compareTo(b.date));

    // Calculate XIRR using Newton-Raphson method
    return _calculateXirrNewtonRaphson(cashFlows);
  }

  /// Calculates absolute return percentage
  static double calculateAbsoluteReturn(double investedAmount, double currentValue) {
    if (investedAmount == 0) return 0.0;
    return ((currentValue - investedAmount) / investedAmount) * 100;
  }

  /// Calculates annualized return percentage
  static double calculateAnnualizedReturn(double investedAmount, double currentValue, DateTime startDate) {
    if (investedAmount == 0) return 0.0;
    
    final years = DateTime.now().difference(startDate).inDays / 365.25;
    if (years == 0) return 0.0;
    
    return (math.pow(currentValue / investedAmount, 1 / years).toDouble() - 1) * 100;
  }

  /// Private method to calculate XIRR using Newton-Raphson method
  static double? _calculateXirrNewtonRaphson(List<XirrCashFlow> cashFlows) {
    if (cashFlows.length < 2) return null;

    double guess = 0.1; // Initial guess of 10%
    const double tolerance = 1e-6;
    const int maxIterations = 100;

    for (int i = 0; i < maxIterations; i++) {
      double npv = 0;
      double dnpv = 0;
      final DateTime baseDate = cashFlows.first.date;

      for (final cashFlow in cashFlows) {
        final double years = cashFlow.date.difference(baseDate).inDays / 365.25;
        final double factor = math.pow(1 + guess, years).toDouble();
        
        npv += cashFlow.amount / factor;
        dnpv -= cashFlow.amount * years / (factor * (1 + guess));
      }

      if (npv.abs() < tolerance) {
        return guess * 100; // Convert to percentage
      }

      if (dnpv == 0) return null; // Avoid division by zero
      
      guess = guess - npv / dnpv;
      
      // Prevent unrealistic values
      if (guess < -1 || guess > 10) return null;
    }

    return null; // Did not converge
  }

  /// Calculates portfolio metrics for a scheme
  static SchemeMetrics calculateSchemeMetrics(List<MfTransaction> transactions, double currentValue) {
    final investedAmount = transactions
        .where((t) => t.isBuy)
        .fold(0.0, (sum, t) => sum + t.transactionAmount.value);
    
    final redeemedAmount = transactions
        .where((t) => t.isSell)
        .fold(0.0, (sum, t) => sum + t.transactionAmount.value);
    
    final netInvested = investedAmount - redeemedAmount;
    final absoluteReturn = calculateAbsoluteReturn(netInvested, currentValue);
    final xirr = calculateXirr(transactions, currentValue);
    
    final firstTransactionDate = transactions.isNotEmpty
        ? transactions.map((t) => t.transactionDate).reduce((a, b) => a.isBefore(b) ? a : b)
        : DateTime.now();
    
    final annualizedReturn = calculateAnnualizedReturn(netInvested, currentValue, firstTransactionDate);

    return SchemeMetrics(
      investedAmount: investedAmount,
      redeemedAmount: redeemedAmount,
      netInvested: netInvested,
      currentValue: currentValue,
      absoluteReturn: absoluteReturn,
      annualizedReturn: annualizedReturn,
      xirr: xirr,
      firstTransactionDate: firstTransactionDate,
      transactionCount: transactions.length,
    );
  }
}

/// Cash flow for XIRR calculation
class XirrCashFlow {
  final DateTime date;
  final double amount;

  XirrCashFlow({
    required this.date,
    required this.amount,
  });
}

/// Portfolio metrics for a scheme
class SchemeMetrics {
  final double investedAmount;
  final double redeemedAmount;
  final double netInvested;
  final double currentValue;
  final double absoluteReturn;
  final double annualizedReturn;
  final double? xirr;
  final DateTime firstTransactionDate;
  final int transactionCount;

  SchemeMetrics({
    required this.investedAmount,
    required this.redeemedAmount,
    required this.netInvested,
    required this.currentValue,
    required this.absoluteReturn,
    required this.annualizedReturn,
    required this.xirr,
    required this.firstTransactionDate,
    required this.transactionCount,
  });

  /// Absolute gains/losses
  double get absoluteGains => currentValue - netInvested;

  /// Whether the investment is profitable
  bool get isProfitable => absoluteGains > 0;

  /// Investment duration in days
  int get investmentDurationDays => DateTime.now().difference(firstTransactionDate).inDays;

  /// Investment duration in years
  double get investmentDurationYears => investmentDurationDays / 365.25;

  /// Formatted return percentage
  String get formattedAbsoluteReturn {
    return '${absoluteReturn >= 0 ? '+' : ''}${absoluteReturn.toStringAsFixed(2)}%';
  }

  /// Formatted XIRR
  String get formattedXirr {
    if (xirr == null) return 'N/A';
    return '${xirr! >= 0 ? '+' : ''}${xirr!.toStringAsFixed(2)}%';
  }

  /// Formatted gains
  String get formattedGains {
    final gains = absoluteGains;
    if (gains >= 10000000) {
      return '${gains >= 0 ? '+' : ''}₹${(gains / 10000000).toStringAsFixed(1)}Cr';
    } else if (gains >= 100000) {
      return '${gains >= 0 ? '+' : ''}₹${(gains / 100000).toStringAsFixed(1)}L';
    } else if (gains >= 1000) {
      return '${gains >= 0 ? '+' : ''}₹${(gains / 1000).toStringAsFixed(1)}K';
    } else {
      return '${gains >= 0 ? '+' : ''}₹${gains.toStringAsFixed(0)}';
    }
  }
}

