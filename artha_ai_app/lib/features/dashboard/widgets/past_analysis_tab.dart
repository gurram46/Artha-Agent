import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/app_card.dart';
import '../../../core/widgets/app_button.dart';

class PastAnalysisTab extends StatelessWidget {
  const PastAnalysisTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildAgentHeader(),
          const SizedBox(height: 24),
          _buildPortfolioPerformance(),
          const SizedBox(height: 16),
          _buildInvestmentHistory(),
          const SizedBox(height: 16),
          _buildKeyInsights(),
          const SizedBox(height: 16),
          _buildActionButton(),
        ],
      ),
    );
  }

  Widget _buildAgentHeader() {
    return AgentCard(
      agentName: 'Past Agent',
      description: 'Analyzing your investment history and portfolio performance',
      agentColor: AppColors.pastAgentColor,
      icon: Icons.history,
      isActive: false,
    );
  }

  Widget _buildPortfolioPerformance() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Portfolio Performance',
                style: AppTextStyles.heading4,
              ),
              Icon(
                Icons.trending_up,
                color: AppColors.success,
                size: 24,
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
                      'Total Returns',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.grey600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '15.8% XIRR',
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
                      'Best Performer',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.grey600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Axis Bluechip',
                      style: AppTextStyles.bodyMedium.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      '22% XIRR',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.success,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            height: 120,
            decoration: BoxDecoration(
              color: AppColors.grey100,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.bar_chart,
                    size: 40,
                    color: AppColors.grey500,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Performance Chart',
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.grey600,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInvestmentHistory() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Investment History',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          _buildInvestmentItem(
            'Mutual Fund SIPs',
            '₹35,000/month',
            '24 months consistent',
            Icons.trending_up,
            AppColors.success,
          ),
          const SizedBox(height: 12),
          _buildInvestmentItem(
            'Lump Sum Investments',
            '₹2,50,000',
            'Bonus investments',
            Icons.account_balance_wallet,
            AppColors.primaryBlue,
          ),
          const SizedBox(height: 12),
          _buildInvestmentItem(
            'Emergency Fund',
            '₹1,80,000',
            'Liquid funds',
            Icons.security,
            AppColors.warning,
          ),
        ],
      ),
    );
  }

  Widget _buildInvestmentItem(
    String title,
    String amount,
    String subtitle,
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
                subtitle,
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.grey600,
                ),
              ),
            ],
          ),
        ),
        Text(
          amount,
          style: AppTextStyles.bodyMedium.copyWith(
            fontWeight: FontWeight.w600,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildKeyInsights() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Key Insights',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          _buildInsightItem(
            'Excellent SIP discipline with 100% consistency',
            Icons.check_circle,
            AppColors.success,
          ),
          const SizedBox(height: 12),
          _buildInsightItem(
            'Portfolio outperformed market by 3.8%',
            Icons.trending_up,
            AppColors.success,
          ),
          const SizedBox(height: 12),
          _buildInsightItem(
            'Optimal timing on bonus investments',
            Icons.schedule,
            AppColors.primaryBlue,
          ),
        ],
      ),
    );
  }

  Widget _buildInsightItem(String text, IconData icon, Color color) {
    return Row(
      children: [
        Icon(
          icon,
          size: 20,
          color: color,
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            text,
            style: AppTextStyles.bodyMedium,
          ),
        ),
      ],
    );
  }

  Widget _buildActionButton() {
    return AppButton(
      text: 'View Detailed Analysis',
      type: ButtonType.primary,
      fullWidth: true,
      onPressed: () {
        // Navigate to detailed analysis
      },
    );
  }
}