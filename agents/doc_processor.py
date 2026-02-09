from datetime import datetime
from opik import track
from config.characters import AgentCharacters
from tools.gemini_client import GeminiBrain
from tools.data_store import DataStore
from tools.models import DocumentExtraction, AgentResponse
from tools.utils import generate_id, parse_json

class DocProcessorAgent:
    def __init__(self):
        self.character = AgentCharacters.DOC_PROCESSOR_CHARACTER
        self.brain = GeminiBrain()
        self.data_store = DataStore()

    @track(name="meera.process_document")
    def process(self, file_path: str) -> DocumentExtraction:
        """
        Meera looks at a document and extracts information.
        Optimized to do identification, extraction, and validation in ONE step.
        """
        # Single consolidated step: Identify -> Extract -> Validate
        analysis = self.brain.see_and_think(
            character=self.character,
            image_path=file_path,
            question="""
            Analyze this document completely.
            
            PART 1: IDENTIFICATION
            - What type of document is this? (invoice, receipt, bank statement, etc)
            - Is it readable?
            
            PART 2: EXTRACTION
            Extract ALL financial details as a JSON object inside the response. Look for:
            - key_dates (date, due_date)
            - entities (vendor_name, client_name, bank_name)
            - amounts (base_amount, tax_amount, total_amount)
            - references (invoice_number, po_number)
            - line_items (summary of what was bought/sold)
            
            PART 3: VALIDATION
            - Do the numbers add up? (base + tax = total)
            - Are dates valid?
            - Any warning flags?
            
            OUTPUT FORMAT:
            Provide your thinking process first, then output the final extraction as a valid JSON object.
            The JSON should have this structure:
            {
                "document_type": "...",
                "extracted_data": { ... },
                "validation_notes": "...",
                "confidence_score": 0.0 to 1.0
            }
            """
        )

        # Parse the result
        result_json = self.brain.extract_json(analysis.response)
        
        # Fallback if JSON parsing fails or keys are missing - try to find type in text
        doc_type = result_json.get("document_type")
        if not doc_type:
            # Fallback: Guess based on text content
            lower_text = analysis.response.lower()
            if "invoice" in lower_text:
                doc_type = "invoice"
            elif "statement" in lower_text:
                doc_type = "bank_statement"
            elif "receipt" in lower_text:
                doc_type = "receipt"
            else:
                doc_type = "unknown_document"

        extracted_data = result_json.get("extracted_data", {})
        validation_notes = result_json.get("validation_notes", analysis.response[:200]) # Fallback to raw text

        # Return the extraction
        return DocumentExtraction(
            document_id=generate_id(),
            document_type=doc_type,
            file_name=file_path,
            processed_at=datetime.now(),
            raw_text=analysis.response,
            extracted_data=extracted_data,
            confidence_notes=validation_notes
        )

    def match_vendor(self, vendor_name: str) -> dict:
        """
        Meera tries to match extracted vendor with known vendors.
        """
        vendors = self.data_store.get_all_vendors()
        match_result = self.brain.think(
            character=self.character,
            context=f"""
            Extracted vendor name: {vendor_name}
            Known vendors in our system: {vendors}
            """,
            question="""
            Is this vendor already in our system? Look for:
            - Exact matches
            - Partial matches (abbreviations, spelling variations)
            - Similar sounding names
            
            If you find a match, which one and how confident?
            If no match, this might be a new vendor.
            Give your answer as a JSON object with keys: matched_vendor (null if none), confidence, and notes.
            """
        )
        return parse_json(match_result.response)
