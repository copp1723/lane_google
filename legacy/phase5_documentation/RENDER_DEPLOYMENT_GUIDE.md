# Render Deployment Guide for Lane MCP

## 🚀 Quick Start Deployment Checklist

### 1. **Google Ads API Setup** (CRITICAL)

You've provided:
- ✅ Developer Token: `T3WOJXJ3JgRJ1Wg-1wd4Kg`
- ✅ Client ID: `800-216-1531`
- ❌ Client Secret: **NEEDS TO BE GENERATED**
- ❌ Refresh Token: **NEEDS TO BE GENERATED**

#### Setting up Google Cloud Console:

1. **Go to Google Cloud Console**:
   - Visit: https://console.cloud.google.com/
   - Create a new project or select existing one

2. **Enable Google Ads API**:
   ```
   APIs & Services → Library → Search "Google Ads API" → Enable
   ```

3. **Create OAuth 2.0 Credentials**:
   ```
   APIs & Services → Credentials → Create Credentials → OAuth Client ID
   - Application Type: Web application
   - Name: Lane MCP Production
   - Authorized redirect URIs:
     - https://your-app.onrender.com/api/auth/google/callback
     - http://localhost:5000/api/auth/google/callback (for testing)
   ```

4. **Download Client Secret**:
   - After creating, download the JSON file
   - Extract the `client_secret` value

### 2. **Generate OAuth Refresh Token**

Create and run this script locally to get your refresh token:

```python
# save as: generate_refresh_token.py
from google_auth_oauthlib.flow import Flow
from google.ads.googleads.client import GoogleAdsClient

# Replace with your actual values
CLIENT_ID = "800-216-1531"
CLIENT_SECRET = "YOUR_CLIENT_SECRET_FROM_GOOGLE_CLOUD"
REDIRECT_URI = "http://localhost:8080"

flow = Flow.from_client_config(
    {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    scopes=["https://www.googleapis.com/auth/adwords"]
)
flow.redirect_uri = REDIRECT_URI

print("Visit this URL to authorize:")
print(flow.authorization_url()[0])

code = input("Enter the authorization code: ")
flow.fetch_token(code=code)

print("\nYour refresh token is:")
print(flow.credentials.refresh_token)
```

### 3. **Security Keys Generation**

Run this command to generate secure keys:

```bash
# Generate SECRET_KEY
python -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print('JWT_SECRET_KEY:', secrets.token_urlsafe(32))"
```

### 4. **Render Environment Variables**

In your Render Dashboard, set these environment variables:

```bash
# Google Ads API (Required)
GOOGLE_ADS_DEVELOPER_TOKEN=T3WOJXJ3JgRJ1Wg-1wd4Kg
GOOGLE_ADS_CLIENT_ID=800-216-1531
GOOGLE_ADS_CLIENT_SECRET=<from Google Cloud Console>
GOOGLE_ADS_REFRESH_TOKEN=<from generate_refresh_token.py>

# Security Keys (Use generated values)
SECRET_KEY=<generated secure key>
JWT_SECRET_KEY=<generated secure key>

# OpenRouter API (Required for AI features)
OPENROUTER_API_KEY=<get from https://openrouter.ai/keys>

# Optional: Set your default customer ID
GOOGLE_ADS_LOGIN_CUSTOMER_ID=<your-mcc-account-id-if-using>
```

### 5. **Database Migration**

The render.yaml is configured to run migrations automatically during build.
If you need to run them manually:

```bash
cd migrations
python run_migrations.py
```

### 6. **Frontend Configuration**

Update your frontend environment configuration:

```javascript
// frontend/.env.production
VITE_API_BASE_URL=https://lane-mcp-api.onrender.com
```

## 📋 Pre-Deployment Checklist

- [ ] Google Cloud Console project created
- [ ] Google Ads API enabled
- [ ] OAuth 2.0 credentials created
- [ ] Client Secret obtained from Google Cloud
- [ ] Refresh Token generated using the script
- [ ] Secure keys generated for SECRET_KEY and JWT_SECRET_KEY
- [ ] OpenRouter API key obtained
- [ ] All environment variables set in Render Dashboard
- [ ] Database connection tested locally
- [ ] Frontend API URL configured

## 🚨 Common Issues and Solutions

### Issue: "Invalid Client" Error
**Solution**: Ensure your Client ID matches exactly what's in Google Cloud Console

### Issue: "Refresh Token Expired"
**Solution**: Re-run the refresh token generation script

### Issue: "Developer Token Not Approved"
**Solution**: 
- For testing, use test account
- For production, ensure developer token has basic or standard access

### Issue: Database Connection Failed
**Solution**: Render automatically provides DATABASE_URL when you create a PostgreSQL database

## 🔧 Testing Your Setup Locally

1. **Set up local environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

2. **Test Google Ads connection**:
   ```python
   # test_google_ads.py
   from google.ads.googleads.client import GoogleAdsClient
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   config = {
       "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
       "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
       "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
       "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
       "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
   }
   
   try:
       client = GoogleAdsClient.load_from_dict(config)
       print("✅ Google Ads API connection successful!")
   except Exception as e:
       print(f"❌ Error: {e}")
   ```

## 🚀 Deploy to Render

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Create New Web Service on Render**:
   - Go to https://dashboard.render.com/
   - New → Web Service
   - Connect your GitHub repository
   - Use `render.yaml` for configuration
   - Set environment variables in dashboard

3. **Monitor Deployment**:
   - Check build logs for any errors
   - Verify database migrations completed
   - Test API endpoints once deployed

## 📊 Post-Deployment Verification

1. **Health Check**:
   ```bash
   curl https://your-app.onrender.com/api/health
   ```

2. **Test Authentication**:
   ```bash
   curl -X POST https://your-app.onrender.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password"}'
   ```

3. **Verify Google Ads Connection**:
   ```bash
   curl https://your-app.onrender.com/api/google-ads/accounts \
     -H "Authorization: Bearer <your-jwt-token>"
   ```

## 🔒 Security Reminders

1. **Never commit `.env` file to Git**
2. **Rotate refresh tokens periodically**
3. **Use environment-specific API keys**
4. **Enable 2FA on Google Cloud Console**
5. **Monitor API usage and quotas**

## 📞 Support

If you encounter issues:
1. Check Render logs: Dashboard → Your Service → Logs
2. Verify all environment variables are set
3. Ensure Google Ads API access is approved
4. Test with a Google Ads test account first