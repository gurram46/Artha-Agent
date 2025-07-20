import os
import time
from typing import List, Dict, Optional
import logging
from datetime import datetime

from search_engine import WebSearchEngine
from article_fetcher import ArticleFetcher
from gemini_processor import GeminiProcessor
from financial_scraper import FinancialDataScraper
from comprehensive_scraper import ComprehensiveFinancialScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerplexityAgent:
    """Advanced Perplexity-like agent that fetches articles and generates comprehensive reports."""
    
    def __init__(self):
        """Initialize the agent with all necessary components."""
        self.search_engine = WebSearchEngine()
        self.article_fetcher = ArticleFetcher()
        self.gemini_processor = GeminiProcessor()
        self.financial_scraper = FinancialDataScraper()
        self.comprehensive_scraper = ComprehensiveFinancialScraper()
        
        # Configuration
        self.max_articles_per_query = 2  # Reduced for speed
        self.max_search_queries = 2  # Reduced for speed
        self.output_dir = "reports"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("PerplexityAgent initialized successfully")
    
    def research(self, user_query: str, max_articles: int = 20) -> Dict:
        """
        Main research method that orchestrates the entire process.
        
        Args:
            user_query: The user's question or query
            max_articles: Maximum number of articles to fetch
            
        Returns:
            Dictionary containing the research results
        """
        logger.info(f"Starting research for query: '{user_query}'")
        start_time = time.time()
        
        try:
            # Step 1: Enhance the user query
            logger.info("Step 1: Enhancing user query...")
            enhanced_query = self.gemini_processor.enhance_query(user_query)
            logger.info(f"Enhanced query: '{enhanced_query}'")
            
            # Step 2: Generate multiple search queries
            logger.info("Step 2: Generating search queries...")
            search_queries = self.gemini_processor.generate_search_queries(enhanced_query)
            search_queries = search_queries[:self.max_search_queries]
            logger.info(f"Generated {len(search_queries)} search queries")
            
            # Step 3: Search for articles using all queries
            logger.info("Step 3: Searching for articles...")
            all_search_results = []
            for i, query in enumerate(search_queries):
                logger.info(f"Executing search query {i+1}/{len(search_queries)}: {query}")
                results = self.search_engine.search_multiple_sources(query, self.max_articles_per_query)
                all_search_results.extend(results)
                time.sleep(1)  # Be respectful to APIs
            
            # Remove duplicates and limit results
            unique_urls = set()
            unique_results = []
            for result in all_search_results:
                if result['url'] not in unique_urls and self.article_fetcher.is_valid_url(result['url']):
                    unique_urls.add(result['url'])
                    unique_results.append(result)
                    if len(unique_results) >= max_articles:
                        break
            
            logger.info(f"Found {len(unique_results)} unique articles to fetch")
            
            # Step 4: Fetch article content
            logger.info("Step 4: Fetching article content...")
            articles = self.article_fetcher.fetch_multiple_articles([r['url'] for r in unique_results])
            logger.info(f"Successfully fetched {len(articles)} articles")
            
            # Step 5: Analyze articles with Gemini
            logger.info("Step 5: Analyzing articles with Gemini...")
            analysis = self.gemini_processor.analyze_articles(articles, user_query)
            
            # Step 6: Generate final report
            logger.info("Step 6: Generating final report...")
            final_report = self.gemini_processor.generate_final_report(user_query, analysis, articles)
            
            end_time = time.time()
            duration = end_time - start_time
            
            research_results = {
                'user_query': user_query,
                'enhanced_query': enhanced_query,
                'search_queries': search_queries,
                'total_search_results': len(all_search_results),
                'articles_fetched': len(articles),
                'analysis': analysis,
                'final_report': final_report,
                'articles': articles,
                'duration_seconds': duration,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Research completed in {duration:.2f} seconds")
            return research_results
            
        except Exception as e:
            logger.error(f"Error during research: {e}")
            raise
    
    def financial_research(self, user_query: str, max_articles: int = 20) -> Dict:
        """
        Specialized financial research method with stock data integration.
        
        Args:
            user_query: The user's financial question or query
            max_articles: Maximum number of articles to fetch
            
        Returns:
            Dictionary containing the research results with financial data
        """
        logger.info(f"Starting financial research for query: '{user_query}'")
        start_time = time.time()
        
        try:
            # Check if this involves a specific stock
            financial_keywords = ['stock', 'share', 'invest', 'buy', 'sell', 'market', 'price', 'earnings']
            is_financial_query = any(keyword in user_query.lower() for keyword in financial_keywords)
            
            stock_data = None
            
            # Try to extract and get stock data
            if is_financial_query:
                stock_symbol = self.financial_scraper.analyze_stock_symbol(user_query)
                if stock_symbol:
                    logger.info(f"Identified stock symbol: {stock_symbol}")
                    
                    # Try Yahoo Finance first, then MoneyControl for Indian stocks
                    stock_data = self.financial_scraper.get_stock_data_yahoo(stock_symbol)
                    if not stock_data and '.NS' in stock_symbol:
                        # Try Indian stock sources
                        base_symbol = stock_symbol.replace('.NS', '')
                        stock_data = self.financial_scraper.get_stock_data_moneycontrol(base_symbol)
            
            # Step 1: Enhance the user query
            logger.info("Step 1: Enhancing user query...")
            enhanced_query = self.gemini_processor.enhance_query(user_query)
            logger.info(f"Enhanced query: '{enhanced_query}'")
            
            # Step 2: Generate multiple search queries (financial-aware)
            logger.info("Step 2: Generating search queries...")
            search_queries = self.gemini_processor.generate_search_queries(enhanced_query)
            search_queries = search_queries[:self.max_search_queries]
            logger.info(f"Generated {len(search_queries)} search queries")
            
            # Step 3: Search for articles using financial sources if applicable
            logger.info("Step 3: Searching for articles...")
            all_search_results = []
            
            # Use financial search if this is a financial query
            if is_financial_query:
                financial_results = self.search_engine.financial_search(enhanced_query, max_articles // 2)
                all_search_results.extend(financial_results)
                logger.info(f"Found {len(financial_results)} financial-specific results")
            
            # Also get financial news
            if is_financial_query:
                financial_news = self.financial_scraper.get_financial_news(enhanced_query, max_articles // 4)
                # Convert to search result format
                for news_item in financial_news:
                    all_search_results.append({
                        'title': news_item['title'],
                        'url': news_item['url'],
                        'snippet': news_item['snippet'],
                        'source': f"financial_news_{news_item['source']}"
                    })
                logger.info(f"Found {len(financial_news)} financial news items")
            
            # Regular search queries
            for i, query in enumerate(search_queries):
                logger.info(f"Executing search query {i+1}/{len(search_queries)}: {query}")
                if is_financial_query:
                    results = self.search_engine.financial_search(query, self.max_articles_per_query)
                else:
                    results = self.search_engine.search_multiple_sources(query, self.max_articles_per_query)
                all_search_results.extend(results)
                time.sleep(1)  # Be respectful to APIs
            
            # Remove duplicates and limit results
            unique_urls = set()
            unique_results = []
            for result in all_search_results:
                if result['url'] not in unique_urls and self.article_fetcher.is_valid_url(result['url']):
                    unique_urls.add(result['url'])
                    unique_results.append(result)
                    if len(unique_results) >= max_articles:
                        break
            
            logger.info(f"Found {len(unique_results)} unique articles to fetch")
            
            # Step 4: Fetch article content
            logger.info("Step 4: Fetching article content...")
            articles = self.article_fetcher.fetch_multiple_articles([r['url'] for r in unique_results])
            logger.info(f"Successfully fetched {len(articles)} articles")
            
            # Step 5: Analyze with Gemini (use financial analysis if applicable)
            logger.info("Step 5: Analyzing with Gemini...")
            if is_financial_query and (stock_data or articles):
                analysis = self.gemini_processor.analyze_financial_data(user_query, articles, stock_data)
            else:
                analysis = self.gemini_processor.analyze_articles(articles, user_query)
            
            # Step 6: Generate final report
            logger.info("Step 6: Generating final report...")
            final_report = self._generate_financial_report(user_query, analysis, articles, stock_data)
            
            end_time = time.time()
            duration = end_time - start_time
            
            research_results = {
                'user_query': user_query,
                'enhanced_query': enhanced_query,
                'search_queries': search_queries,
                'total_search_results': len(all_search_results),
                'articles_fetched': len(articles),
                'stock_data': stock_data,
                'analysis': analysis,
                'final_report': final_report,
                'articles': articles,
                'duration_seconds': duration,
                'timestamp': datetime.now().isoformat(),
                'research_type': 'financial' if is_financial_query else 'general'
            }
            
            logger.info(f"Financial research completed in {duration:.2f} seconds")
            return research_results
            
        except Exception as e:
            logger.error(f"Error during financial research: {e}")
            raise
    
    def _generate_financial_report(self, user_query: str, analysis: str, articles: List[Dict], stock_data: Dict = None) -> str:
        """Generate a financial report with stock data integration."""
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# Financial Research Report: {user_query}
Generated on: {current_time}

## Executive Summary
{analysis}
"""
        
        # Add stock data section if available
        if stock_data:
            report += f"""

## Current Stock Data
**Symbol**: {stock_data.get('symbol', 'N/A')}
**Company**: {stock_data.get('company_name', 'N/A')}
**Current Price**: {stock_data.get('current_price', 'N/A')}
**Price Change**: {stock_data.get('price_change', 'N/A')} ({stock_data.get('percent_change', 'N/A')})
**Previous Close**: {stock_data.get('previous_close', 'N/A')}
**Market Cap**: {stock_data.get('market_cap', 'N/A')}
**PE Ratio**: {stock_data.get('pe_ratio', 'N/A')}
**52 Week Range**: {stock_data.get('52_week_range', 'N/A')}
**Data Source**: {stock_data.get('source', 'N/A')}
"""
        
        report += f"""

## Source Articles ({len(articles)} articles analyzed)
"""
        
        for i, article in enumerate(articles):
            report += f"""
### Article {i+1}: {article.get('title', 'No title')}
- **URL**: {article.get('url', 'No URL')}
- **Source**: {article.get('source', 'Unknown')}
- **Published**: {article.get('publish_date', 'Date unknown')}
- **Summary**: {self.gemini_processor.summarize_article(article)}

---
"""
        
        report += f"""
## Important Disclaimers
⚠️ **INVESTMENT RISK WARNING**: This report is generated by an AI system for informational purposes only. 

- This is NOT personalized financial advice
- Past performance does not guarantee future results
- All investments carry risk of loss
- Stock prices are volatile and can change rapidly
- Always do your own research and due diligence
- Consult with qualified financial advisors before making investment decisions
- Consider your risk tolerance, investment timeline, and financial goals

## Data Sources & Methodology
- **Articles analyzed**: {len(articles)}
- **Stock data sources**: Yahoo Finance, MoneyControl, Economic Times
- **News sources**: Economic Times, MoneyControl, Reuters, Bloomberg, Business Standard
- **AI Analysis**: Google Gemini Pro
- **Search methodology**: Multi-source web scraping with financial site prioritization

*Generated at {current_time} by Perplexity-like Financial Research Agent*
"""
        
        return report
    
    def comprehensive_research(self, user_query: str, max_articles: int = 30) -> Dict:
        """
        Comprehensive research method that gathers vast amounts of content.
        Uses LLM only for generating search queries, returns pure article data.
        
        Args:
            user_query: The user's financial question or query
            max_articles: Maximum number of articles to fetch (default: 30)
            
        Returns:
            Dictionary containing comprehensive research results with raw data only
        """
        logger.info(f"Starting comprehensive research for query: '{user_query}'")
        start_time = time.time()
        
        try:
            # Step 1: Generate multiple search queries using LLM
            logger.info("Step 1: Generating search queries with LLM...")
            search_queries = self.gemini_processor.generate_search_queries(user_query)
            logger.info(f"Generated {len(search_queries)} search queries: {search_queries}")
            
            # Step 2: Search for articles using generated queries
            logger.info("Step 2: Comprehensive article search...")
            all_articles = []
            
            # Use the original user query
            articles = self.comprehensive_scraper.comprehensive_search(user_query, max_articles // 2)
            all_articles.extend(articles)
            
            # Use LLM-generated queries for more comprehensive search
            for query in search_queries[:3]:  # Limit to 3 additional queries
                logger.info(f"Searching with query: {query}")
                query_articles = self.comprehensive_scraper.comprehensive_search(query, max_articles // (len(search_queries) + 1))
                all_articles.extend(query_articles)
                time.sleep(1)  # Be respectful
            
            # Remove duplicates
            seen_urls = set()
            unique_articles = []
            for article in all_articles:
                if article['url'] not in seen_urls:
                    seen_urls.add(article['url'])
                    unique_articles.append(article)
            
            logger.info(f"Found {len(unique_articles)} unique articles")
            
            # Step 3: Fetch all content (NO LLM ANALYSIS)
            logger.info("Step 3: Fetching comprehensive content...")
            articles_with_content = self.comprehensive_scraper.fetch_all_content(unique_articles[:max_articles], max_workers=3)
            logger.info(f"Successfully fetched content for {len(articles_with_content)} articles")
            
            # Step 4: Generate PURE DATA report (no LLM analysis)
            logger.info("Step 4: Generating pure data report...")
            final_report = self._generate_pure_data_report(user_query, search_queries, articles_with_content)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate content stats
            total_content_length = sum(len(article.get('content', '')) for article in articles_with_content)
            
            research_results = {
                'user_query': user_query,
                'search_queries_generated': search_queries,
                'articles_fetched': len(articles_with_content),
                'total_content_length': total_content_length,
                'final_report': final_report,
                'articles': articles_with_content,
                'duration_seconds': duration,
                'timestamp': datetime.now().isoformat(),
                'research_type': 'comprehensive_data_only'
            }
            
            logger.info(f"Comprehensive data collection completed in {duration:.2f} seconds")
            logger.info(f"Total content: {total_content_length:,} characters")
            return research_results
            
        except Exception as e:
            logger.error(f"Error during comprehensive research: {e}")
            raise
    
    def _generate_pure_data_report(self, user_query: str, search_queries: List[str], articles: List[Dict]) -> str:
        """Generate a pure data report with only scraped article content (no LLM analysis)."""
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        total_content_length = sum(len(article.get('content', '')) for article in articles)
        
        report = f"""# RAW FINANCIAL DATA COLLECTION\nQuery: {user_query}\nGenerated: {current_time}\nArticles Collected: {len(articles)}\nTotal Content: {total_content_length:,} characters\n\n## Search Queries Generated by LLM\nOriginal Query: {user_query}\nGenerated Queries:\n"""
        
        for i, query in enumerate(search_queries, 1):
            report += f"{i}. {query}\n"
        
        report += f"""\n## PURE ARTICLE DATA\nBelow is the raw scraped content from {len(articles)} financial articles.\nThis data is ready for your own LLM processing and analysis.\n\n"""
        
        for i, article in enumerate(articles, 1):
            content = article.get('content', 'No content available')
            # Add line breaks to content for better readability
            if content and content != 'No content available':
                # Split long content into smaller chunks with line breaks
                words = content.split()
                formatted_content = ""
                line_length = 0
                for word in words:
                    if line_length + len(word) + 1 > 100:  # Start new line after ~100 chars
                        formatted_content += f"\n{word} "
                        line_length = len(word) + 1
                    else:
                        formatted_content += f"{word} "
                        line_length += len(word) + 1
                content = formatted_content.strip()
            
            report += f"""\n{'='*80}\nARTICLE {i}: {article.get('title', 'No title')}\nSource: {article.get('source', 'Unknown')}\nURL: {article.get('url', 'No URL')}\nContent Length: {article.get('content_length', 0):,} characters\n{'='*80}\n\n{content}\n\n"""
        
        report += f"""\n{'='*80}\nEND OF RAW DATA COLLECTION\n{'='*80}\n\n## Data Collection Summary\n- Total Articles: {len(articles)}\n- Total Characters: {total_content_length:,}\n- Sources: Economic Times, MoneyControl, Business Standard\n- Collection Method: Multi-query web scraping with content extraction\n- LLM Usage: Only for query generation (no analysis included)\n\n## Ready for LLM Processing\nThis raw dataset is prepared for:\n- Investment decision analysis\n- Market sentiment evaluation\n- Risk assessment\n- Custom financial analysis\n- Any LLM processing you require\n\nGenerated at {current_time}\n"""
        
        return report
    
    def save_report_to_file(self, research_results: Dict, filename: Optional[str] = None) -> str:
        """Save the research report to a text file."""
        if not filename:
            # Generate filename from query and timestamp
            safe_query = "".join(c for c in research_results['user_query'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_query = safe_query.replace(' ', '_')[:50]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_report_{safe_query}_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(research_results['final_report'])
                
                # Add raw article content as appendix
                f.write("\n\n" + "="*80 + "\n")
                f.write("APPENDIX: RAW ARTICLE CONTENT\n")
                f.write("="*80 + "\n\n")
                
                for i, article in enumerate(research_results['articles']):
                    f.write(f"\n--- Article {i+1} ---\n")
                    f.write(f"Title: {article.get('title', 'No title')}\n")
                    f.write(f"URL: {article.get('url', 'No URL')}\n")
                    f.write(f"Content:\n{article.get('content', 'No content')}\n")
                    f.write("\n" + "-"*50 + "\n")
            
            logger.info(f"Report saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            raise
    
    def quick_research(self, user_query: str) -> str:
        """Quick research method that returns just the analysis text."""
        try:
            results = self.research(user_query, max_articles=10)
            return results['analysis']
        except Exception as e:
            logger.error(f"Quick research failed: {e}")
            return f"Research failed: {e}"
    
    def get_stats(self) -> Dict:
        """Get statistics about the agent's capabilities."""
        return {
            'search_engine': 'Google Custom Search API + DuckDuckGo fallback',
            'article_extraction': 'Newspaper3k + BeautifulSoup fallback',
            'ai_processor': 'Google Gemini Pro',
            'max_articles_default': 20,
            'supported_formats': ['TXT'],
            'output_directory': self.output_dir
        }

def main():
    """Example usage of the PerplexityAgent."""
    agent = PerplexityAgent()
    
    # Example query
    user_query = "Can I buy Reliance stock right now?"
    
    print(f"Researching: {user_query}")
    print("-" * 50)
    
    try:
        # Perform research
        results = agent.research(user_query)
        
        # Save to file
        filepath = agent.save_report_to_file(results)
        
        print(f"\nResearch completed!")
        print(f"Articles analyzed: {results['articles_fetched']}")
        print(f"Duration: {results['duration_seconds']:.2f} seconds")
        print(f"Report saved to: {filepath}")
        
        # Print summary
        print("\nQuick Summary:")
        print(results['analysis'][:500] + "...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()