## 🧪 Required Environment Variables for Testing

Based on the configuration files, here are the **minimum required environment variables** to test the Lane MCP application:

### ⚡ **Quick Start - Minimal Testing Setup**

Create a `.env` file in the root directory with these **essential variables**:

```bash
# Basic Application Settings
ENVIRONMENT=development
SECRET_KEY=test-secret-key-for-development
JWT_SECRET_KEY=test-jwt-secret-key-for-development

# Database (SQLite for easy testing)
DATABASE_URL=sqlite:///lane_mcp.db

# Basic Server Config
HOST=0.0.0.0
PORT=5000
DEBUG=true
```

### 🔧 **For Full Feature Testing**

Add these variables to enable all features:

```bash
# Google Ads API (for Google Ads features)
GOOGLE_ADS_CLIENT_ID=800-216-1531
GOOGLE_ADS_CLIENT_SECRET=your-google-ads-client-secret  # Generated via Google Cloud Console OAuth 2.0
GOOGLE_ADS_REFRESH_TOKEN=your-google-ads-refresh-token  # May be required - check if project calls for it
GOOGLE_ADS_DEVELOPER_TOKEN=T3WOJXJ3JgRJ1Wg-1wd4Kg

# OpenAI API (for AI chat features)
OPENAI_API_KEY=your-openai-api-key

# Optional: Redis (for caching)
REDIS_URL=redis://localhost:6379/0
```

### 📋 **Testing Scenarios**

#### **1. Basic Application Testing (No External APIs)**
```bash
# Minimum .env file
ENVIRONMENT=development
SECRET_KEY=test-secret-key
JWT_SECRET_KEY=test-jwt-secret-key
DATABASE_URL=sqlite:///lane_mcp.db
DEBUG=true
```

**What works:**
- ✅ Application startup
- ✅ Health check endpoints
- ✅ User authentication/registration
- ✅ Database operations
- ✅ Basic UI functionality

**What's mocked:**
- 🔄 Google Ads API calls return mock data
- 🔄 AI chat uses fallback responses

#### **2. Google Ads Testing**
Add these to enable real Google Ads integration:
```bash
GOOGLE_ADS_CLIENT_ID=800-216-1531
GOOGLE_ADS_CLIENT_SECRET=your-client-secret  # See note below
GOOGLE_ADS_REFRESH_TOKEN=your-refresh-token  # Generate if needed
GOOGLE_ADS_DEVELOPER_TOKEN=T3WOJXJ3JgRJ1Wg-1wd4Kg
```

**Note on Client Secret:** The Google Ads API secret needs to be generated through the Google Cloud Console:
1. Create a project in Google Cloud Console
2. Enable the Google Ads API
3. Generate OAuth 2.0 credentials
4. The client secret will be part of these credentials
5. Treat it like a password - keep it secure!

#### **3. AI Features Testing**
Add this to enable real AI chat:
```bash
OPENAI_API_KEY=sk-your-openai-api-key
```

### 🚀 **Quick Test Commands**

1. **Copy environment template:**
   ```bash
   cp config/env/.env.example .env
   ```

2. **Edit the .env file with your values**

3. **Install dependencies:**
   ```bash
   pip install -r config/requirements.txt
   ```

4. **Test application startup:**
   ```bash
   python src/main_production.py
   ```

5. **Test health endpoint:**
   ```bash
   curl http://localhost:5000/health
   ```

### 🔍 **Environment Variable Priority**

The application will work with different levels of configuration:

1. **Level 1 - Basic (App starts):**
   - `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`

2. **Level 2 - Google Ads (Real campaigns):**
   - Add Google Ads API credentials

3. **Level 3 - AI Features (Real chat):**
   - Add `OPENAI_API_KEY`

4. **Level 4 - Production (Full features):**
   - Add Redis, monitoring, email services

### ⚠️ **Important Notes**

- **Development Mode**: The app automatically uses mock data when API keys are missing
- **Database**: SQLite is used by default for easy testing (no PostgreSQL setup needed)
- **Security**: Development keys are fine for testing, but change them for production
- **Feature Flags**: All features are enabled by default, but will gracefully degrade without API keys
- **Google Ads Developer Token**: T3WOJXJ3JgRJ1Wg-1wd4Kg (provided)
- **Google Ads Client ID**: 800-216-1531 (provided)
- **Refresh Token**: Contact the team if you need a refresh token and the project requires it

### 🎯 **Recommended Testing Approach**

1. **Start with minimal config** (Level 1) to verify app startup
2. **Add Google Ads credentials** if you want to test campaign management
3. **Add OpenAI key** if you want to test AI chat features
4. **Use Docker** for full production-like testing

The application is designed to work gracefully with missing API keys, so you can test incrementally!