# Development Guide

## Getting Started

This guide will help you set up the development environment and understand the codebase structure for contributing to the Lane MCP Platform.

## Prerequisites

### Required Software
- **Python 3.11+**: Core backend language
- **Node.js 20+**: Frontend development
- **PostgreSQL 14+**: Primary database
- **Redis 6+**: Caching and session storage
- **Git**: Version control

### Development Tools
- **VS Code** or **PyCharm**: Recommended IDEs
- **Postman**: API testing
- **pgAdmin**: Database management
- **Redis CLI**: Cache debugging

## Project Structure

```
lane_mcp_platform/
├── enterprise_backend/          # Backend application
│   └── core_api/               # Main API service
│       ├── src/                # Source code
│       │   ├── config.py       # Configuration management
│       │   ├── database.py     # Database setup
│       │   ├── main.py         # Application entry point
│       │   ├── middleware.py   # Custom middleware
│       │   ├── models/         # Database models
│       │   ├── routes/         # API endpoints
│       │   ├── services/       # Business logic
│       │   └── utils/          # Utility functions
│       ├── requirements.txt    # Python dependencies
│       ├── .env.example       # Environment template
│       └── .env               # Local environment
├── mcp_dashboard/              # Frontend application
│   ├── src/                   # React source code
│   │   ├── App.jsx            # Main component
│   │   ├── config/            # Configuration
│   │   ├── components/        # React components
│   │   └── hooks/             # Custom hooks
│   ├── package.json           # Node dependencies
│   ├── .env.example          # Environment template
│   └── .env.local            # Local environment
├── README.md                  # Main documentation
├── API_DOCUMENTATION.md       # API reference
└── .gitignore                # Git ignore rules
```

## Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd lane_mcp_platform
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
cd enterprise_backend/core_api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

#### Setup Database
```bash
# Create PostgreSQL database
createdb lane_mcp_development

# Run migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

#### Start Backend Server
```bash
python src/main.py
```

The backend will be available at `http://localhost:5001`

### 3. Frontend Setup

#### Install Dependencies
```bash
cd ../../mcp_dashboard
pnpm install
```

#### Configure Environment
```bash
cp .env.example .env.local
# Edit .env.local with your settings
```

#### Start Development Server
```bash
pnpm run dev
```

The frontend will be available at `http://localhost:5173`

## Development Workflow

### 1. Feature Development

#### Create Feature Branch
```bash
git checkout -b feature/campaign-optimization
```

#### Make Changes
- Follow coding standards
- Write tests for new functionality
- Update documentation as needed

#### Test Changes
```bash
# Backend tests
cd enterprise_backend/core_api
python -m pytest tests/

# Frontend tests
cd mcp_dashboard
pnpm run test
```

#### Commit Changes
```bash
git add .
git commit -m "feat: add campaign optimization algorithm

- Implement budget pacing optimization
- Add performance threshold monitoring
- Update campaign model with optimization history"
```

### 2. Code Review Process

#### Submit Pull Request
- Create detailed PR description
- Include screenshots for UI changes
- Reference related issues

#### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass and coverage is maintained
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact is acceptable

### 3. Deployment

#### Staging Deployment
```bash
# Deploy to staging environment
git push origin feature/campaign-optimization
# Automated deployment via CI/CD
```

#### Production Deployment
```bash
# Merge to main branch
git checkout main
git merge feature/campaign-optimization
git push origin main
# Automated production deployment
```

## Coding Standards

### Python (Backend)

#### Style Guide
- Follow **PEP 8** style guide
- Use **Black** for code formatting
- Use **isort** for import sorting
- Maximum line length: 88 characters

#### Code Organization
```python
"""
Module docstring explaining purpose and usage
"""

# Standard library imports
import os
import json
from datetime import datetime

# Third-party imports
from flask import Flask, request
from sqlalchemy import Column, String

# Local imports
from src.models.base import BaseModel
from src.utils.validation import validate_email

class UserService:
    """
    Service class for user management
    
    Handles user creation, authentication, and profile management
    with comprehensive validation and security measures.
    """
    
    def __init__(self, db_session):
        """Initialize service with database session"""
        self.db = db_session
    
    def create_user(self, email: str, password: str) -> User:
        """
        Create new user account
        
        Args:
            email: User email address
            password: Plain text password (will be hashed)
            
        Returns:
            User: Created user instance
            
        Raises:
            ValidationError: If email or password is invalid
            DuplicateError: If email already exists
        """
        # Implementation here
        pass
```

