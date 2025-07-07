"""
Analytics Engine with Forecasting
Provides advanced analytics and ML-powered forecasting for campaign performance
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
from database import db
import json
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    metric_type: str
    trend: str  # increasing, decreasing, stable
    slope: float
    percentage_change: float
    confidence: float
    data_points: List[Dict[str, Any]]
    summary: str


@dataclass
class Forecast:
    """Forecast result"""
    metric_type: str
    forecast_values: List[Dict[str, Any]]  # date, value, confidence
    trend: str
    seasonal_pattern: Optional[Dict[str, Any]]
    confidence_score: float
    insights: List[Dict[str, Any]]


class AnalyticsEngine:
    """Advanced analytics engine for campaign performance"""
    
    def __init__(self):
        self.snapshot_interval = 3600  # 1 hour
        self.monitoring_task = None
        self.analytics_history = {}
        
        # ML parameters for forecasting
        self.ml_params = {
            'min_data_points': 7,
            'seasonality_period': 7,  # weekly seasonality
            'trend_threshold': 0.1,
            'confidence_decay': 0.05  # per day forecast
        }
    
    async def start_monitoring(self):
        """Start analytics monitoring"""
        if self.monitoring_task:
            return
        
        logger.info("Starting analytics monitoring service")
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop analytics monitoring"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
        
        logger.info("Analytics monitoring service stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await self._capture_analytics_snapshot()
                await asyncio.sleep(self.snapshot_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in analytics monitoring: {str(e)}")
                await asyncio.sleep(60)
    
    async def _capture_analytics_snapshot(self):
        """Capture current analytics snapshot"""
        try:
            # Get all active campaigns
            from campaign import Campaign
            campaigns = Campaign.query.filter_by(status='active').all()
            
            for campaign in campaigns:
                metrics = await self._get_campaign_metrics(campaign.id)
                await self._save_analytics_snapshot(campaign.id, metrics)
            
            logger.info(f"Captured analytics snapshot for {len(campaigns)} campaigns")
            
        except Exception as e:
            logger.error(f"Error capturing analytics snapshot: {str(e)}")
    
    async def _get_campaign_metrics(self, campaign_id: str) -> Dict[str, float]:
        """Get current metrics for a campaign"""
        # In production, this would fetch from Google Ads API
        # For now, return mock data with some randomness
        import random
        
        base_metrics = {
            'impressions': random.randint(1000, 10000),
            'clicks': random.randint(50, 500),
            'conversions': random.randint(5, 50),
            'cost': random.uniform(100, 1000),
            'ctr': random.uniform(0.01, 0.05),
            'conversion_rate': random.uniform(0.05, 0.15),
            'cpc': random.uniform(0.5, 5.0),
            'cpa': random.uniform(10, 100)
        }
        
        return base_metrics
    
    async def _save_analytics_snapshot(self, campaign_id: str, metrics: Dict[str, float]):
        """Save analytics snapshot to database"""
        from src.models.analytics_snapshot import AnalyticsSnapshot
        
        try:
            for metric_name, value in metrics.items():
                snapshot = AnalyticsSnapshot(
                    campaign_id=campaign_id,
                    metric_type=metric_name,
                    metric_value=value,
                    dimension='overall',
                    period_type='hourly'
                )
                db.session.add(snapshot)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error saving analytics snapshot: {str(e)}")
            db.session.rollback()
    
    async def get_trend_analysis(self, campaign_id: str, metric_type: str,
                               days: int = 30) -> TrendAnalysis:
        """Get trend analysis for a metric"""
        try:
            # Get historical data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            historical_data = await self._get_historical_data(
                campaign_id, metric_type, start_date, end_date
            )
            
            if len(historical_data) < 2:
                return TrendAnalysis(
                    metric_type=metric_type,
                    trend='insufficient_data',
                    slope=0,
                    percentage_change=0,
                    confidence=0,
                    data_points=historical_data,
                    summary='Insufficient data for trend analysis'
                )
            
            # Calculate trend using linear regression
            x_values = np.arange(len(historical_data))
            y_values = np.array([d['value'] for d in historical_data])
            
            # Simple linear regression
            slope, intercept = np.polyfit(x_values, y_values, 1)
            
            # Determine trend
            if abs(slope) < self.ml_params['trend_threshold']:
                trend = 'stable'
            elif slope > 0:
                trend = 'increasing'
            else:
                trend = 'decreasing'
            
            # Calculate percentage change
            first_value = y_values[0]
            last_value = y_values[-1]
            percentage_change = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
            
            # Calculate confidence (R-squared)
            y_pred = slope * x_values + intercept
            ss_res = np.sum((y_values - y_pred) ** 2)
            ss_tot = np.sum((y_values - np.mean(y_values)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            summary = self._generate_trend_summary(metric_type, trend, percentage_change)
            
            return TrendAnalysis(
                metric_type=metric_type,
                trend=trend,
                slope=float(slope),
                percentage_change=float(percentage_change),
                confidence=float(r_squared),
                data_points=historical_data,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error in trend analysis: {str(e)}")
            raise
    
    async def generate_forecast(self, campaign_id: str, metric_type: str,
                              forecast_days: int = 30) -> Forecast:
        """Generate ML-powered forecast for a metric"""
        try:
            # Get historical data (90 days for better patterns)
            trend_analysis = await self.get_trend_analysis(
                campaign_id, metric_type, days=90
            )
            
            if trend_analysis.trend == 'insufficient_data':
                return Forecast(
                    metric_type=metric_type,
                    forecast_values=[],
                    trend='unknown',
                    seasonal_pattern=None,
                    confidence_score=0,
                    insights=[{
                        'type': 'error',
                        'message': 'Insufficient historical data for forecasting'
                    }]
                )
            
            # Extract patterns
            seasonal_pattern = self._detect_seasonality(trend_analysis.data_points)
            
            # Generate forecast
            forecast_values = self._calculate_forecast(
                trend_analysis, seasonal_pattern, forecast_days
            )
            
            # Calculate overall confidence
            confidence_score = self._calculate_forecast_confidence(
                trend_analysis, len(trend_analysis.data_points), forecast_days
            )
            
            # Generate insights
            insights = self._generate_forecast_insights(
                metric_type, forecast_values, trend_analysis, seasonal_pattern
            )
            
            return Forecast(
                metric_type=metric_type,
                forecast_values=forecast_values,
                trend=trend_analysis.trend,
                seasonal_pattern=seasonal_pattern,
                confidence_score=confidence_score,
                insights=insights
            )
            
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            raise
    
    def _detect_seasonality(self, data_points: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Detect seasonal patterns in data"""
        if len(data_points) < 14:  # Need at least 2 weeks
            return None
        
        try:
            # Group by day of week
            day_values = {}
            for point in data_points:
                date = datetime.fromisoformat(point['date'])
                day = date.weekday()
                if day not in day_values:
                    day_values[day] = []
                day_values[day].append(point['value'])
            
            # Calculate average for each day
            day_averages = {}
            for day, values in day_values.items():
                day_averages[day] = np.mean(values)
            
            # Check if there's significant variation
            all_avg = np.mean(list(day_averages.values()))
            variation = np.std(list(day_averages.values())) / all_avg if all_avg != 0 else 0
            
            if variation > 0.1:  # 10% variation threshold
                # Find peak and trough days
                peak_day = max(day_averages, key=day_averages.get)
                trough_day = min(day_averages, key=day_averages.get)
                
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                return {
                    'type': 'weekly',
                    'peak_day': days[peak_day],
                    'trough_day': days[trough_day],
                    'variation': float(variation),
                    'day_factors': {days[d]: day_averages[d] / all_avg for d in day_averages}
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting seasonality: {str(e)}")
            return None
    
    def _calculate_forecast(self, trend_analysis: TrendAnalysis,
                          seasonal_pattern: Optional[Dict[str, Any]],
                          forecast_days: int) -> List[Dict[str, Any]]:
        """Calculate forecast values"""
        forecast_values = []
        last_value = trend_analysis.data_points[-1]['value']
        base_date = datetime.fromisoformat(trend_analysis.data_points[-1]['date'])
        
        for i in range(1, forecast_days + 1):
            forecast_date = base_date + timedelta(days=i)
            
            # Linear projection
            trend_value = last_value + (trend_analysis.slope * i)
            
            # Apply seasonality
            if seasonal_pattern and 'day_factors' in seasonal_pattern:
                day_name = forecast_date.strftime('%A')
                seasonal_factor = seasonal_pattern['day_factors'].get(day_name, 1.0)
                forecast_value = trend_value * seasonal_factor
            else:
                forecast_value = trend_value
            
            # Add some uncertainty
            uncertainty = 0.05 * i  # 5% per day
            
            # Calculate confidence for this point
            point_confidence = max(0.5, 1 - (i * self.ml_params['confidence_decay']))
            
            forecast_values.append({
                'date': forecast_date.isoformat(),
                'value': max(0, forecast_value),  # Ensure non-negative
                'confidence': point_confidence,
                'lower_bound': max(0, forecast_value * (1 - uncertainty)),
                'upper_bound': forecast_value * (1 + uncertainty)
            })
        
        return forecast_values
    
    def _calculate_forecast_confidence(self, trend_analysis: TrendAnalysis,
                                     data_points: int, forecast_days: int) -> float:
        """Calculate overall forecast confidence"""
        # Base confidence on trend confidence
        base_confidence = trend_analysis.confidence
        
        # Adjust for data availability
        data_factor = min(1.0, data_points / 30)  # Full confidence with 30+ days
        
        # Adjust for forecast horizon
        horizon_factor = max(0.5, 1 - (forecast_days / 60))  # Decay over 60 days
        
        return base_confidence * data_factor * horizon_factor
    
    def _generate_forecast_insights(self, metric_type: str,
                                  forecast_values: List[Dict[str, Any]],
                                  trend_analysis: TrendAnalysis,
                                  seasonal_pattern: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate actionable insights from forecast"""
        insights = []
        
        # Trend insight
        if trend_analysis.trend == 'increasing':
            insights.append({
                'type': 'positive',
                'priority': 'medium',
                'message': f'{metric_type} shows positive growth trend',
                'recommendation': 'Consider increasing budget to capitalize on momentum'
            })
        elif trend_analysis.trend == 'decreasing':
            insights.append({
                'type': 'warning',
                'priority': 'high',
                'message': f'{metric_type} is declining',
                'recommendation': 'Review campaign settings and targeting for optimization opportunities'
            })
        
        # Forecast insight
        if forecast_values:
            last_forecast = forecast_values[-1]['value']
            current_value = trend_analysis.data_points[-1]['value']
            change_percent = ((last_forecast - current_value) / current_value * 100) if current_value != 0 else 0
            
            if abs(change_percent) > 20:
                insights.append({
                    'type': 'forecast',
                    'priority': 'high',
                    'message': f'Expecting {abs(change_percent):.1f}% {"increase" if change_percent > 0 else "decrease"} in {metric_type}',
                    'recommendation': 'Plan resources accordingly'
                })
        
        # Seasonal insight
        if seasonal_pattern:
            insights.append({
                'type': 'pattern',
                'priority': 'low',
                'message': f'Weekly pattern detected: Best performance on {seasonal_pattern["peak_day"]}',
                'recommendation': 'Adjust daily budgets to match traffic patterns'
            })
        
        return insights
    
    def _generate_trend_summary(self, metric_type: str, trend: str,
                              percentage_change: float) -> str:
        """Generate human-readable trend summary"""
        direction = 'up' if trend == 'increasing' else 'down' if trend == 'decreasing' else 'stable'
        change = abs(percentage_change)
        
        if trend == 'stable':
            return f'{metric_type} has remained stable'
        
        return f'{metric_type} is {direction} {change:.1f}% over the period'
    
    async def _get_historical_data(self, campaign_id: str, metric_type: str,
                                 start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get historical data from database"""
        from src.models.analytics_snapshot import AnalyticsSnapshot
        
        snapshots = AnalyticsSnapshot.query.filter(
            AnalyticsSnapshot.campaign_id == campaign_id,
            AnalyticsSnapshot.metric_type == metric_type,
            AnalyticsSnapshot.created_at >= start_date,
            AnalyticsSnapshot.created_at <= end_date
        ).order_by(AnalyticsSnapshot.created_at).all()
        
        # Aggregate by day
        daily_data = {}
        for snapshot in snapshots:
            date_key = snapshot.created_at.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = []
            daily_data[date_key].append(snapshot.metric_value)
        
        # Calculate daily averages
        result = []
        for date, values in sorted(daily_data.items()):
            result.append({
                'date': date,
                'value': np.mean(values)
            })
        
        return result
    
    async def export_analytics(self, campaign_id: str, start_date: datetime,
                             end_date: datetime, format: str = 'json') -> Any:
        """Export analytics data"""
        try:
            # Gather data
            metrics = ['impressions', 'clicks', 'conversions', 'cost', 'ctr', 'conversion_rate']
            export_data = {
                'campaign_id': campaign_id,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'metrics': {}
            }
            
            # Get trends and forecasts for each metric
            for metric in metrics:
                trend = await self.get_trend_analysis(campaign_id, metric, 
                                                    days=(end_date - start_date).days)
                forecast = await self.generate_forecast(campaign_id, metric, forecast_days=30)
                
                export_data['metrics'][metric] = {
                    'trend': {
                        'direction': trend.trend,
                        'change_percent': trend.percentage_change,
                        'summary': trend.summary
                    },
                    'forecast': {
                        'next_30_days': forecast.forecast_values[-1]['value'] if forecast.forecast_values else None,
                        'confidence': forecast.confidence_score
                    },
                    'current_value': trend.data_points[-1]['value'] if trend.data_points else None
                }
            
            if format == 'csv':
                return self._format_as_csv(export_data)
            elif format == 'summary':
                return self._format_as_summary(export_data)
            else:
                return export_data
                
        except Exception as e:
            logger.error(f"Error exporting analytics: {str(e)}")
            raise
    
    def _format_as_csv(self, data: Dict[str, Any]) -> str:
        """Format data as CSV"""
        lines = ['Metric,Current Value,Trend,Change %,30-Day Forecast,Confidence']
        
        for metric, values in data['metrics'].items():
            current = values.get('current_value', 0)
            trend = values['trend']['direction']
            change = values['trend']['change_percent']
            forecast = values['forecast'].get('next_30_days', 'N/A')
            confidence = values['forecast'].get('confidence', 0)
            
            lines.append(f'{metric},{current:.2f},{trend},{change:.1f}%,{forecast},{confidence:.2f}')
        
        return '\n'.join(lines)
    
    def _format_as_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format as executive summary"""
        summary = {
            'campaign_id': data['campaign_id'],
            'period': data['period'],
            'key_findings': [],
            'recommendations': []
        }
        
        # Analyze metrics
        declining_metrics = []
        improving_metrics = []
        
        for metric, values in data['metrics'].items():
            if values['trend']['direction'] == 'decreasing':
                declining_metrics.append(metric)
            elif values['trend']['direction'] == 'increasing':
                improving_metrics.append(metric)
        
        # Generate findings
        if improving_metrics:
            summary['key_findings'].append({
                'type': 'positive',
                'message': f'Improving metrics: {", ".join(improving_metrics)}'
            })
        
        if declining_metrics:
            summary['key_findings'].append({
                'type': 'concern',
                'message': f'Declining metrics: {", ".join(declining_metrics)}'
            })
        
        # Generate recommendations
        if 'cost' in declining_metrics and 'conversions' in improving_metrics:
            summary['recommendations'].append({
                'priority': 'high',
                'action': 'Optimize for efficiency',
                'detail': 'Cost is decreasing while conversions improve - good efficiency gains'
            })
        
        if 'ctr' in declining_metrics:
            summary['recommendations'].append({
                'priority': 'medium',
                'action': 'Review ad creative',
                'detail': 'Click-through rate is declining - consider refreshing ad copy'
            })
        
        return summary


# Global analytics engine instance
analytics_engine = AnalyticsEngine()