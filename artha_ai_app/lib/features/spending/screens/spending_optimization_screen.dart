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

class SpendingOptimizationScreen extends ConsumerWidget {
  const SpendingOptimizationScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final netWorthState = ref.watch(netWorthProvider);
    
    return AppScaffold(
      title: 'Spending Optimization',
      body: Container(
        color: AppColors.backgroundSecondary,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDataUnavailableMessage(),
              const SizedBox(height: 16),
              if (netWorthState.data?.accountDetailsBulkResponse.savingsAccounts.isNotEmpty == true)
                _buildAccountSummary(netWorthState.data!),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDataUnavailableMessage() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.info_outline, color: AppColors.primaryBlue, size: 24),
              const SizedBox(width: 12),
              Text(
                'Spending Data Unavailable',
                style: AppTextStyles.heading4.copyWith(
                  color: AppColors.grey900,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            'Spending optimization features require transaction data from bank accounts. Connect your bank accounts to access:',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.grey600,
            ),
          ),
          const SizedBox(height: 12),
          _buildFeatureItem('• Spending breakdown by category'),
          _buildFeatureItem('• Monthly spending trends'),
          _buildFeatureItem('• Personalized optimization tips'),
          _buildFeatureItem('• Budget recommendations'),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.primaryBlue.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.primaryBlue.withOpacity(0.2)),
            ),
            child: Row(
              children: [
                Icon(Icons.lightbulb_outline, color: AppColors.primaryBlue),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Connect your bank accounts to unlock spending insights',
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: AppColors.primaryBlue,
                      fontWeight: FontWeight.w500,
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

  Widget _buildFeatureItem(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Text(
        text,
        style: AppTextStyles.bodyMedium.copyWith(
          color: AppColors.grey700,
        ),
      ),
    );
  }

  Widget _buildAccountSummary(FullNetWorthData netWorth) {
    final savingsAccounts = netWorth.accountDetailsBulkResponse.savingsAccounts;
    
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Connected Accounts',
            style: AppTextStyles.heading4.copyWith(
              color: AppColors.grey900,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 16),
          ...savingsAccounts.map((account) {
            final balance = account.depositSummary?.currentBalance.formattedCompact ?? '--';
            final bankName = account.accountDetails.fipMeta.displayName;
            final accountNumber = account.accountDetails.maskedAccountNumber;
            
            return Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.primaryBlue.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.primaryBlue.withOpacity(0.2)),
              ),
              child: Row(
                children: [
                  Icon(Icons.account_balance, color: AppColors.primaryBlue),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          bankName,
                          style: AppTextStyles.bodyMedium.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          'Account: $accountNumber',
                          style: AppTextStyles.bodySmall.copyWith(
                            color: AppColors.grey600,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Text(
                    balance,
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: AppColors.primaryBlue,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.warning.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline, color: AppColors.warning),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Spending analysis requires transaction history data which is not available in the current API.',
                    style: AppTextStyles.bodySmall.copyWith(
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
}