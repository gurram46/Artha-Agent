import 'dart:math' as math;
import 'package:intl/intl.dart';
import '../models/currency.dart';

/// Utility class for formatting financial data
class DataFormatters {
  
  /// Formats currency values with Indian number system
  static String formatCurrency(double amount, {bool compact = false, bool showSymbol = true}) {
    final symbol = showSymbol ? '₹' : '';
    
    if (compact) {
      return formatCompactCurrency(amount, showSymbol: showSymbol);
    }
    
    // Use Indian number formatting
    final formatter = NumberFormat.currency(
      locale: 'en_IN',
      symbol: symbol,
      decimalDigits: amount % 1 == 0 ? 0 : 2,
    );
    
    return formatter.format(amount);
  }

  /// Formats currency in compact form (1.2L, 1.2Cr, etc.)
  static String formatCompactCurrency(double amount, {bool showSymbol = true}) {
    final symbol = showSymbol ? '₹' : '';
    final absAmount = amount.abs();
    final sign = amount < 0 ? '-' : '';
    
    if (absAmount >= 10000000) {
      return '$sign$symbol${(absAmount / 10000000).toStringAsFixed(1)}Cr';
    } else if (absAmount >= 100000) {
      return '$sign$symbol${(absAmount / 100000).toStringAsFixed(1)}L';
    } else if (absAmount >= 1000) {
      return '$sign$symbol${(absAmount / 1000).toStringAsFixed(1)}K';
    } else {
      return '$sign$symbol${absAmount.toStringAsFixed(0)}';
    }
  }

  /// Formats percentage values
  static String formatPercentage(double percentage, {int decimalPlaces = 2, bool showSign = true}) {
    final sign = showSign && percentage > 0 ? '+' : '';
    return '$sign${percentage.toStringAsFixed(decimalPlaces)}%';
  }

  /// Formats date in Indian format (DD/MM/YYYY)
  static String formatDate(DateTime date) {
    return DateFormat('dd/MM/yyyy').format(date);
  }

  /// Formats date with time
  static String formatDateTime(DateTime date) {
    return DateFormat('dd/MM/yyyy HH:mm').format(date);
  }

  /// Formats date in readable format (1 Jan 2024)
  static String formatReadableDate(DateTime date) {
    return DateFormat('d MMM yyyy').format(date);
  }

  /// Formats relative time (1 day ago, 2 weeks ago, etc.)
  static String formatRelativeTime(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);
    
