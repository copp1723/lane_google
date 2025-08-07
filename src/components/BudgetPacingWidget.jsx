import React, { useState, useEffect } from 'react'
import {
  DollarSign, TrendingUp, AlertTriangle, Clock,
  Calendar, ArrowUp, ArrowDown, Info, Loader2
} from 'lucide-react'
import apiClient from '../services/api'

const BudgetPacingWidget = ({ campaignId = null, customerId = 'demo-customer' }) => {
  const [budgetData, setBudgetData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedPeriod, setSelectedPeriod] = useState('today')
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchBudgetData()
  }, [campaignId, customerId, selectedPeriod])

  const fetchBudgetData = async () => {
    try {
      setLoading(true)
      const response = await apiClient.budget.getSummary(customerId)
      setBudgetData(response.data)
    } catch (err) {
      console.error('Error fetching budget data:', err)
      setError('Failed to load budget data')
      // Set mock data on error
      setBudgetData({
        totalBudget: 10000,
        totalSpent: 7234.56,
        projectedSpend: 9876.54,
        remainingBudget: 2765.44,
        daysRemaining: 15,
        pacingStatus: 'on_track',
        campaigns: [
          {
            id: 'camp_001',
            name: 'Summer Sale 2024',
            budget: 5000,
            spent: 3456.78,
            projectedSpend: 4987.65,
            pacingStatus: 'slightly_over'
          },
          {
            id: 'camp_002',
            name: 'Brand Awareness',
            budget: 3000,
            spent: 2345.67,
            projectedSpend: 2876.54,
            pacingStatus: 'on_track'
          },
          {
            id: 'camp_003',
            name: 'Product Launch',
            budget: 2000,
            spent: 1432.11,
            projectedSpend: 2012.35,
            pacingStatus: 'at_risk'
          }
        ]
      })
    } finally {
      setLoading(false)
    }
  }

  const getPacingColor = (status) => {
    switch (status) {
      case 'under_pacing': return 'text-blue-600 bg-blue-50'
      case 'on_track': return 'text-green-600 bg-green-50'
      case 'slightly_over': return 'text-yellow-600 bg-yellow-50'
      case 'at_risk': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getPacingIcon = (status) => {
    switch (status) {
      case 'under_pacing': return <ArrowDown size={16} />
      case 'on_track': return <TrendingUp size={16} />
      case 'slightly_over': return <ArrowUp size={16} />
      case 'at_risk': return <AlertTriangle size={16} />
      default: return <Info size={16} />
    }
  }

  const getPacingLabel = (status) => {
    switch (status) {
      case 'under_pacing': return 'Under Pacing'
      case 'on_track': return 'On Track'
      case 'slightly_over': return 'Slightly Over'
      case 'at_risk': return 'At Risk'
      default: return 'Unknown'
    }
  }

  const calculatePercentage = (spent, budget) => {
    if (!budget || budget === 0) return 0
    return Math.min((spent / budget) * 100, 100)
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="animate-spin text-gray-400" size={32} />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center">
          <AlertTriangle className="mx-auto mb-4 text-red-500" size={48} />
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    )
  }

  if (!budgetData) return null

  const overallPercentage = calculatePercentage(budgetData.totalSpent, budgetData.totalBudget)

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <DollarSign className="text-blue-600" size={24} />
            Budget Pacing
          </h2>
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="all">All Time</option>
          </select>
        </div>

        {/* Overall Budget Summary */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Overall Budget Usage</span>
            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getPacingColor(budgetData.pacingStatus)}`}>
              {getPacingIcon(budgetData.pacingStatus)}
              {getPacingLabel(budgetData.pacingStatus)}
            </span>
          </div>
          
          {/* Progress Bar */}
          <div className="relative h-6 bg-gray-100 rounded-full overflow-hidden mb-2">
            <div
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500"
              style={{ width: `${overallPercentage}%` }}
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-medium text-gray-700">
                {overallPercentage.toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Budget Details */}
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div>
              <p className="text-xs text-gray-500">Spent</p>
              <p className="text-lg font-semibold text-gray-900">
                ${budgetData.totalSpent.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Budget</p>
              <p className="text-lg font-semibold text-gray-900">
                ${budgetData.totalBudget.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Projected</p>
              <p className="text-lg font-semibold text-gray-900">
                ${budgetData.projectedSpend.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>

          {/* Time Remaining */}
          <div className="flex items-center gap-2 mt-4 p-3 bg-gray-50 rounded-lg">
            <Calendar className="text-gray-400" size={16} />
            <span className="text-sm text-gray-600">
              {budgetData.daysRemaining} days remaining in billing period
            </span>
          </div>
        </div>
      </div>

      {/* Campaign Breakdown */}
      {!campaignId && budgetData.campaigns && budgetData.campaigns.length > 0 && (
        <div className="p-6">
          <h3 className="font-medium mb-4">Campaign Breakdown</h3>
          <div className="space-y-4">
            {budgetData.campaigns.map(campaign => {
              const percentage = calculatePercentage(campaign.spent, campaign.budget)
              return (
                <div key={campaign.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{campaign.name}</h4>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getPacingColor(campaign.pacingStatus)}`}>
                      {getPacingIcon(campaign.pacingStatus)}
                      {getPacingLabel(campaign.pacingStatus)}
                    </span>
                  </div>
                  
                  {/* Campaign Progress Bar */}
                  <div className="relative h-4 bg-gray-100 rounded-full overflow-hidden mb-2">
                    <div
                      className={`absolute top-0 left-0 h-full transition-all duration-500 ${
                        campaign.pacingStatus === 'at_risk' ? 'bg-red-500' :
                        campaign.pacingStatus === 'slightly_over' ? 'bg-yellow-500' :
                        campaign.pacingStatus === 'on_track' ? 'bg-green-500' :
                        'bg-blue-500'
                      }`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">
                      ${campaign.spent.toLocaleString()} / ${campaign.budget.toLocaleString()}
                    </span>
                    <span className="text-gray-500">
                      Projected: ${campaign.projectedSpend.toLocaleString()}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div className="p-6 bg-gray-50 border-t border-gray-200">
        <h3 className="font-medium mb-3 flex items-center gap-2">
          <Info className="text-blue-600" size={16} />
          Recommendations
        </h3>
        <ul className="space-y-2 text-sm text-gray-600">
          {budgetData.pacingStatus === 'at_risk' && (
            <li className="flex items-start gap-2">
              <span className="text-red-500 mt-0.5">•</span>
              <span>Consider reducing bids or pausing low-performing keywords to control spending.</span>
            </li>
          )}
          {budgetData.pacingStatus === 'under_pacing' && (
            <li className="flex items-start gap-2">
              <span className="text-blue-500 mt-0.5">•</span>
              <span>You have budget available. Consider increasing bids or expanding targeting to maximize reach.</span>
            </li>
          )}
          {budgetData.pacingStatus === 'on_track' && (
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">•</span>
              <span>Your budget pacing looks good. Continue monitoring for any significant changes.</span>
            </li>
          )}
          <li className="flex items-start gap-2">
            <span className="text-gray-500 mt-0.5">•</span>
            <span>Set up automated alerts to notify you when campaigns exceed 80% of their budget.</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

export default BudgetPacingWidget