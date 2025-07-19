import 'agent_type.dart';

class ChatMessage {
  final String id;
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final AgentType? agentType;
  final Map<String, String>? agentContributions;

  ChatMessage({
    required this.id,
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.agentType,
    this.agentContributions,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'],
      text: json['text'],
      isUser: json['isUser'],
      timestamp: DateTime.parse(json['timestamp']),
      agentType: json['agentType'] != null
          ? AgentType.values.firstWhere(
              (e) => e.toString() == 'AgentType.${json['agentType']}',
            )
          : null,
      agentContributions: json['agentContributions'] != null
          ? Map<String, String>.from(json['agentContributions'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'text': text,
      'isUser': isUser,
      'timestamp': timestamp.toIso8601String(),
      'agentType': agentType?.toString().split('.').last,
      'agentContributions': agentContributions,
    };
  }
}