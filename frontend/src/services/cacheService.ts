/**
 * Secure Cache Service - Frontend interface for 24-hour financial data caching
 * Integrates with backend secure cache system for persistent data storage
 */

interface CacheStatus {
  enabled: boolean;
  has_cache: boolean;
  expires_at?: string;
  time_remaining?: string;
  cached_at?: string;
  message: string;
}

interface CacheSystemStatus {
  enabled: boolean;
  database_connected?: boolean;
  scheduler?: {
    running: boolean;
    next_cleanup?: string;
    last_cleanup?: string;
  };
  message: string;
}

class CacheService {
  private static instance: CacheService;
  private backendUrl: string;

  private constructor() {
    this.backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  }

  static getInstance(): CacheService {
    if (!CacheService.instance) {
      CacheService.instance = new CacheService();
    }
    return CacheService.instance;
  }

  /**
   * Check if user has valid cached financial data
   */
  async checkCacheStatus(email: string): Promise<CacheStatus> {
    try {
      const response = await fetch(`${this.backendUrl}/api/cache/status?email=${encodeURIComponent(email)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(15000)
      });

      if (!response.ok) {
        throw new Error(`Cache status check failed: ${response.status}`);
      }

      const result: CacheStatus = await response.json();
      
      if (result.has_cache) {
        console.log(`Valid cache found for ${email}, expires: ${result.expires_at}`);
      } else {
        console.log(`No valid cache found for ${email}`);
      }

      return result;

    } catch (error) {
      console.error('Cache status check error:', error);
      return {
        enabled: false,
        has_cache: false,
        message: error instanceof Error ? error.message : 'Cache status check failed'
      };
    }
  }

  /**
   * Store financial data in secure cache with 24-hour expiration
   */
  async storeFinancialData(email: string, financialData: any, dataSource: string = 'artha_ai'): Promise<{
    success: boolean;
    message: string;
    expires_in?: string;
  }> {
    try {
      console.log(`Storing financial data in secure cache for ${email}...`);

      const response = await fetch(`${this.backendUrl}/api/cache/store`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          financial_data: financialData,
          data_source: dataSource
        }),
        signal: AbortSignal.timeout(10000)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Cache storage failed: ${response.status}`);
      }

      const result = await response.json();
      
      console.log(`Financial data cached successfully for ${email}`);
      return {
        success: true,
        message: result.message,
        expires_in: result.expires_in
      };

    } catch (error) {
      console.error('Cache storage error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Cache storage failed'
      };
    }
  }

  /**
   * Retrieve cached financial data if available
   */
  async retrieveFinancialData(email: string): Promise<{
    success: boolean;
    data?: any;
    message: string;
    from_cache: boolean;
  }> {
    try {
      console.log(`Retrieving cached financial data for ${email}...`);

      const response = await fetch(`${this.backendUrl}/api/cache/retrieve?email=${encodeURIComponent(email)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(15000) // Increased timeout to 15 seconds
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Cache retrieval failed: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.status === 'success') {
        console.log(`Retrieved cached financial data for ${email}`);
        return {
          success: true,
          data: result.data,
          message: result.message,
          from_cache: true
        };
      } else {
        console.log(`No cached data found for ${email}`);
        return {
          success: false,
          message: result.message,
          from_cache: false
        };
      }

    } catch (error) {
      console.error('Cache retrieval error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Cache retrieval failed',
        from_cache: false
      };
    }
  }

  /**
   * Manually invalidate user's cached financial data
   */
  async invalidateCache(email: string): Promise<{
    success: boolean;
    message: string;
  }> {
    try {
      console.log(`Invalidating cache for ${email}...`);

      const response = await fetch(`${this.backendUrl}/api/cache/invalidate?email=${encodeURIComponent(email)}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(15000)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Cache invalidation failed: ${response.status}`);
      }

      const result = await response.json();
      
      console.log(`Cache invalidated for ${email}`);
      return {
        success: true,
        message: result.message
      };

    } catch (error) {
      console.error('Cache invalidation error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Cache invalidation failed'
      };
    }
  }

  /**
   * Get status of the cache system and scheduler
   */
  async getSystemStatus(): Promise<CacheSystemStatus> {
    try {
      const response = await fetch(`${this.backendUrl}/api/cache/system-status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(15000)
      });

      if (!response.ok) {
        throw new Error(`System status check failed: ${response.status}`);
      }

      const result: CacheSystemStatus = await response.json();
      
      if (result.enabled && result.database_connected) {
        console.log('Cache system is operational');
      } else {
        console.warn('Cache system has issues:', result.message);
      }

      return result;

    } catch (error) {
      console.error('System status check error:', error);
      return {
        enabled: false,
        message: error instanceof Error ? error.message : 'System status check failed'
      };
    }
  }

  /**
   * Format time remaining for display
   */
  formatTimeRemaining(timeRemaining?: string): string {
    if (!timeRemaining) return 'Unknown';
    
    try {
      const hours = parseFloat(timeRemaining);
      if (hours < 1) {
        const minutes = Math.floor(hours * 60);
        return `${minutes} minutes`;
      } else if (hours < 24) {
        return `${Math.floor(hours)} hours ${Math.floor((hours % 1) * 60)} minutes`;
      } else {
        return `${Math.floor(hours / 24)} days`;
      }
    } catch {
      return timeRemaining;
    }
  }

  /**
   * Check if cache is about to expire (within 1 hour)
   */
  isCacheExpiringSoon(timeRemaining?: string): boolean {
    if (!timeRemaining) return true;
    
    try {
      const hours = parseFloat(timeRemaining);
      return hours <= 1;
    } catch {
      return true;
    }
  }

  /**
   * Get cache expiry warning message
   */
  getCacheExpiryWarning(timeRemaining?: string): string | null {
    if (!timeRemaining) return null;
    
    try {
      const hours = parseFloat(timeRemaining);
      if (hours <= 0.5) {
        return 'Your cached data will expire in less than 30 minutes. Please re-login to refresh.';
      } else if (hours <= 1) {
        return 'Your cached data will expire within 1 hour. Consider re-logging in soon.';
      } else if (hours <= 2) {
        return 'Your cached data will expire in less than 2 hours.';
      }
    } catch {
      // Ignore parsing errors
    }
    
    return null;
  }
}

export default CacheService;