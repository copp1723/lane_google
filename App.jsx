import { useState, useEffect } from 'react'
import { Button } from './src/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './src/components/ui/card'
import { Input } from './src/components/ui/input'
import { Textarea } from './src/components/ui/textarea'
import { Badge } from './src/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './src/components/ui/tabs'
import { MessageCircle, Settings, BarChart3, Users, DollarSign, TrendingUp, Activity, Target, Zap, Monitor } from 'lucide-react'
import './App.css'
import EnvironmentConfig from './src/config/environment.js';

// Import advanced dashboard components
import AdvancedAnalyticsDashboard from './src/components/dashboards/AdvancedAnalyticsDashboard'
import BudgetPacingDashboard from './src/components/dashboards/BudgetPacingDashboard'
import PerformanceOptimizationDashboard from './src/components/dashboards/PerformanceOptimizationDashboard'
import RealTimeMonitoringDashboard from './src/components/dashboards/RealTimeMonitoringDashboard'

const API_BASE_URL = EnvironmentConfig.getApiBaseUrl();

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [chatMessage, setChatMessage] = useState('')
  const [conversation, setConversation] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [accounts, setAccounts] = useState([])
  const [campaigns, setCampaigns] = useState([])
  const [selectedAccount, setSelectedAccount] = useState(null)

  // Load accounts on component mount
  useEffect(() => {
    loadAccounts()
    loadCampaigns()
  }, [])

  const loadAccounts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/google-ads/accounts`)
      if (response.ok) {
        const data = await response.json()
        setAccounts(data.accounts || [])
      }
    } catch (error) {
      console.error('Failed to load accounts:', error)
    }
  }

  const loadCampaigns = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/campaigns/list`)
      if (response.ok) {
        const data = await response.json()
        setCampaigns(data.campaigns || [])
      }
    } catch (error) {
      console.error('Failed to load campaigns:', error)
    }
  }

  const sendMessage = async () => {
    if (!chatMessage.trim()) return

    setIsLoading(true)
    const userMessage = { role: 'user', content: chatMessage }
    const newConversation = [...conversation, userMessage]
    setConversation(newConversation)
    setChatMessage('')

    try {
      const response = await fetch(`${API_BASE_URL}/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: chatMessage,
          conversation_history: conversation
        })
      })

      if (response.ok) {
        const data = await response.json()
        const assistantMessage = { role: 'assistant', content: data.response }
        setConversation([...newConversation, assistantMessage])
      } else {
        const error = await response.json()
        console.error('Chat error:', error)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateCampaignBrief = async () => {
    if (conversation.length === 0) return

    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/ai/generate-campaign-brief`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_history: conversation
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Generated brief:', data.brief)
        // You could show this in a modal or new tab
        alert('Campaign brief generated! Check console for details.')
      }
    } catch (error) {
      console.error('Failed to generate brief:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Lane MCP</h1>
              <Badge variant="secondary" className="ml-2">AI-Powered</Badge>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline">
                {accounts.length} Accounts Connected
              </Badge>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-8">
            <TabsTrigger value="chat" className="flex items-center">
              <MessageCircle className="h-4 w-4 mr-2" />
              AI Chat
            </TabsTrigger>
            <TabsTrigger value="campaigns" className="flex items-center">
              <BarChart3 className="h-4 w-4 mr-2" />
              Campaigns
            </TabsTrigger>
            <TabsTrigger value="accounts" className="flex items-center">
              <Users className="h-4 w-4 mr-2" />
              Accounts
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center">
              <TrendingUp className="h-4 w-4 mr-2" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="advanced-analytics" className="flex items-center">
              <Activity className="h-4 w-4 mr-2" />
              Advanced Analytics
            </TabsTrigger>
            <TabsTrigger value="budget-pacing" className="flex items-center">
              <DollarSign className="h-4 w-4 mr-2" />
              Budget Pacing
            </TabsTrigger>
            <TabsTrigger value="performance-optimization" className="flex items-center">
              <Target className="h-4 w-4 mr-2" />
              Performance
            </TabsTrigger>
            <TabsTrigger value="real-time-monitoring" className="flex items-center">
              <Monitor className="h-4 w-4 mr-2" />
              Monitoring
            </TabsTrigger>
          </TabsList>

          {/* AI Chat Tab */}
          <TabsContent value="chat" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>AI Campaign Assistant</CardTitle>
                <CardDescription>
                  Describe your advertising goals in natural language and I'll help you create optimized campaigns.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Conversation Display */}
                <div className="h-96 overflow-y-auto border rounded-lg p-4 bg-gray-50">
                  {conversation.length === 0 ? (
                    <div className="text-center text-gray-500 mt-20">
                      <MessageCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>Start a conversation to create your first campaign</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {conversation.map((message, index) => (
                        <div
                          key={index}
                          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                              message.role === 'user'
                                ? 'bg-blue-500 text-white'
                                : 'bg-white text-gray-900 border'
                            }`}
                          >
                            {message.content}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Message Input */}
                <div className="flex space-x-2">
                  <Textarea
                    placeholder="Describe your campaign goals, target audience, budget, etc..."
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        sendMessage()
                      }
                    }}
                    className="flex-1"
                  />
                  <div className="flex flex-col space-y-2">
                    <Button onClick={sendMessage} disabled={isLoading || !chatMessage.trim()}>
                      {isLoading ? 'Sending...' : 'Send'}
                    </Button>
                    {conversation.length > 0 && (
                      <Button variant="outline" onClick={generateCampaignBrief} disabled={isLoading}>
                        Generate Brief
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Campaigns Tab */}
          <TabsContent value="campaigns" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {campaigns.map((campaign) => (
                <Card key={campaign.id}>
                  <CardHeader>
                    <CardTitle className="text-lg">{campaign.name}</CardTitle>
                    <CardDescription>
                      Customer ID: {campaign.customer_id}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Status:</span>
                        <Badge variant={campaign.status === 'approved' ? 'default' : 'secondary'}>
                          {campaign.status}
                        </Badge>
                      </div>
                      {campaign.google_campaign_id && (
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Google ID:</span>
                          <span className="text-sm font-mono">{campaign.google_campaign_id}</span>
                        </div>
                      )}
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Created:</span>
                        <span className="text-sm">
                          {new Date(campaign.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Accounts Tab */}
          <TabsContent value="accounts" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {accounts.map((account) => (
                <Card key={account.id}>
                  <CardHeader>
                    <CardTitle className="text-lg">{account.name}</CardTitle>
                    <CardDescription>ID: {account.id}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Currency:</span>
                        <span className="text-sm font-semibold">{account.currency}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Timezone:</span>
                        <span className="text-sm">{account.timezone}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Status:</span>
                        <Badge variant={account.status === 'ENABLED' ? 'default' : 'secondary'}>
                          {account.status}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Campaigns</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{campaigns.length}</div>
                  <p className="text-xs text-muted-foreground">
                    Across all accounts
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Accounts</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{accounts.length}</div>
                  <p className="text-xs text-muted-foreground">
                    Connected accounts
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Approved Campaigns</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {campaigns.filter(c => c.status === 'approved').length}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Ready to launch
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Draft Campaigns</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {campaigns.filter(c => c.status === 'draft').length}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Awaiting approval
                  </p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Campaign Performance</CardTitle>
                <CardDescription>
                  Performance analytics will be displayed here once campaigns are active
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>Performance data will appear here</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Advanced Analytics Tab */}
          <TabsContent value="advanced-analytics" className="space-y-6">
            <AdvancedAnalyticsDashboard />
          </TabsContent>

          {/* Budget Pacing Tab */}
          <TabsContent value="budget-pacing" className="space-y-6">
            <BudgetPacingDashboard />
          </TabsContent>

          {/* Performance Optimization Tab */}
          <TabsContent value="performance-optimization" className="space-y-6">
            <PerformanceOptimizationDashboard />
          </TabsContent>

          {/* Real-Time Monitoring Tab */}
          <TabsContent value="real-time-monitoring" className="space-y-6">
            <RealTimeMonitoringDashboard />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App

