import React, { useState, useEffect } from 'react'
import { Send, MessageCircle } from 'lucide-react'

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your AI assistant for Google Ads management. How can I help you today?',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')

  const sendMessage = () => {
    if (input.trim()) {
      const newMessage = {
        id: messages.length + 1,
        type: 'user',
        content: input,
        timestamp: new Date()
      }
      
      setMessages([...messages, newMessage])
      setInput('')
      
      // Simulate AI response
      setTimeout(() => {
        const aiResponse = {
          id: messages.length + 2,
          type: 'assistant',
          content: 'I understand you want to ' + input + '. Let me help you with that. This feature connects to the AI service from yesterday\'s backend implementation.',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, aiResponse])
      }, 1000)
    }
  }

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
        gap: '12px'
      }}>
        <MessageCircle size={24} style={{ color: '#6366f1' }} />
        <h2 style={{ color: '#111827', fontSize: '1.25rem', fontWeight: '700', margin: 0 }}>
          AI Assistant
        </h2>
        <div style={{
          background: 'rgba(16, 185, 129, 0.2)',
          borderRadius: '12px',
          padding: '4px 8px',
          color: '#10b981',
          fontSize: '0.75rem',
          fontWeight: '600',
          marginLeft: 'auto'
        }}>
          Online
        </div>
      </div>

      {/* Messages */}
      <div style={{ 
        flex: 1, 
        padding: '1rem 2rem',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem'
      }}>
        {messages.map((message) => (
          <div
            key={message.id}
            style={{
              alignSelf: message.type === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%'
            }}
          >
            <div style={{
              background: message.type === 'user' 
                ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
                : 'rgba(255, 255, 255, 0.9)',
              color: message.type === 'user' ? 'white' : '#1f2937',
              padding: '12px 16px',
              borderRadius: message.type === 'user' 
                ? '20px 20px 5px 20px'
                : '20px 20px 20px 5px',
              backdropFilter: 'blur(10px)',
              border: message.type === 'assistant' ? '1px solid rgba(255, 255, 255, 0.5)' : 'none'
            }}>
              {message.content}
            </div>
            <div style={{
              fontSize: '0.75rem',
              color: '#6b7280',
              marginTop: '4px',
              textAlign: message.type === 'user' ? 'right' : 'left'
            }}>
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div style={{ 
        padding: '1rem 2rem',
        borderTop: '1px solid rgba(255, 255, 255, 0.2)',
        display: 'flex',
        gap: '12px'
      }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about campaigns, keywords, optimization..."
          style={{
            flex: 1,
            padding: '12px 16px',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            borderRadius: '12px',
            background: 'rgba(255, 255, 255, 0.5)',
            backdropFilter: 'blur(10px)',
            outline: 'none',
            fontSize: '0.875rem'
          }}
        />
        <button
          onClick={sendMessage}
          style={{
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
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
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}

export default ChatInterface
