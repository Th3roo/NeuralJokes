import time
import logging
import json

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.LLM.LLMRequests import LLMRequester
from config.config import BOT_JOKE_GENERATION__COOLDOWN, BOT_JOKE_GENERATION__MAX_RETRIES

# Logger setup
logger = logging.getLogger(__name__)

class Form(StatesGroup):
    waiting_for_topic = State()

class JokeBot:
    def __init__(self, dp: Dispatcher, llm_requester: LLMRequester):
        self.dp = dp
        self.llm_requester = llm_requester
        self.last_joke_time = {}
        self.router = Router()

        self.register_handlers()

    def register_handlers(self):
        self.router.message(Command("start"))(self.send_welcome)
        self.router.message(Command("generate_random_joke"))(self.generate_random_joke)
        self.router.message(Command("generate_joke"))(self.start_generate_joke_with_topic)
        self.router.message(Form.waiting_for_topic)(self.generate_joke_with_topic)

        self.dp.include_router(self.router)

    async def send_welcome(self, message: types.Message):
        logger.info(f"Received /start command from user {message.from_user.id}")

        await message.reply("Hi! I'm a bot that can generate jokes. Use the commands /generate_random_joke or /generate_joke <Topic>.")

    async def generate_random_joke(self, message: types.Message):
        logger.info(f"Received /generate_random_joke command from user {message.from_user.id}")

        user_id = message.from_user.id
        current_time = time.time()

        if user_id in self.last_joke_time and current_time - self.last_joke_time[user_id] < BOT_JOKE_GENERATION__COOLDOWN:
            remaining_time = int(BOT_JOKE_GENERATION__COOLDOWN - (current_time - self.last_joke_time[user_id]))

            await message.reply(f"Please wait {remaining_time} more seconds before generating another joke.")
            logger.info(f"User {message.from_user.id} requested a joke too soon. Remaining time: {remaining_time} seconds.")

            return

        self.last_joke_time[user_id] = current_time
        await message.reply("Generating a random joke...")

        for attempt in range(BOT_JOKE_GENERATION__MAX_RETRIES):
            response = await self.llm_requester.generate_response_async("Generate a random joke")

            try:
                data = json.loads(response)

                if 'joke' in data:
                    joke = data['joke']

                    await message.reply(joke)
                    logger.info(f"Generated a random joke for user {message.from_user.id}")

                    break
                else:
                    logger.warning(f"Response does not contain 'joke' key: {response}")
                    raise ValueError("Response does not contain 'joke' key")
            except (json.JSONDecodeError, ValueError):
                logger.warning(
                    f"Attempt {attempt + 1} failed to generate a joke for user {message.from_user.id}. Retrying...")

                if attempt == BOT_JOKE_GENERATION__MAX_RETRIES - 1:
                    await message.reply("Sorry, I couldn't generate a joke right now. Please try again later.")
                    logger.error(f"Failed to generate a joke for user {message.from_user.id} after multiple attempts.")

    async def start_generate_joke_with_topic(self, message: types.Message, state: FSMContext):
        logger.info(f"Received /generate_joke command from user {message.from_user.id}")
        
        # Проверяем, есть ли тема в сообщении
        command_args = message.text.split(" ", 1)
        if len(command_args) > 1:
            await self.generate_joke_with_topic(message, state, command_args[1])
        else:
            await message.reply("Please enter a topic for the joke.")
            await state.set_state(Form.waiting_for_topic)

    async def generate_joke_with_topic(self, message: types.Message, state: FSMContext, topic: str = None):
        user_id = message.from_user.id
        current_time = time.time()

        if user_id in self.last_joke_time and current_time - self.last_joke_time[user_id] < BOT_JOKE_GENERATION__COOLDOWN:
            remaining_time = int(BOT_JOKE_GENERATION__COOLDOWN - (current_time - self.last_joke_time[user_id]))

            await message.reply(f"Please wait {remaining_time} more seconds before generating another joke.")
            logger.info(f"User {message.from_user.id} requested a joke too soon. Remaining time: {remaining_time} seconds.")
            await state.clear()

            return

        self.last_joke_time[user_id] = current_time
        
        # Если тема не передана, берем ее из сообщения
        if topic is None:
            topic = message.text

        if topic:
            processing_message = await message.reply(f"Generating a joke on the topic: {topic}...")

            for attempt in range(BOT_JOKE_GENERATION__MAX_RETRIES):
                response = await self.llm_requester.generate_response_async(f"Generate a joke on the topic: {topic}")

                try:
                    data = json.loads(response)

                    if 'joke' in data:
                        joke = data['joke']

                        await processing_message.edit_text(joke)
                        logger.info(f"Generated a joke on the topic '{topic}' for user {message.from_user.id}")

                        break
                    else:
                        logger.warning(f"Response does not contain 'joke' key: {response}")
                        raise ValueError("Response does not contain 'joke' key")
                except (json.JSONDecodeError, ValueError):
                    logger.warning(
                        f"Attempt {attempt + 1} to generate a joke on the topic '{topic}' for user {message.from_user.id} failed. Retrying...")
                    await processing_message.edit_text(f"Generating a joke on the topic: {topic}... (Attempt {attempt + 1})")

                    if attempt == BOT_JOKE_GENERATION__MAX_RETRIES - 1:
                        await processing_message.edit_text("Sorry, I couldn't generate a joke for this topic right now. Please try again later.")
                        logger.error(
                            f"Failed to generate a joke on the topic '{topic}' for user {message.from_user.id} after multiple attempts.")
        else:
            await message.reply("Please specify a topic for the joke after the /generate_joke command.")
            logger.warning(f"User {message.from_user.id} did not specify a topic for the joke.")

        await state.clear()