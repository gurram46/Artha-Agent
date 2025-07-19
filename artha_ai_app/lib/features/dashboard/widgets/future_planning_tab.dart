import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/app_card.dart';
import '../../../core/widgets/app_button.dart';

class FuturePlanningTab extends StatelessWidget {
  const FuturePlanningTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildAgentHeader(),
          const SizedBox(height: 24),
          _buildGoalTracker(),
          const SizedBox(height: 16),
          _buildRetirementPlanning(),
          const SizedBox(height: 16),
          _buildLifeEventPlanning(),
          const SizedBox(height: 16),
          _buildActionButton(),
        ],
      ),
    );
  }

  Widget _buildAgentHeader() {
    return AgentCard(
      agentName: 'Future Agent',
      description: 'Planning your financial goals and life events',
      agentColor: AppColors.futureAgentColor,
      icon: Icons.timeline,
      isActive: false,
    );
  }

  Widget _buildGoalTracker() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Goal Tracker',
                style: AppTextStyles.heading4,
              ),
              Text(
                '3 Active Goals',
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.grey600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildGoalItem(
            'Home Purchase',
            '₹50,00,000',
            '₹32,50,000',
            0.65,
            '2 years left',
            Icons.home,
            AppColors.success,
          ),
          const SizedBox(height: 16),
          _buildGoalItem(
            'Child Education',
            '₹25,00,000',
            '₹8,75,000',
            0.35,
            '12 years left',
            Icons.school,
            AppColors.warning,
          ),
          const SizedBox(height: 16),
          _buildGoalItem(
            'Dream Car',
            '₹15,00,000',
            '₹4,50,000',
            0.30,
            '18 months left',
            Icons.directions_car,
            AppColors.primaryBlue,
          ),
        ],
      ),
    );
  }

  Widget _buildGoalItem(
    String goalName,
    String targetAmount,
    String currentAmount,
    double progress,
    String timeLeft,
    IconData icon,
    Color color,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
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
                    goalName,
                    style: AppTextStyles.bodyMedium.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    '$currentAmount / $targetAmount',
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.grey600,
                    ),
                  ),
                ],
              ),
            ),
            Text(
              timeLeft,
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.grey600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        LinearProgressIndicator(
          value: progress,
          backgroundColor: AppColors.grey300,
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
        const SizedBox(height: 4),
        Text(
          '${(progress * 100).toInt()}% Complete',
          style: AppTextStyles.bodySmall.copyWith(
            color: AppColors.grey600,
          ),
        ),
      ],
    );
  }

  Widget _buildRetirementPlanning() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Retirement Planning',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Target Corpus',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.grey600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '₹5,00,00,000',
                      style: AppTextStyles.currencyLarge.copyWith(
                        color: AppColors.futureAgentColor,
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
                      'Current Projection',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.grey600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '₹3,20,00,000',
                      style: AppTextStyles.currency.copyWith(
                        color: AppColors.warning,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.futureAgentColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Recommendation',
                  style: AppTextStyles.bodyMedium.copyWith(
                    fontWeight: FontWeight.w600,
                    color: AppColors.futureAgentColor,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Increase SIP by ₹12,000/month to reach your retirement goal',
                  style: AppTextStyles.bodyMedium,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLifeEventPlanning() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Life Event Planning',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          _buildLifeEventItem(
            'Marriage Expenses',
            '₹8,00,000',
            '6 months',
            Icons.favorite,
            AppColors.error,
          ),
          const SizedBox(height: 12),
          _buildLifeEventItem(
            'Child Birth & Care',
            '₹3,00,000',
            '2 years',
            Icons.child_care,
            AppColors.presentAgentColor,
          ),
          const SizedBox(height: 12),
          _buildLifeEventItem(
            'Emergency Fund',
            '₹6,00,000',
            'Ongoing',
            Icons.security,
            AppColors.warning,
          ),
        ],
      ),
    );
  }

  Widget _buildLifeEventItem(
    String event,
    String amount,
    String timeline,
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
                event,
                style: AppTextStyles.bodyMedium.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                'Timeline: $timeline',
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

  Widget _buildActionButton() {
    return AppButton(
      text: 'Create New Goal',
      type: ButtonType.primary,
      fullWidth: true,
      onPressed: () {
        // Navigate to goal creation
      },
    );
  }
}