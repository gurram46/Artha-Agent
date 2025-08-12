/**
 * Chat Service for Frontend
 * Handles conversation persistence and API integration with backend chat system
 */

import { getApiBaseUrl, buildApiUrl, apiFetch, API_CONFIG } from '../config/api';

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  created_at: string;
  agent_mode?: string;
  tokens_used?: number;
  metadata?: any;
}

export interface ChatConversation {
  id: string;
  title?: string;
  agent_mode: string;
  created_at: string;
  updated_at: string;
  last_message_at: string;
  is_active: boolean;
  is_archived: boolean;
  is_favorite: boolean;
  message_count: number;
  total_tokens_used: number;
  summary?: string;
  tags?: string[];
  messages?: ChatMessage[];
}

export interface CreateConversationRequest {
  user_id: string;
  agent_mode: string;
  title?: string;
  financial_context?: any;
}

export interface AddMessageRequest {
  conversation_id: string;
  message_type: 'user' | 'assistant';
  content: string;
  agent_mode?: string;
  tokens_used?: number;
  metadata?: any;
  financial_snapshot?: any;
}

class ChatService {
  private baseUrl: string;
  private currentConversationId: string | null = null;
  private userId: string;

  constructor() {
    // Initialize API base URL
    this.baseUrl = buildApiUrl(API_CONFIG.CHAT_BASE);
    // Generate or retrieve user ID
    this.userId = this.getUserId();
  }

