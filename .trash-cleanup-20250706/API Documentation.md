# API Documentation

## Overview

The Lane MCP Platform API provides comprehensive endpoints for managing AI-powered Google Ads campaigns. This RESTful API follows standard HTTP conventions and returns JSON responses.

## Base URL

- **Development**: `http://localhost:5001/api`
- **Production**: `https://your-domain.com/api`

## Authentication

All API endpoints (except health checks) require authentication using JWT tokens.

### Getting a Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

### Using the Token

Include the JWT token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Optional success message",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Response
```json
{
  "status": "error",
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Endpoints

### Authentication

#### Login
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "access_token": "jwt_token",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "role": "manager",
      "permissions": ["campaigns.read", "campaigns.create"]
    }
  }
}
```

#### Logout
```http
POST /api/auth/logout
```

**Headers:**
```
Authorization: Bearer <token>
```

#### Refresh Token
```http
POST /api/auth/refresh
```

**Headers:**
```
Authorization: Bearer <token>
```

### AI Agent

#### Chat with AI Agent
```http
POST /api/ai/chat
```

**Request Body:**
```json
{
  "message": "I want to create a search campaign for my new product",
  "conversation_id": "optional_uuid"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "response": "I'd be happy to help you create a search campaign...",
    "conversation_id": "uuid",
    "suggestions": [
      "What's your target audience?",
      "What's your budget range?",
      "What keywords are you targeting?"
    ]
  }
}
```

#### Generate Campaign Brief
```http
POST /api/ai/generate-brief
```

**Request Body:**
```json
{
  "conversation_id": "uuid"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "brief": {
      "campaign_name": "New Product Launch",
      "campaign_type": "SEARCH",
      "budget_amount": 1000.00,
      "target_audience": "Tech enthusiasts aged 25-45",
      "keywords": ["new product", "innovative tech", "gadget"],
      "ad_copy_suggestions": ["Discover the future of tech..."]
    }
  }
}
```

### Campaigns

