/*
Real-time Monitoring Dashboard Component
Comprehensive monitoring, alerting, and issue detection interface
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
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  EyeOff,
  Play,
  Pause,
  RefreshCw,
  Shield,
  Zap,
  Bell,
  Settings,
  Activity,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Info,
  X
} from 'lucide-react';
import { LEGACY_ENDPOINTS } from '../../config/api';

const RealTimeMonitoringDashboard = ({ customerId }) => {
  const [monitoringStatus, setMonitoringStatus] = useState({});
  const [activeIssues, setActiveIssues] = useState([]);
  const [dashboardData, setDashboardData] = useState({});
  const [monitoringRules, setMonitoringRules] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [monitoringEnabled, setMonitoringEnabled] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Load monitoring data on component mount
  useEffect(() => {
    if (customerId) {
      loadMonitoringData();
      const interval = setInterval(loadMonitoringData, 30 * 1000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [customerId]);

  const loadMonitoringData = async () => {
    try {
      setIsLoading(true);
      
      // Load all monitoring data in parallel
      const [statusResponse, issuesResponse, dashboardResponse, rulesResponse] = await Promise.all([
        fetch(LEGACY_ENDPOINTS.MONITORING.STATUS(customerId)),
        fetch(LEGACY_ENDPOINTS.MONITORING.ISSUES(customerId)),
        fetch(LEGACY_ENDPOINTS.MONITORING.DASHBOARD(customerId)),
        fetch(LEGACY_ENDPOINTS.MONITORING.RULES)
      ]);

      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setMonitoringStatus(statusData.data || {});
        setMonitoringEnabled(statusData.data?.monitoring_enabled || false);
      }

      if (issuesResponse.ok) {
        const issuesData = await issuesResponse.json();
        setActiveIssues(issuesData.data?.active_issues || []);
      }

      if (dashboardResponse.ok) {
        const dashboardResponseData = await dashboardResponse.json();
        setDashboardData(dashboardResponseData.data || {});
      }

      if (rulesResponse.ok) {
        const rulesData = await rulesResponse.json();
        setMonitoringRules(rulesData.data?.monitoring_rules || []);
      }

      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to load monitoring data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMonitoring = async () => {
    try {
      setIsLoading(true);
      
      const endpoint = monitoringEnabled 
        ? LEGACY_ENDPOINTS.MONITORING.STOP
        : LEGACY_ENDPOINTS.MONITORING.START(customerId);
      
      const response = await fetch(endpoint, { method: 'POST' });
      
      if (response.ok) {
        setMonitoringEnabled(!monitoringEnabled);
        await loadMonitoringData();
      }
    } catch (error) {
      console.error('Failed to toggle monitoring:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const resolveIssue = async (issueId, resolutionNotes = '') => {
    try {
      setIsLoading(true);
      const response = await fetch(LEGACY_ENDPOINTS.MONITORING.RESOLVE_ISSUE(issueId), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ resolution_notes: resolutionNotes }),
      });

      if (response.ok) {
        await loadMonitoringData();
      }
    } catch (error) {
      console.error('Failed to resolve issue:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const ignoreIssue = async (issueId, reason = '') => {
    try {
      setIsLoading(true);
      const response = await fetch(LEGACY_ENDPOINTS.MONITORING.IGNORE_ISSUE(issueId), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason }),
      });

      if (response.ok) {
        await loadMonitoringData();
      }
    } catch (error) {
      console.error('Failed to ignore issue:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleRule = async (ruleId) => {
    try {
      const response = await fetch(LEGACY_ENDPOINTS.MONITORING.TOGGLE_RULE(ruleId), {
        method: 'POST',
      });

      if (response.ok) {
        await loadMonitoringData();
      }
    } catch (error) {
      console.error('Failed to toggle rule:', error);
    }
  };

  const testAlerts = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(LEGACY_ENDPOINTS.MONITORING.TEST_ALERT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customer_id: customerId,
          campaign_id: 'test_campaign_123'
        }),
      });

      if (response.ok) {
        // Show success message or notification
        console.log('Test alerts sent successfully');
      }
    } catch (error) {
      console.error('Failed to test alerts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-blue-100 text-blue-800',
      info: 'bg-gray-100 text-gray-800'
    };
    return colors[severity] || 'bg-gray-100 text-gray-800';
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <AlertTriangle className="h-4 w-4" />;
      case 'high':
        return <AlertCircle className="h-4 w-4" />;
      case 'medium':
        return <Clock className="h-4 w-4" />;
      case 'low':
        return <Info className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getHealthScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    if (score >= 50) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Real-time Monitoring</h2>
          <p className="text-gray-600">Comprehensive campaign monitoring, alerting, and issue detection</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            {lastUpdated && `Last updated: ${lastUpdated.toLocaleTimeString()}`}
          </div>
          <Button
            onClick={loadMonitoringData}
            disabled={isLoading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button
            onClick={toggleMonitoring}
            disabled={isLoading}
            variant={monitoringEnabled ? "default" : "outline"}
            size="sm"
          >
            {monitoringEnabled ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
            {monitoringEnabled ? 'Stop' : 'Start'} Monitoring
          </Button>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monitoring Status</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              <Badge variant={monitoringEnabled ? "default" : "secondary"}>
                {monitoringEnabled ? 'ACTIVE' : 'INACTIVE'}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              {monitoringStatus.campaigns_monitored || 0} campaigns monitored
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Health Score</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getHealthScoreColor(monitoringStatus.monitoring_health_score || 0)}`}>
              {(monitoringStatus.monitoring_health_score || 0).toFixed(1)}/100
            </div>
            <p className="text-xs text-muted-foreground">
              Overall system health
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Issues</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{monitoringStatus.active_issues || 0}</div>
            <p className="text-xs text-muted-foreground">
              {monitoringStatus.critical_issues || 0} critical issues
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resolution Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(monitoringStatus.avg_resolution_time_minutes || 0).toFixed(0)}m
            </div>
            <p className="text-xs text-muted-foreground">
              Average resolution time
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Issue Distribution */}
      {dashboardData.issues_by_severity && Object.keys(dashboardData.issues_by_severity).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Issue Distribution</CardTitle>
            <CardDescription>Current issues breakdown by severity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-5">
              {Object.entries(dashboardData.issues_by_severity).map(([severity, count]) => (
                <div key={severity} className="text-center">
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(severity)}`}>
                    {getSeverityIcon(severity)}
                    <span className="ml-1 capitalize">{severity}</span>
                  </div>
                  <div className="text-2xl font-bold mt-2">{count}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="issues" className="space-y-6">
        <TabsList>
          <TabsTrigger value="issues">Active Issues</TabsTrigger>
          <TabsTrigger value="rules">Monitoring Rules</TabsTrigger>
          <TabsTrigger value="trends">Issue Trends</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="issues" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Active Issues</CardTitle>
              <CardDescription>
                Real-time issues detected across your campaigns
              </CardDescription>
            </CardHeader>
            <CardContent>
              {activeIssues.length > 0 ? (
                <div className="space-y-4">
                  {activeIssues.map((issue) => (
                    <div key={issue.issue_id} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center space-x-2">
                          <Badge className={getSeverityColor(issue.severity)}>
                            {getSeverityIcon(issue.severity)}
                            <span className="ml-1">{issue.severity}</span>
                          </Badge>
                          <Badge variant="outline">
                            {issue.issue_type.replace('_', ' ')}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-500">
                          {new Date(issue.detected_at).toLocaleString()}
                        </div>
                      </div>
                      
                      <h4 className="font-semibold mb-2">{issue.title}</h4>
                      <p className="text-sm text-gray-600 mb-3">{issue.description}</p>
                      
                      {/* Issue Metrics */}
                      <div className="grid gap-2 md:grid-cols-3 mb-3 text-sm">
                        <div>
                          <span className="font-medium">Campaign:</span> {issue.campaign_id}
                        </div>
                        <div>
                          <span className="font-medium">Confidence:</span> {(issue.confidence_score * 100).toFixed(0)}%
                        </div>
                        <div>
                          <span className="font-medium">Impact:</span> {issue.impact_assessment}
                        </div>
                      </div>
                      
                      {/* Recommended Actions */}
                      {issue.recommended_actions && issue.recommended_actions.length > 0 && (
                        <div className="mb-3">
                          <div className="text-sm font-medium mb-1">Recommended Actions:</div>
                          <ul className="text-sm text-gray-600 list-disc list-inside">
                            {issue.recommended_actions.slice(0, 3).map((action, index) => (
                              <li key={index}>{action}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      <div className="flex justify-between items-center">
                        <div className="text-xs text-gray-500">
                          {issue.auto_resolution_attempted && (
                            <span className="inline-flex items-center">
                              <Zap className="h-3 w-3 mr-1" />
                              Auto-resolution attempted
                            </span>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            onClick={() => ignoreIssue(issue.issue_id, 'Manually ignored from dashboard')}
                            disabled={isLoading}
                            size="sm"
                            variant="outline"
                          >
                            <EyeOff className="h-4 w-4 mr-2" />
                            Ignore
                          </Button>
                          <Button
                            onClick={() => resolveIssue(issue.issue_id, 'Manually resolved from dashboard')}
                            disabled={isLoading}
                            size="sm"
                            variant={issue.severity === 'critical' ? 'default' : 'outline'}
                          >
                            <CheckCircle className="h-4 w-4 mr-2" />
                            Resolve
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-300" />
                  <p>No active issues detected</p>
                  <p className="text-sm">Your campaigns are running smoothly</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rules" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Monitoring Rules</CardTitle>
              <CardDescription>
                Configure monitoring rules and thresholds
              </CardDescription>
            </CardHeader>
            <CardContent>
              {monitoringRules.length > 0 ? (
                <div className="space-y-4">
                  {monitoringRules.map((rule) => (
                    <div key={rule.rule_id} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-semibold">{rule.name}</h4>
                          <p className="text-sm text-gray-600 mb-2">{rule.description}</p>
                          <div className="flex items-center space-x-4 text-sm">
                            <Badge className={getSeverityColor(rule.severity)}>
                              {rule.severity}
                            </Badge>
                            <span>Type: {rule.issue_type.replace('_', ' ')}</span>
                            <span>Auto-resolve: {rule.auto_resolve ? 'Yes' : 'No'}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={rule.enabled ? "default" : "secondary"}>
                            {rule.enabled ? 'Enabled' : 'Disabled'}
                          </Badge>
                          <Button
                            onClick={() => toggleRule(rule.rule_id)}
                            size="sm"
                            variant="outline"
                          >
                            {rule.enabled ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Settings className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No monitoring rules configured</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Issue Trends</CardTitle>
              <CardDescription>
                Historical issue detection and resolution trends
              </CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardData.recent_trends && dashboardData.recent_trends.length > 0 ? (
                <div className="space-y-4">
                  {dashboardData.recent_trends.map((trend, index) => (
                    <div key={index} className="flex justify-between items-center p-3 border rounded">
                      <div className="text-sm font-medium">{trend.date}</div>
                      <div className="flex items-center space-x-4 text-sm">
                        <span className="flex items-center">
                          <TrendingUp className="h-4 w-4 mr-1 text-red-500" />
                          {trend.issues_detected} detected
                        </span>
                        <span className="flex items-center">
                          <TrendingDown className="h-4 w-4 mr-1 text-green-500" />
                          {trend.issues_resolved} resolved
                        </span>
                        <span className="flex items-center">
                          <AlertTriangle className="h-4 w-4 mr-1 text-orange-500" />
                          {trend.critical_issues} critical
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Activity className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No trend data available</p>
                  <p className="text-sm">Historical data will appear here</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Monitoring Settings</CardTitle>
              <CardDescription>
                Configure monitoring behavior and alert preferences
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <div>
                    <h4 className="font-medium">Real-time Monitoring</h4>
                    <p className="text-sm text-gray-600">Enable continuous campaign monitoring</p>
                  </div>
                  <Button
                    onClick={toggleMonitoring}
                    variant={monitoringEnabled ? "default" : "outline"}
                  >
                    {monitoringEnabled ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>
                
                <div className="flex justify-between items-center">
                  <div>
                    <h4 className="font-medium">Test Alerts</h4>
                    <p className="text-sm text-gray-600">Send test alerts to verify configuration</p>
                  </div>
                  <Button
                    onClick={testAlerts}
                    disabled={isLoading}
                    variant="outline"
                  >
                    <Bell className="h-4 w-4 mr-2" />
                    Test Alerts
                  </Button>
                </div>
                
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="p-4 border rounded-lg">
                    <h5 className="font-medium mb-2">Monitoring Interval</h5>
                    <p className="text-sm text-gray-600">5 minutes</p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <h5 className="font-medium mb-2">Issue Retention</h5>
                    <p className="text-sm text-gray-600">30 days</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default RealTimeMonitoringDashboard;