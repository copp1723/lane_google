import React, { useState, useEffect, useRef } from 'react';
import { Send, MessageCircle, StopCircle, FileText, Sparkles, AlertCircle } from 'lucide-react';
import MessageBubble from './MessageBubble.jsx';
import useAIStream from '../../hooks/useAIStream.js';

const EnhancedChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your AI assistant for Google Ads campaign planning. I can help you create effective campaigns by understanding your business goals, target audience, and marketing objectives. What would you like to achieve with your advertising?',
      timestamp: new Date().toISOString()
    }
  ]);
  
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [streamingMessage, setStreamingMessage] = useState(null);
  const [canGenerateBrief, setCanGenerateBrief] = useState(false);
  const [isGeneratingBrief, setIsGeneratingBrief] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  
  const messagesEndRef = useRef(null);
  const { isStreaming, error: streamError, streamChat, stopStreaming } = useAIStream();

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  // Check API health on component mount
  useEffect(() => {
    checkAPIHealth();
  }, []);

  const checkAPIHealth = async () => {
    try {
      const response = await fetch('/api/ai/health');
      if (!response.ok) {
        throw new Error(`API Health Check Failed: ${response.status}`);
      }
      const health = await response.json();
      console.log('AI Service Health:', health);
      setConnectionError(null);
    } catch (err) {
      console.error('API health check failed:', err);
      setConnectionError('Unable to connect to AI service. Please check your backend.');
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setConnectionError(null);

    // Initialize streaming message
    const streamingMsgId = Date.now() + 1;
    setStreamingMessage({
      id: streamingMsgId,
      type: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isStreaming: true
    });

    // Stream the AI response
    await streamChat(
      userMessage.content,
      conversationId,
      // onChunk callback
      (chunk) => {
        setStreamingMessage(prev => ({
          ...prev,
          content: chunk.content,
          isComplete: chunk.isComplete
        }));
      },
      // onComplete callback
      (result) => {
        const assistantMessage = {
          id: streamingMsgId,
          type: 'assistant',
          content: result.content,
          timestamp: new Date().toISOString(),
          metadata: result.metadata
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        setStreamingMessage(null);
        
        // Update conversation state
        if (result.conversation_id) {
          setConversationId(result.conversation_id);
        }
        
        // Check if we can generate brief (after some conversation)
        setCanGenerateBrief(prev => prev || (messages.length + 1) >= 4);
      },
      // onError callback
      (errorMsg) => {
        setStreamingMessage(null);
        setConnectionError(`Failed to get AI response: ${errorMsg}`);
        
        // Add fallback message
        const fallbackMessage = {
          id: streamingMsgId,
          type: 'assistant',
          content: 'I apologize, but I\'m having trouble connecting to the AI service right now. Please try again in a moment, or contact support if the issue persists.',
          timestamp: new Date().toISOString(),
          error: true
        };
        setMessages(prev => [...prev, fallbackMessage]);
      }
    );
  };

  const generateCampaignBrief = async () => {
    if (!conversationId || isGeneratingBrief) return;

    setIsGeneratingBrief(true);
    
    try {
      const response = await fetch(`/api/ai/conversations/${conversationId}/brief`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to generate brief: ${response.status}`);
      }

      const result = await response.json();
      
      // Add brief generation message
      const briefMessage = {
        id: Date.now(),
        type: 'assistant',
        content: `I've generated a comprehensive campaign brief based on our conversation. Here's what I've prepared for you:

**Campaign Overview:**
• Campaign Name: ${result.brief.campaign_name}
• Objective: ${result.brief.objective}
• Budget: $${result.brief.budget?.toLocaleString()}

**Target Audience:** ${result.brief.target_audience}

**Geographic Targeting:** ${result.brief.geographic_targeting}

**Key Messages:** ${result.brief.key_messages}

**Success Metrics:** ${result.brief.success_metrics}

**Timeline:** ${result.brief.timeline}

${result.brief.additional_notes ? `**Additional Notes:** ${result.brief.additional_notes}` : ''}

Would you like me to proceed with creating the actual Google Ads campaign based on this brief?`,
        timestamp: new Date().toISOString(),
        metadata: {
          brief_generated: true,
          brief_data: result.brief
        }
      };

      setMessages(prev => [...prev, briefMessage]);
      
    } catch (err) {
      console.error('Brief generation failed:', err);
      setConnectionError(`Failed to generate campaign brief: ${err.message}`);
    } finally {
      setIsGeneratingBrief(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.6)',
      backdropFilter: 'blur(15px)',
      WebkitBackdropFilter: 'blur(15px)',
      border: '1px solid rgba(255, 255, 255, 0.5)',
      borderRadius: '20px',
      overflow: 'hidden',
      height: '600px',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Chat Header */}
      <div style={{ 
        padding: '1.5rem 2rem', 
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <MessageCircle size={24} style={{ color: '#6366f1' }} />
          <div>
            <h2 style={{ color: '#111827', fontSize: '1.25rem', fontWeight: '700', margin: 0 }}>
              Campaign AI Assistant
            </h2>
            <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: 0 }}>
              Google Ads Campaign Planning
            </p>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Status Indicator */}
          <div style={{
            background: connectionError 
              ? 'rgba(239, 68, 68, 0.2)' 
              : isStreaming 
                ? 'rgba(249, 115, 22, 0.2)'
                : 'rgba(16, 185, 129, 0.2)',
            borderRadius: '12px',
            padding: '4px 8px',
            color: connectionError 
              ? '#dc2626' 
              : isStreaming 
                ? '#ea580c'
                : '#10b981',
            fontSize: '0.75rem',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            {connectionError ? (
              <>
                <AlertCircle size={12} />
                Error
              </>
            ) : isStreaming ? (
              <>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: 'currentColor',
                  animation: 'pulse 1s infinite'
                }} />
                Thinking...
              </>
            ) : (
              'Online'
            )}
          </div>

          {/* Generate Brief Button */}
          {canGenerateBrief && conversationId && (
            <button
              onClick={generateCampaignBrief}
              disabled={isGeneratingBrief}
              style={{
                background: 'linear-gradient(135deg, #16a34a, #15803d)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                padding: '6px 12px',
                fontSize: '0.75rem',
                fontWeight: '600',
                cursor: isGeneratingBrief ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                opacity: isGeneratingBrief ? 0.6 : 1
              }}
            >
              {isGeneratingBrief ? (
                <>
                  <Sparkles size={12} />
                  Generating...
                </>
              ) : (
                <>
                  <FileText size={12} />
                  Generate Brief
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Connection Error Banner */}
      {connectionError && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          borderBottom: '1px solid rgba(239, 68, 68, 0.2)',
          padding: '12px 24px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <AlertCircle size={16} color="#dc2626" />
          <span style={{ color: '#dc2626', fontSize: '0.875rem' }}>
            {connectionError}
          </span>
          <button
            onClick={checkAPIHealth}
            style={{
              background: 'none',
              border: '1px solid #dc2626',
              color: '#dc2626',
              borderRadius: '4px',
              padding: '4px 8px',
              fontSize: '0.75rem',
              cursor: 'pointer',
              marginLeft: 'auto'
            }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Messages */}
      <div style={{ 
        flex: 1, 
        padding: '1rem 2rem',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {messages.map((message) => (
          <MessageBubble 
            key={message.id} 
            message={message}
            error={message.error}
          />
        ))}
        
        {/* Streaming Message */}
        {streamingMessage && (
          <MessageBubble 
            message={streamingMessage}
            isStreaming={true}
            error={streamError}
          />
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{ 
        padding: '1rem 2rem',
        borderTop: '1px solid rgba(255, 255, 255, 0.2)',
        display: 'flex',
        gap: '12px'
      }}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Describe your business goals, target audience, or ask about campaign optimization..."
          disabled={isStreaming}
          rows={1}
          style={{
            flex: 1,
            padding: '12px 16px',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            borderRadius: '12px',
            background: 'rgba(255, 255, 255, 0.5)',
            backdropFilter: 'blur(10px)',
            outline: 'none',
            fontSize: '0.875rem',
            resize: 'none',
            fontFamily: 'inherit',
            lineHeight: '1.5',
            minHeight: '44px',
            maxHeight: '120px'
          }}
        />
        
        {isStreaming ? (
          <button
            onClick={stopStreaming}
            style={{
              background: 'linear-gradient(135deg, #ef4444, #dc2626)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              padding: '12px 16px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <StopCircle size={16} />
          </button>
        ) : (
          <button
            onClick={sendMessage}
            disabled={!input.trim()}
            style={{
              background: input.trim() 
                ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
                : 'rgba(156, 163, 175, 0.5)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              padding: '12px 16px',
              cursor: input.trim() ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Send size={16} />
          </button>
        )}
      </div>

      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}
      </style>
    </div>
  );
};

export default EnhancedChatInterface;