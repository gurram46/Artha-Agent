import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/app_card.dart';
import '../../../core/widgets/app_button.dart';

class PresentOptimizationTab extends StatelessWidget {
  const PresentOptimizationTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildAgentHeader(),
          const SizedBox(height: 24),
          _buildCurrentFinancialHealth(),
          const SizedBox(height: 16),
          _buildSpendingAnalysis(),
          const SizedBox(height: 16),
          _buildOptimizationOpportunities(),
          const SizedBox(height: 16),
          _buildActionButton(),
        ],
      ),
    );
  }

  Widget _buildAgentHeader() {
    return AgentCard(
      agentName: 'Present Agent',
      description: 'Optimizing your current financial situation and cash flow',
      agentColor: AppColors.presentAgentColor,
      icon: Icons.today,
      isActive: false,
    );
  }

  Widget _buildCurrentFinancialHealth() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Current Financial Health',
                style: AppTextStyles.heading4,
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: AppColors.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  'Excellent',
                  style: AppTextStyles.labelSmall.copyWith(
                    color: AppColors.success,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Credit Score',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.grey600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '780',
                      style: AppTextStyles.currencyLarge.copyWith(
                        color: AppColors.success,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Liquid Cash',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.grey600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '₹2,50,000',
                      style: AppTextStyles.currency.copyWith(
                        color: AppColors.grey900,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          LinearProgressIndicator(
            value: 0.85,
            backgroundColor: AppColors.grey300,
            valueColor: AlwaysStoppedAnimation<Color>(AppColors.success),
          ),
          const SizedBox(height: 8),
          Text(
            'Financial Health Score: 85/100',
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.grey600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSpendingAnalysis() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Monthly Spending Analysis',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          _buildSpendingItem(
            'Monthly Income',
            '₹1,20,000',
            null,
            Icons.account_balance_wallet,
            AppColors.success,
          ),
          const SizedBox(height: 12),
          _buildSpendingItem(
            'Fixed Expenses',
            '₹40,000',
            '33%',
            Icons.home,
            AppColors.warning,
          ),
          const SizedBox(height: 12),
          _buildSpendingItem(
            'Investments',
            '₹35,000',
            '29%',
            Icons.trending_up,
            AppColors.primaryBlue,
          ),
          const SizedBox(height: 12),
          _buildSpendingItem(
            'Available Surplus',
            '₹45,000',
            '38%',
            Icons.savings,
            AppColors.success,
          ),
        ],
      ),
    );
  }

  Widget _buildSpendingItem(
    String title,
    String amount,
    String? percentage,
    IconData icon,
    Color color,
  ) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            icon,
            size: 20,
            color: color,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            title,
            style: AppTextStyles.bodyMedium.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              amount,
              style: AppTextStyles.bodyMedium.copyWith(
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
            if (percentage != null)
              Text(
                percentage,
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.grey600,
                ),
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildOptimizationOpportunities() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Optimization Opportunities',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          _buildOpportunityItem(
            'Reduce subscription services',
            'Save ₹2,500/month',
            Icons.subscriptions,
            AppColors.warning,
          ),
          const SizedBox(height: 12),
          _buildOpportunityItem(
            'Optimize credit card usage',
            'Improve credit score by 15 points',
            Icons.credit_card,
            AppColors.primaryBlue,
          ),
          const SizedBox(height: 12),
          _buildOpportunityItem(
            'Tax saving investments',
            'Save ₹15,000 in taxes',
            Icons.receipt_long,
            AppColors.success,
          ),
        ],
      ),
    );
  }

  Widget _buildOpportunityItem(
    String title,
    String benefit,
    IconData icon,
    Color color,
  ) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            icon,
            size: 20,
            color: color,
          ),
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
                benefit,
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
          color: AppColors.grey500,
        ),
      ],
    );
  }

  Widget _buildActionButton() {
    return AppButton(
      text: 'Start Optimization',
      type: ButtonType.primary,
      fullWidth: true,
      onPressed: () {
        // Navigate to optimization details
      },
    );
  }
}