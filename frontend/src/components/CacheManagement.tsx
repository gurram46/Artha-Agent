'use client';

import React, { useState, useEffect } from 'react';
import CacheService from '../services/cacheService';
import MCPDataService from '../services/mcpDataService';

interface CacheStatus {
  hasCache: boolean;
  expiresAt?: string;
  isExpired?: boolean;
  timeRemaining?: string;
}

interface SystemStatus {
  cacheEnabled: boolean;
  schedulerRunning: boolean;
  lastCleanup?: string;
  totalCachedUsers?: number;
}

interface CacheManagementProps {
  userEmail?: string;
  onClose: () => void;
}

export default function CacheManagement({ userEmail, onClose }: CacheManagementProps) {
  const [cacheStatus, setCacheStatus] = useState<CacheStatus | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cacheService = CacheService.getInstance();
  const mcpService = MCPDataService.getInstance();

  useEffect(() => {
    loadCacheInfo();
  }, []);

  const loadCacheInfo = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Load cache status
      if (userEmail) {
        const status = await mcpService.getCacheStatus();
        setCacheStatus(status);
      }

      // Load system status
      const sysStatus = await cacheService.getSystemStatus();
      setSystemStatus(sysStatus);
    } catch (err) {
      setError('Failed to load cache information');
      console.error('Cache info error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInvalidateCache = async () => {
    if (!userEmail) return;
    
    setIsLoading(true);
    try {
      await mcpService.invalidateSecureCache();
      await loadCacheInfo();
    } catch (err) {
      setError('Failed to invalidate cache');
      console.error('Cache invalidation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6 max-w-md w-full max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">Cache Management</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-[rgba(0,184,153,0.1)] rounded-xl transition-colors"
          >
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-[rgba(220,53,69,0.1)] border border-[rgba(220,53,69,0.3)] rounded-xl">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[rgb(0,184,153)]"></div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* User Cache Status */}
            {userEmail && cacheStatus && (
              <div className="bg-[rgba(30,30,30,0.8)] rounded-xl p-4">
                <h3 className="text-lg font-semibold text-white mb-3">Your Cache Status</h3>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Status:</span>
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${
                        cacheStatus.isExpired ? 'bg-red-400' : 
                        cacheStatus.hasCache ? 'bg-green-400' : 'bg-gray-400'
                      }`}></div>
                      <span className={`text-sm font-medium ${
                        cacheStatus.isExpired ? 'text-red-400' : 
                        cacheStatus.hasCache ? 'text-green-400' : 'text-gray-400'
                      }`}>
                        {cacheStatus.isExpired ? 'Expired' : 
                         cacheStatus.hasCache ? 'Active' : 'No Cache'}
                      </span>
                    </div>
                  </div>

                  {cacheStatus.expiresAt && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Expires:</span>
                      <span className="text-sm text-[rgb(0,184,153)]">
                        {formatDateTime(cacheStatus.expiresAt)}
                      </span>
                    </div>
                  )}

                  {cacheStatus.timeRemaining && !cacheStatus.isExpired && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Time Remaining:</span>
                      <span className="text-sm text-[rgb(0,184,153)]">
                        {cacheStatus.timeRemaining}
                      </span>
                    </div>
                  )}

                  {cacheStatus.hasCache && (
                    <button
                      onClick={handleInvalidateCache}
                      disabled={isLoading}
                      className="w-full mt-3 px-4 py-2 bg-[rgba(220,53,69,0.1)] hover:bg-[rgba(220,53,69,0.2)] border border-[rgba(220,53,69,0.3)] text-red-400 font-medium rounded-xl transition-colors disabled:opacity-50"
                    >
                      Clear Cache
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* System Status */}
            {systemStatus && (
              <div className="bg-[rgba(30,30,30,0.8)] rounded-xl p-4">
                <h3 className="text-lg font-semibold text-white mb-3">System Status</h3>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Cache System:</span>
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${
                        systemStatus.cacheEnabled ? 'bg-green-400' : 'bg-red-400'
                      }`}></div>
                      <span className={`text-sm font-medium ${
                        systemStatus.cacheEnabled ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {systemStatus.cacheEnabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Scheduler:</span>
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${
                        systemStatus.schedulerRunning ? 'bg-green-400' : 'bg-red-400'
                      }`}></div>
                      <span className={`text-sm font-medium ${
                        systemStatus.schedulerRunning ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {systemStatus.schedulerRunning ? 'Running' : 'Stopped'}
                      </span>
                    </div>
                  </div>

                  {systemStatus.lastCleanup && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Last Cleanup:</span>
                      <span className="text-sm text-[rgb(0,184,153)]">
                        {formatDateTime(systemStatus.lastCleanup)}
                      </span>
                    </div>
                  )}

                  {systemStatus.totalCachedUsers !== undefined && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Cached Users:</span>
                      <span className="text-sm text-[rgb(0,184,153)]">
                        {systemStatus.totalCachedUsers}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Information */}
            <div className="bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] rounded-xl p-4">
              <h4 className="text-sm font-semibold text-[rgb(0,184,153)] mb-2">About Secure Caching</h4>
              <p className="text-xs text-gray-300 leading-relaxed">
                Your financial data is securely cached for 24 hours using AES-256 encryption. 
                This improves performance and reduces API calls to Fi Money. 
                Cache is automatically cleaned up hourly and expires after 24 hours.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}