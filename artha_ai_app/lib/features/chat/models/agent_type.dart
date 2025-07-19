import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

enum AgentType {
  past,
  present,
  future,
  coordinator,
}

extension AgentTypeExtension on AgentType {
  String get displayName {
    switch (this) {
      case AgentType.past:
        return 'Past Agent';
      case AgentType.present:
        return 'Present Agent';
      case AgentType.future:
        return 'Future Agent';
      case AgentType.coordinator:
        return 'Artha AI';
    }
  }

  String get description {
    switch (this) {
      case AgentType.past:
        return 'Analyzes investment history and portfolio performance';
      case AgentType.present:
        return 'Optimizes current spending and financial health';
      case AgentType.future:
        return 'Plans financial goals and life events';
      case AgentType.coordinator:
        return 'Coordinates all agents for comprehensive advice';
    }
  }

  Color get color {
    switch (this) {
      case AgentType.past:
        return AppColors.pastAgentColor;
      case AgentType.present:
        return AppColors.presentAgentColor;
      case AgentType.future:
        return AppColors.futureAgentColor;
      case AgentType.coordinator:
        return AppColors.primaryBlue;
    }
  }

  IconData get icon {
    switch (this) {
      case AgentType.past:
        return Icons.history;
      case AgentType.present:
        return Icons.today;
      case AgentType.future:
        return Icons.timeline;
      case AgentType.coordinator:
        return Icons.psychology;
    }
  }
}