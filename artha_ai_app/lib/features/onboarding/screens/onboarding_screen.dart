import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/modern_components.dart';
import '../../../core/widgets/animated_widgets.dart';
import '../../../core/widgets/app_button.dart';
import '../../../core/navigation/app_router.dart';
import '../../../core/services/navigation_service.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({Key? key}) : super(key: key);

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen>
    with TickerProviderStateMixin {
  final PageController _pageController = PageController();
  int _currentPage = 0;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  final List<OnboardingData> _onboardingData = [
    OnboardingData(
      title: 'Welcome to Artha AI',
      description: 'Your intelligent financial advisor powered by AI agents specialized in Past, Present, and Future financial planning.',
      icon: Icons.psychology,
      color: AppColors.primaryBlue,
    ),
    OnboardingData(
      title: 'Past Agent',
      description: 'Analyzes your investment history, portfolio performance, and learns from your financial decisions.',
      icon: Icons.history,
      color: AppColors.pastAgentColor,
    ),
    OnboardingData(
      title: 'Present Agent',
      description: 'Optimizes your current spending, manages expenses, and maximizes your financial health today.',
      icon: Icons.today,
      color: AppColors.presentAgentColor,
    ),
    OnboardingData(
      title: 'Future Agent',
      description: 'Plans your financial goals, retirement, and major life events with personalized strategies.',
      icon: Icons.timeline,
      color: AppColors.futureAgentColor,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              _onboardingData[_currentPage].color.withOpacity(0.1),
              AppColors.backgroundSecondary,
              AppColors.surfaceVariant,
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              _buildSkipButton(),
              Expanded(
                child: PageView.builder(
                  controller: _pageController,
                  onPageChanged: (index) {
                    setState(() {
                      _currentPage = index;
                    });
                    _animationController.reset();
                    _animationController.forward();
                  },
                  itemCount: _onboardingData.length,
                  itemBuilder: (context, index) {
                    final data = _onboardingData[index];
                    return _buildOnboardingPage(data);
                  },
                ),
              ),
              _buildBottomSection(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildOnboardingPage(OnboardingData data) {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedSlideIn(
              duration: const Duration(milliseconds: 800),
              child: Container(
                width: 180,
                height: 180,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      data.color,
                      data.color.withOpacity(0.7),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: data.color.withOpacity(0.3),
                      blurRadius: 30,
                      offset: const Offset(0, 15),
                    ),
                    BoxShadow(
                      color: data.color.withOpacity(0.1),
                      blurRadius: 60,
                      offset: const Offset(0, 30),
                    ),
                  ],
                ),
                child: Icon(
                  data.icon,
                  size: 80,
                  color: AppColors.white,
                ),
              ),
            ),
            const SizedBox(height: 48),
            AnimatedSlideIn(
              duration: const Duration(milliseconds: 800),
              delay: const Duration(milliseconds: 200),
              child: Text(
                data.title,
                style: AppTextStyles.displayMedium.copyWith(
                  color: AppColors.grey900,
                  fontWeight: FontWeight.w800,
                ),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(height: 24),
            AnimatedSlideIn(
              duration: const Duration(milliseconds: 800),
              delay: const Duration(milliseconds: 400),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  data.description,
                  style: AppTextStyles.bodyLarge.copyWith(
                    color: AppColors.grey700,
                    height: 1.6,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomSection() {
    return AnimatedSlideIn(
      duration: const Duration(milliseconds: 800),
      delay: const Duration(milliseconds: 600),
      child: Container(
        padding: const EdgeInsets.all(32),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(
                _onboardingData.length,
                (index) => AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  width: _currentPage == index ? 32 : 8,
                  height: 8,
                  margin: const EdgeInsets.symmetric(horizontal: 4),
                  decoration: BoxDecoration(
                    color: _currentPage == index
                        ? _onboardingData[_currentPage].color
                        : AppColors.grey300,
                    borderRadius: BorderRadius.circular(4),
                    boxShadow: _currentPage == index
                        ? [
                            BoxShadow(
                              color: _onboardingData[_currentPage].color.withOpacity(0.3),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ]
                        : null,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 32),
            Row(
              children: [
                if (_currentPage > 0)
                  Expanded(
                    child: ModernButton(
                      text: 'Previous',
                      onPressed: () {
                        _pageController.previousPage(
                          duration: const Duration(milliseconds: 300),
                          curve: Curves.easeInOut,
                        );
                      },
                      isOutlined: true,
                      icon: Icons.arrow_back,
                    ),
                  ),
                if (_currentPage > 0) const SizedBox(width: 16),
                Expanded(
                  child: ModernButton(
                    text: _currentPage == _onboardingData.length - 1
                        ? 'Get Started'
                        : 'Next',
                    onPressed: () {
                      if (_currentPage == _onboardingData.length - 1) {
                        NavigationService.navigateTo(context, AppRouter.dashboard);
                      } else {
                        _pageController.nextPage(
                          duration: const Duration(milliseconds: 300),
                          curve: Curves.easeInOut,
                        );
                      }
                    },
                    backgroundColor: _onboardingData[_currentPage].color,
                    icon: _currentPage == _onboardingData.length - 1
                        ? Icons.rocket_launch
                        : Icons.arrow_forward,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSkipButton() {
    if (_currentPage == _onboardingData.length - 1) return const SizedBox.shrink();
    
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          AnimatedScaleWidget(
            child: TextButton(
              onPressed: () {
                NavigationService.navigateTo(context, AppRouter.dashboard);
              },
              child: Text(
                'Skip',
                style: AppTextStyles.buttonMedium.copyWith(
                  color: AppColors.grey600,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class OnboardingData {
  final String title;
  final String description;
  final IconData icon;
  final Color color;

  OnboardingData({
    required this.title,
    required this.description,
    required this.icon,
    required this.color,
  });
}