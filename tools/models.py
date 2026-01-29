from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class BankAccount(BaseModel):
    account_id: str
    bank_name: str
    account_number: str
    account_type: str
    balance: float
    cc_limit: Optional[float] = None
    last_updated: datetime

class Vendor(BaseModel):
    vendor_id: str
    name: str
    gstin: str
    category: str
    bank_account: str
    ifsc: str
    credit_days: int
    contact_person: str
    contact_phone: str
    is_active: bool = True

class Client(BaseModel):
    client_id: str
    name: str
    client_type: str
    gstin: str
    payment_terms_days: int
    avg_payment_days: float
    contact_person: str
    contact_phone: str
    contact_email: str

class PayableInvoice(BaseModel):
    invoice_id: str
    vendor_id: str
    vendor_name: str
    invoice_number: str
    invoice_date: datetime
    due_date: datetime
    base_amount: float
    gst_amount: float
    total_amount: float
    tds_amount: float
    net_payable: float
    project_id: str
    status: str

class ReceivableInvoice(BaseModel):
    invoice_id: str
    client_id: str
    client_name: str
    project_id: str
    invoice_number: str
    invoice_date: datetime
    due_date: datetime
    base_amount: float
    gst_amount: float
    total_amount: float
    tds_deducted: float
    retention_held: float
    net_receivable: float
    amount_received: float
    balance_due: float
    status: str

class DocumentExtraction(BaseModel):
    document_id: str
    document_type: str
    file_name: str
    processed_at: datetime
    raw_text: str
    extracted_data: Dict[str, Any]
    confidence_notes: str

class AgentResponse(BaseModel):
    agent_name: str
    query: str
    thinking: str
    response: str
    confidence: float
    needs_human_review: bool
    timestamp: datetime
