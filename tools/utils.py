import uuid
import json
import re

def generate_id(prefix: str = "doc") -> str:
    """Generate a unique ID with an optional prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def parse_json(text: str) -> dict:
    """
    Attempt to parse JSON from text, handling markdown code blocks.
    """
    try:
        # Look for markdown code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # If no code block, try finding anything that looks like { ... } or [ ... ]
        json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # Fallback to direct parse
        return json.loads(text)
    except Exception:
        return {}

def format_data(data: list) -> str:
    """Format a list of dicts for LLM consumption."""
    if not data: return "No data available."
    return json.dumps(data, indent=2)

def format_summary(data: list) -> str:
    """Create a high-level summary of records."""
    if not data: return "None"
    total = sum(float(item.get("total_amount", 0) or item.get("net_payable", 0) or item.get("net_receivable", 0) or 0) for item in data)
    return f"Count: {len(data)}, Total Value: {total:.2f}"

def format_detailed(data: list) -> str:
    """Format detailed records for analysis."""
    if not data: return "None"
    return json.dumps(data, indent=2)

def format_cheques_issued(cheques: list) -> str:
    issued = [c for c in cheques if c.get("type") == "issued" and c.get("status") != "cleared"]
    return format_detailed(issued)

def format_cheques_received(cheques: list) -> str:
    received = [c for c in cheques if c.get("type") == "received" and c.get("status") != "cleared"]
    return format_detailed(received)

def format_vendor_context(vendors: list) -> str:
    if not vendors: return "No vendor master data."
    return format_detailed(vendors)

def format_client_context(clients: list) -> str:
    if not clients: return "No client master data."
    return format_detailed(clients)
