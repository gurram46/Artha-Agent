class ChatResponse {
  final String sessionId;
  final List<AgentDiscussionMessage> chatroomDiscussion;
  final Map<String, AgentResponse> agentResponses;
  final CollaborationSummary collaborationSummary;
  final UnifiedRecommendation unifiedRecommendation;
  final double confidenceScore;
  final String responseType;
  final DateTime timestamp;

  ChatResponse({
    required this.sessionId,
    required this.chatroomDiscussion,
    required this.agentResponses,
    required this.collaborationSummary,
    required this.unifiedRecommendation,
    required this.confidenceScore,
    required this.responseType,
    required this.timestamp,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      sessionId: json['session_id'] ?? '',
      chatroomDiscussion: (json['chatroom_discussion'] as List<dynamic>?)
          ?.map((item) => AgentDiscussionMessage.fromJson(item))
          .toList() ?? [],
      agentResponses: _parseAgentResponses(json['agent_responses']),
      collaborationSummary: CollaborationSummary.fromJson(
        json['collaboration_summary'] ?? {}
      ),
      unifiedRecommendation: UnifiedRecommendation.fromJson(
        json['unified_recommendation'] ?? {}
      ),
      confidenceScore: (json['confidence_score'] ?? 0.0).toDouble(),
      responseType: json['response_type'] ?? 'general_advice',
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
    );
  }

  static Map<String, AgentResponse> _parseAgentResponses(dynamic agentResponsesJson) {
    if (agentResponsesJson == null) return {};
    
    final Map<String, AgentResponse> responses = {};
    (agentResponsesJson as Map<String, dynamic>).forEach((key, value) {
      responses[key] = AgentResponse.fromJson(value);
    });
    return responses;
  }
}

class AgentDiscussionMessage {
  final String agent;
  final String agentName;
  final String message;
  final double? confidence;
  final String? type;
  final DateTime timestamp;

  AgentDiscussionMessage({
    required this.agent,
    required this.agentName,
    required this.message,
    this.confidence,
    this.type,
    required this.timestamp,
  });

  factory AgentDiscussionMessage.fromJson(Map<String, dynamic> json) {
    return AgentDiscussionMessage(
      agent: json['agent'] ?? '',
      agentName: json['agent_name'] ?? '',
      message: json['message'] ?? '',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      type: json['type'],
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
    );
  }
}

class AgentResponse {
  final String agent;
  final String analysis;
  final List<String> keyInsights;
  final double confidence;
  final String? dataQuality;
  final List<String>? historicalPatterns;
  final List<String>? optimizationOpportunities;
  final int? currentHealthScore;
  final List<String>? immediateActions;
  final Map<String, String>? goalFeasibility;
  final List<String>? planningRecommendations;
  final Map<String, dynamic>? timelineProjections;
  final DateTime timestamp;

  AgentResponse({
    required this.agent,
    required this.analysis,
    required this.keyInsights,
    required this.confidence,
    this.dataQuality,
    this.historicalPatterns,
    this.optimizationOpportunities,
    this.currentHealthScore,
    this.immediateActions,
    this.goalFeasibility,
    this.planningRecommendations,
    this.timelineProjections,
    required this.timestamp,
  });

  factory AgentResponse.fromJson(Map<String, dynamic> json) {
    return AgentResponse(
      agent: json['agent'] ?? '',
      analysis: json['analysis'] ?? '',
      keyInsights: List<String>.from(json['key_insights'] ?? []),
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      dataQuality: json['data_quality'],
      historicalPatterns: json['historical_patterns']?.cast<String>(),
      optimizationOpportunities: json['optimization_opportunities']?.cast<String>(),
      currentHealthScore: json['current_health_score'],
      immediateActions: json['immediate_actions']?.cast<String>(),
      goalFeasibility: json['goal_feasibility']?.cast<String, String>(),
      planningRecommendations: json['planning_recommendations']?.cast<String>(),
      timelineProjections: json['timeline_projections'],
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
    );
  }
}

class CollaborationSummary {
  final int totalInteractions;
  final int conflictsResolved;
  final int synergiesIdentified;
  final int intelligenceShared;

  CollaborationSummary({
    required this.totalInteractions,
    required this.conflictsResolved,
    required this.synergiesIdentified,
    required this.intelligenceShared,
  });

  factory CollaborationSummary.fromJson(Map<String, dynamic> json) {
    return CollaborationSummary(
      totalInteractions: json['total_interactions'] ?? 0,
      conflictsResolved: json['conflicts_resolved'] ?? 0,
      synergiesIdentified: json['synergies_identified'] ?? 0,
      intelligenceShared: json['intelligence_shared'] ?? 0,
    );
  }
}

class UnifiedRecommendation {
  final String summary;
  final List<String> actionSteps;
  final Map<String, String> agentContributions;
  final double confidence;
  final Map<String, String> implementationTimeline;
  final DateTime timestamp;

  UnifiedRecommendation({
    required this.summary,
    required this.actionSteps,
    required this.agentContributions,
    required this.confidence,
    required this.implementationTimeline,
    required this.timestamp,
  });

  factory UnifiedRecommendation.fromJson(Map<String, dynamic> json) {
    return UnifiedRecommendation(
      summary: json['summary'] ?? '',
      actionSteps: List<String>.from(json['action_steps'] ?? []),
      agentContributions: Map<String, String>.from(json['agent_contributions'] ?? {}),
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      implementationTimeline: Map<String, String>.from(json['implementation_timeline'] ?? {}),
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
    );
  }
}