from datetime import date, datetime
from opik import track
from config.characters import AgentCharacters
from tools.gemini_client import GeminiBrain
from tools.data_store import DataStore
from tools.models import AgentResponse
from tools.utils import (
    format_data, format_summary, format_detailed, 
    format_cheques_issued, format_cheques_received,
    format_vendor_context, format_client_context
)

class FinanceManagerAgent:
    def __init__(self):
        self.character = AgentCharacters.FINANCE_MANAGER_CHARACTER
        self.brain = GeminiBrain()
        self.data_store = DataStore()

    @track(name="arjun.analyze_cash")
    def analyze_cash_position(self) -> AgentResponse:
        """
        Arjun looks at the company's cash situation and assesses it.
        """
        # Gather all relevant data
        bank_accounts = self.data_store.get_all_bank_accounts()
        cheques = self.data_store.get_cheque_register()
        pending_payables = self.data_store.get_all_payables()
        pending_receivables = self.data_store.get_all_receivables()

        # Arjun thinks about the cash situation
        analysis = self.brain.think(
            character=self.character,
            context=f"""
BANK ACCOUNTS: {format_data(bank_accounts)}
CHEQUES ISSUED (not yet cleared): {format_cheques_issued(cheques)}
CHEQUES RECEIVED (not yet cleared): {format_cheques_received(cheques)}
PENDING PAYMENTS (what we owe): {format_summary(pending_payables)}
PENDING COLLECTIONS (what we're owed): {format_summary(pending_receivables)}
TODAY'S DATE: {date.today()}
""",
            question="""
Analyze our cash position. Think about:
1. What's our actual available cash right now?
2. What's our real liquidity (including credit lines)?
3. How does this compare to our near-term obligations?
4. Are we in a comfortable, tight, or critical situation?
5. What worries you most?
6. What's positive about the situation?

Give me your assessment as our Finance Manager. Be honest and direct.
"""
        )
        return analysis

    @track(name="arjun.recommend_payments")
    def recommend_payments(self, cash_analysis: str) -> AgentResponse:
        """
        Arjun decides which payments to make and which to hold.
        """
        payables = self.data_store.get_all_payables()
        vendors = self.data_store.get_all_vendors()

        recommendation = self.brain.think(
            character=self.character,
            context=f"""
CASH SITUATION: {cash_analysis}
PENDING PAYMENTS: {format_detailed(payables)}
VENDOR INFORMATION: {format_vendor_context(vendors)}
TODAY: {date.today()}
""",
            question="""
Which payments should we make and which should we hold? Think about:
1. What MUST be paid today? (statutory, salaries, critical)
2. What SHOULD be paid to avoid problems?
3. What CAN wait a few days?
4. What can we negotiate or delay?

For each payment, tell me:
- Pay now, or hold?
- Why?
- Any risks of your recommendation?

Remember: We need to survive today AND tomorrow. Be strategic, not just mechanical.

Format your response as:
- PAY NOW: (list with amounts and reasons)
- HOLD: (list with amounts and reasons)
- Total paying: X
- Cash remaining after: Y
"""
        )
        return recommendation

    @track(name="arjun.analyze_collections")
    def analyze_collections(self) -> AgentResponse:
        """
        Arjun reviews receivables and collection status.
        """
        receivables = self.data_store.get_all_receivables()
        clients = self.data_store.get_all_clients()

        analysis = self.brain.think(
            character=self.character,
            context=f"""
RECEIVABLES (what clients owe us): {format_detailed(receivables)}
CLIENT INFORMATION: {format_client_context(clients)}
TODAY: {date.today()}
""",
            question="""
Analyze our collection situation. Think about:
1. What's our total outstanding?
2. What's overdue and by how much?
3. Which collections are likely to come soon?
4. Which ones are you worried about?
5. Who should we follow up with and how?

For overdue amounts:
- Is this normal for this client or concerning?
- What action do you recommend?

Give me a practical assessment.
"""
        )
        return analysis

    @track(name="arjun.answer_question")
    def answer_question(self, question: str) -> AgentResponse:
        """
        Arjun answers any finance-related question.
        """
        # Gather relevant context
        context = self._gather_relevant_context(question)
        answer = self.brain.think(
            character=self.character,
            context=context,
            question=question
        )
        return answer

    def _gather_relevant_context(self, question: str) -> str:
        """
        Arjun figures out what data he needs to answer the question.
        """
        # Ask Arjun what data he needs
        data_needs = self.brain.think(
            character=self.character,
            context=f"Question: {question}",
            question="What data do you need to answer this question? Just name the data types if possible (e.g., bank accounts, vendors, payables)."
        )
        
        # Simple fetch logic: if it's in the response, get it.
        # This is a basic implementation of Arjun's "thinking" about what he needs.
        needs = data_needs.response.lower()
        context_parts = []
        
        if "bank" in needs or "cash" in needs:
            context_parts.append(f"BANK ACCOUNTS: {format_data(self.data_store.get_all_bank_accounts())}")
        if "vendor" in needs or "payment" in needs or "payable" in needs:
            context_parts.append(f"PAYABLES: {format_summary(self.data_store.get_all_payables())}")
            context_parts.append(f"VENDORS: {format_vendor_context(self.data_store.get_all_vendors())}")
        if "client" in needs or "collection" in needs or "receivable" in needs:
            context_parts.append(f"RECEIVABLES: {format_summary(self.data_store.get_all_receivables())}")
            context_parts.append(f"CLIENTS: {format_client_context(self.data_store.get_all_clients())}")
            
        return "\n\n".join(context_parts) if context_parts else "No specific context gathered."

    @track(name="arjun.analyze_goals")
    def analyze_financial_goals(self) -> AgentResponse:
        """
        Arjun reviews progress towards financial goals.
        """
        goals = self.data_store.get_financial_goals()
        if not goals:
            return AgentResponse(
                agent_name="Arjun",
                query="Analyze financial goals",
                thinking="No goals found.",
                response="We haven't set any financial goals yet. I recommend we set some targets for emergency funds or specific purchases.",
                confidence=1.0,
                needs_human_review=False,
                timestamp=datetime.now()
            )

        # Calculate current liquid assets for context
        total_cash = self.data_store.get_total_bank_balance()
        
        analysis = self.brain.think(
            character=self.character,
            context=f"""
FINANCIAL GOALS: {format_data(goals)}
TOTAL LIQUID CASH AVAILABLE: {total_cash}
TODAY: {date.today()}
""",
            question="""
Analyze our progress towards these financial goals.
1. Are we on track?
2. Which goals are at risk?
3. Do we have enough cash to allocate towards them?
4. What specific action should we take this week to get closer to our goals?

Explain your reasoning in plain language (for financial literacy).
"""
        )
        return analysis
