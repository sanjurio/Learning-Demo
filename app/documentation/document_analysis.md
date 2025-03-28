# Document Analysis System Documentation

This document explains the document analysis system that allows users to upload and analyze documents with AI assistance.

## Overview

The document analysis feature enables users to upload documents (PDF, DOCX, or TXT files) and receive AI-generated summaries and contextual questions about the document content. The system extracts text from various file formats, applies natural language processing techniques, and leverages OpenAI's API for deeper analysis.

![Document Analysis System Workflow](../documentation/images/document_analysis_workflow.png)

## Components

### 1. Document Processor Module

**File: `app/utils/document_processor.py`**

This module contains the core document analysis functionality:

#### Text Extraction Functions

```python
def extract_text_from_pdf(file_stream):
    """Extract text content from a PDF file."""
    # Uses PyPDF2 to extract text from PDF files
    
def extract_text_from_docx(file_stream):
    """Extract text content from a DOCX file."""
    # Uses python-docx to extract text from DOCX files
    
def extract_text_from_txt(file_stream):
    """Extract text content from a plain text file."""
    # Reads and decodes text files
    
def extract_text(file_stream, filename):
    """Extract text from various file types based on file extension."""
    # Determines file type and calls appropriate extraction function
```

These functions handle the extraction of text content from different file formats. They manage file streams and handle errors that might occur during extraction.

#### AI Analysis Functions

```python
def get_openai_client():
    """Initialize and return the OpenAI client with the current API key."""
    # Configures and returns the OpenAI client for API access
    
def analyze_with_ai(text, prompt_type="summary"):
    """Analyze text using OpenAI API."""
    # Sends text to OpenAI for analysis and handles responses
```

These functions manage interactions with the OpenAI API. They include error handling, fallback options, and compatibility with different versions of the OpenAI client library.

#### NLP Functions

```python
def summarize_text(text, max_length=500):
    """Summarize text using basic NLP techniques (used as fallback when AI is unavailable)."""
    # Uses NLTK to perform extractive summarization based on word frequency
    
def generate_basic_questions(text):
    """Generate basic questions from text without using AI (fallback method)."""
    # Creates simple questions based on sentences in the document
```

These functions provide fallback capabilities when the OpenAI API is unavailable, using NLTK for basic natural language processing tasks.

#### Main Analysis Function

```python
def analyze_document(file_stream, filename):
    """Main function to analyze a document and return summary and questions."""
    # Orchestrates the entire document analysis process
```

This is the main entry point for document analysis that:
1. Extracts text from the uploaded document
2. Checks for OpenAI API availability
3. Generates summaries (with AI or fallback methods)
4. Creates questions and answers about the document
5. Formats and returns the results

### 2. Web Interface

**File: `templates/document_analysis.html`**

This template provides the user interface for document analysis, featuring:

- A drag-and-drop upload area for documents
- A chatbot-like interface showing analysis results
- Error messages and loading indicators
- Responsive design that works on mobile and desktop

### 3. API Endpoint

**File: `app/api/routes.py`**

The API endpoint handles document uploads and returns analysis results:

```python
@api_bp.route('/analyze-document', methods=['POST'])
@login_required
def api_analyze_document():
    """API endpoint to analyze an uploaded document"""
    # Validates uploaded file
    # Calls analyze_document function
    # Returns JSON response with results
```

### 4. Configuration and Status Endpoints

```python
@api_bp.route('/check-api-config', methods=['GET'])
@login_required
def check_api_config():
    """Simple endpoint to check if OpenAI API key is configured"""
    
@api_bp.route('/test-openai-connection', methods=['GET'])
@login_required
@admin_required
def test_openai_connection():
    """Diagnostic endpoint to test OpenAI API connectivity"""
```

These endpoints help verify API configuration and connectivity.

## Document Analysis Process Flow

1. **User uploads a document**:
   - Frontend JavaScript sends the file to the `/api/analyze-document` endpoint
   - Server validates the file (type, size, etc.)

2. **Text extraction**:
   - Based on file extension, the appropriate extraction function is called
   - Text is extracted and processed

3. **AI Analysis** (if OpenAI API is available):
   - Text is sent to OpenAI with specific prompts for:
     - Generating a concise summary
     - Creating contextual questions and answers
   - Responses are processed and formatted

4. **Fallback processing** (if AI is unavailable):
   - Basic NLP techniques are used to:
     - Extract key sentences for a summary
     - Generate simple questions based on content

5. **Response formatting**:
   - Results are structured into a JSON response
   - Frontend renders the analysis in a conversational format

## Error Handling

The system includes robust error handling:

- Validation of file types and sizes
- Graceful degradation when API keys are missing
- Fallback to basic NLP when AI services are unavailable
- Detailed logging for troubleshooting
- User-friendly error messages

## Implementation Details

### OpenAI Integration

The system uses OpenAI's GPT models to analyze documents with two main prompt types:

1. **Summary generation**:
   ```
   "Please provide a concise summary of the following document in about 200 words:\n\n{text}"
   ```

2. **Question generation**:
   ```
   "Based on the following document, generate 3 important questions someone might ask about this content, along with their answers:\n\n{text}"
   ```

The system supports different versions of the OpenAI client library and includes fallback mechanisms to handle API changes.

### Response Parsing

AI responses for questions are parsed using regex patterns to extract structured question-answer pairs. Multiple parsing strategies are attempted to handle different response formats from the AI.

### Performance Considerations

- Text length is limited to prevent excessive token usage
- Document size limits prevent memory issues
- Caching could be implemented to store analysis results

## Usage Examples

### Basic Usage

1. Navigate to the Document Analysis page
2. Upload a document (PDF, DOCX, or TXT)
3. Wait for analysis to complete
4. View the summary and generated questions
5. Explore the document insights

### Admin Configuration

1. Log in as an admin
2. Go to API Keys management
3. Add or update the OpenAI API key
4. Test the connection to ensure functionality