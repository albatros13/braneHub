import os
import sys
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

from pypdf import PdfReader
from api.qdrant_remote_client import build_text_index_remote, ask

def test_vectorize_gdpr():
    project_root = os.path.dirname(os.path.dirname(__file__))
    pdf_path = os.path.join(project_root, "static", "resources", "gdpr.pdf")
    
    assert os.path.exists(pdf_path), f"PDF file not found at {pdf_path}"
    
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    collection_name = "gdpr_test_collection"
    build_text_index_remote(text, collection_name=collection_name)
    
    question = "What are the data subject rights under GDPR?"
    answers = ask(question, collection_name=collection_name)
    
    print(f"\nQuestion: {question}")
    print("\nTop Answers:\n")
    for score, text in answers:
        print(f"- Score {score:.4f} → {text[:300]}...\n")
    
    assert len(answers) > 0
    assert any("right" in text.lower() for _, text in answers)

if __name__ == "__main__":
    test_vectorize_gdpr()
