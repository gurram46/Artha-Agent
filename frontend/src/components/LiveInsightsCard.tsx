'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  type: 'user' | 'ai' | 'thinking';
  content: string;
  timestamp: Date;
}

export default function LiveInsightsCard() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const connectWebSocket = () => {
    try {
      wsRef.current = new WebSocket('ws://localhost:8000/ws/live-insights');
      
      wsRef.current.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
      };
      
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'thinking') {
          setIsThinking(true);
          setMessages(prev => [...prev, {
            type: 'thinking',
            content: data.message,
            timestamp: new Date()
          }]);
        } else if (data.type === 'insights') {
          setIsThinking(false);
          // Remove thinking message
          setMessages(prev => prev.filter(msg => msg.type !== 'thinking'));
          
          // Add AI response
          setMessages(prev => [...prev, {
            type: 'ai',
            content: formatAIResponse(data.data),
            timestamp: new Date()
          }]);
        } else if (data.type === 'error') {
          setIsThinking(false);
          setMessages(prev => prev.filter(msg => msg.type !== 'thinking'));
          
          setMessages(prev => [...prev, {
            type: 'ai',
            content: `Sorry, I encountered an error: ${data.message}`,
            timestamp: new Date()
          }]);
        }
      };
      
      wsRef.current.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');
      };
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setIsConnected(false);
    }
  };

  const formatAIResponse = (data: any) => {
    if (typeof data === 'string') {
      return data;
    }
    
    if (data.real_time_insight) {
      return data.real_time_insight;
    }
    
    // Try to format structured response
    let formatted = '';
    if (data.direct_answer) formatted += `**Answer:** ${data.direct_answer}\n\n`;
    if (data.relevant_data) formatted += `**Your Data:** ${data.relevant_data}\n\n`;
    if (data.immediate_insights) formatted += `**Insights:** ${data.immediate_insights}\n\n`;
    if (data.quick_actions) formatted += `**Actions:** ${data.quick_actions}\n\n`;
    
    return formatted || JSON.stringify(data, null, 2);
  };

  const sendMessage = () => {
    if (!inputValue.trim() || !isConnected || isThinking) return;
    
    // Add user message
    setMessages(prev => [...prev, {
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    }]);
    
    // Send to WebSocket
    wsRef.current?.send(JSON.stringify({
      query: inputValue
    }));
    
    setInputValue('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const suggestedQuestions = [
    "What's my biggest money leak?",
    "How much should I invest monthly?",
    "Is my portfolio risk level appropriate?",
    "When can I retire comfortably?",
    "Should I pay off my debt faster?"
  ];

  const handleSuggestedQuestion = (question: string) => {
    setInputValue(question);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">🤖 Live AI Insights</h2>
            <p className="text-sm text-gray-600 mt-1">Ask anything about your finances</p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-1">
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-xs text-gray-500">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <button
              onClick={isConnected ? disconnectWebSocket : connectWebSocket}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                isConnected 
                  ? 'text-red-600 bg-red-50 hover:bg-red-100'
                  : 'text-green-600 bg-green-50 hover:bg-green-100'
              }`}
            >
              {isConnected ? 'Disconnect' : 'Connect'}
            </button>
          </div>
        </div>
      </div>
      
      <div className="p-6">
        {/* Chat Messages */}
        <div className="h-64 overflow-y-auto mb-4 space-y-3 bg-gray-50 rounded-lg p-4">
          {messages.length === 0 && (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">💬</div>
              <p className="text-gray-500 text-sm">Start a conversation with AI</p>
            </div>
          )}
          
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg text-sm ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.type === 'thinking'
                    ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                    : 'bg-white text-gray-800 border border-gray-200'
                }`}
              >
                {message.type === 'thinking' && (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-3 w-3 border-2 border-yellow-600 border-t-transparent"></div>
                    <span>{message.content}</span>
                  </div>
                )}
                {message.type !== 'thinking' && (
                  <div className="whitespace-pre-wrap">{message.content}</div>
                )}
                <div className={`text-xs mt-1 ${
                  message.type === 'user' ? 'text-blue-200' : 'text-gray-500'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Questions */}
        {messages.length === 0 && (
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">Try asking:</p>
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestedQuestion(question)}
                  className="text-xs px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full hover:bg-blue-100 transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="flex space-x-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about your finances..."
            disabled={!isConnected || isThinking}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            rows={2}
          />
          <button
            onClick={sendMessage}
            disabled={!inputValue.trim() || !isConnected || isThinking}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isThinking ? (
              <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>

        {!isConnected && (
          <p className="text-xs text-gray-500 mt-2">
            Connect to start chatting with AI about your finances
          </p>
        )}
      </div>
    </div>
  );
}