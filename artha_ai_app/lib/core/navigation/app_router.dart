import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/register_screen.dart';
import '../../features/dashboard/screens/dashboard_screen.dart';
import '../../features/chat/screens/chat_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import '../../features/settings/screens/settings_screen.dart';
import '../../features/fi_money/screens/fi_connection_screen.dart';
import '../../features/portfolio/screens/portfolio_screen.dart';
import '../../features/portfolio/screens/portfolio_analysis_screen.dart';
import '../../features/spending/screens/spending_optimization_screen.dart';
import '../../features/goals/screens/goals_planning_screen.dart';
import '../../features/transactions/screens/transactions_screen.dart';
import '../../features/onboarding/screens/onboarding_screen.dart';
import '../widgets/main_layout.dart';

class AppRouter {
  static const String login = '/login';
  static const String register = '/register';
  static const String onboarding = '/onboarding';
  static const String dashboard = '/dashboard';
  static const String chat = '/chat';
  static const String profile = '/profile';
  static const String settings = '/settings';
  static const String fiConnection = '/fi-connection';
  static const String portfolio = '/portfolio';
  static const String portfolioAnalysis = '/portfolio-analysis';
  static const String spendingOptimization = '/spending-optimization';
  static const String goalsPlanning = '/goals-planning';
  static const String transactions = '/transactions';

  static final GoRouter router = GoRouter(
    initialLocation: onboarding,
    routes: [
      // Authentication Routes
      GoRoute(
        path: login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: register,
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: onboarding,
        builder: (context, state) => const OnboardingScreen(),
      ),
      
      // Main App Routes with Bottom Navigation
      ShellRoute(
        builder: (context, state, child) => MainLayout(child: child),
        routes: [
          GoRoute(
            path: dashboard,
            builder: (context, state) => const DashboardScreen(),
          ),
          GoRoute(
            path: chat,
            builder: (context, state) => const ChatScreen(),
          ),
          GoRoute(
            path: profile,
            builder: (context, state) => const ProfileScreen(),
          ),
          GoRoute(
            path: portfolioAnalysis,
            builder: (context, state) => const PortfolioAnalysisScreen(),
          ),
          GoRoute(
            path: spendingOptimization,
            builder: (context, state) => const SpendingOptimizationScreen(),
          ),
          GoRoute(
            path: goalsPlanning,
            builder: (context, state) => const GoalsPlanningScreen(),
          ),
        ],
      ),
      
      // Secondary Routes
      GoRoute(
        path: settings,
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: fiConnection,
        builder: (context, state) => const FiConnectionScreen(),
      ),
      GoRoute(
        path: portfolio,
        builder: (context, state) => const PortfolioScreen(),
      ),
      GoRoute(
        path: transactions,
        builder: (context, state) => const TransactionsScreen(),
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              'Page not found',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              'The page you\'re looking for doesn\'t exist.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.go(dashboard),
              child: const Text('Go to Dashboard'),
            ),
          ],
        ),
      ),
    ),
  );
}

extension GoRouterExtensions on GoRouter {
  void clearAndNavigate(String location) {
    while (canPop()) {
      pop();
    }
    go(location);
  }
}