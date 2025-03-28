# AI Learning Platform

A comprehensive learning management system with AI-powered features for personalized education experiences.

## About

The AI Learning Platform is a web-based application that combines traditional learning management functionality with advanced AI features. It provides a secure, structured environment for creating, managing, and delivering educational content, with intelligent tools to enhance the learning experience.

### Key Features

- **Secure Authentication**: Email-based registration with mandatory two-factor authentication
- **User Management**: Admin approval process and interest-based access control
- **Course System**: Structured courses with ordered lessons and progress tracking
- **Interest Categories**: Organization of content by topic with personalized recommendations
- **Discussion Forums**: General and course-specific discussion boards
- **Document Analysis**: AI-powered tool to extract insights from uploaded documents
- **Admin Dashboard**: Comprehensive tools for content and user management
- **Responsive Design**: Mobile-friendly interface that works on various devices

## Screenshots

![Admin Dashboard](app/documentation/images/screenshot_admin_dashboard.png)
![Course View](app/documentation/images/screenshot_course_view.png)
![Document Analysis](app/documentation/images/screenshot_document_analysis.png)

## Technology Stack

- **Backend**: Python with Flask framework
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login with TOTP-based 2FA
- **Frontend**: Bootstrap, HTML, CSS, JavaScript
- **AI Integration**: OpenAI API for document analysis
- **Text Processing**: NLTK for natural language processing
- **Document Handling**: PyPDF2 and python-docx for file processing

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL database
- OpenAI API key (for document analysis)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-learning-platform.git
   cd ai-learning-platform
   ```

2. Install dependencies:
   ```
   pip install -r deployment_requirements.txt
   ```

3. Configure environment variables:
   ```
   export DATABASE_URL=postgresql://username:password@localhost/dbname
   export FLASK_SECRET_KEY=your-secret-key
   export OPENAI_API_KEY=your-openai-api-key
   ```

4. Initialize the database:
   ```
   python setup_db.py
   ```

5. Create an admin user:
   ```
   python create_admin.py
   ```

6. Run the application:
   ```
   python main.py
   ```

7. Access the application at http://localhost:5000

## Usage

After installation, you can access the platform:

1. Login with the default admin account (email: admin@example.com, password: Admin123)
2. Create interest categories through the admin interface
3. Add courses and lessons to your interests
4. Create user accounts and grant them access to specific interests
5. Upload and analyze documents with the document analysis tool

For a detailed user guide, see the [Documentation](#documentation) section.

## Documentation

Comprehensive documentation is available in the [app/documentation](app/documentation) directory:

- [Project Overview](app/documentation/README.md): High-level explanation of the platform
- [User Guide](app/documentation/user_guide.md): Instructions for end users
- [Admin Guide](app/documentation/admin_system.md): Guide for administrators
- [API Documentation](app/documentation/api.md): Details on API endpoints
- [Database Schema](app/documentation/models.md): Database model documentation
- [Deployment Guide](app/documentation/deployment.md): Instructions for production deployment
- [Troubleshooting Guide](app/documentation/troubleshooting.md): Solutions for common issues

## Development

### Project Structure

```
/
├── app/                # Main application package
│   ├── __init__.py     # Application factory
│   ├── admin/          # Admin routes and functionality
│   ├── api/            # API endpoints
│   ├── auth/           # Authentication functionality
│   ├── core/           # Core application routes
│   ├── documentation/  # Project documentation
│   ├── models/         # Database models
│   └── utils/          # Utility functions
├── static/             # Static assets (CSS, JS, images)
├── templates/          # Jinja2 templates
├── instance/           # Instance-specific files
├── main.py             # Application entry point
└── tests/              # Test suite
```

### Testing

Run the test suite with:
```
python -m unittest discover tests
```

## Deployment

The application can be deployed to various platforms:

- **Render**: Deploy directly from GitHub with PostgreSQL add-on
- **PythonAnywhere**: Upload code and configure with their MySQL database
- **Custom VPS**: Deploy to any server with Python and PostgreSQL

For detailed deployment instructions, see the [deployment guide](app/documentation/deployment.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask and its extensions for the web framework
- Bootstrap for the responsive UI components
- OpenAI for the document analysis capabilities
- NLTK for natural language processing features