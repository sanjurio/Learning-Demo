# Erlang Systems Learning Platform

## Overview

This is a comprehensive Erlang Systems learning platform built with Flask that provides enterprise-grade training, certification, and knowledge management for Erlang/OTP development. The platform features user registration with mandatory 2FA, admin approval systems, domain-based access control, specialized content delivery, discussion forums, and document analysis capabilities for Erlang documentation.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (July 16, 2025)

✓ Successfully migrated from Replit Agent to Replit environment
✓ Fixed Flask app architecture to follow Replit standards with ProxyFix
✓ Set up PostgreSQL database with proper connection and environment variables
✓ Implemented domain-based access control system:
  - @thbs.com users: full_access (can view text and video content)
  - @bt.com users: text_only (can view only text content)
  - Other domains: basic (require admin approval)
✓ Enhanced User model with access_level and email_domain fields
✓ Added content type support to lessons (text, video, mixed)
✓ Created sample courses and lessons to demonstrate access control
✓ Fixed admin approval system - all users now require admin approval before login
✓ Updated database schema with required columns for new features

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (production) with SQLite fallback (development)
- **Authentication**: Flask-Login with mandatory TOTP-based 2FA
- **Security**: CSRF protection via Flask-WTF
- **Session Management**: Server-side sessions with secure secret keys

### Frontend Architecture
- **UI Framework**: Bootstrap with custom dark theme
- **JavaScript**: Vanilla JS with modular components
- **Styling**: Custom CSS with responsive design
- **Icons**: Font Awesome and Bootstrap Icons

### Data Storage Solutions
- **Primary Database**: PostgreSQL for production deployment
- **Development Database**: SQLite for local development
- **Connection Management**: Connection pooling with automatic reconnection

## Key Components

### User Management System
- **Registration**: Multi-step process with email validation and strong password requirements
- **2FA Authentication**: Mandatory TOTP setup using QR codes (pyotp library)
- **Admin Approval**: All new users require admin approval before access
- **Role-Based Access**: Admin and regular user roles with different permissions

### Content Management
- **Courses**: Hierarchical course structure with lessons and progress tracking
- **Interests**: Category-based content organization with user-specific access control
- **Lessons**: Sequential lesson structure with progress tracking
- **Forums**: Both general and course-specific discussion areas

### Domain-Based Access Control
- **THBS Users (@thbs.com)**: Full access to both text and video content including Erlang system demonstrations
- **BT Users (@bt.com)**: Text-only access to Erlang documentation and tutorials
- **Other Domains**: Basic access requiring individual admin approval
- **Video Access Control**: Erlang system demonstrations restricted based on user domain

### Content Management Features
- **Document Analysis**: PDF, DOCX, and TXT file processing for Erlang documentation
- **Content Summarization**: Automatic summary generation from Erlang technical documents
- **Mixed Content Support**: Lessons with both text documentation and video demonstrations
- **Access-Level Filtering**: Content visibility based on user's domain and approval status

### Administrative Features
- **User Management**: Approve/reject user registrations, manage access permissions
- **Content Administration**: Create and manage courses, lessons, and interest categories
- **API Key Management**: Configure external service integrations (OpenAI)
- **System Monitoring**: Dashboard with key metrics and statistics

## Data Flow

### User Registration Flow
1. User submits registration form with username, email, and password
2. System validates input and creates pending user account
3. User sets up mandatory 2FA using authenticator app
4. Admin reviews and approves/rejects the registration
5. Approved users gain access to platform based on assigned interests

### Content Access Flow
1. Users select interests during or after registration
2. Admin grants access to specific interest categories
3. System shows courses associated with user's approved interests
4. Users can enroll in courses and track progress through lessons
5. Course-specific forums become available upon enrollment

### Document Analysis Flow
1. User uploads document (PDF, DOCX, or TXT) via floating chat interface
2. System extracts text content using appropriate parser
3. Content is sent to OpenAI API for analysis (if configured)
4. System generates summary, key points, and Q&A
5. Results are displayed in formatted interface with downloadable options

## External Dependencies

### Required Services
- **PostgreSQL Database**: Primary data storage (Render, Neon, or similar)
- **OpenAI API**: Document analysis and AI features (optional but recommended)

### Python Packages
- **Flask Ecosystem**: flask, flask-sqlalchemy, flask-login, flask-wtf
- **Database**: psycopg2-binary for PostgreSQL connectivity
- **Authentication**: pyotp for 2FA, qrcode for QR generation
- **Document Processing**: PyPDF2, python-docx for file parsing
- **AI Integration**: openai for API communication
- **Text Processing**: nltk for natural language processing

### Frontend Dependencies
- **Bootstrap**: UI framework and responsive design
- **Font Awesome**: Icon library
- **Custom CSS**: Platform-specific styling and theming

## Deployment Strategy

### Environment Configuration
- **Database URL**: PostgreSQL connection string or SQLite fallback
- **Session Secret**: Secure random key for Flask sessions
- **OpenAI API Key**: Required for document analysis features (optional)

### Production Deployment
- **Platform**: Designed for Render, PythonAnywhere, or similar platforms
- **Web Server**: Gunicorn with optimized worker configuration
- **Database**: PostgreSQL with connection pooling and automatic reconnection
- **Static Files**: Served via CDN for Bootstrap and icon libraries

### Development Setup
- **Local Database**: SQLite with automatic creation
- **Hot Reload**: Flask development server with debug mode
- **Database Initialization**: Automated setup scripts for admin user and sample data

### Security Considerations
- **CSRF Protection**: All forms protected with CSRF tokens
- **Password Security**: Strong password requirements with hashing
- **Session Security**: Secure session configuration with proper timeouts
- **Input Validation**: Comprehensive form validation on client and server side
- **API Security**: Secure handling of external API keys and credentials