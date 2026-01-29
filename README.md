# CFO AI Agent - Construction Financial Management 🏗️💰

A sophisticated multi-agent AI system designed to automate financial workflows for construction companies. The system processes invoices, bank statements, manages cash flow, and communicates with the human CFO via Telegram.

## 🤖 Meet the Team

- **Meera (Document Processor)**: The meticulous accountant who "sees" and extracts every detail from your invoices and receipts using Gemini Vision.
- **Arjun (Finance Manager)**: The strategist who analyzes cash positions and recommends which payments to make or hold.
- **Rajesh (CFO Brain)**: The senior orchestrator who synthesizes all financial data and prepares daily briefings.
- **Priya (Human Interface)**: Your personal assistant on Telegram who keeps you informed and takes your approvals.

---

## 🛠 macOS Setup Guide

Follow these steps to get the system running on your Mac.

### 1. Clone the Repository
Open your Terminal and run:
```bash
git clone https://github.com/draaz96/hardcfo.git
cd hardcfo
```

### 2. Set Up a Virtual Environment (Recommended)
This keeps your system clean and avoids version conflicts.
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and fill in your keys:
```bash
cp .env.example .env
```
Now, open the `.env` file in your favorite editor (e.g., `nano .env`) and add your credentials:
- `GEMINI_API_KEY`: Get one from [Google AI Studio](https://aistudio.google.com/).
- `TELEGRAM_BOT_TOKEN`: Get one from [@BotFather](https://t.me/botfather) on Telegram.
- `CFO_CHAT_ID`: Your chat ID (you can find this by messaging [@userinfobot](https://t.me/userinfobot)).
- `OPIK_API_KEY`: (Optional) For tracing and debugging.

---

## 🚀 How to Run

### System Verification
First, ensure all connections (Gemini, Telegram, Database) are working:
```bash
python3 main.py verify
```

### Start the Telegram Bot
To start interacting with your AI CFO team via Telegram:
```bash
python3 main.py bot
```

### View Financial Status
Generate a quick snapshot of your current financial standing:
```bash
python3 main.py status
```

### Send Daily Briefing
Trigger the morning briefing to your Telegram:
```bash
python3 main.py briefing
```

---

## 📂 Project Structure
- `agents/`: Core logic for Meera, Arjun, Rajesh, and Priya.
- `tools/`: Data storage, Gemini client, and utility functions.
- `data/`: Local storage for the JSON database and uploaded documents.
- `config/`: Agent characters and system settings.

## 📝 License
This project is for internal financial management automation. Use with care.