#### Testing Standards
```python
import pytest
from unittest.mock import Mock, patch

class TestUserService:
    """Test suite for UserService"""
    
    @pytest.fixture
    def user_service(self):
        """Create UserService instance for testing"""
        mock_db = Mock()
        return UserService(mock_db)
    
    def test_create_user_success(self, user_service):
        """Test successful user creation"""
        # Arrange
        email = "test@example.com"
        password = "secure_password"
        
        # Act
        user = user_service.create_user(email, password)
        
        # Assert
        assert user.email == email
        assert user.password_hash != password  # Should be hashed
```

### JavaScript/React (Frontend)

#### Style Guide
- Use **ESLint** with Airbnb config
- Use **Prettier** for formatting
- Prefer **functional components** with hooks
- Use **TypeScript** for type safety

#### Component Structure
```jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Button } from '@/components/ui/button';
import { useApi } from '@/hooks/useApi';

/**
 * CampaignCard component for displaying campaign information
 * 
 * @param {Object} props - Component props
 * @param {Object} props.campaign - Campaign data object
 * @param {Function} props.onEdit - Callback for edit action
 * @param {Function} props.onDelete - Callback for delete action
 */
const CampaignCard = ({ campaign, onEdit, onDelete }) => {
  const [isLoading, setIsLoading] = useState(false);
  const { updateCampaign } = useApi();

  /**
   * Handle campaign status toggle
   */
  const handleStatusToggle = async () => {
    setIsLoading(true);
    try {
      const newStatus = campaign.status === 'active' ? 'paused' : 'active';
      await updateCampaign(campaign.id, { status: newStatus });
    } catch (error) {
      console.error('Failed to update campaign status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="campaign-card">
      <h3>{campaign.name}</h3>
      <p>Status: {campaign.status}</p>
      <p>Budget: ${campaign.budget_amount}</p>
      
      <div className="actions">
        <Button onClick={onEdit}>Edit</Button>
        <Button 
          onClick={handleStatusToggle} 
          disabled={isLoading}
          variant={campaign.status === 'active' ? 'secondary' : 'primary'}
        >
          {campaign.status === 'active' ? 'Pause' : 'Activate'}
        </Button>
        <Button onClick={onDelete} variant="destructive">
          Delete
        </Button>
      </div>
    </div>
  );
};

CampaignCard.propTypes = {
  campaign: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    status: PropTypes.string.isRequired,
    budget_amount: PropTypes.number.isRequired,
  }).isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
};

export default CampaignCard;
```

## Database Management

### Migrations

#### Create Migration
```bash
flask db migrate -m "Add campaign optimization fields"
```

#### Review Migration
```python
# Check generated migration file
# migrations/versions/xxx_add_campaign_optimization_fields.py

def upgrade():
    # Add new columns
    op.add_column('campaigns', sa.Column('optimization_score', sa.Float(), nullable=True))
    op.add_column('campaigns', sa.Column('last_optimized_at', sa.DateTime(), nullable=True))

def downgrade():
    # Remove columns
    op.drop_column('campaigns', 'last_optimized_at')
    op.drop_column('campaigns', 'optimization_score')
```

#### Apply Migration
```bash
flask db upgrade
```

### Model Relationships

```python
class Campaign(db.Model):
    """Campaign model with relationships"""
    
    # Foreign keys
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='campaigns')
    performance_data = db.relationship('CampaignPerformance', backref='campaign', cascade='all, delete-orphan')
    
    def to_dict(self, include_performance=False):
        """Convert to dictionary with optional performance data"""
        data = {
            'id': self.id,
            'name': self.name,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
        }
        
        if include_performance and self.performance_data:
            data['performance'] = [p.to_dict() for p in self.performance_data]
        
        return data
```

## API Development

### Endpoint Structure

