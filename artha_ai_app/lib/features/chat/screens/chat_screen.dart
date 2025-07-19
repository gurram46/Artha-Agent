import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/modern_components.dart';
import '../../../core/widgets/animated_widgets.dart';
import '../../../core/services/navigation_service.dart';
import '../../../core/navigation/app_router.dart';
import '../widgets/chat_message_bubble.dart';
import '../models/chat_message.dart';
import '../models/agent_type.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({Key? key}) : super(key: key);

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _isTyping = false;
  List<AgentType> _activeAgents = [];

  @override
  void initState() {
    super.initState();
    _addWelcomeMessage();
    _messageController.addListener(_onMessageChanged);
  }

  @override
  void dispose() {
    _messageController.removeListener(_onMessageChanged);
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onMessageChanged() {
    setState(() {});
  }

  void _addWelcomeMessage() {
    setState(() {
      _messages.add(
        ChatMessage(
          id: '1',
          text: "Hi! I'm Artha AI, your personal financial advisor. I can help you analyze your investments, optimize spending, and plan for your financial goals.\n\nWhat would you like to know about your finances today?",
          isUser: false,
          timestamp: DateTime.now(),
          agentType: AgentType.coordinator,
        ),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.backgroundSecondary,
      appBar: _buildAppBar(),
      body: Column(
        children: [
          if (_activeAgents.isNotEmpty || _isTyping)
            _buildSimpleAgentStatus(),
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              itemCount: _messages.length + (_isTyping ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages.length && _isTyping) {
                  return _buildTypingIndicator();
                }
                return Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: ChatMessageBubble(
                    message: _messages[index],
                  ),
                );
              },
            ),
          ),
          _buildInputArea(),
        ],
      ),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      title: Row(
        children: [
          AnimatedScaleWidget(
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [AppColors.primaryBlue, AppColors.primaryAccent],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primaryBlue.withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Icon(
                Icons.psychology,
                color: AppColors.white,
                size: 24,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Artha AI',
                  style: AppTextStyles.heading4.copyWith(
                    color: AppColors.grey900,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Row(
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: AppColors.success,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Online • Financial Advisor',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.grey600,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
      backgroundColor: AppColors.surface,
      foregroundColor: AppColors.grey900,
      elevation: 0,
      actions: [
        AnimatedScaleWidget(
          child: IconButton(
            icon: Icon(Icons.more_vert, color: AppColors.grey600),
            onPressed: () {
              _showChatOptions(context);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildSimpleAgentStatus() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: AppColors.primaryBlue.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                SizedBox(
                  width: 12,
                  height: 12,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(AppColors.primaryBlue),
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  'AI is thinking...',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.primaryBlue,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.primaryBlue,
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.psychology,
              color: AppColors.white,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: AppColors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.cardBorder),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildTypingDot(0),
                const SizedBox(width: 4),
                _buildTypingDot(1),
                const SizedBox(width: 4),
                _buildTypingDot(2),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTypingDot(int index) {
    return AnimatedContainer(
      duration: Duration(milliseconds: 600),
      width: 6,
      height: 6,
      decoration: BoxDecoration(
        color: AppColors.primaryBlue.withOpacity(0.7),
        shape: BoxShape.circle,
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        boxShadow: [
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        children: [
          if (_messages.length == 1) _buildSmartSuggestions(),
          const SizedBox(height: 12),
          _buildMessageInput(),
        ],
      ),
    );
  }

  Widget _buildSmartSuggestions() {
    final suggestions = [
      _SuggestionItem(
        'Show my portfolio',
        Icons.pie_chart,
        AppColors.pastAgentColor,
        'Analyze my portfolio performance',
      ),
      _SuggestionItem(
        'Optimize spending',
        Icons.savings,
        AppColors.presentAgentColor,
        'Help me optimize my current spending',
      ),
      _SuggestionItem(
        'Plan for goals',
        Icons.flag,
        AppColors.futureAgentColor,
        'Help me plan my financial goals',
      ),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Try asking about:',
          style: AppTextStyles.bodySmall.copyWith(
            color: AppColors.grey600,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: suggestions.map((suggestion) => _buildSuggestionChip(suggestion)).toList(),
        ),
      ],
    );
  }

  Widget _buildSuggestionChip(_SuggestionItem suggestion) {
    return AnimatedScaleWidget(
      child: GestureDetector(
        onTap: () => _handleSuggestionTap(suggestion),
        child: GlassCard(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          borderRadius: BorderRadius.circular(16),
          elevation: 1,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: suggestion.color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  suggestion.icon,
                  size: 16,
                  color: suggestion.color,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                suggestion.label,
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.grey800,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMessageInput() {
    return GlassCard(
      borderRadius: BorderRadius.circular(24),
      elevation: 2,
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _messageController,
              decoration: InputDecoration(
                hintText: 'Ask about your finances...',
                hintStyle: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.grey500,
                ),
                filled: false,
                border: InputBorder.none,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 14,
                ),
              ),
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.grey900,
              ),
              maxLines: null,
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _sendMessage(),
            ),
          ),
          AnimatedScaleWidget(
            child: Container(
              margin: const EdgeInsets.only(right: 8),
              decoration: BoxDecoration(
                gradient: _messageController.text.isEmpty
                    ? null
                    : AppColors.primaryGradient,
                color: _messageController.text.isEmpty
                    ? AppColors.grey400
                    : null,
                shape: BoxShape.circle,
                boxShadow: _messageController.text.isEmpty
                    ? null
                    : [
                        BoxShadow(
                          color: AppColors.primaryBlue.withOpacity(0.3),
                          blurRadius: 8,
                          offset: const Offset(0, 4),
                        ),
                      ],
              ),
              child: IconButton(
                icon: Icon(
                  _isTyping ? Icons.stop : Icons.send_rounded,
                  color: AppColors.white,
                  size: 20,
                ),
                onPressed: _isTyping ? _stopTyping : _sendMessage,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _sendQuickMessage(String message) {
    _messageController.text = message;
    _sendMessage();
  }

  void _handleSuggestionTap(_SuggestionItem suggestion) {
    // Navigate to the appropriate screen based on the suggestion
    if (suggestion.label == 'Show my portfolio') {
      NavigationService.navigateTo(context, AppRouter.portfolioAnalysis);
    } else if (suggestion.label == 'Optimize spending') {
      NavigationService.navigateTo(context, AppRouter.spendingOptimization);
    } else if (suggestion.label == 'Plan for goals') {
      NavigationService.navigateTo(context, AppRouter.goalsPlanning);
    } else {
      // Fallback to sending the message
      _sendQuickMessage(suggestion.message);
    }
  }

  void _sendMessage() {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

    setState(() {
      _messages.add(
        ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: message,
          isUser: true,
          timestamp: DateTime.now(),
        ),
      );
      _isTyping = true;
      _activeAgents = _determineActiveAgents(message);
    });

    _messageController.clear();
    _scrollToBottom();

    // Simulate AI response
    Future.delayed(const Duration(seconds: 3), () {
      if (mounted) {
        setState(() {
          _messages.add(
            ChatMessage(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              text: _generateResponse(message),
              isUser: false,
              timestamp: DateTime.now(),
              agentType: _activeAgents.isNotEmpty ? _activeAgents.first : AgentType.coordinator,
              agentContributions: _activeAgents.length > 1 ? _generateAgentContributions() : null,
            ),
          );
          _isTyping = false;
          _activeAgents = [];
        });
        _scrollToBottom();
      }
    });
  }

  void _stopTyping() {
    setState(() {
      _isTyping = false;
      _activeAgents = [];
    });
  }

  void _showChatOptions(BuildContext context) {
    ModernBottomSheet.show(
      context: context,
      title: 'Chat Options',
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(
            leading: Icon(Icons.delete_outline, color: AppColors.error),
            title: Text('Clear Chat History'),
            onTap: () {
              Navigator.pop(context);
              _clearChatHistory();
            },
          ),
          ListTile(
            leading: Icon(Icons.download, color: AppColors.primaryBlue),
            title: Text('Export Chat'),
            onTap: () {
              Navigator.pop(context);
              _exportChat();
            },
          ),
          ListTile(
            leading: Icon(Icons.settings, color: AppColors.grey600),
            title: Text('Chat Settings'),
            onTap: () {
              Navigator.pop(context);
              NavigationService.navigateTo(context, AppRouter.settings);
            },
          ),
        ],
      ),
    );
  }

  void _clearChatHistory() {
    setState(() {
      _messages.clear();
      _addWelcomeMessage();
    });
  }

  void _exportChat() {
    // Implementation for exporting chat
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Chat exported successfully!'),
        backgroundColor: AppColors.success,
      ),
    );
  }

  List<AgentType> _determineActiveAgents(String message) {
    final lowerMessage = message.toLowerCase();
    final List<AgentType> agents = [];

    if (lowerMessage.contains('portfolio') || 
        lowerMessage.contains('performance') || 
        lowerMessage.contains('history') || 
        lowerMessage.contains('past')) {
      agents.add(AgentType.past);
    }

    if (lowerMessage.contains('spending') || 
        lowerMessage.contains('budget') || 
        lowerMessage.contains('current') || 
        lowerMessage.contains('expense')) {
      agents.add(AgentType.present);
    }

    if (lowerMessage.contains('goal') || 
        lowerMessage.contains('plan') || 
        lowerMessage.contains('future') || 
        lowerMessage.contains('retirement')) {
      agents.add(AgentType.future);
    }

    if (agents.isEmpty) {
      agents.add(AgentType.coordinator);
    }

    return agents;
  }

  String _generateResponse(String message) {
    final lowerMessage = message.toLowerCase();
    
    if (lowerMessage.contains('portfolio')) {
      return "Based on your portfolio analysis, you've achieved a 15.8% XIRR over the past 3 years. Your best performing fund is Axis Bluechip with 22% returns. Your SIP discipline has been excellent with 100% consistency over 24 months.\n\nKey insights:\n• Portfolio outperformed market by 3.8%\n• Optimal asset allocation maintained\n• Strong defensive positioning during market downturns\n\nWould you like a detailed breakdown of any specific fund?";
    }
    
    if (lowerMessage.contains('spending')) {
      return "Your current financial health is excellent! Here's your spending analysis:\n\n• Monthly Income: ₹1,20,000\n• Fixed Expenses: ₹40,000 (33%)\n• Investments: ₹35,000 (29%)\n• Available Surplus: ₹45,000 (38%)\n\nOptimization opportunities:\n• Reduce subscription services: Save ₹2,500/month\n• Optimize credit card usage: Improve score by 15 points\n• Tax saving investments: Save ₹15,000 annually\n\nShall I help you implement these optimizations?";
    }
    
    if (lowerMessage.contains('goal')) {
      return "Great! Let's plan your financial goals. Currently tracking:\n\n🏠 Home Purchase: ₹32.5L saved / ₹50L target (65% complete)\n🎓 Child Education: ₹8.75L saved / ₹25L target (35% complete)\n🚗 Dream Car: ₹4.5L saved / ₹15L target (30% complete)\n\nBased on your current trajectory, you're on track for most goals. For faster achievement, consider:\n• Increasing SIP by ₹5,000/month\n• Utilizing bonus amounts strategically\n• Exploring debt funds for short-term goals\n\nWhich goal would you like to prioritize?";
    }
    
    return "I'm here to help with all your financial questions! I can analyze your past investments, optimize your current spending, or plan your future goals. What specific area would you like to focus on today?";
  }

  Map<String, String> _generateAgentContributions() {
    return {
      'Past Agent': 'Historical performance analysis',
      'Present Agent': 'Current cash flow optimization',
      'Future Agent': 'Goal alignment strategy',
    };
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }
}

class _SuggestionItem {
  final String label;
  final IconData icon;
  final Color color;
  final String message;

  _SuggestionItem(this.label, this.icon, this.color, this.message);
}