# telegram_bot.py
from telegram import Bot
import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('config.ini')

TELEGRAM_TOKEN = config['telegram']['token']
TELEGRAM_CHAT_ID = config['telegram']['chat_id']

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(symbol, latest_data, analysis):
    message = f"Latest data for {symbol}:\n{latest_data.to_string(index=False)}\n\nAnalysis:\n{analysis}"
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("Message sent to Telegram group.")
    except Exception as e:
        print(f"Failed to send message to Telegram: {e}")