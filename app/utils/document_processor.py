"""
Document Processor: Functionality for analyzing and processing documents.

This module provides text extraction, summarization, and AI-powered analysis
capabilities for various document formats (PDF, DOCX, TXT).
"""
import os
import re
import io
import logging
from werkzeug.utils import secure_filename

# Set up logging
logger = logging.getLogger('document_analysis')

# Don't initialize client at module level
# Will create client on demand in functions that need it
client = None


def get_openai_client():
    """
    Initialize and return the OpenAI client with the current API key.
    
    Uses the OPENAI_API_KEY environment variable to configure the client.
    Returns None if no API key is available or if initialization fails.
    
    Returns:
        The initialized OpenAI module or None if initialization fails
    """
    global client
    
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # If we have an API key, create or update the client
    if api_key:
        try:
            # Clear existing client if it exists
            if client:
                logger.info("Resetting existing OpenAI client with new key")
                client = None
            
            # Avoid issues with OpenAI constructor by directly using dict instead of kwargs
            # This fixes compatibility issues with proxies argument in older/newer versions
            import openai
            openai.api_key = api_key
            
            # Use the top-level client from the module
            logger.info(f"OpenAI client initialized with API key: {api_key[:4]}...{api_key[-4:]}")
            
            # Return the module as the client
            return openai
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            return None
    else:
        logger.error("No OpenAI API key found in environment variables")
        return None


def extract_text_from_pdf(file_stream):
    """
    Extract text content from a PDF file.
    
    Args:
        file_stream: File-like object containing PDF data
        
    Returns:
        Extracted text as a string, or empty string on error
    """
    try:
        from PyPDF2 import PdfReader
        pdf_reader = PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""


def extract_text_from_docx(file_stream):
    """
    Extract text content from a DOCX file.
    
    Args:
        file_stream: File-like object containing DOCX data
        
    Returns:
        Extracted text as a string, or empty string on error
    """
    try:
        from docx import Document
        doc = Document(file_stream)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""


def extract_text_from_txt(file_stream):
    """
    Extract text content from a plain text file.
    
    Args:
        file_stream: File-like object containing text data
        
    Returns:
        Extracted text as a string, or empty string on error
    """
    try:
        text = file_stream.read().decode('utf-8')
        return text
    except Exception as e:
        logger.error(f"Error extracting text from text file: {e}")
        return ""


def extract_text(file_stream, filename):
    """
    Extract text from various file types based on file extension.
    
    Supports PDF, DOCX, and TXT formats.
    
    Args:
        file_stream: File-like object containing the document data
        filename: Original filename with extension
        
    Returns:
        Extracted text as a string, or error message on failure
    """
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_stream)
    elif file_ext == '.docx':
        return extract_text_from_docx(file_stream)
    elif file_ext == '.txt':
        return extract_text_from_txt(file_stream)
    else:
        return "Unsupported file format. Please upload a PDF, DOCX, or TXT file."


def summarize_text(text, max_length=500):
    """
    Summarize text using basic NLP techniques (used as fallback when AI is unavailable).
    
    Uses a frequency-based approach to identify important sentences.
    
    Args:
        text: The text to summarize
        max_length: Maximum desired length of summary (not strictly enforced)
        
    Returns:
        Summarized text as a string
    """
    if not text:
        return "No text content found in the document."
    
    # Import here to avoid loading nltk on module import
    import nltk
    from nltk.tokenize import sent_tokenize
    
    # Basic summarization using sentence scoring
    sentences = sent_tokenize(text)
    
    if len(sentences) <= 3:
        return text
    
    # Simple frequency-based summarization
    word_frequencies = {}
    for sentence in sentences:
        for word in nltk.word_tokenize(sentence.lower()):
            if word not in nltk.corpus.stopwords.words('english'):
                if word not in word_frequencies:
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1
    
    # Normalize frequencies
    if word_frequencies:
        max_frequency = max(word_frequencies.values())
        for word in word_frequencies:
            word_frequencies[word] = word_frequencies[word] / max_frequency
    
    # Score sentences
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        for word in nltk.word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if i not in sentence_scores:
                    sentence_scores[i] = word_frequencies[word]
                else:
                    sentence_scores[i] += word_frequencies[word]
    
    # Get top 3 sentences
    if not sentence_scores:
        return ' '.join(sentences[:3])
    
    # Sort by score
    summary_sentences_indices = []
    for idx, score in sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:3]:
        summary_sentences_indices.append(idx)
    
    # Sort by position in text to maintain flow
    summary_sentences_indices.sort()
    
    summary = ' '.join([sentences[i] for i in summary_sentences_indices])
    return summary


