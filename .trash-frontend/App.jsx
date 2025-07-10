import { useState, useEffect } from 'react'
import { Button } from './components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card'
import { Input } from './components/ui/input'
import { Textarea } from './components/ui/textarea'
import { Badge } from './components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs'
import { MessageCircle, Settings, BarChart3, Users, DollarSign, TrendingUp, Activity, Target, Zap, Monitor, Sparkles, Bell, Search, Filter, MoreVertical, ArrowUpRight, ArrowDownRight, Plus, ChevronRight, Bot, Cpu, Gauge, PieChart, BarChart2, Eye, Clock, AlertTriangle, CheckCircle, Loader, Rocket } from 'lucide-react'
import EnvironmentConfig from './config/environment.js';

// Import advanced dashboard components
import AdvancedAnalyticsDashboard from './components/dashboards/AdvancedAnalyticsDashboard'
import BudgetPacingDashboard from './components/dashboards/BudgetPacingDashboard'
import PerformanceOptimizationDashboard from './components/dashboards/PerformanceOptimizationDashboard'
import RealTimeMonitoringDashboard from './components/dashboards/RealTimeMonitoringDashboard'

const API_BASE_URL = EnvironmentConfig.getApiBaseUrl();

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [campaigns, setCampaigns] = useState([])
  const [metrics, setMetrics] = useState({
    impressions: '2.4M',
    clicks: '124K',
    conversions: '3,248',
    spend: '$12,456'
  })

  useEffect(() => {
    fetchCampaigns()
  }, [])

  const fetchCampaigns = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/campaigns`)
      if (response.ok) {
        const data = await response.json()
        setCampaigns(data)
      } else {
        setCampaigns(getDemoCampaigns())
      }
    } catch (error) {
      console.error('Error fetching campaigns:', error)
      setCampaigns(getDemoCampaigns())
    }
  }

  const getDemoCampaigns = () => [
    { id: 1, name: 'Summer Sale Campaign', status: 'active', budget: '$5,000', performance: '+23%' },
    { id: 2, name: 'Product Launch', status: 'paused', budget: '$8,000', performance: '+15%' },
    { id: 3, name: 'Brand Awareness', status: 'active', budget: '$3,500', performance: '+31%' }
  ]

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = { role: 'user', content: inputMessage }
    setMessages([...messages, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputMessage })
      })

      if (response.ok) {
        const data = await response.json()
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
      } else {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: 'I can help you optimize your Google Ads campaigns! Try asking about campaign performance, bid strategies, or keyword suggestions.' 
        }])
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'I can help you optimize your Google Ads campaigns! Try asking about campaign performance, bid strategies, or keyword suggestions.' 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen relative">
      {/* Floating orbs */}
      <div className="floating-orb floating-orb-1"></div>
      <div className="floating-orb floating-orb-2"></div>
      <div className="floating-orb floating-orb-3"></div>

      {/* Header */}
      <header className="glass-header sticky top-0 z-40 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="brand-logo w-12 h-12 flex items-center justify-center relative">
              <Zap className="w-6 h-6 text-white" />
              <div className="status-pulse absolute -top-1 -right-1 w-4 h-4 border-2 border-white rounded-full"></div>
            </div>
            <h1 className="gradient-text text-3xl font-bold tracking-tight">Lane MCP</h1>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">3</span>
            </Button>
            <Button variant="ghost" size="icon">
              <Settings className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="content-layer max-w-7xl mx-auto p-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          {/* Tab Navigation */}
          <TabsList className="glass-tabs grid grid-cols-4 lg:grid-cols-8 gap-2">
            <TabsTrigger value="dashboard" className="data-[state=active]:glass-tab-active rounded-xl transition-all duration-200">
              <Monitor className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="campaigns" className="data-[state=active]:glass-tab-active rounded-xl transition-all duration-200">
              <Target className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Campaigns</span>
            </TabsTrigger>
            <TabsTrigger value="accounts" className="data-[state=active]:glass-tab-active rounded-xl transition-all duration-200">
              <Users className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Accounts</span>
            </TabsTrigger>
            <TabsTrigger value="ai-chat" className="data-[state=active]:glass-tab-active rounded-xl transition-all duration-200">
              <MessageCircle className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">AI Chat</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="data-[state=active]:glass-tab-active rounded-xl transition-all duration-200">
              <BarChart3 className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Analytics</span>
            </TabsTrigger>
            <TabsTrigger value="budget" className="data-[state=active]:glass-tab-active rounded-xl transition-all duration-200">
              <DollarSign className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Budget</span>
            </TabsTrigger>
            <TabsTrigger value="optimization" className="data-[state=active]:glass-tab-active rounded-xl transition-all duration-200">
              <TrendingUp className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Optimize</span>
            </TabsTrigger>
            <TabsTrigger value="monitoring" className="data-[state=active]:glass-tab-active rounded-xl transition-all duration-200">
              <Activity className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Monitor</span>
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {[
                { icon: Eye, label: 'Impressions', value: metrics.impressions, trend: '+12%', color: 'blue' },
                { icon: BarChart2, label: 'Clicks', value: metrics.clicks, trend: '+8%', color: 'purple' },
                { icon: Target, label: 'Conversions', value: metrics.conversions, trend: '+23%', color: 'green' },
                { icon: DollarSign, label: 'Spend', value: metrics.spend, trend: '-5%', color: 'orange' }
              ].map((metric, index) => (
                <Card key={index} className="glass-card">
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium text-gray-700">{metric.label}</CardTitle>
                    <metric.icon className="w-5 h-5 text-gray-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-gray-900">{metric.value}</div>
                    <p className={`text-xs mt-2 flex items-center font-medium ${
                      metric.trend.startsWith('+') ? 'text-green-700' : 'text-red-700'
                    }`}>
                      {metric.trend.startsWith('+') ? 
                        <ArrowUpRight className="w-3 h-3 mr-1" /> : 
                        <ArrowDownRight className="w-3 h-3 mr-1" />
                      }
                      {metric.trend} from last period
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between text-gray-900">
                    Recent Campaigns
                    <Button variant="ghost" size="sm" className="text-gray-600">
                      <Plus className="w-4 h-4" />
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {campaigns.slice(0, 3).map((campaign) => (
                      <div key={campaign.id} className="flex items-center justify-between p-4 rounded-lg bg-white/50 hover:bg-white/70 transition-colors">
                        <div>
                          <p className="font-medium text-gray-900">{campaign.name}</p>
                          <p className="text-sm text-gray-600">Budget: {campaign.budget}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={campaign.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                            {campaign.status}
                          </Badge>
                          <span className="text-sm font-medium text-green-600">{campaign.performance}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center text-gray-900">
                    <Cpu className="w-5 h-5 mr-2 text-purple-600" />
                    AI Insights
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="p-4 rounded-lg bg-blue-50/80">
                      <p className="text-sm font-medium text-blue-900">🎯 Campaign Optimization</p>
                      <p className="text-sm text-blue-700 mt-1">Your "Summer Sale" campaign could improve CTR by 15% with bid adjustments.</p>
                    </div>
                    <div className="p-4 rounded-lg bg-purple-50/80">
                      <p className="text-sm font-medium text-purple-900">💡 Keyword Suggestion</p>
                      <p className="text-sm text-purple-700 mt-1">Add "discount summer deals" to capture 2.3K more searches/month.</p>
                    </div>
                    <div className="p-4 rounded-lg bg-green-50/80">
                      <p className="text-sm font-medium text-green-900">📈 Performance Alert</p>
                      <p className="text-sm text-green-700 mt-1">Conversion rate up 23% this week. Great job!</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Campaigns Tab */}
          <TabsContent value="campaigns" className="animate-fade-in">
            <Card className="glass-card">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-gray-900">Campaign Management</CardTitle>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Filter className="w-4 h-4 mr-2" />
                      Filter
                    </Button>
                    <Button size="sm" className="gradient-button">
                      <Plus className="w-4 h-4 mr-2" />
                      New Campaign
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {getDemoCampaigns().map((campaign) => (
                    <div key={campaign.id} className="glass-card p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="font-semibold text-lg text-gray-900">{campaign.name}</h3>
                          <p className="text-sm text-gray-600">Created 2 weeks ago</p>
                        </div>
                        <div className="flex items-center gap-4">
                          <Badge className={campaign.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                            {campaign.status}
                          </Badge>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="grid grid-cols-4 gap-4">
                        <div>
                          <p className="text-sm text-gray-600">Budget</p>
                          <p className="font-semibold text-gray-900">{campaign.budget}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Impressions</p>
                          <p className="font-semibold text-gray-900">245K</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Clicks</p>
                          <p className="font-semibold text-gray-900">12.3K</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Performance</p>
                          <p className="font-semibold text-green-600">{campaign.performance}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Accounts Tab */}
          <TabsContent value="accounts" className="animate-fade-in">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-gray-900">Connected Accounts</CardTitle>
                <CardDescription className="text-gray-700">Manage your Google Ads accounts</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { name: 'Main Business Account', id: '123-456-7890', status: 'Active', spend: '$45,678' },
                    { name: 'E-commerce Store', id: '234-567-8901', status: 'Active', spend: '$23,456' },
                    { name: 'Local Services', id: '345-678-9012', status: 'Paused', spend: '$12,345' }
                  ].map((account, index) => (
                    <div key={index} className="glass-card p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold text-gray-900">{account.name}</h3>
                          <p className="text-sm text-gray-600">ID: {account.id}</p>
                        </div>
                        <div className="text-right">
                          <Badge className={account.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                            {account.status}
                          </Badge>
                          <p className="text-sm text-gray-600 mt-2">Monthly spend: {account.spend}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <Button className="w-full mt-6 gradient-button">
                  <Plus className="w-4 h-4 mr-2" />
                  Connect New Account
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* AI Chat Tab */}
          <TabsContent value="ai-chat" className="animate-fade-in">
            <Card className="chat-container">
              <CardHeader className="chat-header">
                <CardTitle className="flex items-center text-white">
                  <Bot className="w-6 h-6 mr-2" />
                  AI Campaign Assistant
                </CardTitle>
                <CardDescription className="text-blue-100">
                  Ask me anything about your Google Ads campaigns
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div className="h-96 overflow-y-auto p-6 bg-white/10">
                  {messages.length === 0 ? (
                    <div className="text-center py-12">
                      <Bot className="w-16 h-16 mx-auto text-gray-600 mb-4" />
                      <p className="text-gray-700 mb-6">Hi! I'm your AI assistant. How can I help optimize your campaigns today?</p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                        {[
                          'How can I improve my CTR?',
                          'Suggest keywords for my campaign',
                          'Analyze my campaign performance',
                          'Help me set up conversion tracking'
                        ].map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => setInputMessage(suggestion)}
                            className="glass-card p-3 text-left hover:bg-white/30 transition-all"
                          >
                            <p className="text-sm font-medium text-gray-900">{suggestion}</p>
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {messages.map((message, index) => (
                        <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <div className={`max-w-sm p-4 ${
                            message.role === 'user' ? 'message-user' : 'message-assistant'
                          }`}>
                            {message.content}
                          </div>
                        </div>
                      ))}
                      {isLoading && (
                        <div className="flex justify-start">
                          <div className="message-assistant p-4">
                            <div className="typing-dots">
                              <div className="typing-dot"></div>
                              <div className="typing-dot"></div>
                              <div className="typing-dot"></div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                <div className="p-4 border-t bg-white/20">
                  <div className="flex space-x-2">
                    <Input
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      placeholder="Ask about campaigns, keywords, optimization..."
                      className="flex-1 bg-white/50 border-white/30"
                      disabled={isLoading}
                    />
                    <Button onClick={handleSendMessage} disabled={isLoading} className="gradient-button">
                      {isLoading ? <Loader className="w-4 h-4 animate-spin" /> : <MessageCircle className="w-4 h-4" />}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="animate-fade-in">
            <AdvancedAnalyticsDashboard />
          </TabsContent>

          {/* Budget Tab */}
          <TabsContent value="budget" className="animate-fade-in">
            <BudgetPacingDashboard />
          </TabsContent>

          {/* Optimization Tab */}
          <TabsContent value="optimization" className="animate-fade-in">
            <PerformanceOptimizationDashboard />
          </TabsContent>

          {/* Monitoring Tab */}
          <TabsContent value="monitoring" className="animate-fade-in">
            <RealTimeMonitoringDashboard />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App
