import 'package:flutter/material.dart';

/// Responsive design utility class
class ResponsiveUtils {
  static const double _mobileBreakpoint = 600;
  static const double _tabletBreakpoint = 1024;
  static const double _desktopBreakpoint = 1440;

  /// Check if the screen is mobile size
  static bool isMobile(BuildContext context) {
    return MediaQuery.of(context).size.width < _mobileBreakpoint;
  }

  /// Check if the screen is tablet size
  static bool isTablet(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return width >= _mobileBreakpoint && width < _tabletBreakpoint;
  }

  /// Check if the screen is desktop size
  static bool isDesktop(BuildContext context) {
    return MediaQuery.of(context).size.width >= _tabletBreakpoint;
  }

  /// Check if the screen is large desktop
  static bool isLargeDesktop(BuildContext context) {
    return MediaQuery.of(context).size.width >= _desktopBreakpoint;
  }

  /// Get responsive padding based on screen size
  static EdgeInsets getResponsivePadding(BuildContext context) {
    if (isMobile(context)) {
      return const EdgeInsets.all(16);
    } else if (isTablet(context)) {
      return const EdgeInsets.all(24);
    } else {
      return const EdgeInsets.all(32);
    }
  }

  /// Get responsive margin based on screen size
  static EdgeInsets getResponsiveMargin(BuildContext context) {
    if (isMobile(context)) {
      return const EdgeInsets.all(8);
    } else if (isTablet(context)) {
      return const EdgeInsets.all(16);
    } else {
      return const EdgeInsets.all(24);
    }
  }

  /// Get responsive font size multiplier
  static double getFontSizeMultiplier(BuildContext context) {
    if (isMobile(context)) {
      return 1.0;
    } else if (isTablet(context)) {
      return 1.1;
    } else {
      return 1.2;
    }
  }

  /// Get responsive icon size
  static double getResponsiveIconSize(BuildContext context, {double baseSize = 24}) {
    final multiplier = getFontSizeMultiplier(context);
    return baseSize * multiplier;
  }

  /// Get responsive border radius
  static BorderRadius getResponsiveBorderRadius(BuildContext context, {double baseRadius = 16}) {
    if (isMobile(context)) {
      return BorderRadius.circular(baseRadius);
    } else if (isTablet(context)) {
      return BorderRadius.circular(baseRadius * 1.2);
    } else {
      return BorderRadius.circular(baseRadius * 1.5);
    }
  }

  /// Get responsive card elevation
  static double getResponsiveElevation(BuildContext context, {double baseElevation = 4}) {
    if (isMobile(context)) {
      return baseElevation;
    } else if (isTablet(context)) {
      return baseElevation * 1.2;
    } else {
      return baseElevation * 1.5;
    }
  }

  /// Get responsive grid column count
  static int getResponsiveGridColumns(BuildContext context, {int mobileColumns = 2, int tabletColumns = 3, int desktopColumns = 4}) {
    if (isMobile(context)) {
      return mobileColumns;
    } else if (isTablet(context)) {
      return tabletColumns;
    } else {
      return desktopColumns;
    }
  }

  /// Get responsive list item height
  static double getResponsiveListItemHeight(BuildContext context, {double baseHeight = 80}) {
    if (isMobile(context)) {
      return baseHeight;
    } else if (isTablet(context)) {
      return baseHeight * 1.2;
    } else {
      return baseHeight * 1.4;
    }
  }

  /// Get responsive button height
  static double getResponsiveButtonHeight(BuildContext context, {double baseHeight = 48}) {
    if (isMobile(context)) {
      return baseHeight;
    } else if (isTablet(context)) {
      return baseHeight * 1.1;
    } else {
      return baseHeight * 1.2;
    }
  }

  /// Get responsive horizontal spacing
  static double getResponsiveHorizontalSpacing(BuildContext context, {double baseSpacing = 16}) {
    if (isMobile(context)) {
      return baseSpacing;
    } else if (isTablet(context)) {
      return baseSpacing * 1.5;
    } else {
      return baseSpacing * 2;
    }
  }

  /// Get responsive vertical spacing
  static double getResponsiveVerticalSpacing(BuildContext context, {double baseSpacing = 16}) {
    if (isMobile(context)) {
      return baseSpacing;
    } else if (isTablet(context)) {
      return baseSpacing * 1.2;
    } else {
      return baseSpacing * 1.5;
    }
  }

  /// Get responsive width for centered content
  static double getResponsiveContentWidth(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    if (isMobile(context)) {
      return screenWidth;
    } else if (isTablet(context)) {
      return screenWidth * 0.8;
    } else {
      return screenWidth * 0.6;
    }
  }

  /// Get responsive max width for content
  static double getResponsiveMaxWidth(BuildContext context, {double maxWidth = 1200}) {
    final screenWidth = MediaQuery.of(context).size.width;
    return screenWidth > maxWidth ? maxWidth : screenWidth;
  }