#### List Campaigns
```http
GET /api/campaigns?page=1&per_page=20&status=active
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 20, max: 100)
- `status` (string): Filter by status (draft, pending, active, paused, archived)
- `customer_id` (string): Filter by Google Ads customer ID
- `search` (string): Search in campaign names

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Summer Sale Campaign",
      "status": "active",
      "campaign_type": "SEARCH",
      "budget_amount": 1500.00,
      "daily_spend": 45.67,
      "performance": {
        "impressions": 12500,
        "clicks": 234,
        "ctr": 1.87,
        "cpc": 0.65,
        "conversions": 12,
        "cost": 152.10
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-02T12:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

#### Create Campaign
```http
POST /api/campaigns
```

**Request Body:**
```json
{
  "name": "New Campaign",
  "campaign_type": "SEARCH",
  "budget_amount": 1000.00,
  "target_audience": "Target description",
  "keywords": ["keyword1", "keyword2"],
  "google_customer_id": "1234567890",
  "description": "Campaign description"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "name": "New Campaign",
    "status": "draft",
    "campaign_type": "SEARCH",
    "budget_amount": 1000.00,
    "google_customer_id": "1234567890",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Campaign created successfully"
}
```

#### Get Campaign Details
```http
GET /api/campaigns/{id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "name": "Campaign Name",
    "status": "active",
    "campaign_type": "SEARCH",
    "budget_amount": 1000.00,
    "target_audience": "Target description",
    "keywords": ["keyword1", "keyword2"],
    "performance": {
      "impressions": 5000,
      "clicks": 100,
      "ctr": 2.0,
      "cpc": 0.50,
      "conversions": 5,
      "cost": 50.00,
      "roas": 4.5
    },
    "optimization_history": [
      {
        "date": "2024-01-01",
        "action": "bid_adjustment",
        "details": "Increased bids for high-performing keywords",
        "impact": "+15% CTR"
      }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-02T12:30:00Z"
  }
}
```

#### Update Campaign
```http
PUT /api/campaigns/{id}
```

**Request Body:**
```json
{
  "name": "Updated Campaign Name",
  "budget_amount": 1500.00,
  "status": "paused"
}
```

#### Delete Campaign
```http
DELETE /api/campaigns/{id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Campaign archived successfully"
}
```

### Analytics

#### Dashboard Analytics
```http
GET /api/analytics/dashboard?date_range=30d
```

**Query Parameters:**
- `date_range` (string): 7d, 30d, 90d, or custom
- `start_date` (string): Start date for custom range (YYYY-MM-DD)
- `end_date` (string): End date for custom range (YYYY-MM-DD)

**Response:**
```json
{
  "status": "success",
  "data": {
    "summary": {
      "total_campaigns": 25,
      "active_campaigns": 18,
      "total_spend": 15420.50,
      "total_conversions": 234,
      "average_cpc": 0.65,
      "average_roas": 4.2
    },
    "performance_trends": [
      {
        "date": "2024-01-01",
        "impressions": 10000,
        "clicks": 200,
        "cost": 130.00,
        "conversions": 8
      }
    ],
    "top_campaigns": [
      {
        "id": 1,
        "name": "Best Performing Campaign",
        "roas": 6.5,
        "conversions": 45,
        "cost": 890.00
      }
    ]
  }
}
```

#### Campaign Performance
```http
GET /api/analytics/campaigns/{id}/performance?date_range=30d
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "campaign_id": 123,
    "date_range": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-30"
    },
    "metrics": {
      "impressions": 50000,
      "clicks": 1000,
      "ctr": 2.0,
      "cpc": 0.50,
      "cost": 500.00,
      "conversions": 25,
      "conversion_rate": 2.5,
      "roas": 5.0
    },
    "daily_performance": [
      {
        "date": "2024-01-01",
        "impressions": 1500,
        "clicks": 30,
        "cost": 15.00,
        "conversions": 1
      }
    ],
    "keyword_performance": [
      {
        "keyword": "best product",
        "impressions": 5000,
        "clicks": 100,
        "ctr": 2.0,
        "cpc": 0.45,
        "conversions": 5
      }
    ]
  }
}
```

### Google Ads Integration

#### List Google Ads Accounts
```http
GET /api/google-ads/accounts
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "customer_id": "1234567890",
      "name": "My Business Account",
      "currency": "USD",
      "timezone": "America/New_York",
      "status": "ENABLED"
    }
  ]
}
```

#### Sync Campaign Data
```http
POST /api/google-ads/sync/{customer_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "synced_campaigns": 15,
    "updated_campaigns": 8,
    "new_campaigns": 2,
    "sync_timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Health Checks

#### Basic Health Check
```http
GET /api/health/
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "version": "1.0.0"
  }
}
```

#### Detailed Health Check
```http
GET /api/health/detailed
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "services": {
      "database": {
        "status": "healthy",
        "response_time_ms": 5
      },
      "redis": {
        "status": "healthy",
        "response_time_ms": 2
      },
      "openrouter_api": {
        "status": "healthy",
        "response_time_ms": 150
      }
    },
    "system": {
      "cpu_usage": 25.5,
      "memory_usage": 45.2,
      "disk_usage": 60.1
    }
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `UNAUTHORIZED` | Authentication required |
| `FORBIDDEN` | Insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `RATE_LIMITED` | Rate limit exceeded |
| `INTERNAL_ERROR` | Internal server error |
| `SERVICE_UNAVAILABLE` | External service unavailable |

## Rate Limits

- **Authentication**: 10 requests per minute
- **API Endpoints**: 1000 requests per hour
- **AI Agent**: 100 requests per hour

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

## Webhooks

### Campaign Status Updates
```http
POST /api/webhooks/campaign-status
```

**Payload:**
```json
{
  "event": "campaign.status_changed",
  "campaign_id": 123,
  "old_status": "pending",
  "new_status": "active",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Performance Alerts
```http
POST /api/webhooks/performance-alert
```

**Payload:**
```json
{
  "event": "performance.threshold_exceeded",
  "campaign_id": 123,
  "metric": "cpc",
  "threshold": 1.00,
  "current_value": 1.25,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## SDKs and Libraries

### Python SDK
```python
from lane_mcp import LaneMCPClient

client = LaneMCPClient(
    api_key="your_api_key",
    base_url="https://api.lane-mcp.com"
)

# List campaigns
campaigns = client.campaigns.list(status="active")

# Create campaign
campaign = client.campaigns.create({
    "name": "New Campaign",
    "campaign_type": "SEARCH",
    "budget_amount": 1000.00
})
```

### JavaScript SDK
```javascript
import { LaneMCPClient } from '@lane-mcp/sdk';

const client = new LaneMCPClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.lane-mcp.com'
});

// List campaigns
const campaigns = await client.campaigns.list({ status: 'active' });

// Create campaign
const campaign = await client.campaigns.create({
  name: 'New Campaign',
  campaign_type: 'SEARCH',
  budget_amount: 1000.00
});
```

## Testing

### Postman Collection
A Postman collection is available for testing all API endpoints. Import the collection and set up your environment variables:

- `base_url`: API base URL
- `jwt_token`: Your authentication token

### cURL Examples

#### Authentication
```bash
curl -X POST \
  http://localhost:5001/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
```

#### Create Campaign
```bash
curl -X POST \
  http://localhost:5001/api/campaigns \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Test Campaign",
    "campaign_type": "SEARCH",
    "budget_amount": 1000.00,
    "target_audience": "Tech enthusiasts",
    "keywords": ["technology", "innovation"]
  }'
```

## Support

For API support, please contact:
- **Email**: api-support@lane-mcp.com
- **Documentation**: https://docs.lane-mcp.com
- **Status Page**: https://status.lane-mcp.com

