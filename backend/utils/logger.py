"""
Logger utility for Artha AI Revolutionary Multi-Agent System
Provides structured logging for the 4-stage collaboration framework
"""

import logging
import sys
from datetime import datetime
from typing import Optional


def setup_logger(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with custom formatting for the revolutionary Artha AI system
    
    Args:
        name: Logger name (defaults to 'artha_ai')
        level: Logging level (defaults to INFO)
    
    Returns:
        Configured logger instance
    """
    logger_name = name or 'artha_ai'
    logger = logging.getLogger(logger_name)
    
    # Avoid adding multiple handlers if logger already exists
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter with emojis for the revolutionary system
    formatter = logging.Formatter(
        '🤖 %(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Create default logger for the system
default_logger = setup_logger('artha_ai')


class CollaborationLogger:
    """
    Specialized logger for the 4-stage collaboration framework
    Provides structured logging for agent collaboration events
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logger = setup_logger(f'collaboration_{session_id}')
    
    def log_stage_start(self, stage_number: int, stage_name: str):
        """Log the start of a collaboration stage"""
        stage_emojis = {1: '🎯', 2: '⚡', 3: '🔥', 4: '🤝'}
        emoji = stage_emojis.get(stage_number, '🚀')
        self.logger.info(f"{emoji} Stage {stage_number}: {stage_name} - STARTED")
    
    def log_stage_complete(self, stage_number: int, stage_name: str, duration_ms: Optional[int] = None):
        """Log the completion of a collaboration stage"""
        stage_emojis = {1: '🎯', 2: '⚡', 3: '🔥', 4: '🤝'}
        emoji = stage_emojis.get(stage_number, '✅')
        duration_str = f" ({duration_ms}ms)" if duration_ms else ""
        self.logger.info(f"{emoji} Stage {stage_number}: {stage_name} - COMPLETED{duration_str}")
    
    def log_agent_start(self, agent_name: str, agent_type: str):
        """Log when an agent starts analysis"""
        agent_emojis = {
            'analyst': '🕵️',
            'research': '🎯', 
            'risk_management': '🛡️'
        }
        emoji = agent_emojis.get(agent_type, '🤖')
        self.logger.info(f"{emoji} {agent_name} - ANALYSIS STARTED")
    
    def log_agent_complete(self, agent_name: str, agent_type: str, confidence: float):
        """Log when an agent completes analysis"""
        agent_emojis = {
            'analyst': '🕵️',
            'research': '🎯',
            'risk_management': '🛡️'
        }
        emoji = agent_emojis.get(agent_type, '✅')
        self.logger.info(f"{emoji} {agent_name} - ANALYSIS COMPLETED (Confidence: {confidence:.1%})")
    
    def log_conflicts_detected(self, conflict_count: int, conflict_types: list):
        """Log conflict detection results"""
        if conflict_count > 0:
            self.logger.warning(f"⚡ {conflict_count} conflicts detected: {', '.join(conflict_types)}")
        else:
            self.logger.info("✅ No conflicts detected - agents in agreement")
    
    def log_discussion_round(self, round_number: int, agents_involved: list):
        """Log discussion round information"""
        self.logger.info(f"🔥 Discussion Round {round_number} - Agents: {', '.join(agents_involved)}")
    
    def log_consensus_reached(self, consensus_score: float):
        """Log when consensus is achieved"""
        self.logger.info(f"🤝 CONSENSUS REACHED - Score: {consensus_score:.1%}")
    
    def log_collaboration_complete(self, total_duration_ms: int, final_confidence: float):
        """Log completion of entire collaboration process"""
        self.logger.info(f"🏆 COLLABORATION COMPLETE - Duration: {total_duration_ms}ms, Final Confidence: {final_confidence:.1%}")
    
    def log_error(self, error_message: str, stage: Optional[str] = None):
        """Log collaboration errors"""
        stage_info = f" in {stage}" if stage else ""
        self.logger.error(f"❌ Collaboration Error{stage_info}: {error_message}")


# Export main functions
__all__ = ['setup_logger', 'get_logger', 'CollaborationLogger', 'default_logger']