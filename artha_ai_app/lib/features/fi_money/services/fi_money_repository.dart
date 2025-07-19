import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'fi_money_api_service.dart';
import 'fi_money_mock_service.dart';
import '../models/net_worth.dart';
import '../models/credit_report.dart';
import '../models/epf_details.dart';
import '../models/mf_transactions.dart';

class FiMoneyRepository {
  static const String _netWorthKey = 'fi_money_net_worth';
  static const String _creditReportKey = 'fi_money_credit_report';
  static const String _epfDetailsKey = 'fi_money_epf_details';
  static const String _mfTransactionsKey = 'fi_money_mf_transactions';
  static const String _lastUpdateKey = 'fi_money_last_update';
  static const String _serviceStatusKey = 'fi_money_service_status';

  static const int _cacheExpiryHours = 24; // Cache expires after 24 hours

  final FiMoneyMockService _mockService;
  final SharedPreferences _prefs;

  static FiMoneyRepository? _instance;
  
  FiMoneyRepository._(this._mockService, this._prefs);

  static Future<FiMoneyRepository> getInstance() async {
    if (_instance == null) {
      final mockService = FiMoneyMockService();
      final prefs = await SharedPreferences.getInstance();
      _instance = FiMoneyRepository._(mockService, prefs);
    }
    return _instance!;
  }

  /// Fetches net worth data with caching
  Future<RepositoryResponse<FullNetWorthData>> getNetWorth({bool forceRefresh = false}) async {
    try {
      // Check cache first
      if (!forceRefresh && _isCacheValid()) {
        final cachedData = _getCachedNetWorth();
        if (cachedData != null) {
          return RepositoryResponse.success(cachedData, isFromCache: true);
        }
      }

      // Fetch from Mock Service
      final apiResponse = await _mockService.fetchNetWorth();
      
      if (apiResponse.isSuccess) {
        // Cache the result
        await _cacheNetWorth(apiResponse.data!);
        await _updateLastUpdateTime();
        return RepositoryResponse.success(apiResponse.data!, isFromCache: false);
      } else {
        // Try to return cached data as fallback
        final cachedData = _getCachedNetWorth();
        if (cachedData != null) {
          return RepositoryResponse.success(cachedData, isFromCache: true, hasError: true, error: apiResponse.error);
        }
        return RepositoryResponse.error(apiResponse.error!, apiResponse.statusCode);
      }
    } catch (e) {
      // Try to return cached data as fallback
      final cachedData = _getCachedNetWorth();
      if (cachedData != null) {
        return RepositoryResponse.success(cachedData, isFromCache: true, hasError: true, error: e.toString());
      }
      return RepositoryResponse.error(e.toString(), 0);
    }
  }

  /// Fetches credit report with caching
  Future<RepositoryResponse<CreditReportResponse>> getCreditReport({bool forceRefresh = false}) async {
    try {
      // Check cache first
      if (!forceRefresh && _isCacheValid()) {
        final cachedData = _getCachedCreditReport();
        if (cachedData != null) {
          return RepositoryResponse.success(cachedData, isFromCache: true);
        }
      }

      // Fetch from Mock Service
      final apiResponse = await _mockService.fetchCreditReport();
      
      if (apiResponse.isSuccess) {
        // Cache the result
        await _cacheCreditReport(apiResponse.data!);
        await _updateLastUpdateTime();
        return RepositoryResponse.success(apiResponse.data!, isFromCache: false);
      } else {
        // Try to return cached data as fallback
        final cachedData = _getCachedCreditReport();
        if (cachedData != null) {
          return RepositoryResponse.success(cachedData, isFromCache: true, hasError: true, error: apiResponse.error);
        }
        return RepositoryResponse.error(apiResponse.error!, apiResponse.statusCode);
      }
    } catch (e) {
      // Try to return cached data as fallback
      final cachedData = _getCachedCreditReport();
      if (cachedData != null) {
        return RepositoryResponse.success(cachedData, isFromCache: true, hasError: true, error: e.toString());
      }
      return RepositoryResponse.error(e.toString(), 0);
    }
  }

