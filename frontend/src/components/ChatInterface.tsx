'use client';

import { useState, useRef, useEffect } from 'react';
import UnifiedCard, { CardContent } from '@/components/ui/UnifiedCard';
import UnifiedButton from '@/components/ui/UnifiedButton';
import ErrorBoundary from './ErrorBoundary';
import { Message, StreamMessage, DEFAULT_STREAMING_CONFIG, AgentDetail, AgentMode } from '@/types/chat';
import ReactMarkdown from 'react-markdown';
import { designSystem } from '@/styles/designSystem';

// Real-time AI Agent Progress Tracker
const AIThinkingProcess = ({ agentDetails, isComplete }: { agentDetails: Record<string, AgentDetail>, isComplete: boolean }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  // Get actual agents from the real data
  const activeAgents = Object.entries(agentDetails || {}).map(([agentId, detail]) => ({
    id: agentId,
    name: detail.title,
    content: detail.content,
    status: 'completed'
  }));

  if (activeAgents.length === 0) {
    return null;
  }

  return (
    <div className="my-4">
      {/* Real-time Agent Progress Header */}
      <div 
        className="flex items-center justify-between p-4 bg-gradient-to-r from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.1)] border border-[rgba(0,184,153,0.2)] rounded-2xl cursor-pointer hover:from-[rgba(0,184,153,0.15)] hover:to-[rgba(0,164,133,0.15)] transition-all duration-300"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              isComplete ? 'bg-[rgb(0,184,153)]' : 'bg-[rgb(0,164,133)]'
            } shadow-lg`}>
              {isComplete ? (
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <div className="flex space-x-0.5">
                  <div className="w-1.5 h-1.5 bg-white rounded-full animate-bounce"></div>
                  <div className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              )}
            </div>
            {!isComplete && (
              <div className="absolute -inset-1 bg-blue-400 rounded-full animate-ping opacity-30"></div>
            )}
          </div>
          <div>
            <h4 className="font-semibold text-white text-base">
              {isComplete ? '✅ AI Analysis Complete' : '🧠 AI Agents Working...'}
            </h4>
            <p className="text-xs text-[rgb(0,184,153)] font-medium">
              {activeAgents.length} {activeAgents.length === 1 ? 'agent' : 'agents'} {isComplete ? 'completed' : 'analyzing'}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <div className="text-xs bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] px-3 py-1 rounded-full font-semibold text-[rgb(0,184,153)]">
            {isComplete ? 'View Analysis' : 'In Progress'}
          </div>
          <svg
            className={`w-5 h-5 text-gray-300 transform transition-transform duration-300 ${
              isExpanded ? 'rotate-180' : ''
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Real-time Agent Analysis */}
      {isExpanded && (
        <div className="mt-4 space-y-3 animate-in slide-in-from-top-2 duration-300">
          {activeAgents.map((agent, index) => {
            // Generate colors for different agents
            const colors = [
              { bg: 'bg-blue-500', border: 'border-blue-200', bgLight: 'bg-blue-50/30' },
              { bg: 'bg-purple-500', border: 'border-purple-200', bgLight: 'bg-purple-50/30' },
              { bg: 'bg-green-500', border: 'border-green-200', bgLight: 'bg-green-50/30' },
              { bg: 'bg-orange-500', border: 'border-orange-200', bgLight: 'bg-orange-50/30' },
              { bg: 'bg-pink-500', border: 'border-pink-200', bgLight: 'bg-pink-50/30' }
            ];
            const color = colors[index % colors.length];
            
            return (
              <div key={agent.id} className={`border rounded-xl transition-all duration-300 ${color.border} ${color.bgLight}`}>
                <div 
                  className="flex items-center justify-between p-4 cursor-pointer"
                  onClick={() => setExpandedAgent(expandedAgent === agent.id ? null : agent.id)}
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-white shadow-lg ${color.bg}`}>
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div>
                      <h5 className="font-semibold text-white text-base">{agent.name}</h5>
                      <p className="text-xs text-[rgb(0,184,153)] font-semibold flex items-center">
                        <div className="w-1.5 h-1.5 bg-[rgb(0,184,153)] rounded-full mr-2 animate-pulse"></div>
                        Analysis complete
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="text-xs bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] text-[rgb(0,184,153)] px-2 py-0.5 rounded-full font-semibold">
                      ✅ Done
                    </div>
                    <svg
                      className={`w-5 h-5 text-gray-300 transform transition-transform ${
                        expandedAgent === agent.id ? 'rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
                
                {/* Real Agent Analysis Content */}
                {expandedAgent === agent.id && (
                  <div className="px-4 pb-4">
                    <div className="bg-[rgba(30,32,34,0.8)] backdrop-blur-sm rounded-2xl p-4 border border-[rgba(0,184,153,0.2)] shadow-sm">
                      <ReactMarkdown
                        components={{
                          h1: ({node, ...props}) => <h1 className="text-base font-bold mb-2 text-white" {...props} />,
                          h2: ({node, ...props}) => <h2 className="text-sm font-semibold mb-2 text-gray-200" {...props} />,
                          h3: ({node, ...props}) => <h3 className="text-sm font-semibold mb-1 text-gray-300" {...props} />,
                          p: ({node, ...props}) => <p className="mb-2 leading-relaxed text-sm text-gray-300" {...props} />,
                          strong: ({node, ...props}) => <strong className="font-semibold text-white" {...props} />,
                          ul: ({node, ...props}) => <ul className="list-disc list-inside mb-2 space-y-1 text-sm" {...props} />,
                          ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-2 space-y-1 text-sm" {...props} />,
                          li: ({node, ...props}) => <li className="leading-relaxed text-sm text-gray-300" {...props} />,
                          code: ({node, ...props}) => <code className="bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] px-1.5 py-0.5 rounded font-mono text-xs text-[rgb(0,184,153)]" {...props} />
                        }}
                      >
                        {agent.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I\'m your AI financial advisor with quick responses powered by advanced AI. Toggle **FiXpert Mode** for deep 3-agent analysis when you need comprehensive research. I have access to your complete financial data through Fi MCP.',
      timestamp: new Date('2024-01-01T00:00:00Z'), // Fixed timestamp to prevent hydration mismatch
      agentDetails: {}
    }
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [agentMode, setAgentMode] = useState<AgentMode>('quick');
  const [isDemoMode, setIsDemoMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Detect demo mode from session storage
    const demoMode = sessionStorage.getItem('demoMode') === 'true';
    setIsDemoMode(demoMode);
  }, []);

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
      timestamp: new Date(),
      mode: agentMode
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
      streaming: true,
      mode: agentMode
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
        const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'https://artha-agent.onrender.com';
        const streamResponse = await fetch(`${baseUrl}/api/stream/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            query,
            mode: agentMode,
            demo_mode: isDemoMode
          }),
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
                // Skip adding logs to message content - they'll be handled separately
              } else if (parsed.type === 'content' && parsed.content) {
                console.log('💬 Adding content chunk:', parsed.content.substring(0, 50) + '...'); // Debug log
                
                // Filter out unwanted footer text and dividers while preserving spacing
                const filteredContent = parsed.content
                  .replace(/─{30,}.*?─{30,}/gs, ' ') // Remove lines of dashes with content, add space
                  .replace(/──────────────────────────────────────── 📊 DETAILED AGENT ANALYSIS \(Click to expand\) ────────────────────────────────────────/g, ' ')
                  .replace(/📊 DETAILED AGENT ANALYSIS \(Click to expand\)/g, ' ')
                  .replace(/\s+/g, ' ') // Replace multiple spaces with single space
                  .trim();
                
                if (filteredContent) {
                  // Immediate update for better real-time feel with proper spacing
                  setMessages(prev => 
                    prev.map(msg => {
                      if (msg.id === messageId) {
                        // Ensure proper spacing between chunks
                        let newContent = msg.content;
                        if (newContent && !newContent.endsWith(' ') && !newContent.endsWith('\n') && 
                            !filteredContent.startsWith(' ') && !filteredContent.startsWith('\n')) {
                          // Add space if both parts don't have whitespace at the junction
                          newContent += ' ';
                        }
                        newContent += filteredContent;
                        return { ...msg, content: newContent, streaming: true };
                      }
                      return msg;
                    })
                  );
                }
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
                console.log('📊 Real-time agent details received:', parsed.agent, parsed.title);
                
                // Update agent details in real-time as they complete
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === messageId
                      ? { 
                          ...msg, 
                          agentDetails: {
                            ...msg.agentDetails,
                            [parsed.agent]: {
                              title: parsed.title || `Agent ${parsed.agent}`,
                              content: parsed.content || 'Analysis in progress...'
                            }
                          },
                          streaming: true
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

      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'https://artha-agent.onrender.com';
      const response = await fetch(`${baseUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query,
          mode: agentMode,
          demo_mode: isDemoMode
        }),
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
      <div className="max-w-6xl mx-auto">
        {/* Modern Premium Chat Interface */}
        <div className="bg-[rgb(24,25,27)] border border-[rgba(0,184,153,0.2)] rounded-3xl overflow-hidden shadow-2xl">
          {/* Premium Header with Dark Glass Effect */}
          <div className="border-b border-[rgba(0,184,153,0.2)] px-6 py-4 bg-gradient-to-r from-[rgba(0,26,30,0.95)] to-[rgba(24,25,27,0.95)] backdrop-blur-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-2xl flex items-center justify-center shadow-lg">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white tracking-tight">Artha AI</h2>
                  <p className="text-sm text-gray-300 font-medium">Financial Intelligence Assistant</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                {agentMode === 'research' && (
                  <div className="text-xs bg-gradient-to-r from-purple-500/20 to-blue-500/20 border border-purple-400/30 px-3 py-1 rounded-full font-semibold text-purple-300 animate-pulse">
                    🔬 FiXpert Mode Active
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Premium Message Area with Modern Bubbles */}
          <div className="h-[600px] overflow-y-auto p-4 bg-gradient-to-b from-[rgba(0,26,30,0.5)] to-[rgba(24,25,27,0.5)] backdrop-blur-sm">
            {messages.map((message) => (
              <div key={message.id} className="mb-4">
                <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] group ${
                    message.type === 'user' 
                      ? 'bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white shadow-lg' 
                      : 'bg-[rgb(24,25,27)] text-white border border-[rgba(0,184,153,0.2)] shadow-md backdrop-blur-sm'
                  } rounded-3xl px-5 py-3 transition-all duration-300 hover:shadow-xl hover:scale-[1.02]`}>
                    {message.processing ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <span className="text-sm">Thinking...</span>
                      </div>
                    ) : (
                      <div>
                        {/* Real-time AI Thinking Process */}
                        {message.type === 'assistant' && (message.agentDetails && Object.keys(message.agentDetails).length > 0) && (
                          <AIThinkingProcess 
                            agentDetails={message.agentDetails} 
                            isComplete={!message.streaming}
                          />
                        )}
                        
                        {/* Main Response Content */}
                        {message.content ? (
                          <div className={message.type === 'assistant' && message.agentDetails ? 'mt-4 pt-4 border-t border-[rgba(0,184,153,0.2)]' : ''}>
                            <ReactMarkdown 
                              components={{
                                h1: ({node, ...props}) => <h1 className="text-base font-bold mb-2 text-current" {...props} />,
                                h2: ({node, ...props}) => <h2 className="text-sm font-semibold mb-2 text-current" {...props} />,
                                h3: ({node, ...props}) => <h3 className="text-sm font-semibold mb-1 text-current" {...props} />,
                                p: ({node, ...props}) => <p className="mb-2 leading-relaxed text-sm text-current" {...props} />,
                                strong: ({node, ...props}) => <strong className="font-semibold" {...props} />,
                                ul: ({node, ...props}) => <ul className="list-disc list-inside mb-2 space-y-0.5 text-sm" {...props} />,
                                ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-2 space-y-0.5 text-sm" {...props} />,
                                li: ({node, ...props}) => <li className="leading-relaxed text-sm" {...props} />,
                                code: ({node, ...props}) => <code className="bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] px-1.5 py-0.5 rounded text-xs font-mono" {...props} />
                              }}
                            >
                              {message.content}
                            </ReactMarkdown>
                          </div>
                        ) : (
                          message.streaming && (!message.agentDetails || Object.keys(message.agentDetails).length === 0) ? (
                            <div className="flex items-center space-x-3 p-4 bg-gradient-to-r from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.1)] rounded-2xl border border-[rgba(0,184,153,0.2)]">
                              <div className="relative">
                                <div className="w-8 h-8 bg-[rgb(0,184,153)] rounded-full flex items-center justify-center shadow-lg">
                                  <div className="flex space-x-0.5">
                                    <div className="w-1 h-1 bg-white rounded-full animate-bounce"></div>
                                    <div className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                    <div className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                  </div>
                                </div>
                                <div className="absolute -inset-1 bg-[rgb(0,184,153)] rounded-full animate-ping opacity-30"></div>
                              </div>
                              <div>
                                <span className="text-sm font-bold text-white">🧠 Artha AI is initializing...</span>
                                <p className="text-xs text-[rgb(0,184,153)] font-medium">Connecting to financial agents</p>
                              </div>
                            </div>
                          ) : ''
                        )}
                        <div className="flex items-center justify-between mt-3 pt-2 border-t border-[rgba(0,184,153,0.1)]">
                          <div className="text-xs text-gray-400 font-medium">
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </div>
                          {message.mode && (
                            <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-semibold ${
                              message.mode === 'quick' ? 'bg-[rgba(245,158,11,0.1)] text-yellow-400 border border-[rgba(245,158,11,0.2)]' : 'bg-[rgba(0,184,153,0.1)] text-[rgb(0,184,153)] border border-[rgba(0,184,153,0.2)]'
                            }`}>
                              <span>{message.mode === 'quick' ? '⚡' : '🔬'}</span>
                              <span>{message.mode === 'quick' ? 'Quick' : 'FiXpert'}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Premium Input Area with Dark Glass Effect */}
          <div className="border-t border-[rgba(0,184,153,0.2)] px-6 py-5 bg-gradient-to-r from-[rgba(0,26,30,0.95)] to-[rgba(24,25,27,0.95)] backdrop-blur-xl">
            <div className="flex items-end space-x-4">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about your portfolio, investments, or financial goals..."
                  className="w-full px-6 py-4 bg-[rgba(30,32,34,0.8)] border border-[rgba(0,184,153,0.2)] rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[rgb(0,184,153)] focus:border-[rgb(0,184,153)] backdrop-blur-sm transition-all duration-300 shadow-sm hover:shadow-md"
                  disabled={isLoading}
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <div className="w-8 h-8 bg-gradient-to-br from-[rgba(0,184,153,0.1)] to-[rgba(0,184,153,0.2)] border border-[rgba(0,184,153,0.2)] rounded-xl flex items-center justify-center">
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setAgentMode(agentMode === 'quick' ? 'research' : 'quick')}
                className={`p-3 rounded-2xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 ${
                  agentMode === 'research'
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white border-2 border-purple-400/50'
                    : 'bg-[rgba(30,32,34,0.8)] border-2 border-[rgba(0,184,153,0.3)] text-gray-300 hover:text-white hover:border-[rgba(0,184,153,0.6)]'
                }`}
                title={agentMode === 'research' ? 'DeepFI Mode Active' : 'Enable DeepFI Mode'}
              >
                DeepFI
              </button>
              <button
                onClick={handleSendMessage}
                disabled={!currentMessage.trim() || isLoading}
                className={`p-4 rounded-2xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform ${
                  !currentMessage.trim() || isLoading
                    ? 'bg-[rgba(156,163,175,0.2)] text-gray-500 cursor-not-allowed border border-[rgba(156,163,175,0.2)]'
                    : 'bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white hover:from-[rgb(0,164,133)] hover:to-[rgb(0,144,113)] hover:scale-105 active:scale-95'
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
            
            {/* Example Questions */}
            <div className="mt-4 space-y-3">
              {/* Example Questions */}
              <div className="flex flex-wrap gap-3 justify-center">
              {exampleQueries.slice(0, 3).map((query, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleQuery(query.text)}
                  className="group flex items-center space-x-2 px-4 py-2 bg-[rgba(0,184,153,0.1)] border border-[rgba(0,184,153,0.2)] text-gray-300 rounded-2xl hover:bg-[rgba(0,184,153,0.2)] hover:border-[rgba(0,184,153,0.4)] hover:text-white transition-all duration-300 backdrop-blur-sm shadow-sm hover:shadow-md"
                >
                  <span className="text-sm">{query.icon}</span>
                  <span className="text-sm font-medium">{query.text}</span>
                </button>
              ))}
              </div>
            </div>
          </div>
        </div>
        
        {/* Modern Quick Start Tips */}
        <div className="mt-6 text-center">
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.1)] border border-[rgba(0,184,153,0.2)] rounded-2xl">
            <svg className="w-4 h-4 text-[rgb(0,184,153)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm text-[rgb(0,184,153)] font-medium">
              Powered by advanced AI agents with real-time market data & portfolio analysis
            </p>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}