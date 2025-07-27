import { NextResponse } from 'next/server';

/**
 * Stock Data Proxy API
 * This proxy server fetches real NSE data and serves it to the frontend
 * to avoid CORS issues when calling NSE APIs directly from the browser
 */

// Alternative free NSE data sources that support server-side requests
const NSE_DATA_SOURCES = [
  'https://query1.finance.yahoo.com/v8/finance/chart/', // Yahoo Finance for Indian stocks
  'https://api.polygon.io/v2/aggs/ticker/', // Polygon (has free tier)
  'https://query2.finance.yahoo.com/v1/finance/search' // Yahoo search
];

interface StockQuote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap?: string;
  dayHigh?: number;
  dayLow?: number;
  open?: number;
  previousClose?: number;
}

// Top 10 Indian stocks with NSE symbols
const TOP_INDIAN_STOCKS = [
  { symbol: 'TCS.NS', name: 'Tata Consultancy Services', sector: 'Information Technology' },
  { symbol: 'RELIANCE.NS', name: 'Reliance Industries', sector: 'Oil & Gas' },
  { symbol: 'HDFCBANK.NS', name: 'HDFC Bank', sector: 'Banking' },
  { symbol: 'INFY.NS', name: 'Infosys', sector: 'Information Technology' },
  { symbol: 'ICICIBANK.NS', name: 'ICICI Bank', sector: 'Banking' },
  { symbol: 'BHARTIARTL.NS', name: 'Bharti Airtel', sector: 'Telecommunications' },
  { symbol: 'ITC.NS', name: 'ITC Limited', sector: 'FMCG' },
  { symbol: 'WIPRO.NS', name: 'Wipro', sector: 'Information Technology' },
  { symbol: 'AXISBANK.NS', name: 'Axis Bank', sector: 'Banking' },
  { symbol: 'MARUTI.NS', name: 'Maruti Suzuki', sector: 'Automobile' }
];

