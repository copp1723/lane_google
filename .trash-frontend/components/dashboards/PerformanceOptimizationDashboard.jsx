/*
Performance Optimization Dashboard Component
Real-time campaign performance monitoring and optimization interface
*/

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '../ui/tabs';
import {
  TrendingUp,
  TrendingDown,
  Target,
  Zap,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  Lightbulb,
  Settings,
  RefreshCw
} from 'lucide-react';
import EnvironmentConfig from '../../config/environment.js';

const API_BASE_URL = EnvironmentConfig.getApiBaseUrl();

const PerformanceOptimizationDashboard = ({ customerId }) => {
  const [performanceData, setPerformanceData] = useState({});
  const [recommendations, setRecommendations] = useState([]);
  const [optimizationSummary, setOptimizationSummary] = useState({});
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [autoOptimizationEnabled, setAutoOptimizationEnabled] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Load optimization summary on component mount
  useEffect(() => {
    if (customerId) {
      loadOptimizationSummary();
      const interval = setInterval(loadOptimizationSummary, 5 * 60 * 1000); // Refresh every 5 minutes
      return () => clearInterval(interval);
    }
  }, [customerId]);

  const loadOptimizationSummary = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/performance/summary/${customerId}`);
      if (response.ok) {
        const data = await response.json();
        setOptimizationSummary(data.data || {});
        setLastUpdated(new Date());
      }
    } catch (error) {
      console.error('Failed to load optimization summary:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadCampaignPerformance = async (campaignId) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/performance/analyze/${customerId}/${campaignId}`);
      if (response.ok) {
        const data = await response.json();
        setPerformanceData(data.data || {});
        setSelectedCampaign(campaignId);
      }
    } catch (error) {
      console.error('Failed to load campaign performance:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadRecommendations = async (campaignId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/performance/recommendations/${customerId}/${campaignId}`);
      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.data?.recommendations || []);
      }
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    }
  };

  const applyOptimization = async (recommendation) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/performance/optimize/${customerId}/${recommendation.campaign_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(recommendation),
      });

      if (response.ok) {
        // Reload data after optimization
        await loadCampaignPerformance(recommendation.campaign_id);
        await loadRecommendations(recommendation.campaign_id);
        await loadOptimizationSummary();
      }
    } catch (error) {
      console.error('Failed to apply optimization:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleAutoOptimization = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/performance/auto-optimize/${customerId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled: !autoOptimizationEnabled }),
      });

      if (response.ok) {
        setAutoOptimizationEnabled(!autoOptimizationEnabled);
      }
    } catch (error) {
      console.error('Failed to toggle auto-optimization:', error);
    }
  };

  const getPerformanceStatusColor = (status) => {
    const colors = {
      excellent: 'bg-green-100 text-green-800',
      good: 'bg-blue-100 text-blue-800',
      average: 'bg-yellow-100 text-yellow-800',
      poor: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getPerformanceIcon = (status) => {
    switch (status) {
      case 'excellent':
      case 'good':
        return <TrendingUp className="h-4 w-4" />;
      case 'poor':
      case 'critical':
        return <TrendingDown className="h-4 w-4" />;
      default:
        return <Target className="h-4 w-4" />;
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    };
    return colors[priority] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Performance Optimization</h2>
          <p className="text-gray-600">AI-powered campaign performance monitoring and optimization</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            {lastUpdated && `Last updated: ${lastUpdated.toLocaleTimeString()}`}
          </div>
          <Button
            onClick={loadOptimizationSummary}
            disabled={isLoading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button
            onClick={toggleAutoOptimization}
            variant={autoOptimizationEnabled ? "default" : "outline"}
            size="sm"
          >
            <Zap className="h-4 w-4 mr-2" />
            Auto-Optimize {autoOptimizationEnabled ? 'ON' : 'OFF'}
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Campaigns</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{optimizationSummary.total_campaigns || 0}</div>
            <p className="text-xs text-muted-foreground">
              Across all accounts
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Optimization Score</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {optimizationSummary.average_optimization_score?.toFixed(1) || '0.0'}/100
            </div>
            <p className="text-xs text-muted-foreground">
              Average across campaigns
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Opportunities</CardTitle>
            <Lightbulb className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{optimizationSummary.optimization_opportunities || 0}</div>
            <p className="text-xs text-muted-foreground">
              Campaigns needing optimization
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Auto-Optimization</CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              <Badge variant={autoOptimizationEnabled ? "default" : "secondary"}>
                {autoOptimizationEnabled ? 'ENABLED' : 'DISABLED'}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              4-hour optimization cycle
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Performance Distribution */}
      {optimizationSummary.performance_distribution && (
        <Card>
          <CardHeader>
            <CardTitle>Performance Distribution</CardTitle>
            <CardDescription>Campaign performance status breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-5">
              {Object.entries(optimizationSummary.performance_distribution).map(([status, count]) => (
                <div key={status} className="text-center">
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getPerformanceStatusColor(status)}`}>
                    {getPerformanceIcon(status)}
                    <span className="ml-1 capitalize">{status}</span>
                  </div>
                  <div className="text-2xl font-bold mt-2">{count}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Campaign Details */}
      <Tabs defaultValue="campaigns" className="space-y-6">
        <TabsList>
          <TabsTrigger value="campaigns">Campaign Performance</TabsTrigger>
          <TabsTrigger value="recommendations">Optimization Recommendations</TabsTrigger>
          <TabsTrigger value="trends">Performance Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="campaigns" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Campaign Performance Analysis</CardTitle>
              <CardDescription>
                Select a campaign to view detailed performance metrics and optimization opportunities
              </CardDescription>
            </CardHeader>
            <CardContent>
              {optimizationSummary.campaign_details && optimizationSummary.campaign_details.length > 0 ? (
                <div className="grid gap-4">
                  {optimizationSummary.campaign_details.map((campaign) => (
                    <div
                      key={campaign.campaign_id}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedCampaign === campaign.campaign_id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => {
                        loadCampaignPerformance(campaign.campaign_id);
                        loadRecommendations(campaign.campaign_id);
                      }}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold">{campaign.name}</h3>
                          <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                            <span>CTR: {(campaign.key_metrics?.ctr * 100)?.toFixed(2)}%</span>
                            <span>ROAS: {campaign.key_metrics?.roas?.toFixed(2)}x</span>
                            <span>QS: {campaign.key_metrics?.quality_score?.toFixed(1)}/10</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getPerformanceStatusColor(campaign.performance_status)}>
                            {campaign.performance_status}
                          </Badge>
                          <div className="text-right">
                            <div className="text-sm font-medium">{campaign.optimization_score?.toFixed(1)}/100</div>
                            <div className="text-xs text-gray-500">Optimization Score</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No campaign data available</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Selected Campaign Details */}
          {performanceData.campaign_id && (
            <Card>
              <CardHeader>
                <CardTitle>Campaign Performance Metrics</CardTitle>
                <CardDescription>
                  Detailed performance analysis for selected campaign
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                  <div className="space-y-2">
                    <div className="text-sm text-gray-600">Click-Through Rate</div>
                    <div className="text-2xl font-bold">{(performanceData.ctr * 100)?.toFixed(3)}%</div>
                    <div className="text-xs text-gray-500">
                      {performanceData.clicks?.toLocaleString()} clicks / {performanceData.impressions?.toLocaleString()} impressions
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-sm text-gray-600">Return on Ad Spend</div>
                    <div className="text-2xl font-bold">{performanceData.roas?.toFixed(2)}x</div>
                    <div className="text-xs text-gray-500">
                      ${performanceData.revenue?.toFixed(2)} revenue / ${performanceData.cost?.toFixed(2)} cost
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-sm text-gray-600">Quality Score</div>
                    <div className="text-2xl font-bold">{performanceData.quality_score?.toFixed(1)}/10</div>
                    <div className="text-xs text-gray-500">
                      Impression Share: {(performanceData.impression_share * 100)?.toFixed(1)}%
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-sm text-gray-600">Cost Per Acquisition</div>
                    <div className="text-2xl font-bold">${performanceData.cpa?.toFixed(2)}</div>
                    <div className="text-xs text-gray-500">
                      {performanceData.conversions?.toFixed(1)} conversions
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>AI-Powered Optimization Recommendations</CardTitle>
              <CardDescription>
                Intelligent recommendations to improve campaign performance
              </CardDescription>
            </CardHeader>
            <CardContent>
              {recommendations.length > 0 ? (
                <div className="space-y-4">
                  {recommendations.map((rec, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center space-x-2">
                          <Badge className={getPriorityColor(rec.priority)}>
                            {rec.priority} priority
                          </Badge>
                          <Badge variant="outline">
                            {rec.action.replace('_', ' ')}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-500">
                          Confidence: {(rec.confidence_score * 100)?.toFixed(0)}%
                        </div>
                      </div>
                      
                      <h4 className="font-semibold mb-2">{rec.description}</h4>
                      <p className="text-sm text-gray-600 mb-3">{rec.expected_impact}</p>
                      
                      <div className="flex justify-between items-center">
                        <div className="text-xs text-gray-500">
                          Created: {new Date(rec.created_at).toLocaleString()}
                        </div>
                        <Button
                          onClick={() => applyOptimization(rec)}
                          disabled={isLoading}
                          size="sm"
                          variant={rec.priority === 'high' ? 'default' : 'outline'}
                        >
                          <Zap className="h-4 w-4 mr-2" />
                          Apply Optimization
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Lightbulb className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Select a campaign to view optimization recommendations</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Performance Trends</CardTitle>
              <CardDescription>
                Historical performance data and trend analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Performance trend charts will be displayed here</p>
                <p className="text-sm">Select a campaign to view historical data</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PerformanceOptimizationDashboard;