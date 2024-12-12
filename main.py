import asyncio
import logging

from aiogram.contrib.fsm_storage.memory import MemoryStorage

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
    storage = MemoryStorage()
    bot = JokeBot(llm_requester)

    await bot.start_polling()

if __name__ == "__main__":
    asyncio.run(main())