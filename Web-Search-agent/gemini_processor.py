import google.generativeai as genai
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import logging
import time

load_dotenv()
logger = logging.getLogger(__name__)

class GeminiProcessor:
    """Processes queries and content using Google's Gemini API."""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1  # 1 second between requests
    
    def _rate_limit(self):
        """Implement basic rate limiting."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()
    
    def generate_search_queries(self, user_query: str) -> List[str]:
        """Generate multiple search queries based on user input."""
        self._rate_limit()
        
        # Check if this is a financial query
        financial_keywords = ['stock', 'share', 'invest', 'buy', 'sell', 'market', 'price', 'earnings', 'dividend', 'financial', 'revenue', 'profit']
        is_financial = any(keyword in user_query.lower() for keyword in financial_keywords)
        
        if is_financial:
            prompt = f"""
            Given the financial query: "{user_query}"
            
            Generate 4-5 simple search queries that would find relevant financial articles.
            Focus on these aspects:
            1. Company earnings and financial results
            2. Stock price analysis and market performance
            3. Industry news and company developments
            4. Investment outlook and analyst views
            
            Return only simple search queries, one per line, without numbering.
            Do NOT include site restrictions or complex operators.
            Make them simple and effective for web search.
            
            Example format:
            [Company name] earnings report 2024
            [Company name] stock analysis
            [Company name] market news
            """
        else:
            prompt = f"""
            Given the user query: "{user_query}"
            
            Generate 3-5 diverse search queries that would help find comprehensive information about this topic.
            Focus on:
            1. Recent news and developments
            2. Current market conditions (if applicable)
            3. Expert opinions and analysis
            4. Different perspectives on the topic
            
            Return only the search queries, one per line, without numbering or bullet points.
            Make them specific and targeted for web search.
            """
        
        try:
            response = self.model.generate_content(prompt)
            queries = response.text.strip().split('\n')
            # Clean up queries
            queries = [q.strip() for q in queries if q.strip()]
            return queries[:5]  # Limit to 5 queries
        except Exception as e:
            logger.error(f"Error generating search queries: {e}")
            # Fallback to simple query variations
            return [
                user_query,
                f"{user_query} news",
                f"{user_query} analysis",
                f"{user_query} recent developments"
            ]
    
    def analyze_articles(self, articles: List[Dict], user_query: str) -> str:
        """Analyze fetched articles and generate a comprehensive response."""
        self._rate_limit()
        
        if not articles:
            return "No articles were found or successfully fetched for your query."
        
        # Prepare article summaries for analysis
        article_summaries = []
        for i, article in enumerate(articles):
            summary = f"""
Article {i+1}:
Title: {article.get('title', 'No title')}
URL: {article.get('url', 'No URL')}
Content Preview: {article.get('content', '')[:1000]}...
"""
            article_summaries.append(summary)
        
        articles_text = '\n'.join(article_summaries)
        
        prompt = f"""
        User Query: "{user_query}"
        
        Based on the following articles, provide a comprehensive, well-structured analysis:
        
        {articles_text}
        
        Please provide:
        1. A direct answer to the user's question
        2. Key findings and insights from the articles
        3. Current market sentiment or trends (if applicable)
        4. Different perspectives or opinions mentioned
        5. Important dates, numbers, or facts
        6. Conclusion with actionable insights
        
        Structure your response clearly with headings and bullet points where appropriate.
        Be objective and cite information from the articles when relevant.
        If the query is about investment decisions, provide balanced analysis but remind that this is not financial advice.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error analyzing articles: {e}")
            return f"Error analyzing articles: {e}. Please check the raw articles below."
    
    def summarize_article(self, article: Dict) -> str:
        """Summarize a single article."""
        self._rate_limit()
        
        content = article.get('content', '')
        if len(content) < 200:
            return content
        
        prompt = f"""
        Summarize the following article in 2-3 sentences, focusing on the key points:
        
        Title: {article.get('title', 'No title')}
        Content: {content[:2000]}...
        
        Provide a concise summary that captures the main message and important details.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error summarizing article: {e}")
            return article.get('content', '')[:500] + '...'
    
    def enhance_query(self, user_query: str) -> str:
        """Enhance the user query for better search results."""
        self._rate_limit()
        
        prompt = f"""
        Given the user query: "{user_query}"
        
        Enhance this query to make it more effective for web search while preserving the original intent.
        Add relevant keywords, specify time frames if needed (recent, latest, current), and make it more specific.
        
        Return only the enhanced query, nothing else.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error enhancing query: {e}")
            return user_query
    
    def generate_final_report(self, user_query: str, analysis: str, articles: List[Dict]) -> str:
        """Generate a final comprehensive report."""
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# Research Report: {user_query}
Generated on: {current_time}