  /// Fetches EPF details with caching
  Future<RepositoryResponse<EpfDetailsResponse>> getEpfDetails({bool forceRefresh = false}) async {
    try {
      // Check cache first
      if (!forceRefresh && _isCacheValid()) {
        final cachedData = _getCachedEpfDetails();
        if (cachedData != null) {
          return RepositoryResponse.success(cachedData, isFromCache: true);
        }
      }

      // Fetch from Mock Service
      final apiResponse = await _mockService.fetchEpfDetails();
      
      if (apiResponse.isSuccess) {
        // Cache the result
        await _cacheEpfDetails(apiResponse.data!);
        await _updateLastUpdateTime();
        return RepositoryResponse.success(apiResponse.data!, isFromCache: false);
      } else {
        // Try to return cached data as fallback
        final cachedData = _getCachedEpfDetails();
        if (cachedData != null) {
          return RepositoryResponse.success(cachedData, isFromCache: true, hasError: true, error: apiResponse.error);
        }
        return RepositoryResponse.error(apiResponse.error!, apiResponse.statusCode);
      }
    } catch (e) {
      // Try to return cached data as fallback
      final cachedData = _getCachedEpfDetails();
      if (cachedData != null) {
        return RepositoryResponse.success(cachedData, isFromCache: true, hasError: true, error: e.toString());
      }
      return RepositoryResponse.error(e.toString(), 0);
    }
  }

  /// Fetches MF transactions with caching
  Future<RepositoryResponse<MfTransactionsResponse>> getMfTransactions({bool forceRefresh = false}) async {
    try {
      // Check cache first
      if (!forceRefresh && _isCacheValid()) {
        final cachedData = _getCachedMfTransactions();
        if (cachedData != null) {
          return RepositoryResponse.success(cachedData, isFromCache: true);
        }
      }

      // Fetch from Mock Service
      final apiResponse = await _mockService.fetchMfTransactions();
      
      if (apiResponse.isSuccess) {
        // Cache the result
        await _cacheMfTransactions(apiResponse.data!);
        await _updateLastUpdateTime();
        return RepositoryResponse.success(apiResponse.data!, isFromCache: false);
      } else {
        // Try to return cached data as fallback
        final cachedData = _getCachedMfTransactions();
        if (cachedData != null) {
          return RepositoryResponse.success(cachedData, isFromCache: true, hasError: true, error: apiResponse.error);
        }
        return RepositoryResponse.error(apiResponse.error!, apiResponse.statusCode);
      }
    } catch (e) {
      // Try to return cached data as fallback
      final cachedData = _getCachedMfTransactions();
      if (cachedData != null) {
        return RepositoryResponse.success(cachedData, isFromCache: true, hasError: true, error: e.toString());
      }
      return RepositoryResponse.error(e.toString(), 0);
    }
  }

  /// Fetches all financial data with caching
  Future<AllFinancialDataRepositoryResponse> getAllFinancialData({bool forceRefresh = false}) async {
    final List<Future> futures = [
      getNetWorth(forceRefresh: forceRefresh),
      getCreditReport(forceRefresh: forceRefresh),
      getEpfDetails(forceRefresh: forceRefresh),
      getMfTransactions(forceRefresh: forceRefresh),
    ];

    final results = await Future.wait(futures);

    final response = AllFinancialDataRepositoryResponse(
      netWorth: results[0] as RepositoryResponse<FullNetWorthData>,
      creditReport: results[1] as RepositoryResponse<CreditReportResponse>,
      epfDetails: results[2] as RepositoryResponse<EpfDetailsResponse>,
      mfTransactions: results[3] as RepositoryResponse<MfTransactionsResponse>,
    );

    // Update service status
    await _updateServiceStatus(response);

    return response;
  }

  /// Gets cached data summary
  Future<CacheStatus> getCacheStatus() async {
    final lastUpdateTime = _getLastUpdateTime();
    final isValid = _isCacheValid();
    
    return CacheStatus(
      hasNetWorth: _getCachedNetWorth() != null,
      hasCreditReport: _getCachedCreditReport() != null,
      hasEpfDetails: _getCachedEpfDetails() != null,
      hasMfTransactions: _getCachedMfTransactions() != null,
      lastUpdated: lastUpdateTime,
      isValid: isValid,
      expiresAt: lastUpdateTime?.add(Duration(hours: _cacheExpiryHours)),
    );
  }

  /// Clears all cached data
  Future<void> clearCache() async {
    await _prefs.remove(_netWorthKey);
    await _prefs.remove(_creditReportKey);
    await _prefs.remove(_epfDetailsKey);
    await _prefs.remove(_mfTransactionsKey);
    await _prefs.remove(_lastUpdateKey);
    await _prefs.remove(_serviceStatusKey);
  }

