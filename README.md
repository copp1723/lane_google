# Lane MCP - Google Ads Automation Platform

A production-ready AI-powered system that transforms campaign briefs into fully managed Google Ads campaigns with ML-driven optimization.

## 🚀 Recent Critical Fixes Applied

### Authentication System Standardization
- **Fixed**: Replaced inconsistent `flask_login` usage with JWT authentication across all dashboard APIs
- **Impact**: Dashboard endpoints now properly authenticate using JWT tokens
- **Files**: `src/api/dashboard_apis.py`

### Environment Configuration
- **Fixed**: Replaced hardcoded localhost URLs with environment-based configuration
- **Added**: Comprehensive environment configuration system
- **Files**: `src/config/environment.js`, `.env.development`, `.env.production`, `.env`

### Missing Service Dependencies
- **Fixed**: Created proper AI Agent service class to replace Blueprint-based implementation
- **Fixed**: Resolved campaign orchestrator import issues
- **Files**: `src/services/ai_agent_service.py`, route imports

### Database Model Integration
- **Fixed**: Created missing Conversation model and integrated with database configuration
- **Fixed**: Resolved circular import issues
- **Files**: `src/models/conversation.py`, `src/config/database.py`

### Configuration Management
- **Added**: Centralized settings system with validation and environment support
- **Added**: Comprehensive environment variable templates
- **Files**: `src/config/settings.py`, `.env.example`

## 🏗️ Architecture Overview

### Backend (Python/Flask)
- **Framework**: Flask with Blueprint architecture
- **Database**: SQLAlchemy ORM (PostgreSQL/SQLite)
- **Authentication**: JWT-based with bcrypt password hashing
- **APIs**: RESTful APIs with comprehensive error handling
- **Services**: Modular service architecture for Google Ads, AI, and orchestration

### Frontend (React/Vite)
- **Framework**: React with modern hooks and functional components
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Inline styles with glassmorphism design
- **State Management**: React hooks with context for global state

### External Integrations
- **Google Ads API**: Real API integration with v15
- **OpenAI API**: GPT-4 for campaign generation and chat
- **Redis**: Session management and caching (optional)

## 📁 Project Structure

```
lane_google/
├── README.md                    # Main documentation
├── .gitignore                   # Git ignore rules
├── src/                         # Main application source code
│   ├── api/                     # API endpoints and handlers
│   ├── auth/                    # Authentication modules
│   ├── components/              # React components
│   ├── config/                  # Application configuration
│   ├── models/                  # Database models
│   ├── routes/                  # Flask route blueprints
│   ├── services/                # Business logic services
│   ├── utils/                   # Utility functions
│   └── main_production.py       # Production entry point
├── config/                      # Configuration files
│   ├── env/                     # Environment configurations
│   │   ├── .env.development     # Development environment
│   │   ├── .env.production      # Production environment
│   │   └── .env.example         # Environment template
│   ├── linting/                 # Code quality configurations
│   │   ├── .editorconfig        # Editor configuration
│   │   ├── .flake8              # Python linting
│   │   ├── .prettierrc          # JavaScript formatting
│   │   └── pyproject.toml       # Python project configuration
│   ├── requirements.txt         # Python dependencies
│   └── Makefile                 # Build automation
├── docker/                      # Docker configuration
│   ├── docker-compose.yml       # Multi-container setup
│   └── Dockerfile               # Container definition
├── frontend/                    # Frontend application
│   ├── src/                     # React source code
│   ├── index.html               # HTML entry point
│   ├── package.json             # Node.js dependencies
│   ├── package-lock.json        # Dependency lock file
│   └── vite.config.js           # Vite configuration
├── scripts/                     # Automation scripts
│   ├── quick_start.py           # Quick setup script
│   ├── setup_production.sh      # Production setup
│   └── start_frontend.sh        # Frontend dev server
├── docs/                        # Documentation
│   ├── QUICK_START.md           # Quick start guide
│   ├── STARTUP_GUIDE.md         # Detailed startup guide
│   └── PRODUCTION_SETUP_CHECKLIST.md # Production checklist
└── migrations/                  # Database migrations
    ├── postgres/                # PostgreSQL migrations
    └── run_migrations.py        # Migration runner
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL (for production) or SQLite (for development)
- Redis (optional, for caching)

### Backend Setup

1. **Clone and navigate to the project**
   ```bash
   cd lane_google
   ```

2. **Create Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp config/env/.env.example .env
   # Edit .env with your actual API keys and configuration
   ```

5. **Initialize database**
   ```bash
   python -c "from src.config.database import init_db; init_db()"
   ```

6. **Run the backend server**
   ```bash
   # Development
   python src/main.py
   
   # Production
   python src/main_production.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   # Copy and edit environment files
   cp ../config/env/.env.development .env.local
   # Edit .env.local with your backend URL
   ```

