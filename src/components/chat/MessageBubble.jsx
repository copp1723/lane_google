import React from 'react';
import { User, Bot, AlertCircle, CheckCircle } from 'lucide-react';

const MessageBubble = ({ 
  message, 
  isStreaming = false, 
  error = null,
  showAvatar = true,
  showTimestamp = true 
}) => {
  const isUser = message.type === 'user';
  const isAssistant = message.type === 'assistant';

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getBubbleStyles = () => {
    if (isUser) {
      return {
        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
        color: 'white',
        borderRadius: '20px 20px 5px 20px',
        marginLeft: 'auto',
        maxWidth: '80%'
      };
    }
    
    return {
      background: error 
        ? 'rgba(239, 68, 68, 0.1)' 
        : 'rgba(255, 255, 255, 0.9)',
      color: error ? '#dc2626' : '#1f2937',
      borderRadius: '20px 20px 20px 5px',
      border: `1px solid ${error ? 'rgba(239, 68, 68, 0.3)' : 'rgba(255, 255, 255, 0.5)'}`,
      backdropFilter: 'blur(10px)',
      maxWidth: '80%'
    };
  };

  const TypingIndicator = () => (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '4px',
      padding: '8px 0'
    }}>
      <div style={{
        display: 'flex',
        gap: '4px'
      }}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: '#6b7280',
              animation: `typing-bounce 1.4s infinite ${i * 0.2}s`,
            }}
          />
        ))}
      </div>
      <span style={{ 
        fontSize: '0.875rem', 
        color: '#6b7280',
        marginLeft: '8px'
      }}>
        AI is thinking...
      </span>
      <style>
        {`
          @keyframes typing-bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
          }
        `}
      </style>
    </div>
  );

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: isUser ? 'flex-end' : 'flex-start',
      marginBottom: '1rem'
    }}>
      {/* Avatar and Message Container */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-end',
        gap: '12px',
        maxWidth: '100%',
        flexDirection: isUser ? 'row-reverse' : 'row'
      }}>
        {/* Avatar */}
        {showAvatar && (
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            background: isUser 
              ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
              : 'linear-gradient(135deg, #10b981, #059669)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0
          }}>
            {isUser ? (
              <User size={16} color="white" />
            ) : (
              <Bot size={16} color="white" />
            )}
          </div>
        )}

        {/* Message Bubble */}
        <div style={{
          ...getBubbleStyles(),
          padding: '12px 16px',
          position: 'relative'
        }}>
          {/* Error Icon */}
          {error && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '8px'
            }}>
              <AlertCircle size={16} color="#dc2626" />
              <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>
                Error
              </span>
            </div>
          )}

          {/* Message Content */}
          <div style={{ lineHeight: '1.5' }}>
            {isStreaming && !message.content ? (
              <TypingIndicator />
            ) : (
              <>
                {message.content}
                {isStreaming && (
                  <span style={{
                    display: 'inline-block',
                    width: '2px',
                    height: '1em',
                    backgroundColor: 'currentColor',
                    marginLeft: '2px',
                    animation: 'cursor-blink 1s infinite'
                  }} />
                )}
              </>
            )}
          </div>

          {/* Success Indicator for completed messages */}
          {!isStreaming && !error && isAssistant && (
            <div style={{
              position: 'absolute',
              bottom: '4px',
              right: '8px',
              opacity: 0.6
            }}>
              <CheckCircle size={12} color="#10b981" />
            </div>
          )}

          <style>
            {`
              @keyframes cursor-blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0; }
              }
            `}
          </style>
        </div>
      </div>

      {/* Timestamp and Metadata */}
      {showTimestamp && (message.timestamp || message.metadata) && (
        <div style={{
          fontSize: '0.75rem',
          color: '#6b7280',
          marginTop: '4px',
          textAlign: isUser ? 'right' : 'left',
          paddingLeft: showAvatar && !isUser ? '44px' : '0',
          paddingRight: showAvatar && isUser ? '44px' : '0'
        }}>
          {showTimestamp && message.timestamp && formatTimestamp(message.timestamp)}
          {message.metadata?.model_used && (
            <span style={{ marginLeft: '8px', opacity: 0.7 }}>
              • {message.metadata.model_used}
            </span>
          )}
          {message.metadata?.tokens_used && (
            <span style={{ marginLeft: '4px', opacity: 0.7 }}>
              • {message.metadata.tokens_used} tokens
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default MessageBubble;