import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/app_card.dart';
import '../../../core/widgets/app_button.dart';

class FiConnectionScreen extends StatelessWidget {
  const FiConnectionScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Fi Money Integration'),
        backgroundColor: AppColors.primaryBlue,
        foregroundColor: AppColors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            _buildHeader(),
            const SizedBox(height: 24),
            _buildBenefits(),
            const SizedBox(height: 24),
            _buildConnectionStatus(),
            const SizedBox(height: 24),
            _buildConnectButton(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return AppCard(
      child: Column(
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: AppColors.primaryBlue.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.account_balance_wallet,
              size: 40,
              color: AppColors.primaryBlue,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Connect Fi Money',
            style: AppTextStyles.heading2,
          ),
          const SizedBox(height: 8),
          Text(
            'Get real-time access to your financial data for personalized advice',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.grey600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildBenefits() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'What you get:',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          _buildBenefitItem(
            'Real Portfolio Analysis',
            'Actual XIRR and performance metrics',
            Icons.analytics,
            AppColors.success,
          ),
          const SizedBox(height: 12),
          _buildBenefitItem(
            'Live Credit Score',
            'Monitor your credit health',
            Icons.credit_score,
            AppColors.primaryBlue,
          ),
          const SizedBox(height: 12),
          _buildBenefitItem(
            'Cash Flow Tracking',
            'Real-time account balances',
            Icons.account_balance,
            AppColors.warning,
          ),
          const SizedBox(height: 12),
          _buildBenefitItem(
            'Goal Progress',
            'Track actual vs target amounts',
            Icons.flag,
            AppColors.futureAgentColor,
          ),
        ],
      ),
    );
  }

  Widget _buildBenefitItem(String title, String description, IconData icon, Color color) {
    return Row(
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
                description,
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.grey600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildConnectionStatus() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Connection Status',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          _buildStatusItem('Fi Money App', false),
          const SizedBox(height: 12),
          _buildStatusItem('Bank Accounts', false),
          const SizedBox(height: 12),
          _buildStatusItem('Mutual Funds', false),
          const SizedBox(height: 12),
          _buildStatusItem('Credit Score', false),
          const SizedBox(height: 12),
          _buildStatusItem('EPF Account', false),
        ],
      ),
    );
  }

  Widget _buildStatusItem(String item, bool isConnected) {
    return Row(
      children: [
        Icon(
          isConnected ? Icons.check_circle : Icons.radio_button_unchecked,
          color: isConnected ? AppColors.success : AppColors.grey400,
          size: 20,
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            item,
            style: AppTextStyles.bodyMedium,
          ),
        ),
        if (isConnected)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.success.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              'Connected',
              style: AppTextStyles.labelSmall.copyWith(
                color: AppColors.success,
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildConnectButton() {
    return AppButton(
      text: 'Connect Fi Money',
      type: ButtonType.primary,
      fullWidth: true,
      onPressed: () {
        // Show connection dialog or redirect to Fi Money
        _showConnectionDialog();
      },
    );
  }

  void _showConnectionDialog() {
    // This would typically redirect to Fi Money app or show connection instructions
    // For now, just show a placeholder dialog
  }
}