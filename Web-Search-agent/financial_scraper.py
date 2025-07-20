import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
import time
import random
from urllib.parse import quote_plus

class FinancialDataScraper:
    """Specialized scraper for financial data including stock prices, market data, and financial news."""
    
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def get_stock_data_yahoo(self, symbol: str) -> Optional[Dict]:
        """Scrape stock data from Yahoo Finance."""
        try:
            # Rotate user agent
            self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
            
            url = f"https://finance.yahoo.com/quote/{symbol.upper()}"
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stock_data = {
                'symbol': symbol.upper(),
                'source': 'yahoo_finance',
                'timestamp': time.time()
            }
            
            # Current price
            price_elem = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
            if price_elem:
                stock_data['current_price'] = price_elem.get_text(strip=True)
            
            # Price change
            change_elem = soup.find('fin-streamer', {'data-field': 'regularMarketChange'})
            if change_elem:
                stock_data['price_change'] = change_elem.get_text(strip=True)
            
            # Percent change
            percent_change_elem = soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent'})
            if percent_change_elem:
                stock_data['percent_change'] = percent_change_elem.get_text(strip=True)
            
            # Previous close
            prev_close = soup.find('td', string='Previous Close')
            if prev_close:
                prev_close_val = prev_close.find_next_sibling('td')
                if prev_close_val:
                    stock_data['previous_close'] = prev_close_val.get_text(strip=True)
            
            # Market cap
            market_cap = soup.find('td', string='Market Cap')
            if market_cap:
                market_cap_val = market_cap.find_next_sibling('td')
                if market_cap_val:
                    stock_data['market_cap'] = market_cap_val.get_text(strip=True)
            
            # PE Ratio
            pe_ratio = soup.find('td', string='PE Ratio (TTM)')
            if pe_ratio:
                pe_ratio_val = pe_ratio.find_next_sibling('td')
                if pe_ratio_val:
                    stock_data['pe_ratio'] = pe_ratio_val.get_text(strip=True)
            
            # 52 Week Range
            week_range = soup.find('td', string='52 Week Range')
            if week_range:
                week_range_val = week_range.find_next_sibling('td')
                if week_range_val:
                    stock_data['52_week_range'] = week_range_val.get_text(strip=True)
            
            # Company name
            company_name = soup.find('h1', class_='D(ib)')
            if company_name:
                stock_data['company_name'] = company_name.get_text(strip=True)
            
            return stock_data
            
        except Exception as e:
            print(f"Yahoo Finance scraping failed for {symbol}: {e}")
            return None
    
    def get_stock_data_moneycontrol(self, symbol: str) -> Optional[Dict]:
        """Scrape Indian stock data from MoneyControl."""
        try:
            # For Indian stocks, try MoneyControl
            self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
            
            # Search for the stock first
            search_url = f"https://www.moneycontrol.com/stocks/marketstats/indexcomp.php?optex=NSE&opttopic=indexcomp&index=9"
            time.sleep(random.uniform(1, 3))
            
            # Try direct stock page pattern
            stock_url = f"https://www.moneycontrol.com/india/stockpricequote/{symbol.lower()}"
            
            response = self.session.get(stock_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stock_data = {
                'symbol': symbol.upper(),
                'source': 'moneycontrol',
                'timestamp': time.time()
            }
            
            # Current price
            price_elem = soup.find('span', class_='span_price_wrap')
            if price_elem:
                stock_data['current_price'] = price_elem.get_text(strip=True)
            
            # Price change
            change_elems = soup.find_all('span', class_='span_price_change')
            if change_elems:
                stock_data['price_change'] = change_elems[0].get_text(strip=True) if len(change_elems) > 0 else 'N/A'
                stock_data['percent_change'] = change_elems[1].get_text(strip=True) if len(change_elems) > 1 else 'N/A'
            
            return stock_data
            
        except Exception as e:
            print(f"MoneyControl scraping failed for {symbol}: {e}")
            return None
    
    def get_financial_news(self, query: str, num_results: int = 10) -> List[Dict]:
        """Scrape financial news from multiple sources."""
        news_sources = [
            self._scrape_economic_times_news,
            self._scrape_moneycontrol_news,
            self._scrape_reuters_finance_news,
            self._scrape_bloomberg_news
        ]
        
        all_news = []
        
        for scraper in news_sources:
            try:
                news = scraper(query, num_results // len(news_sources))
                all_news.extend(news)
                time.sleep(random.uniform(1, 2))  # Be respectful
            except Exception as e:
                print(f"News scraping failed: {e}")
                continue
        
        return all_news[:num_results]
    
    def _scrape_economic_times_news(self, query: str, num_results: int) -> List[Dict]:
        """Scrape Economic Times for financial news."""
        try:
            self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
            
            search_url = f"https://economictimes.indiatimes.com/markets/stocks/news"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = []
            
            # Find news articles
            articles = soup.find_all('div', class_='eachStory')[:num_results]
            
            for article in articles:
                try:
                    title_elem = article.find('h3') or article.find('h2')
                    link_elem = article.find('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        url = link_elem.get('href', '')
                        
                        if not url.startswith('http'):
                            url = 'https://economictimes.indiatimes.com' + url
                        
                        news_items.append({
                            'title': title,
                            'url': url,
                            'source': 'Economic Times',
                            'snippet': title[:200] + '...'
                        })
                except Exception as e:
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"Economic Times scraping failed: {e}")
            return []
    
    def _scrape_moneycontrol_news(self, query: str, num_results: int) -> List[Dict]:
        """Scrape MoneyControl for financial news."""
        try:
            self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
            
            search_url = f"https://www.moneycontrol.com/news/business/markets/"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = []
            
            # Find news articles
            articles = soup.find_all('li', class_='clearfix')[:num_results]
            
            for article in articles:
                try:
                    title_elem = article.find('a')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        
                        if not url.startswith('http'):
                            url = 'https://www.moneycontrol.com' + url
                        
                        news_items.append({
                            'title': title,
                            'url': url,
                            'source': 'MoneyControl',
                            'snippet': title[:200] + '...'
                        })
                except Exception as e:
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"MoneyControl news scraping failed: {e}")
            return []
    
    def _scrape_reuters_finance_news(self, query: str, num_results: int) -> List[Dict]:
        """Scrape Reuters for financial news."""
        try:
            self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
            
            search_url = f"https://www.reuters.com/markets/"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = []
            
            # Find news articles
            articles = soup.find_all('div', class_='media-story-card__body__3tRWy')[:num_results]
            
            for article in articles:
                try:
                    title_elem = article.find('a')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        
                        if not url.startswith('http'):
                            url = 'https://www.reuters.com' + url
                        
                        news_items.append({
                            'title': title,
                            'url': url,
                            'source': 'Reuters',
                            'snippet': title[:200] + '...'
                        })
                except Exception as e:
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"Reuters scraping failed: {e}")
            return []
    
    def _scrape_bloomberg_news(self, query: str, num_results: int) -> List[Dict]:
        """Scrape Bloomberg for financial news."""
        try:
            self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
            
            search_url = f"https://www.bloomberg.com/markets"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = []
            
            # Find news articles - Bloomberg has dynamic content, so this is basic
            articles = soup.find_all('a', href=True)[:num_results*2]  # Get more to filter
            
            for article in articles:
                try:
                    href = article.get('href', '')
                    if '/news/' in href or '/opinion/' in href:
                        title = article.get_text(strip=True)
                        
                        if title and len(title) > 20:  # Filter out short non-title text
                            url = href if href.startswith('http') else 'https://www.bloomberg.com' + href
                            
                            news_items.append({
                                'title': title,
                                'url': url,
                                'source': 'Bloomberg',
                                'snippet': title[:200] + '...'
                            })
                            
                            if len(news_items) >= num_results:
                                break
                except Exception as e:
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"Bloomberg scraping failed: {e}")
            return []
    
    def get_market_indices(self) -> Dict:
        """Get major market indices data."""
        try:
            self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
            
            # Get Indian market indices
            nse_url = "https://www.nseindia.com/"
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(nse_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            indices_data = {
                'source': 'NSE India',
                'timestamp': time.time(),
                'indices': {}
            }
            
            # This would need to be adapted based on NSE's actual HTML structure
            # For now, return a placeholder structure
            indices_data['indices'] = {
                'NIFTY 50': {'value': 'N/A', 'change': 'N/A'},
                'SENSEX': {'value': 'N/A', 'change': 'N/A'},
                'BANK NIFTY': {'value': 'N/A', 'change': 'N/A'}
            }
            
            return indices_data
            
        except Exception as e:
            print(f"Market indices scraping failed: {e}")
            return {'error': str(e)}
    
    def analyze_stock_symbol(self, query: str) -> str:
        """Extract stock symbol from query text."""
        # Common Indian stock symbols
        indian_stocks = {
            'reliance': 'RELIANCE.NS',
            'tcs': 'TCS.NS',
            'infosys': 'INFY.NS',
            'hdfc': 'HDFCBANK.NS',
            'icici': 'ICICIBANK.NS',
            'sbi': 'SBIN.NS',
            'wipro': 'WIPRO.NS',
            'bharti airtel': 'BHARTIARTL.NS',
            'itc': 'ITC.NS',
            'bajaj finance': 'BAJFINANCE.NS'
        }
        
        query_lower = query.lower()
        
        for company, symbol in indian_stocks.items():
            if company in query_lower:
                return symbol
        
        # Look for explicit stock symbols
        symbol_pattern = r'\b([A-Z]{2,5}(?:\.[A-Z]{2})?)\b'
        matches = re.findall(symbol_pattern, query.upper())
        
        if matches:
            return matches[0]
        
        return None