'use client';

import { useState, useEffect } from 'react';
import MCPDataService from '@/services/mcpDataService';

interface Transaction {
  id: string;
  type: 'bank' | 'mutual_fund' | 'stock';
  amount: number;
  description: string;
  date: string;
  transaction_type: string;
  bank?: string;
  fund_name?: string;
  isin?: string;
  nav?: number;
  balance?: number;
  mode?: string;
}

interface TransactionSummary {
  total_count: number;
  bank_transactions: number;
  mf_transactions: number;
  stock_transactions: number;
  bank_credits: number;
  bank_debits: number;
  net_bank_flow: number;
}

interface AllTransactionsProps {
  financialData?: any;
}

const getTransactionIcon = (type: string, transactionType: string) => {
  if (type === 'bank') {
    return transactionType === 'credit' ? '💰' : '💸';
  } else if (type === 'mutual_fund') {
    return transactionType === 'buy' ? '📈' : '📉';
  } else if (type === 'stock') {
    return transactionType === 'buy' ? '🏪' : '💹';
  }
  return '💳';
};

const getTransactionColor = (type: string, transactionType: string) => {
  if (type === 'bank') {
    return transactionType === 'credit' ? 'text-green-400' : 'text-red-400';
  } else if (type === 'mutual_fund') {
    return transactionType === 'buy' ? 'text-blue-400' : 'text-orange-400';
  } else if (type === 'stock') {
    return transactionType === 'buy' ? 'text-purple-400' : 'text-pink-400';
  }
  return 'text-gray-400';
};

const formatAmount = (amount: number) => {
  const value = Math.abs(amount);
  if (value >= 10000000) return `₹${(value / 10000000).toFixed(1)}Cr`;
  if (value >= 100000) return `₹${(value / 100000).toFixed(1)}L`;
  if (value >= 1000) return `₹${(value / 1000).toFixed(1)}K`;
  return `₹${value.toLocaleString()}`;
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', { 
    day: '2-digit', 
    month: 'short',
    year: 'numeric'
  });
};

const getTypeDisplayName = (type: string) => {
  const typeMap: { [key: string]: string } = {
    'bank': 'Bank',
    'mutual_fund': 'Mutual Fund',
    'stock': 'Stock'
  };
  return typeMap[type] || type;
};

const getTypeBadgeColor = (type: string) => {
  const colorMap: { [key: string]: string } = {
    'bank': 'bg-[rgba(0,184,153,0.1)] text-[rgb(0,184,153)] border-[rgba(0,184,153,0.2)]',
    'mutual_fund': 'bg-[rgba(59,130,246,0.1)] text-blue-400 border-[rgba(59,130,246,0.2)]',
    'stock': 'bg-[rgba(168,85,247,0.1)] text-purple-400 border-[rgba(168,85,247,0.2)]'
  };
  return colorMap[type] || 'bg-[rgba(156,163,175,0.1)] text-gray-400 border-[rgba(156,163,175,0.2)]';
};

