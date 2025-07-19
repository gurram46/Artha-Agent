import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/fi_money_repository.dart';
import '../services/fi_money_api_service.dart';
import '../models/net_worth.dart';
import '../models/credit_report.dart';
import '../models/epf_details.dart';
import '../models/mf_transactions.dart';

// Repository provider
final fiMoneyRepositoryProvider = FutureProvider<FiMoneyRepository>((ref) async {
  return await FiMoneyRepository.getInstance();
});

// Data state providers
final netWorthProvider = StateNotifierProvider<NetWorthNotifier, NetWorthState>((ref) {
  final repository = ref.watch(fiMoneyRepositoryProvider);
  return NetWorthNotifier(repository.asData?.value);
});

final creditReportProvider = StateNotifierProvider<CreditReportNotifier, CreditReportState>((ref) {
  final repository = ref.watch(fiMoneyRepositoryProvider);
  return CreditReportNotifier(repository.asData?.value);
});

final epfDetailsProvider = StateNotifierProvider<EpfDetailsNotifier, EpfDetailsState>((ref) {
  final repository = ref.watch(fiMoneyRepositoryProvider);
  return EpfDetailsNotifier(repository.asData?.value);
});

final mfTransactionsProvider = StateNotifierProvider<MfTransactionsNotifier, MfTransactionsState>((ref) {
  final repository = ref.watch(fiMoneyRepositoryProvider);
  return MfTransactionsNotifier(repository.asData?.value);
});

// Combined financial data provider
final allFinancialDataProvider = StateNotifierProvider<AllFinancialDataNotifier, AllFinancialDataState>((ref) {
  final repository = ref.watch(fiMoneyRepositoryProvider);
  return AllFinancialDataNotifier(repository.asData?.value);
});

// Connection status provider
final connectionStatusProvider = StateNotifierProvider<ConnectionStatusNotifier, ConnectionStatusState>((ref) {
  final repository = ref.watch(fiMoneyRepositoryProvider);
  return ConnectionStatusNotifier(repository.asData?.value);
});

// Data states
class NetWorthState {
  final FullNetWorthData? data;
  final bool isLoading;
  final String? error;
  final bool isFromCache;
  final DateTime? lastUpdated;

  NetWorthState({
    this.data,
    this.isLoading = false,
    this.error,
    this.isFromCache = false,
    this.lastUpdated,
  });

