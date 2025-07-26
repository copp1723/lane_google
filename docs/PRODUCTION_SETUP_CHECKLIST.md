# Production Setup Checklist for Real Data & Client Testing

## 🔑 **CRITICAL MISSING COMPONENTS**

### 1. **Environment Configuration** (URGENT)
You need to create a `.env` file with real credentials:

```bash
# Copy from .env.example and fill in real values:
cp .env.example .env
```

**Required API Credentials:**
- ✅ **Google Ads API Setup** (Most Critical)
  - `GOOGLE_ADS_CLIENT_ID` - OAuth2 client ID
  - `GOOGLE_ADS_CLIENT_SECRET` - OAuth2 client secret  
  - `GOOGLE_ADS_REFRESH_TOKEN` - Long-lived refresh token
  - `GOOGLE_ADS_DEVELOPER_TOKEN` - Google Ads API developer token
  - `GOOGLE_ADS_CUSTOMER_ID` - Default customer account ID

- ✅ **OpenRouter API Key** (For AI Chat)
  - `OPENROUTER_API_KEY` - Get from https://openrouter.ai/

- ✅ **Security Keys**
  - `SECRET_KEY` - Generate strong random key
  - `JWT_SECRET_KEY` - Generate strong random key  
  - `PASSWORD_SALT` - Generate strong random salt

### 2. **Missing API Endpoints** (HIGH PRIORITY)

**Keyword Research API** - Currently missing:
```python
# Need to implement: /api/keywords/research
# Your frontend expects this but backend doesn't exist
```

**Client Account Management API** - Not implemented:
```python
# Need: /api/accounts/connect
# Need: /api/accounts/permissions  
# Need: /api/accounts/client-setup
```

### 3. **Database Setup** (HIGH PRIORITY)

**Run Database Migrations:**
```bash
# You have migrations but need to run them:
cd migrations
python run_migrations.py
```

**Missing Database Tables:**
- Client account linking
- User permissions  
- Account access controls
- Audit logs for client actions

### 4. **Google Ads API Authorization Flow** (CRITICAL)

You need to implement the OAuth2 flow for clients:

**Missing Components:**
- Client consent screen
- OAuth2 callback handling  
- Refresh token management
- Account linking interface

## 🚀 **IMPLEMENTATION PRIORITIES**

### **Phase 1: Core Infrastructure (Week 1)**
1. ✅ **Google Ads API Credentials Setup**
2. ✅ **Database Migration Execution** 
3. ✅ **Environment Configuration**
4. ✅ **Basic Client Authentication**

### **Phase 2: Client Onboarding (Week 2)**  
1. 🔄 **OAuth2 Authorization Flow**
2. 🔄 **Account Linking System**
3. 🔄 **Permission Management**
4. 🔄 **Client Dashboard Setup**

### **Phase 3: Real Data Integration (Week 3)**
1. 🔄 **Keyword Research API Implementation**
2. 🔄 **Real Campaign Data Fetching**
3. 🔄 **Client-Specific Data Filtering**
4. 🔄 **Performance Analytics**

## 📋 **DETAILED SETUP GUIDE**

### **Google Ads API Setup Process:**

1. **Apply for Google Ads API Access:**
   - Go to Google Ads API Center
   - Apply for developer token (can take 1-2 weeks)
   - Set up OAuth2 credentials in Google Cloud Console

2. **Generate OAuth2 Credentials:**
   ```bash
   # Create OAuth2 app in Google Cloud Console
   # Add redirect URIs for your application
   # Download client_secret.json
   ```

3. **Generate Refresh Token:**
   ```python
   # Run the OAuth2 flow once to get refresh token
   # Store refresh token securely in environment variables
   ```

### **Client Onboarding Flow:**

1. **Client Signs Up:**
   ```
   Client Account Creation → Email Verification → Initial Setup
   ```

2. **Google Ads Authorization:**
   ```
   OAuth2 Consent → Account Selection → Permission Grant → Token Storage
   ```

3. **Account Verification:**
   ```
   Verify Access → Fetch Account Details → Set Permissions → Ready for Use
   ```

## 🔧 **MISSING CODE IMPLEMENTATIONS**

### **1. Keyword Research API Endpoint:**
```python
# Need to create: src/api/keyword_research_api.py
@app.route('/api/keywords/research', methods=['POST'])
@login_required
def research_keywords():
    # Implement keyword research logic
    # Connect to Google Keyword Planner API
    # Return formatted keyword data
```

### **2. Client Account Linking:**
```python  
# Need to create: src/api/client_accounts_api.py
@app.route('/api/accounts/connect', methods=['POST'])
@login_required  
def connect_google_ads_account():
    # OAuth2 flow for Google Ads
    # Store account credentials
    # Verify account access
```

### **3. Real Data Filtering:**
```python
# Need to update: src/api/dashboard_apis.py
# Add customer_id filtering to all endpoints
# Ensure users only see their own data
# Implement proper access controls
```

## 🛡️ **SECURITY CONSIDERATIONS**

### **Production Security Checklist:**
- ✅ JWT token expiration (24 hours max)
- ✅ API rate limiting implementation
- ✅ Input validation and sanitization  
- ✅ HTTPS enforcement
- ✅ CORS configuration
- ✅ SQL injection prevention
- ✅ Client data isolation

### **Google Ads API Security:**
- ✅ Refresh token rotation
- ✅ Scope limitation (read-only for analytics)
- ✅ Account access verification
- ✅ Audit logging for all actions

## 🎯 **READY FOR CLIENT TESTING WHEN:**

### **Minimum Viable Product (MVP) Requirements:**
1. ✅ Real Google Ads account connection working
2. ✅ Client can see their actual campaign data  
3. ✅ Keyword research returns real data
4. ✅ AI chat generates actual campaign briefs
5. ✅ Workflow approval system functional
6. ✅ Basic performance analytics working

### **Testing Readiness Checklist:**
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] Google Ads API credentials working
- [ ] Client registration/login working
- [ ] Account linking functional
- [ ] Real data flowing through all components
- [ ] Error handling and fallbacks tested
- [ ] Security audit completed

## 🚨 **IMMEDIATE ACTION ITEMS**

### **This Week:**
1. **Set up Google Ads API developer account**
2. **Create .env file with real credentials**  
3. **Run database migrations**
4. **Implement keyword research API endpoint**
5. **Test Google Ads API connection**

### **Next Week:**
1. **Build client OAuth2 flow**
2. **Implement account linking system**
3. **Add client data filtering**
4. **Test with real client account**

## 💡 **QUICK WIN OPPORTUNITIES**

### **Demo-Ready in 2-3 Days:**
1. Use your own Google Ads account for initial testing
2. Hard-code single client credentials temporarily  
3. Implement basic keyword research with Google Keyword Planner
4. Test full workflow with real but limited data

### **Client-Ready in 1-2 Weeks:**
1. Full OAuth2 implementation
2. Multi-client support
3. Complete data isolation
4. Production security measures