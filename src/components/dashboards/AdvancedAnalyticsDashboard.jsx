/*
Advanced Analytics Dashboard Component
Comprehensive analytics, reporting, and business intelligence interface
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  Eye,
  Download,
  RefreshCw,
  Calendar,
  BarChart3,
  PieChart as PieChartIcon,
  FileText,
  Lightbulb,
  Award,
  AlertCircle,
  CheckCircle,
  Activity,
  Zap
} from 'lucide-react';
import EnvironmentConfig from '../config/environment.js';

const API_BASE_URL = EnvironmentConfig.getApiBaseUrl();

const AdvancedAnalyticsDashboard = ({ customerId }) => {
  const [dashboardData, setDashboardData] = useState({});
  const [insights, setInsights] = useState([]);
  const [benchmarks, setBenchmarks] = useState({});
  const [reportTemplates, setReportTemplates] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState('last_30_days');
  const [selectedMetric, setSelectedMetric] = useState('revenue');
  const [lastUpdated, setLastUpdated] = useState(null);

  // Chart colors
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  // Load analytics data on component mount
  useEffect(() => {
    if (customerId) {
      loadAnalyticsData();
      const interval = setInterval(loadAnalyticsData, 5 * 60 * 1000); // Refresh every 5 minutes
      return () => clearInterval(interval);
    }
  }, [customerId, selectedTimeRange]);

  const loadAnalyticsData = async () => {
    try {
      setIsLoading(true);
      
      // Load all analytics data in parallel
      const [dashboardResponse, insightsResponse, benchmarksResponse, templatesResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/api/analytics/dashboard/${customerId}`),
        fetch(`${API_BASE_URL}/api/analytics/insights/${customerId}?time_range=${selectedTimeRange}`),
        fetch(`${API_BASE_URL}/api/analytics/benchmarks`),
        fetch(`${API_BASE_URL}/api/analytics/reports/templates`)
      ]);

      if (dashboardResponse.ok) {
        const dashboardData = await dashboardResponse.json();
        setDashboardData(dashboardData.data || {});
      }

      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setInsights(insightsData.data || {});
      }

      if (benchmarksResponse.ok) {
        const benchmarksData = await benchmarksResponse.json();
        setBenchmarks(benchmarksData.data || {});
      }

      if (templatesResponse.ok) {
        const templatesData = await templatesResponse.json();
        setReportTemplates(templatesData.data || {});
      }

      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateReport = async (reportType, format = 'pdf') => {
    try {
      setIsLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/api/analytics/reports/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customer_id: customerId,
          report_type: reportType,
          time_range: selectedTimeRange,
          format: format,
          include_charts: true,
          include_recommendations: true,
          created_by: 'dashboard_user'
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Report generated:', result);
        // In a real implementation, you would handle file download here
      }
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getPerformanceColor = (value, benchmark, isHigherBetter = true) => {
    if (!benchmark) return 'text-gray-600';
    
    const ratio = value / benchmark;
    if (isHigherBetter) {
      if (ratio >= 1.2) return 'text-green-600';
      if (ratio >= 1.0) return 'text-blue-600';
      if (ratio >= 0.8) return 'text-yellow-600';
      return 'text-red-600';
    } else {
      if (ratio <= 0.8) return 'text-green-600';
      if (ratio <= 1.0) return 'text-blue-600';
      if (ratio <= 1.2) return 'text-yellow-600';
      return 'text-red-600';
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }).format(value);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  // Prepare chart data
  const dailyPerformanceData = dashboardData.daily_performance || [];
  const topCampaignsData = (dashboardData.top_campaigns || []).map(campaign => ({
    name: campaign.campaign_id.substring(0, 10) + '...',
    roas: campaign.roas,
    cost: campaign.cost,
    revenue: campaign.revenue
  }));

  const performanceSummary = dashboardData.performance_summary || {};
  const budgetSummary = dashboardData.budget_summary || {};
  const optimizationSummary = dashboardData.optimization_summary || {};
  const monitoringSummary = dashboardData.monitoring_summary || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Advanced Analytics</h2>
          <p className="text-gray-600">Comprehensive analytics, reporting, and business intelligence</p>
        </div>
        <div className="flex items-center space-x-4">
          <Select value={selectedTimeRange} onValueChange={setSelectedTimeRange}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Time Range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="last_7_days">Last 7 Days</SelectItem>
              <SelectItem value="last_30_days">Last 30 Days</SelectItem>
              <SelectItem value="last_90_days">Last 90 Days</SelectItem>
              <SelectItem value="last_year">Last Year</SelectItem>
            </SelectContent>
          </Select>
          <div className="text-sm text-gray-500">
            {lastUpdated && `Updated: ${lastUpdated.toLocaleTimeString()}`}
          </div>
          <Button
            onClick={loadAnalyticsData}
            disabled={isLoading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Key Performance Metrics */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(performanceSummary.revenue || 0)}</div>
            <p className="text-xs text-muted-foreground">
              Profit: {formatCurrency(performanceSummary.profit || 0)} ({formatPercentage(performanceSummary.profit_margin || 0)})
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">ROAS</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getPerformanceColor(performanceSummary.roas || 0, benchmarks.industry_averages?.roas)}`}>
              {(performanceSummary.roas || 0).toFixed(2)}x
            </div>
            <p className="text-xs text-muted-foreground">
              Industry avg: {(benchmarks.industry_averages?.roas || 0).toFixed(2)}x
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CTR</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getPerformanceColor(performanceSummary.ctr || 0, benchmarks.industry_averages?.ctr)}`}>
              {formatPercentage(performanceSummary.ctr || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Industry avg: {formatPercentage(benchmarks.industry_averages?.ctr || 0)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Budget Utilization</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatPercentage(budgetSummary.budget_utilization || 0)}</div>
            <p className="text-xs text-muted-foreground">
              Daily avg: {formatCurrency(budgetSummary.daily_avg_spend || 0)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
          <TabsTrigger value="benchmarks">Benchmarks</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Performance Charts */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Daily Performance Trend</CardTitle>
                <CardDescription>Revenue and cost trends over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={dailyPerformanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(value, name) => [formatCurrency(value), name]} />
                    <Legend />
                    <Line type="monotone" dataKey="revenue" stroke="#8884d8" strokeWidth={2} />
                    <Line type="monotone" dataKey="cost" stroke="#82ca9d" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Campaigns by ROAS</CardTitle>
                <CardDescription>Best performing campaigns</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={topCampaignsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value, name) => [name === 'roas' ? `${value.toFixed(2)}x` : formatCurrency(value), name]} />
                    <Legend />
                    <Bar dataKey="roas" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Summary Cards */}
          <div className="grid gap-6 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Optimization Summary</CardTitle>
                <CardDescription>Automated optimization performance</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Total Optimizations</span>
                    <span className="text-lg font-bold">{optimizationSummary.total_optimizations || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Success Rate</span>
                    <span className="text-lg font-bold text-green-600">
                      {formatPercentage(optimizationSummary.success_rate || 0)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Cost Savings</span>
                    <span className="text-lg font-bold text-blue-600">
                      {formatCurrency(optimizationSummary.cost_savings || 0)}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Monitoring Summary</CardTitle>
                <CardDescription>Issue detection and resolution</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Total Issues</span>
                    <span className="text-lg font-bold">{monitoringSummary.total_issues || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Auto-Resolved</span>
                    <span className="text-lg font-bold text-green-600">
                      {monitoringSummary.auto_resolved || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Avg Resolution</span>
                    <span className="text-lg font-bold">
                      {(monitoringSummary.avg_resolution_time || 0).toFixed(0)}m
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Performance Trends</CardTitle>
                <CardDescription>Recent performance changes</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboardData.trends && Object.entries(dashboardData.trends).map(([key, value]) => {
                    if (key.includes('_trend') && typeof value === 'number') {
                      const isPositive = value > 0;
                      return (
                        <div key={key} className="flex justify-between items-center">
                          <span className="text-sm font-medium capitalize">
                            {key.replace('_trend', '').replace('_', ' ')}
                          </span>
                          <div className="flex items-center">
                            {isPositive ? (
                              <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                            ) : (
                              <TrendingDown className="h-4 w-4 text-red-600 mr-1" />
                            )}
                            <span className={`text-sm font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                              {value > 0 ? '+' : ''}{value.toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Performance Analysis</CardTitle>
              <CardDescription>Detailed performance metrics and comparisons</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-2">
                <div>
                  <h4 className="font-semibold mb-4">Current Performance</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span>Impressions</span>
                      <span className="font-bold">{formatNumber(performanceSummary.impressions || 0)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Clicks</span>
                      <span className="font-bold">{formatNumber(performanceSummary.clicks || 0)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Conversions</span>
                      <span className="font-bold">{(performanceSummary.conversions || 0).toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Cost</span>
                      <span className="font-bold">{formatCurrency(performanceSummary.cost || 0)}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-4">Industry Comparison</h4>
                  <div className="space-y-3">
                    {benchmarks.industry_averages && Object.entries(benchmarks.industry_averages).map(([metric, benchmark]) => {
                      const currentValue = performanceSummary[metric] || 0;
                      const isHigherBetter = !['cpc', 'cpa'].includes(metric);
                      const performance = currentValue / benchmark;
                      
                      return (
                        <div key={metric} className="flex justify-between items-center">
                          <span className="capitalize">{metric.replace('_', ' ')}</span>
                          <div className="flex items-center">
                            <span className={`font-bold mr-2 ${getPerformanceColor(currentValue, benchmark, isHigherBetter)}`}>
                              {metric.includes('ctr') || metric.includes('share') ? formatPercentage(currentValue) : 
                               metric.includes('score') ? currentValue.toFixed(1) :
                               metric.includes('cost') || metric.includes('cpa') || metric.includes('cpc') ? formatCurrency(currentValue) :
                               currentValue.toFixed(2)}
                            </span>
                            <Badge variant={performance >= 1.1 ? "default" : performance >= 0.9 ? "secondary" : "destructive"}>
                              {performance >= 1.1 ? "Above" : performance >= 0.9 ? "Average" : "Below"}
                            </Badge>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Lightbulb className="h-5 w-5 mr-2" />
                  Key Insights
                </CardTitle>
                <CardDescription>AI-powered analysis of your campaign performance</CardDescription>
              </CardHeader>
              <CardContent>
                {insights.insights && insights.insights.length > 0 ? (
                  <div className="space-y-4">
                    {insights.insights.map((insight, index) => (
                      <div key={index} className="p-3 bg-blue-50 border-l-4 border-blue-400 rounded">
                        <p className="text-sm">{insight}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Lightbulb className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No insights available</p>
                    <p className="text-sm">Insights will appear as data is analyzed</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Target className="h-5 w-5 mr-2" />
                  Recommendations
                </CardTitle>
                <CardDescription>Actionable optimization suggestions</CardDescription>
              </CardHeader>
              <CardContent>
                {insights.recommendations && insights.recommendations.length > 0 ? (
                  <div className="space-y-4">
                    {insights.recommendations.map((recommendation, index) => (
                      <div key={index} className="p-3 bg-green-50 border-l-4 border-green-400 rounded">
                        <p className="text-sm">{recommendation}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Target className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No recommendations available</p>
                    <p className="text-sm">Recommendations will appear based on performance analysis</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="reports" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Report Generation</CardTitle>
              <CardDescription>Generate comprehensive reports in multiple formats</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {Object.entries(reportTemplates).map(([key, template]) => (
                  <div key={key} className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2">{template.name}</h4>
                    <p className="text-sm text-gray-600 mb-4">{template.description}</p>
                    <div className="flex space-x-2">
                      <Button
                        onClick={() => generateReport(key, 'pdf')}
                        disabled={isLoading}
                        size="sm"
                        variant="outline"
                      >
                        <FileText className="h-4 w-4 mr-2" />
                        PDF
                      </Button>
                      <Button
                        onClick={() => generateReport(key, 'excel')}
                        disabled={isLoading}
                        size="sm"
                        variant="outline"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Excel
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="benchmarks" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Industry Benchmarks</CardTitle>
              <CardDescription>Compare your performance against industry standards</CardDescription>
            </CardHeader>
            <CardContent>
              {benchmarks.performance_tiers && (
                <div className="grid gap-6 md:grid-cols-2">
                  <div>
                    <h4 className="font-semibold mb-4">Performance Tiers</h4>
                    <div className="space-y-4">
                      {Object.entries(benchmarks.performance_tiers).map(([tier, metrics]) => (
                        <div key={tier} className="p-3 border rounded">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium capitalize">{tier.replace('_', ' ')}</span>
                            <Badge variant={tier === 'excellent' ? 'default' : tier === 'good' ? 'secondary' : 'outline'}>
                              {tier === 'excellent' ? <Award className="h-3 w-3 mr-1" /> : 
                               tier === 'good' ? <CheckCircle className="h-3 w-3 mr-1" /> :
                               <AlertCircle className="h-3 w-3 mr-1" />}
                              {tier.replace('_', ' ')}
                            </Badge>
                          </div>
                          <div className="text-sm space-y-1">
                            <div>CTR: {formatPercentage(metrics.ctr)}</div>
                            <div>ROAS: {metrics.roas.toFixed(1)}x</div>
                            <div>Quality Score: {metrics.quality_score.toFixed(1)}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-4">Optimization Targets</h4>
                    {benchmarks.optimization_targets && (
                      <div className="space-y-3">
                        {Object.entries(benchmarks.optimization_targets).map(([metric, target]) => (
                          <div key={metric} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span className="text-sm font-medium capitalize">
                              {metric.replace('_', ' ').replace('min ', 'Min ').replace('max ', 'Max ').replace('target ', 'Target ')}
                            </span>
                            <span className="text-sm font-bold">
                              {metric.includes('ctr') || metric.includes('share') ? formatPercentage(target) :
                               metric.includes('score') ? target.toFixed(1) :
                               metric.includes('roas') ? `${target.toFixed(1)}x` :
                               formatCurrency(target)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedAnalyticsDashboard;