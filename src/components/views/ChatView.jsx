import React, { useState, useRef, useEffect } from 'react'
import { 
  Send, MessageCircle, Sparkles, Copy, 
  ThumbsUp, ThumbsDown, RotateCcw, 
  Zap, Target, DollarSign, BarChart3,
  FileText, Download, ChevronDown,
  Loader2, AlertCircle, CheckCircle,
  ArrowRight, Brain, Lightbulb
} from 'lucide-react'
import apiClient from '../../services/api'
import { useAuth } from '../../contexts/AuthContext'

// Message Component
const Message = ({ message, onActionClick, onFeedback }) => {
  const [copied, setCopied] = useState(false)
  const isUser = message.type === 'user'
  
  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`mb-6 ${isUser ? 'flex justify-end' : ''}`}>
      <div className={`max-w-3xl ${isUser ? 'ml-auto' : ''}`}>
        <div className={`rounded-lg p-4 ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-gray-100 text-gray-900'
        }`}>
          {/* Message Header */}
          <div className="flex items-center gap-2 mb-2">
            <div className={`p-1 rounded ${isUser ? 'bg-blue-700' : 'bg-gray-200'}`}>
              {isUser ? (
                <MessageCircle size={16} className={isUser ? 'text-blue-200' : 'text-gray-600'} />
              ) : (
                <Sparkles size={16} className="text-gray-600" />
              )}
            </div>
            <span className={`text-sm font-medium ${isUser ? 'text-blue-200' : 'text-gray-600'}`}>
              {isUser ? 'You' : 'AI Assistant'}
            </span>
            <span className={`text-xs ${isUser ? 'text-blue-200' : 'text-gray-500'}`}>
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          </div>
          
          {/* Message Content */}
          <div className={`prose ${isUser ? 'prose-invert' : ''} max-w-none`}>
            {message.isStreaming ? (
              <div className="flex items-center gap-2">
                <Loader2 className="animate-spin" size={16} />
                <span className="animate-pulse">{message.content || 'Thinking...'}</span>
              </div>
            ) : (
              <p className="whitespace-pre-wrap">{message.content}</p>
            )}
          </div>
          
          {/* Action Buttons */}
          {!isUser && !message.isStreaming && (
            <div className="flex items-center gap-2 mt-4">
              <button
                onClick={handleCopy}
                className="p-1.5 rounded hover:bg-gray-200 transition-colors"
                title="Copy message"
              >
                {copied ? (
                  <CheckCircle size={16} className="text-green-600" />
                ) : (
                  <Copy size={16} className="text-gray-500" />
                )}
              </button>
              <button
                onClick={() => onFeedback(message.id, 'up')}
                className={`p-1.5 rounded hover:bg-gray-200 transition-colors ${
                  message.feedback === 'up' ? 'bg-green-100' : ''
                }`}
                title="Helpful"
              >
                <ThumbsUp size={16} className={
                  message.feedback === 'up' ? 'text-green-600' : 'text-gray-500'
                } />
              </button>
              <button
                onClick={() => onFeedback(message.id, 'down')}
                className={`p-1.5 rounded hover:bg-gray-200 transition-colors ${
                  message.feedback === 'down' ? 'bg-red-100' : ''
                }`}
                title="Not helpful"
              >
                <ThumbsDown size={16} className={
                  message.feedback === 'down' ? 'text-red-600' : 'text-gray-500'
                } />
              </button>
            </div>
          )}
        </div>
        
        {/* Suggestions */}
        {message.suggestions && message.suggestions.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => onActionClick(suggestion)}
                className="w-full text-left p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-between group"
              >
                <span className="text-sm text-gray-700">{suggestion}</span>
                <ArrowRight className="text-gray-400 group-hover:text-gray-600" size={16} />
              </button>
            ))}
          </div>
        )}
        
        {/* Campaign Brief */}
        {message.campaignBrief && (
          <div className="mt-3 p-4 bg-white border border-gray-200 rounded-lg">
            <h4 className="font-medium mb-2 flex items-center gap-2">
              <FileText size={16} />
              Campaign Brief Generated
            </h4>
            <pre className="text-sm text-gray-600 whitespace-pre-wrap">
              {JSON.stringify(message.campaignBrief, null, 2)}
            </pre>
            <button
              onClick={() => onActionClick('create-campaign', message.campaignBrief)}
              className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Zap size={16} />
              Create Campaign
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

const ChatView = ({ viewMode }) => {
  const { user } = useAuth()
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
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
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const [error, setError] = useState(null)
  
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const abortControllerRef = useRef(null)

  // Predefined prompts for different tasks
  const taskPrompts = [
    {
      category: 'Campaign Management',
      icon: Zap,
      prompts: [
        'Create a new search campaign for my e-commerce store',
        'Optimize my existing campaigns for better performance',
        'Pause underperforming campaigns'
      ]
    },
    {
      category: 'Keyword Research',
      icon: Target,
      prompts: [
        'Find high-intent keywords for my product',
        'Analyze competitor keywords',
        'Suggest negative keywords to add'
      ]
    },
    {
      category: 'Budget & Bidding',
      icon: DollarSign,
      prompts: [
        'Analyze my budget pacing',
        'Recommend optimal bid strategies',
        'Set up budget alerts'
      ]
    },
    {
      category: 'Performance Analysis',
      icon: BarChart3,
      prompts: [
        'Show me campaign performance trends',
        'Identify top performing keywords',
        'Generate a performance report'
      ]
    }
  ]

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Handle sending a message
  const sendMessage = async (content) => {
    if (!content.trim() || isLoading) return
    
    setError(null)
    
    // Add user message
    const userMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: content.trim(),
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    
    // Add assistant message placeholder
    const assistantMessageId = `assistant-${Date.now()}`
    const assistantMessage = {
      id: assistantMessageId,
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    }
    
    setMessages(prev => [...prev, assistantMessage])
    
    try {
      // For streaming responses
      if (viewMode === 'expert') {
        // Use streaming API for expert mode
        const generator = apiClient.ai.streamChat(content, conversationId)
        
        for await (const chunk of generator) {
          if (chunk.type === 'content') {
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessageId
                ? { ...msg, content: msg.content + chunk.content }
                : msg
            ))
          } else if (chunk.type === 'conversation_id') {
            setConversationId(chunk.conversation_id)
          } else if (chunk.type === 'complete') {
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessageId
                ? { ...msg, isStreaming: false }
                : msg
            ))
          }
        }
      } else {
        // Use regular API for simpler modes
        const response = await apiClient.ai.chat(content, conversationId)
        
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessageId
            ? { 
                ...msg, 
                content: response.response,
                isStreaming: false,
                suggestions: response.suggestions,
                campaignBrief: response.campaign_brief
              }
            : msg
        ))
        
        if (response.conversation_id) {
          setConversationId(response.conversation_id)
        }
      }
    } catch (err) {
      console.error('Chat error:', err)
      setError(err.message || 'Failed to send message')
      
      // Remove the assistant message on error
      setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId))
    } finally {
      setIsLoading(false)
    }
  }

  // Handle suggestion click
  const handleSuggestionClick = async (suggestion) => {
    await sendMessage(suggestion)
  }

  // Handle action click
  const handleActionClick = async (action, data) => {
    if (action === 'create-campaign' && data) {
      try {
        const response = await apiClient.ai.createCampaign(conversationId)
        
        const message = {
          id: `system-${Date.now()}`,
          type: 'assistant',
          content: `Campaign creation workflow initiated! Workflow ID: ${response.workflow_id}. You can track the progress in the Campaigns section.`,
          timestamp: new Date()
        }
        
        setMessages(prev => [...prev, message])
      } catch (err) {
        console.error('Campaign creation error:', err)
        setError('Failed to create campaign')
      }
    } else {
      await sendMessage(action)
    }
  }

  // Handle feedback
  const handleFeedback = (messageId, feedback) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId 
        ? { ...msg, feedback: msg.feedback === feedback ? null : feedback }
        : msg
    ))
  }

  // Handle form submit
  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage(input)
  }

  return (
    <div className="chat-view h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Brain className="text-blue-600" />
              AI Assistant
            </h1>
            <p className="text-gray-600 mt-1">
              Ask questions, get insights, and manage campaigns with natural language
            </p>
          </div>
          {conversationId && (
            <div className="text-sm text-gray-500">
              Conversation ID: {conversationId.slice(0, 8)}...
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      {messages.length === 1 && viewMode !== 'simple' && (
        <div className="p-6 border-b border-gray-200">
          <h3 className="font-medium mb-4 flex items-center gap-2">
            <Lightbulb className="text-yellow-500" size={20} />
            Quick Actions
          </h3>
          <div className="space-y-4">
            {taskPrompts.map((category) => (
              <div key={category.category}>
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <category.icon size={16} />
                  {category.category}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                  {category.prompts.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSuggestionClick(prompt)}
                      className="text-left p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-sm"
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

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="text-red-500 mt-0.5" size={20} />
            <div>
              <p className="text-sm text-red-700">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-sm text-red-600 underline mt-1"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}
        
        {messages.map((message) => (
          <Message
            key={message.id}
            message={message}
            onActionClick={handleActionClick}
            onFeedback={handleFeedback}
          />
        ))}
        
        {isLoading && messages[messages.length - 1]?.type !== 'assistant' && (
          <div className="flex items-center gap-2 text-gray-500 mb-4">
            <Loader2 className="animate-spin" size={16} />
            <span>AI is thinking...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything about your Google Ads campaigns..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="animate-spin" size={20} />
            ) : (
              <Send size={20} />
            )}
            Send
          </button>
        </form>
        
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}

export default ChatView