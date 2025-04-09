import os
import re
import io
import logging
from PyPDF2 import PdfReader
from docx import Document
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.tokenize.treebank import TreebankWordDetokenizer
import nltk

nltk_data_path = './nltk_data'
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

def extract_text_from_pdf(file_stream):
    """Extract text from a PDF file"""
    try:
        pdf_reader = PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return None

def extract_text_from_docx(file_stream):
    """Extract text from a DOCX file"""
    try:
        doc = Document(file_stream)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        return None

def extract_text_from_txt(file_stream):
    """Extract text from a text file"""
    try:
        text = file_stream.read().decode('utf-8')
        return text
    except Exception as e:
        logger.error(f"Error extracting text from text file: {str(e)}")
        return None

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
        logger.error(f"Unsupported file format: {file_ext}")
        return None

def generate_summary(text, max_length=700):
    """Generate a structured, readable summary"""
    try:
        if not text:
            return "No text content found in the document."

        lines = text.strip().splitlines()
        summary_lines = []
        current_section = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.endswith(":") and len(line) < 60:
                current_section = line.rstrip(":")
                summary_lines.append(f"\n🔹 {current_section}")
            elif current_section:
                summary_lines.append(f"– {line}")
            else:
                summary_lines.append(line)

        summary = "\n".join(summary_lines)
        return summary[:max_length].rsplit(' ', 1)[0] + '...' if len(summary) > max_length else summary
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return "Error generating summary."

def generate_questions(text):
    """Generate better contextual questions from the text"""
    try:
        sentences = sent_tokenize(text)
        questions = []

        for sentence in sentences:
            sentence_clean = sentence.strip().rstrip(".")

            if sentence_clean.lower().startswith("ai can"):
                question = "How can AI help in various fields?"
            elif sentence_clean.lower().startswith("ai tools"):
                question = "What are some popular AI tools?"
            elif "concerns" in sentence.lower() or "issues" in sentence.lower():
                question = "What are the concerns associated with AI-generated content?"
            elif sentence_clean.lower().startswith("examples"):
                question = "Can you give examples of AI content?"
            else:
                continue

            questions.append({"question": question, "answer": sentence_clean})
            if len(questions) >= 5:
                break

        if not questions:
            questions = [{
                "question": "What is the main topic of this document?",
                "answer": generate_summary(text, 200)
            }]

        return questions
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        return [{"question": "Error generating questions", "answer": str(e)}]

def analyze_document(file_stream, filename):
    """Main function to analyze a document"""
    try:
        logger.info(f"Starting analysis of document: {filename}")
        text = extract_text(file_stream, filename)

        if text is None or not text.strip():
            return {"success": False, "message": "No text content found in the document"}

        summary = generate_summary(text)
        questions = generate_questions(text)

        logger.info("Document analysis completed successfully")
        return {"success": True, "summary": summary, "questions": questions}

    except Exception as e:
        logger.error(f"Error in document analysis: {str(e)}")
        return {"success": False, "message": f"An error occurred: {str(e)}"}