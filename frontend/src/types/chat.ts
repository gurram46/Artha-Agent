export interface AgentDetail {
  title: string;
  content: string;
}

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  processing?: boolean;
  streaming?: boolean;
  agentDetails?: Record<string, AgentDetail>;
}

export interface StreamMessage {
  type: 'content' | 'status' | 'error' | 'log' | 'agent_details';
  content: string;
  agent?: string;
  title?: string;
}

export interface QueryResponse {
  response: string;
  processing_time: number;
  sources_count: number;
  agents_used: string[];
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}

export interface StreamingConfig {
  maxRetries: number;
  retryDelay: number;
  timeout: number;
  fallbackToRegular: boolean;
}

export const DEFAULT_STREAMING_CONFIG: StreamingConfig = {
  maxRetries: 2,
  retryDelay: 1000,
  timeout: 60000, // 60 seconds for streaming responses
  fallbackToRegular: true,
};