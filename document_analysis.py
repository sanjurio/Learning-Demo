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

# Only download 'punkt' and ignore 'punkt_tab'
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', download_dir=nltk_data_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def get_important_sentences(text, num_sentences=5):
    """Extract important sentences based on word frequency"""
    try:
        # Use simple sentence splitting as fallback if NLTK fails
        sentences = text.split('. ')
        words = [word.strip().lower() for word in text.split()]
        stop_words = set(stopwords.words('english'))
        word_freq = FreqDist(word for word in words
                             if word.isalnum() and word not in stop_words)

        sentence_scores = {}
        for sentence in sentences:
            score = 0
            words = sentence.lower().split()
            for word in words:
                if word in word_freq:
                    score += word_freq[word]
            sentence_scores[sentence] = score / len(words) if words else 0

        important_sentences = sorted(sentence_scores.items(),
                                     key=lambda x: x[1],
                                     reverse=True)[:num_sentences]
        return [sentence for sentence, score in important_sentences]
    except Exception as e:
        logger.error(f"Error getting important sentences: {str(e)}")
        return []


def generate_summary(text, max_length=500):
    """Generate a summary of the text"""
    try:
        if not text:
            return "No text content found in the document."

        important_sentences = get_important_sentences(text)
        if not important_sentences:
            return "Could not generate summary from the document content."

        summary = ' '.join(important_sentences)

        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(' ', 1)[0] + '...'

        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return "Error generating summary."


def generate_questions(text):
    """Generate better contextual questions from the text"""
    try:
        # Use NLTK's punkt tokenizer for sentence splitting
        sentences = nltk.sent_tokenize(text)
        important_sentences = []

        # First pass: identify important sentences
        for sentence in sentences:
            if not sentence.strip():
                continue
            words = nltk.word_tokenize(sentence)
            pos_tags = nltk.pos_tag(words)

            # Check if sentence contains important elements
            if any(tag.startswith(('NN', 'VB', 'JJ')) for _, tag in pos_tags):
                important_sentences.append(sentence)

        questions = []
        for sentence in important_sentences[:5]:  # Limit to top 5 sentences
            try:
                words = word_tokenize(sentence)
                pos_tags = nltk.pos_tag(words)

                # Generate different types of questions based on sentence content
                if any(word.lower() in ['defines', 'means', 'refers', 'is', 'are'] for word in words):
                    # Definition question
                    for i, (word, tag) in enumerate(pos_tags):
                        if tag.startswith('NN') and i > 0:
                            questions.append({
                                "question": f"Can you explain what {word} is?",
                                "answer": sentence
                            })
                            break

                elif any(tag in ['NNP', 'NNPS'] for _, tag in pos_tags):
                    # Question about named entities
                    entity = next(word for word, tag in pos_tags if tag in ['NNP', 'NNPS'])
                    questions.append({
                        "question": f"What role does {entity} play in this context?",
                        "answer": sentence
                    })

                elif any(word.lower() in ['can', 'could', 'will', 'would'] for word in words):
                    # Capability question
                    questions.append({
                        "question": f"What capabilities or possibilities are mentioned in: {sentence}?",
                        "answer": sentence
                    })

                else:
                    # Extract key concepts
                    key_terms = [word for word, tag in pos_tags if tag.startswith('NN') and len(word) > 3]
                    if key_terms:
                        questions.append({
                            "question": f"What are the key points about {key_terms[0]}?",
                            "answer": sentence
                        })

            except Exception as e:
                logger.error(f"Error processing sentence: {str(e)}")
                continue

            if len(questions) >= 5:
                break

        # Always include a main topic question
        questions.insert(0, {
            "question": "What is the main topic of this document?",
            "answer": generate_summary(text, 300)
        })

        return questions[:6]  # Return at most 6 questions
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        return [{"question": "Error generating questions", "answer": str(e)}]


def analyze_document(file_stream, filename):
    """Main function to analyze a document"""
    try:
        logger.info(f"Starting analysis of document: {filename}")

        # Extract text from the document
        text = extract_text(file_stream, filename)

        if text is None:
            logger.error("Failed to extract text from document")
            return {
                "success": False,
                "message": "Failed to extract text from the document"
            }

        if not text.strip():
            logger.error("Extracted text is empty")
            return {
                "success": False,
                "message": "No text content found in the document"
            }

        # Generate summary and questions using pure Python/NLTK
        summary = generate_summary(text)
        questions = generate_questions(text)

        logger.info("Document analysis completed successfully")
        return {"success": True, "summary": summary, "questions": questions}

    except Exception as e:
        logger.error(f"Error in document analysis: {str(e)}")
        return {
            "success": False,
            "message": f"An error occurred during document analysis: {str(e)}"
        }