import React, { useState, useEffect } from 'react'
import { 
  Plus, Search, Filter, MoreVertical, 
  Play, Pause, Trash2, Edit, Copy,
  TrendingUp, AlertTriangle, CheckCircle,
  Calendar, DollarSign, Target, BarChart3,
  Loader2, X, ChevronRight, Info,
  Settings, Zap, Users, Globe
} from 'lucide-react'
import apiClient from '../../services/api'
import { useAuth } from '../../contexts/AuthContext'

// Campaign Card Component
const CampaignCard = ({ campaign, onEdit, onStatusChange, onViewDetails }) => {
  const [menuOpen, setMenuOpen] = useState(false)
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'ENABLED': return 'bg-green-100 text-green-700'
      case 'PAUSED': return 'bg-yellow-100 text-yellow-700'
      case 'REMOVED': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }
  
  const getPerformanceColor = (roas) => {
    if (roas >= 4) return 'text-green-600'
    if (roas >= 2) return 'text-yellow-600'
    return 'text-red-600'
  }
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-semibold text-lg text-gray-900">{campaign.name}</h3>
            <p className="text-sm text-gray-500 mt-1">{campaign.advertising_channel_type}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(campaign.status)}`}>
              {campaign.status}
            </span>
            <div className="relative">
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <MoreVertical size={16} />
              </button>
              {menuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                  <button
                    onClick={() => {
                      onEdit(campaign)
                      setMenuOpen(false)
                    }}
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center gap-2"
                  >
                    <Edit size={16} />
                    Edit Campaign
                  </button>
                  <button
                    onClick={() => {
                      onStatusChange(campaign.id, campaign.status === 'ENABLED' ? 'PAUSED' : 'ENABLED')
                      setMenuOpen(false)
                    }}
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center gap-2"
                  >
                    {campaign.status === 'ENABLED' ? <Pause size={16} /> : <Play size={16} />}
                    {campaign.status === 'ENABLED' ? 'Pause' : 'Resume'}
                  </button>
                  <button
                    onClick={() => {
                      onViewDetails(campaign)
                      setMenuOpen(false)
                    }}
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center gap-2"
                  >
                    <BarChart3 size={16} />
                    View Details
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <p className="text-xs text-gray-500">Impressions</p>
            <p className="text-lg font-semibold">{(campaign.metrics?.impressions || 0).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Clicks</p>
            <p className="text-lg font-semibold">{(campaign.metrics?.clicks || 0).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">CTR</p>
            <p className="text-lg font-semibold">
              {campaign.metrics?.clicks && campaign.metrics?.impressions
                ? `${((campaign.metrics.clicks / campaign.metrics.impressions) * 100).toFixed(2)}%`
                : '0%'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Conversions</p>
            <p className="text-lg font-semibold">{(campaign.metrics?.conversions || 0).toLocaleString()}</p>
          </div>
        </div>
        
        {/* Budget and Performance */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <DollarSign size={16} className="text-gray-400" />
              <span className="text-sm text-gray-600">
                ${((campaign.metrics?.cost_micros || 0) / 1000000).toFixed(2)} / 
                ${(campaign.budget_amount_micros / 1000000).toFixed(0)}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <TrendingUp size={16} className="text-gray-400" />
              <span className={`text-sm font-medium ${getPerformanceColor(3.5)}`}>
                ROAS: {campaign.metrics?.conversions > 0 
                  ? `${((campaign.metrics.conversions * 50) / (campaign.metrics.cost_micros / 1000000)).toFixed(1)}x`
                  : 'N/A'}
              </span>
            </div>
          </div>
          <button
            onClick={() => onViewDetails(campaign)}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1"
          >
            View Details
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}

// Campaign Creation Modal
const CampaignCreationModal = ({ isOpen, onClose, onSubmit }) => {
  const [step, setStep] = useState(1)
  const [campaignData, setCampaignData] = useState({
    name: '',
    type: 'SEARCH',
    budget: '',
    targetLocation: '',
    targetAudience: '',
    keywords: '',
    startDate: '',
    endDate: ''
  })
  
  if (!isOpen) return null
  
  const handleSubmit = (e) => {
    e.preventDefault()
    if (step < 3) {
      setStep(step + 1)
    } else {
      onSubmit(campaignData)
    }
  }
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Create New Campaign</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <X size={20} />
            </button>
          </div>
          
          {/* Progress Indicator */}
          <div className="flex items-center gap-4 mt-6">
            <div className={`flex items-center gap-2 ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                step >= 1 ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
              }`}>
                1
              </div>
              <span className="text-sm font-medium">Basic Info</span>
            </div>
            <div className="flex-1 h-0.5 bg-gray-200">
              <div className={`h-full bg-blue-600 transition-all ${step >= 2 ? 'w-full' : 'w-0'}`} />
            </div>
            <div className={`flex items-center gap-2 ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                step >= 2 ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
              }`}>
                2
              </div>
              <span className="text-sm font-medium">Targeting</span>
            </div>
            <div className="flex-1 h-0.5 bg-gray-200">
              <div className={`h-full bg-blue-600 transition-all ${step >= 3 ? 'w-full' : 'w-0'}`} />
            </div>
            <div className={`flex items-center gap-2 ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                step >= 3 ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
              }`}>
                3
              </div>
              <span className="text-sm font-medium">Review</span>
            </div>
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto max-h-[60vh]">
          {/* Step 1: Basic Info */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Campaign Name
                </label>
                <input
                  type="text"
                  value={campaignData.name}
                  onChange={(e) => setCampaignData({...campaignData, name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Summer Sale 2024"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Campaign Type
                </label>
                <select
                  value={campaignData.type}
                  onChange={(e) => setCampaignData({...campaignData, type: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="SEARCH">Search</option>
                  <option value="DISPLAY">Display</option>
                  <option value="VIDEO">Video</option>
                  <option value="SHOPPING">Shopping</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Daily Budget
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-2.5 text-gray-400" size={20} />
                  <input
                    type="number"
                    value={campaignData.budget}
                    onChange={(e) => setCampaignData({...campaignData, budget: e.target.value})}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="0.00"
                    min="1"
                    step="0.01"
                    required
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={campaignData.startDate}
                    onChange={(e) => setCampaignData({...campaignData, startDate: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    End Date (Optional)
                  </label>
                  <input
                    type="date"
                    value={campaignData.endDate}
                    onChange={(e) => setCampaignData({...campaignData, endDate: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          )}
          
          {/* Step 2: Targeting */}
          {step === 2 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Location
                </label>
                <div className="relative">
                  <Globe className="absolute left-3 top-2.5 text-gray-400" size={20} />
                  <input
                    type="text"
                    value={campaignData.targetLocation}
                    onChange={(e) => setCampaignData({...campaignData, targetLocation: e.target.value})}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., United States, New York"
                    required
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Audience
                </label>
                <div className="relative">
                  <Users className="absolute left-3 top-2.5 text-gray-400" size={20} />
                  <input
                    type="text"
                    value={campaignData.targetAudience}
                    onChange={(e) => setCampaignData({...campaignData, targetAudience: e.target.value})}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 18-35, interested in fitness"
                    required
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Keywords (for Search campaigns)
                </label>
                <textarea
                  value={campaignData.keywords}
                  onChange={(e) => setCampaignData({...campaignData, keywords: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows="4"
                  placeholder="Enter keywords separated by commas"
                />
              </div>
            </div>
          )}
          
          {/* Step 3: Review */}
          {step === 3 && (
            <div className="space-y-6">
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="font-medium mb-4">Campaign Summary</h3>
                <dl className="space-y-3">
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Name:</dt>
                    <dd className="text-sm font-medium">{campaignData.name}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Type:</dt>
                    <dd className="text-sm font-medium">{campaignData.type}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Daily Budget:</dt>
                    <dd className="text-sm font-medium">${campaignData.budget}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Location:</dt>
                    <dd className="text-sm font-medium">{campaignData.targetLocation}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Audience:</dt>
                    <dd className="text-sm font-medium">{campaignData.targetAudience}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-600">Duration:</dt>
                    <dd className="text-sm font-medium">
                      {campaignData.startDate} - {campaignData.endDate || 'Ongoing'}
                    </dd>
                  </div>
                </dl>
              </div>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <Info className="text-blue-600 mt-0.5" size={20} />
                  <div>
                    <p className="text-sm text-blue-800">
                      Your campaign will be created and enter review status. You'll receive a notification once it's approved and live.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Form Actions */}
          <div className="flex items-center justify-between mt-8">
            <button
              type="button"
              onClick={step > 1 ? () => setStep(step - 1) : onClose}
              className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              {step > 1 ? 'Back' : 'Cancel'}
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {step < 3 ? 'Next' : 'Create Campaign'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

const CampaignsView = ({ viewMode }) => {
  const { user } = useAuth()
  const [campaigns, setCampaigns] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [selectedCampaigns, setSelectedCampaigns] = useState([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [error, setError] = useState(null)

  // Fetch campaigns
  const fetchCampaigns = async () => {
    try {
      setIsLoading(true)
      const response = await apiClient.campaigns.list()
      setCampaigns(response.data?.campaigns || [])
    } catch (err) {
      console.error('Error fetching campaigns:', err)
      setError('Failed to load campaigns')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchCampaigns()
  }, [])

  // Filter campaigns
  const filteredCampaigns = campaigns.filter(campaign => {
    const matchesSearch = campaign.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = filterStatus === 'all' || campaign.status === filterStatus
    return matchesSearch && matchesStatus
  })

  // Handle campaign status change
  const handleStatusChange = async (campaignId, newStatus) => {
    try {
      await apiClient.campaigns.updateStatus(campaignId, newStatus)
      await fetchCampaigns()
    } catch (err) {
      console.error('Error updating campaign status:', err)
      setError('Failed to update campaign status')
    }
  }

  // Handle campaign creation
  const handleCreateCampaign = async (campaignData) => {
    try {
      await apiClient.campaigns.create(campaignData)
      setShowCreateModal(false)
      await fetchCampaigns()
    } catch (err) {
      console.error('Error creating campaign:', err)
      setError('Failed to create campaign')
    }
  }

  return (
    <div className="campaigns-view">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Campaigns</h1>
            <p className="text-gray-600 mt-1">
              Manage and monitor your Google Ads campaigns
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Plus size={20} />
            Create Campaign
          </button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search campaigns..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Status</option>
            <option value="ENABLED">Active</option>
            <option value="PAUSED">Paused</option>
            <option value="REMOVED">Removed</option>
          </select>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertTriangle className="text-red-500 mt-0.5" size={20} />
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

      {/* Campaigns Grid/List */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="animate-spin text-gray-400" size={48} />
        </div>
      ) : filteredCampaigns.length === 0 ? (
        <div className="text-center py-12">
          <Zap className="mx-auto mb-4 text-gray-300" size={48} />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns found</h3>
          <p className="text-gray-500 mb-4">
            {searchQuery || filterStatus !== 'all' 
              ? 'Try adjusting your filters'
              : 'Get started by creating your first campaign'}
          </p>
          {!searchQuery && filterStatus === 'all' && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
            >
              <Plus size={20} />
              Create Campaign
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredCampaigns.map(campaign => (
            <CampaignCard
              key={campaign.id}
              campaign={campaign}
              onEdit={(c) => console.log('Edit:', c)}
              onStatusChange={handleStatusChange}
              onViewDetails={(c) => console.log('View details:', c)}
            />
          ))}
        </div>
      )}

      {/* Campaign Creation Modal */}
      <CampaignCreationModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateCampaign}
      />
    </div>
  )
}

export default CampaignsView