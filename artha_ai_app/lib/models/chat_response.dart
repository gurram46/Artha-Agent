class ChatResponse {
  final String sessionId;
  final String userQuery;
  final String finalSummary;
  final Map<String, AgentInsight> agentInsights;
  final double overallConfidence;
  final DateTime timestamp;
  final bool? error;

  ChatResponse({
    required this.sessionId,
    required this.userQuery,
    required this.finalSummary,
    required this.agentInsights,
    required this.overallConfidence,
    required this.timestamp,
    this.error,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      sessionId: json['session_id'] ?? '',
      userQuery: json['user_query'] ?? '',
      finalSummary: json['final_summary'] ?? '',
      agentInsights: _parseAgentInsights(json['agent_insights']),
      overallConfidence: (json['overall_confidence'] ?? 0.0).toDouble(),
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
      error: json['error'],
    );
  }

  static Map<String, AgentInsight> _parseAgentInsights(dynamic agentInsightsJson) {
    if (agentInsightsJson == null) return {};
    
    final Map<String, AgentInsight> insights = {};
    (agentInsightsJson as Map<String, dynamic>).forEach((key, value) {
      insights[key] = AgentInsight.fromJson(value);
    });
    return insights;
  }

  Map<String, dynamic> toJson() {
    return {
      'session_id': sessionId,
      'user_query': userQuery,
      'final_summary': finalSummary,
      'agent_insights': agentInsights.map((key, value) => MapEntry(key, value.toJson())),
      'overall_confidence': overallConfidence,
      'timestamp': timestamp.toIso8601String(),
      'error': error,
    };
  }
}

class AgentInsight {
  final String agentName;
  final List<String> keyFindings;
  final double confidence;

  AgentInsight({
    required this.agentName,
    required this.keyFindings,
    required this.confidence,
  });

  factory AgentInsight.fromJson(Map<String, dynamic> json) {
    return AgentInsight(
      agentName: json['agent_name'] ?? '',
      keyFindings: List<String>.from(json['key_findings'] ?? []),
      confidence: (json['confidence'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'agent_name': agentName,
      'key_findings': keyFindings,
      'confidence': confidence,
    };
  }
}

// Legacy models for backward compatibility - can be removed later
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