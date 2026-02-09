"""
Data Store - Reads and writes to JSON database
This replaces Google Sheets connector
"""

import json
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Optional, Any


class DataStore:
    """
    Simple JSON-based data store.
    All data lives in data/database.json
    """
    
    def __init__(self, db_path: str = "data/database.json"):
        self.db_path = Path(db_path)
        self._load_data()
    
    def _load_data(self):
        """Load data from JSON file"""
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            raise FileNotFoundError(f"Database not found at {self.db_path}")
    
    def _save_data(self):
        """Save data back to JSON file"""
        # Update metadata
        self.data['metadata']['last_updated'] = datetime.now().isoformat()
        
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False, default=str)
    
    def refresh(self):
        """Reload data from file"""
        self._load_data()
    
    # ============ READ METHODS ============
    
    def get_company_info(self) -> Dict:
        """Get company information"""
        return self.data.get('company', {})
    
    def get_all_bank_accounts(self) -> List[Dict]:
        """Get all bank accounts"""
        return self.data.get('bank_accounts', [])
    
    def get_bank_account(self, account_id: str) -> Optional[Dict]:
        """Get specific bank account by ID"""
        for account in self.data.get('bank_accounts', []):
            if account['account_id'] == account_id:
                return account
        return None
    
    def get_all_vendors(self) -> List[Dict]:
        """Get all vendors"""
        return self.data.get('vendors', [])
    
    def get_active_vendors(self) -> List[Dict]:
        """Get only active vendors"""
        return [v for v in self.data.get('vendors', []) if v.get('is_active', True)]
    
    def get_vendor(self, vendor_id: str) -> Optional[Dict]:
        """Get specific vendor by ID"""
        for vendor in self.data.get('vendors', []):
            if vendor['vendor_id'] == vendor_id:
                return vendor
        return None
    
    def get_vendor_by_name(self, name: str) -> Optional[Dict]:
        """Find vendor by name (partial match)"""
        name_lower = name.lower()
        for vendor in self.data.get('vendors', []):
            if name_lower in vendor['name'].lower():
                return vendor
        return None
    
    def get_all_clients(self) -> List[Dict]:
        """Get all clients"""
        return self.data.get('clients', [])
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Get specific client by ID"""
        for client in self.data.get('clients', []):
            if client['client_id'] == client_id:
                return client
        return None
    
    def get_client_by_name(self, name: str) -> Optional[Dict]:
        """Find client by name (partial match)"""
        name_lower = name.lower()
        for client in self.data.get('clients', []):
            if name_lower in client['name'].lower():
                return client
        return None
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects"""
        return self.data.get('projects', [])
    
    def get_active_projects(self) -> List[Dict]:
        """Get only active projects"""
        return [p for p in self.data.get('projects', []) if p.get('status') == 'Active']
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get specific project by ID"""
        for project in self.data.get('projects', []):
            if project['project_id'] == project_id:
                return project
        return None
    
    def get_all_payables(self) -> List[Dict]:
        """Get all payable invoices"""
        return self.data.get('payables', [])
    
    def get_pending_payables(self) -> List[Dict]:
        """Get pending payables (not paid)"""
        return [p for p in self.data.get('payables', []) 
                if p.get('status') not in ['Paid', 'Cancelled']]
    
    def get_overdue_payables(self) -> List[Dict]:
        """Get overdue payables"""
        return [p for p in self.data.get('payables', []) 
                if p.get('status') == 'Overdue']
    
    def get_all_receivables(self) -> List[Dict]:
        """Get all receivable invoices"""
        return self.data.get('receivables', [])
    
    def get_pending_receivables(self) -> List[Dict]:
        """Get pending receivables (not fully paid)"""
        return [r for r in self.data.get('receivables', []) 
                if r.get('status') not in ['Paid', 'Cancelled']]
    
    def get_overdue_receivables(self) -> List[Dict]:
        """Get overdue receivables"""
        return [r for r in self.data.get('receivables', []) 
                if r.get('status') == 'Overdue']
    
    def get_financial_goals(self) -> List[Dict]:
        """Get all financial goals"""
        return self.data.get('financial_goals', [])
    
    def get_cheque_register(self) -> List[Dict]:
        """Get all cheques"""
        return self.data.get('cheque_register', [])
    
    def get_pending_cheques_issued(self) -> List[Dict]:
        """Get cheques issued but not cleared"""
        return [c for c in self.data.get('cheque_register', []) 
                if c.get('type') == 'Issued' and c.get('status') == 'Pending']
    
    def get_pending_cheques_received(self) -> List[Dict]:
        """Get cheques received but not cleared"""
        return [c for c in self.data.get('cheque_register', []) 
                if c.get('type') == 'Received' and c.get('status') == 'Pending']
    
    def get_metadata(self) -> Dict:
        """Get database metadata"""
        return self.data.get('metadata', {})
    
    # ============ SUMMARY METHODS ============
    
    def get_total_bank_balance(self) -> float:
        """Get total of all bank balances"""
        return sum(acc.get('balance', 0) for acc in self.get_all_bank_accounts())
    
    def get_pending_cheques_summary(self) -> Dict:
        """Get summary of pending cheques"""
        issued = sum(c['amount'] for c in self.get_pending_cheques_issued())
        received = sum(c['amount'] for c in self.get_pending_cheques_received())
        return {'issued': issued, 'received': received}
    
    def get_total_pending_payables(self) -> float:
        """Get total pending payables amount"""
        return sum(p.get('net_payable', 0) for p in self.get_pending_payables())
    
    def get_total_pending_receivables(self) -> float:
        """Get total pending receivables amount"""
        return sum(r.get('balance_due', 0) for r in self.get_pending_receivables())
    
    # ============ WRITE METHODS ============
    
    def add_payable(self, payable: Dict) -> bool:
        """Add new payable invoice"""
        try:
            self.data['payables'].append(payable)
            self._save_data()
            return True
        except Exception as e:
            print(f"Error adding payable: {e}")
            return False
    
    def update_payable(self, invoice_id: str, updates: Dict) -> bool:
        """Update existing payable"""
        try:
            for i, p in enumerate(self.data['payables']):
                if p['invoice_id'] == invoice_id:
                    self.data['payables'][i].update(updates)
                    self._save_data()
                    return True
            return False
        except Exception as e:
            print(f"Error updating payable: {e}")
            return False
    
    def add_receivable(self, receivable: Dict) -> bool:
        """Add new receivable invoice"""
        try:
            self.data['receivables'].append(receivable)
            self._save_data()
            return True
        except Exception as e:
            print(f"Error adding receivable: {e}")
            return False
    
    def update_receivable(self, invoice_id: str, updates: Dict) -> bool:
        """Update existing receivable"""
        try:
            for i, r in enumerate(self.data['receivables']):
                if r['invoice_id'] == invoice_id:
                    self.data['receivables'][i].update(updates)
                    self._save_data()
                    return True
            return False
        except Exception as e:
            print(f"Error updating receivable: {e}")
            return False
    
    def update_bank_balance(self, account_id: str, new_balance: float) -> bool:
        """Update bank account balance"""
        try:
            for i, acc in enumerate(self.data['bank_accounts']):
                if acc['account_id'] == account_id:
                    self.data['bank_accounts'][i]['balance'] = new_balance
                    self.data['bank_accounts'][i]['last_updated'] = date.today().isoformat()
                    self._save_data()
                    return True
            return False
        except Exception as e:
            print(f"Error updating bank balance: {e}")
            return False

    def add_financial_goal(self, goal: Dict) -> bool:
        """Add new financial goal"""
        try:
            if 'financial_goals' not in self.data:
                self.data['financial_goals'] = []
            self.data['financial_goals'].append(goal)
            self._save_data()
            return True
        except Exception as e:
            print(f"Error adding financial goal: {e}")
            return False

    def update_financial_goal(self, goal_id: str, updates: Dict) -> bool:
        """Update existing financial goal"""
        try:
            if 'financial_goals' not in self.data:
                return False
            for i, g in enumerate(self.data['financial_goals']):
                if g['goal_id'] == goal_id:
                    self.data['financial_goals'][i].update(updates)
                    self._save_data()
                    return True
            return False
        except Exception as e:
            print(f"Error updating financial goal: {e}")
            return False


# ============ FORMATTING HELPERS ============

def format_currency(amount: float) -> str:
    """Format amount in Indian style (lakhs/crores)"""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.0f}"


def format_data_for_llm(data: Any) -> str:
    """Format data nicely for LLM consumption"""
    if isinstance(data, list):
        if len(data) == 0:
            return "No data"
        
        result = []
        for item in data:
            if isinstance(item, dict):
                formatted_item = []
                for key, value in item.items():
                    if 'amount' in key.lower() or 'balance' in key.lower() or 'payable' in key.lower() or 'receivable' in key.lower():
                        formatted_item.append(f"  {key}: {format_currency(value) if value else 'N/A'}")
                    else:
                        formatted_item.append(f"  {key}: {value}")
                result.append("\n".join(formatted_item))
            else:
                result.append(str(item))
        return "\n---\n".join(result)
    
    elif isinstance(data, dict):
        result = []
        for key, value in data.items():
            if 'amount' in key.lower() or 'balance' in key.lower():
                result.append(f"{key}: {format_currency(value) if value else 'N/A'}")
            else:
                result.append(f"{key}: {value}")
        return "\n".join(result)
    
    else:
        return str(data)