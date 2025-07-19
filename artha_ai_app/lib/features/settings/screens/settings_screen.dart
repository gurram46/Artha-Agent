import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/app_card.dart';
import '../../../core/services/navigation_service.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BackGestureWrapper(
      child: Scaffold(
        backgroundColor: AppColors.background,
        appBar: CustomAppBar(
          title: 'Settings',
          backgroundColor: AppColors.primaryBlue,
          foregroundColor: AppColors.white,
        ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            _buildSection('Account', [
              _buildSettingItem('Profile', Icons.person_outlined, () {}),
              _buildSettingItem('Security', Icons.security_outlined, () {}),
              _buildSettingItem('Privacy', Icons.privacy_tip_outlined, () {}),
            ]),
            const SizedBox(height: 16),
            _buildSection('Preferences', [
              _buildSettingItem('Notifications', Icons.notifications_outlined, () {}),
              _buildSettingItem('Language', Icons.language_outlined, () {}),
              _buildSettingItem('Theme', Icons.palette_outlined, () {}),
            ]),
            const SizedBox(height: 16),
            _buildSection('Support', [
              _buildSettingItem('Help Center', Icons.help_outline, () {}),
              _buildSettingItem('Contact Support', Icons.support_agent_outlined, () {}),
              _buildSettingItem('About', Icons.info_outline, () {}),
            ]),
          ],
        ),
      ),
    ),
    );
  }

  Widget _buildSection(String title, List<Widget> items) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          ...items,
        ],
      ),
    );
  }

  Widget _buildSettingItem(String title, IconData icon, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 12),
        child: Row(
          children: [
            Icon(icon, color: AppColors.grey600, size: 24),
            const SizedBox(width: 16),
            Expanded(
              child: Text(
                title,
                style: AppTextStyles.bodyMedium,
              ),
            ),
            Icon(
              Icons.arrow_forward_ios,
              size: 16,
              color: AppColors.grey400,
            ),
          ],
        ),
      ),
    );
  }
}