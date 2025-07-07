"""Email service for lane_google using Mailgun"""

import os
import re
import requests
from typing import List, Dict, Any, Optional, Union
import logging
from datetime import datetime
import hashlib
import time
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EmailType(Enum):
    """Email types for tracking and preferences"""
    TRANSACTIONAL = "transactional"
    CAMPAIGN_ALERT = "campaign_alert"
    BUDGET_ALERT = "budget_alert"
    PERFORMANCE_REPORT = "performance_report"
    SYSTEM_NOTIFICATION = "system_notification"
    INVITATION = "invitation"


@dataclass
class EmailAttachment:
    """Email attachment data"""
    filename: str
    data: bytes
    content_type: str = "application/octet-stream"


class MailgunClient:
    """Mailgun client for sending emails"""
    
    def __init__(self):
        self.api_key = os.getenv('MAILGUN_API_KEY')
        self.domain = os.getenv('MAILGUN_DOMAIN')
        self.region = os.getenv('MAILGUN_REGION', 'US')
        self.from_email = os.getenv('FROM_EMAIL', f'Lane MCP <noreply@{self.domain}>')
        self.reply_to = os.getenv('REPLY_TO_EMAIL', f'support@{self.domain}')
        
        if not self.api_key or not self.domain:
            logger.warning("Mailgun configuration missing")
        
        self.base_url = 'https://api.eu.mailgun.net/v3' if self.region == 'EU' else 'https://api.mailgun.net/v3'
    
    def send_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        html: str,
        text: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        variables: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[EmailAttachment]] = None
    ) -> bool:
        """Send an email via Mailgun"""
        
        if not self.api_key or not self.domain:
            logger.error("Mailgun not configured")
            return False
        
        try:
            # Prepare recipient list
            recipients = to if isinstance(to, list) else [to]
            
            # Strip HTML tags for text version if not provided
            if not text:
                text = re.sub('<[^<]+?>', '', html)
            
            # Prepare data
            data = {
                'from': from_email or self.from_email,
                'to': recipients,
                'subject': subject,
                'html': html,
                'text': text,
                'h:Reply-To': reply_to or self.reply_to,
                'o:tag': tags or ['transactional'],
            }
            
            # Add custom variables
            if variables:
                data['h:X-Mailgun-Variables'] = str(variables)
            
            # Prepare files for attachments
            files = []
            if attachments:
                for attachment in attachments:
                    files.append((
                        'attachment',
                        (attachment.filename, attachment.data, attachment.content_type)
                    ))
            
            # Send request
            response = requests.post(
                f'{self.base_url}/{self.domain}/messages',
                auth=('api', self.api_key),
                data=data,
                files=files if files else None
            )
            
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Email sent successfully: {result.get('id')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        return bool(re.match(pattern, email))
    
    def generate_unsubscribe_token(self, user_id: str, email_type: str) -> str:
        """Generate secure unsubscribe token"""
        secret = os.getenv('UNSUBSCRIBE_SECRET', 'default-secret-change-me')
        timestamp = str(int(time.time()))
        
        # Create hash
        data = f"{user_id}:{email_type}:{timestamp}:{secret}"
        token = hashlib.sha256(data.encode()).hexdigest()
        
        return f"{token}:{timestamp}"
    
    def verify_unsubscribe_token(self, token: str, user_id: str, email_type: str, max_age_days: int = 30) -> bool:
        """Verify unsubscribe token"""
        try:
            token_hash, timestamp = token.split(':')
            token_time = int(timestamp)
            
            # Check age
            current_time = int(time.time())
            if current_time - token_time > (max_age_days * 24 * 60 * 60):
                return False
            
            # Regenerate and compare
            secret = os.getenv('UNSUBSCRIBE_SECRET', 'default-secret-change-me')
            data = f"{user_id}:{email_type}:{timestamp}:{secret}"
            expected_hash = hashlib.sha256(data.encode()).hexdigest()
            
            return token_hash == expected_hash
            
        except Exception:
            return False
    
    def get_unsubscribe_url(self, user_id: str, email_type: str) -> str:
        """Generate unsubscribe URL"""
        base_url = os.getenv('APP_URL', 'http://localhost:5000')
        token = self.generate_unsubscribe_token(user_id, email_type)
        return f"{base_url}/api/email/unsubscribe?token={token}&user={user_id}&type={email_type}"


class EmailTemplates:
    """Email templates for lane_google"""
    
    @staticmethod
    def base_template(content: str, unsubscribe_url: Optional[str] = None) -> str:
        """Base email template"""
        footer = ""
        if unsubscribe_url:
            footer = f'''
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; text-align: center; font-size: 12px; color: #666;">
                <p>You're receiving this email because you're subscribed to Lane MCP notifications.</p>
                <p><a href="{unsubscribe_url}" style="color: #0066cc;">Unsubscribe</a></p>
            </div>
            '''
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Lane MCP</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 40px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #333; font-size: 24px; margin: 0;">Lane MCP</h1>
                    <p style="color: #666; font-size: 14px; margin: 5px 0 0 0;">AI-Powered Google Ads Management</p>
                </div>
                {content}
                {footer}
            </div>
        </body>
        </html>
        '''
    
    @staticmethod
    def campaign_alert(campaign_name: str, alert_type: str, message: str, action_url: str) -> str:
        """Campaign alert email template"""
        content = f'''
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 15px; margin-bottom: 20px;">
            <h2 style="color: #856404; font-size: 18px; margin: 0 0 10px 0;">Campaign Alert: {alert_type}</h2>
            <p style="color: #856404; margin: 0;"><strong>Campaign:</strong> {campaign_name}</p>
        </div>
        
        <div style="margin: 20px 0;">
            <p style="color: #333; line-height: 1.6;">{message}</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{action_url}" style="display: inline-block; background-color: #007bff; color: #ffffff; text-decoration: none; padding: 12px 30px; border-radius: 4px; font-weight: 500;">View Campaign Details</a>
        </div>
        '''
        return EmailTemplates.base_template(content)
    
    @staticmethod
    def budget_alert(campaign_name: str, current_spend: float, budget_limit: float, percentage: float) -> str:
        """Budget alert email template"""
        content = f'''
        <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; padding: 15px; margin-bottom: 20px;">
            <h2 style="color: #721c24; font-size: 18px; margin: 0 0 10px 0;">Budget Alert</h2>
            <p style="color: #721c24; margin: 0;"><strong>Campaign:</strong> {campaign_name}</p>
        </div>
        
        <div style="margin: 20px 0;">
            <p style="color: #333; line-height: 1.6;">Your campaign has reached <strong>{percentage:.1f}%</strong> of its budget limit.</p>
            
            <div style="background-color: #f8f9fa; border-radius: 4px; padding: 15px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Current Spend:</strong> ${current_spend:,.2f}</p>
                <p style="margin: 5px 0;"><strong>Budget Limit:</strong> ${budget_limit:,.2f}</p>
                <p style="margin: 5px 0;"><strong>Remaining:</strong> ${budget_limit - current_spend:,.2f}</p>
            </div>
        </div>
        '''
        return EmailTemplates.base_template(content)
    
    @staticmethod
    def invitation(inviter_name: str, agency_name: str, role: str, invitation_url: str) -> str:
        """User invitation email template"""
        content = f'''
        <div style="margin: 20px 0;">
            <p style="color: #333; line-height: 1.6;">Hello,</p>
            
            <p style="color: #333; line-height: 1.6;">
                {inviter_name} has invited you to join <strong>{agency_name}</strong> on Lane MCP 
                as a <strong>{role}</strong>.
            </p>
            
            <p style="color: #333; line-height: 1.6;">
                Lane MCP is an AI-powered platform that helps businesses manage their Google Ads 
                campaigns more efficiently with natural language commands and intelligent automation.
            </p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{invitation_url}" style="display: inline-block; background-color: #28a745; color: #ffffff; text-decoration: none; padding: 12px 30px; border-radius: 4px; font-weight: 500;">Accept Invitation</a>
        </div>
        
        <p style="color: #666; font-size: 14px; margin-top: 20px;">
            This invitation will expire in 7 days. If you have any questions, please contact your administrator.
        </p>
        '''
        return EmailTemplates.base_template(content)
    
    @staticmethod
    def performance_report(campaign_name: str, date_range: str, metrics: Dict[str, Any]) -> str:
        """Performance report email template"""
        content = f'''
        <h2 style="color: #333; font-size: 20px; margin: 0 0 20px 0;">Performance Report: {campaign_name}</h2>
        <p style="color: #666; margin: 0 0 20px 0;">Report for {date_range}</p>
        
        <div style="background-color: #f8f9fa; border-radius: 4px; padding: 20px; margin: 20px 0;">
            <h3 style="color: #333; font-size: 16px; margin: 0 0 15px 0;">Key Metrics</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <p style="color: #666; margin: 0; font-size: 14px;">Impressions</p>
                    <p style="color: #333; margin: 0; font-size: 24px; font-weight: 600;">{metrics.get('impressions', 0):,}</p>
                </div>
                <div>
                    <p style="color: #666; margin: 0; font-size: 14px;">Clicks</p>
                    <p style="color: #333; margin: 0; font-size: 24px; font-weight: 600;">{metrics.get('clicks', 0):,}</p>
                </div>
                <div>
                    <p style="color: #666; margin: 0; font-size: 14px;">CTR</p>
                    <p style="color: #333; margin: 0; font-size: 24px; font-weight: 600;">{metrics.get('ctr', 0):.2f}%</p>
                </div>
                <div>
                    <p style="color: #666; margin: 0; font-size: 14px;">Cost</p>
                    <p style="color: #333; margin: 0; font-size: 24px; font-weight: 600;">${metrics.get('cost', 0):,.2f}</p>
                </div>
            </div>
        </div>
        '''
        return EmailTemplates.base_template(content)


# Initialize global email client
email_client = MailgunClient()


# Helper functions
def send_campaign_alert(user_email: str, campaign_name: str, alert_type: str, message: str, campaign_id: str) -> bool:
    """Send campaign alert email"""
    action_url = f"{os.getenv('APP_URL', 'http://localhost:5000')}/campaigns/{campaign_id}"
    html = EmailTemplates.campaign_alert(campaign_name, alert_type, message, action_url)
    
    return email_client.send_email(
        to=user_email,
        subject=f"Campaign Alert: {alert_type} - {campaign_name}",
        html=html,
        tags=['campaign_alert', alert_type.lower()]
    )


def send_budget_alert(user_email: str, campaign_name: str, current_spend: float, budget_limit: float) -> bool:
    """Send budget alert email"""
    percentage = (current_spend / budget_limit) * 100
    html = EmailTemplates.budget_alert(campaign_name, current_spend, budget_limit, percentage)
    
    return email_client.send_email(
        to=user_email,
        subject=f"Budget Alert: {campaign_name} at {percentage:.0f}% of limit",
        html=html,
        tags=['budget_alert']
    )


def send_invitation(email: str, inviter_name: str, agency_name: str, role: str, token: str) -> bool:
    """Send user invitation email"""
    invitation_url = f"{os.getenv('APP_URL', 'http://localhost:5000')}/invite/{token}"
    html = EmailTemplates.invitation(inviter_name, agency_name, role, invitation_url)
    
    return email_client.send_email(
        to=email,
        subject=f"Invitation to join {agency_name} on Lane MCP",
        html=html,
        tags=['invitation']
    )