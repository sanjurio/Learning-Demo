# API Documentation

This document details the API endpoints available in the AI Learning Platform.

## Overview

The platform provides several API endpoints for document analysis and system configuration. These endpoints are primarily used by the frontend JavaScript to interact with backend services, particularly for the document analysis feature.

## Authentication

All API endpoints require authentication. Users must be logged in to access these endpoints. Some endpoints also require admin privileges.

Authentication is managed through Flask-Login sessions, so API requests inherit the authentication context from the user's browser session.

## Document Analysis Endpoints

### Analyze Document

**Endpoint:** `/api/analyze-document`  
**Method:** POST  
**Authentication:** Requires login  

This endpoint processes uploaded documents and returns analysis results including a summary and generated questions.

#### Request

The request should be a multipart form with:

```
Content-Type: multipart/form-data
```

Form fields:
- `document`: The file to analyze (PDF, DOCX, or TXT format)

Example request using fetch:

```javascript
const formData = new FormData();
formData.append('document', fileInput.files[0]);

fetch('/api/analyze-document', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  // Handle analysis results
});
```

#### Response

The response is a JSON object with the following structure:

```json
{
  "success": true,
  "summary": "This is a summary of the document content...",
  "questions": [
    {
      "question": "What is the main topic of this document?",
      "answer": "The main topic is..."
    },
    {
      "question": "How does the document address...?",
      "answer": "The document addresses this by..."
    }
  ],
  "error": null
}
```

In case of an error:

```json
{
  "success": false,
  "error": "Error message explaining what went wrong",
  "summary": null,
  "questions": null
}
```

#### Error Codes

- 400: Invalid request (missing file, unsupported format)
- 401: Not authenticated
- 500: Server error during processing

### Check API Configuration

**Endpoint:** `/api/check-api-config`  
**Method:** GET  
**Authentication:** Requires login  

This endpoint checks if the OpenAI API key is configured and returns the status.

#### Request

Simple GET request:

```javascript
fetch('/api/check-api-config')
.then(response => response.json())
.then(data => {
  // Handle configuration status
});
```

#### Response

```json
{
  "api_configured": true,
  "service": "openai"
}
```

Or if not configured:

```json
{
  "api_configured": false,
  "service": "openai"
}
```

### Test OpenAI Connection

**Endpoint:** `/api/test-openai-connection`  
**Method:** GET  
**Authentication:** Requires login and admin privileges  

This diagnostic endpoint tests the connection to the OpenAI API and returns detailed status information.

#### Request

Simple GET request:

```javascript
fetch('/api/test-openai-connection')
.then(response => response.json())
.then(data => {
  // Handle connection test results
});
```

#### Response

```json
{
  "success": true,
  "message": "Successfully connected to OpenAI API",
  "details": {
    "model": "gpt-4o",
    "response": "Sample response from model"
  }
}
```

Or if connection fails:

```json
{
  "success": false,
  "message": "Failed to connect to OpenAI API",
  "error": "Error details from the API",
  "details": null
}
```

## Error Handling

All API endpoints follow a consistent error handling pattern:

1. HTTP status codes indicate the general category of response
2. JSON responses include a `success` boolean flag
3. Error details are provided in the `error` field when `success` is `false`
4. Validation errors include specific field information when relevant

## Development Guidelines

When extending the API, follow these guidelines:

1. **Authentication**: All endpoints should require authentication
2. **Response Format**: Use consistent JSON structure with `success` flag
3. **Error Handling**: Provide meaningful error messages
4. **Documentation**: Update this documentation with new endpoints
5. **Testing**: Create tests for all new endpoints

## Testing the API

You can test the API using:

### cURL

```bash
# Analyze document
curl -X POST -F "document=@/path/to/document.pdf" \
  -b "session_cookie=your_session_cookie" \
  http://localhost:5000/api/analyze-document

# Check API configuration
curl -b "session_cookie=your_session_cookie" \
  http://localhost:5000/api/check-api-config
```

### JavaScript (Browser Console)

```javascript
// Analyze document
const fileInput = document.createElement('input');
fileInput.type = 'file';
fileInput.onchange = () => {
  const formData = new FormData();
  formData.append('document', fileInput.files[0]);
  
  fetch('/api/analyze-document', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(console.log);
};
fileInput.click();

// Check API configuration
fetch('/api/check-api-config')
  .then(response => response.json())
  .then(console.log);
```

### Postman

1. Create a new request
2. Set the URL to the endpoint (e.g., `http://localhost:5000/api/check-api-config`)
3. For POST requests, configure the Body with appropriate parameters
4. Include cookies from a logged-in browser session
5. Send the request and view the response