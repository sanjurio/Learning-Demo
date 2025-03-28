# Deployment Guide

This document provides comprehensive instructions for deploying the AI Learning Platform to production environments.

## Overview

The AI Learning Platform can be deployed to various hosting services, including:

- **Render**: A cloud platform with easy PostgreSQL integration
- **PythonAnywhere**: Python-specific hosting with MySQL support
- **Heroku**: Cloud platform with add-on database support
- **Custom VPS**: Any server with Python and PostgreSQL

This guide primarily focuses on deployment to Render, which offers a straightforward deployment process with good free tier options.

## Prerequisites

Before deployment, ensure you have:

1. **Application Code**: Complete codebase with all dependencies
2. **Database**: PostgreSQL database for production
3. **Environment Variables**: API keys and configuration settings
4. **Static Files**: Optimized images and assets
5. **Dependencies**: All required packages listed in requirements.txt

## Preparing for Deployment

### 1. Create Requirements File

The application includes a `deployment_requirements.txt` file with all dependencies:

```
docx==0.2.4
email-validator==2.1.0.post1
Flask==3.0.0
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1
gunicorn==21.2.0
nltk==3.8.1
openai==1.3.7
Pillow==10.1.0
psycopg2-binary==2.9.9
PyOTP==2.9.0
PyPDF2==3.0.1
python-docx==1.0.1
qrcode==7.4.2
SQLAlchemy==2.0.23
Werkzeug==3.0.1
WTForms==3.1.1
```

### 2. Configure Procfile

The `Procfile` defines how to start the application:

```
web: gunicorn --bind 0.0.0.0:$PORT --reuse-port --workers 2 main:app
```

This configuration:
- Uses Gunicorn as the WSGI server
- Binds to the port provided by the hosting environment
- Uses 2 worker processes for concurrency
- Points to the `app` object in `main.py`

### 3. Prepare Environment Variables

The application requires several environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_SECRET_KEY`: Secret key for session encryption
- `OPENAI_API_KEY`: API key for OpenAI services
- `ENVIRONMENT`: Set to "production" for production settings

### 4. Configure Database URL

The application supports different database URLs for development and production:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
```

For Render, the PostgreSQL connection string is automatically provided as `DATABASE_URL`.

## Deployment to Render

### 1. Create a Render Account

