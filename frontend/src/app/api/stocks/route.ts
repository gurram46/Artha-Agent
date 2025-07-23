import { NextResponse } from 'next/server';

// Using the free GitHub NSE API - no rate limits, no API keys needed!
const NSE_API_BASE = 'https://latest-stock-price.p.rapidapi.com';
const BACKUP_API_BASE = 'https://api.kite.trade'; // Backup API

// Stock symbol mapping for NSE
const STOCK_SYMBOLS: { [key: string]: string } = {
  'RELIANCE.NS': 'RELIANCE',
  'TCS.NS': 'TCS',
  'HDFCBANK.NS': 'HDFCBANK',
  'INFY.NS': 'INFY',
  'ICICIBANK.NS': 'ICICIBANK',
  'BHARTIARTL.NS': 'BHARTIARTL',
  'ITC.NS': 'ITC',
  'WIPRO.NS': 'WIPRO',
  'AXISBANK.NS': 'AXISBANK',
  'MARUTI.NS': 'MARUTI',
};

// Function to fetch data using stock-market-india API approach
async function fetchNSEData(symbol: string) {
  try {
    const nseSymbol = STOCK_SYMBOLS[symbol] || symbol.replace('.NS', '');
    
    // Method 1: Try stock-market-india API structure
    try {
      const stockMarketResponse = await fetch(
        `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?metrics=high?&interval=1d&range=1d`,
        {
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          },
        }
      );

      if (stockMarketResponse.ok) {
        const data = await stockMarketResponse.json();
        if (data?.chart?.result?.[0]) {
          const result = data.chart.result[0];
          const meta = result.meta;
          const quote = result.indicators?.quote?.[0];
          const timestamps = result.timestamp || [];
          
          if (meta && timestamps.length > 0) {
            const lastIndex = timestamps.length - 1;
            console.log('Yahoo Finance API response for', symbol, ':', {
              symbol: meta.symbol,
              price: meta.regularMarketPrice,
              change: meta.regularMarketPrice - meta.previousClose
            });
            
            return {
              symbol: meta.symbol,
              regularMarketPrice: meta.regularMarketPrice || 0,
              regularMarketChange: (meta.regularMarketPrice || 0) - (meta.previousClose || 0),
              regularMarketChangePercent: ((meta.regularMarketPrice || 0) - (meta.previousClose || 0)) / (meta.previousClose || 1) * 100,
              regularMarketVolume: quote?.volume?.[lastIndex] || 0,
              regularMarketOpen: quote?.open?.[lastIndex] || meta.regularMarketPrice || 0,
              regularMarketPreviousClose: meta.previousClose || 0,
              regularMarketDayHigh: meta.regularMarketDayHigh || quote?.high?.[lastIndex] || 0,
              regularMarketDayLow: meta.regularMarketDayLow || quote?.low?.[lastIndex] || 0,
              marketCap: meta.marketCap || 0,
              longName: meta.longName || meta.symbol || nseSymbol,
              shortName: meta.shortName || meta.symbol || nseSymbol,
            };
          }
        }
      }
    } catch (error) {
      console.log('Yahoo Finance failed for', symbol, ':', error);
    }
    
    // Method 2: Try NSE direct API as fallback
    try {
      const nseResponse = await fetch(
        `https://www.nseindia.com/api/quote-equity?symbol=${nseSymbol}`,
        {
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.nseindia.com/',
            'X-Requested-With': 'XMLHttpRequest',
          },
        }
      );

      if (nseResponse.ok) {
        const nseData = await nseResponse.json();
        console.log('NSE API response for', symbol, ':', nseData);
        return nseData;
      }
    } catch (error) {
      console.log('NSE API also failed for', symbol, ':', error);
    }
  } catch (error) {
    console.log('All APIs failed for', symbol, ':', error);
  }
  
  return null;
}

