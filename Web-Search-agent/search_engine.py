import requests
import json
from typing import List, Dict, Optional
import time
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import re
import random

load_dotenv()

class WebSearchEngine:
    """Web search engine that scrapes search results from multiple sources."""
    
    def __init__(self):
        self.session = requests.Session()
        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def google_search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search using Google search scraping with better filtering."""
        # Skip Google scraping since it's being blocked, go directly to reliable sources
        return self._direct_financial_search(query, num_results)
    
    def _direct_financial_search(self, query: str, num_results: int) -> List[Dict]:
        """Search reliable English financial news sources directly."""
        # Construct URLs for reliable financial news sources
        financial_sources = [
            ("Yahoo Finance", f"https://finance.yahoo.com/topic/stock-market-news/"),
            ("Reuters", f"https://www.reuters.com/markets/"),
            ("MarketWatch", f"https://www.marketwatch.com/"),
            ("CNBC", f"https://www.cnbc.com/markets/"),
            ("Economic Times", f"https://economictimes.indiatimes.com/markets"),
            ("MoneyControl", f"https://www.moneycontrol.com/news/business/markets/")
        ]
        
        results = []
        for source_name, base_url in financial_sources[:4]:  # Limit to 4 sources for speed
            try:
                # Use the bing search as it's more reliable
                search_query = f"{query} site:{base_url.split('/')[2]}"
                bing_results = self.bing_search(search_query, 2)
                
                # Filter and add source info
                for result in bing_results:
                    if any(domain in result['url'] for domain in ['yahoo.com', 'reuters.com', 'marketwatch.com', 'cnbc.com', 'economictimes.indiatimes.com', 'moneycontrol.com']):
                        result['source'] = f"{source_name}_direct"
                        results.append(result)
                
                if len(results) >= num_results:
                    break
                    
                time.sleep(0.5)  # Small delay
                
            except Exception as e:
                continue
        
        return results[:num_results]
    
    def duckduckgo_search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Fallback search using DuckDuckGo web scraping."""
        try:
            # Rotate user agent
            self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
            
            # DuckDuckGo search URL
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            # Add delay
            time.sleep(random.uniform(1, 2))
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Find search results
            search_results = soup.find_all('div', class_='result')
            
            for result in search_results[:num_results]:
                try:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                        
                        if url and title:
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'source': 'duckduckgo_scrape'
                            })
                except Exception as e:
                    continue
            
            if not results:
                # Try alternative approach with Bing scraping
                return self.bing_search(query, num_results)
            
            print(f"DuckDuckGo scraping found {len(results)} results")
            return results
            
        except Exception as e:
            print(f"DuckDuckGo scraping failed: {e}. Trying Bing...")
            return self.bing_search(query, num_results)
    
    def bing_search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Alternative search using Bing scraping."""
        try:
            # Rotate user agent
            self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
            
            # Bing search URL
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}&count={min(num_results, 20)}"
            
            # Add delay
            time.sleep(random.uniform(1, 2))
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Find search results
            search_results = soup.find_all('li', class_='b_algo')
            
            for result in search_results[:num_results]:
                try:
                    title_elem = result.find('h2')
                    if title_elem:
                        link_elem = title_elem.find('a')
                        if link_elem:
                            title = link_elem.get_text(strip=True)
                            url = link_elem.get('href', '')
                            
                            snippet_elem = result.find('p') or result.find('div', class_='b_caption')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                            
                            if url and title:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'snippet': snippet,
                                    'source': 'bing_scrape'
                                })
                except Exception as e:
                    continue
            
            print(f"Bing scraping found {len(results)} results")
            return results
            
        except Exception as e:
            print(f"Bing scraping failed: {e}")
            return []
    
    def news_search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search for recent news articles using Google News scraping."""
        try:
            # Rotate user agent
            self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
            
            # Google News search URL
            news_query = quote_plus(f"{query} news")
            search_url = f"https://news.google.com/search?q={news_query}&hl=en-US&gl=US&ceid=US%3Aen"
            
            # Add delay
            time.sleep(random.uniform(1, 2))
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Find news articles
            articles = soup.find_all('article')
            
            for article in articles[:num_results]:
                try:
                    title_elem = article.find('h3') or article.find('h4')
                    link_elem = article.find('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        url = link_elem.get('href', '')
                        
                        # Clean Google News URL
                        if url.startswith('./'):
                            url = 'https://news.google.com' + url[1:]
                        
                        # Try to get actual article URL from Google News redirect
                        # For now, use the Google News URL
                        if url and title:
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': title,  # Use title as snippet for news
                                'source': 'google_news_scrape'
                            })
                except Exception as e:
                    continue
            
            if results:
                print(f"Google News scraping found {len(results)} results")
                return results
            else:
                # Fallback to regular search with news keywords
                news_query_fallback = f"{query} news latest"
                return self.google_search(news_query_fallback, num_results)
                
        except Exception as e:
            print(f"Google News scraping failed: {e}. Using regular search...")
            news_query_fallback = f"{query} news latest"
            return self.google_search(news_query_fallback, num_results)
    
    def search_multiple_sources(self, query: str, num_results: int = 20) -> List[Dict]:
        """Search from multiple sources and combine results."""
        all_results = []
        
        # Get general search results
        general_results = self.google_search(query, num_results // 2)
        all_results.extend(general_results)
        
        # Get news-specific results
        news_results = self.news_search(query, num_results // 2)
        all_results.extend(news_results)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return unique_results[:num_results]
    
    def financial_search(self, query: str, num_results: int = 15) -> List[Dict]:
        """Specialized financial search targeting financial websites."""
        financial_sites = [
            "site:economictimes.indiatimes.com",
            "site:moneycontrol.com", 
            "site:business-standard.com",
            "site:livemint.com",
            "site:reuters.com/markets",
            "site:bloomberg.com/markets",
            "site:cnbc.com",
            "site:marketwatch.com",
            "site:finance.yahoo.com"
        ]
        
        all_results = []
        
        # Search with financial site constraints
        for site in financial_sites[:6]:  # Limit to prevent too many requests
            financial_query = f"{query} {site}"
            try:
                results = self.google_search(financial_query, 3)
                all_results.extend(results)
                time.sleep(random.uniform(1, 2))
            except Exception as e:
                continue
        
        # Remove duplicates
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return unique_results[:num_results]