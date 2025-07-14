/*
Budget Pacing Dashboard Component
Real-time budget monitoring and pacing controls for campaigns
*/

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Pause, 
  Play,
  Settings,
  DollarSign,
  Clock,
  Target
} from 'lucide-react';

const BudgetPacingDashboard = ({ customerId }) => {
  const [budgetData, setBudgetData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch budget data
  const fetchBudgetData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/budget-pacing/summary/${customerId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch budget data');
      }

      const data = await response.json();
      setBudgetData(data.data);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh every 2 minutes
  useEffect(() => {
    fetchBudgetData();
    const interval = setInterval(fetchBudgetData, 2 * 60 * 1000);
    return () => clearInterval(interval);
  }, [customerId]);

  // Get status color and icon
  const getStatusDisplay = (status) => {
    const statusConfig = {
      'on_track': {
        color: 'bg-green-100 text-green-800',
        icon: <CheckCircle className="w-4 h-4" />,
        label: 'On Track'
      },
      'under_pacing': {
        color: 'bg-blue-100 text-blue-800',
        icon: <TrendingDown className="w-4 h-4" />,
        label: 'Under Pacing'
      },
      'over_pacing': {
        color: 'bg-yellow-100 text-yellow-800',
        icon: <TrendingUp className="w-4 h-4" />,
        label: 'Over Pacing'
      },
      'critical_overspend': {
        color: 'bg-red-100 text-red-800',
        icon: <AlertTriangle className="w-4 h-4" />,
        label: 'Critical'
      }
    };

    return statusConfig[status] || statusConfig['on_track'];
  };

  // Pause campaign
  const pauseCampaign = async (campaignId) => {
    try {
      const response = await fetch('/api/budget-pacing/pause-campaign', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          customer_id: customerId,
          campaign_id: campaignId,
          reason: 'Manual pause from dashboard'
        })
      });

      if (response.ok) {
        fetchBudgetData(); // Refresh data
      }
    } catch (err) {
      console.error('Error pausing campaign:', err);
    }
  };

  // Resume campaign
  const resumeCampaign = async (campaignId) => {
    try {
      const response = await fetch('/api/budget-pacing/resume-campaign', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          customer_id: customerId,
          campaign_id: campaignId
        })
      });

      if (response.ok) {
        fetchBudgetData(); // Refresh data
      }
    } catch (err) {
      console.error('Error resuming campaign:', err);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Error loading budget data: {error}
        </AlertDescription>
      </Alert>
    );
  }

  if (!budgetData) {
    return (
      <Alert>
        <AlertDescription>
          No budget data available for this account.
        </AlertDescription>
      </Alert>
    );
  }

  const { summary, status_distribution, campaign_metrics } = budgetData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Budget Pacing Dashboard</h2>
          <p className="text-gray-600">
            Real-time budget monitoring and automated pacing controls
          </p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Clock className="w-4 h-4" />
          <span>
            Last updated: {lastUpdated?.toLocaleTimeString()}
          </span>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchBudgetData}
            className="ml-2"
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Budget</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${summary.total_daily_budget?.toFixed(2) || '0.00'}
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Current Spend</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${summary.total_current_spend?.toFixed(2) || '0.00'}
                </p>
              </div>
              <Target className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Budget Used</p>
                <p className="text-2xl font-bold text-gray-900">
                  {summary.budget_utilization?.toFixed(1) || '0.0'}%
                </p>
              </div>
              <div className="w-8 h-8 flex items-center justify-center">
                <Progress 
                  value={summary.budget_utilization || 0} 
                  className="w-8 h-2"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Health Score</p>
                <p className="text-2xl font-bold text-gray-900">
                  {summary.health_score?.toFixed(0) || '0'}/100
                </p>
              </div>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                summary.health_score >= 80 ? 'bg-green-100' :
                summary.health_score >= 60 ? 'bg-yellow-100' : 'bg-red-100'
              }`}>
                {summary.health_score >= 80 ? 
                  <CheckCircle className="w-5 h-5 text-green-600" /> :
                  <AlertTriangle className="w-5 h-5 text-yellow-600" />
                }
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Status Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Campaign Status Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(status_distribution || {}).map(([status, count]) => {
              const statusDisplay = getStatusDisplay(status);
              return (
                <div key={status} className="text-center">
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusDisplay.color}`}>
                    {statusDisplay.icon}
                    <span className="ml-1">{statusDisplay.label}</span>
                  </div>
                  <p className="text-2xl font-bold text-gray-900 mt-2">{count}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Campaign Details */}
      <Card>
        <CardHeader>
          <CardTitle>Campaign Budget Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {campaign_metrics?.map((campaign) => {
              const statusDisplay = getStatusDisplay(campaign.status);
              
              return (
                <div key={campaign.campaign_id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <h4 className="font-medium text-gray-900">
                        Campaign {campaign.campaign_id}
                      </h4>
                      <Badge className={statusDisplay.color}>
                        {statusDisplay.icon}
                        <span className="ml-1">{statusDisplay.label}</span>
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => pauseCampaign(campaign.campaign_id)}
                      >
                        <Pause className="w-4 h-4 mr-1" />
                        Pause
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => resumeCampaign(campaign.campaign_id)}
                      >
                        <Play className="w-4 h-4 mr-1" />
                        Resume
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Daily Budget</p>
                      <p className="font-medium">${campaign.daily_budget?.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Current Spend</p>
                      <p className="font-medium">${campaign.current_spend?.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Projected Spend</p>
                      <p className="font-medium">${campaign.projected_daily_spend?.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Pacing Ratio</p>
                      <p className="font-medium">{campaign.pacing_ratio?.toFixed(2)}x</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Hours Remaining</p>
                      <p className="font-medium">{campaign.hours_remaining?.toFixed(1)}h</p>
                    </div>
                  </div>

                  {/* Budget Progress Bar */}
                  <div className="mt-3">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Budget Usage</span>
                      <span>{campaign.spend_percentage?.toFixed(1)}%</span>
                    </div>
                    <Progress 
                      value={campaign.spend_percentage || 0}
                      className={`h-2 ${
                        campaign.spend_percentage >= 95 ? 'bg-red-100' :
                        campaign.spend_percentage >= 80 ? 'bg-yellow-100' : 'bg-green-100'
                      }`}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default BudgetPacingDashboard;