import { NextResponse } from 'next/server';

// Generate realistic chart data respecting NSE market hours (9:15 AM to 3:30 PM IST)
function generateChartData(symbol: string, range: string) {
  // Base prices for major Indian stocks
  const basePrices: { [key: string]: number } = {
    'RELIANCE.NS': 2456.75,
    'TCS.NS': 3567.90,
    'HDFCBANK.NS': 1623.45,
    'INFY.NS': 1456.30,
    'ICICIBANK.NS': 987.65,
    'BHARTIARTL.NS': 856.20,
    'ITC.NS': 434.75,
    'WIPRO.NS': 456.90,
    'AXISBANK.NS': 1123.45,
    'MARUTI.NS': 10234.50,
  };

  const basePrice = basePrices[symbol] || 1000;
  const timestamps: number[] = [];
  const quotes = {
    open: [] as number[],
    high: [] as number[],
    low: [] as number[],
    close: [] as number[],
    volume: [] as number[],
  };

  let currentPrice = basePrice;
  const volatility = range === '1d' ? 0.005 : range === '5d' ? 0.01 : 0.02;
  const trend = (Math.random() - 0.5) * 0.001; // Small overall trend

  if (range === '1d') {
    // For 1 day, generate data only during market hours (9:15 AM to 3:30 PM IST)
    const today = new Date();
    const marketOpen = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 9, 15, 0); // 9:15 AM
    const marketClose = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 15, 30, 0); // 3:30 PM
    
    // Generate data points every 5 minutes during market hours
    const intervalMs = 5 * 60 * 1000; // 5 minutes
    const totalMarketTimeMs = marketClose.getTime() - marketOpen.getTime();
    const dataPoints = Math.floor(totalMarketTimeMs / intervalMs);

    for (let i = 0; i <= dataPoints; i++) {
      const timestamp = Math.floor((marketOpen.getTime() + i * intervalMs) / 1000);
      timestamps.push(timestamp);

      // Simulate realistic price movement
      const priceChange = (Math.random() - 0.5) * volatility * currentPrice + trend * currentPrice;
      const open = currentPrice;
      currentPrice = Math.max(0, currentPrice + priceChange);
      
      const high = Math.max(open, currentPrice) * (1 + Math.random() * 0.005);
      const low = Math.min(open, currentPrice) * (1 - Math.random() * 0.005);
      const close = currentPrice;
      const volume = Math.floor(Math.random() * 1000000) + 100000;

      quotes.open.push(Math.round(open * 100) / 100);
      quotes.high.push(Math.round(high * 100) / 100);
      quotes.low.push(Math.round(low * 100) / 100);
      quotes.close.push(Math.round(close * 100) / 100);
      quotes.volume.push(volume);
    }
  } else {
    // For longer ranges, generate daily data
    const dataPoints = range === '5d' ? 5 : 
                      range === '1mo' ? 30 : 
                      range === '3mo' ? 90 : 
                      range === '6mo' ? 180 : 
                      range === '1y' ? 250 : 1000;

    const now = Date.now();
    const intervalMs = 86400 * 1000; // 1 day

    for (let i = 0; i < dataPoints; i++) {
      const date = new Date(now - (dataPoints - i - 1) * intervalMs);
      // Skip weekends for stock data
      if (date.getDay() === 0 || date.getDay() === 6) continue;
      
      // Set time to market close (3:30 PM IST)
      const timestamp = Math.floor(new Date(date.getFullYear(), date.getMonth(), date.getDate(), 15, 30, 0).getTime() / 1000);
      timestamps.push(timestamp);

      // Simulate realistic price movement
      const priceChange = (Math.random() - 0.5) * volatility * currentPrice + trend * currentPrice;
      const open = currentPrice;
      currentPrice = Math.max(0, currentPrice + priceChange);
      
      const high = Math.max(open, currentPrice) * (1 + Math.random() * 0.01);
      const low = Math.min(open, currentPrice) * (1 - Math.random() * 0.01);
      const close = currentPrice;
      const volume = Math.floor(Math.random() * 5000000) + 500000;

      quotes.open.push(Math.round(open * 100) / 100);
      quotes.high.push(Math.round(high * 100) / 100);
      quotes.low.push(Math.round(low * 100) / 100);
      quotes.close.push(Math.round(close * 100) / 100);
      quotes.volume.push(volume);
    }
  }

  return { timestamps, quotes };
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const symbol = searchParams.get('symbol');
  const range = searchParams.get('range') || '1d';
  const interval = searchParams.get('interval') || '5m';
  
  if (!symbol) {
    return NextResponse.json({ error: 'No symbol provided' }, { status: 400 });
  }

  console.log('Generating chart data for:', symbol, 'range:', range, 'interval:', interval);

  try {
    // Try to fetch real NSE chart data (this would require more complex implementation)
    // For now, generate realistic-looking data that updates in real-time
    const { timestamps, quotes } = generateChartData(symbol, range);

    // Add a small delay to simulate API call
    await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200));

    // Return in Yahoo Finance chart format for compatibility
    const chartResponse = {
      chart: {
        result: [{
          meta: {
            symbol: symbol,
            exchangeName: 'NSE',
            instrumentType: 'EQUITY',
            firstTradeDate: timestamps[0],
            regularMarketTime: timestamps[timestamps.length - 1],
            gmtoffset: 19800, // IST offset (5.5 hours)
            timezone: 'IST',
            exchangeTimezoneName: 'Asia/Kolkata',
            regularMarketPrice: quotes.close[quotes.close.length - 1],
            currency: 'INR',
            range: range,
          },
          timestamp: timestamps,
          indicators: {
            quote: [quotes]
          }
        }],
        error: null
      }
    };
    
    return NextResponse.json(chartResponse);

  } catch (error) {
    console.error('Error generating chart data:', error);
    return NextResponse.json({ 
      error: 'Failed to generate chart data', 
      details: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 });
  }
}