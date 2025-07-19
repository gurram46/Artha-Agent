import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/app_card.dart';
import '../../../core/widgets/main_layout.dart';
import '../../../core/services/navigation_service.dart';
import '../../fi_money/providers/fi_money_provider.dart';
import '../../fi_money/utils/data_formatters.dart';
import '../../fi_money/models/net_worth.dart';
import '../../fi_money/models/mf_transactions.dart';

class PortfolioAnalysisScreen extends ConsumerWidget {
  const PortfolioAnalysisScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final netWorthState = ref.watch(netWorthProvider);
    final mfTransactionsState = ref.watch(mfTransactionsProvider);
    return AppScaffold(
      title: 'Portfolio Analysis',
      body: Container(
        color: AppColors.backgroundSecondary,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildPortfolioSummary(netWorthState),
              const SizedBox(height: 16),
              _buildPerformanceChart(),
              const SizedBox(height: 16),
              _buildTopHoldings(netWorthState),
              const SizedBox(height: 16),
              _buildAssetAllocation(netWorthState),
              const SizedBox(height: 16),
              _buildRecentTransactions(mfTransactionsState),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPortfolioSummary(NetWorthState netWorthState) {
    if (netWorthState.isLoading) {
      return _buildLoadingCard('Portfolio Summary');
    } else if (netWorthState.hasError) {
      return _buildErrorCard('Portfolio Summary', netWorthState.error!);
    } else if (netWorthState.data != null) {
      return _buildPortfolioSummaryContent(netWorthState.data!);
    } else {
      return _buildLoadingCard('Portfolio Summary');
    }
  }

  Widget _buildPortfolioSummaryContent(FullNetWorthData netWorth) {
    // Calculate portfolio metrics from real data
    final schemes = netWorth.mfSchemeAnalytics;
    
    double totalCurrentValue = 0;
    double totalInvestedValue = 0;
    double totalReturns = 0;
    double weightedXIRR = 0;
    double totalInvestmentForXIRR = 0;
    
    for (final scheme in schemes) {
      final analytics = scheme.enrichedAnalytics.analytics.schemeDetails;
      final currentValue = analytics.currentValue.value;
      final investedValue = analytics.investedValue.value;
      final returns = analytics.absoluteReturns.value;
      final xirr = analytics.xirr;
      
      totalCurrentValue += currentValue;
      totalInvestedValue += investedValue;
      totalReturns += returns;
      
      if (investedValue > 0) {
        weightedXIRR += xirr * investedValue;
        totalInvestmentForXIRR += investedValue;
      }
    }
    
    double portfolioXIRR = totalInvestmentForXIRR > 0 ? weightedXIRR / totalInvestmentForXIRR : 0;
    double returnPercentage = totalInvestedValue > 0 ? (totalReturns / totalInvestedValue) * 100 : 0;
    
    String totalValueStr = DataFormatters.formatCompactCurrency(totalCurrentValue);
    String investedValueStr = DataFormatters.formatCompactCurrency(totalInvestedValue);
    String gainsStr = DataFormatters.formatCompactCurrency(totalReturns);
    String xirrStr = '${portfolioXIRR.toStringAsFixed(1)}%';
    String returnStr = returnPercentage >= 0 ? '+${returnPercentage.toStringAsFixed(1)}%' : '${returnPercentage.toStringAsFixed(1)}%';
    Color returnColor = returnPercentage >= 0 ? AppColors.success : AppColors.error;
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Portfolio Summary',
            style: AppTextStyles.heading4.copyWith(
              color: AppColors.grey900,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildSummaryItem(
                  'Total Value',
                  totalValueStr,
                  returnStr,
                  returnColor,
                  Icons.trending_up,
                ),
              ),
              Expanded(
                child: _buildSummaryItem(
                  'Total Invested',
                  investedValueStr,
                  '${schemes.length} funds',
                  AppColors.primaryBlue,
                  Icons.account_balance_wallet,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildSummaryItem(
                  'Total Gains',
                  gainsStr,
                  returnStr,
                  returnColor,
                  Icons.arrow_upward,
                ),
              ),
              Expanded(
                child: _buildSummaryItem(
                  'XIRR',
                  xirrStr,
                  portfolioXIRR > 15 ? 'Excellent' : portfolioXIRR > 10 ? 'Good' : 'Fair',
                  portfolioXIRR > 0 ? AppColors.success : AppColors.error,
                  Icons.analytics,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value, String change, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Text(
                label,
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.grey600,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: AppTextStyles.heading4.copyWith(
              color: AppColors.grey900,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            change,
            style: AppTextStyles.bodySmall.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPerformanceChart() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.trending_up_outlined, color: AppColors.primaryBlue, size: 24),
              const SizedBox(width: 12),
              Text(
                'Performance Trend',
                style: AppTextStyles.heading4.copyWith(
                  color: AppColors.grey900,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.warning.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.warning.withOpacity(0.2)),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline, color: AppColors.warning),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Historical performance data is not available. This would require time-series portfolio value data.',
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: AppColors.warning,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }


  Widget _buildTopHoldings(NetWorthState netWorthState) {
    if (netWorthState.isLoading) {
      return _buildLoadingCard('Top Holdings');
    } else if (netWorthState.hasError) {
      return _buildErrorCard('Top Holdings', netWorthState.error!);
    } else if (netWorthState.data != null) {
      return _buildTopHoldingsContent(netWorthState.data!);
    } else {
      return _buildLoadingCard('Top Holdings');
    }
  }

  Widget _buildTopHoldingsContent(FullNetWorthData netWorth) {
    final schemes = netWorth.mfSchemeAnalytics;
    
    // Calculate total portfolio value for allocation percentages
    double totalPortfolioValue = schemes.fold(0, (sum, scheme) => 
        sum + scheme.enrichedAnalytics.analytics.schemeDetails.currentValue.value);
    
    // Sort schemes by current value (descending)
    final sortedSchemes = List<MutualFundSchemeAnalytics>.from(schemes)
      ..sort((a, b) => b.enrichedAnalytics.analytics.schemeDetails.currentValue.value
          .compareTo(a.enrichedAnalytics.analytics.schemeDetails.currentValue.value));
    
    // Take top 5 holdings
    final topHoldings = sortedSchemes.take(5).toList();
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Top Holdings',
            style: AppTextStyles.heading4.copyWith(
              color: AppColors.grey900,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 16),
          ...topHoldings.map((scheme) {
            final analytics = scheme.enrichedAnalytics.analytics.schemeDetails;
            final currentValue = analytics.currentValue.value;
            final absoluteReturns = analytics.absoluteReturns.value;
            final investedValue = analytics.investedValue.value;
            
            String name = scheme.schemeDetail.nameData.longName;
            String value = DataFormatters.formatCompactCurrency(currentValue);
            String allocation = totalPortfolioValue > 0 
                ? '${((currentValue / totalPortfolioValue) * 100).toStringAsFixed(0)}%' 
                : '0%';
            
            double returnPercentage = investedValue > 0 ? (absoluteReturns / investedValue) * 100 : 0;
            String returns = returnPercentage >= 0 
                ? '+${returnPercentage.toStringAsFixed(1)}%' 
                : '${returnPercentage.toStringAsFixed(1)}%';
            Color returnColor = returnPercentage >= 0 ? AppColors.success : AppColors.error;
            
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: _buildHoldingItem(name, value, allocation, returns, returnColor),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildLoadingCard(String title) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: AppTextStyles.heading4.copyWith(
              color: AppColors.grey900,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 16),
          const Center(
            child: CircularProgressIndicator(),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorCard(String title, String error) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: AppTextStyles.heading4.copyWith(
              color: AppColors.grey900,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Error loading data: $error',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.error,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHoldingItem(String name, String value, String allocation, String returns, Color color) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          flex: 3,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                name,
                style: AppTextStyles.bodyMedium.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              Text(
                value,
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.grey600,
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: Text(
            allocation,
            style: AppTextStyles.bodyMedium.copyWith(
              fontWeight: FontWeight.w600,
            ),
            textAlign: TextAlign.center,
          ),
        ),
        Expanded(
          child: Text(
            returns,
            style: AppTextStyles.bodyMedium.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
            textAlign: TextAlign.right,
          ),
        ),
      ],
    );
  }

  Widget _buildAssetAllocation(NetWorthState netWorthState) {
    if (netWorthState.isLoading) {
      return _buildLoadingCard('Asset Allocation');
    } else if (netWorthState.hasError) {
      return _buildErrorCard('Asset Allocation', netWorthState.error!);
    } else if (netWorthState.data != null) {
      return _buildAssetAllocationContent(netWorthState.data!);
    } else {
      return _buildLoadingCard('Asset Allocation');
    }
  }

  Widget _buildAssetAllocationContent(FullNetWorthData netWorth) {
    final schemes = netWorth.mfSchemeAnalytics;
    
    // Calculate asset allocation from real data
    Map<String, double> assetAllocation = {};
    double totalValue = 0;
    
    for (final scheme in schemes) {
      final currentValue = scheme.enrichedAnalytics.analytics.schemeDetails.currentValue.value;
      final assetClass = scheme.schemeDetail.assetClass;
      
      totalValue += currentValue;
      assetAllocation[assetClass] = (assetAllocation[assetClass] ?? 0) + currentValue;
    }
    
    // Convert to percentages
    final allocationList = assetAllocation.entries.map((entry) {
      double percentage = totalValue > 0 ? (entry.value / totalValue) * 100 : 0;
      return MapEntry(entry.key, percentage);
    }).toList();
    
    // Sort by percentage (descending)
    allocationList.sort((a, b) => b.value.compareTo(a.value));
    
    final colors = [AppColors.primaryBlue, AppColors.success, AppColors.warning, AppColors.error];
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Asset Allocation',
            style: AppTextStyles.heading4.copyWith(
              color: AppColors.grey900,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: SizedBox(
                  height: 150,
                  child: PieChart(
                    PieChartData(
                      sections: allocationList.asMap().entries.map((entry) {
                        int index = entry.key;
                        MapEntry<String, double> allocation = entry.value;
                        return PieChartSectionData(
                          value: allocation.value,
                          color: colors[index % colors.length],
                          title: '',
                          radius: 60,
                        );
                      }).toList(),
                      sectionsSpace: 2,
                      centerSpaceRadius: 40,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: allocationList.asMap().entries.map((entry) {
                    int index = entry.key;
                    MapEntry<String, double> allocation = entry.value;
                    return _buildAllocationItem(
                      _getAssetClassDisplayName(allocation.key),
                      '${allocation.value.toStringAsFixed(0)}%',
                      colors[index % colors.length],
                    );
                  }).toList(),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAllocationItem(String label, String percentage, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              label,
              style: AppTextStyles.bodyMedium.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Text(
            percentage,
            style: AppTextStyles.bodyMedium.copyWith(
              fontWeight: FontWeight.w700,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  String _getAssetClassDisplayName(String assetClass) {
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

  Widget _buildRecentTransactions(MfTransactionsState mfTransactionsState) {
    if (mfTransactionsState.isLoading) {
      return _buildLoadingCard('Recent Transactions');
    } else if (mfTransactionsState.hasError) {
      return _buildErrorCard('Recent Transactions', mfTransactionsState.error!);
    } else if (mfTransactionsState.data != null) {
      return _buildRecentTransactionsContent(mfTransactionsState.data!);
    } else {
      return _buildLoadingCard('Recent Transactions');
    }
  }

  Widget _buildRecentTransactionsContent(MfTransactionsResponse transactions) {
    final recentTransactions = transactions.transactions.take(4).toList();
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Recent Transactions',
            style: AppTextStyles.heading4.copyWith(
              color: AppColors.grey900,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 16),
          ...recentTransactions.map((transaction) {
            String type = transaction.externalOrderType;
            bool isRedemption = type.toUpperCase() == 'SELL' || type.toUpperCase() == 'REDEMPTION';
            String amount = DataFormatters.formatCurrency(transaction.transactionAmount.value);
            String name = transaction.schemeName.length > 25 
                ? '${transaction.schemeName.substring(0, 22)}...'
                : transaction.schemeName;
            String date = DataFormatters.formatDate(transaction.transactionDate);
            Color color = isRedemption ? AppColors.error : AppColors.success;
            
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: _buildTransactionItem('$type - $name', amount, date, color, isRedemption),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildTransactionItem(String name, String amount, String date, Color color, bool isRedemption) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              isRedemption ? Icons.arrow_upward : Icons.arrow_downward,
              color: color,
              size: 16,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: AppTextStyles.bodyMedium.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  date,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.grey600,
                  ),
                ),
              ],
            ),
          ),
          Text(
            isRedemption ? '+$amount' : '-$amount',
            style: AppTextStyles.bodyMedium.copyWith(
              color: color,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}