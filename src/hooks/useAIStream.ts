import { useState, useCallback, useRef } from 'react';
import { EventSourceParserStream } from 'eventsource-parser/stream';

interface UseAIStreamOptions {
  endpoint?: string;
  model?: string;
  onToken?: (token: string) => void;
  onComplete?: (fullResponse: string) => void;
  onError?: (error: Error) => void;
  retryAttempts?: number;
  retryDelay?: number;
}

interface UseAIStreamReturn {
  stream: (prompt: string, options?: StreamOptions) => Promise<void>;
  cancel: () => void;
  isStreaming: boolean;
  error: Error | null;
  response: string;
  reset: () => void;
}

interface StreamOptions {
  temperature?: number;
  maxTokens?: number;
  systemPrompt?: string;
  signal?: AbortSignal;
}

export function useAIStream({
  endpoint = '/api/ai/stream',
  model = 'gpt-3.5-turbo',
  onToken,
  onComplete,
  onError,
  retryAttempts = 3,
  retryDelay = 1000,
}: UseAIStreamOptions = {}): UseAIStreamReturn {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [response, setResponse] = useState('');
  const abortControllerRef = useRef<AbortController | null>(null);
  const retryCountRef = useRef(0);

  const reset = useCallback(() => {
    setResponse('');
    setError(null);
    retryCountRef.current = 0;
  }, []);

  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const stream = useCallback(async (
    prompt: string,
    options: StreamOptions = {}
  ) => {
    // Reset state
    setError(null);
    setResponse('');
    setIsStreaming(true);

    // Create new abort controller
    abortControllerRef.current = new AbortController();
    const signal = options.signal || abortControllerRef.current.signal;

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          model,
          temperature: options.temperature,
          maxTokens: options.maxTokens,
          systemPrompt: options.systemPrompt,
          stream: true,
        }),
        signal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.message || `HTTP error! status: ${response.status}`
        );
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      // Set up the streaming parser
      const reader = response.body
        .pipeThrough(new TextDecoderStream())
        .pipeThrough(new EventSourceParserStream())
        .getReader();

      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        if (value.data === '[DONE]') {
          break;
        }

        try {
          const data = JSON.parse(value.data || '{}');
          const token = data.choices?.[0]?.delta?.content || '';
          
          if (token) {
            fullResponse += token;
            setResponse(prev => prev + token);
            onToken?.(token);
          }
        } catch (parseError) {
          console.error('Error parsing SSE data:', parseError);
        }
      }

      setIsStreaming(false);
      onComplete?.(fullResponse);
      retryCountRef.current = 0;

    } catch (err) {
      const error = err as Error;
      
      // Don't retry on user cancellation
      if (error.name === 'AbortError') {
        setIsStreaming(false);
        return;
      }

      // Retry logic
      if (retryCountRef.current < retryAttempts) {
        retryCountRef.current++;
        console.log(`Retrying... Attempt ${retryCountRef.current} of ${retryAttempts}`);
        
        setTimeout(() => {
          stream(prompt, options);
        }, retryDelay * retryCountRef.current);
        
        return;
      }

      setError(error);
      setIsStreaming(false);
      onError?.(error);
      retryCountRef.current = 0;
    }
  }, [endpoint, model, onToken, onComplete, onError, retryAttempts, retryDelay]);

  return {
    stream,
    cancel,
    isStreaming,
    error,
    response,
    reset,
  };
}

// Export a simpler hook for basic use cases
export function useSimpleAIStream(endpoint?: string) {
  const [response, setResponse] = useState('');
  
  const { stream, ...rest } = useAIStream({
    endpoint,
    onToken: (token) => setResponse(prev => prev + token),
  });

  return {
    ...rest,
    response,
    sendMessage: stream,
  };
}
