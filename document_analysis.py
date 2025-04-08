import os
import re
import io
import nltk
from PyPDF2 import PdfReader
from docx import Document
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.tokenize.treebank import TreebankWordDetokenizer
from werkzeug.utils import secure_filename

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

def get_important_sentences(text, num_sentences=5):
    """Extract important sentences based on word frequency"""
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    word_freq = FreqDist(word for word in words if word.isalnum() and word not in stop_words)

    sentence_scores = {}
    for sentence in sentences:
        score = 0
        words = word_tokenize(sentence.lower())
        for word in words:
            if word in word_freq:
                score += word_freq[word]
        sentence_scores[sentence] = score / len(words) if words else 0

    important_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
    return [sentence for sentence, score in important_sentences]

def generate_summary(text, max_length=500):
    """Generate a summary of the text"""
    if not text:
        return "No text content found in the document."

    important_sentences = get_important_sentences(text)
    summary = ' '.join(important_sentences)

    if len(summary) > max_length:
        summary = summary[:max_length].rsplit(' ', 1)[0] + '...'

    return summary

def generate_questions(text):
    """Generate questions from the text"""
    sentences = sent_tokenize(text)
    questions = []

    for sentence in sentences:
        words = word_tokenize(sentence)
        pos_tags = nltk.pos_tag(words)

        # Look for sentences with named entities or important information
        if any(tag in ['NNP', 'NNPS', 'CD'] for word, tag in pos_tags):
            # Remove punctuation from the end of the sentence
            sentence = re.sub(r'[.!?]$', '', sentence)

            # Create different types of questions
            if any(word.lower() in ['is', 'are', 'was', 'were'] for word in words):
                question = f"What {words[0].lower()} {' '.join(words[1:])}?"
            else:
                question = f"What can you tell me about {sentence}?"

            questions.append({
                "question": question,
                "answer": sentence
            })

        if len(questions) >= 3:
            break

    return questions if questions else [{
        "question": "What is the main topic of this document?",
        "answer": generate_summary(text, 200)
    }]

def analyze_document(file_stream, filename):
    """Main function to analyze a document"""
    try:
        # Extract text from the document
        text = extract_text(file_stream, filename)

        if not text or text.startswith("Unsupported") or text.startswith("Error"):
            return {
                "success": False,
                "message": text or "Failed to extract text from the document"
            }

        # Generate summary and questions
        summary = generate_summary(text)
        questions = generate_questions(text)

        return {
            "success": True,
            "summary": summary,
            "questions": questions,
            "ai_analysis": False
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "message": f"An error occurred during document analysis: {str(e)}",
            "error_details": traceback.format_exc()
        }