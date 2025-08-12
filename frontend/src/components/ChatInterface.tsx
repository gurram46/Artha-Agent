'use client';

import { useState, useRef, useEffect } from 'react';
import UnifiedCard, { CardContent } from '@/components/ui/UnifiedCard';
import UnifiedButton from '@/components/ui/UnifiedButton';
import ErrorBoundary from './ErrorBoundary';
import { Message, StreamMessage, DEFAULT_STREAMING_CONFIG, AgentDetail, AgentMode } from '@/types/chat';
import ReactMarkdown from 'react-markdown';
import { designSystem } from '@/styles/designSystem';
import { chatService, ChatConversation } from '@/services/chatService';
import ConversationSidebar from './ConversationSidebar';
import { FinancialAnalysisExportButton, ChatExportButton } from './PDFExportButton';

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
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [agentMode, setAgentMode] = useState<AgentMode>('quick');
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [userData, setUserData] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Chat saving state
  const [currentConversation, setCurrentConversation] = useState<ChatConversation | null>(null);
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [showSidebar, setShowSidebar] = useState(false);
  
  // PDF upload state
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isProcessingPDF, setIsProcessingPDF] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Manage body overflow based on messages
  useEffect(() => {
    if (messages.length === 0) {
      document.body.style.overflow = 'hidden';
      document.body.style.height = '100vh';
    } else {
      document.body.style.overflow = 'auto';
      document.body.style.height = 'auto';
    }
    
    // Cleanup function to reset on unmount
    return () => {
      document.body.style.overflow = 'auto';
      document.body.style.height = 'auto';
    };
  }, [messages.length]);

  useEffect(() => {
    // Detect demo mode from session storage
    const demoMode = sessionStorage.getItem('demoMode') === 'true';
    setIsDemoMode(demoMode);
    
    // Load user data from localStorage
    const savedUserData = localStorage.getItem('userData');
    if (savedUserData) {
      try {
        const parsedUserData = JSON.parse(savedUserData);
        setUserData(parsedUserData);
      } catch (error) {
        console.error('Error parsing user data:', error);
      }
    }
  }, []);

  // Set initial greeting message when userData is loaded
  useEffect(() => {
    if (messages.length === 0) {
      // No initial greeting message - start with empty chat
      setMessages([]);
    }
  }, [userData, messages.length]);

  // Load conversations when user data is available
  useEffect(() => {
    if (userData?.user_id) {
      loadConversations();
    }
  }, [userData]);

  // Initialize chat and restore previous conversation on mount
  useEffect(() => {
    const initializeChat = async () => {
      try {
        // Try to restore previous conversation from localStorage
        const savedConversation = await chatService.initializeFromStorage();
        if (savedConversation && savedConversation.messages) {
          setCurrentConversation(savedConversation);
          // Convert messages to the correct format
          const convertedMessages: Message[] = savedConversation.messages.map((msg, index) => ({
            id: `${savedConversation.id}-${index}`,
            type: msg.role as 'user' | 'assistant',
            content: msg.content,
            timestamp: new Date(msg.timestamp),
            mode: (msg.agent_mode as AgentMode) || 'quick',
            streaming: false
          }));
          setMessages(convertedMessages);
        }
      } catch (error) {
        console.error('Failed to restore previous conversation:', error);
      }
    };

    // Initialize chat regardless of demo mode
    initializeChat();
  }, []);

  // Conversation management functions
  const loadConversations = async () => {
    try {
      const userConversations = await chatService.getUserConversations(userData?.user_id || 'anonymous');
      setConversations(userConversations);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  // PDF upload handlers
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== files.length) {
      alert('Please select only PDF files.');
      return;
    }
    
    if (pdfFiles.length > 5) {
      alert('Maximum 5 files allowed at once.');
      return;
    }
    
    setUploadedFiles(prev => [...prev, ...pdfFiles]);
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const processPDFFiles = async () => {
    if (uploadedFiles.length === 0) return null;
    
    setIsProcessingPDF(true);
    
    try {
      // Handle multiple files by processing them one by one
      const results = [];
      
      for (const file of uploadedFiles) {
        const formData = new FormData();
        formData.append('file', file); // Use 'file' (singular) as expected by backend
        formData.append('user_query', currentMessage || 'Analyze my financial data and provide insights');
        
        const response = await fetch('http://localhost:8000/api/pdf/analyze-with-ai', {
          method: 'POST',
          body: formData,
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('PDF processing error response:', errorText);
          throw new Error(`PDF processing failed for ${file.name}: ${response.statusText}`);
        }
        
        const result = await response.json();
        results.push({
          filename: file.name,
          ...result
        });
      }
      
      setUploadedFiles([]); // Clear files after processing
      return results.length === 1 ? results[0] : results;
    } catch (error) {
      console.error('PDF processing error:', error);
      throw error;
    } finally {
      setIsProcessingPDF(false);
    }
  };

  const startNewConversation = async () => {
    try {
      await chatService.startNewConversation();
      setCurrentConversation(null);
      setMessages([]);
    } catch (error) {
      console.error('Failed to start new conversation:', error);
      // Still clear the UI even if the service call fails
      setCurrentConversation(null);
      setMessages([]);
    }
  };

  const loadConversation = async (conversation: ChatConversation) => {
    try {
      setCurrentConversation(conversation);
      const history = await chatService.getConversationHistory(conversation.id);
      
      if (history && history.messages) {
        // Convert chat messages to Message format
        const convertedMessages: Message[] = history.messages.map((msg, index) => ({
          id: `${conversation.id}-${index}`,
          type: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          mode: (msg.agent_mode as AgentMode) || 'quick',
          streaming: false
        }));
        
        setMessages(convertedMessages);
      } else {
        setMessages([]);
      }
      
      setShowSidebar(false); // Close sidebar on mobile after loading
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  // Hackathon example queries from your submitted idea
  const exampleQueries = [
    { icon: '🔮', text: "How much money will I have at 40?", category: 'Planning' },
    { icon: '🏠', text: "Can I afford a ₹50L home loan?", category: 'Loans' },
    { icon: '📊', text: "Which SIPs underperformed the market?", category: 'Analysis' },
    { icon: '🚗', text: "Should I buy a car worth 20 lakhs?", category: 'Purchase' }
  ];

  // System default answers for basic questions
  const getSystemDefaultAnswer = (query: string): string | null => {
    const lowerQuery = query.toLowerCase().trim();
    
    // Model information questions
    if (lowerQuery.includes('which model') || lowerQuery.includes('what model') || 
        lowerQuery.includes('model used') || lowerQuery.includes('ai model') ||
        lowerQuery.includes('model are you') || lowerQuery.includes('model do you use')) {
      return `I'm powered by **Artha V 0.1**, a specialized financial AI model designed specifically for Indian financial markets and personal finance management.

**Key Features:**
• 🧠 **Advanced Financial Analysis** - Deep understanding of Indian financial instruments
• 📊 **Real-time Market Data** - Live integration with stock markets and mutual funds
• 💡 **Personalized Insights** - Tailored advice based on your financial profile
• 🔒 **Secure & Private** - Your financial data is processed securely

**Capabilities:**
• Portfolio analysis and optimization
• Investment recommendations
• Risk assessment
• Financial planning and goal setting
• Market research and analysis

Artha V 0.1 combines the power of large language models with specialized financial knowledge to provide you with accurate, relevant, and actionable financial insights.`;
    }

    // Version information
    if (lowerQuery.includes('version') || lowerQuery.includes('what version')) {
      return `I'm running on **Artha V 0.1** - the latest version of our financial AI assistant.

**Current Version Features:**
• Enhanced portfolio analysis
• Real-time market integration
• Advanced risk assessment
• Personalized investment recommendations
• Multi-agent financial research system

This version includes significant improvements in financial data processing and personalized advice generation.`;
    }

    // About Artha questions
    if (lowerQuery.includes('what is artha') || lowerQuery.includes('about artha') || 
        lowerQuery.includes('tell me about artha')) {
      return `**Artha** is your AI-powered financial intelligence platform, designed specifically for Indian investors and financial planning.

**What Artha Means:**
"Artha" (अर्थ) is a Sanskrit word meaning "wealth," "prosperity," and "economic security" - one of the four goals of human life in Hindu philosophy.

**Our Mission:**
To democratize financial intelligence and make sophisticated financial analysis accessible to every Indian investor.

**Key Features:**
• 📊 **Real-time Portfolio Tracking** - Monitor your investments across all platforms
• 🤖 **AI-Powered Analysis** - Get insights powered by Artha V 0.1
• 📈 **Market Intelligence** - Stay updated with live market data
• 💡 **Personalized Advice** - Recommendations tailored to your goals
• 🔒 **Secure Integration** - Safe connection with your financial accounts

Artha combines cutting-edge AI technology with deep understanding of Indian financial markets to help you make smarter investment decisions.`;
    }

    // Capabilities questions
    if (lowerQuery.includes('what can you do') || lowerQuery.includes('capabilities') || 
        lowerQuery.includes('features') || lowerQuery.includes('help me with')) {
      return `I can help you with a wide range of financial tasks using **Artha V 0.1**:

**📊 Portfolio Management:**
• Analyze your current investments
• Track performance across all assets
• Identify underperforming investments
• Suggest portfolio rebalancing

**💡 Investment Advice:**
• Recommend suitable mutual funds and stocks
• Assess investment risks
• Plan SIP strategies
• Evaluate new investment opportunities

**📈 Market Analysis:**
• Provide real-time stock analysis
• Research company fundamentals
• Track market trends and news
• Compare investment options

**🎯 Financial Planning:**
• Goal-based investment planning
• Retirement planning calculations
• Tax optimization strategies
• Emergency fund planning

**🔍 Research & Insights:**
• Deep dive analysis on specific stocks
• Sector and industry research
• Economic trend analysis
• Risk assessment reports

Just ask me anything about your finances, and I'll provide detailed, personalized insights using advanced AI analysis!`;
    }

    return null;
  };

  const handleSendMessage = async () => {
    if ((!currentMessage.trim() && uploadedFiles.length === 0) || isLoading) return;

    let pdfAnalysisResult = null;
    
    // Process PDFs if any are uploaded
    if (uploadedFiles.length > 0) {
      try {
        setIsLoading(true);
        pdfAnalysisResult = await processPDFFiles();
        
        // If we have PDF analysis result, display it directly
        if (pdfAnalysisResult) {
          // Create user message with PDF info
          const fileNames = uploadedFiles.map(f => f.name).join(', ');
          const userMessage: Message = {
            id: Date.now().toString(),
            type: 'user',
            content: `${currentMessage}\n\n📄 Uploaded files: ${fileNames}`,
            timestamp: new Date(),
            mode: agentMode
          };
          
          setMessages(prev => [...prev, userMessage]);
          setCurrentMessage('');
          
          // Create AI response message with PDF analysis
          const aiMessage: Message = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: pdfAnalysisResult.analysis || pdfAnalysisResult.ai_analysis || 'PDF analysis completed successfully.',
            timestamp: new Date(),
            streaming: false,
            mode: agentMode
          };
          
          setMessages(prev => [...prev, aiMessage]);
          setIsLoading(false);
          
          // Save messages to conversation
          let conversationId = currentConversation?.id;
          if (!conversationId) {
            try {
              conversationId = await chatService.createConversation(agentMode);
              // Load the full conversation object
              const newConversation = await chatService.getConversationHistory(conversationId);
              setCurrentConversation(newConversation);
            } catch (error) {
              console.error('Failed to create conversation:', error);
            }
          }
          
          if (conversationId) {
            try {
              await chatService.addMessage(
                'user',
                userMessage.content,
                agentMode
              );
              
              await chatService.addMessage(
                'assistant',
                aiMessage.content,
                agentMode
              );
              
              // Refresh conversations list
              loadConversations();
            } catch (error) {
              console.error('Failed to save messages:', error);
            }
          }
          
          return; // Exit early since we've handled the PDF response
        }
      } catch (error) {
        setIsLoading(false);
        alert('Failed to process PDF files. Please try again.');
        return;
      }
    }

    // Regular message handling (no PDFs)
    // Create user message with PDF info if applicable
    let messageContent = currentMessage;
    if (uploadedFiles.length > 0) {
      const fileNames = uploadedFiles.map(f => f.name).join(', ');
      messageContent = `${currentMessage}\n\n📄 Uploaded files: ${fileNames}`;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: messageContent,
      timestamp: new Date(),
      mode: agentMode
    };

    const query = pdfAnalysisResult 
      ? `${currentMessage}\n\nPDF Analysis Results:\n${JSON.stringify(pdfAnalysisResult, null, 2)}`
      : currentMessage;
      
    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');

    // Create or get conversation for saving
    let conversationId = currentConversation?.id;
    if (!conversationId) {
      try {
        conversationId = await chatService.createConversation(agentMode);
        // Load the full conversation object
        const newConversation = await chatService.getConversationHistory(conversationId);
        setCurrentConversation(newConversation);
      } catch (error) {
        console.error('Failed to create conversation:', error);
      }
    }

    // Save user message
    if (conversationId) {
      try {
        await chatService.addMessage(
          'user',
          currentMessage,
          agentMode
        );
      } catch (error) {
        console.error('Failed to save user message:', error);
      }
    }

    // Check for system default answers first
    const systemAnswer = getSystemDefaultAnswer(query);
    if (systemAnswer) {
      const systemMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: systemAnswer,
        timestamp: new Date(),
        streaming: false,
        mode: agentMode
      };
      setMessages(prev => [...prev, systemMessage]);
      
      // Save system answer
      if (conversationId) {
        try {
          await chatService.addMessage(
            'assistant',
            systemAnswer,
            agentMode
          );
          // Refresh conversations list
          loadConversations();
        } catch (error) {
          console.error('Failed to save system message:', error);
        }
      }
      return;
    }

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
        const streamResponse = await fetch('http://localhost:8000/api/stream/query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            query,
            mode: agentMode,
            demo_mode: isDemoMode,
            user_data: userData // Include user data in the request
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
                prev.map(msg => {
                  if (msg.id === messageId) {
                    // Save the completed assistant message
                    if (currentConversation?.id && msg.content) {
                      chatService.addMessage(
                        'assistant',
                        msg.content,
                        agentMode
                      ).then(() => {
                        // Refresh conversations list after saving
                        loadConversations();
                      }).catch(error => {
                        console.error('Failed to save assistant message:', error);
                      });
                    }
                    return { ...msg, streaming: false };
                  }
                  return msg;
                })
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

      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query,
          mode: agentMode,
          demo_mode: isDemoMode,
          user_data: userData // Include user data in the request
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
          errorMessage = 'Cannot connect to the AI backend. Please ensure the server is running on port 8000.';
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
      <div className={`bg-[rgb(0,26,30)] flex ${messages.length === 0 ? 'h-screen' : 'min-h-screen'}`}>
        {/* Conversation Sidebar */}
        <ConversationSidebar
          isOpen={showSidebar}
          onClose={() => setShowSidebar(false)}
          onSelectConversation={loadConversation}
          onNewConversation={startNewConversation}
          currentConversationId={currentConversation?.id}
        />
        
        {/* Main Chat Area */}
        <div className={`flex-1 flex flex-col ${messages.length === 0 ? 'h-screen' : 'min-h-screen'}`}>
          {/* Header with Chat History Toggle */}
          <div className="flex items-center justify-between p-4 border-b border-[rgba(255,255,255,0.1)]">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="p-2 rounded-lg bg-[rgba(255,255,255,0.1)] hover:bg-[rgba(255,255,255,0.2)] transition-colors"
              title="Toggle Chat History"
            >
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            
            <div className="flex items-center space-x-4">
              {currentConversation && (
                <div className="text-sm text-gray-400">
                  {currentConversation.title || 'Current Conversation'}
                </div>
              )}
              
              {/* PDF Export Buttons */}
              <div className="flex items-center space-x-2">
                {currentConversation && (
                  <ChatExportButton
                    conversationId={currentConversation.id}
                    userId={userData?.email || 'demo-user'}
                    variant="minimal"
                    className="text-xs"
                    onExportStart={() => console.log('Exporting chat...')}
                    onExportComplete={() => console.log('Chat exported successfully')}
                    onExportError={(error) => console.error('Export error:', error)}
                  />
                )}
                
                <FinancialAnalysisExportButton
                  variant="minimal"
                  className="text-xs"
                  onExportStart={() => console.log('Generating financial analysis...')}
                  onExportComplete={() => console.log('Analysis generated successfully')}
                  onExportError={(error) => console.error('Export error:', error)}
                />
              </div>
              
              <button
                onClick={startNewConversation}
                className="px-3 py-1.5 bg-[rgb(0,184,153)] hover:bg-[rgb(0,164,133)] text-white rounded-lg text-sm font-medium transition-colors"
                title="Start New Conversation"
              >
                New Chat
              </button>
            </div>
          </div>
          
        {/* Gemini-style Layout */}
        {messages.length === 0 ? (
          /* Initial Welcome Screen - Gemini Style */
          <div className="flex-1 flex flex-col items-center justify-center px-4">
            {/* Centered Greeting */}
            <div className="text-center mb-12">
              <h1 className="text-4xl font-normal text-white mb-2">
                {isDemoMode ? 'Hello, Demo User' : (userData?.firstName ? `Hello, ${userData.firstName}` : 'Hello')}
              </h1>
            </div>

            {/* Centered Input Box */}
            <div className="w-full max-w-3xl mb-8">
              <div className="relative">
                <input
                  type="text"
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask Artha anything..."
                  className="w-full pl-16 pr-36 py-4 bg-[rgb(24,25,27)] border border-[rgba(255,255,255,0.1)] rounded-full text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[rgb(0,184,153)] focus:border-[rgb(0,184,153)] text-lg"
                  disabled={isLoading}
                />
                <div className="absolute left-5 top-1/2 transform -translate-y-1/2">
                  {/* PDF Upload Button */}
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="p-2 rounded-full bg-[rgba(255,255,255,0.1)] hover:bg-[rgba(255,255,255,0.2)] transition-colors group"
                    title="Upload PDF Documents"
                    disabled={isLoading || isProcessingPDF}
                  >
                    <svg className="w-5 h-5 text-gray-300 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf"
                    multiple
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </div>
                <div className="absolute right-5 top-1/2 transform -translate-y-1/2 flex items-center space-x-3">
                  {/* Think Button */}
                  <button
                    onClick={() => setAgentMode(agentMode === 'quick' ? 'research' : 'quick')}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                      agentMode === 'research'
                        ? 'bg-[rgb(0,184,153)] text-white shadow-lg'
                        : 'bg-[rgba(255,255,255,0.1)] text-gray-300 hover:bg-[rgba(255,255,255,0.2)]'
                    }`}
                    title={agentMode === 'research' ? 'Think Mode Active' : 'Enable Think Mode'}
                  >
                    Think
                  </button>
                  
                  {/* Send Button */}
                  <button
                    onClick={handleSendMessage}
                    disabled={(!currentMessage.trim() && uploadedFiles.length === 0) || isLoading}
                    className={`p-3 rounded-full transition-all duration-300 ${
                      (!currentMessage.trim() && uploadedFiles.length === 0) || isLoading
                        ? 'bg-[rgba(255,255,255,0.1)] text-gray-500 cursor-not-allowed'
                        : 'bg-[rgb(0,184,153)] text-white hover:bg-[rgb(0,164,133)] shadow-lg'
                    }`}
                  >
                    {isLoading || isProcessingPDF ? (
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
              
              {/* Uploaded Files Display */}
              {uploadedFiles.length > 0 && (
                <div className="mt-4 space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between bg-[rgb(24,25,27)] border border-[rgba(255,255,255,0.1)] rounded-lg px-4 py-2">
                      <div className="flex items-center space-x-3">
                        <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        <span className="text-white text-sm">{file.name}</span>
                        <span className="text-gray-400 text-xs">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                      </div>
                      <button
                        onClick={() => removeFile(index)}
                        className="p-1 rounded-full hover:bg-[rgba(255,255,255,0.1)] transition-colors"
                        disabled={isProcessingPDF}
                      >
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Example Questions - Gemini Style */}
            <div className="w-full max-w-4xl">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {exampleQueries.slice(0, 3).map((query, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleQuery(query.text)}
                    className="p-4 bg-[rgb(24,25,27)] border border-[rgba(255,255,255,0.1)] rounded-2xl text-left hover:bg-[rgb(30,32,34)] transition-all duration-300 group"
                  >
                    <div className="flex items-start space-x-3">
                      <span className="text-2xl">{query.icon}</span>
                      <div>
                        <p className="text-white font-medium text-sm">{query.text}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* Chat Mode - When messages exist */
          <div className="flex-1 flex flex-col">
            {/* Chat Messages - Normal Flow */}
            <div className="flex-1 p-4 max-w-4xl mx-auto w-full pb-24">
              {messages.map((message) => (
                <div key={message.id} className="mb-6">
                  <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] ${
                      message.type === 'user' 
                        ? 'bg-[rgb(0,184,153)] text-white rounded-2xl px-4 py-3' 
                        : 'text-white'
                    }`}>
                      {message.processing ? (
                        <div className="flex items-center space-x-3 p-4 bg-gradient-to-r from-[rgba(0,184,153,0.08)] to-[rgba(0,164,133,0.12)] rounded-2xl border border-[rgba(0,184,153,0.15)]">
                          <div className="w-6 h-6 relative">
                            <div className="absolute inset-0 border-2 border-[rgba(0,184,153,0.3)] border-t-[rgb(0,184,153)] rounded-full animate-spin"></div>
                            <div className="absolute inset-1 bg-[rgb(0,184,153)] rounded-full opacity-60 animate-pulse"></div>
                          </div>
                          <span className="text-sm font-medium text-white">Processing request...</span>
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
                            <div className={message.type === 'assistant' && message.agentDetails ? 'mt-4 pt-4 border-t border-[rgba(255,255,255,0.1)]' : ''}>
                              <ReactMarkdown 
                                components={{
                                  h1: ({node, ...props}) => <h1 className="text-lg font-bold mb-3 text-current" {...props} />,
                                  h2: ({node, ...props}) => <h2 className="text-base font-semibold mb-2 text-current" {...props} />,
                                  h3: ({node, ...props}) => <h3 className="text-base font-semibold mb-2 text-current" {...props} />,
                                  p: ({node, ...props}) => <p className="mb-3 leading-relaxed text-current" {...props} />,
                                  strong: ({node, ...props}) => <strong className="font-semibold" {...props} />,
                                  ul: ({node, ...props}) => <ul className="list-disc list-inside mb-3 space-y-1" {...props} />,
                                  ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-3 space-y-1" {...props} />,
                                  li: ({node, ...props}) => <li className="leading-relaxed" {...props} />,
                                  code: ({node, ...props}) => <code className="bg-[rgba(255,255,255,0.1)] px-2 py-1 rounded text-sm font-mono" {...props} />
                                }}
                              >
                                {message.content}
                              </ReactMarkdown>
                            </div>
                          ) : (
                            message.streaming && (!message.agentDetails || Object.keys(message.agentDetails).length === 0) ? (
                              <div className="flex items-center space-x-4 p-5 bg-gradient-to-r from-[rgba(0,184,153,0.08)] to-[rgba(0,164,133,0.12)] rounded-2xl border border-[rgba(0,184,153,0.15)] backdrop-blur-sm">
                                <div className="relative">
                                  {/* Sophisticated AI Processing Animation */}
                                  <div className="w-10 h-10 relative">
                                    {/* Outer rotating ring */}
                                    <div className="absolute inset-0 border-2 border-[rgba(0,184,153,0.3)] border-t-[rgb(0,184,153)] rounded-full animate-spin"></div>
                                    {/* Inner pulsing core */}
                                    <div className="absolute inset-2 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-full flex items-center justify-center shadow-lg">
                                      <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                                    </div>
                                    {/* Subtle glow effect */}
                                    <div className="absolute -inset-1 bg-[rgb(0,184,153)] rounded-full opacity-20 animate-pulse"></div>
                                  </div>
                                </div>
                                <div className="flex-1">
                                  <div className="flex items-center space-x-2 mb-1">
                                    <span className="text-base font-semibold text-white">Artha AI</span>
                                    <div className="flex space-x-1">
                                      <div className="w-1 h-1 bg-[rgb(0,184,153)] rounded-full animate-pulse"></div>
                                      <div className="w-1 h-1 bg-[rgb(0,184,153)] rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                                      <div className="w-1 h-1 bg-[rgb(0,184,153)] rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                                    </div>
                                  </div>
                                  <p className="text-sm text-[rgba(0,184,153,0.9)] font-medium">Processing your financial query with advanced AI models</p>
                                </div>
                              </div>
                            ) : ''
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Fixed Bottom Input Area - Gemini Style */}
            <div className="fixed bottom-0 left-0 right-0 bg-[rgb(16,17,19)] border-t border-[rgba(255,255,255,0.1)] p-4 z-10">
              <div className="max-w-3xl mx-auto">
                {/* Uploaded Files Display */}
                {uploadedFiles.length > 0 && (
                  <div className="mb-4 space-y-2">
                    {uploadedFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-between bg-[rgb(24,25,27)] border border-[rgba(255,255,255,0.1)] rounded-lg px-4 py-2">
                        <div className="flex items-center space-x-3">
                          <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                          </svg>
                          <span className="text-white text-sm">{file.name}</span>
                          <span className="text-gray-400 text-xs">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                        </div>
                        <button
                          onClick={() => removeFile(index)}
                          className="p-1 rounded-full hover:bg-[rgba(255,255,255,0.1)] transition-colors"
                          disabled={isProcessingPDF}
                        >
                          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="relative">
                  <input
                    type="text"
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask Artha anything..."
                    className="w-full pl-16 pr-36 py-4 bg-[rgb(24,25,27)] border border-[rgba(255,255,255,0.1)] rounded-full text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[rgb(0,184,153)] focus:border-[rgb(0,184,153)] text-lg"
                    disabled={isLoading}
                  />
                  <div className="absolute left-5 top-1/2 transform -translate-y-1/2">
                    {/* PDF Upload Button */}
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="p-2 rounded-full bg-[rgba(255,255,255,0.1)] hover:bg-[rgba(255,255,255,0.2)] transition-colors group"
                      title="Upload PDF Documents"
                      disabled={isLoading || isProcessingPDF}
                    >
                      <svg className="w-5 h-5 text-gray-300 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                      </svg>
                    </button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf"
                      multiple
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                  </div>
                  <div className="absolute right-5 top-1/2 transform -translate-y-1/2 flex items-center space-x-3">
                    {/* Think Button */}
                    <button
                      onClick={() => setAgentMode(agentMode === 'quick' ? 'research' : 'quick')}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                        agentMode === 'research'
                          ? 'bg-[rgb(0,184,153)] text-white shadow-lg'
                          : 'bg-[rgba(255,255,255,0.1)] text-gray-300 hover:bg-[rgba(255,255,255,0.2)]'
                      }`}
                      title={agentMode === 'research' ? 'Think Mode Active' : 'Enable Think Mode'}
                    >
                      Think
                    </button>
                    
                    {/* Send Button */}
                    <button
                      onClick={handleSendMessage}
                      disabled={(!currentMessage.trim() && uploadedFiles.length === 0) || isLoading}
                      className={`p-3 rounded-full transition-all duration-300 ${
                        (!currentMessage.trim() && uploadedFiles.length === 0) || isLoading
                          ? 'bg-[rgba(255,255,255,0.1)] text-gray-500 cursor-not-allowed'
                          : 'bg-[rgb(0,184,153)] text-white hover:bg-[rgb(0,164,133)] shadow-lg'
                      }`}
                    >
                      {isLoading || isProcessingPDF ? (
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
          </div>
        )}
        </div>
      </div>
    </ErrorBoundary>
  );
}