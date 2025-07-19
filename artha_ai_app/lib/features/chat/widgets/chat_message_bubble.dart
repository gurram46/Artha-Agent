import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../models/chat_message.dart';
import '../models/agent_type.dart';

class ChatMessageBubble extends StatelessWidget {
  final ChatMessage message;

  const ChatMessageBubble({
    Key? key,
    required this.message,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: message.isUser 
            ? MainAxisAlignment.end 
            : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser) ...[
            _buildAgentAvatar(),
            const SizedBox(width: 12),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment: message.isUser 
                  ? CrossAxisAlignment.end 
                  : CrossAxisAlignment.start,
              children: [
                _buildMessageBubble(context),
                const SizedBox(height: 4),
                _buildTimestamp(),
              ],
            ),
          ),
          if (message.isUser) ...[
            const SizedBox(width: 12),
            _buildUserAvatar(),
          ],
        ],
      ),
    );
  }

  Widget _buildAgentAvatar() {
    final agentType = message.agentType ?? AgentType.coordinator;
    return Container(
      width: 36,
      height: 36,
      decoration: BoxDecoration(
        color: agentType.color,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: agentType.color.withOpacity(0.3),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Icon(
        agentType.icon,
        color: AppColors.white,
        size: 18,
      ),
    );
  }

  Widget _buildUserAvatar() {
    return Container(
      width: 36,
      height: 36,
      decoration: BoxDecoration(
        color: AppColors.primaryBlue,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: AppColors.primaryBlue.withOpacity(0.3),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: const Icon(
        Icons.person_rounded,
        color: AppColors.white,
        size: 18,
      ),
    );
  }

  Widget _buildMessageBubble(BuildContext context) {
    return Container(
      constraints: BoxConstraints(
        maxWidth: MediaQuery.of(context).size.width * 0.8,
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: message.isUser 
            ? AppColors.primaryBlue 
            : AppColors.white,
        borderRadius: BorderRadius.circular(20).copyWith(
          topLeft: message.isUser ? const Radius.circular(20) : const Radius.circular(6),
          topRight: message.isUser ? const Radius.circular(6) : const Radius.circular(20),
        ),
        border: message.isUser 
            ? null 
            : Border.all(color: AppColors.cardBorder, width: 1),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser && message.agentType != null) ...[
            _buildAgentHeader(),
            const SizedBox(height: 8),
          ],
          Text(
            message.text,
            style: AppTextStyles.bodyMedium.copyWith(
              color: message.isUser ? AppColors.white : AppColors.grey800,
              height: 1.4,
            ),
          ),
          if (message.agentContributions != null) ...[
            const SizedBox(height: 12),
            _buildAgentContributions(),
          ],
        ],
      ),
    );
  }

  Widget _buildAgentHeader() {
    final agentType = message.agentType!;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(
            color: agentType.color,
            shape: BoxShape.circle,
          ),
          child: Icon(
            agentType.icon,
            color: AppColors.white,
            size: 10,
          ),
        ),
        const SizedBox(width: 6),
        Text(
          agentType.displayName,
          style: AppTextStyles.labelSmall.copyWith(
            color: agentType.color,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildAgentContributions() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.grey100,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Agent Contributions',
            style: AppTextStyles.labelSmall.copyWith(
              fontWeight: FontWeight.w600,
              color: AppColors.grey700,
            ),
          ),
          const SizedBox(height: 8),
          ...message.agentContributions!.entries.map((entry) {
            final agentName = entry.key;
            final contribution = entry.value;
            
            Color agentColor;
            IconData agentIcon;
            
            if (agentName.contains('Past')) {
              agentColor = AppColors.pastAgentColor;
              agentIcon = Icons.history;
            } else if (agentName.contains('Present')) {
              agentColor = AppColors.presentAgentColor;
              agentIcon = Icons.today;
            } else if (agentName.contains('Future')) {
              agentColor = AppColors.futureAgentColor;
              agentIcon = Icons.timeline;
            } else {
              agentColor = AppColors.primaryBlue;
              agentIcon = Icons.psychology;
            }
            
            return Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    agentIcon,
                    size: 12,
                    color: agentColor,
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      '$agentName: $contribution',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.grey700,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildTimestamp() {
    return Text(
      DateFormat('HH:mm').format(message.timestamp),
      style: AppTextStyles.bodySmall.copyWith(
        color: AppColors.grey500,
        fontSize: 10,
      ),
    );
  }
}