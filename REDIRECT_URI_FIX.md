# Fix Google OAuth Redirect URI

## Step 1: Add these URIs to Google Cloud Console

Go back to your OAuth client settings and click "Add URI" to add ALL of these:

### For Token Generation:
```
http://localhost
http://localhost:8080
http://localhost:5001
http://localhost:5174
http://127.0.0.1
http://127.0.0.1:8080
http://127.0.0.1:5001
http://127.0.0.1:5174
urn:ietf:wg:oauth:2.0:oob
```

### For OAuth Playground:
```
https://developers.google.com/oauthplayground
```

## Step 2: Save and Wait

After adding all these URIs:
1. Click "Save" at the bottom
2. **IMPORTANT**: Wait 5-10 minutes for changes to propagate

## Step 3: Generate Token (Two Options)

### Option A: Use OAuth Playground (Easier)
1. Go to https://developers.google.com/oauthplayground/
2. Click the gear ⚙️ → Use your own OAuth credentials
3. Enter your Client ID and Secret
4. Select Google Ads API scope
5. Authorize and get your refresh token

### Option B: Use Local Script
After the URIs are saved and propagated:
```bash
python3.11 generate_refresh_token.py
```

## Why This Happens

Google OAuth requires exact match between:
- The redirect URI in your request
- The redirect URIs configured in Google Cloud Console

The error occurs because the OAuth library is using a redirect URI that's not in your approved list.

## Quick Alternative

If you need a token RIGHT NOW and can't wait:

1. Temporarily change the OAuth client type:
   - Go to Google Cloud Console
   - Create a NEW OAuth 2.0 Client ID
   - Choose "Desktop app" instead of "Web application"
   - Use those credentials to generate the token
   - Desktop apps don't have redirect URI restrictions

2. Or use the token you already have (if it's still valid)