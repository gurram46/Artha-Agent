#!/usr/bin/env python3
"""
Comprehensive Article Scraper for Financial Research - SIMPLIFIED VERSION
Focus on actually finding and extracting article content.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random
from typing import List, Dict, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveFinancialScraper:
    """Scrapes financial content from reliable sources - simplified and working."""
    
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
    
    def extract_company_name(self, query: str) -> str:
        """Extract clean company name from query."""
        # Remove common query words
        query = re.sub(r'\b(stock|share|price|buy|sell|invest|analysis|today|now|right now|can i|should i|is|good|bad)\b', '', query, flags=re.IGNORECASE)
        query = re.sub(r'[?!."]', '', query)
        
        # Get the main company name
        words = query.strip().split()
        if words:
            for word in words:
                if len(word) > 2 and word.lower() not in ['the', 'and', 'for', 'to', 'in', 'on', 'at']:
                    return word.lower()
        
        return query.strip().lower()
    
    def search_economic_times(self, company: str, max_articles: int = 10) -> List[Dict]:
        """Search Economic Times for company articles."""
        try:
            logger.info(f"Searching Economic Times for: {company}")
            articles = []
            
            # Go directly to stocks news section
            url = "https://economictimes.indiatimes.com/markets/stocks/news"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all article links
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # Look for company mentions in titles
                if (len(title) > 15 and 
                    company.lower() in title.lower()):
                    
                    if not href.startswith('http'):
                        href = urljoin('https://economictimes.indiatimes.com', href)
                    
                    # Only include actual article URLs
                    if ('/articleshow/' in href or 'companyid' in href):
                        articles.append({
                            'title': title,
                            'url': href,
                            'source': 'Economic Times'
                        })
                        
                        if len(articles) >= max_articles:
                            break
            
            logger.info(f"Found {len(articles)} articles from Economic Times")
            return articles
            
        except Exception as e:
            logger.error(f"Economic Times search failed: {e}")
            return []
    
    def search_moneycontrol(self, company: str, max_articles: int = 10) -> List[Dict]:
        """Search MoneyControl for company articles."""
        try:
            logger.info(f"Searching MoneyControl for: {company}")
            articles = []
            
            # Go to business/markets section
            url = "https://www.moneycontrol.com/news/business/markets/"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all article links
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # Look for company mentions in titles
                if (len(title) > 15 and 
                    company.lower() in title.lower() and
                    '/news/' in href):
                    
                    if not href.startswith('http'):
                        href = urljoin('https://www.moneycontrol.com', href)
                    
                    articles.append({
                        'title': title,
                        'url': href,
                        'source': 'MoneyControl'
                    })
                    
                    if len(articles) >= max_articles:
                        break
            
            logger.info(f"Found {len(articles)} articles from MoneyControl")
            return articles
            
        except Exception as e:
            logger.error(f"MoneyControl search failed: {e}")
            return []
    
    def fetch_article_content(self, article: Dict) -> Dict:
        """Fetch full article content with proper extraction."""
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = self.session.get(article['url'], headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
                element.decompose()
            
            content = ""
            
            # Try specific selectors based on source
            if 'economictimes.indiatimes.com' in article['url']:
                selectors = ['div.Normal', 'div[data-module="ArticleBody"]', 'div.artText']
                for selector in selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        content = elem.get_text(separator='\n', strip=True)
                        break
            
            elif 'moneycontrol.com' in article['url']:
                selectors = ['div.content_wrapper', 'div.arti-flow', 'div.article_desc']
                for selector in selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        content = elem.get_text(separator='\n', strip=True)
                        break
            
            # Fallback: try to get paragraphs with substantial content
            if not content or len(content) < 100:
                paragraphs = soup.find_all('p')
                substantial_paragraphs = [p.get_text(strip=True) for p in paragraphs 
                                        if len(p.get_text(strip=True)) > 20]
                content = '\n\n'.join(substantial_paragraphs)
            
            # Clean up content
            if content:
                # Remove excessive whitespace
                content = re.sub(r'\n+', '\n', content)
                content = re.sub(r'\s+', ' ', content)
                
                # Remove unwanted phrases
                unwanted = ['Subscribe to', 'Follow us', 'Download', 'Click here', 'Read more']
                for phrase in unwanted:
                    content = re.sub(rf'\b{phrase}[^\n]*', '', content, flags=re.IGNORECASE)
                
                content = content.strip()
            
            article['content'] = content
            article['content_length'] = len(content)
            
            logger.info(f"Extracted {len(content)} characters from {article['url']}")
            return article
            
        except Exception as e:
            logger.warning(f"Failed to extract content from {article['url']}: {e}")
            article['content'] = f"Failed to extract: {e}"
            article['content_length'] = 0
            return article
    
    def comprehensive_search(self, query: str, max_total_articles: int = 20) -> List[Dict]:
        """Perform comprehensive search across sources."""
        logger.info(f"Starting search for: {query}")
        
        company = self.extract_company_name(query)
        logger.info(f"Extracted company: {company}")
        
        all_articles = []
        
        # Search Economic Times
        try:
            et_articles = self.search_economic_times(company, max_total_articles // 2)
            all_articles.extend(et_articles)
            time.sleep(2)
        except Exception as e:
            logger.error(f"Economic Times search failed: {e}")
        
        # Search MoneyControl
        try:
            mc_articles = self.search_moneycontrol(company, max_total_articles // 2)
            all_articles.extend(mc_articles)
            time.sleep(2)
        except Exception as e:
            logger.error(f"MoneyControl search failed: {e}")
        
        # Remove duplicates
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        logger.info(f"Found {len(unique_articles)} unique articles")
        return unique_articles[:max_total_articles]
    
    def fetch_all_content(self, articles: List[Dict], max_workers: int = 3) -> List[Dict]:
        """Fetch content for all articles."""
        logger.info(f"Fetching content for {len(articles)} articles...")
        
        articles_with_content = []
        
        # Process articles sequentially to be respectful to servers
        for i, article in enumerate(articles):
            try:
                article_with_content = self.fetch_article_content(article)
                if article_with_content['content_length'] > 100:
                    articles_with_content.append(article_with_content)
                
                logger.info(f"Processed {i+1}/{len(articles)} articles")
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                logger.warning(f"Error processing article: {e}")
        
        logger.info(f"Successfully fetched content for {len(articles_with_content)} articles")
        return articles_with_content

def main():
    """Test the scraper."""
    scraper = ComprehensiveFinancialScraper()
    
    query = "Reliance stock analysis"
    articles = scraper.comprehensive_search(query, 5)
    
    if articles:
        print(f"Found {len(articles)} articles")
        articles_with_content = scraper.fetch_all_content(articles)
        print(f"Extracted content from {len(articles_with_content)} articles")
        
        for article in articles_with_content:
            print(f"- {article['title'][:50]}... ({article['content_length']} chars)")
    else:
        print("No articles found")

if __name__ == "__main__":
    main()