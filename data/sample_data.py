from datetime import datetime, timedelta

SAMPLE_BANK_ACCOUNTS = [
    {
        "account_id": "acc_001",
        "bank_name": "HDFC Bank",
        "account_number": "XXXX1234",
        "account_type": "Current",
        "balance": 2800000.0,
        "cc_limit": 5000000.0,
        "last_updated": datetime.now().isoformat()
    }
]

SAMPLE_VENDORS = [
    {
        "vendor_id": "ven_001",
        "name": "UltraTech Cement",
        "gstin": "27AAACU1234A1Z1",
        "category": "Raw Material",
        "credit_days": 30,
        "is_active": True
    }
]

SAMPLE_PAYABLES = [
    {
        "invoice_id": "inv_p_001",
        "vendor_id": "ven_001",
        "vendor_name": "UltraTech Cement",
        "total_amount": 4500000.0,
        "due_date": (datetime.now() + timedelta(days=2)).isoformat(),
        "status": "pending"
    }
]

SAMPLE_RECEIVABLES = [
    {
        "invoice_id": "inv_r_001",
        "client_name": "Lodha Group",
        "total_amount": 1500000.0,
        "due_date": (datetime.now() - timedelta(days=5)).isoformat(),
        "status": "overdue"
    }
]
