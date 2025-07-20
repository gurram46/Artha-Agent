"""
Gemini AI Client for Agent Interactions
Handles all communication with Google's Gemini API
"""

import os
import json
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from datetime import datetime


class GeminiClient:
    """Client for interacting with Google's Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model (latest fastest model)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generation config optimized for speed
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.3,  # Lower for faster, more focused responses
            top_p=0.6,
            top_k=20,
            max_output_tokens=512,  # Reduced for faster responses
        )
    
    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response using Gemini"""
        try:
            # Add context to prompt if provided
            full_prompt = self._build_prompt_with_context(prompt, context)
            
            # Truncate prompt if too long to avoid timeouts - more aggressive
            if len(full_prompt) > 4000:
                full_prompt = full_prompt[:4000] + "\n\nPlease provide a concise analysis based on the available data."
            
            # Generate response with timeout handling
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            
            # Handle both simple and complex responses
            try:
                return response.text if response.text else self._extract_response_content(response)
            except Exception:
                return self._extract_response_content(response)
            
        except Exception as e:
            print(f"Error generating Gemini response: {e}")
            return f"I encountered an error while processing your request: {str(e)[:100]}. Please try again."
    
    def _build_prompt_with_context(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build a comprehensive prompt with context"""
        if not context:
            return prompt
        
        context_str = ""
        
        # Add financial data context (simplified)
        if 'financial_data' in context:
            financial_data = context['financial_data']
            context_str += "\\n\\nUser's Financial Summary:\\n"
            
            # Add key metrics only to avoid token limits
            if 'net_worth' in financial_data and financial_data['net_worth']:
                net_worth = financial_data['net_worth'].get('netWorthResponse', {})
                if net_worth.get('totalNetWorthValue'):
                    context_str += f"Net Worth: ₹{net_worth['totalNetWorthValue'].get('units', 0)}\\n"
            
            if 'credit_report' in financial_data and financial_data['credit_report']:
                credit_reports = financial_data['credit_report'].get('creditReports', [])
                if credit_reports:
                    score = credit_reports[0].get('creditReportData', {}).get('score', {}).get('bureauScore', 'N/A')
                    context_str += f"Credit Score: {score}\\n"
        
        # Add agent context
        if 'agent_context' in context:
            context_str += f"\\n\\nAgent Role: {context['agent_context']}"
        
        # Add previous agent insights (summarized)
        if 'previous_insights' in context:
            context_str += "\\n\\nPrevious Agent Insights:\\n"
            for insight in context['previous_insights'][:2]:  # Limit to 2 insights
                context_str += f"- {insight['agent']}: {insight['summary'][:100]}...\\n"
        
        return f"{prompt}{context_str}"
    
    def _extract_response_content(self, response) -> str:
        """Extract content from complex Gemini responses"""
        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        # Extract text from all parts
                        text_parts = []
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                        return "".join(text_parts) if text_parts else "No text content found"
            
            # Fallback
            return str(response) if response else "Empty response"
            
        except Exception as e:
            return f"Error extracting response: {str(e)[:100]}"
    
    def analyze_financial_data(self, agent_type: str, user_message: str, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial data based on agent type"""
        
        prompts = {
            'analyst': self._get_analyst_prompt(),
            'research': self._get_research_prompt(),
            'risk_management': self._get_risk_management_prompt()
        }
        
        base_prompt = prompts.get(agent_type, prompts['analyst'])
        
        full_prompt = f"""
{base_prompt}

User Query: {user_message}

Please analyze the provided financial data and respond in JSON format with the following structure:
{{
    "agent": "{agent_type}",
    "analysis": "Your detailed analysis here",
    "key_insights": ["insight1", "insight2", "insight3"],
    "recommendations": ["recommendation1", "recommendation2"],
    "confidence": 0.85,
    "risk_level": "medium",
    "timestamp": "{datetime.now().isoformat()}"
}}

Make sure your response is valid JSON and follows the exact structure above.
"""
        
        context = {
            'financial_data': financial_data,
            'agent_context': f"Acting as {agent_type} agent"
        }
        
        response_text = self.generate_response(full_prompt, context)
        
        # Try to parse JSON response
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "agent": agent_type,
                "analysis": response_text,
                "key_insights": ["Analysis provided in text format"],
                "recommendations": ["Please review the detailed analysis"],
                "confidence": 0.7,
                "risk_level": "unknown",
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_collaboration_message(self, agent_type: str, insights: List[Dict[str, Any]], user_query: str) -> Dict[str, Any]:
        """Generate a message for agent collaboration"""
        
        prompt = f"""
You are a {agent_type} agent participating in a collaborative financial advisory discussion.

User Query: {user_query}

Other agents have provided these insights:
{json.dumps(insights, indent=2)}

Based on your expertise as a {agent_type} agent and the insights from other agents, provide your collaborative input in JSON format:
{{
    "agent": "{agent_type}",
    "collaboration_message": "Your message to other agents",
    "additional_insights": ["insight1", "insight2"],
    "agreements": ["Points you agree with from other agents"],
    "concerns": ["Any concerns or risks you want to highlight"],
    "timestamp": "{datetime.now().isoformat()}"
}}

Focus on how your expertise complements the other agents' insights and what unique perspective you bring to the discussion.
"""
        
        response_text = self.generate_response(prompt)
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "agent": agent_type,
                "collaboration_message": response_text,
                "additional_insights": [],
                "agreements": [],
                "concerns": [],
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_final_summary(self, user_query: str, all_agent_insights: List[Dict[str, Any]]) -> str:
        """Generate dynamic agent collaboration with real discussions and conflict resolution"""
        
        # First, detect conflicts between agent recommendations
        conflict_detection_prompt = f"""
Analyze these 3 agent responses for CONFLICTS and DISAGREEMENTS:

User Question: "{user_query}"

💰 Data Analyst: {all_agent_insights[0].get('analysis', '')}
📊 Research Agent: {all_agent_insights[1].get('analysis', '')}  
⚠️ Risk Manager: {all_agent_insights[2].get('analysis', '')}

CONFLICT ANALYSIS:
1. Do the agents agree or disagree? 
2. What are the specific disagreements?
3. What's the main tension/conflict?
4. Rate conflict level: LOW/MEDIUM/HIGH

Return in this format:
CONFLICT_LEVEL: [LOW/MEDIUM/HIGH]
MAIN_DISAGREEMENT: [describe the core conflict]
AGENT_POSITIONS: [summarize each agent's stance]
"""
        
        conflict_analysis = self.generate_response(conflict_detection_prompt)
        
        # Generate collaborative discussion based on conflict level
        collaboration_prompt = f"""
Create a SPECTACULAR agent collaboration showing REAL AI teamwork for this hackathon demo:

User Question: "{user_query}"

Agent Analysis:
💰 Data Analyst: {all_agent_insights[0].get('analysis', '')}
📊 Research Agent: {all_agent_insights[1].get('analysis', '')}  
⚠️ Risk Manager: {all_agent_insights[2].get('analysis', '')}

Conflict Assessment: {conflict_analysis}

Create a WINNING collaboration format:

🎯 [CATCHY TITLE answering their question]

🚨 [Include ONLY if urgent financial danger detected]

🤖 AGENT COLLABORATION WARFARE:

💰 Analyst Opens: "[Their initial position with numbers]"
📊 Research Responds: "[Strategic counter/agreement]"
⚠️ Risk Challenges: "[Risk concern/validation]"

🔥 HEATED DISCUSSION:
[Create 2-3 rounds of back-and-forth discussion where agents challenge each other's positions, present counter-arguments, and gradually work toward a solution. Show the tension, the "aha!" moments, and the collaborative problem-solving process.]

🤝 BREAKTHROUGH CONSENSUS:
[How agents reached agreement - the "AHA!" moment]

🏆 UNIFIED AI DECISION: [Final collaborative answer]

⚡ COLLABORATIVE MASTERPLAN:

🔥 IMMEDIATE (Week 1):
• ₹[amount] → [action based on consensus]
  💡 [Why all agents agree this works]

💪 STRATEGIC PHASE (1-3 months):
• ₹[amount] → [coordinated strategy]
  💡 [Expected outcome from teamwork]

🚀 GROWTH ACCELERATION (3-12 months):
• ₹[amount] → [long-term vision]
  💡 [Projected results]

📊 TEAM VICTORY METRICS (12 months):
✅ [Specific benefit]: ₹[amount]
✅ [Another benefit]: ₹[amount]
✅ [Risk eliminated]: [description]
🏆 Total Impact: ₹[total]+ value created

🎯 TEAM CONFIDENCE: [90-95]% ✅

Make it feel like watching AI agents ACTUALLY collaborating and problem-solving together!
"""
        
        response = self.generate_response(collaboration_prompt)
        
        # Ensure we return a string, not an object
        if hasattr(response, 'text'):
            return response.text
        elif isinstance(response, str):
            return response
        else:
            return str(response)
    
    def _get_analyst_prompt(self) -> str:
        """Get the base prompt for the analyst agent"""
        return """
You are a Data Analyst Agent specializing in financial data analysis. Your role is to:
- Analyze financial statements, credit reports, and portfolio data
- Identify trends and patterns in financial behavior
- Provide data-driven insights about financial health
- Calculate key financial ratios and metrics
- Assess current financial position objectively

Focus on quantitative analysis and factual assessment of the user's financial situation.
"""
    
    def _get_research_prompt(self) -> str:
        """Get the base prompt for the research agent"""
        return """
You are a Research Agent specializing in market research and investment analysis. Your role is to:
- Research market trends and investment opportunities
- Analyze sector performance and economic indicators
- Provide insights about investment strategies and market conditions
- Evaluate investment options and their potential
- Offer strategic advice based on market research

Focus on market intelligence and strategic investment research.
"""
    
    def _get_risk_management_prompt(self) -> str:
        """Get the base prompt for the risk management agent"""
        return """
You are a Risk Management Agent specializing in financial risk assessment. Your role is to:
- Identify potential financial risks and vulnerabilities
- Assess risk tolerance and capacity
- Evaluate the risk-return profile of investments
- Provide warnings about high-risk scenarios
- Recommend risk mitigation strategies

Focus on protecting the user from financial risks and ensuring sustainable financial decisions.
"""