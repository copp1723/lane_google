#!/bin/bash
# Production Setup Script for Lane MCP
# Prepares the system for testing environment with real data

set -e  # Exit on any error

echo "🚀 Setting up Lane MCP for production testing..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "main_production.py" ]; then
    print_error "Please run this script from the lane_google project root directory"
    exit 1
fi

# Step 1: Check Python environment
print_step "Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python $PYTHON_VERSION found"

# Step 2: Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_step "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Step 3: Activate virtual environment and install dependencies
print_step "Installing dependencies..."
source venv/bin/activate

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Install essential packages if no requirements.txt
    pip install flask flask-sqlalchemy flask-migrate flask-cors \
                python-dotenv google-ads pyjwt bcrypt redis \
                requests python-dateutil sqlalchemy psycopg2-binary
fi
print_success "Dependencies installed"

# Step 4: Environment configuration
print_step "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Created .env from .env.example - PLEASE UPDATE WITH REAL VALUES"
    else
        print_error ".env.example file not found"
        exit 1
    fi
else
    print_success "Environment file already exists"
fi

# Step 5: Create necessary directories
print_step "Creating directories..."
mkdir -p logs
mkdir -p database
mkdir -p static
mkdir -p uploads
print_success "Directories created"

# Step 6: Run database migrations
print_step "Running database migrations..."
if [ -f "migrations/run_migrations.py" ]; then
    python migrations/run_migrations.py migrate
    print_success "Database migrations completed"
else
    print_warning "Migration script not found, skipping migrations"
fi

# Step 7: Generate secret keys if they're still default
print_step "Checking security configuration..."
if grep -q "your-secret-key-change-in-production" .env; then
    print_warning "Please update SECRET_KEY in .env file with a secure random string"
fi

if grep -q "your-jwt-secret-key-change-in-production" .env; then
    print_warning "Please update JWT_SECRET_KEY in .env file with a secure random string"
fi

# Step 8: Check Google Ads API configuration
print_step "Checking Google Ads API configuration..."
if grep -q "your-google-ads-client-id" .env; then
    print_warning "Google Ads API credentials need to be configured in .env"
    echo "   Required fields:"
    echo "   - GOOGLE_ADS_CLIENT_ID"
    echo "   - GOOGLE_ADS_CLIENT_SECRET"
    echo "   - GOOGLE_ADS_REFRESH_TOKEN"
    echo "   - GOOGLE_ADS_DEVELOPER_TOKEN"
    echo "   - GOOGLE_ADS_CUSTOMER_ID"
fi

# Step 9: Test configuration
print_step "Testing configuration..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from src.config.settings import settings
    print('✅ Configuration loaded successfully')
    print(f'Environment: {settings.environment}')
    print(f'Database: {settings.database.url}')
    if settings.is_google_ads_configured():
        print('✅ Google Ads API configured')
    else:
        print('⚠️  Google Ads API not configured')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    sys.exit(1)
"

# Step 10: Create initial admin user (optional)
read -p "Do you want to create an initial admin user? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Creating admin user..."
    python3 -c "
import sys
sys.path.insert(0, '.')
from src.models.user import User, UserRole, UserStatus
from database import db, init_database
from flask import Flask
import getpass

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_database(app)

with app.app_context():
    email = input('Admin email: ')
    password = getpass.getpass('Admin password: ')
    first_name = input('First name: ')
    last_name = input('Last name: ')
    
    # Check if user exists
    existing = User.query.filter_by(email=email).first()
    if existing:
        print('User already exists')
    else:
        user = User(
            email=email,
            username=email.split('@')[0],
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        db.session.add(user)
        db.session.commit()
        print(f'Admin user created: {email}')
"
fi

# Step 11: Final instructions
echo
print_success "🎉 Production setup completed!"
echo
echo "Next steps:"
echo "1. Update .env file with your actual API keys and secrets"
echo "2. Configure Google Ads API credentials"
echo "3. For production deployment, consider:"
echo "   - Using PostgreSQL instead of SQLite"
echo "   - Setting up Redis for caching"
echo "   - Configuring a reverse proxy (nginx)"
echo "   - Setting up SSL certificates"
echo "   - Implementing proper logging and monitoring"
echo
echo "To start the application:"
echo "  source venv/bin/activate"
echo "  python main_production.py"
echo
echo "To check migration status:"
echo "  python migrations/run_migrations.py status"
echo
print_warning "Remember to never commit your .env file to version control!"