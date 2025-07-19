import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/app_card.dart';
import '../../../core/widgets/app_button.dart';
import '../../../core/navigation/app_router.dart';
import '../../../core/services/navigation_service.dart';
import '../../fi_money/providers/fi_money_provider.dart';
import '../../fi_money/utils/data_formatters.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final netWorthState = ref.watch(netWorthProvider);
    final creditReportState = ref.watch(creditReportProvider);
    final mfTransactionsState = ref.watch(mfTransactionsProvider);
    return Scaffold(
      backgroundColor: AppColors.backgroundSecondary,
      appBar: AppBar(
        title: Text(
          'Profile',
          style: AppTextStyles.heading4.copyWith(
            color: AppColors.grey900,
            fontWeight: FontWeight.w700,
          ),
        ),
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.grey900,
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(Icons.settings, color: AppColors.grey600),
            onPressed: () {
              NavigationService.navigateTo(context, AppRouter.settings);
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            _buildProfileHeader(netWorthState, creditReportState),
            const SizedBox(height: 24),
            _buildFinancialOverview(netWorthState, creditReportState, mfTransactionsState),
            const SizedBox(height: 16),
            _buildQuickActions(context),
            const SizedBox(height: 16),
            _buildConnectedAccounts(),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileHeader(
    NetWorthState netWorthState,
    CreditReportState creditReportState,
  ) {
    final netWorth = netWorthState.data;
    final creditReport = creditReportState.data;
    
    // Remove hardcoded goals and connected accounts - show only if real data exists
    int connectedAccounts = netWorth?.accountDetailsBulkResponse.accountDetailsMap.length ?? 0;
    String creditScore = creditReport?.creditReports.isNotEmpty == true
        ? creditReport!.creditReports.first.creditReportData.score.bureauScore
        : '--';
    return AppCard(
      child: Column(
        children: [
          CircleAvatar(
            radius: 40,
            backgroundColor: AppColors.primaryBlue,
            child: const Icon(
              Icons.person,
              size: 40,
              color: AppColors.white,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'User', // No real user data available - keeping minimal
            style: AppTextStyles.heading3,
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              if (connectedAccounts > 0)
                _buildStatItem('Connected', connectedAccounts.toString()),
              _buildStatItem('Score', creditScore),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.primaryBlue,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: AppTextStyles.bodySmall.copyWith(
            color: AppColors.grey600,
          ),
        ),
      ],
    );
  }

  Widget _buildFinancialOverview(
    NetWorthState netWorthState,
    CreditReportState creditReportState,
    MfTransactionsState mfTransactionsState,
  ) {
    final netWorth = netWorthState.data;
    final creditReport = creditReportState.data;
    final mfTransactions = mfTransactionsState.data;
    
    // Calculate real values from Fi Money data
    String netWorthValue = netWorth?.netWorthResponse.totalNetWorthValue.formattedCompact ?? '--';
    
    // Calculate monthly SIP from MF transactions
    double monthlySIP = 0;
    if (mfTransactions?.transactions.isNotEmpty == true) {
      final sipTransactions = mfTransactions!.transactions.where(
        (t) => t.transactionMode.toLowerCase() == 'sip' || t.transactionMode.toLowerCase() == 'n'
      );
      if (sipTransactions.isNotEmpty) {
        monthlySIP = sipTransactions.map((t) => t.transactionAmount.value).reduce((a, b) => a + b);
      }
    }
    String monthlySIPValue = monthlySIP > 0 ? DataFormatters.formatCurrency(monthlySIP) : '--';
    
    String creditScore = creditReport?.creditReports.isNotEmpty == true
        ? creditReport!.creditReports.first.creditReportData.score.bureauScore
        : '--';
    
    // Calculate portfolio return from MF analytics
    String portfolioReturn = '--';
    if (netWorth?.mfSchemeAnalytics.isNotEmpty == true) {
      final schemes = netWorth!.mfSchemeAnalytics;
      double totalCurrentValue = 0;
      double totalInvestedValue = 0;
      
      for (final scheme in schemes) {
        final analytics = scheme.enrichedAnalytics.analytics.schemeDetails;
        totalCurrentValue += analytics.currentValue.value;
        totalInvestedValue += analytics.investedValue.value;
      }
      
      if (totalInvestedValue > 0) {
        double returnPercentage = ((totalCurrentValue - totalInvestedValue) / totalInvestedValue) * 100;
        portfolioReturn = '${returnPercentage.toStringAsFixed(1)}%';
      }
    }
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Financial Overview',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildOverviewItem(
                  'Net Worth',
                  netWorthValue,
                  Icons.account_balance_wallet,
                  AppColors.success,
                ),
              ),
              Expanded(
                child: _buildOverviewItem(
                  'Monthly SIP',
                  monthlySIPValue,
                  Icons.trending_up,
                  AppColors.primaryBlue,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildOverviewItem(
                  'Credit Score',
                  creditScore,
                  Icons.credit_score,
                  AppColors.success,
                ),
              ),
              Expanded(
                child: _buildOverviewItem(
                  'Portfolio Return',
                  portfolioReturn,
                  Icons.analytics,
                  AppColors.success,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOverviewItem(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 8),
        Text(
          value,
          style: AppTextStyles.bodyLarge.copyWith(
            fontWeight: FontWeight.w600,
            color: color,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: AppTextStyles.bodySmall.copyWith(
            color: AppColors.grey600,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Quick Actions',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          _buildActionItem(
            context,
            'Portfolio Analysis',
            'Check your investment performance',
            Icons.pie_chart,
            AppColors.pastAgentColor,
            () {
              NavigationService.navigateTo(context, AppRouter.portfolioAnalysis);
            },
          ),
          const SizedBox(height: 12),
          _buildActionItem(
            context,
            'Spending Optimization',
            'Optimize your current spending',
            Icons.savings,
            AppColors.presentAgentColor,
            () {
              NavigationService.navigateTo(context, AppRouter.spendingOptimization);
            },
          ),
          const SizedBox(height: 12),
          _buildActionItem(
            context,
            'Goals Planning',
            'Plan your future milestones',
            Icons.flag,
            AppColors.futureAgentColor,
            () {
              NavigationService.navigateTo(context, AppRouter.goalsPlanning);
            },
          ),
          const SizedBox(height: 12),
          _buildActionItem(
            context,
            'Transaction History',
            'View all your transactions',
            Icons.history,
            AppColors.primaryBlue,
            () {
              NavigationService.navigateTo(context, AppRouter.transactions);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildActionItem(
    BuildContext context,
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: color, size: 20),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: AppTextStyles.bodyMedium.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.grey600,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.arrow_forward_ios,
              size: 16,
              color: AppColors.grey400,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConnectedAccounts() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Connected Accounts',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          _buildAccountItem(
            'Fi Money',
            'Connected',
            Icons.account_balance,
            AppColors.success,
            true,
          ),
          const SizedBox(height: 12),
          _buildAccountItem(
            'Bank Account',
            'Not Connected',
            Icons.account_balance_wallet,
            AppColors.grey500,
            false,
          ),
          const SizedBox(height: 16),
          AppButton(
            text: 'Connect More Accounts',
            type: ButtonType.outline,
            fullWidth: true,
            onPressed: () {
              // Navigate to connection screen
            },
          ),
        ],
      ),
    );
  }

  Widget _buildAccountItem(
    String name,
    String status,
    IconData icon,
    Color color,
    bool isConnected,
  ) {
    return Row(
      children: [
        Icon(icon, color: color, size: 24),
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
                status,
                style: AppTextStyles.bodySmall.copyWith(
                  color: color,
                ),
              ),
            ],
          ),
        ),
        if (isConnected)
          Icon(
            Icons.check_circle,
            color: AppColors.success,
            size: 20,
          ),
      ],
    );
  }
}