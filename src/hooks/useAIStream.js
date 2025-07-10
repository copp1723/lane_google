import { useState, useCallback, useRef } from 'react';

/**
 * Custom hook for streaming AI chat responses
 * Adapted for lane_google Flask backend
 */
export const useAIStream = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const streamChat = useCallback(async (message, conversationId, onChunk, onComplete, onError) => {
    if (isStreaming) {
      console.warn('Already streaming, ignoring new request');
      return;
    }

    setIsStreaming(true);
    setError(null);
    
    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          user_id: 'demo-user', // TODO: Get from auth context
          context: {}
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Since our Flask backend returns the complete response,
      // we'll simulate streaming by breaking it into chunks
      if (data.response) {
        const text = data.response;
        const words = text.split(' ');
        let currentText = '';
        
        for (let i = 0; i < words.length; i++) {
          if (abortControllerRef.current?.signal.aborted) {
            break;
          }
          
          currentText += (i > 0 ? ' ' : '') + words[i];
          
          // Call onChunk with current progress
          onChunk({
            content: currentText,
            isComplete: i === words.length - 1
          });
          
          // Add small delay to simulate streaming
          await new Promise(resolve => setTimeout(resolve, 50));
        }
        
        // Call completion callback
        onComplete({
          content: text,
          conversation_id: data.conversation_id,
          metadata: data.metadata
        });
      }

    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('Stream aborted');
      } else {
        const errorMessage = err.message || 'Failed to stream chat response';
        setError(errorMessage);
        onError?.(errorMessage);
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  }, [isStreaming]);

  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  return {
    isStreaming,
    error,
    streamChat,
    stopStreaming
  };
};

export default useAIStream;