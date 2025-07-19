import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/net_worth.dart';
import '../models/credit_report.dart';
import '../models/epf_details.dart';
import '../models/mf_transactions.dart';

class FiMoneyApiService {
  static const String _baseUrl = 'https://fi-money-mcp.api.endpoint'; // Replace with actual MCP endpoint
  static const int _timeoutSeconds = 30;
  
  static final FiMoneyApiService _instance = FiMoneyApiService._internal();
  factory FiMoneyApiService() => _instance;
  FiMoneyApiService._internal();

  final http.Client _client = http.Client();

  /// Fetches net worth data from Fi Money API
  Future<ApiResponse<FullNetWorthData>> fetchNetWorth() async {
    try {
      final response = await _client
          .post(
            Uri.parse('$_baseUrl/fetch_net_worth'),
            headers: _getHeaders(),
            body: jsonEncode({}),
          )
          .timeout(Duration(seconds: _timeoutSeconds));

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        final netWorthData = FullNetWorthData.fromJson(jsonData);
        return ApiResponse.success(netWorthData);
      } else {
        return ApiResponse.error(
          'Failed to fetch net worth data: ${response.statusCode}',
          response.statusCode,
        );
      }
    } on SocketException {
      return ApiResponse.error('No internet connection', 0);
    } on HttpException {
      return ApiResponse.error('HTTP error occurred', 0);
    } on FormatException {
      return ApiResponse.error('Invalid response format', 0);
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e', 0);
    }
  }

  /// Fetches credit report data from Fi Money API
  Future<ApiResponse<CreditReportResponse>> fetchCreditReport() async {
    try {
      final response = await _client
          .post(
            Uri.parse('$_baseUrl/fetch_credit_report'),
            headers: _getHeaders(),
            body: jsonEncode({}),
          )
          .timeout(Duration(seconds: _timeoutSeconds));

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        final creditReportData = CreditReportResponse.fromJson(jsonData);
        return ApiResponse.success(creditReportData);
      } else {
        return ApiResponse.error(
          'Failed to fetch credit report: ${response.statusCode}',
          response.statusCode,
        );
      }
    } on SocketException {
      return ApiResponse.error('No internet connection', 0);
    } on HttpException {
      return ApiResponse.error('HTTP error occurred', 0);
    } on FormatException {
      return ApiResponse.error('Invalid response format', 0);
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e', 0);
    }
  }

  /// Fetches EPF details from Fi Money API
  Future<ApiResponse<EpfDetailsResponse>> fetchEpfDetails() async {
    try {
      final response = await _client
          .post(
            Uri.parse('$_baseUrl/fetch_epf_details'),
            headers: _getHeaders(),
            body: jsonEncode({}),
          )
          .timeout(Duration(seconds: _timeoutSeconds));

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        final epfDetailsData = EpfDetailsResponse.fromJson(jsonData);
        return ApiResponse.success(epfDetailsData);
      } else {
        return ApiResponse.error(
          'Failed to fetch EPF details: ${response.statusCode}',
          response.statusCode,
        );
      }
    } on SocketException {
      return ApiResponse.error('No internet connection', 0);
    } on HttpException {
      return ApiResponse.error('HTTP error occurred', 0);
    } on FormatException {
      return ApiResponse.error('Invalid response format', 0);
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e', 0);
    }
  }

  /// Fetches mutual fund transactions from Fi Money API
  Future<ApiResponse<MfTransactionsResponse>> fetchMfTransactions() async {
    try {
      final response = await _client
          .post(
            Uri.parse('$_baseUrl/fetch_mf_transactions'),
            headers: _getHeaders(),
            body: jsonEncode({}),
          )
          .timeout(Duration(seconds: _timeoutSeconds));

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        final mfTransactionsData = MfTransactionsResponse.fromJson(jsonData);
        return ApiResponse.success(mfTransactionsData);
      } else {
        return ApiResponse.error(
          'Failed to fetch MF transactions: ${response.statusCode}',
          response.statusCode,
        );
      }
    } on SocketException {
      return ApiResponse.error('No internet connection', 0);
    } on HttpException {
      return ApiResponse.error('HTTP error occurred', 0);
    } on FormatException {
      return ApiResponse.error('Invalid response format', 0);
    } catch (e) {
      return ApiResponse.error('Unexpected error: $e', 0);
    }
  }

  /// Fetches all financial data in parallel for better performance
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

  /// Gets HTTP headers for API requests
  Map<String, String> _getHeaders() {
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'User-Agent': 'Artha-AI-App/1.0',
    };
  }

  /// Disposes the HTTP client
  void dispose() {
    _client.close();
  }
}

/// Generic API response wrapper
class ApiResponse<T> {
  final T? data;
  final String? error;
  final int statusCode;
  final bool isSuccess;

  ApiResponse._({
    this.data,
    this.error,
    required this.statusCode,
    required this.isSuccess,
  });

  factory ApiResponse.success(T data) {
    return ApiResponse._(
      data: data,
      statusCode: 200,
      isSuccess: true,
    );
  }

  factory ApiResponse.error(String error, int statusCode) {
    return ApiResponse._(
      error: error,
      statusCode: statusCode,
      isSuccess: false,
    );
  }