  NetWorthState copyWith({
    FullNetWorthData? data,
    bool? isLoading,
    String? error,
    bool? isFromCache,
    DateTime? lastUpdated,
  }) {
    return NetWorthState(
      data: data ?? this.data,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      isFromCache: isFromCache ?? this.isFromCache,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  bool get hasData => data != null;
  bool get hasError => error != null;
  bool get isEmpty => data == null && !isLoading && !hasError;
}

class CreditReportState {
  final CreditReportResponse? data;
  final bool isLoading;
  final String? error;
  final bool isFromCache;
  final DateTime? lastUpdated;

  CreditReportState({
    this.data,
    this.isLoading = false,
    this.error,
    this.isFromCache = false,
    this.lastUpdated,
  });

  CreditReportState copyWith({
    CreditReportResponse? data,
    bool? isLoading,
    String? error,
    bool? isFromCache,
    DateTime? lastUpdated,
  }) {
    return CreditReportState(
      data: data ?? this.data,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      isFromCache: isFromCache ?? this.isFromCache,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  bool get hasData => data != null;
  bool get hasError => error != null;
  bool get isEmpty => data == null && !isLoading && !hasError;
  
  int? get creditScore => data?.primaryReport?.creditReportData.score.score;
  String? get creditScoreCategory => data?.primaryReport?.creditReportData.score.scoreCategory;
}

class EpfDetailsState {
  final EpfDetailsResponse? data;
  final bool isLoading;
  final String? error;
  final bool isFromCache;
  final DateTime? lastUpdated;

  EpfDetailsState({
    this.data,
    this.isLoading = false,
    this.error,
    this.isFromCache = false,
    this.lastUpdated,
  });

  EpfDetailsState copyWith({
    EpfDetailsResponse? data,
    bool? isLoading,
    String? error,
    bool? isFromCache,
    DateTime? lastUpdated,
  }) {
    return EpfDetailsState(
      data: data ?? this.data,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      isFromCache: isFromCache ?? this.isFromCache,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  bool get hasData => data != null;
  bool get hasError => error != null;
  bool get isEmpty => data == null && !isLoading && !hasError;
  
  double? get totalBalance => data?.primaryAccount?.rawDetails.overallPfBalance.totalCurrentBalance;
  String? get formattedBalance => data?.primaryAccount?.rawDetails.overallPfBalance.formattedCurrentBalance;
}

class MfTransactionsState {
  final MfTransactionsResponse? data;
  final bool isLoading;
  final String? error;
  final bool isFromCache;
  final DateTime? lastUpdated;

  MfTransactionsState({
    this.data,
    this.isLoading = false,
    this.error,
    this.isFromCache = false,
    this.lastUpdated,
  });

  MfTransactionsState copyWith({
    MfTransactionsResponse? data,
    bool? isLoading,
    String? error,
    bool? isFromCache,
    DateTime? lastUpdated,
  }) {
    return MfTransactionsState(
      data: data ?? this.data,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      isFromCache: isFromCache ?? this.isFromCache,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  bool get hasData => data != null;
  bool get hasError => error != null;
  bool get isEmpty => data == null && !isLoading && !hasError;
  
  double? get totalInvested => data?.totalInvestedAmount;
  double? get totalRedeemed => data?.totalRedeemedAmount;
  double? get netInvested => data?.netInvestedAmount;
  int? get transactionCount => data?.transactions.length;
}

class AllFinancialDataState {
  final AllFinancialDataRepositoryResponse? data;
  final bool isLoading;
  final String? error;
  final DateTime? lastUpdated;

  AllFinancialDataState({
    this.data,
    this.isLoading = false,
    this.error,
    this.lastUpdated,
  });

  AllFinancialDataState copyWith({
    AllFinancialDataRepositoryResponse? data,
    bool? isLoading,
    String? error,
    DateTime? lastUpdated,
  }) {
    return AllFinancialDataState(
      data: data ?? this.data,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  bool get hasData => data != null;
  bool get hasError => error != null;
  bool get isEmpty => data == null && !isLoading && !hasError;
  bool get allSuccessful => data?.allSuccessful ?? false;
  bool get anySuccessful => data?.anySuccessful ?? false;
  int get successCount => data?.successCount ?? 0;
  int get failureCount => data?.failureCount ?? 0;
  List<String> get errors => data?.errors ?? [];
}

class ConnectionStatusState {
  final ServiceStatus? status;
  final CacheStatus? cacheStatus;
  final bool isOnline;
  final DateTime? lastChecked;

  ConnectionStatusState({
    this.status,
    this.cacheStatus,
    this.isOnline = true,
    this.lastChecked,
  });

  ConnectionStatusState copyWith({
    ServiceStatus? status,
    CacheStatus? cacheStatus,
    bool? isOnline,
    DateTime? lastChecked,
  }) {
    return ConnectionStatusState(
      status: status ?? this.status,
      cacheStatus: cacheStatus ?? this.cacheStatus,
      isOnline: isOnline ?? this.isOnline,
      lastChecked: lastChecked ?? this.lastChecked,
    );
  }

  bool get allServicesAvailable => status?.allServicesAvailable ?? false;
  bool get anyServiceAvailable => status?.anyServiceAvailable ?? false;
  double get availabilityPercentage => status?.availabilityPercentage ?? 0.0;
  bool get hasCachedData => cacheStatus?.hasAnyData ?? false;
  bool get isCacheValid => cacheStatus?.isValid ?? false;
}

// State notifiers
class NetWorthNotifier extends StateNotifier<NetWorthState> {
  final FiMoneyRepository? _repository;

  NetWorthNotifier(this._repository) : super(NetWorthState()) {
    _loadCachedData();
  }

  Future<void> _loadCachedData() async {
    if (_repository == null) return;
    
    try {
      final response = await _repository!.getNetWorth(forceRefresh: false);
      if (response.isSuccess) {
        state = state.copyWith(
          data: response.data,
          isFromCache: response.isFromCache,
          lastUpdated: DateTime.now(),
        );
      }
    } catch (e) {
      // Silently fail for cached data loading
    }
  }

  Future<void> loadNetWorth({bool forceRefresh = false}) async {
    if (_repository == null) return;
    
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final response = await _repository!.getNetWorth(forceRefresh: forceRefresh);
      
      if (response.isSuccess) {
        state = state.copyWith(
          data: response.data,
          isLoading: false,
          isFromCache: response.isFromCache,
          lastUpdated: DateTime.now(),
          error: response.hasError ? response.error : null,
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: response.error,
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> refresh() => loadNetWorth(forceRefresh: true);
}

class CreditReportNotifier extends StateNotifier<CreditReportState> {
  final FiMoneyRepository? _repository;

  CreditReportNotifier(this._repository) : super(CreditReportState()) {
    _loadCachedData();
  }

  Future<void> _loadCachedData() async {
    if (_repository == null) return;
    
    try {
      final response = await _repository!.getCreditReport(forceRefresh: false);
      if (response.isSuccess) {
        state = state.copyWith(
          data: response.data,
          isFromCache: response.isFromCache,
          lastUpdated: DateTime.now(),
        );
      }
    } catch (e) {
      // Silently fail for cached data loading
    }
  }

  Future<void> loadCreditReport({bool forceRefresh = false}) async {
    if (_repository == null) return;
    
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final response = await _repository!.getCreditReport(forceRefresh: forceRefresh);
      
      if (response.isSuccess) {
        state = state.copyWith(
          data: response.data,
          isLoading: false,
          isFromCache: response.isFromCache,
          lastUpdated: DateTime.now(),
          error: response.hasError ? response.error : null,
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: response.error,
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> refresh() => loadCreditReport(forceRefresh: true);
}

class EpfDetailsNotifier extends StateNotifier<EpfDetailsState> {
  final FiMoneyRepository? _repository;

  EpfDetailsNotifier(this._repository) : super(EpfDetailsState()) {
    _loadCachedData();
  }

  Future<void> _loadCachedData() async {
    if (_repository == null) return;
    
    try {
      final response = await _repository!.getEpfDetails(forceRefresh: false);
      if (response.isSuccess) {
        state = state.copyWith(
          data: response.data,
          isFromCache: response.isFromCache,
          lastUpdated: DateTime.now(),
        );
      }
    } catch (e) {
      // Silently fail for cached data loading
    }
  }

  Future<void> loadEpfDetails({bool forceRefresh = false}) async {
    if (_repository == null) return;
    
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final response = await _repository!.getEpfDetails(forceRefresh: forceRefresh);
      
      if (response.isSuccess) {
        state = state.copyWith(
          data: response.data,
          isLoading: false,
          isFromCache: response.isFromCache,
          lastUpdated: DateTime.now(),
          error: response.hasError ? response.error : null,
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: response.error,
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> refresh() => loadEpfDetails(forceRefresh: true);
}

class MfTransactionsNotifier extends StateNotifier<MfTransactionsState> {
  final FiMoneyRepository? _repository;

  MfTransactionsNotifier(this._repository) : super(MfTransactionsState()) {
    _loadCachedData();
  }

  Future<void> _loadCachedData() async {
    if (_repository == null) return;
    
    try {
      final response = await _repository!.getMfTransactions(forceRefresh: false);
      if (response.isSuccess) {
        state = state.copyWith(
          data: response.data,
          isFromCache: response.isFromCache,
          lastUpdated: DateTime.now(),
        );
      }
    } catch (e) {
      // Silently fail for cached data loading
    }
  }

  Future<void> loadMfTransactions({bool forceRefresh = false}) async {
    if (_repository == null) return;
    
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final response = await _repository!.getMfTransactions(forceRefresh: forceRefresh);
      
      if (response.isSuccess) {
        state = state.copyWith(
          data: response.data,
          isLoading: false,
          isFromCache: response.isFromCache,
          lastUpdated: DateTime.now(),
          error: response.hasError ? response.error : null,
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: response.error,
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> refresh() => loadMfTransactions(forceRefresh: true);
}

class AllFinancialDataNotifier extends StateNotifier<AllFinancialDataState> {
  final FiMoneyRepository? _repository;

  AllFinancialDataNotifier(this._repository) : super(AllFinancialDataState()) {
    _loadCachedData();
  }

  Future<void> _loadCachedData() async {
    if (_repository == null) return;
    
    try {
      final response = await _repository!.getAllFinancialData(forceRefresh: false);
      state = state.copyWith(
        data: response,
        lastUpdated: DateTime.now(),
      );
    } catch (e) {
      // Silently fail for cached data loading
    }
  }

  Future<void> loadAllFinancialData({bool forceRefresh = false}) async {
    if (_repository == null) return;
    
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final response = await _repository!.getAllFinancialData(forceRefresh: forceRefresh);
      
      state = state.copyWith(
        data: response,
        isLoading: false,
        lastUpdated: DateTime.now(),
        error: response.anySuccessful ? null : 'Failed to load any financial data',
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> refresh() => loadAllFinancialData(forceRefresh: true);
}

class ConnectionStatusNotifier extends StateNotifier<ConnectionStatusState> {
  final FiMoneyRepository? _repository;

  ConnectionStatusNotifier(this._repository) : super(ConnectionStatusState()) {
    _loadStatus();
  }

  Future<void> _loadStatus() async {
    if (_repository == null) return;
    
    try {
      final status = _repository!.getServiceStatus();
      final cacheStatus = await _repository!.getCacheStatus();
      
      state = state.copyWith(
        status: status,
        cacheStatus: cacheStatus,
        lastChecked: DateTime.now(),
      );
    } catch (e) {
      // Silently fail
    }
  }

  Future<void> checkStatus() async {
    await _loadStatus();
  }

  void setOnlineStatus(bool isOnline) {
    state = state.copyWith(isOnline: isOnline);
  }
}

// Utility providers
final hasInternetProvider = StateProvider<bool>((ref) => true);

// Quick access providers
final netWorthValueProvider = Provider<double?>((ref) {
  final netWorthState = ref.watch(netWorthProvider);
  return netWorthState.data?.netWorthResponse.totalNetWorthValue.value;
});

final creditScoreProvider = Provider<int?>((ref) {
  final creditReportState = ref.watch(creditReportProvider);
  return creditReportState.creditScore;
});

final epfBalanceProvider = Provider<double?>((ref) {
  final epfState = ref.watch(epfDetailsProvider);
  return epfState.totalBalance;
});

final totalInvestmentProvider = Provider<double?>((ref) {
  final mfState = ref.watch(mfTransactionsProvider);
  return mfState.totalInvested;
});

// Loading state providers
final isLoadingAnyDataProvider = Provider<bool>((ref) {
  final netWorthState = ref.watch(netWorthProvider);
  final creditReportState = ref.watch(creditReportProvider);
  final epfState = ref.watch(epfDetailsProvider);
  final mfState = ref.watch(mfTransactionsProvider);
  
  return netWorthState.isLoading || 
         creditReportState.isLoading || 
         epfState.isLoading || 
         mfState.isLoading;
});

final hasAnyDataProvider = Provider<bool>((ref) {
  final netWorthState = ref.watch(netWorthProvider);
  final creditReportState = ref.watch(creditReportProvider);
  final epfState = ref.watch(epfDetailsProvider);
  final mfState = ref.watch(mfTransactionsProvider);
  
  return netWorthState.hasData || 
         creditReportState.hasData || 
         epfState.hasData || 
         mfState.hasData;
});

final hasAnyErrorProvider = Provider<bool>((ref) {
  final netWorthState = ref.watch(netWorthProvider);
  final creditReportState = ref.watch(creditReportProvider);
  final epfState = ref.watch(epfDetailsProvider);
  final mfState = ref.watch(mfTransactionsProvider);
  
  return netWorthState.hasError || 
         creditReportState.hasError || 
         epfState.hasError || 
         mfState.hasError;
});

// Refresh all data provider
final refreshAllDataProvider = Provider<Future<void> Function()>((ref) {
  return () async {
    await Future.wait([
      ref.read(netWorthProvider.notifier).refresh(),
      ref.read(creditReportProvider.notifier).refresh(),
      ref.read(epfDetailsProvider.notifier).refresh(),
      ref.read(mfTransactionsProvider.notifier).refresh(),
    ]);
  };
});

// Summary data provider
final financialSummaryProvider = Provider<FinancialSummary?>((ref) {
  final netWorthState = ref.watch(netWorthProvider);
  final creditReportState = ref.watch(creditReportProvider);
  final epfState = ref.watch(epfDetailsProvider);
  final mfState = ref.watch(mfTransactionsProvider);
  
  if (!netWorthState.hasData) return null;
  
  return FinancialSummary(
    totalNetWorth: netWorthState.data!.netWorthResponse.totalNetWorthValue.value,
    totalAssets: netWorthState.data!.netWorthResponse.totalAssets,
    totalLiabilities: netWorthState.data!.netWorthResponse.totalLiabilities,
    creditScore: creditReportState.creditScore,
    epfBalance: epfState.totalBalance,
    totalInvestment: mfState.totalInvested,
    lastUpdated: [
      netWorthState.lastUpdated,
      creditReportState.lastUpdated,
      epfState.lastUpdated,
      mfState.lastUpdated,
    ].where((date) => date != null).map((date) => date!).fold<DateTime?>(
      null,
      (latest, current) => latest == null || current.isAfter(latest) ? current : latest,
    ),
  );
});

// Financial summary model
class FinancialSummary {
  final double totalNetWorth;
  final double totalAssets;
  final double totalLiabilities;
  final int? creditScore;
  final double? epfBalance;
  final double? totalInvestment;
  final DateTime? lastUpdated;

  FinancialSummary({
    required this.totalNetWorth,
    required this.totalAssets,
    required this.totalLiabilities,
    this.creditScore,
    this.epfBalance,
    this.totalInvestment,
    this.lastUpdated,
  });
}