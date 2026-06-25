from telegram import Bot
from config import BOT_TOKEN, CHAT_ID

bot = Bot(token=BOT_TOKEN)

def send_message(text):
    bot.send_message(chat_id=CHAT_ID, text=text)

if __name__ == "__main__":
    send_message("✅ Forex Signal Bot ishga tushdi!")
