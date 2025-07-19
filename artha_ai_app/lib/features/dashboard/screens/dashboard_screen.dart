import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/compact_cards.dart';
import '../../../core/services/navigation_service.dart';
import '../../../core/navigation/app_router.dart';
import '../../fi_money/providers/fi_money_provider.dart';
import '../../fi_money/utils/data_formatters.dart';
import '../../fi_money/models/mf_transactions.dart';
import '../widgets/past_analysis_tab.dart';
import '../widgets/present_optimization_tab.dart';
import '../widgets/future_planning_tab.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    // Load financial data on initialization
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadFinancialData();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadFinancialData() async {
    ref.read(netWorthProvider.notifier).loadNetWorth();
    ref.read(creditReportProvider.notifier).loadCreditReport();
    ref.read(epfDetailsProvider.notifier).loadEpfDetails();
    ref.read(mfTransactionsProvider.notifier).loadMfTransactions();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.backgroundSecondary,
      body: SafeArea(
        child: Column(
          children: [
            _buildCompactHeader(),
            _buildMainContent(),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          NavigationService.navigateTo(context, AppRouter.chat);
        },
        backgroundColor: AppColors.primaryBlue,
        child: const Icon(Icons.chat_bubble_outline, color: AppColors.white),
      ),
    );
  }

  Widget _buildCompactHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 16),
      decoration: BoxDecoration(
        color: AppColors.white,
        boxShadow: [
          BoxShadow(
            color: AppColors.grey200.withOpacity(0.3),
            blurRadius: 1,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Good morning',
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: AppColors.grey600,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Financial Dashboard',
                    style: AppTextStyles.heading1.copyWith(
                      color: AppColors.grey900,
                    ),
                  ),
                ],
              ),
              Row(
                children: [
                  Container(
                    decoration: BoxDecoration(
                      color: AppColors.grey100,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: IconButton(
                      icon: Icon(Icons.account_balance_wallet_outlined, 
                               color: AppColors.grey700, size: 20),
                      onPressed: () {
                        NavigationService.navigateTo(context, AppRouter.fiConnection);
                      },
                      constraints: const BoxConstraints(
                        minWidth: 36,
                        minHeight: 36,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    decoration: BoxDecoration(
                      color: AppColors.grey100,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: IconButton(
                      icon: Icon(Icons.settings_outlined, 
                               color: AppColors.grey700, size: 20),
                      onPressed: () {
                        NavigationService.navigateTo(context, AppRouter.settings);
                      },
                      constraints: const BoxConstraints(
                        minWidth: 36,
                        minHeight: 36,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildCompactSummary(),
        ],
      ),
    );
  }

  Widget _buildCompactSummary() {
    final netWorthState = ref.watch(netWorthProvider);
    final creditReportState = ref.watch(creditReportProvider);
    final isLoadingAny = ref.watch(isLoadingAnyDataProvider);
    
    return Row(
      children: [
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.success.withOpacity(0.05),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: AppColors.success.withOpacity(0.1),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.trending_up,
                  color: AppColors.success,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (isLoadingAny && !netWorthState.hasData)
                        _buildLoadingText()
                      else if (netWorthState.hasData)
                        Text(
                          DataFormatters.formatCompactCurrency(
                            netWorthState.data!.netWorthResponse.totalNetWorthValue.value,
                          ),
                          style: AppTextStyles.currencyCompact.copyWith(
                            color: AppColors.success,
                          ),
                        )
                      else
                        Text(
                          '₹--',
                          style: AppTextStyles.currencyCompact.copyWith(
                            color: AppColors.grey400,
                          ),
                        ),
                      Text(
                        'Net Worth',
                        style: AppTextStyles.bodyExtraSmall.copyWith(
                          color: AppColors.grey600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.primaryBlue.withOpacity(0.05),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: AppColors.primaryBlue.withOpacity(0.1),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.account_balance_wallet,
                  color: AppColors.primaryBlue,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (isLoadingAny && !creditReportState.hasData)
                        _buildLoadingText()
                      else if (creditReportState.hasData)
                        Text(
                          creditReportState.creditScore?.toString() ?? '--',
                          style: AppTextStyles.currencyCompact.copyWith(
                            color: AppColors.primaryBlue,
                          ),
                        )
                      else
                        Text(
                          '--',
                          style: AppTextStyles.currencyCompact.copyWith(
                            color: AppColors.grey400,
                          ),
                        ),
                      Text(
                        'Credit Score',
                        style: AppTextStyles.bodyExtraSmall.copyWith(
                          color: AppColors.grey600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildLoadingText() {
    return Container(
      height: 16,
      width: 80,
      decoration: BoxDecoration(
        color: AppColors.grey200,
        borderRadius: BorderRadius.circular(4),
      ),
    );
  }

  Widget _buildMainContent() {
    return Expanded(
      child: RefreshIndicator(
        color: AppColors.primaryBlue,
        onRefresh: () async {
          await _loadFinancialData();
        },
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildFinancialMetrics(),
              const SizedBox(height: 24),
              _buildQuickActions(),
              const SizedBox(height: 24),
              _buildGoalsSection(),
              const SizedBox(height: 24),
              _buildRecentActivity(),
              const SizedBox(height: 20), // Extra space for pull-to-refresh
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFinancialMetrics() {
    final netWorthState = ref.watch(netWorthProvider);
    final epfState = ref.watch(epfDetailsProvider);
    final mfState = ref.watch(mfTransactionsProvider);
    final isLoadingAny = ref.watch(isLoadingAnyDataProvider);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Financial Overview',
              style: AppTextStyles.heading3.copyWith(
                color: AppColors.grey900,
              ),
            ),
            Row(
              children: [
                if (isLoadingAny)
                  SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(AppColors.primaryBlue),
                    ),
                  ),
                const SizedBox(width: 8),
                Container(
                  decoration: BoxDecoration(
                    color: AppColors.grey100,
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: IconButton(
                    icon: Icon(Icons.refresh, color: AppColors.grey700, size: 16),
                    onPressed: isLoadingAny ? null : _loadFinancialData,
                    constraints: const BoxConstraints(
                      minWidth: 28,
                      minHeight: 28,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 16),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.4,
          children: [
            CompactFinancialCard(
              title: 'Total Assets',
              value: netWorthState.hasData 
                  ? DataFormatters.formatCompactCurrency(netWorthState.data!.netWorthResponse.totalAssets)
                  : '₹--',
              subtitle: netWorthState.isFromCache ? 'Cached data' : 'Live data',
              icon: Icons.account_balance,
              accentColor: AppColors.success,
            ),
            CompactFinancialCard(
              title: 'EPF Balance',
              value: epfState.hasData 
                  ? epfState.formattedBalance ?? '₹--'
                  : '₹--',
              subtitle: epfState.isFromCache ? 'Cached data' : 'Live data',
              icon: Icons.savings,
              accentColor: AppColors.primaryBlue,
            ),
            CompactFinancialCard(
              title: 'MF Investments',
              value: mfState.hasData 
                  ? DataFormatters.formatCompactCurrency(mfState.totalInvested ?? 0)
                  : '₹--',
              subtitle: mfState.hasData 
                  ? '${mfState.transactionCount ?? 0} transactions'
                  : 'No data',
              icon: Icons.show_chart,
              accentColor: AppColors.accentTeal,
            ),
            CompactFinancialCard(
              title: 'Liabilities',
              value: netWorthState.hasData 
                  ? DataFormatters.formatCompactCurrency(netWorthState.data!.netWorthResponse.totalLiabilities)
                  : '₹--',
              subtitle: netWorthState.isFromCache ? 'Cached data' : 'Live data',
              icon: Icons.receipt_long,
              accentColor: AppColors.error,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Actions',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.grey900,
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: CompactActionCard(
                title: 'AI Chat',
                subtitle: 'Get financial advice',
                icon: Icons.chat_bubble_outline,
                accentColor: AppColors.primaryBlue,
                onTap: () => NavigationService.navigateTo(context, AppRouter.chat),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: CompactActionCard(
                title: 'Add Transaction',
                subtitle: 'Record expense',
                icon: Icons.add_circle_outline,
                accentColor: AppColors.accentTeal,
                onTap: () => NavigationService.navigateTo(context, AppRouter.transactions),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildGoalsSection() {
    final netWorthState = ref.watch(netWorthProvider);
    final epfState = ref.watch(epfDetailsProvider);
    
    // Calculate emergency fund target (6 months of expenses, estimated based on net worth)
    double emergencyFundTarget = 300000; // Default target
    double emergencyFundCurrent = 0;
    
    if (netWorthState.hasData) {
      // Get savings account balance as emergency fund
      final savingsAccounts = netWorthState.data!.accountDetailsBulkResponse.savingsAccounts;
      if (savingsAccounts.isNotEmpty) {
        emergencyFundCurrent = savingsAccounts.first.depositSummary?.currentBalance.value ?? 0;
      }
      
      // Set target based on net worth (rough estimate)
      final netWorth = netWorthState.data!.netWorthResponse.totalNetWorthValue.value;
      emergencyFundTarget = (netWorth * 0.2).clamp(300000, 1000000); // 20% of net worth, min 3L, max 10L
    }
    
    // Calculate retirement fund progress
    double retirementFundCurrent = epfState.totalBalance ?? 0;
    double retirementFundTarget = 10000000; // 1 crore target
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Financial Goals',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.grey900,
          ),
        ),
        const SizedBox(height: 16),
        CompactProgressCard(
          title: 'Emergency Fund',
          currentValue: DataFormatters.formatCompactCurrency(emergencyFundCurrent),
          targetValue: DataFormatters.formatCompactCurrency(emergencyFundTarget),
          progress: emergencyFundTarget > 0 ? (emergencyFundCurrent / emergencyFundTarget).clamp(0.0, 1.0) : 0.0,
          progressColor: AppColors.success,
          onTap: () => NavigationService.navigateTo(context, AppRouter.goalsPlanning),
        ),
        const SizedBox(height: 12),
        CompactProgressCard(
          title: 'Retirement Fund',
          currentValue: DataFormatters.formatCompactCurrency(retirementFundCurrent),
          targetValue: DataFormatters.formatCompactCurrency(retirementFundTarget),
          progress: retirementFundTarget > 0 ? (retirementFundCurrent / retirementFundTarget).clamp(0.0, 1.0) : 0.0,
          progressColor: AppColors.primaryBlue,
          onTap: () => NavigationService.navigateTo(context, AppRouter.goalsPlanning),
        ),
      ],
    );
  }

  Widget _buildRecentActivity() {
    final mfState = ref.watch(mfTransactionsProvider);
    final netWorthState = ref.watch(netWorthProvider);
    
    // Get recent transactions (last 7 days)
    final recentTransactions = mfState.hasData 
        ? mfState.data!.getRecentTransactions(7)
        : <MfTransaction>[];
    
    // Calculate totals for recent activity
    double totalInvestments = 0;
    double totalRedemptions = 0;
    double totalCurrentValue = 0;
    
    for (final transaction in recentTransactions) {
      if (transaction.isBuy) {
        totalInvestments += transaction.transactionAmount.value;
      } else if (transaction.isSell) {
        totalRedemptions += transaction.transactionAmount.value;
      }
    }
    
    // Get current value from net worth
    if (netWorthState.hasData) {
      final mfAssets = netWorthState.data!.netWorthResponse.assetValues
          .where((asset) => asset.netWorthAttribute == 'ASSET_TYPE_MUTUAL_FUND');
      if (mfAssets.isNotEmpty) {
        totalCurrentValue = mfAssets.first.value.value;
      }
    }
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Recent Activity',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.grey900,
          ),
        ),
        const SizedBox(height: 16),
        CompactSummaryCard(
          title: 'Investment Activity',
          items: [
            CompactSummaryItem(
              label: 'Total Invested',
              value: mfState.hasData 
                  ? DataFormatters.formatCompactCurrency(mfState.totalInvested ?? 0)
                  : '₹--',
              color: AppColors.success,
            ),
            CompactSummaryItem(
              label: 'Total Redeemed',
              value: mfState.hasData 
                  ? DataFormatters.formatCompactCurrency(mfState.totalRedeemed ?? 0)
                  : '₹--',
              color: AppColors.error,
            ),
            CompactSummaryItem(
              label: 'Current Value',
              value: DataFormatters.formatCompactCurrency(totalCurrentValue),
              color: AppColors.primaryBlue,
            ),
          ],
          onTap: () => NavigationService.navigateTo(context, AppRouter.portfolioAnalysis),
        ),
        if (mfState.hasData && recentTransactions.isNotEmpty) ...[
          const SizedBox(height: 12),
          CompactSummaryCard(
            title: 'Last 7 Days',
            items: [
              CompactSummaryItem(
                label: 'New Investments',
                value: DataFormatters.formatCompactCurrency(totalInvestments),
                color: AppColors.success,
              ),
              CompactSummaryItem(
                label: 'Redemptions',
                value: DataFormatters.formatCompactCurrency(totalRedemptions),
                color: AppColors.error,
              ),
              CompactSummaryItem(
                label: 'Transactions',
                value: recentTransactions.length.toString(),
                color: AppColors.primaryBlue,
              ),
            ],
            onTap: () => NavigationService.navigateTo(context, AppRouter.portfolioAnalysis),
          ),
        ],
      ],
    );
  }
}