import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// Compact Financial Metric Card for dashboard
class CompactFinancialCard extends StatelessWidget {
  final String title;
  final String value;
  final String? subtitle;
  final String? changeText;
  final double? changePercentage;
  final bool? isPositive;
  final IconData? icon;
  final Color? accentColor;
  final VoidCallback? onTap;

  const CompactFinancialCard({
    Key? key,
    required this.title,
    required this.value,
    this.subtitle,
    this.changeText,
    this.changePercentage,
    this.isPositive,
    this.icon,
    this.accentColor,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: AppColors.grey200,
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: AppColors.grey200.withOpacity(0.3),
              blurRadius: 2,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // Header row with title and icon
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    title,
                    style: AppTextStyles.labelMedium.copyWith(
                      color: AppColors.grey600,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (icon != null)
                  Icon(
                    icon,
                    size: 16,
                    color: accentColor ?? AppColors.grey500,
                  ),
              ],
            ),
            const SizedBox(height: 8),
            // Value
            Text(
              value,
              style: AppTextStyles.currencyDisplay.copyWith(
                color: AppColors.grey900,
              ),
            ),
            // Change indicator and subtitle
            if (changeText != null || subtitle != null) ...[
              const SizedBox(height: 6),
              Row(
                children: [
                  if (changeText != null && changePercentage != null) ...[
                    Icon(
                      isPositive == true ? Icons.trending_up : Icons.trending_down,
                      size: 12,
                      color: isPositive == true ? AppColors.success : AppColors.error,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      changeText!,
                      style: AppTextStyles.bodyExtraSmall.copyWith(
                        color: isPositive == true ? AppColors.success : AppColors.error,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ] else if (subtitle != null) ...[
                    Text(
                      subtitle!,
                      style: AppTextStyles.bodyExtraSmall.copyWith(
                        color: AppColors.grey500,
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Compact Action Card for quick actions
class CompactActionCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color accentColor;
  final VoidCallback onTap;

  const CompactActionCard({
    Key? key,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.accentColor,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: AppColors.grey200,
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: AppColors.grey200.withOpacity(0.3),
              blurRadius: 2,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: accentColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                icon,
                size: 20,
                color: accentColor,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: AppTextStyles.labelLarge.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.grey900,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: AppTextStyles.bodyExtraSmall.copyWith(
                color: AppColors.grey600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Compact Progress Card for goals
class CompactProgressCard extends StatelessWidget {
  final String title;
  final String currentValue;
  final String targetValue;
  final double progress;
  final Color progressColor;
  final VoidCallback? onTap;

  const CompactProgressCard({
    Key? key,
    required this.title,
    required this.currentValue,
    required this.targetValue,
    required this.progress,
    required this.progressColor,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: AppColors.grey200,
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: AppColors.grey200.withOpacity(0.3),
              blurRadius: 2,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              title,
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.grey600,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Text(
                  currentValue,
                  style: AppTextStyles.currencyCompact.copyWith(
                    color: progressColor,
                  ),
                ),
                Text(
                  ' / $targetValue',
                  style: AppTextStyles.bodyExtraSmall.copyWith(
                    color: AppColors.grey500,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: LinearProgressIndicator(
                    value: progress,
                    backgroundColor: AppColors.grey200,
                    valueColor: AlwaysStoppedAnimation<Color>(progressColor),
                    minHeight: 3,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  '${(progress * 100).toInt()}%',
                  style: AppTextStyles.bodyExtraSmall.copyWith(
                    color: AppColors.grey600,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

/// Compact Summary Card for overview
class CompactSummaryCard extends StatelessWidget {
  final String title;
  final List<CompactSummaryItem> items;
  final VoidCallback? onTap;

  const CompactSummaryCard({
    Key? key,
    required this.title,
    required this.items,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: AppColors.grey200,
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: AppColors.grey200.withOpacity(0.3),
              blurRadius: 2,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              title,
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.grey600,
              ),
            ),
            const SizedBox(height: 12),
            ...items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    item.label,
                    style: AppTextStyles.bodyExtraSmall.copyWith(
                      color: AppColors.grey700,
                    ),
                  ),
                  Text(
                    item.value,
                    style: AppTextStyles.bodyExtraSmall.copyWith(
                      color: item.color ?? AppColors.grey900,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            )).toList(),
          ],
        ),
      ),
    );
  }
}

class CompactSummaryItem {
  final String label;
  final String value;
  final Color? color;

  CompactSummaryItem({
    required this.label,
    required this.value,
    this.color,
  });
}