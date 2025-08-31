/**
 * API Configuration for Artha AI
 * Handles both HTTP and HTTPS environments dynamically
 */

import { getApiUrl as getEnvironmentApiUrl, getWebSocketUrl as getEnvironmentWebSocketUrl, isHttpsEnabled as getEnvironmentHttpsEnabled } from './environment';

interface ApiConfig {
  baseUrl: string;
  wsUrl: string;
  isHttps: boolean;
}

/**
 * Get API configuration based on environment
 */
export function getApiConfig(): ApiConfig {
  return {
    baseUrl: getEnvironmentApiUrl(),
    wsUrl: getEnvironmentWebSocketUrl(),
    isHttps: getEnvironmentHttpsEnabled()
  };
}

/**
 * Get the base API URL
 */
export function getApiBaseUrl(): string {
  return getApiConfig().baseUrl;
}

/**
 * Get the WebSocket URL
 */
export function getWebSocketUrl(): string {
  return getEnvironmentWebSocketUrl();
}

/**
 * Check if HTTPS is enabled
 */
export function isHttpsEnabled(): boolean {
  return getEnvironmentHttpsEnabled();
}

/**
 * Build API endpoint URL
 */
export function buildApiUrl(endpoint: string): string {
  const baseUrl = getApiBaseUrl();
  // Remove leading slash if present to avoid double slashes
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${baseUrl}/${cleanEndpoint}`;
}

/**
 * Build WebSocket URL
 */
export function buildWebSocketUrl(endpoint: string = ''): string {
  const wsUrl = getWebSocketUrl();
  if (!endpoint) return wsUrl;
  
  // Remove leading slash if present to avoid double slashes
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${wsUrl}/${cleanEndpoint}`;
}

/**
 * Default API configuration
 */
export const API_CONFIG = {
  // Chat endpoints
  CHAT_BASE: '/api/chat',
  CHAT_CONVERSATIONS: '/api/chat/conversations',
  CHAT_MESSAGES: '/api/chat/messages',
  
  // AI endpoints
  QUERY: '/query',
  STREAM_QUERY: '/api/stream/query',
  DEEP_RESEARCH: '/api/deep-research',
  
  // Financial endpoints
  PORTFOLIO_HEALTH: '/api/portfolio-health',
  RISK_ASSESSMENT: '/api/risk-assessment',
  INVESTMENT_RECOMMENDATIONS: '/api/ai-investment-recommendations',
  
  // Stock endpoints
  STOCKS_RECOMMENDATION: '/api/stocks/recommendation',
  
  // PDF endpoints
  PDF_ANALYZE: '/api/pdf/analyze-with-ai',
  
  // User endpoints
  USER_SAVE: '/api/user/save',
  
  // Local LLM endpoints
  LOCAL_LLM_PREPARE: '/api/local-llm/prepare',
  
  // Trip planning endpoints
  TRIP_PLANNING: '/api/trip-planning',
  TRIP_PLANNING_CHAT: '/api/trip-planning/chat',
} as const;

/**
 * Helper function to get full API URL for a specific endpoint
 */
export function getApiUrl(endpoint: keyof typeof API_CONFIG): string {
  return buildApiUrl(API_CONFIG[endpoint]);
}

/**
 * Fetch wrapper with automatic URL building
 */
export async function apiFetch(
  endpoint: string | keyof typeof API_CONFIG,
  options: RequestInit = {}
): Promise<Response> {
  const url = typeof endpoint === 'string' 
    ? buildApiUrl(endpoint)
    : getApiUrl(endpoint);
    
  // Add default headers
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  return fetch(url, {
    ...options,
    headers: defaultHeaders,
  });
}

/**
 * WebSocket wrapper with automatic URL building
 */
export function createWebSocket(endpoint: string = ''): WebSocket {
  const url = buildWebSocketUrl(endpoint);
  return new WebSocket(url);
}

export default {
  getApiConfig,
  getApiBaseUrl,
  getWebSocketUrl,
  isHttpsEnabled,
  buildApiUrl,
  buildWebSocketUrl,
  getApiUrl,
  apiFetch,
  createWebSocket,
  API_CONFIG,
};