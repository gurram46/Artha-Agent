interface StockData {
  symbol: string;
  name: string;
  sector: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: string;
  dayHigh: number;
  dayLow: number;
  open?: number;
  previousClose?: number;
  pe?: number;
  eps?: number;
  week52High?: number;
  week52Low?: number;
  dividend?: number;
  dividendYield?: number;
}

interface ChartData {
  time: string;
  price: number;
  volume: number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
}

class StockService {
  private static instance: StockService;
  private priceUpdateInterval: NodeJS.Timeout | null = null;
  private subscribers: Map<string, (data: StockData[]) => void> = new Map();
  private lastFetchTime: number = 0;
  private cachedData: StockData[] = [];
  private isClient: boolean = false;
  private fetchInProgress: boolean = false;

  private constructor() {
    this.isClient = typeof window !== 'undefined';
    // Don't start updates automatically - only when first subscriber is added
  }

  static getInstance(): StockService {
    if (!StockService.instance) {
      StockService.instance = new StockService();
    }
    return StockService.instance;
  }

  private startPriceUpdates() {
    // Prevent multiple intervals
    if (this.priceUpdateInterval) {
      return;
    }
    
    // Fetch immediately on start
    this.fetchRealTimeData();
    
    // Update every 5 minutes during market hours
    this.priceUpdateInterval = setInterval(() => {
      this.fetchRealTimeData();
    }, 5 * 60 * 1000); // 5 minutes instead of 30 seconds
  }

  private async fetchRealTimeData() {
    try {
      // Prevent concurrent fetches
      if (this.fetchInProgress) {
        console.log('🔄 Fetch already in progress, skipping...');
        return;
      }

      // Only fetch if more than 2 minutes have passed to prevent spam
      if (Date.now() - this.lastFetchTime < 120000 && this.cachedData.length > 0) {
        this.notifySubscribers();
        return;
      }

      this.fetchInProgress = true;

      const realData = await this.getTopIndianStocksFromProxy();
      
      if (realData && realData.length > 0) {
        this.cachedData = realData;
        this.lastFetchTime = Date.now();
        
        // Store data in localStorage for persistence
        if (this.isClient) {
          localStorage.setItem('stockData', JSON.stringify({
            data: realData,
            timestamp: Date.now()
          }));
        }
        
        this.notifySubscribers();
        console.log(`✅ Updated ${realData.length} stocks from proxy API`);
      } else {
        console.warn('⚠️ No data received from proxy API');
        throw new Error('Proxy API returned no data');
      }
    } catch (error) {
      console.error('❌ Failed to fetch real-time data from proxy:', error);
      
      // If rate limited, stop polling for a while
      if (error instanceof Error && error.message.includes('Rate limit exceeded')) {
        console.warn('⚠️ Rate limited - stopping polling temporarily');
        if (this.priceUpdateInterval) {
          clearInterval(this.priceUpdateInterval);
          this.priceUpdateInterval = null;
          // Restart after 2 minutes
          setTimeout(() => {
            if (this.subscribers.size > 0) {
              this.startPriceUpdates();
            }
          }, 2 * 60 * 1000);
        }
      }
      
      // Try to load from localStorage as fallback
      if (this.isClient && this.cachedData.length === 0) {
        this.loadFromStorage();
      }
      
      throw error;
    } finally {
      this.fetchInProgress = false;
    }
  }

  private loadFromStorage() {
    try {
      const stored = localStorage.getItem('stockData');
      if (stored) {
        const { data, timestamp } = JSON.parse(stored);
        // Use stored data if it's less than 5 minutes old
        if (Date.now() - timestamp < 5 * 60 * 1000) {
          this.cachedData = data;
          this.lastFetchTime = timestamp;
          this.notifySubscribers();
          console.log('📱 Loaded stock data from storage');
        }
      }
    } catch (error) {
      console.error('Error loading from storage:', error);
    }
  }