```python
from flask import Blueprint, request, jsonify
from src.utils import require_permission, validate_json_request, APIResponse
from src.models.campaign import Campaign

campaigns_bp = Blueprint('campaigns', __name__)

@campaigns_bp.route('/', methods=['GET'])
@require_permission('campaigns.read')
def list_campaigns():
    """
    List campaigns with filtering and pagination
    
    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20)
        status (str): Filter by status
        search (str): Search in campaign names
    
    Returns:
        JSON response with campaigns list and pagination info
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status = request.args.get('status')
    search = request.args.get('search')
    
    # Build query
    query = Campaign.query
    
    if status:
        query = query.filter(Campaign.status == status)
    
    if search:
        query = query.filter(Campaign.name.ilike(f'%{search}%'))
    
    # Paginate results
    pagination = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # Format response
    campaigns = [campaign.to_dict() for campaign in pagination.items]
    
    return APIResponse.paginated(
        data=campaigns,
        page=page,
        per_page=per_page,
        total=pagination.total
    )

@campaigns_bp.route('/', methods=['POST'])
@require_permission('campaigns.create')
@validate_json_request(
    required_fields=['name', 'campaign_type', 'budget_amount'],
    optional_fields=['description', 'target_audience', 'keywords']
)
def create_campaign():
    """
    Create new campaign
    
    Request Body:
        name (str): Campaign name
        campaign_type (str): Type of campaign
        budget_amount (float): Daily budget amount
        description (str, optional): Campaign description
        target_audience (str, optional): Target audience description
        keywords (list, optional): List of keywords
    
    Returns:
        JSON response with created campaign data
    """
    data = request.get_json()
    
    # Create campaign
    campaign = Campaign(
        name=data['name'],
        campaign_type=data['campaign_type'],
        budget_amount=data['budget_amount'],
        description=data.get('description'),
        target_audience=data.get('target_audience'),
        keywords=data.get('keywords', []),
        user_id=g.current_user.id
    )
    
    db.session.add(campaign)
    db.session.commit()
    
    return APIResponse.created(
        data=campaign.to_dict(),
        message="Campaign created successfully"
    )
```

## Testing

### Backend Testing

#### Unit Tests
```python
# tests/test_services/test_campaign_service.py
import pytest
from unittest.mock import Mock, patch
from src.services.campaign_service import CampaignService
from src.models.campaign import Campaign, CampaignStatus

class TestCampaignService:
    """Test suite for CampaignService"""
    
    @pytest.fixture
    def campaign_service(self):
        """Create CampaignService instance"""
        return CampaignService()
    
    @pytest.fixture
    def sample_campaign_data(self):
        """Sample campaign data for testing"""
        return {
            'name': 'Test Campaign',
            'campaign_type': 'SEARCH',
            'budget_amount': 1000.00,
            'target_audience': 'Tech enthusiasts'
        }
    
    def test_create_campaign_success(self, campaign_service, sample_campaign_data):
        """Test successful campaign creation"""
        # Act
        campaign = campaign_service.create_campaign(sample_campaign_data)
        
        # Assert
        assert campaign.name == sample_campaign_data['name']
        assert campaign.status == CampaignStatus.DRAFT
        assert campaign.budget_amount == sample_campaign_data['budget_amount']
    
    @patch('src.services.campaign_service.google_ads_client')
    def test_sync_with_google_ads(self, mock_google_client, campaign_service):
        """Test Google Ads synchronization"""
        # Arrange
        mock_google_client.get_campaign.return_value = {
            'id': 'google_123',
            'status': 'ENABLED',
            'impressions': 1000,
            'clicks': 50
        }
        
        campaign = Campaign(id='test_123', google_campaign_id='google_123')
        
        # Act
        result = campaign_service.sync_with_google_ads(campaign)
        
        # Assert
        assert result['impressions'] == 1000
        assert result['clicks'] == 50
        mock_google_client.get_campaign.assert_called_once_with('google_123')
```