## Executive Summary
{analysis}

## Source Articles ({len(articles)} articles analyzed)
"""
        
        for i, article in enumerate(articles):
            report += f"""
### Article {i+1}: {article.get('title', 'No title')}
- **URL**: {article.get('url', 'No URL')}
- **Published**: {article.get('publish_date', 'Date unknown')}
- **Authors**: {', '.join(article.get('authors', [])) if article.get('authors') else 'Unknown'}
- **Summary**: {self.summarize_article(article)}

---
"""
        
        report += f"""
## Disclaimer
This report is generated by an AI system for informational purposes only. 
The information should be verified independently and does not constitute professional advice.
For investment decisions, please consult with qualified financial advisors.

## Data Sources
- Total articles analyzed: {len(articles)}
- Search queries generated and executed automatically
- Content extracted using advanced web scraping techniques
- Analysis powered by Google Gemini AI
"""
        
        return report
    
    def analyze_financial_data(self, user_query: str, articles: List[Dict], stock_data: Dict = None) -> str:
        """Specialized financial analysis incorporating stock data and market information."""
        self._rate_limit()
        
        if not articles and not stock_data:
            return "No financial data available for analysis."
        
        # Prepare content for analysis
        content_sections = []
        
        # Add stock data if available
        if stock_data:
            stock_info = f"""
CURRENT STOCK DATA:
Symbol: {stock_data.get('symbol', 'N/A')}
Current Price: {stock_data.get('current_price', 'N/A')}
Price Change: {stock_data.get('price_change', 'N/A')} ({stock_data.get('percent_change', 'N/A')})
Previous Close: {stock_data.get('previous_close', 'N/A')}
Market Cap: {stock_data.get('market_cap', 'N/A')}
PE Ratio: {stock_data.get('pe_ratio', 'N/A')}
52 Week Range: {stock_data.get('52_week_range', 'N/A')}
Company: {stock_data.get('company_name', 'N/A')}
"""
            content_sections.append(stock_info)
        
        # Add articles
        if articles:
            article_summaries = []
            for i, article in enumerate(articles[:10]):  # Limit to avoid token limits
                summary = f"""
Article {i+1}: {article.get('title', 'No title')}
Source: {article.get('source', 'Unknown')}
Content: {article.get('content', article.get('snippet', ''))[:800]}...
"""
                article_summaries.append(summary)
            content_sections.append('\n'.join(article_summaries))
        
        combined_content = '\n\n'.join(content_sections)
        
        prompt = f"""
        Financial Query: "{user_query}"
        
        Based on the following financial data and news articles, provide a comprehensive investment analysis:
        
        {combined_content}
        
        Please provide:
        
        ## EXECUTIVE SUMMARY
        - Direct answer to the user's question
        - Key recommendation (if asking about investment decisions)
        
        ## CURRENT FINANCIAL POSITION
        - Current stock price and recent performance
        - Key financial metrics analysis
        - Market capitalization and valuation
        
        ## MARKET SENTIMENT & NEWS ANALYSIS
        - Recent news impact on stock price
        - Market sentiment from multiple sources
        - Analyst opinions and ratings
        
        ## RISK ASSESSMENT
        - Key risks to consider
        - Market volatility factors
        - Industry-specific challenges
        
        ## TECHNICAL & FUNDAMENTAL ANALYSIS
        - Price trends and technical indicators
        - Financial health metrics
        - Comparison with industry peers
        
        ## INVESTMENT RECOMMENDATION
        - Short-term outlook (1-3 months)
        - Medium-term outlook (3-12 months)
        - Key factors to monitor
        
        ## DISCLAIMER
        - Important risk warnings
        - Advice to consult financial advisors
        
        Structure your response clearly with headings and bullet points.
        Be objective and cite specific information from the provided data.
        If this is about investment decisions, emphasize that this is informational analysis, not financial advice.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error in financial analysis: {e}")
            return f"Error in financial analysis: {e}. Please check the raw data below."