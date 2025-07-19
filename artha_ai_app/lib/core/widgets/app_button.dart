import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

enum ButtonType { primary, secondary, outline, text }
enum ButtonSize { small, medium, large }

class AppButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final ButtonType type;
  final ButtonSize size;
  final bool isLoading;
  final Widget? icon;
  final bool fullWidth;

  const AppButton({
    Key? key,
    required this.text,
    this.onPressed,
    this.type = ButtonType.primary,
    this.size = ButtonSize.medium,
    this.isLoading = false,
    this.icon,
    this.fullWidth = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final buttonStyle = _getButtonStyle();
    final textStyle = _getTextStyle();
    final padding = _getPadding();

    Widget child = isLoading
        ? const SizedBox(
            height: 20,
            width: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.white),
            ),
          )
        : Row(
            mainAxisSize: fullWidth ? MainAxisSize.max : MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (icon != null) ...[
                icon!,
                const SizedBox(width: 8),
              ],
              Text(text, style: textStyle),
            ],
          );

    Widget button;
    
    switch (type) {
      case ButtonType.primary:
        button = ElevatedButton(
          onPressed: isLoading ? null : onPressed,
          style: buttonStyle,
          child: child,
        );
        break;
      case ButtonType.secondary:
        button = ElevatedButton(
          onPressed: isLoading ? null : onPressed,
          style: buttonStyle,
          child: child,
        );
        break;
      case ButtonType.outline:
        button = OutlinedButton(
          onPressed: isLoading ? null : onPressed,
          style: buttonStyle,
          child: child,
        );
        break;
      case ButtonType.text:
        button = TextButton(
          onPressed: isLoading ? null : onPressed,
          style: buttonStyle,
          child: child,
        );
        break;
    }

    return fullWidth
        ? SizedBox(width: double.infinity, child: button)
        : button;
  }

  ButtonStyle _getButtonStyle() {
    final padding = _getPadding();
    final borderRadius = BorderRadius.circular(12);

    switch (type) {
      case ButtonType.primary:
        return ElevatedButton.styleFrom(
          backgroundColor: AppColors.primaryBlue,
          foregroundColor: AppColors.white,
          elevation: 2,
          padding: padding,
          shape: RoundedRectangleBorder(borderRadius: borderRadius),
        );
      case ButtonType.secondary:
        return ElevatedButton.styleFrom(
          backgroundColor: AppColors.grey200,
          foregroundColor: AppColors.grey800,
          elevation: 1,
          padding: padding,
          shape: RoundedRectangleBorder(borderRadius: borderRadius),
        );
      case ButtonType.outline:
        return OutlinedButton.styleFrom(
          foregroundColor: AppColors.primaryBlue,
          side: const BorderSide(color: AppColors.primaryBlue),
          padding: padding,
          shape: RoundedRectangleBorder(borderRadius: borderRadius),
        );
      case ButtonType.text:
        return TextButton.styleFrom(
          foregroundColor: AppColors.primaryBlue,
          padding: padding,
          shape: RoundedRectangleBorder(borderRadius: borderRadius),
        );
    }
  }

  TextStyle _getTextStyle() {
    final baseStyle = switch (size) {
      ButtonSize.small => AppTextStyles.buttonSmall,
      ButtonSize.medium => AppTextStyles.buttonMedium,
      ButtonSize.large => AppTextStyles.buttonLarge,
    };

    return switch (type) {
      ButtonType.primary => baseStyle.copyWith(color: AppColors.white),
      ButtonType.secondary => baseStyle.copyWith(color: AppColors.grey800),
      ButtonType.outline => baseStyle.copyWith(color: AppColors.primaryBlue),
      ButtonType.text => baseStyle.copyWith(color: AppColors.primaryBlue),
    };
  }

  EdgeInsets _getPadding() {
    return switch (size) {
      ButtonSize.small => const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ButtonSize.medium => const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      ButtonSize.large => const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
    };
  }
}