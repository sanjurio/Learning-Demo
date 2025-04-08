# AI-Powered Learning Platform

An AI-powered learning platform that provides intelligent content management, personalized learning experiences, and enhanced user engagement through innovative educational technologies.

## Features

- **User Management:** Registration with mandatory 2FA, admin approval system, and role-based access control
- **Content Management:** Create and organize courses, lessons, and interest categories
- **AI-Powered Recommendations:** Get personalized course recommendations based on user interests
- **Discussion Forums:** Both general and course-specific discussion areas
- **Document Analysis:** AI-powered tool that can analyze PDFs, DOCX, and TXT files to generate summaries and Q&A

## Tech Stack

- **Backend:** Flask
- **Database:** PostgreSQL
- **Frontend:** Bootstrap, HTML/CSS/JS
- **Authentication:** Flask-Login with mandatory 2FA via TOTP
- **Document Processing:** PyPDF2, python-docx, NLTK, OpenAI API
- **Deployment:** Configured for Render or PythonAnywhere

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r deployment_requirements.txt
   ```
3. Set up environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `FLASK_SECRET_KEY`: Secret key for session management
   - `OPENAI_API_KEY`: For document analysis feature (optional)

4. Initialize the database:
   ```bash
   python setup_db.py
   ```

5. Run the application:
   ```bash
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

## Document Analysis Feature

The document analysis feature allows users to upload PDF, DOCX, or TXT files and get AI-powered analysis including:

- Document summary
- Extracted key information
- Generated questions and answers

### API Key Setup

There are two ways to configure the OpenAI API key:

#### Method 1: Through the Admin Interface (Recommended)

1. Log in as an admin user (default: admin@example.com / Admin123)
2. Navigate to Admin Dashboard → API Keys
3. Enter your OpenAI API key (starts with "sk-...")
4. Save the key
5. The document analysis feature will be immediately available

#### Method 2: As an Environment Variable

You can set the OpenAI API key as an environment variable:

- For local development: Set `OPENAI_API_KEY` in your environment
- For deployment on Render:
  1. Go to your Render dashboard
  2. Select your web service
  3. Go to the "Environment" tab
  4. Add key: `OPENAI_API_KEY` and value: your API key
  5. Save changes and Render will restart your service

### Usage

1. Navigate to the Document Analysis page from your dashboard
2. Upload a document (PDF, DOCX, or TXT format)
3. The system will process the document and display a summary and Q&A

If an OpenAI API key is not configured, the system will fall back to basic NLP techniques, but the results will be less comprehensive.

### Troubleshooting

If you're having issues with the document analysis feature:

1. Check if the OpenAI API key is configured correctly
2. Look for any error messages in the application logs
3. Make sure your OpenAI API key is valid and has sufficient credits

## Admin Account

The default admin credentials are:
- Email: admin@example.com
- Password: Admin123

Change these credentials immediately after first login.