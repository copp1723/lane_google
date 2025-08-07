import React, { useState, useEffect } from 'react'
import { 
  TrendingUp, DollarSign, Target, Users, 
  BarChart3, Activity, Eye, Clock,
  ChevronUp, ChevronDown, RefreshCw,
  AlertCircle, CheckCircle, XCircle,
  Loader2, ArrowUpRight, ArrowDownRight
} from 'lucide-react'
import apiClient from '../../services/api'
import { useAuth } from '../../contexts/AuthContext'
import BudgetPacingWidget from '../BudgetPacingWidget'

// Metric Card Component
const MetricCard = ({ icon: Icon, label, value, change, format = 'number', loading }) => {
  const isPositive = change > 0;
  const changeColor = isPositive ? 'text-green-600' : 'text-red-600';
  const changeIcon = isPositive ? <ChevronUp size={16} /> : <ChevronDown size={16} />;
  
  const formatValue = (val) => {
    if (loading) return '---';
    if (!val && val !== 0) return '---';
    
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        }).format(val);
      case 'percent':
        return `${val.toFixed(2)}%`;
      case 'number':
        if (val >= 1000000) return `${(val / 1000000).toFixed(1)}M`;
        if (val >= 1000) return `${(val / 1000).toFixed(1)}K`;
        return val.toFixed(0);
      default:
        return val;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="p-2 bg-blue-50 rounded-lg">
          <Icon className="text-blue-600" size={24} />
        </div>
        {change !== undefined && change !== 0 && (
          <div className={`flex items-center gap-1 text-sm ${changeColor}`}>
            {changeIcon}
            <span>{Math.abs(change).toFixed(1)}%</span>
          </div>
        )}
      </div>
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <p className="text-2xl font-bold text-gray-900">{formatValue(value)}</p>
    </div>
  );
};

