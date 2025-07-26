"""
Local LLM Client for connecting to LM Studio or compatible local LLM servers
Supports OpenAI-compatible API endpoints
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class LocalLLMConfig:
    """Configuration for local LLM server"""
    base_url: str = "http://localhost:1234"
    model: str = "gemma-3n-e2b-it-text"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30

class LocalLLMClient:
    """Client for interacting with local LLM server (LM Studio compatible)"""
    
    def __init__(self, config: Optional[LocalLLMConfig] = None):
        self.config = config or LocalLLMConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info(f"🤖 Local LLM Client initialized - Server: {self.config.base_url}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def connect(self):
        """Initialize HTTP session and test connection"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        
        # Test connection
        connected = await self.test_connection()
        if connected:
            logger.info("✅ Successfully connected to local LLM server")
        else:
            logger.warning("⚠️ Could not connect to local LLM server")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def test_connection(self) -> bool:
        """Test if local LLM server is available and auto-detect model"""
        try:
            if not self.session:
                await self.connect()
            
            async with self.session.get(f"{self.config.base_url}/v1/models") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"📋 Available models: {data}")
                    
                    # Auto-detect the correct model
                    if 'data' in data and data['data']:
                        available_models = [model['id'] for model in data['data']]
                        
                        # Check if our configured model exists
                        if self.config.model not in available_models:
                            # Use the first available model that looks like a text generation model
                            for model in available_models:
                                if any(keyword in model.lower() for keyword in ['gemma', 'llama', 'qwen', 'phi', 'smol']):
                                    if 'embed' not in model.lower():  # Skip embedding models
                                        logger.info(f"🔄 Auto-selected model: {model} (configured: {self.config.model})")
                                        self.config.model = model
                                        break
                    
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to local LLM: {e}")
            return False
    
    async def generate_completion(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        Generate completion using local LLM with OpenAI-compatible API
        """
        try:
            if not self.session:
                await self.connect()
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Prepare request payload
            payload = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "stream": False
            }
            
            logger.info(f"🔄 Sending request to local LLM (prompt length: {len(prompt)} chars)")
            start_time = time.time()
            
            async with self.session.post(
                f"{self.config.base_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    elapsed = time.time() - start_time
                    
                    # Extract response
                    content = result['choices'][0]['message']['content']
                    tokens_used = result.get('usage', {})
                    
                    logger.info(f"✅ Local LLM response received in {elapsed:.2f}s")
                    logger.info(f"📊 Tokens - Prompt: {tokens_used.get('prompt_tokens', 'N/A')}, "
                              f"Completion: {tokens_used.get('completion_tokens', 'N/A')}")
                    
                    return {
                        "success": True,
                        "content": content,
                        "model": result.get('model', self.config.model),
                        "usage": tokens_used,
                        "response_time": elapsed
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Local LLM error: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "error": f"Server error: {response.status}",
                        "details": error_text
                    }
                    
        except asyncio.TimeoutError:
            logger.error("⏱️ Local LLM request timed out")
            return {
                "success": False,
                "error": "Request timed out"
            }
        except Exception as e:
            logger.error(f"❌ Local LLM request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_financial_insights(self, compressed_data: str, user_query: str) -> str:
        """
        Generate comprehensive financial insights using detailed data
        Provides in-depth analysis for Indian investors
        """
        system_prompt = """You are an expert financial advisor specializing in Indian personal finance. You analyze portfolios and provide comprehensive, actionable advice.

IMPORTANT GUIDELINES:
- All amounts are in Indian Rupees (₹). NEVER use dollar symbols ($)
- Provide detailed analysis with specific recommendations
- Focus on Indian financial context (tax, regulations, investment options)
- Format your response in clear markdown with sections and bullet points
- Include specific action items with priority levels
- Consider Indian investment vehicles (SIP, ELSS, PPF, etc.)"""
        
        prompt = f"""{compressed_data}

User Question: {user_query}

Provide a comprehensive financial analysis in markdown format. Structure your response with:

## Portfolio Assessment
## Key Insights  
## Recommendations
## Action Plan

Remember: All amounts are in Indian Rupees (₹). Provide specific, actionable advice for Indian investors."""
        
        result = await self.generate_completion(prompt, system_prompt)
        
        if result["success"]:
            # Post-process to ensure no dollar signs slip through
            content = result["content"]
            # Replace any remaining dollar signs with rupee symbols
            content = content.replace('$', '₹')
            # Fix common dollar references
            content = content.replace('USD', 'INR')
            content = content.replace('dollars', 'rupees')
            content = content.replace('Dollar', 'Rupee')
            
            return content
        else:
            return f"Unable to generate insights: {result.get('error', 'Unknown error')}"
    
    async def analyze_portfolio_health(self, compressed_data: str) -> Dict[str, Any]:
        """
        Analyze portfolio health using local LLM
        Returns structured analysis
        """
        system_prompt = "You are a financial analyst. Analyze the portfolio data and return a JSON response with health_score (0-100), strengths (list), concerns (list), and recommendations (list). Keep each item brief."
        
        prompt = f"""Analyze this financial data and return JSON:
{compressed_data}

Format: {{"health_score": number, "strengths": [], "concerns": [], "recommendations": []}}"""
        
        result = await self.generate_completion(prompt, system_prompt)
        
        if result["success"]:
            try:
                # Try to parse JSON response
                content = result["content"]
                # Extract JSON if wrapped in markdown
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                analysis = json.loads(content)
                return {
                    "success": True,
                    "analysis": analysis,
                    "response_time": result.get("response_time", 0)
                }
            except json.JSONDecodeError:
                # Fallback to text response
                return {
                    "success": True,
                    "analysis": {
                        "health_score": 70,
                        "text_analysis": result["content"]
                    }
                }
        else:
            return {
                "success": False,
                "error": result.get("error", "Analysis failed")
            }

# Global client instance
_local_llm_client: Optional[LocalLLMClient] = None

async def get_local_llm_client() -> LocalLLMClient:
    """Get or create global local LLM client"""
    global _local_llm_client
    if _local_llm_client is None:
        _local_llm_client = LocalLLMClient()
        await _local_llm_client.connect()
    return _local_llm_client

async def cleanup_local_llm_client():
    """Cleanup global client"""
    global _local_llm_client
    if _local_llm_client:
        await _local_llm_client.close()
        _local_llm_client = None