  /// Get responsive app bar height
  static double getResponsiveAppBarHeight(BuildContext context) {
    if (isMobile(context)) {
      return kToolbarHeight;
    } else if (isTablet(context)) {
      return kToolbarHeight * 1.2;
    } else {
      return kToolbarHeight * 1.4;
    }
  }

  /// Get responsive safe area padding
  static EdgeInsets getResponsiveSafeAreaPadding(BuildContext context) {
    final safePadding = MediaQuery.of(context).padding;
    final responsivePadding = getResponsivePadding(context);
    
    return EdgeInsets.only(
      left: responsivePadding.left,
      right: responsivePadding.right,
      top: safePadding.top + responsivePadding.top,
      bottom: safePadding.bottom + responsivePadding.bottom,
    );
  }

  /// Get responsive card width for grids
  static double getResponsiveCardWidth(BuildContext context, {int columns = 2}) {
    final screenWidth = MediaQuery.of(context).size.width;
    final padding = getResponsivePadding(context);
    final spacing = getResponsiveHorizontalSpacing(context);
    
    return (screenWidth - padding.horizontal - (spacing * (columns - 1))) / columns;
  }

  /// Get responsive text scale factor
  static double getResponsiveTextScaleFactor(BuildContext context) {
    final textScaleFactor = MediaQuery.of(context).textScaleFactor;
    
    // Limit text scale factor to prevent UI breaking
    if (textScaleFactor > 1.5) {
      return 1.5;
    } else if (textScaleFactor < 0.8) {
      return 0.8;
    }
    
    return textScaleFactor;
  }

  /// Get responsive bottom sheet height
  static double getResponsiveBottomSheetHeight(BuildContext context, {double ratio = 0.9}) {
    final screenHeight = MediaQuery.of(context).size.height;
    return screenHeight * ratio;
  }

  /// Get responsive dialog width
  static double getResponsiveDialogWidth(BuildContext context, {double maxWidth = 400}) {
    final screenWidth = MediaQuery.of(context).size.width;
    
    if (isMobile(context)) {
      return screenWidth * 0.9;
    } else if (isTablet(context)) {
      return screenWidth * 0.7;
    } else {
      return maxWidth;
    }
  }

  /// Get responsive floating action button size
  static double getResponsiveFABSize(BuildContext context) {
    if (isMobile(context)) {
      return 56;
    } else if (isTablet(context)) {
      return 64;
    } else {
      return 72;
    }
  }

  /// Get responsive tab bar height
  static double getResponsiveTabBarHeight(BuildContext context) {
    if (isMobile(context)) {
      return kToolbarHeight;
    } else if (isTablet(context)) {
      return kToolbarHeight * 1.1;
    } else {
      return kToolbarHeight * 1.2;
    }
  }

  /// Get responsive navigation rail width
  static double getResponsiveNavigationRailWidth(BuildContext context) {
    if (isTablet(context)) {
      return 72;
    } else {
      return 80;
    }
  }

  /// Check if should use navigation rail instead of bottom navigation
  static bool shouldUseNavigationRail(BuildContext context) {
    return isTablet(context) || isDesktop(context);
  }

  /// Get responsive aspect ratio for cards
  static double getResponsiveAspectRatio(BuildContext context, {double defaultRatio = 1.6}) {
    if (isMobile(context)) {
      return defaultRatio;
    } else if (isTablet(context)) {
      return defaultRatio * 1.1;
    } else {
      return defaultRatio * 1.2;
    }
  }

  /// Get responsive slider height
  static double getResponsiveSliderHeight(BuildContext context) {
    if (isMobile(context)) {
      return 40;
    } else if (isTablet(context)) {
      return 48;
    } else {
      return 56;
    }
  }

  /// Get responsive switch size
  static double getResponsiveSwitchSize(BuildContext context) {
    if (isMobile(context)) {
      return 1.0;
    } else if (isTablet(context)) {
      return 1.2;
    } else {
      return 1.4;
    }
  }
}

/// Responsive layout builder widget
class ResponsiveLayoutBuilder extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveLayoutBuilder({
    Key? key,
    required this.mobile,
    this.tablet,
    this.desktop,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < 600) {
          return mobile;
        } else if (constraints.maxWidth < 1024) {
          return tablet ?? mobile;
        } else {
          return desktop ?? tablet ?? mobile;
        }
      },
    );
  }
}

/// Responsive builder widget
class ResponsiveBuilder extends StatelessWidget {
  final Widget Function(BuildContext context, bool isMobile, bool isTablet, bool isDesktop) builder;

  const ResponsiveBuilder({
    Key? key,
    required this.builder,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isMobile = constraints.maxWidth < 600;
        final isTablet = constraints.maxWidth >= 600 && constraints.maxWidth < 1024;
        final isDesktop = constraints.maxWidth >= 1024;

        return builder(context, isMobile, isTablet, isDesktop);
      },
    );
  }
}