  /// Returns data if successful, otherwise throws an exception
  T get dataOrThrow {
    if (isSuccess && data != null) {
      return data!;
    }
    throw Exception(error ?? 'Unknown error occurred');
  }
}

/// Response containing all financial data
class AllFinancialDataResponse {
  final ApiResponse<FullNetWorthData> netWorth;
  final ApiResponse<CreditReportResponse> creditReport;
  final ApiResponse<EpfDetailsResponse> epfDetails;
  final ApiResponse<MfTransactionsResponse> mfTransactions;

  AllFinancialDataResponse({
    required this.netWorth,
    required this.creditReport,
    required this.epfDetails,
    required this.mfTransactions,
  });

  /// Returns true if all API calls were successful
  bool get allSuccessful {
    return netWorth.isSuccess &&
        creditReport.isSuccess &&
        epfDetails.isSuccess &&
        mfTransactions.isSuccess;
  }

  /// Returns true if at least one API call was successful
  bool get anySuccessful {
    return netWorth.isSuccess ||
        creditReport.isSuccess ||
        epfDetails.isSuccess ||
        mfTransactions.isSuccess;
  }

  /// Gets list of all errors that occurred
  List<String> get errors {
    final List<String> errors = [];
    if (!netWorth.isSuccess) errors.add('Net Worth: ${netWorth.error}');
    if (!creditReport.isSuccess) errors.add('Credit Report: ${creditReport.error}');
    if (!epfDetails.isSuccess) errors.add('EPF Details: ${epfDetails.error}');
    if (!mfTransactions.isSuccess) errors.add('MF Transactions: ${mfTransactions.error}');
    return errors;
  }

  /// Gets count of successful API calls
  int get successCount {
    int count = 0;
    if (netWorth.isSuccess) count++;
    if (creditReport.isSuccess) count++;
    if (epfDetails.isSuccess) count++;
    if (mfTransactions.isSuccess) count++;
    return count;
  }

  /// Gets count of failed API calls
  int get failureCount {
    return 4 - successCount;
  }
}

/// Service status for monitoring API health
class ServiceStatus {
  final bool isNetWorthAvailable;
  final bool isCreditReportAvailable;
  final bool isEpfDetailsAvailable;
  final bool isMfTransactionsAvailable;
  final DateTime lastUpdated;

  ServiceStatus({
    required this.isNetWorthAvailable,
    required this.isCreditReportAvailable,
    required this.isEpfDetailsAvailable,
    required this.isMfTransactionsAvailable,
    required this.lastUpdated,
  });

  factory ServiceStatus.fromAllFinancialDataResponse(AllFinancialDataResponse response) {
    return ServiceStatus(
      isNetWorthAvailable: response.netWorth.isSuccess,
      isCreditReportAvailable: response.creditReport.isSuccess,
      isEpfDetailsAvailable: response.epfDetails.isSuccess,
      isMfTransactionsAvailable: response.mfTransactions.isSuccess,
      lastUpdated: DateTime.now(),
    );
  }

  /// Returns true if all services are available
  bool get allServicesAvailable {
    return isNetWorthAvailable &&
        isCreditReportAvailable &&
        isEpfDetailsAvailable &&
        isMfTransactionsAvailable;
  }

  /// Returns true if at least one service is available
  bool get anyServiceAvailable {
    return isNetWorthAvailable ||
        isCreditReportAvailable ||
        isEpfDetailsAvailable ||
        isMfTransactionsAvailable;
  }

  /// Gets percentage of available services
  double get availabilityPercentage {
    int available = 0;
    if (isNetWorthAvailable) available++;
    if (isCreditReportAvailable) available++;
    if (isEpfDetailsAvailable) available++;
    if (isMfTransactionsAvailable) available++;
    return available / 4.0;
  }

  /// Gets list of unavailable services
  List<String> get unavailableServices {
    final List<String> unavailable = [];
    if (!isNetWorthAvailable) unavailable.add('Net Worth');
    if (!isCreditReportAvailable) unavailable.add('Credit Report');
    if (!isEpfDetailsAvailable) unavailable.add('EPF Details');
    if (!isMfTransactionsAvailable) unavailable.add('MF Transactions');
    return unavailable;
  }
}

/// Extensions for easier error handling
extension ApiResponseExtensions<T> on Future<ApiResponse<T>> {
  /// Handles the response with success and error callbacks
  Future<R> handle<R>({
    required R Function(T data) onSuccess,
    required R Function(String error, int statusCode) onError,
  }) async {
    final response = await this;
    if (response.isSuccess) {
      return onSuccess(response.data!);
    } else {
      return onError(response.error!, response.statusCode);
    }
  }

  /// Maps the success data to another type
  Future<ApiResponse<R>> map<R>(R Function(T data) mapper) async {
    final response = await this;
    if (response.isSuccess) {
      return ApiResponse.success(mapper(response.data!));
    } else {
      return ApiResponse.error(response.error!, response.statusCode);
    }
  }

  /// Provides a fallback value in case of error
  Future<T> orElse(T fallback) async {
    final response = await this;
    return response.isSuccess ? response.data! : fallback;
  }
}