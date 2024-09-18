#export TELEGRAM_BOT_TOKEN='your-telegram-bot-token'
# export GROQ_API_KEY='your-groq-api-key'

###pip3 install (python version >= 3.7.0)
#requests
#python-telegram-bot

# Run in background
# nohup python3 main.py &

import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from groq import Groq

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the GROG client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! Send me your text, and I will improve it.')

async def improve_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Improve the text sent by the user."""
    user_text = update.message.text
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": user_text}],
            model="llama-3.1-70b-versatile"
        )
        improved_text = chat_completion.choices[0].message.content
        await update.message.reply_text(improved_text)
    except Exception as e:
        logger.error(f"Error while processing text: {e}")
        await update.message.reply_text('Sorry, there was an error processing your request.')

def main() -> None:
    """Start the bot."""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, improve_text))

    application.run_polling()

if __name__ == '__main__':
    main()