"""
Base Agent Class - Revolutionary Multi-Agent Collaboration Framework
Implements the 4-stage collaboration system for hackathon-winning financial AI
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class BaseAgent(ABC):
    """
    Revolutionary base class for collaborative financial advisor agents
    Implements the 4-stage collaboration framework:
    1. Independent Analysis (Parallel Processing)
    2. Conflict Detection (AI-Powered) 
    3. Collaborative Discussion (Real-Time Simulation)
    4. Unified Decision (Consensus Building)
    """
    
    def __init__(self, agent_id: str, agent_name: str, specialization: str, data_loader):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.specialization = specialization
        self.data_loader = data_loader
        self.logger = logging.getLogger(f"agent.{agent_id}")
        
        # Agent collaboration storage
        self.session_data = {}
        self.collaboration_history = []
        self.conflict_positions = {}
    
    @abstractmethod
    def analyze(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Stage 1: Independent analysis method
        Each agent analyzes the query according to their specialization
        Returns structured analysis with collaboration points
        """
        pass
    
    @abstractmethod
    def collaborate(self, peer_responses: Dict[str, Any], conflict_type: str) -> Dict[str, Any]:
        """
        Stage 3: Collaboration method for discussion
        Engage in collaborative discussion to resolve conflicts
        """
        pass
    
    @abstractmethod
    def defend_position(self, challenge: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 3: Defend position in disagreement
        Provide evidence-based defense of agent's recommendations
        """
        pass
    
    @abstractmethod
    def seek_compromise(self, opposing_views: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Stage 3: Find middle ground with other agents
        Attempt to find compromise solutions
        """
        pass
    
    # ===== COLLABORATION FRAMEWORK METHODS =====
    
    def extract_financial_metrics(self, analysis: str) -> Dict[str, Any]:
        """Extract key financial metrics for conflict detection"""
        import re
        
        metrics = {}
        
        # Extract budget recommendations
        budget_match = re.search(r'₹([\d,]+(?:\.\d+)?)\s*(?:lakhs?|L|crores?|K)?', analysis)
        if budget_match:
            amount = budget_match.group(1).replace(',', '')
            metrics['recommended_budget'] = float(amount)
        
        # Extract risk level indicators
        risk_keywords = {
            'low': ['safe', 'conservative', 'stable', 'secure'],
            'medium': ['moderate', 'balanced', 'reasonable'],
            'high': ['aggressive', 'risky', 'speculative', 'volatile']
        }
        
        analysis_lower = analysis.lower()
        for risk_level, keywords in risk_keywords.items():
            if any(keyword in analysis_lower for keyword in keywords):
                metrics['risk_tolerance'] = risk_level
                break
        
        # Extract timing recommendations
        timing_keywords = {
            'immediate': ['now', 'immediately', 'urgent', 'asap'],
            'short_term': ['soon', 'within weeks', 'short term'],
            'long_term': ['later', 'long term', 'future', 'eventually']
        }
        
        for timing, keywords in timing_keywords.items():
            if any(keyword in analysis_lower for keyword in keywords):
                metrics['timing'] = timing
                break
        
        return metrics
    
    def prepare_collaboration_data(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for agent collaboration"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'specialization': self.specialization,
            'key_insights': analysis.get('key_insights', []),
            'confidence': analysis.get('confidence', 0.5),
            'financial_metrics': self.extract_financial_metrics(analysis.get('analysis', '')),
            'collaboration_points': analysis.get('collaboration_points', []),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_discussion_message(self, context: Dict[str, Any], message_type: str = 'position') -> str:
        """Generate a discussion message for collaboration"""
        if message_type == 'position':
            return f"As the {self.agent_name}, I recommend {context.get('recommendation', 'careful consideration')}"
        elif message_type == 'challenge':
            return f"I question this recommendation because {context.get('concern', 'it may have risks')}"
        elif message_type == 'compromise':
            return f"Perhaps we could find middle ground by {context.get('alternative', 'adjusting our approach')}"
        else:
            return f"From my {self.specialization} perspective, {context.get('insight', 'this requires analysis')}"
    
    def calculate_confidence_with_peers(self, peer_confidences: List[float]) -> float:
        """Calculate adjusted confidence based on peer agreement"""
        base_confidence = 0.8  # Default agent confidence
        
        if not peer_confidences:
            return base_confidence
        
        # Average peer confidence
        avg_peer_confidence = sum(peer_confidences) / len(peer_confidences)
        
        # If peers are very confident and close to each other, boost confidence
        variance = sum((c - avg_peer_confidence) ** 2 for c in peer_confidences) / len(peer_confidences)
        
        if variance < 0.1 and avg_peer_confidence > 0.7:
            return min(base_confidence * 1.1, 1.0)
        elif variance > 0.3:  # High disagreement
            return base_confidence * 0.8
        else:
            return base_confidence
    
    # ===== SESSION AND UTILITY METHODS =====
    
    def update_session_context(self, session_id: str, context: Dict[str, Any]):
        """Update session context for this agent"""
        if session_id not in self.session_data:
            self.session_data[session_id] = {}
        
        self.session_data[session_id].update(context)
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get session context for this agent"""
        return self.session_data.get(session_id, {})
    
    def clear_session(self, session_id: str):
        """Clear session data for this agent"""
        if session_id in self.session_data:
            del self.session_data[session_id]
    
    def get_agent_info(self) -> Dict[str, str]:
        """Get basic agent information"""
        return {
            'id': self.agent_id,
            'name': self.agent_name,
            'specialization': self.specialization,
            'status': 'active',
            'last_active': datetime.now().isoformat()
        }
    
    def validate_input(self, user_message: str, user_id: str) -> Dict[str, Any]:
        """Validate input parameters"""
        errors = []
        
        if not user_message or not user_message.strip():
            errors.append("User message cannot be empty")
        
        if not user_id or not user_id.strip():
            errors.append("User ID cannot be empty")
        
        if len(user_message) > 5000:
            errors.append("User message too long (max 5000 characters)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def log_collaboration(self, session_id: str, event_type: str, data: Dict[str, Any]):
        """Log collaboration events for analysis"""
        self.collaboration_history.append({
            'session_id': session_id,
            'agent_id': self.agent_id,
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        
        self.logger.info(f"Collaboration event: {event_type} - Agent: {self.agent_id}")
    
    def get_collaboration_capabilities(self) -> List[str]:
        """Get agent's collaboration capabilities"""
        return [
            "Independent financial analysis",
            "Conflict detection and resolution",
            "Multi-agent discussion participation",
            "Consensus building and compromise"
        ]
    
    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle errors gracefully and return fallback response"""
        self.logger.error(f"Error in {self.agent_name} - {context}: {str(error)}")
        
        return {
            'agent': self.agent_id,
            'analysis': f"I apologize, but I encountered an issue while processing your request. {context}",
            'key_insights': ["Unable to complete analysis due to technical issue"],
            'confidence': 0.0,
            'error': True,
            'error_message': str(error),
            'collaboration_points': [],
            'financial_metrics': {},
            'timestamp': datetime.now().isoformat()
        }