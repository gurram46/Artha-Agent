import { useState, useCallback, useRef, useMemo } from 'react';
import { StreamMessage, DEFAULT_STREAMING_CONFIG, AgentMode } from '@/types/chat';

interface UseStreamingChatOptions {
  apiEndpoint?: string;
  streamEndpoint?: string;
  config?: Partial<typeof DEFAULT_STREAMING_CONFIG>;
}

export const useStreamingChat = (options: UseStreamingChatOptions = {}) => {
  const {
    apiEndpoint = 'http://localhost:8000/query',
  streamEndpoint = 'http://localhost:8000/api/deep-research',
    config = {}
  } = options;

  const finalConfig = useMemo(() => ({ ...DEFAULT_STREAMING_CONFIG, ...config }), [config]);
  const [isLoading, setIsLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleStreamingResponse = useCallback(
    async (response: Response, onUpdate: (content: string, streaming: boolean) => void) => {
      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let content = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim();
              if (data === '[DONE]') {
                onUpdate(content, false);
                return;
              }

              try {
                const parsed: StreamMessage = JSON.parse(data);
                
                if (parsed.type === 'content' && parsed.content) {
                  content += parsed.content;
                  onUpdate(content, true);
                } else if (parsed.type === 'status' && parsed.content) {
                  onUpdate(parsed.content, true);
                } else if (parsed.type === 'error') {
                  throw new Error(parsed.content);
                }
              } catch (e) {
                if (e instanceof Error && e.message !== data) {
                  throw e;
                }
              }
            }
          }
        }
      } catch (error) {
        throw error;
      }
    },
    []
  );

  const sendMessage = useCallback(
    async (
      message: string,
      onUpdate: (content: string, streaming: boolean) => void,
      mode?: AgentMode
    ): Promise<void> => {
      if (isLoading) return;

      setIsLoading(true);
      abortControllerRef.current = new AbortController();

      let retryCount = 0;

      const attemptRequest = async (): Promise<void> => {
        try {
          const timeoutId = setTimeout(() => abortControllerRef.current?.abort(), finalConfig.timeout);

          const streamResponse = await fetch(streamEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              query: message,
              mode: mode || 'research'
            }),
            signal: abortControllerRef.current?.signal
          });

          clearTimeout(timeoutId);

          if (streamResponse.ok && streamResponse.body) {
            await handleStreamingResponse(streamResponse, onUpdate);
          } else {
            throw new Error(`Streaming failed: ${streamResponse.status}`);
          }
        } catch (requestError) {
          if (retryCount < finalConfig.maxRetries && finalConfig.fallbackToRegular) {
            retryCount++;
            onUpdate(`Retrying... (${retryCount}/${finalConfig.maxRetries})`, true);
            await new Promise(resolve => setTimeout(resolve, finalConfig.retryDelay));
            return attemptRequest();
          } else {
            // Fallback to regular API
            const fallbackResponse = await fetch(apiEndpoint, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ 
                query: message,
                mode: mode || 'research'
              }),
              signal: abortControllerRef.current?.signal
            });

            if (!fallbackResponse.ok) {
              throw new Error(`API request failed: ${fallbackResponse.status}`);
            }

            const data = await fallbackResponse.json();
            onUpdate(data.response || 'No response received', false);
          }
        }
      };

      try {
        await attemptRequest();
      } finally {
        setIsLoading(false);
        abortControllerRef.current = null;
      }
    },
    [isLoading, streamEndpoint, apiEndpoint, handleStreamingResponse, finalConfig]
  );

  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    sendMessage,
    cancelRequest
  };
};