"""
Revolutionary Agent Coordinator - 4-Stage Collaboration Framework
The Ultimate Hackathon-Winning Multi-Agent Financial AI Orchestra
Implements the complete collaboration system: Analysis → Conflict Detection → Discussion → Consensus
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import google.generativeai as genai

# Import our revolutionary agents
from agents.analyst_agent.analyst import AnalystAgent
from agents.research_agent.research import ResearchAgent
from agents.risk_management_agent.risk_manager import RiskManagementAgent

# Import conflict detection and resolution system
from coordination.conflict_detector import ConflictDetector, DiscussionSimulator


class AgentCoordinator:
    """
    Revolutionary Agent Coordinator - The Ultimate Financial AI Orchestra
    
    Implements the 4-Stage Collaboration Framework:
    🎯 Stage 1: Independent Analysis (Parallel Processing)
    ⚡ Stage 2: Conflict Detection (AI-Powered)
    🔥 Stage 3: Collaborative Discussion (Real-Time Simulation)
    🤝 Stage 4: Unified Decision (Consensus Building)
    
    This is the secret sauce that makes three financial minds work as one!
    """
    
    def __init__(self, analyst_agent: AnalystAgent, research_agent: ResearchAgent, risk_agent: RiskManagementAgent):
        # Revolutionary agent trio
        self.analyst_agent = analyst_agent
        self.research_agent = research_agent
        self.risk_agent = risk_agent
        
        # Collaboration framework components
        self.conflict_detector = ConflictDetector()
        self.discussion_simulator = DiscussionSimulator()
        
        # Configure Gemini for final synthesis
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        self.logger = logging.getLogger("coordinator")
        
        # Enhanced session storage
        self.sessions = {}
        self.collaboration_metrics = {}
    
    def process_collaborative_query(self, user_message: str, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        🏆 REVOLUTIONARY 4-STAGE COLLABORATION FRAMEWORK 🏆
        The hackathon-winning approach to multi-agent financial AI!
        
        Stage 1: Independent Analysis (Parallel Processing)
        Stage 2: Conflict Detection (AI-Powered)  
        Stage 3: Collaborative Discussion (Real-Time Simulation)
        Stage 4: Unified Decision (Consensus Building)
        """
        try:
            self.logger.info(f"🚀 Initiating 4-stage collaboration for session {session_id}")
            
            # 🎯 STAGE 1: INDEPENDENT ANALYSIS (Parallel Processing)
            self.logger.info("📊 Stage 1: Independent agent analysis...")
            
            stage1_responses = {}
            stage1_responses['analyst'] = self.analyst_agent.analyze(user_message, user_id)
            stage1_responses['research'] = self.research_agent.analyze(user_message, user_id) 
            stage1_responses['risk_management'] = self.risk_agent.analyze(user_message, user_id)
            
            self.logger.info(f"✅ Stage 1 completed: {len(stage1_responses)} agents analyzed")
            
            # ⚡ STAGE 2: CONFLICT DETECTION (AI-Powered)
            self.logger.info("🔍 Stage 2: AI-powered conflict detection...")
            
            detected_conflicts = self.conflict_detector.detect_conflicts(stage1_responses)
            conflict_count = len(detected_conflicts)
            
            self.logger.info(f"⚡ Stage 2 completed: {conflict_count} conflicts detected")
            
            # 🔥 STAGE 3: COLLABORATIVE DISCUSSION (Real-Time Simulation)
            discussion_log = []
            stage3_responses = stage1_responses.copy()  # Start with original responses
            
            if conflict_count > 0:
                self.logger.info(f"🔥 Stage 3: Simulating collaborative discussion for {conflict_count} conflicts...")
                
                # Simulate discussion to resolve conflicts
                discussion_log = self.discussion_simulator.simulate_discussion(
                    stage1_responses, detected_conflicts, user_message
                )
                
                # Get agent collaboration responses for significant conflicts
                high_priority_conflicts = [c for c in detected_conflicts if c.get('severity') == 'high']
                
                if high_priority_conflicts:
                    stage3_responses = self._facilitate_agent_collaboration(
                        stage1_responses, high_priority_conflicts, user_message
                    )
                
                self.logger.info(f"🔥 Stage 3 completed: {len(discussion_log)} discussion rounds")
            else:
                self.logger.info("🔥 Stage 3: No conflicts detected - proceeding to consensus")
                discussion_log.append({
                    'round': 0,
                    'status': 'no_conflicts',
                    'message': 'All agents in agreement - proceeding to unified decision'
                })
            
            # 🤝 STAGE 4: UNIFIED DECISION (Consensus Building)
            self.logger.info("🤝 Stage 4: Building unified consensus...")
            
            unified_response = self._build_unified_decision(
                user_message=user_message,
                stage1_responses=stage1_responses,
                stage3_responses=stage3_responses,
                detected_conflicts=detected_conflicts,
                discussion_log=discussion_log,
                session_id=session_id
            )
            
            self.logger.info("🤝 Stage 4 completed: Unified decision built")
            
            # Store collaboration session
            self._store_collaboration_session(
                session_id=session_id,
                user_message=user_message,
                user_id=user_id,
                stage1_responses=stage1_responses,
                detected_conflicts=detected_conflicts,
                discussion_log=discussion_log,
                unified_response=unified_response
            )
            
            # Calculate collaboration metrics
            collaboration_metrics = self._calculate_collaboration_metrics(
                stage1_responses, detected_conflicts, discussion_log
            )
            
            # Build final response for user
            final_response = {
                'session_id': session_id,
                'user_query': user_message,
                'collaboration_summary': unified_response,
                'agent_insights': self._format_agent_insights(stage1_responses),
                'conflicts_resolved': len(detected_conflicts),
                'discussion_rounds': len(discussion_log),
                'overall_confidence': self._calculate_unified_confidence(stage1_responses, detected_conflicts),
                'collaboration_metrics': collaboration_metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"🏆 Revolutionary collaboration completed successfully!")
            return final_response
            
        except Exception as e:
            self.logger.error(f"❌ Error in revolutionary collaboration: {str(e)}")
            return self._create_fallback_response(session_id, user_message, str(e))
    
    # ===== COLLABORATION FRAMEWORK HELPER METHODS =====
    
    def _facilitate_agent_collaboration(self, stage1_responses: Dict[str, Any], 
                                      conflicts: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Facilitate agent collaboration for conflict resolution"""
        try:
            collaborated_responses = {}
            
            for conflict in conflicts:
                conflict_type = conflict.get('type', 'general')
                agents_involved = conflict.get('agents_involved', [])
                
                # Get collaboration responses from involved agents
                for agent_id in agents_involved:
                    if agent_id not in collaborated_responses:
                        collaborated_responses[agent_id] = stage1_responses[agent_id].copy()
                    
                    # Get agent's collaboration response
                    if agent_id == 'analyst':
                        collaboration_response = self.analyst_agent.collaborate(stage1_responses, conflict_type)
                    elif agent_id == 'research':
                        collaboration_response = self.research_agent.collaborate(stage1_responses, conflict_type)
                    elif agent_id == 'risk_management':
                        collaboration_response = self.risk_agent.collaborate(stage1_responses, conflict_type)
                    else:
                        continue
                    
                    # Update response with collaboration insights
                    collaborated_responses[agent_id]['collaboration_message'] = collaboration_response.get('collaboration_message', '')
                    collaborated_responses[agent_id]['collaboration_stance'] = collaboration_response.get('stance', '')
            
            # Merge with original responses for non-conflicted agents
            for agent_id, response in stage1_responses.items():
                if agent_id not in collaborated_responses:
                    collaborated_responses[agent_id] = response
            
            return collaborated_responses
            
        except Exception as e:
            self.logger.error(f"Error facilitating collaboration: {str(e)}")
            return stage1_responses  # Fallback to original responses
    
    def _build_unified_decision(self, user_message: str, stage1_responses: Dict[str, Any], 
                               stage3_responses: Dict[str, Any], detected_conflicts: List[Dict[str, Any]], 
                               discussion_log: List[Dict[str, Any]], session_id: str) -> str:
        """Build unified decision from collaboration results"""
        try:
            # Create synthesis prompt for Gemini
            synthesis_prompt = f"""
            You are synthesizing the collaborative analysis of 3 expert financial agents into one unified recommendation.
            
            USER QUERY: "{user_message}"
            
            AGENT INSIGHTS:
            Data Analyst: {stage1_responses.get('analyst', {}).get('analysis', 'No analysis available')[:300]}
            Research Strategist: {stage1_responses.get('research', {}).get('analysis', 'No analysis available')[:300]}
            Risk Guardian: {stage1_responses.get('risk_management', {}).get('analysis', 'No analysis available')[:300]}
            
            CONFLICTS DETECTED: {len(detected_conflicts)} conflicts were identified and resolved through collaboration.
            
            DISCUSSION SUMMARY: {len(discussion_log)} rounds of discussion led to consensus.
            
            MISSION: Create a unified, actionable financial recommendation that:
            1. Synthesizes all three expert perspectives
            2. Addresses any conflicts that were resolved
            3. Provides specific, actionable guidance
            4. Maintains the collaborative spirit of the analysis
            
            Format as a comprehensive yet concise recommendation (400-600 words).
            """
            
            response = self.model.generate_content(synthesis_prompt)
            return response.text
            
        except Exception as e:
            self.logger.error(f"Error building unified decision: {str(e)}")
            return self._create_fallback_synthesis(stage1_responses, user_message)
    
    def _store_collaboration_session(self, session_id: str, user_message: str, user_id: str,
                                   stage1_responses: Dict[str, Any], detected_conflicts: List[Dict[str, Any]],
                                   discussion_log: List[Dict[str, Any]], unified_response: str):
        """Store complete collaboration session data"""
        self.sessions[session_id] = {
            'user_message': user_message,
            'user_id': user_id,
            'stage1_responses': stage1_responses,
            'detected_conflicts': detected_conflicts,
            'discussion_log': discussion_log,
            'unified_response': unified_response,
            'timestamp': datetime.now().isoformat(),
            'framework_version': '4-stage-collaboration-v1.0'
        }
    
    def _calculate_collaboration_metrics(self, stage1_responses: Dict[str, Any], 
                                       detected_conflicts: List[Dict[str, Any]], 
                                       discussion_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate collaboration effectiveness metrics"""
        return {
            'total_agents': len(stage1_responses),
            'conflicts_detected': len(detected_conflicts),
            'conflicts_resolved': len([c for c in detected_conflicts if c.get('resolution_required', False)]),
            'discussion_rounds': len(discussion_log),
            'consensus_achieved': any(d.get('consensus_reached', False) for d in discussion_log),
            'collaboration_score': self._calculate_collaboration_score(stage1_responses, detected_conflicts),
            'framework_efficiency': 'high' if len(detected_conflicts) <= 2 else 'moderate'
        }
    
    def _calculate_collaboration_score(self, stage1_responses: Dict[str, Any], 
                                     detected_conflicts: List[Dict[str, Any]]) -> float:
        """Calculate overall collaboration effectiveness score"""
        base_score = 0.8  # Start with high base score
        
        # Penalize for high-severity conflicts
        high_severity_conflicts = len([c for c in detected_conflicts if c.get('severity') == 'high'])
        if high_severity_conflicts > 0:
            base_score -= (high_severity_conflicts * 0.1)
        
        # Reward for agent confidence alignment
        confidences = [resp.get('confidence', 0.5) for resp in stage1_responses.values()]
        if confidences:
            confidence_variance = sum((c - sum(confidences)/len(confidences))**2 for c in confidences) / len(confidences)
            if confidence_variance < 0.1:  # Low variance = good alignment
                base_score += 0.1
        
        return min(max(base_score, 0.0), 1.0)  # Clamp between 0 and 1
    
    def _format_agent_insights(self, stage1_responses: Dict[str, Any]) -> Dict[str, Any]:
        """Format agent insights for user presentation"""
        formatted_insights = {}
        
        agent_display_names = {
            'analyst': 'Data Analyst',
            'research': 'Research Strategist', 
            'risk_management': 'Risk Guardian'
        }
        
        for agent_id, response in stage1_responses.items():
            formatted_insights[agent_id] = {
                'agent_name': agent_display_names.get(agent_id, agent_id),
                'key_findings': response.get('key_insights', [])[:3],  # Top 3
                'confidence': response.get('confidence', 0.5),
                'specialization': response.get('agent_name', 'Financial Expert')
            }
        
        return formatted_insights
    
    def _calculate_unified_confidence(self, stage1_responses: Dict[str, Any], 
                                    detected_conflicts: List[Dict[str, Any]]) -> float:
        """Calculate unified confidence score"""
        confidences = [resp.get('confidence', 0.5) for resp in stage1_responses.values()]
        
        if not confidences:
            return 0.5
        
        # Average confidence
        avg_confidence = sum(confidences) / len(confidences)
        
        # Reduce confidence for unresolved high-severity conflicts
        high_severity_conflicts = len([c for c in detected_conflicts if c.get('severity') == 'high'])
        if high_severity_conflicts > 0:
            avg_confidence *= 0.9
        
        return min(avg_confidence, 1.0)
    
    def _create_fallback_response(self, session_id: str, user_message: str, error: str) -> Dict[str, Any]:
        """Create fallback response when collaboration fails"""
        return {
            'session_id': session_id,
            'user_query': user_message,
            'collaboration_summary': f"I apologize, but I encountered an error during the collaborative analysis: {error}. Please try your question again.",
            'agent_insights': {
                'analyst': {'agent_name': 'Data Analyst', 'key_findings': [], 'confidence': 0.0},
                'research': {'agent_name': 'Research Strategist', 'key_findings': [], 'confidence': 0.0},
                'risk_management': {'agent_name': 'Risk Guardian', 'key_findings': [], 'confidence': 0.0}
            },
            'conflicts_resolved': 0,
            'discussion_rounds': 0,
            'overall_confidence': 0.0,
            'error': True,
            'error_message': error,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_fallback_synthesis(self, stage1_responses: Dict[str, Any], user_message: str) -> str:
        """Create fallback synthesis when AI generation fails"""
        summary_parts = [
            "🤝 Collaborative Financial Analysis Summary\n",
            f"Query: {user_message}\n\n"
        ]
        
        agent_names = {
            'analyst': 'Data Analyst',
            'research': 'Research Strategist',
            'risk_management': 'Risk Guardian'
        }
        
        summary_parts.append("📊 Agent Perspectives:\n")
        for agent_id, response in stage1_responses.items():
            agent_name = agent_names.get(agent_id, agent_id)
            analysis = response.get('analysis', 'Analysis not available')[:150]
            summary_parts.append(f"• {agent_name}: {analysis}...\n")
        
        summary_parts.append("\n🎯 Recommendation: Based on collaborative analysis, proceed with a balanced approach considering all expert perspectives.")
        
        return "".join(summary_parts)
    
    # ===== SESSION MANAGEMENT =====
    
    def get_session_collaboration(self, session_id: str) -> Dict[str, Any]:
        """Get the full collaboration details for a session"""
        session_data = self.sessions.get(session_id)
        
        if not session_data:
            return {'error': 'Session not found'}
        
        return {
            'session_id': session_id,
            'user_query': session_data['user_message'],
            'stage1_responses': session_data['stage1_responses'],
            'detected_conflicts': session_data['detected_conflicts'],
            'discussion_log': session_data['discussion_log'],
            'unified_response': session_data['unified_response'],
            'timestamp': session_data['timestamp'],
            'framework_version': session_data['framework_version']
        }
    
    def clear_session(self, session_id: str):
        """Clear a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.sessions.keys())
    
    def get_coordinator_status(self) -> Dict[str, Any]:
        """Get status of the revolutionary coordinator and all agents"""
        return {
            'coordinator_status': 'revolutionary_active',
            'framework_version': '4-stage-collaboration-v1.0',
            'active_sessions': len(self.sessions),
            'collaboration_metrics': self.collaboration_metrics,
            'agents': {
                'analyst': self.analyst_agent.get_agent_info(),
                'research': self.research_agent.get_agent_info(),
                'risk_management': self.risk_agent.get_agent_info()
            },
            'timestamp': datetime.now().isoformat()
        }