// Removed mock data generation - we only use real NSE data now

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const symbols = searchParams.get('symbols');
  
  if (!symbols) {
    return NextResponse.json({ error: 'No symbols provided' }, { status: 400 });
  }

  console.log('Fetching real-time NSE stock data for symbols:', symbols);

  try {
    const symbolArray = symbols.split(',');
    const stockData = [];

    // Process all symbols concurrently for speed
    const promises = symbolArray.map(async (symbol) => {
      const trimmedSymbol = symbol.trim();
      
      // Try to get real NSE data first
      const realData = await fetchNSEData(trimmedSymbol);
      
      if (realData) {
        // Handle both Yahoo Finance and NSE API response formats
        if (realData.priceInfo) {
          // NSE API response format
          const priceInfo = realData.priceInfo;
          const securityInfo = realData.securityInfo || {};
          const industryInfo = realData.industryInfo || {};
          
          const issuedSize = parseFloat(securityInfo.issuedSize) || 0;
          const currentPrice = parseFloat(priceInfo.lastPrice) || 0;
          const realMarketCap = issuedSize * currentPrice;
          
          return {
            symbol: trimmedSymbol,
            longName: securityInfo.companyName || trimmedSymbol.replace('.NS', ''),
            shortName: trimmedSymbol.replace('.NS', ''),
            regularMarketPrice: parseFloat(priceInfo.lastPrice) || 0,
            regularMarketChange: parseFloat(priceInfo.change) || 0,
            regularMarketChangePercent: parseFloat(priceInfo.pChange) || 0,
            regularMarketVolume: parseInt(priceInfo.totalTradedVolume) || 0,
            regularMarketOpen: parseFloat(priceInfo.open) || 0,
            regularMarketPreviousClose: parseFloat(priceInfo.previousClose) || 0,
            regularMarketDayHigh: parseFloat(priceInfo.intraDayHighLow?.max) || 0,
            regularMarketDayLow: parseFloat(priceInfo.intraDayHighLow?.min) || 0,
            marketCap: realMarketCap > 0 ? realMarketCap : undefined,
            trailingPE: priceInfo.pe ? parseFloat(priceInfo.pe) : undefined,
            epsTrailingTwelveMonths: priceInfo.eps ? parseFloat(priceInfo.eps) : undefined,
            fiftyTwoWeekHigh: parseFloat(priceInfo.weekHighLow?.max) || 0,
            fiftyTwoWeekLow: parseFloat(priceInfo.weekHighLow?.min) || 0,
            dividendRate: undefined,
            dividendYield: undefined,
            sector: industryInfo.basicIndustry || industryInfo.industry || 'Others',
          };
        } else {
          // Yahoo Finance API response format
          return {
            symbol: realData.symbol || trimmedSymbol,
            longName: realData.longName || trimmedSymbol.replace('.NS', ''),
            shortName: realData.shortName || trimmedSymbol.replace('.NS', ''),
            regularMarketPrice: realData.regularMarketPrice || 0,
            regularMarketChange: realData.regularMarketChange || 0,
            regularMarketChangePercent: realData.regularMarketChangePercent || 0,
            regularMarketVolume: realData.regularMarketVolume || 0,
            regularMarketOpen: realData.regularMarketOpen || 0,
            regularMarketPreviousClose: realData.regularMarketPreviousClose || 0,
            regularMarketDayHigh: realData.regularMarketDayHigh || 0,
            regularMarketDayLow: realData.regularMarketDayLow || 0,
            marketCap: realData.marketCap || undefined,
            trailingPE: undefined,
            epsTrailingTwelveMonths: undefined,
            fiftyTwoWeekHigh: 0,
            fiftyTwoWeekLow: 0,
            dividendRate: undefined,
            dividendYield: undefined,
            sector: 'Others', // Will be determined by symbol mapping
          };
        }
      } else {
        // If no real data available, return null
        console.log('No real data available for', trimmedSymbol);
        return null;
      }
    });

    const results = await Promise.all(promises);
    // Filter out null results (stocks with no real data)
    const validResults = results.filter(result => result !== null);
    stockData.push(...validResults);

    console.log(`Successfully fetched data for ${stockData.length} stocks`);

    // Return in Yahoo Finance format for compatibility
    return NextResponse.json({
      quoteResponse: {
        result: stockData,
        error: null
      }
    });

  } catch (error) {
    console.error('Error fetching stock data:', error);
    return NextResponse.json({ 
      error: 'Failed to fetch stock data', 
      details: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 });
  }
}