Sign up at [render.com](https://render.com) if you don't have an account.

### 2. Create a PostgreSQL Database

1. In the Render dashboard, click "New" and select "PostgreSQL"
2. Configure your database:
   - Name: `ai-learning-platform-db` (or your preferred name)
   - Database: `ai_learning_platform`
   - User: Render will generate a secure username
   - Region: Choose the closest to your target audience
   - Plan: Select Free tier for testing or a paid plan for production
3. Click "Create Database"
4. Note the connection details (internal and external URLs)

### 3. Create a Web Service

1. In the Render dashboard, click "New" and select "Web Service"
2. Connect your repository (GitHub, GitLab, or Bitbucket)
3. Configure the service:
   - Name: `ai-learning-platform` (or your preferred name)
   - Environment: Python 3
   - Build Command: `pip install -r deployment_requirements.txt && python -m nltk.downloader punkt wordnet stopwords`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --reuse-port --workers 2 main:app`
   - Plan: Select Free tier for testing or a paid plan for production
4. Add Environment Variables:
   - `DATABASE_URL`: Use the Internal Database URL from your PostgreSQL database
   - `FLASK_SECRET_KEY`: Generate a secure random string
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ENVIRONMENT`: Set to "production"
5. Click "Create Web Service"

### 4. Deploy the Application

Render will automatically deploy your application based on the configuration.

### 5. Initial Database Setup

After deployment, you'll need to initialize the database:

1. Connect to the Render shell for your web service
2. Run the setup script: `python create_admin.py`
3. This will create an admin user and basic data

## Deployment to PythonAnywhere

### 1. Create a PythonAnywhere Account

Sign up at [pythonanywhere.com](https://www.pythonanywhere.com) if you don't have an account.

### 2. Upload Code

1. Upload your code using Git or the PythonAnywhere file uploader
2. Set up a virtual environment: `mkvirtualenv --python=python3.10 ai-learning-platform`
3. Install dependencies: `pip install -r deployment_requirements.txt`
4. Download NLTK data: `python -m nltk.downloader punkt wordnet stopwords`

### 3. Create a MySQL Database

1. Go to the Databases tab in PythonAnywhere
2. Create a MySQL database
3. Note the connection details

### 4. Configure Web App

1. Go to the Web tab in PythonAnywhere
2. Add a new web app
3. Select "Manual configuration" and Python 3.10
4. Configure the WSGI file:
   ```python
   import sys
   import os
   
   path = '/home/yourusername/ai-learning-platform'
   if path not in sys.path:
       sys.path.insert(0, path)
   
   os.environ['DATABASE_URL'] = 'mysql://username:password@host/dbname'
   os.environ['FLASK_SECRET_KEY'] = 'your-secret-key'
   os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'
   os.environ['ENVIRONMENT'] = 'production'
   
   from main import app as application
   ```
5. Set up static files mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/ai-learning-platform/static`

### 5. Initialize Database

1. Open a PythonAnywhere console
2. Activate your virtual environment: `workon ai-learning-platform`
3. Run the setup script: `python create_admin.py`

## Custom VPS Deployment

### 1. Prepare the Server

1. Install system dependencies:
   ```
   sudo apt update
   sudo apt install python3 python3-pip postgresql nginx
   ```

2. Create a PostgreSQL database:
   ```
   sudo -u postgres psql
   CREATE DATABASE ai_learning_platform;
   CREATE USER aiplatform WITH PASSWORD 'secure-password';
   GRANT ALL PRIVILEGES ON DATABASE ai_learning_platform TO aiplatform;
   \q
   ```

### 2. Deploy the Application

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-learning-platform.git
   cd ai-learning-platform
   ```

2. Set up a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r deployment_requirements.txt
   python -m nltk.downloader punkt wordnet stopwords
   ```

3. Configure environment variables:
   ```
   export DATABASE_URL="postgresql://aiplatform:secure-password@localhost/ai_learning_platform"
   export FLASK_SECRET_KEY="your-secure-secret-key"
   export OPENAI_API_KEY="your-openai-api-key"
   export ENVIRONMENT="production"
   ```

4. Initialize the database:
   ```
   python create_admin.py
   ```

### 3. Configure Systemd Service

Create a systemd service file to manage the application:

```
# /etc/systemd/system/ai-learning-platform.service
[Unit]
Description=AI Learning Platform
After=network.target postgresql.service

[Service]
User=your-username
WorkingDirectory=/path/to/ai-learning-platform
Environment="DATABASE_URL=postgresql://aiplatform:secure-password@localhost/ai_learning_platform"
Environment="FLASK_SECRET_KEY=your-secure-secret-key"
Environment="OPENAI_API_KEY=your-openai-api-key"
Environment="ENVIRONMENT=production"
ExecStart=/path/to/ai-learning-platform/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```
sudo systemctl enable ai-learning-platform
sudo systemctl start ai-learning-platform
```

### 4. Configure Nginx

Set up Nginx as a reverse proxy:

```
# /etc/nginx/sites-available/ai-learning-platform
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/ai-learning-platform/static;
        expires 30d;
    }
}
```

Enable the site and restart Nginx:
```
sudo ln -s /etc/nginx/sites-available/ai-learning-platform /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### 5. Set Up HTTPS

Use Certbot to configure HTTPS:
```
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Post-Deployment Tasks

After deploying to any platform:

### 1. Create Admin User

If not done during deployment:
```
python create_admin.py
```

This creates an admin user with:
- Email: admin@example.com
- Password: Admin123

**Important**: Change the default password immediately after first login.

### 2. Configure OpenAI API

1. Log in as admin
2. Navigate to API Keys in the admin interface
3. Enter your OpenAI API key
4. Test the connection

### 3. Create Basic Content

1. Create interest categories
2. Create initial courses
3. Add lessons to courses

### 4. Verify Functionality

Test all key features:
- User registration and login
- 2FA setup and verification
- Course access and enrollment
- Forum functionality
- Document analysis

## Monitoring and Maintenance

### Database Backups

Set up regular database backups:

- On Render: Automatic daily backups are included
- On PythonAnywhere: Schedule backup tasks
- On custom VPS: Configure pgdump with cron jobs

### Performance Monitoring

Monitor the application's performance:

- Use the hosting platform's monitoring tools
- Configure logging for error tracking
- Set up uptime monitoring services

### Updates and Maintenance

Maintain the application:

- Regularly update dependencies
- Apply security patches
- Monitor API usage and costs
- Review and optimize database performance

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify connection string format
   - Check network access and credentials
   - Ensure database user has necessary permissions

2. **Static Files Not Loading**:
   - Verify static file configuration
   - Check file permissions
   - Clear browser cache

3. **OpenAI API Issues**:
   - Verify API key is correct
   - Check API usage limits
   - Ensure network connectivity to OpenAI servers

4. **Application Errors**:
   - Check application logs
   - Verify environment variables
   - Ensure all dependencies are installed correctly