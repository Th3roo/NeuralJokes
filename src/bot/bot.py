import telebot
from telebot import types
import time
import logging
import json
from src.LLM.LLMRequests import LLMRequester
from config.config import BOT_TOKEN, BOT_JOKE_GENERATION__COOLDOWN, BOT_JOKE_GENERATION__MAX_RETRIES

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

    for attempt in range(BOT_JOKE_GENERATION__MAX_RETRIES):
        response = llm_requester.generate_response("Generate a random joke")
        try:
            joke = json.loads(response)['joke']
            bot.reply_to(message, joke)
            logger.info(f"Generated a random joke for user {message.from_user.id}")
            break
        except (json.JSONDecodeError, KeyError):
            logger.warning(
                f"Attempt {attempt + 1} failed to generate a joke for user {message.from_user.id}. Retrying...")
            if attempt == BOT_JOKE_GENERATION__MAX_RETRIES - 1:
                bot.reply_to(message, "Sorry, I couldn't generate a joke right now. Please try again later.")
                logger.error(f"Failed to generate a joke for user {message.from_user.id} after multiple attempts.")

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

        for attempt in range(BOT_JOKE_GENERATION__MAX_RETRIES):
            response = llm_requester.generate_response(f"Generate a joke on the topic: {topic}")
            try:
                joke = json.loads(response)['joke']
                bot.reply_to(message, joke)
                logger.info(f"Generated a joke on the topic '{topic}' for user {message.from_user.id}")
                break
            except (json.JSONDecodeError, KeyError):
                logger.warning(
                    f"Attempt {attempt + 1} to generate a joke on the topic '{topic}' for user {message.from_user.id} failed. Retrying...")
                if attempt == BOT_JOKE_GENERATION__MAX_RETRIES - 1:
                    bot.reply_to(message,
                                 "Sorry, I couldn't generate a joke for this topic right now. Please try again later.")
                    logger.error(
                        f"Failed to generate a joke on the topic '{topic}' for user {message.from_user.id} after multiple attempts.")
    else:
        bot.reply_to(message, "Please specify a topic for the joke after the /generate_joke command.")
        logger.warning(f"User {message.from_user.id} did not specify a topic for the joke.")
