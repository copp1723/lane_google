# Lane MCP - Google Ads Automation Platform

**Production-ready AI-powered Google Ads automation platform** that transforms campaign briefs into fully managed Google Ads campaigns with ML-driven optimization.

## 🚀 Features

### Core Capabilities
- **AI-Powered Campaign Creation**: Convert natural language briefs into complete Google Ads campaigns
- **ML Budget Pacing**: Intelligent budget allocation with adaptive, conservative, and accelerated strategies
- **Real-Time Monitoring**: Health checks and performance tracking every 2 hours
- **Multi-Account Management**: Enterprise-grade multi-tenant architecture with role-based access
- **Approval Workflows**: Automated approval processes with customizable rules
- **Advanced Analytics**: Time-series forecasting and performance predictions

### Technical Features
- **Production Authentication**: JWT-based auth with bcrypt password hashing
- **Database Support**: PostgreSQL (production) and SQLite (development)
- **Redis Integration**: Session management, caching, and rate limiting
- **Google Ads API v15**: Full integration with real API (no mocks)
- **RESTful APIs**: Complete API suite for all platform features
- **Background Services**: Asynchronous monitoring and optimization

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+ (for production)
- Redis 6+ (recommended for production)
- Google Ads API credentials
- Node.js 14+ (for frontend)

## 🛠️ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/lane_google.git
cd lane_google
```

### 2. Run Setup Script
```bash
chmod +x setup_production.sh
./setup_production.sh
```

This script will:
- Create a Python virtual environment
- Install all dependencies
- Set up the database
- Create configuration files
- Run initial migrations

### 3. Configure Environment

Edit `.env` file with your credentials:
```env
# Google Ads API (Required)
GOOGLE_ADS_CLIENT_ID=your-client-id
GOOGLE_ADS_CLIENT_SECRET=your-client-secret
GOOGLE_ADS_REFRESH_TOKEN=your-refresh-token
GOOGLE_ADS_DEVELOPER_TOKEN=your-developer-token
GOOGLE_ADS_CUSTOMER_ID=your-customer-id

# Security (Change these!)
SECRET_KEY=generate-a-secure-random-key
JWT_SECRET_KEY=generate-another-secure-key

# Database (for production)
DATABASE_URL=postgresql://user:password@localhost:5432/lane_mcp

# Redis (optional but recommended)
REDIS_URL=redis://localhost:6379/0
```

### 4. Run the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Run in development mode
python main_production.py

# Or run with gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 main_production:app
```

## 🧪 Testing

### Local Testing
1. The application runs on `http://localhost:5000` by default
2. API documentation is available at `/api/docs`
3. Health check endpoint: `/api/health`

### Create Test Campaign
```bash
# Get auth token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your-password"}'

# Create campaign brief
curl -X POST http://localhost:5000/api/campaigns/brief \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "E-commerce Fashion",
    "target_audience": "Women 25-45 interested in sustainable fashion",
    "budget": 5000,
    "goals": "Increase online sales by 30%"
  }'
```

## 🚀 Production Deployment

### Database Setup (PostgreSQL)
```bash
# Create database
createdb lane_mcp

# Run migrations
python migrations/run_migrations.py migrate
```

### Redis Setup
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
redis-server
```

### Environment Variables
Ensure all production environment variables are set:
- Use strong, unique keys for `SECRET_KEY` and `JWT_SECRET_KEY`
- Set `FLASK_ENV=production`
- Configure proper database connection string
- Set up email configuration for notifications

### Deployment Options

#### Option 1: Docker
```bash
docker build -t lane-mcp .
docker run -p 5000:5000 --env-file .env lane-mcp
```

#### Option 2: Systemd Service
Create `/etc/systemd/system/lane-mcp.service`:
```ini
[Unit]
Description=Lane MCP Google Ads Platform
After=network.target postgresql.service redis.service

[Service]
User=www-data
WorkingDirectory=/path/to/lane_google
Environment="PATH=/path/to/lane_google/venv/bin"
ExecStart=/path/to/lane_google/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 main_production:app

[Install]
WantedBy=multi-user.target
```

#### Option 3: Cloud Platforms
- **Heroku**: Use included `Procfile`
- **AWS**: Deploy with Elastic Beanstalk or ECS
- **Google Cloud**: Use App Engine or Cloud Run

## 📊 Monitoring

### Health Checks
```bash
# System health
curl http://localhost:5000/api/health

# Detailed health
curl http://localhost:5000/api/health?detailed=true
```

### Logs
- Application logs: `logs/app.log`
- Service logs: Check individual service endpoints
- Database queries: Enable with `DATABASE_ECHO=true`

## 🔒 Security Notes

1. **Always change default keys** in production
2. **Use HTTPS** with proper SSL certificates
3. **Enable rate limiting** for public endpoints
4. **Regular security updates** for dependencies
5. **Backup database** regularly

## 📖 API Documentation

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/profile` - Get user profile

### Campaigns
- `POST /api/campaigns/brief` - Create campaign from brief
- `GET /api/campaigns` - List campaigns
- `GET /api/campaigns/{id}` - Get campaign details
- `PUT /api/campaigns/{id}` - Update campaign
- `POST /api/campaigns/{id}/launch` - Launch campaign

### Analytics
- `GET /api/analytics/campaigns/{id}` - Get campaign analytics
- `GET /api/analytics/forecast/{id}` - Get performance forecast

### Budget Management
- `GET /api/budget/campaigns/{id}/status` - Get budget status
- `POST /api/budget/campaigns/{id}/adjust` - Adjust budget pacing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

- Documentation: `/docs`
- Issues: GitHub Issues
- Email: support@lanemcp.com

---

**Built with ❤️ for Google Ads automation**