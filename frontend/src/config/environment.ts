/**
 * Environment Configuration for Artha AI Frontend
 * Centralized environment variable management with type safety
 */

export interface EnvironmentConfig {
  NODE_ENV: 'development' | 'production' | 'test';
  API_URL: string;
  WS_URL: string;
  DEMO_MODE: boolean;
  APP_ENV: string;
  FORCE_HTTPS: boolean;
  DEBUG: boolean;
}

/**
 * Get environment configuration with proper defaults
 */
export function getEnvironmentConfig(): EnvironmentConfig {
  const nodeEnv = (process.env.NODE_ENV || 'development') as EnvironmentConfig['NODE_ENV'];
  const isProduction = nodeEnv === 'production';
  const isDevelopment = nodeEnv === 'development';
  
  // Determine protocol based on environment and current page (client-side)
  let protocol = 'http';
  let wsProtocol = 'ws';
  
  if (typeof window !== 'undefined') {
    // Client-side: detect from current page
    protocol = window.location.protocol === 'https:' ? 'https' : 'http';
    wsProtocol = protocol === 'https' ? 'wss' : 'ws';
  } else if (isProduction) {
    // Server-side production: default to HTTPS
    protocol = 'https';
    wsProtocol = 'wss';
  }
  
  // Get API URL with environment-based defaults
  const getApiUrl = (): string => {
    // Priority: NEXT_PUBLIC_API_URL > NEXT_PUBLIC_BACKEND_URL > constructed URL
    if (process.env.NEXT_PUBLIC_API_URL) {
      return process.env.NEXT_PUBLIC_API_URL;
    }
    
    if (process.env.NEXT_PUBLIC_BACKEND_URL) {
      return process.env.NEXT_PUBLIC_BACKEND_URL;
    }
    
    // Construct URL based on environment
    if (isProduction) {
      return process.env.NEXT_PUBLIC_PRODUCTION_API_URL || `${protocol}://api.artha-ai.com`;
    }
    
    return `${protocol}://localhost:8000`;
  };
  
  // Get WebSocket URL
  const getWsUrl = (): string => {
    if (process.env.NEXT_PUBLIC_WS_URL) {
      return process.env.NEXT_PUBLIC_WS_URL;
    }
    
    const apiUrl = getApiUrl();
    return apiUrl.replace(/^https?/, wsProtocol);
  };
  
  return {
    NODE_ENV: nodeEnv,
    API_URL: getApiUrl(),
    WS_URL: getWsUrl(),
    DEMO_MODE: process.env.NEXT_PUBLIC_DEMO_MODE === 'true',
    APP_ENV: process.env.NEXT_PUBLIC_APP_ENV || nodeEnv,
    FORCE_HTTPS: process.env.FORCE_HTTPS === 'true' || isProduction,
    DEBUG: process.env.NEXT_PUBLIC_DEBUG === 'true' || isDevelopment,
  };
}

/**
 * Environment-aware API URL getter
 */
export function getApiUrl(): string {
  return getEnvironmentConfig().API_URL;
}

/**
 * Environment-aware WebSocket URL getter
 */
export function getWebSocketUrl(): string {
  return getEnvironmentConfig().WS_URL;
}

/**
 * Check if HTTPS is enabled
 */
export function isHttpsEnabled(): boolean {
  return getApiUrl().startsWith('https://');
}

/**
 * Check if running in production
 */
export function isProduction(): boolean {
  return getEnvironmentConfig().NODE_ENV === 'production';
}

/**
 * Check if running in development
 */
export function isDevelopment(): boolean {
  return getEnvironmentConfig().NODE_ENV === 'development';
}

/**
 * Check if demo mode is enabled
 */
export function isDemoMode(): boolean {
  return getEnvironmentConfig().DEMO_MODE;
}

/**
 * Check if debug mode is enabled
 */
export function isDebugMode(): boolean {
  return getEnvironmentConfig().DEBUG;
}

/**
 * Get environment-specific configuration for logging
 */
export function getLoggingConfig() {
  const config = getEnvironmentConfig();
  return {
    level: config.DEBUG ? 'debug' : config.NODE_ENV === 'production' ? 'error' : 'info',
    enableConsole: config.DEBUG || config.NODE_ENV !== 'production',
    enableRemote: config.NODE_ENV === 'production',
  };
}

/**
 * Export the current environment configuration
 */
export const ENV_CONFIG = getEnvironmentConfig();

export default {
  getEnvironmentConfig,
  getApiUrl,
  getWebSocketUrl,
  isHttpsEnabled,
  isProduction,
  isDevelopment,
  isDemoMode,
  isDebugMode,
  getLoggingConfig,
  ENV_CONFIG,
};