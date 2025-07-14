# 🚀 Lane MCP Deployment Action Plan

## Current Status

### ✅ What You Have:
- **Developer Token**: `T3WOJXJ3JgRJ1Wg-1wd4Kg`
- **Client ID**: `800-216-1531`
- **Project Structure**: Complete and ready
- **Deployment Configuration**: `render.yaml` created
- **Environment Templates**: `.env` and `.env.example` created

### ❌ What You Need:
1. **Google Ads Client Secret** (from Google Cloud Console)
2. **Google Ads Refresh Token** (YES, you need this!)
3. **OpenRouter API Key** (for AI features)
4. **Secure Random Keys** (for SECRET_KEY and JWT_SECRET_KEY)

## 🎯 Immediate Action Items

### 1. Generate Google Ads Client Secret (5 minutes)

**Why you need it**: The Client Secret is like a password that authenticates your application with Google's servers.

**Steps**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Ads API:
   - APIs & Services → Library → Search "Google Ads API" → Enable
4. Create OAuth 2.0 credentials:
   - APIs & Services → Credentials → Create Credentials → OAuth Client ID
   - Application type: **Web application**
   - Name: "Lane MCP Production"
   - Authorized redirect URIs:
     - `http://localhost:8080` (for generating refresh token)
     - `https://your-app.onrender.com/api/auth/google/callback` (for production)
5. Download the JSON file and find the `client_secret` value

### 2. Generate Refresh Token (10 minutes)

**Why you need it**: The refresh token allows your app to access Google Ads API on behalf of your account without requiring login each time. It's absolutely required!

**Easy Method** - Run the script I created:
```bash
cd scripts
chmod +x generate_google_ads_credentials.py
python generate_google_ads_credentials.py YOUR_CLIENT_SECRET_HERE
```

The script will:
- Open a browser for you to authorize
- Automatically capture the authorization code
- Generate your refresh token
- Save all credentials to a file

### 3. Get OpenRouter API Key (2 minutes)

**Why you need it**: Powers the AI chat features in your application.

1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up/Login
3. Go to [API Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Copy the key

### 4. Generate Security Keys (1 minute)

Run these commands:
```bash
# Generate SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY  
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

## 📝 Update Your .env File

After completing the above steps, update your `.env` file:

```env
# Security Keys (use the generated values)
SECRET_KEY=your-generated-secret-key-here
JWT_SECRET_KEY=your-generated-jwt-secret-key-here

# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=T3WOJXJ3JgRJ1Wg-1wd4Kg
GOOGLE_ADS_CLIENT_ID=800-216-1531
GOOGLE_ADS_CLIENT_SECRET=your-client-secret-from-google-cloud
GOOGLE_ADS_REFRESH_TOKEN=your-generated-refresh-token

# OpenRouter API
OPENROUTER_API_KEY=your-openrouter-api-key
```

## 🚀 Deploy to Render

### Step 1: Prepare Your Repository
```bash
# Make sure .env is in .gitignore (it already is)
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Review the configuration
6. Add environment variables in Render dashboard:
   - All the values from your `.env` file
   - Render will auto-generate `SECRET_KEY` and `JWT_SECRET_KEY` if you want
   - Database URL will be auto-set when PostgreSQL is created

### Step 3: Set Environment Variables in Render
In the Render dashboard for your service:
1. Go to Environment tab
2. Add these variables:
   ```
   GOOGLE_ADS_DEVELOPER_TOKEN=T3WOJXJ3JgRJ1Wg-1wd4Kg
   GOOGLE_ADS_CLIENT_ID=800-216-1531
   GOOGLE_ADS_CLIENT_SECRET=[your-value]
   GOOGLE_ADS_REFRESH_TOKEN=[your-value]
   OPENROUTER_API_KEY=[your-value]
   ```

## 🧪 Test Your Deployment

### 1. Local Testing First
```bash
# Test your setup locally
source venv/bin/activate
python src/main_production.py
```

Visit `http://localhost:5000/api/health` to verify it's working.

### 2. Test Google Ads Connection
```python
# Create test_setup.py
from dotenv import load_dotenv
import os

load_dotenv()

print("Checking environment variables...")
required_vars = [
    'GOOGLE_ADS_DEVELOPER_TOKEN',
    'GOOGLE_ADS_CLIENT_ID', 
    'GOOGLE_ADS_CLIENT_SECRET',
    'GOOGLE_ADS_REFRESH_TOKEN',
    'OPENROUTER_API_KEY'
]

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {'*' * 10} (set)")
    else:
        print(f"❌ {var}: NOT SET")
```

## 🎉 You're Almost There!

**Estimated Time**: 20-30 minutes total

1. **Right Now** (10 min): Get Google Cloud credentials
2. **Next** (5 min): Run the refresh token script
3. **Then** (2 min): Get OpenRouter API key
4. **Finally** (10 min): Deploy to Render

## ⚠️ Important Notes

1. **YES, you need the refresh token!** It's not optional - the Google Ads API requires it for authentication.

2. **Client ID Format**: Your Client ID `800-216-1531` looks like a customer ID format. Make sure this is actually the OAuth2 Client ID from Google Cloud Console, not your Google Ads account ID.

3. **Developer Token Access**: Make sure your developer token has at least "Test Account Access" for initial testing.

## 🆘 Troubleshooting

### "Invalid Client" Error
- Your Client ID might be wrong. It should look like: `123456789-abcdef.apps.googleusercontent.com`
- The format `800-216-1531` looks like a Google Ads Customer ID, not a Client ID

### "Refresh Token Invalid"
- Make sure you included the correct scopes when generating
- The token might have expired - regenerate it

### Can't Enable Google Ads API
- You need a Google Cloud Project with billing enabled
- The API might take a few minutes to activate after enabling

## 📞 Next Steps After Deployment

1. Test all API endpoints
2. Verify database migrations ran successfully
3. Check that frontend can connect to backend
4. Monitor logs for any errors
5. Set up custom domain (optional)

Good luck with your deployment! 🚀