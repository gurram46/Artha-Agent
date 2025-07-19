import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../navigation/app_router.dart';

class NavigationService {
  static final NavigationService _instance = NavigationService._internal();
  factory NavigationService() => _instance;
  NavigationService._internal();

  static final List<String> _navigationStack = [AppRouter.dashboard];
  static const List<String> _mainRoutes = [
    AppRouter.dashboard,
    AppRouter.chat,
    AppRouter.profile,
  ];

  /// Check if current route is a main route (bottom navigation)
  static bool isMainRoute(String route) {
    return _mainRoutes.contains(route);
  }

  /// Get the appropriate back destination
  static String getBackDestination(String currentRoute) {
    if (_navigationStack.length > 1) {
      return _navigationStack[_navigationStack.length - 2];
    }
    return AppRouter.dashboard;
  }

  /// Navigate to a new route and manage stack
  static void navigateTo(BuildContext context, String route) {
    if (!isMainRoute(route)) {
      _navigationStack.add(route);
    } else {
      // If navigating to main route, clear stack and set new route
      _navigationStack.clear();
      _navigationStack.add(route);
    }
    context.go(route);
  }

  /// Navigate back with proper stack management
  static void navigateBack(BuildContext context) {
    if (_navigationStack.length > 1) {
      _navigationStack.removeLast();
      final backRoute = _navigationStack.last;
      context.go(backRoute);
    } else {
      context.go(AppRouter.dashboard);
    }
  }

  /// Handle system back button/gesture
  static Future<bool> handleSystemBack(BuildContext context) async {
    final currentRoute = GoRouterState.of(context).uri.path;
    
    // If we're on a main route, minimize app instead of closing
    if (isMainRoute(currentRoute)) {
      // Return false to indicate we don't want to close the app
      return false;
    }
    
    // Navigate back to previous screen
    navigateBack(context);
    return false; // Don't close the app
  }

  /// Clear navigation stack
  static void clearStack() {
    _navigationStack.clear();
    _navigationStack.add(AppRouter.dashboard);
  }

  /// Get current navigation stack
  static List<String> getStack() {
    return List.from(_navigationStack);
  }

  /// Check if we can go back
  static bool canGoBack() {
    return _navigationStack.length > 1;
  }
}

/// Custom back button widget
class CustomBackButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final Color? color;
  final double? size;

  const CustomBackButton({
    Key? key,
    this.onPressed,
    this.color,
    this.size,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: Icon(
        Icons.arrow_back_ios,
        color: color,
        size: size ?? 20,
      ),
      onPressed: onPressed ?? () => NavigationService.navigateBack(context),
      tooltip: 'Back',
    );
  }
}

/// Enhanced app bar with proper back button
class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String? title;
  final List<Widget>? actions;
  final bool showBackButton;
  final VoidCallback? onBackPressed;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final double? elevation;
  final Widget? leading;

  const CustomAppBar({
    Key? key,
    this.title,
    this.actions,
    this.showBackButton = true,
    this.onBackPressed,
    this.backgroundColor,
    this.foregroundColor,
    this.elevation,
    this.leading,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final currentRoute = GoRouterState.of(context).uri.path;
    final canGoBack = NavigationService.canGoBack() && !NavigationService.isMainRoute(currentRoute);

    return AppBar(
      title: title != null ? Text(title!) : null,
      actions: actions,
      backgroundColor: backgroundColor,
      foregroundColor: foregroundColor,
      elevation: elevation ?? 0,
      leading: leading ?? (canGoBack && showBackButton
          ? CustomBackButton(
              onPressed: onBackPressed ?? () => NavigationService.navigateBack(context),
              color: foregroundColor,
            )
          : null),
      automaticallyImplyLeading: false,
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}

/// Wrapper widget to handle back gestures
class BackGestureWrapper extends StatelessWidget {
  final Widget child;

  const BackGestureWrapper({Key? key, required this.child}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvoked: (bool didPop) async {
        if (didPop) return;
        await NavigationService.handleSystemBack(context);
      },
      child: child,
    );
  }
}