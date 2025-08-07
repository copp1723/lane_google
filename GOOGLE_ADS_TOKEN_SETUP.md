# Google Ads Refresh Token Setup Guide

## Step-by-Step Instructions

### 1. Prerequisites
You need to have:
- ✅ Client ID: `YOUR_CLIENT_ID.apps.googleusercontent.com`
- ✅ Client Secret: `YOUR_CLIENT_SECRET`
- ✅ Developer Token: `YOUR_DEVELOPER_TOKEN`
- ✅ Customer ID: `YOUR_CUSTOMER_ID`

### 2. Generate the Refresh Token

Run this command:
```bash
python3.11 generate_refresh_token.py
```

### 3. What Will Happen:
1. A browser window will open automatically
2. You'll be prompted to log in to your Google account
3. Grant permissions to access Google Ads
4. The script will display your refresh token

### 4. Add to .env file:
```
GOOGLE_ADS_REFRESH_TOKEN=your-generated-refresh-token
```

## Alternative Method: OAuth Playground

If the script doesn't work, use Google's OAuth Playground:

1. Go to: https://developers.google.com/oauthplayground/
2. Select Google Ads API v17 scope
3. Use your own OAuth credentials
4. Generate the refresh token

## Troubleshooting

- **"redirect_uri_mismatch" error**: Add http://localhost to your OAuth client's authorized redirect URIs
- **"invalid_client" error**: Double-check your client ID and secret
- **Browser doesn't open**: Copy the URL from the terminal and open manually

## Security Note

Never commit your actual credentials to version control. Always use environment variables.