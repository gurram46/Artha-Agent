'use client';

import { useState, useEffect } from 'react';

interface Transaction {
  transactionId: string;
  accountNumber: string;
  accountType: string;
  transactionDate: string;
  amount: {
    currencyCode: string;
    units: string;
  };
  description: string;
  category: string;
  merchantName: string;
  transactionType: string;
  status: string;
}

interface CreditCardTransactionsProps {
  financialData?: any;
}

const getCategoryIcon = (category: string) => {
  const categoryIcons: { [key: string]: string } = {
    'SHOPPING': '🛒',
    'FOOD_DELIVERY': '🍔',
    'TRANSPORTATION': '🚗',
    'FOOD_BEVERAGE': '☕',
    'ENTERTAINMENT': '🎬',
    'GROCERY': '🛒',
    'FUEL': '⛽',
    'DEFAULT': '💳'
  };
  return categoryIcons[category] || categoryIcons['DEFAULT'];
};

const getCategoryColor = (category: string) => {
  const categoryColors: { [key: string]: string } = {
    'SHOPPING': 'text-purple-400',
    'FOOD_DELIVERY': 'text-orange-400',
    'TRANSPORTATION': 'text-blue-400',
    'FOOD_BEVERAGE': 'text-yellow-400',
    'ENTERTAINMENT': 'text-pink-400',
    'GROCERY': 'text-green-400',
    'FUEL': 'text-red-400',
    'DEFAULT': 'text-gray-400'
  };
  return categoryColors[category] || categoryColors['DEFAULT'];
};

const formatAmount = (amount: { units: string }) => {
  const value = Math.abs(parseInt(amount.units));
  return `₹${value.toLocaleString()}`;
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-IN', { 
    day: '2-digit', 
    month: 'short'
  });
};

export default function CreditCardTransactions({ financialData }: CreditCardTransactionsProps) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    const loadTransactions = async () => {
      try {
        setIsLoading(true);
        
        // Check if we're in demo mode
        const demoMode = sessionStorage.getItem('demoMode') === 'true';
        
        if (demoMode) {
          // Load from demo data
          const response = await fetch('/financial-data?demo=true');
          const data = await response.json();
          
          if (data.success && data.data?.bank_transactions?.transactions) {
            setTransactions(data.data.bank_transactions.transactions);
          }
        } else {
          // For real mode, would fetch from actual API
          // For now, we'll use the demo data structure
          if (financialData?.bank_transactions?.transactions) {
            setTransactions(financialData.bank_transactions.transactions);
          }
        }
      } catch (error) {
        console.error('Error loading transactions:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadTransactions();
  }, [financialData]);

  if (isLoading) {
    return (
      <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
        <div className="animate-pulse">
          <div className="h-6 bg-[rgba(0,184,153,0.2)] rounded mb-4 w-1/3"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-[rgba(0,184,153,0.1)] rounded-xl"></div>
            ))}
          </div>
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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">No Transactions Found</h3>
          <p className="text-gray-400">Credit card transactions will appear here</p>
        </div>
      </div>
    );
  }

  const displayedTransactions = showAll ? transactions : transactions.slice(0, 5);
  const totalSpent = transactions.reduce((sum, txn) => sum + Math.abs(parseInt(txn.amount.units)), 0);

  return (
    <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white mb-1">Recent Transactions</h3>
          <p className="text-sm text-gray-300">Credit Card Activity</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-300">Total Spent</p>
          <p className="text-xl font-bold text-red-400">₹{totalSpent.toLocaleString()}</p>
        </div>
      </div>

      <div className="space-y-3">
        {displayedTransactions.map((transaction) => (
          <div 
            key={transaction.transactionId}
            className="flex items-center justify-between p-4 bg-[rgba(0,184,153,0.05)] border border-[rgba(0,184,153,0.1)] rounded-xl hover:bg-[rgba(0,184,153,0.1)] transition-all duration-300"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-[rgba(0,184,153,0.1)] rounded-xl flex items-center justify-center">
                <span className="text-xl">{getCategoryIcon(transaction.category)}</span>
              </div>
              <div>
                <p className="font-semibold text-white text-sm">{transaction.merchantName}</p>
                <p className="text-xs text-gray-400">{transaction.description}</p>
                <p className={`text-xs font-medium ${getCategoryColor(transaction.category)}`}>
                  {transaction.category.replace(/_/g, ' ')}
                </p>
              </div>
            </div>
            
            <div className="text-right">
              <p className="font-bold text-red-400 text-sm">
                -{formatAmount(transaction.amount)}
              </p>
              <p className="text-xs text-gray-400">
                {formatDate(transaction.transactionDate)}
              </p>
              <div className="flex items-center justify-end mt-1">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                <span className="text-xs text-gray-400">{transaction.status}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {transactions.length > 5 && (
        <div className="mt-6 text-center">
          <button
            onClick={() => setShowAll(!showAll)}
            className="px-6 py-2 bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] text-[rgb(0,184,153)] rounded-xl hover:bg-[rgba(0,184,153,0.2)] transition-all duration-300 font-medium text-sm"
          >
            {showAll ? `Show Less` : `Show All ${transactions.length} Transactions`}
          </button>
        </div>
      )}

      {/* Summary Stats */}
      <div className="mt-6 pt-6 border-t border-[rgba(0,184,153,0.2)]">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-[rgb(0,184,153)]">{transactions.length}</p>
            <p className="text-xs text-gray-400 font-medium">Transactions</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-[rgb(0,184,153)]">
              ₹{Math.round(totalSpent / transactions.length).toLocaleString()}
            </p>
            <p className="text-xs text-gray-400 font-medium">Avg Amount</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-[rgb(0,184,153)]">****5432</p>
            <p className="text-xs text-gray-400 font-medium">Card Number</p>
          </div>
        </div>
      </div>
    </div>
  );
}