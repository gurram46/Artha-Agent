import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final Color? backgroundColor;
  final double? elevation;
  final BorderRadius? borderRadius;
  final List<Color>? gradientColors;
  final VoidCallback? onTap;
  final bool enableGlassMorphism;
  final bool showBorder;
  final Color? borderColor;
  final double? borderWidth;

  const AppCard({
    Key? key,
    required this.child,
    this.padding,
    this.backgroundColor,
    this.elevation,
    this.borderRadius,
    this.gradientColors,
    this.onTap,
    this.enableGlassMorphism = false,
    this.showBorder = true,
    this.borderColor,
    this.borderWidth,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final borderRadiusValue = borderRadius ?? BorderRadius.circular(24);
    final elevationValue = elevation ?? 2;
    
    Widget card = Container(
      decoration: BoxDecoration(
        color: enableGlassMorphism 
            ? AppColors.surfaceGlass.withOpacity(0.8)
            : gradientColors == null 
                ? (backgroundColor ?? AppColors.cardBackground) 
                : null,
        gradient: gradientColors != null
            ? LinearGradient(
                colors: gradientColors!,
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              )
            : enableGlassMorphism
                ? AppColors.glassGradient
                : null,
        borderRadius: borderRadiusValue,
        border: showBorder 
            ? Border.all(
                color: borderColor ?? 
                    (enableGlassMorphism ? AppColors.glassBorder : AppColors.cardBorder), 
                width: borderWidth ?? (enableGlassMorphism ? 0.5 : 1)
              )
            : null,
        boxShadow: [
          BoxShadow(
            color: enableGlassMorphism ? AppColors.shadowGlass : AppColors.shadowElevated,
            blurRadius: elevationValue * 2,
            offset: Offset(0, elevationValue),
            spreadRadius: enableGlassMorphism ? 0 : 0.5,
          ),
          if (enableGlassMorphism)
            BoxShadow(
              color: AppColors.glassWhite.withOpacity(0.1),
              blurRadius: 1,
              offset: const Offset(0, 1),
              spreadRadius: 0,
            ),
        ],
      ),
      child: Padding(
        padding: padding ?? const EdgeInsets.all(20),
        child: child,
      ),
    );

    if (onTap != null) {
      card = InkWell(
        onTap: onTap,
        borderRadius: borderRadiusValue,
        overlayColor: MaterialStateProperty.all(AppColors.hoverOverlay),
        child: card,
      );
    }

    return card;
  }
}

class AgentCard extends StatelessWidget {
  final String agentName;
  final String description;
  final Color agentColor;
  final IconData icon;
  final VoidCallback? onTap;
  final bool isActive;

  const AgentCard({
    Key? key,
    required this.agentName,
    required this.description,
    required this.agentColor,
    required this.icon,
    this.onTap,
    this.isActive = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AppCard(
      onTap: onTap,
      gradientColors: [
        agentColor.withOpacity(0.08),
        agentColor.withOpacity(0.02),
      ],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: agentColor,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: agentColor.withOpacity(0.3),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Icon(
                  icon,
                  color: AppColors.white,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      agentName,
                      style: AppTextStyles.heading4.copyWith(
                        color: AppColors.grey900,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      description,
                      style: AppTextStyles.bodyMedium.copyWith(
                        color: AppColors.grey600,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
              if (isActive)
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: agentColor.withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(agentColor),
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

class FinancialCard extends StatelessWidget {
  final String title;
  final String amount;
  final String? subtitle;
  final Color? valueColor;
  final Widget? trailing;
  final VoidCallback? onTap;

  const FinancialCard({
    Key? key,
    required this.title,
    required this.amount,
    this.subtitle,
    this.valueColor,
    this.trailing,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AppCard(
      onTap: onTap,
      backgroundColor: AppColors.white,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: AppTextStyles.labelMedium.copyWith(
                  color: AppColors.grey600,
                  fontWeight: FontWeight.w600,
                ),
              ),
              if (trailing != null) trailing!,
            ],
          ),
          const SizedBox(height: 12),
          Text(
            amount,
            style: AppTextStyles.currencyLarge.copyWith(
              color: valueColor ?? AppColors.grey900,
            ),
          ),
          if (subtitle != null) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: (valueColor ?? AppColors.grey500).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                subtitle!,
                style: AppTextStyles.bodySmall.copyWith(
                  color: valueColor ?? AppColors.grey600,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}