  /// Cache validation
  bool _isCacheValid() {
    final lastUpdate = _getLastUpdateTime();
    if (lastUpdate == null) return false;
    
    final now = DateTime.now();
    final cacheAge = now.difference(lastUpdate);
    return cacheAge.inHours < _cacheExpiryHours;
  }

  /// Cache operations
  Future<void> _cacheNetWorth(FullNetWorthData data) async {
    final jsonString = jsonEncode(data.toJson());
    await _prefs.setString(_netWorthKey, jsonString);
  }

  FullNetWorthData? _getCachedNetWorth() {
    final jsonString = _prefs.getString(_netWorthKey);
    if (jsonString != null) {
      try {
        final jsonData = jsonDecode(jsonString);
        return FullNetWorthData.fromJson(jsonData);
      } catch (e) {
        return null;
      }
    }
    return null;
  }

  Future<void> _cacheCreditReport(CreditReportResponse data) async {
    final jsonString = jsonEncode(data.toJson());
    await _prefs.setString(_creditReportKey, jsonString);
  }

  CreditReportResponse? _getCachedCreditReport() {
    final jsonString = _prefs.getString(_creditReportKey);
    if (jsonString != null) {
      try {
        final jsonData = jsonDecode(jsonString);
        return CreditReportResponse.fromJson(jsonData);
      } catch (e) {
        return null;
      }
    }
    return null;
  }

  Future<void> _cacheEpfDetails(EpfDetailsResponse data) async {
    final jsonString = jsonEncode(data.toJson());
    await _prefs.setString(_epfDetailsKey, jsonString);
  }

  EpfDetailsResponse? _getCachedEpfDetails() {
    final jsonString = _prefs.getString(_epfDetailsKey);
    if (jsonString != null) {
      try {
        final jsonData = jsonDecode(jsonString);
        return EpfDetailsResponse.fromJson(jsonData);
      } catch (e) {
        return null;
      }
    }
    return null;
  }

  Future<void> _cacheMfTransactions(MfTransactionsResponse data) async {
    final jsonString = jsonEncode(data.toJson());
    await _prefs.setString(_mfTransactionsKey, jsonString);
  }

  MfTransactionsResponse? _getCachedMfTransactions() {
    final jsonString = _prefs.getString(_mfTransactionsKey);
    if (jsonString != null) {
      try {
        final jsonData = jsonDecode(jsonString);
        return MfTransactionsResponse.fromJson(jsonData);
      } catch (e) {
        return null;
      }
    }
    return null;
  }

  Future<void> _updateLastUpdateTime() async {
    await _prefs.setString(_lastUpdateKey, DateTime.now().toIso8601String());
  }

  DateTime? _getLastUpdateTime() {
    final timeString = _prefs.getString(_lastUpdateKey);
    if (timeString != null) {
      try {
        return DateTime.parse(timeString);
      } catch (e) {
        return null;
      }
    }
    return null;
  }

  Future<void> _updateServiceStatus(AllFinancialDataRepositoryResponse response) async {
    final status = ServiceStatus(
      isNetWorthAvailable: response.netWorth.isSuccess,
      isCreditReportAvailable: response.creditReport.isSuccess,
      isEpfDetailsAvailable: response.epfDetails.isSuccess,
      isMfTransactionsAvailable: response.mfTransactions.isSuccess,
      lastUpdated: DateTime.now(),
    );
    
    final jsonString = jsonEncode({
      'isNetWorthAvailable': status.isNetWorthAvailable,
      'isCreditReportAvailable': status.isCreditReportAvailable,
      'isEpfDetailsAvailable': status.isEpfDetailsAvailable,
      'isMfTransactionsAvailable': status.isMfTransactionsAvailable,
      'lastUpdated': status.lastUpdated.toIso8601String(),
    });
    
    await _prefs.setString(_serviceStatusKey, jsonString);
  }

  ServiceStatus? getServiceStatus() {
    final jsonString = _prefs.getString(_serviceStatusKey);
    if (jsonString != null) {
      try {
        final jsonData = jsonDecode(jsonString);
        return ServiceStatus(
          isNetWorthAvailable: jsonData['isNetWorthAvailable'] ?? false,
          isCreditReportAvailable: jsonData['isCreditReportAvailable'] ?? false,
          isEpfDetailsAvailable: jsonData['isEpfDetailsAvailable'] ?? false,
          isMfTransactionsAvailable: jsonData['isMfTransactionsAvailable'] ?? false,
          lastUpdated: DateTime.parse(jsonData['lastUpdated'] ?? DateTime.now().toIso8601String()),
        );
      } catch (e) {
        return null;
      }
    }
    return null;
  }
}

