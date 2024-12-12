import logging

from src.bot.bot import bot

# Logger setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='logs/bot.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Bot...")
    bot.polling()