#### Integration Tests
```python
# tests/test_api/test_campaigns.py
import pytest
from src.main import create_app
from src.database import db
from src.models.user import User
from src.models.campaign import Campaign

class TestCampaignsAPI:
    """Integration tests for campaigns API"""
    
    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authentication headers"""
        # Create test user
        user = User(email='test@example.com', password='password')
        db.session.add(user)
        db.session.commit()
        
        # Login and get token
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password'
        })
        token = response.json['data']['access_token']
        
        return {'Authorization': f'Bearer {token}'}
    
    def test_create_campaign(self, client, auth_headers):
        """Test campaign creation endpoint"""
        # Arrange
        campaign_data = {
            'name': 'Test Campaign',
            'campaign_type': 'SEARCH',
            'budget_amount': 1000.00
        }
        
        # Act
        response = client.post(
            '/api/campaigns/',
            json=campaign_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        assert response.json['status'] == 'success'
        assert response.json['data']['name'] == campaign_data['name']
    
    def test_list_campaigns_with_pagination(self, client, auth_headers):
        """Test campaigns listing with pagination"""
        # Arrange - create test campaigns
        for i in range(25):
            campaign = Campaign(
                name=f'Campaign {i}',
                campaign_type='SEARCH',
                budget_amount=100.00
            )
            db.session.add(campaign)
        db.session.commit()
        
        # Act
        response = client.get(
            '/api/campaigns/?page=2&per_page=10',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        assert len(response.json['data']) == 10
        assert response.json['pagination']['page'] == 2
        assert response.json['pagination']['total'] == 25
```

### Frontend Testing

#### Component Tests
```jsx
// src/components/__tests__/CampaignCard.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import CampaignCard from '../CampaignCard';

// Mock the API hook
vi.mock('@/hooks/useApi', () => ({
  useApi: () => ({
    updateCampaign: vi.fn().mockResolvedValue({}),
  }),
}));

describe('CampaignCard', () => {
  const mockCampaign = {
    id: '123',
    name: 'Test Campaign',
    status: 'active',
    budget_amount: 1000,
  };

  const mockProps = {
    campaign: mockCampaign,
    onEdit: vi.fn(),
    onDelete: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders campaign information', () => {
    render(<CampaignCard {...mockProps} />);
    
    expect(screen.getByText('Test Campaign')).toBeInTheDocument();
    expect(screen.getByText('Status: active')).toBeInTheDocument();
    expect(screen.getByText('Budget: $1000')).toBeInTheDocument();
  });

  test('calls onEdit when edit button is clicked', () => {
    render(<CampaignCard {...mockProps} />);
    
    fireEvent.click(screen.getByText('Edit'));
    
    expect(mockProps.onEdit).toHaveBeenCalledTimes(1);
  });

  test('toggles campaign status when pause/activate button is clicked', async () => {
    const { useApi } = await import('@/hooks/useApi');
    const mockUpdateCampaign = useApi().updateCampaign;
    
    render(<CampaignCard {...mockProps} />);
    
    fireEvent.click(screen.getByText('Pause'));
    
    await waitFor(() => {
      expect(mockUpdateCampaign).toHaveBeenCalledWith('123', { status: 'paused' });
    });
  });
});
```

## Performance Optimization

### Backend Optimization

#### Database Queries
```python
# Efficient query with joins and pagination
def get_campaigns_with_performance(user_id, page=1, per_page=20):
    """Get campaigns with performance data efficiently"""
    return db.session.query(Campaign)\
        .options(
            joinedload(Campaign.performance_data),
            joinedload(Campaign.user)
        )\
        .filter(Campaign.user_id == user_id)\
        .order_by(Campaign.created_at.desc())\
        .paginate(page=page, per_page=per_page)

# Use database indexes for common queries
class Campaign(db.Model):
    # Add indexes for frequently queried fields
    __table_args__ = (
        db.Index('idx_campaign_user_status', 'user_id', 'status'),
        db.Index('idx_campaign_created_at', 'created_at'),
        db.Index('idx_campaign_google_id', 'google_campaign_id'),
    )
```