def analyze_with_ai(text, prompt_type="summary"):
    """
    Analyze text using OpenAI API.
    
    Sends the text to OpenAI's GPT model for analysis, with fallback options
    if the primary approach fails.
    
    Args:
        text: The text to analyze
        prompt_type: Type of analysis to perform ("summary" or "questions")
        
    Returns:
        AI-generated analysis as a string, or None if analysis fails
    """
    # Get a client with the current API key
    openai_module = get_openai_client()
    
    if not openai_module:
        logger.error("Cannot analyze with AI: No OpenAI API key available")
        return None
    
    try:
        # Truncate text if it's too long
        max_tokens = 4000  # Adjust as needed
        text = text[:max_tokens * 4]  # Rough estimate for token/char ratio
        
        prompt = ""
        if prompt_type == "summary":
            prompt = f"Please provide a concise summary of the following document in about 200 words:\n\n{text}"
        elif prompt_type == "questions":
            prompt = f"Based on the following document, generate 3 important questions someone might ask about this content, along with their answers:\n\n{text}"
        
        logger.info(f"Sending request to OpenAI API for {prompt_type}")
        
        # Use the older OpenAI API format which should be compatible with most versions
        try:
            # Set up system message and user message
            messages = [
                {"role": "system", "content": "You are a helpful assistant that analyzes documents and extracts key information."},
                {"role": "user", "content": prompt}
            ]
            
            # Create a Completion request
            response = openai_module.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.5
            )
            
            logger.info(f"Response received successfully")
            # Get the content from the first choice's message content
            result = response.choices[0].message.content
            return result
        except Exception as api_error:
            logger.error(f"Error with OpenAI API: {api_error}")
            # Try fallback to text completion API
            try:
                logger.info("Falling back to text completion API")
                # Use the completions API as fallback
                response = openai_module.Completion.create(
                    model="text-davinci-003", # Fallback to a model that should exist in most OpenAI versions
                    prompt=prompt,
                    max_tokens=500,
                    temperature=0.5
                )
                logger.info(f"Fallback response received successfully")
                result = response.choices[0].text
                return result
            except Exception as fallback_error:
                logger.error(f"Fallback error: {fallback_error}")
                return "Unable to generate AI analysis at this time. Please try again later."
    except Exception as e:
        import traceback
        logger.error(f"Error with OpenAI API: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


def generate_basic_questions(text):
    """
    Generate basic questions from text without using AI (fallback method).
    
    Creates simple questions based on sentences in the document.
    
    Args:
        text: The document text
        
    Returns:
        List of question dictionaries with 'question' and 'context' keys
    """
    # Import here to avoid loading nltk on module import
    from nltk.tokenize import sent_tokenize
    
    sentences = sent_tokenize(text)
    questions = []
    
    if len(sentences) < 3:
        return ["Not enough content to generate meaningful questions."]
    
    # Select a few sentences to convert to questions
    for i, sentence in enumerate(sentences[:10]):
        if len(sentence.split()) > 5 and i % 3 == 0:  # Every 3rd sentence
            # Simple transformation to question
            words = sentence.split()
            if len(words) > 3:
                question = f"What does the document say about {' '.join(words[1:3])}?"
                questions.append({"question": question, "context": sentence})
            
            if len(questions) >= 3:
                break
    
    return questions if questions else ["Unable to generate questions from this document."]


def analyze_document(file_stream, filename):
    """
    Main function to analyze a document and return summary and questions.
    
    This is the primary entry point for document analysis functionality.
    It extracts text, generates a summary, and creates questions about the content.
    
    Args:
        file_stream: File-like object containing the document data
        filename: Original filename with extension
        
    Returns:
        Dictionary with analysis results or error information
    """
    logger.info(f"Starting document analysis for file: {filename}")
    
    try:
        secured_filename = secure_filename(filename)
        logger.info(f"Secured filename: {secured_filename}")
        
        # Step 1: Extract text from the document
        logger.info("Extracting text from document")
        text = extract_text(file_stream, secured_filename)
        
        # Handle extraction failures
        if not text:
            logger.warning("No text extracted from document")
            return {"success": False, "message": "Failed to extract text from the document. The file may be empty or corrupted."}
        
        if text.startswith("Unsupported"):
            logger.warning(f"Unsupported file format: {secured_filename}")
            return {"success": False, "message": text}
        
        if text.startswith("Error"):
            logger.warning(f"Error extracting text: {text}")
            return {"success": False, "message": text}
        
        # Step 2: Check for API key and connectivity before attempting AI analysis
        logger.info("Checking OpenAI client availability")
        client = get_openai_client()
        has_ai = bool(client)
        
        # Log text length for debugging
        text_length = len(text)
        logger.info(f"Extracted {text_length} characters of text")
        if text_length > 500:
            sample_text = text[:500] + "..."
        else:
            sample_text = text
        logger.debug(f"Sample text: {sample_text}")
        
        # Step 3: Generate analysis
        ai_summary = None
        ai_questions = None
        
        if has_ai:
            logger.info("Attempting AI-based summary generation")
            ai_summary = analyze_with_ai(text, "summary")
            if ai_summary:
                logger.info(f"AI summary generated successfully ({len(ai_summary)} chars)")
            else:
                logger.warning("Failed to generate AI summary")
            
            logger.info("Attempting AI-based question generation")
            ai_questions = analyze_with_ai(text, "questions")
            if ai_questions:
                logger.info(f"AI questions generated successfully ({len(ai_questions)} chars)")
            else:
                logger.warning("Failed to generate AI questions")
        else:
            logger.warning("No OpenAI client available, skipping AI analysis")
        
        # Step 4: Fallback to basic methods if AI fails
        if ai_summary:
            summary = ai_summary
            logger.info("Using AI-generated summary")
        else:
            logger.info("Falling back to basic summarization")
            summary = summarize_text(text)
            logger.info(f"Basic summary generated ({len(summary)} chars)")
        
        # Step 5: Process questions
        formatted_questions = []
        
        if ai_questions:
            logger.info("Processing AI-generated questions")
            # Format AI-generated questions into the expected format
            # AI typically returns a string with numbered questions and answers
            
            try:
                # Try to parse the AI response into structured Q&A format
                lines = ai_questions.strip().split('\n')
                current_q = None
                current_a = []
                
                logger.debug(f"Parsing {len(lines)} lines of AI question response")
                
                for line in lines:
                    line = line.strip()
                    # Look for lines that start with Q, Question, 1., etc.
                    if re.match(r'^(Q|Question|[0-9]+\.|\*|\-)\s+', line, re.IGNORECASE):
                        # If we already have a question, save it and its answer
                        if current_q:
                            formatted_questions.append({
                                "question": current_q,
                                "answer": ' '.join(current_a)
                            })
                            logger.debug(f"Parsed question: {current_q[:30]}...")
                        # Start a new question
                        current_q = re.sub(r'^(Q|Question|[0-9]+\.|\*|\-)\s+', '', line, flags=re.IGNORECASE)
                        current_a = []
                    # Look for lines that start with A, Answer, etc.
                    elif re.match(r'^(A|Answer|R|Response):\s+', line, re.IGNORECASE):
                        # This is an answer line
                        answer_text = re.sub(r'^(A|Answer|R|Response):\s+', '', line, flags=re.IGNORECASE)
                        current_a.append(answer_text)
                    elif current_q and not current_a and ':' in line:
                        # This might be a Q: followed by A: on the same line
                        parts = line.split(':', 1)
                        if len(parts) == 2 and parts[0].strip() in ['Q', 'Question']:
                            current_q = parts[1].strip()
                    elif current_q:
                        # This is continuation of an answer
                        current_a.append(line)
                
                # Add the last question/answer pair
                if current_q:
                    formatted_questions.append({
                        "question": current_q,
                        "answer": ' '.join(current_a)
                    })
                    logger.debug(f"Parsed final question: {current_q[:30]}...")
                
                # If we couldn't parse any questions, try a different approach
                if not formatted_questions:
                    logger.info("First parsing approach failed, trying alternative approaches")
                    
                    # Split on numbered questions like "1. Question"
                    sections = re.split(r'\n\s*[0-9]+\.\s+', '\n' + ai_questions)
                    if len(sections) > 1:  # First section is empty due to the leading \n
                        logger.debug(f"Found {len(sections)-1} numbered sections")
                        for section in sections[1:]:  # Skip the first empty section
                            parts = section.split('\n', 1)
                            if len(parts) == 2:
                                formatted_questions.append({
                                    "question": parts[0].strip(),
                                    "answer": parts[1].strip()
                                })
                                logger.debug(f"Parsed numbered question: {parts[0].strip()[:30]}...")
                
                # If we still couldn't parse any questions, fallback to simple splitting
                if not formatted_questions and ai_questions:
                    logger.info("Alternative parsing approach failed, falling back to basic split")
                    from nltk.tokenize import sent_tokenize
                    
                    # Just split the text into roughly equal parts for Q&A
                    sentences = sent_tokenize(ai_questions)
                    mid = len(sentences) // 2
                    
                    formatted_questions = [
                        {
                            "question": "What are the key points in this document?",
                            "answer": ' '.join(sentences[:mid])
                        },
                        {
                            "question": "What additional information does the document provide?",
                            "answer": ' '.join(sentences[mid:])
                        }
                    ]
                    logger.debug("Created basic split questions")
                
                logger.info(f"Successfully parsed {len(formatted_questions)} questions from AI response")
                
            except Exception as e:
                import traceback
                logger.error(f"Error parsing AI questions: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Fallback to the entire response as one Q&A
                formatted_questions = [
                    {
                        "question": "What information is contained in this document?",
                        "answer": ai_questions
                    }
                ]
                logger.info("Using entire AI response as a single question/answer due to parsing error")
            
            result = {
                "success": True,
                "summary": summary,
                "ai_analysis": True,
                "questions": formatted_questions
            }
        else:
            # Basic question generation as fallback
            logger.info("No AI questions available, using basic question generation")
            basic_questions = generate_basic_questions(text)
            
            # Ensure proper formatting for API response
            formatted_questions = []
            for q in basic_questions:
                if isinstance(q, dict) and "question" in q:
                    formatted_questions.append(q)
                else:
                    formatted_questions.append({
                        "question": "What is this document about?",
                        "answer": q if isinstance(q, str) else str(q)
                    })
            
            logger.info(f"Generated {len(formatted_questions)} basic questions")
            
            result = {
                "success": True,
                "summary": summary,
                "ai_analysis": False,
                "questions": formatted_questions
            }
        
        logger.info("Document analysis completed successfully")
        return result
        
    except Exception as e:
        import traceback
        logger.error(f"Critical error in analyze_document: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "message": f"An unexpected error occurred during document analysis: {str(e)}",
            "error_details": traceback.format_exc()
        }