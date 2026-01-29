import os
import json
from datetime import datetime
from opik import track
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config.characters import AgentCharacters
from tools.gemini_client import GeminiBrain
from agents.cfo_brain import CFOBrainAgent
from tools.utils import parse_json
from dotenv import load_dotenv

load_dotenv()

class HumanInterfaceAgent:
    def __init__(self):
        self.character = AgentCharacters.HUMAN_INTERFACE_CHARACTER
        self.brain = GeminiBrain()
        self.cfo_brain = CFOBrainAgent()
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.cfo_chat_id = os.getenv("CFO_CHAT_ID")
        
        # In-memory context for conversations (simplified)
        self.contexts = {} 

    def get_context(self, chat_id: int) -> dict:
        """Retrieve conversation context for a chat ID."""
        if chat_id not in self.contexts:
            self.contexts[chat_id] = {
                "pending_actions": "None",
                "last_message": "None",
                "pending": {}
            }
        return self.contexts[chat_id]

    @track(name="priya.format_briefing")
    def format_for_human(self, briefing_data: dict) -> str:
        """
        Priya takes the CFO's briefing and formats it for the human.
        """
        formatted = self.brain.think(
            character=self.character,
            context=f"""
CFO'S BRIEFING: {briefing_data['briefing']}
ACTIONS NEEDING DECISION: {briefing_data['actions_needed']}
""",
            question="""
Format this briefing for a busy executive reading on their phone. Make it:
- Easy to scan quickly
- Use emojis to highlight key points
- Put the most important thing first
- Make the action items crystal clear
- Tell them exactly how to respond

Keep it under 3000 characters. Make sure they can respond with simple words like YES, NO, APPROVE, HOLD.
"""
        )
        return formatted.response

    @track(name="priya.understand_message")
    def understand_message(self, message: str, context: dict) -> dict:
        """
        Priya figures out what the human is saying.
        """
        understanding_resp = self.brain.think(
            character=self.character,
            context=f"""
PENDING ITEMS WE'RE WAITING FOR RESPONSE ON: {context.get('pending_actions', 'None')}
LAST MESSAGE WE SENT: {context.get('last_message', 'None')}
HUMAN'S MESSAGE: {message}
""",
            question="""
What is the human telling us? 
Think about their intent. Are they approving, rejecting, asking a question, or giving instructions?

Give your answer as a JSON object with keys:
- "intent": (approval/rejection/question/instruction/acknowledgment)
- "is_decision": (boolean)
- "explanation": (what you understood)
- "reply_suggestion": (how we should reply)
"""
        )
        return parse_json(understanding_resp.response)

    def _is_decision(self, understanding: dict) -> bool:
        """Check if Priya thinks this is a decision."""
        return understanding.get("is_decision", False) or \
               understanding.get("intent") in ["approval", "rejection"]

    async def send_message(self, chat_id: int, text: str):
        """Send a message via Telegram."""
        # This would normally use the bot instance
        # For implementation purposes, we'll assume an 'app' instance is provided or initialized
        print(f"TELEGRAM SEND -> {chat_id}: {text}")

    async def on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming message from human."""
        message = update.message.text
        chat_id = update.message.chat_id
        
        # Get conversation context
        conv_context = self.get_context(chat_id)
        
        # Priya understands the message
        understanding = self.understand_message(message, conv_context)
        
        # Route to CFOBrain if it's a decision
        if self._is_decision(understanding):
            result = self.cfo_brain.process_human_response(
                message, 
                conv_context.get('pending')
            )
            response = result.get("understanding", "I've processed your response, sir.")
        else:
            # Priya handles directly (questions, small talk, etc)
            response = understanding.get("reply_suggestion", "I've noted that. Is there anything else?")
            
        # Update context
        conv_context["last_message"] = response
        
        await update.message.reply_text(response)

    async def on_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document/photo upload."""
        doc = update.message.document or update.message.photo[-1]
        file = await context.bot.get_file(doc.file_id)
        
        file_name = doc.file_name if hasattr(doc, 'file_name') else f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        file_path = os.path.join("data", file_name)
        
        await file.download_to_drive(file_path)
        
        # Notify human we're processing
        await update.message.reply_text("I've received the document. Meera and Rajesh are looking at it now...")

        # Send to CFOBrain for processing
        result = self.cfo_brain.handle_new_document(file_path)
        
        # Format response
        decision = result.get("cfo_decision", "The CFO is still reviewing this.")
        
        await update.message.reply_text(f"Update on {file_name}:\n\n{decision}")

    @track(name="priya.send_alert")
    async def send_alert(self, chat_id: int, alert_data: dict, bot):
        """
        Priya sends an urgent alert.
        """
        formatted = self.brain.think(
            character=self.character,
            context=f"ALERT DATA: {alert_data}",
            question="""
Format this as an URGENT alert message. Make it:
- Immediately clear this is urgent
- Say what the problem is in one line
- Say what action is needed
- Give them a way to respond quickly

Use 🚨 emoji to grab attention.
"""
        )
        
        await bot.send_message(chat_id=chat_id, text=formatted.response)

    def handle_directly(self, message: str, understanding: dict) -> str:
        """Priya answers simple things directly."""
        return understanding.get("reply_suggestion", "I'm on it!")

    def format_confirmation(self, result: dict) -> str:
        """Helper to format CFO decision confirmation."""
        return result.get("understanding", "Action confirmed.")
