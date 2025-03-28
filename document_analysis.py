import os
import re
import io
import nltk
import openai
from PyPDF2 import PdfReader
from docx import Document
from nltk.tokenize import sent_tokenize
from werkzeug.utils import secure_filename

# Configure OpenAI API (will need API key from environment)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Update OpenAI client if API key is set
if openai.api_key:
    client = openai.OpenAI(api_key=openai.api_key)
else:
    client = None

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
    if not openai.api_key or not client:
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
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes documents and extracts key information."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5
        )
        
        return response.choices[0].message.content
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
        result = {
            "success": True,
            "summary": summary,
            "ai_analysis": True,
            "questions": ai_questions
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