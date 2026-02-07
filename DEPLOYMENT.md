# Fair-Scan Deployment Guide

## Local Development

```bash
python run.py
# Visit: http://localhost:5000
```

## Docker Deployment (Recommended)

### Prerequisites
- Docker and Docker Compose installed

### Quick Deploy

```bash
cp .env.example .env
# Edit .env with your API keys

docker-compose up --build
# Visit: http://localhost:5000
```

## Heroku Deployment

### Prerequisites
- Account at heroku.com
- Heroku CLI installed

### Deploy Steps

```bash
# 1. Login to Heroku
heroku login

# 2. Create Heroku app
heroku create fair-scan-app

# 3. Add PostgreSQL database
heroku addons:create heroku-postgresql:hobby-dev -a fair-scan-app

# 4. Set environment variables
heroku config:set GEMINI_API_KEY=your-key -a fair-scan-app
heroku config:set MAIL_USERNAME=your-email -a fair-scan-app
heroku config:set MAIL_PASSWORD=your-password -a fair-scan-app
heroku config:set SECRET_KEY=your-secret-key -a fair-scan-app

# 5. Create Procfile
echo "web: python run.py" > Procfile

# 6. Deploy
git push heroku main

# 7. Initialize database
heroku run python -a fair-scan-app << 'EOF'
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
EOF
```

## AWS Elastic Beanstalk Deployment

### Prerequisites
- AWS Account
- AWS CLI and EB CLI installed

### Deploy Steps

```bash
# 1. Initialize Elastic Beanstalk
eb init -p python-3.10 fair-scan

# 2. Create environment
eb create fair-scan-prod

# 3. Set environment variables
eb setenv \
  GEMINI_API_KEY=your-key \
  MAIL_USERNAME=your-email \
  MAIL_PASSWORD=your-password \
  SECRET_KEY=your-secret-key

# 4. Deploy
eb deploy

# 5. Check status
eb status
eb logs
```

## DigitalOcean App Platform

### Deploy Using DigitalOcean Dashboard

1. Push code to GitHub
2. Go to DigitalOcean Dashboard → Apps
3. Click "Create App"
4. Connect your GitHub repository
5. Configure environment variables:
   - `GEMINI_API_KEY`
   - `MAIL_USERNAME`
   - `MAIL_PASSWORD`
   - `SECRET_KEY`
6. Deploy!

## Railway.app Deployment (Easiest!)

### One-Click Deploy

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "GitHub Repo"
4. Authorize and select fair-scan repo
5. Add environment variables
6. Deploy!

## PythonAnywhere Deployment

### Manual Setup

1. Sign up at pythonanywhere.com
2. Upload files via web UI or Git
3. Set up virtual environment
4. Configure WSGI app:
   ```python
   import sys
   path = '/home/yourusername/fair-scan'
   if path not in sys.path:
       sys.path.append(path)
   
   from run import app as application
   ```
5. Reload web app
6. Set environment variables in Web tab

## Cloud Run (Google Cloud) Deployment

```bash
# 1. Ensure Dockerfile exists (included in repo)

# 2. Build and deploy
gcloud run deploy fair-scan \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your-key,MAIL_USERNAME=your-email

# 3. Access your app
gcloud run services describe fair-scan --platform managed
```

## Azure App Service Deployment

```bash
# 1. Create resource group
az group create --name fair-scan-rg --location eastus

# 2. Create App Service Plan
az appservice plan create --name fair-scan-plan \
  --resource-group fair-scan-rg --sku B1 --is-linux

# 3. Create web app
az webapp create --resource-group fair-scan-rg \
  --plan fair-scan-plan --name fair-scan-app --runtime "PYTHON|3.10"

# 4. Deploy
az webapp deployment source config-zip --resource-group fair-scan-rg \
  --name fair-scan-app --src fair-scan.zip

# 5. Configure environment variables
az webapp config appsettings set --resource-group fair-scan-rg \
  --name fair-scan-app --settings GEMINI_API_KEY=your-key
```

## Production Checklist

### Before Going Live
- [ ] Change `FLASK_ENV` to `production`
- [ ] Generate strong `SECRET_KEY`: `python -c 'import secrets; print(secrets.token_hex(32))'`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up proper logging
- [ ] Configure email in production domain
- [ ] Test all features thoroughly
- [ ] Set up database backups
- [ ] Configure error monitoring (Sentry)
- [ ] Set up performance monitoring

### Security Hardening
```python
# In config.py for production:
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
PREFERRED_URL_SCHEME = 'https'
```

### Database Migration (SQLite → PostgreSQL)

```bash
# 1. Install PostgreSQL driver
pip install psycopg2-binary

# 2. Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost/fair_scan

# 3. Run migration
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
>>>     db.create_all()
```

## Scaling Considerations

### High Traffic Setup
1. Use load balancer (Nginx, HAProxy)
2. Run multiple app instances
3. Use PostgreSQL with connection pooling (PgBouncer)
4. Implement caching (Redis)
5. Use CDN for static files
6. Set up async job queue (Celery + Redis)

### Example Nginx Config
```nginx
upstream fair_scan {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    server_name fairscan.com;
    
    location / {
        proxy_pass http://fair_scan;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/fair-scan/app/static;
        expires 1d;
    }
}
```

## Monitoring & Logging

### Sentry (Error Tracking)
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1
)
```

### Datadog Integration
```bash
pip install ddtrace
DD_TRACE_ENABLED=true DD_SERVICE=fair-scan python run.py
```

## Cost Optimization

| Service | Est. Cost | Tier |
|---------|-----------|------|
| Railway.app | $5-50/mo | Starter |
| Heroku | $7/mo | Eco |
| DigitalOcean | $4-6/mo | Basic |
| AWS Free Tier | $0 | Free (1 year) |
| Azure Free | $0 | Free (1 year) |

## Support & Troubleshooting

### Common Deployment Issues

**Database connection failed**
- Check DATABASE_URL format
- Verify database is running
- Check firewall rules

**Email not sending**
- Verify MAIL credentials
- Check SMTP server connectivity
- Review mail logs

**Static files missing (404)**
- Run `flask collect-static` (if using CDN)
- Check STATIC_FOLDER path
- Verify file permissions

**Memory issues**
- Reduce worker count
- Enable caching
- Optimize database queries
- Consider serverless (AWS Lambda)

---

**Questions?** Check the main README.md or create an issue.
