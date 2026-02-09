
import os
import sys
from datetime import datetime, date
from tools.data_store import DataStore
from agents.finance_manager import FinanceManagerAgent
from agents.cfo_brain import CFOBrainAgent
from tools.models import FinancialGoal

def verify_hackathon_criteria():
    print("🚀 Verifying Hackathon Criteria...")
    
    ds = DataStore()
    
    # 1. Goal Alignment: Add a financial goal
    print("\n--- 1. Testing Financial Goal Creation ---")
    goal = {
        "goal_id": "goal_001",
        "description": "Build Emergency Fund",
        "target_amount": 50000.0,
        "current_amount": 0.0, # Will be checked against bank balance
        "deadline": datetime(2025, 12, 31),
        "status": "In Progress",
        "strategy": "Save 10% of every invoice"
    }
    # Clean up old goal if exists
    if 'financial_goals' in ds.data:
        ds.data['financial_goals'] = [g for g in ds.data['financial_goals'] if g['goal_id'] != 'goal_001']
        ds._save_data()
        
    ds.add_financial_goal(goal)
    print("✅ Financial Goal Added.")
    
    # 2. Real-world Relevance: Check progress
    print("\n--- 2. Testing Goal Analysis (Finance Manager) ---")
    fm = FinanceManagerAgent()
    try:
        # Mocking bank balance if 0 to show progress
        if ds.get_total_bank_balance() == 0:
            ds.update_bank_balance("acc_001", 15000.0) # Mock balance
            print("Note: Added mock balance for testing.")
            
        analysis = fm.analyze_financial_goals()
        print(f"Goal Analysis:\n{analysis.response}")
        print("✅ Goal Analysis Working.")
    except Exception as e:
        print(f"❌ Goal Analysis Failed: {e}")

    # 3. Use of LLMs/Agents: Daily Briefing Integration
    print("\n--- 3. Testing Daily Briefing Integration (CFO Brain) ---")
    cfo = CFOBrainAgent()
    try:
        briefing = cfo.create_daily_briefing()
        print(f"Briefing Preview (needs to mention goals):\n{briefing['briefing'][:200]}...")
        if "goal" in briefing['briefing'].lower() or "emergency" in briefing['briefing'].lower():
             print("✅ Goals successfully integrated into briefing.")
        else:
             print("⚠️ Goals might not be explicitly mentioned (check full output).")
    except Exception as e:
        print(f"❌ Briefing Failed: {e}")

    # 4. Evaluation & Observability: Feedback Loop
    print("\n--- 4. Testing Opik Feedback Loop ---")
    try:
        # Simulate human approval
        response_text = "Yes, approve the payments."
        
        # We need pending context for it to make sense, but for unit test, explicit approval is enough
        result = cfo.process_human_response(response_text, {})
        print(f"Processed Response: {result['understanding']}")
        print("✅ Feedback processed (check Opik dashboard for 'human_feedback' trace).")
    except Exception as e:
        print(f"❌ Feedback Loop Failed: {e}")

if __name__ == "__main__":
    verify_hackathon_criteria()