async function fetchFromYahooFinance(symbol: string): Promise<StockQuote | null> {
  try {
    const response = await fetch(
      `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=1d`,
      {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          'Accept': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Yahoo Finance API returned ${response.status}`);
    }

    const data = await response.json();
    const result = data.chart?.result?.[0];
    
    if (!result) {
      throw new Error('No data in Yahoo Finance response');
    }

    const meta = result.meta;
    const quote = result.indicators?.quote?.[0];
    
    if (!meta || !quote) {
      throw new Error('Invalid data structure in Yahoo Finance response');
    }

    // Get the latest values
    const prices = quote.close || [];
    const volumes = quote.volume || [];
    const highs = quote.high || [];
    const lows = quote.low || [];
    const opens = quote.open || [];
    
    const latestIndex = prices.length - 1;
    const currentPrice = prices[latestIndex] || meta.regularMarketPrice || 0;
    const previousClose = meta.previousClose || 0;
    const change = currentPrice - previousClose;
    const changePercent = previousClose > 0 ? (change / previousClose * 100) : 0;

    return {
      symbol: symbol,
      name: meta.longName || symbol.replace('.NS', ''),
      price: currentPrice,
      change: change,
      changePercent: changePercent,
      volume: volumes[latestIndex] || 0,
      marketCap: meta.marketCap ? formatMarketCap(meta.marketCap) : 'N/A',
      dayHigh: highs[latestIndex] || meta.regularMarketDayHigh || 0,
      dayLow: lows[latestIndex] || meta.regularMarketDayLow || 0,
      open: opens[latestIndex] || meta.regularMarketOpen || 0,
      previousClose: previousClose
    };

  } catch (error) {
    console.error(`Error fetching ${symbol} from Yahoo Finance:`, error);
    return null;
  }
}

function formatMarketCap(marketCap: number): string {
  if (marketCap >= 1e12) return `₹${(marketCap / 1e12).toFixed(2)}T`;
  if (marketCap >= 1e9) return `₹${(marketCap / 1e9).toFixed(2)}B`;
  if (marketCap >= 1e6) return `₹${(marketCap / 1e6).toFixed(2)}M`;
  return `₹${marketCap}`;
}

// Rate limiting configuration
const requestCounts = new Map<string, { count: number; resetTime: number }>();
const RATE_LIMIT = 5; // requests per minute
const RATE_WINDOW = 60 * 1000; // 1 minute

// Caching configuration
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_DURATION = 30 * 1000; // 30 seconds for real-time data

function getRateLimitKey(request: Request): string {
  return request.headers.get('x-forwarded-for') || 
         request.headers.get('x-real-ip') || 
         'unknown';
}

function checkRateLimit(key: string): boolean {
  const now = Date.now();
  const userLimit = requestCounts.get(key);
  
  if (!userLimit || now > userLimit.resetTime) {
    requestCounts.set(key, { count: 1, resetTime: now + RATE_WINDOW });
    return true;
  }
  
  if (userLimit.count >= RATE_LIMIT) {
    return false;
  }
  
  userLimit.count++;
  return true;
}

function getCachedData(key: string): any | null {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  return null;
}

function setCachedData(key: string, data: any): void {
  cache.set(key, { data, timestamp: Date.now() });
}

// GET endpoint for fetching stock data
export async function GET(request: Request) {
  try {
    // Rate limiting check
    const rateLimitKey = getRateLimitKey(request);
    if (!checkRateLimit(rateLimitKey)) {
      return NextResponse.json(
        { 
          error: 'Rate limit exceeded. Please wait before making more requests.',
          success: false 
        },
        { status: 429 }
      );
    }

    const { searchParams } = new URL(request.url);
    const symbol = searchParams.get('symbol');
    const action = searchParams.get('action') || 'quote';

    console.log(`🔄 Stock proxy API called - Action: ${action}, Symbol: ${symbol}`);

    if (action === 'top-stocks') {
      // Check cache first
      const cacheKey = 'top-stocks';
      const cachedData = getCachedData(cacheKey);
      if (cachedData) {
        console.log('✅ Serving cached top stocks data');
        return NextResponse.json(cachedData);
      }

      // Fetch top 10 Indian stocks
      console.log('📊 Fetching top 10 Indian stocks via proxy...');
      
      const stockPromises = TOP_INDIAN_STOCKS.map(async (stock) => {
        const quote = await fetchFromYahooFinance(stock.symbol);
        if (quote) {
          return {
            symbol: stock.symbol,
            name: stock.name,
            sector: stock.sector,
            currentPrice: quote.price,
            change: quote.change,
            changePercent: quote.changePercent,
            volume: quote.volume,
            marketCap: quote.marketCap || 'N/A',
            dayHigh: quote.dayHigh || 0,
            dayLow: quote.dayLow || 0,
            open: quote.open || 0,
            previousClose: quote.previousClose || 0
          };
        }
        return null;
      });

      const results = await Promise.allSettled(stockPromises);
      const validStocks = results
        .filter(result => result.status === 'fulfilled' && result.value !== null)
        .map(result => (result as PromiseFulfilledResult<any>).value);

      if (validStocks.length === 0) {
        throw new Error('No stock data could be fetched');
      }

      console.log(`✅ Successfully fetched ${validStocks.length} stocks via proxy`);
      
      const responseData = {
        success: true,
        data: validStocks,
        source: 'Yahoo Finance via Proxy',
        timestamp: new Date().toISOString()
      };

      // Cache the response
      setCachedData(cacheKey, responseData);
      
      return NextResponse.json(responseData);

    } else if (action === 'quote' && symbol) {
      // Fetch single stock quote
      console.log(`📈 Fetching quote for ${symbol} via proxy...`);
      
      const quote = await fetchFromYahooFinance(symbol);
      
      if (!quote) {
        throw new Error(`Unable to fetch data for ${symbol}`);
      }

      // Find sector information from our predefined list
      const stockInfo = TOP_INDIAN_STOCKS.find(stock => stock.symbol === symbol);
      
      // Transform to match frontend interface
      const stockData = {
        symbol: quote.symbol,
        name: quote.name,
        sector: stockInfo?.sector || 'Unknown',
        currentPrice: quote.price,
        change: quote.change,
        changePercent: quote.changePercent,
        volume: quote.volume,
        marketCap: quote.marketCap || 'N/A',
        dayHigh: quote.dayHigh || 0,
        dayLow: quote.dayLow || 0,
        open: quote.open || 0,
        previousClose: quote.previousClose || 0,
        pe: null, // Will be calculated from additional data if available
        eps: null,
        week52High: null,
        week52Low: null,
        dividend: null,
        dividendYield: null
      };

      console.log(`✅ Successfully fetched quote for ${symbol}`);
      
      return NextResponse.json({
        success: true,
        data: stockData,
        source: 'Yahoo Finance via Proxy',
        timestamp: new Date().toISOString()
      });

    } else if (action === 'chart' && symbol) {
      // Fetch chart data for a symbol
      const timeRange = searchParams.get('timeRange') || '1d';
      
      console.log(`📊 Fetching chart data for ${symbol} (${timeRange}) via proxy...`);
      
      // Convert timeRange to Yahoo Finance format
      const rangeMap: { [key: string]: string } = {
        '1D': '1d',
        '1W': '5d', 
        '1M': '1mo',
        '3M': '3mo',
        '1Y': '1y'
      };
      
      const yahooRange = rangeMap[timeRange] || '1d';
      
      try {
        const response = await fetch(
          `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?interval=1d&range=${yahooRange}`,
          {
            headers: {
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
              'Accept': 'application/json',
            },
          }
        );

        if (!response.ok) {
          throw new Error(`Chart data API returned ${response.status}`);
        }

        const data = await response.json();
        const result = data.chart?.result?.[0];
        
        if (!result) {
          throw new Error('No chart data available');
        }

        const timestamps = result.timestamp || [];
        const quote = result.indicators?.quote?.[0] || {};
        const closes = quote.close || [];
        const opens = quote.open || [];
        const highs = quote.high || [];
        const lows = quote.low || [];
        const volumes = quote.volume || [];

        const chartData = timestamps.map((timestamp: number, index: number) => {
          const date = new Date(timestamp * 1000);
          const timeString = timeRange === '1D' 
            ? date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
            : date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            
          return {
            time: timeString,
            price: closes[index] || 0,
            volume: volumes[index] || 0,
            open: opens[index] || 0,
            high: highs[index] || 0,
            low: lows[index] || 0,
            close: closes[index] || 0
          };
        }).filter((point: any) => point.price > 0);

        console.log(`✅ Successfully fetched ${chartData.length} chart points for ${symbol}`);
        
        return NextResponse.json({
          success: true,
          data: chartData,
          source: 'Yahoo Finance via Proxy',
          timestamp: new Date().toISOString()
        });

      } catch (error) {
        console.error(`Chart data error for ${symbol}:`, error);
        throw new Error(`Failed to fetch chart data: ${error.message}`);
      }

    } else {
      return NextResponse.json(
        { error: 'Invalid action or missing symbol parameter' },
        { status: 400 }
      );
    }

  } catch (error) {
    console.error('❌ Stock proxy API error:', error);
    return NextResponse.json(
      { 
        error: 'Stock data proxy failed',
        details: error instanceof Error ? error.message : 'Unknown error',
        success: false
      },
      { status: 500 }
    );
  }
}

// POST endpoint for batch requests
export async function POST(request: Request) {
  try {
    const { symbols, action } = await request.json();

    if (!symbols || !Array.isArray(symbols)) {
      return NextResponse.json(
        { error: 'symbols array is required' },
        { status: 400 }
      );
    }

    console.log(`🔄 Batch stock request for ${symbols.length} symbols`);

    const results = await Promise.allSettled(
      symbols.map((symbol: string) => fetchFromYahooFinance(symbol))
    );

    const validQuotes = results
      .filter(result => result.status === 'fulfilled' && result.value !== null)
      .map(result => (result as PromiseFulfilledResult<StockQuote>).value);

    return NextResponse.json({
      success: true,
      data: validQuotes,
      source: 'Yahoo Finance via Proxy',
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Batch stock request error:', error);
    return NextResponse.json(
      { 
        error: 'Batch request failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}