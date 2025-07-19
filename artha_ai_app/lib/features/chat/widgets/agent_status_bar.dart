import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../models/agent_type.dart';

class AgentStatusBar extends StatelessWidget {
  final List<AgentType> activeAgents;
  final bool isTyping;

  const AgentStatusBar({
    Key? key,
    required this.activeAgents,
    required this.isTyping,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.white,
        border: Border(
          bottom: BorderSide(
            color: AppColors.grey200,
            width: 1,
          ),
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Icon(
                Icons.smart_toy,
                size: 20,
                color: AppColors.primaryBlue,
              ),
              const SizedBox(width: 8),
              Text(
                'AI Agents',
                style: AppTextStyles.bodyMedium.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppColors.grey800,
                ),
              ),
              const Spacer(),
              if (isTyping) ...[
                SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(AppColors.primaryBlue),
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  'Thinking...',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.grey600,
                  ),
                ),
              ],
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildAgentIndicator(
                AgentType.past,
                isActive: activeAgents.contains(AgentType.past),
              ),
              const SizedBox(width: 16),
              _buildAgentIndicator(
                AgentType.present,
                isActive: activeAgents.contains(AgentType.present),
              ),
              const SizedBox(width: 16),
              _buildAgentIndicator(
                AgentType.future,
                isActive: activeAgents.contains(AgentType.future),
              ),
              const Spacer(),
              if (activeAgents.length > 1) ...[
                Icon(
                  Icons.group_work,
                  size: 16,
                  color: AppColors.primaryBlue,
                ),
                const SizedBox(width: 4),
                Text(
                  'Collaborating',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.primaryBlue,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAgentIndicator(AgentType agentType, {required bool isActive}) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: isActive ? agentType.color : AppColors.grey300,
            shape: BoxShape.circle,
          ),
          child: isActive && isTyping
              ? SizedBox(
                  width: 8,
                  height: 8,
                  child: CircularProgressIndicator(
                    strokeWidth: 1,
                    valueColor: AlwaysStoppedAnimation<Color>(AppColors.white),
                  ),
                )
              : null,
        ),
        const SizedBox(width: 6),
        Text(
          _getShortName(agentType),
          style: AppTextStyles.bodySmall.copyWith(
            color: isActive ? agentType.color : AppColors.grey500,
            fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
          ),
        ),
      ],
    );
  }

  String _getShortName(AgentType agentType) {
    switch (agentType) {
      case AgentType.past:
        return 'Past';
      case AgentType.present:
        return 'Present';
      case AgentType.future:
        return 'Future';
      case AgentType.coordinator:
        return 'Coordinator';
    }
  }
}