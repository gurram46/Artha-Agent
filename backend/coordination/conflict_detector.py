"""
Conflict Detection and Resolution System - Stage 2 of Collaboration Framework
Revolutionary AI-powered conflict detection between financial agents
Implements intelligent disagreement detection and resolution coordination
"""

import json
import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime


class ConflictDetector:
    """
    AI-Powered Conflict Detection System
    
    Detects conflicts between agent recommendations and facilitates resolution:
    - Budget disagreements (₹ amount differences)
    - Risk tolerance conflicts (conservative vs aggressive)
    - Timing disagreements (immediate vs delayed)
    - Strategy conflicts (debt vs investment priority)
    """
    
    def __init__(self):
        self.logger = logging.getLogger("conflict_detector")
        
        # Conflict detection thresholds (more lenient to reduce false positives)
        self.BUDGET_THRESHOLD = 0.8  # 80% difference in budget recommendations
        self.CONFIDENCE_THRESHOLD = 0.2  # 20% difference in confidence levels
        self.TIMING_CONFLICT_KEYWORDS = {
            'immediate': ['now', 'immediately', 'urgent', 'asap', 'right away'],
            'short_term': ['soon', 'within weeks', 'short term', '1-3 months'],
            'long_term': ['later', 'long term', 'future', 'eventually', '6+ months']
        }
        
        # Risk tolerance keywords
        self.RISK_KEYWORDS = {
            'conservative': ['safe', 'conservative', 'stable', 'secure', 'cautious', 'protective'],
            'moderate': ['moderate', 'balanced', 'reasonable', 'measured'],
            'aggressive': ['aggressive', 'risky', 'high-growth', 'speculative', 'bold']
        }
    
    def detect_conflicts(self, agent_responses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main conflict detection method
        Analyzes agent responses and identifies conflicts requiring resolution
        """
        conflicts = []
        
        try:
            # Extract analysis data from responses
            analyst_data = self._extract_agent_data(agent_responses.get('analyst', {}))
            research_data = self._extract_agent_data(agent_responses.get('research', {})) 
            risk_data = self._extract_agent_data(agent_responses.get('risk_management', {}))
            
            # Detect budget conflicts
            budget_conflicts = self._detect_budget_conflicts(analyst_data, research_data, risk_data)
            conflicts.extend(budget_conflicts)
            
            # Detect risk tolerance conflicts
            risk_conflicts = self._detect_risk_tolerance_conflicts(analyst_data, research_data, risk_data)
            conflicts.extend(risk_conflicts)
            
            # Detect timing conflicts
            timing_conflicts = self._detect_timing_conflicts(analyst_data, research_data, risk_data)
            conflicts.extend(timing_conflicts)
            
            # Detect strategy priority conflicts
            strategy_conflicts = self._detect_strategy_conflicts(analyst_data, research_data, risk_data)
            conflicts.extend(strategy_conflicts)
            
            # Detect confidence disagreements
            confidence_conflicts = self._detect_confidence_conflicts(analyst_data, research_data, risk_data)
            conflicts.extend(confidence_conflicts)
            
            # Rank conflicts by severity
            conflicts = self._rank_conflicts_by_severity(conflicts)
            
            self.logger.info(f"Detected {len(conflicts)} conflicts requiring resolution")
            
        except Exception as e:
            self.logger.error(f"Error detecting conflicts: {str(e)}")
            conflicts.append({
                'type': 'system_error',
                'severity': 'high',
                'description': 'Error in conflict detection system',
                'agents_involved': ['system'],
                'resolution_required': True
            })
        
        return conflicts
    
    def _extract_agent_data(self, agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant data from agent response for conflict detection"""
        analysis_text = agent_response.get('analysis', '').lower()
        
        return {
            'agent_id': agent_response.get('agent', 'unknown'),
            'agent_name': agent_response.get('agent_name', 'Unknown Agent'),
            'analysis': analysis_text,
            'confidence': agent_response.get('confidence', 0.5),
            'key_insights': agent_response.get('key_insights', []),
            'financial_metrics': agent_response.get('financial_metrics', {}),
            'recommended_budget': self._extract_budget_recommendation(analysis_text),
            'risk_tolerance': self._extract_risk_tolerance(analysis_text),
            'timing_preference': self._extract_timing_preference(analysis_text),
            'strategy_priority': self._extract_strategy_priority(analysis_text)
        }
    
    def _extract_budget_recommendation(self, analysis_text: str) -> Optional[float]:
        """Extract budget/amount recommendations from analysis text"""
        # Look for ₹ amounts in the text with proper unit handling
        amount_patterns = [
            r'₹([\d,]+(?:\.\d+)?)\s*lakh',     # ₹X lakh format
            r'₹([\d,]+(?:\.\d+)?)\s*crore',    # ₹X crore format  
            r'₹([\d,]+(?:\.\d+)?)\s*K',        # ₹X K format
            r'₹([\d,]+(?:\.\d+)?)',            # Regular ₹X format
            r'budget.*?₹([\d,]+(?:\.\d+)?)',   # Context-based
            r'spend.*?₹([\d,]+(?:\.\d+)?)',
            r'afford.*?₹([\d,]+(?:\.\d+)?)'
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.finditer(pattern, analysis_text.lower())
            for match in matches:
                try:
                    # Clean and convert amount
                    clean_amount = match.group(1).replace(',', '')
                    amount = float(clean_amount)
                    
                    # Convert based on specific pattern context
                    if 'lakh' in match.group(0):
                        amount *= 100000  # Convert lakhs to rupees
                    elif 'crore' in match.group(0):
                        amount *= 10000000  # Convert crores to rupees
                    elif 'k' in match.group(0):
                        amount *= 1000  # Convert thousands to rupees
                    # else: amount is already in rupees
                    
                    # Only include reasonable amounts (not tiny decimals that get multiplied)
                    if amount >= 10000 and amount <= 10000000:  # Between ₹10K and ₹1 crore (more realistic)
                        amounts.append(amount)
                        
                except (ValueError, AttributeError):
                    continue
        
        # Return the most relevant amount (prefer budget-related contexts)
        if amounts:
            # If multiple amounts, prefer the median to avoid outliers
            amounts.sort()
            return amounts[len(amounts)//2]
        return None
    
    def _extract_risk_tolerance(self, analysis_text: str) -> str:
        """Extract risk tolerance from analysis text"""
        for risk_level, keywords in self.RISK_KEYWORDS.items():
            if any(keyword in analysis_text for keyword in keywords):
                return risk_level
        
        return 'unknown'
    
    def _extract_timing_preference(self, analysis_text: str) -> str:
        """Extract timing preference from analysis text"""
        for timing, keywords in self.TIMING_CONFLICT_KEYWORDS.items():
            if any(keyword in analysis_text for keyword in keywords):
                return timing
        
        return 'unknown'
    
    def _extract_strategy_priority(self, analysis_text: str) -> str:
        """Extract strategy priority from analysis text"""
        debt_keywords = ['debt', 'loan', 'borrow', 'emi', 'interest', 'repay']
        investment_keywords = ['invest', 'portfolio', 'mutual fund', 'equity', 'returns']
        savings_keywords = ['save', 'emergency fund', 'cash', 'liquidity']
        
        debt_score = sum(1 for keyword in debt_keywords if keyword in analysis_text)
        investment_score = sum(1 for keyword in investment_keywords if keyword in analysis_text)
        savings_score = sum(1 for keyword in savings_keywords if keyword in analysis_text)
        
        if debt_score > investment_score and debt_score > savings_score:
            return 'debt_focus'
        elif investment_score > debt_score and investment_score > savings_score:
            return 'investment_focus'
        elif savings_score > debt_score and savings_score > investment_score:
            return 'savings_focus'
        else:
            return 'balanced'
    
    def _detect_budget_conflicts(self, analyst_data: Dict, research_data: Dict, risk_data: Dict) -> List[Dict[str, Any]]:
        """Detect conflicts in budget recommendations"""
        conflicts = []
        
        budgets = {
            'analyst': analyst_data.get('recommended_budget'),
            'research': research_data.get('recommended_budget'),
            'risk_management': risk_data.get('recommended_budget')
        }
        
        # Filter out None values
        valid_budgets = {k: v for k, v in budgets.items() if v is not None}
        
        if len(valid_budgets) >= 2:
            budget_values = list(valid_budgets.values())
            min_budget = min(budget_values)
            max_budget = max(budget_values)
            
            # Check if there's significant disagreement
            if min_budget > 0 and (max_budget - min_budget) / min_budget > self.BUDGET_THRESHOLD:
                conflicts.append({
                    'type': 'budget_disagreement',
                    'severity': 'high',
                    'description': f'Significant budget disagreement: ₹{min_budget:,.0f} to ₹{max_budget:,.0f}',
                    'agents_involved': list(valid_budgets.keys()),
                    'details': valid_budgets,
                    'resolution_required': True,
                    'conflict_score': (max_budget - min_budget) / min_budget
                })
        
        return conflicts
    
    def _detect_risk_tolerance_conflicts(self, analyst_data: Dict, research_data: Dict, risk_data: Dict) -> List[Dict[str, Any]]:
        """Detect conflicts in risk tolerance recommendations"""
        conflicts = []
        
        risk_tolerances = {
            'analyst': analyst_data.get('risk_tolerance'),
            'research': research_data.get('risk_tolerance'),
            'risk_management': risk_data.get('risk_tolerance')
        }
        
        # Check for opposing risk views
        tolerance_levels = {'conservative': 1, 'moderate': 2, 'aggressive': 3}
        agent_levels = {}
        
        for agent, tolerance in risk_tolerances.items():
            if tolerance in tolerance_levels:
                agent_levels[agent] = tolerance_levels[tolerance]
        
        if len(agent_levels) >= 2:
            levels = list(agent_levels.values())
            if max(levels) - min(levels) >= 2:  # Conservative vs Aggressive
                conflicts.append({
                    'type': 'risk_tolerance_conflict',
                    'severity': 'medium',
                    'description': 'Conflicting risk tolerance recommendations',
                    'agents_involved': list(agent_levels.keys()),
                    'details': {agent: tolerance for agent, tolerance in risk_tolerances.items() if tolerance != 'unknown'},
                    'resolution_required': True,
                    'conflict_score': max(levels) - min(levels)
                })
        
        return conflicts
    
    def _detect_timing_conflicts(self, analyst_data: Dict, research_data: Dict, risk_data: Dict) -> List[Dict[str, Any]]:
        """Detect conflicts in timing recommendations"""
        conflicts = []
        
        timing_preferences = {
            'analyst': analyst_data.get('timing_preference'),
            'research': research_data.get('timing_preference'),
            'risk_management': risk_data.get('timing_preference')
        }
        
        # Check for timing conflicts
        timing_order = {'immediate': 1, 'short_term': 2, 'long_term': 3}
        agent_timings = {}
        
        for agent, timing in timing_preferences.items():
            if timing in timing_order:
                agent_timings[agent] = timing_order[timing]
        
        if len(agent_timings) >= 2:
            timings = list(agent_timings.values())
            if max(timings) - min(timings) >= 2:  # Immediate vs Long-term
                conflicts.append({
                    'type': 'timing_conflict',
                    'severity': 'medium',
                    'description': 'Conflicting timing recommendations',
                    'agents_involved': list(agent_timings.keys()),
                    'details': {agent: timing for agent, timing in timing_preferences.items() if timing != 'unknown'},
                    'resolution_required': True,
                    'conflict_score': max(timings) - min(timings)
                })
        
        return conflicts
    
    def _detect_strategy_conflicts(self, analyst_data: Dict, research_data: Dict, risk_data: Dict) -> List[Dict[str, Any]]:
        """Detect conflicts in strategic priorities"""
        conflicts = []
        
        strategies = {
            'analyst': analyst_data.get('strategy_priority'),
            'research': research_data.get('strategy_priority'),
            'risk_management': risk_data.get('strategy_priority')
        }
        
        # Check for fundamental strategy disagreements
        unique_strategies = set(strategy for strategy in strategies.values() if strategy != 'unknown' and strategy != 'balanced')
        
        if len(unique_strategies) >= 2:
            # Check for conflicting priorities (e.g., debt focus vs investment focus)
            if 'debt_focus' in unique_strategies and 'investment_focus' in unique_strategies:
                conflicts.append({
                    'type': 'strategy_priority_conflict',
                    'severity': 'high',
                    'description': 'Fundamental disagreement on debt vs investment priority',
                    'agents_involved': [agent for agent, strategy in strategies.items() if strategy in unique_strategies],
                    'details': {agent: strategy for agent, strategy in strategies.items() if strategy != 'unknown'},
                    'resolution_required': True,
                    'conflict_score': len(unique_strategies)
                })
        
        return conflicts
    
    def _detect_confidence_conflicts(self, analyst_data: Dict, research_data: Dict, risk_data: Dict) -> List[Dict[str, Any]]:
        """Detect significant confidence disagreements"""
        conflicts = []
        
        confidences = {
            'analyst': analyst_data.get('confidence', 0.5),
            'research': research_data.get('confidence', 0.5),
            'risk_management': risk_data.get('confidence', 0.5)
        }
        
        confidence_values = list(confidences.values())
        if max(confidence_values) - min(confidence_values) > self.CONFIDENCE_THRESHOLD:
            conflicts.append({
                'type': 'confidence_disagreement',
                'severity': 'low',
                'description': 'Significant variance in agent confidence levels',
                'agents_involved': list(confidences.keys()),
                'details': confidences,
                'resolution_required': False,  # Low priority
                'conflict_score': max(confidence_values) - min(confidence_values)
            })
        
        return conflicts
    
    def _rank_conflicts_by_severity(self, conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank conflicts by severity and conflict score"""
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        
        return sorted(conflicts, key=lambda x: (
            severity_order.get(x.get('severity', 'low'), 1),
            x.get('conflict_score', 0)
        ), reverse=True)


class DiscussionSimulator:
    """
    Discussion Simulation System - Stage 3 Coordinator
    
    Facilitates agent discussions to resolve detected conflicts:
    - Generates discussion rounds
    - Coordinates agent collaboration
    - Tracks consensus progress
    - Manages compromise attempts
    """
    
    def __init__(self):
        self.logger = logging.getLogger("discussion_simulator")
        self.max_discussion_rounds = 3
    
    def simulate_discussion(self, agent_responses: Dict[str, Any], conflicts: List[Dict[str, Any]], 
                          original_query: str) -> List[Dict[str, Any]]:
        """
        Simulate agent discussion to resolve conflicts
        Returns discussion log with consensus results
        """
        discussion_log = []
        
        if not conflicts:
            # No conflicts - create simple consensus
            discussion_log.append({
                'round': 0,
                'status': 'no_conflicts',
                'consensus_reached': True,
                'message': 'All agents in agreement - no discussion required'
            })
            return discussion_log
        
        try:
            for conflict in conflicts:
                if not conflict.get('resolution_required', False):
                    continue
                
                conflict_discussion = self._facilitate_conflict_discussion(
                    conflict, agent_responses, original_query
                )
                discussion_log.extend(conflict_discussion)
        
        except Exception as e:
            self.logger.error(f"Error simulating discussion: {str(e)}")
            discussion_log.append({
                'round': 0,
                'status': 'error',
                'message': f'Discussion simulation error: {str(e)}',
                'consensus_reached': False
            })
        
        return discussion_log
    
    def _facilitate_conflict_discussion(self, conflict: Dict[str, Any], agent_responses: Dict[str, Any], 
                                      query: str) -> List[Dict[str, Any]]:
        """Facilitate discussion for a specific conflict"""
        discussion_rounds = []
        agents_involved = conflict.get('agents_involved', [])
        
        # Round 1: Present positions
        round_1 = {
            'round': 1,
            'conflict_type': conflict.get('type'),
            'conflict_description': conflict.get('description'),
            'positions': {},
            'status': 'position_presentation'
        }
        
        for agent_id in agents_involved:
            if agent_id in agent_responses:
                agent_response = agent_responses[agent_id]
                round_1['positions'][agent_id] = {
                    'agent_name': agent_response.get('agent_name', agent_id),
                    'position': self._extract_agent_position(agent_response, conflict),
                    'confidence': agent_response.get('confidence', 0.5)
                }
        
        discussion_rounds.append(round_1)
        
        # Round 2: Simulate collaboration attempts
        if len(agents_involved) >= 2:
            round_2 = self._simulate_collaboration_round(conflict, agent_responses, query)
            discussion_rounds.append(round_2)
        
        # Round 3: Attempt consensus
        round_3 = self._attempt_consensus(conflict, agent_responses, discussion_rounds)
        discussion_rounds.append(round_3)
        
        return discussion_rounds
    
    def _extract_agent_position(self, agent_response: Dict[str, Any], conflict: Dict[str, Any]) -> str:
        """Extract agent's position on the specific conflict"""
        conflict_type = conflict.get('type', '')
        analysis = agent_response.get('analysis', '')
        
        if 'budget' in conflict_type:
            # Extract budget-related stance
            budget_keywords = ['budget', 'afford', 'spend', 'cost', '₹']
            relevant_sentences = [sent for sent in analysis.split('.') 
                                if any(keyword in sent.lower() for keyword in budget_keywords)]
            return '. '.join(relevant_sentences[:2]) if relevant_sentences else "Position on budget considerations"
        
        elif 'risk' in conflict_type:
            # Extract risk-related stance
            risk_keywords = ['risk', 'safe', 'conservative', 'aggressive', 'caution']
            relevant_sentences = [sent for sent in analysis.split('.') 
                                if any(keyword in sent.lower() for keyword in risk_keywords)]
            return '. '.join(relevant_sentences[:2]) if relevant_sentences else "Position on risk management"
        
        elif 'timing' in conflict_type:
            # Extract timing-related stance
            timing_keywords = ['immediate', 'now', 'soon', 'later', 'timing', 'when']
            relevant_sentences = [sent for sent in analysis.split('.') 
                                if any(keyword in sent.lower() for keyword in timing_keywords)]
            return '. '.join(relevant_sentences[:2]) if relevant_sentences else "Position on timing considerations"
        
        else:
            # General position
            return analysis[:200] + "..." if len(analysis) > 200 else analysis
    
    def _simulate_collaboration_round(self, conflict: Dict[str, Any], agent_responses: Dict[str, Any], 
                                    query: str) -> Dict[str, Any]:
        """Simulate collaborative discussion round"""
        return {
            'round': 2,
            'conflict_type': conflict.get('type'),
            'status': 'collaborative_discussion',
            'discussion_summary': f"Agents discussing {conflict.get('description', 'disagreement')}",
            'collaboration_attempts': len(conflict.get('agents_involved', [])),
            'progress': 'agents_exchanging_perspectives'
        }
    
    def _attempt_consensus(self, conflict: Dict[str, Any], agent_responses: Dict[str, Any], 
                         discussion_rounds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Attempt to reach consensus on the conflict"""
        conflict_type = conflict.get('type', '')
        severity = conflict.get('severity', 'medium')
        
        # Simulate consensus based on conflict type and severity
        if severity == 'high':
            consensus_reached = len(discussion_rounds) >= 2  # Require more discussion for high severity
        else:
            consensus_reached = True  # Assume consensus possible for lower severity
        
        if consensus_reached:
            compromise = self._generate_compromise_solution(conflict, agent_responses)
            return {
                'round': 3,
                'conflict_type': conflict_type,
                'status': 'consensus_reached',
                'consensus_reached': True,
                'compromise_solution': compromise,
                'resolution': f"Agents reached agreement on {conflict.get('description', 'the issue')}"
            }
        else:
            return {
                'round': 3,
                'conflict_type': conflict_type,
                'status': 'no_consensus',
                'consensus_reached': False,
                'fallback_action': 'default_to_most_conservative_approach',
                'resolution': f"No consensus reached - applying protective approach for {conflict.get('description', 'the issue')}"
            }
    
    def _generate_compromise_solution(self, conflict: Dict[str, Any], agent_responses: Dict[str, Any]) -> str:
        """Generate a compromise solution for the conflict"""
        conflict_type = conflict.get('type', '')
        
        if 'budget' in conflict_type:
            # For budget conflicts, suggest middle-ground approach
            return "Recommend moderate budget with phased implementation to balance growth and safety"
        
        elif 'risk' in conflict_type:
            # For risk conflicts, balance conservative and aggressive approaches
            return "Adopt balanced risk approach with protective measures for growth strategies"
        
        elif 'timing' in conflict_type:
            # For timing conflicts, suggest phased approach
            return "Implement gradual approach with immediate protective measures and long-term growth planning"
        
        elif 'strategy' in conflict_type:
            # For strategy conflicts, suggest hybrid approach
            return "Pursue hybrid strategy addressing both debt management and strategic investments"
        
        else:
            return "Adopt balanced approach considering all agent perspectives with appropriate safeguards"