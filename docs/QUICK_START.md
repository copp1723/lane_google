# Lane MCP - Quick Start Guide 🚀

Get your Google Ads automation platform running in **5 minutes**!

## Option 1: Docker (Easiest) 🐳

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/lane_google.git
cd lane_google

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your Google Ads credentials
nano .env  # or use your favorite editor

# 4. Start everything with Docker Compose
docker-compose up -d

# 5. Check it's running
curl http://localhost:5000/api/health
```

Your platform is now running at `http://localhost:5000` 🎉

## Option 2: Local Setup 💻

```bash
# 1. Run the setup script
./setup_production.sh

# 2. Configure your credentials
cp .env.example .env
nano .env  # Add your Google Ads API credentials

# 3. Activate environment and run
source venv/bin/activate
python main_production.py
```

## First Steps 👋

### 1. Create Admin User
```bash
# During setup, create an admin account:
Admin email: admin@yourcompany.com
Admin password: [secure-password]
First name: Admin
Last name: User
```

### 2. Login via API
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "password": "your-password"
  }'
```

Save the returned token for API calls.

### 3. Create Your First Campaign
```bash
curl -X POST http://localhost:5000/api/campaigns/brief \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "E-commerce",
    "target_audience": "Adults 25-45 interested in tech",
    "budget": 5000,
    "goals": "Generate 500 conversions per month"
  }'
```

## What's Next? 📚

- **API Docs**: Visit `/api/docs` for full documentation
- **Dashboard**: Access the web UI at `http://localhost:5000`
- **Monitoring**: Check `/api/health` for system status
- **Logs**: View logs in `logs/app.log`

## Common Issues & Solutions 🔧

### Port Already in Use
```bash
# Change port in .env
PORT=8000
```

### Database Connection Failed
```bash
# For Docker users, wait for services to start:
docker-compose logs postgres

# For local users, ensure PostgreSQL is running:
sudo service postgresql start
```

### Redis Connection Failed
```bash
# Optional - the app works without Redis
# To enable caching, install Redis:
sudo apt-get install redis-server
redis-server
```

## Need Help? 🆘

- Check `README.md` for detailed documentation
- View logs: `tail -f logs/app.log`
- Health check: `curl http://localhost:5000/api/health?detailed=true`

---

**Ready to automate your Google Ads? Let's go! 🚀**