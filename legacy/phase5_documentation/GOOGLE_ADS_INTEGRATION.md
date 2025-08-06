# Google Ads API Integration Guide

## Overview

The Lane MCP platform now supports full Google Ads API integration, allowing you to manage campaigns, budgets, and performance metrics directly through the API.

## Features

- **Smart Service Selection**: Automatically uses real Google Ads API when credentials are available, falls back to mock service otherwise
- **Comprehensive Error Handling**: Handles rate limits, authentication errors, and transient failures with automatic retry logic
- **Full Campaign Management**: Create, update, pause, and enable campaigns
- **Performance Metrics**: Track impressions, clicks, conversions, and costs
- **Budget Management**: Update campaign budgets in real-time

## Setup Instructions

### 1. Prerequisites

- Google Ads account (or test account)
- Google Cloud Project with Google Ads API enabled
- Python google-ads client library

Install the Google Ads Python client:
```bash
pip install google-ads
```

### 2. Get OAuth2 Credentials

Run the credential generation script:
```bash
python scripts/generate_google_ads_credentials.py
```

This script will:
1. Guide you through creating OAuth2 credentials in Google Cloud Console
2. Handle the OAuth2 authorization flow
3. Generate a refresh token
4. Save credentials to `google_ads_credentials.txt`

### 3. Get Developer Token

1. Go to https://ads.google.com/aw/apicenter
2. Apply for API access if you haven't already
3. Copy your developer token

### 4. Configure Environment

Add the following to your `.env` file:

```env
# Google Ads API Configuration
GOOGLE_ADS_DEVELOPER_TOKEN=your-developer-token
GOOGLE_ADS_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your-client-secret
GOOGLE_ADS_REFRESH_TOKEN=your-refresh-token

# Optional: Manager account customer ID (without hyphens)
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890

# Force mock mode (set to false to use real API)
GOOGLE_ADS_USE_MOCK=false
```

### 5. Test Your Setup

Run the test script to verify your configuration:
```bash
python scripts/test_google_ads_integration.py
```

## API Endpoints

### Check Service Status
```http
GET /api/google-ads/status
Authorization: Bearer <token>
```

Response:
```json
{
  "success": true,
  "status": {
    "service_type": "real",
    "credentials_present": {
      "developer_token": true,
      "client_id": true,
      "client_secret": true,
      "refresh_token": true
    },
    "client_initialized": true,
    "force_mock": false
  },
  "message": "Using REAL Google Ads API service"
}
```

### Get Accessible Customers
```http
GET /api/google-ads/customers
Authorization: Bearer <token>
```

### Get Campaigns
```http
GET /api/google-ads/customers/{customer_id}/campaigns
Authorization: Bearer <token>
```

### Create Campaign
```http
POST /api/google-ads/customers/{customer_id}/campaigns
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Campaign",
  "budget_amount": 50.0,
  "channel_type": "SEARCH",
  "bidding_strategy": "MAXIMIZE_CLICKS",
  "start_date": "20240101",
  "end_date": "20241231"
}
```

### Update Campaign Budget
```http
PUT /api/google-ads/customers/{customer_id}/campaigns/{campaign_id}/budget
Authorization: Bearer <token>
Content-Type: application/json

{
  "budget_amount": 100.0
}
```

### Get Performance Metrics
```http
GET /api/google-ads/customers/{customer_id}/performance?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

## Error Handling

The integration includes comprehensive error handling:

- **Authentication Errors**: Clear messages about credential issues
- **Rate Limiting**: Automatic exponential backoff and retry
- **Transient Errors**: Automatic retry with configurable attempts
- **Validation Errors**: Detailed field-level error messages

Example error response:
```json
{
  "success": false,
  "error": "Authentication failed. Please ensure you have:\n1. Valid OAuth2 credentials (not Customer ID)\n2. Active Google Ads developer token\n3. Proper API access permissions\nRun: python scripts/generate_google_ads_credentials.py",
  "error_code": "AUTH_ERROR"
}
```

## Troubleshooting

### Common Issues

1. **"Client ID looks like Customer ID"**
   - OAuth Client IDs should end with `.apps.googleusercontent.com`
   - Customer IDs are 10-digit numbers
   - Don't confuse the two!

2. **"Missing refresh token"**
   - Run the credential generation script
   - Make sure to grant all requested permissions
   - The script will save the refresh token automatically

3. **"Authentication failed"**
   - Verify your developer token is active
   - Check that OAuth credentials are valid
   - Ensure the refresh token hasn't been revoked

4. **"No accessible customers"**
   - Make sure your Google account has access to Google Ads accounts
   - For testing, create a test account at https://ads.google.com/home/tools/manager-accounts/

### Debug Mode

To see detailed logs:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Force Mock Mode

To temporarily use mock data:
```env
GOOGLE_ADS_USE_MOCK=true
```

## Best Practices

1. **Use Test Accounts**: Always test with Google Ads test accounts first
2. **Handle Rate Limits**: The API has automatic retry logic, but consider implementing request batching
3. **Monitor Costs**: Be careful with budget changes in production
4. **Log Everything**: Keep detailed logs of all API interactions
5. **Secure Credentials**: Never commit credentials to version control

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Google Ads API documentation: https://developers.google.com/google-ads/api/docs/start
3. Check application logs for detailed error messages