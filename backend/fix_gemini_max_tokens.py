#!/usr/bin/env python3
"""
Fix for Gemini 2.5 Flash MAX_TOKENS bug
Based on research: Setting max_output_tokens causes empty responses
Solution: Remove max_output_tokens and use alternative approaches
"""

import asyncio
import logging
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class GeminiQueryGenerator:
    """Fixed implementation for Gemini query generation"""
    
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        
    async def generate_query_v1_no_max_tokens(self, user_query: str) -> str:
        """Version 1: Remove max_output_tokens completely"""
        try:
            logger.info(f"V1: Testing without max_output_tokens for: {user_query}")
            
            prompt = f"Create search query for: {user_query}\nIndia market 2025\nReply with only the search query:"
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.9
                    # NO max_output_tokens!
                )
            )
            
            if response.text:
                logger.info(f"✅ V1 SUCCESS: {response.text}")
                return response.text.strip()
            else:
                logger.error(f"❌ V1 FAILED: Empty response")
                if hasattr(response, 'candidates') and response.candidates:
                    logger.error(f"Finish reason: {response.candidates[0].finish_reason}")
                return None
                
        except Exception as e:
            logger.error(f"V1 Exception: {e}")
            return None
    
    async def generate_query_v2_system_instruction(self, user_query: str) -> str:
        """Version 2: Use system instruction to control output"""
        try:
            logger.info(f"V2: Testing with system instruction for: {user_query}")
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Search query for: {user_query} India 2025",
                config=types.GenerateContentConfig(
                    system_instruction="Generate a 15-20 word Google search query. Reply with ONLY the search query, nothing else.",
                    temperature=0.6
                )
            )
            
            if response.text:
                logger.info(f"✅ V2 SUCCESS: {response.text}")
                return response.text.strip()
            else:
                logger.error(f"❌ V2 FAILED: Empty response")
                return None
                
        except Exception as e:
            logger.error(f"V2 Exception: {e}")
            return None
    
    async def generate_query_v3_ultra_minimal(self, user_query: str) -> str:
        """Version 3: Ultra-minimal prompt"""
        try:
            logger.info(f"V3: Testing ultra-minimal for: {user_query}")
            
            # Extremely short prompt
            prompt = f"{user_query} India 2025 search:"
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8
                )
            )
            
            if response.text:
                # Clean up the response
                query = response.text.strip()
                # Remove common prefixes if present
                for prefix in ["search:", "query:", "Search query:", "Google search:"]:
                    if query.lower().startswith(prefix.lower()):
                        query = query[len(prefix):].strip()
                
                logger.info(f"✅ V3 SUCCESS: {query}")
                return query
            else:
                logger.error(f"❌ V3 FAILED: Empty response")
                return None
                
        except Exception as e:
            logger.error(f"V3 Exception: {e}")
            return None
    
    async def generate_query_v4_few_shot(self, user_query: str) -> str:
        """Version 4: Few-shot examples"""
        try:
            logger.info(f"V4: Testing few-shot for: {user_query}")
            
            prompt = f"""Examples:
Query: best stocks to buy
Reply: best stocks India 2025 market analysis expert recommendations investment opportunities

Query: {user_query}
Reply:"""
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.5,
                    top_k=40
                )
            )
            
            if response.text:
                logger.info(f"✅ V4 SUCCESS: {response.text}")
                return response.text.strip()
            else:
                logger.error(f"❌ V4 FAILED: Empty response")
                return None
                
        except Exception as e:
            logger.error(f"V4 Exception: {e}")
            return None

async def test_all_approaches():
    """Test all approaches to find what works"""
    generator = GeminiQueryGenerator()
    
    test_queries = [
        "best stocks to buy",
        "should I take personal loan at 12% to invest in index funds",
        "is ola electric good investment",
        "retirement planning strategies"
    ]
    
    print("\n" + "="*80)
    print("TESTING GEMINI 2.5 FLASH MAX_TOKENS FIX")
    print("="*80 + "\n")
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        print("-" * 60)
        
        # Test all versions
        results = {
            "V1 (No max_tokens)": await generator.generate_query_v1_no_max_tokens(query),
            "V2 (System instruction)": await generator.generate_query_v2_system_instruction(query),
            "V3 (Ultra-minimal)": await generator.generate_query_v3_ultra_minimal(query),
            "V4 (Few-shot)": await generator.generate_query_v4_few_shot(query)
        }
        
        # Show results
        for version, result in results.items():
            if result:
                print(f"✅ {version}: {result}")
            else:
                print(f"❌ {version}: FAILED")
        
        # Find working version
        working_versions = [v for v, r in results.items() if r]
        if working_versions:
            print(f"\n🎯 Working versions: {', '.join(working_versions)}")
        else:
            print("\n⚠️ ALL VERSIONS FAILED!")

# Disabled to prevent interference with main server
# if __name__ == "__main__":
#     asyncio.run(test_all_approaches())