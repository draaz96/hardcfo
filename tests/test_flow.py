import os
import sys
import unittest
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.verify_sheets import verify
from tools.sync_sheets_to_json import sync
from tools.data_store import DataStore as JSONDataStore
from agents.finance_manager import FinanceManagerAgent

class TestFullFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
        # Ensure we have a .env file and essential keys
        if not os.getenv("GEMINI_API_KEY"):
            raise unittest.SkipTest("GEMINI_API_KEY not found in .env")

    def test_01_sheets_connection(self):
        """Step 1: Verify Google Sheets connection."""
        print("\n[STEP 1] Verifying Google Sheets connection...")
        self.assertTrue(verify(), "Google Sheets connection failed. Check credentials and spreadsheet ID.")

    def test_02_data_sync(self):
        """Step 2: Synchronize data from Sheets to JSON."""
        print("\n[STEP 2] Synchronizing data to database.json...")
        self.assertTrue(sync(), "Data synchronization failed.")

    def test_03_json_integrity(self):
        """Step 3: Verify local JSON database integrity."""
        print("\n[STEP 3] Checking database.json content...")
        db = JSONDataStore()
        self.assertIsNotNone(db.data)
        self.assertIn("bank_accounts", db.data)
        self.assertIn("vendors", db.data)
        
        # Check if we actually have some data (assuming the sheet isn't empty)
        if len(db.data["bank_accounts"]) > 0:
            print(f"Found {len(db.data['bank_accounts'])} bank accounts in local database.")

    def test_04_agent_reasoning(self):
        """Step 4: Verify Finance Manager can reason with synched data."""
        print("\n[STEP 4] Testing Agent reasoning with synched data...")
        fm = FinanceManagerAgent()
        # We manually bridge Arjun to use the JSON data store if he doesn't by default
        # Note: FinanceManagerAgent in its current form uses tools.sheets_connector.DataStore
        # To test the JSON sync, we temporarily point him to the JSON data store if needed.
        
        # However, to be extra safe and test the 'database.json' as requested:
        from tools.data_store import DataStore as JSONStore
        fm.data_store = JSONStore() # Swap to JSON store for this test
        
        try:
            analysis = fm.analyze_cash_position()
            print(f"Arjun's Cash Analysis: {analysis.response[:100]}...")
            self.assertIsNotNone(analysis.response)
            self.assertGreater(len(analysis.response), 0)
        except Exception as e:
            self.fail(f"Agent reasoning failed: {e}")

if __name__ == "__main__":
    unittest.main()
