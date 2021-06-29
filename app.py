import logging
import os
from flask import Flask, request
from utils import get_reply, fetch_news, topics_keyboard
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import MessageHandler, Filters, CommandHandler, CallbackContext, Dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("token", "")

app = Flask(__name__)


@app.route('/')
def index():
    return "hello"


@app.route(f'/{TOKEN}', methods=['GET', 'POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dp.process_update(update)
    return "ok"


def start(update: Update, context: CallbackContext):
    print(update)
    reply = "How the bot works? \n\nMethod 1: \n1. Type / news \n2. Select the topic \n3. And you will get latest 5 news \n\nMethod 2: \n1. Be more specific \n2. You can type like :\n  - Show me tech news of Germany in Hindi\n  (keyword - tech, India, Hindi)\n  - I want sports news in Marathi\n  (keyword - sports, Marathi), etc \n3. And you will get latest 5 news"
    context.bot.send_message(chat_id=update.message.chat_id, text=reply)


def about(update: Update, context: CallbackContext):
    about_txt = "A telegram bot created using python-telegram-bot, gnewsclient and dialogflow. \n\nTill now topics supported :-\nWorld, Nation, Business, Technology, Entertainment, Sports, Science, Health"
    context.bot.send_message(chat_id=update.message.chat_id, text=about_txt)


def _help(update: Update, context: CallbackContext):
    help_txt = "For help you can contact @prenshoe"
    context.bot.send_message(chat_id=update.message.chat_id, text=help_txt)


def news(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id, text="Choose a Category",
                             reply_markup=ReplyKeyboardMarkup(keyboard=topics_keyboard, one_time_keyboard=True))


def reply_text(update: Update, context: CallbackContext):
    intent, reply = get_reply(update.message.text, update.message.chat_id)
    if intent == "get_news":
        articles = fetch_news(reply)
        for article in articles:
            context.bot.send_message(
                chat_id=update.message.chat_id, text=article['link'])
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=reply)


def echo_sticker(update: Update, context: CallbackContext):
    context.bot.send_sticker(
        chat_id=update.message.chat_id, sticker=update.message.sticker.file_id)


def error(update, context):
    logger.warning("Update '%s' caused error '%s' ", update, context.error)


bot = Bot(TOKEN)
try:
    bot.set_webhook("https://stark-reef-08185.herokuapp.com/" + TOKEN)
except Exception as e:
    print(e)

dp = Dispatcher(bot, None)
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("about", about))
dp.add_handler(CommandHandler("help", _help))
dp.add_handler(CommandHandler("news", news))
dp.add_handler(MessageHandler(Filters.text, reply_text))
dp.add_handler(MessageHandler(Filters.text, echo_sticker))
dp.add_error_handler(error)

if __name__ == "__main__":
    app.run(port=int(os.enviorn.get("PORT")))
