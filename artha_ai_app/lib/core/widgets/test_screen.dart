import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';
import '../widgets/modern_components.dart';
import '../widgets/animated_widgets.dart';
import '../utils/responsive_utils.dart';
import '../utils/accessibility_utils.dart';

/// Test screen to showcase all new modern components and features
class TestScreen extends StatefulWidget {
  const TestScreen({Key? key}) : super(key: key);

  @override
  State<TestScreen> createState() => _TestScreenState();
}

class _TestScreenState extends State<TestScreen> {
  bool _switchValue = false;
  double _sliderValue = 50.0;
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Modern Components Test'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: ResponsiveUtils.getResponsivePadding(context),
        child: StaggeredListAnimation(
          children: [
            _buildSection('Glass Components', _buildGlassComponents()),
            _buildSection('Modern Buttons', _buildModernButtons()),
            _buildSection('Data Visualization', _buildDataVisualization()),
            _buildSection('Progress Cards', _buildProgressCards()),
            _buildSection('Animated Widgets', _buildAnimatedWidgets()),
            _buildSection('Form Components', _buildFormComponents()),
            _buildSection('Responsive Design', _buildResponsiveDemo()),
            _buildSection('Accessibility Features', _buildAccessibilityDemo()),
          ],
        ),
      ),
      floatingActionButton: PulsingFAB(
        onPressed: _showTestBottomSheet,
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildSection(String title, Widget content) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 16),
          child: Text(
            title,
            style: AppTextStyles.heading3,
          ),
        ),
        content,
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildGlassComponents() {
    return Column(
      children: [
        GlassCard(
          child: Column(
            children: [
              Text(
                'Glass Card Example',
                style: AppTextStyles.heading4,
              ),
              const SizedBox(height: 12),
              Text(
                'This is a glassmorphism card with blur effect and subtle shadows.',
                style: AppTextStyles.bodyMedium,
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        GlassCard(
          onTap: () {
            AccessibilityUtils.provideFeedback(HapticFeedbackType.light);
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Glass card tapped!')),
            );
          },
          child: Row(
            children: [
              Icon(Icons.touch_app, color: AppColors.primaryBlue),
              const SizedBox(width: 16),
              Expanded(
                child: Text(
                  'Tappable Glass Card',
                  style: AppTextStyles.bodyMedium,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildModernButtons() {
    return Wrap(
      spacing: 16,
      runSpacing: 16,
      children: [
        ModernButton(
          text: 'Primary Button',
          onPressed: () => _showMessage('Primary button pressed'),
          icon: Icons.star,
        ),
        ModernButton(
          text: 'Secondary Button',
          onPressed: () => _showMessage('Secondary button pressed'),
          isSecondary: true,
          icon: Icons.favorite,
        ),
        ModernButton(
          text: 'Outlined Button',
          onPressed: () => _showMessage('Outlined button pressed'),
          isOutlined: true,
          icon: Icons.settings,
        ),
        ModernButton(
          text: 'Loading Button',
          onPressed: null,
          isLoading: true,
        ),
        ModernButton(
          text: 'Custom Color',
          onPressed: () => _showMessage('Custom color button pressed'),
          backgroundColor: AppColors.accentTeal,
          icon: Icons.palette,
        ),
      ],
    );
  }

  Widget _buildDataVisualization() {
    return Column(
      children: [
        DataVisualizationCard(
          title: 'Portfolio Performance',
          value: '₹15,50,000',
          changeText: '+15.8% this month',
          changePercentage: 15.8,
          isPositive: true,
          icon: Icons.trending_up,
          accentColor: AppColors.success,
        ),
        const SizedBox(height: 16),
        DataVisualizationCard(
          title: 'Monthly Expenses',
          value: '₹45,000',
          changeText: '-8.2% from last month',
          changePercentage: -8.2,
          isPositive: false,
          icon: Icons.trending_down,
          accentColor: AppColors.error,
        ),
      ],
    );
  }

  Widget _buildProgressCards() {
    return Column(
      children: [
        ProgressCard(
          title: 'Emergency Fund',
          currentValue: '₹2,50,000',
          targetValue: '₹5,00,000',
          progress: 0.5,
          progressColor: AppColors.success,
          subtitle: '6 months remaining',
        ),
        const SizedBox(height: 16),
        ProgressCard(
          title: 'Dream Home',
          currentValue: '₹32,50,000',
          targetValue: '₹50,00,000',
          progress: 0.65,
          progressColor: AppColors.primaryBlue,
          subtitle: 'On track',
        ),
      ],
    );
  }

  Widget _buildAnimatedWidgets() {
    return Column(
      children: [
        AnimatedCounter(
          value: 125000,
          prefix: '₹',
          decimalPlaces: 0,
          style: AppTextStyles.currencyLarge,
        ),
        const SizedBox(height: 16),
        AnimatedProgressBar(
          value: 0.7,
          height: 8,
          backgroundColor: AppColors.grey200,
          valueColor: AppColors.primaryBlue,
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: AnimatedScaleWidget(
                onTap: () => _showMessage('Animated scale tapped'),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppColors.primaryBlue,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Center(
                    child: Text(
                      'Tap Me',
                      style: AppTextStyles.buttonMedium.copyWith(
                        color: AppColors.white,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildFormComponents() {
    return Column(
      children: [
        ModernTextField(
          label: 'Email Address',
          hintText: 'Enter your email',
          prefixIcon: Icons.email,
          keyboardType: TextInputType.emailAddress,
        ),
        const SizedBox(height: 16),
        ModernTextField(
          label: 'Password',
          hintText: 'Enter your password',
          prefixIcon: Icons.lock,
          suffixIcon: Icons.visibility,
          obscureText: true,
        ),
        const SizedBox(height: 16),
        ModernTextField(
          label: 'Message',
          hintText: 'Enter your message',
          maxLines: 3,
        ),
      ],
    );
  }

  Widget _buildResponsiveDemo() {
    return ResponsiveBuilder(
      builder: (context, isMobile, isTablet, isDesktop) {
        final deviceType = isMobile ? 'Mobile' : isTablet ? 'Tablet' : 'Desktop';
        final columns = ResponsiveUtils.getResponsiveGridColumns(context);
        
        return Column(
          children: [
            GlassCard(
              child: Column(
                children: [
                  Text(
                    'Current Device: $deviceType',
                    style: AppTextStyles.heading4,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Grid Columns: $columns',
                    style: AppTextStyles.bodyMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Screen Width: ${MediaQuery.of(context).size.width.toInt()}px',
                    style: AppTextStyles.bodyMedium,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: columns,
              mainAxisSpacing: 16,
              crossAxisSpacing: 16,
              childAspectRatio: 1.5,
              children: List.generate(
                6,
                (index) => GlassCard(
                  child: Center(
                    child: Text(
                      'Item ${index + 1}',
                      style: AppTextStyles.bodyMedium,
                    ),
                  ),
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildAccessibilityDemo() {
    return Column(
      children: [
        AccessibleWidget(
          semanticLabel: 'Accessible toggle switch for notifications',
          tooltip: 'Toggle to enable/disable notifications',
          child: GlassCard(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Notifications',
                  style: AppTextStyles.bodyMedium,
                ),
                Switch(
                  value: _switchValue,
                  onChanged: (value) {
                    setState(() {
                      _switchValue = value;
                    });
                    AccessibilityUtils.provideFeedback(HapticFeedbackType.selection);
                  },
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        AccessibleWidget(
          semanticLabel: AccessibilityUtils.getSliderLabel(
            'Volume', _sliderValue, 0, 100
          ),
          tooltip: 'Adjust volume level',
          child: GlassCard(
            child: Column(
              children: [
                Text(
                  'Volume: ${_sliderValue.toInt()}%',
                  style: AppTextStyles.bodyMedium,
                ),
                const SizedBox(height: 8),
                Slider(
                  value: _sliderValue,
                  min: 0,
                  max: 100,
                  divisions: 10,
                  onChanged: (value) {
                    setState(() {
                      _sliderValue = value;
                    });
                    AccessibilityUtils.provideFeedback(HapticFeedbackType.light);
                  },
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        AccessibleText(
          'This is an accessible text widget with proper contrast checking.',
          style: AppTextStyles.bodyMedium,
          backgroundColor: AppColors.primaryBlue,
          semanticLabel: 'Accessible text demonstration',
        ),
      ],
    );
  }

  void _showMessage(String message) {
    AccessibilityUtils.showAccessibleSnackBar(
      context,
      message,
      action: 'OK',
      onAction: () {
        ScaffoldMessenger.of(context).hideCurrentSnackBar();
      },
    );
  }

  void _showTestBottomSheet() {
    ModernBottomSheet.show(
      context: context,
      title: 'Test Bottom Sheet',
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            'This is a modern bottom sheet with enhanced styling and animations.',
            style: AppTextStyles.bodyMedium,
          ),
          const SizedBox(height: 16),
          AnimatedProgressBar(
            value: 0.6,
            height: 8,
            backgroundColor: AppColors.grey200,
            valueColor: AppColors.success,
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: ModernButton(
                  text: 'Cancel',
                  onPressed: () => Navigator.pop(context),
                  isSecondary: true,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: ModernButton(
                  text: 'Confirm',
                  onPressed: () {
                    Navigator.pop(context);
                    _showMessage('Bottom sheet confirmed!');
                  },
                  icon: Icons.check,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}