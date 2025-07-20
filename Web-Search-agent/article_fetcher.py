import requests
from bs4 import BeautifulSoup
from newspaper import Article
import time
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin, urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArticleFetcher:
    """Fetches and extracts content from web articles."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
        self.max_retries = 3
    
    def fetch_article_content(self, url: str) -> Optional[Dict]:
        """Fetch and extract content from a single article URL."""
        try:
            # Try using newspaper3k first (more robust for news articles)
            article = Article(url)
            article.download()
            article.parse()
            
            if article.text and len(article.text) > 100:
                return {
                    'url': url,
                    'title': article.title or 'No title',
                    'content': article.text,
                    'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                    'authors': list(article.authors) if article.authors else [],
                    'summary': article.summary if hasattr(article, 'summary') else '',
                    'method': 'newspaper3k'
                }
        except Exception as e:
            logger.info(f"Newspaper3k failed for {url}: {e}. Trying BeautifulSoup...")
        
        # Fallback to BeautifulSoup
        return self._fetch_with_beautifulsoup(url)
    
    def _fetch_with_beautifulsoup(self, url: str) -> Optional[Dict]:
        """Fallback method using BeautifulSoup for content extraction."""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    script.decompose()
                
                # Try to find the main content
                content = self._extract_main_content(soup)
                title = self._extract_title(soup)
                
                if content and len(content) > 100:
                    return {
                        'url': url,
                        'title': title,
                        'content': content,
                        'publish_date': None,
                        'authors': [],
                        'summary': content[:500] + '...' if len(content) > 500 else content,
                        'method': 'beautifulsoup'
                    }
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                else:
                    logger.error(f"All attempts failed for {url}")
        
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from the webpage."""
        # Try different title selectors
        title_selectors = [
            'h1',
            'title',
            '.article-title',
            '.post-title',
            '.entry-title',
            '[data-testid="headline"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                return title_elem.get_text().strip()
        
        return 'No title found'
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the webpage."""
        # Try different content selectors in order of preference
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            '.story-body',
            '.article-body',
            '[data-testid="article-body"]',
            'main',
            '.main-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Clean up the text
                text = content_elem.get_text(separator=' ', strip=True)
                if len(text) > 200:  # Ensure we have substantial content
                    return self._clean_text(text)
        
        # Fallback: get all paragraph text
        paragraphs = soup.find_all('p')
        if paragraphs:
            text = ' '.join([p.get_text(strip=True) for p in paragraphs])
            return self._clean_text(text)
        
        # Last resort: get all text
        return self._clean_text(soup.get_text(separator=' ', strip=True))
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common unwanted phrases
        unwanted_phrases = [
            'Subscribe to our newsletter',
            'Follow us on',
            'Share this article',
            'Click here',
            'Read more',
            'Advertisement'
        ]
        for phrase in unwanted_phrases:
            text = text.replace(phrase, '')
        
        return text.strip()
    
    def fetch_multiple_articles(self, urls: List[str], max_workers: int = 5) -> List[Dict]:
        """Fetch content from multiple articles."""
        articles = []
        
        for i, url in enumerate(urls):
            try:
                logger.info(f"Fetching article {i+1}/{len(urls)}: {url}")
                article = self.fetch_article_content(url)
                if article:
                    articles.append(article)
                    logger.info(f"Successfully fetched: {article['title'][:50]}...")
                else:
                    logger.warning(f"Failed to fetch content from: {url}")
                
                # Add small delay to be respectful to servers
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                continue
        
        return articles
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and accessible."""
        try:
            parsed = urlparse(url)
            
            # Block problematic domains
            blocked_domains = [
                'zhihu.com', 'baidu.com', 'tff-forum.de', 'finansavisen.no',
                'bing.com/ck/', 'google.com/url', 'redirects', 'forum'
            ]
            
            if any(blocked in url.lower() for blocked in blocked_domains):
                return False
            
            # Prefer English financial sites
            preferred_domains = [
                'yahoo.com', 'reuters.com', 'cnbc.com', 'marketwatch.com',
                'economictimes.indiatimes.com', 'moneycontrol.com',
                'bloomberg.com', 'wsj.com', 'ft.com'
            ]
            
            # If it's a preferred domain, definitely include it
            if any(domain in url.lower() for domain in preferred_domains):
                return True
            
            return bool(parsed.netloc) and parsed.scheme in ['http', 'https']
        except:
            return False