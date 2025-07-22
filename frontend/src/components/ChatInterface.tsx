'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import ErrorBoundary from './ErrorBoundary';
import { Message, StreamMessage, DEFAULT_STREAMING_CONFIG, AgentDetail } from '@/types/chat';
import ReactMarkdown from 'react-markdown';

// Component for expandable agent details
const AgentDetailsSection = ({ agentDetails }: { agentDetails: Record<string, AgentDetail> }) => {
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  if (!agentDetails || Object.keys(agentDetails).length === 0) {
    return null;
  }

  return (
    <div className="mt-4 border-t border-gray-200 pt-4">
      {Object.entries(agentDetails).map(([agentId, detail]) => (
        <div key={agentId} className="mb-3">
          <button
            onClick={() => setExpandedAgent(expandedAgent === agentId ? null : agentId)}
            className="flex items-center justify-between w-full px-3 py-2 text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <span>{detail.title}</span>
            <svg
              className={`w-4 h-4 transform transition-transform ${expandedAgent === agentId ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {expandedAgent === agentId && (
            <div className="mt-2 p-3 bg-gray-50 rounded-lg border-l-4 border-blue-500">
              <ReactMarkdown
                components={{
                  h1: ({node, ...props}) => <h1 className="text-sm font-bold mb-1" {...props} />,
                  h2: ({node, ...props}) => <h2 className="text-xs font-semibold mb-1" {...props} />,
                  h3: ({node, ...props}) => <h3 className="text-xs font-semibold mb-1" {...props} />,
                  p: ({node, ...props}) => <p className="mb-1 leading-relaxed text-xs" {...props} />,
                  strong: ({node, ...props}) => <strong className="font-bold text-gray-900" {...props} />,
                  ul: ({node, ...props}) => <ul className="list-disc list-inside mb-1 space-y-0.5 text-xs" {...props} />,
                  ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-1 space-y-0.5 text-xs" {...props} />,
                  li: ({node, ...props}) => <li className="leading-relaxed text-xs" {...props} />,
                  code: ({node, ...props}) => <code className="bg-gray-200 px-1 py-0.5 rounded text-xs" {...props} />
                }}
              >
                {detail.content}
              </ReactMarkdown>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I\'m your AI financial advisor powered by 3 specialized agents. I have access to your complete financial data through Fi MCP. Ask me anything about your finances, investments, or financial planning.',
      timestamp: new Date()
    }
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Hackathon example queries from your submitted idea
  const exampleQueries = [
    { icon: '🔮', text: "How much money will I have at 40?", category: 'Planning' },
    { icon: '🏠', text: "Can I afford a ₹50L home loan?", category: 'Loans' },
    { icon: '📊', text: "Which SIPs underperformed the market?", category: 'Analysis' },
    { icon: '🚗', text: "Should I buy a car worth 20 lakhs?", category: 'Purchase' }
  ];

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date()
    };

    const query = currentMessage;
    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    // Add streaming message placeholder
    const streamingMessageId = (Date.now() + 1).toString();
    const streamingMessage: Message = {
      id: streamingMessageId,
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      streaming: true
    };
    setMessages(prev => [...prev, streamingMessage]);

    let retryCount = 0;
    const maxRetries = DEFAULT_STREAMING_CONFIG.maxRetries;
    
    const attemptRequest = async (): Promise<void> => {
      let controller: AbortController | null = null;
      let timeoutId: NodeJS.Timeout | null = null;
      
      try {
        controller = new AbortController();
        
        // Set up timeout with proper cleanup
        timeoutId = setTimeout(() => {
          if (controller && !controller.signal.aborted) {
            console.log('Request timed out after', DEFAULT_STREAMING_CONFIG.timeout, 'ms');
            controller.abort();
          }
        }, DEFAULT_STREAMING_CONFIG.timeout);

        // Try streaming first
        const streamResponse = await fetch('http://localhost:8003/api/stream/query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
          signal: controller.signal
        });

        // Clear timeout immediately after fetch completes
        if (timeoutId) {
          clearTimeout(timeoutId);
          timeoutId = null;
        }

        if (streamResponse.ok && streamResponse.body) {
          await handleStreamingResponse(streamResponse, streamingMessageId);
        } else {
          throw new Error(`Streaming failed: ${streamResponse.status} ${streamResponse.statusText}`);
        }

      } catch (error) {
        // Clean up timeout if still active
        if (timeoutId) {
          clearTimeout(timeoutId);
          timeoutId = null;
        }
        
        console.error(`Request attempt ${retryCount + 1} failed:`, error);
        
        // Check if error is due to abort signal
        if (error instanceof Error && error.name === 'AbortError') {
          console.log('Request was aborted');
        }
        
        if (retryCount < maxRetries && DEFAULT_STREAMING_CONFIG.fallbackToRegular) {
          retryCount++;
          
          // Update status message
          setMessages(prev => 
            prev.map(msg => 
              msg.id === streamingMessageId
                ? { ...msg, content: `Retrying... (${retryCount}/${maxRetries})`, streaming: true }
                : msg
            )
          );
          
          // Wait before retry
          await new Promise(resolve => setTimeout(resolve, DEFAULT_STREAMING_CONFIG.retryDelay));
          return attemptRequest();
        } else {
          // Final fallback to regular endpoint
          await handleRegularResponse(query, streamingMessageId);
        }
      } finally {
        // Ensure cleanup
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
      }
    };

    try {
      await attemptRequest();
    } catch (error) {
      console.error('All attempts failed:', error);
      setMessages(prev => 
        prev.map(msg => 
          msg.id === streamingMessageId
            ? {
                ...msg,
                content: 'Sorry, I encountered an error after multiple attempts. Please try again later.',
                streaming: false
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleStreamingResponse = async (response: Response, messageId: string) => {
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let lastUpdateTime = Date.now();
    const throttleDelay = 16; // ~60fps updates
    let pendingUpdate = '';
    let updateTimeoutId: NodeJS.Timeout | null = null;

    const flushPendingUpdate = () => {
      if (pendingUpdate) {
        setMessages(prev => 
          prev.map(msg => 
            msg.id === messageId
              ? { ...msg, content: msg.content + pendingUpdate }
              : msg
          )
        );
        pendingUpdate = '';
      }
    };

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          // Flush any remaining updates
          flushPendingUpdate();
          if (updateTimeoutId) clearTimeout(updateTimeoutId);
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            console.log('📥 Received streaming data:', data); // Debug log
            
            if (data === '[DONE]') {
              // Flush any pending updates before marking as done
              flushPendingUpdate();
              if (updateTimeoutId) clearTimeout(updateTimeoutId);
              
              console.log('✅ Stream completed, marking as done');
              setMessages(prev => 
                prev.map(msg => 
                  msg.id === messageId
                    ? { ...msg, streaming: false }
                    : msg
                )
              );
              return;
            }

            try {
              const parsed: StreamMessage = JSON.parse(data);
              console.log('📊 Parsed message:', parsed); // Debug log
              
              if (parsed.type === 'log' && parsed.content) {
                console.log('🤖 AI Log:', parsed.content);
                
                // Add logs to the message content with proper formatting
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === messageId
                      ? { ...msg, content: msg.content + parsed.content + '\n\n', streaming: true }
                      : msg
                  )
                );
              } else if (parsed.type === 'content' && parsed.content) {
                console.log('💬 Adding content chunk:', parsed.content.substring(0, 50) + '...'); // Debug log
                
                // Immediate update for better real-time feel
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === messageId
                      ? { ...msg, content: msg.content + parsed.content, streaming: true }
                      : msg
                  )
                );
              } else if (parsed.type === 'status' && parsed.content) {
                console.log('📋 Status update:', parsed.content);
                
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === messageId
                      ? { ...msg, content: parsed.content, streaming: true }
                      : msg
                  )
                );
              } else if (parsed.type === 'agent_details') {
                console.log('📊 Agent details received:', parsed.agent);
                
                // Store agent details separately for expandable sections
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === messageId
                      ? { 
                          ...msg, 
                          agentDetails: {
                            ...msg.agentDetails,
                            [parsed.agent]: {
                              title: parsed.title,
                              content: parsed.content
                            }
                          }
                        }
                      : msg
                  )
                );
              } else if (parsed.type === 'error') {
                console.error('❌ Streaming error:', parsed.content);
                throw new Error(parsed.content);
              }
            } catch (e) {
              if (e instanceof Error && e.message !== data) {
                console.error('🔥 JSON parse error:', e);
                throw e; // Re-throw actual errors
              }
              console.warn('⚠️ Skipping invalid JSON:', data);
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      // Clean up any pending timeouts
      if (updateTimeoutId) {
        clearTimeout(updateTimeoutId);
      }
      
      console.error('Streaming error:', error);
      
      // Don't throw AbortError - handle it gracefully
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Streaming was aborted');
        return;
      }
      
      throw error; // Let the caller handle other errors
    } finally {
      // Final cleanup
      if (updateTimeoutId) {
        clearTimeout(updateTimeoutId);
      }
    }
  };

  const handleRegularResponse = async (query: string, messageId: string) => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const response = await fetch('http://localhost:8003/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      setMessages(prev => 
        prev.map(msg => 
          msg.id === messageId
            ? {
                ...msg,
                content: data.response || 'No response received from AI agents',
                streaming: false
              }
            : msg
        )
      );

    } catch (error) {
      console.error('Regular response error:', error);
      let errorMessage = 'Sorry, I encountered an error.';
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = 'Request timed out. The AI agents may be busy processing other requests.';
        } else if (error.message.includes('Failed to fetch')) {
          errorMessage = 'Cannot connect to the AI backend. Please ensure the server is running on port 8003.';
        } else {
          errorMessage = `Error: ${error.message}`;
        }
      }
      
      setMessages(prev => 
        prev.map(msg => 
          msg.id === messageId
            ? {
                ...msg,
                content: errorMessage,
                streaming: false
              }
            : msg
        )
      );
    }
  };

  const handleExampleQuery = (query: string) => {
    setCurrentMessage(query);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <ErrorBoundary>
      <div className="space-y-6">
      {/* Professional Header */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">AI Financial Assistant</h2>
            <p className="text-sm text-gray-600 mt-1">Powered by 3 specialized AI agents with real-time Fi data</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex -space-x-2">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-xs font-medium text-blue-600">A</div>
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center text-xs font-medium text-green-600">R</div>
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center text-xs font-medium text-purple-600">R</div>
            </div>
            <div className="flex items-center space-x-1 text-sm text-gray-600">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>All agents online</span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {exampleQueries.map((query, index) => (
            <button
              key={index}
              onClick={() => handleExampleQuery(query.text)}
              className="p-3 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg transition-colors group text-left"
            >
              <div className="flex items-start space-x-2">
                <span className="text-lg">{query.icon}</span>
                <div className="flex-1">
                  <p className="text-xs font-medium text-gray-500">{query.category}</p>
                  <p className="text-sm text-gray-700 group-hover:text-gray-900 mt-0.5 line-clamp-2">{query.text}</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Container */}
      <Card className="bg-white border border-gray-200 shadow-sm">
        <CardContent className="p-0">
          <div className="h-[500px] flex flex-col">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex mb-4 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start space-x-2 max-w-[70%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.type === 'user' 
                        ? 'bg-gray-700 text-white text-sm font-medium' 
                        : 'bg-blue-100 text-blue-600 text-xs font-medium'
                    }`}>
                      {message.type === 'user' ? 'U' : 'AI'}
                    </div>
                    <div className={`rounded-lg px-4 py-3 ${
                      message.type === 'user'
                        ? 'bg-gray-700 text-white'
                        : message.processing
                        ? 'bg-gray-100 text-gray-600'
                        : 'bg-gray-50 text-gray-800 border border-gray-200'
                    }`}>
                      {message.processing ? (
                        <div className="flex items-center space-x-2">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                          </div>
                          <span className="text-sm">{message.content}</span>
                        </div>
                      ) : (
                        <div className="flex items-start">
                          <div className="text-sm flex-1">
                            {message.content ? (
                              <>
                                <ReactMarkdown 
                                  components={{
                                    // Custom styling for markdown elements
                                    h1: ({node, ...props}) => <h1 className="text-lg font-bold mb-2" {...props} />,
                                    h2: ({node, ...props}) => <h2 className="text-md font-semibold mb-2" {...props} />,
                                    h3: ({node, ...props}) => <h3 className="text-sm font-semibold mb-1" {...props} />,
                                    p: ({node, ...props}) => <p className="mb-2 leading-relaxed" {...props} />,
                                    strong: ({node, ...props}) => <strong className="font-bold text-gray-900" {...props} />,
                                    em: ({node, ...props}) => <em className="italic" {...props} />,
                                    ul: ({node, ...props}) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
                                    ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />,
                                    li: ({node, ...props}) => <li className="leading-relaxed" {...props} />,
                                    code: ({node, ...props}) => <code className="bg-gray-100 px-1 py-0.5 rounded text-xs" {...props} />,
                                    blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-gray-300 pl-4 italic mb-2" {...props} />
                                  }}
                                >
                                  {message.content}
                                </ReactMarkdown>
                                {message.type === 'assistant' && !message.streaming && (
                                  <AgentDetailsSection agentDetails={message.agentDetails || {}} />
                                )}
                              </>
                            ) : (
                              message.streaming ? 'AI is typing...' : ''
                            )}
                          </div>
                          {message.streaming && (
                            <div className="ml-2 flex-shrink-0">
                              <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                            </div>
                          )}
                        </div>
                      )}
                      <div className={`text-xs mt-1 ${message.type === 'user' ? 'text-gray-300' : 'text-gray-500'}`}>
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about your finances, investments, or goals..."
                  className="flex-1 px-4 py-2.5 bg-white border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  disabled={isLoading}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!currentMessage.trim() || isLoading}
                  className={`px-5 py-2.5 rounded-lg font-medium text-sm transition-colors ${
                    currentMessage.trim() && !isLoading
                      ? 'bg-blue-600 hover:bg-blue-700 text-white'
                      : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  {isLoading ? (
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : 'Send'}
                </button>
              </div>
              <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
                <div className="flex items-center space-x-3">
                  <span>Press Enter to send</span>
                  <span>•</span>
                  <span>Shift + Enter for new line</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="flex items-center space-x-1">
                    <svg className="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                      <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd"/>
                    </svg>
                    <span>Analyst</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd"/>
                    </svg>
                    <span>Research</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <svg className="w-3 h-3 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-2.001A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clipRule="evenodd"/>
                    </svg>
                    <span>Risk</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      </div>
    </ErrorBoundary>
  );
}