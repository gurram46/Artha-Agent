import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../models/agent_type.dart';

class AgentTypingIndicator extends StatefulWidget {
  final List<AgentType> activeAgents;

  const AgentTypingIndicator({
    Key? key,
    required this.activeAgents,
  }) : super(key: key);

  @override
  State<AgentTypingIndicator> createState() => _AgentTypingIndicatorState();
}

class _AgentTypingIndicatorState extends State<AgentTypingIndicator>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(
      begin: 0.3,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
    _animationController.repeat(reverse: true);
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildAgentAvatars(),
          const SizedBox(width: 12),
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildTypingBubble(),
                const SizedBox(height: 4),
                _buildAgentNames(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAgentAvatars() {
    if (widget.activeAgents.isEmpty) {
      return Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: AppColors.primaryBlue,
          shape: BoxShape.circle,
        ),
        child: const Icon(
          Icons.psychology,
          color: AppColors.white,
          size: 20,
        ),
      );
    }

    if (widget.activeAgents.length == 1) {
      final agent = widget.activeAgents.first;
      return Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: agent.color,
          shape: BoxShape.circle,
        ),
        child: Icon(
          agent.icon,
          color: AppColors.white,
          size: 20,
        ),
      );
    }

    // Multiple agents - show stacked avatars
    return SizedBox(
      width: 50,
      height: 40,
      child: Stack(
        children: [
          for (int i = 0; i < widget.activeAgents.length && i < 3; i++)
            Positioned(
              left: i * 10.0,
              child: Container(
                width: 30,
                height: 30,
                decoration: BoxDecoration(
                  color: widget.activeAgents[i].color,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: AppColors.white,
                    width: 2,
                  ),
                ),
                child: Icon(
                  widget.activeAgents[i].icon,
                  color: AppColors.white,
                  size: 14,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildTypingBubble() {
    return AnimatedBuilder(
      animation: _fadeAnimation,
      builder: (context, child) {
        return Opacity(
          opacity: _fadeAnimation.value,
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.white,
              borderRadius: BorderRadius.circular(16).copyWith(
                topLeft: const Radius.circular(4),
              ),
              boxShadow: [
                BoxShadow(
                  color: AppColors.grey300.withOpacity(0.3),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildTypingDots(),
                const SizedBox(width: 12),
                Text(
                  _getTypingText(),
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.grey600,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTypingDots() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        for (int i = 0; i < 3; i++)
          AnimatedBuilder(
            animation: _animationController,
            builder: (context, child) {
              final delay = i * 0.2;
              final animationValue = (_animationController.value + delay) % 1.0;
              final opacity = animationValue < 0.5 ? 0.3 : 1.0;
              
              return Container(
                width: 6,
                height: 6,
                margin: EdgeInsets.only(right: i < 2 ? 4 : 0),
                decoration: BoxDecoration(
                  color: AppColors.primaryBlue.withOpacity(opacity),
                  shape: BoxShape.circle,
                ),
              );
            },
          ),
      ],
    );
  }

  Widget _buildAgentNames() {
    if (widget.activeAgents.isEmpty) {
      return Text(
        'AI thinking...',
        style: AppTextStyles.bodySmall.copyWith(
          color: AppColors.grey500,
          fontSize: 10,
        ),
      );
    }

    String agentText;
    if (widget.activeAgents.length == 1) {
      agentText = '${widget.activeAgents.first.displayName} is analyzing...';
    } else {
      final agentNames = widget.activeAgents.map((a) => a.displayName).join(', ');
      agentText = '$agentNames are collaborating...';
    }

    return Text(
      agentText,
      style: AppTextStyles.bodySmall.copyWith(
        color: AppColors.grey500,
        fontSize: 10,
      ),
    );
  }

  String _getTypingText() {
    if (widget.activeAgents.isEmpty) {
      return 'Processing your request...';
    }

    if (widget.activeAgents.length == 1) {
      final agent = widget.activeAgents.first;
      switch (agent) {
        case AgentType.past:
          return 'Analyzing historical data...';
        case AgentType.present:
          return 'Evaluating current situation...';
        case AgentType.future:
          return 'Planning future strategy...';
        case AgentType.coordinator:
          return 'Coordinating response...';
      }
    }

    return 'Agents collaborating...';
  }
}