    if (difference.inDays == 0) {
      if (difference.inHours == 0) {
        return 'Just now';
      } else if (difference.inHours == 1) {
        return '1 hour ago';
      } else {
        return '${difference.inHours} hours ago';
      }
    } else if (difference.inDays == 1) {
      return 'Yesterday';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} days ago';
    } else if (difference.inDays < 30) {
      final weeks = (difference.inDays / 7).floor();
      return weeks == 1 ? '1 week ago' : '$weeks weeks ago';
    } else if (difference.inDays < 365) {
      final months = (difference.inDays / 30).floor();
      return months == 1 ? '1 month ago' : '$months months ago';
    } else {
      final years = (difference.inDays / 365).floor();
      return years == 1 ? '1 year ago' : '$years years ago';
    }
  }

  /// Formats duration in human readable format
  static String formatDuration(Duration duration) {
    final days = duration.inDays;
    final hours = duration.inHours % 24;
    final minutes = duration.inMinutes % 60;
    
    if (days > 0) {
      return '$days days, $hours hours';
    } else if (hours > 0) {
      return '$hours hours, $minutes minutes';
    } else {
      return '$minutes minutes';
    }
  }

  /// Formats service duration in years and months
  static String formatServiceDuration(Duration duration) {
    final totalDays = duration.inDays;
    final years = totalDays ~/ 365;
    final months = (totalDays % 365) ~/ 30;
    
    if (years == 0) {
      return months == 1 ? '1 month' : '$months months';
    } else if (months == 0) {
      return years == 1 ? '1 year' : '$years years';
    } else {
      return '$years years, $months months';
    }
  }

  /// Formats units with proper decimal places
  static String formatUnits(double units, {int decimalPlaces = 3}) {
    return units.toStringAsFixed(decimalPlaces);
  }

  /// Formats NAV (Net Asset Value)
  static String formatNav(double nav) {
    return '₹${nav.toStringAsFixed(4)}';
  }

  /// Formats XIRR percentage
  static String formatXirr(double? xirr) {
    if (xirr == null) return 'N/A';
    return formatPercentage(xirr, decimalPlaces: 2);
  }

  /// Formats credit score
  static String formatCreditScore(int score) {
    return score.toString();
  }

  /// Gets credit score color based on score range
  static String getCreditScoreCategory(int score) {
    if (score >= 750) return 'Excellent';
    if (score >= 700) return 'Good';
    if (score >= 650) return 'Fair';
    if (score >= 600) return 'Poor';
    return 'Very Poor';
  }

  /// Formats account number with masking
  static String formatAccountNumber(String accountNumber) {
    if (accountNumber.length <= 4) return accountNumber;
    return accountNumber.replaceRange(0, accountNumber.length - 4, '*' * (accountNumber.length - 4));
  }

  /// Formats phone number with country code
  static String formatPhoneNumber(String phoneNumber) {
    if (phoneNumber.length == 10) {
      return '+91 $phoneNumber';
    }
    return phoneNumber;
  }

  /// Formats large numbers in Indian system
  static String formatLargeNumber(double number) {
    if (number >= 10000000) {
      return '${(number / 10000000).toStringAsFixed(1)} Crore';
    } else if (number >= 100000) {
      return '${(number / 100000).toStringAsFixed(1)} Lakh';
    } else if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)} Thousand';
    } else {
      return number.toStringAsFixed(0);
    }
  }

  /// Formats growth rate
  static String formatGrowthRate(double currentValue, double previousValue) {
    if (previousValue == 0) return 'N/A';
    final growth = ((currentValue - previousValue) / previousValue) * 100;
    return formatPercentage(growth, showSign: true);
  }

  /// Formats risk level
  static String formatRiskLevel(String riskLevel) {
    switch (riskLevel.toUpperCase()) {
      case 'LOW_RISK':
        return 'Low Risk';
      case 'MODERATE_RISK':
        return 'Moderate Risk';
      case 'HIGH_RISK':
        return 'High Risk';
      case 'VERY_HIGH_RISK':
        return 'Very High Risk';
      default:
        return riskLevel;
    }
  }

  /// Formats asset class
  static String formatAssetClass(String assetClass) {
    switch (assetClass.toUpperCase()) {
      case 'EQUITY':
        return 'Equity';
      case 'DEBT':
        return 'Debt';
      case 'HYBRID':
        return 'Hybrid';
      case 'CASH':
        return 'Cash';
      default:
        return assetClass;
    }
  }

  /// Formats plan type
  static String formatPlanType(String planType) {
    switch (planType.toUpperCase()) {
      case 'DIRECT':
        return 'Direct';
      case 'REGULAR':
        return 'Regular';
      default:
        return planType;
    }
  }

  /// Formats option type
  static String formatOptionType(String optionType) {
    switch (optionType.toUpperCase()) {
      case 'GROWTH':
        return 'Growth';
      case 'DIVIDEND':
        return 'Dividend';
      case 'DIVIDEND_REINVESTMENT':
        return 'Dividend Reinvestment';
      default:
        return optionType;
    }
  }

  /// Formats bank name
  static String formatBankName(String bankName) {
    switch (bankName.toUpperCase()) {
      case 'HDFC':
        return 'HDFC Bank';
      case 'ICICI':
        return 'ICICI Bank';
      case 'SBI':
        return 'State Bank of India';
      case 'AXIS':
        return 'Axis Bank';
      case 'KOTAK':
        return 'Kotak Mahindra Bank';
      case 'IDFC':
        return 'IDFC First Bank';
      default:
        return bankName;
    }
  }

  /// Formats account type
  static String formatAccountType(String accountType) {
    switch (accountType.toUpperCase()) {
      case 'DEPOSIT_ACCOUNT_TYPE_SAVINGS':
        return 'Savings Account';
      case 'DEPOSIT_ACCOUNT_TYPE_CURRENT':
        return 'Current Account';
      case 'DEPOSIT_ACCOUNT_TYPE_FIXED':
        return 'Fixed Deposit';
      case 'RECURRING_DEPOSIT_ACCOUNT_TYPE_RECURRING':
        return 'Recurring Deposit';
      default:
        return accountType.replaceAll('_', ' ').toLowerCase();
    }
  }

  /// Formats EMI amount
  static String formatEmi(double loanAmount, double interestRate, int tenure) {
    final monthlyRate = interestRate / (12 * 100);
    final emi = (loanAmount * monthlyRate * math.pow(1 + monthlyRate, tenure).toDouble()) / 
                (math.pow(1 + monthlyRate, tenure).toDouble() - 1);
    return formatCurrency(emi, compact: true);
  }

  /// Formats loan tenure
  static String formatLoanTenure(int months) {
    final years = months ~/ 12;
    final remainingMonths = months % 12;
    
    if (years == 0) {
      return '$months months';
    } else if (remainingMonths == 0) {
      return '$years years';
    } else {
      return '$years years, $remainingMonths months';
    }
  }

  /// Validates and formats IFSC code
  static String formatIfscCode(String ifscCode) {
    return ifscCode.toUpperCase();
  }

  /// Formats age from date of birth
  static String formatAge(DateTime dateOfBirth) {
    final now = DateTime.now();
    int age = now.year - dateOfBirth.year;
    if (now.month < dateOfBirth.month || 
        (now.month == dateOfBirth.month && now.day < dateOfBirth.day)) {
      age--;
    }
    return '$age years';
  }

  /// Formats retirement years left
  static String formatRetirementYears(int currentAge, {int retirementAge = 60}) {
    final yearsLeft = retirementAge - currentAge;
    if (yearsLeft <= 0) {
      return 'Retired';
    } else if (yearsLeft == 1) {
      return '1 year left';
    } else {
      return '$yearsLeft years left';
    }
  }

  /// Formats investment horizon
  static String formatInvestmentHorizon(DateTime startDate, DateTime? endDate) {
    final end = endDate ?? DateTime.now();
    final duration = end.difference(startDate);
    return formatServiceDuration(duration);
  }

  /// Formats compound annual growth rate (CAGR)
  static String formatCagr(double initialValue, double finalValue, int years) {
    if (initialValue == 0 || years == 0) return 'N/A';
    final cagr = (math.pow(finalValue / initialValue, 1 / years).toDouble() - 1) * 100;
    return formatPercentage(cagr);
  }

  /// Formats mutual fund category
  static String formatMfCategory(String category) {
    switch (category.toUpperCase()) {
      case 'LARGE_CAP':
        return 'Large Cap';
      case 'MID_CAP':
        return 'Mid Cap';
      case 'SMALL_CAP':
        return 'Small Cap';
      case 'MULTI_CAP':
        return 'Multi Cap';
      case 'ELSS_TAX_SAVING':
        return 'ELSS';
      case 'INDEX_FUNDS':
        return 'Index Fund';
      case 'GOVERNMENT_BOND':
        return 'Government Bond';
      case 'CORPORATE_BOND':
        return 'Corporate Bond';
      case 'LIQUID':
        return 'Liquid Fund';
      case 'OVERNIGHT':
        return 'Overnight Fund';
      case 'DYNAMIC_ASSET_ALLOCATION':
        return 'Dynamic Asset Allocation';
      default:
        return category.replaceAll('_', ' ').toLowerCase();
    }
  }

  /// Formats transaction type
  static String formatTransactionType(String transactionType) {
    switch (transactionType.toUpperCase()) {
      case 'BUY':
        return 'Purchase';
      case 'SELL':
        return 'Redemption';
      case 'SIP':
        return 'SIP';
      case 'DIVIDEND':
        return 'Dividend';
      case 'SWITCH_IN':
        return 'Switch In';
      case 'SWITCH_OUT':
        return 'Switch Out';
      default:
        return transactionType;
    }
  }

  /// Formats file size
  static String formatFileSize(int bytes) {
    if (bytes < 1024) {
      return '$bytes B';
    } else if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(1)} KB';
    } else {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    }
  }

  /// Formats data usage
  static String formatDataUsage(int bytes) {
    return formatFileSize(bytes);
  }

  /// Formats time elapsed
  static String formatTimeElapsed(DateTime startTime) {
    final elapsed = DateTime.now().difference(startTime);
    return formatDuration(elapsed);
  }

  /// Formats loading progress
  static String formatProgress(double progress) {
    return '${(progress * 100).toStringAsFixed(0)}%';
  }

  /// Formats API response time
  static String formatResponseTime(Duration responseTime) {
    if (responseTime.inMilliseconds < 1000) {
      return '${responseTime.inMilliseconds}ms';
    } else {
      return '${(responseTime.inMilliseconds / 1000).toStringAsFixed(1)}s';
    }
  }

  /// Formats error messages
  static String formatErrorMessage(String error) {
    // Clean up technical error messages for user display
    return error
        .replaceAll('Exception:', '')
        .replaceAll('Error:', '')
        .replaceAll('_', ' ')
        .trim();
  }

  /// Formats asset allocation percentage
  static String formatAllocationPercentage(double amount, double total) {
    if (total == 0) return '0%';
    final percentage = (amount / total) * 100;
    return '${percentage.toStringAsFixed(1)}%';
  }

  /// Formats portfolio value change
  static String formatPortfolioChange(double currentValue, double previousValue) {
    final change = currentValue - previousValue;
    final changePercentage = previousValue != 0 ? (change / previousValue) * 100 : 0;
    
    final sign = change >= 0 ? '+' : '';
    final formattedChange = formatCompactCurrency(change.abs());
    final formattedPercentage = formatPercentage(changePercentage.abs().toDouble());
    
    return '$sign$formattedChange ($formattedPercentage)';
  }

  /// Formats currency from Currency object
  static String formatCurrencyFromObject(Currency currency, {bool compact = false}) {
    return formatCurrency(currency.value, compact: compact);
  }

  /// Formats net worth breakdown
  static String formatNetWorthBreakdown(double assets, double liabilities) {
    final netWorth = assets - liabilities;
    return 'Assets: ${formatCompactCurrency(assets)} | Liabilities: ${formatCompactCurrency(liabilities)} | Net Worth: ${formatCompactCurrency(netWorth)}';
  }
}