export default function AllTransactions({ financialData }: AllTransactionsProps) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<TransactionSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [limit, setLimit] = useState<number>(50);
  const [showAll, setShowAll] = useState(false);

  const mcpService = MCPDataService.getInstance();

  useEffect(() => {
    loadTransactions();
  }, [filter, limit]);

  const loadTransactions = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const result = await mcpService.getAllTransactions(limit, filter);
      
      if (result.success && result.data) {
        setTransactions(result.data.transactions);
        setSummary(result.data.summary);
      } else {
        setError(result.error || 'Failed to load transactions');
      }
    } catch (err) {
      console.error('Error loading transactions:', err);
      setError('Failed to load transactions');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
        <div className="animate-pulse">
          <div className="h-6 bg-[rgba(0,184,153,0.2)] rounded mb-4 w-1/3"></div>
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-16 bg-[rgba(0,184,153,0.1)] rounded-xl"></div>
            ))}
          </div>
          <div className="space-y-3">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-20 bg-[rgba(0,184,153,0.1)] rounded-xl"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-[rgba(220,53,69,0.1)] rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Error Loading Transactions</h3>
          <p className="text-gray-400 mb-4">{error}</p>
          <button 
            onClick={loadTransactions}
            className="bg-[rgb(0,184,153)] hover:bg-[rgb(0,164,133)] text-white font-medium py-2 px-4 rounded-lg transition-all text-sm"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!transactions || transactions.length === 0) {
    return (
      <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-[rgba(0,184,153,0.1)] rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">No Transactions Found</h3>
          <p className="text-gray-400">Transactions will appear here when available</p>
        </div>
      </div>
    );
  }

  const displayedTransactions = showAll ? transactions : transactions.slice(0, 10);

  return (
    <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white mb-1">All Transactions</h3>
          <p className="text-sm text-gray-300">Complete financial activity overview</p>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] text-[rgb(0,184,153)] rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[rgb(0,184,153)]"
          >
            <option value="all">All Types</option>
            <option value="bank">Bank Only</option>
            <option value="mutual_fund">Mutual Funds</option>
            <option value="stock">Stocks</option>
          </select>
        </div>
      </div>

      {/* Summary Stats */}
      {summary && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-[rgba(0,184,153,0.05)] border border-[rgba(0,184,153,0.1)] rounded-xl p-4">
            <p className="text-2xl font-bold text-[rgb(0,184,153)]">{summary.total_count}</p>
            <p className="text-xs text-gray-400 font-medium">Total</p>
          </div>
          <div className="bg-[rgba(0,184,153,0.05)] border border-[rgba(0,184,153,0.1)] rounded-xl p-4">
            <p className="text-2xl font-bold text-green-400">{formatAmount(summary.bank_credits)}</p>
            <p className="text-xs text-gray-400 font-medium">Credits</p>
          </div>
          <div className="bg-[rgba(0,184,153,0.05)] border border-[rgba(0,184,153,0.1)] rounded-xl p-4">
            <p className="text-2xl font-bold text-red-400">{formatAmount(summary.bank_debits)}</p>
            <p className="text-xs text-gray-400 font-medium">Debits</p>
          </div>
          <div className="bg-[rgba(0,184,153,0.05)] border border-[rgba(0,184,153,0.1)] rounded-xl p-4">
            <p className={`text-2xl font-bold ${summary.net_bank_flow >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {formatAmount(summary.net_bank_flow)}
            </p>
            <p className="text-xs text-gray-400 font-medium">Net Flow</p>
          </div>
        </div>
      )}

      {/* Transactions List */}
      <div className="space-y-3">
        {displayedTransactions.map((transaction) => (
          <div 
            key={transaction.id}
            className="flex items-center justify-between p-4 bg-[rgba(0,184,153,0.05)] border border-[rgba(0,184,153,0.1)] rounded-xl hover:bg-[rgba(0,184,153,0.1)] transition-all duration-300"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-[rgba(0,184,153,0.1)] rounded-xl flex items-center justify-center">
                <span className="text-xl">{getTransactionIcon(transaction.type, transaction.transaction_type)}</span>
              </div>
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <p className="font-semibold text-white text-sm">
                    {transaction.bank || transaction.fund_name || transaction.isin || 'Transaction'}
                  </p>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${getTypeBadgeColor(transaction.type)}`}>
                    {getTypeDisplayName(transaction.type)}
                  </span>
                </div>
                <p className="text-xs text-gray-400 max-w-xs truncate">{transaction.description}</p>
                {transaction.balance && (
                  <p className="text-xs text-gray-500">Balance: {formatAmount(transaction.balance)}</p>
                )}
              </div>
            </div>
            
            <div className="text-right">
              <p className={`font-bold text-sm ${getTransactionColor(transaction.type, transaction.transaction_type)}`}>
                {transaction.transaction_type === 'credit' || transaction.transaction_type === 'buy' ? '+' : '-'}
                {formatAmount(transaction.amount)}
              </p>
              <p className="text-xs text-gray-400">
                {formatDate(transaction.date)}
              </p>
              {transaction.nav && (
                <p className="text-xs text-gray-500">NAV: ₹{transaction.nav}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Show More/Less Button */}
      {transactions.length > 10 && (
        <div className="mt-6 text-center">
          <button
            onClick={() => setShowAll(!showAll)}
            className="px-6 py-2 bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] text-[rgb(0,184,153)] rounded-xl hover:bg-[rgba(0,184,153,0.2)] transition-all duration-300 font-medium text-sm"
          >
            {showAll ? `Show Less` : `Show All ${transactions.length} Transactions`}
          </button>
        </div>
      )}

      {/* Type Breakdown */}
      {summary && (
        <div className="mt-6 pt-6 border-t border-[rgba(0,184,153,0.2)]">
          <h4 className="text-sm font-semibold text-white mb-3">Transaction Breakdown</h4>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-lg font-bold text-[rgb(0,184,153)]">{summary.bank_transactions}</p>
              <p className="text-xs text-gray-400 font-medium">Bank</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-blue-400">{summary.mf_transactions}</p>
              <p className="text-xs text-gray-400 font-medium">Mutual Funds</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-purple-400">{summary.stock_transactions}</p>
              <p className="text-xs text-gray-400 font-medium">Stocks</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}