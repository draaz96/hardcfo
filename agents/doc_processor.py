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
        She doesn't follow rules - she THINKS about what she sees.
        """
        # Step 1: Meera looks at the document
        visual_analysis = self.brain.see_and_think(
            character=self.character,
            image_path=file_path,
            question="""
            Look at this document carefully.
            1. What type of document is this? (vendor invoice, customer invoice, bank statement, cheque, receipt, or something else)
            2. What is the overall quality? Can you read everything?
            3. Give me a summary of what you see. Take your time and be thorough.
            """
        )

        # Step 2: Based on document type, Meera extracts details
        extraction = self.brain.see_and_think(
            character=self.character,
            image_path=file_path,
            question=f"""
            You identified this as: {visual_analysis.response}
            Now extract ALL the important financial information. Look for:
            - Names (vendor/client/bank)
            - Numbers (invoice number, account number)
            - Dates (invoice date, due date)
            - Amounts (base amount, taxes, total)
            - Any reference numbers (PO, project, etc)

            For each piece of information:
            - What is the value?
            - How confident are you? (certain/likely/unsure)
            - Any concerns about this value?

            Give me a complete extraction. Format as JSON.
            """
        )

        # Step 3: Meera validates what she found
        validation = self.brain.think(
            character=self.character,
            context=f"Extracted data: {extraction.response}",
            question="""
            Review what you extracted.
            1. Do the numbers add up? (base + gst = total?)
            2. Are the dates sensible?
            3. Does anything look suspicious?
            4. Is any critical information missing?
            5. Should a human double-check anything?

            Give your validation assessment.
            """
        )

        # Return the extraction
        return DocumentExtraction(
            document_id=generate_id(),
            document_type=visual_analysis.response,
            file_name=file_path,
            processed_at=datetime.now(),
            raw_text=visual_analysis.response,
            extracted_data=parse_json(extraction.response),
            confidence_notes=validation.response
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
