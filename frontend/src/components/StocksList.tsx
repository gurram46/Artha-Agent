'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import StockService, { StockData } from '../services/stockService';

interface StocksListProps {
  // No props needed - always navigate to separate page
}

export default function StocksList({}: StocksListProps = {}) {
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const stockService = StockService.getInstance();
  const router = useRouter();

  useEffect(() => {
    const componentId = 'stocks-list-' + Date.now();
    
    // Initial fetch
    fetchStockData();
    
    // Subscribe to real-time updates
    stockService.subscribe(componentId, (updatedStocks) => {
      setStocks(updatedStocks);
      setLoading(false);
    });

    return () => {
      stockService.unsubscribe(componentId);
    };
  }, []);

  const fetchStockData = async () => {
    try {
      setError(null);
      const data = await stockService.getTopStocks();
      setStocks(data);
      setLoading(false);
      
      // If no data but no error, show a gentle message
      if (data.length === 0) {
        setError('Stock data temporarily unavailable. Please try again later.');
      }
    } catch (err) {
      console.error('Stock fetch error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Stock data temporarily unavailable: ${errorMessage}`);
      setLoading(false);
      setStocks([]);
    }
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

  const handleStockClick = (symbol: string) => {
    // Always navigate to stock detail page
    router.push(`/stocks/${symbol}`);
  };

  if (loading) {
    return (
      <div className="bg-[rgb(24,25,27)] rounded-2xl border border-[rgba(204,166,149,0.2)] p-8 shadow-xl">
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#cca695]"></div>
          <div className="text-center">
            <p className="text-white font-medium">Loading Real-Time Stock Data</p>
            <p className="text-sm text-gray-300 mt-1">Fetching live NSE prices...</p>
            <p className="text-xs text-gray-400 mt-2">Unlimited updates • No rate limits • Real-time data</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || (stocks.length === 0 && !loading)) {
    return (
      <div className="bg-[rgb(24,25,27)] rounded-2xl border border-[rgba(204,166,149,0.2)] p-6 shadow-xl">
        <div className="text-center">
          <div className="w-12 h-12 bg-[rgba(220,53,69,0.1)] border border-[rgba(220,53,69,0.3)] rounded-xl flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-sm font-semibold text-red-400 mb-2">Stock Data Unavailable</h3>
          <p className="text-xs text-red-400 mb-3">{error || 'Unable to fetch real-time data'}</p>
          <p className="text-xs text-gray-400 mb-4">
            This doesn't affect other features. You can continue using the chat and other services.
          </p>
          <button
            onClick={fetchStockData}
            className="px-4 py-2 bg-[#cca695] text-white rounded-lg hover:bg-[#b8956a] transition-colors text-sm font-medium shadow-lg"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[rgb(24,25,27)] rounded-2xl border border-[rgba(204,166,149,0.2)] shadow-xl overflow-hidden">
      <div className="px-6 py-4 border-b border-[rgba(204,166,149,0.2)]">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white">Top Indian Stocks</h3>
            <p className="text-sm text-gray-300">Real-time market data across sectors</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-[#cca695] rounded-full animate-pulse"></div>
            <span className="text-xs text-gray-300">Live</span>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-[rgba(204,166,149,0.05)]">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Stock</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Sector</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">Price</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">Change</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">Volume</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">Market Cap</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-300 uppercase tracking-wider">Day Range</th>
            </tr>
          </thead>
          <tbody className="bg-[rgb(24,25,27)] divide-y divide-[rgba(204,166,149,0.1)]">
            {stocks.map((stock) => (
              <tr
                key={stock.symbol}
                className="hover:bg-[rgba(204,166,149,0.05)] cursor-pointer transition-colors"
                onClick={() => handleStockClick(stock.symbol)}
              >
                <td className="px-6 py-4">
                  <div>
                    <div className="text-sm font-medium text-[#cca695] hover:text-[#b8956a]">{stock.symbol}</div>
                    <div className="text-sm text-gray-400">{stock.name}</div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-[rgba(204,166,149,0.1)] text-[#cca695] border border-[rgba(204,166,149,0.2)]">
                    {stock.sector}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-white text-right font-medium">
                  {formatPrice(stock.currentPrice)}
                </td>
                <td className="px-6 py-4 text-sm text-right">
                  <div className={stock.change >= 0 ? 'text-[#cca695]' : 'text-red-400'}>
                    <div className="font-medium">
                      {stock.change >= 0 ? '+' : ''}{formatPrice(stock.change)}
                    </div>
                    <div className="text-xs">
                      {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-white text-right">
                  {formatVolume(stock.volume)}
                </td>
                <td className="px-6 py-4 text-sm text-white text-right font-medium">
                  {stock.marketCap}
                </td>
                <td className="px-6 py-4 text-sm text-slate-600 text-center">
                  <div className="text-xs">
                    <span className="text-green-600">{formatPrice(stock.dayHigh)}</span>
                    <span className="mx-1">-</span>
                    <span className="text-red-600">{formatPrice(stock.dayLow)}</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}