  private getUserId(): string {
    // Check if we're in a browser environment
    if (typeof window === 'undefined') {
      // Server-side rendering - return a temporary ID
      return `temp_user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    let userId = localStorage.getItem('artha_user_id');
    if (!userId) {
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('artha_user_id', userId);
    }
    return userId;
  }

  /**
   * Create a new conversation
   */
  async createConversation(agentMode: string = 'quick', title?: string): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.userId,
          agent_mode: agentMode,
          title,
        } as CreateConversationRequest),
      });

      if (!response.ok) {
        throw new Error(`Failed to create conversation: ${response.statusText}`);
      }

      const data = await response.json();
      this.currentConversationId = data.conversation_id;
      
      // Store current conversation in localStorage (only in browser)
      if (typeof window !== 'undefined') {
        localStorage.setItem('current_conversation_id', this.currentConversationId);
      }
      
      console.log('✅ Created conversation:', this.currentConversationId);
      return this.currentConversationId;
    } catch (error) {
      console.error('❌ Failed to create conversation:', error);
      throw error;
    }
  }

  /**
   * Add a message to the current conversation
   */
  async addMessage(
    messageType: 'user' | 'assistant',
    content: string,
    agentMode?: string,
    tokensUsed?: number,
    metadata?: any
  ): Promise<string> {
    try {
      // Create conversation if none exists
      if (!this.currentConversationId) {
        await this.createConversation(agentMode || 'quick');
      }

      const response = await fetch(`${this.baseUrl}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: this.currentConversationId,
          message_type: messageType,
          content,
          agent_mode: agentMode,
          tokens_used: tokensUsed,
          metadata,
        } as AddMessageRequest),
      });

      if (!response.ok) {
        throw new Error(`Failed to add message: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Added message to conversation');
      return data.message_id;
    } catch (error) {
      console.error('❌ Failed to add message:', error);
      throw error;
    }
  }

  /**
   * Get conversation history
   */
  async getConversationHistory(conversationId?: string): Promise<ChatConversation | null> {
    try {
      const targetId = conversationId || this.currentConversationId;
      if (!targetId) return null;

      const response = await fetch(`${this.baseUrl}/conversations/${targetId}?user_id=${this.userId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`Failed to get conversation history: ${response.statusText}`);
      }

      const data = await response.json();
      return data.conversation;
    } catch (error) {
      console.error('❌ Failed to get conversation history:', error);
      return null;
    }
  }

  /**
   * Get all user conversations
   */
  async getUserConversations(limit: number = 50, includeArchived: boolean = false): Promise<ChatConversation[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/conversations?user_id=${this.userId}&limit=${limit}&include_archived=${includeArchived}`
      );

      if (!response.ok) {
        throw new Error(`Failed to get conversations: ${response.statusText}`);
      }

      const data = await response.json();
      return data.conversations;
    } catch (error) {
      console.error('❌ Failed to get user conversations:', error);
      return [];
    }
  }

  /**
   * Search conversations
   */
  async searchConversations(query: string, limit: number = 20): Promise<ChatConversation[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/search?user_id=${this.userId}&query=${encodeURIComponent(query)}&limit=${limit}`
      );

      if (!response.ok) {
        throw new Error(`Failed to search conversations: ${response.statusText}`);
      }

      const data = await response.json();
      return data.results;
    } catch (error) {
      console.error('❌ Failed to search conversations:', error);
      return [];
    }
  }

  /**
   * Toggle favorite status
   */
  async toggleFavorite(conversationId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations/${conversationId}/favorite`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: this.userId }),
      });

      if (!response.ok) {
        throw new Error(`Failed to toggle favorite: ${response.statusText}`);
      }

      const data = await response.json();
      return data.is_favorite;
    } catch (error) {
      console.error('❌ Failed to toggle favorite:', error);
      return false;
    }
  }

  /**
   * Archive conversation
   */
  async archiveConversation(conversationId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations/${conversationId}/archive`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: this.userId }),
      });

      if (!response.ok) {
        throw new Error(`Failed to archive conversation: ${response.statusText}`);
      }

      return true;
    } catch (error) {
      console.error('❌ Failed to archive conversation:', error);
      return false;
    }
  }

  /**
   * Delete conversation
   */
  async deleteConversation(conversationId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: this.userId }),
      });

      if (!response.ok) {
        throw new Error(`Failed to delete conversation: ${response.statusText}`);
      }

      // Clear current conversation if it was deleted
      if (conversationId === this.currentConversationId) {
        this.currentConversationId = null;
        if (typeof window !== 'undefined') {
          localStorage.removeItem('current_conversation_id');
        }
      }

      return true;
    } catch (error) {
      console.error('❌ Failed to delete conversation:', error);
      return false;
    }
  }

  /**
   * Start a new conversation (clears current)
   */
  async startNewConversation(agentMode: string = 'quick'): Promise<string> {
    this.currentConversationId = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('current_conversation_id');
    }
    return await this.createConversation(agentMode);
  }

  /**
   * Load existing conversation
   */
  async loadConversation(conversationId: string): Promise<ChatConversation | null> {
    this.currentConversationId = conversationId;
    if (typeof window !== 'undefined') {
      localStorage.setItem('current_conversation_id', conversationId);
    }
    return await this.getConversationHistory(conversationId);
  }

  /**
   * Get current conversation ID
   */
  getCurrentConversationId(): string | null {
    return this.currentConversationId;
  }

  /**
   * Initialize from localStorage
   */
  async initializeFromStorage(): Promise<ChatConversation | null> {
    if (typeof window === 'undefined') {
      return null;
    }
    
    const savedConversationId = localStorage.getItem('current_conversation_id');
    if (savedConversationId) {
      this.currentConversationId = savedConversationId;
      return await this.getConversationHistory(savedConversationId);
    }
    return null;
  }

  /**
   * Get chat analytics
   */
  async getChatAnalytics(days: number = 30): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/analytics?user_id=${this.userId}&days=${days}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get analytics: ${response.statusText}`);
      }

      const data = await response.json();
      return data.analytics;
    } catch (error) {
      console.error('❌ Failed to get chat analytics:', error);
      return null;
    }
  }

  /**
   * Check if chat saving is available (backend connectivity)
   */
  async isAvailable(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations?user_id=${this.userId}&limit=1`);
      return response.ok;
    } catch (error) {
      console.warn('Chat saving service not available:', error);
      return false;
    }
  }
}

// Export singleton instance
export const chatService = new ChatService();
export default chatService;