#### Caching
```python
from flask_caching import Cache
import redis

# Configure Redis cache
cache = Cache()
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@cache.memoize(timeout=300)  # Cache for 5 minutes
def get_campaign_performance(campaign_id):
    """Get campaign performance with caching"""
    return CampaignPerformance.query.filter_by(
        campaign_id=campaign_id
    ).order_by(CampaignPerformance.date.desc()).first()

# Cache expensive calculations
def calculate_optimization_score(campaign_id):
    """Calculate optimization score with caching"""
    cache_key = f"optimization_score:{campaign_id}"
    
    # Try to get from cache
    score = redis_client.get(cache_key)
    if score:
        return float(score)
    
    # Calculate score (expensive operation)
    score = perform_complex_calculation(campaign_id)
    
    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, str(score))
    
    return score
```

### Frontend Optimization

#### Code Splitting
```jsx
// Lazy load components
import { lazy, Suspense } from 'react';

const CampaignDashboard = lazy(() => import('./components/CampaignDashboard'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));

function App() {
  return (
    <Router>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/campaigns" element={<CampaignDashboard />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Routes>
      </Suspense>
    </Router>
  );
}
```

#### Memoization
```jsx
import { memo, useMemo, useCallback } from 'react';

const CampaignList = memo(({ campaigns, onCampaignUpdate }) => {
  // Memoize expensive calculations
  const totalBudget = useMemo(() => {
    return campaigns.reduce((sum, campaign) => sum + campaign.budget_amount, 0);
  }, [campaigns]);

  // Memoize event handlers
  const handleCampaignEdit = useCallback((campaignId) => {
    onCampaignUpdate(campaignId, { status: 'editing' });
  }, [onCampaignUpdate]);

  return (
    <div>
      <h2>Total Budget: ${totalBudget}</h2>
      {campaigns.map(campaign => (
        <CampaignCard
          key={campaign.id}
          campaign={campaign}
          onEdit={() => handleCampaignEdit(campaign.id)}
        />
      ))}
    </div>
  );
});
```

## Security Guidelines

### Authentication & Authorization

```python
# Secure password hashing
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class User(db.Model):
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(
            password, 
            method='pbkdf2:sha256:100000'  # Strong hashing
        )
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

# Secure JWT tokens
def generate_jwt_token(user_id):
    """Generate secure JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
        'jti': secrets.token_urlsafe(32)  # Unique token ID
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
```

### Input Validation

```python
from marshmallow import Schema, fields, validate, ValidationError

class CampaignSchema(Schema):
    """Campaign validation schema"""
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=100),
            validate.Regexp(r'^[a-zA-Z0-9\s\-_]+$')  # Alphanumeric only
        ]
    )
    budget_amount = fields.Float(
        required=True,
        validate=validate.Range(min=1.0, max=1000000.0)
    )
    keywords = fields.List(
        fields.Str(validate=validate.Length(max=50)),
        validate=validate.Length(max=100)
    )

def validate_campaign_data(data):
    """Validate campaign data"""
    schema = CampaignSchema()
    try:
        return schema.load(data)
    except ValidationError as err:
        raise ValidationError(f"Invalid campaign data: {err.messages}")
```

### SQL Injection Prevention

```python
# Use parameterized queries
def get_campaigns_by_status(status):
    """Safe query with parameters"""
    return db.session.execute(
        text("SELECT * FROM campaigns WHERE status = :status"),
        {'status': status}
    ).fetchall()

# Use SQLAlchemy ORM (automatically safe)
def search_campaigns(search_term):
    """Safe search using ORM"""
    return Campaign.query.filter(
        Campaign.name.ilike(f'%{search_term}%')
    ).all()
```

## Deployment

### Environment Configuration

#### Production Settings
```python
# config.py
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
```

#### Docker Configuration
```dockerfile
# Dockerfile for backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health/ || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.main:app"]
```

### Monitoring & Logging

```python
import logging
import structlog
from pythonjsonlogger import jsonlogger

# Configure structured logging
def configure_logging():
    """Configure application logging"""
    
    # JSON formatter for production
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    
    # File handler for errors
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler, error_handler]
    )

# Application metrics
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.before_request
def before_request():
    """Track request metrics"""
    g.start_time = time.time()

@app.after_request
def after_request(response):
    """Record request metrics"""
    duration = time.time() - g.start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
    REQUEST_DURATION.observe(duration)
    return response

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()
```

This development guide provides comprehensive information for contributing to the Lane MCP Platform. Follow these guidelines to maintain code quality, security, and performance standards.

