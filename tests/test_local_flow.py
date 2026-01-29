import os
import sys
import unittest
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.data_store import DataStore
from agents.finance_manager import FinanceManagerAgent

class TestLocalFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
        if not os.getenv("GEMINI_API_KEY"):
            raise unittest.SkipTest("GEMINI_API_KEY not found in .env")

    def test_01_json_integrity(self):
        """Step 1: Verify local JSON database integrity."""
        print("\n[STEP 1] Checking database.json content...")
        try:
            db = DataStore()
            self.assertIsNotNone(db.data)
            self.assertIn("bank_accounts", db.data)
            print(f"✅ Database loaded. Found {len(db.data.get('bank_accounts', []))} bank accounts.")
        except Exception as e:
            self.fail(f"Failed to load database.json: {e}")

    def test_02_agent_reasoning(self):
        """Step 2: Verify Finance Manager can reason with local JSON data."""
        print("\n[STEP 2] Testing Agent reasoning with local JSON data...")
        fm = FinanceManagerAgent()
        
        try:
            # Analyze cash position from JSON
            analysis = fm.analyze_cash_position()
            print(f"Arjun's Cash Analysis: {analysis.response[:150]}...")
            self.assertIsNotNone(analysis.response)
            self.assertGreater(len(analysis.response), 0)
            print("✅ Agent successfully reasoned using local data.")
        except Exception as e:
            self.fail(f"Agent reasoning failed: {e}")

if __name__ == "__main__":
    unittest.main()
