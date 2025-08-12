'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import StockChart from '@/components/StockChart';
import StockSpeedometer from '@/components/StockSpeedometer';
import StockService, { StockData } from '@/services/stockService';

export default function StockDetailPage() {
  const params = useParams();
  const router = useRouter();
  const symbol = params.symbol as string;
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recommendation, setRecommendation] = useState(null);
  const [recommendationLoading, setRecommendationLoading] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [priceHistory, setPriceHistory] = useState<{time: string, price: number}[]>([]);

  const stockService = StockService.getInstance();

  useEffect(() => {
    loadStockData();
    loadUserProfile();
    loadHistoricalData();
    
    // Subscribe to real-time updates
    const componentId = 'stock-detail-' + symbol + '-' + Date.now();
    stockService.subscribe(componentId, (stocks) => {
      const currentStock = stocks.find(s => s.symbol === symbol);
      if (currentStock) {
        setStockData(currentStock);
        updatePriceHistory(currentStock.currentPrice);
        setLoading(false);
        setError(null);
      }
    });

    return () => {
      stockService.unsubscribe(componentId);
    };
  }, [symbol]);

  const loadStockData = async () => {
    try {
      setError(null);
      setLoading(true);
      
      // Try to load from stored data first
      const stored = localStorage.getItem('stockData');
      if (stored) {
        const { data } = JSON.parse(stored);
        const cachedStock = data.find((stock: StockData) => stock.symbol === symbol);
        if (cachedStock) {
          setStockData(cachedStock);
          setLoading(false);
        }
      }
      
      // Then fetch fresh data
      const data = await stockService.getStockDetails(symbol);
      if (data) {
        setStockData(data);
        updatePriceHistory(data.currentPrice);
      }
      setLoading(false);
    } catch (err) {
      console.error('Error fetching stock details:', err);
      setError('Failed to load stock details');
      setLoading(false);
    }
  };

  const loadUserProfile = () => {
    const savedProfile = localStorage.getItem('userRiskProfile');
    if (savedProfile) {
      setUserProfile(JSON.parse(savedProfile));
    }
  };

  const loadHistoricalData = () => {
    const historicalKey = `historical_${symbol}`;
    const stored = localStorage.getItem(historicalKey);
    if (stored) {
      const data = JSON.parse(stored);
      setHistoricalData(data);
    }
  };

  const updatePriceHistory = (price: number) => {
    const now = new Date().toLocaleTimeString();
    setPriceHistory(prev => {
      const updated = [...prev, { time: now, price }].slice(-20); // Keep last 20 points
      
      // Store price history
      localStorage.setItem(`priceHistory_${symbol}`, JSON.stringify(updated));
      return updated;
    });
  };

  const fetchAIRecommendation = async () => {
    if (!userProfile || !stockData) {
      alert('Please set up your investment profile first to get AI recommendations.');
      router.push('/');
      return;
    }

    setRecommendationLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/stocks/recommendation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol,
          userProfile,
          stockData
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch recommendation');
      }

      const recommendationData = await response.json();
      setRecommendation(recommendationData);
    } catch (err) {
      console.error('Error fetching AI recommendation:', err);
      setError('Failed to get AI recommendation');
    } finally {
      setRecommendationLoading(false);
    }
  };

  const handleBack = () => {
    router.push('/');
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const formatVolume = (volume: number) => {
    if (volume >= 10000000) return `${(volume / 10000000).toFixed(2)}Cr`;
    if (volume >= 100000) return `${(volume / 100000).toFixed(2)}L`;
    if (volume >= 1000) return `${(volume / 1000).toFixed(2)}K`;
    return volume.toString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[rgb(0,26,30)] flex items-center justify-center">
        <div className="text-center space-y-8 max-w-md">
          <div className="relative">
            <div className="w-20 h-20 border-4 border-[rgba(0,184,153,0.2)] border-t-[rgb(0,184,153)] rounded-full animate-spin mx-auto"></div>
            <div className="absolute inset-0 w-20 h-20 border-4 border-transparent border-r-[rgba(0,184,153,0.3)] rounded-full animate-spin mx-auto" style={{animationDirection: 'reverse', animationDuration: '3s'}}></div>
          </div>
          <div className="space-y-3">
            <h2 className="text-2xl font-bold text-white">Loading Stock Data</h2>
            <p className="text-gray-300 text-lg">Fetching real-time information for {symbol}...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !stockData) {
    return (
      <div className="min-h-screen bg-[rgb(0,26,30)]">
        <div className="container mx-auto px-4 pt-8">
          <button
            onClick={handleBack}
            className="mb-6 flex items-center text-[rgb(0,184,153)] hover:text-white transition-all duration-200 bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] px-4 py-2 rounded-xl shadow-md hover:shadow-lg"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </button>
          
          <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-8 text-center shadow-xl">
            <div className="w-16 h-16 bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)] rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Stock Not Found</h3>
            <p className="text-red-400 mb-4">{error || 'Unable to load stock details'}</p>
            <button
              onClick={loadStockData}
              className="px-6 py-2 bg-[rgb(0,184,153)] text-white rounded-lg hover:bg-[rgb(0,164,133)] transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[rgb(0,26,30)]">
      <div className="container mx-auto px-4 pt-8 pb-8">
        {/* Enhanced Header */}
        <div className="mb-8">
          <button
            onClick={handleBack}
            className="mb-6 flex items-center text-[rgb(0,184,153)] hover:text-white transition-all duration-200 bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] px-4 py-2 rounded-xl shadow-md hover:shadow-lg"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </button>
          
          {/* Hero Stock Info */}
          <div className="bg-gradient-to-r from-[rgb(24,25,27)] to-black border border-[rgba(0,184,153,0.2)] rounded-3xl p-8 text-white relative overflow-hidden shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-r from-[rgba(0,184,153,0.05)] to-transparent"></div>
            <div className="absolute top-0 right-0 w-64 h-64 bg-[rgba(0,184,153,0.05)] rounded-full -translate-y-32 translate-x-32"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-[rgba(0,184,153,0.03)] rounded-full translate-y-24 -translate-x-24"></div>
            <div className="relative z-10">
              <div className="flex items-start justify-between flex-wrap gap-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="px-3 py-1 bg-[rgba(0,184,153,0.2)] border border-[rgba(0,184,153,0.3)] rounded-full text-sm font-medium backdrop-blur-sm">
                      📈 {stockData.sector}
                    </div>
                    <div className={`px-3 py-1 rounded-full text-sm font-medium backdrop-blur-sm border ${
                      stockData.change >= 0 
                        ? 'bg-[rgba(0,184,153,0.2)] border-[rgba(0,184,153,0.3)]' 
                        : 'bg-[rgba(239,68,68,0.2)] border-[rgba(239,68,68,0.3)]'
                    }`}>
                      {stockData.change >= 0 ? '📈 Rising' : '📉 Falling'}
                    </div>
                  </div>
                  <div>
                    <h1 className="text-4xl font-bold leading-tight">{stockData.name}</h1>
                    <p className="text-xl text-gray-300 mt-2">{stockData.symbol}</p>
                  </div>
                </div>
                <div className="text-right space-y-2">
                  <div className="text-4xl font-bold">{formatPrice(stockData.currentPrice)}</div>
                  <div className={`text-xl font-semibold flex items-center justify-end space-x-2 ${
                    stockData.change >= 0 ? 'text-[rgb(0,184,153)]' : 'text-red-400'
                  }`}>
                    <span>{stockData.change >= 0 ? '↗' : '↘'}</span>
                    <span>
                      {stockData.change >= 0 ? '+' : ''}{formatPrice(stockData.change)} 
                      ({stockData.changePercent >= 0 ? '+' : ''}{stockData.changePercent.toFixed(2)}%)
                    </span>
                  </div>
                  <div className="flex items-center justify-end space-x-2">
                    <div className="w-2 h-2 bg-[rgb(0,184,153)] rounded-full animate-pulse"></div>
                    <span className="text-sm text-gray-300">Live data</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Key Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Open', value: formatPrice(stockData.open || 0), icon: '🔄' },
            { label: 'Previous Close', value: formatPrice(stockData.previousClose || 0), icon: '📊' },
            { label: 'Day Range', value: `${formatPrice(stockData.dayLow)} - ${formatPrice(stockData.dayHigh)}`, icon: '📈' },
            { label: 'Volume', value: formatVolume(stockData.volume), icon: '📦' }
          ].map((stat, index) => (
            <div key={index} className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-xl p-6 shadow-lg hover:shadow-xl hover:border-[rgba(0,184,153,0.5)] transition-all duration-300">
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">{stat.icon}</span>
                <div className="w-8 h-8 bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-lg flex items-center justify-center">
                  <div className="w-3 h-3 bg-[rgb(0,184,153)] rounded-full"></div>
                </div>
              </div>
              <p className="text-sm text-gray-400 mb-1">{stat.label}</p>
              <p className="text-lg font-bold text-white">{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Enhanced Chart Section */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 mb-8 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
              <span>📊</span>
              <span>Price Chart</span>
            </h2>
            <div className="flex items-center space-x-2 px-4 py-2 bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-xl">
              <div className="w-2 h-2 bg-[rgb(0,184,153)] rounded-full animate-pulse"></div>
              <span className="text-sm font-semibold text-[rgb(0,184,153)]">Real-time</span>
            </div>
          </div>
          <StockChart symbol={symbol} embedded={true} />
        </div>

        {/* AI Recommendation Section */}
        <div className="mb-8">
          <StockSpeedometer 
            recommendation={recommendation}
            loading={recommendationLoading}
            symbol={symbol}
            userProfile={userProfile}
            onAnalysisStart={fetchAIRecommendation}
            onProfileSetup={() => router.push('/')}
          />
        </div>

        {/* Enhanced Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
            <h3 className="text-xl font-bold text-white mb-6 flex items-center space-x-2">
              <span>📊</span>
              <span>Market Data</span>
            </h3>
            <div className="space-y-4">
              {[
                { label: 'Market Cap', value: stockData.marketCap, icon: '🏢' },
                { label: 'P/E Ratio', value: stockData.pe ? stockData.pe.toFixed(2) : 'N/A', icon: '📈' },
                { label: 'EPS', value: stockData.eps ? formatPrice(stockData.eps) : 'N/A', icon: '💰' },
                { label: '52 Week High', value: formatPrice(stockData.week52High || 0), icon: '⬆️' },
                { label: '52 Week Low', value: formatPrice(stockData.week52Low || 0), icon: '⬇️' }
              ].map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-[rgba(0,184,153,0.05)] border border-[rgba(0,184,153,0.1)] rounded-lg hover:bg-[rgba(0,184,153,0.1)] hover:border-[rgba(0,184,153,0.2)] transition-colors">
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{item.icon}</span>
                    <span className="text-gray-300">{item.label}</span>
                  </div>
                  <span className="font-semibold text-white">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
            <h3 className="text-xl font-bold text-white mb-6 flex items-center space-x-2">
              <span>🏢</span>
              <span>Company Information</span>
            </h3>
            <div className="space-y-4">
              {[
                { label: 'Dividend Rate', value: stockData.dividend ? formatPrice(stockData.dividend) : 'N/A', icon: '💎' },
                { label: 'Dividend Yield', value: stockData.dividendYield ? `${stockData.dividendYield.toFixed(2)}%` : 'N/A', icon: '📊' },
                { label: 'Sector', value: stockData.sector, icon: '🏭' },
                { label: 'Exchange', value: 'NSE', icon: '🏦' },
                { label: 'Currency', value: 'INR', icon: '₹' }
              ].map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-[rgba(0,184,153,0.05)] border border-[rgba(0,184,153,0.1)] rounded-lg hover:bg-[rgba(0,184,153,0.1)] hover:border-[rgba(0,184,153,0.2)] transition-colors">
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{item.icon}</span>
                    <span className="text-gray-300">{item.label}</span>
                  </div>
                  <span className="font-semibold text-white">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}