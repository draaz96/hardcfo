from datetime import date
from opik import track
from config.characters import AgentCharacters
from tools.gemini_client import GeminiBrain
from tools.data_store import DataStore
from agents.doc_processor import DocProcessorAgent
from agents.finance_manager import FinanceManagerAgent

class CFOBrainAgent:
    def __init__(self):
        self.character = AgentCharacters.CFO_BRAIN_CHARACTER
        self.brain = GeminiBrain()
        self.doc_processor = DocProcessorAgent()
        self.finance_manager = FinanceManagerAgent()
        self.data_store = DataStore()

    @track(name="rajesh.daily_briefing")
    def create_daily_briefing(self) -> dict:
        """
        Rajesh creates the morning briefing for himself/human.
        """
        # Get input from Finance Manager
        cash_analysis = self.finance_manager.analyze_cash_position()
        payment_reco = self.finance_manager.recommend_payments(cash_analysis.response)
        collection_status = self.finance_manager.analyze_collections()

        # Rajesh synthesizes everything
        briefing = self.brain.think(
            character=self.character,
            context=f"""
FINANCE MANAGER'S CASH ANALYSIS: {cash_analysis.response}
FINANCE MANAGER'S PAYMENT RECOMMENDATIONS: {payment_reco.response}
FINANCE MANAGER'S COLLECTION STATUS: {collection_status.response}
TODAY: {date.today()}
DAY: {date.today().strftime('%A')}
""",
            question="""
As CFO, prepare your daily briefing. Think about:
1. What's the ONE thing I must focus on today?
2. What decisions need to be made right now?
3. What can wait?
4. Any red flags I should be worried about?
5. Any good news?

Create a briefing that:
- Starts with the most important thing
- Is clear about what needs my decision
- Gives me enough context to decide
- Doesn't waste my time with details I don't need

Format it for a busy person reading on their phone.
"""
        )

        # Rajesh identifies what needs human decision
        actions = self.brain.think(
            character=self.character,
            context=f"My briefing: {briefing.response}",
            question="""
What specific decisions/approvals do I need from the human?
For each decision:
- What is the decision?
- What are the options?
- What do I recommend?
- How should they respond?

Format as a clear list of action items.
"""
        )

        return {
            "briefing": briefing.response,
            "actions_needed": actions.response,
            "cash_analysis": cash_analysis.response,
            "payment_reco": payment_reco.response,
            "collection_status": collection_status.response
        }

    @track(name="rajesh.handle_document")
    def handle_new_document(self, file_path: str) -> dict:
        """
        Rajesh handles a newly uploaded document.
        """
        # Get Doc Processor to read it
        extraction = self.doc_processor.process(file_path)

        # Rajesh decides what to do with it
        decision = self.brain.think(
            character=self.character,
            context=f"""
A new document was uploaded.
DOCUMENT TYPE: {extraction.document_type}
EXTRACTED DATA: {extraction.extracted_data}
CONFIDENCE NOTES: {extraction.confidence_notes}
""",
            question="""
What should we do with this document? Think about:
1. Is the extraction reliable?
2. Should this go into our system automatically?
3. Does a human need to verify anything?
4. Any immediate actions needed?
5. How should I inform the human CFO?

Give me your decision and reasoning.
"""
        )

        return {
            "extraction": extraction,
            "cfo_decision": decision.response
        }

    @track(name="rajesh.process_response")
    def process_human_response(
        self, 
        response: str, 
        pending_context: dict
    ) -> dict:
        """
        Rajesh processes what the human said.
        """
        understanding = self.brain.think(
            character=self.character,
            context=f"""
WHAT WE ASKED THE HUMAN: {pending_context.get('actions_needed', '')}
HUMAN'S RESPONSE: {response}
""",
            question="""
What is the human telling us? Think about:
1. What did they approve or reject?
2. Did they modify anything?
3. Did they ask for more information?
4. What actions should we take now?

If their response is unclear, what should we ask?

Give me:
- What I understood
- Actions to take
- Confirmation message to send back
"""
        )

        return {
            "understanding": understanding.response,
            "needs_clarification": "unclear" in understanding.response.lower()
        }

    @track(name="rajesh.handle_unusual")
    def handle_unusual_situation(self, situation: str, data: dict) -> dict:
        """
        Rajesh handles anything that doesn't fit normal patterns.
        """
        decision = self.brain.think(
            character=self.character,
            context=f"""
UNUSUAL SITUATION: {situation}
RELEVANT DATA: {data}
""",
            question="""
This is an unusual situation. How should we handle it? Think about:
1. What's the risk if we do nothing?
2. What's the safest action?
3. Should I involve the human CFO?
4. Is this urgent or can it wait?

When in doubt, I prefer to ask the human rather than guess.
"""
        )
        return {"decision": decision.response}