/// Repository response wrapper
class RepositoryResponse<T> {
  final T? data;
  final String? error;
  final int statusCode;
  final bool isSuccess;
  final bool isFromCache;
  final bool hasError;

  RepositoryResponse._({
    this.data,
    this.error,
    required this.statusCode,
    required this.isSuccess,
    this.isFromCache = false,
    this.hasError = false,
  });

  factory RepositoryResponse.success(T data, {bool isFromCache = false, bool hasError = false, String? error}) {
    return RepositoryResponse._(
      data: data,
      error: error,
      statusCode: 200,
      isSuccess: true,
      isFromCache: isFromCache,
      hasError: hasError,
    );
  }

  factory RepositoryResponse.error(String error, int statusCode) {
    return RepositoryResponse._(
      error: error,
      statusCode: statusCode,
      isSuccess: false,
      isFromCache: false,
      hasError: true,
    );
  }

  T get dataOrThrow {
    if (isSuccess && data != null) {
      return data!;
    }
    throw Exception(error ?? 'Unknown error occurred');
  }
}

/// Combined repository response
class AllFinancialDataRepositoryResponse {
  final RepositoryResponse<FullNetWorthData> netWorth;
  final RepositoryResponse<CreditReportResponse> creditReport;
  final RepositoryResponse<EpfDetailsResponse> epfDetails;
  final RepositoryResponse<MfTransactionsResponse> mfTransactions;

  AllFinancialDataRepositoryResponse({
    required this.netWorth,
    required this.creditReport,
    required this.epfDetails,
    required this.mfTransactions,
  });

  bool get allSuccessful {
    return netWorth.isSuccess &&
        creditReport.isSuccess &&
        epfDetails.isSuccess &&
        mfTransactions.isSuccess;
  }

  bool get anySuccessful {
    return netWorth.isSuccess ||
        creditReport.isSuccess ||
        epfDetails.isSuccess ||
        mfTransactions.isSuccess;
  }

  bool get allFromCache {
    return netWorth.isFromCache &&
        creditReport.isFromCache &&
        epfDetails.isFromCache &&
        mfTransactions.isFromCache;
  }

  bool get anyFromCache {
    return netWorth.isFromCache ||
        creditReport.isFromCache ||
        epfDetails.isFromCache ||
        mfTransactions.isFromCache;
  }

  List<String> get errors {
    final List<String> errors = [];
    if (!netWorth.isSuccess) errors.add('Net Worth: ${netWorth.error}');
    if (!creditReport.isSuccess) errors.add('Credit Report: ${creditReport.error}');
    if (!epfDetails.isSuccess) errors.add('EPF Details: ${epfDetails.error}');
    if (!mfTransactions.isSuccess) errors.add('MF Transactions: ${mfTransactions.error}');
    return errors;
  }

  int get successCount {
    int count = 0;
    if (netWorth.isSuccess) count++;
    if (creditReport.isSuccess) count++;
    if (epfDetails.isSuccess) count++;
    if (mfTransactions.isSuccess) count++;
    return count;
  }

  int get failureCount {
    return 4 - successCount;
  }
}

/// Cache status information
class CacheStatus {
  final bool hasNetWorth;
  final bool hasCreditReport;
  final bool hasEpfDetails;
  final bool hasMfTransactions;
  final DateTime? lastUpdated;
  final bool isValid;
  final DateTime? expiresAt;

  CacheStatus({
    required this.hasNetWorth,
    required this.hasCreditReport,
    required this.hasEpfDetails,
    required this.hasMfTransactions,
    this.lastUpdated,
    required this.isValid,
    this.expiresAt,
  });

  bool get hasAnyData {
    return hasNetWorth || hasCreditReport || hasEpfDetails || hasMfTransactions;
  }

  bool get hasAllData {
    return hasNetWorth && hasCreditReport && hasEpfDetails && hasMfTransactions;
  }

  double get completeness {
    int count = 0;
    if (hasNetWorth) count++;
    if (hasCreditReport) count++;
    if (hasEpfDetails) count++;
    if (hasMfTransactions) count++;
    return count / 4.0;
  }

  Duration? get timeUntilExpiry {
    if (expiresAt != null) {
      final now = DateTime.now();
      if (expiresAt!.isAfter(now)) {
        return expiresAt!.difference(now);
      }
    }
    return null;
  }
}