  private async getTopIndianStocksFromProxy(): Promise<StockData[]> {
    try {
      console.log('🔄 Fetching real-time data for top 10 Indian stocks from proxy...');

      // Only make fetch calls from client side
      if (!this.isClient) {
        throw new Error('Server-side fetch not supported');
      }

      const response = await fetch('/api/stocks/proxy?action=top-stocks', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(30000) // Increased to 30 seconds
      });

      if (!response.ok) {
        if (response.status === 429) {
          console.warn('⚠️ Rate limit exceeded, using cached data if available');
          throw new Error('Rate limit exceeded. Using cached data.');
        }
        throw new Error(`Proxy API returned ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      if (!result.success || !result.data) {
        throw new Error(result.error || 'Invalid response from proxy API');
      }

      console.log(`✅ Successfully fetched ${result.data.length} stocks from proxy (${result.source})`);
      return result.data;

    } catch (error) {
      console.error('❌ Error fetching stocks from proxy:', error);
      throw error;
    }
  }

  private notifySubscribers() {
    this.subscribers.forEach(callback => callback(this.cachedData));
  }

  subscribe(id: string, callback: (data: StockData[]) => void) {
    this.subscribers.set(id, callback);
    
    // Start polling only when first subscriber is added
    if (this.subscribers.size === 1 && this.isClient && !this.priceUpdateInterval) {
      this.startPriceUpdates();
    }
  }

  unsubscribe(id: string) {
    this.subscribers.delete(id);
    
    // Stop polling when no more subscribers
    if (this.subscribers.size === 0 && this.priceUpdateInterval) {
      clearInterval(this.priceUpdateInterval);
      this.priceUpdateInterval = null;
    }
  }

  async getTopStocks(): Promise<StockData[]> {
    try {
      // If not client-side, return cached data immediately
      if (!this.isClient) {
        if (this.cachedData.length > 0) {
          return this.cachedData;
        }
        // Return empty array instead of throwing error on server side
        return [];
      }

      // Load from storage first if cache is empty
      if (this.cachedData.length === 0) {
        this.loadFromStorage();
      }

      // Check if we have recent cached data first
      if (this.cachedData.length > 0 && (Date.now() - this.lastFetchTime < 120000)) {
        return this.cachedData;
      }

      // Prevent concurrent calls
      if (this.fetchInProgress) {
        console.log('🔄 Fetch already in progress, returning cached data');
        return this.cachedData.length > 0 ? this.cachedData : [];
      }

      // Try to get fresh data with timeout handling
      try {
        const realData = await this.getTopIndianStocksFromProxy();
        
        if (realData && realData.length > 0) {
          this.cachedData = realData;
          this.lastFetchTime = Date.now();
          return realData;
        }
      } catch (fetchError) {
        console.warn('⚠️ Failed to fetch fresh data, using fallback:', fetchError);
        // Continue to fallback options below
      }
      
      // If no real data and we have cached data, return it
      if (this.cachedData.length > 0) {
        console.log('⚠️ Using cached stock data');
        return this.cachedData;
      }
      
      // Try loading from storage as last resort
      if (this.isClient) {
        this.loadFromStorage();
        if (this.cachedData.length > 0) {
          console.log('📱 Loaded stock data from storage as fallback');
          return this.cachedData;
        }
      }
      
      // Return empty array instead of throwing error to prevent blocking UI
      console.warn('⚠️ No stock data available, returning empty array');
      return [];
      
    } catch (error) {
      console.error('❌ Failed to fetch top stocks:', error);
      
      // Return cached data if available
      if (this.cachedData.length > 0) {
        console.log('⚠️ Error occurred, using cached data');
        return this.cachedData;
      }
      
      // Try loading from storage as last resort
      if (this.isClient) {
        this.loadFromStorage();
        if (this.cachedData.length > 0) {
          console.log('📱 Loaded stock data from storage as fallback');
          return this.cachedData;
        }
      }
      
      // Return empty array instead of throwing error to prevent blocking UI
      console.warn('⚠️ All fallbacks failed, returning empty array');
      return [];
    }
  }

  async getStockDetails(symbol: string): Promise<StockData | null> {
    try {
      console.log(`🔄 Fetching details for ${symbol} from proxy...`);
      
      // Only make fetch calls from client side
      if (!this.isClient) {
        // Try to find in cached data first
        const cachedStock = this.cachedData.find(stock => stock.symbol === symbol);
        return cachedStock || null;
      }
      
      const response = await fetch(`/api/stocks/proxy?action=quote&symbol=${symbol}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(20000) // Increased to 20 seconds
      });

      if (!response.ok) {
        throw new Error(`Proxy API returned ${response.status} for ${symbol}`);
      }

      const result = await response.json();
      
      if (!result.success || !result.data) {
        throw new Error(result.error || `No data for ${symbol}`);
      }

      console.log(`✅ Successfully fetched details for ${symbol}`);
      return result.data;
      
    } catch (error) {
      console.error(`❌ Failed to fetch stock details for ${symbol}:`, error);
      return null;
    }
  }

  async getStockChartData(symbol: string, timeRange: string): Promise<ChartData[]> {
    try {
      console.log(`🔄 Fetching chart data for ${symbol} (${timeRange}) from proxy...`);
      
      // Only make fetch calls from client side
      if (!this.isClient) {
        return [];
      }
      
      const response = await fetch(`/api/stocks/proxy?action=chart&symbol=${symbol}&timeRange=${timeRange}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(15000)
      });

      if (!response.ok) {
        throw new Error(`Chart data API returned ${response.status}`);
      }

      const result = await response.json();
      
      if (!result.success || !result.data) {
        throw new Error(result.error || 'No chart data available');
      }
      
      console.log(`✅ Received ${result.data.length} chart data points for ${symbol}`);
      return result.data;
      
    } catch (error) {
      console.error(`❌ Failed to fetch chart data for ${symbol}:`, error);
      throw new Error(`Chart data unavailable for ${symbol}: ${error.message}`);
    }
  }

  destroy() {
    if (this.priceUpdateInterval) {
      clearInterval(this.priceUpdateInterval);
    }
    this.subscribers.clear();
  }
}

export default StockService;
export type { StockData, ChartData };