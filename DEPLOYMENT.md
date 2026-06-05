# Deployment Guide

## Production Deployment Checklist

Before deploying to production, ensure all items are completed:

### Security
- [ ] Change `SECRET_KEY` to a strong random value (min 32 characters)
- [ ] Change default admin password
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use HTTPS only
- [ ] Set secure cookie flags
- [ ] Implement CSRF protection
- [ ] Add rate limiting
- [ ] Configure CORS properly
- [ ] Use strong database passwords
- [ ] Enable SQL error suppression (no SQL in error messages)

### Database
- [ ] Create strong database password
- [ ] Set restrictive database user permissions
- [ ] Enable database backups
- [ ] Test database recovery procedures
- [ ] Monitor database performance

### Infrastructure
- [ ] Use environment variables for all secrets
- [ ] Configure reverse proxy (nginx/Apache)
- [ ] Set up SSL/TLS certificates (Let's Encrypt recommended)
- [ ] Configure firewall rules
- [ ] Enable logging and monitoring
- [ ] Set up alerting for errors and performance issues

### Application
- [ ] Run full test suite
- [ ] Load test the application
- [ ] Review all error messages (no sensitive info)
- [ ] Verify all input validation
- [ ] Check SQL injection protection
- [ ] Enable security headers
- [ ] Configure Content Security Policy (CSP)

### Deployment Methods

#### Option 1: Docker (Recommended)

1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=False

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
```

2. Build and run:
```bash
docker build -t flaskapp .
docker run -p 5000:5000 --env-file .env flaskapp
```

#### Option 2: Gunicorn + Nginx

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Run with Gunicorn:
```bash
gunicorn --workers 4 --bind 127.0.0.1:5000 run:app
```

3. Configure Nginx as reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Option 3: Cloud Platforms

**Azure App Service:**
```bash
az webapp up --resource-group mygroup --name myapp
```

**AWS Elastic Beanstalk:**
```bash
eb init -p python-3.11 myapp
eb create myapp-env
eb deploy
```

**Heroku:**
```bash
git push heroku main
```

### Monitoring & Logging

1. Enable application logging:
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

2. Set up centralized logging (e.g., ELK stack, Datadog, New Relic)

3. Monitor:
   - Response times
   - Error rates
   - Database performance
   - Server resources (CPU, memory, disk)

### Backup & Recovery

1. Automated database backups:
```bash
# MySQL backup
mysqldump -u user -p database > backup.sql

# Restore
mysql -u user -p database < backup.sql
```

2. Test recovery procedures regularly

3. Store backups in secure location (S3, Azure Blob, etc.)

### Scaling

For high traffic scenarios:
- Use load balancer
- Scale horizontally (multiple app instances)
- Implement database connection pooling
- Use Redis for caching/sessions
- Consider CDN for static files

### Performance Optimization

1. Enable gzip compression
2. Minify static assets
3. Use caching headers
4. Implement database query optimization
5. Monitor slow queries

### Health Checks

Add health check endpoint:
```python
@app.route('/health')
def health():
    try:
        conn = get_connection()
        if conn:
            conn.close()
            return {'status': 'healthy'}, 200
    except:
        pass
    return {'status': 'unhealthy'}, 503
```

## Support

For deployment issues, refer to:
- [Flask Deployment Documentation](https://flask.palletsprojects.com/en/3.0.x/deploying/)
- [Docker Documentation](https://docs.docker.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
