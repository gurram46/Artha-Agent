import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/app_card.dart';

class PortfolioScreen extends StatelessWidget {
  const PortfolioScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Portfolio'),
        backgroundColor: AppColors.primaryBlue,
        foregroundColor: AppColors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            _buildPortfolioSummary(),
            const SizedBox(height: 16),
            _buildHoldingsList(),
          ],
        ),
      ),
    );
  }

  Widget _buildPortfolioSummary() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Portfolio Summary',
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
                      'Total Value',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.grey600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '₹18,50,000',
                      style: AppTextStyles.currencyLarge,
                    ),
                  ],
                ),
              ),
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
                      style: AppTextStyles.percentage.copyWith(
                        color: AppColors.success,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHoldingsList() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Holdings',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          _buildHoldingItem(
            'Axis Bluechip Fund',
            '₹5,50,000',
            '22.5%',
            true,
          ),
          const SizedBox(height: 12),
          _buildHoldingItem(
            'HDFC Top 100 Fund',
            '₹4,20,000',
            '18.2%',
            true,
          ),
          const SizedBox(height: 12),
          _buildHoldingItem(
            'Mirae Asset Large Cap',
            '₹3,80,000',
            '15.1%',
            true,
          ),
          const SizedBox(height: 12),
          _buildHoldingItem(
            'Kotak Small Cap Fund',
            '₹2,50,000',
            '8.9%',
            true,
          ),
          const SizedBox(height: 12),
          _buildHoldingItem(
            'HDFC Liquid Fund',
            '₹2,50,000',
            '6.2%',
            true,
          ),
        ],
      ),
    );
  }

  Widget _buildHoldingItem(String name, String value, String returns, bool isProfit) {
    return Row(
      children: [
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
              const SizedBox(height: 4),
              Text(
                value,
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.grey600,
                ),
              ),
            ],
          ),
        ),
        Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              returns,
              style: AppTextStyles.bodyMedium.copyWith(
                fontWeight: FontWeight.w600,
                color: isProfit ? AppColors.success : AppColors.error,
              ),
            ),
            Icon(
              isProfit ? Icons.trending_up : Icons.trending_down,
              size: 16,
              color: isProfit ? AppColors.success : AppColors.error,
            ),
          ],
        ),
      ],
    );
  }
}