import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../theme/app_colors.dart';

/// Accessibility utility class for improved app accessibility
class AccessibilityUtils {
  
  /// Get appropriate text contrast color for background
  static Color getContrastColor(Color backgroundColor) {
    final luminance = backgroundColor.computeLuminance();
    return luminance > 0.5 ? Colors.black : Colors.white;
  }

  /// Check if color combination meets WCAG contrast requirements
  static bool meetsContrastRequirements(Color foreground, Color background, {double minimumContrast = 4.5}) {
    final contrast = calculateContrastRatio(foreground, background);
    return contrast >= minimumContrast;
  }

  /// Calculate contrast ratio between two colors
  static double calculateContrastRatio(Color foreground, Color background) {
    final foregroundLuminance = foreground.computeLuminance();
    final backgroundLuminance = background.computeLuminance();
    
    final lighter = foregroundLuminance > backgroundLuminance ? foregroundLuminance : backgroundLuminance;
    final darker = foregroundLuminance < backgroundLuminance ? foregroundLuminance : backgroundLuminance;
    
    return (lighter + 0.05) / (darker + 0.05);
  }

  /// Get semantic label for financial amounts
  static String getFinancialAmountLabel(String amount, {bool isPositive = true}) {
    final cleanAmount = amount.replaceAll('₹', '').replaceAll(',', '');
    final prefix = isPositive ? 'Positive amount' : 'Negative amount';
    return '$prefix: $cleanAmount rupees';
  }

  /// Get semantic label for percentage values
  static String getPercentageLabel(double percentage, {bool isChange = false}) {
    final prefix = isChange ? 'Change of' : 'Percentage';
    final direction = isChange ? (percentage > 0 ? 'increase' : 'decrease') : '';
    return '$prefix ${percentage.abs().toStringAsFixed(1)} percent $direction'.trim();
  }

  /// Get semantic label for dates
  static String getDateLabel(DateTime date) {
    return 'Date: ${date.day}/${date.month}/${date.year}';
  }

  /// Get semantic label for time
  static String getTimeLabel(TimeOfDay time) {
    return 'Time: ${time.hour}:${time.minute.toString().padLeft(2, '0')}';
  }

  /// Get semantic label for navigation items
  static String getNavigationLabel(String item, {bool isSelected = false}) {
    final status = isSelected ? 'Selected' : 'Not selected';
    return '$item, $status';
  }

  /// Get semantic label for buttons with state
  static String getButtonLabel(String text, {bool isEnabled = true, bool isLoading = false}) {
    if (isLoading) {
      return '$text, Loading';
    }
    return isEnabled ? text : '$text, Disabled';
  }

  /// Get semantic label for progress indicators
  static String getProgressLabel(double progress, {String? context}) {
    final percentage = (progress * 100).toInt();
    final base = 'Progress: $percentage percent';
    return context != null ? '$base for $context' : base;
  }

  /// Get semantic label for charts and graphs
  static String getChartLabel(String type, String data) {
    return '$type chart showing $data';
  }

  /// Get semantic label for status indicators
  static String getStatusLabel(String status, {bool isPositive = true}) {
    final sentiment = isPositive ? 'positive' : 'negative';
    return 'Status: $status, $sentiment';
  }

  /// Get semantic label for financial goals
  static String getGoalLabel(String goalName, double progress, String target) {
    final percentage = (progress * 100).toInt();
    return 'Goal: $goalName, $percentage percent complete, target: $target';
  }

  /// Get semantic label for investment performance
  static String getInvestmentLabel(String name, double returns, String period) {
    final returnsText = returns > 0 ? 'positive' : 'negative';
    return 'Investment: $name, $returnsText returns of ${returns.abs().toStringAsFixed(1)} percent over $period';
  }

  /// Get semantic label for transaction items
  static String getTransactionLabel(String type, String amount, String date, {String? description}) {
    final base = 'Transaction: $type, amount $amount, date $date';
    return description != null ? '$base, description: $description' : base;
  }

  /// Get semantic label for cards with data
  static String getCardLabel(String title, String value, {String? subtitle}) {
    final base = 'Card: $title, value: $value';
    return subtitle != null ? '$base, additional info: $subtitle' : base;
  }

