import os
import re
import io
import nltk
import openai
from PyPDF2 import PdfReader
from docx import Document
from nltk.tokenize import sent_tokenize
from werkzeug.utils import secure_filename

# Don't initialize client at module level
# Will create client on demand in functions that need it
client = None

def get_openai_client():
    """Get OpenAI client with current API key"""
    global client
    
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # If we have an API key, create or update the client
    if api_key:
        try:
            # Check which version of openai is installed
            if hasattr(openai, 'OpenAI'):
                # New version (>=1.0.0)
                client = openai.OpenAI(api_key=api_key)
                print(f"OpenAI client (new API) initialized with API key: {api_key[:5]}...{api_key[-4:]}")
            else:
                # Legacy version (<1.0.0)
                openai.api_key = api_key
                client = openai
                print(f"OpenAI client (legacy API) initialized with API key: {api_key[:5]}...{api_key[-4:]}")
            
            return client
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            return None
    else:
        print("No OpenAI API key found in environment variables")
        return None

def extract_text_from_pdf(file_stream):
    """Extract text from a PDF file"""
    try:
        pdf_reader = PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_stream):
    """Extract text from a DOCX file"""
    try:
        doc = Document(file_stream)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_txt(file_stream):
    """Extract text from a text file"""
    try:
        text = file_stream.read().decode('utf-8')
        return text
    except Exception as e:
        print(f"Error extracting text from text file: {e}")
        return ""

def extract_text(file_stream, filename):
    """Extract text from various file types"""
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
    """Summarize text using basic NLP techniques as fallback"""
    if not text:
        return "No text content found in the document."
    
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
    """Analyze text using OpenAI API"""
    # Get a client with the current API key
    client = get_openai_client()
    
    if not client:
        print("Cannot analyze with AI: No OpenAI API key available")
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
        
        print(f"Sending request to OpenAI API for {prompt_type}")
        
        # Check which version of the client we're using
        if hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
            # New version (>=1.0.0)
            print("Using new OpenAI API format")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes documents and extracts key information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            result = response.choices[0].message.content
        else:
            # Legacy version (<1.0.0)
            print("Using legacy OpenAI API format")
            response = client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes documents and extracts key information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            result = response.choices[0].message['content']
        
        print(f"Successfully received response from OpenAI API")
        return result
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None

def generate_basic_questions(text):
    """Generate basic questions from text without AI"""
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
    """Main function to analyze a document and return summary and questions"""
    secured_filename = secure_filename(filename)
    text = extract_text(file_stream, secured_filename)
    
    if not text or text.startswith("Unsupported") or text.startswith("Error"):
        return {
            "success": False,
            "message": text or "Failed to extract text from the document."
        }
    
    # Try to use OpenAI for analysis
    ai_summary = analyze_with_ai(text, "summary")
    ai_questions = analyze_with_ai(text, "questions")
    
    # Fallback to basic methods if AI fails
    summary = ai_summary if ai_summary else summarize_text(text)
    
    if ai_questions:
        # Format AI-generated questions into the expected format
        # AI typically returns a string with numbered questions and answers
        formatted_questions = []
        
        try:
            # Try to parse the AI response into structured Q&A format
            lines = ai_questions.strip().split('\n')
            current_q = None
            current_a = []
            
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
            
            # If we couldn't parse any questions, try a different approach
            if not formatted_questions:
                # Split on numbered questions like "1. Question"
                sections = re.split(r'\n\s*[0-9]+\.\s+', '\n' + ai_questions)
                if len(sections) > 1:  # First section is empty due to the leading \n
                    for section in sections[1:]:  # Skip the first empty section
                        parts = section.split('\n', 1)
                        if len(parts) == 2:
                            formatted_questions.append({
                                "question": parts[0].strip(),
                                "answer": parts[1].strip()
                            })
            
            # If we still couldn't parse any questions, fallback to simple splitting
            if not formatted_questions and ai_questions:
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
        except Exception as e:
            print(f"Error parsing AI questions: {e}")
            # Fallback to the entire response as one Q&A
            formatted_questions = [
                {
                    "question": "What information is contained in this document?",
                    "answer": ai_questions
                }
            ]
        
        result = {
            "success": True,
            "summary": summary,
            "ai_analysis": True,
            "questions": formatted_questions
        }
    else:
        # Basic question generation as fallback
        basic_questions = generate_basic_questions(text)
        result = {
            "success": True,
            "summary": summary,
            "ai_analysis": False,
            "questions": basic_questions
        }
    
    return result