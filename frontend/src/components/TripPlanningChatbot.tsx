'use client';

import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface TripPlanningChatbotProps {
  onClose?: () => void;
}

export default function TripPlanningChatbot({ onClose }: TripPlanningChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [financialContext, setFinancialContext] = useState<any>({});
  const [isDemoMode, setIsDemoMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Detect demo mode
  useEffect(() => {
    const demoMode = sessionStorage.getItem('demoMode') === 'true';
    setIsDemoMode(demoMode);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initialize the chatbot when component mounts
    initializeChatbot();
  }, []);

  const initializeChatbot = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/trip-planning/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: 'start', mode: 'research', demo_mode: isDemoMode })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setFinancialContext(data.financial_context);
        setMessages([{
          id: '1',
          type: 'assistant',
          content: data.response,
          timestamp: new Date()
        }]);
        setIsInitialized(true);
      }
    } catch (error) {
      console.error('Failed to initialize trip planning chatbot:', error);
      setMessages([{
        id: 'error',
        type: 'assistant',
        content: '🧳 **Welcome to Smart Trip Planner!**\n\nI\'m having trouble connecting right now, but I\'m still here to help! Tell me where you\'d like to go and I\'ll create an amazing itinerary for you! ✈️',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date()
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    const query = currentMessage;
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/trip-planning/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query, 
          mode: 'research',
          demo_mode: isDemoMode,
          conversation_history: updatedMessages.map(msg => ({
            type: msg.type,
            content: msg.content,
            timestamp: msg.timestamp.toISOString()
          }))
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: data.response,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        setFinancialContext(data.financial_context);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: '🧳 Sorry, I\'m having trouble right now! Could you try asking again? I\'m here to help with your trip planning! ✈️',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickQuestions = [
    "Plan a budget trip to Goa 🏖️",
    "Weekend getaway near me 🎯",
    "Family vacation under ₹50K 👨‍👩‍👧‍👦",
    "Solo travel recommendations 🧳",
    "Best time to visit Kerala 📅"
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-[rgb(24,25,27)] border border-[rgba(34,197,94,0.2)] rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="border-b border-[rgba(34,197,94,0.2)] px-6 py-4 bg-gradient-to-r from-[rgba(0,26,30,0.95)] to-[rgba(24,25,27,0.95)] backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-[rgb(34,197,94)] to-[rgb(22,163,74)] rounded-2xl flex items-center justify-center shadow-lg">
                <span className="text-white text-xl">🧳</span>
              </div>
              <div>
                <h2 className="text-xl font-bold text-white tracking-tight">Smart Trip Planner</h2>
                <p className="text-sm text-gray-300 font-medium">AI Travel Assistant with Budget Analysis</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="text-xs bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] px-3 py-1 rounded-full font-semibold text-[rgb(0,184,153)]">
                Budget: ₹{financialContext.recommended_budget ? (financialContext.recommended_budget / 1000).toFixed(0) + 'K' : 'Calculating...'}
              </div>
              {onClose && (
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-[rgba(0,184,153,0.1)] rounded-lg transition-colors"
                >
                  <svg className="w-6 h-6 text-gray-400 hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="h-[500px] overflow-y-auto p-4 bg-gradient-to-b from-[rgba(0,26,30,0.5)] to-[rgba(24,25,27,0.5)]">
          {messages.map((message) => (
            <div key={message.id} className="mb-4">
              <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] group ${
                  message.type === 'user' 
                    ? 'bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white shadow-lg' 
                    : 'bg-[rgb(24,25,27)] text-white border border-[rgba(0,184,153,0.2)] shadow-md backdrop-blur-sm'
                } rounded-3xl px-5 py-3 transition-all duration-300 hover:shadow-xl hover:scale-[1.02]`}>
                  {message.type === 'assistant' ? (
                    <div className="prose prose-invert max-w-none">
                      <ReactMarkdown
                        components={{
                          h1: ({children}) => <h1 className="text-lg font-bold mb-3 text-white">{children}</h1>,
                          h2: ({children}) => <h2 className="text-base font-semibold mb-2 text-white">{children}</h2>,
                          h3: ({children}) => <h3 className="text-sm font-semibold mb-2 text-gray-200">{children}</h3>,
                          p: ({children}) => <p className="mb-2 leading-relaxed text-sm text-gray-100">{children}</p>,
                          ul: ({children}) => <ul className="list-disc list-inside mb-2 space-y-1 text-sm">{children}</ul>,
                          ol: ({children}) => <ol className="list-decimal list-inside mb-2 space-y-1 text-sm">{children}</ol>,
                          li: ({children}) => <li className="leading-relaxed text-sm text-gray-200">{children}</li>,
                          strong: ({children}) => <strong className="font-semibold text-[rgb(0,184,153)]">{children}</strong>,
                          code: ({children}) => <code className="bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] px-1.5 py-0.5 rounded text-xs font-mono text-[rgb(0,184,153)]">{children}</code>
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="text-sm">{message.content}</p>
                  )}
                  <div className="flex items-center justify-between mt-2 pt-2 border-t border-[rgba(0,184,153,0.1)]">
                    <div className="text-xs text-gray-400">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl px-5 py-3 max-w-[80%]">
                <div className="flex items-center space-x-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-[rgb(0,184,153)] rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-[rgb(0,184,153)] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-[rgb(0,184,153)] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-gray-300">Planning your trip...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-[rgba(0,184,153,0.2)] px-6 py-4 bg-gradient-to-r from-[rgba(0,26,30,0.95)] to-[rgba(24,25,27,0.95)] backdrop-blur-xl">
          {/* Quick Questions */}
          {messages.length <= 1 && (
            <div className="mb-4">
              <p className="text-sm text-gray-400 mb-2">Quick suggestions:</p>
              <div className="flex flex-wrap gap-2">
                {quickQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentMessage(question.replace(/[🏖️🎯👨‍👩‍👧‍👦🧳📅]/g, '').trim())}
                    className="text-xs px-3 py-2 bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] text-gray-300 rounded-xl hover:bg-[rgba(0,184,153,0.2)] hover:text-white transition-all duration-300"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}
          
          <div className="flex items-end space-x-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Where would you like to go? ✈️"
                className="w-full px-6 py-4 bg-[rgba(30,32,34,0.8)] border border-[rgba(0,184,153,0.2)] rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[rgb(0,184,153)] focus:border-[rgb(0,184,153)] backdrop-blur-sm transition-all duration-300 shadow-sm hover:shadow-md"
                disabled={isLoading}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!currentMessage.trim() || isLoading}
              className={`p-4 rounded-2xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform ${
                !currentMessage.trim() || isLoading
                  ? 'bg-[rgba(156,163,175,0.2)] text-gray-500 cursor-not-allowed border border-[rgba(156,163,175,0.2)]'
                  : 'bg-gradient-to-br from-[rgb(34,197,94)] to-[rgb(22,163,74)] text-white hover:from-[rgb(22,163,74)] hover:to-[rgb(16,143,64)] hover:scale-105 active:scale-95'
              }`}
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}