  /// Get semantic label for tab items
  static String getTabLabel(String tabName, int index, int total, {bool isSelected = false}) {
    final position = 'Tab ${index + 1} of $total';
    final status = isSelected ? 'selected' : 'not selected';
    return '$tabName, $position, $status';
  }

  /// Get semantic label for form fields
  static String getFormFieldLabel(String fieldName, {bool isRequired = false, bool hasError = false}) {
    String label = fieldName;
    if (isRequired) label += ', required';
    if (hasError) label += ', has error';
    return label;
  }

  /// Get semantic label for switches and checkboxes
  static String getSwitchLabel(String name, bool isEnabled) {
    final status = isEnabled ? 'enabled' : 'disabled';
    return '$name, $status';
  }

  /// Get semantic label for sliders
  static String getSliderLabel(String name, double value, double min, double max) {
    return '$name, value $value, minimum $min, maximum $max';
  }

  /// Get semantic label for dropdown menus
  static String getDropdownLabel(String name, String? selectedValue, List<String> options) {
    final selected = selectedValue ?? 'none selected';
    return '$name, selected: $selected, ${options.length} options available';
  }

  /// Get semantic label for expandable items
  static String getExpandableLabel(String title, bool isExpanded) {
    final status = isExpanded ? 'expanded' : 'collapsed';
    return '$title, $status';
  }

  /// Get semantic label for rating widgets
  static String getRatingLabel(String name, double rating, double maxRating) {
    return '$name, rating: $rating out of $maxRating';
  }

  /// Get semantic label for badges and indicators
  static String getBadgeLabel(String text, {String? count}) {
    return count != null ? '$text, $count items' : text;
  }

  /// Provide haptic feedback for user actions
  static void provideFeedback(HapticFeedbackType type) {
    switch (type) {
      case HapticFeedbackType.light:
        HapticFeedback.lightImpact();
        break;
      case HapticFeedbackType.medium:
        HapticFeedback.mediumImpact();
        break;
      case HapticFeedbackType.heavy:
        HapticFeedback.heavyImpact();
        break;
      case HapticFeedbackType.selection:
        HapticFeedback.selectionClick();
        break;
      case HapticFeedbackType.vibrate:
        HapticFeedback.vibrate();
        break;
    }
  }

  /// Get minimum touch target size
  static double getMinimumTouchTargetSize() {
    return 48.0; // Material Design minimum
  }

  /// Get accessible focus color
  static Color getFocusColor(BuildContext context) {
    return Theme.of(context).focusColor;
  }

  /// Get accessible text style with proper contrast
  static TextStyle getAccessibleTextStyle(BuildContext context, TextStyle baseStyle, Color backgroundColor) {
    final textColor = getContrastColor(backgroundColor);
    return baseStyle.copyWith(color: textColor);
  }

  /// Check if device has accessibility features enabled
  static bool hasAccessibilityFeatures(BuildContext context) {
    final data = MediaQuery.of(context);
    return data.accessibleNavigation || data.boldText || data.highContrast;
  }

  /// Get accessible color scheme
  static ColorScheme getAccessibleColorScheme(BuildContext context) {
    final brightness = Theme.of(context).brightness;
    final data = MediaQuery.of(context);
    
    if (data.highContrast) {
      return brightness == Brightness.dark
          ? const ColorScheme.highContrastDark()
          : const ColorScheme.highContrastLight();
    }
    
    return Theme.of(context).colorScheme;
  }

  /// Get accessible text scale factor
  static double getAccessibleTextScaleFactor(BuildContext context) {
    final textScaleFactor = MediaQuery.of(context).textScaleFactor;
    
    // Ensure text doesn't become too small or too large
    return textScaleFactor.clamp(0.8, 2.0);
  }

  /// Get accessible animation duration
  static Duration getAccessibleAnimationDuration(BuildContext context, Duration defaultDuration) {
    final data = MediaQuery.of(context);
    
    if (data.disableAnimations) {
      return Duration.zero;
    }
    
    // Reduce animation duration for accessibility
    if (data.accessibleNavigation) {
      return Duration(milliseconds: (defaultDuration.inMilliseconds * 0.5).round());
    }
    
    return defaultDuration;
  }