4. **Run the frontend development server**
   ```bash
   npm run dev
   ```

5. **Build for production**
   ```bash
   npm run build
   ```

## 🔧 Configuration

### Required Environment Variables

#### Google Ads API (Required for production)
```env
GOOGLE_ADS_CLIENT_ID=800-216-1531
GOOGLE_ADS_CLIENT_SECRET=your-client-secret  # Generate via Google Cloud Console OAuth 2.0
GOOGLE_ADS_REFRESH_TOKEN=your-refresh-token  # Generate if needed - check if project requires it
GOOGLE_ADS_DEVELOPER_TOKEN=T3WOJXJ3JgRJ1Wg-1wd4Kg
```

#### OpenAI API (Required for AI features)
```env
OPENAI_API_KEY=your-openai-api-key
```

#### Security (Required for production)
```env
SECRET_KEY=your-secure-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
```

#### Database (Production)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/lane_mcp
```

### Optional Configuration

#### Redis (for caching and sessions)
```env
REDIS_URL=redis://localhost:6379/0
```

#### Feature Flags
```env
FEATURE_AI_CHAT=true
FEATURE_REAL_TIME_MONITORING=true
FEATURE_AUTO_OPTIMIZATION=true
FEATURE_WORKFLOW_APPROVAL=true
```

## 🚦 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Token refresh

### Dashboard APIs (JWT Protected)
- `GET /api/analytics/dashboard/{customer_id}` - Analytics dashboard data
- `GET /api/budget-pacing/summary/{customer_id}` - Budget pacing information
- `GET /api/performance/summary/{customer_id}` - Performance optimization data
- `GET /api/monitoring/status/{customer_id}` - Real-time monitoring status

### Campaign Management
- `GET /api/campaigns` - List campaigns
- `POST /api/campaigns/create` - Create new campaign
- `GET /api/campaigns/{campaign_id}` - Get campaign details

### AI Agent
- `POST /api/ai/chat` - Chat with AI agent
- `POST /api/ai/generate-campaign` - Generate campaign brief

### Google Ads Integration
- `GET /api/google-ads/accounts` - List accessible accounts
- `GET /api/google-ads/accounts/{account_id}/campaigns` - Get account campaigns

## 🔍 Development Mode

The application includes comprehensive development features:

### Mock Data
- Google Ads API calls use mock data when credentials aren't configured
- AI responses can be mocked for testing without OpenAI API usage

### Debug Features
- Detailed logging with configurable levels
- Database query logging (set `DATABASE_ECHO=true`)
- Request/response logging for API debugging

### Auto-Setup
- Automatic database initialization
- Default admin user creation in development
- Sample data generation for testing

## 🚀 Production Deployment

### Docker Deployment (Recommended)
```bash
# Build and run with Docker Compose
cd docker && docker-compose up --build
```

### Manual Deployment
1. Set `ENVIRONMENT=production` in `.env`
2. Configure production database (PostgreSQL recommended)
3. Set secure secret keys
4. Configure Google Ads and OpenAI API credentials
5. Use a production WSGI server (Gunicorn recommended)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 src.main_production:app
```

## 🧪 Testing

### Backend Tests
```bash
python -m pytest tests/
```

### Frontend Tests
```bash
npm test
```

### Integration Tests
```bash
npm run test:integration
```

## 📊 Monitoring and Logging

### Application Logs
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- File-based logging with rotation
- Structured logging for production monitoring

### Health Checks
- `GET /health` - Application health status
- `GET /api/health` - API health with service status
- Database connectivity checks
- External service availability checks

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication with configurable expiration
- Bcrypt password hashing with configurable salt rounds
- Role-based access control (RBAC)
- Account-level access restrictions

### API Security
- CORS configuration for cross-origin requests
- Rate limiting (configurable)
- Input validation and sanitization
- SQL injection prevention through ORM

### Data Protection
- Sensitive data encryption at rest
- Secure session management
- Environment variable protection
- API key rotation support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `/docs` folder
- Review the configuration examples in `.env.example`

## 🔄 Version History

### v1.0.0 (Current)
- ✅ Fixed critical authentication inconsistencies
- ✅ Implemented environment-based configuration
- ✅ Resolved missing service dependencies
- ✅ Added comprehensive error handling
- ✅ Created production-ready deployment configuration
- ✅ Standardized API response formats
- ✅ Added health check endpoints
- ✅ Implemented proper logging system

### Next Planned Features
- [ ] Unit and integration test coverage
- [ ] API documentation with OpenAPI/Swagger
- [ ] Performance monitoring and alerting
- [ ] Advanced campaign optimization algorithms
- [ ] Multi-tenant architecture support