import time
import logging
import asyncio

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.LLM.LLMRequests import LLMRequester
from config.config import BOT_JOKE_GENERATION__COOLDOWN, BOT_JOKE_GENERATION__STREAMING_DELAY

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

        processing_message = await message.reply("Generating a random joke...")

        await self.generate_and_stream_response(processing_message, "Generate a random joke")

    async def start_generate_joke_with_topic(self, message: types.Message, state: FSMContext):
        logger.info(f"Received /generate_joke command from user {message.from_user.id}")

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

        if topic is None:
            topic = message.text

        if topic:
            processing_message = await message.reply(f"Generating a joke on the topic: {topic}...")
            await self.generate_and_stream_response(processing_message, f"Generate a joke on the topic: {topic}")
        else:
            await message.reply("Please specify a topic for the joke after the /generate_joke command.")
            logger.warning(f"User {message.from_user.id} did not specify a topic for the joke.")

        await state.clear()

    async def generate_and_stream_response(self, processing_message: types.Message, prompt: str):
        full_response = ""
        last_sent_message = ""

        try:
            async for response_part in self.llm_requester.generate_response_streaming(prompt):
                if response_part:
                    full_response += response_part

                    if full_response != last_sent_message:
                        try:
                            await processing_message.edit_text(full_response)
                            last_sent_message = full_response
                        except Exception as e:
                            if "message is not modified" not in str(e):
                                logger.warning(f"Failed to edit message: {e}")

                    await asyncio.sleep(BOT_JOKE_GENERATION__STREAMING_DELAY)

            logger.info(f"Completed streaming response for prompt: '{prompt}'")

        except Exception as e:
            logger.error(f"Error during streaming response: {e}")
            await processing_message.edit_text("Извините, произошла ошибка при генерации шутки.")