// Campaign Performance Table Component
const CampaignTable = ({ campaigns, loading }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin text-gray-400" size={32} />
      </div>
    );
  }

  if (!campaigns || campaigns.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <BarChart3 className="mx-auto mb-4 text-gray-300" size={48} />
        <p>No campaigns found</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Campaign</th>
            <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Status</th>
            <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">Impressions</th>
            <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">Clicks</th>
            <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">CTR</th>
            <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">Conversions</th>
            <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">Cost</th>
            <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">ROAS</th>
          </tr>
        </thead>
        <tbody>
          {campaigns.map((campaign) => (
            <tr key={campaign.id} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-3 px-4">
                <div>
                  <p className="font-medium text-gray-900">{campaign.name}</p>
                  <p className="text-sm text-gray-500">{campaign.advertising_channel_type}</p>
                </div>
              </td>
              <td className="py-3 px-4">
                <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                  campaign.status === 'ENABLED' 
                    ? 'bg-green-100 text-green-700' 
                    : campaign.status === 'PAUSED'
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {campaign.status === 'ENABLED' && <CheckCircle size={12} />}
                  {campaign.status === 'PAUSED' && <AlertCircle size={12} />}
                  {campaign.status}
                </span>
              </td>
              <td className="py-3 px-4 text-right">
                {campaign.metrics?.impressions?.toLocaleString() || '0'}
              </td>
              <td className="py-3 px-4 text-right">
                {campaign.metrics?.clicks?.toLocaleString() || '0'}
              </td>
              <td className="py-3 px-4 text-right">
                {campaign.metrics?.clicks && campaign.metrics?.impressions
                  ? `${((campaign.metrics.clicks / campaign.metrics.impressions) * 100).toFixed(2)}%`
                  : '0%'}
              </td>
              <td className="py-3 px-4 text-right">
                {campaign.metrics?.conversions?.toLocaleString() || '0'}
              </td>
              <td className="py-3 px-4 text-right">
                ${((campaign.metrics?.cost_micros || 0) / 1000000).toFixed(2)}
              </td>
              <td className="py-3 px-4 text-right">
                <span className={`font-medium ${
                  (campaign.metrics?.conversions || 0) > 0 ? 'text-green-600' : 'text-gray-500'
                }`}>
                  {campaign.metrics?.conversions > 0 
                    ? `${((campaign.metrics.conversions * 50) / (campaign.metrics.cost_micros / 1000000)).toFixed(2)}x`
                    : '---'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const DashboardView = ({ viewMode }) => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [refreshing, setRefreshing] = useState(false);
  
  // Dashboard data state
  const [dashboardData, setDashboardData] = useState({
    overview: null,
    campaigns: [],
    insights: [],
    trends: null
  });

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Fetch multiple APIs in parallel
      const [analyticsResponse, campaignsResponse] = await Promise.all([
        apiClient.analytics.getDashboard(),
        apiClient.campaigns.list()
      ]);

      setDashboardData({
        overview: analyticsResponse.data?.overview || {},
        campaigns: campaignsResponse.data?.campaigns || [],
        insights: analyticsResponse.data?.insights || [],
        trends: analyticsResponse.data?.trends || {}
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Set some default data on error
      setDashboardData({
        overview: {
          impressions: 0,
          clicks: 0,
          ctr: 0,
          cost: 0,
          conversions: 0,
          cpa: 0,
          roas: 0
        },
        campaigns: [],
        insights: [],
        trends: {}
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Refresh data
  const refreshData = async () => {
    setRefreshing(true);
    await fetchDashboardData();
    setRefreshing(false);
  };

  // Fetch data on mount and when period changes
  useEffect(() => {
    fetchDashboardData();
  }, [selectedPeriod]);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  const { overview } = dashboardData;

  return (
    <div className="dashboard-view">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Welcome back, {user?.first_name || 'User'}! Here's your campaign overview.
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* Period Selector */}
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="1d">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
            
            {/* Refresh Button */}
            <button
              onClick={refreshData}
              disabled={refreshing}
              className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`${refreshing ? 'animate-spin' : ''}`} size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          icon={Eye}
          label="Impressions"
          value={overview?.impressions}
          change={12.5}
          loading={isLoading}
        />
        <MetricCard
          icon={Target}
          label="Clicks"
          value={overview?.clicks}
          change={8.3}
          loading={isLoading}
        />
        <MetricCard
          icon={DollarSign}
          label="Total Spend"
          value={overview?.cost}
          change={-5.2}
          format="currency"
          loading={isLoading}
        />
        <MetricCard
          icon={TrendingUp}
          label="ROAS"
          value={overview?.roas}
          change={15.7}
          format="decimal"
          loading={isLoading}
        />
      </div>

      {/* Secondary Metrics */}
      {viewMode !== 'simple' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            icon={Activity}
            label="CTR"
            value={overview?.ctr}
            change={3.2}
            format="percent"
            loading={isLoading}
          />
          <MetricCard
            icon={Users}
            label="Conversions"
            value={overview?.conversions}
            change={22.4}
            loading={isLoading}
          />
          <MetricCard
            icon={DollarSign}
            label="CPA"
            value={overview?.cpa}
            change={-8.9}
            format="currency"
            loading={isLoading}
          />
          <MetricCard
            icon={BarChart3}
            label="Conv. Rate"
            value={(overview?.conversions / overview?.clicks * 100) || 0}
            change={5.6}
            format="percent"
            loading={isLoading}
          />
        </div>
      )}

      {/* Insights & Alerts */}
      {dashboardData.insights.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">AI Insights & Recommendations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {dashboardData.insights.map((insight, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border ${
                  insight.type === 'opportunity'
                    ? 'bg-blue-50 border-blue-200'
                    : 'bg-amber-50 border-amber-200'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${
                    insight.type === 'opportunity' ? 'bg-blue-100' : 'bg-amber-100'
                  }`}>
                    {insight.type === 'opportunity' ? (
                      <ArrowUpRight className="text-blue-600" size={20} />
                    ) : (
                      <AlertCircle className="text-amber-600" size={20} />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 mb-1">{insight.title}</h3>
                    <p className="text-sm text-gray-600">{insight.description}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs">
                      <span className={`font-medium ${
                        insight.impact === 'high' ? 'text-red-600' : 
                        insight.impact === 'medium' ? 'text-amber-600' : 
                        'text-green-600'
                      }`}>
                        {insight.impact.toUpperCase()} IMPACT
                      </span>
                      <span className="text-gray-500">
                        {(insight.confidence * 100).toFixed(0)}% confidence
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Two Column Layout for Tables and Budget */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Campaign Performance Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold">Campaign Performance</h2>
          </div>
          <div className="p-6">
            <CampaignTable 
              campaigns={dashboardData.campaigns} 
              loading={isLoading}
            />
          </div>
        </div>

        {/* Budget Pacing Widget */}
        <BudgetPacingWidget />
      </div>

      {/* Quick Actions */}
      {viewMode === 'expert' && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2">
            <BarChart3 size={20} />
            Generate Performance Report
          </button>
          <button className="p-4 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
            <Target size={20} />
            Optimize Campaigns
          </button>
          <button className="p-4 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
            <Clock size={20} />
            Schedule Review
          </button>
        </div>
      )}
    </div>
  );
};

export default DashboardView;