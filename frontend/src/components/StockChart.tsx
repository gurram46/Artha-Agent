'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import StockService, { StockData, ChartData } from '../services/stockService';

interface StockChartProps {
  symbol: string;
  onClose?: () => void;
  embedded?: boolean;
}

const timeRanges = ['1D', '1W', '1M', '3M', '6M', '1Y'];

export default function StockChart({ symbol, onClose, embedded = false }: StockChartProps) {
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [timeRange, setTimeRange] = useState('1D');
  const [chartType, setChartType] = useState<'line' | 'area'>('area');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const stockService = StockService.getInstance();

  useEffect(() => {
    loadChartData();
  }, [symbol, timeRange]);

  const loadChartData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load stock data first
      const stock = await stockService.getStockDetails(symbol);
      setStockData(stock);
      
      // Load chart data
      const chart = await stockService.getStockChartData(symbol, timeRange);
      console.log('Chart data received:', chart);
      
      if (chart && chart.length > 0) {
        setChartData(chart);
      } else {
        // Generate mock data if no chart data available
        const mockData = generateMockData(stock?.currentPrice || 3000);
        setChartData(mockData);
      }
      
    } catch (err) {
      console.error('Failed to load chart data:', err);
      setError('Failed to load chart data');
      
      // Generate mock data as fallback
      const mockData = generateMockData(stockData?.currentPrice || 3000);
      setChartData(mockData);
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = (basePrice: number): ChartData[] => {
    const points = timeRange === '1D' ? 24 : 30;
    const data: ChartData[] = [];
    let currentPrice = basePrice;
    
    for (let i = 0; i < points; i++) {
      const change = (Math.random() - 0.5) * (basePrice * 0.02); // 2% max change
      currentPrice = Math.max(currentPrice + change, basePrice * 0.9); // Don't go below 90% of base
      
      const time = timeRange === '1D' 
        ? new Date(Date.now() - (points - i) * 60 * 60 * 1000).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
        : new Date(Date.now() - (points - i) * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      
      data.push({
        time,
        price: currentPrice,
        volume: Math.floor(Math.random() * 1000000),
        open: currentPrice,
        high: currentPrice * 1.01,
        low: currentPrice * 0.99,
        close: currentPrice
      });
    }
    
    return data;
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const formatTooltipValue = (value: any, name: string) => {
    if (name === 'price') {
      return [formatPrice(value), 'Price'];
    }
    return [value, name];
  };

  if (loading) {
    return (
      <div className={embedded ? "flex items-center justify-center py-12" : "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"}>
        <div className="text-center space-y-4">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-slate-600">Loading chart data...</p>
        </div>
      </div>
    );
  }

  const containerClass = embedded 
    ? "w-full" 
    : "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4";
  const contentClass = embedded 
    ? "w-full" 
    : "bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-8 max-w-7xl w-full max-h-[90vh] overflow-y-auto";

  return (
    <div className={containerClass}>
      <div className={contentClass}>
        {/* Header - only show if not embedded */}
        {!embedded && stockData && (
          <div className="flex items-start justify-between mb-8">
            <div className="space-y-2">
              <div className="flex items-center space-x-4">
                <h2 className="text-3xl font-bold text-white">{stockData.name}</h2>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-[rgba(34,197,94,0.1)] text-[rgb(34,197,94)] border border-[rgba(34,197,94,0.2)]">
                  {stockData.sector}
                </span>
              </div>
              <p className="text-lg text-gray-300">{stockData.symbol}</p>
              <div className="flex items-baseline space-x-4">
                <h3 className="text-4xl font-bold text-white">{formatPrice(stockData.currentPrice)}</h3>
                <div className={`flex items-center space-x-2 ${stockData.change >= 0 ? 'text-[rgb(34,197,94)]' : 'text-red-600'}`}>
                  <span className="text-xl font-semibold">
                    {stockData.change >= 0 ? '+' : ''}{formatPrice(stockData.change)} 
                    ({stockData.changePercent >= 0 ? '+' : ''}{stockData.changePercent.toFixed(2)}%)
                  </span>
                </div>
              </div>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                className="p-2 hover:bg-[rgba(0,184,153,0.1)] rounded-lg transition-colors"
              >
                <svg className="w-6 h-6 text-gray-400 hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        )}

        {/* Chart Controls */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex space-x-2">
            {timeRanges.map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  timeRange === range
                    ? 'bg-[rgb(0,184,153)] text-white shadow-lg'
                    : 'bg-[rgba(0,184,153,0.1)] text-gray-300 hover:bg-[rgba(0,184,153,0.2)] hover:text-white border border-[rgba(0,184,153,0.2)]'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setChartType('line')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                chartType === 'line'
                  ? 'bg-[rgb(0,184,153)] text-white shadow-lg'
                  : 'bg-[rgba(0,184,153,0.1)] text-gray-300 hover:bg-[rgba(0,184,153,0.2)] hover:text-white border border-[rgba(0,184,153,0.2)]'
              }`}
            >
              Line
            </button>
            <button
              onClick={() => setChartType('area')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                chartType === 'area'
                  ? 'bg-[rgb(0,184,153)] text-white shadow-lg'
                  : 'bg-[rgba(0,184,153,0.1)] text-gray-300 hover:bg-[rgba(0,184,153,0.2)] hover:text-white border border-[rgba(0,184,153,0.2)]'
              }`}
            >
              Area
            </button>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-gradient-to-br from-black to-[rgb(30,32,34)] border border-[rgba(0,184,153,0.1)] rounded-2xl p-6 mb-6">
          <div className="h-80">
            {error ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-4">
                  <div className="w-12 h-12 bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.2)] rounded-xl flex items-center justify-center mx-auto">
                    <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-red-400 font-medium">{error}</p>
                  <button
                    onClick={loadChartData}
                    className="px-4 py-2 bg-[rgb(0,184,153)] text-white rounded-lg hover:bg-[rgb(0,164,133)] transition-colors"
                  >
                    Retry
                  </button>
                </div>
              </div>
            ) : chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                {chartType === 'line' ? (
                  <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 184, 153, 0.1)" />
                    <XAxis 
                      dataKey="time" 
                      stroke="#9ca3af" 
                      fontSize={12}
                      tick={{ fill: '#9ca3af' }}
                    />
                    <YAxis 
                      stroke="#9ca3af" 
                      fontSize={12}
                      domain={['dataMin - 50', 'dataMax + 50']}
                      tick={{ fill: '#9ca3af' }}
                      tickFormatter={(value) => `₹${value.toFixed(0)}`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgb(24, 25, 27)',
                        border: '1px solid rgba(0, 184, 153, 0.2)',
                        borderRadius: '12px',
                        boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
                        color: 'white'
                      }}
                      formatter={formatTooltipValue}
                      labelStyle={{ color: 'white', fontWeight: 'bold' }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="price" 
                      stroke="rgb(0, 184, 153)" 
                      strokeWidth={3} 
                      dot={false}
                      activeDot={{ r: 6, fill: 'rgb(0, 184, 153)' }}
                    />
                  </LineChart>
                ) : (
                  <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 184, 153, 0.1)" />
                    <XAxis 
                      dataKey="time" 
                      stroke="#9ca3af" 
                      fontSize={12}
                      tick={{ fill: '#9ca3af' }}
                    />
                    <YAxis 
                      stroke="#9ca3af" 
                      fontSize={12}
                      domain={['dataMin - 50', 'dataMax + 50']}
                      tick={{ fill: '#9ca3af' }}
                      tickFormatter={(value) => `₹${value.toFixed(0)}`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgb(24, 25, 27)',
                        border: '1px solid rgba(0, 184, 153, 0.2)',
                        borderRadius: '12px',
                        boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
                        color: 'white'
                      }}
                      formatter={formatTooltipValue}
                      labelStyle={{ color: 'white', fontWeight: 'bold' }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="price" 
                      stroke="rgb(0, 184, 153)" 
                      fill="url(#colorPrice)"
                      strokeWidth={3}
                    />
                    <defs>
                      <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="rgb(0, 184, 153)" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="rgb(0, 184, 153)" stopOpacity={0.05}/>
                      </linearGradient>
                    </defs>
                  </AreaChart>
                )}
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-4">
                  <div className="w-12 h-12 bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-xl flex items-center justify-center mx-auto">
                    <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <p className="text-gray-400">No chart data available</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Data Summary */}
        {chartData.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[rgb(30,32,34)] rounded-xl p-4 border border-[rgba(0,184,153,0.2)]">
              <p className="text-sm text-slate-600 mb-1">Data Points</p>
              <p className="text-lg font-bold text-slate-900">{chartData.length}</p>
            </div>
            <div className="bg-[rgb(30,32,34)] rounded-xl p-4 border border-[rgba(0,184,153,0.2)]">
              <p className="text-sm text-slate-600 mb-1">Range</p>
              <p className="text-lg font-bold text-slate-900">{timeRange}</p>
            </div>
            <div className="bg-[rgb(30,32,34)] rounded-xl p-4 border border-[rgba(0,184,153,0.2)]">
              <p className="text-sm text-slate-600 mb-1">Min Price</p>
              <p className="text-lg font-bold text-slate-900">
                {formatPrice(Math.min(...chartData.map(d => d.price)))}
              </p>
            </div>
            <div className="bg-[rgb(30,32,34)] rounded-xl p-4 border border-[rgba(0,184,153,0.2)]">
              <p className="text-sm text-slate-600 mb-1">Max Price</p>
              <p className="text-lg font-bold text-slate-900">
                {formatPrice(Math.max(...chartData.map(d => d.price)))}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}