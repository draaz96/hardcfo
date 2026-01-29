import os
import asyncio
import sys
import logging
from datetime import date
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Import agents and tools
from agents.cfo_brain import CFOBrainAgent
from agents.human_interface import HumanInterfaceAgent
from agents.finance_manager import FinanceManagerAgent
from tools.data_store import DataStore

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

async def run_telegram_bot():
    """Start the Telegram bot and keep running."""
    logger.info("Initializing Human Interface (Priya)...")
    human_interface = HumanInterfaceAgent()
    
    if not human_interface.token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables.")
        return

    app = ApplicationBuilder().token(human_interface.token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Priya at your service, sir. How can I help you today?")))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), human_interface.on_message))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, human_interface.on_document))

    logger.info("Priya is now active on Telegram. Waiting for messages...")
    
    # Run the bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Keep running until interrupted
    while True:
        await asyncio.sleep(1)

def run_daily_briefing(chat_id: str):
    """Generate and send daily briefing."""
    logger.info("Rajesh is preparing the daily briefing...")
    cfo_brain = CFOBrainAgent()
    human_interface = HumanInterfaceAgent()
    
    briefing_data = cfo_brain.create_daily_briefing()
    formatted = human_interface.format_for_human(briefing_data)
    
    logger.info("Briefing prepared. Sending to Telegram...")
    
    # In a real async environment, this would be part of an event loop
    async def send():
        app = ApplicationBuilder().token(human_interface.token).build()
        await app.bot.send_message(chat_id=chat_id, text=formatted)
        logger.info("Briefing sent successfully.")

    asyncio.run(send())

def check_status():
    """Quick status check of the system."""
    logger.info("Arjun is analyzing the cash position...")
    fm = FinanceManagerAgent()
    try:
        analysis = fm.analyze_cash_position()
        print("\n--- CURRENT FINANCIAL STATUS ---")
        print(analysis.response)
        print("--------------------------------\n")
    except Exception as e:
        logger.error(f"Error checking status: {e}")

def verify_connections():
    """Verify all external connections."""
    logger.info("Verifying connections...")
    try:
        # Check JSON Database
        ds = DataStore()
        logger.info("✅ Local JSON Database verified.")
        
        # Check Gemini (via an agent)
        fm = FinanceManagerAgent()
        # Simple think call to verify API key
        fm.brain.model.generate_content("Ping")
        logger.info("✅ Google Gemini connection verified.")
        
        # Check Telegram token
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if token:
            logger.info("✅ Telegram Bot Token found.")
        else:
            logger.warning("❌ Telegram Bot Token MISSING.")
            
        return True
    except Exception as e:
        logger.error(f"❌ Connection verification failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py [bot|briefing|status|verify]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "bot":
        try:
            asyncio.run(run_telegram_bot())
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
        except Exception as e:
            logger.critical(f"Critical error in bot: {e}")
            
    elif command == "briefing":
        chat_id = os.getenv("CFO_CHAT_ID")
        if not chat_id:
            print("Error: CFO_CHAT_ID not found in .env")
        else:
            run_daily_briefing(chat_id)
            
    elif command == "status":
        check_status()
        
    elif command == "verify":
        if verify_connections():
            print("\nAll systems GO! 🚀")
        else:
            print("\nSystem verification FAILED. Check logs.")
            
    else:
        print(f"Unknown command: {command}")
        print("Usage: python main.py [bot|briefing|status|verify]")
