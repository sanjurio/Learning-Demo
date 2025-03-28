# Deploying AI Learning Platform on Render

This guide will walk you through the steps to deploy this Flask application on Render.

## Prerequisites

1. A [Render](https://render.com/) account
2. A PostgreSQL database (you can use Render's PostgreSQL service or an external one like Neon)

## Step 1: Set Up the PostgreSQL Database

1. In Render dashboard, create a new PostgreSQL database
   - Go to "New" > "PostgreSQL"
   - Name your database (e.g., "ai-learning-platform-db")
   - Choose a plan
   - Click "Create Database"
2. Once created, note the following information:
   - Internal Database URL
   - External Database URL
   - Database name
   - Username
   - Password

Alternatively, if you're using Neon or another provider, make sure you have the connection details ready.

## Step 2: Deploy the Web Service

1. In Render dashboard, create a new Web Service
   - Go to "New" > "Web Service"
   - Connect your GitHub or GitLab repository
2. Configure the service:
   - **Name**: Choose a name (e.g., "ai-learning-platform")
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r deployment_requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --reuse-port main:app`

   Note: Alternatively, you can use the included Procfile which already has the correct start command.

3. Add Environment Variables:
   - `DATABASE_URL`: Your PostgreSQL connection string (from Step 1)
     - For Render PostgreSQL, use the Internal Database URL
     - Make sure the connection string is in this format: `postgresql://username:password@host:port/database_name`
   - `SESSION_SECRET`: A secure random string for Flask's secret key (e.g., generate one with `python -c "import secrets; print(secrets.token_hex(16))"`)

   These are the only environment variables required by the application.

4. Click "Create Web Service"

## Step 3: Ensure Database Migration

When your application first starts, it will automatically create the database tables.

## Step 4: Create an Admin User

After deployment, you'll need to create an admin user. You can do this by setting temporary environment variables and running the create_admin.py script:

1. In the Render dashboard, go to your Web Service
2. Click "Shell"
3. Run: `python create_admin.py`

This will create an admin user with email "admin@example.com" and password "Admin123".

## Step 5: Verify the Deployment

1. Navigate to your application URL (provided by Render)
2. Login with the admin credentials
3. Verify that all functionality works correctly

## Troubleshooting

If you encounter issues, check the following:

1. Render logs for your Web Service
2. Make sure all environment variables are correctly set
3. Check if the database connection is properly established
4. Ensure that the PostgreSQL extensions required by your application are available

## Security Considerations

1. Change the default admin password immediately after deployment
2. Set up proper SSL/TLS (Render handles this automatically)
3. Consider implementing rate limiting for sensitive endpoints
4. Make sure error handling doesn't expose sensitive information