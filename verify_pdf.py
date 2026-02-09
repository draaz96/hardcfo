from tools.gemini_client import GeminiBrain
import os

def test_pdf_processing():
    print("Testing PDF Processing...")
    
    # Use the existing PDF file
    pdf_path = "data/6ea9510a-e0a9-49ed-a49c-b1b020597599_project_master.pdf"
    
    # If file doesn't exist, we can't test
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        # Try to find any pdf in data/
        files = [f for f in os.listdir("data") if f.endswith(".pdf")]
        if files:
            pdf_path = os.path.join("data", files[0])
            print(f"Using alternative file: {pdf_path}")
        else:
            print("No PDF files found in data/ to test with.")
            return

    brain = GeminiBrain()
    
    response = brain.see_and_think(
        character="You are a helpful assistant.",
        image_path=pdf_path,
        question="What type of document is this? Summarize it in one sentence."
    )
    
    print("\n--- RESPONSE ---")
    print(response.response)
    print("----------------")

if __name__ == "__main__":
    test_pdf_processing()
