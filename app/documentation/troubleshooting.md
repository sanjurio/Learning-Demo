# Troubleshooting Guide

This document provides solutions for common issues that may arise during development and deployment of the AI Learning Platform.

## Database Connection Issues

### PostgreSQL Connection Errors

**Error: `endpoint is disabled`**

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at "hostname", port 5432 failed: ERROR: Console request failed: endpoint is disabled
```

**Solution:**
1. For Neon or other serverless PostgreSQL providers, ensure your database instance is active
2. Check if your database has been suspended due to inactivity or billing issues
3. Verify your connection string is correct in the DATABASE_URL environment variable
4. Try restarting your database instance through the provider's dashboard

**Error: `password authentication failed`**

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL: password authentication failed for user "username"
```

**Solution:**
1. Double-check your database username and password
2. Ensure the DATABASE_URL environment variable has the correct credentials
3. Try resetting the user's password through your database provider
4. Check if the user has the necessary permissions

**Error: `database "dbname" does not exist`**

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL: database "dbname" does not exist
```

**Solution:**
1. Create the database using your provider's interface
2. Check the database name in your DATABASE_URL environment variable
3. Run `CREATE DATABASE dbname;` through a SQL client if you have admin access

### Local Development Database Setup

For local development, you can use SQLite instead of PostgreSQL:

1. Modify the `app/__init__.py` file to fall back to SQLite:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "sqlite:///app.db"
```

2. Create the database with:

```python
with app.app_context():
    db.create_all()
```

3. Run the setup script: `python setup_db.py`

## OpenAI API Issues

### API Key Configuration

**Error: `Invalid API key provided`**

```
openai.error.AuthenticationError: Invalid API key provided
```

**Solution:**
1. Verify your OpenAI API key in the admin interface
2. Check if the OPENAI_API_KEY environment variable is set correctly
3. Regenerate your API key in the OpenAI dashboard
4. Ensure the API key hasn't expired or been revoked

**Error: `Incorrect API key provided`**

```
openai.error.AuthenticationError: Incorrect API key provided: sk-...
```

**Solution:**
1. Check for whitespace or special characters in your API key
2. Ensure you're using the correct API key format (starts with "sk-")
3. Try generating a new API key

### API Usage Limits

**Error: `Rate limit exceeded`**

```
openai.error.RateLimitError: Rate limit exceeded
```

**Solution:**
1. Implement rate limiting in your application
2. Add exponential backoff for retries
3. Check your API usage limits in the OpenAI dashboard
4. Consider upgrading your OpenAI plan for higher limits

## Authentication Issues

### 2FA Problems

**Issue: User is locked out due to 2FA**

**Solution:**
1. Admin users can disable 2FA for a user in the admin interface
2. For admin accounts, use the `reset_admin_2fa.py` script:
   ```
   python reset_admin_2fa.py
   ```
3. Ensure users save their QR code or backup codes

**Issue: QR code not scanning properly**

**Solution:**
1. Ensure the QR code is displayed at an appropriate size
2. Check that the user's authenticator app is compatible (Google Authenticator, Microsoft Authenticator, etc.)
3. Provide the manual entry option with the TOTP secret key

## Deployment Issues

### Render Deployment

**Issue: Application crashes on Render**

**Solution:**
1. Check Render logs for specific error messages
2. Verify all environment variables are set correctly
3. Ensure your PostgreSQL database is active
4. Check if your application exceeds Render's free tier limits

**Issue: Static files not loading**

**Solution:**
1. Ensure your static files are included in the repository
2. Check file paths in templates (should use relative paths)
3. Verify that Render is serving static files correctly

## Application Performance

### Slow Document Analysis

**Issue: Document analysis takes too long**

**Solution:**
1. Add a timeout for OpenAI API calls
2. Optimize text extraction from large documents
3. Implement caching for repeated analyses
4. Consider breaking large documents into chunks

### Memory Issues

**Issue: Application crashes with large documents**

**Solution:**
1. Implement file size limits for uploads
2. Process large documents in chunks
3. Add memory monitoring and graceful degradation
4. Optimize PDF and DOCX extraction routines

## Missing Dependencies

**Issue: NLTK data not found**

```
LookupError: Resource 'tokenizers/punkt/english.pickle' not found
```

**Solution:**
1. Run the NLTK data downloader:
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   nltk.download('wordnet')
   ```
2. Ensure the download script is included in your deployment process

## Browser Compatibility

**Issue: Application doesn't work in older browsers**

**Solution:**
1. Add polyfills for older browsers
2. Use more compatible JavaScript features
3. Test with browser compatibility tools
4. Add browser requirement notes to documentation

## Common Workflow Solutions

### Reset Admin Password

If you need to reset an admin password:

```python
python create_admin.py
```

This will create a new admin account or reset the existing one.

### Initialize Database

To initialize the database with sample data:

```python
python setup_db.py
```

This will create interests, courses, and other basic data.

### Test API Connectivity

To test OpenAI API connectivity:

1. Log in as admin
2. Go to API Keys in the admin interface
3. Click "Test Connection"

## Debugging Tips

1. Check the application logs for detailed error messages
2. Use Flask's debug mode during development (`app.run(debug=True)`)
3. Add more logging statements to problematic areas
4. Use Python's debugger (pdb) for interactive debugging

## Getting Help

If you encounter issues not covered in this guide:

1. Check the Flask documentation: https://flask.palletsprojects.com/
2. Review the SQLAlchemy documentation: https://docs.sqlalchemy.org/
3. Consult the OpenAI API reference: https://platform.openai.com/docs/api-reference
4. Search for error messages in programming communities like Stack Overflow