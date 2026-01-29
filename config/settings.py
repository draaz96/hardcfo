import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPIK_API_KEY = os.getenv("OPIK_API_KEY")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    #GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
    #SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    CFO_CHAT_ID = os.getenv("CFO_CHAT_ID")

    # App Config
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    MODEL_NAME = "gemini-flash-latest"
    VISION_MODEL_NAME = "gemini-flash-latest"
