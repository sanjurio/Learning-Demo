"""
Simple script to test the document analysis functionality without using the web UI
"""
import os
import sys
import io
from document_analysis import analyze_document

def test_document_analysis():
    """Test the document analysis functionality"""
    print("Testing document analysis...")
    
    # Check if OpenAI API key is set
    openai_key = os.environ.get('OPENAI_API_KEY')
    if not openai_key:
        print("ERROR: OPENAI_API_KEY is not set in environment variables")
        return False
    
    print(f"OpenAI API key available: {openai_key[:5]}...{openai_key[-4:]}")
    
    # Create a simple text file in memory
    sample_text = """
    Artificial Intelligence (AI) is revolutionizing various industries, from healthcare to finance. 
    Machine learning, a subset of AI, enables computers to learn from data and improve over time without explicit programming. 
    Deep learning, a more advanced technique, utilizes neural networks with many layers to process complex patterns.
    Natural Language Processing (NLP) is another important area of AI that focuses on enabling computers to understand, interpret, and generate human language.
    Computer vision allows machines to interpret and make decisions based on visual data, similar to human vision.
    Reinforcement learning is a type of machine learning where an agent learns to make decisions by taking actions in an environment to maximize some notion of cumulative reward.
    """
    
    # Convert string to file-like object
    file_stream = io.BytesIO(sample_text.encode('utf-8'))
    
    # Analyze the document
    result = analyze_document(file_stream, "sample_text.txt")
    
    # Print results
    print("\nAnalysis Result:")
    print(f"Success: {result['success']}")
    
    if result['success']:
        print("\nSummary:")
        print(result['summary'])
        
        print("\nAI Analysis Used:", result['ai_analysis'])
        
        print("\nQuestions:")
        if isinstance(result['questions'], list):
            for q in result['questions']:
                print(f"- {q}")
        else:
            print(result['questions'])
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")
    
    return result['success']

if __name__ == "__main__":
    success = test_document_analysis()
    sys.exit(0 if success else 1)