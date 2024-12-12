import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.bot import JokeBot
from src.LLM.LLMRequests import LLMRequester
from config.config import BOT_TOKEN

# Logger setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='logs/bot.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting Bot...")

    llm_requester = LLMRequester()
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    joke_bot = JokeBot(dp, llm_requester)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())