  /// Get accessible border radius
  static BorderRadius getAccessibleBorderRadius(BuildContext context, BorderRadius defaultRadius) {
    final data = MediaQuery.of(context);
    
    // Reduce border radius for better touch accessibility
    if (data.accessibleNavigation) {
      return BorderRadius.circular(defaultRadius.topLeft.x * 0.7);
    }
    
    return defaultRadius;
  }

  /// Get accessible padding
  static EdgeInsets getAccessiblePadding(BuildContext context, EdgeInsets defaultPadding) {
    final data = MediaQuery.of(context);
    
    // Increase padding for better touch accessibility
    if (data.accessibleNavigation) {
      return EdgeInsets.all(defaultPadding.top * 1.2);
    }
    
    return defaultPadding;
  }

  /// Get accessible elevation
  static double getAccessibleElevation(BuildContext context, double defaultElevation) {
    final data = MediaQuery.of(context);
    
    // Reduce elevation for high contrast mode
    if (data.highContrast) {
      return defaultElevation * 0.5;
    }
    
    return defaultElevation;
  }

  /// Show accessible snackbar
  static void showAccessibleSnackBar(BuildContext context, String message, {String? action, VoidCallback? onAction}) {
    final messenger = ScaffoldMessenger.of(context);
    
    messenger.showSnackBar(
      SnackBar(
        content: Text(message),
        action: action != null
            ? SnackBarAction(
                label: action,
                onPressed: onAction ?? () {},
              )
            : null,
        duration: const Duration(seconds: 4), // Longer duration for accessibility
      ),
    );
  }

  /// Announce message for screen readers
  static void announceMessage(BuildContext context, String message) {
    final messenger = ScaffoldMessenger.of(context);
    
    messenger.showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(milliseconds: 1), // Very short duration
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
    );
  }
}

/// Enum for haptic feedback types
enum HapticFeedbackType {
  light,
  medium,
  heavy,
  selection,
  vibrate,
}

/// Accessible widget wrapper
class AccessibleWidget extends StatelessWidget {
  final Widget child;
  final String? semanticLabel;
  final String? tooltip;
  final VoidCallback? onTap;
  final bool excludeFromSemantics;
  final bool isButton;
  final bool isSelected;
  final bool isEnabled;

  const AccessibleWidget({
    Key? key,
    required this.child,
    this.semanticLabel,
    this.tooltip,
    this.onTap,
    this.excludeFromSemantics = false,
    this.isButton = false,
    this.isSelected = false,
    this.isEnabled = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    Widget widget = child;

    if (tooltip != null) {
      widget = Tooltip(
        message: tooltip!,
        child: widget,
      );
    }

    if (semanticLabel != null) {
      widget = Semantics(
        label: semanticLabel,
        button: isButton,
        selected: isSelected,
        enabled: isEnabled,
        excludeSemantics: excludeFromSemantics,
        child: widget,
      );
    }

    if (onTap != null) {
      widget = GestureDetector(
        onTap: isEnabled ? onTap : null,
        child: widget,
      );
    }

    return widget;
  }
}

/// Accessible text widget with proper contrast
class AccessibleText extends StatelessWidget {
  final String text;
  final TextStyle? style;
  final Color? backgroundColor;
  final TextAlign? textAlign;
  final int? maxLines;
  final TextOverflow? overflow;
  final String? semanticLabel;

  const AccessibleText(
    this.text, {
    Key? key,
    this.style,
    this.backgroundColor,
    this.textAlign,
    this.maxLines,
    this.overflow,
    this.semanticLabel,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    TextStyle? finalStyle = style;
    
    if (backgroundColor != null && style != null) {
      final contrastColor = AccessibilityUtils.getContrastColor(backgroundColor!);
      finalStyle = style!.copyWith(color: contrastColor);
    }

    return Semantics(
      label: semanticLabel ?? text,
      child: Text(
        text,
        style: finalStyle,
        textAlign: textAlign,
        maxLines: maxLines,
        overflow: overflow,
      ),
    );
  }
}