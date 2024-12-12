import telebot
from telebot import types
import time
import logging
from src.LLM.LLMRequests import LLMRequester
from config.config import BOT_TOKEN, BOT_JOKE_GENERATION__COOLDOWN

# Logger setup
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN)

llm_requester = LLMRequester()

last_joke_time = 0

@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info(f"Received /start command from user {message.from_user.id}")
    bot.reply_to(message, "Hi! I'm a bot that can generate jokes. Use the commands /generate_random_joke or /generate_joke <Topic>.")

@bot.message_handler(commands=['generate_random_joke'])
def generate_random_joke(message):
    logger.info(f"Received /generate_random_joke command from user {message.from_user.id}")
    global last_joke_time
    current_time = time.time()
    if current_time - last_joke_time < BOT_JOKE_GENERATION__COOLDOWN:
        remaining_time = int(BOT_JOKE_GENERATION__COOLDOWN - (current_time - last_joke_time))
        bot.reply_to(message, f"Please wait {remaining_time} more seconds before generating another joke.")
        logger.info(f"User {message.from_user.id} requested a joke too soon. Remaining time: {remaining_time} seconds.")
        return

    last_joke_time = current_time
    bot.reply_to(message, "Generating a random joke...")
    response = llm_requester.generate_response("Generate a random joke")
    bot.reply_to(message, response)
    logger.info(f"Generated a random joke for user {message.from_user.id}")

@bot.message_handler(commands=['generate_joke'])
def generate_joke_with_topic(message):
    logger.info(f"Received /generate_joke command from user {message.from_user.id}")
    global last_joke_time
    current_time = time.time()
    if current_time - last_joke_time < BOT_JOKE_GENERATION__COOLDOWN:
        remaining_time = int(BOT_JOKE_GENERATION__COOLDOWN - (current_time - last_joke_time))
        bot.reply_to(message, f"Please wait {remaining_time} more seconds before generating another joke.")
        logger.info(f"User {message.from_user.id} requested a joke too soon. Remaining time: {remaining_time} seconds.")
        return

    last_joke_time = current_time
    topic = message.text.split(' ', 1)
    if len(topic) > 1:
        topic = topic[1]
        bot.reply_to(message, f"Generating a joke on the topic: {topic}...")
        response = llm_requester.generate_response(f"Generate a joke on the topic: {topic}")
        bot.reply_to(message, response)
        logger.info(f"Generated a joke on the topic '{topic}' for user {message.from_user.id}")
    else:
        bot.reply_to(message, "Please specify a topic for the joke after the /generate_joke command.")
        logger.warning(f"User {message.from_user.id} did not specify a topic for the joke.")