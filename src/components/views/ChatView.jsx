import React, { useState, useRef, useEffect } from 'react'
import { 
  Send, MessageCircle, Sparkles, Copy, 
  ThumbsUp, ThumbsDown, RotateCcw, 
  Zap, Target, DollarSign, BarChart3,
  FileText, Download, ChevronDown
} from 'lucide-react'
import { useAIStream } from '../../hooks/useAIStream'

const ChatView = ({ viewMode }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your AI assistant for Google Ads management. I can help you with campaign optimization, keyword research, budget recommendations, and more. What would you like to work on today?',
      timestamp: new Date(),
      suggestions: [
        'Analyze my campaign performance',
        'Suggest keyword optimizations',
        'Review budget allocation',
        'Create a new campaign'
      ]
    }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Use the AI stream hook
  const { stream, isStreaming, response, reset } = useAIStream({
    endpoint: '/api/ai/chat',
    onComplete: (fullResponse) => {
      setMessages(prev => {
        const updatedMessages = [...prev]
        updatedMessages[updatedMessages.length - 1] = {
          ...updatedMessages[updatedMessages.length - 1],
          content: fullResponse,
          isStreaming: false
        }
        return updatedMessages
      })
      setIsTyping(false)
    }
  })

  // Predefined prompts for different tasks
  const taskPrompts = [
    {
      category: 'Campaign Management',
      icon: Zap,
      prompts: [
        'Create a search campaign for [product/service]',
        'Optimize my underperforming campaigns',
        'Pause campaigns with low ROI',
        'Duplicate my best performing campaign'
      ]
    },
    {
      category: 'Keyword Research',
      icon: Target,
      prompts: [
        'Find new keywords for [topic]',
        'Analyze keyword competition',
        'Suggest negative keywords',
        'Expand my keyword list'
      ]
    },
    {
      category: 'Budget & Bidding',
      icon: DollarSign,
      prompts: [
        'Optimize my daily budget allocation',
        'Suggest bid adjustments',
        'Analyze cost per conversion',
        'Set up automated bidding'
      ]
    },
    {
      category: 'Performance Analysis',
      icon: BarChart3,
      prompts: [
        'Show me campaign performance trends',
        'Compare this month vs last month',
        'Identify top converting keywords',
        'Analyze device performance'
      ]
    }
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (input.trim() && !isStreaming) {
      const userMessage = {
        id: messages.length + 1,
        type: 'user',
        content: input,
        timestamp: new Date()
      }
      
      const aiMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true
      }
      
      setMessages([...messages, userMessage, aiMessage])
      setInput('')
      setIsTyping(true)
      
      // Stream the AI response
      await stream(input, {
        systemPrompt: 'You are an expert Google Ads assistant. Provide helpful, actionable advice for managing and optimizing Google Ads campaigns.'
      })
    }
  }

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion)
    inputRef.current?.focus()
  }

  const copyMessage = (content) => {
    navigator.clipboard.writeText(content)
    // You could add a toast notification here
  }

  const regenerateLastResponse = () => {
    const lastUserMessage = [...messages].reverse().find(m => m.type === 'user')
    if (lastUserMessage) {
      setInput(lastUserMessage.content)
      sendMessage()
    }
  }

  return (
    <div className="chat-view">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-content">
          <div className="chat-header-left">
            <MessageCircle size={24} className="chat-icon" />
            <div>
              <h2 className="chat-title">AI Assistant</h2>
              <p className="chat-subtitle">Powered by advanced AI for Google Ads optimization</p>
            </div>
          </div>
          <div className="chat-status">
            <Sparkles size={16} />
            <span>AI Ready</span>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.type}`}
          >
            <div className="message-content">
              {message.isStreaming ? (
                <div className="message-text streaming">
                  {response || 'Thinking...'}
                  <span className="cursor-blink">|</span>
                </div>
              ) : (
                <div className="message-text">
                  {message.content}
                </div>
              )}
              
              {/* Suggestions for assistant messages */}
              {message.suggestions && !message.isStreaming && (
                <div className="message-suggestions">
                  {message.suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      className="suggestion-chip"
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}

              {/* Message actions for non-streaming messages */}
              {!message.isStreaming && viewMode !== 'simple' && (
                <div className="message-actions">
                  <button 
                    className="message-action"
                    onClick={() => copyMessage(message.content)}
                    title="Copy"
                  >
                    <Copy size={14} />
                  </button>
                  {message.type === 'assistant' && (
                    <>
                      <button className="message-action" title="Helpful">
                        <ThumbsUp size={14} />
                      </button>
                      <button className="message-action" title="Not helpful">
                        <ThumbsDown size={14} />
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>
            
            <div className="message-time">
              {message.timestamp.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </div>
          </div>
        ))}
        {isTyping && messages[messages.length - 1]?.isStreaming && (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Task Prompts - Show in Professional and Expert modes */}
      {viewMode !== 'simple' && messages.length === 1 && (
        <div className="task-prompts">
          <h3 className="prompts-title">Quick Actions</h3>
          <div className="prompts-grid">
            {taskPrompts.map((category) => (
              <div key={category.category} className="prompt-category">
                <div className="category-header">
                  <category.icon size={16} />
                  <span>{category.category}</span>
                </div>
                <div className="category-prompts">
                  {category.prompts.map((prompt, index) => (
                    <button
                      key={index}
                      className="prompt-button"
                      onClick={() => handleSuggestionClick(prompt)}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="chat-input-container">
        {viewMode === 'expert' && (
          <div className="chat-tools">
            <button className="tool-button" title="Attach file">
              <FileText size={16} />
            </button>
            <button className="tool-button" title="Export conversation">
              <Download size={16} />
            </button>
            <button 
              className="tool-button" 
              title="Regenerate last response"
              onClick={regenerateLastResponse}
            >
              <RotateCcw size={16} />
            </button>
          </div>
        )}
        
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                sendMessage()
              }
            }}
            placeholder="Ask about campaigns, keywords, optimization strategies..."
            className="chat-input"
            rows="1"
            disabled={isStreaming}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isStreaming}
            className="send-button"
          >
            <Send size={20} />
          </button>
        </div>
        
        <div className="input-hint">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  )
}

export default ChatView