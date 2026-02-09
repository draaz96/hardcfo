
import time
from unittest.mock import MagicMock
from tools.gemini_client import GeminiBrain
from datetime import datetime

class MockResponse:
    def __init__(self, text):
        self.text = text

def test_retry_logic():
    print("🚀 Testing Improved Gemini Client Retry Logic...")
    
    # 1. Setup Mock
    # We need to bypass __init__ because it requires API key which might not be set
    brain = GeminiBrain.__new__(GeminiBrain)
    brain.model = MagicMock()
    
    # 2. Simulate Rate Limit (429) then Success
    error = Exception("429 Resource exhausted")
    success_response = MockResponse("Success!")
    
    # Side effect: Raise error twice, then return success
    brain.model.generate_content.side_effect = [error, error, success_response]
    
    start_time = time.time()
    try:
        print("Intentional fail: Triggering rate limit simulation...")
        response = brain._generate_with_retry(brain.model.generate_content, "test prompt")
        end_time = time.time()
        
        print(f"✅ Success! Response received: {response.text}")
        print(f"⏱️ Total time taken: {end_time - start_time:.2f}s (Should be > 6s due to backoff)")
        
        if (end_time - start_time) > 4:
            print("✅ Backoff logic verified.")
        else:
            print("❌ Backoff too fast.")
            
    except Exception as e:
        print(f"❌ Failed to handle retry: {e}")

if __name__ == "__main__":
    test_retry_logic()
