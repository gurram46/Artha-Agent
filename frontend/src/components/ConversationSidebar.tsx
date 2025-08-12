'use client';

import { useState, useEffect } from 'react';
import { ChatConversation, chatService } from '@/services/chatService';
import { designSystem } from '@/styles/designSystem';

interface ConversationSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectConversation: (conversation: ChatConversation) => void;
  onNewConversation: () => void;
  currentConversationId?: string;
}

export default function ConversationSidebar({
  isOpen,
  onClose,
  onSelectConversation,
  onNewConversation,
  currentConversationId
}: ConversationSidebarProps) {
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showArchived, setShowArchived] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadConversations();
    }
  }, [isOpen, showArchived]);

  const loadConversations = async () => {
    setLoading(true);
    try {
      const userConversations = await chatService.getUserConversations(50, showArchived);
      setConversations(userConversations);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadConversations();
      return;
    }

    setLoading(true);
    try {
      const results = await chatService.searchConversations(searchQuery);
      setConversations(results);
    } catch (error) {
      console.error('Failed to search conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await chatService.toggleFavorite(conversationId);
      loadConversations(); // Refresh list
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const handleArchive = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await chatService.archiveConversation(conversationId);
      loadConversations(); // Refresh list
    } catch (error) {
      console.error('Failed to archive conversation:', error);
    }
  };

  const handleDelete = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this conversation? This action cannot be undone.')) {
      try {
        await chatService.deleteConversation(conversationId);
        loadConversations(); // Refresh list
      } catch (error) {
        console.error('Failed to delete conversation:', error);
      }
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    return date.toLocaleDateString();
  };

  const getConversationTitle = (conversation: ChatConversation) => {
    return conversation.title || `${conversation.agent_mode} Chat`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <div className="relative w-80 bg-[rgb(18,19,21)] border-r border-[rgba(255,255,255,0.1)] flex flex-col h-full">
        {/* Header */}
        <div className="p-4 border-b border-[rgba(255,255,255,0.1)]">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Chat History</h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* New Conversation Button */}
          <button
            onClick={onNewConversation}
            className="w-full p-3 bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white rounded-lg font-medium hover:from-[rgb(0,164,133)] hover:to-[rgb(0,144,113)] transition-all duration-300 mb-4"
          >
            + New Conversation
          </button>

          {/* Search */}
          <div className="flex space-x-2">
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1 px-3 py-2 bg-[rgb(24,25,27)] border border-[rgba(255,255,255,0.1)] rounded-lg text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-[rgb(0,184,153)]"
            />
            <button
              onClick={handleSearch}
              className="px-3 py-2 bg-[rgb(24,25,27)] border border-[rgba(255,255,255,0.1)] rounded-lg text-gray-400 hover:text-white transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          </div>

          {/* Toggle Archived */}
          <div className="flex items-center mt-3">
            <input
              type="checkbox"
              id="showArchived"
              checked={showArchived}
              onChange={(e) => setShowArchived(e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="showArchived" className="text-sm text-gray-400">
              Show archived
            </label>
          </div>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-400">
              <div className="animate-spin w-6 h-6 border-2 border-[rgb(0,184,153)] border-t-transparent rounded-full mx-auto mb-2"></div>
              Loading conversations...
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-4 text-center text-gray-400">
              {searchQuery ? 'No conversations found' : 'No conversations yet'}
            </div>
          ) : (
            <div className="p-2">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => onSelectConversation(conversation)}
                  className={`p-3 rounded-lg mb-2 cursor-pointer transition-all duration-200 group ${
                    conversation.id === currentConversationId
                      ? 'bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.3)]'
                      : 'hover:bg-[rgb(24,25,27)] border border-transparent'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="text-sm font-medium text-white truncate">
                          {getConversationTitle(conversation)}
                        </h3>
                        {conversation.is_favorite && (
                          <svg className="w-4 h-4 text-yellow-400 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                          </svg>
                        )}
                        {conversation.is_archived && (
                          <span className="text-xs text-gray-500 bg-gray-700 px-2 py-1 rounded">
                            Archived
                          </span>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-2 text-xs text-gray-400 mb-1">
                        <span className="capitalize">{conversation.agent_mode}</span>
                        <span>•</span>
                        <span>{conversation.message_count} messages</span>
                        <span>•</span>
                        <span>{formatDate(conversation.last_message_at)}</span>
                      </div>

                      {conversation.summary && (
                        <p className="text-xs text-gray-500 truncate">
                          {conversation.summary}
                        </p>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => handleToggleFavorite(conversation.id, e)}
                        className="p-1 text-gray-400 hover:text-yellow-400 transition-colors"
                        title={conversation.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                      >
                        <svg className="w-4 h-4" fill={conversation.is_favorite ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                        </svg>
                      </button>

                      {!conversation.is_archived && (
                        <button
                          onClick={(e) => handleArchive(conversation.id, e)}
                          className="p-1 text-gray-400 hover:text-blue-400 transition-colors"
                          title="Archive conversation"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8l6 6 6-6" />
                          </svg>
                        </button>
                      )}

                      <button
                        onClick={(e) => handleDelete(conversation.id, e)}
                        className="p-1 text-gray-400 hover:text-red-400 transition-colors"
                        title="Delete conversation"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[rgba(255,255,255,0.1)] text-xs text-gray-400">
          <div className="flex justify-between">
            <span>{conversations.length} conversations</span>
            <span>Artha Chat History</span>
          </div>
        </div>
      </div>
    </div>
  );
}